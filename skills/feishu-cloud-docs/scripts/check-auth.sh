#!/usr/bin/env bash
# 检查当前飞书 CLI 的认证状态，显示 token 模式和用户信息
# 用法: bash skills/feishu-cloud-docs/scripts/check-auth.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")"
CLI="$PROJECT_DIR/scripts/feishu-cli.sh"

echo "=== Feishu CLI 认证状态检查 ==="
echo ""

# 检测 token 模式
TOKEN_FILE="${FEISHU_TOKEN_FILE:-$HOME/.config/feishu-cli/user_token.json}"

if [ -n "${FEISHU_USER_ACCESS_TOKEN:-}" ]; then
    echo "Token 模式: 环境变量 FEISHU_USER_ACCESS_TOKEN（最高优先级）"
elif [ -f "$TOKEN_FILE" ]; then
    echo "Token 模式: user token（本地会话文件: $TOKEN_FILE）"
elif [ -n "${FEISHU_APP_ID:-}" ] && [ -n "${FEISHU_APP_SECRET:-}" ]; then
    echo "Token 模式: tenant token（FEISHU_APP_ID + FEISHU_APP_SECRET）"
else
    echo "Token 模式: 未知（未设置任何凭证）"
fi

echo ""
echo ">>> 调用 auth whoami..."
RESULT=$("$CLI" auth whoami 2>&1) || true
echo "$RESULT"

echo ""
if echo "$RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); exit(0 if d.get('success') else 1)" 2>/dev/null; then
    echo "状态: ✓ 已认证"
    NAME=$(echo "$RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('data',{}).get('name','(未知)'))" 2>/dev/null || echo "(无法解析)")
    echo "用户: $NAME"
else
    echo "状态: ✗ 未认证或 token 已过期"
    echo ""
    echo "修复建议:"
    echo "  1. 刷新 token:   $CLI auth refresh"
    echo "  2. 重新登录:     $CLI auth login"
    echo "  3. 设置环境变量: export FEISHU_APP_ID=cli_xxx && export FEISHU_APP_SECRET=xxx"
fi
