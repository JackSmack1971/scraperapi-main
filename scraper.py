import os
import requests
import random
import logging
import time
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry  # FIXED: Updated import path
from requests.exceptions import HTTPError, Timeout, TooManyRedirects, RequestException
import concurrent.futures
from urllib.parse import urljoin, urlparse
from utils import configure_logging

# Configure logging
configure_logging()

# Load API key from environment variable - SECURITY IMPROVEMENT
API_KEY = os.getenv('SCRAPER_API_KEY')
if not API_KEY:
    logging.error("SCRAPER_API_KEY environment variable is required")
    raise ValueError("SCRAPER_API_KEY environment variable must be set")

SCRAPERAPI_URL = f'https://api.scraperapi.com?api_key={API_KEY}&url='

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
]

# IMPROVED: Better retry configuration with more specific status codes and methods
session = requests.Session()
retries = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504, 520, 521, 522, 523, 524],
    allowed_methods=frozenset(['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'TRACE'])  # Updated from 'method_whitelist'
)
session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))  # Added HTTPS adapter


def get_random_user_agent():
    """Select a random user agent from the list."""
    return random.choice(USER_AGENTS)


def validate_url(url):
    """Validate URL format and scheme."""
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid URL format: {url}")
        if parsed.scheme not in ['http', 'https']:
            raise ValueError(f"Unsupported URL scheme: {parsed.scheme}")
        return True
    except Exception as e:
        logging.error(f"URL validation failed for {url}: {e}")
        return False


def fetch_url(url, timeout=10):
    """Fetch content from the URL with a specified timeout and return the response text."""
    if not validate_url(url):  # ADDED: URL validation
        raise ValueError(f"Invalid URL: {url}")
    
    headers = {'User-Agent': get_random_user_agent()}
    logging.debug(f'Fetching URL: {url} with headers: {headers}')
    
    try:
        response = session.get(SCRAPERAPI_URL + url, headers=headers, timeout=timeout)
        response.raise_for_status()
        logging.debug(f'URL fetched successfully: {url} - Response size: {len(response.content)} bytes')
        return response.text
    except (HTTPError, Timeout, TooManyRedirects) as e:
        logging.error(f'HTTP/Network error fetching {url}: {e}')
        raise
    except RequestException as e:  # IMPROVED: More specific exception handling
        logging.error(f'Request error fetching {url}: {e}')
        raise
    except Exception as e:
        logging.error(f'Unexpected error fetching {url}: {e}')
        raise


def get_page_content(url, retries=3, delay=5, timeout=10):
    """Fetch page content with retries and exponential backoff."""
    if not validate_url(url):  # ADDED: URL validation
        logging.error(f"Invalid URL provided: {url}")
        return None
    
    for attempt in range(retries):
        try:
            return fetch_url(url, timeout)
        except RequestException as e:  # IMPROVED: More specific exception handling
            logging.warning(f'Request error fetching {url}: {e}, attempt {attempt + 1} of {retries}')
            if attempt < retries - 1:  # Don't sleep on the last attempt
                sleep_time = delay * (2 ** attempt)
                logging.debug(f'Waiting {sleep_time} seconds before retry...')
                time.sleep(sleep_time)
        except Exception as e:
            logging.error(f'Unexpected error fetching {url}: {e}, attempt {attempt + 1} of {retries}')
            if attempt < retries - 1:
                time.sleep(delay * (2 ** attempt))
    
    logging.error(f'Failed to fetch {url} after {retries} attempts')
    return None


