---
name: table-cleanup
description: Clean up markdown tables for plain-text sharing (email, chat, Slack). Use when the user asks to "clean up a table", "format table for email", "remove markdown from table", "make table plain text", "align table columns", "fix table formatting", or any request involving stripping markdown syntax from tables and aligning columns for readable plain-text output.
---

# Table Cleanup

Strip markdown formatting from tables and produce cleanly aligned plain-text tables suitable for email, chat, or pasting into documents.

## Workflow

1. Read the source file containing the markdown table
2. Strip markdown syntax:
   - Remove bold markers (`**`)
   - Remove italic markers (`*`)
   - Remove markdown links (`[text](url)` -> `text`, `([label][ref])` -> remove entirely)
   - Remove emoji characters if they were part of markdown annotations (e.g. checkmarks used as markers)
3. Align all columns so pipe (`|`) characters are vertically consistent across every row
4. Write the cleaned file back

## Column Alignment

Use the bundled Python script for reliable alignment:

```bash
python3 scripts/align_table.py <file_path>
```

The script:
- Parses pipe-delimited rows
- Calculates max width per column across all data rows
- Pads every cell to uniform width
- Rebuilds the separator row to match
- Preserves non-table lines (headers, blank lines) as-is

If the script is unavailable, align manually:
1. Split each row by `|`
2. Find the max content width for each column
3. Left-justify and pad each cell with spaces to that width
4. Rebuild the separator line with dashes matching column widths

## Stripping Patterns (quick reference)

| Pattern              | Action                        |
|----------------------|-------------------------------|
| `**text**`           | Replace with `text`           |
| `*text*`             | Replace with `text`           |
| `([label][ref])`     | Remove entirely               |
| `[text](url)`        | Replace with `text`           |
| `✅` (marker emoji)  | Remove                        |
| Trailing ref links   | Remove `[1]: url` lines       |

## Tips

- Always strip formatting first, then align — stripping changes cell widths
- Preserve the table structure (pipes and separator row) for readability
- Keep non-table content (intro text, notes) untouched
