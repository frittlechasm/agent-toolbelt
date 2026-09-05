# Architecture diagrams

Use this reference for system, infrastructure, cloud, security, and network topology maps.

## Select and preserve the visual system

- Use a neutral architecture map by default.
- Use illustrated mode only when:
  - the user requests it, or
  - the user supplies a matching visual reference.
- When given a visual benchmark, inventory its:
  - shell
  - palette
  - fonts
  - relative composition
  - region and node arrangement
  - route axes
  - reusable sourced SVG symbols
- Preserve those choices and assets.
- Make only requested changes.
- Make only the smallest geometry corrections required by this reference's clearance and legibility contracts.
- Preserve relative composition instead of copying flawed coordinates.
- Similar content is not a visual match.
- Arrange components by request path, dependency direction, or supplied system layers.
- Do not use flowchart shapes for architecture components.
- Add only supplied regions, trust zones, clusters, or ownership boundaries.

## Plan the topology

1. Inventory supplied boundaries, nodes, relationships, and connector labels.
   - Do not invent components for visual balance.
2. Choose the reading direction, semantic lanes, and a small set of size and spacing tokens.
3. After `document.fonts.ready`, measure labels in the final font.
   - Plan the complete footprint of each node.
   - Include its icon or card, component name, secondary label, and node-owned annotations.
4. Set explicit boxes for every outer and nested boundary around those footprints.
   - Reserve measured annotation lanes and connector corridors before routing.
5. Align related nodes on shared axes when this creates straight, collision-free connectors.
   - Route through reserved corridors.
6. Paint in this order:
   1. canvas and grid
   2. translucent boundary fills
   3. boundary strokes
   4. connectors
   5. opaque nodes and icons
   6. labels

Reuse node and icon sizes, gaps, strokes, marker geometry, and label padding unless content requires a variation.

## Geometry and responsive sizing

- Lay out semantic lanes, complete footprints, label bounds, and connector corridors in SVG user units before scaling.
- Scaling cannot repair crowded source geometry.

| Contract | Rendered requirement |
| --- | ---: |
| Representative desktop content width | 1360–1600 CSS px |
| Sibling boundary gap, edge to edge | at least 64px |
| Complete sibling footprint gap, edge to edge | at least 40px |
| Nested borders and complete node footprints: inset from parent border, edge to edge | at least 32px |
| Busy annotation lane | label height + 12px total vertical clearance |
| Parallel tracks | at least 16px; prefer 24px when labelled or busy |

Use these sizing formulas:

- `scale = rendered width / viewBox width`
- `source value = rendered target / scale`

Plan routing space explicitly:

- Give each busy connector family an annotation lane.
- Treat container gaps as routing gutters.
- Exclude labels, bends, and parallel tracks from a gutter unless it was sized for them.
- If a busy corridor cannot hold its tracks, use one unmarked trunk with distinct terminal branches.
- If any footprint, label, lane, or route does not fit, expand the affected geometry, boundaries, and view box.
- Do not force a fit by shrinking type, nodes, spacing, or the whole diagram below these contracts.

Calculate the minimum readable width as:

```text
viewBox width × minimum rendered label size ÷ smallest SVG label font size
```

Choose the natural width after layout.

- It must meet this floor.
- It may exceed 1600px.

Worked example: a 2720-unit view box whose smallest label is 24 units has a 1360px floor for a 12px rendered minimum.

Large diagrams need a labelled horizontal scroller, not `width: 100%` alone:

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

This pattern fills wider containers and scrolls inside narrower ones.

- Scrolling is valid for irreducibly wide maps.
- Do not add rows solely to avoid scrolling.
- Choose width or semantic rows from topology and reading order.
- When geometry grows, keep text, cards, icons, and spacing proportional.
  - They must still meet rendered targets at the natural width.

## Boundaries and titles

- Use a solid stroke for the outer region.
- Use a broken stroke for every nested boundary.
  - Default to `stroke-dasharray="8 6"`.
  - Use `stroke-dasharray="1 7"` with `stroke-linecap="round"` only when the user requests a true dotted treatment.
- Use even internal padding.
- Keep legends outside boundaries.
- Put each title on its boundary's top border.
- Draw translucent fills and strokes separately.
- Mask only the stroke behind the title.
  - Keep the grid and parent fill visible.
  - Never use an opaque title plate.
- Wait for `document.fonts.ready`.
- Measure the final title font, weight, and `letter-spacing` with `getComputedTextLength()`.
- Set the mask width to the measured title width plus about 16 rendered px total horizontal padding.
  - Convert this padding to user units.
