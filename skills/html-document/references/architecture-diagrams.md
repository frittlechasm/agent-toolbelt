# Architecture diagrams

Read `diagrams.md` first for shared SVG construction and responsive behavior.
Use this reference for system, infrastructure, cloud, security, or network topology maps.

## Choose the visual mode

- Use a neutral architecture map by default.
- Use illustrated architecture mode only when the user requests it or supplies a matching visual reference.
- Arrange components by request path, dependency direction, or supplied system layers. Do not impose flowchart shapes on architecture components.
- Use boundaries only for supplied regions, trust zones, clusters, or ownership groups. Leave even internal padding and place legends outside boundaries.
- Use a solid stroke for an outer boundary and a broken stroke for every nested boundary.

## Construction contract

- Inventory the supplied boundaries, nodes, relationships, and connector labels before drawing. Do not invent components to balance the layout.
- Establish the reading direction, semantic lanes, boundary bounds, and a small set of node and spacing tokens.
- Align directly related nodes on a shared horizontal or vertical axis when that enables a straight connector without creating a collision.
- Place every complete node footprint before routing any connector. The footprint includes the icon tile, component name, secondary label, and any node-owned annotation.
- Paint layers in this order to keep the relationships behind components and text :
  `canvas and grid -> translucent boundaries -> connectors -> opaque node cards and icons -> then node and connector labels.`
- Reuse the same node sizes, icon sizes, gaps, stroke widths, marker geometry, and label padding throughout one diagram. Vary a token only when content requires it.

## Desktop fit and spacing

- Scaling cannot repair crowded source geometry. Allocate semantic lanes, node footprints, label bounds, and connector corridors in SVG user units before choosing the responsive scale.
- Choose a representative desktop content width, normally 1360–1600 CSS pixels. Estimate the desktop scale as `rendered width / viewBox width`, then convert every rendered clearance target back to source units with `source gap = rendered gap / scale`.
- Keep sibling container borders at least 64 rendered pixels apart. Keep a nested container border and every complete node footprint at least 32 rendered pixels inside its parent border. These are edge-to-edge clearances, not center-to-center spacing.
- Treat the space between containers as a routing gutter. Do not place component names, connector labels, bends, or parallel tracks there unless the gutter is deliberately widened for that content.
- Give each busy connector family its own annotation lane. The source-unit lane height must cover the rendered label height plus at least 12 rendered pixels of total vertical clearance. If the lanes do not fit, expand the view box and affected boundaries. Do not squeeze the lanes or reduce the label font below the minimum.
- Compute the readable width floor with `viewBox width × minimum rendered label size ÷ smallest SVG label font size`.
- Choose a natural canvas width after laying out the topology. It must be at least the readable width floor and may exceed the representative desktop content width when the topology needs more space.
- Do not use `width: 100%` as the sole sizing rule for a large architecture SVG. It forces the natural canvas into the viewport and can recreate congestion. Put the SVG in the labelled, keyboard-focusable horizontal scroller and use this sizing contract:

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

- This contract expands the diagram to fill a container wider than its natural width. In a narrower container, it preserves the natural width and overflows only inside the diagram scroller.
- Example: a 2720-unit-wide view box with 24-unit secondary labels and a 12px rendered minimum has a 1360px readable floor. A dense topology may use a 1760px natural width, so it scrolls inside a 1360px desktop content area instead of shrinking into it.
- Scrolling is acceptable for an irreducibly wide architecture map. Do not fold a clear horizontal topology into extra rows solely to eliminate scrolling. Choose more width or more semantic rows based on the topology and reading order.
- When the source geometry expands, keep its typography, cards, icons, and spacing proportional enough to meet the rendered-size and clearance targets at the chosen natural width.
- Keep parallel connector tracks at least 16 rendered pixels apart and prefer 24 rendered pixels in a labelled or high-traffic corridor. If the available corridor cannot provide that separation, consolidate common travel into one unmarked trunk with distinct terminal branches.

## Boundaries and titles

