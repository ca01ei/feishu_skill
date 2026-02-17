# Feishu Cloud Docs CLI + Skill Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a CLI tool (`feishu-cli`) + Claude Code Skill that enables AI agents to perform all Feishu cloud document operations (docs, docx, sheets, bitable, wiki).

**Architecture:** A Python CLI built with typer wraps the `lark-oapi` SDK. Each cloud document API domain is a typer sub-app. A Claude Code Skill file describes available commands. A one-time setup script installs all dependencies.

**Tech Stack:** Python 3.7+, typer, lark-oapi (local SDK), uv (package manager), pytest

---

### Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `feishu_cli/__init__.py`
- Create: `feishu_cli/main.py`
- Create: `tests/__init__.py`

**Step 1: Create pyproject.toml**

```toml
[project]
name = "feishu-cli"
version = "0.1.0"
description = "CLI tool for Feishu cloud document operations"
requires-python = ">=3.7"
dependencies = [
    "typer[all]>=0.9.0",
    "python-dotenv>=1.0.0",
]

[project.scripts]
feishu-cli = "feishu_cli.main:app"

[tool.pytest.ini_options]
testpaths = ["tests"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Step 2: Create .env.example**

```
FEISHU_APP_ID=your_app_id_here
FEISHU_APP_SECRET=your_app_secret_here
```

**Step 3: Create .gitignore**

```
.venv/
__pycache__/
*.pyc
.env
.feishu_cli_installed
dist/
*.egg-info/
```

**Step 4: Create feishu_cli/__init__.py**

```python
"""Feishu Cloud Docs CLI tool."""
```

**Step 5: Create minimal feishu_cli/main.py**

```python
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
```

**Step 6: Create tests/__init__.py**

Empty file.

**Step 7: Commit**

```bash
git add pyproject.toml .env.example .gitignore feishu_cli/ tests/
git commit -m "chore: scaffold feishu-cli project"
```

---

### Task 2: Setup Scripts (One-Time Install)

**Files:**
- Create: `scripts/setup.sh`
- Create: `scripts/feishu-cli.sh`

**Step 1: Create scripts/setup.sh**

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MARKER="$PROJECT_DIR/.feishu_cli_installed"

echo "=== Feishu CLI Setup ==="

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found. Please install Python 3.7+."
    exit 3
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python version: $PYTHON_VERSION"

# Check uv
if ! command -v uv &>/dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "uv version: $(uv --version)"

# Create venv if not exists
if [ ! -d "$PROJECT_DIR/.venv" ]; then
    echo "Creating virtual environment..."
    uv venv "$PROJECT_DIR/.venv"
fi

# Install dependencies
echo "Installing dependencies..."
cd "$PROJECT_DIR"
uv pip install -e "." --python "$PROJECT_DIR/.venv/bin/python"

# Install local SDK
uv pip install -e "$PROJECT_DIR/oapi-sdk-python" --python "$PROJECT_DIR/.venv/bin/python"

# Write marker
date > "$MARKER"
echo "=== Setup complete ==="
```

**Step 2: Create scripts/feishu-cli.sh**

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MARKER="$PROJECT_DIR/.feishu_cli_installed"

# Auto-install if needed
if [ ! -f "$MARKER" ]; then
    echo "First run detected. Running setup..."
    bash "$SCRIPT_DIR/setup.sh"
fi

# Load .env if exists
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a
    source "$PROJECT_DIR/.env"
    set +a
fi

# Run CLI
exec "$PROJECT_DIR/.venv/bin/python" -m feishu_cli.main "$@"
```

**Step 3: Make scripts executable**

```bash
chmod +x scripts/setup.sh scripts/feishu-cli.sh
```

**Step 4: Commit**

```bash
git add scripts/
git commit -m "chore: add setup and cli entry scripts"
```

---

### Task 3: Config & Client Module

**Files:**
- Create: `feishu_cli/config.py`
- Create: `feishu_cli/client.py`
- Create: `tests/test_config.py`

**Step 1: Write failing test for config**

```python
# tests/test_config.py
import os
import pytest
from feishu_cli.config import load_config, ConfigError


