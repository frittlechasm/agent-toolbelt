---
name: bitbucket-pr-fetch
description: Use this skill to pull a specific Bitbucket Cloud pull request into the local session before doing anything with it — its diff, changed files, metadata, commits, and comments (inline and general). This is the required first step whenever a user references one particular Bitbucket PR — by number, by id in a workspace/repo, or via a pasted bitbucket.org/.../pull-requests/ URL — and wants to work with its contents: grab it, snag it, get it, fetch it, download it, look through it, read its comments, or review it against the repo they have checked out. The verb and the stated reason don't matter; if a specific Bitbucket PR is named and its data isn't local yet, run this skill to retrieve it first. Not for GitHub or GitLab, self-hosted Bitbucket Server/Data Center, listing or searching many PRs, cloning repos, or creating/merging/commenting on a PR.
---

# Bitbucket PR Fetch

Fetch a single Bitbucket **Cloud** pull request and write everything a reviewer
needs into a folder under the system temp directory. This skill only **fetches**
— reviewing the PR against the local codebase is a separate step (handled by a
review skill or by you directly, reading the files this produces).

## What it fetches

Running the script produces, for one PR:

- **`summary.md`** — a human/AI-readable overview: title, state, author,
  branches, description, changed files, commits, and existing comments. Read
  this first.
- **`metadata.json`** — the cleaned `summary` fields plus the full raw API
  payload (for anything the summary omits).
- **`diff.patch`** — the complete unified diff of the PR.
- **`diffstat.json`** — changed files with per-file add/modify/delete status and
  line counts.
- **`comments.json`** — existing PR comments (inline and general), with file/line
  location where applicable.

## Prerequisites

The script authenticates with a Bitbucket **app password** over HTTP Basic auth,
read from a **`.env` file** (environment variables are not used). Copy
`.env.example` to `.env` and fill in:

| Variable | Value |
| --- | --- |
| `BITBUCKET_USERNAME` | Your Bitbucket username (the username, not your email) |
| `BITBUCKET_APP_PASSWORD` | An app password with **Pull requests: Read** and **Repositories: Read** scopes |

The script looks for `.env` in the current directory, then in the skill
directory, or wherever you point it with `--env-file <path>`. The real `.env`
is gitignored so credentials aren't committed.

Create an app password at
<https://bitbucket.org/account/settings/app-passwords/>. If no `.env` is found,
or a credential is missing, the script stops and explains exactly what to set.

Only the Python standard library is used, so there is nothing to `pip install`.

## How to use

1. **Get the PR URL.** The user normally provides it. It looks like:
   `https://bitbucket.org/<workspace>/<repo>/pull-requests/<id>`.
   **If the user has not given you a PR URL, ask for it before running** —
   don't guess a workspace, repo, or id.

2. **Run the script**, passing the URL as the first argument:

   ```bash
   python <skill-dir>/scripts/fetch_pr.py "https://bitbucket.org/<workspace>/<repo>/pull-requests/<id>"
   ```

   The script prints the output folder path to stdout (and a progress summary to
   stderr). Capture that path — the review step reads from it.

3. **Confirm and hand off.** Tell the user where the data landed (the path under
   the temp dir) and give a one-line summary from `summary.md`. The PR is now
   ready to be reviewed against the checked-out codebase.

### Options

- `--output-dir <path>` — write into a specific directory instead of the default
  temp-dir folder (`<tmp>/bitbucket-pr-<workspace>-<repo>-<id>`).

## Notes & troubleshooting

- **Only Bitbucket Cloud** (`bitbucket.org`) is supported. Self-hosted Bitbucket
  Server / Data Center uses a different REST API and won't work here.
- **401 Unauthorized** → check `BITBUCKET_USERNAME` / `BITBUCKET_APP_PASSWORD`.
  Use the username, not the email address.
- **403 Forbidden** → the app password is missing the read scopes, or you don't
  have access to that repository.
- **404 Not Found** → the workspace/repo/id in the URL is wrong, or you lack
  access to the PR.
- Pagination is handled automatically, so large PRs return all changed files and
  all comments, not just the first page.
