"""Tests for runtime API invocation helper."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from feishu_cli.runtime import call_api


def test_call_api_without_user_option() -> None:
    client = MagicMock()
    api_method = MagicMock(return_value="ok")
    request = object()

    with patch("feishu_cli.runtime.resolve_user_request_option", return_value=None):
        result = call_api(client, api_method, request)

    assert result == "ok"
    api_method.assert_called_once_with(request)


def test_call_api_with_user_option() -> None:
    client = MagicMock()
    api_method = MagicMock(return_value="ok")
    request = object()
    option = SimpleNamespace(user_access_token="u-token")

    with patch("feishu_cli.runtime.resolve_user_request_option", return_value=option):
        result = call_api(client, api_method, request)

    assert result == "ok"
    api_method.assert_called_once_with(request, option)