def test_load_config_from_env(monkeypatch):
    monkeypatch.setenv("FEISHU_APP_ID", "test_id")
    monkeypatch.setenv("FEISHU_APP_SECRET", "test_secret")
    config = load_config()
    assert config.app_id == "test_id"
    assert config.app_secret == "test_secret"


def test_load_config_missing_raises(monkeypatch):
    monkeypatch.delenv("FEISHU_APP_ID", raising=False)
    monkeypatch.delenv("FEISHU_APP_SECRET", raising=False)
    with pytest.raises(ConfigError, match="FEISHU_APP_ID"):
        load_config()
```

**Step 2: Run test to verify it fails**

```bash
scripts/feishu-cli.sh  # trigger setup first
.venv/bin/python -m pytest tests/test_config.py -v
```

Expected: FAIL - `ModuleNotFoundError: No module named 'feishu_cli.config'`

**Step 3: Implement config.py**

```python
# feishu_cli/config.py
"""Configuration management for Feishu CLI."""

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


class ConfigError(Exception):
    """Raised when configuration is invalid."""
    pass


@dataclass(frozen=True)
class FeishuConfig:
    """Immutable Feishu configuration."""
    app_id: str
    app_secret: str


def load_config() -> FeishuConfig:
    """Load config from environment variables, falling back to .env file.

    Priority: environment variables > .env file in project root.
    """
    # Try loading .env from project root
    project_root = Path(__file__).parent.parent
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=False)

    app_id = os.environ.get("FEISHU_APP_ID")
    app_secret = os.environ.get("FEISHU_APP_SECRET")

    if not app_id:
        raise ConfigError(
            "FEISHU_APP_ID not set. "
            "Set it as an environment variable or in .env file."
        )
    if not app_secret:
        raise ConfigError(
            "FEISHU_APP_SECRET not set. "
            "Set it as an environment variable or in .env file."
        )

    return FeishuConfig(app_id=app_id, app_secret=app_secret)
```

**Step 4: Run test to verify it passes**

```bash
.venv/bin/python -m pytest tests/test_config.py -v
```

Expected: PASS

**Step 5: Implement client.py**

```python
# feishu_cli/client.py
"""Feishu API client initialization."""

import lark_oapi as lark
from feishu_cli.config import load_config


def create_client() -> lark.Client:
    """Create and return a configured Feishu API client."""
    config = load_config()
    return (
        lark.Client.builder()
        .app_id(config.app_id)
        .app_secret(config.app_secret)
        .build()
    )
```

**Step 6: Commit**

```bash
git add feishu_cli/config.py feishu_cli/client.py tests/test_config.py
git commit -m "feat: add config and client modules"
```

---

### Task 4: Output Utility

**Files:**
- Create: `feishu_cli/utils/__init__.py`
- Create: `feishu_cli/utils/output.py`
- Create: `tests/test_output.py`

**Step 1: Write failing test**

```python
# tests/test_output.py
import json
from unittest.mock import MagicMock
from feishu_cli.utils.output import format_response, format_error


def test_format_response_success():
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = MagicMock()

    import lark_oapi as lark
    # Mock JSON.marshal to return a known string
    result = format_response(mock_resp)
    parsed = json.loads(result)
    assert parsed["success"] is True


def test_format_error():
    result = format_error(code=99991400, msg="token invalid")
    parsed = json.loads(result)
    assert parsed["success"] is False
    assert parsed["code"] == 99991400
    assert parsed["msg"] == "token invalid"
```

**Step 2: Run test to verify it fails**

```bash
.venv/bin/python -m pytest tests/test_output.py -v
```

Expected: FAIL

**Step 3: Implement output.py**

```python
# feishu_cli/utils/output.py
"""Unified output formatting for Feishu CLI."""

import json
from typing import Any

import lark_oapi as lark


def format_response(response: Any) -> str:
    """Format an API response as JSON string."""
    if response.success():
        data = json.loads(lark.JSON.marshal(response.data)) if response.data else None
        return json.dumps({"success": True, "data": data}, ensure_ascii=False, indent=2)
    return format_error(
        code=response.code,
        msg=response.msg,
        log_id=response.get_log_id(),
    )


