# Web Scraping Application

## Introduction
This project is a web scraping application developed using Kivy for the user interface and various Python libraries for web scraping and data processing. The application allows users to enter URLs, select a file format, and scrape data from the provided URLs. The scraped data is then saved to files in the chosen format.

## Features
- User-friendly GUI for entering URLs and selecting output format.
- Concurrent URL scraping with retry logic and exponential backoff.
- Supports saving data in both text (`.txt`) and markdown (`.md`) formats.
- Logging for debugging and tracking the scraping process.

## Installation

### Prerequisites
Ensure you have Python installed on your system. This project uses the following Python libraries:
- Kivy
- Requests
- BeautifulSoup4
- Python's logging module

### Setup
1. Clone the repository or download the source code.
2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

## Usage
1. Ensure you have the necessary environment variables set up, specifically:
   - `SCRAPER_API_KEY` for the API key used in the scraping process.
   - Optional environment variables for configuring Kivy graphics settings.
   
   You can set these in a `.env` file in the root directory:
   ```
   SCRAPER_API_KEY=your_api_key_here
   KIVY_FULLSCREEN=auto
   KIVY_WIDTH=800
   KIVY_HEIGHT=600
   ```

2. Run the application:
   ```sh
   python main.py
   ```

3. In the GUI, enter the URLs separated by commas, select the desired file format (TXT or MD), and click "Start Scraping".

## Project Structure
- **main.py**: The entry point for the application. It loads environment variables, configures logging, and starts the Kivy app.
- **ui.py**: Contains the Kivy-based user interface definition and logic.
- **scraper.py**: Contains functions for web scraping, including fetching URLs, parsing content, and saving data.
- **utils.py**: Utility functions for configuring logging.

## Code Overview

### main.py
```python
import os
from dotenv import load_dotenv
from utils import configure_logging
from kivy.config import Config
from ui import ScraperApp
import logging

load_dotenv()
configure_logging()

Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'fullscreen', os.getenv('KIVY_FULLSCREEN', 'auto'))
Config.set('graphics', 'width', os.getenv('KIVY_WIDTH', '800'))
Config.set('graphics', 'height', os.getenv('KIVY_HEIGHT', '600'))

def main():
    try:
        ScraperApp().run()
    except Exception as e:
        logging.error(f'Application error: {e}', exc_info=True)
    finally:
        logging.info('ScraperApp ended')

if __name__ == "__main__":
    main()
```

### scraper.py
```python
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
from utils import configure_logging

configure_logging()

API_KEY = os.getenv('SCRAPER_API_KEY', '   ')
SCRAPERAPI_URL = f'http://api.scraperapi.com?api_key={API_KEY}&url='
USER_AGENTS = [ ... ]  # User agents list here

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def fetch_url(url, timeout=10):
    headers = {'User-Agent': get_random_user_agent()}
    try:
        response = session.get(SCRAPERAPI_URL + url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except (HTTPError, Timeout, TooManyRedirects) as e:
        logging.error(f'Error fetching {url}: {e}')
        raise
    except Exception as e:
        logging.error(f'Unexpected error fetching {url}: {e}')
        raise

def get_page_content(url, retries=3, delay=5, timeout=10):
    for attempt in range(retries):
        try:
            return fetch_url(url, timeout)
        except Exception as e:
            logging.error(f'Error fetching {url}: {e}, attempt {attempt + 1} of {retries}')
            time.sleep(delay * (2 ** attempt))  # Exponential backoff
    return None

def scrape_text_data(url):
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
    return full_content.strip()

def save_data_to_file(data, filename, file_format='txt'):
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
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(scrape_text_data, urls)
    return list(results)
```

