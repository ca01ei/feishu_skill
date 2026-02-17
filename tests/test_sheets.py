"""Tests for sheets commands."""

import json
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from feishu_cli.commands.sheets import sheets_app

runner = CliRunner()


def _mock_success_response(data=None):
    resp = MagicMock()
    resp.success.return_value = True
    resp.data = data
    return resp


def _mock_client():
    return MagicMock()


# --- Spreadsheet CRUD ---


@patch("feishu_cli.commands.sheets.create_client")
def test_sheets_create(mock_create_client):
    mock_client = _mock_client()
    mock_client.sheets.v3.spreadsheet.create.return_value = _mock_success_response()
    mock_create_client.return_value = mock_client
    result = runner.invoke(sheets_app, ["create", "--title", "Test Sheet"])
    assert result.exit_code == 0


@patch("feishu_cli.commands.sheets.create_client")
def test_sheets_create_with_folder(mock_create_client):
    mock_client = _mock_client()
    mock_client.sheets.v3.spreadsheet.create.return_value = _mock_success_response()
    mock_create_client.return_value = mock_client
    result = runner.invoke(
        sheets_app, ["create", "--title", "Test", "--folder-token", "fldcnXXX"]
    )
    assert result.exit_code == 0


@patch("feishu_cli.commands.sheets.create_client")
def test_sheets_get(mock_create_client):
    mock_client = _mock_client()
    mock_client.sheets.v3.spreadsheet.get.return_value = _mock_success_response()
    mock_create_client.return_value = mock_client
    result = runner.invoke(sheets_app, ["get", "--token", "shtcnXXX"])
    assert result.exit_code == 0


@patch("feishu_cli.commands.sheets.create_client")
def test_sheets_update(mock_create_client):
    mock_client = _mock_client()
    mock_client.sheets.v3.spreadsheet.patch.return_value = _mock_success_response()
    mock_create_client.return_value = mock_client
    result = runner.invoke(
        sheets_app, ["update", "--token", "shtcnXXX", "--title", "New Title"]
    )
    assert result.exit_code == 0


# --- Sheet list ---


@patch("feishu_cli.commands.sheets.create_client")
def test_sheet_list(mock_create_client):
    mock_client = _mock_client()
    mock_client.sheets.v3.spreadsheet_sheet.query.return_value = (
        _mock_success_response()
    )
    mock_create_client.return_value = mock_client
    result = runner.invoke(sheets_app, ["sheet", "list", "--token", "shtcnXXX"])
    assert result.exit_code == 0


# --- Filter CRUD ---


@patch("feishu_cli.commands.sheets.create_client")
def test_filter_create(mock_create_client):
    mock_client = _mock_client()
    mock_client.sheets.v3.spreadsheet_sheet_filter.create.return_value = (
        _mock_success_response()
    )
    mock_create_client.return_value = mock_client
    data = json.dumps({"range": "A1:B2", "col": "A", "condition": {}})
    result = runner.invoke(
        sheets_app,
        ["filter", "create", "--token", "shtcnXXX", "--sheet-id", "s1", "--data", data],
    )
    assert result.exit_code == 0


@patch("feishu_cli.commands.sheets.create_client")
def test_filter_get(mock_create_client):
    mock_client = _mock_client()
    mock_client.sheets.v3.spreadsheet_sheet_filter.get.return_value = (
        _mock_success_response()
    )
    mock_create_client.return_value = mock_client
    result = runner.invoke(
        sheets_app, ["filter", "get", "--token", "shtcnXXX", "--sheet-id", "s1"]
    )
    assert result.exit_code == 0


@patch("feishu_cli.commands.sheets.create_client")
def test_filter_update(mock_create_client):
    mock_client = _mock_client()
    mock_client.sheets.v3.spreadsheet_sheet_filter.update.return_value = (
        _mock_success_response()
    )
    mock_create_client.return_value = mock_client
    data = json.dumps({"col": "A", "condition": {}})
    result = runner.invoke(
        sheets_app,
        ["filter", "update", "--token", "shtcnXXX", "--sheet-id", "s1", "--data", data],
    )
    assert result.exit_code == 0


@patch("feishu_cli.commands.sheets.create_client")
def test_filter_delete(mock_create_client):
    mock_client = _mock_client()
    mock_client.sheets.v3.spreadsheet_sheet_filter.delete.return_value = (
        _mock_success_response()
    )
    mock_create_client.return_value = mock_client
    result = runner.invoke(
        sheets_app, ["filter", "delete", "--token", "shtcnXXX", "--sheet-id", "s1"]
    )
    assert result.exit_code == 0


# --- Filter View CRUD ---


@patch("feishu_cli.commands.sheets.create_client")
def test_filter_view_create(mock_create_client):
    mock_client = _mock_client()
    mock_client.sheets.v3.spreadsheet_sheet_filter_view.create.return_value = (
        _mock_success_response()
    )
    mock_create_client.return_value = mock_client
    data = json.dumps({"filter_view_name": "view1", "range": "A1:B2"})
    result = runner.invoke(
        sheets_app,
        [
            "filter-view", "create",
            "--token", "shtcnXXX", "--sheet-id", "s1", "--data", data,
        ],
    )
    assert result.exit_code == 0


