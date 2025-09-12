import os
import requests
import random
import logging
import time
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.exceptions import HTTPError, Timeout, TooManyRedirects
import concurrent.futures
from utils import configure_logging  # Ensure this import is present

# Configure logging
configure_logging()

# Load API key from environment variable
API_KEY = os.getenv('SCRAPER_API_KEY', '913388054fb0c4f83448119baf79617e')
SCRAPERAPI_URL = f'http://api.scraperapi.com?api_key={API_KEY}&url='
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
]

session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))

def get_random_user_agent():
    """Select a random user agent from the list."""
    return random.choice(USER_AGENTS)

def fetch_url(url, timeout=10):
    """Fetch content from the URL with a specified timeout and return the response text."""
    headers = {'User-Agent': get_random_user_agent()}
    logging.debug(f'Fetching URL: {url} with headers: {headers}')
    try:
        response = session.get(SCRAPERAPI_URL + url, headers=headers, timeout=timeout)
        response.raise_for_status()
        logging.debug(f'URL fetched successfully: {url} - Response size: {len(response.content)} bytes')
        return response.text
    except (HTTPError, Timeout, TooManyRedirects) as e:
        logging.error(f'Error fetching {url}: {e}')
        raise
    except Exception as e:
        logging.error(f'Unexpected error fetching {url}: {e}')
        raise

def get_page_content(url, retries=3, delay=5, timeout=10):
    """Fetch page content with retries and delay."""
    for attempt in range(retries):
        try:
            return fetch_url(url, timeout)
        except Exception as e:
            logging.error(f'Error fetching {url}: {e}, attempt {attempt + 1} of {retries}')
            time.sleep(delay * (2 ** attempt))  # Exponential backoff
    return None

def scrape_text_data(url):
    """Scrape text data from the specified URL."""
    logging.debug(f'Start scraping text data from {url}')
    page_content = get_page_content(url)
    if not page_content:
        logging.error(f'Failed to retrieve content from {url}')
        return None
    
    soup = BeautifulSoup(page_content, 'html.parser')
    title = soup.title.string if soup.title else 'No title found'
    content = []
    for tag in soup.select('h1, h2, h3, h4, h5, h6, p, div, span, li, code, pre'):
        text = tag.get_text(separator=' ', strip=True)
        if tag.name in ['code', 'pre']:
            content.append(f"\n{text}\n")
        else:
            content.append(text)
    
    full_content = f"{title}\n\n" + "\n".join(content)
    logging.debug(f'Scraped content from {url}')
    return full_content.strip()

def save_data_to_file(data, filename, file_format='txt'):
    """Save data to a file with the specified format."""
    if file_format == 'txt':
        filename = filename.replace('.md', '.txt')
    elif file_format == 'md':
        filename = filename.replace('.txt', '.md')
    
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(data)
        logging.info(f'Successfully saved data to {filename}')
    except Exception as e:
        logging.error(f'Failed to save data to {filename}: {e}')

def scrape_multiple_urls(urls):
    """Scrape multiple URLs concurrently."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(scrape_text_data, urls)
    return list(results)