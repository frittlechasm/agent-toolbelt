# Elements Catalog

Detailed pattern reference for `html-document`. Every distinctive element used in a polished standalone HTML document is here: when to use it, the semantic structure, key style cues, and the demo on [thariqs.github.io/html-effectiveness](https://thariqs.github.io/html-effectiveness/) that the pattern is derived from. Reach for these when laying anything out — do not reinvent them.

The catalog is grouped: §1–§3 frame the document, §4–§6 highlight content, §7–§9 show structure spatially, §10–§14 add interaction, §15–§17 are specialty patterns, §18 composes them into full document scaffolds.

## Contents

1. [Framing](#1-framing)
2. [Summary & Stat Cards](#2-summary--stat-cards)
3. [Body Typography](#3-body-typography)
4. [Code & Comparison](#4-code--comparison)
5. [Callouts & Glossary](#5-callouts--glossary)
6. [Badges & Risk](#6-badges--risk)
7. [Diagrams & Flow](#7-diagrams--flow)
8. [Sequential Flow](#8-sequential-flow)
9. [Timelines & Phase Cards](#9-timelines--phase-cards)
10. [Tabs](#10-tabs)
11. [Click-to-Reveal](#11-click-to-reveal)
12. [Tooltips & Hover Glossary](#12-tooltips--hover-glossary)
13. [Copy Buttons](#13-copy-buttons)
14. [Custom Interactive Controls](#14-custom-interactive-controls)
15. [Inline Mockups](#15-inline-mockups)
16. [Tables](#16-tables)
17. [Design Tokens](#17-design-tokens)
18. [Document Scaffolds](#18-document-scaffolds)

---

## 1. Framing

The first screen identifies the document type, names it, and tells the reader who it is for. Everything in §1 spans the full container width, not the body line-length.

### Document type breadcrumb (eyebrow)

A small, uppercase, letter-spaced label placed above the title. Two segments separated by a middle dot.

```
ARCHITECTURE REPORT · ACME PLATFORM
RESEARCH & LEARNING · CONCEPT EXPLAINER
INCIDENT REPORT · SEV-2
IMPLEMENTATION PLAN · ACME WEB CLIENT
PR WRITE-UP · #312
```

Structure: `<p class="eyebrow">`. Style: `font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted);`. Inspired by demos like *Research & Learning · feature summary* in `14-research-feature-explainer.html`.

### Title block

A single `<h1>` carries the document title. Optional `<p class="subtitle">` underneath gives audience, scope, date, or product context — for example `"Acme web client · for engineering review · 2026-05-28"`. Keep the title under ~70 characters; let the subtitle carry context.

### Files-read / Evidence provenance

A small block listing the source files, docs, or configs that informed the document. Labeled "FILES READ" or "EVIDENCE". Renders inline near the top of the document — never sticky. Each entry is a monospace path with optional one-line summary. Lets a reader audit the document without reading the body.

```html
<aside class="evidence">
  <h2>Files read</h2>
  <ul>
    <li><code>src/auth/session.ts</code> — token verification</li>
    <li><code>config/limits.yaml</code> — per-route limits</li>
  </ul>
</aside>
```

Used in `14-research-feature-explainer.html` and the evidence index of architecture reports.

---

## 2. Summary & Stat Cards

### TL;DR block

A prominent summary placed just below the title block. One paragraph or three terse lines — a reader who reads *only* this should get the essential point.

Visual treatment: left border in the accent color (3–4px), subtle tinted background (`color-mix(in srgb, var(--accent) 6%, transparent)`), generous padding. Spans the full container width, not the body width.

### Stat summary cards

A row of 3–5 key counts or facts displayed as compact cards. Each card has a small label and a large value, optionally a delta or context line.

```html
<div class="stats">
  <div class="stat"><div class="value">14</div><div class="label">PRs merged</div><div class="delta">+3 vs wk10</div></div>
  <div class="stat"><div class="value">1</div><div class="label">Incidents</div><div class="delta">SEV-2 · 47m</div></div>
</div>
```

`.stats` is `display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 1rem;`. `.value` is the visually loudest item on the page above the fold. Inspired by the four-card row in `11-status-report.html`.

Common contents: PR/deploy counts, incident severity + duration, file/module counts, gap counts, effort estimates ("~2 weeks"), test coverage. Pick metrics that change with the document; static labels are wasted space.

---

## 3. Body Typography

- Body paragraphs: `max-width: 70ch` so lines stay readable.
- Headings step down clearly: `h1` (display) > `h2` (section) > `h3` (subsection) > `h4` (component). Avoid bold-only fake hierarchy.
- Monospace for code, file paths, identifiers, configuration values, command output. Use `<code>` inline and `<pre><code>` for blocks.
- Pull quotes / emphasized lines: italic or oversized with a colored left border, sparingly. Reserve for the most important sentence on the page.
- `<dl>` definition lists for FAQ and structured Q-and-A — they print and screen-read better than ad-hoc headings.

---

## 4. Code & Comparison

This is the densest section because code, comparisons, and diffs are where HTML earns its keep against markdown. Spatial structure matters.

### Inline code block

Standard fenced-style block with optional file-path header strip on top.

```html
<figure class="code">
  <figcaption><code>src/routes/search.ts</code></figcaption>
  <pre><code class="lang-ts">…code…</code></pre>
</figure>
```

Style: `pre` uses `overflow-x: auto`, monospace stack (`ui-monospace, "SF Mono", "JetBrains Mono", Consolas, monospace`), comfortable padding, no syntax-highlight library dependency unless the document is large enough to need it. The file-path strip uses a muted background and small monospace text.

### Multi-column code (config + impl + response)

Three short related snippets side-by-side — useful when one file's config drives another file's runtime behaviour and a third file shows the result. Used in `14-research-feature-explainer.html` (yaml config + ts route + HTTP response).

Lay out as a 3-column grid on desktop, single column on mobile and in print. Each column has its own caption strip. Keep each snippet short — if any column scrolls, the comparison breaks.

### Tabbed snippets

For longer alternatives or environment variants (`dev | staging | prod`, `limits.yaml | route.ts | client response`), use tabs. See §10. Print fallback: stack all tabs visible.

### Annotated diff (single-column with margin comments)

Single-column traditional diff with line numbers in a gutter, `+`/`-` prefixes, and context lines interspersed. Comments live *immediately under the relevant line*, each prefixed with a severity badge (§6).

```html
<div class="diff">
  <table>
    <tr class="ctx"><td class="ln">12</td><td class="sign"> </td><td>function handle(req) {</td></tr>
    <tr class="add"><td class="ln">13</td><td class="sign">+</td><td>  const limit = await getLimit(req);</td></tr>
    <tr class="del"><td class="ln">14</td><td class="sign">-</td><td>  const limit = 100;</td></tr>
  </table>
  <div class="diff-comment">
    <span class="badge badge-blocking">Blocking</span>
    <p><code>getLimit</code> is async — caller must <code>await</code>. Check line 31 too.</p>
  </div>
</div>
```

Color cues: `+` rows a light tinted background (`color-mix(in srgb, #4ade80 12%, transparent)`), `-` rows similarly with a red tint, context rows untinted. Line numbers in a muted gutter on the left. Inspired by `03-code-review-pr.html`.

### Before / After stacked panels

For teaching code changes or showing behavioural change. Two stacked sections labeled "Before" and "After" — *not* a unified diff. Each panel is its own card with equal height and internal scroll for long snippets. Stack on mobile and in print.

```html
<div class="ba">
  <section><h3>Before</h3><pre><code>…</code></pre></section>
  <section><h3>After</h3><pre><code>…</code></pre></section>
</div>
```

`.ba` is `display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;` collapsing to single column under ~720px. Highlight changed lines with subtle tint — not loud markers, because the teaching context already names the change. Used in `17-pr-writeup.html` and the lesson core of `code-change-explainer-html`.

### Multi-approach comparison

Three (or four) numbered approaches with a tradeoff matrix below each. Each approach card carries: number, title, sub-title/tagline, code snippet, Pro/Con two-column block, and a row of metric pills (e.g. *Bundle +0kb · Testability medium · Reuse low · SSR yes*). The document closes with a Recommendation section calling out the favoured approach and *why* the alternatives are deferred.

Inspired by `01-exploration-code-approaches.html`. Use this pattern any time the document is helping a reader choose between alternatives.

Layout: numbered cards stacked vertically (not side-by-side columns — code snippets need breathing room). The metric pill row is the visual anchor that lets the reader cross-compare without re-reading code.

### Versus table

When the comparison is about properties rather than code, use a small table: first column is `Aspect`, remaining columns are the alternatives. Used in `15-research-concept-explainer.html` (hash mod N vs consistent hashing across "keys moved", "hot-spot risk", "lookup cost", "used by").

---

## 5. Callouts & Glossary

### Concept callout box

Tightly structured boxed explainer for a single concept or syntactic feature. Five fields: Name, Minimal syntax, Semantic, Java parallel (or the audience's mental model), Gotcha. Rendered inline near the line of code that introduced the concept — proximity is the point.

```html
<aside class="concept-callout">
  <h4>Optional chaining <code>?.</code></h4>
  <pre><code>user?.profile?.name</code></pre>
  <dl>
    <dt>Semantic</dt><dd>Returns <code>undefined</code> as soon as any link is nullish…</dd>
    <dt>Java parallel</dt><dd>Like <code>Optional.ofNullable(...).map(...).orElse(null)</code>.</dd>
    <dt>Gotcha</dt><dd>Distinct from the optional-property <code>?</code> in type annotations.</dd>
  </dl>
</aside>
```

Style: 1px border, 3px left border in the accent colour, subtle tinted background, `break-inside: avoid` for print. The `<dl>` uses a two-column grid (`max-content 1fr`) so labels stack neatly. `code-change-explainer-html` is the canonical consumer of this pattern; its `references/concept-callouts.md` has the full specification including when to add callouts and starter HTML/CSS.

### Inline glossary (definition list)

End-of-document glossary or in-line term definitions. `<dl>` with `<dt>` terms and `<dd>` definitions. Each term should also be discoverable inline in the body via a hover-linked term (§12).

Used in `15-research-concept-explainer.html` for ring/node/arc/virtual-node/successor.

### Gotcha / Note callouts

Short inline notes, less structured than concept callouts. A small label (e.g. `★ Shortcut`, `⚠ Gotcha`, `★ Note`), followed by 1–2 sentences. Use sparingly — too many and they fade into the body.

---

## 6. Badges & Risk

### Status / severity badges

Small inline labels for status, confidence, severity, or ownership. Keep them compact: padded text with a colored background.

| Category | Suggested labels | Color cue |
| --- | --- | --- |
| Evidence (architecture reports) | `Source-backed`, `Inferred`, `Unclear`, `Gap` | green / amber / grey / red |
| Code review severity | `Blocking`, `Worth a look`, `Nitpick`, `Safe` | red / amber / grey / green |
| Risk level | `Low`, `Medium`, `High` | green / amber / red |
| Status | `Shipped`, `In progress`, `Blocked`, `Slipped` | green / blue / red / grey |
| Confidence | `High`, `Medium`, `Low` | green / amber / red |

Color discipline: badge backgrounds need at least ~12–15% opacity and borders at least ~45–50% opacity, otherwise green/amber/red wash out to indistinguishable pale tints. Verify visually before shipping. Inspired by `03-code-review-pr.html` (severity) and architecture-report evidence labelling.

```css
.badge { display: inline-flex; align-items: center; gap: 0.25rem; padding: 0.15rem 0.5rem;
  font-size: 0.75rem; font-weight: 600; border-radius: 4px; border: 1px solid; }
.badge-blocking { background: color-mix(in srgb, #dc2626 14%, transparent); color: #991b1b; border-color: color-mix(in srgb, #dc2626 50%, transparent); }
.badge-safe     { background: color-mix(in srgb, #16a34a 14%, transparent); color: #15803d; border-color: color-mix(in srgb, #16a34a 50%, transparent); }
.badge-worth    { background: color-mix(in srgb, #d97706 14%, transparent); color: #92400e; border-color: color-mix(in srgb, #d97706 50%, transparent); }
```

### Risk map

Color-coded file or module badges showing risk level. Two forms:

1. **Horizontal row of badges** — quick scan at the top of a section: `src/auth/session.ts (High) · src/api/router.ts (Med) · src/lib/util.ts (Low)`.
2. **Table** with columns: file/module, likelihood, impact, mitigation, severity badge.

Used in `03-code-review-pr.html` and `16-implementation-plan.html` (risk mitigation table with HIGH/MED/LOW severity column).

### Focus areas

For PR write-ups and reviews: a short list of "focus areas" highlighting risky spots, each entry containing a `file:line` reference, the specific failure mode it could cause, and what the author deliberately left out of scope. Inspired by `17-pr-writeup.html`.

---

## 7. Diagrams & Flow

### SVG architecture map

Inline SVG showing system runtime boundaries — frontend, backend, workers, queues, data stores, external integrations — and how they connect. Boxes for components, lines for connections, labels for protocol/data type.

Dimensions: aim for `720 × 320` to `960 × 480` viewport so the diagram fits inline without a horizontal scroll. Inline SVG with no external dependencies.

Palette discipline (from `10-svg-illustrations.html`):

- Restricted palette: a focus color (e.g. clay `#D97757`), a success/done color (e.g. olive `#788C5D`), and neutrals.
- Strokes: `1.5px` for neutral boxes, `2px` for emphasized containers (the thing currently in focus).
- All rectangles share the same corner radius (`r-md`, e.g. 6–8px).
- No gradients, no shadows. The diagram should be legible in monochrome.

Annotation placement:

- External labels next to the diagram in `12px sans-serif, gray-500`.
- Internal labels on shapes in monospace where the label is a file path, identifier, or shape name.

### Annotated flowchart

Process flow with three node types: **rectangles** for process steps, **diamonds** for decisions, **terminals** (pill or rounded) for endpoints. Arrows are labeled on decision branches (`pass` / `fail`, `healthy` / `canary-fails`). Inline annotations note duration estimates (e.g. `~2 min`, `90s`) and resource references (e.g. `.github/workflows/`).

Include a legend explaining: process node, decision node, terminal, success path, failure path. Color-coded states (legend on right or above).

Click-to-reveal on each node: clicking opens a detail panel adjacent to the diagram (not a modal) showing what runs at that step, expected duration, and where it can short-circuit. See §11.

Inspired by `13-flowchart-diagram.html`.

### Inline mockups / SVG figure sheet

For research and learning documents, embed 3–5 hand-drawn diagrams as a coordinated figure set. Each figure has a heading caption above (describing its documentation context: "For 'How jobs are picked up'") rather than a "Figure N" number. Optional download button below the SVG for re-use.

### Mermaid as fallback

Use only when graph/sequence/flowchart syntax suffices. Include via CDN (`https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js`) and one `<div class="mermaid">…</div>` per diagram. Mermaid loses the editorial polish of hand-built SVG — pick it deliberately, not as a default.

---

## 8. Sequential Flow

### Numbered step boxes

A horizontal row of numbered step boxes for workflows, pipelines, or implementation phases. Each box has a step number, short title, and 1-line description.

Add **visual connectors** between steps (arrow characters `→` or CSS `::after` shapes). Without connectors, side-by-side boxes read as a grid of peers, not a sequence. On mobile where the grid collapses to a single column, switch connectors from horizontal (`→`) to vertical (`↓`).

```html
<ol class="seq">
  <li><span class="n">1</span><h4>Receive request</h4><p>…</p></li>
  <li><span class="n">2</span><h4>Validate token</h4><p>…</p></li>
  <li><span class="n">3</span><h4>Apply rate limit</h4><p>…</p></li>
</ol>
```

Inspired by the request path walkthrough in `14-research-feature-explainer.html` and the step-by-step callstack walkthroughs throughout html-effectiveness.

### Numbered phase cards (for plans)

Vertically stacked numbered cards labelled `01`, `02`, `03` … each containing a week/day range (`Week 1 · Mon–Tue`), section title, and bullet list of deliverables. Package or module tags appear inline next to deliverables (`packages/db`, `apps/web`). Inspired by `16-implementation-plan.html`.

---

## 9. Timelines & Phase Cards

### Vertical timeline (incident, postmortem, rollout)

Left-aligned timestamps with bold milestone labels. Each entry is a discrete row marked with a timestamp (bold) and narrative description. Phase transitions are highlighted in heavier weight ("Impact starts", "Mitigated").

```html
<ol class="timeline">
  <li><time>14:02</time><p>Deploy to production starts.</p></li>
  <li><time>14:06</time><p><strong>Impact starts.</strong> 502 errors begin appearing on <code>/api</code>.</p></li>
  <li><time>14:49</time><p><strong>Mitigated.</strong> Rollback to previous deploy. Error rate returns to baseline.</p></li>
</ol>
```

For incident reports, surface SEV level, resolution status, and duration as inline metadata tags at the top: `SEV-2 · Resolved · Duration 47 min`. Impact summary directly below in a structured key/value block (`Requests failed (502): ~41,200 · Peak error rate: 21.4% · Users affected: ~2,300 workspaces`).

Inspired by `12-incident-report.html`.

### Horizontal timeline (rollout, status)

For weekly status and rollout plans: a horizontal timeline with date markers, milestone labels, package/module badges, and brief descriptions. Use color-coded dots for status (complete, in-progress, blocked).

---

## 10. Tabs

For comparing alternatives, environments, or subsystems (`limits.yaml | route.ts | client response`; `dev | staging | prod`).

```html
<div class="tabs" role="tablist">
  <button role="tab" aria-selected="true" aria-controls="t1" id="tab1">limits.yaml</button>
  <button role="tab" aria-selected="false" aria-controls="t2" id="tab2">route.ts</button>
  …
</div>
<section role="tabpanel" id="t1" aria-labelledby="tab1">…</section>
<section role="tabpanel" id="t2" aria-labelledby="tab2" hidden>…</section>
```

Requirements: keyboard navigable (arrow keys move focus, Enter activates), and degrade to stacked blocks under `@media print` so every panel is visible on a printed page. Tab labels short — file names, environment names, or one-word categories.

---

## 11. Click-to-Reveal

For flowcharts, step-by-step processes, and decision trees: clicking a step reveals detail in an *adjacent* panel (not a modal, not a tooltip). The detail panel shows what runs, relevant code, timing, failure paths, or config.

Two layouts work:

1. **Diagram + sidecar panel** — diagram on the left, detail panel on the right; clicking a node updates the panel.
2. **Stacked accordions** — for textual step-by-step, each step is a `<details>` element that expands inline.

```html
<details>
  <summary>Step 2 · Validate token</summary>
  <div>…detail…</div>
</details>
```

Print fallback: render all detail inline (`@media print { details[open] { display: block; } details > summary::marker { display: none; } }`).

Used in `13-flowchart-diagram.html` and `14-research-feature-explainer.html`.

---

## 12. Tooltips & Hover Glossary

Terms in the document body underlined or dotted-underlined. On hover, a tooltip or inline expansion shows the definition. Optionally collect all terms in a glossary section at the end (§5). Useful for technical documents with domain-specific vocabulary.

```html
<span class="term" tabindex="0">consistent hashing
  <span class="term-def" role="tooltip">A scheme that minimises key movement when nodes join or leave.</span>
</span>
```

Style: `text-decoration: underline dotted; cursor: help;`. The tooltip appears on `:hover` and `:focus-within` so it works for keyboard users. Print: render the definition inline in parentheses or omit if also present in the end glossary.

---

## 13. Copy Buttons

Code and config snippets readers will want to paste benefit from a small copy button in the top-right of the block. Pure HTML/JS, no clipboard libraries needed (`navigator.clipboard.writeText`).

```html
<figure class="code">
  <button class="copy" onclick="navigator.clipboard.writeText(this.nextElementSibling.querySelector('code').innerText)">Copy</button>
  <pre><code>…</code></pre>
</figure>
```

Place the button absolutely positioned in the top-right corner of the figure. After click, swap text to "Copied" for ~1.5s. Hide in print (`@media print { .copy { display: none; } }`).

---

## 14. Custom Interactive Controls

For live concept demos: a small SVG or canvas illustration plus controls (sliders, toggles, buttons) that mutate the illustration in real time. Show a feedback counter ("**4** nodes · **32** keys · 6 moved on last change") under the illustration.

Used in `15-research-concept-explainer.html` for consistent hashing — an interactive ring with controls for add/remove/reset nodes.

Constraints:

- Single static HTML, no build step.
- Controls keyboard-accessible.
- Print fallback: render a representative final state (the most-illustrative configuration) and a one-line caption explaining what the live version does.

---

## 15. Inline Mockups

When explaining a feature or UI change, render what it would look like directly in the document — built as HTML, not pasted screenshots, so it stays editable and consistent with the document's styling.

Label mockups `A` / `B` / `C` when comparing alternatives (`16-implementation-plan.html` uses Mockup A: thread inside card, Mockup B: sidebar digest). Each mockup is wrapped in a card with a small label and 1-line caption above.

For design-direction documents (`02-exploration-visual-designs.html`), stack mockup cards vertically — letter identifier + label + headline + supporting copy + CTA + a paragraph analysing the design rationale. Optionally include a light/dark surface toggle that swaps the mockup container background.

---

## 16. Tables

Use tables when the data has multiple comparable columns and rows: risks (file × likelihood × impact × mitigation), decisions (decision × evidence × tradeoff × related gaps), shipped items (PR × title × author × risk), versus (aspect × option A × option B), gaps (gap × evidence × severity).

Style cues:

- Header row sticky only when the table is long *and* the page is screen-only (no sticky in print).
- Zebra striping only when rows are visually similar; otherwise omit and rely on cell padding.
- Right-align numeric columns.
- Badges inside cells (§6) — do **not** combine `table-layout: fixed` with `white-space: nowrap` badges; either use auto layout or set `white-space: normal` on badges inside cells, otherwise badges overflow when columns get squeezed.

---

## 17. Design Tokens

Only relevant for design-system reference documents (`05-design-system.html`). Three token families:

- **Colors**: swatches with hex, semantic name, and role (`clay #D97757 — focus`, `slate #141413 — text`, `ivory #FAF9F5 — surface`).
- **Type scale**: each step labelled with `size / line-height / weight` and a sample. Display down through caption.
- **Spacing / radius / shadow**: numeric scale with visible boxes demonstrating each step.

Pair each token with a small live example (button states, badge variants, input states). Treat the page as the source of truth for the design system — the document is the canonical reference, not a screenshot of one.

---

## 18. Document Scaffolds

Common documents and the patterns they compose. Use these as starting compositions; the consumer skill provides the content.

### Architecture report

`§1 framing (ARCHITECTURE REPORT · <project>)` → `§2 TL;DR + stat cards (modules / flows traced / gaps found)` → executive summary → architecture map (`§7 SVG architecture map`) → major modules → data model + storage → external integrations → key flows (each with `§7 annotated flowchart` and `§4 multi-column code` or `§10 tabbed snippets`) → architecture decisions (cards with `§6 evidence badges`) → security controls (when in scope) → gaps and risks (`§6 risk map`) → recommendations → evidence index (`§1 files-read`).

Owned by `codebase-architecture-report` for content; this skill renders.

### Implementation plan

`§1 framing (IMPLEMENTATION PLAN · <project>)` → `§2 stat cards (effort estimate, surfaces touched, new tables, feature flag)` → goal/non-goals → `§8 numbered phase cards (01…0N)` with weekly breakdown → `§15 inline mockups` for UI changes → `§4 code blocks` for migrations/schemas → risk mitigation table (`§16 + §6 severity badges`) → testing strategy → rollout plan → open questions.

Inspired by `16-implementation-plan.html`.

### PR write-up

`§1 framing (PR WRITE-UP · #N)` → `§2 stat cards (files changed, +/- lines, branch)` → TL;DR → "What changed" file list (files in reading order, each with new/mod indicator + line counts + 1-sentence summary + why-it-matters) → `§4 before/after panels` for behavioural changes → focus areas (`§6`) with `file:line` references and failure-mode notes → "What I deliberately did not do" scope boundary → testing checklist (unit / integration / staging / manual) → phased rollout with success metrics → linked TOC at bottom.

Inspired by `17-pr-writeup.html`.

### Code review (annotated PR)

`§1 framing (PR REVIEW · #N)` → metadata (author, branch, change stats) → "What this PR does" summary → `§6 risk map` of files → for each file: `§4 annotated diff` with `§6 severity badges` on margin comments.

Inspired by `03-code-review-pr.html`.

### Research / feature explainer

`§1 framing (RESEARCH & LEARNING · <topic>)` → "On this page" navigation list → `§1 files-read` provenance → TL;DR → request path / step-by-step (`§8 sequential flow`) → `§4 multi-column code` (config + impl + response) → gotchas + FAQ (`§5 callouts`, `<dl>` definition lists).

Inspired by `14-research-feature-explainer.html`.

### Concept explainer

`§1 framing (RESEARCH & LEARNING · concept explainer)` → large title with optional wordplay → `§14 live interactive demo` (SVG + controls + counter) → `§4 versus table` comparing alternative approaches → `§5 inline glossary` of domain terms.

Inspired by `15-research-concept-explainer.html`.

### Status report

`§1 framing (ENGINEERING STATUS · Week N)` with period subtitle → `§2 stat cards` (PRs merged, deploys, incidents, flaky tests fixed) with delta vs previous period → Highlights (narrative bullets) → Shipped (`§16 table` PR × title × author × risk) → Velocity (text-based chart or sparkline) → Carryover (In review / Blocked / Slipped subsections).

Inspired by `11-status-report.html`.

### Incident report

`§1 framing (INCIDENT REPORT · SEV-N)` with inline metadata tags (`Resolved · Duration 47m`) → impact summary (`§2`-style structured key/value rows) → `§9 vertical timeline` of events → root cause (narrative followed by `§4 code diff` showing the offending change) → mitigation taken → action items.

Inspired by `12-incident-report.html`.

### Code-change explainer (teaching document)

Owned by `code-change-explainer-html` for content. Composition: `§1 framing` → audience + summary → status/verification strip → concept map (TOC of every concept taught) → Lessons (one per change: title + Java equivalent + concept + Java mental model `§5 callout` + strategy + `§4 before/after` + line-by-line walkthrough + `§5 concept callouts` for non-trivial syntax + gotchas + verification) → optimised end-to-end flow → end-to-end verification → remaining work → files to read next.

`code-change-explainer-html` extends this skill: it defines the lesson structure; this skill renders every element.
