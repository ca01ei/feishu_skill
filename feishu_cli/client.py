"""Feishu API client initialization."""

import lark_oapi as lark
from feishu_cli.config import load_config


def create_client() -> lark.Client:
    """Create and return a configured Feishu API client."""
    config = load_config()
    return (
        lark.Client.builder()
        .app_id(config.app_id)
        .app_secret(config.app_secret)
        .build()
    )