### ui.py
```python
import os
import re
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import threading
import logging
from scraper import scrape_text_data, save_data_to_file, scrape_multiple_urls
from utils import configure_logging

class ScraperApp(App):
    def build(self):
        configure_logging()
        self.format_var = 'txt'
        anchor_layout = AnchorLayout()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint=(0.8, 0.8))
        
        header = Label(text='Web Scraping App', font_size=24, size_hint_y=None, height=50)
        layout.add_widget(header)

        description = Label(text='Enter URLs separated by commas and choose the file format for the scraped data.', font_size=16, size_hint_y=None, height=60)
        layout.add_widget(description)

        self.url_entry = TextInput(hint_text='Enter URLs separated by commas', multiline=True, font_size=14, size_hint_y=None, height=100)
        layout.add_widget(self.url_entry)

        layout.add_widget(self.create_format_selection())

        start_button = Button(text='Start Scraping', size_hint_y=None, height=50)
        start_button.bind(on_press=self.start_scraping)
        layout.add_widget(start_button)

        self.progress_bar = ProgressBar(max=100, size_hint_y=None, height=30)
        layout.add_widget(self.progress_bar)

        self.progress_label = Label(text='Waiting to start...', font_size=16, size_hint=(1, None), height=40)
        layout.add_widget(self.progress_label)

        self.log_output = TextInput(readonly=True, multiline=True)
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.log_output)
        layout.add_widget(scroll_view)

        layout.add_widget(self.create_footer())

        anchor_layout.add_widget(layout)

        return anchor_layout

    def create_format_selection(self):
        format_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        txt_layout = BoxLayout(orientation='horizontal')
        txt_checkbox = CheckBox(group='format')
        txt_checkbox.bind(active=self.set_format_txt)
        txt_checkbox.active = True  # Default to txt
        txt_layout.add_widget(txt_checkbox)
        txt_layout.add_widget(Label(text='TXT', font_size=16))
        format_layout.add_widget(txt_layout)

        md_layout = BoxLayout(orientation='horizontal')
        md_checkbox = CheckBox(group='format')
        md_checkbox.bind(active=self.set_format_md)
        md_layout.add_widget(md_checkbox)
        md_layout.add_widget(Label(text='MD', font_size=16))
        format_layout.add_widget(md_layout)

        return format_layout

    def create_footer(self):
        footer_layout = BoxLayout(size_hint_y=None, height=50, padding=[10, 10, 10, 10],

 spacing=10)
        
        help_button = Button(text='Help', size_hint=(0.2, 1), height=50)
        help_button.bind(on_press=self.show_help)
        footer_layout.add_widget(help_button)
        
        footer_label = Label(text='© 2024 ARTOfficial Intelligence LLC', size_hint=(0.8, 1), halign='center', valign='middle', font_size=14)
        footer_label.bind(size=self.update_text_size)
        footer_layout.add_widget(footer_label)
        
        return footer_layout

    def update_text_size(self, instance, value):
        instance.text_size = instance.size

    def show_help(self, instance):
        help_content = Label(text='Enter the URLs separated by commas, select the format, and click "Start Scraping".',
                             text_size=(400, None), halign='center', valign='middle')
        help_content.bind(size=self.update_text_size)
        popup = Popup(title='Help', content=help_content, size_hint=(0.8, 0.4))
        popup.open()

    def set_format_txt(self, checkbox, value):
        if value:
            self.format_var = "txt"
            logging.debug('Format set to TXT')

    def set_format_md(self, checkbox, value):
        if value:
            self.format_var = "md"
            logging.debug('Format set to MD')

    def update_progress(self, message, progress=None):
        Clock.schedule_once(lambda dt: self._update_progress(message, progress))

    def _update_progress(self, message, progress=None):
        self.progress_label.text = message
        self.log_output.text += message + '\n'
        if progress is not None:
            self.progress_bar.value = progress
        logging.debug(message)

    def start_scraping(self, instance):
        logging.debug('Start Scraping button pressed')
        self.update_progress('Initializing web scraping process...')
        urls = [url.strip() for url in self.url_entry.text.split(',') if url.strip()]
        file_format = self.format_var
        logging.debug(f'URLs entered: {urls}')
        logging.debug(f'File format selected: {file_format}')
        if not urls:
            logging.error('No URLs entered')
            self.update_progress('No URLs entered. Please provide at least one URL.')
            popup = Popup(title='Input Error', content=Label(text='Please enter at least one URL.'),
                          size_hint=(0.8, 0.2))
            popup.open()
            return
        self.update_progress('Validating URLs...')
        valid_urls = [url for url in urls if url.startswith('http')]
        if not valid_urls:
            self.update_progress('No valid URLs to scrape.')
            return
        logging.debug('Starting thread for scrape_and_save')
        self.update_progress('Starting scraping...')
        threading.Thread(target=self.scrape_and_save, args=(valid_urls, file_format)).start()

    def scrape_and_save(self, urls, file_format):
        logging.debug('Scraping and saving started')
        total_urls = len(urls)
        base_directory = '/storage/emulated/0/latest scraper/all_scraped_data'
        
        if not os.path.exists(base_directory):
            os.makedirs(base_directory)

        for index, url in enumerate(urls):
            progress = ((index + 1) / total_urls) * 100
            logging.debug(f'Scraping URL: {url}')
            self.update_progress(f'Starting to scrape URL: {url}', progress)
            scraped_data = scrape_text_data(url)
            if scraped_data:
                sanitized_url = re.sub(r'[^a-zA-Z0-9]', '_', url)
                filename = f'{sanitized_url}_{index + 1}.{file_format}'
                file_path = os.path.join(base_directory, filename)
                logging.debug(f'Saving scraped data to file: {file_path}')
                save_data_to_file(scraped_data, filename=file_path, file_format=file_format)
                self.update_progress(f'Data successfully scraped from {url}. Saving to {file_path}...', progress)
                self.update_progress(f'Data saved to {file_path}.', progress)
            else:
                logging.error(f'No data scraped from {url}')
                self.update_progress(f'No data found at {url}.', progress)
        self.update_progress(f'All URLs processed successfully. Scraping completed. Files saved to {base_directory}', 100)

if __name__ == '__main__':
    configure_logging()
    ScraperApp().run()
```

### utils.py
```python
import logging
import os
from logging.handlers import RotatingFileHandler

def configure_logging(log_dir=None):
    if (log_dir is None) or (not log_dir.strip()):
        log_dir = os.getenv('SCRAPER_LOG_DIR', '/storage/emulated/0/latest scraper')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_filename = 'scraper.log'
    log_filepath = os.path.join(log_dir, log_filename)
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(log_filepath, maxBytes=5*1024*1024, backupCount=5),
            logging.StreamHandler()
        ]
    )
    logging.debug("Logging configured successfully.")
```

## License
This project is licensed under the MIT License.

## Acknowledgements
- Kivy: For providing the framework for the UI.
- BeautifulSoup: For making HTML parsing easy.
- Requests: For simplifying HTTP requests.

## Contact
For any inquiries or support, please contact ARTOfficial Intelligence LLC.

---
