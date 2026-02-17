#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CLI="$SCRIPT_DIR/feishu-cli.sh"
TS="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="${TMPDIR:-/tmp}/feishu_cli_full_e2e_${TS}_$$"
mkdir -p "$OUT_DIR"

PASS_COUNT=0
FAIL_COUNT=0

DOCX_TOKEN=""
DOCX_ROOT_BLOCK_ID=""
DOCX_CHILD_BLOCK_ID=""

SHEET_TOKEN=""
SHEET_ID=""
FILTER_VIEW_ID=""
FLOAT_IMAGE_ID=""

BITABLE_APP_TOKEN=""
BITABLE_TABLE_ID=""
BITABLE_RECORD_ID=""
BITABLE_FIELD_ID=""
BITABLE_VIEW_ID=""
BITABLE_COPIED_APP_TOKEN=""

EXISTING_DOCX_TOKEN="${EXISTING_DOCX_TOKEN:-}"
EXISTING_SHEETS_TOKEN="${EXISTING_SHEETS_TOKEN:-}"
EXISTING_BITABLE_APP_TOKEN="${EXISTING_BITABLE_APP_TOKEN:-}"
EXISTING_BITABLE_TABLE_ID="${EXISTING_BITABLE_TABLE_ID:-}"
SHEETS_FLOAT_IMAGE_TOKEN="${SHEETS_FLOAT_IMAGE_TOKEN:-}"

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
        if isinstance(cur, dict):
            if part in cur:
                cur = cur[part]
                continue
            return None
        if isinstance(cur, list):
            try:
                idx = int(part)
            except ValueError:
                return None
            if idx < 0 or idx >= len(cur):
                return None
            cur = cur[idx]
            continue
        return None
    return cur

try:
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception:
    sys.exit(1)

for p in paths:
    value = lookup(data, p)
    if isinstance(value, (str, int, float)) and str(value) != "":
        print(value)
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

require_value() {
    local label="$1"
    local value="${2:-}"
    if [ -z "$value" ]; then
        FAIL_COUNT=$((FAIL_COUNT + 1))
        echo "FAIL: missing required value for $label"
        return 1
    fi
    return 0
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
keys = set()
with open(sys.argv[1], "r", encoding="utf-8") as f:
    for line in f:
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        keys.add(s.split("=", 1)[0].strip())
sys.exit(0 if {"FEISHU_APP_ID", "FEISHU_APP_SECRET"}.issubset(keys) else 1)
PY
}

if ! ensure_auth_present; then
    echo "Missing FEISHU credentials. Set FEISHU_APP_ID/FEISHU_APP_SECRET (or provide them in .env)."
    exit 3
fi

echo "Output directory: $OUT_DIR"
echo "Running full Feishu CLI E2E tests (docx/sheets/bitable)..."

# ----------------------
# Docx / Docs flow (new resource)
# ----------------------
DOCX_TITLE="full-docx-${TS}"
if run_step "docx_create" "$CLI" docx create --title "$DOCX_TITLE"; then
    DOCX_TOKEN="$(extract_first_json_field "$OUT_DIR/docx_create.json" \
        "data.document.document_id" \
        "data.document_id" \
        "data.document.document_token" || true)"
fi
require_value "DOCX_TOKEN" "$DOCX_TOKEN" || true

