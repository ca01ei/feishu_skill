"""Configuration management for Feishu CLI."""

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


class ConfigError(Exception):
    """Raised when configuration is invalid."""
    pass


@dataclass(frozen=True)
class FeishuConfig:
    """Immutable Feishu configuration."""
    app_id: str
    app_secret: str


def load_config() -> FeishuConfig:
    """Load config from environment variables, falling back to .env file."""
    project_root = Path(__file__).parent.parent
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=False)

    app_id = os.environ.get("FEISHU_APP_ID")
    app_secret = os.environ.get("FEISHU_APP_SECRET")

    if not app_id:
        raise ConfigError(
            "FEISHU_APP_ID not set. "
            "Set it as an environment variable or in .env file."
        )
    if not app_secret:
        raise ConfigError(
            "FEISHU_APP_SECRET not set. "
            "Set it as an environment variable or in .env file."
        )

    return FeishuConfig(app_id=app_id, app_secret=app_secret)
