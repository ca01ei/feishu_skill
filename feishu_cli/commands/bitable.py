"""Bitable (multidimensional table) commands for Feishu CLI."""

import json
from pathlib import Path
from typing import Optional

import typer
from lark_oapi.api.bitable.v1 import (
    CopyAppRequest,
    CopyAppRequestBody,
    CreateAppRequest,
    CreateAppTableFieldRequest,
    CreateAppTableRecordRequest,
    CreateAppTableRequest,
    CreateAppTableRequestBody,
    CreateAppTableViewRequest,
    DeleteAppTableFieldRequest,
    DeleteAppTableRecordRequest,
    DeleteAppTableRequest,
    DeleteAppTableViewRequest,
    GetAppRequest,
    GetAppTableRecordRequest,
    GetAppTableViewRequest,
    ListAppTableFieldRequest,
    ListAppTableRecordRequest,
    ListAppTableRequest,
    ListAppTableViewRequest,
    PatchAppTableRequest,
    PatchAppTableRequestBody,
    UpdateAppRequest,
    UpdateAppRequestBody,
    UpdateAppTableFieldRequest,
    UpdateAppTableRecordRequest,
    AppTable,
    AppTableField,
    AppTableRecord,
    AppTableView,
    ReqApp,
    ReqTable,
)

from feishu_cli.client import create_client
from feishu_cli.runtime import call_api
from feishu_cli.utils.output import format_error, format_response

bitable_app = typer.Typer(
    name="bitable", help="Bitable (multidimensional table) operations.", no_args_is_help=True
)
table_app = typer.Typer(name="table", help="Table operations.", no_args_is_help=True)
record_app = typer.Typer(name="record", help="Record operations.", no_args_is_help=True)
field_app = typer.Typer(name="field", help="Field operations.", no_args_is_help=True)
view_app = typer.Typer(name="view", help="View operations.", no_args_is_help=True)

bitable_app.add_typer(table_app, name="table")
bitable_app.add_typer(record_app, name="record")
bitable_app.add_typer(field_app, name="field")
bitable_app.add_typer(view_app, name="view")


def _parse_json(data: str) -> dict:
    """Parse JSON from string or @file reference."""
    try:
        if data.startswith("@"):
            file_path = Path(data[1:])
            return json.loads(file_path.read_text(encoding="utf-8"))
        return json.loads(data)
    except FileNotFoundError:
        _json_param_error(f"JSON file not found: {data[1:]}")
    except json.JSONDecodeError as exc:
        _json_param_error(f"Invalid JSON: {exc}")
    except OSError as exc:
        _json_param_error(f"Failed to read JSON file: {exc}")
    return {}


def _json_param_error(message: str) -> None:
    """Emit a structured parameter error and exit with code 2."""
    typer.echo(format_error(code=2, msg=message))
    raise typer.Exit(code=2)


# ── App-level commands ──────────────────────────────────────────────────────


