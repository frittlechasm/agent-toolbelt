#!/usr/bin/env python3
"""Create local repository and configuration evidence for link workflow evals."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


REMOTES = {
    "bitbucket-alias": "git@toolbelt-bitbucket:eval-workspace/sample-service.git",
    "bitbucket": "https://bitbucket.org/eval-workspace/sample-service.git",
    "github": "git@github.com:eval-org/sample-service.git",
}


def git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        text=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("scenario", choices=(*REMOTES, "jira-known", "no-target"))
    parser.add_argument("workspace", type=Path)
    args = parser.parse_args()
    root = args.workspace

    git(root, "init", "--quiet")
    (root / "README.md").write_text("# Isolated link-formatting fixture\n", encoding="utf-8")
    remote = REMOTES.get(args.scenario)
    if remote is not None:
        git(root, "remote", "add", "origin", remote)
    if args.scenario == "bitbucket-alias":
        (root / "ssh_config").write_text(
            "Host toolbelt-bitbucket\n    HostName bitbucket.org\n    User git\n",
            encoding="utf-8",
        )
    if args.scenario == "jira-known":
        (root / "jira-site.txt").write_text(
            "https://toolbelt-eval.atlassian.net\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()
