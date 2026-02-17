"""Sheets commands for Feishu CLI."""

import json
from typing import Optional

import typer
from lark_oapi.api.sheets.v3 import (
    CreateSpreadsheetRequest,
    CreateSpreadsheetSheetFilterRequest,
    CreateSpreadsheetSheetFilterViewRequest,
    CreateSpreadsheetSheetFloatImageRequest,
    DeleteSpreadsheetSheetFilterRequest,
    DeleteSpreadsheetSheetFilterViewRequest,
    DeleteSpreadsheetSheetFloatImageRequest,
    GetSpreadsheetRequest,
    GetSpreadsheetSheetFilterRequest,
    GetSpreadsheetSheetFilterViewRequest,
    GetSpreadsheetSheetFloatImageRequest,
    PatchSpreadsheetRequest,
    PatchSpreadsheetSheetFilterViewRequest,
    PatchSpreadsheetSheetFloatImageRequest,
    QuerySpreadsheetSheetFilterViewRequest,
    QuerySpreadsheetSheetFloatImageRequest,
    QuerySpreadsheetSheetRequest,
    Spreadsheet,
    UpdateSpreadsheetProperties,
    UpdateSpreadsheetSheetFilterRequest,
    CreateSheetFilter,
    UpdateSheetFilter,
    FilterView,
    FloatImage,
)

from feishu_cli.client import create_client
from feishu_cli.runtime import call_api
from feishu_cli.utils.output import format_response

sheets_app = typer.Typer(name="sheets", help="Spreadsheet operations.", no_args_is_help=True)
sheet_app = typer.Typer(name="sheet", help="Sheet operations.", no_args_is_help=True)
filter_app = typer.Typer(name="filter", help="Sheet filter operations.", no_args_is_help=True)
filter_view_app = typer.Typer(
    name="filter-view", help="Sheet filter view operations.", no_args_is_help=True
)
float_image_app = typer.Typer(
    name="float-image", help="Sheet float image operations.", no_args_is_help=True
)

sheets_app.add_typer(sheet_app)
sheets_app.add_typer(filter_app)
sheets_app.add_typer(filter_view_app)
sheets_app.add_typer(float_image_app)


# --- Spreadsheet CRUD ---