- Keep the title mask on the straight portion of a rounded border.
- If the mask reaches a corner:
  - expand the boundary,
  - reduce non-essential letter spacing, or
  - shorten the title.
- Keep titles and strokes fully opaque.
- Apply transparency to the fill, never the boundary group.

## Connectors

- Use restrained neutral-slate lines for ordinary runtime and data relationships.
- Use dash patterns for identity, provisioning, build, and deployment.
- Reserve saturated colors for relationships that require them.

### Routing

- Route horizontally and vertically.
- Prefer a straight aligned segment.
- Otherwise use the shortest clear orthogonal path with the fewest bends.
- Use diagonals only when the requested notation requires them.
- Never cross an icon or arrowhead.
- If an icon's label blocks the clear route below it, use a side port.
- A connector may terminate on a label owned by its source or target.
- A supplied region boundary may be the semantic target.
- Describe either endpoint exception in `<desc>`.
- Do not redirect an exceptional endpoint to an unrelated card.

### Fan-out and terminal segments

- Draw one unmarked trunk exactly once for fan-out.
- Draw one arrowed terminal branch per target.
- Never overpaint a trunk or branch.
  - This includes coincident same-direction paths.
- Do not place tracks only 5–10 rendered px apart.
  - Realign or reorder nodes instead.
- A routed card-edge target needs a straight terminal segment at least 24 rendered px long.
  - Make it perpendicular to the edge.
- Do not add an artificial bend to a direct connector or a node-label target.

### Connector labels

- Put labels beside clear straight segments.
- Never center labels on paths.
- Never distort glyphs with `textLength`.
- Never add symmetric decorative knockouts.
- Do not use an opaque backing plate, text stroke, `text-shadow`, filter, or similar text halo to hide a collision.
- If a label does not fit:
  - shorten or reflow it without changing its meaning,
  - move it into a related region, or
  - create space.
- Give boundary-crossing labels dedicated annotation lanes.
- Keep the full label on one side of the stroke.
  - Maintain at least 8 rendered px clearance.
- If needed, move the label into a related region.
  - Use `text-anchor="start"` or `"end"` beside a clear segment.
- Never straddle, mask, or interrupt a boundary for a connector label.

### Titles, boundaries, and knockouts

- When a connector begins below a boundary title, route horizontally inside the region first.
- Cross the boundary outside the title footprint.
- Stop boundary-targeting arrowheads 6–8 rendered px outside the stroke.
- When a legitimate connector passes behind a node, title, or connector label, use one shared mask on the connector layer.
- Remove only the hidden connector segment.
  - Retain the canvas and translucent fill.
- Pad text knockouts by 4–6 rendered px.
- Never mask arrowheads or boundary strokes. A boundary may have only its measured title gap.
- Remove an unused knockout mask.

### Strokes and markers

- Use thin strokes near 1.25–1.5 rendered px.
- Use small arrowheads.
- Define markers with `markerUnits="userSpaceOnUse"`.
- Place the reference point at the tip.
- Put one arrowhead only at the target end.

In illustrated mode:

- Use `#475569` at `0.72` opacity for paths and arrowheads.
- Use a fully opaque node-card border near `#64748b`.
- Use darker, fully opaque connector labels.
- Maintain at least 3:1 contrast between the composited connector and every background it crosses.
- Darken the base color before raising opacity so connectors remain subordinate.

## Illustrated mode and icons

- Use a light graph-paper canvas.
- Use translucent semantic regions, icon tiles, and labels below each tile.
- Fill boundaries at about 8–16% opacity.
  - Use `fill-opacity` or `rgba()`.
  - Never use group opacity.
- Use the full document width.
- Do not use a centered 80%-width frame.

| Element at desktop size | Rendered target |
| --- | ---: |
| Icon tile | 64px |
| Icon artwork | 36–40px |
| Component name | at least 14px |
| Secondary, connector, and boundary label | at least 12px |
| Connector stroke | 1.5px |

- Center the visible artwork, not only its source view box.
- Use explicit geometry instead of CSS transforms on `<use>`.
- Apply optical correction to asymmetric art.
- Verify both axes within 1px.

- Collect the actual SVG for every recognizable product or service before layout.
  - Use `awsicons.dev` for AWS.
  - Use `svgl.app` for other available brands.
