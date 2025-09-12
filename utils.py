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
