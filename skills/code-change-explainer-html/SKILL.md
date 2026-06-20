---
name: code-change-explainer-html
description: Create or refine standalone HTML documents that teach code changes line by line, anchored to a comparison language the reader already knows (their most-familiar language) and with detailed callouts explaining the non-obvious syntax of the language the code is actually written in. Use this whenever the user wants a teaching document for code changes, refactors, optimization passes, implementation explainers, before/after walkthroughs, PR write-ups for review, understanding what an AI agent changed across a coding session in an unfamiliar language, or any artifact whose purpose is to *teach* a reader what changed and why. Triggers on phrases like "explain the code change", "walk through this refactor", "write up what changed and why", "explain what you changed this session", "walk me through what the agent did", "explain this in terms of a language I know", "before/after document", "implementation explainer", "teach me what this code does", "PR explainer", or any time the goal is teaching rather than tracking work. Extends `html-document` for presentation.
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

After resolving, **record the choice in persistent memory** (if your environment supports it) as the user's preferred comparison language, so future documents skip the question. A prompt naming a one-off comparison language for a single document overrides memory for that document but should not silently replace a stored general preference; when in doubt, keep the stored preference and ask if the user wants it changed.

Throughout this skill, *"the comparison language"* means whatever was resolved here. The examples below happen to use various languages; substitute the resolved one.

## Boundaries and dependencies

- This skill owns **what** goes on the page: the lessons, the comparison-language mental model, the choice of which target-language concepts deserve callouts, the line-by-line walkthroughs, the verification step.
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

Fluent in the **comparison language** and its ecosystem — they think in its idioms, libraries, and patterns. They have *not* internalised the **target** language's idioms — spell those out. If you catch yourself writing "as you know, in <target language> …", reframe: the reader does *not* know the target language; that is why the document exists.

## Lesson Anatomy

**One Lesson per distinct concept — not one per diff.** A single code change usually bundles several things to learn, and each deserves its own Lesson. A function refactor that introduces an async signature, an awaited call, and an optional-unwrap is **three Lessons**, each teaching one concept end to end — that segregation is what makes the document scannable and lets the reader re-derive the change one idea at a time. Lumping a multi-concept change into a single sprawling Lesson is the most common failure here: prefer several short, focused Lessons. Collapse to one Lesson only when the change genuinely teaches just one thing (e.g. extracting a named constant). When Lessons interlock, add the end-to-end flow section (see Document Structure) to show how they compose.

Use this section order within each Lesson; skip a section only when it truly does not apply.

### 1. Title, Equivalent, and Trust

One-line title plus a one-line equivalent naming the closest analogue **in the comparison language**, and a **trust badge** rating the change — so a reader learning from an agent's output absorbs the *good* way, not just what compiled.

> **Adding a user-by-email lookup** — *In Spring terms: a `findByEmail` on a Spring Data JPA Repository.* (when the comparison language is Java)

Tag each Lesson with one of `html-document`'s confidence / severity **Badges** (reuse them; do not invent new CSS):

- **Idiomatic** (`badge-green`) — the standard, safe way to do this in the target language / platform.
- **Works, but unusual** (`badge-amber`) — functional, but not how an experienced practitioner would write it; name the idiomatic alternative in Strategy.
- **Risky** (`badge-red`) — a latent bug, footgun, or violated platform constraint; explain the risk in Gotchas.

This is honest labelling, not a code review — one badge per Lesson, justified in a few words. When you are unsure, say so rather than stamping `Idiomatic` by default.

### 2. Concept

What the change accomplishes, 2–4 plain sentences, no code yet. Define any target-language jargon inline.

### 3. Explain Like I'm Five (optional — hard concepts only)

Only when a lesson's central concept is genuinely hard for *anyone*, regardless of language background — async/await, closures, ownership and move semantics, generics variance, pointers vs. references, the event loop. Skip it entirely for anything the reader already groks from the comparison language (a method, a field, a loop, an assignment). Forcing an analogy onto an easy concept patronises the reader and bloats the page; if you can't find one that's genuinely illuminating, omit the section — a weak analogy is worse than none.

