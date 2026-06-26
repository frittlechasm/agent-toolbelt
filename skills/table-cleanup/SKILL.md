---
name: table-cleanup
description: Clean up markdown tables for plain-text sharing (email, chat, Slack). Use when the user asks to "clean up a table", "format table for email", "remove markdown from table", "make table plain text", "align table columns", "fix table formatting", or any request involving stripping markdown syntax from tables and aligning columns for readable plain-text output.
---

# Table Cleanup

Produce clean, aligned plain-text tables for email, chat, Slack, or documents.

## Output

Reply with only the cleaned table/content unless the user asks for explanation.
Do not edit source files unless the user explicitly asks you to update a file.

## Cleanup Rules

- Strip markdown emphasis markers from cell text.
- Strip inline code markers from cell text while preserving the code/value text.
- Convert inline links (`[text](url)`) to `text`.
- Remove reference-style annotation links inside cells, such as `([label][ref])`.
- Remove marker emoji used as table annotations when they do not add content.
- Preserve non-table text the user included, but keep it plain.
- Align columns by padding cells so pipes line up across every row.

## Helper Script

Use the bundled script when a table is in a file or deterministic alignment helps:

```bash
python3 scripts/align_table.py --strip <file_path>
```

The script prints the cleaned result to stdout by default. Use `--in-place` only when the user explicitly requests file modification.
