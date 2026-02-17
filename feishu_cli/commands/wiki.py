"""Wiki commands for spaces, nodes, members, settings, and search."""
from typing import Optional

import lark_oapi as lark
import typer
from lark_oapi.api.wiki.v1 import SearchNodeRequest, SearchNodeRequestBody
from lark_oapi.api.wiki.v2 import (
    CopySpaceNodeRequest,
    CopySpaceNodeRequestBody,
    CreateSpaceMemberRequest,
    CreateSpaceNodeRequest,
    CreateSpaceRequest,
    DeleteSpaceMemberRequest,
    GetNodeSpaceRequest,
    GetSpaceRequest,
    ListSpaceMemberRequest,
    ListSpaceNodeRequest,
    ListSpaceRequest,
    MoveSpaceNodeRequest,
    MoveSpaceNodeRequestBody,
    UpdateSpaceSettingRequest,
)

from feishu_cli.client import create_client
from feishu_cli.runtime import call_api
from feishu_cli.utils.output import format_error, format_response

wiki_app = typer.Typer(name="wiki", help="Wiki operations.", no_args_is_help=True)
space_cmd = typer.Typer(name="space", help="Wiki space operations.", no_args_is_help=True)
node_cmd = typer.Typer(name="node", help="Wiki node operations.", no_args_is_help=True)
member_cmd = typer.Typer(name="member", help="Wiki member operations.", no_args_is_help=True)
setting_cmd = typer.Typer(name="setting", help="Wiki setting operations.", no_args_is_help=True)

wiki_app.add_typer(space_cmd, name="space")
wiki_app.add_typer(node_cmd, name="node")
wiki_app.add_typer(member_cmd, name="member")
wiki_app.add_typer(setting_cmd, name="setting")

def _json_param_error(message: str) -> None:
    """Emit a structured parameter error and exit with code 2."""
    typer.echo(format_error(code=2, msg=message))
    raise typer.Exit(code=2)


def _parse_json_body(data: str, schema: object) -> object:
    """Parse request body JSON into SDK schema object."""
    try:
        return lark.JSON.unmarshal(data, schema)
    except Exception as exc:
        _json_param_error(f"Invalid JSON: {exc}")
    return None


# --- Space commands ---


