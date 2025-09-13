import os
import sys
import types

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
)
os.environ.setdefault("SCRAPER_API_KEY", "test")

import scraper  # noqa: E402


class DummyResponse:
    def __init__(self):
        self.text = "ok"
        self.content = b"ok"

    def raise_for_status(self):
        pass


def test_fetch_url_uses_default_headers(monkeypatch):
    captured = {}

    def mock_get(url, headers=None, timeout=None):
        captured.update(headers)
        return DummyResponse()

    monkeypatch.setattr(
        scraper,
        "session",
        types.SimpleNamespace(get=mock_get),
    )

    result = scraper.fetch_url("http://example.com")
    assert result == "ok"
    assert captured["DNT"] == "1"
    assert captured["Connection"] == "close"
    assert "User-Agent" in captured


def test_fetch_url_allows_custom_headers(monkeypatch):
    captured = {}

    def mock_get(url, headers=None, timeout=None):
        captured.update(headers)
        return DummyResponse()

    monkeypatch.setattr(
        scraper,
        "session",
        types.SimpleNamespace(get=mock_get),
    )

    custom = {"X-Test": "1", "User-Agent": "custom"}
    scraper.fetch_url("http://example.com", headers=custom)
    assert captured["X-Test"] == "1"
    assert captured["User-Agent"] == "custom"


def test_fetch_url_uses_env_timeout(monkeypatch):
    monkeypatch.setenv("SCRAPER_TIMEOUT", "1")
    import importlib

    importlib.reload(scraper)
    captured = {}

    def mock_get(url, headers=None, timeout=None):
        captured["timeout"] = timeout
        return DummyResponse()

    monkeypatch.setattr(
        scraper,
        "session",
        types.SimpleNamespace(get=mock_get),
    )

    scraper.fetch_url("http://example.com")
    assert captured["timeout"] == 1

    monkeypatch.delenv("SCRAPER_TIMEOUT", raising=False)
    importlib.reload(scraper)
