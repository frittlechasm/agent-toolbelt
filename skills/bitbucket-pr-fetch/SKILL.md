---
name: bitbucket-pr-fetch
description: Use this for any read-only interaction with a specific Bitbucket Cloud PR.
metadata:
  scope: global
  agents: all
  machines: all
---

# Bitbucket PR Fetch

## Resolve PR URL

- Use a supplied Bitbucket Cloud PR URL directly.
- For a bare PR number, infer the workspace and repository if current repo has one `bitbucket.org` remote.
- If unable to resolve the URL, ask the user to provide one.

## Fetch the PR

- Reuse the output directory already returned in the current session.
- Do not call the script again merely to continue the same review or address another existing comment.
- Call the script once at the start of work in a new session.
- The script checks PR metadata and reuses the persistent bundle under `~/.bitbucket-reviews`.
- Format to call the script:

  ```bash
  python <skill-dir>/scripts/fetch_pr.py "<pr-url>"
  ```

- Add `--refresh` when the user's prompt says there are new or updated comments, or PR changes.
- The script cannot infer those prompt signals, and PR metadata may not reflect every comment change.
- Do not force a refresh for a re-review when the user has not indicated that the PR changed.

## Output

- Read the output directory printed by the script.
  - Start with `summary.md`.
  - Use `diff.patch` for code changes.
  - Use `comments.json` for review threads.
  - Use `comments.raw.json` when normalized comments omit a Bitbucket field.
  - Use `commits.json` for complete commit data.
  - Use `metadata.json` for complete PR data.
  - Use `diffstat.json` for file statistics.
  - Use `manifest.json` to verify bundle identity, freshness, and completeness.

- If `review-summary.md` exists in the output directory, read it before a review or re-review.
- It records the last completed review and is not a fetched Bitbucket artifact.

- Complete the requested task using the fetched artifacts and the checked-out repo where relevant.

## Record a completed review

- Create or update `review-summary.md` only after completing a review.
- The fetch script never creates, modifies, validates, or deletes `review-summary.md` file.
- Treat it as a rolling checkpoint, not an append-only transcript:
  - Record `reviewed_at` as a UTC ISO 8601 timestamp, plus `source_commit`, `destination_commit`, `pr_updated_on`, and `comment_count` in YAML frontmatter.
  - Keep the current assessment and open findings. Preserve stable finding IDs across re-reviews.
  - Move verified fixed findings to a concise resolved section.
  - Append one compact row to a review history table for each completed review.
- On a re-review, compare the checkpoint with the current fetched artifacts, carry forward unresolved findings, and update the file only when the review finishes successfully.
- Prepare the complete replacement before atomically replacing the file.
- An interrupted review must leave the prior checkpoint intact.