- Draw the outer region with a solid stroke. Draw every container nested inside another container with a dashed stroke such as `stroke-dasharray="8 6"`; use `stroke-dasharray="1 7"` with `stroke-linecap="round"` only when a true dotted treatment is requested.
- Place each boundary title on its top border, not floating above the container or inset like ordinary content. Interrupt only the stroke behind the title so the title reads as part of the border.
- Create the title gap by drawing the translucent fill and border stroke as separate shapes, then mask the stroke behind the title. Keep the gap tight: measured text width plus about 16 rendered pixels of total horizontal padding.
- Measure each title with `getComputedTextLength()` after `document.fonts.ready`; character-count estimates are not sufficient. The measurement must include the final font, weight, and `letter-spacing`. Convert the rendered padding target back to SVG user units before sizing the mask.
- Verify the title and its padded mask fit on the straight portion of a rounded top border. Expand the boundary, reduce non-essential letter spacing, or shorten the title if the mask would consume a rounded corner.
- Do not cover the title gap with an opaque plate. The graph grid and parent region must remain visible behind the title.
- Keep titles and boundary strokes fully opaque even when the boundary fill is translucent.

## Reusable SVG scaffold

Use direct SVG for stable primitives and layer order.
Customize the view box, grid, masks, and content for the actual topology.
Do not copy placeholder nodes or routes into the result.

```html
<svg class="architecture-diagram" viewBox="0 0 1200 760" role="img" aria-labelledby="architecture-title architecture-description">
  <title id="architecture-title">SYSTEM architecture</title>
  <desc id="architecture-description">Concise description of the supplied components and relationships.</desc>
  <defs>
    <pattern id="architecture-grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0H0V40" fill="none" stroke="#d7dee8" stroke-width="0.75" />
    </pattern>
    <marker id="architecture-arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="8" markerHeight="8" markerUnits="userSpaceOnUse" orient="auto">
      <path d="M0 0L8 4L0 8Z" fill="#475569" fill-opacity="0.72" />
    </marker>
    <mask id="connector-knockouts" maskUnits="userSpaceOnUse" x="0" y="0" width="1200" height="760">
      <rect width="1200" height="760" fill="white" />
      <!-- Add a black rect only where a connector must pass beneath an intervening label. -->
    </mask>
    <mask id="boundary-title-gaps" maskUnits="userSpaceOnUse" x="0" y="0" width="1200" height="760">
      <rect width="1200" height="760" fill="white" />
      <!-- One tight black rect per measured title, centered vertically on its top border. -->
      <rect x="TITLE_X_MINUS_8" y="BOUNDARY_Y_MINUS_10" width="TITLE_WIDTH_PLUS_16" height="20" fill="black" />
    </mask>
  </defs>

  <rect class="canvas" width="1200" height="760" fill="url(#architecture-grid)" />
  <g class="boundary-fills"><!-- translucent supplied region fills; no strokes --></g>
  <g class="boundary-strokes" mask="url(#boundary-title-gaps)" fill="none">
    <!-- solid outer stroke; dashed nested strokes -->
  </g>
  <g class="connectors" mask="url(#connector-knockouts)" fill="none" stroke="#475569" stroke-opacity="0.72" stroke-width="1.5">
    <!-- shortest clear orthogonal routes; marker-end only on terminal segments -->
  </g>
  <g class="nodes"><!-- opaque cards and centered icon artwork --></g>
  <g class="labels"><!-- node and connector labels --></g>
</svg>
```

Keep this scaffold in the reference rather than putting a complete SVG topology in `SKILL.md`.
The scaffold stabilizes the mechanics without forcing unrelated systems into one layout.

## Illustrated architecture mode

### Canvas and nodes

- Use a light graph-paper SVG canvas, translucent semantic regions, icon tiles, and labels below each tile.
- Keep every colored container fill near 8–16% opacity so the grid and nested regions remain visible through it.
- Set transparency on the fill with `fill-opacity` or an `rgba()` fill.
- Do not lower the opacity of the whole container group because that also weakens its border and title.
- Keep the canvas at the full available document width. Size visual elements to the rendered targets below and distribute nodes and routes across the extra space.
- Do not shrink the entire SVG into a centered, 80%-width frame.
- At the rendered desktop size, target roughly 64px icon tiles, 36–40px icon artwork, at least 14px component names, 12px secondary, connector, and boundary labels, and 1.5px connector strokes. Choose SVG source values relative to the view box so these CSS-pixel sizes survive browser scaling.
- Center the final visible icon artwork within each tile, not only its source SVG view box.
- Set explicit icon geometry instead of relying on a CSS transform whose anchor may vary for `<use>` elements.
- Apply a small optical correction when the visible bounds are asymmetric, then verify both center axes within 1px.
- Keep at least 32 rendered pixels between a complete node footprint and its boundary.

