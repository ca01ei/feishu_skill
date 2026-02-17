"""Legacy docs commands."""

import typer
from lark_oapi.api.docs.v1 import GetContentRequest

from feishu_cli.client import create_client
from feishu_cli.utils.output import format_response

docs_app = typer.Typer(name="docs", help="Legacy document operations.", no_args_is_help=True)


@docs_app.command("get")
def get_content(
    token: str = typer.Option(..., help="Document token"),
    doc_type: str = typer.Option("docx", help="Document type"),
    content_type: str = typer.Option(
        "markdown", help="Content type (markdown/plaintext)"
    ),
) -> None:
    """Get legacy document content."""
    client = create_client()
    request = (
        GetContentRequest.builder()
        .doc_token(token)
        .doc_type(doc_type)
        .content_type(content_type)
        .build()
    )
    response = client.docs.v1.content.get(request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)
