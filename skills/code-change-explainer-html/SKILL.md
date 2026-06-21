---
name: code-change-explainer-html
description: 'Create standalone HTML that teaches what a code change does, line by line — anchored to a comparison language the reader already knows, with callouts on the non-obvious syntax of the language the code is written in. Use to *teach* what changed and why (not to track work): refactors, before/after walkthroughs, PR explainers, or understanding what an AI agent changed in an unfamiliar language. Triggers: "explain this code change", "walk me through what the agent did", "explain this in terms of a language I know", "implementation explainer". Extends `html-document` for presentation.'
---

# Code Change Explainer HTML

Build a standalone `.html` document that **teaches** what changed in code, line by line. Comprehension is the goal — a reader should finish each lesson able to re-derive the change. Preserve the code exactly as it was changed — whether pasted in or read from the diff; your job is to expand the explanation around it, not to alter the code.

Two languages are in play in every document, and keeping them straight is the whole job:

- **Target language** — the language the code is *written in* (Swift, TypeScript, Rust, …). You **explain its non-obvious syntax**.
- **Comparison language** — the language the reader is *most fluent in*. You **map the target back to it** as the mental model, but you **never explain the comparison language's own syntax** — the reader already knows it.

## Comparison language (resolve this first)

Before drafting, decide which language to anchor explanations to, in this strict priority:

