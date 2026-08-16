#!/usr/bin/env python3
"""Fetch a Bitbucket Cloud pull request for code review.

Downloads everything a reviewer needs — PR metadata, the full unified diff,
the changed-files list, and existing comments — and writes them into a folder
under the system temp directory so a downstream review can read them.

Auth uses HTTP Basic with a Bitbucket app password, read from a .env file
(copy .env.example to .env). The file must define:
    BITBUCKET_USERNAME        your Atlassian/Bitbucket username (not email)
    BITBUCKET_APP_PASSWORD    an app password with "Pull requests: Read" and
                              "Repositories: Read" scopes

Only the Python standard library is used, so no `pip install` is required.

Usage:
    python fetch_pr.py <pr-url>
    python fetch_pr.py https://bitbucket.org/myteam/myrepo/pull-requests/42
    python fetch_pr.py <pr-url> --output-dir /custom/path
"""

import argparse
import base64
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request

API_BASE = "https://api.bitbucket.org/2.0"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
REAL_SKILL_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# Credentials, loaded from a .env file (the only credential source).
CREDS = {}


def read_env_file(path):
    """Return variables parsed from one .env file."""
    values = {}
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            if line.startswith("export "):
                line = line[len("export "):]
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                values[key] = value
    return values


def has_bitbucket_credentials(values):
    return bool(
        values.get("BITBUCKET_USERNAME")
        and values.get("BITBUCKET_APP_PASSWORD")
    )


def load_env_file(explicit_path=None):
    """Read credentials from the first usable .env file into CREDS.

    The .env file is the single source of credentials. Environment variables
    are intentionally not consulted. An explicit file must be complete. During
    automatic discovery, incomplete or unrelated .env files are skipped so a
    valid skill-level file can still be used.
    """
    CREDS.clear()

    if explicit_path:
        if not os.path.isfile(explicit_path):
            die(f"--env-file not found: {explicit_path}")
        values = read_env_file(explicit_path)
        if not has_bitbucket_credentials(values):
            die(
                "the --env-file must define BITBUCKET_USERNAME and "
                "BITBUCKET_APP_PASSWORD"
            )
        CREDS.update(values)
        return

    candidates = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(SKILL_DIR, ".env"),
    ]
    real_skill_env = os.path.join(REAL_SKILL_DIR, ".env")
    if real_skill_env not in candidates:
        candidates.append(real_skill_env)

    for path in candidates:
        if not os.path.isfile(path):
            continue
        values = read_env_file(path)
        if has_bitbucket_credentials(values):
            CREDS.update(values)
            return

    locations = ", ".join(dict.fromkeys(os.path.dirname(p) for p in candidates))
    die(
        "no usable .env file found. Copy .env.example to .env and define "
        "BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD, or pass "
        "--env-file <path>.\n"
        f"Looked in: {locations}"
    )

# Matches both the human URL (.../pull-requests/42) and minor variants
# (trailing slash, /diff, /commits, query strings, optional www).
URL_RE = re.compile(
    r"bitbucket\.org/"
    r"(?P<workspace>[^/]+)/"
    r"(?P<repo>[^/]+)/"
    r"pull-requests/"
    r"(?P<id>\d+)",
    re.IGNORECASE,
)


