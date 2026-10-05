from __future__ import annotations

import contextlib
import io
import os
import runpy
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sync-skills"
SYNC = runpy.run_path(SCRIPT)
RSYNC_OPTIONS = SYNC["RSYNC_OPTIONS"]


class ChatGPTExportTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repo"
        (self.repo / "skills").mkdir(parents=True)
        self.output = self.root / "exports"
        self.home = self.root / "home"
        self.addCleanup(patch.stopall)
        patch.dict(SYNC["main"].__globals__, {"REPO_ROOT": self.repo}).start()
        patch.object(Path, "home", return_value=self.home).start()

    def make_skill(
        self, name: str, agents: str = "all", machines: str = "all", private: bool = False,
    ) -> Path:
        parent = self.repo / "skills"
        if private:
            parent /= "private"
        skill = parent / name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Test skill\nmetadata:\n"
            f"  agents: {agents}\n  machines: {machines}\n---\nInstructions.\n"
        )
        return skill

    def run_main(self, action: str, *options: str) -> tuple[int, str]:
        arguments = [str(SCRIPT), action, "--machine", "fmp", *options]
        output = io.StringIO()
        with patch.object(sys, "argv", arguments), contextlib.redirect_stdout(output):
            return SYNC["main"](), output.getvalue()

    def chatgpt(self, action: str) -> tuple[int, str]:
        return self.run_main(action, "--target", "chatgpt", "--output-dir", str(self.output))

    def test_export_respects_agent_machine_and_private_routing(self) -> None:
        self.make_skill("shared")
        self.make_skill("chatgpt-only", agents="chatgpt")
        self.make_skill("codex-only", agents="codex")
        self.make_skill("claude-only", agents="claude")
        self.make_skill("local-agents", agents="claude, codex")
        self.make_skill("other-machine", machines="mowork")
        self.make_skill("private-shared", private=True)

        code, output = self.chatgpt("apply")

        self.assertEqual(code, 0)
        self.assertEqual(
            {path.name for path in self.output.iterdir()},
            {"shared.zip", "chatgpt-only.zip", "private-shared.zip"},
        )
        self.assertIn("ZIP export only", output)
        self.assertFalse(self.home.exists())

    def test_bundle_keeps_support_files_and_excludes_machine_local_files(self) -> None:
        skill = self.make_skill("portable")
        for relative in (
            ".env", ".env.local", ".DS_Store", ".git/config", "scripts/helper.pyc",
            "scripts/__pycache__/helper.pyc", "scripts/.env.secret", "references/.DS_Store",
        ):
            path = skill / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("machine-local fixture\n")
        for relative in (".env.example", "references/guide.md", "assets/template.txt", "scripts/helper.py"):
            path = skill / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("bundled fixture\n")
        (skill / "scripts/helper.py").chmod(0o755)

        self.chatgpt("apply")

        with zipfile.ZipFile(self.output / "portable.zip") as archive:
            self.assertEqual(set(archive.namelist()), {
                "portable/SKILL.md", "portable/.env.example", "portable/references/guide.md",
                "portable/assets/template.txt", "portable/scripts/helper.py",
            })
            self.assertEqual(archive.read("portable/SKILL.md"), (skill / "SKILL.md").read_bytes())
            permissions = archive.getinfo("portable/scripts/helper.py").external_attr >> 16
            self.assertEqual(stat.S_IMODE(permissions), 0o755)
            self.assertIsNone(archive.testzip())

    def test_check_is_read_only_and_reports_content_and_permission_drift(self) -> None:
        skill = self.make_skill("portable")
        code, output = self.chatgpt("check")
        self.assertEqual(code, 1)
        self.assertIn("MISSING", output)
        self.assertFalse(self.output.exists())

        self.chatgpt("apply")
        destination = self.output / "portable.zip"
        original = destination.read_bytes()
        original_mtime = destination.stat().st_mtime_ns
        os.utime(skill / "SKILL.md", (1_000_000_000, 1_000_000_000))
        self.assertEqual(self.chatgpt("check")[0], 0)
        self.assertIn("OK", self.chatgpt("apply")[1])
        self.assertEqual(destination.stat().st_mtime_ns, original_mtime)

        (skill / "SKILL.md").write_text((skill / "SKILL.md").read_text() + "Updated.\n")
        code, output = self.chatgpt("check")
        self.assertEqual(code, 1)
        self.assertIn("DRIFT", output)
        self.assertEqual(destination.read_bytes(), original)
        self.assertEqual(self.chatgpt("apply")[0], 0)
        (skill / "SKILL.md").chmod(0o755)
        self.assertEqual(self.chatgpt("check")[0], 1)
        self.assertEqual(self.chatgpt("apply")[0], 0)
        self.assertEqual(self.chatgpt("check")[0], 0)

    def test_corrupt_zip_is_repaired_and_deleted_source_files_are_removed(self) -> None:
        skill = self.make_skill("portable")
        reference = skill / "reference.md"
        reference.write_text("Old reference.\n")
        self.chatgpt("apply")
        reference.unlink()
        self.assertEqual(self.chatgpt("check")[0], 1)
        self.chatgpt("apply")
        with zipfile.ZipFile(self.output / "portable.zip") as archive:
            self.assertNotIn("portable/reference.md", archive.namelist())
        (self.output / "portable.zip").write_bytes(b"broken archive")
        self.assertEqual(self.chatgpt("check")[0], 1)
        self.assertEqual(self.chatgpt("apply")[0], 0)
        self.assertEqual(self.chatgpt("check")[0], 0)

    def test_source_symlinks_are_rejected_before_any_export_is_written(self) -> None:
        self.make_skill("first")
        skill = self.make_skill("second")
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "file.txt").write_text("Outside fixture.\n")
        for target in (outside, outside / "file.txt"):
            with self.subTest(target=target):
                link = skill / "linked"
                link.symlink_to(target)
                with self.assertRaisesRegex(SystemExit, "cannot package symlink"):
                    self.chatgpt("apply")
                self.assertFalse(self.output.exists())
                link.unlink()

    def test_destination_symlink_is_replaced_without_modifying_its_target(self) -> None:
        self.make_skill("portable")
        outside = self.root / "outside.zip"
        outside.write_bytes(b"leave this alone")
        self.output.mkdir()
        destination = self.output / "portable.zip"
        destination.symlink_to(outside)

        self.assertIn("LINK", self.chatgpt("check")[1])
        self.assertEqual(self.chatgpt("apply")[0], 0)
        self.assertFalse(destination.is_symlink())
        self.assertEqual(outside.read_bytes(), b"leave this alone")

    def test_default_export_directory_is_inside_checkout(self) -> None:
        self.make_skill("portable")
        code, _ = self.run_main("apply", "--target", "chatgpt")
        self.assertEqual(code, 0)
        self.assertTrue((self.repo / ".chatgpt/skills/portable.zip").is_file())

    def test_invalid_options_do_not_create_exports_or_local_installs(self) -> None:
        skill = self.make_skill("portable")
        for options in (
            ("--target", "chatgpt", "--host", "mowork"),
            ("--output-dir", str(self.output)),
            ("--target", "chatgpt", "--output-dir", str(skill / "exports")),
        ):
            with self.subTest(options=options), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    self.run_main("apply", *options)
                self.assertEqual(error.exception.code, 2)
        self.assertFalse(self.output.exists())
        self.assertFalse(self.home.exists())
        self.assertFalse((skill / "exports").exists())

    def test_failed_atomic_replace_preserves_previous_zip_and_cleans_temporary_file(self) -> None:
        skill = self.make_skill("portable")
        self.chatgpt("apply")
        destination = self.output / "portable.zip"
        original = destination.read_bytes()
        (skill / "SKILL.md").write_text((skill / "SKILL.md").read_text() + "Updated.\n")

        with patch.object(Path, "replace", side_effect=OSError("fixture replace failure")):
            with self.assertRaises(OSError):
                self.chatgpt("apply")

        self.assertEqual(destination.read_bytes(), original)
        self.assertEqual(list(self.output.iterdir()), [destination])
        self.assertEqual(self.chatgpt("apply")[0], 0)

    def test_local_install_routing_remains_the_default(self) -> None:
        shared = self.make_skill("shared")
        codex = self.make_skill("codex-only", agents="codex")
        claude = self.make_skill("claude-only", agents="claude")

        self.assertEqual(self.run_main("apply")[0], 0)
        self.assertEqual((self.home / ".agents/skills/shared").resolve(), shared.resolve())
        self.assertEqual((self.home / ".claude/skills/shared").resolve(), shared.resolve())
        self.assertEqual((self.home / ".codex/skills/codex-only").resolve(), codex.resolve())
        self.assertEqual((self.home / ".claude/skills/claude-only").resolve(), claude.resolve())
        self.assertFalse(self.output.exists())

    def test_local_agent_pair_preserves_shared_paths_without_cloud_export(self) -> None:
        skill = self.make_skill("local-agents", agents="claude, codex", private=True)
        self.make_skill("portable")

        self.assertEqual(self.run_main("apply")[0], 0)
        self.assertEqual((self.home / ".agents/skills/local-agents").resolve(), skill.resolve())
        self.assertEqual((self.home / ".claude/skills/local-agents").resolve(), skill.resolve())
        self.assertEqual(self.run_main("check")[0], 0)
        self.assertEqual(SYNC["destinations"](skill, {"claude", "codex"}), {
            "primary": ".agents/skills/local-agents",
            "claude_link": ".claude/skills/local-agents",
        })
        self.assertEqual(self.chatgpt("apply")[0], 0)
        self.assertEqual({path.name for path in self.output.iterdir()}, {"portable.zip"})

    def test_grouped_skills_keep_flat_install_and_export_names(self) -> None:
        shared = self.make_skill("mailbox-review/grouped-shared", private=True)
        self.make_skill("mailbox-review/grouped-chatgpt", agents="chatgpt", private=True)
        # Groups are one level deep; a group inside a group is not scanned.
        self.make_skill("mailbox-review/nested/too-deep", private=True)

        self.assertEqual(self.run_main("apply")[0], 0)
        self.assertEqual((self.home / ".agents/skills/grouped-shared").resolve(), shared.resolve())
        self.assertFalse((self.home / ".agents/skills/grouped-chatgpt").exists())
        self.assertFalse((self.home / ".agents/skills/too-deep").exists())
        self.assertEqual(self.chatgpt("apply")[0], 0)
        self.assertEqual(
            {path.name for path in self.output.iterdir()},
            {"grouped-shared.zip", "grouped-chatgpt.zip"},
        )
        with zipfile.ZipFile(self.output / "grouped-chatgpt.zip") as archive:
            self.assertEqual(archive.namelist(), ["grouped-chatgpt/SKILL.md"])

    def test_local_install_skips_chatgpt_only_skills(self) -> None:
        self.make_skill("shared")
        self.make_skill("chatgpt-only", agents="chatgpt", private=True)
        self.make_skill("chatgpt-trailing-comma", agents="chatgpt,", private=True)
        codex = self.make_skill("codex-chatgpt", agents="codex, chatgpt")

        code, output = self.run_main("apply")
        self.assertEqual(code, 0)
        self.assertNotIn("chatgpt-only", output)
        self.assertFalse((self.home / ".agents/skills/chatgpt-only").exists())
        self.assertFalse((self.home / ".agents/skills/chatgpt-trailing-comma").exists())
        self.assertEqual((self.home / ".codex/skills/codex-chatgpt").resolve(), codex.resolve())
        self.assertEqual(self.run_main("check")[0], 0)


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