if [ -n "$DOCX_TOKEN" ]; then
    run_step "docx_get" "$CLI" docx get --token "$DOCX_TOKEN" || true
    run_step "docx_content" "$CLI" docx content --token "$DOCX_TOKEN" || true
    run_step "docx_block_list_initial" "$CLI" docx block list --token "$DOCX_TOKEN" || true
    run_step "docs_get_markdown" "$CLI" docs get --token "$DOCX_TOKEN" --doc-type docx --content-type markdown || true

    DOCX_ROOT_BLOCK_ID="$(extract_first_json_field "$OUT_DIR/docx_block_list_initial.json" \
        "data.items.0.block_id" \
        "data.items.0.block.block_id" || true)"
    require_value "DOCX_ROOT_BLOCK_ID" "$DOCX_ROOT_BLOCK_ID" || true

    if [ -n "$DOCX_ROOT_BLOCK_ID" ]; then
        run_step "docx_block_get_root" "$CLI" docx block get --token "$DOCX_TOKEN" --block-id "$DOCX_ROOT_BLOCK_ID" || true
        run_step "docx_block_create_child" "$CLI" docx block create --token "$DOCX_TOKEN" --block-id "$DOCX_ROOT_BLOCK_ID" \
            --data '{"children":[{"block_type":2,"text":{"elements":[{"text_run":{"content":"e2e child block"}}]}}]}' || true

        DOCX_CHILD_BLOCK_ID="$(extract_first_json_field "$OUT_DIR/docx_block_create_child.json" \
            "data.children.0.block_id" \
            "data.children.0.block.block_id" || true)"
        require_value "DOCX_CHILD_BLOCK_ID" "$DOCX_CHILD_BLOCK_ID" || true

        run_step "docx_block_list_after_create" "$CLI" docx block list --token "$DOCX_TOKEN" || true
        if [ -n "$DOCX_CHILD_BLOCK_ID" ]; then
            run_step "docx_block_get_child" "$CLI" docx block get --token "$DOCX_TOKEN" --block-id "$DOCX_CHILD_BLOCK_ID" || true
            run_step "docx_block_delete_child" "$CLI" docx block delete --token "$DOCX_TOKEN" --block-id "$DOCX_ROOT_BLOCK_ID" \
                --start-index 0 --end-index 1 || true
            run_step "docx_block_list_after_delete" "$CLI" docx block list --token "$DOCX_TOKEN" || true
        fi
    fi
fi

# ----------------------
# Sheets flow (new resource)
# ----------------------
SHEETS_TITLE="full-sheets-${TS}"
if run_step "sheets_create" "$CLI" sheets create --title "$SHEETS_TITLE"; then
    SHEET_TOKEN="$(extract_first_json_field "$OUT_DIR/sheets_create.json" \
        "data.spreadsheet.spreadsheet_token" \
        "data.spreadsheet_token" || true)"
fi
require_value "SHEET_TOKEN" "$SHEET_TOKEN" || true

