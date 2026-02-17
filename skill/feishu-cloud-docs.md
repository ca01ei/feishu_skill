---
name: feishu-cloud-docs
description: Operate Feishu cloud documents (docs, docx, sheets, bitable, wiki).
  Use when user asks to create/edit/query Feishu documents, spreadsheets, bitables, or wiki pages.
---

## Setup

On first use, the CLI auto-installs dependencies. If it fails, run manually:
```
bash /path/to/feishu_skill/scripts/setup.sh
```

## Credentials

Requires `FEISHU_APP_ID` and `FEISHU_APP_SECRET` as environment variables or in `.env` at the project root.

## Authentication Modes

### Tenant mode (default)
- Works with app credentials only (`FEISHU_APP_ID` + `FEISHU_APP_SECRET`).
- CLI obtains tenant token automatically via SDK.

### User mode (OIDC, preferred when available)
- `auth login-url` — generate login URL
- `auth login` — interactive login (auto local callback by default)
- `auth login --manual` — manual code/callback paste flow
- `auth exchange-code --code CODE` — exchange code directly
- `auth refresh` — refresh saved session token
- `auth whoami` — verify current user token
- `auth logout` — clear local saved session

Default callback URI: `http://127.0.0.1:3080/callback`
Default scope includes: `offline_access auth:user.id:read docx:document docx:document:create docs:document.content:read drive:drive sheets:spreadsheet sheets:spreadsheet:create bitable:app base:app:create`

### Token source priority
For business commands (`docx/docs/sheets/bitable/wiki`), CLI uses this order:
1. `FEISHU_USER_ACCESS_TOKEN` (environment variable)
2. Local user session file (`~/.config/feishu-cli/user_token.json`, override via `FEISHU_TOKEN_FILE`)
3. Tenant token from app credentials (SDK default)

## CLI Reference

All commands: `scripts/feishu-cli.sh <domain> <command> [options]`
All output is JSON. Use `--help` on any command for full options.
### auth (User Token Lifecycle)
- `auth login-url [--redirect-uri URI] [--scope SCOPE]` — Generate OIDC authorize URL
- `auth login [--manual] [--no-open-browser]` — Interactive login and persist session
- `auth exchange-code --code CODE` — Exchange authorization code and persist session
- `auth refresh [--refresh-token TOKEN]` — Refresh user session token
- `auth whoami` — Query current user profile by user token
- `auth logout` — Clear local user session

### docx (New Documents)
- `docx create --title T [--folder-token F]` — Create document
- `docx get --token T` — Get document info
- `docx content --token T` — Get raw content
- `docx block list --token T` — List blocks
- `docx block get --token T --block-id B` — Get block
- `docx block create --token T --block-id B --data '{...}'` — Add child blocks
- `docx block delete --token T --block-id B --start-index N --end-index M` — Delete blocks

### docs (Legacy)
- `docs get --token T [--content-type markdown]` — Get content

### sheets (Spreadsheets)
- `sheets create --title T` — Create spreadsheet
- `sheets get --token T` — Get spreadsheet
- `sheets update --token T --title T` — Update properties
- `sheets sheet list --token T` — List sheet tabs
- `sheets filter create/get/update/delete` — Filter operations
- `sheets filter-view create/get/list/update/delete` — Filter views
- `sheets float-image create/get/list/update/delete` — Float images

### bitable (Multi-dimensional Tables)
- `bitable create/get/update/copy` — App management
- `bitable table create/list/delete/patch` — Table management
- `bitable record create/get/list/update/delete` — Record CRUD
- `bitable field create/list/update/delete` — Field management
- `bitable view create/get/list/delete` — View management

### wiki (Knowledge Base)
- `wiki space create/get/list` — Space management
- `wiki node create/list/copy/move --space S` — Node (page) management
- `wiki space get-node --token T [--obj-type TYPE]` — Get node in space
- `wiki member create/list/delete --space S` — Permissions
- `wiki setting update --space S` — Settings
- `wiki search --data '{"query":"Q"}'` — Search

## Common Workflows
### Login with user token (recommended)
1. `auth login` (or `auth login --manual`)
2. `auth whoami` to verify token is valid
3. Run normal business commands (`docx/...`, `sheets/...`, `bitable/...`, `wiki/...`) — user token is auto-prioritized
### Refresh user session
1. `auth refresh`
2. If refresh fails, run `auth login` again
### Create a document with content
1. `docx create --title "Title"` → get document_id
2. `docx block list --token DOC_ID` → get root block_id
3. `docx block create --token DOC_ID --block-id ROOT --data '{"children": [...]}'`

### Create bitable and import data
1. `bitable create --name "DB"` → get app_token
2. `bitable table create --app-token APP --name "Table1"` → get table_id
3. `bitable field create --app-token APP --table-id TBL --field-name "Name" --field-type 1`
4. `bitable record create --app-token APP --table-id TBL --fields '{"Name": "value"}'`

### Build wiki structure
1. `wiki space create --data '{"name":"Wiki"}'` → get space_id
2. `wiki node create --space S --data '{"title":"Root Page"}'` → get node_token
3. `wiki node create --space S --data '{"title":"Child","parent_node_token":"NODE"}'`

## Error Handling

All errors return: `{"success": false, "code": N, "msg": "..."}`.
Exit codes: 0=success, 1=API error, 2=param error.
