from __future__ import annotations

import runpy
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sync-skills"
RSYNC_OPTIONS = runpy.run_path(SCRIPT)["RSYNC_OPTIONS"]


@unittest.skipUnless(shutil.which("rsync"), "rsync is required")
class SyncFiltersTest(unittest.TestCase):
    def test_machine_local_files_are_preserved_and_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "source"
            destination = root / "destination"
            source.mkdir()
            destination.mkdir()

            (source / ".env").write_text("source-machine-credential\n")
            (source / ".env.local").write_text("source-machine-override\n")
            (source / ".env.example").write_text("documented-variable=\n")
            (source / "SKILL.md").write_text("current skill\n")
            source_cache = source / "scripts" / "__pycache__"
            source_cache.mkdir(parents=True)
            (source_cache / "helper.pyc").write_bytes(b"source cache")

            (destination / ".env").write_text("destination-machine-credential\n")
            (destination / ".env.local").write_text("destination-machine-override\n")
            destination_cache = destination / "scripts" / "__pycache__"
            destination_cache.mkdir(parents=True)
            (destination_cache / "helper.pyc").write_bytes(b"destination cache")
            (destination / "stale-managed-file.txt").write_text("remove me\n")

            self.run_rsync(source, destination)

            self.assertEqual(
                (destination / ".env").read_text(),
                "destination-machine-credential\n",
            )
            self.assertEqual(
                (destination / ".env.local").read_text(),
                "destination-machine-override\n",
            )
            self.assertEqual(
                (destination / ".env.example").read_text(),
                "documented-variable=\n",
            )
            self.assertEqual(
                (destination_cache / "helper.pyc").read_bytes(),
                b"destination cache",
            )
            self.assertEqual((destination / "SKILL.md").read_text(), "current skill\n")
            self.assertFalse((destination / "stale-managed-file.txt").exists())

            dry_run = self.run_rsync(source, destination, "--dry-run")
            self.assertEqual(dry_run.stdout, b"")

    def run_rsync(
        self,
        source: Path,
        destination: Path,
        *extra_options: str,
    ) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(
            [
                "rsync",
                *RSYNC_OPTIONS,
                "--itemize-changes",
                *extra_options,
                "--",
                f"{source}/",
                f"{destination}/",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
