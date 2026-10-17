#!/usr/bin/env python3
"""Offline PR with a misleading checkout and documented operational intent."""

import json
import sys
from pathlib import Path

from setup_bitbucket_review import create_fetch_shim, run_git, write


def main():
    workspace = Path(sys.argv[1])
    run_git(workspace, "init", "-q", "-b", "release")
    run_git(workspace, "config", "user.name", "Eval Fixture")
    run_git(workspace, "config", "user.email", "eval@example.invalid")
    write(workspace / "migrations/V1__base.sql", "CREATE TABLE jobs (id bigint PRIMARY KEY);\n")
    write(workspace / "OPERATIONS.md", """# Deployment and processing contract

Production and shared staging databases have applied only V1 from the release branch.
Feature branches are never deployed or migrated into shared databases.

Polling may be disabled in development and staging to avoid external side effects.
Production deployment configuration must enable polling. A disabled poller deliberately returns zero.
For enabled polling, handler exceptions must leave the cursor at the last successfully processed item.
The caller retries from the stored cursor after failure.
""")
    write(workspace / "src/worker.py", """def consume(batch, store, handler, poll_enabled=True):
    for item in batch:
        handler(item)
        store.save_cursor(item.id)
    return len(batch)
""")
    run_git(workspace, "add", ".")
    run_git(workspace, "commit", "-q", "-m", "Deployed release baseline")
    destination = run_git(workspace, "rev-parse", "HEAD")

    run_git(workspace, "checkout", "-q", "-b", "feature/draft-schema")
    write(workspace / "migrations/V2__jobs.sql", "ALTER TABLE jobs ADD COLUMN draft_label text;\n")
    run_git(workspace, "add", ".")
    run_git(workspace, "commit", "-q", "-m", "Unreleased draft schema")

    run_git(workspace, "checkout", "-q", "-b", "feature/pr", destination)
    write(workspace / "migrations/V2__jobs.sql", "ALTER TABLE jobs ADD COLUMN status text NOT NULL DEFAULT 'pending';\n")
    write(workspace / "deploy/production.env", "POLL_ENABLED=true\n")
    write(workspace / "deploy/staging.env", "POLL_ENABLED=false\n")
    write(workspace / "src/worker.py", """def consume(batch, store, handler, poll_enabled=True):
    if not poll_enabled:
        return 0
    for item in batch:
        store.save_cursor(item.id)
        handler(item)
    return len(batch)
""")
    run_git(workspace, "add", ".")
    run_git(workspace, "commit", "-q", "-m", "Prepare job schema and polling switch")
    source = run_git(workspace, "rev-parse", "HEAD")
    diff = run_git(workspace, "diff", destination, source) + "\n"
    run_git(workspace, "checkout", "-q", "feature/draft-schema")

    bundle = workspace / "bitbucket-review"
    metadata = {
        "id": 73, "title": "Prepare job processing", "state": "OPEN",
        "source": {"branch": {"name": "feature/pr"}, "commit": {"hash": source}},
        "destination": {"branch": {"name": "release"}, "commit": {"hash": destination}},
        "updated_on": "2026-10-01T10:00:00Z",
    }
    artifacts = {
        "metadata.json": metadata, "comments.json": [], "comments.raw.json": {"values": []},
        "commits.json": [{"hash": source, "message": "Prepare job schema and polling switch"}],
        "diffstat.json": [],
        "manifest.json": {"workspace": "example-workspace", "repository": "example-repo", "pr_id": 73, "source_commit": source, "complete": True},
    }
    for name, value in artifacts.items():
        write(bundle / name, json.dumps(value, indent=2) + "\n")
    write(bundle / "summary.md", f"""# PR #73: Prepare job processing

- Source: `{source}` (`feature/pr`)
- Destination: `{destination}` (`release`)
- Updated: `2026-10-01T10:00:00Z`
- Comments: 0

Adds the release-ready V2 migration and a poller switch. See OPERATIONS.md for deployment and processing contracts.
""")
    write(bundle / "diff.patch", diff)
    create_fetch_shim(workspace, {
        "allow_fetch": False, "expected_url": "https://bitbucket.org/example-workspace/example-repo/pull-requests/73",
        "expected_refresh": False, "bundle": str(bundle),
    })


if __name__ == "__main__":
    main()
