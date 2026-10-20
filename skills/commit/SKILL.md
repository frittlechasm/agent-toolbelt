---
name: commit
description: Draft commit messages from repository changes. Use when asked for a commit message or when committing changes.
metadata:
  scope: global
  agents: claude, codex
  machines: all
---

# Commit Message Generator

## Inspect changes

- Run `git status --short` so untracked files are visible.
- Run `git diff --cached` to inspect staged changes.
- For a message-only request, use the staged diff when present; otherwise inspect `git diff` for unstaged changes.
- If only untracked files remain, inspect their relevant contents before writing the message.
- If there are no changes, say there are no changes to summarize.

## Commit scope

- When asked to commit, use the user's requested files or task as the boundary. Staging alone does not authorize unrelated changes.
- Inspect the diff for the authorized changes and derive the message from what the commit will contain.
- Commit only those changes after normal repository checks. Preserve unrelated staged and unstaged changes, including their index state.
- Each commit should cover one meaningful change and include its related tests and documentation.
- Keep commits buildable and testable when practical. Do not split changes just to increase the number of commits.

## Write the message

- For a message-only request, return the message with no recap, alternatives, or command instructions.
- Choose the type and optional scope from the actual behavioral intent of the diff.
- Do not add commit trailers or attribution lines such as `Co-authored-by:`.
- For breaking changes, add `!` before the colon: `feat(auth)!: remove OAuth 1.0`.

## Gotchas

- For message-only requests, do not mix staged and unstaged changes unless the user asks to cover the whole working tree.
- Prefer the narrowest accurate type. A dependency bump that fixes a bug can be `fix`; routine metadata churn is usually `chore`.
- If the diff combines unrelated changes:
  - Suggest one message only when the user intends to commit them together.
  - Otherwise, mention that separate commits would be clearer.

## Format

```
<type>(<scope>): <subject>

[optional body]
```

- **Subject**: concise, imperative, lowercase, no period; reflect the diff and the user's intent
- **Scope**: component or area affected (optional but preferred)
- **Body**: include only if changes are complex; explain what changed and why

Types: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `style`, `perf`, `build`, `ci`, `revert`.
