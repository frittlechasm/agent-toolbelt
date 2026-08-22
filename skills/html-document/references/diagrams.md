# Diagrams

Use inline SVG when a diagram communicates the supplied content more clearly than prose.
For an architecture map, read this reference and `architecture-diagrams.md`.

## Shared construction

- Keep nodes on a simple grid with consistent dimensions. Leave at least 40px between nodes and enough room for arrowheads and labels.
- Size nodes for their longest label. Reserve separate space for node labels, connector labels, and arrowheads.
- Do not let a label overlap another label, node boundary, connector, or arrowhead.
- Draw connectors before nodes so lines pass behind opaque node backgrounds.
- Connect to the nearest clear edge of the node footprint rather than its center.
- A label that belongs to a node is part of that footprint and is a valid connector endpoint. Avoid crossings.

## Flow diagrams

- Choose one reading direction. Use left to right for short flows and top to bottom when branching would make the diagram too wide.
- Use capsules for start and end, diamonds for decisions, and rectangles for steps when those distinctions clarify the process.
- Route retries and loops outside the main path. Place branch labels near their departure points.
- Keep steps neutral unless color communicates a decision, state, failure, or rollback.

## Fit and access

- Trim the view box to the drawing plus a small even margin.
- Choose the diagram's natural rendered width after layout. Do not let responsive sizing enlarge it beyond that width or shrink labels below readability.
- Verify final text sizes in CSS pixels after view box scaling.
- Give the SVG a concise `<title>` and `<desc>`. Do not repeat the same full description in nearby prose.
- Do not fit a wide, text-heavy SVG by shrinking it until labels become unreadable.
- At narrow widths, reflow it top to bottom or preserve its readable size inside a labelled keyboard-focusable horizontal scroller.
- Inspect at desktop and 320–375px widths. Measure rendered label sizes after view box scaling; do not infer them from the source `font-size` value.
- At both widths, verify that:
  - connector strokes and arrowheads retain their intended rendered size
  - each terminal arrowhead follows the final path direction
  - each path endpoint meets its target edge in browser coordinates within 1 CSS pixel
- Check node spacing, labels, clipping, contrast, and page overflow.
