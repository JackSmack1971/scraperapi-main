import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ.setdefault("SCRAPER_API_KEY", "test")

import logging  # noqa: E402
import threading  # noqa: E402
from typing import Optional  # noqa: E402
import ui  # noqa: E402
from ui import ScraperApp  # noqa: E402


def test_generate_filename_sanitizes_domain(monkeypatch):
    app = ScraperApp()
    monkeypatch.setattr(ui.time, "strftime", lambda fmt: "20240101_120000")
    test_cases = {
        "https://example.com": "example_com",
        "https://sub.domain.com": "sub_domain_com",
        "https://exa*mple.com": "exa_mple_com",
        "https://example..com": "example__com",
    }
    for url, expected in test_cases.items():
        filename = app._generate_filename(url, 1, "txt")
        assert filename.startswith(f"{expected}_20240101_120000_001.txt")
        assert "." not in filename.split("_20240101")[0]


def test_generate_filename_blocks_path_chars(monkeypatch):
    app = ScraperApp()
    monkeypatch.setattr(ui.time, "strftime", lambda fmt: "20240101_120000")
    url = "https://evil.com/../bad"
    filename = app._generate_filename(url, 1, "txt")
    assert ".." not in filename
    assert "/" not in filename
    assert "\\" not in filename


def test_scrape_and_save_rejects_outside_path(monkeypatch, tmp_path):
    app = ScraperApp()
    app.update_progress = lambda *args, **kwargs: None
    with app.state_lock:
        app.is_scraping = True
    app.total_urls = 1
    app.completed_urls = 0
    app.failed_urls = []
    monkeypatch.setattr(ui, "get_default_output_directory", lambda: str(tmp_path))
    monkeypatch.setattr(
        app, "_generate_filename", lambda url, index, fmt: "../evil.txt"
    )
    monkeypatch.setattr(ui, "scrape_text_data", lambda url: "data")
    saved_paths = []
    monkeypatch.setattr(
        ui,
        "save_data_to_file",
        lambda data, path, fmt: saved_paths.append(path) or True,
    )
    app._scrape_and_save(["http://example.com"], "txt")
    assert saved_paths == []
    assert "http://example.com" in app.failed_urls


def test_on_stop_logs_when_thread_does_not_terminate(caplog):
    app = ScraperApp()

    class DummyThread(threading.Thread):
        def __init__(self):
            super().__init__()
            # mirror Thread.join timeout parameter for inspection
            self.join_timeout: Optional[float] = None

        def join(self, timeout: Optional[float] = None) -> None:
            self.join_timeout = timeout

        def is_alive(self) -> bool:
            return True

    app.scraping_thread = DummyThread()
    with app.state_lock:
        app.is_scraping = True

    with caplog.at_level(logging.INFO):
        app.on_stop()

    assert app.stop_event.is_set()
    assert app.scraping_thread.join_timeout == 30
    assert any("failed to terminate" in record.message for record in caplog.records)
