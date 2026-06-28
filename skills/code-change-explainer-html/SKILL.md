---
name: code-change-explainer-html
description: 'Create standalone HTML that goes over the code changes done in a commit or session, line by line — anchored to a comparison language the reader already knows, with callouts on the non-obvious syntax of the language the code is written in. Use to *teach* what changed and why (not to track work): refactors, before/after walkthroughs, PR explainers, or understanding what an AI agent changed in an unfamiliar language. Triggers: "explain this code change", "walk me through what the agent did", "explain this in terms of a language I know", "implementation explainer". Extends `html-document` for presentation.'
---

# Code Change Explainer HTML

Build a standalone `.html` document that **teaches** what changed in code and why, line by line. Keep the explanation as simple as possible. A reader should be able to understand each lesson with ease. Preserve the code exactly as it was changed; your job is to expand the explanation around it, not to alter the code.

Two languages are in play in every document:
- **Target language** — the language the code is *written in* (Swift, TypeScript, Rust, …). You **explain its non-obvious syntax**.
- **Comparison language** — the language the reader is *most fluent in*. You **map the target back to it** for comparison. You **never explain the comparison language's own syntax** — the reader already knows it.

## Comparison language (resolve this first)

Before drafting, decide which language to anchor explanations to, in this strict priority:

