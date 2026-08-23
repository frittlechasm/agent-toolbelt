# Architecture diagrams

Read `diagrams.md` first for shared SVG construction, accessibility, and responsive behavior.
Use this reference for system, infrastructure, cloud, security, and network topology maps.

## Choose a mode

- Use a neutral architecture map by default.
- Use illustrated architecture mode only when the user requests it or supplies a matching visual reference.
- Arrange components by request path, dependency direction, or supplied system layers. Do not impose flowchart shapes on architecture components.
- Add boundaries only for supplied regions, trust zones, clusters, or ownership groups.

## Plan the topology

1. Inventory the supplied boundaries, nodes, relationships, and connector labels. Do not invent components to balance the layout.
2. Choose the reading direction, semantic lanes, boundary bounds, and a small set of sizing and spacing tokens.
3. Place every complete node footprint before routing connectors. A footprint includes its icon or card, component name, secondary label, and node-owned annotations.
4. Align related nodes on a shared axis when this creates a straight, collision-free connector.
5. Paint in this order: canvas and grid, translucent boundary fills, boundary strokes, connectors, opaque nodes and icons, then labels.

Reuse node sizes, icon sizes, gaps, stroke widths, marker geometry, and label padding throughout the diagram. Vary a token only when the content requires it.

## Size and space the diagram

Lay out semantic lanes, complete node footprints, label bounds, and connector corridors in SVG user units before choosing the responsive scale. Scaling cannot repair crowded source geometry.

- Use 1360–1600 CSS pixels as the representative desktop content width.
- Calculate `scale = rendered width / viewBox width`. Convert rendered targets to source units with `source value = rendered target / scale`.
- Keep sibling container borders at least 64 rendered pixels apart.
- Keep nested borders and complete node footprints at least 32 rendered pixels inside their parent border. All clearances are edge to edge.
- Treat gaps between containers as routing gutters. Keep labels, bends, and parallel tracks out unless the gutter was sized for them.
- Give each busy connector family an annotation lane. Its height must fit the rendered label plus 12 rendered pixels of total vertical clearance. Expand the view box and affected boundaries when lanes do not fit.
- Keep parallel tracks at least 16 rendered pixels apart; prefer 24 pixels in labelled or busy corridors. If the corridor is too narrow, use one unmarked trunk with distinct terminal branches.

Calculate the minimum readable width as:

```text
viewBox width × minimum rendered label size ÷ smallest SVG label font size
```

Choose the natural canvas width after laying out the topology. It must meet that readable-width floor and may exceed the representative content width. For example, a 2720-unit view box with 24-unit secondary labels and a 12px rendered minimum has a 1360px readable-width floor.

Do not use `width: 100%` as the only sizing rule for a large architecture SVG. Put it in the labelled, keyboard-focusable horizontal scroller required by `diagrams.md` and use:

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

This fills containers wider than the natural width and preserves readable geometry by scrolling inside narrower containers. Scrolling is acceptable for an irreducibly wide map. Do not add rows solely to avoid it; choose width or semantic rows according to the topology and reading order.

When source geometry expands, keep text, cards, icons, and spacing proportional enough to meet the rendered targets at the chosen natural width.

## Draw boundaries and titles

- Use a solid stroke for the outer region and a broken stroke for every nested boundary. Default to `stroke-dasharray="8 6"`. Use `stroke-dasharray="1 7"` with `stroke-linecap="round"` only when a true dotted treatment is requested.
- Leave even internal padding and place legends outside boundaries.
- Put each boundary title on its top border. Interrupt only the stroke behind the title so the grid and parent fill remain visible.
- Draw translucent fills and border strokes as separate shapes. Mask the stroke behind each title using the measured text width plus about 16 rendered pixels of total horizontal padding.
- Measure title width with `getComputedTextLength()` after `document.fonts.ready`. Use the final font, weight, and `letter-spacing`, and convert rendered padding to SVG user units.
- Keep the title mask on the straight part of a rounded border. Expand the boundary, reduce non-essential letter spacing, or shorten the title if it reaches a corner.
- Keep titles and strokes fully opaque. Set transparency on the fill, never on the whole boundary group, and do not place an opaque plate behind a title.

