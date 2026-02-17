# Feishu Cloud Docs CLI Skill
CLI toolkit + Agent Skill for operating Feishu cloud documents:
- Docx (`docx`)
- Legacy docs read (`docs`)
- Sheets (`sheets`)
- Bitable (`bitable`)
- Wiki (`wiki`)
- User token auth lifecycle (`auth`)

## Features
- Standard CLI entrypoint: `scripts/feishu-cli.sh`
- Auto bootstrap on first run (`scripts/setup.sh`)
- Supports tenant-token and user-token modes
- User-token OIDC flow with local callback:
  - `auth login-url`
  - `auth login`
  - `auth refresh`
  - `auth whoami`
  - `auth logout`
- JSON output contract for easy automation
- Built-in validation scripts:
  - smoke test
  - full end-to-end CRUD/list coverage

## Prerequisites
- macOS / Linux shell
- Python 3.7+
- Network access to Feishu Open APIs

`scripts/setup.sh` will install:
- `uv`
- project dependencies
- local SDK in `oapi-sdk-python`

## Installation (Standard GitHub Flow)
After cloning this repository:
```bash
bash scripts/setup.sh
```

Or run any CLI command once (auto setup on first use):
```bash
scripts/feishu-cli.sh --help
```

## Configuration
Provide Feishu app credentials through environment variables or `.env` in repo root.

Example `.env`:
```bash
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
```

## Authentication
### Tenant mode
If no user token exists, CLI falls back to tenant-token flow with app credentials.

### User mode (recommended)
```bash
scripts/feishu-cli.sh auth login
scripts/feishu-cli.sh auth whoami
```

Default callback URI:
- `http://127.0.0.1:3080/callback`

Make sure this URI is configured in Feishu app security settings, otherwise authorization may fail with `20029`.

### Token source priority
Business APIs (`docx/docs/sheets/bitable/wiki`) use:
1. `FEISHU_USER_ACCESS_TOKEN`
2. local session file `~/.config/feishu-cli/user_token.json` (or `FEISHU_TOKEN_FILE`)
3. tenant token from app credentials

## Quick Start
```bash
# Login as user
scripts/feishu-cli.sh auth login

# Create docx
scripts/feishu-cli.sh docx create --title "Hello"

# Create sheet
scripts/feishu-cli.sh sheets create --title "Sheet Demo"

# Create bitable
scripts/feishu-cli.sh bitable create --name "Bitable Demo"
```

## Command Domains
```bash
scripts/feishu-cli.sh auth --help
scripts/feishu-cli.sh docx --help
scripts/feishu-cli.sh docs --help
scripts/feishu-cli.sh sheets --help
scripts/feishu-cli.sh bitable --help
scripts/feishu-cli.sh wiki --help
```

## Testing
### Unit/CLI tests
```bash
.venv/bin/pytest
```

### Smoke validation
```bash
scripts/smoke_feishu_cli.sh
```

### Full E2E validation (new resources)
```bash
scripts/full_feishu_cli_e2e.sh
```

### Full E2E including existing resources
Provide target tokens:
```bash
EXISTING_DOCX_TOKEN=xxx \
EXISTING_SHEETS_TOKEN=xxx \
EXISTING_BITABLE_APP_TOKEN=xxx \
scripts/full_feishu_cli_e2e.sh
```

Optional vars:
- `EXISTING_BITABLE_TABLE_ID` (if you want a specific table)
- `SHEETS_FLOAT_IMAGE_TOKEN` (enable float-image create/update/delete path)

## Output and Exit Codes
All commands return JSON.

Success:
```json
{"success": true, "data": {...}}
```

Failure:
```json
{"success": false, "code": 123, "msg": "...", "log_id": "..."}
```

Exit codes:
- `0` success
- `1` API/business failure
- `2` parameter/input failure

## Troubleshooting
- `20029 redirect_uri 请求不合法`:
  callback URI is not whitelisted in Feishu app settings.
- `99991679 Unauthorized`:
  user token lacks required scope; re-authorize with needed permissions.
- Missing credentials:
  ensure `FEISHU_APP_ID` and `FEISHU_APP_SECRET` are set.

## Agent Skill File
Skill definition is located at:
- `skill/feishu-cloud-docs.md`
