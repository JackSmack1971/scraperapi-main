import json
import os
import platform
import re
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.textinput import TextInput
from kivy.utils import platform as kivy_platform

from progress_tracker import ScrapingProgressTracker
from scraper import validate_url
from utils import configure_logging, get_logger


def get_default_output_directory():
    """Get the appropriate output directory based on the operating system."""
    system_name = platform.system().lower()

    if kivy_platform == "android" or (
        system_name == "linux" and "android" in platform.platform().lower()
    ):
        # Android path
        return "/storage/emulated/0/ScraperApp/scraped_data"
    elif system_name == "windows":
        # Windows: Documents folder
        documents = os.path.join(os.path.expanduser("~"), "Documents")
        return os.path.join(documents, "ScraperApp", "scraped_data")
    elif system_name == "darwin":  # macOS
        # macOS: Documents folder
        return os.path.expanduser("~/Documents/ScraperApp/scraped_data")
    else:  # Linux and other Unix-like systems
        # Linux: Home directory
        return os.path.expanduser("~/ScraperApp/scraped_data")


class EnhancedURLInput(BoxLayout):
    """Widget for URL entry with validation and optional file import."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(orientation="vertical", **kwargs)
        self.logger = get_logger(__name__)

        self.text_input = TextInput(
            hint_text=(
                "Enter URLs (separated by commas or new lines)\n"
                "Example: https://example.com, https://another-site.com"
            ),
            multiline=True,
            font_size=14,
            size_hint_y=None,
            height=120,
        )
        self.add_widget(self.text_input)

        status_layout = BoxLayout(size_hint_y=None, height=30, spacing=5)
        self.status_label = Label(text="Enter URLs...", size_hint_x=0.7)
        import_button = Button(text="Import URLs", size_hint_x=0.3)
        import_button.bind(on_press=self._open_file_chooser)  # type: ignore
        status_layout.add_widget(self.status_label)
        status_layout.add_widget(import_button)
        self.add_widget(status_layout)

        self.valid_urls: List[str] = []
        self.invalid_urls: List[str] = []
        self._validation_event = None
        self.text_input.bind(text=self._on_text_change)

    def _on_text_change(self, *_: Any) -> None:
        if self._validation_event:
            self._validation_event.cancel()
        # Debounce validation to avoid excessive processing
        self._validation_event = Clock.schedule_once(self._validate_urls, 0.5)

    def _validate_urls(self, *_: Any) -> None:
        raw_text = self.text_input.text.strip()
        urls = [u.strip() for u in re.split(r"[,\n]+", raw_text) if u.strip()]
        self.valid_urls = []
        self.invalid_urls = []
        for url in urls:
            if validate_url(url):
                self.valid_urls.append(url)
            else:
                self.invalid_urls.append(url)
        if not urls:
            self.status_label.text = "Enter URLs..."
        else:
            self.status_label.text = (
                f"{len(self.valid_urls)} valid / {len(self.invalid_urls)} invalid"
            )

    def _open_file_chooser(self, _instance: Button) -> None:
        chooser = FileChooserListView()
        popup = Popup(title="Select URL file", content=chooser, size_hint=(0.9, 0.9))
        chooser.bind(
            on_submit=lambda inst, selection, touch: self._file_chosen(popup, selection)
        )
        popup.open()

    def _file_chosen(self, popup: Popup, selection: List[str]) -> None:
        popup.dismiss()
        if selection:
            self._load_file(selection[0])

    def _load_file(self, file_path: str) -> None:
        try:
            path = Path(file_path).expanduser().resolve()
            if not path.is_file() or path.stat().st_size > 1_000_000:
                raise ValueError("Invalid file")
            # Security: read file safely with explicit encoding
            content = path.read_text(encoding="utf-8")
        except Exception as exc:  # Security: broad catch to avoid leaking errors
            self.logger.error("Failed to import URLs: %s", exc)
            self.status_label.text = "File load failed"
            return
        if self.text_input.text:
            self.text_input.text += "\n"
        self.text_input.text += content
        self._validate_urls()

    def get_valid_urls(self) -> List[str]:
        """Return currently valid URLs."""
        self._validate_urls()
        return list(self.valid_urls)


class ConfigurationManager(BoxLayout):
    """Manage configuration settings and templates."""

    default_config: Dict[str, Any] = {
        "output_format": "txt",  # Validated: 'txt' or 'md'
        "concurrent_workers": 3,  # Range: 1-10
        "request_timeout": 10,  # Seconds: 1-60
        "retry_attempts": 3,  # Range: 1-10
        "auto_scroll_log": True,  # Boolean
        "filename_template": "{domain}_{timestamp}_{index}",  # String template
        "create_subdirectories": False,  # Boolean
    }

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(orientation="vertical", **kwargs)
        self.logger = get_logger(__name__)
        self.config: Dict[str, Any] = dict(self.default_config)
        self._config_dir = self._get_config_directory()

        # Simple button to open settings dialog
        settings_btn = Button(text="Settings", size_hint=(1, None), height=40)
        settings_btn.bind(on_press=lambda *_: self.open_settings())  # type: ignore
        self.add_widget(settings_btn)

    def _get_config_directory(self) -> str:
        """Return path to configuration directory, creating it securely."""
        base = Path(get_default_output_directory()).expanduser()
        config_dir = base.parent / "config_templates"
        try:
            # Security: restrict permissions to user-only where supported
            config_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        except Exception as exc:  # Broad catch to avoid leaking details
            self.logger.error("Failed to create config directory: %s", exc)
        return str(config_dir)

    def _sanitize_name(self, name: str) -> str:
        return re.sub(r"[^A-Za-z0-9_-]", "_", name)

    def _validate_config(self, config: Dict[str, Any]) -> None:
        if config.get("output_format") not in {"txt", "md"}:
            raise ValueError("Invalid output_format")
        workers = int(config.get("concurrent_workers", 0))
        if not 1 <= workers <= 10:
            raise ValueError("concurrent_workers out of range")
        timeout = int(config.get("request_timeout", 0))
        if not 1 <= timeout <= 60:
            raise ValueError("request_timeout out of range")
        retries = int(config.get("retry_attempts", 0))
        if not 1 <= retries <= 10:
            raise ValueError("retry_attempts out of range")
        if not isinstance(config.get("auto_scroll_log"), bool):
            raise ValueError("auto_scroll_log must be boolean")
        if not isinstance(config.get("filename_template"), str):
            raise ValueError("filename_template must be string")
        if not isinstance(config.get("create_subdirectories"), bool):
            raise ValueError("create_subdirectories must be boolean")

    def _save_template(self, name: str) -> bool:
        """Persist current config as JSON template."""
        safe_name = self._sanitize_name(name)
        if not safe_name:
            self.logger.error("Invalid template name")
            return False
        data = {
            "name": safe_name,
            "created": datetime.utcnow().isoformat() + "Z",
            "config": self.config,
        }
        try:
            path = Path(self._config_dir) / f"{safe_name}.json"
            with path.open("w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
            return True
        except Exception as exc:
            self.logger.error("Failed to save template: %s", exc)
            return False

    def open_settings(self) -> None:
        panel = TabbedPanel(do_default_tab=False)

        # General tab
        general_box = BoxLayout(orientation="vertical", padding=10, spacing=10)
        self.output_format_input = TextInput(text=self.config["output_format"])
        general_box.add_widget(Label(text="Output Format (txt/md)"))
        general_box.add_widget(self.output_format_input)

        self.auto_scroll_checkbox = CheckBox(active=self.config["auto_scroll_log"])
        auto_layout = BoxLayout(size_hint_y=None, height=30)
        auto_layout.add_widget(Label(text="Auto scroll log", size_hint_x=0.7))
        auto_layout.add_widget(self.auto_scroll_checkbox)
        general_box.add_widget(auto_layout)

        self.template_input = TextInput(text=self.config["filename_template"])
        general_box.add_widget(Label(text="Filename template"))
        general_box.add_widget(self.template_input)

        general_tab = TabbedPanelItem(text="General")
        general_tab.content = general_box
        panel.add_widget(general_tab)

        # Advanced tab
        advanced_box = BoxLayout(orientation="vertical", padding=10, spacing=10)
        self.workers_input = TextInput(
            text=str(self.config["concurrent_workers"]), input_filter="int"
        )
        advanced_box.add_widget(Label(text="Concurrent workers"))
        advanced_box.add_widget(self.workers_input)

        self.timeout_input = TextInput(
            text=str(self.config["request_timeout"]), input_filter="int"
        )
        advanced_box.add_widget(Label(text="Request timeout (s)"))
        advanced_box.add_widget(self.timeout_input)

        self.retry_input = TextInput(
            text=str(self.config["retry_attempts"]), input_filter="int"
        )
        advanced_box.add_widget(Label(text="Retry attempts"))
        advanced_box.add_widget(self.retry_input)

        self.subdir_checkbox = CheckBox(
            active=self.config["create_subdirectories"], size_hint_x=None
        )
        subdir_layout = BoxLayout(size_hint_y=None, height=30)
        subdir_layout.add_widget(Label(text="Create subdirectories", size_hint_x=0.7))
        subdir_layout.add_widget(self.subdir_checkbox)
        advanced_box.add_widget(subdir_layout)

        advanced_tab = TabbedPanelItem(text="Advanced")
        advanced_tab.content = advanced_box
        panel.add_widget(advanced_tab)

        # Root layout with save button
        root = BoxLayout(orientation="vertical")
        root.add_widget(panel)
        save_btn = Button(text="Apply", size_hint_y=None, height=40)
        root.add_widget(save_btn)
        popup = Popup(title="Advanced Settings", content=root, size_hint=(0.9, 0.9))
        save_btn.bind(on_press=lambda *_: self._apply_settings(popup))  # type: ignore
        popup.open()

    def _apply_settings(self, popup: Popup) -> None:
        new_config = {
            "output_format": self.output_format_input.text.strip(),
            "concurrent_workers": int(self.workers_input.text or 0),
            "request_timeout": int(self.timeout_input.text or 0),
            "retry_attempts": int(self.retry_input.text or 0),
            "auto_scroll_log": bool(self.auto_scroll_checkbox.active),
            "filename_template": self.template_input.text.strip(),
            "create_subdirectories": bool(self.subdir_checkbox.active),
        }
        try:
            self._validate_config(new_config)
        except ValueError as exc:
            self.logger.error("Invalid configuration: %s", exc)
            return
        self.config.update(new_config)
        self._save_template("autosave")
        popup.dismiss()


class ModernScraperApp(App):
    """Tabbed UI for web scraping with shared state."""

    def __init__(
        self,
        url_input_cls: Any = EnhancedURLInput,
        progress_cls: Any = ScrapingProgressTracker,
        config_cls: Any = ConfigurationManager,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.logger = get_logger(__name__)
        # Store widget classes for deferred instantiation
        self.url_input_cls = url_input_cls
        self.progress_cls = progress_cls
        self.config_cls = config_cls
        self.url_input = None
        self.progress_tracker = None
        self.config_manager = None
        self.help_label = None
        # Centralized state guarded by a lock for thread safety
        self.app_state: Dict[str, Any] = {}
        self.state_lock = threading.Lock()

    def build(self) -> TabbedPanel:
        configure_logging()
        # Instantiate widgets only when building the UI to avoid early Window access
        self.url_input = self.url_input_cls()
        self.progress_tracker = self.progress_cls()
        self.config_manager = self.config_cls()
        self.help_label = Label(
            text=(
                "Use the tabs to configure settings, start scraping, "
                "monitor progress, and view help information."
            )
        )
        with self.state_lock:
            # Initialize shared state in a thread-safe manner
            self.app_state.update({"is_scraping": False, "urls": []})
        panel = TabbedPanel(do_default_tab=False)
        scrape_tab = TabbedPanelItem(text="Scrape")
        scrape_tab.content = self.url_input
        progress_tab = TabbedPanelItem(text="Progress")
        progress_tab.content = self.progress_tracker
        config_tab = TabbedPanelItem(text="Configuration")
        config_tab.content = self.config_manager
        help_tab = TabbedPanelItem(text="Help")
        help_tab.content = self.help_label
        for item in (scrape_tab, progress_tab, config_tab, help_tab):
            panel.add_widget(item)
        return panel

    def start_scraping(self) -> None:
        """Validate URLs and start tracking."""
        urls = [u for u in self.url_input.get_valid_urls() if validate_url(u)]
        with self.state_lock:
            self.app_state["urls"] = urls
            self.app_state["is_scraping"] = True
        for url in urls:
            self.progress_tracker.add_url(url)
        # Real scraping would be initiated here.

    def stop_scraping(self) -> None:
        """Signal that scraping should stop."""
        with self.state_lock:
            self.app_state["is_scraping"] = False
