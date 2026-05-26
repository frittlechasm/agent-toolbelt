---
name: html-document
description: Create or refine standalone HTML documents for human reading, printing, and PDF export. Use when generating, editing, beautifying, or converting .html reports, explainers, proposals, plans, memos, technical summaries, PR write-ups, incident timelines, code-change explainers, or any document-like HTML artifact. Also use whenever another skill (e.g. `codebase-architecture-report`, `code-change-explainer-html`) needs to emit HTML — it owns presentation for the whole system.
---

# HTML Document

Create standalone `.html` documents meant to be read, shared, printed, or exported as PDF. The bar to clear, set by [thariqs.github.io/html-effectiveness](https://thariqs.github.io/html-effectiveness/): *"trade a document you'd skim for one you'd actually read."* Diffs, call graphs, comparisons, flows, and timelines are **spatial** information — markdown flattens them. HTML preserves the structure that makes them readable.

## Boundaries

- For standalone explanatory `.html` documents: reports, explainers, proposals, implementation plans, architecture notes, memos, onboarding docs, RFP/RFI responses, status reports, incident timelines, PR write-ups, code-teaching documents, design-system references, research explainers.
- Not for web app screens, dashboards, landing pages, or product UI — use `frontend-design` for those.
- Standalone or downstream: this skill owns presentation. The calling skill owns substance.

## How this skill relates to others

This skill sits between three others. Hold the contract explicit so the right skill makes each decision.

- **Consult `frontend-design`** as the design-thinking foundation *before* laying out anything non-trivial. Use it to pick typography, color, spatial composition, and motion craft so the output is intentional and designed, not generic AI aesthetic. Then constrain the result to a *document* aesthetic — editorial, restrained, readable across long form, printable. The output must not feel like a landing page or product UI even though it borrows the same craft. Do not modify `frontend-design` itself; treat it as upstream guidance.
- **Called by `codebase-architecture-report`** and **`code-change-explainer-html`** (and any future skill that emits HTML). Those skills decide **what** goes on the page — sections, evidence, lessons, code, callouts, recommendations. This skill decides **how** every element is rendered, laid out, highlighted, and made interactive. When you act as the downstream skill, never reinvent presentation choices documented here.

In short: `frontend-design` → `html-document` → consumer skill. Each layer constrains the one below.

## Core Principle

Every element earns its place by clarifying meaning. No decorative heroes, no stock images, no gradients for their own sake. If removing an element would not reduce understanding, remove it. Prefer spatial layouts that reveal relationships (side-by-side panels, multi-column grids, annotated diagrams, timelines) over linear prose wherever the spatial structure carries real information.

## Styling and CSS

Write self-contained editorial CSS in a `<style>` block. Do not use Tailwind, Bootstrap, or other utility/component frameworks — they produce web-app-feeling output, not document-feeling output.

**Design language**: when the document is generated for a specific project, match that project's existing palette, fonts, and spacing rhythm. When no project context exists, default to:

- Clean white or very light gray background
- High-contrast text (near-black on near-white)
- One accent color for links, badges, and highlights
- System font stack for body (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`)
- Optional serif for headings when an editorial tone fits
- Generous whitespace, readable line lengths (60–80ch max for body paragraphs)

**Typography**: restrained and readable for long form. Strong heading hierarchy. Monospace for code, file paths, and config values.

**Width constraints**: apply `max-width` line-length limits only to body text paragraphs, not to header-area elements. The title, subtitle, TL;DR block, stat cards, TOC, and tables should span the full document container — constraining them creates a visible misalignment with everything below.

## Element Catalog

Every element pattern — code blocks, diffs, callouts, badges, comparison panels, diagrams, timelines, interactive controls, mockups, design tokens, and the document scaffolds that compose them — lives in `references/elements.md`. Read it before laying out anything non-trivial. Each entry maps back to a working demo on html-effectiveness.

Quick navigation by need:

| When the content involves... | Read in `references/elements.md` |
| --- | --- |
| Header, breadcrumb, audience, provenance ("Files read") | §1 Framing |
| Summary block, key counts/metrics at the top | §2 Summary & Stat Cards |
| Body prose, line length, pull quotes | §3 Body Typography |
| Code, diffs, before/after, multi-approach comparison | §4 Code & Comparison |
| Concept callouts, glossary, gotchas | §5 Callouts & Glossary |
| Evidence labels, severity, risk maps | §6 Badges & Risk |
| Architecture maps, annotated flowcharts, SVG figures | §7 Diagrams & Flow |
| Numbered step-by-step walkthroughs | §8 Sequential Flow |
| Plans, rollouts, incidents | §9 Timelines & Phase Cards |
| Multi-file snippets, environment switching | §10 Tabs |
| Step-by-step reveal, decision trees, hot-path detail | §11 Click-to-Reveal |
| Domain vocabulary inline | §12 Tooltips & Hover Glossary |
| Snippets readers will copy | §13 Copy Buttons |
| Live concept demos with controls | §14 Custom Interactive Controls |
| What a UI/feature would look like | §15 Inline Mockups |
| Structured rows of data | §16 Tables |
| Color/type/spacing tokens (for design-system docs) | §17 Design Tokens |
| Composing the whole document | §18 Document Scaffolds |

## Diagrams and Visuals

**SVG-first** for architecture maps, flow diagrams, request paths, and annotated flowcharts — hand-built diagrams produce better results than Mermaid when the diagram needs annotation, hot-path emphasis, click-to-reveal detail, or editorial polish.

**Mermaid as fallback** via CDN (`https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js`) only when graph/sequence/flowchart syntax suffices and hand-building would not add value.

Do not include stock-like images or decorative illustrations. Every image reveals a real system, state, artifact, or domain concept.

Concrete dimensions, palette discipline, stroke weights, annotation placement, and click-to-reveal patterns are in `references/elements.md` §7.

## Interaction Requirements

Add interactivity only when it improves explanation. Catalogued patterns in `references/elements.md`:

- tabs (§10) for comparing alternatives, environments, or subsystems
- accordions (§11) for evidence, logs, detailed references, or appendices
- toggles for current-vs-proposed or summary-vs-detail
- click-to-reveal (§11) for step-by-step flows or hot-path detail
- copy buttons (§13) for code/config snippets
- hover tooltips (§12) for glossary terms
- custom controls (§14) for live concept demos

All interactions must:

- Work in a single static HTML file with no build step
- Be keyboard-accessible
- Degrade cleanly for print (interactive content rendered inline or expanded)

## Document Flow

This skill does not dictate content structure — the consumer skill (or the user's prompt) owns that. Ensure:

- A clear narrative arc from context through evidence to conclusion.
- The most useful conclusion appears early; progressively disclose detail beneath it.
- Sections flow logically — no forward references that force backtracking.
- Long documents include a non-sticky table of contents near the top.

For commonly composed documents — architecture report, implementation plan, PR write-up, incident timeline, research/feature explainer, code-change explainer, status report — see `references/elements.md` §18 Document Scaffolds.

## Layout

- Start with document type breadcrumb, title, and context (audience, date, scope).
- Compact, readable sections with strong headings.
- Cards for repeated items: risks, decisions, controls, evidence entries.
- Multi-column grids for repeated cards: if an odd item count leaves an orphan, span it full width (`grid-column: 1 / -1` on `:last-child:nth-child(odd)`) rather than leaving empty space.
- No landing-page hero sections.
- Responsive: readable on mobile, no text overflow.
- **Tables with badges/tags**: do not combine `table-layout: fixed` with `white-space: nowrap` tags inside table cells. Either use auto layout or override tags inside tables with `white-space: normal` so they wrap within their cell.

## Print and PDF

- `@page` with sensible margins.
- `break-inside: avoid` on cards, tables, diagrams, decision blocks.
- Backgrounds and borders legible without relying on color alone.
- No fixed-position elements that overlap printed content.
- Interactive sections expanded or rendered inline for print via `@media print`.

## Quality Checklist

Before finishing:

- The first screen explains the document type, title, and audience.
- The section order tells a coherent story.
- Spatial elements (diffs, comparisons, diagrams, timelines) are used wherever the relationship between items carries real information.
- Decisions include why, alternatives, and tradeoffs.
- Evidence is visible without overwhelming the narrative.
- Interactive elements clarify, not decorate.
- The document works as a single standalone `.html` file.
- It is readable on mobile.
- It is printable/PDF-friendly.
- Diagrams render without console errors.

## Verification

When practical, open the HTML in a browser and inspect at desktop and mobile widths. Verify diagrams render, interactive elements work, and there are no console-blocking errors.

## Example Triggers

- "Generate an HTML document I can send as a PDF."
- "Refine this HTML report and make it easier to understand."
- "Add diagrams and interactive explanations to this architecture document."
- "Beautify this client-facing technical report."
- "Convert this markdown into a polished standalone HTML document."
- "Create an HTML explainer for how rate limiting works in this repo."
- "Write up this PR as a single self-contained HTML page."
- "Turn this incident postmortem into a shareable HTML timeline."
