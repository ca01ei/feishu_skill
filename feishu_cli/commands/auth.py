"""Authentication commands for user access token workflows."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import secrets
import threading
from typing import Optional
from urllib.parse import parse_qs, urlencode, urlparse
import webbrowser

import typer

from feishu_cli.auth.session import (
    UserTokenSession,
    clear_user_token_session,
    exchange_oidc_code_for_session,
    get_token_file_path,
    get_user_info_by_token,
    load_user_token_session,
    refresh_user_token_session,
    resolve_user_request_option,
    save_user_token_session,
)
from feishu_cli.client import create_client
from feishu_cli.config import load_config
from feishu_cli.utils.output import format_error, format_response


DEFAULT_REDIRECT_URI = "http://127.0.0.1:3080/callback"
DEFAULT_AUTH_SCOPES = [
    "offline_access",
    "auth:user.id:read",
    "docx:document",
    "docx:document:create",
    "docs:document.content:read",
    "drive:drive",
    "sheets:spreadsheet",
    "sheets:spreadsheet:create",
    "bitable:app",
    "base:app:create",
]
DEFAULT_AUTH_SCOPE = " ".join(DEFAULT_AUTH_SCOPES)
AUTHORIZE_BASE_URL = "https://open.feishu.cn/open-apis/authen/v1/authorize"


auth_app = typer.Typer(
    name="auth",
    help="User access token authentication operations.",
    no_args_is_help=True,
)


@auth_app.command("login-url")
def login_url(
    redirect_uri: str = typer.Option(DEFAULT_REDIRECT_URI, help="OIDC callback URI"),
    scope: str = typer.Option(DEFAULT_AUTH_SCOPE, help="OAuth scope"),
    state: Optional[str] = typer.Option(None, help="CSRF state value"),
) -> None:
    """Generate OIDC authorization URL."""
    app_id = load_config().app_id
    final_state = state or secrets.token_urlsafe(16)
    url = build_authorize_url(
        app_id=app_id,
        redirect_uri=redirect_uri,
        scope=scope,
        state=final_state,
    )
    _echo_success(
        {
            "authorize_url": url,
            "state": final_state,
            "redirect_uri": redirect_uri,
            "scope": scope,
        }
    )


@auth_app.command("login")
def login(
    redirect_uri: str = typer.Option(DEFAULT_REDIRECT_URI, help="OIDC callback URI"),
    scope: str = typer.Option(DEFAULT_AUTH_SCOPE, help="OAuth scope"),
    state: Optional[str] = typer.Option(None, help="CSRF state value"),
    timeout_seconds: int = typer.Option(180, help="Callback wait timeout in seconds"),
    manual: bool = typer.Option(
        False, "--manual", help="Manual mode: paste callback URL/code instead of local callback"
    ),
    no_open_browser: bool = typer.Option(
        False, "--no-open-browser", help="Do not open browser automatically"
    ),
) -> None:
    """Run interactive login and persist user token session."""
    app_id = load_config().app_id
    final_state = state or secrets.token_urlsafe(16)
    url = build_authorize_url(
        app_id=app_id,
        redirect_uri=redirect_uri,
        scope=scope,
        state=final_state,
    )

    code: Optional[str]
    returned_state: Optional[str]

    if manual:
        _echo_success(
            {
                "authorize_url": url,
                "state": final_state,
                "hint": "Open authorize_url, then paste callback URL or code.",
            }
        )
        raw_input = typer.prompt("Paste callback URL or authorization code")
        code, returned_state = extract_code_and_state(raw_input)
    else:
        code, returned_state = wait_for_callback_code(
            authorize_url=url,
            redirect_uri=redirect_uri,
            timeout_seconds=timeout_seconds,
            no_open_browser=no_open_browser,
        )

    if not code:
        _exit_with_error("Failed to obtain authorization code.", code=2)
    if returned_state and returned_state != final_state:
        _exit_with_error("State mismatch. Please retry login.", code=2)

    _exchange_code_and_save_session(code)


@auth_app.command("exchange-code")
def exchange_code(
    code: str = typer.Option(..., help="Authorization code"),
) -> None:
    """Exchange OIDC code for access token and persist session."""
    _exchange_code_and_save_session(code)


@auth_app.command("refresh")
def refresh(
    refresh_token: Optional[str] = typer.Option(None, help="Refresh token (optional)"),
) -> None:
    """Refresh current user session token."""
    client = create_client()

    if refresh_token:
        session = UserTokenSession(
            access_token="",
            refresh_token=refresh_token,
            expires_at=None,
            refresh_expires_at=None,
            token_type=None,
            scope=None,
            obtained_at=0,
        )
    else:
        session = load_user_token_session()
        if session is None:
            _exit_with_error("No local user token session found.", code=2)

    refreshed = refresh_user_token_session(client, session)
    if refreshed is None:
        _exit_with_error("Failed to refresh user token. Please login again.", code=1)

    path = save_user_token_session(refreshed)
    _echo_success(session_metadata(refreshed, path))


@auth_app.command("whoami")
def whoami() -> None:
    """Show current authenticated user profile."""
    client = create_client()
    option = resolve_user_request_option(client)
    if option is None or not option.user_access_token:
        _exit_with_error("No user token available. Run `auth login` first.", code=2)

    response = get_user_info_by_token(client, option.user_access_token)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@auth_app.command("logout")
def logout() -> None:
    """Remove persisted local user token session."""
    clear_user_token_session()
    _echo_success(
        {
            "message": "User session cleared.",
            "token_file": str(get_token_file_path()),
        }
    )


def build_authorize_url(app_id: str, redirect_uri: str, scope: str, state: str) -> str:
    """Build Feishu OIDC authorize URL."""
    params = {
        "app_id": app_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,
    }
    return f"{AUTHORIZE_BASE_URL}?{urlencode(params)}"


def extract_code_and_state(value: str) -> tuple[Optional[str], Optional[str]]:
    """Extract code/state from callback URL or raw code input."""
    text = value.strip()
    if not text:
        return None, None
    if text.startswith("http://") or text.startswith("https://"):
        parsed = urlparse(text)
        query = parse_qs(parsed.query)
        code = _first(query, "code")
        state = _first(query, "state")
        return code, state
    return text, None


def wait_for_callback_code(
    authorize_url: str,
    redirect_uri: str,
    timeout_seconds: int,
    no_open_browser: bool,
) -> tuple[Optional[str], Optional[str]]:
    """Wait for one-shot local callback and return (code, state)."""
    parsed = urlparse(redirect_uri)
    host = parsed.hostname
    port = parsed.port
    path = parsed.path or "/"

    if parsed.scheme != "http" or host not in {"127.0.0.1", "localhost"} or port is None:
        _exit_with_error(
            "Automatic callback requires http://127.0.0.1:<port>/... or http://localhost:<port>/...",
            code=2,
        )

    result: dict[str, Optional[str]] = {}
    done = threading.Event()

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            req = urlparse(self.path)
            if req.path != path:
                self.send_response(404)
                self.end_headers()
                return
            query = parse_qs(req.query)
            result["code"] = _first(query, "code")
            result["state"] = _first(query, "state")
            result["error"] = _first(query, "error")
            result["error_description"] = _first(query, "error_description")

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h3>Authorization received. You can close this page.</h3></body></html>"
            )
            done.set()

        def log_message(self, format, *args):  # noqa: A003
            return

    try:
        server = HTTPServer((host, port), CallbackHandler)
    except OSError as exc:
        _exit_with_error(f"Failed to start local callback server: {exc}", code=2)

    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()

    if not no_open_browser:
        webbrowser.open(authorize_url)

    if not done.wait(timeout_seconds):
        server.server_close()
        return None, None

    server.server_close()
    if result.get("error"):
        desc = result.get("error_description") or result["error"]
        _exit_with_error(f"Authorization failed: {desc}", code=1)
    return result.get("code"), result.get("state")


def _exchange_code_and_save_session(code: str) -> None:
    client = create_client()
    session = exchange_oidc_code_for_session(client, code)
    if session is None:
        _exit_with_error("Failed to exchange code for user token.", code=1)

    path = save_user_token_session(session)
    _echo_success(session_metadata(session, path))


def session_metadata(session: UserTokenSession, path: Path) -> dict:
    """Build safe metadata payload without exposing raw tokens."""
    return {
        "mode": "user",
        "token_file": str(path),
        "token_type": session.token_type,
        "scope": session.scope,
        "obtained_at": session.obtained_at,
        "expires_at": session.expires_at,
        "refresh_expires_at": session.refresh_expires_at,
        "has_refresh_token": bool(session.refresh_token),
    }


def _first(data: dict[str, list[str]], key: str) -> Optional[str]:
    values = data.get(key)
    if not values:
        return None
    return values[0] if values[0] else None


def _echo_success(data: dict) -> None:
    typer.echo(
        json.dumps(
            {"success": True, "data": data},
            ensure_ascii=False,
            indent=2,
        )
    )


def _exit_with_error(message: str, code: int) -> None:
    typer.echo(format_error(code=code, msg=message))
    raise typer.Exit(code=code)
