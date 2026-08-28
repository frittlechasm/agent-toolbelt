#!/usr/bin/env python3
"""Create an offline Bitbucket review bundle and a narrow fetch shim."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


WORKSPACE = "example-workspace"
REPOSITORY = "example-repo"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_git(workspace: Path, *args: str) -> None:
    result = subprocess.run(
        ["git", *args], cwd=workspace, text=True, capture_output=True, check=False
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())


def create_repository(workspace: Path, add_remote: bool, scenario: str) -> None:
    audit_parameter = "request_id" if scenario in {"refresh", "existing"} else "token"
    write(
        workspace / "src/access.py",
        f"""def can_view(user, resource):
    if user.role == "admin":
        return True
    return resource.owner_id == user.id


def audit_view(logger, user, {audit_parameter}):
    logger.info("resource viewed", extra={{"user_id": user.id, "{audit_parameter}": {audit_parameter}}})
""",
    )
    write(
        workspace / "tests/test_access.py",
        """def test_owner_can_view():
    assert True

# No test defines which resources an administrator may view.
""",
    )
    run_git(workspace, "init", "-q", "-b", "main")
    run_git(workspace, "config", "user.name", "Eval Fixture")
    run_git(workspace, "config", "user.email", "eval@example.invalid")
    run_git(workspace, "add", "src/access.py", "tests/test_access.py")
    run_git(workspace, "commit", "-q", "-m", "Add PR head fixture")
    if add_remote:
        run_git(
            workspace,
            "remote",
            "add",
            "origin",
            f"git@bitbucket.org:{WORKSPACE}/{REPOSITORY}.git",
        )


def bundle_files(pr_number: int, scenario: str) -> dict[str, str]:
    commit_marker = {"refresh": "b", "existing": "c"}.get(scenario, "a")
    source_commit = commit_marker * 40
    summary = f"""# PR #{pr_number}: Tighten resource access

- Source: `{source_commit}`
- Destination: `{'d' * 40}`
- Updated: `2026-08-28T13:30:00Z`
- Comments: 1

The PR changes administrator access and request audit logging in `src/access.py`.
"""
    if scenario in {"refresh", "existing"}:
        diff = """diff --git a/src/access.py b/src/access.py
@@
 def can_view(user, resource):
     if user.role == "admin":
         return True
     return resource.owner_id == user.id
@@
-def audit_view(logger, user, token):
-    logger.info("resource viewed", extra={"user_id": user.id, "token": token})
+def audit_view(logger, user, request_id):
+    logger.info("resource viewed", extra={"user_id": user.id, "request_id": request_id})
"""
    else:
        diff = """diff --git a/src/access.py b/src/access.py
@@
+def can_view(user, resource):
+    if user.role == "admin":
+        return True
+    return resource.owner_id == user.id
+
+
+def audit_view(logger, user, token):
+    logger.info("resource viewed", extra={"user_id": user.id, "token": token})
"""
    comments = [
        {
            "id": 501,
            "user": "maintainer",
            "created_on": "2026-08-28T13:35:00Z",
            "content": "Administrator scope still needs an explicit policy and test.",
        }
    ]
    metadata = {
        "id": pr_number,
        "title": "Tighten resource access",
        "state": "OPEN",
        "source": {"commit": {"hash": source_commit}},
        "destination": {"commit": {"hash": "d" * 40}},
        "updated_on": "2026-08-28T13:30:00Z",
    }
    return {
        "summary.md": summary,
        "diff.patch": diff,
        "comments.json": json.dumps(comments, indent=2) + "\n",
        "comments.raw.json": json.dumps({"values": comments}, indent=2) + "\n",
        "commits.json": json.dumps([{"hash": source_commit, "message": "Update access rules"}], indent=2) + "\n",
        "metadata.json": json.dumps(metadata, indent=2) + "\n",
        "diffstat.json": json.dumps([{"new": {"path": "src/access.py"}, "lines_added": 8}], indent=2) + "\n",
        "manifest.json": json.dumps(
            {
                "workspace": WORKSPACE,
                "repository": REPOSITORY,
                "pr_id": pr_number,
                "source_commit": source_commit,
                "complete": True,
            },
            indent=2,
        )
        + "\n",
    }


def prior_checkpoint() -> str:
    return f"""---
