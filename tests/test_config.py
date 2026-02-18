from pathlib import Path
import pytest
from feishu_cli.config import load_config, ConfigError


def test_load_config_from_env(monkeypatch):
    monkeypatch.setenv("FEISHU_APP_ID", "test_id")
    monkeypatch.setenv("FEISHU_APP_SECRET", "test_secret")
    config = load_config()
    assert config.app_id == "test_id"
    assert config.app_secret == "test_secret"


def test_load_config_missing_raises(monkeypatch):
    original_exists = Path.exists

    def _fake_exists(path_obj):
        if str(path_obj).endswith("/.env"):
            return False
        return original_exists(path_obj)

    monkeypatch.setattr("feishu_cli.config.Path.exists", _fake_exists)
    monkeypatch.delenv("FEISHU_APP_ID", raising=False)
    monkeypatch.delenv("FEISHU_APP_SECRET", raising=False)
    with pytest.raises(ConfigError, match="FEISHU_APP_ID"):
        load_config()
