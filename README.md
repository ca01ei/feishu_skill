# Feishu Skills Repository
This repository packages a Feishu operational skill using the common Agent Skills layout:
- skill definitions live under `skills/<skill-name>/SKILL.md`
- implementation code and scripts live in the same repo

Current skill:
- `skills/feishu-cloud-docs/SKILL.md`

## Repository Structure
```text
skills/
  feishu-cloud-docs/
    SKILL.md
feishu_cli/
scripts/
tests/
```

## What this skill supports
The `feishu-cloud-docs` skill drives a local Feishu CLI for:
- user auth lifecycle (`auth`)
- docx/docs operations
- sheets operations
- bitable operations
- wiki operations

## Standard Installation
After cloning from GitHub:
```bash
bash scripts/setup.sh
```

You can also trigger automatic first-time setup by running:
```bash
scripts/feishu-cli.sh --help
```

## Configuration
Set credentials via environment variables or `.env` in repo root:
```bash
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
```

## Authentication
Recommended user-token flow:
```bash
scripts/feishu-cli.sh auth login
scripts/feishu-cli.sh auth whoami
```

Default callback URI:
- `http://127.0.0.1:3080/callback`

If authorization fails with `20029`, add that callback URI to Feishu app security settings.

## Run Commands
```bash
scripts/feishu-cli.sh auth --help
scripts/feishu-cli.sh docx --help
scripts/feishu-cli.sh docs --help
scripts/feishu-cli.sh sheets --help
scripts/feishu-cli.sh bitable --help
scripts/feishu-cli.sh wiki --help
```

## Testing
Unit tests:
```bash
.venv/bin/pytest
```

Smoke:
```bash
scripts/smoke_feishu_cli.sh
```

Full E2E:
```bash
scripts/full_feishu_cli_e2e.sh
```

Full E2E with existing resources:
```bash
EXISTING_DOCX_TOKEN=xxx \
EXISTING_SHEETS_TOKEN=xxx \
EXISTING_BITABLE_APP_TOKEN=xxx \
scripts/full_feishu_cli_e2e.sh
```

Optional vars:
- `EXISTING_BITABLE_TABLE_ID`
- `SHEETS_FLOAT_IMAGE_TOKEN`

## Output Contract
All CLI commands return JSON:
- success: `{"success": true, "data": ...}`
- failure: `{"success": false, "code": N, "msg": "...", "log_id": "..."}`

Exit codes:
- `0` success
- `1` API/business error
- `2` parameter/input error
