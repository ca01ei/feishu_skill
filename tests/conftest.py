"""Shared pytest fixtures."""

import pytest


@pytest.fixture(autouse=True)
def isolate_user_token_sources(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """Prevent local machine user-token state from affecting test behavior."""
    monkeypatch.delenv("FEISHU_USER_ACCESS_TOKEN", raising=False)
    monkeypatch.setenv("FEISHU_TOKEN_FILE", str(tmp_path / "user_token.json"))
