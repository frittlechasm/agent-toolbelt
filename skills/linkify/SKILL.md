---
name: linkify
description: Use to format repository and Jira links when a response cites commit, PR, ticket, or issue identifiers, or a file or line in a PR.
metadata:
    scope: global
    agents: claude, codex
    machines: all
---

Render commit hashes, PR, ticket, and issue IDs as links, keeping the short identifier as the link text:
`[a1b2c3d](...)`, `[#42](...)`, `[PROJ-123](...)`, or `[Service.java:262](...)` for a PR line.

- Build repository links from the current repository's remote, using that provider's URL format. Do not assume GitHub or Bitbucket.
- If the remote uses an SSH host alias, read local SSH config to find the real hostname.
- Bitbucket Cloud paths: `/commits/<hash>`, `/pull-requests/<id>`, `/pull-requests/<id>#comment-thread-<comment-id>`,
  and PR lines as `<pr-url>/diff#L<repo-relative-path>T<new-line>`. Use the repository that hosts the PR, even when its source branch is a fork.
- Link Jira keys such as `PROJ-123` to `<jira-site>/browse/PROJ-123`.

## Gotchas

- Never invent a repository, workspace, project, or Jira site. Leave the identifier as plain text when its target is unknown.
- Do not connect to a host just to format a link.
- Do not link ambiguous bare numbers.
