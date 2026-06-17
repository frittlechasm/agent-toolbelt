# Extended Elements

Optional patterns that extend the base CSS defined in `SKILL.md`. Only reach for these when the content needs structure beyond headings, paragraphs, lists, code blocks, and blockquotes.

All additions use the canonical `:root` tokens. No new colors, no new font stacks.

## Contents

1. [Framing](#1-framing)
2. [Summary](#2-summary)
3. [Code extensions](#3-code-extensions)
4. [Callouts](#4-callouts)
5. [Badges](#5-badges)
6. [Diagrams](#6-diagrams)
7. [Timelines](#7-timelines)
8. [Tables](#8-tables)
9. [Interactive patterns](#9-interactive-patterns)
10. [Document scaffolds](#10-document-scaffolds)

---

## 1. Framing

### Eyebrow

Small label above `<h1>`. Identifies document type and project.

```html
<p class="eyebrow">ARCHITECTURE REPORT · ACME PLATFORM</p>
```

```css
.eyebrow { font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--faint); font-family: var(--mono); margin-bottom: 12px; }
```

### Evidence provenance

Source files that informed the document. Near the top, never sticky.

```html
<aside class="evidence">
  <h3>Files read</h3>
  <ul>
    <li><code>src/auth/session.ts</code> — token verification</li>
  </ul>
</aside>
```

Style with `color: var(--faint); font-size: 15px;`.

---

## 2. Summary

### TL;DR block

One paragraph or three terse lines below the subtitle. Use a blockquote — it already has the left border from the base CSS.

```html
<blockquote><p>Rate limiting now applies per-route. Default is 100 req/min. Override via limits.yaml.</p></blockquote>
```

### Stat cards

Row of 3–5 key metrics when the document has quantitative data worth surfacing.

```html
<div class="stats">
  <div class="stat"><div class="value">14</div><div class="label">PRs merged</div></div>
  <div class="stat"><div class="value">1</div><div class="label">Incidents</div></div>
</div>
```

```css
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 1rem; margin: 28px 0; }
.stat { border: 1px solid var(--line); padding: 1rem; }
.stat .value { color: var(--text); font-size: 2rem; font-weight: 700; }
.stat .label { color: var(--faint); font-size: 14px; }
```

---

## 3. Code extensions

The base CSS handles `<pre><code>`. These patterns are for specialized code presentation.

### File-path header

```html
<div class="code-file">
  <div class="code-path">src/routes/search.ts</div>
  <pre><code>…</code></pre>
</div>
```

```css
.code-path { background: var(--line); color: var(--faint); font-family: var(--mono);
  font-size: 13px; padding: 6px 18px; border: 1px solid var(--line); border-bottom: none; }
.code-file pre { margin-top: 0; }
```

### Annotated diff

`overflow-wrap: anywhere` on the code cell lets long lines wrap inside the code column instead of widening the table. The number and sign columns use `white-space: nowrap` + `width: 1px` so they shrink to fit and never wrap (don't give `.ln` a `ch` width — with `box-sizing: border-box` the cell padding would squeeze the digits onto two lines). `vertical-align: top` keeps the number aligned with the first row of a wrapped line.

```html
<table class="diff">
  <tr class="ctx"><td class="ln">12</td><td class="sign"> </td><td>function handle(req) {</td></tr>
  <tr class="add"><td class="ln">13</td><td class="sign">+</td><td>  const limit = await getLimit(req);</td></tr>
  <tr class="del"><td class="ln">14</td><td class="sign">-</td><td>  const limit = 100;</td></tr>
</table>
```

```css
.diff { width: 100%; border-collapse: collapse; font-family: var(--mono); font-size: 14px;
  border: 1px solid var(--line); margin: 20px 0; }
.diff td { padding: 2px 12px; vertical-align: top; white-space: pre-wrap; overflow-wrap: anywhere; }
.diff .ln { color: var(--faint); width: 1px; text-align: right; user-select: none; white-space: nowrap; }
.diff .sign { width: 1px; white-space: nowrap; }
.diff .add { background: color-mix(in srgb, #4ade80 10%, var(--code-bg)); }
.diff .del { background: color-mix(in srgb, #f87171 10%, var(--code-bg)); }
.diff .ctx { background: var(--code-bg); }
```

### Before / After

Two panels side-by-side on desktop, stacked on mobile. The rules below stretch each code block to fill its panel, so both boxes match the taller one's height — the shorter side gets trailing space, not a ragged box. Code stays top-aligned, so each version's shape stays visible.

```html
<div class="ba">
  <section><h3>Before</h3><pre><code>…</code></pre></section>
  <section><h3>After</h3><pre><code>…</code></pre></section>
</div>
```

```css
.ba { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 1rem; margin: 20px 0; }
.ba > section { display: flex; flex-direction: column; min-width: 0; }   /* min-width:0: panel may shrink below its code's width */
.ba > section > :last-child { flex: 1; display: flex; flex-direction: column; min-width: 0; margin: 0; }  /* code area fills the panel */
.ba > section > :last-child > pre { flex: 1; min-width: 0; margin: 0; }  /* nested <pre> (under a label header) fills too */
@media (max-width: 640px) { .ba { grid-template-columns: minmax(0, 1fr); } }
```

`minmax(0, 1fr)` and `min-width: 0` are load-bearing: without them a `1fr` track (or flex item) won't shrink below its content's intrinsic width, so the panel widens the whole page instead of letting the `<pre>` wrap inside it. Apply the same pattern to any grid/flex container holding a `<pre>` or `<table>` — it's what keeps the document fitting a ~320px side panel.

The `:last-child` selector targets the panel's code area — a bare `<pre>` or a `code-file` wrapper (file-path header + `<pre>`) — and stretches it while the `<h3>` label keeps its height, so equal heights hold with or without a header bar. Keep the code block last in the `<section>`, or it won't be the element that stretches.

### Multi-column code

Three short snippets side-by-side. Same grid pattern as Before/After but with `grid-template-columns: repeat(3, minmax(0, 1fr))` plus `min-width: 0` on the children, so each column can shrink and its code wraps. Collapse to one column at the 640px breakpoint.

---

## 4. Callouts

### Concept callout

Boxed explainer for a concept. Rendered near the relevant code.

```html
<aside class="callout">
  <h4>Optional chaining <code>?.</code></h4>
  <pre><code>user?.profile?.name</code></pre>
  <dl>
    <dt>Semantic</dt><dd>Returns undefined as soon as any link is nullish.</dd>
    <dt>Gotcha</dt><dd>Distinct from the optional-property ? in type annotations.</dd>
  </dl>
</aside>
```

```css
.callout { border: 1px solid var(--line); border-left: 3px solid var(--link); padding: 18px;
  margin: 28px 0; break-inside: avoid; }
.callout h4 { margin: 0 0 8px; }
.callout dl { display: grid; grid-template-columns: max-content 1fr; gap: 4px 16px; margin: 8px 0 0; }
.callout dt { color: var(--faint); font-weight: 600; }
.callout dd { margin: 0; color: var(--muted); }
```

### Note / Gotcha

Short inline note: a label followed by 1–2 sentences.

```html
<p class="note"><strong>⚠ Gotcha:</strong> The config is read once at boot.</p>
```

---

## 5. Badges

Small inline labels for status, severity, or confidence.

| Category | Labels |
| --- | --- |
| Severity | `Blocking`, `Worth a look`, `Nitpick`, `Safe` |
| Risk | `Low`, `Medium`, `High` |
| Status | `Shipped`, `In progress`, `Blocked` |
| Evidence | `Source-backed`, `Inferred`, `Gap` |

```css
.badge { display: inline-block; padding: 2px 8px; font-size: 0.75rem; font-weight: 600;
  border-radius: 3px; border: 1px solid; }
.badge-red { background: color-mix(in srgb, #dc2626 15%, var(--code-bg)); color: #fca5a5;
  border-color: color-mix(in srgb, #dc2626 50%, transparent); }
.badge-green { background: color-mix(in srgb, #16a34a 15%, var(--code-bg)); color: #86efac;
  border-color: color-mix(in srgb, #16a34a 50%, transparent); }
.badge-amber { background: color-mix(in srgb, #d97706 15%, var(--code-bg)); color: #fcd34d;
  border-color: color-mix(in srgb, #d97706 50%, transparent); }
.badge-gray { background: var(--line); color: var(--muted); border-color: var(--line); }
```

---

## 6. Diagrams

Two routes — hand-built SVG (preferred) and themed Mermaid (for dense or UML diagrams). Both are driven by the canonical tokens so they match the document and re-theme automatically in print.

### Choosing a route

- **Hand-SVG** for the architecture map and simple flows (a handful of nodes and edges). It needs no JS or network, and because it styles via the `:root` tokens it flips to light colors in print along with the rest of the document. This is the default.
- **Mermaid** when the graph is dense or genuinely UML (class / sequence / state). It's faster to author from text, but needs the CDN + JS and its rendered colors do **not** auto-flip for print — so prefer hand-SVG when print fidelity matters.

### SVG diagram kit

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

### Layout rules

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

### Wide diagrams, images & art

Code wraps to fit a narrow screen; visual content can't — reflowing an image or diagram destroys it. So anything that must keep its shape — an oversized diagram, a wide screenshot, raster or vector art — keeps its natural size and scrolls *horizontally inside its own block* via one shared wrapper, leaving the document layout (and the page) untouched. This `.scroll-x` is the **only** horizontal scroll the document should ever have.

```css
.scroll-x { overflow-x: auto; margin: 24px 0; }
.scroll-x > * { margin: 0; }                            /* media sits flush in the scroller */
.scroll-x img { max-width: none; }                      /* natural size; swipe/scroll to pan */
.scroll-x .diagram { width: auto; min-width: 720px; }   /* match the diagram's viewBox width */
```

```html
<div class="scroll-x"><img src="architecture.png" alt="System map" width="1400"></div>
<div class="scroll-x"><svg class="diagram" viewBox="0 0 720 200" …>…</svg></div>
```

Defaults first: a hand-SVG `.diagram` (`width: 100%`) and a plain `<img>` (`max-width: 100%`, from the base CSS) already scale to fit the column, and the reader can pinch/zoom — that's preferred. Reach for `.scroll-x` only when shrinking would make a detailed diagram or image unreadable. No JS, and it prints at full size.

### Themed Mermaid

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

---

## 7. Timelines

### Vertical timeline

```html
<ol class="timeline">
  <li><time>14:02</time><p>Deploy starts.</p></li>
  <li><time>14:06</time><p><strong>Impact starts.</strong> 502 errors on /api.</p></li>
  <li><time>14:49</time><p><strong>Mitigated.</strong> Rollback complete.</p></li>
</ol>
```

```css
.timeline { list-style: none; padding-left: 0; }
.timeline li { display: grid; grid-template-columns: 5ch 1fr; gap: 16px; padding: 8px 0;
  border-top: 1px solid var(--line); }
.timeline time { color: var(--faint); font-family: var(--mono); font-size: 14px; }
```

### Sequential steps

Numbered steps for workflows or pipelines.

```html
<ol class="steps">
  <li><h4>Receive request</h4><p>…</p></li>
  <li><h4>Validate</h4><p>…</p></li>
</ol>
```

```css
.steps { counter-reset: step; list-style: none; padding-left: 0; }
.steps li { counter-increment: step; padding: 12px 0; border-top: 1px solid var(--line); }
.steps li::before { content: counter(step); color: var(--faint); font-family: var(--mono);
  font-size: 14px; font-weight: 700; }
```

---

## 8. Tables

Use for multi-column comparable data.

```css
table { width: 100%; border-collapse: collapse; font-size: 15px; margin: 20px 0; }
th { text-align: left; color: var(--faint); font-size: 13px; text-transform: uppercase;
  letter-spacing: 0.05em; padding: 8px 12px; border-bottom: 1px solid var(--line); }
td { padding: 8px 12px; color: var(--muted); border-bottom: 1px solid var(--line); }
```

Right-align numeric columns. No sticky headers. No zebra striping by default.

If a table has many columns or long unbreakable cells, it can push past the viewport and scroll the whole page sideways on a narrow screen. For prose-heavy cells, let them wrap (`td { overflow-wrap: anywhere; }`). For a genuinely wide grid that can't wrap, reuse the `.scroll-x` wrapper (see Diagrams) so only the table scrolls: `<div class="scroll-x"><table>…</table></div>`.

---

## 9. Interactive patterns

These add JavaScript. Use only when the content genuinely benefits — most documents don't need them.

### Tabs

```html
<div class="tabs" role="tablist">
  <button role="tab" aria-selected="true" aria-controls="t1">limits.yaml</button>
  <button role="tab" aria-selected="false" aria-controls="t2">route.ts</button>
</div>
<section role="tabpanel" id="t1">…</section>
<section role="tabpanel" id="t2" hidden>…</section>
```

Keyboard navigable. Print: stack all panels visible.

### Accordions

```html
<details>
  <summary>Implementation details</summary>
  <div>…</div>
</details>
```

Print: render all open.

### Copy buttons

Top-right of code blocks. `navigator.clipboard.writeText`. Hide in print.

---

## 10. Document scaffolds

Common compositions. The content is yours; these are starting structures.

### Architecture report
`<h1>` title → subtitle → TL;DR → stat cards → SVG architecture map (see Diagrams) → modules → data model → key flows (code blocks) → decisions (with badges) → gaps/risks → recommendations → evidence provenance.

### Implementation plan
`<h1>` title → subtitle → stat cards → goals/non-goals → phased steps → code for migrations → risk table (with badges) → testing → rollout → open questions.

### PR write-up
`<h1>` title → subtitle → stat cards → TL;DR → file list → before/after panels → focus areas → scope boundary → testing checklist.

### Code review
`<h1>` title → subtitle → summary → risk map → per-file annotated diffs with badges.

### Research explainer
`<h1>` title → subtitle → evidence → TL;DR → sequential steps → code blocks → callouts + FAQ.

### Incident report
`<h1>` title → subtitle with metadata → impact summary → vertical timeline → root cause + diff → mitigation → action items.

### Status report
`<h1>` title → subtitle → stat cards with deltas → highlights → shipped table → carryover.

### Code-change explainer
`<h1>` title → subtitle → concept map → lessons (each: before/after + walkthrough + callouts) → end-to-end flow → verification.
