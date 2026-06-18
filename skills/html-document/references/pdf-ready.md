# PDF-Ready Mode

Use this mode only when the user explicitly asks for PDF-ready, print-ready, page-perfect, deck-style, slide-style, fixed-page, or similar output. For ordinary long-form HTML, stay with the flowing layout in SKILL.md.

Wanting to *export, save, or print to PDF* is **not** a trigger on its own — a flowing document already produces a clean PDF through the browser's print dialog. Switch to this mode only when the user wants each page deliberately composed (slides, a deck, fixed pages, page-perfect handouts). Forcing a short or flowing document into fixed-height pages just scatters its sections with large empty gaps — when in doubt, stay flowing.

PDF-ready mode changes the contract from "content flows" to "each page is intentionally composed." Treat every page like a slide: one page, one job, a bounded amount of content, and a layout chosen from a small set of templates. The guiding constraint is that nothing may spill off a page — so you compose to fit rather than letting the browser decide where breaks fall.

## Structure

Use explicit page sections instead of one flowing article:

```html
<body class="pdf-ready" data-paper="letter">
  <main class="pdf-sheet">
    <section class="pdf-page title-page">...</section>
    <section class="pdf-page two-column-page">...</section>
  </main>
</body>
```

Paper size:

- `data-paper="letter"` by default.
- `data-paper="a4"` when the user asks for A4 or the document is for a non-US audience.
- State the chosen paper size in the final response.

## PDF CSS

Append this after the base CSS. Keep the base tokens and typography; these rules own the fixed page geometry.

The key decision is that `.pdf-page` has a **fixed `height`** (not `min-height`) with `overflow: hidden`, on screen as well as in print. This makes the on-screen render an honest preview of the PDF: content that doesn't fit gets clipped on screen exactly as it would in the printed page, so both the screenshot and the overflow check below catch it. A `min-height` would let the page silently grow on screen — hiding the very overflow you're trying to prevent — while print still clips it, losing content with no warning.

```css
body.pdf-ready { background: var(--bg); }

.pdf-sheet { width: 8.5in; margin: 0 auto; }
body[data-paper="a4"] .pdf-sheet { width: 210mm; }

.pdf-page {
  width: 8.5in;
  height: 11in;            /* fixed: what you see on screen is what prints */
  padding: 0.55in;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  break-after: page;
  page-break-after: always;
}
body[data-paper="a4"] .pdf-page { width: 210mm; height: 297mm; padding: 14mm; }
.pdf-page:last-child { break-after: auto; page-break-after: auto; }

.page-header, .page-footer {
  display: flex; justify-content: space-between; gap: 16px;
  color: var(--faint); font-family: var(--mono); font-size: 11px; line-height: 1.3;
}
.page-header { margin-bottom: 28px; }
.page-footer { margin-top: auto; padding-top: 18px; }

.pdf-page h1 { font-size: 42px; line-height: 1.05; }
.pdf-page h2 { margin-top: 0; padding-top: 0; }

.page-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; align-items: start; }
.page-fill { flex: 1; }

@media print {
  body.pdf-ready { margin: 0; background: #fff; }
  .pdf-sheet, .pdf-page { margin: 0; }
}
```

Also emit exactly one top-level `@page` rule — `@page { size: letter; margin: 0; }` for Letter, or `@page { size: A4; margin: 0; }` for A4. Never leave both active.

## Page templates

Pick a layout before writing each page's content:

- `title-page` — title, subtitle, metadata, optional short summary.
- `summary-page` — 3-5 bullets or stat cards; no dense prose.
- `section-page` — one focused section: heading plus short body.
- `two-column-page` — explanation beside a diagram, list, table, or code excerpt.
- `diagram-page` — one diagram with a short interpretation.
- `code-page` — one code block or before/after pair plus a concise explanation.
- `comparison-page` — two balanced columns with matching headings.
- `table-page` — one table with only the necessary columns.
- `appendix-page` — overflow details that don't fit the main narrative.

## Fit rules

The whole point is that each page is self-contained and fits. When content is too much for one page, split it across more pages — never shrink text below readability or cram.

- Prefer more pages over crowded pages.
- Keep code excerpts short. If a block would need scrolling, split or summarize it.
- Keep tables narrow. Too many columns → split the table, rotate it into key-value lists, or move it to an appendix.
- Move dense evidence, long code, and large tables to `appendix-page`s.
- `break-inside: avoid` helps grouped blocks, but don't rely on it as the pagination strategy — composing to fit is the strategy.
- No fixed-position elements. Headers and footers live inside each `.pdf-page`.

## Required browser check

Verify with `agent-browser` before finalizing. Load the workflow if needed:

```bash
agent-browser skills get core
```

Open the file and measure overflow. Because pages are fixed-height, any page whose content exceeds its box reports a positive `overflowY` (in px), telling you exactly how much to trim:

```bash
agent-browser open file:///absolute/path/to/document.html
cat <<'EOF' | agent-browser eval --stdin
(() => {
  const TOL = 2; // px — ignore sub-pixel rounding
  return [...document.querySelectorAll('.pdf-page')].map((p, i) => ({
    page: i + 1,
    cls: p.className,
    overflowY: p.scrollHeight - p.clientHeight,
    overflowX: p.scrollWidth - p.clientWidth,
  })).filter(r => r.overflowY > TOL || r.overflowX > TOL);
})()
EOF
```

An empty array means every page fits. If anything is reported, revise — split the page, shorten copy, reduce table/code density, or move details to an appendix — then re-check. Don't call the document PDF-ready until the check returns empty.

Also capture a screenshot with `agent-browser screenshot` and visually inspect the first page plus any dense page (and any diagram-, table-, or code-heavy page). Since the screen mirrors print, clipped content in the screenshot is content that would be lost in the PDF.