One short everyday-world analogy, **no code and no programming terms** — the point is to build raw intuition *before* Section 4 maps it back to the comparison language. Keep it to 2–4 sentences.

Distinct from its neighbours, and the model must not just restate them:

- **Concept (2)** — what the change accomplishes, in plain technical sentences.
- **Explain Like I'm Five (3)** — one non-technical analogy for the hard idea, zero jargon.
- **Mental Model (4)** — the precise mapping to comparison-language terms.

> *Example (closures):* A closure is like a chef who walks out of the kitchen carrying a backpack of ingredients. Wherever they cook later, they still have exactly the ingredients they grabbed on the way out — not whatever happens to be in the new kitchen.

Render via `html-document`'s **Callout** pattern (reuse `<aside class="callout">`) with an `<h4>` such as "In plain terms" so it reads distinctly from the concept callouts. Do not add new CSS.

### 4. Mental Model (required)

Callout box mapping the new code to specific **comparison-language** terms. Be concrete — vague analogies are worse than none. For example, if the comparison language is Java:

- "This module is a Spring `@Service`; the default export is the instance."
- "The arrow function is a lambda — equivalent to `users.stream().map(User::getEmail).toList()`."
- "`async` returns `CompletableFuture<User>`; `await` is `.join()`, non-blocking."

Phrase the mapping in whatever the resolved comparison language is. Render via `html-document`'s concept callout pattern (**Callouts**).

### 5. Strategy

Why the code changed, 3–6 sentences. Tie back to architectural concerns the reader recognises from the comparison language: cohesion, layering, testability, transactional boundaries, error propagation.

When an AI agent made the change, the rationale is usually *undocumented* — infer it from the evidence: what the new code replaced, what problem or constraint it resolves, what pattern it conforms to. State an inference *as* an inference ("this looks aimed at removing the callback nesting"), not as established fact. And be honest when the change is **not** clearly right: if a choice is unusual, risky, or you cannot reconstruct a good reason for it, say so plainly — a reader learning from the change is better served by "this works but is an unusual way to do it" than by a confident rationalisation. Carry that judgement into the Lesson's trust badge (Section 1).

### 6. Code Comparison

Use the before/after stacked-panel pattern from `html-document` `references/elements.md` (**Code extensions**). Two separate sections — *not* a unified diff — because unified diffs hide spatial structure and that is exactly what we want the reader to see. Use the document skill's panel styling for height, scroll, and stacking behaviour.

### 7. Line-by-Line Walkthrough (the heart)

For every meaningful line of the After code (group boilerplate together; never skip silently):

- **Quote** the line in monospace.
- **What it says**: literal reading of tokens.
- **What it does**: behavioural effect at runtime — value type, side effects.
- **Why this way**: why this construct over alternatives — the author's call.

Use an ordered list of cards or a `<dl>` definition list — not a wide table. Lean on the base typography in `html-document`'s SKILL.md rather than inventing new styling.

Worked entry (target TypeScript, comparison Java):

> **Line 5:** `const result = await fetchUser(id);`
> *Says:* declare `result` from awaiting `fetchUser(id)`.
> *Does:* `fetchUser` returns `Promise<User>`. `await` suspends the surrounding `async` function until resolved; a rejection throws here.
> *Why:* `.then(...)` chains push the rest into a callback and lose linear flow. `await` reads top-to-bottom like blocking Java, without blocking the thread.

### 8. Concept Callouts (required for non-trivial target syntax)

Every non-trivial construct **of the target language** gets a callout with five fields: Name, Minimal syntax, Semantic, Parallel (in the comparison language), Gotcha. Use the concept callout pattern from `html-document` (**Callouts**); the HTML structure, the dedup rule, and the scope rules live in `references/concept-callouts.md`. To decide *which* constructs deserve a callout, run the category sweep in `references/any-language.md` over the actual code.

