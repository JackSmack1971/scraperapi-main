import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ.setdefault("SCRAPER_API_KEY", "test")

import scraper  # noqa: E402


def test_scrape_multiple_urls_skips_invalid(monkeypatch):
    called = []

    def fake_scrape_text_data(url):
        called.append(url)
        return f"data for {url}"

    monkeypatch.setattr(scraper, "scrape_text_data", fake_scrape_text_data)
    urls = ["http://example.com", "http://localhost"]
    results = scraper.scrape_multiple_urls(urls, max_workers=1)
    assert called == ["http://example.com"]
    assert len(results) == 1
