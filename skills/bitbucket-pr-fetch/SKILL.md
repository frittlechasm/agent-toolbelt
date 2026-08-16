---
name: bitbucket-pr-fetch
description: Use this for any read-only interaction with a specific Bitbucket Cloud PR.
---

# Bitbucket PR Fetch

## Resolve PR URL

- Use a supplied Bitbucket Cloud PR URL directly.
- For a bare PR number, infer the workspace and repository only when the
  checked-out repository has one unambiguous `bitbucket.org` remote.
- If unable to resolve the URL, ask the user to provide one.

## Fetch the PR

- Call the script:

  ```bash
  python <skill-dir>/scripts/fetch_pr.py "<pr-url>"
  ```

## Output

- Read the output directory printed by the script.
  - Start with `summary.md`.
  - Use `diff.patch` for code changes.
  - Use `comments.json` for review threads.
  - Use `metadata.json` for complete PR data.
  - Use `diffstat.json` for file statistics.

- Complete the user's requested read-only task using the fetched artifacts and
  the checked-out repository where relevant.
