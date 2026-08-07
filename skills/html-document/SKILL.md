---
name: html-document
description: Create standalone HTML documents for reports, explainers, proposals, plans, and other document-style reading. Use only when the user asks to generate, edit, or convert document content as HTML, or when another skill requires HTML output. Do not use for websites, landing pages, web apps, React apps, dashboards, or product UI.
---

# HTML Document

Create one self-contained `.html` file for document-style reading.
Follow any supplied template, brand, or design system; otherwise use the restrained default below.

## Ownership

- Render the primary content and elements requested by the user or invoking skill.
- When neither specifies them, choose the smallest structure that communicates the content clearly.
- Add supporting presentation—such as copy controls, tabs, timelines, stat panels, badges, callouts, or comparison layouts when:
  - existing content naturally supports it
  - the enhancement improves scanning, comparison, navigation, or reuse.
- Do not invent content, change meaning, or hide information merely to support a visual pattern. This skill owns presentation, not domain content.
- If required primary content was not supplied and cannot be found in the available context, ask for it instead of fabricating examples or domain details.

## Default

- Use a flowing, single-column layout around 920px wide with system fonts, a near-black screen theme, high-contrast text, and muted secondary text.
- Use thin separators sparingly and at most once per content boundary.
- Avoid gradients, shadows, decorative cards, imagery without informational value, navigation, and a table of contents unless requested.
- Keep HTML, CSS, and required JavaScript in the file. Add no frameworks, web fonts, CDN assets, or other external dependencies unless requested.
- Generate only the styles and behavior the document needs.

- Keep the page readable to about 320px without page-level horizontal scrolling.
- Drive multi-column reflow from container width, let grid and flex children shrink with `min-width: 0`, wrap code.
- Give only irreducibly wide media its own horizontal scroller.

## References

Read only what the selected content requires:
- `references/elements.md` — supporting layouts and visual emphasis.
- `references/interactions.md` — when content includes reusable code, prompts, commands, payloads, or configuration; independent alternate views; or an explicit request.
- `references/diagrams.md` — selected diagrams.
- `references/tables.md` — only for data tables, tabular presentation, or spreadsheet transfer. Ignore for prose comparisons, option panels, or layout grids.
- `references/print.md` — requested printing, PDF export, or print-preview QA for flowing HTML.
- `references/pdf-ready.md` — requested fixed pages, decks, or page-perfect output.

## Verify

- Render every result in an available browser and visually inspect it at narrow and desktop widths.
- Check hierarchy, readability, clipping, page overflow, interactions, semantics, and visible focus. Confirm section transitions have no duplicate or stranded separators.
- Fix issues before delivery. Perform print-preview QA only when print or fixed-page output was requested.
