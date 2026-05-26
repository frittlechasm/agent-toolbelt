---
name: sync-upstream
description: Syncs a forked repository's local main branch with its upstream parent, then rebases all feature branches onto the updated main and rebuilds dev by merging all feature branches. Use this skill whenever the user says "sync upstream", "sync with upstream", "pull from upstream", "update from upstream", "keep branches in sync", "sync the repo", or runs /sync-upstream. Also trigger when the user asks to bring their fork up to date with the original project.
---

# sync-upstream

Keeps a fork in sync with its upstream parent: updates `main`, rebases every feature branch, and rebuilds `dev` as a clean merge of all features.

## Before you start

Stash any dirty working tree so nothing gets clobbered:

```bash
git stash list   # note count before
git stash        # only if git status shows changes
```

Remember whether you stashed so you can pop at the end.

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

### Handling conflicts

If rebase stops with conflicts:

1. Before touching any file, gather intent context:
   - Check for `PATCH.md` at the repo root (`./PATCH.md`) and in `docs/PATCH.md`. If either exists, read it — it describes the overall intent and motivation behind the branch's changes, which is essential for resolving conflicts correctly.
   - Check `docs/branch-<branchname>.md` — it has a **Conflict Hot-Spots** table and **Resolution guidance** section written specifically for that branch.
   - If neither file exists, infer intent on your own: read `git log main..<branch> --oneline` to see what commits the branch adds, inspect the conflicted files to understand what the branch is trying to change, and form a clear mental model of the branch's purpose before resolving anything.
   Together these sources tell you *why* the branch exists and *where* the tricky spots are. If PATCH.md contradicts a specific resolution in the branch doc, prefer the branch doc — it is more granular.
2. Resolve each conflicted file following the guidance. The intent described in PATCH.md and the branch docs tells you what the branch changes are trying to accomplish — make sure both the upstream additions and the branch's changes are preserved.
3. Stage resolved files and continue:
   ```bash
   git add <resolved-files>
   git rebase --continue
   ```
4. If a conflict is unresolvable, abort, skip the branch, and report it at the end:
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
git branch -D dev
git checkout -b dev
```

### Merge order matters

Before merging, scan the `docs/branch-*.md` files for the phrase **"strict superset"**. If branch B is described as a strict superset of branch A, merge A first, then B. This avoids redundant commits and keeps the graph clean.

If a merge into `dev` produces conflicts, follow the same resolution process as Step 3: check `PATCH.md` (root or `docs/`) for intent, then `docs/branch-<branchname>.md` for specific guidance.

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
