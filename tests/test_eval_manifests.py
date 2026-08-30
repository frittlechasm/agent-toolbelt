from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from evals.triggers import build_trigger_manifest  # noqa: E402
from evals.workflows import build_workflow_manifest  # noqa: E402


class EvalManifestTests(unittest.TestCase):
    def test_trigger_manifest_defines_explicit_invocation_and_run_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill = Path(temporary) / "explicit-task"
            (skill / "agents").mkdir(parents=True)
            (skill / "evals").mkdir()
            (skill / "SKILL.md").write_text(
                "---\n"
                "name: explicit-task\n"
                "description: Run an explicitly invoked task.\n"
                "metadata:\n"
                "  scope: global\n"
                "  agents: all\n"
                "  machines: all\n"
                "---\n",
                encoding="utf-8",
            )
            (skill / "agents" / "openai.yaml").write_text(
                "policy:\n  allow_implicit_invocation: false\n",
                encoding="utf-8",
            )
            (skill / "evals" / "trigger-evals.json").write_text(
                json.dumps(
                    {
                        "skill_name": "explicit-task",
                        "evals": [{"id": 1, "prompt": "Run the task.", "should_trigger": False}],
                    }
                ),
                encoding="utf-8",
            )

            manifest = build_trigger_manifest([skill])

        self.assertEqual(
            manifest["run_metadata_format"],
            {"model": "string", "reasoning_effort": "string", "capabilities": "string_list"},
        )
        self.assertIn(
            "requesting the underlying task is not explicit skill invocation",
            " ".join(manifest["instructions"]),
        )
        self.assertFalse(manifest["cases"][0]["skill"]["allow_implicit_invocation"])

    def test_workflow_manifest_declares_capabilities_and_git_writable_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill = Path(temporary) / "git-task"
            fixture = skill / "evals" / "fixtures" / "repository"
            (fixture / ".git").mkdir(parents=True)
            (fixture / "tracked.txt").write_text("fixture\n", encoding="utf-8")
            (skill / "SKILL.md").write_text(
                "---\n"
                "name: git-task\n"
                "description: Exercise a temporary Git fixture.\n"
                "metadata:\n"
                "  scope: global\n"
                "  agents: all\n"
                "  machines: all\n"
                "---\n",
                encoding="utf-8",
            )
            (skill / "evals" / "evals.json").write_text(
                json.dumps(
                    {
                        "skill_name": "git-task",
                        "evals": [
                            {
                                "id": 1,
                                "prompt": "Inspect the fixture.",
                                "expected_output": "A verified result.",
                                "files": [],
                                "expectations": ["Inspects the fixture."],
                                "fixture": "fixtures/repository",
                                "capabilities": ["browser"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            manifest = build_workflow_manifest([skill], None)
            workspace = Path(manifest["cases"][0]["workspace"])
            try:
                subject = manifest["cases"][0]["subject"]
                self.assertEqual(subject["required_capabilities"], ["browser"])
                self.assertEqual(subject["sandbox_writable_paths"], [str(workspace), str(workspace / ".git")])
                self.assertEqual(manifest["case_result_format"]["status"], ["passed", "failed", "skipped"])
            finally:
                shutil.rmtree(workspace, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
