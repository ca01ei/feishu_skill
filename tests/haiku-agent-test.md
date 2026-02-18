# Feishu Skill Agent Test

Use the **feishu-cloud-docs** skill to complete the tasks below. The skill will tell you everything you need to know about how to operate.

## Reporting format

After each task, output exactly one line:
```
[PASS] T<N>: <what you did / key value obtained>
[FAIL] T<N>: <what went wrong and what you tried>
[SKIP] T<N>: <reason>
```

At the end, output a summary block:
```
=== AGENT TEST SUMMARY ===
PASS: <count>
FAIL: <count>
SKIP: <count>
DOCX_TOKEN: <value or N/A>
BITABLE_APP_TOKEN: <value or N/A>
BITABLE_TABLE_ID: <value or N/A>
BITABLE_RECORD_ID: <value or N/A>
SHEETS_TOKEN: <value or N/A>
WIKI_SPACE_COUNT: <number or N/A>
```

---

## Tasks

### T1 — Auth check

Verify that authentication is set up and working.

Checkpoint: Report the auth mode (user / tenant / none).

---

### T2 — Create a docx document

Create a new Feishu document titled `"HaikuTest-<current_unix_timestamp>"`.

Checkpoint: Report the `document_id`. You will need it for T3, T4, T5. Skip those tasks if this fails.

---

### T3 — Write a paragraph

Write a paragraph with the text `"AgentTestMark-CONTENT-1"` into the document from T2.

Checkpoint: Report whether the write succeeded.

---

### T4 — Read back document content

Read the full content of the document from T2.

Checkpoint: Does the content contain `"AgentTestMark-CONTENT-1"`? Report YES or NO.

---

### T5 — Write a code block using a template

Write a code block to the document from T2. Use the template file under the skill's `templates/` directory for the block JSON.

Checkpoint: Report whether the write succeeded.

---

### T6 — Bitable: create app, add record, update, delete

**T6a** — Create a bitable app named `"HaikuBitableTest-<current_unix_timestamp>"`.  
Checkpoint: Report the `app_token`.

**T6b** — List the tables inside that app.  
Checkpoint: Report the `table_id` of the first table.

**T6c** — List the fields in that table.  
Checkpoint: Report all field names.

**T6d** — Create a record in the table using a real field name from T6c.  
Checkpoint: Report the `record_id`.

**T6e** — Update the record from T6d.  
Checkpoint: Report success/failure.

**T6f** — Delete the record from T6d.  
Checkpoint: Report success/failure.

---

### T7 — Error handling

Attempt to fetch a docx document using the token `"INVALID_TOKEN_HAIKU_TEST_XYZ"`.

Checkpoint: Report the error `code` and `msg` from the response, and whether the command exited with a non-zero code.

---

### T8 — Sheets: create spreadsheet and list sheets

Create a spreadsheet titled `"HaikuSheetsTest-<current_unix_timestamp>"`. Then list the sheets inside it.

Checkpoint: Report the `spreadsheet_token` and the `sheet_id` of the first sheet.

---

### T9 — Wiki: list spaces (read-only)

List all Wiki spaces you have access to. If there are spaces, also list the root nodes of the first space.

Checkpoint: Report how many spaces exist and how many root nodes the first space has.

---

### T10 — Run a scenario script

Run the `docx-create-and-write` scenario script from the skill's `scripts/` directory with:
- title: `"HaikuScriptTest-<current_unix_timestamp>"`
- content: `"ScriptTestMark-CONTENT-2"`

Checkpoint: Report the `document_id` from the script output.

---

## After all tasks

1. Output the full summary block.
2. Note any tasks where the skill documentation was unclear or missing. These are documentation gaps to fix.
