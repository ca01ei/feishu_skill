# Feishu Cloud Docs Skill
这是一个面向编码代理（Agent）的飞书文档操作技能仓库。  
它基于本地 CLI，提供一套可组合、可自动化的文档能力，包括 docx、docs、sheets、bitable、wiki 与用户鉴权流程。

## 它如何工作
项目采用标准 Skill 目录结构：
- 技能定义：`skills/feishu-cloud-docs/SKILL.md`
- CLI 实现：`feishu_cli/`
- 执行脚本：`scripts/`
- 自动化测试：`tests/`

代理在使用该技能时，核心是调用：
```bash
scripts/feishu-cli.sh <domain> <command> [options]
```

## 安装
克隆仓库后，执行标准安装：
```bash
bash scripts/setup.sh
```

也可以直接运行任意 CLI 命令，首次会自动安装：
```bash
scripts/feishu-cli.sh --help
```

## 基础使用流程
### 1) 配置应用凭据
在仓库根目录配置 `.env`（或使用环境变量）：
```bash
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
```

### 2) 完成用户授权（推荐）
```bash
scripts/feishu-cli.sh auth login
scripts/feishu-cli.sh auth whoami
```

默认回调地址：
- `http://127.0.0.1:3080/callback`

如果出现 `20029 redirect_uri 请求不合法`，请到飞书开放平台安全设置中加入该回调地址。

### 3) 执行业务命令
```bash
scripts/feishu-cli.sh docx --help
scripts/feishu-cli.sh sheets --help
scripts/feishu-cli.sh bitable --help
scripts/feishu-cli.sh wiki --help
scripts/feishu-cli.sh docs --help
```

## 仓库包含内容
### 技能层
- `skills/feishu-cloud-docs/SKILL.md`：技能说明、使用边界、执行约定

### CLI 能力域
- `auth`：用户 token 登录、刷新、登出、身份确认
- `docx` / `docs`：文档创建、读取、块级操作、legacy 内容读取
- `sheets`：表格、筛选器、筛选视图、浮动图片
- `bitable`：应用、数据表、字段、视图、记录
- `wiki`：空间、节点、成员、设置、搜索

### 验证脚本
- `scripts/smoke_feishu_cli.sh`：快速冒烟测试
- `scripts/full_feishu_cli_e2e.sh`：全链路 E2E（CRUD/List + 可选 existing 资源修改）

## 测试与验证
### 单元/CLI 测试
```bash
.venv/bin/pytest
```

### 冒烟测试
```bash
scripts/smoke_feishu_cli.sh
```

### 全量 E2E（新建资源）
```bash
scripts/full_feishu_cli_e2e.sh
```

### 全量 E2E（现有资源）
```bash
EXISTING_DOCX_TOKEN=xxx \
EXISTING_SHEETS_TOKEN=xxx \
EXISTING_BITABLE_APP_TOKEN=xxx \
scripts/full_feishu_cli_e2e.sh
```

可选参数：
- `EXISTING_BITABLE_TABLE_ID`
- `SHEETS_FLOAT_IMAGE_TOKEN`

## 输出契约
所有命令输出 JSON：
- 成功：`{"success": true, "data": ...}`
- 失败：`{"success": false, "code": N, "msg": "...", "log_id": "..."}`

退出码：
- `0` 成功
- `1` API/业务失败
- `2` 参数或输入错误

## 更新方式
拉取最新代码后，建议重新执行：
```bash
bash scripts/setup.sh
```

## 许可证
本项目遵循仓库内现有许可证策略。

## 支持
如遇问题，请优先附上：
- 执行命令
- CLI JSON 输出
- `log_id`
- 对应测试产物目录（尤其是 E2E 脚本输出目录）