reviewed_at: 2026-08-27T12:00:00Z
source_commit: {'a' * 40}
destination_commit: {'d' * 40}
pr_updated_on: 2026-08-27T11:30:00Z
comment_count: 0
---

# Current assessment

- **AUTH-1** Open: administrator access has no documented resource boundary or focused test.
- **LOG-1** Open: audit logging records a value named `token`.

## Review history

| Reviewed at | Source | Result |
| --- | --- | --- |
| 2026-08-27T12:00:00Z | `{'a' * 12}` | 2 open |
"""


def existing_checkpoint() -> str:
    return f"""---
reviewed_at: 2026-08-28T10:00:00Z
source_commit: {'c' * 40}
destination_commit: {'d' * 40}
pr_updated_on: 2026-08-28T09:30:00Z
comment_count: 0
---

# Current assessment

- **LOG-1** Open: `request_id` may contain a credential.

## Review history

| Reviewed at | Source | Result |
| --- | --- | --- |
| 2026-08-28T10:00:00Z | `{'c' * 12}` | 1 open |
"""


def create_bundle(bundle: Path, pr_number: int, scenario: str) -> None:
    for relative, content in bundle_files(pr_number, scenario).items():
        write(bundle / relative, content)
    if scenario == "refresh":
        write(bundle / "review-summary.md", prior_checkpoint())
    if scenario == "existing":
        write(bundle / "review-summary.md", existing_checkpoint())
        write(
            bundle / "comments.json",
            json.dumps(
                [
                    {
                        "id": 601,
                        "user": "author",
                        "created_on": "2026-08-28T11:00:00Z",
                        "content": "request_id is generated per request and is never an authentication credential.",
                    }
                ],
                indent=2,
            )
            + "\n",
        )


def create_fetch_shim(workspace: Path, policy: dict) -> None:
    control = workspace / ".eval"
    write(control / "fetch-policy.json", json.dumps(policy, indent=2) + "\n")
    fetch_script = Path(__file__).resolve().parents[2] / "scripts" / "fetch_pr.py"
    shim = f'''#!{sys.executable}
import json
import os
import sys
from pathlib import Path

REAL_PYTHON = {str(Path(sys.executable).resolve())!r}
FETCH_SCRIPT = {str(fetch_script.resolve())!r}
workspace = Path(__file__).resolve().parents[2]

if len(sys.argv) > 1 and str(Path(sys.argv[1]).resolve()) == FETCH_SCRIPT:
    policy = json.loads((workspace / ".eval/fetch-policy.json").read_text())
    log = workspace / ".eval/fetch-calls.jsonl"
    previous = log.read_text().splitlines() if log.exists() else []
    with log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({{"args": sys.argv[2:]}}) + "\\n")
    args = sys.argv[2:]
    refresh = "--refresh" in args
    urls = [arg for arg in args if arg != "--refresh"]
    valid = (
        policy["allow_fetch"]
        and not previous
        and urls == [policy["expected_url"]]
        and refresh == policy["expected_refresh"]
    )
    if not valid:
        print("fixture rejected unexpected Bitbucket fetch", file=sys.stderr)
        raise SystemExit(64)
    print(policy["bundle"])
    raise SystemExit(0)

os.execv(REAL_PYTHON, [REAL_PYTHON, *sys.argv[1:]])
'''
    for name in ("python", "python3"):
        path = control / "bin" / name
        write(path, shim)
        path.chmod(0o755)


def main() -> None:
    scenario = sys.argv[1]
    workspace = Path(sys.argv[2])
    if scenario not in {"new-url", "bare-number", "refresh", "existing", "unresolvable"}:
        raise RuntimeError(f"unknown scenario: {scenario}")

    pr_number = 184 if scenario == "bare-number" else 42
    url = f"https://bitbucket.org/{WORKSPACE}/{REPOSITORY}/pull-requests/{pr_number}"
    if scenario != "unresolvable":
        create_repository(workspace, scenario == "bare-number", scenario)

    bundle = workspace / ("bitbucket-review" if scenario == "existing" else ".eval/bundle")
    if scenario != "unresolvable":
        create_bundle(bundle, pr_number, scenario)

    create_fetch_shim(
        workspace,
        {
            "allow_fetch": scenario in {"new-url", "bare-number", "refresh"},
            "expected_url": url,
            "expected_refresh": scenario == "refresh",
            "bundle": str(bundle),
        },
    )


if __name__ == "__main__":
    main()
