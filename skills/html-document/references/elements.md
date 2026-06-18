# Extended Elements

Optional patterns that extend the base CSS defined in `SKILL.md`. Only reach for these when the content needs structure beyond headings, paragraphs, lists, code blocks, and blockquotes.

All additions use the canonical `:root` tokens. No new colors, no new font stacks.

## Contents

1. [Framing](#1-framing)
2. [Summary](#2-summary)
3. [Code extensions](#3-code-extensions)
4. [Callouts](#4-callouts)
5. [Badges](#5-badges)
6. [Diagrams & wide content](#6-diagrams--wide-content) (diagram kit in `diagrams.md`)
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

Side-by-side when there's room, stacked vertically when there isn't — **stacking is the primary response to a narrow layout**, since two full-width panels read better than two cramped, wrapped columns (code-wrapping is the last resort, for when a single stacked panel is itself narrow). The rules also stretch each code block to fill its panel so both boxes match the taller one's height — top-aligned, so each version's shape stays visible.

```html
<div class="ba">
  <section><h3>Before</h3><pre><code>…</code></pre></section>
  <section><h3>After</h3><pre><code>…</code></pre></section>
</div>
```

```css
.ba { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 22rem), 1fr)); gap: 1rem; margin: 20px 0; }
.ba > section { display: flex; flex-direction: column; min-width: 0; }   /* min-width:0: panel may shrink below its code's width */
.ba > section > :last-child { flex: 1; display: flex; flex-direction: column; min-width: 0; margin: 0; }  /* code area fills the panel */
.ba > section > :last-child > pre { flex: 1; min-width: 0; margin: 0; }  /* nested <pre> (under a label header) fills too */
```

`repeat(auto-fit, minmax(min(100%, 22rem), 1fr))` does the stacking: each panel wants ~22rem, so when the container can't hold two side-by-side — narrow window, side panel, phone — the grid drops to one column. It keys off the **container's real width**, not the viewport, so a narrow desktop window stacks too (no media query, no breakpoint to tune). `min(100%, 22rem)` caps the track at the container width so a sub-22rem container never overflows.

`min-width: 0` on the section and its code area is load-bearing: a grid/flex item won't shrink below its content's intrinsic width without it, so the panel would widen the page instead of letting the `<pre>` wrap. Apply this same `auto-fit` + `min-width: 0` pattern to any grid holding a `<pre>` or `<table>` — it's what keeps the document fitting a ~320px panel.

The `:last-child` selector stretches the panel's code area — a bare `<pre>` or a `code-file` wrapper — while the `<h3>` keeps its height, so equal heights hold with or without a header bar. Keep the code block last in the `<section>`.

### Multi-column code

Three or more short snippets side-by-side. Same self-stacking pattern as Before/After: `grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr))` plus `min-width: 0` on the children. Columns sit side-by-side while they fit and reflow to fewer columns (down to a single stacked column) as the width drops — no breakpoint to tune. Use a smaller min (~18rem) than Before/After so three columns can coexist on a roomy page.

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

## 6. Diagrams & wide content

When the document needs a **diagram**, read `references/diagrams.md` — it has the hand-SVG kit (CSS, layout rules, a worked example) and the themed-Mermaid setup. Default to hand-SVG; it needs no JS and re-themes for print. Skip that file entirely for documents without diagrams.

### Wide content, images & art

Code wraps; visual content can't — reflowing an image or diagram destroys it. So anything that must keep its shape — an oversized diagram, wide screenshot, raster or vector art, a many-column table — keeps its natural size and scrolls *horizontally inside its own block* via one shared wrapper, leaving the page untouched. `.scroll-x` is the **only** horizontal scroll the document should ever have.

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

Defaults first: a hand-SVG `.diagram` (`width: 100%`) and a plain `<img>` (`max-width: 100%`) already scale to fit the column — preferred. Reach for `.scroll-x` only when shrinking would make a detailed diagram or image unreadable. No JS; prints at full size.

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

If a table has many columns or long unbreakable cells, it can push past the viewport and scroll the whole page sideways on a narrow screen. For prose-heavy cells, let them wrap (`td { overflow-wrap: anywhere; }`). For a genuinely wide grid that can't wrap, reuse the `.scroll-x` wrapper (§6) so only the table scrolls: `<div class="scroll-x"><table>…</table></div>`.

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
`<h1>` title → subtitle → TL;DR → stat cards → SVG architecture map (see `diagrams.md`) → modules → data model → key flows (code blocks) → decisions (with badges) → gaps/risks → recommendations → evidence provenance.

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
