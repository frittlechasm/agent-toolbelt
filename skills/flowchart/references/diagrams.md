# Inline SVG flow diagrams

## Layout

- Choose one reading direction: left to right for short flows, top to bottom when branching would get too wide.
- Use capsules for start and end, diamonds for decisions, and rectangles for steps when the distinction helps.
- Keep nodes on a simple grid with consistent sizes, at least 40 rendered CSS px apart, and sized for their longest label.
- Reserve separate space for node labels, connector labels, and arrowheads. No label may overlap another label, node, connector, or arrowhead.
- Put retry and loop steps beside the main column and route their connectors outside it. Place branch labels near where they leave, and avoid crossings.
- Keep steps neutral unless color marks a decision, state, failure, or rollback.

## Text and connectors

- At the natural width, render node titles at 14 CSS px, secondary labels at 11, and connector labels at 10.
  Set each SVG font size to `target / scale`, where `scale = rendered SVG width / viewBox width`.
- Draw connectors before nodes so lines pass behind opaque node backgrounds.
- Use strokes near 1.5 rendered CSS px with `vector-effect="non-scaling-stroke"`.
- Use one `marker-end` defined with `markerUnits="strokeWidth"` and `orient="auto"`, sized to render near 7–9 CSS px, with its reference point at the tip.
- Connect to the nearest clear edge of a node, not its center; a node's own label counts as part of the node.
- End each connector with a clear straight segment, keeping the arrowhead clear of labels, bends, and other nodes.

## Fit and accessibility

- Trim the viewBox to the drawing plus a small even margin.
- Choose a natural width after layout. Never scale above it, and never shrink labels below readable size to fit.
- At narrow widths, either reflow top to bottom (checked at that width) or keep the readable size in a labelled, keyboard-focusable horizontal scroller.
- Give the SVG a concise `<title>` and `<desc>`, and do not repeat the description in nearby prose.

## Verify

At desktop and 320–375px widths, measure in the browser rather than reading source `font-size` values:

- text renders at the target sizes after scaling
- strokes and arrowheads keep their intended size, and each arrowhead follows its path's final direction
- each path endpoint meets its target edge within 1 CSS px
- node spacing, labels, clipping, contrast, and page overflow are correct
