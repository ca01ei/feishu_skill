#!/usr/bin/env bash
# validate-results.sh — verify resources created by a haiku agent test run
#
# Usage (env vars):
#   DOCX_TOKEN=xxx BITABLE_APP_TOKEN=xxx BITABLE_TABLE_ID=xxx SHEETS_TOKEN=xxx \
#     bash tests/validate-results.sh
#
# Usage (parse haiku summary block from file):
#   bash tests/validate-results.sh --from haiku_output.txt
#
# Usage (parse haiku summary block from stdin):
#   cat haiku_output.txt | bash tests/validate-results.sh --from -

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CLI="$PROJECT_DIR/scripts/feishu-cli.sh"
TS="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="${TMPDIR:-/tmp}/feishu_skill_validate_${TS}_$$"
mkdir -p "$OUT_DIR"

PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0

# ---------------------------------------------------------------------------
# Parse haiku summary block from a file / stdin
# ---------------------------------------------------------------------------
parse_from_file() {
    local src="$1"
    local content
    if [ "$src" = "-" ]; then
        content="$(cat)"
    else
        content="$(cat "$src")"
    fi

    extract_var() {
        echo "$content" | grep -m1 "^${1}:" | sed "s/^${1}: *//" | tr -d '\r\n'
    }

    local docx; docx="$(extract_var DOCX_TOKEN)"
    local app;  app="$(extract_var BITABLE_APP_TOKEN)"
    local tbl;  tbl="$(extract_var BITABLE_TABLE_ID)"
    local rec;  rec="$(extract_var BITABLE_RECORD_ID)"
    local sht;  sht="$(extract_var SHEETS_TOKEN)"

    [ -n "$docx" ] && [ "$docx" != "N/A" ] && export DOCX_TOKEN="$docx"
    [ -n "$app"  ] && [ "$app"  != "N/A" ] && export BITABLE_APP_TOKEN="$app"
    [ -n "$tbl"  ] && [ "$tbl"  != "N/A" ] && export BITABLE_TABLE_ID="$tbl"
    [ -n "$rec"  ] && [ "$rec"  != "N/A" ] && export BITABLE_RECORD_ID="$rec"
    [ -n "$sht"  ] && [ "$sht"  != "N/A" ] && export SHEETS_TOKEN="$sht"

    echo "Parsed from file: DOCX_TOKEN=${DOCX_TOKEN:-<unset>}"
    echo "                  BITABLE_APP_TOKEN=${BITABLE_APP_TOKEN:-<unset>}"
    echo "                  BITABLE_TABLE_ID=${BITABLE_TABLE_ID:-<unset>}"
    echo "                  SHEETS_TOKEN=${SHEETS_TOKEN:-<unset>}"
}

if [ "${1:-}" = "--from" ]; then
    parse_from_file "${2:--}"
fi

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
extract_first_json_field() {
    local json_file="$1"
    shift
    python3 - "$json_file" "$@" <<'PY'
import json, sys

def lookup(obj, path):
    cur = obj
    for part in path.split("."):
        if isinstance(cur, dict):
            if part in cur: cur = cur[part]; continue
            return None
        if isinstance(cur, list):
            try: idx = int(part)
            except ValueError: return None
            if 0 <= idx < len(cur): cur = cur[idx]; continue
            return None
        return None
    return cur

try:
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception:
    sys.exit(1)

for p in sys.argv[2:]:
    v = lookup(data, p)
    if isinstance(v, (str, int, float)) and str(v) != "":
        print(v); sys.exit(0)
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
        [ -s "$out_json" ] && cat "$out_json"
        [ -s "$out_err"  ] && cat "$out_err"
    fi
    return "$code"
}

skip_step() {
    local name="$1"
    local reason="${2:-missing prerequisite token}"
    SKIP_COUNT=$((SKIP_COUNT + 1))
    echo ""
    echo "SKIP: $name — $reason"
}

# ---------------------------------------------------------------------------
# Docx validation
# ---------------------------------------------------------------------------
if [ -n "${DOCX_TOKEN:-}" ]; then
    echo ""
    echo "--- Validating docx (token=$DOCX_TOKEN) ---"

    run_step "val_docx_get" "$CLI" docx get --token "$DOCX_TOKEN" || true

    # Verify the expected content marker is present
    if run_step "val_docx_content" "$CLI" docx content --token "$DOCX_TOKEN"; then
        if python3 - "$OUT_DIR/val_docx_content.json" <<'PY'
import json, sys
try:
    data = json.load(open(sys.argv[1], encoding="utf-8"))
except Exception:
    sys.exit(1)
content_str = json.dumps(data, ensure_ascii=False)
sys.exit(0 if "AgentTestMark-CONTENT-1" in content_str else 1)
PY
        then
            PASS_COUNT=$((PASS_COUNT + 1))
            echo "PASS: val_docx_content_has_marker (AgentTestMark-CONTENT-1 found)"
        else
            FAIL_COUNT=$((FAIL_COUNT + 1))
            echo "FAIL: val_docx_content_has_marker (AgentTestMark-CONTENT-1 NOT found in document)"
        fi
    fi
else
    skip_step "val_docx" "DOCX_TOKEN not set"
fi

