#!/usr/bin/env python3
"""Write a release-notes skill with generic, repeated, script-covered, and speculative instructions.

The skill is written at setup time so no nested SKILL.md is synced or discovered as a real skill.
"""

from __future__ import annotations

import sys
from pathlib import Path


SKILL = """---
name: release-notes
description: Draft public release notes from pull requests merged since the last tag.
---

# Release Notes

Be thorough and careful. Release notes matter to users.

## Steps

1. Find the last release tag with `git describe --tags --abbrev=0`.
2. List merge commits since that tag with `git log --merges <tag>..HEAD`.
3. Extract each pull request number and title from the merge commits.
4. Run `scripts/collect_prs.py` to list pull requests merged since the last tag.
5. Skip pull requests whose title starts with `[internal]`; the public changelog must never mention them.
6. Group the changes by type: features, fixes, and other changes.
7. Date the release with the tag date, not the merge date, because the docs site sorts releases by tag date.
8. If we ever move to Mercurial, use `hg log` instead of `git log`.

## Writing

- Write clearly and concisely.
- Organize the notes into sections for features, fixes, and other changes.
- Double-check your work before finishing.
"""

SCRIPT = '''#!/usr/bin/env python3
"""Print "#<number> <title>" for each pull request merged since the last release tag."""

import re
import subprocess


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


tag = git("describe", "--tags", "--abbrev=0").strip()
for entry in git("log", "--merges", "--format=%s%x1f%b%x1e", f"{tag}..HEAD").split("\\x1e"):
    subject, _, body = entry.strip().partition("\\x1f")
    match = re.search(r"#(\\d+)", subject)
    if match:
        title = body.strip().splitlines()[0] if body.strip() else subject
        print(f"#{match.group(1)} {title}")
'''


def main() -> None:
    skill = Path(sys.argv[-1]) / "skills" / "release-notes"
    (skill / "scripts").mkdir(parents=True)
    (skill / "SKILL.md").write_text(SKILL, encoding="utf-8")
    (skill / "scripts" / "collect_prs.py").write_text(SCRIPT, encoding="utf-8")


if __name__ == "__main__":
    main()