- Inline the original `viewBox`, paths, and definitions in a local `<symbol>`.
- Rename colliding definition IDs.
- Do not use external images or runtime requests.
- Put each symbol's source URL in an adjacent HTML comment.
- Preserve each symbol's aspect ratio and brand colors unless the supplied design system calls for monochrome.
- If the preferred library lacks an asset, check the product's official source.
  - If an official SVG is available, use it and cite its URL in an adjacent comment.
  - If no official SVG is available:
    - draw a simple generic inline SVG.
- Do not redraw a known logo from memory.
- Do not substitute a category glyph without checking.
- Do not claim provenance for hand-drawn work.

## Type and neutral visual language

Use JetBrains Mono for all SVG text. This is this reference's only intentional external stylesheet:

```html
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&amp;display=swap" rel="stylesheet">
```

- Set `font-family: "JetBrains Mono", ui-monospace, monospace` on the SVG root.
- After scaling, component names must remain at least 14 CSS px.
- After scaling, secondary, connector, and boundary labels must remain at least 12 CSS px.

- Use the document background or `#0a0a0a`.
- Do not place the diagram in a decorative card.
- Default to one neutral node style.
- Add color only as a consistent encoding of a supplied category, path, or state.
- For failure and rollback paths:
  - use amber `#fbbf24` plus text or line style,
  - match the arrowhead, and
  - keep labels short.
- Avoid the following without meaningful encoding:
  - icons
  - status dots
  - gradients
  - shadows
  - animation
  - decorative cards
  - summary panels
  - legends

- Normal text needs at least 4.5:1 contrast against its composited background.
  - This includes boundary titles.
- Meaningful shapes and lines need at least 3:1 contrast.
- For themes other than near-black, preserve these contrast requirements and this category mapping:

| Category | Accent | Color |
| --- | --- | --- |
| Services | Emerald | `#34d399` |
| Data stores | Violet | `#a78bfa` |
| External systems | Slate | `#94a3b8` |
| Security components | Rose | `#fb7185` |
| Message brokers | Orange | `#fb923c` |

## Reusable SVG scaffold

- Use direct SVG for stable primitives and layer order.
- Customize its view box, grid, masks, IDs, and content.
- Never copy placeholder nodes or routes.

```html
<svg class="architecture-diagram" viewBox="0 0 1200 760" role="img"
     aria-labelledby="architecture-title architecture-description">
  <title id="architecture-title">SYSTEM architecture</title>
  <desc id="architecture-description">Supplied components and relationships.</desc>
  <defs>
    <pattern id="architecture-grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0H0V40" fill="none" stroke="#d7dee8" stroke-width="0.75" />
    </pattern>
    <marker id="architecture-arrow" viewBox="0 0 8 8" refX="8" refY="4"
      markerWidth="8" markerHeight="8" markerUnits="userSpaceOnUse" orient="auto">
      <path d="M0 0L8 4L0 8Z" fill="#475569" fill-opacity="0.72" />
    </marker>
    <mask id="connector-knockouts" maskUnits="userSpaceOnUse" x="0" y="0" width="1200" height="760">
      <rect width="1200" height="760" fill="white" />
      <!-- Add black rectangles only where connectors pass beneath intervening labels. -->
    </mask>
    <mask id="boundary-title-gaps" maskUnits="userSpaceOnUse" x="0" y="0" width="1200" height="760">
      <rect width="1200" height="760" fill="white" />
      <!-- One tight measured rectangle per title. -->
      <rect x="TITLE_X_MINUS_8" y="BOUNDARY_Y_MINUS_10"
        width="TITLE_WIDTH_PLUS_16" height="20" fill="black" />
    </mask>
  </defs>
  <rect class="canvas" width="1200" height="760" fill="url(#architecture-grid)" />
  <g class="boundary-fills"><!-- translucent fills; no strokes --></g>
  <g class="boundary-strokes" mask="url(#boundary-title-gaps)" fill="none"><!-- outer solid; nested broken --></g>
  <g class="connectors" mask="url(#connector-knockouts)" fill="none"
    stroke="#475569" stroke-opacity="0.72" stroke-width="1.5"><!-- terminal markers only --></g>
  <g class="nodes"><!-- opaque cards and centered artwork --></g>
  <g class="labels"><!-- node, boundary, and connector labels --></g>
</svg>
```

## Accessibility, embedding, and responsive behavior

- Give the SVG concise `<title>` and `<desc>` elements.
- Connect them with `aria-labelledby`.
- Do not repeat the full description nearby.
- Trim the view box to the drawing plus a small even margin.
- Preserve the readable-width floor on narrow screens.
- Fill containers wider than the natural width.
- In a narrower container, keep the SVG readable inside a labelled horizontal scroller.
- Only while the scroller overflows:
  - make it keyboard-focusable, and
  - provide a visible focus style.