### Icon sources and provenance

- Before laying out nodes, collect the actual SVG asset for every recognizable product or service. Use `awsicons.dev` for AWS services and `svgl.app` for other available brands.
- Inline the source asset's original `viewBox`, paths, and definitions in a local `<symbol>`. Rename colliding definition IDs when needed. Do not use external `<img>` elements or runtime requests.
- Do not redraw a known logo from memory, replace it with a category glyph, or claim source provenance for hand-drawn artwork. Use a simple generic inline SVG only after the named product or service cannot be found in the required source library.
- Add an adjacent HTML comment containing the source URL for every sourced symbol. This makes provenance inspectable without adding visual clutter.
- Preserve the source artwork's aspect ratio and brand colors unless the user's design system requires a monochrome treatment. Center the final visible bounds inside the card after scaling.

## Connectors

- Use restrained neutral-slate connectors for ordinary runtime and data relationships.
- Use line style, such as a dash pattern, to distinguish identity, provisioning, build, or deployment relationships.
- Reserve saturated colors for a relationship whose meaning requires them.
- Use thin strokes near 1.25–1.5 rendered pixels and small terminal arrowheads.
- Use one connector token for paths and arrowheads. On the illustrated light canvas, start with `#475569` at `0.72` opacity and a fully opaque node-card border near `#64748b`. Keep connector labels darker and fully opaque.
- Maintain at least 3:1 contrast between the composited connector token and every canvas or translucent region it crosses. If a background fails, darken the base connector color before increasing opacity so connectors remain visually subordinate to nodes and boundaries.
- Define marker size in user-space units so changing stroke width does not inflate the arrowhead. Put one arrowhead at the target end only.
- Route horizontally and vertically. Prefer an aligned straight segment, then the shortest clear orthogonal route with the fewest bends.
- Do not use diagonal connectors unless the requested notation requires them.
- Never route through an icon or arrowhead. A connector may terminate on a label that belongs to its source or target node.
- Use a side port when passing through labels below an icon tile would be unclear.
- Consolidate fan-out that shares a source and corridor into one unmarked trunk, then draw one marked terminal branch per target. Do not replace that trunk with several tracks only 5–10 rendered pixels apart.
- Do not draw partially overlapping parallel lines. If opposite-direction paths would overlap, reorder or align nodes so each path remains distinct.
- When a routed connector targets a card edge, end it with a straight segment of at least 24 rendered pixels that meets the border perpendicularly.
- A direct connector or one that terminates on a node label does not need an artificial terminal bend.
- A node-owned label or a supplied region boundary may be the intentional semantic target. Terminate visibly at that footprint or stroke and describe the relationship in the SVG `<desc>`; do not reroute it to an unrelated card merely to make every arrow look alike.
- Place each connector label beside a straight segment when open space exists. Do not center it on the path or create a knockout only for stylistic alignment.
- Do not use `textLength` or glyph scaling to force a label into a narrow corridor. Shorten the label without changing its meaning, move it wholly into the source or target region, or create more space.
- When a legitimate connector must pass behind a node, boundary title, or connector label, knock out only the connector beneath that element with the shared SVG mask. Pad text knockouts by 4–6 rendered pixels, leave the canvas and translucent fill visible, and never mask an arrowhead or boundary stroke.
- Keep boundary-title knockout zones tight: text width plus about 16 rendered pixels of total horizontal padding.
- When a connector originates below the title, route horizontally inside the region before crossing the boundary outside the title footprint.
- Put boundary-crossing labels in dedicated annotation lanes. Treat every boundary stroke as collision geometry and keep the full rendered label on one side with at least 8 rendered pixels of clearance.
- If an inter-boundary corridor is too narrow for that clearance, move the label wholly into a related region and use `text-anchor="start"` or `text-anchor="end"` beside a clear segment. Never straddle, mask, or interrupt a boundary for a connector label.
- Stop boundary-targeting arrowheads 6–8 rendered pixels outside the stroke.
- Remove the connector-knockout mask from the final SVG when it contains no real knockout rectangles.

