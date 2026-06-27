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
- Remove marker emoji only when they are decoration that adds no content (e.g. a 🔹 bullet prefixing every row). Keep emoji that carry the cell's meaning — a ✅/❌ in a Status column *is* the status, so it stays.
- Preserve non-table text the user included, but keep it plain.
- Align columns by padding cells so pipes line up across every row.

## Gotchas

- Preserve the user's data exactly. Cleanup changes presentation, not values, labels, order, or meaning.
- Do not remove symbols that carry meaning, such as checkmarks, warning markers, currency, units, or version prefixes.
- If the input mixes table and prose, clean the table and keep the prose readable instead of forcing everything into a table.

## Helper Script

Prefer the bundled script for the final alignment pass — hand-aligning is error-prone and drifts in format from one run to the next, while the script always emits a GitHub-style pipe table (outer pipes + a rebuilt separator row) with columns padded to equal width. It strips markdown but preserves meaningful content, including status emoji.

For a table already in a file:

```bash
python3 scripts/align_table.py --strip <file_path>
```

For a table pasted into the conversation, pipe it through stdin:

```bash
printf '%s' "$TABLE" | python3 scripts/align_table.py --strip -
```

The script prints to stdout by default. Use `--in-place` only when the user explicitly asks you to modify a file.
