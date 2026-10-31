#!/usr/bin/env python3

import subprocess

paths = subprocess.run(
    ["git", "diff", "--cached", "--name-only", "--diff-filter=d", "-z"],
    capture_output=True, check=True,
).stdout.split(b"\0")
blocked = any(path.startswith(b"legacy-eval-workspaces/") for path in paths)
if blocked:
    print("Generated evaluation workspace files cannot be committed.")
raise SystemExit(int(blocked))
