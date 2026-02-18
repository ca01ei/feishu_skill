# 常见错误码及修复指南

## 如何识别错误

CLI 失败时输出结构：

```json
{
  "success": false,
  "code": 99991663,
  "msg": "user access token is expired",
  "log_id": "xxxxx"
}
```

Exit code 含义：
- `0`：成功
- `1`：API / 业务错误（查看 `code` 和 `msg`）
- `2`：参数错误（JSON 格式错误、缺少必填参数等）

---

## 鉴权类错误

| code | 含义 | 修复方法 |
|------|------|----------|
| `99991663` | user_access_token 不存在或已过期 | 运行 `auth refresh` 或重新 `auth login` |
| `99991664` | user_access_token 过期 | 运行 `auth refresh` |
| `99991665` | refresh_token 过期 | 必须重新运行 `auth login` |
| `99991680` | app_access_token 无效 | 检查 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET` 是否正确 |
| `99991400` | app_access_token 不可用 | 检查应用是否已发布，凭证是否正确 |
| `99991672` | IP 不在白名单 | 在飞书开放平台后台添加 IP 白名单 |

**快速修复鉴权问题**：

```bash
# 步骤 1：检查当前状态
scripts/feishu-cli.sh auth whoami

# 步骤 2a：token 过期时刷新
scripts/feishu-cli.sh auth refresh

# 步骤 2b：refresh_token 也过期时重新登录
scripts/feishu-cli.sh auth login

# CI 环境：改用 tenant token
export FEISHU_APP_ID=cli_xxx
export FEISHU_APP_SECRET=xxx
```

---

## 权限类错误

| code | 含义 | 修复方法 |
|------|------|----------|
| `230005` | 缺少必要 scope 权限 | 检查应用是否开启了对应 scope，并重新授权 |
| `99991679` | 用户无此文档权限 | 确认用户对目标文档有读写权限 |
| `1254040` | docx: 无读取权限 | 文档未对应用/用户开放 |
| `1254041` | docx: 无编辑权限 | 文档设置为只读 |
| `1252xxx` | sheets 权限相关 | 检查表格共享设置 |

**缺少 scope 时的处理**：

```bash
# 重新登录并明确包含所需 scope
scripts/feishu-cli.sh auth login \
  --scope "offline_access docx:document docx:document:create bitable:app sheets:spreadsheet"
```

---

## 参数类错误（exit code=2）

| 现象 | 原因 | 修复方法 |
|------|------|----------|
| `Invalid JSON` | `--data` 或 `--fields` 格式错误 | 使用 JSON 校验工具，或改用 `@file.json` 传入 |
| `JSON file not found` | `@filename.json` 路径错误 | 检查文件路径，路径相对于当前工作目录 |
| `Missing option '--xxx'` | 缺少必填参数 | 查看 `--help` 确认必填项 |

**JSON 格式错误的常见原因**：

```bash
# ❌ 错误：单引号嵌套中文会有问题
--data '{"名称":"hello"}'

# ✓ 正确：使用文件避免 shell 转义
echo '{"名称":"hello"}' > /tmp/data.json
--data @/tmp/data.json

# ✓ 正确：使用模板文件
--data @skills/feishu-cloud-docs/templates/docx-block-text.json
```

**验证 JSON 格式**：

```bash
echo '{"key":"value"}' | python3 -m json.tool
```

---

## 业务逻辑类错误

| code | 含义 | 修复方法 |
|------|------|----------|
| `1254xxx` | docx 操作相关错误 | 检查 block_id 和 block_type 是否正确 |
| `1254002` | docx: document 不存在 | 检查 `--token` 是否正确 |
| `1254010` | docx: block 不存在 | 检查 `--block-id` 是否正确（用 block list 获取） |
| `1252002` | sheets: 表格不存在 | 检查 `--token` 是否正确 |
| `1252040` | sheets: sheet 不存在 | 先用 `sheets sheet list` 获取正确的 sheet_id |
| `29xxx` | bitable 相关错误 | 检查 app_token 和 table_id 是否匹配 |
| `1310xxx` | wiki 相关错误 | 检查 space_id 和 node_token 是否正确 |

---

## 频率限制错误

| code | 含义 | 修复方法 |
|------|------|----------|
| `99991400` 或 `429` | 请求频率超限 | 添加延迟重试（等待 1-2 秒后重试） |

---

## 调试技巧

**查看完整错误信息（含 log_id）**：

```bash
# log_id 可用于联系飞书技术支持排查问题
scripts/feishu-cli.sh docx get --token "xxx" 2>&1 | python3 -m json.tool
```

**常见排查步骤**：

1. `auth whoami` → 确认认证状态
2. 检查 URL 中的 token 提取是否正确（见 SKILL.md 的 Token 提取规则）
3. 对于 bitable/sheets，确认是否先获取了 table_id / sheet_id
4. 验证 `--data` / `--fields` JSON 格式（用 `python3 -m json.tool` 验证）
5. 如仍有问题，用 `log_id` 联系飞书技术支持