## Draw connectors

- Use restrained neutral-slate connectors for ordinary runtime and data relationships. Use dash patterns for identity, provisioning, build, or deployment relationships. Reserve saturated colors for relationships that require them.
- Route horizontally and vertically. Prefer a straight aligned segment, then the shortest clear orthogonal route with the fewest bends. Use diagonals only when the requested notation requires them.
- Never route through an icon or arrowhead. Use a side port when a label below an icon blocks the clear route.
- A connector may terminate on a label owned by its source or target. A supplied region boundary may also be the semantic target. Describe these relationships in the SVG `<desc>` rather than redirecting them to an unrelated card.
- For fan-out in a shared corridor, use one unmarked trunk and one arrowed terminal branch per target. Do not draw overlapping paths or tracks only 5–10 rendered pixels apart; reorder or align nodes when necessary.
- When a routed connector targets a card edge, use a straight terminal segment of at least 24 rendered pixels that meets the edge perpendicularly. Do not add an artificial bend to a direct connector or one targeting a node label.
- Place labels beside clear straight segments. Do not center them on paths, scale glyphs with `textLength`, or create knockouts only for visual symmetry. Shorten a label without changing its meaning, move it into a related region, or create more space.
- Give boundary-crossing labels dedicated annotation lanes. Keep each full label on one side of the boundary stroke with at least 8 rendered pixels of clearance. If the corridor is too narrow, move the label into a related region and use `text-anchor="start"` or `text-anchor="end"` beside a clear segment. Never straddle, mask, or interrupt a boundary for a connector label.
- When a connector starts below a boundary title, route horizontally inside the region before crossing outside the title footprint. Stop boundary-targeting arrowheads 6–8 rendered pixels outside the stroke.
- If a legitimate connector must pass behind a node, title, or connector label, use the shared SVG mask to remove only the hidden connector segment while leaving the canvas and translucent fill visible. Pad text knockouts by 4–6 rendered pixels. Never mask an arrowhead or boundary stroke. Remove an unused knockout mask from the final SVG.

Use thin strokes near 1.25–1.5 rendered pixels and small arrowheads. Define markers in user-space units so stroke changes do not resize them, and put one arrowhead at the target end only.

In illustrated mode, use `#475569` at `0.72` opacity for paths and arrowheads, a fully opaque node-card border near `#64748b`, and darker fully opaque connector labels. Maintain at least 3:1 contrast between the composited connector and every background it crosses. Darken the base color before increasing opacity so connectors remain subordinate to nodes and boundaries.

## Illustrated architecture mode

Use a light graph-paper canvas, translucent semantic regions, icon tiles, and labels below each tile.

- Keep colored boundary fills near 8–16% opacity so the grid and nested regions remain visible. Set it with `fill-opacity` or an `rgba()` fill, not group opacity.
- Use the full available document width. Do not shrink the SVG into a centered 80%-width frame.
- At the rendered desktop size, target 64px icon tiles, 36–40px icon artwork, at least 14px component names, 12px secondary, connector, and boundary labels, and 1.5px connector strokes.
- Center the visible icon artwork, not merely its source view box. Set explicit geometry instead of relying on CSS transforms for `<use>`. Apply an optical correction for asymmetric artwork and verify both axes within 1px.

### Icon sources and provenance

- Collect the actual SVG asset for each recognizable product or service before layout. Use `awsicons.dev` for AWS services and `svgl.app` for other available brands.
- Inline the asset's original `viewBox`, paths, and definitions in a local `<symbol>`. Rename colliding definition IDs. Do not use external images or runtime requests.
- Add an adjacent HTML comment with the source URL for every sourced symbol.
- Preserve the artwork's aspect ratio and brand colors unless the user's design system requires monochrome treatment.
- If the required library has no asset, use a simple generic inline SVG. Do not redraw a known logo from memory, substitute a category glyph without checking, or claim provenance for hand-drawn artwork.

