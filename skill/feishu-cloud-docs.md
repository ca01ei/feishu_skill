---
name: feishu-cloud-docs
description: Use this skill to operate Feishu cloud documents via CLI (docx, docs, sheets, bitable, wiki, auth), including create/get/update/delete/list flows and user-token login.
---

## Purpose
This skill provides a reliable command interface for Feishu cloud document operations:
- `docx` (new docs API)
- `docs` (legacy docs read API)
- `sheets`
- `bitable`
- `wiki`
- `auth` (OIDC user token lifecycle)

## Repository Setup
Run from the project root after cloning:
```bash
bash scripts/setup.sh
```
Or just run any CLI command once (auto setup will run on first execution):
```bash
scripts/feishu-cli.sh --help
```

## Credentials
Set credentials in environment variables, or in a project-root `.env` file:
- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`

Example `.env`:
```bash
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
```

## Authentication Modes
### Tenant mode (default fallback)
If no user token is available, requests use tenant-token flow via app credentials.

### User mode (preferred)
Use OIDC login to obtain/persist user token:
```bash
scripts/feishu-cli.sh auth login
scripts/feishu-cli.sh auth whoami
```

Default callback URI:
- `http://127.0.0.1:3080/callback`

Default requested scopes:
- `offline_access`
- `auth:user.id:read`
- `docx:document`
- `docx:document:create`
- `docs:document.content:read`
- `drive:drive`
- `sheets:spreadsheet`
- `sheets:spreadsheet:create`
- `bitable:app`
- `base:app:create`

### Token priority
Business commands (`docx/docs/sheets/bitable/wiki`) resolve auth in this order:
1. `FEISHU_USER_ACCESS_TOKEN`
2. local session file (`~/.config/feishu-cli/user_token.json`, override via `FEISHU_TOKEN_FILE`)
3. tenant token (app credentials)

## Command Reference
General form:
```bash
scripts/feishu-cli.sh <domain> <command> [options]
```

### auth
- `auth login-url`
- `auth login`
- `auth login --manual`
- `auth exchange-code --code CODE`
- `auth refresh`
- `auth whoami`
- `auth logout`

### docx
- `docx create/get/content`
- `docx block list/get/create/delete`

### docs (legacy)
- `docs get`

### sheets
- `sheets create/get/update`
- `sheets sheet list`
- `sheets filter create/get/update/delete`
- `sheets filter-view create/get/list/update/delete`
- `sheets float-image create/get/list/update/delete`

### bitable
- `bitable create/get/update/copy`
- `bitable table create/list/patch/delete`
- `bitable field create/list/update/delete`
- `bitable view create/get/list/delete`
- `bitable record create/get/list/update/delete`

### wiki
- `wiki space create/get/list/get-node`
- `wiki node create/list/copy/move`
- `wiki member create/list/delete`
- `wiki setting update`
- `wiki search`

## Standard Usage Workflows
### Quick auth + create doc
```bash
scripts/feishu-cli.sh auth login
scripts/feishu-cli.sh docx create --title "Skill Demo"
```

### Bitable CRUD baseline
```bash
scripts/feishu-cli.sh bitable create --name "Skill Bitable"
scripts/feishu-cli.sh bitable table create --app-token APP_TOKEN --name "Table1"
scripts/feishu-cli.sh bitable field create --app-token APP_TOKEN --table-id TABLE_ID --field-name "Name" --field-type 1
scripts/feishu-cli.sh bitable record create --app-token APP_TOKEN --table-id TABLE_ID --fields '{"Name":"value"}'
```

## Validation Scripts
- Smoke: `scripts/smoke_feishu_cli.sh`
- Full E2E: `scripts/full_feishu_cli_e2e.sh`

Optional existing-resource modification env vars for full E2E:
- `EXISTING_DOCX_TOKEN`
- `EXISTING_SHEETS_TOKEN`
- `EXISTING_BITABLE_APP_TOKEN`
- `EXISTING_BITABLE_TABLE_ID` (optional)
- `SHEETS_FLOAT_IMAGE_TOKEN` (optional, to enable float-image create/update/delete path)

## Error Contract
CLI output is JSON:
- success: `{"success": true, "data": ...}`
- failure: `{"success": false, "code": N, "msg": "...", "log_id": "..."}`

Exit codes:
- `0`: success
- `1`: API/business failure
- `2`: parameter/input failure
