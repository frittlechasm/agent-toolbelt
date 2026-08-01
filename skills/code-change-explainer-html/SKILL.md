---
name: code-change-explainer-html
description: Create HTML explainers that teach code changes using a language the reader knows. Use when the user asks to explain, walkthrough, or teach changes from a commit, diff, or coding session.
---

# Code Change Explainer HTML

- Build a standalone `.html` document that **teaches** what changed in code and why, line by line.
- Keep the explanation as simple as possible. A reader should be able to understand each lesson with ease.
- Preserve the code exactly as it was changed, except secret values, which must always be redacted as described in **Scrub secrets**.
- Your job is to expand the explanation around the code, not to alter it.

Two languages are in play in every document:
- **Target language** — the language the code is *written in*.
- **Comparison language** — the language the reader is *most fluent in*. You **map the target back to it** for comparison.

## Comparison language (resolve this first)

Before drafting, decide which language to anchor explanations to, in this strict priority:

- **Prompt.** If the request names the language to compare with use that. The prompt always wins.
- **Memory.** If the prompt is silent and your environment has a stored preference (a memory recording the user's most-familiar language), use that.
- **Ask.** Only when *neither* the prompt nor memory specifies, collect the comparison language with the environment's user-input tool when available; otherwise ask a concise question and wait.

Throughout this skill, *"the comparison language"* means whatever was resolved here.

## Boundaries and dependencies

- This skill owns **what** goes on the page.
- This skill does **not** own how the page is rendered.
- Invoke the `html-document` skill to render the final `.html` if available; otherwise render the standalone HTML directly.
- You **never explain the comparison language's own syntax**; the reader already knows it.

## Ingesting the change set

### Source the diff
- Use `git diff`, `git diff --staged`, or a diff against the commit the session started from.
- Read the actual before/after from the repo so the snippets are real.

### Scrub secrets before drafting
- Treat the following as secrets:
  - tokens
  - API keys
  - passwords
  - private or signing keys
  - JWTs
  - authentication headers or cookies
  - embedded URL or connection-string credentials
  - suspicious high-entropy values assigned to secret-like names
- Replace every detected or suspected secret anywhere in the HTML or final response with a consistent labeled placeholder such as `[REDACTED:API_TOKEN]`.
- Use distinct labels for distinct secrets. Preserve the surrounding syntax and delimiters; redact only the credential component, and in multiline keys preserve only non-sensitive boundary markers.
- Redact both Before and After, even when removing the secret is the change being taught. When uncertain, redact and disclose the uncertainty; never ask the user to paste or reveal the value.
- State visibly in the document that credential values were redacted. If a real credential appeared in committed content, warn in the final response that it may remain in Git history and should be rotated.

### Triage signal from noise
- Skip lockfiles, generated/vendored code, and pure formatting, whitespace, or import-reordering churn — they teach nothing.
- Do not skip files silently; add one concise coverage note describing what was omitted.

### Order by architecture, not by file order
- Sequence the lessons along the data / dependency flow — entry point → core logic → edges (storage, network, UI).
- The concept map at the top should reflect this ordering.

## Lesson Anatomy

### One Lesson per distinct concept, not one per diff
- One concept can often span several files; one file often bundles several concepts.
- Split multi-concept changes into short focused Lessons; collapse only when the change teaches one idea.
- When Lessons interlock, add the end-to-end flow section.

- Use these visible sections inside each Lesson where applicable; keep the header names reader-facing:
  - **Title and Trust** — title plus one concise badge chosen to help the reader interpret the Lesson.
  - **The Change In Plain English**:
    - A very simple explanation of what this change does and why it was needed.
    - When the change fixes a bug, state the bug and what triggered it.
    - For a feature or refactor, describe the motivation instead.
    - Match the heading to the actual change — don't force bug framing onto non-bug work.
  - **Terms You Need** — brief definitions for target/platform vocabulary the reader needs to understand the code.
  - **Before**:
    - A very simple explanation of the old behavior or code and its implications. Title it *"Before The Fix"* only when the change is a fix.
    - Use a 3–6 step timeline for event-driven, async, UI, cross-process, distributed, or lifecycle changes.
  - **What Changed** — short bullets; use subheads for compound fixes.
  - **Why It Matters** — explain the user-visible, runtime, or safety effect.
  - **Code Comparison** — before/after panels, never a unified diff.
  - **Line-By-Line Walkthrough**:
    - For focused snippets, explain every meaningful line of the After code.
    - For larger changes, group boilerplate and repeated patterns so the document teaches the change without becoming a transcript; call out what was grouped.
    - **Quote** the line in monospace.
    - Explain the target-language syntax by breaking the line into meaningful pieces.
    - Compare the line with the comparison language.
    - Add a callout with **Name**, **Minimal syntax**, **Semantic**, **Parallel**, and **Gotcha** when it would improve learning. Choose what deserves a callout based on the changes.

### Architecture Decision (optional)
- Name the design choice, explain the simpler alternative, explain why this change chose the current shape, and call out the tradeoff.
- Mention patterns such as Adapter, Strategy, Repository, Visitor, or Builder only when they genuinely clarify the decision.

## Style

- As simple language as possible
- Tie every explanation to a quoted snippet — no abstract lectures.
- Prefer short sentences; if a sentence needs several target/platform terms, split it and define them first.

## Gotchas

- Explain target-language constructs that are not a 1:1 match for the comparison language. Do not explain the comparison language itself.
- Do not explain constructs the reader already knows from the comparison language unless the target language behaves differently.
- Preserve changed code exactly in code blocks. Secret redaction is the sole exception and always overrides source fidelity; any other simplification belongs in prose, not in the quoted source.
- The goal is teaching, not proving coverage. Skip generated, vendored, or mechanical churn after noting that it was skipped.