@sheets_app.command("create")
def spreadsheet_create(
    title: str = typer.Option(..., help="Spreadsheet title"),
    folder_token: Optional[str] = typer.Option(None, help="Parent folder token"),
) -> None:
    """Create a new spreadsheet."""
    client = create_client()
    body_builder = Spreadsheet.builder().title(title)
    if folder_token is not None:
        body_builder = body_builder.folder_token(folder_token)
    request = (
        CreateSpreadsheetRequest.builder()
        .request_body(body_builder.build())
        .build()
    )
    response = call_api(client, client.sheets.v3.spreadsheet.create, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@sheets_app.command("get")
def spreadsheet_get(
    token: str = typer.Option(..., help="Spreadsheet token"),
) -> None:
    """Get spreadsheet info."""
    client = create_client()
    request = (
        GetSpreadsheetRequest.builder()
        .spreadsheet_token(token)
        .build()
    )
    response = call_api(client, client.sheets.v3.spreadsheet.get, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@sheets_app.command("update")
def spreadsheet_update(
    token: str = typer.Option(..., help="Spreadsheet token"),
    title: Optional[str] = typer.Option(None, help="New title"),
) -> None:
    """Update spreadsheet properties."""
    client = create_client()
    props_builder = UpdateSpreadsheetProperties.builder()
    if title is not None:
        props_builder = props_builder.title(title)
    request = (
        PatchSpreadsheetRequest.builder()
        .spreadsheet_token(token)
        .request_body(props_builder.build())
        .build()
    )
    response = call_api(client, client.sheets.v3.spreadsheet.patch, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


# --- Sheet ---


@sheet_app.command("list")
def sheet_list(
    token: str = typer.Option(..., help="Spreadsheet token"),
) -> None:
    """List all sheets in a spreadsheet."""
    client = create_client()
    request = (
        QuerySpreadsheetSheetRequest.builder()
        .spreadsheet_token(token)
        .build()
    )
    response = call_api(client, client.sheets.v3.spreadsheet_sheet.query, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


# --- Filter ---


def _parse_json(data: str) -> dict:
    """Parse a JSON string, raising a typer error on failure."""
    try:
        return json.loads(data)
    except json.JSONDecodeError as exc:
        raise typer.BadParameter(f"Invalid JSON: {exc}") from exc


@filter_app.command("create")
def filter_create(
    token: str = typer.Option(..., help="Spreadsheet token"),
    sheet_id: str = typer.Option(..., help="Sheet ID"),
    data: str = typer.Option(..., help="Filter JSON data"),
) -> None:
    """Create a sheet filter."""
    client = create_client()
    body = CreateSheetFilter(_parse_json(data))
    request = (
        CreateSpreadsheetSheetFilterRequest.builder()
        .spreadsheet_token(token)
        .sheet_id(sheet_id)
        .request_body(body)
        .build()
    )
    response = call_api(
        client,
        client.sheets.v3.spreadsheet_sheet_filter.create,
        request,
    )
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@filter_app.command("get")
def filter_get(
    token: str = typer.Option(..., help="Spreadsheet token"),
    sheet_id: str = typer.Option(..., help="Sheet ID"),
) -> None:
    """Get a sheet filter."""
    client = create_client()
    request = (
        GetSpreadsheetSheetFilterRequest.builder()
        .spreadsheet_token(token)
        .sheet_id(sheet_id)
        .build()
    )
    response = call_api(client, client.sheets.v3.spreadsheet_sheet_filter.get, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@filter_app.command("update")
def filter_update(
    token: str = typer.Option(..., help="Spreadsheet token"),
    sheet_id: str = typer.Option(..., help="Sheet ID"),
    data: str = typer.Option(..., help="Filter JSON data"),
) -> None:
    """Update a sheet filter."""
    client = create_client()
    body = UpdateSheetFilter(_parse_json(data))
    request = (
        UpdateSpreadsheetSheetFilterRequest.builder()
        .spreadsheet_token(token)
        .sheet_id(sheet_id)
        .request_body(body)
        .build()
    )
    response = call_api(
        client,
        client.sheets.v3.spreadsheet_sheet_filter.update,
        request,
    )
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@filter_app.command("delete")
def filter_delete(
    token: str = typer.Option(..., help="Spreadsheet token"),
    sheet_id: str = typer.Option(..., help="Sheet ID"),
) -> None:
    """Delete a sheet filter."""
    client = create_client()
    request = (
        DeleteSpreadsheetSheetFilterRequest.builder()
        .spreadsheet_token(token)
        .sheet_id(sheet_id)
        .build()
    )
    response = call_api(
        client,
        client.sheets.v3.spreadsheet_sheet_filter.delete,
        request,
    )
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


# --- Filter View ---


@filter_view_app.command("create")
def filter_view_create(
    token: str = typer.Option(..., help="Spreadsheet token"),
    sheet_id: str = typer.Option(..., help="Sheet ID"),
    data: str = typer.Option(..., help="Filter view JSON data"),
) -> None:
    """Create a filter view."""
    client = create_client()
    body = FilterView(_parse_json(data))
    request = (
        CreateSpreadsheetSheetFilterViewRequest.builder()
        .spreadsheet_token(token)
        .sheet_id(sheet_id)
        .request_body(body)
        .build()
    )
    response = call_api(
        client,
        client.sheets.v3.spreadsheet_sheet_filter_view.create,
        request,
    )
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@filter_view_app.command("get")
def filter_view_get(
    token: str = typer.Option(..., help="Spreadsheet token"),
    sheet_id: str = typer.Option(..., help="Sheet ID"),
    filter_view_id: str = typer.Option(..., help="Filter view ID"),
) -> None:
    """Get a filter view."""
    client = create_client()
    request = (
        GetSpreadsheetSheetFilterViewRequest.builder()
        .spreadsheet_token(token)
        .sheet_id(sheet_id)
        .filter_view_id(filter_view_id)
        .build()
    )
    response = call_api(
        client,
        client.sheets.v3.spreadsheet_sheet_filter_view.get,
        request,
    )
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@filter_view_app.command("list")
def filter_view_list(
    token: str = typer.Option(..., help="Spreadsheet token"),
    sheet_id: str = typer.Option(..., help="Sheet ID"),
) -> None:
    """List all filter views."""
    client = create_client()
    request = (
        QuerySpreadsheetSheetFilterViewRequest.builder()
        .spreadsheet_token(token)
        .sheet_id(sheet_id)
        .build()
    )
    response = call_api(
        client,
        client.sheets.v3.spreadsheet_sheet_filter_view.query,
        request,
    )
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@filter_view_app.command("update")
def filter_view_update(
    token: str = typer.Option(..., help="Spreadsheet token"),
    sheet_id: str = typer.Option(..., help="Sheet ID"),
    filter_view_id: str = typer.Option(..., help="Filter view ID"),
    data: str = typer.Option(..., help="Filter view JSON data"),
) -> None:
    """Update a filter view."""
    client = create_client()
    body = FilterView(_parse_json(data))
    request = (
        PatchSpreadsheetSheetFilterViewRequest.builder()
        .spreadsheet_token(token)
        .sheet_id(sheet_id)
        .filter_view_id(filter_view_id)
        .request_body(body)
        .build()
    )
    response = call_api(
        client,
        client.sheets.v3.spreadsheet_sheet_filter_view.patch,
        request,
    )
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@filter_view_app.command("delete")
def filter_view_delete(
    token: str = typer.Option(..., help="Spreadsheet token"),
    sheet_id: str = typer.Option(..., help="Sheet ID"),
    filter_view_id: str = typer.Option(..., help="Filter view ID"),
) -> None:
    """Delete a filter view."""
    client = create_client()
    request = (
        DeleteSpreadsheetSheetFilterViewRequest.builder()
        .spreadsheet_token(token)
        .sheet_id(sheet_id)
        .filter_view_id(filter_view_id)
        .build()
    )
    response = call_api(
        client,
        client.sheets.v3.spreadsheet_sheet_filter_view.delete,
        request,
    )
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


# --- Float Image ---


@float_image_app.command("create")
def float_image_create(
    token: str = typer.Option(..., help="Spreadsheet token"),
    sheet_id: str = typer.Option(..., help="Sheet ID"),
    data: str = typer.Option(..., help="Float image JSON data"),
) -> None:
    """Create a float image."""
    client = create_client()
    body = FloatImage(_parse_json(data))
    request = (
        CreateSpreadsheetSheetFloatImageRequest.builder()
        .spreadsheet_token(token)
        .sheet_id(sheet_id)
        .request_body(body)
        .build()
    )
    response = call_api(
        client,
        client.sheets.v3.spreadsheet_sheet_float_image.create,
        request,
    )
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@float_image_app.command("get")
def float_image_get(
    token: str = typer.Option(..., help="Spreadsheet token"),
    sheet_id: str = typer.Option(..., help="Sheet ID"),
    float_image_id: str = typer.Option(..., help="Float image ID"),
) -> None:
    """Get a float image."""
    client = create_client()
    request = (
        GetSpreadsheetSheetFloatImageRequest.builder()
        .spreadsheet_token(token)
        .sheet_id(sheet_id)
        .float_image_id(float_image_id)
        .build()
    )
    response = call_api(
        client,
        client.sheets.v3.spreadsheet_sheet_float_image.get,
        request,
    )
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@float_image_app.command("list")
def float_image_list(
    token: str = typer.Option(..., help="Spreadsheet token"),
    sheet_id: str = typer.Option(..., help="Sheet ID"),
) -> None:
    """List all float images."""
    client = create_client()
    request = (
        QuerySpreadsheetSheetFloatImageRequest.builder()
        .spreadsheet_token(token)
        .sheet_id(sheet_id)
        .build()
    )
    response = call_api(
        client,
        client.sheets.v3.spreadsheet_sheet_float_image.query,
        request,
    )
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@float_image_app.command("update")
def float_image_update(
    token: str = typer.Option(..., help="Spreadsheet token"),
    sheet_id: str = typer.Option(..., help="Sheet ID"),
    float_image_id: str = typer.Option(..., help="Float image ID"),
    data: str = typer.Option(..., help="Float image JSON data"),
) -> None:
    """Update a float image."""
    client = create_client()
    body = FloatImage(_parse_json(data))
    request = (
        PatchSpreadsheetSheetFloatImageRequest.builder()
        .spreadsheet_token(token)
        .sheet_id(sheet_id)
        .float_image_id(float_image_id)
        .request_body(body)
        .build()
    )
    response = call_api(
        client,
        client.sheets.v3.spreadsheet_sheet_float_image.patch,
        request,
    )
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@float_image_app.command("delete")
def float_image_delete(
    token: str = typer.Option(..., help="Spreadsheet token"),
    sheet_id: str = typer.Option(..., help="Sheet ID"),
    float_image_id: str = typer.Option(..., help="Float image ID"),
) -> None:
    """Delete a float image."""
    client = create_client()
    request = (
        DeleteSpreadsheetSheetFloatImageRequest.builder()
        .spreadsheet_token(token)
        .sheet_id(sheet_id)
        .float_image_id(float_image_id)
        .build()
    )
    response = call_api(
        client,
        client.sheets.v3.spreadsheet_sheet_float_image.delete,
        request,
    )
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)
