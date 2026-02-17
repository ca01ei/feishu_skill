import typer

from feishu_cli.commands.bitable import bitable_app
from feishu_cli.commands.docs import docs_app
from feishu_cli.commands.docx import docx_app
from feishu_cli.commands.sheets import sheets_app
from feishu_cli.commands.wiki import wiki_app

app = typer.Typer(
    name="feishu-cli",
    help="CLI tool for Feishu cloud document operations.",
    no_args_is_help=True,
)

app.add_typer(docx_app, name="docx")
app.add_typer(docs_app, name="docs")
app.add_typer(sheets_app, name="sheets")
app.add_typer(bitable_app, name="bitable")
app.add_typer(wiki_app, name="wiki")


@app.callback()
def main():
    """Feishu Cloud Docs CLI - operate docs, sheets, bitable, wiki."""
    pass


if __name__ == "__main__":
    app()
