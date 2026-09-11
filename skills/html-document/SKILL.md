---
name: html-document
description: Create or edit standalone HTML documents when requested by the user or required by another skill. Not for websites or product UI.
metadata:
    scope: global
    agents: all
    machines: all
---

# HTML Document

- Create one standalone `.html` file for document-style reading.
- Keep it self-contained except for explicitly permitted dependencies.
- Follow supplied template, brand, or design system. Otherwise read `references/design.md` and use its default visual system.

## Content

- Preserve the supplied content and requested elements without inventing facts or changing meaning.
- Use the smallest semantic structure that communicates the content clearly.
- Keep short alternatives and comparisons visible. Do not hide content or add controls merely to create a visual pattern.
- For a process flow diagram, use the `flow-diagram` skill when available and embed its SVG in the document.
- For a system architecture diagram, use the `architecture-diagram` skill when available and embed its SVG in the document.
- Do not use a generic process-flow fallback as a system architecture diagram.
- For database content, use the `erd-diagram` skill and include its ERD in the same HTML document.
- If required content was not supplied and cannot be found, ask for it instead of fabricating examples or domain details.

## Output

- Keep HTML, CSS, and any required JavaScript in the file.
- Add JavaScript only for behavior the user requested.
- Keep the page readable to about 320px without page-level horizontal scrolling.
- For flowing documents, drive multi-column reflow from container width, let grid and flex children shrink with `min-width: 0`, and wrap code.
- Give only irreducibly wide content its own labelled horizontal scroller. Make it keyboard focusable with a visible focus style only when it overflows.

## Print and fixed pages

- When print or PDF export is requested for a flowing document:
    - add print styles with a light high-contrast palette
    - sensible page margins
    - hidden interactive controls
    - practical break avoidance for compact grouped content
    - Let the browser paginate it.
- Use fixed pages only when the user explicitly requests page-perfect or deliberately composed pages.
- Match the requested paper size with exact page containers, `@page`, and explicit page breaks.
- Preserve fixed-page geometry at narrow widths by scaling each page inside its wrapper instead of reflowing its contents.
- Check every page for horizontal and vertical overflow.
- For any requested print output, inspect print preview for paper size, page count, margins, breaks, contrast, clipping, and hidden controls before delivery.

## References

Read only what the selected content requires:

- `references/design.md` — the default visual system when no template, brand, or design system was supplied.
- `references/interactions.md` — explicitly requested tabs, copy controls, or other interaction.
- `references/tables.md` — only for data tables, tabular presentation, or spreadsheet transfer. Ignore for prose comparisons, option panels, or layout grids.

## Verify

- Render every result in an available browser and visually inspect it at narrow and desktop widths.
- Check hierarchy, readability, clipping, page overflow, semantics, and any requested interactions.
- Remove every element that adds no information or required behavior, then re-render.
- Prefer fewer boxes, borders, controls, and hidden views when both versions communicate the same content.
- Fix issues before delivery.
