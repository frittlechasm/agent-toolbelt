import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / "scripts/summarize_history.py"
SPEC = importlib.util.spec_from_file_location("summarize_history", SCRIPT)
helper = importlib.util.module_from_spec(SPEC)
with patch.object(sys, "path", [str(SCRIPT.parent), *sys.path]):
    SPEC.loader.exec_module(helper)


def message(thread="root", time="2026-10-20T12:00:00Z", **extra):
    row = {"agent": "codex", "machine": "fmp", "session_path": thread + ".jsonl", "session": thread + ".jsonl",
           "thread_id": thread, "root_thread_id": thread, "record_type": "message", "role": "user",
           "text": "PRIVATE EXAMPLE TEXT", "timestamp": time, "message_origin": "direct", "event_id": thread}
    return {**row, **extra}


def usage(thread="root", response="r1", tokens=10, **extra):
    return {**message(thread), "record_type": "usage", "role": "usage", "text": "", "model": "test-model",
            "usage_source": "token_usage_record", "response_id": response,
            "usage": {"input_tokens": tokens, "cached_input_tokens": 3, "output_tokens": 2}, **extra}


def diagnostics(complete=True, remote=0, summary=True):
    line = json.dumps({"record_type": "collection_diagnostics", "agent": "codex", "machine": "fmp",
                       "complete": complete, "files_seen": 2, "files_read": 2, "invalid_records": 0})
    return line + (f"\ncollected 2 events; remote failures: {remote}\n" if summary else "")


class SummaryTests(unittest.TestCase):
    def test_parsed_times_rank_messages_not_usage_and_report_shortfall(self):
        rows = [message("a", "2026-10-20T11:00:00+01:00"), message("b", "2026-10-20T10:30:00Z"),
                usage("a", timestamp="2026-10-22T12:00:00Z")]
        result = helper.summarize(rows, last=3)
        self.assertEqual(["b", "a"], [row["root_or_session_id"] for row in result["selected"]])
        self.assertEqual(1, result["selection"]["shortfall"])
        self.assertNotIn("PRIVATE EXAMPLE TEXT", json.dumps(result))

    def test_excluding_root_removes_children_even_when_parent_has_no_records(self):
        rows = [message("child", root_thread_id="audit", parent_thread_id="audit", delegated=True),
                usage("child", root_thread_id="audit", parent_thread_id="audit", delegated=True), message("work")]
        result = helper.summarize(rows, exclude={"audit"})
        self.assertEqual(["work"], [row["root_or_session_id"] for row in result["selected"]])
        self.assertEqual([], result["selected_usage_by_agent_model"])

    def test_excluding_child_preserves_parent_and_qualified_filters_work(self):
        rows = [message(), message("child", root_thread_id="root", parent_thread_id="root", delegated=True),
                usage("child", root_thread_id="root", parent_thread_id="root")]
        result = helper.summarize(rows, exclude={"codex:fmp:child.jsonl"}, include={"root"})
        self.assertEqual(1, len(result["selected"][0]["sessions"]))
        self.assertEqual(2, result["selection"]["excluded_records"])

    def test_response_dedup_and_empty_fingerprints_preserve_unranked_usage(self):
        first = usage("one", "r1", session_fingerprint="empty")
        rows = [message(), first, dict(first), usage("two", "r2", tokens=7,
                                                       session_fingerprint="empty", duplicate_of="one.jsonl")]
        result = helper.summarize(rows, last=1)
        self.assertEqual(17, result["unranked_usage_by_agent_model"][0]["input_tokens"])
        self.assertEqual(2, result["unranked_usage_by_agent_model"][0]["records"])
        self.assertEqual(2, result["sessions_without_orderable_messages"])

    def test_identical_fingerprints_do_not_collapse_independent_scheduled_sessions(self):
        rows = [message("a", session_fingerprint="same"),
                message("b", session_fingerprint="same", duplicate_of="a.jsonl")]
        self.assertEqual(2, helper.summarize(rows)["selection"]["selected_tasks"])

    def test_injected_invalid_and_orphan_sessions_are_not_ranked_as_independent_tasks(self):
        rows = [message("injected", injected=True), message("invalid", time="not-a-time"),
                message("orphan", delegated=True), usage("orphan")]
        result = helper.summarize(rows, last=2)
        self.assertEqual([], result["selected"])
        self.assertEqual(3, len(result["unranked"]))
        self.assertEqual(10, result["unranked_usage_by_agent_model"][0]["input_tokens"])

    def test_coverage_requires_summary_line_and_detects_remote_failure(self):
        self.assertEqual("unknown", helper.coverage(None)["status"])
        self.assertEqual("unknown", helper.coverage(diagnostics(summary=False))["status"])
        self.assertEqual("partial", helper.coverage(diagnostics(remote=1))["status"])
        self.assertEqual("partial", helper.coverage(diagnostics(complete=False))["status"])
        self.assertEqual("complete_for_reported_roots", helper.coverage(diagnostics())["status"])

    def test_vendor_fields_remain_separate_and_unknown_model_is_retained(self):
        claude = {**usage("claude"), "agent": "claude", "usage_source": "assistant_message", "message_id": "c1",
                  "model": None, "usage": {"input_tokens": 4, "cache_read_input_tokens": 50}}
        rows = [message(), usage(), {**message("claude"), "agent": "claude"}, claude]
        result = helper.summarize(rows)
        totals = result["selected_usage_by_agent_model"]
        self.assertEqual("unknown", totals[0]["model"])
        self.assertEqual(50, totals[0]["cache_read_input_tokens"])
        self.assertNotIn("cached_input_tokens", totals[0])
        self.assertEqual(3, totals[1]["cached_input_tokens"])

    def test_cli_partial_input_emits_usable_aggregates_without_exposing_bad_records(self):
        with tempfile.TemporaryDirectory() as directory:
            history = Path(directory) / "normalized.jsonl"
            history.write_text(json.dumps(message()) + '\n{"secret": "synthetic-bad-record"}\n')
            result = subprocess.run([sys.executable, str(SCRIPT), str(history)], capture_output=True, text=True)
        self.assertEqual(1, result.returncode)
        self.assertEqual([2], json.loads(result.stdout)["input"]["invalid_record_lines"])
        self.assertNotIn("synthetic-bad-record", result.stdout + result.stderr)
        self.assertNotIn("PRIVATE EXAMPLE TEXT", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
