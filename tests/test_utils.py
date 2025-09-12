import os
import logging

os.environ.setdefault("SCRAPER_API_KEY", "test")

from utils import sanitize_url  # noqa: E402
import scraper  # noqa: E402


def test_sanitize_url_strips_control_chars():
    raw = "http://example.com/\nattack\r"
    assert sanitize_url(raw) == "http://example.com/attack"


def test_validate_url_logs_sanitized(caplog):
    bad = "http://example.com/\nattack"
    with caplog.at_level(logging.DEBUG):
        scraper.validate_url(bad)
    for record in caplog.records:
        assert "\n" not in record.getMessage()
        assert "\r" not in record.getMessage()
