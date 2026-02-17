# Feishu Cloud Docs Skill - Design Document

## Overview

构建一个 Claude Code Skill，让 AI agent 能直接操作飞书云文档。通过统一 CLI 工具 + Skill 文件的方式，覆盖飞书 OpenAPI SDK 提供的全部 5 个云文档 API。

## Goals

- 覆盖 docs、docx、sheets、bitable、wiki 全部 5 个 API
- 首次使用一次性安装依赖，后续零感知
- Claude 通过 Bash 调用 CLI 完成所有操作

## Architecture

```
feishu_skill/
├── oapi-sdk-python/              # 已有 SDK（不修改）
├── feishu_cli/                   # CLI 工具包
│   ├── __init__.py
│   ├── main.py                   # CLI 入口（typer）
│   ├── config.py                 # 凭证管理（env → .env fallback）
│   ├── client.py                 # 统一 lark client 初始化
│   ├── setup.py                  # 一次性初始化逻辑
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── docx.py              # 新文档操作
│   │   ├── docs.py              # 旧文档操作
│   │   ├── sheets.py            # 电子表格操作
│   │   ├── bitable.py           # 多维表格操作
│   │   └── wiki.py              # 知识库操作
│   └── utils/
│       ├── __init__.py
│       └── output.py            # 统一输出格式化
├── scripts/
│   ├── feishu-cli.sh            # CLI 入口脚本（自动检测安装状态）
│   └── setup.sh                 # 环境初始化（uv + venv + 依赖）
├── skill/
│   └── feishu-cloud-docs.md     # Claude Code Skill 文件
├── tests/
├── .env.example
└── pyproject.toml               # uv 项目配置
```

## Dependency Installation Mechanism

1. **首次调用**：`scripts/setup.sh` 执行：
   - 检查 Python >= 3.7
   - 检查/安装 uv
   - 创建 venv（如不存在）
   - `uv pip install` 安装所有依赖
   - 写入标记文件 `.feishu_cli_installed`

2. **后续调用**：`scripts/feishu-cli.sh` 检查标记文件
   - 存在 → 直接运行 CLI
   - 不存在 → 自动调用 setup.sh，再运行 CLI

## CLI Command Design

### docx（新文档）

| 命令 | 说明 |
|------|------|
| `docx create --title T` | 创建文档 |
| `docx get --token T` | 获取文档信息 |
| `docx content --token T --format md` | 获取内容 |
| `docx block list/create/update/delete` | 块操作 |
| `docx block children --token T --block-id B` | 子块查询 |

### docs（旧文档）

| 命令 | 说明 |
|------|------|
| `docs get --token T --type md` | 获取文档内容 |

### sheets（电子表格）

| 命令 | 说明 |
|------|------|
| `sheets create/get/update` | 表格 CRUD |
| `sheets sheet list/create` | 工作表管理 |
| `sheets filter create/get/update/delete` | 筛选 |
| `sheets filter-view create/get/list/update/delete` | 筛选视图 |
| `sheets float-image create/get/list/update/delete` | 浮动图片 |

### bitable（多维表格）

| 命令 | 说明 |
|------|------|
| `bitable app create/get/update/copy` | 应用管理 |
| `bitable table create/list/delete` | 表管理 |
| `bitable record create/get/list/update/delete` | 记录 CRUD |
| `bitable record batch-create/batch-update/batch-delete` | 批量操作 |
| `bitable field create/list/update/delete` | 字段管理 |
| `bitable view create/list/get/update/delete` | 视图管理 |
| `bitable form get/update/field-list/field-update` | 表单 |
| `bitable role create/list/update/delete/member-*` | 权限 |
| `bitable dashboard list` | 仪表盘 |

### wiki（知识库）

| 命令 | 说明 |
|------|------|
| `wiki space create/get/list/update` | 空间管理 |
| `wiki node create/get/move/copy/list` | 节点管理 |
| `wiki member create/list/delete` | 成员权限 |
| `wiki setting get/update` | 设置 |
| `wiki search --query Q` | 搜索 |

## Common Design Principles

- 所有输出默认 JSON 格式，`--format table` 可切换
- `--data` 参数接受 JSON 字符串或 `@file.json`
- 错误输出统一：`{"success": false, "code": xxx, "msg": "..."}`
- 退出码：0=成功，1=API 错误，2=参数错误，3=配置错误
- 支持 `--dry-run` 预览请求

## Credential Management

- 优先读环境变量 `FEISHU_APP_ID` / `FEISHU_APP_SECRET`
- Fallback 到项目根目录 `.env` 文件
- 缺失时明确报错提示

## Skill File Design

- 文件路径：`skill/feishu-cloud-docs.md`
- 不超过 300 行
- 包含：setup 说明、凭证配置、命令参考、常见工作流
- 详细参数让 Claude 用 `--help` 自助查询

## Testing Strategy

- 单元测试：mock SDK 调用，验证参数构建和输出格式
- 集成测试：可选，使用真实凭证
- 框架：pytest + pytest-mock
- 覆盖率目标：80%+

## Error Handling

- 统一捕获 SDK 异常，输出标准 JSON 错误
- 网络超时默认 30s，`--timeout` 可调
- 凭证缺失明确提示

## Constraints

- Python 模块文件不超过 400 行
- 不可变数据传递
- 输入参数边界校验
