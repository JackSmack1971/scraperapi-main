import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

os.environ.setdefault("SCRAPER_API_KEY", "test")

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


def test_scrape_and_save_rejects_outside_path(monkeypatch, tmp_path):
    app = ScraperApp()
    app.update_progress = lambda *args, **kwargs: None
    app.is_scraping = True
    app.total_urls = 1
    app.completed_urls = 0
    app.failed_urls = []
    monkeypatch.setattr(
        ui, "get_default_output_directory", lambda: str(tmp_path)
    )
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