if [ -n "$SHEET_TOKEN" ]; then
    run_step "sheets_get" "$CLI" sheets get --token "$SHEET_TOKEN" || true
    run_step "sheets_update" "$CLI" sheets update --token "$SHEET_TOKEN" --title "${SHEETS_TITLE}-updated" || true
    run_step "sheets_sheet_list" "$CLI" sheets sheet list --token "$SHEET_TOKEN" || true

    SHEET_ID="$(extract_first_json_field "$OUT_DIR/sheets_sheet_list.json" \
        "data.sheets.0.sheet_id" \
        "data.sheets.0.properties.sheet_id" || true)"
    require_value "SHEET_ID" "$SHEET_ID" || true

    if [ -n "$SHEET_ID" ]; then
        if run_step "sheets_filter_create" "$CLI" sheets filter create --token "$SHEET_TOKEN" --sheet-id "$SHEET_ID" \
            --data '{"range":"'"$SHEET_ID"'!A1:B20","col":"A","condition":{"filter_type":"text","compare_type":"contains","expected":["e2e"]}}'; then
            run_step "sheets_filter_get" "$CLI" sheets filter get --token "$SHEET_TOKEN" --sheet-id "$SHEET_ID" || true
            run_step "sheets_filter_update" "$CLI" sheets filter update --token "$SHEET_TOKEN" --sheet-id "$SHEET_ID" \
                --data '{"col":"A","condition":{"filter_type":"text","compare_type":"contains","expected":["updated"]}}' || true
            run_step "sheets_filter_delete" "$CLI" sheets filter delete --token "$SHEET_TOKEN" --sheet-id "$SHEET_ID" || true
        fi

        run_step "sheets_filter_view_create" "$CLI" sheets filter-view create --token "$SHEET_TOKEN" --sheet-id "$SHEET_ID" \
            --data '{"filter_view_name":"e2e-view","range":"'"$SHEET_ID"'!A1:B20"}' || true
        FILTER_VIEW_ID="$(extract_first_json_field "$OUT_DIR/sheets_filter_view_create.json" \
            "data.filter_view.filter_view_id" \
            "data.filter_view_id" || true)"
        require_value "FILTER_VIEW_ID" "$FILTER_VIEW_ID" || true
        run_step "sheets_filter_view_list" "$CLI" sheets filter-view list --token "$SHEET_TOKEN" --sheet-id "$SHEET_ID" || true
        if [ -n "$FILTER_VIEW_ID" ]; then
            run_step "sheets_filter_view_get" "$CLI" sheets filter-view get --token "$SHEET_TOKEN" --sheet-id "$SHEET_ID" --filter-view-id "$FILTER_VIEW_ID" || true
            run_step "sheets_filter_view_update" "$CLI" sheets filter-view update --token "$SHEET_TOKEN" --sheet-id "$SHEET_ID" \
                --filter-view-id "$FILTER_VIEW_ID" --data '{"filter_view_name":"e2e-view-updated"}' || true
            run_step "sheets_filter_view_delete" "$CLI" sheets filter-view delete --token "$SHEET_TOKEN" --sheet-id "$SHEET_ID" --filter-view-id "$FILTER_VIEW_ID" || true
        fi

        run_step "sheets_float_image_list" "$CLI" sheets float-image list --token "$SHEET_TOKEN" --sheet-id "$SHEET_ID" || true
        if [ -n "$SHEETS_FLOAT_IMAGE_TOKEN" ]; then
            run_step "sheets_float_image_create" "$CLI" sheets float-image create --token "$SHEET_TOKEN" --sheet-id "$SHEET_ID" \
                --data '{"float_image_token":"'"$SHEETS_FLOAT_IMAGE_TOKEN"'","range":"'"$SHEET_ID"'!A1:B2","width":120,"height":80,"offset_x":0,"offset_y":0}' || true
            FLOAT_IMAGE_ID="$(extract_first_json_field "$OUT_DIR/sheets_float_image_create.json" \
                "data.float_image.float_image_id" \
                "data.float_image_id" || true)"
            if [ -n "$FLOAT_IMAGE_ID" ]; then
                run_step "sheets_float_image_get" "$CLI" sheets float-image get --token "$SHEET_TOKEN" --sheet-id "$SHEET_ID" --float-image-id "$FLOAT_IMAGE_ID" || true
                run_step "sheets_float_image_update" "$CLI" sheets float-image update --token "$SHEET_TOKEN" --sheet-id "$SHEET_ID" \
                    --float-image-id "$FLOAT_IMAGE_ID" --data '{"width":200}' || true
                run_step "sheets_float_image_delete" "$CLI" sheets float-image delete --token "$SHEET_TOKEN" --sheet-id "$SHEET_ID" --float-image-id "$FLOAT_IMAGE_ID" || true
            fi
        else
            echo "SKIP: sheets_float_image_create/get/update/delete (set SHEETS_FLOAT_IMAGE_TOKEN)"
        fi
    fi
fi

# ----------------------
# Bitable flow (new resource)
# ----------------------
BITABLE_NAME="full-bitable-${TS}"
if run_step "bitable_create" "$CLI" bitable create --name "$BITABLE_NAME"; then
    BITABLE_APP_TOKEN="$(extract_first_json_field "$OUT_DIR/bitable_create.json" \
        "data.app.app_token" \
        "data.app_token" || true)"
