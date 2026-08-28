#!/usr/bin/env python3
"""Create deterministic Git states for commit-msg workflow evals."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        text=True,
    )


def write(path: Path, contents: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("scenario", choices=("staged", "unstaged", "untracked"))
    parser.add_argument("workspace", type=Path)
    args = parser.parse_args()
    root = args.workspace

    git(root, "init", "--quiet")
    git(root, "config", "user.name", "Eval User")
    git(root, "config", "user.email", "eval@example.invalid")
    git(root, "config", "commit.gpgsign", "false")
    write(root / "README.md", "# Fixture service\n")
    write(root / "src" / "server.ts", "export const port = 3000\n")
    git(root, "add", "README.md", "src/server.ts")
    git(root, "commit", "--quiet", "-m", "chore: initialize fixture")

    if args.scenario == "untracked":
        write(
            root / "src" / "health-check.ts",
            "export const healthCheck = () => ({ status: 'ok' })\n",
        )
        return

    write(
        root / "src" / "server.ts",
        "export const port = 3000\nexport const requestTimeoutMs = 5000\n",
    )
    if args.scenario == "staged":
        git(root, "add", "src/server.ts")


if __name__ == "__main__":
    main()
