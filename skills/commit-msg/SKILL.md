---
name: commit-msg
description: Generate Conventional Commit messages from staged or unstaged Git changes. Use whenever the user asks to write, draft, suggest, choose, or use a commit message, including requests to commit changes where a message must be authored. Do not trigger for explaining Conventional Commits generally unless a concrete message is needed.
---

# Commit Message Generator

## Workflow

1. Run `git diff --cached` to inspect staged changes.
2. If staged changes exist, base the message only on the staged diff; otherwise run `git diff` for unstaged changes.
3. If there are no staged or unstaged changes, say there are no changes to summarize.
4. Choose the type, optional scope, and subject from the actual behavioral intent of the diff.
5. Generate a commit message following the format below.
6. If the user only asked for a message, lead with the message itself and keep surrounding prose to nothing — at most one short line before it, and only to flag something the user genuinely needs to act on the message safely (e.g. nothing was staged so it is based on unstaged changes, or the diff mixes unrelated changes that may belong in separate commits). Don't add a recap of the diff, a body the user didn't ask for, alternative phrasings, or `git add`/`git commit` instructions — the user knows how to commit.
7. If the user explicitly asked to commit, use the generated message for the commit after normal repository checks.
8. Do not add commit trailers or attribution lines such as `Co-authored-by:`.

## Gotchas

- Staged changes win. Do not mix in unstaged changes unless the user asks for a message covering the whole working tree.
- Prefer the narrowest accurate type. A dependency bump that fixes a bug can be `fix`; routine metadata churn is usually `chore`.
- If the diff combines unrelated changes, suggest one message only when they are intentionally being committed together; otherwise mention that separate commits would be clearer.

## Format

```
<type>(<scope>): <subject>

[optional body]
```

- **Subject**: 50 chars max, imperative mood, lowercase, no period
- **Scope**: component or area affected (optional but preferred)
- **Body**: include only if changes are complex; explain what changed and why
- **Breaking change**: add `!` before colon — `feat(auth)!: remove OAuth 1.0`
- **Trailers**: do not include `Co-authored-by:` or any other commit trailer

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
