#!/usr/bin/env python3
"""Fetch a Bitbucket Cloud pull request for code review.

Downloads everything a reviewer needs and writes a validated bundle under
~/.bitbucket-reviews. Later calls fetch only PR metadata and reuse an unchanged
bundle across sessions. Use --refresh to force a complete download.

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
    python fetch_pr.py <pr-url> --refresh
"""

import argparse
import base64
import contextlib
import datetime
import fcntl
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request

API_BASE = "https://api.bitbucket.org/2.0"
CACHE_SCHEMA_VERSION = 2
ARTIFACT_NAMES = (
    "summary.md",
    "metadata.json",
    "diff.patch",
    "diffstat.json",
    "comments.json",
    "comments.raw.json",
    "commits.json",
)

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
    return (
        cache_segment(match.group("workspace"), "workspace"),
        cache_segment(match.group("repo"), "repository"),
        int(match.group("id")),
    )


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


def cache_segment(value, label):
    """Return one safe, canonical segment for the persistent cache path."""
    segment = value.lower()
    if (
        segment in {".", ".."}
        or not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", segment)
    ):
        die(f"invalid {label} in PR URL: {value!r}")
    return segment


def default_output_dir(workspace, repo, pr_id):
    cache_root = os.path.join(os.path.expanduser("~"), ".bitbucket-reviews")
    os.makedirs(cache_root, mode=0o700, exist_ok=True)
    try:
        os.chmod(cache_root, 0o700)
    except OSError as exc:
        die(f"could not secure cache directory {cache_root}: {exc}")
    return os.path.join(
        cache_root,
        cache_segment(workspace, "workspace"),
        cache_segment(repo, "repository"),
        f"pr-{pr_id}",
    )


def pr_api_url(workspace, repo, pr_id):
    return f"{API_BASE}/repositories/{workspace}/{repo}/pullrequests/{pr_id}"


def fetch(workspace, repo, pr_id, metadata=None):
    base = pr_api_url(workspace, repo, pr_id)

    print(f"Fetching PR #{pr_id} from {workspace}/{repo} ...", file=sys.stderr)

    if metadata is None:
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
            "updated_on": c.get("updated_on"),
            "content": (c.get("content") or {}).get("raw"),
            "resolution": c.get("resolution"),
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


def freshness_fields(meta):
    """Return the remote fields that determine whether a bundle is current."""
    source = meta.get("source") or {}
    destination = meta.get("destination") or {}
    return {
        "id": meta.get("id"),
        "state": meta.get("state"),
        "source_commit": (source.get("commit") or {}).get("hash"),
        "destination_commit": (destination.get("commit") or {}).get("hash"),
        "updated_on": meta.get("updated_on"),
        "comment_count": meta.get("comment_count"),
    }


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_manifest(out_dir):
    path = os.path.join(out_dir, "manifest.json")
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError, TypeError):
        return None


def cache_is_complete(out_dir, workspace, repo, pr_id, manifest):
    if not manifest or manifest.get("schema_version") != CACHE_SCHEMA_VERSION:
        return False
    if manifest.get("pr") != {
        "workspace": workspace,
        "repository": repo,
        "id": pr_id,
    }:
        return False

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict) or set(artifacts) != set(ARTIFACT_NAMES):
        return False

    for name in ARTIFACT_NAMES:
        details = artifacts.get(name)
        path = os.path.join(out_dir, name)
        if not isinstance(details, dict) or not os.path.isfile(path):
            return False
        try:
            if os.path.getsize(path) != details.get("size"):
                return False
            if sha256_file(path) != details.get("sha256"):
                return False
        except OSError:
            return False
    return True


