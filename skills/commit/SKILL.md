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
- Follow the format below.
- Choose the type and optional scope from the actual behavioral intent of the diff.
- Write a concise, human-readable subject that reflects the diff and the user's intent.
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

- **Subject**: concise, imperative, lowercase, no period
- **Scope**: component or area affected (optional but preferred)
- **Body**: include only if changes are complex; explain what changed and why

## Types

| Type | Use For | Example |
|----------|----------------------|-----------------------------------------------|
| feat | New features | `feat(auth): add JWT refresh token` |
| fix | Bug fixes | `fix(api): handle null pointer in user service` |
| refactor | Code restructuring | `refactor: extract duplicate logic into helper` |
| chore | Maintenance tasks | `chore(deps): bump spring-boot to 3.2.0` |
| docs | Documentation only | `docs(readme): update API endpoint examples` |
| test | Adding/updating tests | `test(auth): add unit tests for token validation` |
| style | Formatting only | `style: run prettier on all ts files` |
| perf | Performance | `perf(cache): add redis for session storage` |
| build | Build system changes | `build(docker): optimize image layers` |
| ci | CI/CD pipeline | `ci(github): add integration test workflow` |
| revert | Reverting commits | `revert: undo breaking change in auth module` |