@space_cmd.command("list")
def space_list(
    page_size: Optional[int] = typer.Option(None, help="Page size"),
    page_token: Optional[str] = typer.Option(None, help="Page token"),
) -> None:
    """List wiki spaces."""
    client = create_client()
    builder = ListSpaceRequest.builder()
    if page_size is not None:
        builder = builder.page_size(page_size)
    if page_token is not None:
        builder = builder.page_token(page_token)
    response = call_api(client, client.wiki.v2.space.list, builder.build())
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@space_cmd.command("create")
def space_create(
    data: str = typer.Option(..., help="JSON data for space creation"),
) -> None:
    """Create a wiki space."""
    client = create_client()
    body = _parse_json_body(data, lark.api.wiki.v2.Space)
    request = CreateSpaceRequest.builder().request_body(body).build()
    response = call_api(client, client.wiki.v2.space.create, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@space_cmd.command("get")
def space_get(
    space: str = typer.Option(..., help="Space ID"),
    lang: Optional[str] = typer.Option(None, help="Language"),
) -> None:
    """Get wiki space info."""
    client = create_client()
    builder = GetSpaceRequest.builder().space_id(space)
    if lang is not None:
        builder = builder.lang(lang)
    response = call_api(client, client.wiki.v2.space.get, builder.build())
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@space_cmd.command("get-node")
def space_get_node(
    token: str = typer.Option(..., help="Node token"),
    obj_type: Optional[str] = typer.Option(None, help="Object type"),
) -> None:
    """Get node info for a wiki space."""
    client = create_client()
    builder = GetNodeSpaceRequest.builder().token(token)
    if obj_type is not None:
        builder = builder.obj_type(obj_type)
    response = call_api(client, client.wiki.v2.space.get_node, builder.build())
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


# --- Node commands ---


@node_cmd.command("create")
def node_create(
    space: str = typer.Option(..., help="Space ID"),
    data: str = typer.Option(..., help="JSON data for node creation"),
) -> None:
    """Create a wiki node."""
    client = create_client()
    body = _parse_json_body(data, lark.api.wiki.v2.Node)
    request = CreateSpaceNodeRequest.builder().space_id(space).request_body(body).build()
    response = call_api(client, client.wiki.v2.space_node.create, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@node_cmd.command("list")
def node_list(
    space: str = typer.Option(..., help="Space ID"),
    parent: Optional[str] = typer.Option(None, help="Parent node token"),
    page_size: Optional[int] = typer.Option(None, help="Page size"),
    page_token: Optional[str] = typer.Option(None, help="Page token"),
) -> None:
    """List wiki nodes in a space."""
    client = create_client()
    builder = ListSpaceNodeRequest.builder().space_id(space)
    if parent is not None:
        builder = builder.parent_node_token(parent)
    if page_size is not None:
        builder = builder.page_size(page_size)
    if page_token is not None:
        builder = builder.page_token(page_token)
    response = call_api(client, client.wiki.v2.space_node.list, builder.build())
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@node_cmd.command("copy")
def node_copy(
    space: str = typer.Option(..., help="Space ID"),
    node: str = typer.Option(..., help="Node token"),
    data: str = typer.Option(..., help="JSON data for copy"),
) -> None:
    """Copy a wiki node."""
    client = create_client()
    body = _parse_json_body(data, CopySpaceNodeRequestBody)
    request = (
        CopySpaceNodeRequest.builder()
        .space_id(space)
        .node_token(node)
        .request_body(body)
        .build()
    )
    response = call_api(client, client.wiki.v2.space_node.copy, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@node_cmd.command("move")
def node_move(
    space: str = typer.Option(..., help="Space ID"),
    node: str = typer.Option(..., help="Node token"),
    data: str = typer.Option(..., help="JSON data for move"),
) -> None:
    """Move a wiki node."""
    client = create_client()
    body = _parse_json_body(data, MoveSpaceNodeRequestBody)
    request = (
        MoveSpaceNodeRequest.builder()
        .space_id(space)
        .node_token(node)
        .request_body(body)
        .build()
    )
    response = call_api(client, client.wiki.v2.space_node.move, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


# --- Member commands ---


@member_cmd.command("create")
def member_create(
    space: str = typer.Option(..., help="Space ID"),
    data: str = typer.Option(..., help="JSON data for member"),
) -> None:
    """Add a member to a wiki space."""
    client = create_client()
    body = _parse_json_body(data, lark.api.wiki.v2.Member)
    request = CreateSpaceMemberRequest.builder().space_id(space).request_body(body).build()
    response = call_api(client, client.wiki.v2.space_member.create, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@member_cmd.command("list")
def member_list(
    space: str = typer.Option(..., help="Space ID"),
    page_size: Optional[int] = typer.Option(None, help="Page size"),
    page_token: Optional[str] = typer.Option(None, help="Page token"),
) -> None:
    """List members of a wiki space."""
    client = create_client()
    builder = ListSpaceMemberRequest.builder().space_id(space)
    if page_size is not None:
        builder = builder.page_size(page_size)
    if page_token is not None:
        builder = builder.page_token(page_token)
    response = call_api(client, client.wiki.v2.space_member.list, builder.build())
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@member_cmd.command("delete")
def member_delete(
    space: str = typer.Option(..., help="Space ID"),
    member_id: str = typer.Option(..., help="Member ID"),
    data: str = typer.Option(..., help="JSON data with member_type"),
) -> None:
    """Remove a member from a wiki space."""
    client = create_client()
    body = _parse_json_body(data, lark.api.wiki.v2.Member)
    request = (
        DeleteSpaceMemberRequest.builder()
        .space_id(space)
        .member_id(member_id)
        .request_body(body)
        .build()
    )
    response = call_api(client, client.wiki.v2.space_member.delete, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


# --- Setting commands ---


@setting_cmd.command("update")
def setting_update(
    space: str = typer.Option(..., help="Space ID"),
    data: str = typer.Option(..., help="JSON data for setting"),
) -> None:
    """Update wiki space settings."""
    client = create_client()
    body = _parse_json_body(data, lark.api.wiki.v2.Setting)
    request = UpdateSpaceSettingRequest.builder().space_id(space).request_body(body).build()
    response = call_api(client, client.wiki.v2.space_setting.update, request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


# --- Search command (v1) ---


@wiki_app.command("search")
def search(
    data: str = typer.Option(..., help="JSON data with search query"),
    page_size: Optional[int] = typer.Option(None, help="Page size"),
    page_token: Optional[str] = typer.Option(None, help="Page token"),
) -> None:
    """Search wiki nodes (v1 API)."""
    client = create_client()
    body = _parse_json_body(data, SearchNodeRequestBody)
    builder = SearchNodeRequest.builder().request_body(body)
    if page_size is not None:
        builder = builder.page_size(page_size)
    if page_token is not None:
        builder = builder.page_token(page_token)
    response = call_api(client, client.wiki.v1.node.search, builder.build())
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)
