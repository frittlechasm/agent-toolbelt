---
name: commit-msg
description: Generate conventional commit messages from uncommitted changes. ALWAYS use this skill for ANY request to produce, write, draft, suggest, propose, create, or generate a git commit message — including "commit", "commit message", "commit msg", "generate/write/draft/suggest a commit message", "what should the commit message be", "message for this commit", "git commit message", "check changes and commit", or "now commit". Trigger whenever a commit message needs to be authored from staged or unstaged changes, regardless of exact wording.
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
