---
name: bitbucket
description: Use only for any read-only interaction with a specific Bitbucket Cloud PR.
metadata:
    scope: global
    agents: claude, codex
    machines: all
---

# Bitbucket PR Review

## Fetch

- Use a supplied PR URL. For a bare PR number, build the URL from the repo's single `bitbucket.org` remote; otherwise ask for the URL.
- Run the fetch script once per session. It reuses the cached bundle under `~/.bitbucket-reviews` when PR metadata is unchanged:

    ```bash
    python <skill-dir>/scripts/fetch_pr.py "<pr-url>"
    ```

- Later in the session, reuse the returned directory instead of fetching again.
- Add `--refresh` only when the user says the PR or its comments changed; metadata does not catch every comment change.

## Read the bundle

- Read `summary.md` and any `review-summary.md` first. `manifest.json` shows bundle identity and freshness.
- `review-summary.md` is your prior review, not Bitbucket data.
- Read thread state from `resolved` in `comments.json`; a resolved thread's `resolution` can be `{}`, which is falsy in Python.
  Use `comments.raw.json` for fields that normalization drops.

## Check revisions

- Read the source and destination commits from the bundle. Confirm the checkout matches before using local files as evidence.
  If it differs, inspect the recorded revisions with Git without changing the checkout.
- Compare against the PR's real destination. For merge claims, check the parents and merge base.
- A migration on another branch was not necessarily released. Check deployment history before claiming migration immutability or checksum breakage.

## Validate findings

- On re-review, separate new defects from existing comments and resolved findings, and recheck carried-forward claims against current revisions.

## Record the review

After a completed review, write `review-summary.md` in the bundle directory, never the repository.
Replace it atomically so an interrupted review keeps the previous one:

- YAML frontmatter: `reviewed_at` (UTC ISO 8601), `source_commit`, `destination_commit`, `pr_updated_on`, and `comment_count`.
- The current assessment and open findings with stable IDs. Move verified fixes to a short resolved section.
- One compact row per completed review in a history table.
