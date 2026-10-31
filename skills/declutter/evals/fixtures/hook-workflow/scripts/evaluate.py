#!/usr/bin/env python3

from pathlib import Path
import tempfile

with tempfile.TemporaryDirectory(prefix="forge-eval-") as directory:
    workspace = Path(directory)
    (workspace / "result.txt").write_text("Evaluation result\n")
    print(workspace)