1. **Prompt.** If the request names the language to compare with — "I know Python", "explain this in C# terms", "our team comes from Kotlin" — use that. The prompt always wins.
2. **Memory.** If the prompt is silent and your environment has a stored preference (a memory recording the user's most-familiar language), use that.
3. **Ask.** Only when *neither* the prompt nor memory specifies, ask the user — e.g. *"Which language are you most familiar with? I'll explain the change in those terms."* — and wait for the answer before drafting. Do not guess a default.

After resolving, **record the choice in persistent memory** (if supported) so future documents skip the question. A one-off language named in the prompt overrides memory for that document only — don't silently overwrite a stored general preference; when in doubt, keep it and ask.

Throughout this skill, *"the comparison language"* means whatever was resolved here. The examples below happen to use various languages; substitute the resolved one.

## Boundaries and dependencies

- This skill owns **what** goes on the page: the lessons, the comparison-language mental model, the choice of which target-language concepts deserve callouts, and the line-by-line walkthroughs.
- This skill does **not** own how the page is rendered. Presentation — fonts, spacing, code-block styling, callout boxes, before/after panel layout, badges, print rules — lives in [`html-document`](../html-document/SKILL.md). Read its `references/elements.md` before drafting. Sections are referenced by name (not number) so they survive renumbering — the ones this skill leans on:
  - **Code extensions** — before/after panels, annotated diffs, multi-column code
  - **Callouts** — the concept callout box this skill leans on
  - **Badges** — severity, confidence
  - **Document scaffolds** — the *Code-change explainer* scaffold
- Always invoke `html-document` to render the final `.html`. Do not redefine styling here that already exists there.

Read these references before drafting:

- How to surface the **target language's** non-obvious syntax — the category sweep that works for *any* target language (TypeScript, Python, Go, Rust, Swift, Kotlin, C#, Ruby, …) → `references/any-language.md`. There are deliberately no per-language cheat-sheets: a fixed list would surface the same callouts every time, whereas the goal is to react to the non-obvious constructs in *this* code so the reader learns the language's implications over time.
- Callout HTML structure and the dedup / scope rules → `references/concept-callouts.md`

## Ingesting the change set

The usual trigger is *"explain what the agent changed this session,"* not a hand-picked snippet — so start from the real changes, then shape them into lessons.

1. **Source the diff.** Prefer the working tree over anything pasted: `git diff`, `git diff --staged`, or a diff against the commit the session started from. Read the actual before/after from the repo so the snippets are real. Fall back to pasted code only when there is no repo to diff.
2. **Triage signal from noise.** Skip lockfiles, generated/vendored code, and pure formatting, whitespace, or import-reordering churn — they teach nothing. Do not drop them *silently*: note what you skipped in one line ("18 files of generated API client — not taught") so the reader knows the document's coverage instead of assuming it is exhaustive.
3. **Group by concept, not by file.** One concept (introducing a repository layer, switching to async) often spans several files; one file often bundles several concepts. Lessons track concepts — keep the one-Lesson-per-concept rule from *Lesson Anatomy*, sourced across files.
4. **Order by architecture, not by file order.** Sequence the lessons along the data / dependency flow — entry point → core logic → edges (storage, network, UI) — so the reader rebuilds the *system* in their head, not the alphabetical file list. The concept map at the top should reflect this ordering.

## The Reader

Fluent in the **comparison language** and its idioms; has *not* internalised the **target** language's — spell those out. If you catch yourself writing "as you know, in <target language> …", reframe: the reader does *not* know the target language; that is why the document exists.

## Reader-first teaching rules

Every Lesson must be understandable before code. Start with the practical problem, before comparison-language equivalents, architecture terms, pattern names, or trust-badge commentary. Define target/platform terms before relying on them. Use a 3–6 step **Before The Fix** timeline for event-driven, async, UI, cross-process, distributed, or lifecycle behavior. For related sub-fixes, add subheads under **What Changed** or split into separate Lessons.

## Lesson Anatomy

**One Lesson per distinct concept, not one per diff.** Split multi-concept changes into short focused Lessons; collapse only when the change teaches one idea. Do not create Lessons for constructs trivial to the comparison-language reader. When Lessons interlock, add the end-to-end flow section.

Use these visible headings inside each Lesson; keep the names reader-facing and skip only when truly irrelevant:

1. **Title and Trust** — title plus one badge: `Idiomatic`, `Works, but unusual`, or `Risky`. Badge and **Target And Platform Gotchas** must agree.
2. **The Bug In Plain English** — 2–4 plain sentences; first explanatory paragraph starts with the practical problem.
3. **Terms You Need** — 2–4 bullets defining target/platform vocabulary.
4. **Before The Fix** — timeline for behavior/lifecycle bugs; otherwise 1–3 old-behavior bullets.
5. **What Changed** — short bullets; use subheads for compound fixes.
6. **Why It Matters** — user-visible/runtime/safety effect before any architecture framing.
7. **Explain Like I'm Five** — optional; only for genuinely hard concepts, 2–4 jargon-free sentences in a callout.
8. **Mental Model** — closest comparison-language analogue and concrete mapping callout.
9. **Code Comparison** — before/after panels from `html-document` (**Code extensions**), never a unified diff.
10. **Line-By-Line Walkthrough** — the heart:

For every meaningful line of the After code (group boilerplate together; never skip silently):

- **Quote** the line in monospace.
- **What it says**: literal reading of tokens.
- **What it does**: behavioural effect at runtime — value type, side effects.
- **Why this way**: why this construct over alternatives — the author's call.

Use an ordered list of cards or a `<dl>` definition list — not a wide table. Lean on the base typography in `html-document`'s SKILL.md rather than inventing new styling.
11. **Target-Language Callouts** — non-trivial target syntax only; follow `concept-callouts.md`, never teach the comparison language, never repeat a construct.
12. **Target And Platform Gotchas** — actual language/platform/runtime pitfalls touched by this code; feed real hazards into the trust badge.

## Style

- Pair-programming voice anchored to the comparison language: "Notice that …", "If you've written a service in <comparison language>, this is the same idea."
- Tie every explanation to a quoted snippet — no abstract lectures.
- Name patterns (Adapter, Strategy, Repository, Visitor, Builder) and tie them to the comparison language.
- Explain the *why* in plain language before architecture framing.
- Prefer short sentences; if a sentence needs several target/platform terms, split it and define them first.

## Document Structure

1. Title, audience (state the comparison language), summary — including a one-line **coverage note**: what was taught vs. what was skipped as noise (generated files, lockfiles, formatting).
2. Status / scope strip.
3. Concept map — outline of every concept taught (TOC + learning contract).
4. Lessons.
5. Optimised flow / end-to-end runtime path (when changes interlock).
6. Remaining work.
7. Files to read next.

Compose using the *Code-change explainer* scaffold in `html-document` `references/elements.md` (**Document scaffolds**).

## Quality Checklist

- Comparison language resolved (prompt → memory → ask) and recorded in memory when newly learned.
- Change set sourced from the real diff; noise (generated / lockfiles / formatting) noted in the coverage line, not silently dropped.
- Lessons split one-per-concept and ordered along data flow; interlocking Lessons get end-to-end flow.
- Every Lesson uses the standard headings, starts with the practical problem, defines terms before use, and has a specific Mental Model plus justified trust badge.
- **What Changed** and **Why It Matters** explain the fix plainly; agent-change inferences are labelled and questionable choices called out.
- Gotchas cover platform / runtime / framework footguns, not only language syntax.
- Two hard rules held: no comparison-language syntax explained (it appears only as the parallel), and no construct taught twice.
- Every line of in-scope After code is accounted for; "Explain Like I'm Five" only on genuinely hard concepts, never restating Concept/Mental Model.
- Presentation fully deferred to `html-document` (before/after panels, callouts, badges, print).
