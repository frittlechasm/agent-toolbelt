"""Discover and run nested Python unit tests."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


def run_unit_tests(repo_root: Path) -> tuple[bool, int, int]:
    """Discover and run every unittest suite, including nested skill tests."""
    test_directories = sorted(
        {path.parent for path in repo_root.rglob("test_*.py")},
        key=lambda path: str(path.relative_to(repo_root)),
    )
    if not test_directories:
        print("ERROR no unit tests found")
        return False, 0, 0

    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for directory in test_directories:
        suite.addTests(
            loader.discover(
                start_dir=str(directory),
                pattern="test_*.py",
                top_level_dir=str(directory),
            )
        )

    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
    return result.wasSuccessful(), result.testsRun, len(test_directories)
