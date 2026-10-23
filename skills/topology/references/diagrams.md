# Architecture diagrams

Use this for system, infrastructure, cloud, security, and network topology maps.

## Visual system

- Use a neutral map by default. Use illustrated mode only when requested or when a supplied visual reference uses it.
- For a visual benchmark, inventory and keep its shell, palette, fonts, composition, node and region layout, route axes, and sourced SVG symbols.
  Similar content is not a visual match. Apply only requested changes and the smallest geometry fixes needed for clearance and legibility.
- Arrange components by request path, dependency direction, or supplied layers. Do not use flowchart shapes for components.
- Add only supplied regions, trust zones, clusters, or ownership boundaries. Do not invent components for visual balance.

## Plan the layout

1. Inventory the supplied boundaries, nodes, relationships, and connector labels.
2. Choose the reading direction, semantic lanes, and a small set of size and spacing tokens. Reuse them unless content needs a variation.
3. After `document.fonts.ready`, measure labels in the final font. Plan each node's full footprint: icon or card, name, secondary label, and annotations.
4. Set explicit boxes for every boundary around those footprints, and reserve annotation lanes and connector corridors before routing.
5. Align related nodes on shared axes when that gives straight, collision-free connectors.
6. Paint in order: canvas and grid, translucent boundary fills, boundary strokes, connectors, opaque nodes and icons, then labels.

## Sizing

Lay out in SVG user units first; scaling cannot fix crowded geometry.
Convert with `scale = rendered width / viewBox width` and `source value = rendered target / scale`.

| Rendered requirement | Value |
| --- | ---: |
| Representative desktop content width | 1360–1600 CSS px |
| Gap between sibling boundaries, edge to edge | at least 64px |
| Gap between complete sibling node footprints | at least 40px |
| Inset of nested boundaries and node footprints from the parent border | at least 32px |
| Busy annotation lane | label height + 12px vertical clearance |
| Parallel tracks | at least 16px; prefer 24px when labelled or busy |
| Component name | at least 14px |
| Secondary, connector, and boundary labels | at least 12px |
| Connector stroke | 1.25–1.5px; 1.5px in illustrated mode |

- Treat container gaps as routing gutters. Keep labels, bends, and parallel tracks out of a gutter unless it was sized for them.
- Give each busy connector family an annotation lane. If a corridor cannot hold its tracks, use one unmarked trunk with separate terminal branches.
- If anything does not fit, expand the geometry, boundaries, and viewBox. Never shrink type, nodes, spacing, or the diagram below these values.
- Minimum readable width = `viewBox width × minimum rendered label size ÷ smallest SVG label font size`.
  Choose the natural width after layout; it must meet that floor and may exceed 1600px.
- As geometry grows, keep text, cards, icons, and spacing proportional and still at their rendered targets.
- Scrolling is fine for irreducibly wide maps; do not add rows just to avoid it. Choose width or rows from the topology and reading order.
  Use a labelled scroller, not `width: 100%` alone:

```css
.diagram-scroll {
  --diagram-natural-width: 1760px;
  overflow-x: auto;
  overflow-y: hidden;
}

.architecture-diagram {
  display: block;
  width: var(--diagram-natural-width);
  min-width: 100%;
  max-width: none;
  height: auto;
}
```

This fills wider containers and scrolls inside narrower ones.

## Boundaries

- Outer region: solid stroke. Nested boundaries: broken stroke, `stroke-dasharray="8 6"` by default,
  or `"1 7"` with `stroke-linecap="round"` only when the user asks for dotted.
- Use even internal padding and keep legends outside boundaries.
- Draw translucent fills separately from fully opaque strokes and titles. Apply transparency to the fill, never the boundary group.
- Put each title on its boundary's top border by masking only the stroke behind it, so the grid and parent fill stay visible. Never use an opaque title plate.
- After `document.fonts.ready`, size each mask with `getComputedTextLength()` on the final font, weight, and `letter-spacing`,
  plus about 16 rendered px of total horizontal padding converted to user units.
