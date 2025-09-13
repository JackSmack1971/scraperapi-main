import os
import logging
import stat

os.environ.setdefault("SCRAPER_API_KEY", "test")
os.environ.setdefault("SCRAPER_LOG_DIR", "/tmp/scraper_logs")

from utils import sanitize_url, configure_logging  # noqa: E402
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


def test_configure_logging_sets_strict_permissions(tmp_path, monkeypatch):
    monkeypatch.setenv("SCRAPER_ENV", "development")
    log_path = configure_logging(log_dir=str(tmp_path))
    assert log_path is not None
    mode = stat.S_IMODE(os.stat(log_path).st_mode)
    assert mode == 0o600
