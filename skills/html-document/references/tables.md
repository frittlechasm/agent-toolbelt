# Tables

Read this only when selected content already contains a data table, the user explicitly requests tabular presentation, or spreadsheet transfer is requested.
Do not read it for prose comparisons, option panels, CSS grids, or other layouts that merely use rows or columns.

## Structure

- Use `<caption>`, `<thead>`, `<tbody>`, scoped column headers, and row headers where appropriate.
- Preserve logical reading order. Right-align numeric columns and use tabular numerals.
- Use readable gridlines, padding, and wrapping. Let narrow tables fit naturally.
- For a genuinely wide table, choose deliberate column widths and use the document's item-level scroller rule.
- Do not create a vertically scrolling data grid unless requested.

## Spreadsheet transfer

Apply this only when the user asks to copy a table or move it into a spreadsheet.

- Derive the copied payload from the rendered table so it cannot drift from the visible data.
- Use TSV by default. For requested CSV, double embedded quotes and quote fields containing commas, quotes, or line breaks.
- Label the control `Copy TSV` or `Copy CSV` accurately and keep it hidden if its JavaScript cannot initialize.
- Preserve blank cells and rectangular shape. Expand merged cells into their grid positions without duplicating text unless requested.
- Report clipboard success or failure next to the control through an accessible live region.

## Verify

- Check header associations and wide-table scrolling.
- For spreadsheet transfer, test blank cells, merged cells, escaping, the exact payload, and clipboard failure.
