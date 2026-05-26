---
name: code-change-explainer-html
description: Create or refine standalone HTML documents that teach code changes line by line, with a Java-first mental model and detailed concept callouts for language-specific syntax (TypeScript, Python, Go, Rust). Use this whenever the user wants a teaching document for code changes, refactors, optimization passes, implementation explainers, before/after walkthroughs, PR write-ups for review, or any artifact whose purpose is to *teach* a Java-background reader what changed and why. Triggers on phrases like "explain the code change", "walk through this refactor", "write up what changed and why", "explain this in Java terms", "before/after document", "implementation explainer", "teach me what this code does", "PR explainer", or any time the goal is teaching rather than tracking work. Extends `html-document` for presentation.
---

# Code Change Explainer HTML

Build a standalone `.html` document that **teaches** what changed in code, line by line, with the reader's Java background as the default mental model. Comprehension is the goal — a reader should finish each lesson able to re-derive the change. Preserve the user's existing code snippets; your job is to expand the explanation around them, not to alter the code.

## Boundaries and dependencies

- This skill owns **what** goes on the page: the lessons, the Java mental model, the choice of which concepts deserve callouts, the line-by-line walkthroughs, the verification step.
- This skill does **not** own how the page is rendered. Presentation — fonts, spacing, code-block styling, callout boxes, before/after panel layout, badges, print rules — lives in [`html-document`](../html-document/SKILL.md). Read its `references/elements.md` before drafting, especially:
  - §4 Code & Comparison (before/after panels, annotated diffs, multi-approach)
  - §5 Callouts & Glossary (the concept callout box this skill leans on)
  - §6 Badges (severity, confidence)
  - §18 Document Scaffolds (Code-change explainer scaffold)
- Always invoke `html-document` to render the final `.html`. Do not redefine styling here that already exists there.

Read the matching language reference before drafting:

- TypeScript/JavaScript → `references/java-typescript-mapping.md`
- Python → `references/java-python-mapping.md`
- Go → `references/java-go-mapping.md`
- Rust → `references/java-rust-mapping.md`
- Callout HTML structure → `references/concept-callouts.md`

## The Reader

Fluent in Java with Spring (DI, services, repositories, DTOs, `@Transactional`), comfortable with `Stream`, `Optional`, `CompletableFuture`, and lambdas. Has *not* internalised the source-language idioms — spell them out. If you catch yourself writing "as you know, in JavaScript ...", reframe from Java.

## Lesson Anatomy

One Lesson per code change. Use this section order; skip a section only when it truly does not apply.

### 1. Title and Java Equivalent

One-line title plus `Java equivalent: ...` naming the closest Java analogue.

> **Adding a user-by-email lookup** — *Java equivalent: a `findByEmail` on a Spring Data JPA Repository.*

### 2. Concept

What the change accomplishes, 2–4 plain sentences, no code yet. Define any source-language jargon inline.

### 3. Java Mental Model (required)

Callout box mapping the new code to specific Java terms. Be concrete — vague analogies are worse than none:

- "This module is a Spring `@Service`; the default export is the instance."
- "The arrow function is a lambda — equivalent to `users.stream().map(User::getEmail).toList()`."
- "`async` returns `CompletableFuture<User>`; `await` is `.join()`, non-blocking."

Render via `html-document`'s concept callout pattern (§5).

### 4. Strategy

Why the code changed, 3–6 sentences. Tie back to architectural concerns a Java engineer recognises: cohesion, layering, testability, transactional boundaries, error propagation.

### 5. Code Comparison

Use the before/after stacked-panel pattern from `html-document` `references/elements.md` §4. Two separate sections — *not* a unified diff — because unified diffs hide spatial structure and that is exactly what we want the reader to see. Use the document skill's panel styling for height, scroll, and stacking behaviour.

### 6. Line-by-Line Walkthrough (the heart)

For every meaningful line of the After code (group boilerplate together; never skip silently):

- **Quote** the line in monospace.
- **What it says**: literal reading of tokens.
- **What it does**: behavioural effect at runtime — value type, side effects.
- **Why this way**: why this construct over alternatives — the author's call.

Use an ordered list of cards or a `<dl>` definition list — not a wide table. `html-document` §3 covers the typography choices.

Worked entry:

> **Line 5:** `const result = await fetchUser(id);`
> *Says:* declare `result` from awaiting `fetchUser(id)`.
> *Does:* `fetchUser` returns `Promise<User>`. `await` suspends the surrounding `async` function until resolved; a rejection throws here.
> *Why:* `.then(...)` chains push the rest into a callback and lose linear flow. `await` reads top-to-bottom like blocking Java, without blocking the thread.

### 7. Concept Callouts (required for non-trivial syntax)

Every non-trivial construct gets a callout with five fields: Name, Minimal syntax, Semantic, Java parallel, Gotcha. Use the concept callout pattern from `html-document` §5; the HTML structure and decision rules live in `references/concept-callouts.md`, and the always-callout-worthy list per language is in each language reference.

### 8. Gotchas

Short list of language-specific pitfalls drawn from the actual code: equality (`===` vs `==`, `is` vs `==`), mutation in collection ops, `this`-binding, mutable default args, nil interface values, move semantics.

### 9. Verification

A concrete, copy-pasteable check: a command, a curl, a UI flow, a test name.

## Explanation Style

- Pair-programming voice: "Notice that ...", "If you've written a Spring `@Service`, this is the same idea."
- Tie every explanation to a quoted snippet — no abstract lectures.
- Name patterns (Adapter, Strategy, Repository, Visitor, Builder) and tie them to Java.
- Explain the *why*, not only the *what*.

## Document Structure

1. Title, audience, summary.
2. Status / verification strip.
3. Concept map — outline of every concept taught (TOC + learning contract).
4. Lessons.
5. Optimised flow / end-to-end runtime path (when changes interlock).
6. End-to-end verification.
7. Remaining work.
8. Files to read next.

Compose using the *Code-change explainer scaffold* in `html-document` `references/elements.md` §18.

## Quality Checklist

- Every Lesson has a Java Mental Model with a *specific* Java analogue, not a hand-wave.
- Every non-trivial syntactic feature has a Concept Callout with Java parallel and gotcha.
- Every line of After code is accounted for — quoted, grouped, or explicitly noted.
- Pattern names stated where applicable.
- Concept map at the top lists every feature taught below.
- Presentation deferred to `html-document`: before/after panels, callout boxes, badges, and print fallbacks all rendered through its element catalog.
- No "as you know, in <language> ..." remains.
