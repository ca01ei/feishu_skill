"""User access token session management for Feishu CLI."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import time
from typing import Optional

import lark_oapi as lark
from lark_oapi.api.authen.v1 import (
    CreateOidcAccessTokenRequest,
    CreateOidcAccessTokenRequestBody,
    CreateOidcRefreshAccessTokenRequest,
    CreateOidcRefreshAccessTokenRequestBody,
    GetUserInfoRequest,
)
from lark_oapi.core.model import RequestOption


ACCESS_TOKEN_REFRESH_BUFFER_SECONDS = 120
REFRESH_TOKEN_REFRESH_BUFFER_SECONDS = 60


@dataclass
class UserTokenSession:
    """Persistent user token session."""

    access_token: str
    refresh_token: Optional[str]
    expires_at: Optional[int]
    refresh_expires_at: Optional[int]
    token_type: Optional[str]
    scope: Optional[str]
    obtained_at: int


def _default_token_file() -> Path:
    return Path.home() / ".config" / "feishu-cli" / "user_token.json"


def get_token_file_path() -> Path:
    """Return the configured session file path."""
    raw = os.environ.get("FEISHU_TOKEN_FILE")
    return Path(raw).expanduser() if raw else _default_token_file()


def save_user_token_session(session: UserTokenSession) -> Path:
    """Persist user token session to local file with restrictive permissions."""
    path = get_token_file_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(asdict(session), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return path


def load_user_token_session() -> Optional[UserTokenSession]:
    """Load user token session from local file."""
    path = get_token_file_path()
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        access_token = str(raw.get("access_token", "")).strip()
        if not access_token:
            return None
        return UserTokenSession(
            access_token=access_token,
            refresh_token=_get_optional_str(raw, "refresh_token"),
            expires_at=_get_optional_int(raw, "expires_at"),
            refresh_expires_at=_get_optional_int(raw, "refresh_expires_at"),
            token_type=_get_optional_str(raw, "token_type"),
            scope=_get_optional_str(raw, "scope"),
            obtained_at=int(raw.get("obtained_at", int(time.time()))),
        )
    except (json.JSONDecodeError, OSError, ValueError, TypeError):
        return None


def clear_user_token_session() -> None:
    """Delete local user token session file."""
    path = get_token_file_path()
    if path.exists():
        try:
            path.unlink()
        except OSError:
            pass


def get_env_user_access_token() -> Optional[str]:
    """Return user token from environment if present."""
    token = os.environ.get("FEISHU_USER_ACCESS_TOKEN", "").strip()
    return token or None


def resolve_user_request_option(client: lark.Client) -> Optional[RequestOption]:
    """Resolve current user token and build request option for user-priority auth."""
    env_token = get_env_user_access_token()
    if env_token:
        return RequestOption.builder().user_access_token(env_token).build()

    session = load_user_token_session()
    if session is None:
        return None

    if _is_token_expiring(session.expires_at, ACCESS_TOKEN_REFRESH_BUFFER_SECONDS):
        refreshed = refresh_user_token_session(client, session)
        if refreshed is None:
            clear_user_token_session()
            return None
        session = refreshed
        save_user_token_session(session)

    return RequestOption.builder().user_access_token(session.access_token).build()


def exchange_oidc_code_for_session(client: lark.Client, code: str) -> Optional[UserTokenSession]:
    """Exchange OIDC authorization code for user token session."""
    body = (
        CreateOidcAccessTokenRequestBody.builder()
        .grant_type("authorization_code")
        .code(code)
        .build()
    )
    request = CreateOidcAccessTokenRequest.builder().request_body(body).build()
    response = client.authen.v1.oidc_access_token.create(request)
    if not response.success() or response.data is None:
        return None
    return build_session_from_token_response_data(response.data)


def refresh_user_token_session(
    client: lark.Client, session: UserTokenSession
) -> Optional[UserTokenSession]:
    """Refresh user token session if refresh token is available and not expired."""
    if not session.refresh_token:
        return None
    if _is_token_expiring(session.refresh_expires_at, REFRESH_TOKEN_REFRESH_BUFFER_SECONDS):
        return None

    body = (
        CreateOidcRefreshAccessTokenRequestBody.builder()
        .grant_type("refresh_token")
        .refresh_token(session.refresh_token)
        .build()
    )
    request = CreateOidcRefreshAccessTokenRequest.builder().request_body(body).build()
    response = client.authen.v1.oidc_refresh_access_token.create(request)
    if not response.success() or response.data is None:
        return None
    refreshed = build_session_from_token_response_data(response.data)
    if refreshed is None:
        return None
    if not refreshed.refresh_token:
        refreshed.refresh_token = session.refresh_token
    if refreshed.refresh_expires_at is None:
        refreshed.refresh_expires_at = session.refresh_expires_at
    return refreshed


def get_user_info_by_token(client: lark.Client, access_token: str):
    """Get current user profile from user access token."""
    request = GetUserInfoRequest.builder().build()
    option = RequestOption.builder().user_access_token(access_token).build()
    return client.authen.v1.user_info.get(request, option)


def build_session_from_token_response_data(data) -> Optional[UserTokenSession]:
    access_token = getattr(data, "access_token", None)
    if not access_token:
        return None
    now = int(time.time())
    expires_in = _safe_int(getattr(data, "expires_in", None))
    refresh_expires_in = _safe_int(getattr(data, "refresh_expires_in", None))
    return UserTokenSession(
        access_token=str(access_token),
        refresh_token=_safe_optional_str(getattr(data, "refresh_token", None)),
        expires_at=now + expires_in if expires_in is not None else None,
        refresh_expires_at=(
            now + refresh_expires_in if refresh_expires_in is not None else None
        ),
        token_type=_safe_optional_str(getattr(data, "token_type", None)),
        scope=_safe_optional_str(getattr(data, "scope", None)),
        obtained_at=now,
    )


def _is_token_expiring(expires_at: Optional[int], buffer_seconds: int) -> bool:
    if expires_at is None:
        return False
    return int(time.time()) >= (expires_at - buffer_seconds)


def _safe_optional_str(value) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _safe_int(value) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _get_optional_str(data: dict, key: str) -> Optional[str]:
    return _safe_optional_str(data.get(key))


def _get_optional_int(data: dict, key: str) -> Optional[int]:
    return _safe_int(data.get(key))
