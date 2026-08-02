# Tables

Read this only when selected content already contains a data table, the user explicitly requests tabular presentation, or spreadsheet/TSV transfer is requested.
Do not read it for prose comparisons, option panels, CSS grids, or other layouts that merely use rows or columns.
This reference governs how a selected data table renders; it does not decide whether domain content needs one.

## Structure and layout

- Use `<caption>` for a simple title. Use a figure with a visible heading and description only when the table also needs context or tools.
- Use `<thead>`, `<tbody>`, scoped column headers, and row headers where appropriate. Preserve logical reading order.
- Use readable gridlines, padding, and wrapping. Right-align numeric columns and use tabular numerals.
- Let narrow tables fit naturally. For genuinely wide tables, choose deliberate column widths and give only the table a labelled, keyboard-focusable horizontal scroller.
- Do not create a vertically scrolling data grid unless requested.

## Optional TSV transfer

Apply this section only when the user asks to copy a table or move it into a spreadsheet.

- Add a restrained `Copy TSV` control; keep it hidden if its JavaScript cannot initialize.
- Generate tab-separated rows from the table while preserving blank cells and rectangular shape.
- Expand merged cells into their grid positions without duplicating their text unless the user requests another convention.
- Copy through the clipboard when available and announce success or failure through an accessible live region.
- A fallback must not claim it copied TSV unless it actually did.

## Verify

Check header associations and wide-table scrolling. If TSV transfer was requested, test blank cells, merged cells, and clipboard failure.