fi
require_value "BITABLE_APP_TOKEN" "$BITABLE_APP_TOKEN" || true

if [ -n "$BITABLE_APP_TOKEN" ]; then
    run_step "bitable_get" "$CLI" bitable get --app-token "$BITABLE_APP_TOKEN" || true
    run_step "bitable_update" "$CLI" bitable update --app-token "$BITABLE_APP_TOKEN" --name "${BITABLE_NAME}-updated" || true
    run_step "bitable_copy" "$CLI" bitable copy --app-token "$BITABLE_APP_TOKEN" --name "${BITABLE_NAME}-copy" || true
    BITABLE_COPIED_APP_TOKEN="$(extract_first_json_field "$OUT_DIR/bitable_copy.json" \
        "data.app.app_token" \
        "data.app_token" || true)"

    run_step "bitable_table_create" "$CLI" bitable table create --app-token "$BITABLE_APP_TOKEN" --name "E2E_Table" || true
    BITABLE_TABLE_ID="$(extract_first_json_field "$OUT_DIR/bitable_table_create.json" \
        "data.table.table_id" \
        "data.table_id" || true)"
    if [ -z "$BITABLE_TABLE_ID" ]; then
        run_step "bitable_table_list_for_id" "$CLI" bitable table list --app-token "$BITABLE_APP_TOKEN" || true
        BITABLE_TABLE_ID="$(extract_first_json_field "$OUT_DIR/bitable_table_list_for_id.json" \
            "data.items.0.table_id" \
            "data.items.0.table.table_id" || true)"
    fi
    require_value "BITABLE_TABLE_ID" "$BITABLE_TABLE_ID" || true

    run_step "bitable_table_list" "$CLI" bitable table list --app-token "$BITABLE_APP_TOKEN" || true
    if [ -n "$BITABLE_TABLE_ID" ]; then
        run_step "bitable_table_patch" "$CLI" bitable table patch --app-token "$BITABLE_APP_TOKEN" --table-id "$BITABLE_TABLE_ID" --name "E2E_Table_Updated" || true

        BITABLE_RECORD_FIELD_NAME="E2E_Text"
        run_step "bitable_field_create" "$CLI" bitable field create --app-token "$BITABLE_APP_TOKEN" --table-id "$BITABLE_TABLE_ID" \
            --field-name "$BITABLE_RECORD_FIELD_NAME" --field-type 1 || true
        BITABLE_FIELD_ID="$(extract_first_json_field "$OUT_DIR/bitable_field_create.json" \
            "data.field.field_id" \
            "data.field_id" || true)"
        run_step "bitable_field_list" "$CLI" bitable field list --app-token "$BITABLE_APP_TOKEN" --table-id "$BITABLE_TABLE_ID" || true
        if [ -n "$BITABLE_FIELD_ID" ]; then
            BITABLE_RECORD_FIELD_NAME="E2E_Text_Updated"
            run_step "bitable_field_update" "$CLI" bitable field update --app-token "$BITABLE_APP_TOKEN" --table-id "$BITABLE_TABLE_ID" \
                --field-id "$BITABLE_FIELD_ID" --field-name "$BITABLE_RECORD_FIELD_NAME" --field-type 1 || true
        fi

        run_step "bitable_view_create" "$CLI" bitable view create --app-token "$BITABLE_APP_TOKEN" --table-id "$BITABLE_TABLE_ID" \
            --view-name "E2E_View" --view-type grid || true
        BITABLE_VIEW_ID="$(extract_first_json_field "$OUT_DIR/bitable_view_create.json" \
            "data.view.view_id" \
            "data.view_id" || true)"
        run_step "bitable_view_list" "$CLI" bitable view list --app-token "$BITABLE_APP_TOKEN" --table-id "$BITABLE_TABLE_ID" || true
        if [ -n "$BITABLE_VIEW_ID" ]; then
            run_step "bitable_view_get" "$CLI" bitable view get --app-token "$BITABLE_APP_TOKEN" --table-id "$BITABLE_TABLE_ID" --view-id "$BITABLE_VIEW_ID" || true
        fi

        run_step "bitable_record_create" "$CLI" bitable record create --app-token "$BITABLE_APP_TOKEN" --table-id "$BITABLE_TABLE_ID" \
            --fields '{"'"$BITABLE_RECORD_FIELD_NAME"'":"hello-e2e"}' || true
        BITABLE_RECORD_ID="$(extract_first_json_field "$OUT_DIR/bitable_record_create.json" \
            "data.record.record_id" \
            "data.record_id" || true)"
        run_step "bitable_record_list" "$CLI" bitable record list --app-token "$BITABLE_APP_TOKEN" --table-id "$BITABLE_TABLE_ID" || true
        if [ -n "$BITABLE_RECORD_ID" ]; then
            run_step "bitable_record_get" "$CLI" bitable record get --app-token "$BITABLE_APP_TOKEN" --table-id "$BITABLE_TABLE_ID" --record-id "$BITABLE_RECORD_ID" || true
            run_step "bitable_record_update" "$CLI" bitable record update --app-token "$BITABLE_APP_TOKEN" --table-id "$BITABLE_TABLE_ID" \
                --record-id "$BITABLE_RECORD_ID" --fields '{"'"$BITABLE_RECORD_FIELD_NAME"'":"hello-e2e-updated"}' || true
        fi

        if [ -n "$BITABLE_RECORD_ID" ]; then
            run_step "bitable_record_delete" "$CLI" bitable record delete --app-token "$BITABLE_APP_TOKEN" --table-id "$BITABLE_TABLE_ID" --record-id "$BITABLE_RECORD_ID" || true
        fi
        if [ -n "$BITABLE_VIEW_ID" ]; then
            run_step "bitable_view_delete" "$CLI" bitable view delete --app-token "$BITABLE_APP_TOKEN" --table-id "$BITABLE_TABLE_ID" --view-id "$BITABLE_VIEW_ID" || true
        fi
        if [ -n "$BITABLE_FIELD_ID" ]; then
            run_step "bitable_field_delete" "$CLI" bitable field delete --app-token "$BITABLE_APP_TOKEN" --table-id "$BITABLE_TABLE_ID" --field-id "$BITABLE_FIELD_ID" || true
        fi
        run_step "bitable_table_delete" "$CLI" bitable table delete --app-token "$BITABLE_APP_TOKEN" --table-id "$BITABLE_TABLE_ID" || true
    fi