Two hard rules (detailed in `references/concept-callouts.md`):

- **Never explain the comparison language's syntax.** The reader knows it. It appears only as the *parallel*, to anchor the target construct — never as a thing to be taught.
- **Never explain the same target construct twice.** The first time a construct appears, give it a full callout; afterwards reference back ("as covered in Lesson 2, `?.` short-circuits on nullish values").

### 9. Gotchas

Short list of **language and platform** pitfalls drawn from the actual code.

- *Language*: equality semantics, mutation in collection ops, scoping/binding surprises, default-argument traps, nil/null edge cases, move semantics.
- *Platform / runtime / framework*: the footguns that aren't in the syntax but bite at runtime — React render/effect timing and stale closures, Node-vs-browser event-loop behaviour, ORM lazy-loading and N+1 queries, main-thread / UI-thread constraints, GC and retain cycles, framework lifecycle ordering, library API traps.

These are often *why* the change was made — surface the ones the actual code touches, and feed any genuine hazard into the Lesson's trust badge.

### 10. Verification

A concrete, copy-pasteable check: a command, a curl, a UI flow, a test name.

## Explanation Style

- Pair-programming voice anchored to the comparison language: "Notice that …", "If you've written a service in <comparison language>, this is the same idea."
- Tie every explanation to a quoted snippet — no abstract lectures.
- Name patterns (Adapter, Strategy, Repository, Visitor, Builder) and tie them to the comparison language.
- Explain the *why*, not only the *what*.

## Document Structure

1. Title, audience (state the comparison language), summary — including a one-line **coverage note**: what was taught vs. what was skipped as noise (generated files, lockfiles, formatting).
2. Status / verification strip.
3. Concept map — outline of every concept taught (TOC + learning contract).
4. Lessons.
5. Optimised flow / end-to-end runtime path (when changes interlock).
6. End-to-end verification.
7. Remaining work.
8. Files to read next.

Compose using the *Code-change explainer* scaffold in `html-document` `references/elements.md` (**Document scaffolds**).

## Quality Checklist

- Change set ingested from the real diff where one exists; skipped noise (generated files, lockfiles, formatting) noted in the coverage line, not silently dropped.
- Lessons grouped by concept across files and ordered along the architecture / data flow, not by file order.
- Every Lesson carries a trust badge (Idiomatic / Works-but-unusual / Risky), justified in a few words, with uncertainty stated rather than defaulting to Idiomatic.
- Gotchas cover the platform / runtime / framework footguns the code touches, not only language syntax.
- The *why* is reconstructed for agent-made changes, with inferences flagged as inferences and questionable choices called out honestly.
- Comparison language resolved by the prompt → memory → ask priority, and recorded in memory when newly learned.
- Audience line names the comparison language so the reader knows the anchor.
- Multi-concept changes are split into one Lesson per concept (not lumped into a single sprawling Lesson); interlocking Lessons get the end-to-end flow section.
- Every Lesson has a Mental Model with a *specific* comparison-language analogue, not a hand-wave.
- "Explain Like I'm Five" appears only on genuinely hard concepts, adds a jargon-free analogy, and never just restates the Concept or Mental Model — easy lessons have none.
- Every non-trivial **target** syntactic feature has a Concept Callout with a comparison-language parallel and a gotcha.
- **No explanation of the comparison language's own syntax** anywhere — it appears only as the parallel.
- **No duplicate syntax explanations** — each target construct is taught once, then referenced back.
- Every line of the in-scope After code is accounted for — quoted, grouped, or explicitly noted (noise triaged out is covered by the coverage line, not silently skipped).
- Pattern names stated where applicable.
- Concept map at the top lists every feature taught below.
- Presentation deferred to `html-document`: before/after panels, callout boxes, badges, and print fallbacks all rendered through its element catalog.
- No "as you know, in <target language> …" remains.