def scrape_text_data(url):
    """Scrape text data from the specified URL."""
    logging.debug(f'Start scraping text data from {url}')
    
    if not validate_url(url):  # ADDED: URL validation
        logging.error(f'Invalid URL provided: {url}')
        return None
    
    page_content = get_page_content(url)
    if not page_content:
        logging.error(f'Failed to retrieve content from {url}')
        return None
    
    try:
        soup = BeautifulSoup(page_content, 'html.parser')
        
        # IMPROVED: Better title extraction with fallbacks
        title = 'No title found'
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.find('h1'):
            title = soup.find('h1').get_text(strip=True)
        
        content = []
        
        # IMPROVED: More comprehensive content extraction
        content_selectors = [
            'article', 'main', '.content', '#content',  # Common content containers
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',       # Headers
            'p', 'div', 'span', 'li',                   # Text content
            'code', 'pre',                              # Code blocks
            'blockquote', 'q'                           # Quotes
        ]
        
        # Try to find main content area first
        main_content = soup.find(['article', 'main']) or soup.find(class_=['content', 'main-content']) or soup.find(id=['content', 'main-content'])
        search_area = main_content if main_content else soup
        
        for tag in search_area.select(', '.join(content_selectors[4:])):  # Skip container selectors for individual elements
            if tag.name in ['script', 'style', 'nav', 'header', 'footer']:  # Skip unwanted elements
                continue
                
            text = tag.get_text(separator=' ', strip=True)
            if text and len(text.strip()) > 10:  # Filter out very short or empty content
                if tag.name in ['code', 'pre']:
                    content.append(f"\n{text}\n")
                elif tag.name in ['blockquote', 'q']:
                    content.append(f'> {text}')
                elif tag.name.startswith('h'):
                    content.append(f'\n{"#" * int(tag.name[1])} {text}\n')
                else:
                    content.append(text)
        
        if not content:  # Fallback if no content found
            logging.warning(f'No structured content found for {url}, using body text')
            body_text = soup.get_text(separator=' ', strip=True)
            content = [body_text] if body_text else ['No content found']
        
        full_content = f"Title: {title}\n\n" + "\n".join(content)
        logging.debug(f'Scraped {len(content)} content elements from {url}')
        return full_content.strip()
        
    except Exception as e:
        logging.error(f'Error parsing content from {url}: {e}')
        return None


def save_data_to_file(data, filename, file_format='txt'):
    """Save data to a file with the specified format."""
    if not data:
        logging.warning(f'No data to save for {filename}')
        return False
    
    try:
        # IMPROVED: Better file extension handling
        base_name, current_ext = os.path.splitext(filename)
        if file_format == 'txt':
            filename = base_name + '.txt'
        elif file_format == 'md':
            filename = base_name + '.md'
        else:
            logging.warning(f'Unsupported file format: {file_format}, defaulting to txt')
            filename = base_name + '.txt'
        
        # ADDED: Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(data)
        logging.info(f'Successfully saved {len(data)} characters to {filename}')
        return True
        
    except Exception as e:
        logging.error(f'Failed to save data to {filename}: {e}')
        return False


def scrape_multiple_urls(urls, max_workers=3):  # IMPROVED: Reduced default workers to be more respectful
    """Scrape multiple URLs concurrently with improved error handling."""
    if not urls:
        logging.warning('No URLs provided for scraping')
        return []
    
    # Filter out invalid URLs
    valid_urls = [url for url in urls if validate_url(url)]
    invalid_count = len(urls) - len(valid_urls)
    
    if invalid_count > 0:
        logging.warning(f'Skipped {invalid_count} invalid URLs')
    
    if not valid_urls:
        logging.error('No valid URLs to scrape')
        return []
    
    logging.info(f'Starting concurrent scraping of {len(valid_urls)} URLs with {max_workers} workers')
    
    results = []
    failed_urls = []
    
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_url = {executor.submit(scrape_text_data, url): url for url in valid_urls}
            
            # Process completed tasks
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result(timeout=60)  # 60 second timeout per URL
                    if result:
                        results.append(result)
                    else:
                        failed_urls.append(url)
                        logging.warning(f'No content scraped from {url}')
                except concurrent.futures.TimeoutError:
                    logging.error(f'Timeout scraping {url}')
                    failed_urls.append(url)
                except Exception as e:
                    logging.error(f'Error scraping {url}: {e}')
                    failed_urls.append(url)
    
    except Exception as e:
        logging.error(f'Error in concurrent scraping: {e}')
    
    success_count = len(results)
    logging.info(f'Scraping completed: {success_count} successful, {len(failed_urls)} failed')
    
    if failed_urls:
        logging.warning(f'Failed URLs: {failed_urls}')
    
    return results


# ADDED: Utility function for batch processing
def scrape_urls_to_files(urls, output_dir='scraped_data', file_format='txt', max_workers=3):
    """Scrape URLs and save each to a separate file."""
    if not urls:
        return []
    
    os.makedirs(output_dir, exist_ok=True)
    results = scrape_multiple_urls(urls, max_workers)
    saved_files = []
    
    for i, (url, content) in enumerate(zip(urls, results)):
        if content:
            # Generate filename from URL
            parsed_url = urlparse(url)
            safe_filename = parsed_url.netloc.replace('.', '_') + f'_{i+1}'
            filepath = os.path.join(output_dir, f'{safe_filename}.{file_format}')
            
            if save_data_to_file(content, filepath, file_format):
                saved_files.append(filepath)
    
    logging.info(f'Saved {len(saved_files)} files to {output_dir}')
    return saved_files
