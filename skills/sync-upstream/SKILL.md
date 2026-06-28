---
name: sync-upstream
description: Sync a forked repository with its upstream parent: fast-forward local main from upstream/main, rebase every feature branch, and rebuild dev from the rebased branches. Use this skill whenever the user says "sync upstream", "sync with upstream", "pull from upstream", "update from upstream", "keep branches in sync", "sync the repo", runs /sync-upstream, or asks to bring a fork up to date with the original project.
---

# sync-upstream

Use this workflow from the target repository. It rewrites feature branches, so prefer fast-forward updates for `main`, `--force-with-lease` for rewritten branches, and explicit reporting whenever you stop.

## Before you start

Check the working tree before changing branches:

```bash
git status --short
git stash list
```

If there are tracked or untracked changes, do not overwrite them. If the user clearly asked for the sync to proceed, stash them and remember that you did. Otherwise collect confirmation with `request_user_input` or the environment's equivalent user-input tool when available; if not, ask a concise question before stashing.

```bash
git stash push -u -m "sync-upstream temporary stash"
```

## Step 1 — Wire up the upstream remote

Detect the parent repo automatically:

```bash
gh repo view --json parent --jq '.parent | "\(.owner.login)/\(.name)"'
```

If no remote named `upstream` exists yet, add it:

```bash
git remote add upstream https://github.com/<owner>/<repo>.git
```

Then fetch:

```bash
git fetch upstream main
```

## Step 2 — Update local main

```bash
git checkout main
git merge upstream/main --ff-only
```

If the fast-forward fails (local main has diverged), **stop and tell the user** — do not force-merge. Show them what diverged with `git log --oneline main..upstream/main` and `git log --oneline upstream/main..main` so they can decide what to do.

If it succeeds, push:

```bash
git push origin main
```

## Step 3 — Rebase every feature branch onto updated main

Collect branches to process — everything except `main` and `dev`:

```bash
git branch --format='%(refname:short)' | grep -Ev '^(main|dev)$'
```

For each branch:

```bash
git checkout <branch>
git rebase main
```

### Conflict resolution

Before resolving rebase or merge conflicts, gather intent context:

1. Read `./PATCH.md` or `docs/PATCH.md` if present.
2. Read `docs/branch-<branchname>.md` if present; prefer it over PATCH.md for branch-specific conflicts.
3. If no guidance exists, infer intent from `git log main..<branch> --oneline` and the conflicted files before editing.

Preserve both upstream changes and the branch's purpose. After resolving rebase conflicts:

```bash
git add <resolved-files>
git rebase --continue
```

If a conflict is not safely resolvable, abort, skip the branch, and report it at the end:

```bash
git rebase --abort
git checkout main
```

After a clean (or resolved) rebase:

```bash
git push origin <branch> --force-with-lease
```

Always use `--force-with-lease`, never bare `--force`.

### Rebase state edge case

If git reports "no rebase in progress" but `REBASE_HEAD` still exists, the rebase machinery lost its state directory. Handle it manually:

1. The conflicted files in the working tree are already at the correct merged state for the unstaged files — stage them.
2. Commit using the original commit's message (`git show <REBASE_HEAD> --format="%s%n%n%b" --no-patch`).
3. Cherry-pick any remaining commits from the original branch (`git cherry-pick <remaining-sha>`).
4. Move the branch ref: `git branch -f <branch> HEAD && git checkout <branch>`.

## Step 4 — Rebuild dev

Delete the old `dev` and create a fresh one from `main`:

```bash
git checkout main
git branch -D dev 2>/dev/null || true
git checkout -b dev
```

### Merge order matters

Before merging, scan the `docs/branch-*.md` files for the phrase **"strict superset"**. If branch B is described as a strict superset of branch A, merge A first, then B. This avoids redundant commits and keeps the graph clean.

If a merge into `dev` produces conflicts, use the conflict-resolution process above.

Merge each branch:

```bash
git merge <branch> --no-ff -m "Merge branch '<branch>' into dev"
```

Push dev:

```bash
git push origin dev --force-with-lease
```

## Commit messages

Never add a `Co-Authored-By` trailer attributing yourself (the AI agent) to any commit made during this workflow. All commits (manual conflict resolutions, rebase continuations, merge commits) must contain only the original message — no AI attribution lines.

## Gotchas

- Rebasing feature branches rewrites history. Use `--force-with-lease` for rewritten branches and report every branch that was rewritten.
- Do not force-update `main`. If `main` diverged from `upstream/main`, stop and show both sides of the divergence.
- Conflict guidance files are hints, not commands. Use them to understand intent, then preserve both upstream changes and the branch's purpose when possible.

## Step 5 — Restore stash and report

If you stashed at the start, restore it:

```bash
git stash pop
```

Then print a summary:

```
## Sync complete

| Branch               | Result             |
|----------------------|--------------------|
| main                 | ✓ updated          |
| <branch-1>           | ✓ rebased, pushed  |
| <branch-2>           | ✓ rebased, pushed  |
| <branch-n>           | ✗ skipped (conflict — <reason>) |
| dev                  | ✓ rebuilt          |
```

Finish with the dev graph so the user can see the shape of what was merged:

```bash
git log --oneline --graph dev | head -30
```

If any branches were skipped, describe the conflict and what the user needs to do to resolve it manually.
