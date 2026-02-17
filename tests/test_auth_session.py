"""Tests for user token session helpers."""
from typing import Optional

from unittest.mock import MagicMock

import feishu_cli.auth.session as session_mod
from feishu_cli.auth.session import (
    UserTokenSession,
    clear_user_token_session,
    load_user_token_session,
    resolve_user_request_option,
    save_user_token_session,
)


def _session(
    access_token: str = "access-token",
    refresh_token: str = "refresh-token",
    expires_at: Optional[int] = None,
    refresh_expires_at: Optional[int] = None,
) -> UserTokenSession:
    return UserTokenSession(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at,
        refresh_expires_at=refresh_expires_at,
        token_type="Bearer",
        scope="offline_access",
        obtained_at=1700000000,
    )


def test_save_load_and_clear_session_roundtrip() -> None:
    original = _session()
    path = save_user_token_session(original)

    loaded = load_user_token_session()
    assert loaded is not None
    assert loaded.access_token == original.access_token
    assert loaded.refresh_token == original.refresh_token
    assert loaded.token_type == "Bearer"
    assert path.exists()

    clear_user_token_session()
    assert load_user_token_session() is None
    assert not path.exists()


def test_resolve_user_request_option_prefers_env_token(monkeypatch) -> None:
    monkeypatch.setenv("FEISHU_USER_ACCESS_TOKEN", "env-user-token")
    option = resolve_user_request_option(MagicMock())
    assert option is not None
    assert option.user_access_token == "env-user-token"


def test_resolve_user_request_option_refreshes_and_persists(monkeypatch) -> None:
    stale = _session(access_token="old", expires_at=0)
    refreshed = _session(access_token="new", expires_at=9999999999)
    save_mock = MagicMock()

    monkeypatch.setattr(session_mod, "load_user_token_session", lambda: stale)
    monkeypatch.setattr(session_mod, "refresh_user_token_session", lambda _c, _s: refreshed)
    monkeypatch.setattr(session_mod, "save_user_token_session", save_mock)

    option = resolve_user_request_option(MagicMock())
    assert option is not None
    assert option.user_access_token == "new"
    save_mock.assert_called_once_with(refreshed)


def test_resolve_user_request_option_clears_when_refresh_fails(monkeypatch) -> None:
    stale = _session(access_token="old", expires_at=0)
    clear_mock = MagicMock()

    monkeypatch.setattr(session_mod, "load_user_token_session", lambda: stale)
    monkeypatch.setattr(session_mod, "refresh_user_token_session", lambda _c, _s: None)
    monkeypatch.setattr(session_mod, "clear_user_token_session", clear_mock)

    option = resolve_user_request_option(MagicMock())
    assert option is None
    clear_mock.assert_called_once()
