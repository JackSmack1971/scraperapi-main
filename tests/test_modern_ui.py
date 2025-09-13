import os
import sys

os.environ.setdefault("KIVY_WINDOW", "mock")
os.environ.setdefault("KIVY_NO_ARGS", "1")
os.environ.setdefault("SCRAPER_API_KEY", "test")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kivy.base import EventLoop

from ui import ModernScraperApp, EnhancedURLInput, ConfigurationManager
from progress_tracker import ScrapingProgressTracker

EventLoop.ensure_window = lambda *args, **kwargs: None
EventLoop.window = type("_W", (), {"dpi": 96})()

def test_app_initializes_with_dependencies():
    app = ModernScraperApp()
    assert app.url_input_cls is EnhancedURLInput
    assert app.progress_cls is ScrapingProgressTracker
    assert app.config_cls is ConfigurationManager


def test_state_thread_safety():
    app = ModernScraperApp()
    with app.state_lock:
        app.app_state["value"] = 42
    assert app.app_state["value"] == 42
