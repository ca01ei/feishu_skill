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

## CLI Reference

All commands: `scripts/feishu-cli.sh <domain> <command> [options]`
All output is JSON. Use `--help` on any command for full options.

### docx (New Documents)
- `docx create --title T [--folder-token F]` — Create document
- `docx get --token T` — Get document info
- `docx content --token T` — Get raw content
- `docx block list --token T` — List blocks
- `docx block get --token T --block-id B` — Get block
- `docx block create --token T --block-id B --data '{...}'` — Add child blocks
- `docx block delete --token T --block-id B --start-index N --end-index M` — Delete blocks

### docs (Legacy)
- `docs --token T [--content-type markdown]` — Get content

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
- `wiki node create/list/copy/move` — Node (page) management
- `wiki space get-node --space-id S --token T` — Get node in space
- `wiki member create/list/delete --space-id S` — Permissions
- `wiki setting update --space-id S` — Settings
- `wiki search --query Q` — Search

## Common Workflows

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
1. `wiki space create --name "Wiki"` → get space_id
2. `wiki node create --space-id S --title "Root Page"` → get node_token
3. `wiki node create --space-id S --title "Child" --parent-node-token NODE`

## Error Handling

All errors return: `{"success": false, "code": N, "msg": "..."}`.
Exit codes: 0=success, 1=API error, 2=param error.
