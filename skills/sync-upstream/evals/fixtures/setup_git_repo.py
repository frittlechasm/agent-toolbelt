#!/usr/bin/env python3
"""Create isolated fork topologies for sync-upstream workflow evals."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


SCENARIOS = {
    "success",
    "diverged-main",
    "rebase-conflict",
    "dirty-worktree",
    "unique-dev",
    "dev-merge-conflict",
    "corrupt-rebase",
}
GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_DATE": "2026-08-28T19:00:00+05:30",
    "GIT_COMMITTER_DATE": "2026-08-28T19:00:00+05:30",
}


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        env=GIT_ENV,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout.strip()


def write(repo: Path, relative: str, content: str) -> None:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def commit_file(repo: Path, relative: str, content: str, message: str) -> str:
    write(repo, relative, content)
    git(repo, "add", relative)
    git(repo, "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def configure_repository(repo: Path) -> None:
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.name", "Eval Fixture")
    git(repo, "config", "user.email", "eval@example.invalid")
    git(repo, "config", "core.editor", "true")
    git(repo, "config", "sequence.editor", "true")
    git(repo, "config", "protocol.file.allow", "always")
    write(repo, ".git/info/exclude", ".eval/\n")


def base_files(repo: Path, scenario: str) -> None:
    write(repo, "README.md", "# Fork fixture\n")
    write(repo, "config.txt", "mode=base\n")
    write(repo, "notes.txt", "shared notes\n")
    if scenario == "rebase-conflict":
        write(
            repo,
            "PATCH.md",
            "During auth-refresh rebases, retain upstream mode and the branch's auth_refresh flag.\n",
        )
        write(
            repo,
            "docs/branch-auth-refresh.md",
            "Resolve config.txt as exactly: mode=upstream followed by auth_refresh=true.\n",
        )
    if scenario == "dev-merge-conflict":
        write(
            repo,
            "PATCH.md",
            "feature/a and feature/b select mutually exclusive modes. A conflict has no safe combined value; abort that dev merge.\n",
        )
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "Base fork")


def configure_remotes(repo: Path) -> tuple[Path, Path]:
    remotes = repo / ".eval" / "remotes"
    origin = remotes / "origin.git"
    upstream = remotes / "upstream.git"
    origin.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "--bare", "-q", str(origin)], check=True)
    subprocess.run(["git", "init", "--bare", "-q", str(upstream)], check=True)

    origin_url = "https://github.com/eval/fork.git"
    upstream_url = "https://github.com/eval/upstream.git"
    git(repo, "config", f"url.file://{origin}.insteadOf", origin_url)
    git(repo, "config", f"url.file://{upstream}.insteadOf", upstream_url)
    git(repo, "remote", "add", "origin", origin_url)
    git(repo, "remote", "add", "upstream", upstream_url)
    git(repo, "push", "-q", "-u", "origin", "main")
    git(repo, "push", "-q", "upstream", "main")
    return origin, upstream


def add_upstream_commit(repo: Path, scenario: str, base: str) -> str:
    if scenario == "rebase-conflict":
        commit_file(repo, "config.txt", "mode=upstream\n", "Change upstream mode")
    else:
        commit_file(repo, "upstream.txt", "upstream release\n", "Advance upstream")
    upstream_commit = git(repo, "rev-parse", "HEAD")
    git(repo, "push", "-q", "upstream", "main")
    git(repo, "reset", "--hard", "-q", base)
    return upstream_commit


def feature(repo: Path, name: str, relative: str, content: str, message: str) -> None:
    git(repo, "checkout", "-q", "main")
    git(repo, "checkout", "-q", "-b", name)
    commit_file(repo, relative, content, message)
    git(repo, "push", "-q", "-u", "origin", name)


def create_normal_features(repo: Path) -> list[str]:
    feature(repo, "feature/auth", "auth.txt", "require verified identity\n", "Add auth policy")
    feature(
        repo,
        "feature/payments",
        "payments.txt",
        "use idempotency keys\n",
        "Add payment policy",
    )
    return ["feature/auth", "feature/payments"]


def create_dev(repo: Path, branches: list[str]) -> None:
    git(repo, "checkout", "-q", "main")
    git(repo, "checkout", "-q", "-b", "dev")
    for branch in branches:
        git(repo, "merge", "-q", "--no-ff", "-m", f"Merge {branch}", branch)
    git(repo, "push", "-q", "-u", "origin", "dev")


def configure_scenario(repo: Path, scenario: str, base: str) -> None:
    if scenario == "diverged-main":
        git(repo, "checkout", "-q", "main")
        commit_file(repo, "local.txt", "local main work\n", "Keep local main work")
        git(repo, "push", "-q", "origin", "main")
        feature(repo, "feature/auth", "auth.txt", "auth feature\n", "Add auth feature")
        create_dev(repo, ["feature/auth"])
        git(repo, "checkout", "-q", "main")
        return

    if scenario == "rebase-conflict":
        git(repo, "checkout", "-q", "main")
        git(repo, "checkout", "-q", "-b", "auth-refresh")
        commit_file(
            repo,
            "config.txt",
            "mode=feature\nauth_refresh=true\n",
            "Refresh authentication",
        )
        git(repo, "push", "-q", "-u", "origin", "auth-refresh")
        create_dev(repo, [])
        git(repo, "checkout", "-q", "auth-refresh")
        return

    if scenario == "dev-merge-conflict":
        feature(repo, "feature/a", "config.txt", "mode=a\n", "Select mode A")
        feature(repo, "feature/b", "config.txt", "mode=b\n", "Select mode B")
        create_dev(repo, [])
        git(repo, "checkout", "-q", "feature/a")
        return

    branches = create_normal_features(repo)
    create_dev(repo, branches)

    if scenario == "unique-dev":
        git(repo, "checkout", "-q", "dev")
        dev_base = git(repo, "rev-parse", "HEAD")
        commit_file(repo, "remote-dev.txt", "origin-only dev patch\n", "Origin dev patch")
        git(repo, "push", "-q", "origin", "dev")
        git(repo, "reset", "--hard", "-q", dev_base)
        commit_file(repo, "local-dev.txt", "local-only dev patch\n", "Local dev patch")
        git(repo, "checkout", "-q", "main")
        return

    if scenario == "dirty-worktree":
        git(repo, "checkout", "-q", "feature/payments")
        write(repo, "notes.txt", "pre-existing stash content\n")
        git(repo, "stash", "push", "-q", "-m", "pre-existing fixture stash")
        write(repo, "payments.txt", "use idempotency keys\nlocal uncommitted edit\n")
        write(repo, "scratch.txt", "untracked local work\n")
        return

    if scenario == "corrupt-rebase":
        git(repo, "checkout", "-q", "feature/auth")
        rebase_dir = repo / ".git" / "rebase-merge"
        rebase_dir.mkdir()
        write(repo, ".git/rebase-merge/head-name", "refs/heads/feature/auth\n")
        write(repo, ".git/rebase-merge/msgnum", "not-a-number\n")
        return

    git(repo, "checkout", "-q", "feature/auth")


def record_start_refs(repo: Path) -> None:
    refs = git(repo, "for-each-ref", "--format=%(refname) %(objectname)", "refs/heads", "refs/remotes/origin")
    for line in refs.splitlines():
        ref, object_name = line.split()
        if ref.startswith("refs/heads/"):
            suffix = ref.removeprefix("refs/heads/")
            git(repo, "update-ref", f"refs/eval/start/{suffix}", object_name)
        elif ref.startswith("refs/remotes/origin/") and not ref.endswith("/HEAD"):
            suffix = ref.removeprefix("refs/remotes/origin/")
            git(repo, "update-ref", f"refs/eval/start-origin/{suffix}", object_name)


def create_gh(repo: Path) -> None:
    script = f'''#!{sys.executable}
import json
import sys

args = sys.argv[1:]
if args[:2] != ["repo", "view"]:
    print("unsupported fixture gh command", file=sys.stderr)
    raise SystemExit(64)
query = None
for flag in ("--jq", "-q"):
    if flag in args and args.index(flag) + 1 < len(args):
        query = args[args.index(flag) + 1]
if query:
    if "defaultBranchRef" in query:
        print("main")
    elif "nameWithOwner" in query:
        print("eval/upstream")
    elif "parent" in query or "url" in query:
        print("https://github.com/eval/upstream")
    else:
        print("")
else:
    print(json.dumps({{"parent": {{"nameWithOwner": "eval/upstream", "url": "https://github.com/eval/upstream"}}, "defaultBranchRef": {{"name": "main"}}}}))
'''
    path = repo / ".eval" / "bin" / "gh"
    write(repo, ".eval/bin/gh", script)
    path.chmod(0o755)


def main() -> None:
    scenario = sys.argv[1]
    repo = Path(sys.argv[2])
    if scenario not in SCENARIOS:
        raise RuntimeError(f"unknown scenario: {scenario}")

    configure_repository(repo)
    base_files(repo, scenario)
    base = git(repo, "rev-parse", "HEAD")
    configure_remotes(repo)
    upstream_commit = add_upstream_commit(repo, scenario, base)
    configure_scenario(repo, scenario, base)
    if scenario != "corrupt-rebase":
        record_start_refs(repo)
    else:
        # Record refs before corrupt metadata is created by rebuilding the minimal records directly.
        for ref in ("main", "feature/auth", "dev"):
            git(repo, "update-ref", f"refs/eval/start/{ref}", git(repo, "rev-parse", ref))
    create_gh(repo)
    write(
        repo,
        ".eval/scenario.json",
        json.dumps({"scenario": scenario, "base": base, "upstream": upstream_commit}, indent=2) + "\n",
    )


if __name__ == "__main__":
    main()