@patch("feishu_cli.commands.sheets.create_client")
def test_filter_view_list(mock_create_client):
    mock_client = _mock_client()
    mock_client.sheets.v3.spreadsheet_sheet_filter_view.query.return_value = (
        _mock_success_response()
    )
    mock_create_client.return_value = mock_client
    result = runner.invoke(
        sheets_app,
        ["filter-view", "list", "--token", "shtcnXXX", "--sheet-id", "s1"],
    )
    assert result.exit_code == 0


@patch("feishu_cli.commands.sheets.create_client")
def test_filter_view_get(mock_create_client):
    mock_client = _mock_client()
    mock_client.sheets.v3.spreadsheet_sheet_filter_view.get.return_value = (
        _mock_success_response()
    )
    mock_create_client.return_value = mock_client
    result = runner.invoke(
        sheets_app,
        [
            "filter-view", "get",
            "--token", "shtcnXXX", "--sheet-id", "s1",
            "--filter-view-id", "fv1",
        ],
    )
    assert result.exit_code == 0


@patch("feishu_cli.commands.sheets.create_client")
def test_filter_view_update(mock_create_client):
    mock_client = _mock_client()
    mock_client.sheets.v3.spreadsheet_sheet_filter_view.patch.return_value = (
        _mock_success_response()
    )
    mock_create_client.return_value = mock_client
    data = json.dumps({"filter_view_name": "updated"})
    result = runner.invoke(
        sheets_app,
        [
            "filter-view", "update",
            "--token", "shtcnXXX", "--sheet-id", "s1",
            "--filter-view-id", "fv1", "--data", data,
        ],
    )
    assert result.exit_code == 0


@patch("feishu_cli.commands.sheets.create_client")
def test_filter_view_delete(mock_create_client):
    mock_client = _mock_client()
    mock_client.sheets.v3.spreadsheet_sheet_filter_view.delete.return_value = (
        _mock_success_response()
    )
    mock_create_client.return_value = mock_client
    result = runner.invoke(
        sheets_app,
        [
            "filter-view", "delete",
            "--token", "shtcnXXX", "--sheet-id", "s1",
            "--filter-view-id", "fv1",
        ],
    )
    assert result.exit_code == 0


# --- Float Image CRUD ---


@patch("feishu_cli.commands.sheets.create_client")
def test_float_image_create(mock_create_client):
    mock_client = _mock_client()
    mock_client.sheets.v3.spreadsheet_sheet_float_image.create.return_value = (
        _mock_success_response()
    )
    mock_create_client.return_value = mock_client
    data = json.dumps({"float_image_token": "img_xxx"})
    result = runner.invoke(
        sheets_app,
        [
            "float-image", "create",
            "--token", "shtcnXXX", "--sheet-id", "s1", "--data", data,
        ],
    )
    assert result.exit_code == 0


@patch("feishu_cli.commands.sheets.create_client")
def test_float_image_list(mock_create_client):
    mock_client = _mock_client()
    mock_client.sheets.v3.spreadsheet_sheet_float_image.query.return_value = (
        _mock_success_response()
    )
    mock_create_client.return_value = mock_client
    result = runner.invoke(
        sheets_app,
        ["float-image", "list", "--token", "shtcnXXX", "--sheet-id", "s1"],
    )
    assert result.exit_code == 0


@patch("feishu_cli.commands.sheets.create_client")
def test_float_image_get(mock_create_client):
    mock_client = _mock_client()
    mock_client.sheets.v3.spreadsheet_sheet_float_image.get.return_value = (
        _mock_success_response()
    )
    mock_create_client.return_value = mock_client
    result = runner.invoke(
        sheets_app,
        [
            "float-image", "get",
            "--token", "shtcnXXX", "--sheet-id", "s1",
            "--float-image-id", "fi1",
        ],
    )
    assert result.exit_code == 0


@patch("feishu_cli.commands.sheets.create_client")
def test_float_image_update(mock_create_client):
    mock_client = _mock_client()
    mock_client.sheets.v3.spreadsheet_sheet_float_image.patch.return_value = (
        _mock_success_response()
    )
    mock_create_client.return_value = mock_client
    data = json.dumps({"width": 100})
    result = runner.invoke(
        sheets_app,
        [
            "float-image", "update",
            "--token", "shtcnXXX", "--sheet-id", "s1",
            "--float-image-id", "fi1", "--data", data,
        ],
    )
    assert result.exit_code == 0


@patch("feishu_cli.commands.sheets.create_client")
def test_float_image_delete(mock_create_client):
    mock_client = _mock_client()
    mock_client.sheets.v3.spreadsheet_sheet_float_image.delete.return_value = (
        _mock_success_response()
    )
    mock_create_client.return_value = mock_client
    result = runner.invoke(
        sheets_app,
        [
            "float-image", "delete",
            "--token", "shtcnXXX", "--sheet-id", "s1",
            "--float-image-id", "fi1",
        ],
    )
    assert result.exit_code == 0
