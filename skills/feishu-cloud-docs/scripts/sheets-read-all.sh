#!/usr/bin/env bash
# 获取一个电子表格的基本信息和所有 Sheet 列表（含 sheet_id）
# 用法: bash skills/feishu-cloud-docs/scripts/sheets-read-all.sh <spreadsheet_token>
#
# 示例:
#   bash skills/feishu-cloud-docs/scripts/sheets-read-all.sh "shtcnABCD1234"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")"
CLI="$PROJECT_DIR/scripts/feishu-cli.sh"

TOKEN="${1:?用法: $0 <spreadsheet_token>}"

echo "=== 读取电子表格信息 ==="
echo "Token: $TOKEN"
echo ""

# Step 1: 获取电子表格基本信息
echo ">>> [1/2] 获取表格元数据..."
META=$("$CLI" sheets get --token "$TOKEN")

if ! echo "$META" | python3 -c "import json,sys; d=json.load(sys.stdin); exit(0 if d.get('success') else 1)" 2>/dev/null; then
    echo "ERROR: 获取表格信息失败"
    echo "$META"
    exit 1
fi

TITLE=$(echo "$META" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('data',{}).get('spreadsheet',{}).get('title','(未知)'))" 2>/dev/null || echo "(未知)")
echo "✓ 表格标题: $TITLE"

# Step 2: 列出所有 Sheet
echo ""
echo ">>> [2/2] 列出所有 Sheet..."
SHEETS=$("$CLI" sheets sheet list --token "$TOKEN")

if ! echo "$SHEETS" | python3 -c "import json,sys; d=json.load(sys.stdin); exit(0 if d.get('success') else 1)" 2>/dev/null; then
    echo "ERROR: 获取 Sheet 列表失败"
    echo "$SHEETS"
    exit 1
fi

echo ""
echo "=== Sheet 列表 ==="
echo "$SHEETS" | python3 -c "
import json, sys
d = json.load(sys.stdin)
sheets = d.get('data', {}).get('sheets', [])
print(f'共 {len(sheets)} 个 Sheet:')
print()
for s in sheets:
    sheet_id = s.get('sheet_id', '?')
    title    = s.get('title', '(无标题)')
    index    = s.get('index', '?')
    rows     = s.get('row_count', '?')
    cols     = s.get('column_count', '?')
    print(f'  [{index}] sheet_id={sheet_id}  title={title}  ({rows}行 x {cols}列)')
print()
print('提示: 使用 sheet_id 作为 --sheet-id 参数')
" 2>/dev/null || echo "$SHEETS"