fi

echo ""
echo "Running existing-resource modification checks (optional)..."

if [ -n "$EXISTING_DOCX_TOKEN" ]; then
    EXISTING_DOCX_ROOT_BLOCK_ID=""
    EXISTING_DOCX_CHILD_BLOCK_ID=""
    run_step "existing_docx_block_list_before" "$CLI" docx block list --token "$EXISTING_DOCX_TOKEN" || true
    EXISTING_DOCX_ROOT_BLOCK_ID="$(extract_first_json_field "$OUT_DIR/existing_docx_block_list_before.json" \
        "data.items.0.block_id" \
        "data.items.0.block.block_id" || true)"
    if [ -n "$EXISTING_DOCX_ROOT_BLOCK_ID" ]; then
        run_step "existing_docx_block_create_child" "$CLI" docx block create --token "$EXISTING_DOCX_TOKEN" \
            --block-id "$EXISTING_DOCX_ROOT_BLOCK_ID" \
            --data '{"children":[{"block_type":2,"text":{"elements":[{"text_run":{"content":"existing-docx-e2e"}}]}}]}' || true
        EXISTING_DOCX_CHILD_BLOCK_ID="$(extract_first_json_field "$OUT_DIR/existing_docx_block_create_child.json" \
            "data.children.0.block_id" \
            "data.children.0.block.block_id" || true)"
        run_step "existing_docx_block_list_after_create" "$CLI" docx block list --token "$EXISTING_DOCX_TOKEN" || true
        if [ -n "$EXISTING_DOCX_CHILD_BLOCK_ID" ]; then
            run_step "existing_docx_block_get_child" "$CLI" docx block get --token "$EXISTING_DOCX_TOKEN" --block-id "$EXISTING_DOCX_CHILD_BLOCK_ID" || true
            run_step "existing_docx_block_delete_child" "$CLI" docx block delete --token "$EXISTING_DOCX_TOKEN" \
                --block-id "$EXISTING_DOCX_ROOT_BLOCK_ID" --start-index 0 --end-index 1 || true
            run_step "existing_docx_block_list_after_delete" "$CLI" docx block list --token "$EXISTING_DOCX_TOKEN" || true
        fi
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
        echo "FAIL: unable to resolve root block for EXISTING_DOCX_TOKEN"
    fi
