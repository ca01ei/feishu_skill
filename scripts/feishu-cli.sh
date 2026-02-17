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
