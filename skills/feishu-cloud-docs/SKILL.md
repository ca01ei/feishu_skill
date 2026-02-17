---
name: feishu-cloud-docs
description: Operate Feishu cloud documents using the local CLI. Use when users need create/get/update/delete/list workflows for docx, docs, sheets, bitable, wiki, and user-token authentication.
allowed-tools: Read, Grep, Glob, Bash
argument-hint: "[domain] [command] [options]"
---

## What this skill does
This skill provides operational guidance for the Feishu CLI in this repository:
- Auth lifecycle (`auth login`, `auth whoami`, `auth refresh`, `auth logout`)
- Document operations (`docx`, `docs`)
- Spreadsheet operations (`sheets`)
- Bitable operations (`bitable`)
- Wiki operations (`wiki`)
- Test automation (`scripts/smoke_feishu_cli.sh`, `scripts/full_feishu_cli_e2e.sh`)

## Prerequisites
- Python 3.7+
- Network access to Feishu Open Platform APIs
- Feishu app credentials

## Setup

### Via Claude Code Marketplace (recommended)
```
/plugin marketplace add ca01ei/feishu_skill
/plugin install feishu-cloud-docs@ca01ei/feishu_skill
```

### Manual
Run once from repository root:
```bash
bash scripts/setup.sh
```

Or trigger auto-setup with:
```bash
scripts/feishu-cli.sh --help
```

## Credentials
Provide credentials via environment or `.env` in repository root:
```bash
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
```

## Authentication model
### Tenant mode
If no user token is available, CLI uses tenant-token flow from app credentials.

### User mode (recommended)
```bash
scripts/feishu-cli.sh auth login
scripts/feishu-cli.sh auth whoami
```

Default callback URI:
- `http://127.0.0.1:3080/callback`

Default user scopes include docx/docs/sheets/bitable permissions plus `offline_access`.

### Token priority
Business commands resolve auth in this order:
1. `FEISHU_USER_ACCESS_TOKEN`
2. local user session file (`~/.config/feishu-cli/user_token.json`, override via `FEISHU_TOKEN_FILE`)
3. tenant token via app credentials

## Core command groups
```bash
scripts/feishu-cli.sh auth --help
scripts/feishu-cli.sh docx --help
scripts/feishu-cli.sh docs --help
scripts/feishu-cli.sh sheets --help
scripts/feishu-cli.sh bitable --help
scripts/feishu-cli.sh wiki --help
```

## Validation workflows
Smoke:
```bash
scripts/smoke_feishu_cli.sh
```

Full E2E:
```bash
scripts/full_feishu_cli_e2e.sh
```

With existing resources:
```bash
EXISTING_DOCX_TOKEN=xxx \
EXISTING_SHEETS_TOKEN=xxx \
EXISTING_BITABLE_APP_TOKEN=xxx \
scripts/full_feishu_cli_e2e.sh
```

Optional:
- `EXISTING_BITABLE_TABLE_ID`
- `SHEETS_FLOAT_IMAGE_TOKEN`

## Output contract
- Success: `{"success": true, "data": ...}`
- Failure: `{"success": false, "code": N, "msg": "...", "log_id": "..."}`
- Exit codes: `0` success, `1` API/business error, `2` parameter error