else
    echo "SKIP: existing docx flow (set EXISTING_DOCX_TOKEN)"
fi

if [ -n "$EXISTING_SHEETS_TOKEN" ]; then
    EXISTING_SHEET_ID=""
    EXISTING_FILTER_VIEW_ID=""
    run_step "existing_sheets_get" "$CLI" sheets get --token "$EXISTING_SHEETS_TOKEN" || true
    run_step "existing_sheets_sheet_list" "$CLI" sheets sheet list --token "$EXISTING_SHEETS_TOKEN" || true
    EXISTING_SHEET_ID="$(extract_first_json_field "$OUT_DIR/existing_sheets_sheet_list.json" \
        "data.sheets.0.sheet_id" \
        "data.sheets.0.properties.sheet_id" || true)"
    if [ -n "$EXISTING_SHEET_ID" ]; then
        if run_step "existing_sheets_filter_create" "$CLI" sheets filter create --token "$EXISTING_SHEETS_TOKEN" --sheet-id "$EXISTING_SHEET_ID" \
            --data '{"range":"'"$EXISTING_SHEET_ID"'!A1:B20","col":"A","condition":{"filter_type":"text","compare_type":"contains","expected":["existing-e2e"]}}'; then
            run_step "existing_sheets_filter_update" "$CLI" sheets filter update --token "$EXISTING_SHEETS_TOKEN" --sheet-id "$EXISTING_SHEET_ID" \
                --data '{"col":"A","condition":{"filter_type":"text","compare_type":"contains","expected":["existing-e2e-updated"]}}' || true
            run_step "existing_sheets_filter_get" "$CLI" sheets filter get --token "$EXISTING_SHEETS_TOKEN" --sheet-id "$EXISTING_SHEET_ID" || true
            run_step "existing_sheets_filter_delete" "$CLI" sheets filter delete --token "$EXISTING_SHEETS_TOKEN" --sheet-id "$EXISTING_SHEET_ID" || true
        fi

        run_step "existing_sheets_filter_view_create" "$CLI" sheets filter-view create --token "$EXISTING_SHEETS_TOKEN" \
            --sheet-id "$EXISTING_SHEET_ID" --data '{"filter_view_name":"existing-e2e-view","range":"'"$EXISTING_SHEET_ID"'!A1:B20"}' || true
        EXISTING_FILTER_VIEW_ID="$(extract_first_json_field "$OUT_DIR/existing_sheets_filter_view_create.json" \
            "data.filter_view.filter_view_id" \
            "data.filter_view_id" || true)"
        run_step "existing_sheets_filter_view_list" "$CLI" sheets filter-view list --token "$EXISTING_SHEETS_TOKEN" --sheet-id "$EXISTING_SHEET_ID" || true
        if [ -n "$EXISTING_FILTER_VIEW_ID" ]; then
            run_step "existing_sheets_filter_view_get" "$CLI" sheets filter-view get --token "$EXISTING_SHEETS_TOKEN" \
                --sheet-id "$EXISTING_SHEET_ID" --filter-view-id "$EXISTING_FILTER_VIEW_ID" || true
            run_step "existing_sheets_filter_view_update" "$CLI" sheets filter-view update --token "$EXISTING_SHEETS_TOKEN" \
                --sheet-id "$EXISTING_SHEET_ID" --filter-view-id "$EXISTING_FILTER_VIEW_ID" \
                --data '{"filter_view_name":"existing-e2e-view-updated"}' || true
            run_step "existing_sheets_filter_view_delete" "$CLI" sheets filter-view delete --token "$EXISTING_SHEETS_TOKEN" \
                --sheet-id "$EXISTING_SHEET_ID" --filter-view-id "$EXISTING_FILTER_VIEW_ID" || true
        fi
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
        echo "FAIL: unable to resolve sheet_id for EXISTING_SHEETS_TOKEN"
    fi