def die(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def parse_pr_url(url):
    match = URL_RE.search(url)
    if not match:
        die(
            "could not parse a Bitbucket Cloud PR URL from "
            f"{url!r}.\n"
            "Expected something like "
            "https://bitbucket.org/<workspace>/<repo>/pull-requests/<id>"
        )
    return match.group("workspace"), match.group("repo"), int(match.group("id"))


def auth_header():
    username = CREDS.get("BITBUCKET_USERNAME")
    app_password = CREDS.get("BITBUCKET_APP_PASSWORD")
    if not username or not app_password:
        die(
            "missing credentials. Your .env file must define BITBUCKET_USERNAME "
            "and BITBUCKET_APP_PASSWORD (see .env.example).\n"
            "Create an app password at "
            "https://bitbucket.org/account/settings/app-passwords/ with "
            '"Pull requests: Read" and "Repositories: Read" scopes.'
        )
    token = base64.b64encode(f"{username}:{app_password}".encode()).decode()
    return f"Basic {token}"


def request(url, accept="application/json"):
    """Make an authenticated GET request, returning the raw response body."""
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", auth_header())
    req.add_header("Accept", accept)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        if exc.code == 401:
            die("401 Unauthorized — check BITBUCKET_USERNAME / "
                "BITBUCKET_APP_PASSWORD.")
        if exc.code == 403:
            die("403 Forbidden — the app password lacks the required scopes, "
                "or you cannot access this repository.")
        if exc.code == 404:
            die("404 Not Found — the workspace, repository, or PR id is wrong, "
                "or you lack access to it.")
        die(f"HTTP {exc.code} from {url}\n{body}")
    except urllib.error.URLError as exc:
        die(f"network error contacting Bitbucket: {exc.reason}")


def get_json(url):
    return json.loads(request(url))


def get_paginated(url):
    """Follow Bitbucket's `next` links and collect all `values` entries."""
    results = []
    while url:
        page = get_json(url)
        results.extend(page.get("values", []))
        url = page.get("next")
    return results


def slugify(value):
    return re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-")


def fetch(workspace, repo, pr_id):
    base = f"{API_BASE}/repositories/{workspace}/{repo}/pullrequests/{pr_id}"

    print(f"Fetching PR #{pr_id} from {workspace}/{repo} ...", file=sys.stderr)

    metadata = get_json(base)
    diff = request(f"{base}/diff", accept="text/plain")
    diffstat = get_paginated(f"{base}/diffstat?pagelen=100")
    comments = get_paginated(f"{base}/comments?pagelen=100")
    commits = get_paginated(f"{base}/commits?pagelen=100")

    return {
        "metadata": metadata,
        "diff": diff,
        "diffstat": diffstat,
        "comments": comments,
        "commits": commits,
    }


def summarize_metadata(meta):
    """Pull the review-relevant fields out of the verbose API payload."""
    def name(obj):
        if not obj:
            return None
        return obj.get("display_name") or obj.get("nickname") or obj.get("uuid")

    return {
        "id": meta.get("id"),
        "title": meta.get("title"),
        "state": meta.get("state"),
        "author": name(meta.get("author")),
        "source_branch": (meta.get("source") or {}).get("branch", {}).get("name"),
        "destination_branch": (meta.get("destination") or {}).get("branch", {}).get("name"),
        "source_commit": (meta.get("source") or {}).get("commit", {}).get("hash"),
        "destination_commit": (meta.get("destination") or {}).get("commit", {}).get("hash"),
        "reviewers": [name(r) for r in meta.get("reviewers", [])],
        "created_on": meta.get("created_on"),
        "updated_on": meta.get("updated_on"),
        "comment_count": meta.get("comment_count"),
        "description": meta.get("description"),
        "url": (meta.get("links", {}).get("html") or {}).get("href"),
    }


def normalize_comments(comments):
    out = []
    for c in comments:
        if c.get("deleted"):
            continue
        inline = c.get("inline")
        out.append({
            "id": c.get("id"),
            "user": (c.get("user") or {}).get("display_name"),
            "created_on": c.get("created_on"),
            "content": (c.get("content") or {}).get("raw"),
            "inline": {
                "path": inline.get("path"),
                "from": inline.get("from"),
                "to": inline.get("to"),
            } if inline else None,
            "parent_id": (c.get("parent") or {}).get("id"),
        })
    return out


def normalize_diffstat(diffstat):
    out = []
    for d in diffstat:
        out.append({
            "status": d.get("status"),
            "lines_added": d.get("lines_added"),
            "lines_removed": d.get("lines_removed"),
            "old_path": (d.get("old") or {}).get("path"),
            "new_path": (d.get("new") or {}).get("path"),
        })
    return out


def write_summary(path, summary, files, comments, commits):
    lines = []
    lines.append(f"# PR #{summary['id']}: {summary['title']}")
    lines.append("")
    lines.append(f"- **State:** {summary['state']}")
    lines.append(f"- **Author:** {summary['author']}")
    lines.append(
        f"- **Branch:** `{summary['source_branch']}` → "
        f"`{summary['destination_branch']}`"
    )
    if summary.get("reviewers"):
        lines.append(f"- **Reviewers:** {', '.join(filter(None, summary['reviewers']))}")
    lines.append(f"- **URL:** {summary['url']}")
    lines.append("")

    if summary.get("description"):
        lines.append("## Description")
        lines.append("")
        lines.append(summary["description"])
        lines.append("")

    lines.append(f"## Changed files ({len(files)})")
    lines.append("")
    for f in files:
        path_label = f["new_path"] or f["old_path"]
        lines.append(
            f"- `{path_label}` — {f['status']} "
            f"(+{f['lines_added'] or 0}/-{f['lines_removed'] or 0})"
        )
    lines.append("")

    lines.append(f"## Commits ({len(commits)})")
    lines.append("")
    for c in commits:
        message = (c.get("message") or "").strip().splitlines()
        first = message[0] if message else ""
        lines.append(f"- `{c.get('hash', '')[:12]}` {first}")
    lines.append("")

    lines.append(f"## Existing comments ({len(comments)})")
    lines.append("")
    if not comments:
        lines.append("_None._")
    for c in comments:
        loc = ""
        if c.get("inline"):
            loc = f" [{c['inline']['path']}:{c['inline'].get('to') or c['inline'].get('from')}]"
        lines.append(f"- **{c['user']}**{loc}: {c['content']}")
    lines.append("")

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(
        description="Fetch a Bitbucket Cloud PR for code review."
    )
    parser.add_argument(
        "url",
        nargs="?",
        help="Bitbucket Cloud PR URL "
             "(https://bitbucket.org/<workspace>/<repo>/pull-requests/<id>)",
    )
    parser.add_argument(
        "--output-dir",
        help="Directory to write into. Defaults to a folder under the system "
             "temp directory.",
    )
    parser.add_argument(
        "--env-file",
        help="Path to the .env file with BITBUCKET_USERNAME / "
             "BITBUCKET_APP_PASSWORD. Defaults to .env in the current "
             "directory, then the skill directory.",
    )
    args = parser.parse_args()

    load_env_file(args.env_file)

    if not args.url:
        die("no PR URL provided. Pass the Bitbucket PR URL as the first "
            "argument, e.g.\n"
            "  python fetch_pr.py "
            "https://bitbucket.org/<workspace>/<repo>/pull-requests/<id>")

    workspace, repo, pr_id = parse_pr_url(args.url)
    data = fetch(workspace, repo, pr_id)

    summary = summarize_metadata(data["metadata"])
    files = normalize_diffstat(data["diffstat"])
    comments = normalize_comments(data["comments"])

    if args.output_dir:
        out_dir = args.output_dir
    else:
        folder = f"bitbucket-pr-{slugify(workspace)}-{slugify(repo)}-{pr_id}"
        out_dir = os.path.join(tempfile.gettempdir(), folder)
    os.makedirs(out_dir, exist_ok=True)

    # Full raw metadata, for anything the summary leaves out.
    with open(os.path.join(out_dir, "metadata.json"), "w", encoding="utf-8") as fh:
        json.dump(
            {"summary": summary, "raw": data["metadata"]},
            fh, indent=2, ensure_ascii=False,
        )

    with open(os.path.join(out_dir, "diff.patch"), "w", encoding="utf-8") as fh:
        fh.write(data["diff"])

    with open(os.path.join(out_dir, "diffstat.json"), "w", encoding="utf-8") as fh:
        json.dump(files, fh, indent=2, ensure_ascii=False)

    with open(os.path.join(out_dir, "comments.json"), "w", encoding="utf-8") as fh:
        json.dump(comments, fh, indent=2, ensure_ascii=False)

    write_summary(
        os.path.join(out_dir, "summary.md"),
        summary, files, comments, data["commits"],
    )

    print(f"\nFetched PR #{pr_id}: {summary['title']}", file=sys.stderr)
    print(f"  {len(files)} changed file(s), {len(comments)} comment(s), "
          f"{len(data['commits'])} commit(s)", file=sys.stderr)
    print(f"\nSaved to: {out_dir}", file=sys.stderr)
    print(out_dir)  # stdout: the path, so callers can capture it


if __name__ == "__main__":
    main()
