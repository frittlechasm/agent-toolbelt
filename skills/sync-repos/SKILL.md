---
name: sync-repos
description: Sync tracked code changes from one local git repository to another, including deletions while preserving target deploy.yml. Use this skill whenever the user wants to copy, mirror, or sync changes between two local repos, including phrases like "move changes to", "copy changes over", "sync the repo", or "mirror public to work".
---

# Sync Repos

## Workflow

### 1. Identify source and target

If either path is missing, ask. Verify both are git repos.

```bash
git -C <source> rev-parse --git-dir
git -C <target> rev-parse --git-dir
```

Check both worktrees before changing files. If the target has existing uncommitted changes, show them and ask before overwriting or deleting anything. Source changes may be synced as-is, but the user should see what is being copied.

```bash
git -C <source> status --short
git -C <target> status --short
```

### 2. Mirror tracked files

```bash
src=<source>
dst=<target>
src_list=$(mktemp)
dst_list=$(mktemp)

git -C "$src" ls-files | sort > "$src_list"
git -C "$dst" ls-files | sort > "$dst_list"

rsync -a --files-from="$src_list" "$src"/ "$dst"/

comm -13 "$src_list" "$dst_list" | while IFS= read -r rel; do
  [ "$rel" = "deploy.yml" ] && continue
  rm -f "$dst/$rel"
done

rm -f "$src_list" "$dst_list"
```

This mirrors source-tracked content and deletes target-tracked files that no longer exist in source. Preserve `deploy.yml` because the work repo needs it for deployment.

### 3. Stage and verify

```bash
git -C <target> add -A
git -C <target> status --short
git -C <target> diff --cached --stat
```

Also compare counts/content for source-tracked files:

```bash
git -C <source> ls-files | wc -l
git -C <target> ls-files | wc -l
git -C <source> ls-files | while IFS= read -r rel; do
  cmp -s "<source>/$rel" "<target>/$rel" || printf '%s\n' "$rel"
done
```

The target count may be one higher when `deploy.yml` exists only in target. Commit only when the user asks for a commit.

### 4. Ask before pushing

Push only after explicit approval.

```bash
git -C <target> show --stat HEAD
git -C <target> log -1 --pretty=format:"%s%n%n%b"
```