def format_error(code: int = 0, msg: str = "", log_id: str = "") -> str:
    """Format an error as JSON string."""
    result = {"success": False, "code": code, "msg": msg}
    if log_id:
        result["log_id"] = log_id
    return json.dumps(result, ensure_ascii=False, indent=2)
```

**Step 4: Run test to verify it passes**

```bash
.venv/bin/python -m pytest tests/test_output.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add feishu_cli/utils/ tests/test_output.py
git commit -m "feat: add output formatting utility"
```

---

### Task 5: Docx Commands

**Files:**
- Create: `feishu_cli/commands/__init__.py`
- Create: `feishu_cli/commands/docx.py`
- Modify: `feishu_cli/main.py` (register sub-app)
- Create: `tests/test_docx.py`

**Step 1: Write failing test**

```python
# tests/test_docx.py
import json
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from feishu_cli.main import app

runner = CliRunner()


@patch("feishu_cli.commands.docx.create_client")
def test_docx_create(mock_create_client):
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = None
    mock_client.docx.v1.document.create.return_value = mock_resp
    mock_create_client.return_value = mock_client

    result = runner.invoke(app, ["docx", "create", "--title", "Test Doc"])
    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["success"] is True


@patch("feishu_cli.commands.docx.create_client")
def test_docx_get(mock_create_client):
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = None
    mock_client.docx.v1.document.get.return_value = mock_resp
    mock_create_client.return_value = mock_client

    result = runner.invoke(app, ["docx", "get", "--token", "doccnXXX"])
    assert result.exit_code == 0
```

**Step 2: Run test to verify it fails**

```bash
.venv/bin/python -m pytest tests/test_docx.py -v
```

Expected: FAIL

**Step 3: Implement docx.py**

```python
# feishu_cli/commands/docx.py
"""Docx (new document) commands."""

from typing import Optional
import json

import typer
import lark_oapi as lark
from lark_oapi.api.docx.v1 import (
    CreateDocumentRequest,
    CreateDocumentRequestBody,
    GetDocumentRequest,
    RawContentDocumentRequest,
    ListDocumentBlockRequest,
    GetDocumentBlockRequest,
    CreateDocumentBlockChildrenRequest,
    CreateDocumentBlockChildrenRequestBody,
    DeleteDocumentBlockChildrenRequest,
    BatchUpdateDocumentBlockRequest,
    BatchUpdateDocumentBlockRequestBody,
)

from feishu_cli.client import create_client
from feishu_cli.utils.output import format_response, format_error

docx_app = typer.Typer(name="docx", help="New document (docx) operations.", no_args_is_help=True)
block_app = typer.Typer(name="block", help="Document block operations.", no_args_is_help=True)
docx_app.add_typer(block_app)


