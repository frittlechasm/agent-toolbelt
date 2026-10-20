---
name: bitbucket
description: Use this for any read-only interaction with a specific Bitbucket Cloud PR.
metadata:
    scope: global
    agents: claude, codex
    machines: all
---

# Bitbucket PR Fetch

## Resolve PR URL

- Use a supplied Bitbucket Cloud PR URL directly.
- For a bare PR number, infer the workspace and repository if current repo has one `bitbucket.org` remote.
- If unable to resolve the URL, ask the user to provide one.

## Fetch or reuse the PR

- Call the script once at the start of a new session; it checks PR metadata and reuses the persistent bundle under `~/.bitbucket-reviews`:

    ```bash
    python <skill-dir>/scripts/fetch_pr.py "<pr-url>"
    ```

- Within the session, reuse its returned directory when continuing a review or checking existing comments.
- Add `--refresh` only when the user indicates new or updated comments or PR changes.
  The script cannot infer those prompt signals, and PR metadata may not reflect every comment change.

## Read the review bundle

- In the returned directory, read `summary.md` and any `review-summary.md` before evaluating the diff, comments, commits, or metadata.
  You may check `manifest.json` first for bundle identity, freshness, and completeness.
- `review-summary.md` holds prior finding IDs and the last completed assessment; it is not fetched from Bitbucket.
- Read comment thread state from `comments.json`'s `resolved`; a resolved thread's `resolution` can be `{}`, which Python treats as false.
  Use `comments.raw.json` when normalization omits a needed field.
- Use the bundle's detailed artifacts and checked-out source where relevant, subject to the revision checks below.

## Check revisions and deployment

- Read source and destination commit IDs from the bundle. Confirm the local revision before using checked-out files as evidence.
  - If the checkout differs, inspect the recorded revisions with Git.
- Compare against the PR's actual destination.
  - For merge-related claims, inspect the relevant parents and merge base.
  - A migration on another feature branch does not prove it was released or applied.
  - Verify deployment history before claiming migration immutability or checksum breakage.

## Validate findings

- For each defect, identify a reachable scenario, expected behavior, and the changed code that violates it.
  - Check product requirements, supported configurations, and data invariants before treating a hypothetical case as a bug.
- Respect documented operational intent, including non-production switches and deliberate restrictions.
  - If reachability or intent is unclear, state the uncertainty or ask a focused question instead of claiming a confirmed defect.
- On re-review, distinguish new defects from existing comments and resolved findings.
  - Recheck claims against the current source and destination revisions before carrying them forward.

## Record a completed review

- After a successful review, write `<output-directory>/review-summary.md` in the returned or reused bundle directory, never the repository or workspace root.
- The fetch script never creates, modifies, validates, or deletes this checkpoint.
- Treat it as a rolling checkpoint, not an append-only transcript:
    - Record `reviewed_at` as a UTC ISO 8601 timestamp, plus `source_commit`, `destination_commit`, `pr_updated_on`, and `comment_count` in YAML frontmatter.
    - Keep the current assessment and open findings. Preserve stable finding IDs across re-reviews.
    - Move verified fixed findings to a concise resolved section.
    - Append one compact row to a review history table for each completed review.
- On re-review, compare the checkpoint with current artifacts and carry forward unresolved findings.
- Prepare the complete replacement and replace it atomically; an interrupted review must leave the prior checkpoint intact.