- A wrapper-local `ResizeObserver` may manage this state.
- Keep the page itself free of horizontal overflow.
- Use JavaScript only for these rendering mechanics.
- Keep JavaScript wrapper-local.
- Add no controls, animation, or unrequested interaction.

## Verify in the browser

Render at both required viewport ranges:

- the representative desktop width
- 320–390px

Use browser measurements, not visual judgment alone.

### Topology

- Confirm that every supplied component and relationship exists.
- Confirm that each element remains in its supplied boundary.
- Confirm that nothing unsupported appears.

### Minimum measurements

- Wait for `document.fonts.ready` before measuring.
- Record the viewport and the SVG's browser-observed scale.
- Computed SVG `font-size` and `stroke-width` values remain in source user units.
- For uniform rendering, multiply those computed values by the scale from `getScreenCTM()`.
- Geometry from `getBoundingClientRect()` is already rendered.
- Do not scale a computed `stroke-width` again when its path uses `vector-effect="non-scaling-stroke"`.

Record each browser-observed value and compare it with its threshold:

| Measurement | Threshold |
| --- | ---: |
| Sibling-boundary gap | 64px |
| Sibling-footprint gap | 40px |
| Nested inset | 32px |
| Component-name size | 14px |
| Secondary-label size | 12px |
| Connector width | 1.5px |

### Collisions

- Compare the full rendered painted box of every text element, including glyph stroke, with every:
  - other text box
  - node footprint
  - connector
  - arrowhead
  - boundary stroke
- Treat connectors and boundaries as stroked geometry, not zero-width centerlines.
- Connector labels must clear boundary strokes by at least 8 rendered px.
- Check every connector-label and boundary pair for both intersection and clearance.
- Report their minimum painted-edge distance and number of clearance violations.
- Zero intersections does not imply that the 8px clearance passes.
- A boundary title's measured gap is intentional only for that title against its own boundary.
- The title gap is not an exception for connector labels or connectors.
- Test every relevant text and geometry class and every applicable pair.
- Record the tested element count, pair count, and computed collision count for each class.
- Each applicable collision class must have a computed count of zero to pass.
- A required class cannot pass when unchecked.
- Report an unchecked or inapplicable class as `unchecked` or `N/A` with the reason.
- Never hardcode zero.
- Do not check only connector collisions.

### Routes and duplicate segments

- Use shared clear axes where possible.
- Use the fewest necessary orthogonal bends.
- Consolidate trunks.
- Keep terminal arrowheads stable.
- Draw every shared same-direction axis segment as one unmarked trunk exactly once.
- Treat any duplicate rendered segment as a failure.
  - This includes coincident same-direction paths.
- Give reverse-direction relationships either:
  - separate visible routes, or
  - an explicit bidirectional encoding.

### Node targets and arrow direction

- Verify every endpoint and visible marker tip in browser coordinates.
- Each must reach its intended target edge within 1 CSS px.
- Each final segment must enter the intended side port perpendicularly.
- Do not terminate at a rounded corner.
- For every terminal arrowhead, record:
  - the final segment vector, and
  - the marker-tip direction.
- Both must point toward the target.

### Boundary targets and rendering

- Stop arrowheads 6–8 rendered px outside the boundary stroke.
- Use solid outer boundaries.
- Use broken nested boundaries.
- Confirm that measured title masks preserve the grid and rounded corners.

### Illustrated icons

For every known icon, confirm:

- inline source data
- an adjacent source URL comment
- artwork centered within 1px on both axes

### Responsive fit

- Confirm that the natural width meets the readable-width floor.
- Below that floor, only the diagram scroller may overflow.
- Above that floor, the SVG must fill the available width.

### Runtime and embedding

- Confirm that the console has no errors.
- Confirm that embedded content and behavior still work.
- Confirm that IDs do not collide.
- Confirm that added CSS and JavaScript remain wrapper-scoped.

### Completion report

- Report a concise QA checkpoint table in the completion response.
- Do not put the table in the HTML unless requested.
- Include for each checkpoint:
  - viewport
  - SVG scale or screen transform used
  - browser-observed minimum or collision count
  - tested element and pair counts for collision checks
  - threshold
  - pass or fail
- Any applicable collision or clearance violation fails its checkpoint.
- If any checkpoint fails:
  1. fix the geometry,
  2. rerender both viewports, and
  3. replace the measurements before claiming completion.
