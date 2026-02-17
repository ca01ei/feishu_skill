"""Tests for legacy docs commands."""

import json
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from feishu_cli.commands.docs import docs_app

runner = CliRunner()


@patch("feishu_cli.commands.docs.create_client")
def test_docs_get(mock_create_client: MagicMock) -> None:
    """Test getting document content."""
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = None
    mock_client.docs.v1.content.get.return_value = mock_resp
    mock_create_client.return_value = mock_client

    result = runner.invoke(docs_app, ["--token", "doccnXXX"])

    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["success"] is True


@patch("feishu_cli.commands.docs.create_client")
def test_docs_get_failure(mock_create_client: MagicMock) -> None:
    """Test getting document content when API fails."""
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.success.return_value = False
    mock_resp.code = 99999
    mock_resp.msg = "not found"
    mock_resp.get_log_id.return_value = "log123"
    mock_client.docs.v1.content.get.return_value = mock_resp
    mock_create_client.return_value = mock_client

    result = runner.invoke(docs_app, ["--token", "doccnXXX"])

    assert result.exit_code == 1
    parsed = json.loads(result.stdout)
    assert parsed["success"] is False
    assert parsed["code"] == 99999
