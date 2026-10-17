---
name: bitbucket-pr-fetch
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

## Read the review bundle

- Read the output directory printed by the script.
    - You may verify `manifest.json` first to confirm bundle identity and completeness.
    - Then read `summary.md` and, when present, `review-summary.md` before evaluating `diff.patch`, comments, commits, or metadata.
    - Use `diff.patch` for code changes.
    - Use `comments.json` for review threads.
    - Read comment thread state from `resolved`; a resolved thread's `resolution` can be `{}`, which Python treats as false.
    - Use `comments.raw.json` when normalized comments omit a Bitbucket field.
    - Use `commits.json` for complete commit data.
    - Use `metadata.json` for complete PR data.
    - Use `diffstat.json` for file statistics.
    - Use `manifest.json` to verify bundle identity, freshness, and completeness.

- Use `review-summary.md` for prior finding IDs and assessment state. It records the last completed review and is not a fetched artifact.

- Complete the requested task using the fetched artifacts and the checked-out repo where relevant.

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

- Create or update `review-summary.md` only after completing a review.
- Store it as `<output-directory>/review-summary.md`, where `<output-directory>` is the path printed by `fetch_pr.py` or reused from earlier in the session.
- Never create the file in the repository or workspace root.
- The fetch script never creates, modifies, validates, or deletes `review-summary.md` file.
- Treat it as a rolling checkpoint, not an append-only transcript:
    - Record `reviewed_at` as a UTC ISO 8601 timestamp, plus `source_commit`, `destination_commit`, `pr_updated_on`, and `comment_count` in YAML frontmatter.
    - Keep the current assessment and open findings. Preserve stable finding IDs across re-reviews.
    - Move verified fixed findings to a concise resolved section.
    - Append one compact row to a review history table for each completed review.
- On re-review, compare the checkpoint with current artifacts and carry forward unresolved findings.
    - Update the file only after the review succeeds.
- Prepare the complete replacement before atomically replacing the file.
- An interrupted review must leave the prior checkpoint intact.
