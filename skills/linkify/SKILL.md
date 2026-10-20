---
name: linkify
description: Use to resolve and format repository and Jira links when a response cites commit, PR, ticket, or issue identifiers.
metadata:
    scope: global
    agents: claude, codex
    machines: all
---

- Render commit hashes, pull request IDs, ticket IDs, and issue IDs as clickable links
- Resolve repository links from the current repository's remote URL.
- If the remote uses an SSH host alias, resolve its actual hostname from local configuration read-only
- For Bitbucket Cloud:
    - link commits to `/commits/<hash>`
    - pull requests to `/pull-requests/<id>`
    - comments to `/pull-requests/<id>#comment-thread-<comment-id>`
- Link Jira issue keys such as `PROJ-123` to the matching Jira Cloud `/browse/PROJ-123` URL.
- Preserve the concise identifier as the link text, for example `[a1b2c3d](...)`, `[#42](...)`, and `[PROJ-123](...)`.

## Gotchas:

- Never fabricate a repository, workspace, project, or Jira site URL.
- Leave the identifier as plain text when its target cannot be established.
- Do not connect to the host just to format a link.
- Use the matching source-control provider rather than assuming GitHub or Bitbucket.
- Do not link ambiguous bare numbers.
