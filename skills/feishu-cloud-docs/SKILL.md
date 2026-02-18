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

## Quick task → command lookup

Read a document's full text content:
  `scripts/feishu-cli.sh docx content --token <doc_token>`

Create a new document and write content (multi-step):
  Step 1: `docx create --title <title>` → get `document_id`
  Step 2: `docx block list --token <id>` → get root block_id (index 0)
  Step 3: `docx block create --token <id> --block-id <root_id> --data '<json>'`
  Or use: `skills/feishu-cloud-docs/scripts/docx-create-and-write.sh <title> <text>`

Read all sheets in a spreadsheet:
  `scripts/feishu-cli.sh sheets sheet list --token <spreadsheet_token>`
  Or use: `skills/feishu-cloud-docs/scripts/sheets-read-all.sh <token>`

Create / read / update / delete a Bitable record:
  `scripts/feishu-cli.sh bitable record create --app-token <t> --table-id <id> --fields '<json>'`
  `scripts/feishu-cli.sh bitable record list   --app-token <t> --table-id <id>`
  `scripts/feishu-cli.sh bitable record update  --app-token <t> --table-id <id> --record-id <r> --fields '<json>'`
  `scripts/feishu-cli.sh bitable record delete  --app-token <t> --table-id <id> --record-id <r>`
  Or use: `skills/feishu-cloud-docs/scripts/bitable-full-crud.sh <app_token> <table_id>`

List all Wiki spaces and their nodes:
  `scripts/feishu-cli.sh wiki space list`
  `scripts/feishu-cli.sh wiki node list --space <space_id>`
  Or use: `skills/feishu-cloud-docs/scripts/wiki-list-all.sh`

Check / fix authentication:
  `scripts/feishu-cli.sh auth whoami`
  `scripts/feishu-cli.sh auth refresh`   (when token expired)
  `scripts/feishu-cli.sh auth login`     (first time or after logout)
  Or use: `skills/feishu-cloud-docs/scripts/check-auth.sh`

Read a legacy (old-format) document:
  `scripts/feishu-cli.sh docs get --token <token>`

## docx (new) vs docs (legacy)
- **`docx`** — New Feishu Docs format. Supports full read/write and block-level operations. **Use this by default.**
- **`docs`** — Legacy document format. **Read-only** (`docs get` only). Use only when the document URL contains `/docs/` (not `/docx/`).

## How to find tokens from Feishu URLs

  `https://xxx.feishu.cn/docx/<document_id>`     → use as `--token` for `docx` commands
  `https://xxx.feishu.cn/sheets/<spreadsheet_token>` → use as `--token` for `sheets` commands
  `https://xxx.feishu.cn/base/<app_token>`        → use as `--app-token` for `bitable` commands
  `https://xxx.feishu.cn/wiki/<node_token>`       → use as node token; get space_id via `wiki space list`
  `https://xxx.feishu.cn/docs/<doc_token>`        → use as `--token` for `docs get` (legacy)

For Bitable: `table_id` is NOT in the URL. Get it with:
  `scripts/feishu-cli.sh bitable table list --app-token <app_token>`

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

## Detailed per-type references
- `skills/feishu-cloud-docs/references/auth.md` — auth flow, token lifecycle, CI/headless setup
- `skills/feishu-cloud-docs/references/docx.md` — all docx commands with JSON examples and block_type table
- `skills/feishu-cloud-docs/references/sheets.md` — sheets commands with sheet_id / filter usage
- `skills/feishu-cloud-docs/references/bitable.md` — bitable hierarchy (app→table→record/field/view)
- `skills/feishu-cloud-docs/references/wiki.md` — wiki space/node/member/setting/search
- `skills/feishu-cloud-docs/references/error-codes.md` — common error codes and fixes

## JSON templates for --data / --fields parameters
- `skills/feishu-cloud-docs/templates/docx-block-text.json` — paragraph text block
- `skills/feishu-cloud-docs/templates/docx-block-code.json` — code block (Python default)
- `skills/feishu-cloud-docs/templates/bitable-record.json` — record fields
- `skills/feishu-cloud-docs/templates/bitable-field-types.json` — field type enum reference
- `skills/feishu-cloud-docs/templates/wiki-node.json` — wiki node creation body

Usage with template file: `--data @skills/feishu-cloud-docs/templates/docx-block-text.json`

## Ready-to-use scenario scripts
- `skills/feishu-cloud-docs/scripts/check-auth.sh` — show current auth status and token mode
- `skills/feishu-cloud-docs/scripts/docx-create-and-write.sh <title> <text>` — create doc and insert a paragraph
- `skills/feishu-cloud-docs/scripts/sheets-read-all.sh <spreadsheet_token>` — list all sheets with IDs
- `skills/feishu-cloud-docs/scripts/bitable-full-crud.sh <app_token> <table_id>` — create/read/update/delete a record
- `skills/feishu-cloud-docs/scripts/wiki-list-all.sh` — list all spaces and their root nodes

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