# ---------------------------------------------------------------------------
# Bitable validation
# ---------------------------------------------------------------------------
if [ -n "${BITABLE_APP_TOKEN:-}" ]; then
    echo ""
    echo "--- Validating bitable (app_token=$BITABLE_APP_TOKEN) ---"

    run_step "val_bitable_app_get" "$CLI" bitable app get --app-token "$BITABLE_APP_TOKEN" || true

    if [ -n "${BITABLE_TABLE_ID:-}" ]; then
        # Verify the table_id is discoverable via table list (the key pitfall test)
        if run_step "val_bitable_table_list" "$CLI" bitable table list --app-token "$BITABLE_APP_TOKEN"; then
            if python3 - "$OUT_DIR/val_bitable_table_list.json" "$BITABLE_TABLE_ID" <<'PY'
import json, sys
try:
    data = json.load(open(sys.argv[1], encoding="utf-8"))
except Exception:
    sys.exit(1)
needle = sys.argv[2]
sys.exit(0 if needle in json.dumps(data) else 1)
PY
            then
                PASS_COUNT=$((PASS_COUNT + 1))
                echo "PASS: val_bitable_table_id_in_list (table_id found via list)"
            else
                FAIL_COUNT=$((FAIL_COUNT + 1))
                echo "FAIL: val_bitable_table_id_in_list (table_id $BITABLE_TABLE_ID not in table list — haiku may have used a hard-coded guess)"
            fi
        fi

        # Verify field list works on the table
        run_step "val_bitable_field_list" \
            "$CLI" bitable field list --app-token "$BITABLE_APP_TOKEN" --table-id "$BITABLE_TABLE_ID" || true
    else
        skip_step "val_bitable_table" "BITABLE_TABLE_ID not set"
    fi
else
    skip_step "val_bitable" "BITABLE_APP_TOKEN not set"
fi

# ---------------------------------------------------------------------------
# Sheets validation
# ---------------------------------------------------------------------------
if [ -n "${SHEETS_TOKEN:-}" ]; then
    echo ""
    echo "--- Validating sheets (token=$SHEETS_TOKEN) ---"

    run_step "val_sheets_get" "$CLI" sheets get --token "$SHEETS_TOKEN" || true

    # The critical test: can we list sheets and get a sheet_id?
    if run_step "val_sheets_sheet_list" "$CLI" sheets sheet list --token "$SHEETS_TOKEN"; then
        FOUND_SHEET_ID="$(extract_first_json_field \
            "$OUT_DIR/val_sheets_sheet_list.json" \
            "data.sheets.0.sheet_id" \
            "data.0.sheet_id" || true)"
        if [ -n "$FOUND_SHEET_ID" ]; then
            PASS_COUNT=$((PASS_COUNT + 1))
            echo "PASS: val_sheets_has_sheet_id (found sheet_id=$FOUND_SHEET_ID via list)"
        else
            FAIL_COUNT=$((FAIL_COUNT + 1))
            echo "FAIL: val_sheets_has_sheet_id (could not extract sheet_id from list response)"
        fi
    fi
else
    skip_step "val_sheets" "SHEETS_TOKEN not set"
fi

# ---------------------------------------------------------------------------
# Error response validation (static, no token needed)
# The command is EXPECTED to fail with a non-zero exit; we validate the JSON format.
# ---------------------------------------------------------------------------
echo ""
echo "--- Validating error response format ---"
_ERR_OUT="$OUT_DIR/val_error_invalid_token.json"
_ERR_ERR="$OUT_DIR/val_error_invalid_token.err"
echo ""
echo "==> val_error_format"
set +e
"$CLI" docx get --token "INVALID_TOKEN_HAIKU_TEST_XYZ" >"$_ERR_OUT" 2>"$_ERR_ERR"
_ERR_CODE=$?
set -e

if [ "$_ERR_CODE" -ne 0 ] && python3 - "$_ERR_OUT" <<'PY'
import json, sys
try:
    data = json.load(open(sys.argv[1], encoding="utf-8"))
except Exception:
    print("ERROR: response is not valid JSON")
    sys.exit(1)
code_field = data.get("code") or (data.get("data") or {}).get("code")
msg_field = data.get("msg") or data.get("message")
if code_field is not None and str(code_field) != "0":
    print(f"OK: error code={code_field}, msg={msg_field}")
    sys.exit(0)
sys.exit(1)
PY
then
    PASS_COUNT=$((PASS_COUNT + 1))
    echo "PASS: val_error_format (non-zero exit + parseable JSON error code)"
else
    FAIL_COUNT=$((FAIL_COUNT + 1))
    echo "FAIL: val_error_format (exit=$_ERR_CODE; expected non-zero exit AND parseable error JSON)"
    [ -s "$_ERR_OUT" ] && cat "$_ERR_OUT"
    [ -s "$_ERR_ERR" ] && cat "$_ERR_ERR"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "=== VALIDATION SUMMARY ==="
echo "Output dir: $OUT_DIR"
echo "PASS: $PASS_COUNT"
echo "FAIL: $FAIL_COUNT"
echo "SKIP: $SKIP_COUNT"
echo ""
if [ "$FAIL_COUNT" -eq 0 ]; then
    echo "All validations passed."
    exit 0
else
    echo "Some validations failed — check output above."
    exit 1
fi
