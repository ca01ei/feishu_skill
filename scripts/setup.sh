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
uv pip install -e ".[dev]" --python "$PROJECT_DIR/.venv/bin/python"

# Write marker
date > "$MARKER"
echo "=== Setup complete ==="
