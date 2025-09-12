import os
from dotenv import load_dotenv
from utils import configure_logging  # Ensure this import is present

# Load environment variables from .env file
load_dotenv()
configure_logging()

from kivy.config import Config
from ui import ScraperApp
import logging

# Configure Kivy settings from environment variables
Config.set('graphics', 'multisamples', '0')  # Disable multisampling
Config.set('graphics', 'fullscreen', os.getenv('KIVY_FULLSCREEN', 'auto'))
Config.set('graphics', 'width', os.getenv('KIVY_WIDTH', '800'))
Config.set('graphics', 'height', os.getenv('KIVY_HEIGHT', '600'))

def main():
    try:
        ScraperApp().run()
    except Exception as e:
        logging.error('Application encountered an error')
        logging.debug('Application error: %s', e, exc_info=True)
    finally:
        logging.info('ScraperApp ended')

if __name__ == "__main__":  # FIXED: Changed **name** to __name__
    main()
