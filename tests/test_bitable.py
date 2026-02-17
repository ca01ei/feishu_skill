"""Tests for bitable commands."""

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from feishu_cli.commands.bitable import bitable_app
from lark_oapi.api.bitable.v1 import ReqApp

runner = CliRunner()


def _mock_success() -> MagicMock:
    resp = MagicMock()
    resp.success.return_value = True
    resp.data = None
    return resp


def _mock_failure() -> MagicMock:
    resp = MagicMock()
    resp.success.return_value = False
    resp.code = 99999
    resp.msg = "error"
    resp.get_log_id.return_value = "log123"
    return resp


# ── App commands ────────────────────────────────────────────────────────────


@patch("feishu_cli.commands.bitable.create_client")
def test_app_get(mock_cc: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.bitable.v1.app.get.return_value = _mock_success()
    mock_cc.return_value = mock_client
    result = runner.invoke(bitable_app, ["get", "--app-token", "appXXX"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["success"] is True


@patch("feishu_cli.commands.bitable.create_client")
def test_app_create(mock_cc: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.bitable.v1.app.create.return_value = _mock_success()
    mock_cc.return_value = mock_client
    result = runner.invoke(bitable_app, ["create", "--name", "Test"])
    assert result.exit_code == 0
    request = mock_client.bitable.v1.app.create.call_args[0][0]
    assert isinstance(request.request_body, ReqApp)
    assert request.request_body.name == "Test"


@patch("feishu_cli.commands.bitable.create_client")
def test_app_update_requires_any_field(mock_cc: MagicMock) -> None:
    mock_cc.return_value = MagicMock()
    result = runner.invoke(bitable_app, ["update", "--app-token", "appXXX"])
    assert result.exit_code == 2
    parsed = json.loads(result.stdout)
    assert parsed["success"] is False
    assert parsed["code"] == 2


@patch("feishu_cli.commands.bitable.create_client")
def test_app_update(mock_cc: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.bitable.v1.app.update.return_value = _mock_success()
    mock_cc.return_value = mock_client
    result = runner.invoke(bitable_app, ["update", "--app-token", "appXXX", "--name", "New"])
    assert result.exit_code == 0


@patch("feishu_cli.commands.bitable.create_client")
def test_app_copy(mock_cc: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.bitable.v1.app.copy.return_value = _mock_success()
    mock_cc.return_value = mock_client
    result = runner.invoke(bitable_app, ["copy", "--app-token", "appXXX", "--name", "Copy"])
    assert result.exit_code == 0


# ── Table commands ──────────────────────────────────────────────────────────


@patch("feishu_cli.commands.bitable.create_client")
def test_table_list(mock_cc: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.bitable.v1.app_table.list.return_value = _mock_success()
    mock_cc.return_value = mock_client
    result = runner.invoke(bitable_app, ["table", "list", "--app-token", "appXXX"])
    assert result.exit_code == 0


@patch("feishu_cli.commands.bitable.create_client")
def test_table_create(mock_cc: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.bitable.v1.app_table.create.return_value = _mock_success()
    mock_cc.return_value = mock_client
    result = runner.invoke(bitable_app, ["table", "create", "--app-token", "appXXX", "--name", "T1"])
    assert result.exit_code == 0


@patch("feishu_cli.commands.bitable.create_client")
def test_table_delete(mock_cc: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.bitable.v1.app_table.delete.return_value = _mock_success()
    mock_cc.return_value = mock_client
    result = runner.invoke(bitable_app, ["table", "delete", "--app-token", "appXXX", "--table-id", "tblXXX"])
    assert result.exit_code == 0


@patch("feishu_cli.commands.bitable.create_client")
def test_table_patch(mock_cc: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.bitable.v1.app_table.patch.return_value = _mock_success()
    mock_cc.return_value = mock_client
    result = runner.invoke(bitable_app, ["table", "patch", "--app-token", "appXXX", "--table-id", "tblXXX", "--name", "New"])
    assert result.exit_code == 0


# ── Record commands ─────────────────────────────────────────────────────────


@patch("feishu_cli.commands.bitable.create_client")
def test_record_list(mock_cc: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.bitable.v1.app_table_record.list.return_value = _mock_success()
    mock_cc.return_value = mock_client
    result = runner.invoke(bitable_app, ["record", "list", "--app-token", "appXXX", "--table-id", "tblXXX"])
    assert result.exit_code == 0


@patch("feishu_cli.commands.bitable.create_client")
def test_record_get(mock_cc: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.bitable.v1.app_table_record.get.return_value = _mock_success()
    mock_cc.return_value = mock_client
    result = runner.invoke(bitable_app, ["record", "get", "--app-token", "appXXX", "--table-id", "tblXXX", "--record-id", "recXXX"])
    assert result.exit_code == 0


@patch("feishu_cli.commands.bitable.create_client")
def test_record_create(mock_cc: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.bitable.v1.app_table_record.create.return_value = _mock_success()
    mock_cc.return_value = mock_client
    result = runner.invoke(bitable_app, ["record", "create", "--app-token", "appXXX", "--table-id", "tblXXX", "--fields", '{"name": "test"}'])
    assert result.exit_code == 0


@patch("feishu_cli.commands.bitable.create_client")
def test_record_update(mock_cc: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.bitable.v1.app_table_record.update.return_value = _mock_success()
    mock_cc.return_value = mock_client
    result = runner.invoke(bitable_app, ["record", "update", "--app-token", "appXXX", "--table-id", "tblXXX", "--record-id", "recXXX", "--fields", '{"name": "updated"}'])
    assert result.exit_code == 0


@patch("feishu_cli.commands.bitable.create_client")
def test_record_delete(mock_cc: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.bitable.v1.app_table_record.delete.return_value = _mock_success()
    mock_cc.return_value = mock_client
    result = runner.invoke(bitable_app, ["record", "delete", "--app-token", "appXXX", "--table-id", "tblXXX", "--record-id", "recXXX"])
    assert result.exit_code == 0


@patch("feishu_cli.commands.bitable.create_client")
def test_record_create_invalid_json(mock_cc: MagicMock) -> None:
    mock_cc.return_value = MagicMock()
    result = runner.invoke(
        bitable_app,
        ["record", "create", "--app-token", "appXXX", "--table-id", "tblXXX", "--fields", "{"],
    )
    assert result.exit_code == 2
    parsed = json.loads(result.stdout)
    assert parsed["success"] is False
    assert parsed["code"] == 2
    assert "Invalid JSON" in parsed["msg"]


# ── Field commands ──────────────────────────────────────────────────────────


@patch("feishu_cli.commands.bitable.create_client")
def test_field_list(mock_cc: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.bitable.v1.app_table_field.list.return_value = _mock_success()
    mock_cc.return_value = mock_client
    result = runner.invoke(bitable_app, ["field", "list", "--app-token", "appXXX", "--table-id", "tblXXX"])
    assert result.exit_code == 0


@patch("feishu_cli.commands.bitable.create_client")
def test_field_create(mock_cc: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.bitable.v1.app_table_field.create.return_value = _mock_success()
    mock_cc.return_value = mock_client
    result = runner.invoke(bitable_app, ["field", "create", "--app-token", "appXXX", "--table-id", "tblXXX", "--field-name", "Age", "--field-type", "2"])
    assert result.exit_code == 0


@patch("feishu_cli.commands.bitable.create_client")
def test_field_delete(mock_cc: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.bitable.v1.app_table_field.delete.return_value = _mock_success()
    mock_cc.return_value = mock_client
    result = runner.invoke(bitable_app, ["field", "delete", "--app-token", "appXXX", "--table-id", "tblXXX", "--field-id", "fldXXX"])
    assert result.exit_code == 0


# ── View commands ───────────────────────────────────────────────────────────


@patch("feishu_cli.commands.bitable.create_client")
def test_view_list(mock_cc: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.bitable.v1.app_table_view.list.return_value = _mock_success()
    mock_cc.return_value = mock_client
    result = runner.invoke(bitable_app, ["view", "list", "--app-token", "appXXX", "--table-id", "tblXXX"])
    assert result.exit_code == 0


@patch("feishu_cli.commands.bitable.create_client")
def test_view_get(mock_cc: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.bitable.v1.app_table_view.get.return_value = _mock_success()
    mock_cc.return_value = mock_client
    result = runner.invoke(bitable_app, ["view", "get", "--app-token", "appXXX", "--table-id", "tblXXX", "--view-id", "vewXXX"])
    assert result.exit_code == 0


@patch("feishu_cli.commands.bitable.create_client")
def test_view_create(mock_cc: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.bitable.v1.app_table_view.create.return_value = _mock_success()
    mock_cc.return_value = mock_client
    result = runner.invoke(bitable_app, ["view", "create", "--app-token", "appXXX", "--table-id", "tblXXX", "--view-name", "V1"])
    assert result.exit_code == 0


@patch("feishu_cli.commands.bitable.create_client")
def test_view_delete(mock_cc: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.bitable.v1.app_table_view.delete.return_value = _mock_success()
    mock_cc.return_value = mock_client
    result = runner.invoke(bitable_app, ["view", "delete", "--app-token", "appXXX", "--table-id", "tblXXX", "--view-id", "vewXXX"])
    assert result.exit_code == 0


# ── Failure case ────────────────────────────────────────────────────────────


@patch("feishu_cli.commands.bitable.create_client")
def test_app_get_failure(mock_cc: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.bitable.v1.app.get.return_value = _mock_failure()
    mock_cc.return_value = mock_client
    result = runner.invoke(bitable_app, ["get", "--app-token", "appXXX"])
    assert result.exit_code == 1
    parsed = json.loads(result.stdout)
    assert parsed["success"] is False
