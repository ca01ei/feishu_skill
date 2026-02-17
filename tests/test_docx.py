"""Tests for docx commands."""

import json
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from feishu_cli.commands.docx import docx_app

runner = CliRunner()


def _mock_success_response(data=None):
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = data
    return mock_resp


def _mock_failure_response(code=99991400, msg="token invalid", log_id="log123"):
    mock_resp = MagicMock()
    mock_resp.success.return_value = False
    mock_resp.code = code
    mock_resp.msg = msg
    mock_resp.get_log_id.return_value = log_id
    return mock_resp


@patch("feishu_cli.commands.docx.create_client")
def test_docx_create(mock_create_client):
    mock_client = MagicMock()
    mock_resp = _mock_success_response()
    mock_client.docx.v1.document.create.return_value = mock_resp
    mock_create_client.return_value = mock_client
    result = runner.invoke(docx_app, ["create", "--title", "Test Doc"])
    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["success"] is True


@patch("feishu_cli.commands.docx.create_client")
def test_docx_create_with_folder(mock_create_client):
    mock_client = MagicMock()
    mock_resp = _mock_success_response()
    mock_client.docx.v1.document.create.return_value = mock_resp
    mock_create_client.return_value = mock_client
    result = runner.invoke(
        docx_app, ["create", "--title", "Test", "--folder-token", "fldcnXXX"]
    )
    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["success"] is True


@patch("feishu_cli.commands.docx.create_client")
def test_docx_create_failure(mock_create_client):
    mock_client = MagicMock()
    mock_resp = _mock_failure_response()
    mock_client.docx.v1.document.create.return_value = mock_resp
    mock_create_client.return_value = mock_client
    result = runner.invoke(docx_app, ["create", "--title", "Test"])
    assert result.exit_code == 1
    parsed = json.loads(result.stdout)
    assert parsed["success"] is False


@patch("feishu_cli.commands.docx.create_client")
def test_docx_get(mock_create_client):
    mock_client = MagicMock()
    mock_resp = _mock_success_response()
    mock_client.docx.v1.document.get.return_value = mock_resp
    mock_create_client.return_value = mock_client
    result = runner.invoke(docx_app, ["get", "--token", "doxcnABC"])
    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["success"] is True


@patch("feishu_cli.commands.docx.create_client")
def test_docx_content(mock_create_client):
    mock_client = MagicMock()
    mock_resp = _mock_success_response()
    mock_client.docx.v1.document.raw_content.return_value = mock_resp
    mock_create_client.return_value = mock_client
    result = runner.invoke(docx_app, ["content", "--token", "doxcnABC"])
    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["success"] is True


@patch("feishu_cli.commands.docx.create_client")
def test_docx_content_with_lang(mock_create_client):
    mock_client = MagicMock()
    mock_resp = _mock_success_response()
    mock_client.docx.v1.document.raw_content.return_value = mock_resp
    mock_create_client.return_value = mock_client
    result = runner.invoke(
        docx_app, ["content", "--token", "doxcnABC", "--lang", "1"]
    )
    assert result.exit_code == 0


@patch("feishu_cli.commands.docx.create_client")
def test_block_list(mock_create_client):
    mock_client = MagicMock()
    mock_resp = _mock_success_response()
    mock_client.docx.v1.document_block.list.return_value = mock_resp
    mock_create_client.return_value = mock_client
    result = runner.invoke(docx_app, ["block", "list", "--token", "doxcnABC"])
    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["success"] is True


@patch("feishu_cli.commands.docx.create_client")
def test_block_list_with_pagination(mock_create_client):
    mock_client = MagicMock()
    mock_resp = _mock_success_response()
    mock_client.docx.v1.document_block.list.return_value = mock_resp
    mock_create_client.return_value = mock_client
    result = runner.invoke(
        docx_app,
        ["block", "list", "--token", "doxcnABC", "--page-size", "10", "--page-token", "pt1"],
    )
    assert result.exit_code == 0


@patch("feishu_cli.commands.docx.create_client")
def test_block_get(mock_create_client):
    mock_client = MagicMock()
    mock_resp = _mock_success_response()
    mock_client.docx.v1.document_block.get.return_value = mock_resp
    mock_create_client.return_value = mock_client
    result = runner.invoke(
        docx_app, ["block", "get", "--token", "doxcnABC", "--block-id", "blk123"]
    )
    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["success"] is True


@patch("feishu_cli.commands.docx.create_client")
def test_block_create(mock_create_client):
    mock_client = MagicMock()
    mock_resp = _mock_success_response()
    mock_client.docx.v1.document_block_children.create.return_value = mock_resp
    mock_create_client.return_value = mock_client
    data = json.dumps({"children": [], "index": 0})
    result = runner.invoke(
        docx_app,
        ["block", "create", "--token", "doxcnABC", "--block-id", "blk123", "--data", data],
    )
    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["success"] is True


@patch("feishu_cli.commands.docx.create_client")
def test_block_create_from_file(mock_create_client, tmp_path):
    mock_client = MagicMock()
    mock_resp = _mock_success_response()
    mock_client.docx.v1.document_block_children.create.return_value = mock_resp
    mock_create_client.return_value = mock_client
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps({"children": [], "index": 0}))
    result = runner.invoke(
        docx_app,
        ["block", "create", "--token", "doxcnABC", "--block-id", "blk123", "--data", f"@{data_file}"],
    )
    assert result.exit_code == 0


@patch("feishu_cli.commands.docx.create_client")
def test_block_delete(mock_create_client):
    mock_client = MagicMock()
    mock_resp = _mock_success_response()
    mock_client.docx.v1.document_block_children.batch_delete.return_value = mock_resp
    mock_create_client.return_value = mock_client
    result = runner.invoke(
        docx_app,
        [
            "block", "delete",
            "--token", "doxcnABC",
            "--block-id", "blk123",
            "--start-index", "0",
            "--end-index", "2",
        ],
    )
    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["success"] is True