else
    echo "SKIP: existing sheets flow (set EXISTING_SHEETS_TOKEN)"
fi

if [ -n "$EXISTING_BITABLE_APP_TOKEN" ]; then
    EXISTING_TABLE_ID="$EXISTING_BITABLE_TABLE_ID"
    EXISTING_FIELD_ID=""
    EXISTING_VIEW_ID=""
    EXISTING_RECORD_ID=""
    run_step "existing_bitable_get" "$CLI" bitable get --app-token "$EXISTING_BITABLE_APP_TOKEN" || true
    run_step "existing_bitable_table_list" "$CLI" bitable table list --app-token "$EXISTING_BITABLE_APP_TOKEN" || true
    if [ -z "$EXISTING_TABLE_ID" ]; then
        EXISTING_TABLE_ID="$(extract_first_json_field "$OUT_DIR/existing_bitable_table_list.json" \
            "data.items.0.table_id" \
            "data.items.0.table.table_id" || true)"
    fi
    if [ -n "$EXISTING_TABLE_ID" ]; then
        EXISTING_RECORD_FIELD_NAME="EXISTING_E2E_TEXT_${TS}"
        run_step "existing_bitable_table_patch" "$CLI" bitable table patch --app-token "$EXISTING_BITABLE_APP_TOKEN" \
            --table-id "$EXISTING_TABLE_ID" --name "EXISTING_E2E_PATCH_${TS}" || true

        run_step "existing_bitable_field_create" "$CLI" bitable field create --app-token "$EXISTING_BITABLE_APP_TOKEN" \
            --table-id "$EXISTING_TABLE_ID" --field-name "$EXISTING_RECORD_FIELD_NAME" --field-type 1 || true
        EXISTING_FIELD_ID="$(extract_first_json_field "$OUT_DIR/existing_bitable_field_create.json" \
            "data.field.field_id" \
            "data.field_id" || true)"
        run_step "existing_bitable_field_list" "$CLI" bitable field list --app-token "$EXISTING_BITABLE_APP_TOKEN" --table-id "$EXISTING_TABLE_ID" || true
        if [ -n "$EXISTING_FIELD_ID" ]; then
            EXISTING_RECORD_FIELD_NAME="EXISTING_E2E_TEXT_UPDATED_${TS}"
            run_step "existing_bitable_field_update" "$CLI" bitable field update --app-token "$EXISTING_BITABLE_APP_TOKEN" \
                --table-id "$EXISTING_TABLE_ID" --field-id "$EXISTING_FIELD_ID" \
                --field-name "$EXISTING_RECORD_FIELD_NAME" --field-type 1 || true
        fi

        run_step "existing_bitable_view_create" "$CLI" bitable view create --app-token "$EXISTING_BITABLE_APP_TOKEN" \
            --table-id "$EXISTING_TABLE_ID" --view-name "EXISTING_E2E_VIEW_${TS}" --view-type grid || true
        EXISTING_VIEW_ID="$(extract_first_json_field "$OUT_DIR/existing_bitable_view_create.json" \
            "data.view.view_id" \
            "data.view_id" || true)"
        run_step "existing_bitable_view_list" "$CLI" bitable view list --app-token "$EXISTING_BITABLE_APP_TOKEN" --table-id "$EXISTING_TABLE_ID" || true
        if [ -n "$EXISTING_VIEW_ID" ]; then
            run_step "existing_bitable_view_get" "$CLI" bitable view get --app-token "$EXISTING_BITABLE_APP_TOKEN" \
                --table-id "$EXISTING_TABLE_ID" --view-id "$EXISTING_VIEW_ID" || true
        fi

        run_step "existing_bitable_record_create" "$CLI" bitable record create --app-token "$EXISTING_BITABLE_APP_TOKEN" \
            --table-id "$EXISTING_TABLE_ID" --fields '{"'"$EXISTING_RECORD_FIELD_NAME"'":"existing-e2e"}' || true
        EXISTING_RECORD_ID="$(extract_first_json_field "$OUT_DIR/existing_bitable_record_create.json" \
            "data.record.record_id" \
            "data.record_id" || true)"
        run_step "existing_bitable_record_list" "$CLI" bitable record list --app-token "$EXISTING_BITABLE_APP_TOKEN" --table-id "$EXISTING_TABLE_ID" || true
        if [ -n "$EXISTING_RECORD_ID" ]; then
            run_step "existing_bitable_record_get" "$CLI" bitable record get --app-token "$EXISTING_BITABLE_APP_TOKEN" \
                --table-id "$EXISTING_TABLE_ID" --record-id "$EXISTING_RECORD_ID" || true
            run_step "existing_bitable_record_update" "$CLI" bitable record update --app-token "$EXISTING_BITABLE_APP_TOKEN" \
                --table-id "$EXISTING_TABLE_ID" --record-id "$EXISTING_RECORD_ID" --fields '{"'"$EXISTING_RECORD_FIELD_NAME"'":"existing-e2e-updated"}' || true
            run_step "existing_bitable_record_delete" "$CLI" bitable record delete --app-token "$EXISTING_BITABLE_APP_TOKEN" \
                --table-id "$EXISTING_TABLE_ID" --record-id "$EXISTING_RECORD_ID" || true
        fi

        if [ -n "$EXISTING_VIEW_ID" ]; then
            run_step "existing_bitable_view_delete" "$CLI" bitable view delete --app-token "$EXISTING_BITABLE_APP_TOKEN" \
                --table-id "$EXISTING_TABLE_ID" --view-id "$EXISTING_VIEW_ID" || true
        fi
        if [ -n "$EXISTING_FIELD_ID" ]; then
            run_step "existing_bitable_field_delete" "$CLI" bitable field delete --app-token "$EXISTING_BITABLE_APP_TOKEN" \
                --table-id "$EXISTING_TABLE_ID" --field-id "$EXISTING_FIELD_ID" || true
        fi
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
        echo "FAIL: unable to resolve table_id for EXISTING_BITABLE_APP_TOKEN"
    fi
else
    echo "SKIP: existing bitable flow (set EXISTING_BITABLE_APP_TOKEN)"
fi

echo ""
echo "Full E2E summary: PASS=$PASS_COUNT FAIL=$FAIL_COUNT"
echo "Artifacts: $OUT_DIR"
if [ -n "$BITABLE_COPIED_APP_TOKEN" ]; then
    echo "Copied bitable app token: $BITABLE_COPIED_APP_TOKEN"
fi
echo "Docx token: ${DOCX_TOKEN:-N/A}"
echo "Sheets token: ${SHEET_TOKEN:-N/A}"
echo "Bitable app token: ${BITABLE_APP_TOKEN:-N/A}"

if [ "$FAIL_COUNT" -gt 0 ]; then
    exit 1
fi