- Keep the mask on the straight part of a rounded border. If it reaches a corner, widen the boundary, reduce letter spacing, or shorten the title.

## Connectors

- Use restrained neutral-slate lines for runtime and data relationships, and dash patterns for identity, provisioning, build, and deployment.
  Reserve saturated color for relationships that need it.
- Use thin strokes and small arrowheads defined with `markerUnits="userSpaceOnUse"`, with the reference point at the tip and one arrowhead at the target end.

### Routing

- Route horizontally and vertically: a straight aligned segment if possible, otherwise the shortest clear path with the fewest bends.
  Use diagonals only when the requested notation requires them.
- Never cross an icon or arrowhead. If an icon's label blocks the route below it, end on that label when it belongs to the source or target;
  otherwise use a side port.
- A connector may end on a label owned by its source or target, or on a supplied region boundary.
  Describe either exception in `<desc>`, and do not redirect it to an unrelated card.
- For fan-out, draw one unmarked trunk once and one arrowed branch per target. Never draw a segment twice, including coincident same-direction paths.
- Do not place tracks 5–10 rendered px apart; realign or reorder nodes instead.
- Give reverse-direction relationships separate visible routes or an explicit bidirectional encoding.
- A routed connector ending on a card edge needs a straight, perpendicular final segment of at least 24 rendered px.
  Do not add bends to direct connectors or node-label targets.
- A connector starting below a boundary title runs horizontally inside the region first, then crosses the boundary away from the title.
- Stop arrowheads that target a boundary 6–8 rendered px outside its stroke.

### Labels

- Put labels beside clear straight segments, fully on one side of the stroke. Never center them on a path.
- Keep connector labels at least 8 rendered px from boundary strokes. Give boundary-crossing labels their own annotation lanes,
  and never straddle, mask, or interrupt a boundary for a label.
- Never hide a collision with `textLength`, an opaque plate, text stroke, `text-shadow`, a filter, or a decorative knockout.
  If a label does not fit, shorten it without changing its meaning, move it into a related region with `text-anchor="start"` or `"end"`, or make room.

### Knockouts

- When a connector legitimately passes behind a node, title, or label, use one shared mask on the connector layer.
  It removes only the hidden segment, padded 4–6 rendered px, and keeps the canvas and fill visible.
- Never mask arrowheads or boundary strokes; a boundary's only gap is its measured title gap. Remove unused masks.

## Type and color

Use JetBrains Mono for all SVG text, set on the SVG root as `"JetBrains Mono", ui-monospace, monospace`. Its stylesheet is the only external one:

```html
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&amp;display=swap" rel="stylesheet">
```

- Use the document background or `#0a0a0a`, with no decorative card around the diagram. Default to one neutral node style.
- Add color only as a consistent encoding of a supplied category, path, or state.
  For failure and rollback paths, use amber `#fbbf24` with text or line style, a matching arrowhead, and short labels.
- Without a meaningful encoding, avoid icons, status dots, gradients, shadows, animation, decorative cards, summary panels, and legends.
- Normal text, including boundary titles, needs at least 4.5:1 contrast against its composited background; meaningful shapes and lines need 3:1.
- For themes other than near-black, keep those contrast ratios and this category mapping:

| Category | Accent | Color |
| --- | --- | --- |
| Services | Emerald | `#34d399` |
| Data stores | Violet | `#a78bfa` |
| External systems | Slate | `#94a3b8` |
| Security components | Rose | `#fb7185` |
| Message brokers | Orange | `#fb923c` |

## Illustrated mode

- Use a light graph-paper canvas across the full document width, not a centered 80%-width frame.
- Fill semantic regions at 8–16% opacity with `fill-opacity` or `rgba()`, never group opacity.
- Use 64px icon tiles with 36–40px artwork and a label below each tile.
- Draw paths and arrowheads in `#475569` at `0.72` opacity, node-card borders fully opaque near `#64748b`, and connector labels darker and fully opaque.
- Keep that connector color and opacity. If a crossing falls below 3:1 contrast, lighten or reroute around that background instead.
- Center the visible artwork, not just its viewBox, with explicit geometry instead of CSS transforms on `<use>`.
  Correct asymmetric art optically and check both axes within 1px.