@docx_app.command("create")
def create_document(
    title: str = typer.Option(..., help="Document title"),
    folder_token: Optional[str] = typer.Option(None, help="Parent folder token"),
):
    """Create a new document."""
    client = create_client()
    body_builder = CreateDocumentRequestBody.builder().title(title)
    if folder_token:
        body_builder = body_builder.folder_token(folder_token)

    request = (
        CreateDocumentRequest.builder()
        .request_body(body_builder.build())
        .build()
    )
    response = client.docx.v1.document.create(request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@docx_app.command("get")
def get_document(
    token: str = typer.Option(..., help="Document token"),
):
    """Get document metadata."""
    client = create_client()
    request = GetDocumentRequest.builder().document_id(token).build()
    response = client.docx.v1.document.get(request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@docx_app.command("content")
def get_raw_content(
    token: str = typer.Option(..., help="Document token"),
    lang: Optional[int] = typer.Option(0, help="Language (0=all, 1=zh, 2=en, 3=ja)"),
):
    """Get document raw content."""
    client = create_client()
    request = RawContentDocumentRequest.builder().document_id(token).lang(lang).build()
    response = client.docx.v1.document.raw_content(request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@block_app.command("list")
def list_blocks(
    token: str = typer.Option(..., help="Document token"),
    page_size: Optional[int] = typer.Option(500, help="Page size"),
    page_token: Optional[str] = typer.Option(None, help="Page token for pagination"),
):
    """List all blocks in a document."""
    client = create_client()
    builder = ListDocumentBlockRequest.builder().document_id(token).page_size(page_size)
    if page_token:
        builder = builder.page_token(page_token)
    request = builder.build()
    response = client.docx.v1.document_block.list(request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@block_app.command("get")
def get_block(
    token: str = typer.Option(..., help="Document token"),
    block_id: str = typer.Option(..., help="Block ID"),
):
    """Get a specific block."""
    client = create_client()
    request = (
        GetDocumentBlockRequest.builder()
        .document_id(token)
        .block_id(block_id)
        .build()
    )
    response = client.docx.v1.document_block.get(request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@block_app.command("create")
def create_block_children(
    token: str = typer.Option(..., help="Document token"),
    block_id: str = typer.Option(..., help="Parent block ID"),
    data: str = typer.Option(..., help="Block children JSON data or @file.json"),
):
    """Create child blocks under a parent block."""
    client = create_client()
    json_data = _load_json(data)

    request = (
        CreateDocumentBlockChildrenRequest.builder()
        .document_id(token)
        .block_id(block_id)
        .request_body(
            CreateDocumentBlockChildrenRequestBody.builder()
            .children(json_data.get("children", []))
            .index(json_data.get("index", -1))
            .build()
        )
        .build()
    )
    response = client.docx.v1.document_block_children.create(request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@block_app.command("delete")
def delete_block_children(
    token: str = typer.Option(..., help="Document token"),
    block_id: str = typer.Option(..., help="Parent block ID"),
    start_index: int = typer.Option(..., help="Start index"),
    end_index: int = typer.Option(..., help="End index"),
):
    """Delete child blocks by index range."""
    client = create_client()
    request = (
        DeleteDocumentBlockChildrenRequest.builder()
        .document_id(token)
        .block_id(block_id)
        .start_index(start_index)
        .end_index(end_index)
        .build()
    )
    response = client.docx.v1.document_block_children.batch_delete(request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


def _load_json(data: str) -> dict:
    """Load JSON from string or @file.json path."""
    if data.startswith("@"):
        from pathlib import Path
        return json.loads(Path(data[1:]).read_text(encoding="utf-8"))
    return json.loads(data)
```

**Step 4: Register in main.py**

```python
# feishu_cli/main.py
import typer
from feishu_cli.commands.docx import docx_app

app = typer.Typer(
    name="feishu-cli",
    help="CLI tool for Feishu cloud document operations.",
    no_args_is_help=True,
)
app.add_typer(docx_app)


@app.callback()
def main():
    """Feishu Cloud Docs CLI - operate docs, sheets, bitable, wiki."""
    pass


if __name__ == "__main__":
    app()
```

**Step 5: Run tests**

```bash
.venv/bin/python -m pytest tests/test_docx.py -v
```

Expected: PASS

**Step 6: Commit**

```bash
git add feishu_cli/commands/ feishu_cli/main.py tests/test_docx.py
git commit -m "feat: add docx commands"
```

---

### Task 6: Docs Commands (Legacy)

**Files:**
- Create: `feishu_cli/commands/docs.py`
- Modify: `feishu_cli/main.py` (register)
- Create: `tests/test_docs.py`

**Step 1: Write failing test**

```python
# tests/test_docs.py
import json
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from feishu_cli.main import app

runner = CliRunner()


@patch("feishu_cli.commands.docs.create_client")
def test_docs_get(mock_create_client):
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = None
    mock_client.docs.v1.content.get.return_value = mock_resp
    mock_create_client.return_value = mock_client

    result = runner.invoke(app, ["docs", "get", "--token", "doccnXXX"])
    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["success"] is True
```

**Step 2: Run test - expect FAIL**

**Step 3: Implement docs.py**

```python
# feishu_cli/commands/docs.py
"""Legacy docs commands."""

from typing import Optional
import typer
from lark_oapi.api.docs.v1 import GetContentRequest

from feishu_cli.client import create_client
from feishu_cli.utils.output import format_response

docs_app = typer.Typer(name="docs", help="Legacy document operations.", no_args_is_help=True)


@docs_app.command("get")
def get_content(
    token: str = typer.Option(..., help="Document token"),
    doc_type: Optional[str] = typer.Option("docx", help="Document type"),
    content_type: Optional[str] = typer.Option("markdown", help="Content type (markdown/plaintext)"),
):
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
```

**Step 4: Register in main.py - add `from feishu_cli.commands.docs import docs_app` and `app.add_typer(docs_app)`**

**Step 5: Run test - expect PASS**

**Step 6: Commit**

```bash
git add feishu_cli/commands/docs.py feishu_cli/main.py tests/test_docs.py
git commit -m "feat: add legacy docs commands"
```

---

### Task 7: Sheets Commands

**Files:**
- Create: `feishu_cli/commands/sheets.py`
- Modify: `feishu_cli/main.py` (register)
- Create: `tests/test_sheets.py`

**Step 1: Write failing test**

```python
# tests/test_sheets.py
import json
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from feishu_cli.main import app

runner = CliRunner()


@patch("feishu_cli.commands.sheets.create_client")
def test_sheets_create(mock_create_client):
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = None
    mock_client.sheets.v3.spreadsheet.create.return_value = mock_resp
    mock_create_client.return_value = mock_client

    result = runner.invoke(app, ["sheets", "create", "--title", "Test Sheet"])
    assert result.exit_code == 0


@patch("feishu_cli.commands.sheets.create_client")
def test_sheets_get(mock_create_client):
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = None
    mock_client.sheets.v3.spreadsheet.get.return_value = mock_resp
    mock_create_client.return_value = mock_client

    result = runner.invoke(app, ["sheets", "get", "--token", "shtcnXXX"])
    assert result.exit_code == 0
```

**Step 2: Run test - expect FAIL**

**Step 3: Implement sheets.py**

```python
# feishu_cli/commands/sheets.py
"""Sheets (spreadsheet) commands."""

from typing import Optional
import json

import typer
from lark_oapi.api.sheets.v3 import (
    CreateSpreadsheetRequest,
    CreateSpreadsheetRequestBody,
    GetSpreadsheetRequest,
    PatchSpreadsheetRequest,
    PatchSpreadsheetRequestBody,
    QuerySpreadsheetSheetRequest,
    CreateSpreadsheetSheetFilterRequest,
    CreateSpreadsheetSheetFilterRequestBody,
    GetSpreadsheetSheetFilterRequest,
    UpdateSpreadsheetSheetFilterRequest,
    UpdateSpreadsheetSheetFilterRequestBody,
    DeleteSpreadsheetSheetFilterRequest,
    CreateSpreadsheetSheetFilterViewRequest,
    CreateSpreadsheetSheetFilterViewRequestBody,
    GetSpreadsheetSheetFilterViewRequest,
    QuerySpreadsheetSheetFilterViewRequest,
    PatchSpreadsheetSheetFilterViewRequest,
    PatchSpreadsheetSheetFilterViewRequestBody,
    DeleteSpreadsheetSheetFilterViewRequest,
    CreateSpreadsheetSheetFilterViewConditionRequest,
    CreateSpreadsheetSheetFilterViewConditionRequestBody,
    GetSpreadsheetSheetFilterViewConditionRequest,
    QuerySpreadsheetSheetFilterViewConditionRequest,
    UpdateSpreadsheetSheetFilterViewConditionRequest,
    UpdateSpreadsheetSheetFilterViewConditionRequestBody,
    DeleteSpreadsheetSheetFilterViewConditionRequest,
    CreateSpreadsheetSheetFloatImageRequest,
    CreateSpreadsheetSheetFloatImageRequestBody,
    GetSpreadsheetSheetFloatImageRequest,
    QuerySpreadsheetSheetFloatImageRequest,
    PatchSpreadsheetSheetFloatImageRequest,
    PatchSpreadsheetSheetFloatImageRequestBody,
    DeleteSpreadsheetSheetFloatImageRequest,
)

from feishu_cli.client import create_client
from feishu_cli.utils.output import format_response

sheets_app = typer.Typer(name="sheets", help="Spreadsheet operations.", no_args_is_help=True)
sheet_app = typer.Typer(name="sheet", help="Sheet tab operations.", no_args_is_help=True)
filter_app = typer.Typer(name="filter", help="Sheet filter operations.", no_args_is_help=True)
filter_view_app = typer.Typer(name="filter-view", help="Filter view operations.", no_args_is_help=True)
float_image_app = typer.Typer(name="float-image", help="Float image operations.", no_args_is_help=True)

sheets_app.add_typer(sheet_app)
sheets_app.add_typer(filter_app)
sheets_app.add_typer(filter_view_app)
sheets_app.add_typer(float_image_app)


@sheets_app.command("create")
def create_spreadsheet(
    title: str = typer.Option(..., help="Spreadsheet title"),
    folder_token: Optional[str] = typer.Option(None, help="Parent folder token"),
):
    """Create a new spreadsheet."""
    client = create_client()
    body_builder = CreateSpreadsheetRequestBody.builder().title(title)
    if folder_token:
        body_builder = body_builder.folder_token(folder_token)
    request = CreateSpreadsheetRequest.builder().request_body(body_builder.build()).build()
    response = client.sheets.v3.spreadsheet.create(request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@sheets_app.command("get")
def get_spreadsheet(
    token: str = typer.Option(..., help="Spreadsheet token"),
):
    """Get spreadsheet metadata."""
    client = create_client()
    request = GetSpreadsheetRequest.builder().spreadsheet_token(token).build()
    response = client.sheets.v3.spreadsheet.get(request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@sheets_app.command("update")
def update_spreadsheet(
    token: str = typer.Option(..., help="Spreadsheet token"),
    title: Optional[str] = typer.Option(None, help="New title"),
):
    """Update spreadsheet properties."""
    client = create_client()
    body_builder = PatchSpreadsheetRequestBody.builder()
    if title:
        body_builder = body_builder.title(title)
    request = (
        PatchSpreadsheetRequest.builder()
        .spreadsheet_token(token)
        .request_body(body_builder.build())
        .build()
    )
    response = client.sheets.v3.spreadsheet.patch(request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


@sheet_app.command("list")
def list_sheets(
    token: str = typer.Option(..., help="Spreadsheet token"),
):
    """List all sheets in a spreadsheet."""
    client = create_client()
    request = QuerySpreadsheetSheetRequest.builder().spreadsheet_token(token).build()
    response = client.sheets.v3.spreadsheet_sheet.query(request)
    typer.echo(format_response(response))
    raise typer.Exit(code=0 if response.success() else 1)


# Filter, filter-view, and float-image commands follow the same pattern.
# Each uses the corresponding SDK request/response classes.
# Implementation is repetitive - use the same create_client() + request builder + format_response() pattern.
# For brevity, the full implementations should follow the exact pattern above,
# substituting the appropriate request classes for each operation.
```

> **Note to implementer:** The filter, filter-view, filter-view-condition, and float-image sub-commands all follow the identical pattern. Each CRUD operation uses the corresponding `Create*/Get*/Update*/Delete*Request` class from the SDK. Implement each using the same `create_client() → build request → call SDK → format_response()` pattern. Keep total file under 400 lines by extracting a helper if needed.

**Step 4: Register in main.py**

**Step 5: Run test - expect PASS**

**Step 6: Commit**

```bash
git add feishu_cli/commands/sheets.py feishu_cli/main.py tests/test_sheets.py
git commit -m "feat: add sheets commands"
```

---

### Task 8: Bitable Commands

**Files:**
- Create: `feishu_cli/commands/bitable.py`
- Modify: `feishu_cli/main.py` (register)
- Create: `tests/test_bitable.py`

> **Note:** Bitable has the most operations (app, table, record, field, view, form, role, dashboard). Due to the 400-line file limit, split into `bitable.py` (app/table/record) and `bitable_extra.py` (field/view/form/role/dashboard) if needed.

**Step 1: Write failing tests for core operations (app create, record create, record list)**

```python
# tests/test_bitable.py
import json
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from feishu_cli.main import app

runner = CliRunner()


@patch("feishu_cli.commands.bitable.create_client")
def test_bitable_app_create(mock_create_client):
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = None
    mock_client.bitable.v1.app.create.return_value = mock_resp
    mock_create_client.return_value = mock_client

    result = runner.invoke(app, ["bitable", "app", "create", "--name", "Test App"])
    assert result.exit_code == 0


@patch("feishu_cli.commands.bitable.create_client")
def test_bitable_record_list(mock_create_client):
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = None
    mock_client.bitable.v1.app_table_record.list.return_value = mock_resp
    mock_create_client.return_value = mock_client

    result = runner.invoke(app, [
        "bitable", "record", "list",
        "--token", "appXXX",
        "--table", "tblXXX",
    ])
    assert result.exit_code == 0
```

**Step 2: Run test - expect FAIL**

**Step 3: Implement bitable.py** (app, table, record sub-commands)

Follow the same pattern as docx.py/sheets.py. Key SDK paths:
- `client.bitable.v1.app.create/get/update/copy`
- `client.bitable.v1.app_table.create/list/batch_delete`
- `client.bitable.v1.app_table_record.create/get/list/update/delete/batch_create/batch_update/batch_delete`

**Step 4: If over 400 lines, create `bitable_extra.py`** for field/view/form/role/dashboard:
- `client.bitable.v1.app_table_field.create/list/update/delete`
- `client.bitable.v1.app_table_view.create/list/get/patch/delete`
- `client.bitable.v1.app_table_form.get/patch`
- `client.bitable.v1.app_table_form_field.list/patch`
- `client.bitable.v1.app_role.create/list/update/delete`
- `client.bitable.v1.app_dashboard.list`

**Step 5: Register in main.py**

**Step 6: Run tests - expect PASS**

**Step 7: Commit**

```bash
git add feishu_cli/commands/bitable*.py feishu_cli/main.py tests/test_bitable.py
git commit -m "feat: add bitable commands"
```

---

### Task 9: Wiki Commands

**Files:**
- Create: `feishu_cli/commands/wiki.py`
- Modify: `feishu_cli/main.py` (register)
- Create: `tests/test_wiki.py`

**Step 1: Write failing tests**

```python
# tests/test_wiki.py
import json
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from feishu_cli.main import app

runner = CliRunner()


@patch("feishu_cli.commands.wiki.create_client")
def test_wiki_space_create(mock_create_client):
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = None
    mock_client.wiki.v2.space.create.return_value = mock_resp
    mock_create_client.return_value = mock_client

    result = runner.invoke(app, ["wiki", "space", "create", "--name", "Test Wiki"])
    assert result.exit_code == 0


@patch("feishu_cli.commands.wiki.create_client")
def test_wiki_node_create(mock_create_client):
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.success.return_value = True
    mock_resp.data = None
    mock_client.wiki.v2.space_node.create.return_value = mock_resp
    mock_create_client.return_value = mock_client

    result = runner.invoke(app, [
        "wiki", "node", "create",
        "--space", "spaceXXX",
        "--title", "Test Page",
    ])
    assert result.exit_code == 0
```

**Step 2: Run test - expect FAIL**

**Step 3: Implement wiki.py**

Key SDK paths:
- `client.wiki.v2.space.create/get_node/list`
- `client.wiki.v2.space_node.create/copy/move`
- `client.wiki.v2.space_member.create/list/delete`
- `client.wiki.v2.space_setting.update`
- `client.wiki.v1.node.search`

**Step 4: Register in main.py**

**Step 5: Run tests - expect PASS**

**Step 6: Commit**

```bash
git add feishu_cli/commands/wiki.py feishu_cli/main.py tests/test_wiki.py
git commit -m "feat: add wiki commands"
```

---

### Task 10: Skill File

**Files:**
- Create: `skill/feishu-cloud-docs.md`

**Step 1: Create the skill file**

```markdown
---
name: feishu-cloud-docs
description: Operate Feishu cloud documents (docs, docx, sheets, bitable, wiki).
  Use when user asks to create/edit/query Feishu documents, spreadsheets, bitables, or wiki pages.
---

## Setup

If `scripts/feishu-cli.sh` fails with "not installed", run:
```
bash /path/to/feishu_skill/scripts/setup.sh
```

## Credentials

Requires `FEISHU_APP_ID` and `FEISHU_APP_SECRET` as environment variables or in `.env`.

## CLI Reference

All commands: `scripts/feishu-cli.sh <domain> <command> [options]`
All output is JSON. Use `--help` on any command for full options.

### docx (New Documents)
- `docx create --title T [--folder-token F]` — Create document
- `docx get --token T` — Get document info
- `docx content --token T` — Get raw content
- `docx block list --token T` — List blocks
- `docx block get --token T --block-id B` — Get block
- `docx block create --token T --block-id B --data '{...}'` — Add child blocks
- `docx block delete --token T --block-id B --start-index N --end-index M` — Delete blocks

### docs (Legacy)
- `docs get --token T [--content-type markdown]` — Get content

### sheets (Spreadsheets)
- `sheets create --title T` — Create spreadsheet
- `sheets get --token T` — Get spreadsheet
- `sheets update --token T --title T` — Update properties
- `sheets sheet list --token T` — List sheet tabs
- `sheets filter create/get/update/delete` — Filter operations
- `sheets filter-view create/get/list/update/delete` — Filter views
- `sheets float-image create/get/list/update/delete` — Float images

### bitable (Multi-dimensional Tables)
- `bitable app create/get/update/copy` — App management
- `bitable table create/list/delete --token T` — Table management
- `bitable record create/get/list/update/delete --token T --table TBL` — Record CRUD
- `bitable record batch-create/batch-update/batch-delete` — Batch operations
- `bitable field create/list/update/delete` — Field management
- `bitable view create/list/get/update/delete` — View management
- `bitable form get/update` — Form operations
- `bitable role create/list/update/delete` — Role management
- `bitable dashboard list` — List dashboards

### wiki (Knowledge Base)
- `wiki space create/get/list/update` — Space management
- `wiki node create/get/move/copy/list --space S` — Page management
- `wiki member create/list/delete --space S` — Permissions
- `wiki setting get/update --space S` — Settings
- `wiki search --query Q` — Search

## Common Workflows

### Create a document with content
1. `docx create --title "Title"` → get document_id
2. `docx block list --token DOC_ID` → get root block_id
3. `docx block create --token DOC_ID --block-id ROOT --data '{"children": [...]}'`

### Create bitable and import data
1. `bitable app create --name "DB"` → get app_token
2. `bitable table create --token APP --name "Table1"` → get table_id
3. `bitable field create --token APP --table TBL --data '{"field_name": "Name", "type": 1}'`
4. `bitable record batch-create --token APP --table TBL --data '{"records": [...]}'`

### Build wiki structure
1. `wiki space create --name "Wiki"` → get space_id
2. `wiki node create --space S --title "Root Page"` → get node_token
3. `wiki node create --space S --title "Child" --parent NODE`

## Error Handling

All errors return: `{"success": false, "code": N, "msg": "..."}`.
Exit codes: 0=success, 1=API error, 2=param error, 3=config error.
```

**Step 2: Commit**

```bash
git add skill/
git commit -m "feat: add feishu-cloud-docs skill file"
```

---

### Task 11: Integration Test & Final Verification

**Step 1: Run full test suite**

```bash
.venv/bin/python -m pytest tests/ -v --tb=short
```

Expected: All tests PASS

**Step 2: Check coverage**

```bash
.venv/bin/python -m pytest tests/ --cov=feishu_cli --cov-report=term-missing
```

Expected: ≥80% coverage

**Step 3: Verify CLI help works**

```bash
scripts/feishu-cli.sh --help
scripts/feishu-cli.sh docx --help
scripts/feishu-cli.sh bitable record --help
```

**Step 4: Final commit**

```bash
git add -A
git commit -m "chore: finalize feishu-cli with full test coverage"
```

---

## Summary

| Task | Description | Est. Steps |
|------|-------------|-----------|
| 1 | Project scaffolding | 7 |
| 2 | Setup scripts | 4 |
| 3 | Config & Client | 6 |
| 4 | Output utility | 5 |
| 5 | Docx commands | 6 |
| 6 | Docs commands | 6 |
| 7 | Sheets commands | 6 |
| 8 | Bitable commands | 7 |
| 9 | Wiki commands | 6 |
| 10 | Skill file | 2 |
| 11 | Integration test | 4 |
