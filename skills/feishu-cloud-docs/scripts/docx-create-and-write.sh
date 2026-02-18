#!/usr/bin/env bash
# 创建一个新的飞书文档（docx）并写入文本段落
# 用法: bash skills/feishu-cloud-docs/scripts/docx-create-and-write.sh <title> <text_content> [folder_token]
#
# 参数:
#   title        文档标题（必填）
#   text_content 要写入的文本内容（必填）
#   folder_token 目标文件夹 token（可选，不填则放到根目录）
#
# 示例:
#   bash skills/feishu-cloud-docs/scripts/docx-create-and-write.sh "会议记录" "今天讨论了产品规划"
#   bash skills/feishu-cloud-docs/scripts/docx-create-and-write.sh "周报" "本周完成了..." "fldcnXxx"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")"
CLI="$PROJECT_DIR/scripts/feishu-cli.sh"

TITLE="${1:?用法: $0 <title> <text_content> [folder_token]}"
CONTENT="${2:?用法: $0 <title> <text_content> [folder_token]}"
FOLDER_TOKEN="${3:-}"

echo "=== 创建飞书文档并写入内容 ==="
echo "标题: $TITLE"
echo ""

# Step 1: 创建文档
echo ">>> [1/3] 创建文档..."
if [ -n "$FOLDER_TOKEN" ]; then
    CREATE_OUTPUT=$("$CLI" docx create --title "$TITLE" --folder-token "$FOLDER_TOKEN")
else
    CREATE_OUTPUT=$("$CLI" docx create --title "$TITLE")
fi

if ! echo "$CREATE_OUTPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); exit(0 if d.get('success') else 1)" 2>/dev/null; then
    echo "ERROR: 创建文档失败"
    echo "$CREATE_OUTPUT"
    exit 1
fi

DOC_TOKEN=$(echo "$CREATE_OUTPUT" | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['document']['document_id'])")
echo "✓ 文档创建成功，token: $DOC_TOKEN"

# Step 2: 获取文档根块 ID
echo ""
echo ">>> [2/3] 获取文档根块 ID..."
BLOCKS_OUTPUT=$("$CLI" docx block list --token "$DOC_TOKEN")

if ! echo "$BLOCKS_OUTPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); exit(0 if d.get('success') else 1)" 2>/dev/null; then
    echo "ERROR: 获取块列表失败"
    echo "$BLOCKS_OUTPUT"
    exit 1
fi

ROOT_BLOCK_ID=$(echo "$BLOCKS_OUTPUT" | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['items'][0]['block_id'])")
echo "✓ 根块 ID: $ROOT_BLOCK_ID"

# Step 3: 写入文本段落
echo ""
echo ">>> [3/3] 写入文本段落..."

# 用 python3 构建 JSON，避免 shell 转义问题
BLOCK_DATA=$(python3 -c "
import json
data = {
    'children': [{
        'block_type': 2,
        'text': {
            'elements': [{'text_run': {'content': '''$CONTENT''', 'text_element_style': {}}}],
            'style': {}
        }
    }]
}
print(json.dumps(data, ensure_ascii=False))
")

WRITE_OUTPUT=$("$CLI" docx block create \
    --token "$DOC_TOKEN" \
    --block-id "$ROOT_BLOCK_ID" \
    --data "$BLOCK_DATA")

if ! echo "$WRITE_OUTPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); exit(0 if d.get('success') else 1)" 2>/dev/null; then
    echo "ERROR: 写入内容失败"
    echo "$WRITE_OUTPUT"
    exit 1
fi

echo "✓ 文本写入成功"

echo ""
echo "=== 完成 ==="
echo "文档 token:  $DOC_TOKEN"
echo "飞书 URL:    https://feishu.cn/docx/$DOC_TOKEN"