## Typography and neutral visual language

Use JetBrains Mono for all SVG text. This is the only intentional external stylesheet in this reference:

```html
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&amp;display=swap" rel="stylesheet">
```

- Set `font-family: "JetBrains Mono", ui-monospace, monospace` on the SVG root.
- After scaling, keep component names at least 14 CSS pixels and secondary, connector, and boundary labels at least 12 CSS pixels.
- Use the document background or `#0a0a0a`. Do not put the diagram in a decorative card.
- Use one neutral node style by default. Add color only when it consistently distinguishes a supplied category, path, or state.
- Use amber `#fbbf24` for failure or rollback paths, paired with text or line style. Match arrowheads to their connector and keep labels short.
- Give normal-size text, including boundary titles, at least 4.5:1 contrast against its composited background.
- Avoid icons, status dots, gradients, shadows, animation, decorative cards, summary panels, and legends without a meaningful encoding.

The default palette assumes a near-black background. For another theme, preserve the category mapping while maintaining at least 3:1 contrast for meaningful shapes and lines and 4.5:1 for normal-size text.

| Component category | Accent | Color |
| --- | --- | --- |
| Services | Emerald | `#34d399` |
| Data stores | Violet | `#a78bfa` |
| External systems | Slate | `#94a3b8` |
| Security components | Rose | `#fb7185` |
| Message brokers | Orange | `#fb923c` |

## Reusable SVG scaffold

Use direct SVG for stable primitives and layer order. Customize the view box, grid, masks, and content for the supplied topology. Do not copy placeholder nodes or routes into the result.

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
      <!-- Add black rectangles only where connectors pass beneath intervening labels. -->
    </mask>
    <mask id="boundary-title-gaps" maskUnits="userSpaceOnUse" x="0" y="0" width="1200" height="760">
      <rect width="1200" height="760" fill="white" />
      <!-- Add one tight measured rectangle per boundary title. -->
      <rect x="TITLE_X_MINUS_8" y="BOUNDARY_Y_MINUS_10" width="TITLE_WIDTH_PLUS_16" height="20" fill="black" />
    </mask>
  </defs>

  <rect class="canvas" width="1200" height="760" fill="url(#architecture-grid)" />
  <g class="boundary-fills"><!-- translucent fills; no strokes --></g>
  <g class="boundary-strokes" mask="url(#boundary-title-gaps)" fill="none"><!-- solid outer and dashed nested strokes --></g>
  <g class="connectors" mask="url(#connector-knockouts)" fill="none" stroke="#475569" stroke-opacity="0.72" stroke-width="1.5"><!-- routes; terminal markers only --></g>
  <g class="nodes"><!-- opaque cards and centered icon artwork --></g>
  <g class="labels"><!-- node, boundary, and connector labels --></g>
</svg>
```

Keep this scaffold here rather than in `SKILL.md`. It standardizes SVG mechanics without imposing one topology on unrelated systems.

## Verify

Run the checks in `diagrams.md` at desktop and narrow widths. Measure browser geometry rather than judging it only by eye.

- Confirm every supplied component and relationship is present, every element stays within its supplied boundary, and nothing unsupported was added.
- Check every quantified size, clearance, contrast, and track-separation rule above at the rendered scale.
- Check text against other text, cards, connectors, arrowheads, and boundary strokes. A connector-only collision check is insufficient.
- Confirm routes use clear shared axes where possible, the fewest necessary orthogonal bends, consolidated trunks, and stable terminal arrowheads.
- Confirm outer boundaries are solid, nested boundaries are broken, and measured title masks leave the grid visible and rounded corners intact.
- In illustrated mode, confirm each known icon has inline source data, an adjacent source URL comment, and visible artwork centered within 1px on both axes.
- Confirm the natural width meets the readable-width floor. Below that width, only the diagram scroller overflows; above it, the SVG fills the available width.
