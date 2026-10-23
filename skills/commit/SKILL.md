---
name: commit
description: Draft commit messages from repository changes. Use when asked for a commit message or when committing changes.
metadata:
  scope: global
  agents: claude, codex
  machines: all
---

# Commit Message

## Inspect

- Run `git status --short` (it shows untracked files) and `git diff --cached`.
- For a message only, describe the staged diff. If nothing is staged, use `git diff`; if only untracked files remain, read them.
  Do not mix staged and unstaged changes unless asked to cover the whole tree.
- If there are no changes, say so.

## Commit

- Commit only the files or task the user named. Staged changes alone do not authorize unrelated work.
- Preserve unrelated staged and unstaged changes, including their index state.
- Make one meaningful change per commit, with its tests and docs. Keep commits buildable; do not split just to make more commits.
- If the diff mixes unrelated changes, suggest separate commits unless the user wants them together.

## Message

```
<type>(<scope>): <subject>

[optional body]
```

- Subject: short, imperative, lowercase, no period. Scope: the affected area (optional but preferred).
- Add a body only for complex changes, saying what changed and why.
- Pick the narrowest type from the change's intent: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `style`, `perf`, `build`, `ci`, `revert`.
  A dependency bump that fixes a bug is `fix`; routine metadata churn is `chore`.
- Mark breaking changes with `!`: `feat(auth)!: remove OAuth 1.0`.
- Do not add trailers or attribution lines such as `Co-authored-by:`.
- For a message-only request, return just the message: no recap, alternatives, or commit instructions.
