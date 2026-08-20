# Diagrams

Use inline SVG when a flow or architecture map communicates the supplied content more clearly than prose.

## Shared construction

- Keep nodes on a simple grid with consistent dimensions. Leave at least 40px between nodes and enough room for arrowheads and labels.
- Draw connectors before nodes so lines pass behind opaque node backgrounds.
- Connect node borders rather than centers. Prefer straight or orthogonal routes and avoid crossings.

## Flow diagrams

- Choose one reading direction. Use left to right for short flows and top to bottom when branching would make the diagram too wide.
- Use capsules for start and end, diamonds for decisions, and rectangles for steps when those distinctions clarify the process.
- Route retries and loops outside the main path. Place branch labels near their departure points.
- Keep steps neutral unless color communicates a decision, state, failure, or rollback.

## Architecture maps

- Arrange components by request path, dependency direction, or supplied system layers.
- Do not impose flowchart shapes on architecture components.
- Use boundaries only for supplied regions, trust zones, clusters, or ownership groups. Leave even internal padding and place legends outside boundaries.

The following architecture palette assumes a near-black background.
For another theme, preserve the category mapping but adjust every accent, including failure and rollback, to provide at least 3:1 contrast for meaningful lines and shapes and 4.5:1 for normal-size text.

| Component category | Accent | Color |
| --- | --- | --- |
| Services | Emerald | `#34d399` |
| Data stores | Violet | `#a78bfa` |
| External systems | Slate | `#94a3b8` |
| Security components | Rose | `#fb7185` |
| Message brokers | Orange | `#fb923c` |

## Typography

Use JetBrains Mono for all SVG text. The stylesheet below is the diagram reference's one intentional external dependency:

```html
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&amp;display=swap" rel="stylesheet">
```

Set `font-family: "JetBrains Mono", ui-monospace, monospace` on the SVG root so every label inherits it.
Use 14px for component names, 11px for secondary labels, and 10px for connector annotations. Increase them when scaled down.

## Visual language

- Use the document background or `#0a0a0a` for the SVG. Do not place the diagram in a decorative card.
- Use one neutral node style by default. Add color only when it consistently distinguishes a supplied category, path, or state.
- Use amber `#fbbf24` for failure or rollback paths. Pair color with text or line style.
- Match arrowheads to the connector's color and line style.
- Keep labels short. Put one muted secondary line inside the node and short protocol or transition labels near connectors.
- Avoid icons, status dots, gradients, shadows, animation, decorative cards, summary panels, and legends that explain no meaningful encoding.

## Fit and access

- Trim the view box to the drawing plus a small even margin.
- Do not leave large empty regions or scale the diagram beyond its natural readable size.
- Give the SVG a concise `<title>` and `<desc>`. Do not repeat the same full description in nearby prose.
- Let the SVG shrink to the content column. If labels become unreadable, give only the diagram a labelled keyboard-focusable horizontal scroller.
- Inspect node spacing, connector endpoints, arrowheads, labels, boundaries, clipping, contrast, and narrow-width behavior.
