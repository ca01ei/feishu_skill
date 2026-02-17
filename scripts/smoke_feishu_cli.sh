#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CLI="$SCRIPT_DIR/feishu-cli.sh"
TS="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="${TMPDIR:-/tmp}/feishu_cli_smoke_${TS}_$$"
mkdir -p "$OUT_DIR"

PASS_COUNT=0
FAIL_COUNT=0

extract_first_json_field() {
    local json_file="$1"
    shift
    python3 - "$json_file" "$@" <<'PY'
import json
import sys

json_file = sys.argv[1]
paths = sys.argv[2:]

def lookup(obj, path):
    cur = obj
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur

try:
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception:
    sys.exit(1)

for p in paths:
    v = lookup(data, p)
    if isinstance(v, str) and v:
        print(v)
        sys.exit(0)

sys.exit(1)
PY
}

run_step() {
    local name="$1"
    shift
    local out_json="$OUT_DIR/${name}.json"
    local out_err="$OUT_DIR/${name}.err"
    echo ""
    echo "==> $name"
    set +e
    "$@" >"$out_json" 2>"$out_err"
    local code=$?
    set -e
    if [ "$code" -eq 0 ]; then
        PASS_COUNT=$((PASS_COUNT + 1))
        echo "PASS: $name"
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
        echo "FAIL: $name (exit=$code)"
        if [ -s "$out_json" ]; then
            cat "$out_json"
        fi
        if [ -s "$out_err" ]; then
            cat "$out_err"
        fi
    fi
    return "$code"
}

ensure_auth_present() {
    if [ -n "${FEISHU_APP_ID:-}" ] && [ -n "${FEISHU_APP_SECRET:-}" ]; then
        return 0
    fi
    if [ ! -f "$PROJECT_DIR/.env" ]; then
        return 1
    fi
    python3 - "$PROJECT_DIR/.env" <<'PY'
import sys

env_file = sys.argv[1]
keys = set()
with open(env_file, "r", encoding="utf-8") as f:
    for line in f:
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        keys.add(s.split("=", 1)[0].strip())

ok = "FEISHU_APP_ID" in keys and "FEISHU_APP_SECRET" in keys
sys.exit(0 if ok else 1)
PY
}

if ! ensure_auth_present; then
    echo "Missing FEISHU credentials. Set FEISHU_APP_ID/FEISHU_APP_SECRET (or .env with both keys)."
    exit 3
fi

echo "Output directory: $OUT_DIR"
echo "Running Feishu CLI smoke tests..."

DOCX_TITLE="smoke-docx-${TS}"
if run_step "docx_create" "$CLI" docx create --title "$DOCX_TITLE"; then
    DOCX_TOKEN="$(extract_first_json_field "$OUT_DIR/docx_create.json" \
        "data.document.document_id" \
        "data.document_id" \
        "data.document.document_token" \
        "data.document.token" || true)"
    if [ -n "${DOCX_TOKEN:-}" ]; then
        run_step "docx_get" "$CLI" docx get --token "$DOCX_TOKEN" || true
        run_step "docx_block_list" "$CLI" docx block list --token "$DOCX_TOKEN" || true
        run_step "docs_get" "$CLI" docs get --token "$DOCX_TOKEN" --doc-type docx --content-type markdown || true
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
        echo "FAIL: unable to extract docx token from docx_create output"
    fi
fi

SHEETS_TITLE="smoke-sheets-${TS}"
if run_step "sheets_create" "$CLI" sheets create --title "$SHEETS_TITLE"; then
    SHEET_TOKEN="$(extract_first_json_field "$OUT_DIR/sheets_create.json" \
        "data.spreadsheet.spreadsheet_token" \
        "data.spreadsheet_token" \
        "data.spreadsheet.token" || true)"
    if [ -n "${SHEET_TOKEN:-}" ]; then
        run_step "sheets_get" "$CLI" sheets get --token "$SHEET_TOKEN" || true
        run_step "sheets_sheet_list" "$CLI" sheets sheet list --token "$SHEET_TOKEN" || true
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
        echo "FAIL: unable to extract sheets token from sheets_create output"
    fi
fi

BITABLE_NAME="smoke-bitable-${TS}"
if run_step "bitable_create" "$CLI" bitable create --name "$BITABLE_NAME"; then
    APP_TOKEN="$(extract_first_json_field "$OUT_DIR/bitable_create.json" \
        "data.app.app_token" \
        "data.app_token" || true)"
    if [ -n "${APP_TOKEN:-}" ]; then
        run_step "bitable_get" "$CLI" bitable get --app-token "$APP_TOKEN" || true
        run_step "bitable_table_list" "$CLI" bitable table list --app-token "$APP_TOKEN" || true
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
        echo "FAIL: unable to extract bitable app token from bitable_create output"
    fi
fi

echo ""
echo "Smoke test summary: PASS=$PASS_COUNT FAIL=$FAIL_COUNT"
echo "Artifacts: $OUT_DIR"

if [ "$FAIL_COUNT" -gt 0 ]; then
    exit 1
fi