## Neutral architecture palette

The default palette assumes a near-black background.
For another theme, preserve the category mapping but adjust every accent to provide at least 3:1 contrast for meaningful lines and shapes and 4.5:1 for normal-size text.

| Component category | Accent | Color |
| --- | --- | --- |
| Services | Emerald | `#34d399` |
| Data stores | Violet | `#a78bfa` |
| External systems | Slate | `#94a3b8` |
| Security components | Rose | `#fb7185` |
| Message brokers | Orange | `#fb923c` |

## Typography and visual language

Use JetBrains Mono for all SVG text. This is the architecture reference's one intentional external stylesheet:

```html
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&amp;display=swap" rel="stylesheet">
```

- Set `font-family: "JetBrains Mono", ui-monospace, monospace` on the SVG root so every label inherits it.
- After browser scaling, keep component names at least 14 CSS pixels and secondary, connector, and boundary labels at least 12 CSS pixels.
- Use the document background or `#0a0a0a` for a neutral architecture SVG. Do not place it in a decorative card.
- Use one neutral node style by default. Add color only when it consistently distinguishes a supplied category, path, or state.
- Use amber `#fbbf24` for failure or rollback paths. Pair color with text or line style.
- Match arrowheads to the connector's color. Keep labels short.
- Give boundary titles and other 12px-equivalent text at least 4.5:1 contrast against the composited translucent fill behind them.
- Outside illustrated architecture mode, avoid icons, status dots, gradients, shadows, animation, decorative cards, summary panels, and legends that explain no meaningful encoding.

## Verify

In addition to the checks in `diagrams.md`, verify:

- every supplied component and relationship is present and no unsupported element was invented
- all complete node footprints fit within their supplied boundaries
- sibling container borders keep at least 64 rendered pixels of clear edge-to-edge separation; nested borders and node footprints keep at least 32 rendered pixels of inner boundary clearance
- inter-container routing gutters contain no accidental labels, bends, or parallel tracks
- related nodes use collision-free shared axes where possible
- routes are straight where possible and otherwise use the fewest clear orthogonal bends
- shared routes are consolidated and terminal arrowheads remain small and stable
- colored boundary fills remain translucent while their strokes and titles stay opaque
- outer boundaries are solid; every nested boundary has a broken stroke and a title integrated into a tight top-border gap
- each known AWS or brand icon contains inline path data from the required source library with an adjacent source URL comment; no hand-drawn substitute is presented as sourced artwork
- visible icon artwork is centered within 1px on both card axes
- labels sit beside clear paths; only unavoidable intersections use transparent SVG knockouts
- rendered connector-label bounds stay wholly on one side of every boundary stroke with at least 8 rendered pixels of clearance at desktop and narrow widths
- the chosen view box, SVG label sizes, and natural canvas width keep primary labels at 14px or more and secondary, connector, and boundary labels at 12px or more
- the natural canvas width is at least the readable width floor; when it exceeds the container, the diagram scroller has `scrollWidth > clientWidth` while the document itself has no horizontal overflow
- at container widths above the natural canvas width, the SVG expands to fill the available width instead of leaving unused desktop space
- every busy connector family has collision-free annotation lanes at the representative desktop scale
- parallel connector tracks remain at least 16 rendered pixels apart, or common travel is consolidated into a shared trunk
- browser geometry checks include text-to-text, text-to-card, text-to-connector, text-to-arrowhead, and text-to-boundary-stroke intersections; a connector-only collision check is insufficient
- every boundary-title mask is based on the browser-measured title length, including letter spacing, and leaves the rounded corners intact
- connector strokes and arrowheads use the same `#475569` at `0.72` token, maintain at least 3:1 composited contrast, and remain lighter than node borders, boundary strokes, and primary text
