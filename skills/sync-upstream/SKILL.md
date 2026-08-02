---
name: sync-upstream
description: Sync every local branch in a fork with its upstream parent. Use only for full-fork updates that include the base branch, feature branches, and dev. Do not use for fetching origin or rebasing only the current branch.
---

# Sync Upstream

Preserve every commit and the user's working state. Stop when safety cannot be proven.

## Inspect

- Record the current branch so it can be restored.
- Run `git status --short`, `git stash list`, and `git remote -v`.
- Stop on a detached HEAD or an unfinished merge, rebase, or cherry-pick.
- If the tree is dirty, stash tracked and untracked files only when the user requested the sync. Record the created stash.
- Detect the GitHub parent and its default branch with `gh repo view`.
- Add `upstream` when absent. Stop if an existing `upstream` points elsewhere.
- Fetch `origin` and `upstream` with pruning.

## Update the base branch

Check out the parent's default branch and update it with:

```bash
git merge upstream/<base> --ff-only
git push origin <base>
```

If the merge cannot fast-forward, show both sides and stop:

```bash
git log --oneline <base>..upstream/<base>
git log --oneline upstream/<base>..<base>
```

Never reset, force-merge, rebase, or force-push the base branch.

## Rebase feature branches

Process every local branch except the base branch and `dev`.

For each branch:

```bash
git checkout <branch>
git rebase <base>
git push origin <branch> --force-with-lease
```

Before resolving a conflict, read these files when present:

- `PATCH.md` or `docs/PATCH.md`
- `docs/branch-<branch>.md`
- `git log <base>..<branch> --oneline` when no guidance exists

Preserve upstream behavior and branch intent. After resolving a rebase conflict, stage the files and run `git rebase --continue`.

If resolution is unsafe, run `git rebase --abort`, mark the branch skipped, and continue from the base branch. If rebase metadata is missing or corrupt, stop; do not reconstruct the rebase manually.

## Rebuild dev

Before replacing local `dev` or `origin/dev`:

- Ignore merge commits created by earlier dev builds.
- Use `git cherry` or `git log --cherry-pick` to identify non-merge patches already represented by the updated base or feature branches.
- Stop and show any remaining unique patches.

Only after that check passes:

```bash
git checkout <base>
git branch -D dev 2>/dev/null || true
git checkout -b dev
```

Merge each successfully rebased feature branch with `--no-ff`. If branch guidance describes one branch as a strict superset of another, merge the subset first.

For a dev merge conflict:

- read the same intent files
- stage resolved files and run `git commit`
- run `git merge --abort` when resolution is unsafe

Push rebuilt dev with `git push origin dev --force-with-lease`. Stop and report a rejected lease; never retry with bare `--force`.

## Restore and report

- Return to the recorded starting branch.
- Apply the recorded stash there.
- Drop it only after a clean apply; otherwise keep it and report the conflict.
- Do not add AI attribution trailers to any commit.
- Report each branch, skipped work, push failures, stash state, and `git log --oneline --graph dev | head -30`.
