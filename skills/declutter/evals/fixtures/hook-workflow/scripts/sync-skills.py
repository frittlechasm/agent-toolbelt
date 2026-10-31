#!/usr/bin/env python3

from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
shutil.copytree(root / "skills", root / "installed-skills", dirs_exist_ok=True)
