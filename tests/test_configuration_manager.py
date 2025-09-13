import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ.setdefault("SCRAPER_API_KEY", "test")
os.environ.setdefault("KIVY_WINDOW", "mock")

import logging
import ui  # noqa: E402


def test_get_config_directory_creates_secure_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(
        ui, "get_default_output_directory", lambda: str(tmp_path / "out")
    )
    manager = ui.ConfigurationManager.__new__(ui.ConfigurationManager)
    manager.logger = logging.getLogger("test")
    manager.config = dict(ui.ConfigurationManager.default_config)
    manager._config_dir = manager._get_config_directory()
    config_dir = Path(manager._config_dir)
    assert config_dir.exists()
    assert config_dir.parent == tmp_path


def test_save_template_sanitizes_name(monkeypatch, tmp_path):
    monkeypatch.setattr(
        ui, "get_default_output_directory", lambda: str(tmp_path / "out")
    )
    manager = ui.ConfigurationManager.__new__(ui.ConfigurationManager)
    manager.logger = logging.getLogger("test")
    manager.config = dict(ui.ConfigurationManager.default_config)
    manager._config_dir = manager._get_config_directory()
    assert manager._save_template("bad*name")
    path = tmp_path / "config_templates" / "bad_name.json"
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["name"] == "bad_name"
    assert data["config"] == manager.config


def test_validate_config_rejects_invalid():
    manager = ui.ConfigurationManager.__new__(ui.ConfigurationManager)
    manager.logger = logging.getLogger("test")
    manager.config = dict(ui.ConfigurationManager.default_config)
    bad = dict(manager.config)
    bad["concurrent_workers"] = 0
    with pytest.raises(ValueError):
        manager._validate_config(bad)
    bad["output_format"] = "pdf"
    with pytest.raises(ValueError):
        manager._validate_config(bad)