### Icons

- Collect the real SVG for every recognizable product before layout: `awsicons.dev` for AWS and `svgl.app` for other brands.
  If the library lacks it, check the product's official source.
- Inline the original `viewBox`, paths, and definitions in a local `<symbol>`, renaming colliding IDs. No external images or runtime requests.
- Put each symbol's source URL in an adjacent HTML comment. Keep its aspect ratio and brand colors unless the design system calls for monochrome.
- If no official SVG exists, draw a simple generic glyph. Never redraw a known logo from memory, substitute a category glyph without checking,
  or claim a source for hand-drawn work.

## Accessibility and embedding

- Give the SVG `role="img"` and concise `<title>` and `<desc>` joined by `aria-labelledby`. Do not repeat the full description nearby.
- Trim the viewBox to the drawing plus a small even margin.
- Make the scroller keyboard-focusable with a visible focus style only while it overflows; a wrapper-local `ResizeObserver` may manage this.
  The page itself must not scroll horizontally.
- Keep JavaScript wrapper-local and limited to these mechanics and, when requested, playback from [motion.md](motion.md).

## Verify in the browser

Render at the representative desktop width and at 320–390px. Use browser measurements, not visual judgment alone.

- **Content:** every supplied component and relationship exists and stays in its boundary, and nothing unsupported appears.
- **Scale:** wait for `document.fonts.ready`, then record the viewport and the SVG's observed scale.
  Computed SVG `font-size` and `stroke-width` are in user units, so multiply them by the `getScreenCTM()` scale.
  `getBoundingClientRect()` is already rendered. Do not rescale strokes that use `vector-effect="non-scaling-stroke"`.
- **Minimums:** check boundary gaps, footprint gaps, nested insets, label sizes, and connector width against the sizing table.
- **Collisions:** compare each text element's full painted box with every other text box, node footprint, connector, arrowhead, and boundary stroke,
  treating strokes as having width.
  - Check every connector-label and boundary pair for both intersection and the 8px clearance; zero intersections does not mean clearance passes.
  - A title's gap applies only to that title and its own boundary, not to connectors or connector labels.
  - Record element, pair, and collision counts per class. Each must be zero to pass. Report a class you could not check as `unchecked`
    or `N/A` with the reason; it cannot pass. Never hardcode zero.
- **Routes:** no duplicate rendered segments, shared same-direction axes drawn once as unmarked trunks, the fewest bends,
  and reverse-direction relationships on separate visible routes or with an explicit bidirectional encoding.
- **Endpoints:** every endpoint and marker tip reaches its target edge within 1 CSS px, enters its side port perpendicularly, and avoids rounded corners.
  Record each arrowhead's final segment vector and marker direction; both must point at the target.
  Boundary targets stop 6–8px outside the stroke.
- **Boundaries:** outer solid, nested broken, and title masks keep the grid and rounded corners intact.
- **Icons:** each known icon has inline source data, an adjacent source URL comment, and artwork centered within 1px.
- **Fit:** the natural width meets the readable floor. Below it, only the diagram scroller overflows; above it, the SVG fills the width.
- **Runtime:** no console errors, embedded content still works, IDs do not collide, and added CSS and JavaScript stay wrapper-scoped.

### Completion report

Put a concise QA table in your response, not in the HTML unless asked. For each checkpoint give the viewport, the scale used,
the observed minimum or collision count, element and pair counts for collision checks, the threshold, and pass or fail.
Give every check its own row, including the trunk and reverse-route checks (`N/A` with a reason when they do not apply).
Measure each value; never hardcode a result. Any violation fails.
If anything fails, fix the geometry, rerender both viewports, and replace the measurements before claiming completion.
