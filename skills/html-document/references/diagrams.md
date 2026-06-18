# Diagrams

Read this only when the document needs a diagram. Two routes — hand-built SVG (preferred) and themed Mermaid (for dense or UML diagrams). Both are driven by the canonical `:root` tokens so they match the document and re-theme automatically in print.

## Choosing a route

- **Hand-SVG** for the architecture map and simple flows (a handful of nodes and edges). It needs no JS or network, and because it styles via the `:root` tokens it flips to light colors in print along with the rest of the document. This is the default.
- **Mermaid** when the graph is dense or genuinely UML (class / sequence / state). It's faster to author from text, but needs the CDN + JS and its rendered colors do **not** auto-flip for print — so prefer hand-SVG when print fidelity matters.

## SVG diagram kit

Don't restyle every diagram by hand. Add this CSS once, then compose diagrams from classed elements — the tokens do the theming, so nothing drifts. Dimensions: `720 × 320` to `960 × 480`; corner radius 6–8px; no gradients, no shadows.

```css
.diagram { width: 100%; height: auto; margin: 24px 0; }
.diagram text { font-family: var(--sans); }
.diagram .node { fill: var(--code-bg); stroke: var(--line); stroke-width: 1.5; }
.diagram .node-emph { stroke: var(--link); stroke-width: 2; }   /* highlight one box */
.diagram .label { fill: var(--text); font-size: 14px; }
.diagram .annot { fill: var(--faint); font-size: 12px; }        /* edge labels, notes */
.diagram .edge { stroke: var(--line); color: var(--line); stroke-width: 1.5; fill: none; }
.diagram .edge-emph { stroke: var(--link); color: var(--link); stroke-width: 2; fill: none; }
```

## Layout rules

SVG has no auto-layout — every coordinate is manual and nothing reflows. These rules are what keep a block diagram clean instead of overlapping, misaligned, or clipped:

- **Center text in its box** with `text-anchor="middle"` *and* `dominant-baseline="central"`, positioned at the box center (`x + width/2`, `y + height/2`). Don't hand-tune the baseline — `dominant-baseline` makes vertical centering robust across fonts.
- **Size the box to the text, not the text to the box.** Budget ~8.5px per character at 14px plus ~32px horizontal padding; floor at 120px wide. SVG text never wraps on its own — keep labels under ~20 characters, or split them across two `<tspan>` lines with `dy="1.2em"`.
- **One baseline, one rhythm.** In a row, give every box the same `y` and `width` and a uniform horizontal gap (~90–110px), so arrows have room and the row reads as aligned rather than ragged.
- **Connect borders, not centers.** An edge runs from the source's right border to the target's left border along their shared center line (`y1 = y2 =` box-center y). Stop the line at the target border — the marker's `refX` seats the arrowhead just outside it, so never run the line into the box interior.
- **Put edge labels in the gap**, at the edge midpoint, ~8px above the line (`.annot`, `text-anchor="middle"`). Keep them to a few words; a long label between close boxes will collide.
- **Size the `viewBox` to the content plus ~20px padding on every side.** Anything outside the `viewBox` clips silently — account for labels that sit above edges or below boxes.
- **Direction and wrapping.** Left-to-right for up to ~4 boxes; beyond that, or when the flow branches, stack top-to-bottom with vertical edges (`orient="auto-start-reverse"` already flips the shared arrowhead). Dense or branching graphs are far less error-prone in Mermaid — switch rather than fight the coordinates.

One shared arrowhead `<marker>` in `<defs>`, then reuse it on every edge with `marker-end`. The marker fills with `currentColor`, which resolves to each edge's `color` — that's why the edge classes set `color` alongside `stroke`, so an emphasized edge gets an emphasized arrowhead for free (and both flip correctly in print). The example below follows every rule above; mirror its coordinate pattern.

```html
<svg class="diagram" viewBox="0 0 720 200" role="img" aria-label="Request flow: client to API to database">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0 0 L10 5 L0 10 z" fill="currentColor"/>
    </marker>
  </defs>

  <!-- Boxes: same y (72) and width (150); centers at x+75, y+28 = 100 -->
  <g>
    <rect class="node" x="24"  y="72" width="150" height="56" rx="6"/>
    <text class="label" x="99"  y="100" text-anchor="middle" dominant-baseline="central">Client</text>
  </g>
  <g>
    <rect class="node node-emph" x="285" y="72" width="150" height="56" rx="6"/>
    <text class="label" x="360" y="100" text-anchor="middle" dominant-baseline="central">API</text>
  </g>
  <g>
    <rect class="node" x="546" y="72" width="150" height="56" rx="6"/>
    <text class="label" x="621" y="100" text-anchor="middle" dominant-baseline="central">Database</text>
  </g>

  <!-- Edges run border-to-border on the shared center line y=100 -->
  <line class="edge"      x1="174" y1="100" x2="285" y2="100" marker-end="url(#arrow)"/>
  <text class="annot"     x="229" y="92"  text-anchor="middle">POST /login</text>
  <line class="edge edge-emph" x1="435" y1="100" x2="546" y2="100" marker-end="url(#arrow)"/>
</svg>
```

The same kit composes a **UML class box** — a `.node` rect with an internal divider `<line class="edge">` under the class name to separate the name compartment from its fields. For multi-class or sequence diagrams, the hand-SVG quickly gets tedious; switch to Mermaid below.

An oversized diagram that can't shrink without becoming unreadable goes in a `.scroll-x` wrapper (defined in `elements.md` §6) so it scrolls inside its own block rather than widening the page.

## Themed Mermaid

Mermaid runs in JS and can't read CSS `var()`, so mirror the token **hex values** in `themeVariables`. Initialize once per document; add one `<div class="mermaid">` per diagram.

```html
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
  mermaid.initialize({
    startOnLoad: true,
    theme: 'base',
    themeVariables: {                 // mirror of the :root tokens
      background:         '#000',
      primaryColor:       '#090909',  // --code-bg (node fill)
      primaryBorderColor: '#2a2a2a',  // --line
      primaryTextColor:   '#f5f5f5',  // --text
      lineColor:          '#2a2a2a',  // --line (edges)
      secondaryColor:     '#090909',
      tertiaryColor:      '#000',
      fontFamily:         'ui-sans-serif, system-ui, sans-serif',
    },
  });
</script>

<div class="mermaid">
classDiagram
  class Account { +id: UUID; +seats: int; +addMember() }
  class Member { +id: UUID; +email: string }
  Account "1" --> "*" Member : has
</div>
```

Swap the body for `flowchart`, `sequenceDiagram`, or `stateDiagram-v2` as needed — the theme applies to all of them. If the hex values here ever fall out of sync with the `:root` block in `SKILL.md`, the tokens there are the source of truth; update these to match.
