---
name: upstream
description: Synchronize every local branch in a fork with its upstream parent. Use only for full-fork updates, not ordinary fetches or current-branch rebases.
metadata:
  scope: global
  agents: claude, codex
  machines: all
disable-model-invocation: true
---

# Sync Upstream

Keep every commit and the user's working state. Stop whenever you cannot show that a step is safe.

## Inspect

- Record the current branch so you can return to it.
- Run `git status`, `git stash list`, and `git remote -v`. Stop on a detached HEAD or any Git operation in progress.
  Continue or abort the operation Git reports; never replace a rebase with a cherry-pick or rebuild missing state by hand.
- If the tree is dirty, stash tracked and untracked files and record the stash.
- Find the GitHub parent and its default branch with `gh repo view`. Add `upstream` if missing; stop if it points elsewhere.
- Fetch `origin` and `upstream` with pruning.

## Update the base branch

Check out the parent's default branch, then:

```bash
git merge upstream/<base> --ff-only
git push origin <base>
```

If it cannot fast-forward, show both sides with `git log --oneline <base>..upstream/<base>` and `git log --oneline upstream/<base>..<base>`, then stop.
Never reset, force-merge, rebase, or force-push the base branch.

## Rebase feature branches

For every local branch except the base and `dev`:

```bash
git checkout <branch>
git rebase <base>
git push origin <branch> --force-with-lease
```

- Before resolving a conflict, read `PATCH.md` or `docs/PATCH.md` and `docs/branch-<branch>.md` when present,
  or `git log <base>..<branch> --oneline` when there is no guidance. Keep upstream behavior and the branch's intent.
- After resolving, stage the files and run `git rebase --continue`.
- If resolution is unsafe, run `git rebase --abort`, mark the branch skipped, and continue from the base branch.
- If rebase metadata is missing or corrupt, stop.

## Rebuild dev

- Before replacing local `dev` or `origin/dev`, check each separately with `git cherry` or `git log --cherry-pick` for non-merge patches,
  ignoring merge commits from earlier dev builds. One ref being safe says nothing about the other.
  If unique patches remain, show them and stop.
- Only after that check passes, recreate `dev`:

    ```bash
    git checkout <base>
    git branch -D dev 2>/dev/null || true
    git checkout -b dev
    ```

- Merge each rebased feature branch with `--no-ff`. If guidance says one branch is a strict superset of another, merge the subset first.
- On a merge conflict, read the same guidance files, then stage and `git commit`, or run `git merge --abort` when resolution is unsafe.
- Push with `git push origin dev --force-with-lease`. If the lease is rejected, stop and report it; never retry with bare `--force`.

## Restore and report

- Return to the starting branch and apply the recorded stash there. Drop it only after a clean apply; otherwise keep it and report the conflict.
- Do not add AI attribution trailers to any commit.
- Report each branch, skipped work, push failures, and the actual output of `git log --oneline --graph dev | head -30`.
- For each skipped rebase or dev merge, explain why it was unsafe and the smallest next step before it can be integrated or pushed.