@contextlib.contextmanager
def pr_lock(out_dir):
    """Serialize cache checks and writes for one output directory."""
    lock_path = f"{out_dir}.lock"
    os.makedirs(os.path.dirname(os.path.abspath(lock_path)), exist_ok=True)
    with open(lock_path, "a+", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def write_json(path, value):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(value, fh, indent=2, ensure_ascii=False)


def write_bundle(out_dir, workspace, repo, pr_id, data):
    """Stage a complete bundle, then publish each artifact and manifest."""
    summary = summarize_metadata(data["metadata"])
    files = normalize_diffstat(data["diffstat"])
    comments = normalize_comments(data["comments"])

    parent = os.path.dirname(os.path.abspath(out_dir))
    os.makedirs(parent, exist_ok=True)
    staging = tempfile.mkdtemp(
        prefix=f".{os.path.basename(out_dir)}-",
        dir=parent,
    )
    try:
        write_json(
            os.path.join(staging, "metadata.json"),
            {"summary": summary, "raw": data["metadata"]},
        )
        with open(os.path.join(staging, "diff.patch"), "w", encoding="utf-8") as fh:
            fh.write(data["diff"])
        write_json(os.path.join(staging, "diffstat.json"), files)
        write_json(os.path.join(staging, "comments.json"), comments)
        write_json(os.path.join(staging, "comments.raw.json"), data["comments"])
        write_json(os.path.join(staging, "commits.json"), data["commits"])
        write_summary(
            os.path.join(staging, "summary.md"),
            summary, files, comments, data["commits"],
        )

        artifacts = {}
        for name in ARTIFACT_NAMES:
            path = os.path.join(staging, name)
            artifacts[name] = {
                "size": os.path.getsize(path),
                "sha256": sha256_file(path),
            }

        manifest = {
            "schema_version": CACHE_SCHEMA_VERSION,
            "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "pr": {
                "workspace": workspace,
                "repository": repo,
                "id": pr_id,
            },
            "url": (
                f"https://bitbucket.org/{workspace}/{repo}/pull-requests/{pr_id}"
            ),
            "freshness": freshness_fields(data["metadata"]),
            "artifacts": artifacts,
        }
        write_json(os.path.join(staging, "manifest.json"), manifest)

        os.makedirs(out_dir, exist_ok=True)
        for name in ARTIFACT_NAMES:
            os.replace(os.path.join(staging, name), os.path.join(out_dir, name))
        # Publish the manifest last. Its hashes describe the files now in place.
        os.replace(
            os.path.join(staging, "manifest.json"),
            os.path.join(out_dir, "manifest.json"),
        )
    finally:
        shutil.rmtree(staging, ignore_errors=True)

    return summary, files, comments


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
    # Cached PR data can contain private source code and review comments.
    os.umask(0o077)

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
        help="Directory to write into. Defaults to "
             "~/.bitbucket-reviews/<workspace>/<repository>/pr-<id>.",
    )
    parser.add_argument(
        "--env-file",
        help="Path to the .env file with BITBUCKET_USERNAME / "
             "BITBUCKET_APP_PASSWORD. Defaults to .env in the current "
             "directory, then the skill directory.",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force a full download instead of reusing an unchanged cache.",
    )
    args = parser.parse_args()

    load_env_file(args.env_file)

    if not args.url:
        die("no PR URL provided. Pass the Bitbucket PR URL as the first "
            "argument, e.g.\n"
            "  python fetch_pr.py "
            "https://bitbucket.org/<workspace>/<repo>/pull-requests/<id>")

    workspace, repo, pr_id = parse_pr_url(args.url)

    if args.output_dir:
        out_dir = os.path.abspath(os.path.expanduser(args.output_dir))
    else:
        out_dir = default_output_dir(workspace, repo, pr_id)

    with pr_lock(out_dir):
        manifest = read_manifest(out_dir)
        complete = cache_is_complete(
            out_dir, workspace, repo, pr_id, manifest,
        )
        remote_metadata = None
        if complete and not args.refresh:
            print(
                f"Checking PR #{pr_id} for changes in {workspace}/{repo} ...",
                file=sys.stderr,
            )
            remote_metadata = get_json(pr_api_url(workspace, repo, pr_id))
            if manifest.get("freshness") == freshness_fields(remote_metadata):
                print(f"\nReusing unchanged PR #{pr_id} cache", file=sys.stderr)
                print(f"  Cached at: {manifest.get('fetched_at')}", file=sys.stderr)
                print(f"\nSaved to: {out_dir}", file=sys.stderr)
                print(out_dir)
                return

        data = fetch(workspace, repo, pr_id, metadata=remote_metadata)
        summary, files, comments = write_bundle(
            out_dir, workspace, repo, pr_id, data,
        )

        print(f"\nFetched PR #{pr_id}: {summary['title']}", file=sys.stderr)
        print(f"  {len(files)} changed file(s), {len(comments)} comment(s), "
              f"{len(data['commits'])} commit(s)", file=sys.stderr)
        print(f"\nSaved to: {out_dir}", file=sys.stderr)
    print(out_dir)  # stdout: the path, so callers can capture it


if __name__ == "__main__":
    main()
