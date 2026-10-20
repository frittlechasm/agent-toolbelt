---
name: walkthrough
description: Create standalone HTML walkthroughs of a commit, diff, or coding session. Use only when the user explicitly requests an HTML code-change explainer.
metadata:
    scope: global
    agents: claude, codex
    machines: all
---

# Code Change Explainer HTML

Create a standalone `.html` document that teaches what changed in code and why, with only the context the reader needs.

## Goal

- Lead with the practical outcome or mental model, then move from old behavior to new behavior, mechanism, and meaningful line-level detail.
- Define unfamiliar target-language or platform terms briefly near first use.
- Claim only what the supplied diff, source, or prompt supports. Do not invent bugs, causes, or consequences.
- Choose a structure that fits the change; avoid repeating the introduction in outcome callouts or later sections.

## Comparison language

Use the comparison language named in the prompt, otherwise a stored preference, otherwise explain the target code directly.
Ask only when the missing language would materially change the teaching approach.
Compare languages only to clarify an unfamiliar mechanism; keep the analogy brief, state its limits, and skip familiar syntax.

## Gather the change

- Read the real before and after from `git diff`, `git diff --staged`, the requested commit, or the supplied source.
- Read `CONTEXT.md` when present and use its established domain terms unless the source contradicts them.
- Understand the changes and their motivation. Check the interaction, prompts, and decisions from the session when available.
- Clearly distinguish observed behavior, stated intent or specification, and inferred rationale.
- Use examples from the supplied change. When only the prompt describes it, label reconstructed surrounding code as illustrative.
  Do not let examples imply unsupported behavior.
- Skip generated, vendored, lockfile, formatting-only, and import-order churn. Briefly note material omissions.
- Group related changes by concept or runtime flow when that is clearer than file order.

## Protect secrets

- Redact passwords, tokens, API keys, private keys, JWTs, authentication values, embedded URL credentials, and suspicious secret-like values.
- Use distinct labeled placeholders such as `[REDACTED:API_TOKEN]` for distinct secrets.
- Preserve surrounding syntax and redact only the credential component.
- Redact secrets in both Before and After snippets, even when removing the secret is the change.
- State visibly that credentials were redacted. If a real committed credential is found, warn that it may remain in Git history and should be rotated.

## Teach the change

For each distinct concept:

- Explain the practical old and new behavior and why the change matters before walking through syntax.
- Show aligned Before and After code panels when code is available; do not use a unified diff.
- Walk through every meaningful changed line in a focused snippet. Group boilerplate or repetition in larger changes and say what was grouped.
- Quote the relevant line and explain unfamiliar syntax or semantics.
- When an unfamiliar protocol or platform feature drives the change, show one small request/response or input/output example.
- Explain tradeoffs or failure behavior only when supported by the evidence.

## Preserve source code

- Copy source code exactly, including snippets delimited in the user's prompt. Preserve punctuation, spacing, line breaks, and supplied context.
  Secret redaction is the only exception.
- Before finalizing, compare every code block with its source and confirm that only secret redactions differ.
- Put simplifications and explanations in prose, not inside quoted code.

## Render

- Use the `html` skill when available; otherwise create the standalone HTML directly.
