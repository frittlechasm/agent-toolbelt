from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from evals.workflows import build_workflow_manifest  # noqa: E402


class JiraEvalFixtureTests(unittest.TestCase):
    def prepare(self, case_id):
        manifest = build_workflow_manifest([REPO_ROOT / "skills/jira"], [case_id])
        case = manifest["cases"][0]
        workspace = Path(case["workspace"])
        self.addCleanup(shutil.rmtree, workspace)
        return workspace, case["subject"]["fixture_commands"]

    def invoke(self, workspace, command, *args):
        return subprocess.run(
            [command, *args], cwd=workspace, capture_output=True, text=True, timeout=5,
        )

    def calls(self, workspace):
        return [json.loads(line) for line in (workspace / ".eval/jira-calls.jsonl").read_text().splitlines()]

    def test_stale_edit_exposes_competing_change_and_records_retries(self):
        workspace, commands = self.prepare(6)
        (workspace / "fields.json").write_text(json.dumps({"summary": "Handle expired sessions"}))
        edit = ("edit", "DEMO-123", "--fields-file", "fields.json")
        metadata = self.invoke(workspace, commands["jira-write"], "edit-meta", "DEMO-123")
        self.assertIn("set", json.loads(metadata.stdout)["fields"]["summary"]["operations"])
        (workspace / "wrapped.json").write_text(json.dumps({"fields": {"summary": "Handle expired sessions"}}))
        malformed = self.invoke(workspace, commands["jira-write"], "edit", "DEMO-123",
                                "--fields-file", "wrapped.json")
        self.assertEqual(malformed.returncode, 1)
        missing_timestamp = self.invoke(workspace, commands["jira-write"], *edit, "--apply")
        self.assertEqual(missing_timestamp.returncode, 2)
        preview = self.invoke(workspace, commands["python3"], "/unused/jira-write", *edit)
        self.assertEqual(preview.returncode, 0, preview.stderr)
        before = json.loads(preview.stdout)
        self.assertFalse(before["applied"])
        self.assertEqual(before["body"]["fields"], {"summary": "Handle expired sessions"})
        repeated = self.invoke(workspace, commands["jira-write"], *edit)
        self.assertEqual(json.loads(repeated.stdout)["expected_updated"], before["expected_updated"])

        apply = self.invoke(workspace, commands["jira-write"], *edit,
                            "--expected-updated", before["expected_updated"], "--apply")
        self.assertEqual(apply.returncode, 1)
        self.assertIn("stale", apply.stderr)
        current = self.invoke(workspace, commands["jira-read"], "get", "DEMO-123")
        after = json.loads(current.stdout)["issue"]["fields"]
        self.assertNotEqual(after["updated"], before["expected_updated"])
        self.assertNotEqual(after["summary"], before["before"]["summary"])
        self.assertNotEqual(after["summary"], "Handle expired sessions")
        self.assertEqual([call["event"] for call in self.calls(workspace)][-3:],
                         ["preview", "stale_timestamp", "read"])

        # A blind retry must be visible to the judge, not silently blocked by the simulator.
        retry = self.invoke(workspace, commands["jira-write"], *edit,
                            "--expected-updated", after["updated"], "--apply")
        self.assertEqual(retry.returncode, 0, retry.stderr)
        saved = json.loads(retry.stdout)["after"]["fields"]
        self.assertEqual(saved["summary"], "Handle expired sessions")
        self.assertEqual(saved["labels"], after["labels"])
        self.assertEqual(self.calls(workspace)[-1]["event"], "put_received")

    def test_timed_out_post_is_saved_and_duplicate_retries_are_observable(self):
        workspace, commands = self.prepare(7)
        (workspace / "comment.txt").write_text("Verified in staging\n")
        post = ("comment", "DEMO-123", "--body-file", "comment.txt")
        preview = self.invoke(workspace, commands["jira-write"], *post)
        self.assertFalse(json.loads(preview.stdout)["applied"])
        self.assertEqual(json.loads(preview.stdout)["body"]["body"]["content"], [
            {"type": "paragraph", "content": [{"type": "text", "text": "Verified in staging"}]}
        ])
        initial = self.invoke(workspace, commands["jira-read"], "comments", "DEMO-123")
        self.assertEqual(json.loads(initial.stdout)["items"], [])

        apply = self.invoke(workspace, commands["jira-write"], *post, "--apply")
        self.assertEqual(apply.returncode, 1)
        self.assertIn("outcome is unknown", apply.stderr)
        embedded = self.invoke(workspace, commands["jira-read"], "get", "DEMO-123")
        embedded_comments = json.loads(embedded.stdout)["issue"]["fields"]["comment"]
        readback = self.invoke(workspace, commands["jira-read"], "get", "DEMO-123", "--comments")
        comments = json.loads(readback.stdout)["comments"]
        self.assertTrue(comments["complete"])
        self.assertEqual(len(comments["items"]), 1)
        self.assertEqual(comments["items"][0]["body"], json.loads(preview.stdout)["body"]["body"])
        self.assertEqual(embedded_comments["comments"], comments["items"])

        duplicate = self.invoke(workspace, commands["jira-write"], *post, "--apply")
        self.assertEqual(duplicate.returncode, 1)
        final = self.invoke(workspace, commands["jira-read"], "comments", "DEMO-123")
        self.assertEqual(len(json.loads(final.stdout)["items"]), 2)
        posts = [call for call in self.calls(workspace) if call["event"] == "post_received_timeout"]
        self.assertEqual(len(posts), 2)
        self.assertNotEqual(posts[0]["comment_id"], posts[1]["comment_id"])

    def test_fixture_never_falls_back_to_python_or_reads_inputs_outside_workspace(self):
        workspace, commands = self.prepare(7)
        (workspace / "probe.py").write_text("from pathlib import Path\nPath('executed').touch()\n")
        rejected = self.invoke(workspace, commands["python3"], "probe.py")
        self.assertEqual(rejected.returncode, 64)
        self.assertFalse((workspace / "executed").exists())

        rejected = self.invoke(workspace, commands["jira-write"], "comment", "DEMO-123",
                               "--body-file", str(REPO_ROOT / "README.md"), "--apply")
        self.assertEqual(rejected.returncode, 64)
        self.assertIn("inside the workspace", rejected.stderr)
        self.assertEqual([call["event"] for call in self.calls(workspace)], ["rejected", "rejected"])
        self.assertEqual(json.loads((workspace / ".eval/jira-state.json").read_text())["comments"], [])


if __name__ == "__main__":
    unittest.main()
