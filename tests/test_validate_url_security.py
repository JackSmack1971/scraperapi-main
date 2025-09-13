import os

os.environ.setdefault("SCRAPER_API_KEY", "test")

import scraper  # noqa: E402


def test_private_ip_rejected():
    assert not scraper.validate_url("http://192.168.1.1")


def test_localhost_rejected():
    assert not scraper.validate_url("http://localhost")


def test_unusual_port_rejected():
    assert not scraper.validate_url("http://example.com:8080")


def test_valid_url_allowed():
    assert scraper.validate_url("http://example.com")


def test_non_http_scheme_rejected():
    assert not scraper.validate_url("ftp://example.com")
    assert not scraper.validate_url("javascript:alert(1)")
    assert not scraper.validate_url("file:///etc/passwd")
