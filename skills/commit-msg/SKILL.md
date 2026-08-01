---
name: commit-msg
description: Generate Conventional Commit messages. Use whenever the user asks to write, draft, suggest commit messages or when committing changes.
---

# Commit Message Generator

## Workflow

- Run `git diff --cached` to inspect staged changes.
- If staged changes exist, base the message only on the staged diff; otherwise run `git diff` for unstaged changes.
- If there are no staged or unstaged changes, say there are no changes to summarize.
- If the user only asked for a message, lead with the message itself
- If the user explicitly asked to commit, use the generated message for the commit after normal repository checks.
- Generate a commit message following the format below.
- Choose the type and optional scope from the actual behavioral intent of the diff.
- Generate the subject based on the diff and actual intent of the change based on user's original prompt.
- Always write a concise, human-readable subject that explains why the change matters.
- Do not add commit trailers or attribution lines such as `Co-authored-by:`.
- Add `!` before colon — `feat(auth)!: remove OAuth 1.0` for breaking changes.

## Gotchas

- Staged changes win. Do not mix in unstaged changes unless the user asks for a message covering the whole working tree.
- Prefer the narrowest accurate type. A dependency bump that fixes a bug can be `fix`; routine metadata churn is usually `chore`.
- If the diff combines unrelated changes, suggest one message only when they are intentionally being committed together; otherwise mention that separate commits would be clearer.
:wq
## Format

```
<type>(<scope>): <subject>

[optional body]
```

- **Subject**: human-readable, lowercase, no period
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
