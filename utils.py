import logging
import os
import sys
import platform
from logging.handlers import RotatingFileHandler
from pathlib import Path


def get_default_log_directory():
    """
    Get the appropriate default log directory based on the operating system.
    Returns a cross-platform compatible path.
    """
    system = platform.system().lower()
    
    if system == 'android' or (system == 'linux' and 'android' in platform.platform().lower()):
        # Android path (if running on Android)
        return '/storage/emulated/0/scraper_logs'
    elif system == 'windows':
        # Windows: Use AppData\Local
        appdata = os.getenv('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
        return os.path.join(appdata, 'ScraperApp', 'logs')
    elif system == 'darwin':  # macOS
        # macOS: Use ~/Library/Logs
        return os.path.expanduser('~/Library/Logs/ScraperApp')
    else:  # Linux and other Unix-like systems
        # Linux: Use ~/.local/share or /var/log if available
        if os.access('/var/log', os.W_OK):
            return '/var/log/scraperapp'
        else:
            return os.path.expanduser('~/.local/share/scraperapp/logs')


def ensure_directory_exists(directory_path):
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path (str): Path to the directory
        
    Returns:
        bool: True if directory exists or was created successfully, False otherwise
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except (OSError, PermissionError) as e:
        print(f"Warning: Could not create log directory {directory_path}: {e}")
        return False


def configure_logging(log_dir=None, log_level=None, max_bytes=5*1024*1024, backup_count=5, log_filename='scraper.log'):
    """
    Configure logging with both file and console output.
    
    Args:
        log_dir (str, optional): Directory for log files. If None, uses system-appropriate default.
        log_level (int, optional): Logging level. If None, uses INFO for production-like behavior.
        max_bytes (int): Maximum size of each log file before rotation (default: 5MB).
        backup_count (int): Number of backup files to keep (default: 5).
        log_filename (str): Name of the log file (default: 'scraper.log').
    
    Returns:
        str: Path to the log file, or None if file logging couldn't be set up.
    """
    # Prevent duplicate handler setup
    logger = logging.getLogger()
    if logger.handlers:
        # Clear existing handlers to avoid duplicates
        logger.handlers.clear()
    
    # Determine log level
    if log_level is None:
        # Check environment variable, default to INFO
        env_level = os.getenv('SCRAPER_LOG_LEVEL', 'INFO').upper()
        log_level = getattr(logging, env_level, logging.INFO)
    
    # Determine log directory
    if log_dir is None or not log_dir.strip():
        log_dir = os.getenv('SCRAPER_LOG_DIR')
        if not log_dir:
            log_dir = get_default_log_directory()
    
    # Ensure log directory exists
    log_filepath = None
    handlers = []
    
    if ensure_directory_exists(log_dir):
        try:
            log_filepath = os.path.join(log_dir, log_filename)
            
            # Create rotating file handler
            file_handler = RotatingFileHandler(
                log_filepath, 
                maxBytes=max_bytes, 
                backupCount=backup_count,
                encoding='utf-8'  # Ensure UTF-8 encoding for international characters
            )
            file_handler.setLevel(log_level)
            
            # Format for file output (more detailed)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            handlers.append(file_handler)
            
        except (OSError, PermissionError) as e:
            print(f"Warning: Could not set up file logging: {e}")
            print("Continuing with console logging only...")
    else:
        print("Warning: Could not create log directory. File logging disabled.")
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Format for console output (simpler, more readable)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        force=True  # Force reconfiguration even if already configured
    )
    
    # Test the logging setup
    logger = logging.getLogger(__name__)
    if log_filepath:
        logger.info(f"Logging configured successfully. File: {log_filepath}, Level: {logging.getLevelName(log_level)}")
    else:
        logger.info(f"Console logging configured. Level: {logging.getLevelName(log_level)}")
    
    return log_filepath


def set_log_level(level):
    """
    Change the logging level for all handlers.
    
    Args:
        level (int or str): New logging level (e.g., logging.DEBUG, 'DEBUG', 'INFO', etc.)
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    for handler in root_logger.handlers:
        handler.setLevel(level)
    
    logging.info(f"Log level changed to: {logging.getLevelName(level)}")


def get_logger(name=None):
    """
    Get a logger instance with the specified name.
    
    Args:
        name (str, optional): Logger name. If None, uses the calling module's name.
        
    Returns:
        logging.Logger: Logger instance
    """
    if name is None:
        # Get the caller's module name
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'scraper')
    
    return logging.getLogger(name)


# Utility function for quick setup with sensible defaults
def quick_setup(debug=False):
    """
    Quick logging setup with sensible defaults.
    
    Args:
        debug (bool): If True, sets log level to DEBUG. Otherwise, uses INFO.
        
    Returns:
        str: Path to log file or None if file logging unavailable
    """
    level = logging.DEBUG if debug else logging.INFO
    return configure_logging(log_level=level)


# Example usage and testing
if __name__ == "__main__":
    # Test the logging configuration
    print("Testing logging configuration...")
    
    # Test with default settings
    log_file = configure_logging()
    
    # Test logging at different levels
    logger = get_logger("test_module")
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    if log_file:
        print(f"\nLog file created at: {log_file}")
        print("Check the log file to verify file output is working.")
    else:
        print("\nFile logging is not available. Check console output above.")
