"""Docx document commands."""

import json
from pathlib import Path
from typing import Optional

import typer
from lark_oapi.api.docx.v1 import (
    BatchDeleteDocumentBlockChildrenRequest,
    BatchDeleteDocumentBlockChildrenRequestBody,
    CreateDocumentBlockChildrenRequest,
    CreateDocumentBlockChildrenRequestBody,
    CreateDocumentRequest,
    CreateDocumentRequestBody,
    GetDocumentBlockRequest,
    GetDocumentRequest,
    ListDocumentBlockRequest,
    RawContentDocumentRequest,
)

from feishu_cli.client import create_client
from feishu_cli.runtime import call_api
from feishu_cli.utils.output import format_error, format_response

docx_app = typer.Typer(name="docx", help="Docx document operations.", no_args_is_help=True)
block_app = typer.Typer(name="block", help="Document block operations.", no_args_is_help=True)
docx_app.add_typer(block_app)


def _load_json_data(data: str) -> dict:
    """Load JSON from a raw string or @file.json path."""
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


@docx_app.command("create")
def create_document(
    title: str = typer.Option(..., help="Document title"),
    folder_token: Optional[str] = typer.Option(None, help="Folder token"),
) -> None:
    """Create a new document."""
    client = create_client()
    body_builder = CreateDocumentRequestBody.builder().title(title)
    if folder_token is not None:
        body_builder = body_builder.folder_token(folder_token)
    request = (
        CreateDocumentRequest.builder()
        .request_body(body_builder.build())
        .build()
    )
    response = call_api(client, client.docx.v1.document.create, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@docx_app.command("get")
def get_document(
    token: str = typer.Option(..., help="Document token"),
) -> None:
    """Get document metadata."""
    client = create_client()
    request = GetDocumentRequest.builder().document_id(token).build()
    response = call_api(client, client.docx.v1.document.get, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@docx_app.command("content")
def get_raw_content(
    token: str = typer.Option(..., help="Document token"),
    lang: Optional[int] = typer.Option(None, help="Language (0=default, 1=zh, 2=en, 3=ja)"),
) -> None:
    """Get document raw text content."""
    client = create_client()
    builder = RawContentDocumentRequest.builder().document_id(token)
    if lang is not None:
        builder = builder.lang(lang)
    request = builder.build()
    response = call_api(client, client.docx.v1.document.raw_content, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@block_app.command("list")
def list_blocks(
    token: str = typer.Option(..., help="Document token"),
    page_size: Optional[int] = typer.Option(None, help="Page size"),
    page_token: Optional[str] = typer.Option(None, help="Page token"),
) -> None:
    """List document blocks."""
    client = create_client()
    builder = ListDocumentBlockRequest.builder().document_id(token)
    if page_size is not None:
        builder = builder.page_size(page_size)
    if page_token is not None:
        builder = builder.page_token(page_token)
    request = builder.build()
    response = call_api(client, client.docx.v1.document_block.list, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@block_app.command("get")
def get_block(
    token: str = typer.Option(..., help="Document token"),
    block_id: str = typer.Option(..., help="Block ID"),
) -> None:
    """Get a specific block."""
    client = create_client()
    request = (
        GetDocumentBlockRequest.builder()
        .document_id(token)
        .block_id(block_id)
        .build()
    )
    response = call_api(client, client.docx.v1.document_block.get, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@block_app.command("create")
def create_block_children(
    token: str = typer.Option(..., help="Document token"),
    block_id: str = typer.Option(..., help="Parent block ID"),
    data: str = typer.Option(..., help="JSON data or @file.json path"),
) -> None:
    """Create child blocks under a parent block."""
    client = create_client()
    json_data = _load_json_data(data)
    body = CreateDocumentBlockChildrenRequestBody(json_data)
    request = (
        CreateDocumentBlockChildrenRequest.builder()
        .document_id(token)
        .block_id(block_id)
        .request_body(body)
        .build()
    )
    response = call_api(client, client.docx.v1.document_block_children.create, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@block_app.command("delete")
def delete_block_children(
    token: str = typer.Option(..., help="Document token"),
    block_id: str = typer.Option(..., help="Block ID"),
    start_index: int = typer.Option(..., help="Start index"),
    end_index: int = typer.Option(..., help="End index"),
) -> None:
    """Delete child blocks by index range."""
    client = create_client()
    body = (
        BatchDeleteDocumentBlockChildrenRequestBody.builder()
        .start_index(start_index)
        .end_index(end_index)
        .build()
    )
    request = (
        BatchDeleteDocumentBlockChildrenRequest.builder()
        .document_id(token)
        .block_id(block_id)
        .request_body(body)
        .build()
    )
    response = call_api(
        client,
        client.docx.v1.document_block_children.batch_delete,
        request,
    )
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)