1. **Prompt.** If the request names the language to compare with — "I know Python", "explain this in C# terms", "our team comes from Kotlin" — use that. The prompt always wins.
2. **Memory.** If the prompt is silent and your environment has a stored preference (a memory recording the user's most-familiar language), use that.
3. **Ask.** Only when *neither* the prompt nor memory specifies, collect the comparison language with `request_user_input` or the environment's equivalent user-input tool when available; otherwise ask a concise question and wait. Do not guess a default.

After resolving, **record the choice in persistent memory** (if supported) so future documents skip the question. A one-off language named in the prompt overrides memory for that document only — don't silently overwrite a stored general preference; when in doubt, keep it and ask.

Throughout this skill, *"the comparison language"* means whatever was resolved here. The examples below happen to use various languages; substitute the resolved one.

## Boundaries and dependencies

- This skill owns **what** goes on the page: the lessons, the comparison-language mental model, the choice of which target-language concepts deserve callouts, and the line-by-line walkthroughs.
- This skill does **not** own how the page is rendered.
- Invoke the `html-document` skill to render the final `.html`. Do not redefine styling here that already exists there.

## Ingesting the change set

The usual trigger is *"explain what the agent changed this session,"* not a hand-picked snippet — so start from the real changes, then shape them into lessons.

1. **Source the diff.** Prefer the working tree over anything pasted: `git diff`, `git diff --staged`, or a diff against the commit the session started from. Read the actual before/after from the repo so the snippets are real. Fall back to pasted code only when there is no repo to diff.
2. **Triage signal from noise.** Skip lockfiles, generated/vendored code, and pure formatting, whitespace, or import-reordering churn — they teach nothing. Do not drop them *silently*: note what you skipped in one line ("18 files of generated API client — not taught") so the reader knows the document's coverage instead of assuming it is exhaustive.
3. **Group by concept, not by file.** One concept (introducing a repository layer, switching to async) often spans several files; one file often bundles several concepts. Lessons track concepts — keep the one-Lesson-per-concept rule from *Lesson Anatomy*, sourced across files.
4. **Order by architecture, not by file order.** Sequence the lessons along the data / dependency flow — entry point → core logic → edges (storage, network, UI) — so the reader rebuilds the *system* in their head, not the alphabetical file list. The concept map at the top should reflect this ordering.

## Lesson Anatomy

**One Lesson per distinct concept, not one per diff.** Split multi-concept changes into short focused Lessons; collapse only when the change teaches one idea. Do not create Lessons for constructs trivial to the comparison-language reader. When Lessons interlock, add the end-to-end flow section.

Use these visible headings inside each Lesson; keep the names reader-facing and skip only when truly irrelevant:

1. **Title and Trust** — title plus one badge: `Idiomatic`, `Works, but unusual`, or `Risky`. Choose the badge from the actual target-language/platform behavior explained in the Lesson; if the code has a gotcha, name it in **Terms You Need** or the relevant syntax callout.
2. **The Change In Plain English** — A very simple explanation of what this change does and why it was needed. When the change fixes a bug, title this *"The Bug In Plain English"* and state the bug and what triggered it; for a feature or refactor, describe the motivation instead. Match the heading to the actual change — don't force bug framing onto non-bug work.
3. **Terms You Need** — brief definitions for target/platform vocabulary the reader needs before the code.
4. **Before** — A very simple explanation of the old behavior or code and its implications (for a bug, what went wrong; for a refactor, the prior shape). Title it *"Before The Fix"* only when the change is a fix. Use a 3–6 step timeline for event-driven, async, UI, cross-process, distributed, or lifecycle changes.
5. **What Changed** — short bullets; use subheads for compound fixes.
6. **Why It Matters** — the user-visible, runtime, or safety effect before any architecture framing.
7. **Code Comparison** — before/after panels from `html-document` (**Code extensions**), never a unified diff.
8. **Line-By-Line Walkthrough** — the heart:

For focused snippets, explain every meaningful line of the After code. For larger changes, group boilerplate and repeated patterns so the document teaches the change without becoming a transcript; call out what was grouped.

- **Quote** the line in monospace.
- Explain the target-language syntax by breaking the line into meaningful pieces.
- Compare the line with the comparison language.

9. **Architecture Decision** (optional): Name the design choice, explain the simpler alternative, explain why this change chose the current shape, and call out the tradeoff. Mention patterns such as Adapter, Strategy, Repository, Visitor, or Builder only when they genuinely clarify the decision.

## Non-obvious target-language syntax

Explain target-language constructs that are not a 1:1 match for the comparison language. Do not explain the comparison language itself.

Add a callout when the target code uses:

- **Absence / null** — optionals, `nil`/`null`/`None`, `?.`, `?:`, `!!`, `guard let`, `if let`, force unwraps.
- **Equality & identity** — value vs reference equality, operator overloading, structural vs nominal comparison.
- **Mutability & binding** — `val`/`var`/`let`/`const`, immutable-by-default rules, shadowing, binding vs contained value.
- **Functions & closures** — lambda syntax, trailing closures, capture semantics, partial application, named/default/variadic parameters.
- **Async & concurrency** — async/await, futures, coroutines, actors, structured concurrency, eager vs lazy async behavior.
- **Error model** — checked/unchecked exceptions, result types, `try`/`throws`/`rethrows`, optional-returning failures.
- **Type-system surprises** — inference, generics and variance, unions/intersections/sum types, structural vs nominal typing, extension methods.
- **Syntactic sugar** — destructuring, pattern matching, string interpolation, ranges, comprehensions, operator overloading, property syntax.
- **Memory / ownership** — value vs reference types, copy semantics, ownership/borrowing, ARC/ref-counting, RAII, `defer`-style cleanup.
- **Metaprogramming** — annotations, attributes, macros, reflection, decorators, compile-time vs runtime behavior.
- **Platform / runtime / framework behavior** — event loops, render/effect timing, ORM lazy loading, thread/UI-thread constraints, retain cycles, library API contracts.

Skip constructs that mean the same thing in the comparison language: plain `if`, plain `for`, assignment, direct method calls, and already-explained constructs. Teach each construct once, near its first meaningful line, then refer back later.

Each callout should have five fields: **Name**, **Minimal syntax**, **Semantic**, **Parallel**, and **Gotcha**. Open the Parallel field with the comparison language ("In Python, ...", "In C#, ..."). Use the `html-document` Callout pattern for the final HTML.

## Style

- As simple language as possible
- Tie every explanation to a quoted snippet — no abstract lectures.
- Prefer short sentences; if a sentence needs several target/platform terms, split it and define them first.

## Gotchas

- Do not explain constructs the reader already knows from the comparison language unless the target language behaves differently.
- Preserve changed code exactly in code blocks. Any simplification belongs in prose, not in the quoted source.
- The goal is teaching, not proving coverage. Skip generated, vendored, or mechanical churn after noting that it was skipped.
