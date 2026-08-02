---
name: code-change-explainer-html
description: Creates standalone HTML explainers that teach code changes using a language the reader knows. Use only when the user explicitly requests an HTML walkthrough or explainer for a commit, diff, or coding session.
---

# Code Change Explainer HTML

Create a standalone `.html` document that teaches what changed in code and why.

## Goal

- Use the simplest language that remains accurate.
- Start with the practical old behavior or motivation, then explain the change and why it matters.
- Define unfamiliar target-language or platform terms briefly near first use.
- Claim only what the supplied diff, source, or prompt supports. Do not invent bugs, causes, or consequences.
- Choose the structure that makes the change easiest to understand. Timelines, concept maps, glossaries, and fixed section labels are optional.

## Comparison language

Anchor unfamiliar concepts to the language the reader knows best:

1. Use the language named in the prompt.
2. Otherwise use a stored preference when available. Check Memory.
3. Otherwise ask the user.

Explain unfamiliar target-language behavior through that comparison. Do not teach syntax the reader already knows.

## Gather the change

- Read the real before and after from `git diff`, `git diff --staged`, the requested commit, or the supplied source.
- Understand the changes made and why they were made. Check the interaction , prompts and decisions made in the session.
- When only the prompt contains the change, use only those facts and label any reconstructed surrounding code as illustrative.
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

- Explain the old behavior or motivation in plain language.
- Explain what changed and why it matters.
- Show aligned Before and After code panels when code is available; do not use a unified diff.
- Walk through every meaningful changed line in a focused snippet. Group boilerplate or repetition in larger changes and say what was grouped.
- Quote the relevant line, explain unfamiliar syntax or semantics, and compare it with the reader's language only when useful.
- Explain tradeoffs or failure behavior only when supported by the evidence.

## Preserve source code

- Copy source code exactly, including punctuation, semicolons, spacing, and line breaks.
- Treat code delimited in the user's prompt as exact source. Do not add or remove punctuation, formatting, or surrounding context.
- Secret redaction is the only exception to source fidelity.
- Before finalizing, compare every code block with its source and confirm that only secret redactions differ.
- Put simplifications and explanations in prose, not inside quoted code.

## Render

Use the `html-document` skill when available; otherwise create the standalone HTML directly. Keep the document readable and focused on teaching the change.
