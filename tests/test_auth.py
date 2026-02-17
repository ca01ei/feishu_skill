"""Tests for auth commands."""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from feishu_cli.auth.session import UserTokenSession
from feishu_cli.commands.auth import auth_app

runner = CliRunner()


def _session(access_token: str = "u_access") -> UserTokenSession:
    return UserTokenSession(
        access_token=access_token,
        refresh_token="u_refresh",
        expires_at=1890000000,
        refresh_expires_at=1890003600,
        token_type="Bearer",
        scope="offline_access",
        obtained_at=1700000000,
    )


def _success_response() -> MagicMock:
    resp = MagicMock()
    resp.success.return_value = True
    resp.data = None
    return resp


@patch("feishu_cli.commands.auth.load_config")
def test_auth_login_url(mock_load_config: MagicMock) -> None:
    mock_load_config.return_value = SimpleNamespace(app_id="cli_test_app")
    result = runner.invoke(auth_app, ["login-url", "--state", "state123"])
    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["success"] is True
    assert parsed["data"]["state"] == "state123"
    assert "cli_test_app" in parsed["data"]["authorize_url"]


@patch("feishu_cli.commands.auth.save_user_token_session")
@patch("feishu_cli.commands.auth.exchange_oidc_code_for_session")
@patch("feishu_cli.commands.auth.create_client")
def test_auth_exchange_code_success(
    mock_create_client: MagicMock,
    mock_exchange: MagicMock,
    mock_save: MagicMock,
    tmp_path,
) -> None:
    mock_create_client.return_value = MagicMock()
    mock_exchange.return_value = _session()
    mock_save.return_value = tmp_path / "token.json"

    result = runner.invoke(auth_app, ["exchange-code", "--code", "code123"])
    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["success"] is True
    assert parsed["data"]["mode"] == "user"
    assert parsed["data"]["token_file"] == str(tmp_path / "token.json")


@patch("feishu_cli.commands.auth.exchange_oidc_code_for_session")
@patch("feishu_cli.commands.auth.create_client")
def test_auth_exchange_code_failure(
    mock_create_client: MagicMock,
    mock_exchange: MagicMock,
) -> None:
    mock_create_client.return_value = MagicMock()
    mock_exchange.return_value = None

    result = runner.invoke(auth_app, ["exchange-code", "--code", "badcode"])
    assert result.exit_code == 1
    parsed = json.loads(result.stdout)
    assert parsed["success"] is False
    assert parsed["code"] == 1


@patch("feishu_cli.commands.auth.resolve_user_request_option")
@patch("feishu_cli.commands.auth.create_client")
def test_auth_whoami_requires_user_token(
    mock_create_client: MagicMock,
    mock_resolve: MagicMock,
) -> None:
    mock_create_client.return_value = MagicMock()
    mock_resolve.return_value = None

    result = runner.invoke(auth_app, ["whoami"])
    assert result.exit_code == 2
    parsed = json.loads(result.stdout)
    assert parsed["success"] is False
    assert parsed["code"] == 2


@patch("feishu_cli.commands.auth.get_user_info_by_token")
@patch("feishu_cli.commands.auth.resolve_user_request_option")
@patch("feishu_cli.commands.auth.create_client")
def test_auth_whoami_success(
    mock_create_client: MagicMock,
    mock_resolve: MagicMock,
    mock_get_user_info: MagicMock,
) -> None:
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client
    mock_resolve.return_value = SimpleNamespace(user_access_token="env_or_session_token")
    mock_get_user_info.return_value = _success_response()

    result = runner.invoke(auth_app, ["whoami"])
    assert result.exit_code == 0
    mock_get_user_info.assert_called_once_with(mock_client, "env_or_session_token")


@patch("feishu_cli.commands.auth.load_user_token_session")
@patch("feishu_cli.commands.auth.create_client")
def test_auth_refresh_requires_session_when_no_explicit_token(
    mock_create_client: MagicMock,
    mock_load_session: MagicMock,
) -> None:
    mock_create_client.return_value = MagicMock()
    mock_load_session.return_value = None

    result = runner.invoke(auth_app, ["refresh"])
    assert result.exit_code == 2
    parsed = json.loads(result.stdout)
    assert parsed["success"] is False
    assert parsed["code"] == 2


@patch("feishu_cli.commands.auth.save_user_token_session")
@patch("feishu_cli.commands.auth.refresh_user_token_session")
@patch("feishu_cli.commands.auth.create_client")
def test_auth_refresh_with_explicit_refresh_token(
    mock_create_client: MagicMock,
    mock_refresh: MagicMock,
    mock_save: MagicMock,
    tmp_path,
) -> None:
    mock_create_client.return_value = MagicMock()
    mock_refresh.return_value = _session(access_token="new_access")
    mock_save.return_value = tmp_path / "token.json"

    result = runner.invoke(auth_app, ["refresh", "--refresh-token", "refresh_123"])
    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["success"] is True
    assert parsed["data"]["has_refresh_token"] is True

    refresh_session = mock_refresh.call_args[0][1]
    assert refresh_session.refresh_token == "refresh_123"


@patch("feishu_cli.commands.auth.get_token_file_path")
@patch("feishu_cli.commands.auth.clear_user_token_session")
def test_auth_logout(
    mock_clear: MagicMock,
    mock_get_path: MagicMock,
) -> None:
    mock_get_path.return_value = Path("/tmp/feishu-user-token.json")
    result = runner.invoke(auth_app, ["logout"])
    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["success"] is True
    assert parsed["data"]["token_file"] == "/tmp/feishu-user-token.json"
    mock_clear.assert_called_once()
