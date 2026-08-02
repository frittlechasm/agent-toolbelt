# Flowing print output

Read this only when the user requests printing, PDF export, or print-preview QA for an ordinary flowing document.
Do not switch to fixed-page composition unless the user separately requests deliberate pages, a deck, or page-perfect output.

## Output

- Add print styles with a light, high-contrast palette, sensible page margins, and no fixed-position controls or dark page backgrounds.
- Let the browser paginate flowing content.
- Avoid breaks inside compact code blocks, figures, callouts, and other small grouped content when practical.
- Hide interactive controls and other screen-only affordances. Preserve visible link meaning and repeat table headers when useful.

## Verify

- Inspect print preview at the requested paper size.
- Check page count, margins, contrast, clipping, awkward breaks, repeated headers, and hidden controls.
- Fix print issues without weakening the screen layout.
