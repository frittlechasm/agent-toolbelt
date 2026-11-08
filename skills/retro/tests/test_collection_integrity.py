import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "collect_history_integrity", Path(__file__).parents[1] / "scripts/collect_history.py"
)
collector = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(collector)


def user_event(text, event_id):
    return {
        "type": "response_item", "timestamp": "2026-10-01T12:00:00Z",
        "payload": {
            "type": "message", "role": "user", "id": event_id,
            "content": [{"type": "input_text", "text": text}],
            "internal_chat_message_metadata_passthrough": {"content_item_kinds": ["user.text"]},
        },
    }


class CollectionIntegrityTests(unittest.TestCase):
    def test_prose_credentials_are_redacted_including_quoted_spaces(self):
        cases = (
            "password would be synthetic-password",
            'password is "synthetic password with spaces"',
            "API key was `synthetic-api-key`",
            "token will be 'synthetic token'",
            "secret is: synthetic-secret",
        )
        for text in cases:
            with self.subTest(text=text):
                result = collector.redact(text)
                self.assertNotIn("synthetic", result)
                self.assertIn("[REDACTED]", result)

    def test_known_wrappers_override_user_text_metadata(self):
        prefixes = (
            "<command-message>", "<skill>", "<skill name='fixture'>",
            "Delegated task node:", "Context handoff (manual_context):",
            "[Request interrupted by user]",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sessions").mkdir()
            (root / "sessions/wrappers.jsonl").write_text("\n".join(
                json.dumps(user_event(prefix + " synthetic content", str(index)))
                for index, prefix in enumerate(prefixes)
            ))
            records = collector.collect_codex(root, "fixture")
        self.assertEqual(len(prefixes), len(records))
        self.assertTrue(all(record["injected"] for record in records))
        self.assertEqual({"injected"}, {record["message_origin"] for record in records})

    def test_prompt_forms_preserve_later_human_feedback(self):
        cases = (
            ("Automation: Sync files\nAutomation ID: fixture-sync\nRun the task.", "scheduled"),
            ("Act as review sub-agent for this task. Inspect the patch.", "reviewer_prompt"),
            ("Scheduled automation execution.\nRun the synthetic task.", "scheduled"),
            ("Explicitly forwarded scheduled automation trigger for 2026-10-01.", "scheduled"),
            ("Forwarded scheduled automation trigger for 2026-10-01.", "scheduled"),
            ("Act as the review sub-agent for this task.", "reviewer_prompt"),
            ("Act as a reviewer sub-agent for this task.", "reviewer_prompt"),
            ("Act as the test sub-agent for this task.", "delegate_prompt"),
            ("Act as an implementation sub-agent for this task.", "delegate_prompt"),
            ("Act as the design sub-agent for this task.", "delegate_prompt"),
            ("Harness correction: keep the synthetic workspace for inspection.", "injected"),
            ("This session is being continued from a previous conversation that ran out of context.", "injected"),
            ("Context continuation:\nSynthetic summary of earlier work.", "injected"),
        )
        feedback = "The previous command used the wrong remote."
        texts = [text for prompt, _ in cases for text in ("\n  " + prompt, feedback)]
        for agent, source, human_origin in (
            ("codex", "cli", "direct"),
            ("codex", "exec", "unknown"),
            ("claude", None, "unknown"),
        ):
            records = self.collect_user_texts(agent, texts, source)
            self.assertEqual(len(texts), len(records))
            for index, (prompt, expected) in enumerate(cases):
                with self.subTest(agent=agent, source=source, prompt=prompt):
                    generated, human = records[2 * index:2 * index + 2]
                    self.assertEqual(expected, generated["message_origin"])
                    self.assertEqual(expected == "injected", generated["injected"])
                    self.assertFalse(generated["delegated"])
                    self.assertEqual(human_origin, generated["delegation_status"])
                    self.assertEqual(human_origin, human["message_origin"])
                    self.assertFalse(human["injected"] or human["delegated"])
                    self.assertEqual(feedback, human["text"])

    def test_discussions_of_wrappers_and_side_chat_remain_user_text(self):
        texts = [
            "Scheduled automation execution is broken; fix it.",
            "Forwarded scheduled automation trigger failed; fix it.",
            "Explicitly forwarded scheduled automation trigger failed; fix it.",
            "Act as the reviewer for this task.",
            "Harness correction needs a regression test.",
            "Side chat:\nWhy did the previous command use the wrong remote?",
        ]
        records = self.collect_user_texts("codex", texts, "cli")
        self.assertEqual(texts, [r["text"] for r in records])
        self.assertEqual(["direct"] * len(texts), [r["message_origin"] for r in records])
        self.assertFalse(any(r["injected"] or r["delegated"] for r in records))

    def collect_user_texts(self, agent, texts, source):
        if agent == "codex":
            events = [user_event(text, str(index)) for index, text in enumerate(texts)]
            events.insert(0, {"type": "session_meta", "payload": {"id": "fixture", "source": source}})
        else:
            events = [{
                "type": "user", "timestamp": "2026-10-01T12:00:00Z", "uuid": str(index),
                "message": {"role": "user", "content": text},
            } for index, text in enumerate(texts)]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / ("sessions" if agent == "codex" else "projects")
            folder.mkdir()
            (folder / "task.jsonl").write_text("\n".join(map(json.dumps, events)))
            collect = collector.collect_codex if agent == "codex" else collector.collect_claude
            return collect(root, "fixture")

    def test_partial_collection_reports_bad_lines_and_missing_root_without_raw_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sessions = root / "codex/sessions"
            sessions.mkdir(parents=True)
            valid = json.dumps(user_event("Review this fixture", "valid")).encode()
            (sessions / "partial.jsonl").write_bytes(
                b'{"fixture": "synthetic-secret"\n[]\n\xff\n' + valid + b"\n"
            )
            args = SimpleNamespace(machine="fixture", agent="all", claude_root=str(root / "missing"), codex_root=str(root / "codex"))
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                records = collector.collect_local(args)
        diagnostics = [json.loads(line) for line in stderr.getvalue().splitlines()]
        self.assertEqual(1, len(records))
        self.assertEqual("Review this fixture", records[0]["text"])
        self.assertEqual([False, False], [d["complete"] for d in diagnostics])
        self.assertEqual("missing_or_not_directory", diagnostics[0]["issues"][0]["error"])
        self.assertEqual((1, 1, 3), tuple(diagnostics[1][k] for k in ("files_seen", "files_read", "invalid_records")))
        self.assertEqual([1, 2, 3], diagnostics[1]["issues"][0]["first_lines"])
        self.assertNotIn("synthetic-secret", stderr.getvalue())

    def test_unreadable_file_reports_error_type_without_exception_text(self):
        diagnostics = {"complete": True, "issues": [], "files_read": 0, "invalid_records": 0}
        with patch.object(Path, "open", side_effect=PermissionError("password is synthetic-secret")):
            records = list(collector.read_jsonl(Path("blocked.jsonl"), diagnostics))
        self.assertEqual([], records)
        self.assertFalse(diagnostics["complete"])
        self.assertEqual("PermissionError", diagnostics["issues"][0]["error"])
        self.assertNotIn("synthetic-secret", json.dumps(diagnostics))

    def test_successful_remote_collection_preserves_redacted_diagnostics(self):
        result = SimpleNamespace(returncode=0, stdout=b'{"record_type":"message"}\n', stderr=b'collection warning: password would be synthetic-secret\n')
        stderr = io.StringIO()
        with patch.object(collector.subprocess, "run", return_value=result), redirect_stderr(stderr):
            records = collector.collect_remote("fixture-host", "codex")
        self.assertEqual([{"record_type": "message"}], records)
        self.assertIn("collection warning", stderr.getvalue())
        self.assertIn("[REDACTED]", stderr.getvalue())
        self.assertNotIn("synthetic-secret", stderr.getvalue())

    def test_failed_remote_collection_redacts_error(self):
        result = SimpleNamespace(returncode=1, stdout=b"", stderr=b'password=synthetic-secret')
        with patch.object(collector.subprocess, "run", return_value=result):
            with self.assertRaises(RuntimeError) as raised:
                collector.collect_remote("fixture-host", "all")
        self.assertIn("[REDACTED]", str(raised.exception))
        self.assertNotIn("synthetic-secret", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
