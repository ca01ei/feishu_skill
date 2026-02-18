#!/usr/bin/env bash
# 列出所有飞书 Wiki 知识空间及其根节点
# 用法: bash skills/feishu-cloud-docs/scripts/wiki-list-all.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")"
CLI="$PROJECT_DIR/scripts/feishu-cli.sh"

echo "=== 飞书 Wiki 知识库概览 ==="
echo ""

# Step 1: 列出所有知识空间
echo ">>> [1/2] 获取所有知识空间..."
SPACES_OUTPUT=$("$CLI" wiki space list)

if ! echo "$SPACES_OUTPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); exit(0 if d.get('success') else 1)" 2>/dev/null; then
    echo "ERROR: 获取知识空间失败"
    echo "$SPACES_OUTPUT"
    exit 1
fi

# 解析 space_id 列表
SPACE_INFO=$(echo "$SPACES_OUTPUT" | python3 -c "
import json, sys
d = json.load(sys.stdin)
spaces = d.get('data', {}).get('items', [])
print(f'共 {len(spaces)} 个知识空间:')
for s in spaces:
    space_id = s.get('space_id', '?')
    name     = s.get('name', '(未命名)')
    desc     = s.get('description', '')
    vis      = s.get('visibility', '?')
    print(f'  space_id={space_id}  name={name}  visibility={vis}')
    if desc:
        print(f'    描述: {desc}')
    # 输出 space_id 到 stdout 供后续使用（单独一行，便于 grep）
    print(f'__SPACE_ID__:{space_id}')
" 2>/dev/null || echo "(解析失败)")

echo "$SPACE_INFO" | grep -v "^__SPACE_ID__:"
echo ""

# Step 2: 列出每个空间的根节点
SPACE_IDS=$(echo "$SPACE_INFO" | grep "^__SPACE_ID__:" | cut -d: -f2)

if [ -z "$SPACE_IDS" ]; then
    echo "未找到知识空间，或没有访问权限。"
    exit 0
fi

echo ">>> [2/2] 列出各空间的根节点..."
for SPACE_ID in $SPACE_IDS; do
    echo ""
    echo "--- 空间 $SPACE_ID 的根节点 ---"
    NODE_OUTPUT=$("$CLI" wiki node list --space "$SPACE_ID" --page-size 20 2>&1) || true

    if echo "$NODE_OUTPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); exit(0 if d.get('success') else 1)" 2>/dev/null; then
        echo "$NODE_OUTPUT" | python3 -c "
import json, sys
d = json.load(sys.stdin)
nodes = d.get('data', {}).get('items', [])
print(f'  共 {len(nodes)} 个根节点:')
for n in nodes:
    node_token = n.get('node_token', '?')
    title      = n.get('title', '(无标题)')
    obj_type   = n.get('obj_type', '?')
    obj_token  = n.get('obj_token', '')
    print(f'  node_token={node_token}  type={obj_type}  title={title}')
    if obj_token:
        print(f'    obj_token={obj_token}  (可用于 {obj_type} 命令的 --token)')
" 2>/dev/null || echo "  (解析失败)"
    else
        echo "  获取节点失败（可能权限不足）:"
        echo "  $NODE_OUTPUT" | head -3
    fi
done

echo ""
echo "=== 完成 ==="
echo "提示: 使用 space_id 和 node_token 进行后续操作"
echo "      例: scripts/feishu-cli.sh wiki node list --space <space_id> --parent <node_token>"
