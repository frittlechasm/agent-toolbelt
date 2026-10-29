#!/usr/bin/env python3
"""Prepare local Jira commands for the stale-update and uncertain-POST evals."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", choices=("stale", "timeout"))
    parser.add_argument("workspace", type=Path)
    args = parser.parse_args()
    control = args.workspace / ".eval"
    commands = control / "bin"
    commands.mkdir(parents=True)
    state = {
        "scenario": args.scenario,
        "conflict_injected": False,
        "issue": {
            "key": "DEMO-123",
            "fields": {
                "summary": "Expired sessions lose diagnostics",
                "updated": "2026-08-01T10:00:00.000+0000",
                "labels": ["support"],
            },
        },
        "comments": [],
    }
    (control / "jira-state.json").write_text(json.dumps(state) + "\n", encoding="utf-8")
    (control / "jira-calls.jsonl").write_text("", encoding="utf-8")
    source = Path(__file__).with_name("jira_cli.py").read_text(encoding="utf-8")
    for name in ("jira-read", "jira-write", "python", "python3"):
        command = commands / name
        command.write_text(f"#!{sys.executable}\n{source}", encoding="utf-8")
        command.chmod(0o755)


if __name__ == "__main__":
    main()
