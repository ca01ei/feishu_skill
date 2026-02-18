# 鉴权参考 (auth)

## Token 优先级（从高到低）

1. 环境变量 `FEISHU_USER_ACCESS_TOKEN`（直接传入 user access token）
2. 本地会话文件 `~/.config/feishu-cli/user_token.json`（通过 `auth login` 写入）
   - 可通过 `FEISHU_TOKEN_FILE` 覆盖文件路径
3. Tenant Token（由 `FEISHU_APP_ID` + `FEISHU_APP_SECRET` 自动申请，无需登录）

**当无法确定用哪种模式时：先运行 `auth whoami` 检查当前状态。**

---

## 模式选择

| 场景 | 推荐模式 | 原因 |
|------|----------|------|
| 交互式操作用户文档 | User mode | 内容归属于用户，权限更广 |
| CI/自动化 | Tenant mode（或环境变量） | 无需浏览器，只需 app 凭证 |
| 读取应用自己创建的文档 | Tenant mode | 简单，不需要用户授权 |

---

## 完整命令说明

### auth login — 发起用户登录（推荐首次使用）

```bash
scripts/feishu-cli.sh auth login
```

- 自动打开浏览器，完成授权后自动保存 token
- token 存储于 `~/.config/feishu-cli/user_token.json`

无头/远程环境（无法打开浏览器）：

```bash
scripts/feishu-cli.sh auth login --manual
# 手动访问输出的 URL，授权后粘贴回调 URL 或 code
```

自定义参数：

```bash
scripts/feishu-cli.sh auth login \
  --redirect-uri "http://127.0.0.1:3080/callback" \
  --timeout-seconds 300
```

---

### auth whoami — 查看当前登录用户

```bash
scripts/feishu-cli.sh auth whoami
```

成功响应（user mode）：

```json
{
  "success": true,
  "data": {
    "name": "张三",
    "open_id": "ou_xxx",
    "en_name": "San Zhang"
  }
}
```

失败响应（未登录或 token 过期）：

```json
{
  "success": false,
  "code": 2,
  "msg": "No user token available. Run `auth login` first."
}
```

---

### auth refresh — 刷新 token（token 过期时）

```bash
# 使用本地保存的 refresh_token 自动刷新
scripts/feishu-cli.sh auth refresh

# 手动指定 refresh_token
scripts/feishu-cli.sh auth refresh --refresh-token "ur-xxx"
```

**注意**：refresh_token 本身也有有效期（通常 30 天）。过期后需要重新 `auth login`。

---

### auth logout — 清除本地 token

```bash
scripts/feishu-cli.sh auth logout
```

---

### auth login-url — 只生成授权 URL（不等待回调）

```bash
scripts/feishu-cli.sh auth login-url
# 输出 authorize_url，手动访问完成授权
```

---

### auth exchange-code — 手动换取 token

```bash
scripts/feishu-cli.sh auth exchange-code --code "authcode_xxx"
```

---

## CI / 无头环境配置

**方案 1：使用 Tenant Token（最简单）**

```bash
export FEISHU_APP_ID=cli_xxx
export FEISHU_APP_SECRET=your_secret
scripts/feishu-cli.sh docx get --token "doxcnXxx"  # 自动使用 tenant token
```

**方案 2：预设 User Access Token**

```bash
export FEISHU_USER_ACCESS_TOKEN=u-xxx
scripts/feishu-cli.sh auth whoami
```

**方案 3：.env 文件**

在仓库根目录创建 `.env`：

```
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
```

---

## 默认 OAuth Scopes

```
offline_access
auth:user.id:read
docx:document
docx:document:create
docs:document.content:read
drive:drive
sheets:spreadsheet
sheets:spreadsheet:create
bitable:app
base:app:create
```

如果操作时遇到权限错误（code=230005），需要检查应用是否开启了对应 scope。
