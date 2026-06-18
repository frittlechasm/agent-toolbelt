---
name: html-document
description: Create or refine standalone HTML documents for human reading, printing, and PDF export. Use when generating, editing, beautifying, or converting .html reports, explainers, proposals, plans, memos, technical summaries, PR write-ups, incident timelines, code-change explainers, or any document-like HTML artifact. Also use whenever another skill needs to emit HTML — this skill owns presentation. Trigger on any request for polished HTML output, document generation, or "make this into a nice HTML page."
---

# HTML Document

Generate standalone `.html` files: single column, dark, minimal, the same base CSS for every document — no project-specific styling. When the user explicitly asks for PDF-ready, print-ready, page-perfect, deck-style, slide-style, or fixed-page output, switch to the opt-in PDF-Ready Mode (`references/pdf-ready.md`). Wanting to *export, save, or print to PDF* is **not** that request — a flowing document already produces a clean PDF through the browser; stay in the default mode unless the user wants each page deliberately composed.

## Scope

Standalone `.html` documents: reports, explainers, proposals, plans, memos, architecture notes, PR write-ups, incident timelines, status reports, research explainers, code-teaching documents. Not for web apps, dashboards, marketing pages, or product UI — those want a distinctive, decorative aesthetic, which is the opposite of this skill's restrained document style; use `frontend-design` for them instead.

## Base CSS

Single `<style>` block in `<head>`. No frameworks, no external stylesheets, no web fonts, no CDN CSS.

```css
:root {
  --bg: #000;
  --text: #f5f5f5;
  --muted: #b7b7b7;
  --faint: #777;
  --line: #2a2a2a;
  --code-bg: #090909;
  --code: #d8d8d8;
  --link: #8ab4ff;
  --sans: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
}

* { box-sizing: border-box; }
html { background: var(--bg); color: var(--text); font-family: var(--sans); }
body { margin: 0; background: var(--bg); line-height: 1.62; }
.page { width: min(920px, calc(100vw - 40px)); margin: 0 auto; padding: 56px 0 76px; }

h1, h2, h3, h4, h5, h6, p { margin-top: 0; }
h1 { margin-bottom: 18px; font-size: 68px; line-height: 0.98; }
h2 { margin: 56px 0 14px; padding-top: 28px; border-top: 1px solid var(--line); font-size: 26px; line-height: 1.2; }
h3 { margin: 30px 0 8px; font-size: 17px; }
h4, h5, h6 { margin: 24px 0 8px; font-size: 16px; }

p { color: var(--muted); font-size: 18px; }
h1 + p { max-width: 800px; color: var(--text); font-size: 22px; line-height: 1.45; }
ul, ol { margin: 0 0 20px; padding-left: 24px; color: var(--muted); font-size: 18px; }
li + li { margin-top: 8px; }
strong { color: var(--text); }

code { color: var(--code); font-family: var(--mono); font-size: 0.93em; }
pre { margin: 20px 0; padding: 18px; border: 1px solid var(--line);
  background: var(--code-bg); color: var(--code); font-family: var(--mono); font-size: 14px; line-height: 1.55;
  white-space: pre-wrap; overflow-wrap: anywhere; }
pre code { font-size: inherit; }

img { max-width: 100%; height: auto; }

blockquote { margin: 28px 0; padding: 0 0 0 18px; border-left: 2px solid var(--text); }
blockquote p { color: var(--text); }
a { color: var(--link); }

@media (max-width: 640px) {
  .page { width: min(100vw - 28px, 920px); padding-top: 42px; }
  h1 { font-size: 42px; }
  h1 + p { font-size: 20px; }
  p, ul, ol { font-size: 17px; }
}
```

Use this CSS verbatim. Extend it only when the document needs elements not covered by base HTML (diffs, badges, stat cards, diagrams) — see `references/elements.md`.

## Design rules

- Dark only. No light mode, no theme toggle.
- System fonts only. Zero downloads.
- No decoration — no gradients, no shadows, no border-radius on containers, no images unless informational.
- No syntax highlighting. Code is monochrome `var(--code)` on `var(--code-bg)`.
- Sections separated by `h2` border-top lines. Not cards, not boxes, not background changes.
- Body text is `var(--muted)` (gray). Headings and `<strong>` are `var(--text)` (white). Hierarchy through color contrast.
- The first `<p>` after `<h1>` is the subtitle — larger, white, max-width 800px.
- `var(--faint)` for metadata, timestamps, and de-emphasized labels.
- Single breakpoint at 640px.

## Layout

- `<main class="page">` wraps all content: single column, 920px max. Start with `<h1>`; the first `<p>` is the subtitle (audience, date, scope). Content flows vertically — no sidebar, sticky nav, or table of contents.
- **The page never scrolls horizontally** down to ~320px (side panel, in-app browser). Three responses, in order of preference:
  - **Side-by-side panels stack.** Before/after and multi-column code collapse to one column when the columns won't fit, driven by the container's real width (`repeat(auto-fit, minmax(min(100%, Nrem), 1fr))`) rather than a viewport breakpoint — so a narrow desktop window stacks too.
  - **Code wraps.** Long lines reflow (`white-space: pre-wrap; overflow-wrap: anywhere`); grid/flex parents need `min-width: 0` so the panel can shrink. The fallback once a column is itself narrow.
  - **Images and art scroll.** What can't reflow without losing meaning — images, SVG diagrams, wide data tables — keeps its size and scrolls inside its own `.scroll-x` block, never widening the page.

  See `references/elements.md`.

## Extended patterns

For elements beyond base HTML — diffs, badges, stat cards, timelines, comparison panels, tabs, accordions, copy buttons — read `references/elements.md`. For diagrams (hand-SVG or themed Mermaid), read `references/diagrams.md` directly. Only add these when the content needs them.

## Print and PDF

Default documents are flowing HTML: they print cleanly, but browser pagination decides where page breaks fall.

```css
@media print {
  :root { --bg: #fff; --text: #111; --muted: #555; --faint: #888; --line: #ddd; --code-bg: #f5f5f5; --code: #333; --link: #1a5fb4; }
  .page { width: 100%; padding: 0; }
}
@page { margin: 2cm; }
```

`break-inside: avoid` on `pre`, tables, and any grouped content. No fixed-position elements.

## PDF-Ready Mode

When the user explicitly asks for PDF-ready, print-ready, page-perfect, deck-style, slide-style, or fixed-page output, read `references/pdf-ready.md` and follow it — fixed page geometry, one job per page, composed to fit, verified with an `agent-browser` check. Not for ordinary flowing documents, and **not** merely because the user mentions exporting/saving/printing to PDF — forcing short content into fixed pages leaves large empty gaps. When unsure, prefer the default flowing mode; it prints and exports to PDF cleanly on its own.

## Checklist

- Single standalone `.html` file, base CSS verbatim.
- `<h1>` and subtitle visible on first screen; sections use `<h2>` (carries the border-top separator).
- Readable on mobile; no horizontal *page* scroll to ~320px (panels stack, code wraps, media scrolls in `.scroll-x`).
- Printable.
- PDF-ready mode, if requested (`references/pdf-ready.md`): fixed-height `.pdf-page` sections, declared paper size, passing `agent-browser` overflow check, screenshot inspection.
