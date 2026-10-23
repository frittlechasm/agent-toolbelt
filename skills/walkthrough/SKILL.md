---
name: walkthrough
description: Create standalone HTML walkthroughs of a commit, diff, or coding session. Use only when the user explicitly requests an HTML code-change explainer.
metadata:
    scope: global
    agents: claude, codex
    machines: all
---

# Code Change Explainer

Create a standalone `.html` document, built with the `html` skill, that teaches what changed in code and why, with only the context the reader needs.

## Gather the change

- Read the real before and after from `git diff`, `git diff --staged`, the requested commit, or the supplied source.
  Use the session's prompts and decisions for motivation when available.
- Use domain terms from `CONTEXT.md` when present, unless the source contradicts them.
- Separate observed behavior, stated intent, and inferred rationale. Claim only what the evidence supports; do not invent bugs, causes, or consequences.
- Use examples from the change. Label reconstructed surrounding code as illustrative, and do not let it imply unsupported behavior.
- Skip generated, vendored, lockfile, formatting-only, and import-order churn, and briefly note material omissions.
- Group changes by concept or runtime flow when that is clearer than file order.

## Teach it

- Lead with the practical outcome or mental model, then old and new behavior, the mechanism, and meaningful line-level detail.
  Do not repeat the introduction in later sections.
- Define unfamiliar language or platform terms briefly near first use.
- Use the comparison language from the prompt or a stored preference; otherwise explain the target code directly.
  Ask only when the missing language would change the approach. Keep comparisons brief, state their limits, and skip familiar syntax.
- For each concept, explain the behavior change and why it matters before the syntax.
- Show aligned Before and After panels, not a unified diff. Walk through every meaningful changed line, quoting it and explaining unfamiliar syntax.
  In large changes, group boilerplate and say what you grouped.
- When an unfamiliar protocol or platform feature drives the change, show one small request/response or input/output example.
- Explain tradeoffs or failure behavior only when the evidence supports them.

## Copy code exactly

- Copy source code exactly, including snippets from the prompt: punctuation, spacing, line breaks, and context. Secret redaction is the only exception.
- Put simplifications and explanations in prose, never inside quoted code.
- Before finishing, compare every code block with its source.

## Redact secrets

- Redact passwords, tokens, API keys, private keys, JWTs, auth values, URL credentials, and anything secret-like.
  Do it in both Before and After, even when removing the secret is the change.
- Use distinct labeled placeholders such as `[REDACTED:API_TOKEN]`, and redact only the credential part, keeping the surrounding syntax.
- Say visibly that credentials were redacted. If a real committed credential appears, warn that it stays in Git history and should be rotated.