@bitable_app.command("create")
def app_create(
    name: str = typer.Option(..., help="App name"),
    folder_token: Optional[str] = typer.Option(None, help="Folder token"),
) -> None:
    """Create a new bitable app."""
    client = create_client()
    body_builder = ReqApp.builder().name(name)
    if folder_token is not None:
        body_builder = body_builder.folder_token(folder_token)
    body = body_builder.build()
    request = CreateAppRequest.builder().request_body(body).build()
    response = call_api(client, client.bitable.v1.app.create, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@bitable_app.command("get")
def app_get(
    app_token: str = typer.Option(..., help="App token"),
) -> None:
    """Get bitable app metadata."""
    client = create_client()
    request = GetAppRequest.builder().app_token(app_token).build()
    response = call_api(client, client.bitable.v1.app.get, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@bitable_app.command("update")
def app_update(
    app_token: str = typer.Option(..., help="App token"),
    name: Optional[str] = typer.Option(None, help="New app name"),
) -> None:
    """Update bitable app."""
    client = create_client()
    if name is None:
        _json_param_error("At least one field to update must be provided.")
    body = UpdateAppRequestBody.builder().name(name).build()
    request = UpdateAppRequest.builder().app_token(app_token).request_body(body).build()
    response = call_api(client, client.bitable.v1.app.update, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@bitable_app.command("copy")
def app_copy(
    app_token: str = typer.Option(..., help="App token"),
    name: Optional[str] = typer.Option(None, help="Copy name"),
    folder_token: Optional[str] = typer.Option(None, help="Target folder token"),
) -> None:
    """Copy a bitable app."""
    client = create_client()
    body_builder = CopyAppRequestBody.builder()
    if name is not None:
        body_builder = body_builder.name(name)
    if folder_token is not None:
        body_builder = body_builder.folder_token(folder_token)
    body = body_builder.build()
    request = CopyAppRequest.builder().app_token(app_token).request_body(body).build()
    response = call_api(client, client.bitable.v1.app.copy, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


# ── Table commands ──────────────────────────────────────────────────────────


@table_app.command("list")
def table_list(
    app_token: str = typer.Option(..., help="App token"),
    page_size: int = typer.Option(20, help="Page size"),
    page_token: str = typer.Option("", help="Page token"),
) -> None:
    """List tables in a bitable app."""
    client = create_client()
    builder = ListAppTableRequest.builder().app_token(app_token).page_size(page_size)
    if page_token:
        builder = builder.page_token(page_token)
    response = call_api(client, client.bitable.v1.app_table.list, builder.build())
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@table_app.command("create")
def table_create(
    app_token: str = typer.Option(..., help="App token"),
    name: str = typer.Option(..., help="Table name"),
) -> None:
    """Create a table."""
    client = create_client()
    table = ReqTable.builder().name(name).build()
    body = CreateAppTableRequestBody.builder().table(table).build()
    request = CreateAppTableRequest.builder().app_token(app_token).request_body(body).build()
    response = call_api(client, client.bitable.v1.app_table.create, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@table_app.command("delete")
def table_delete(
    app_token: str = typer.Option(..., help="App token"),
    table_id: str = typer.Option(..., help="Table ID"),
) -> None:
    """Delete a table."""
    client = create_client()
    request = DeleteAppTableRequest.builder().app_token(app_token).table_id(table_id).build()
    response = call_api(client, client.bitable.v1.app_table.delete, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@table_app.command("patch")
def table_patch(
    app_token: str = typer.Option(..., help="App token"),
    table_id: str = typer.Option(..., help="Table ID"),
    name: str = typer.Option(..., help="New table name"),
) -> None:
    """Update a table name."""
    client = create_client()
    body = PatchAppTableRequestBody.builder().name(name).build()
    request = (
        PatchAppTableRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .request_body(body)
        .build()
    )
    response = call_api(client, client.bitable.v1.app_table.patch, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


# ── Record commands ─────────────────────────────────────────────────────────


@record_app.command("list")
def record_list(
    app_token: str = typer.Option(..., help="App token"),
    table_id: str = typer.Option(..., help="Table ID"),
    page_size: int = typer.Option(20, help="Page size"),
    page_token: str = typer.Option("", help="Page token"),
) -> None:
    """List records in a table."""
    client = create_client()
    builder = (
        ListAppTableRecordRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .page_size(page_size)
    )
    if page_token:
        builder = builder.page_token(page_token)
    response = call_api(client, client.bitable.v1.app_table_record.list, builder.build())
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@record_app.command("get")
def record_get(
    app_token: str = typer.Option(..., help="App token"),
    table_id: str = typer.Option(..., help="Table ID"),
    record_id: str = typer.Option(..., help="Record ID"),
) -> None:
    """Get a single record."""
    client = create_client()
    request = (
        GetAppTableRecordRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .record_id(record_id)
        .build()
    )
    response = call_api(client, client.bitable.v1.app_table_record.get, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@record_app.command("create")
def record_create(
    app_token: str = typer.Option(..., help="App token"),
    table_id: str = typer.Option(..., help="Table ID"),
    fields: str = typer.Option(..., help="Fields JSON or @file.json"),
) -> None:
    """Create a record."""
    client = create_client()
    data = _parse_json(fields)
    record = AppTableRecord.builder().fields(data).build()
    request = (
        CreateAppTableRecordRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .request_body(record)
        .build()
    )
    response = call_api(client, client.bitable.v1.app_table_record.create, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@record_app.command("update")
def record_update(
    app_token: str = typer.Option(..., help="App token"),
    table_id: str = typer.Option(..., help="Table ID"),
    record_id: str = typer.Option(..., help="Record ID"),
    fields: str = typer.Option(..., help="Fields JSON or @file.json"),
) -> None:
    """Update a record."""
    client = create_client()
    data = _parse_json(fields)
    record = AppTableRecord.builder().fields(data).build()
    request = (
        UpdateAppTableRecordRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .record_id(record_id)
        .request_body(record)
        .build()
    )
    response = call_api(client, client.bitable.v1.app_table_record.update, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@record_app.command("delete")
def record_delete(
    app_token: str = typer.Option(..., help="App token"),
    table_id: str = typer.Option(..., help="Table ID"),
    record_id: str = typer.Option(..., help="Record ID"),
) -> None:
    """Delete a record."""
    client = create_client()
    request = (
        DeleteAppTableRecordRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .record_id(record_id)
        .build()
    )
    response = call_api(client, client.bitable.v1.app_table_record.delete, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


# ── Field commands ──────────────────────────────────────────────────────────


@field_app.command("list")
def field_list(
    app_token: str = typer.Option(..., help="App token"),
    table_id: str = typer.Option(..., help="Table ID"),
    page_size: int = typer.Option(20, help="Page size"),
    page_token: str = typer.Option("", help="Page token"),
) -> None:
    """List fields in a table."""
    client = create_client()
    builder = (
        ListAppTableFieldRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .page_size(page_size)
    )
    if page_token:
        builder = builder.page_token(page_token)
    response = call_api(client, client.bitable.v1.app_table_field.list, builder.build())
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@field_app.command("create")
def field_create(
    app_token: str = typer.Option(..., help="App token"),
    table_id: str = typer.Option(..., help="Table ID"),
    field_name: str = typer.Option(..., help="Field name"),
    field_type: int = typer.Option(..., help="Field type (1=text, 2=number, etc.)"),
) -> None:
    """Create a field."""
    client = create_client()
    field = AppTableField.builder().field_name(field_name).type(field_type).build()
    request = (
        CreateAppTableFieldRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .request_body(field)
        .build()
    )
    response = call_api(client, client.bitable.v1.app_table_field.create, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@field_app.command("update")
def field_update(
    app_token: str = typer.Option(..., help="App token"),
    table_id: str = typer.Option(..., help="Table ID"),
    field_id: str = typer.Option(..., help="Field ID"),
    field_name: str = typer.Option(..., help="New field name"),
    field_type: int = typer.Option(..., help="Field type"),
) -> None:
    """Update a field."""
    client = create_client()
    field = AppTableField.builder().field_name(field_name).type(field_type).build()
    request = (
        UpdateAppTableFieldRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .field_id(field_id)
        .request_body(field)
        .build()
    )
    response = call_api(client, client.bitable.v1.app_table_field.update, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@field_app.command("delete")
def field_delete(
    app_token: str = typer.Option(..., help="App token"),
    table_id: str = typer.Option(..., help="Table ID"),
    field_id: str = typer.Option(..., help="Field ID"),
) -> None:
    """Delete a field."""
    client = create_client()
    request = (
        DeleteAppTableFieldRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .field_id(field_id)
        .build()
    )
    response = call_api(client, client.bitable.v1.app_table_field.delete, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


# ── View commands ───────────────────────────────────────────────────────────


@view_app.command("list")
def view_list(
    app_token: str = typer.Option(..., help="App token"),
    table_id: str = typer.Option(..., help="Table ID"),
    page_size: int = typer.Option(20, help="Page size"),
    page_token: str = typer.Option("", help="Page token"),
) -> None:
    """List views of a table."""
    client = create_client()
    builder = (
        ListAppTableViewRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .page_size(page_size)
    )
    if page_token:
        builder = builder.page_token(page_token)
    response = call_api(client, client.bitable.v1.app_table_view.list, builder.build())
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@view_app.command("get")
def view_get(
    app_token: str = typer.Option(..., help="App token"),
    table_id: str = typer.Option(..., help="Table ID"),
    view_id: str = typer.Option(..., help="View ID"),
) -> None:
    """Get a view."""
    client = create_client()
    request = (
        GetAppTableViewRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .view_id(view_id)
        .build()
    )
    response = call_api(client, client.bitable.v1.app_table_view.get, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@view_app.command("create")
def view_create(
    app_token: str = typer.Option(..., help="App token"),
    table_id: str = typer.Option(..., help="Table ID"),
    view_name: str = typer.Option(..., help="View name"),
    view_type: str = typer.Option("grid", help="View type (grid/kanban/gallery/gantt/form)"),
) -> None:
    """Create a view."""
    client = create_client()
    view = AppTableView.builder().view_name(view_name).view_type(view_type).build()
    request = (
        CreateAppTableViewRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .request_body(view)
        .build()
    )
    response = call_api(client, client.bitable.v1.app_table_view.create, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@view_app.command("delete")
def view_delete(
    app_token: str = typer.Option(..., help="App token"),
    table_id: str = typer.Option(..., help="Table ID"),
    view_id: str = typer.Option(..., help="View ID"),
) -> None:
    """Delete a view."""
    client = create_client()
    request = (
        DeleteAppTableViewRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .view_id(view_id)
        .build()
    )
    response = call_api(client, client.bitable.v1.app_table_view.delete, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)
