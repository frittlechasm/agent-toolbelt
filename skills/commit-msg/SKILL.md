---
name: commit-msg
description: Generate conventional commit messages from uncommitted changes. Use when the user asks to "commit", "generate a commit message", "write a commit message", "check changes and commit", or any request involving creating git commit messages from staged or unstaged changes.
---

# Commit Message Generator

## Workflow

1. Run `git diff --cached` to inspect staged changes (if nothing staged, run `git diff` for unstaged)
2. Analyze the changes to determine the type, scope, and purpose
3. Generate a commit message following the format below
4. Output ONLY the commit message — do not run `git commit`
5. Do NOT add any commit trailers or attribution lines such as `Co-authored-by:`

## Format

```
<type>(<scope>): <subject>

[optional body]
```

- **Subject**: 50 chars max, imperative mood, lowercase, no period
- **Scope**: component or area affected (optional but preferred)
- **Body**: include only if changes are complex — explain WHAT and WHY
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
