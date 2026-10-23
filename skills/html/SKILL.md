---
name: html
description: Create or edit standalone HTML documents when requested by the user or required by another skill. Not for websites or product UI.
metadata:
    scope: global
    agents: all
    machines: all
---

# HTML Document

Create one self-contained `.html` file for document-style reading, with external dependencies only when permitted.
Follow any supplied template, brand, or design system; otherwise use the default in `references/design.md`.

## Content

- Keep the supplied content and its meaning. Do not invent facts, examples, or domain details; ask for required content you cannot find.
- Use the smallest semantic structure that works. Keep short alternatives and comparisons visible; do not hide content or add controls for looks.
- Embed diagrams from the matching skill: `flowchart` for process flows, `topology` for system architecture
  (never a generic process flow in its place), and `erd` for database relationships.
- Add JavaScript only for requested behavior. Read `references/interactions.md` for requested tabs, copy controls, or other interaction,
  and `references/tables.md` only for data tables or spreadsheet transfer, not for prose comparisons or layout grids.

## Layout

- Keep the page readable at about 320px with no page-level horizontal scrolling.
- Drive multi-column reflow from container width, give grid and flex children `min-width: 0`, and wrap code.
- Give only irreducibly wide content its own labelled horizontal scroller, focusable with a visible focus style only while it overflows.

## Print

- For requested print or PDF output of a flowing document, add print styles with a light high-contrast palette, sensible margins,
  hidden controls, and break avoidance for compact groups. Let the browser paginate.
- Use fixed pages only when page-perfect pages are explicitly requested: exact page containers for the paper size, `@page`, and explicit breaks.
  At narrow widths, scale each page inside its wrapper instead of reflowing it. Check every page for overflow.
- Before delivering print output, check print preview for paper size, page count, margins, breaks, contrast, clipping, and hidden controls.

## Verify

- Render in a browser at narrow and desktop widths. Check hierarchy, readability, clipping, overflow, semantics, and requested interactions.
- Remove anything that adds no information or needed behavior; prefer fewer boxes, borders, controls, and hidden views. Re-render after changes.
