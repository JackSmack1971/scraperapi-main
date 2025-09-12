import os
import re
import platform
from pathlib import Path
from urllib.parse import urlparse
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
from kivy.clock import Clock, mainthread
from kivy.utils import platform as kivy_platform
import threading
import logging
import time
from scraper import scrape_text_data, save_data_to_file, scrape_multiple_urls, validate_url
from utils import configure_logging, get_logger


def get_default_output_directory():
    """Get the appropriate output directory based on the operating system."""
    system_name = platform.system().lower()
    
    if kivy_platform == 'android' or (system_name == 'linux' and 'android' in platform.platform().lower()):
        # Android path
        return '/storage/emulated/0/ScraperApp/scraped_data'
    elif system_name == 'windows':
        # Windows: Documents folder
        documents = os.path.join(os.path.expanduser('~'), 'Documents')
        return os.path.join(documents, 'ScraperApp', 'scraped_data')
    elif system_name == 'darwin':  # macOS
        # macOS: Documents folder
        return os.path.expanduser('~/Documents/ScraperApp/scraped_data')
    else:  # Linux and other Unix-like systems
        # Linux: Home directory
        return os.path.expanduser('~/ScraperApp/scraped_data')


class ScraperApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = get_logger(__name__)
        self.format_var = 'txt'
        self.scraping_thread = None
        self.is_scraping = False
        self.total_urls = 0
        self.completed_urls = 0
        self.failed_urls = []
        
    def build(self):
        # Configure logging once at app start
        configure_logging()
        self.logger.info("ScraperApp initialized")
        
        anchor_layout = AnchorLayout()
        layout = BoxLayout(
            orientation='vertical', 
            padding=10, 
            spacing=10, 
            size_hint=(0.9, 0.9)  # Increased from 0.8 for better screen usage
        )
        
        # Header with better styling
        header = Label(
            text='Web Scraper Pro', 
            font_size=28, 
            size_hint_y=None, 
            height=60,
            color=(0.2, 0.6, 1, 1)  # Nice blue color
        )
        layout.add_widget(header)

        # Improved description with word wrapping
        description = Label(
            text='Enter URLs separated by commas or new lines. Select output format and start scraping.',
            font_size=16, 
            size_hint_y=None, 
            height=80,
            text_size=(None, None),  # Will be set in bind
            halign='center',
            valign='middle'
        )
        description.bind(size=self._update_text_size)
        layout.add_widget(description)

        # Improved URL input with better placeholder
        self.url_entry = TextInput(
            hint_text='Enter URLs (separated by commas or new lines)\nExample: https://example.com, https://another-site.com',
            multiline=True, 
            font_size=14, 
            size_hint_y=None, 
            height=120
        )
        layout.add_widget(self.url_entry)

        # Format selection
        layout.add_widget(self._create_format_selection())

        # Action buttons
        button_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        self.start_button = Button(text='Start Scraping', size_hint=(0.7, 1))
        self.start_button.bind(on_press=self.start_scraping)
        button_layout.add_widget(self.start_button)
        
        self.stop_button = Button(text='Stop', size_hint=(0.3, 1), disabled=True)
        self.stop_button.bind(on_press=self.stop_scraping)
        button_layout.add_widget(self.stop_button)
        
        layout.add_widget(button_layout)

        # Progress indicators
        progress_layout = BoxLayout(size_hint_y=None, height=60, spacing=5, orientation='vertical')
        
        self.progress_bar = ProgressBar(max=100, size_hint_y=None, height=20)
        progress_layout.add_widget(self.progress_bar)

        self.progress_label = Label(
            text='Ready to start scraping...', 
            font_size=14, 
            size_hint_y=None, 
            height=40
        )
        progress_layout.add_widget(self.progress_label)
        
        layout.add_widget(progress_layout)

        # Log output with improved styling
        log_label = Label(text='Activity Log:', size_hint_y=None, height=30, halign='left')
        log_label.bind(size=self._update_text_size)
        layout.add_widget(log_label)
        
        self.log_output = TextInput(
            readonly=True, 
            multiline=True,
            font_size=12,
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(0.9, 0.9, 0.9, 1)
        )
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.log_output)
        layout.add_widget(scroll_view)

        # Footer
        layout.add_widget(self._create_footer())

        anchor_layout.add_widget(layout)
        return anchor_layout

    def _create_format_selection(self):
        """Create format selection UI with improved layout."""
        format_layout = BoxLayout(size_hint_y=None, height=50, spacing=20)
        
        format_label = Label(text='Output Format:', size_hint_x=None, width=120)
        format_layout.add_widget(format_label)

        # TXT option
        txt_layout = BoxLayout(orientation='horizontal', size_hint_x=None, width=80, spacing=5)
        txt_checkbox = CheckBox(group='format', active=True, size_hint_x=None, width=30)
        txt_checkbox.bind(active=self.set_format_txt)
        txt_layout.add_widget(txt_checkbox)
        txt_layout.add_widget(Label(text='TXT', font_size=16, size_hint_x=None, width=50))
        format_layout.add_widget(txt_layout)

        # MD option
        md_layout = BoxLayout(orientation='horizontal', size_hint_x=None, width=80, spacing=5)
        md_checkbox = CheckBox(group='format', size_hint_x=None, width=30)
        md_checkbox.bind(active=self.set_format_md)
        md_layout.add_widget(md_checkbox)
        md_layout.add_widget(Label(text='MD', font_size=16, size_hint_x=None, width=50))
        format_layout.add_widget(md_layout)

        return format_layout

    def _create_footer(self):
        """Create footer with improved styling."""
        footer_layout = BoxLayout(size_hint_y=None, height=60, padding=[10, 5, 10, 5], spacing=10)
        
        help_button = Button(
            text='Help', 
            size_hint=(0.2, 1), 
            background_color=(0.3, 0.7, 0.3, 1)
        )
        help_button.bind(on_press=self.show_help)
        footer_layout.add_widget(help_button)
        
        settings_button = Button(
            text='Settings', 
            size_hint=(0.2, 1),
            background_color=(0.7, 0.7, 0.3, 1)
        )
        settings_button.bind(on_press=self.show_settings)
        footer_layout.add_widget(settings_button)
        
        footer_label = Label(
            text='© 2024 ARTOfficial Intelligence LLC\nCross-Platform Web Scraper', 
            size_hint=(0.6, 1), 
            halign='center', 
            valign='middle', 
            font_size=12
        )
        footer_label.bind(size=self._update_text_size)
        footer_layout.add_widget(footer_label)
        
        return footer_layout

    def _update_text_size(self, instance, value):
        """Update text size for proper word wrapping."""
        instance.text_size = (instance.width, None)

    def show_help(self, instance):
        """Show help dialog with comprehensive information."""
        help_text = """WEB SCRAPER PRO - HELP

How to use:
1. Enter URLs in the text field (one per line or comma-separated)
2. Choose output format (TXT or Markdown)
3. Click 'Start Scraping' to begin
4. Monitor progress in the activity log

Supported URLs:
• Must start with http:// or https://
• Examples: https://example.com, http://news.site.com

Output Location:
• Files are saved to your Documents/ScraperApp folder
• Each URL gets a separate file with timestamps
• Failed URLs are logged for retry

Tips:
• Use STOP button to cancel ongoing scraping
• Check activity log for detailed information
• Large pages may take longer to process"""

        content = Label(
            text=help_text,
            text_size=(400, None),
            halign='left',
            valign='top',
            font_size=14
        )
        content.bind(size=self._update_text_size)
        
        popup = Popup(
            title='Help - Web Scraper Pro', 
            content=content, 
            size_hint=(0.9, 0.8)
        )
        popup.open()

    def show_settings(self, instance):
        """Show settings dialog."""
        settings_text = f"""CURRENT SETTINGS

Output Directory:
{get_default_output_directory()}

Platform: {platform.system()}
Python Version: {platform.python_version()}

Logging:
Level: {logging.getLevelName(self.logger.level)}
File: Check logs directory for details

To modify settings:
• Edit environment variables
• Check utils.py for configuration options"""

        content = Label(
            text=settings_text,
            text_size=(400, None),
            halign='left',
            valign='top',
            font_size=14
        )
        content.bind(size=self._update_text_size)
        
        popup = Popup(
            title='Settings', 
            content=content, 
            size_hint=(0.8, 0.6)
        )
        popup.open()

    def set_format_txt(self, checkbox, value):
        """Set format to TXT."""
        if value:
            self.format_var = "txt"
            self.logger.debug('Format set to TXT')

    def set_format_md(self, checkbox, value):
        """Set format to Markdown."""
        if value:
            self.format_var = "md"
            self.logger.debug('Format set to MD')

    @mainthread
    def update_progress(self, message, progress=None):
        """Thread-safe progress update using @mainthread decorator."""
        self.progress_label.text = message
        timestamp = time.strftime("%H:%M:%S")
        self.log_output.text += f"[{timestamp}] {message}\n"
        
        # Auto-scroll to bottom
        self.log_output.cursor = (len(self.log_output.text), 0)
        
        if progress is not None:
            self.progress_bar.value = progress
        
        self.logger.info(message)

    @mainthread  
    def update_ui_state(self, is_scraping):
        """Thread-safe UI state update."""
        self.start_button.disabled = is_scraping
        self.stop_button.disabled = not is_scraping
        self.is_scraping = is_scraping

    def start_scraping(self, instance):
        """Start the scraping process with improved validation."""
        if self.is_scraping:
            self.logger.warning("Scraping already in progress")
            return

        self.logger.info('Start Scraping button pressed')
        
        # Parse and validate URLs
        url_text = self.url_entry.text.strip()
        if not url_text:
            self._show_error_popup('Input Error', 'Please enter at least one URL.')
            return

        # Support both comma and newline separation
        urls = []
        for url in re.split(r'[,\n]+', url_text):
            url = url.strip()
            if url:
                urls.append(url)

        if not urls:
            self._show_error_popup('Input Error', 'No valid URLs found.')
            return

        # Validate URLs
        valid_urls = []
        invalid_urls = []
        
        for url in urls:
            if validate_url(url):
                valid_urls.append(url)
            else:
                invalid_urls.append(url)

        if invalid_urls:
            invalid_list = '\n'.join(invalid_urls[:5])  # Show first 5
            if len(invalid_urls) > 5:
                invalid_list += f'\n... and {len(invalid_urls) - 5} more'
            
            self._show_error_popup(
                'Invalid URLs Found', 
                f'The following URLs are invalid and will be skipped:\n\n{invalid_list}'
            )

        if not valid_urls:
            self._show_error_popup('No Valid URLs', 'All URLs are invalid. Please check the format.')
            return

        # Initialize progress tracking
        self.total_urls = len(valid_urls)
        self.completed_urls = 0
        self.failed_urls = []

        # Update UI and start scraping
        self.update_ui_state(True)
        self.update_progress(f'Starting to scrape {len(valid_urls)} URLs...', 0)
        
        self.logger.info(f'Starting scraping thread for {len(valid_urls)} URLs')
        self.scraping_thread = threading.Thread(
            target=self._scrape_and_save, 
            args=(valid_urls, self.format_var),
            daemon=True  # Daemon thread will exit when main thread exits
        )
        self.scraping_thread.start()

    def stop_scraping(self, instance):
        """Stop the scraping process."""
        if not self.is_scraping:
            return
            
        self.logger.info('Stop requested by user')
        self.update_progress('Stopping scraping process...', None)
        
        # Note: This is a soft stop - we can't forcefully kill threads in Python
        # The thread will complete the current URL and then check if it should continue
        self.is_scraping = False
        self.update_ui_state(False)

    def _show_error_popup(self, title, message):
        """Show error popup with improved styling."""
        content = Label(
            text=message,
            text_size=(350, None),
            halign='center',
            valign='middle'
        )
        content.bind(size=self._update_text_size)
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        popup.open()

    def _generate_filename(self, url, index, file_format):
        """Generate a safe filename from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            
            # Create safe filename
            safe_domain = re.sub(r'[^\w\-_.]', '_', domain)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_domain}_{timestamp}_{index:03d}.{file_format}"
            
            return filename
        except Exception as e:
            self.logger.error(f"Error generating filename for {url}: {e}")
            # Fallback filename
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            return f"scraped_{timestamp}_{index:03d}.{file_format}"

    def _scrape_and_save(self, urls, file_format):
        """Scrape URLs and save data (runs in background thread)."""
        self.logger.info('Background scraping thread started')
        
        try:
            # Ensure output directory exists
            base_directory = get_default_output_directory()
            Path(base_directory).mkdir(parents=True, exist_ok=True)
            
            self.update_progress(f'Created output directory: {base_directory}')

            for index, url in enumerate(urls):
                # Check if we should stop
                if not self.is_scraping:
                    self.update_progress('Scraping stopped by user.', None)
                    break

                progress = ((index + 1) / self.total_urls) * 100
                self.update_progress(f'Scraping URL {index + 1}/{self.total_urls}: {url[:50]}...', progress)
                
                try:
                    # Scrape the URL
                    scraped_data = scrape_text_data(url)
                    
                    if scraped_data and scraped_data.strip():
                        # Generate filename
                        filename = self._generate_filename(url, index + 1, file_format)
                        file_path = os.path.join(base_directory, filename)
                        
                        # Save data
                        if save_data_to_file(scraped_data, file_path, file_format):
                            self.completed_urls += 1
                            self.update_progress(f'✓ Saved: {filename} ({len(scraped_data)} chars)', progress)
                        else:
                            self.failed_urls.append(url)
                            self.update_progress(f'✗ Failed to save data for: {url}', progress)
                    else:
                        self.failed_urls.append(url)
                        self.update_progress(f'✗ No data found at: {url}', progress)
                        
                except Exception as e:
                    self.failed_urls.append(url)
                    self.logger.error(f'Error scraping {url}: {e}')
                    self.update_progress(f'✗ Error scraping {url}: {str(e)[:50]}...', progress)
                
                # Small delay to prevent overwhelming servers
                time.sleep(1)

            # Final summary
            success_count = self.completed_urls
            failed_count = len(self.failed_urls)
            
            summary_message = f'Scraping completed! ✓ {success_count} successful, ✗ {failed_count} failed'
            if failed_count > 0:
                summary_message += f'\nFailed URLs: {", ".join(self.failed_urls[:3])}'
                if failed_count > 3:
                    summary_message += f'... and {failed_count - 3} more'
            
            summary_message += f'\nFiles saved to: {base_directory}'
            
            self.update_progress(summary_message, 100)
            
        except Exception as e:
            self.logger.error(f'Critical error in scraping thread: {e}')
            self.update_progress(f'Critical error: {str(e)}', None)
        
        finally:
            # Reset UI state
            self.update_ui_state(False)
            self.logger.info('Background scraping thread completed')

    def on_stop(self):
        """Called when the app is about to close."""
        self.logger.info('App stopping')
        if self.is_scraping and self.scraping_thread:
            self.logger.info('Stopping scraping thread')
            self.is_scraping = False
            # Give thread a moment to finish gracefully
            if self.scraping_thread.is_alive():
                self.scraping_thread.join(timeout=2)
        return True


if __name__ == '__main__':
    try:
        app = ScraperApp()
        app.run()
    except Exception as e:
        # Fallback logging if app fails to start
        print(f"Failed to start ScraperApp: {e}")
        logging.error(f"Failed to start ScraperApp: {e}")
        raise
