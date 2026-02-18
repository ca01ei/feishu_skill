#!/usr/bin/env bash
# 演示 Bitable 记录的完整增删改查（CRUD）
# 用法: bash skills/feishu-cloud-docs/scripts/bitable-full-crud.sh <app_token> <table_id>
#
# 如果不知道 table_id，先运行:
#   scripts/feishu-cli.sh bitable table list --app-token <app_token>
#
# 示例:
#   bash skills/feishu-cloud-docs/scripts/bitable-full-crud.sh "bascnABCD1234" "tblXXXX1111"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")"
CLI="$PROJECT_DIR/scripts/feishu-cli.sh"

APP_TOKEN="${1:?用法: $0 <app_token> <table_id>}"
TABLE_ID="${2:?用法: $0 <app_token> <table_id>}"

echo "=== Bitable Record CRUD 演示 ==="
echo "App token:  $APP_TOKEN"
echo "Table ID:   $TABLE_ID"
echo ""

# Step 1: 查看字段列表（了解字段名）
echo ">>> [0/5] 查看字段结构（用于确认字段名）..."
FIELDS_OUTPUT=$("$CLI" bitable field list --app-token "$APP_TOKEN" --table-id "$TABLE_ID" 2>&1) || true
echo "$FIELDS_OUTPUT" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    fields = d.get('data', {}).get('items', [])
    print(f'  共 {len(fields)} 个字段:')
    for f in fields:
        print(f'    field_id={f.get(\"field_id\",\"?\")}  name={f.get(\"field_name\",\"?\")}  type={f.get(\"type\",\"?\")}')
except Exception:
    pass
" 2>/dev/null || true

echo ""

# Step 2: 列出现有记录
echo ">>> [1/5] 列出当前记录（最多 5 条）..."
"$CLI" bitable record list \
    --app-token "$APP_TOKEN" \
    --table-id "$TABLE_ID" \
    --page-size 5

echo ""

# Step 3: 创建测试记录
echo ">>> [2/5] 创建测试记录..."
# 使用通用字段名，实际使用时请修改为目标表的真实字段名
TEST_FIELDS='{"Name":"CRUD-演示记录"}'
CREATE_OUTPUT=$("$CLI" bitable record create \
    --app-token "$APP_TOKEN" \
    --table-id "$TABLE_ID" \
    --fields "$TEST_FIELDS")
echo "$CREATE_OUTPUT"

if ! echo "$CREATE_OUTPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); exit(0 if d.get('success') else 1)" 2>/dev/null; then
    echo ""
    echo "⚠️  创建失败。可能原因：字段名 'Name' 在此表中不存在。"
    echo "    请先查看上方字段列表，修改 TEST_FIELDS 变量中的字段名后重试。"
    exit 1
fi

RECORD_ID=$(echo "$CREATE_OUTPUT" | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['record']['record_id'])")
echo "✓ 创建成功，record_id: $RECORD_ID"

echo ""

# Step 4: 查询该记录
echo ">>> [3/5] 查询该记录..."
"$CLI" bitable record get \
    --app-token "$APP_TOKEN" \
    --table-id "$TABLE_ID" \
    --record-id "$RECORD_ID"

echo ""

# Step 5: 更新该记录
echo ">>> [4/5] 更新该记录..."
UPDATE_FIELDS='{"Name":"CRUD-演示记录（已更新）"}'
UPDATE_OUTPUT=$("$CLI" bitable record update \
    --app-token "$APP_TOKEN" \
    --table-id "$TABLE_ID" \
    --record-id "$RECORD_ID" \
    --fields "$UPDATE_FIELDS")
echo "$UPDATE_OUTPUT"

if ! echo "$UPDATE_OUTPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); exit(0 if d.get('success') else 1)" 2>/dev/null; then
    echo "⚠️  更新失败，继续执行删除..."
fi

echo ""

# Step 6: 删除该记录
echo ">>> [5/5] 删除该记录..."
DELETE_OUTPUT=$("$CLI" bitable record delete \
    --app-token "$APP_TOKEN" \
    --table-id "$TABLE_ID" \
    --record-id "$RECORD_ID")
echo "$DELETE_OUTPUT"

if echo "$DELETE_OUTPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); exit(0 if d.get('success') else 1)" 2>/dev/null; then
    echo "✓ 删除成功"
fi

echo ""
echo "=== CRUD 演示完成 ==="
