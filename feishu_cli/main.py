import typer

app = typer.Typer(
    name="feishu-cli",
    help="CLI tool for Feishu cloud document operations.",
    no_args_is_help=True,
)


@app.callback()
def main():
    """Feishu Cloud Docs CLI - operate docs, sheets, bitable, wiki."""
    pass


if __name__ == "__main__":
    app()
