import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "collect_history.py"
SPEC = importlib.util.spec_from_file_location("collect_history", MODULE_PATH)
collect_history = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(collect_history)


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record) + "\n" for record in records))


class CollectHistoryTests(unittest.TestCase):
    def test_redact_masks_passwords_in_uri_authority(self):
        cases = (
            (
                "postgres://audit:database-password@db.internal/history",
                "postgres://audit:[REDACTED]@db.internal/history",
            ),
            (
                "mongodb+srv://audit:database-password@cluster.internal/history",
                "mongodb+srv://audit:[REDACTED]@cluster.internal/history",
            ),
            (
                "https://audit:web-password@example.internal/history",
                "https://audit:[REDACTED]@example.internal/history",
            ),
            (
                "postgres://audit@db.internal/history",
                "postgres://audit@db.internal/history",
            ),
        )

        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(expected, collect_history.redact(value))

    def test_claude_captures_model_and_deduplicates_usage_by_message_id(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            message = {
                "role": "assistant",
                "id": "msg-1",
                "model": "claude-test",
                "content": [{"type": "text", "text": "Result"}],
                "usage": {
                    "input_tokens": 10,
                    "cache_read_input_tokens": 7,
                    "output_tokens": 3,
                },
            }
            write_jsonl(
                root / "projects" / "session.jsonl",
                [
                    {"type": "assistant", "timestamp": "2026-08-01T00:00:00Z", "message": message},
                    {"type": "assistant", "timestamp": "2026-08-01T00:00:01Z", "message": message},
                ],
            )

            records = collect_history.collect_claude(root, "test-machine")

            messages = [record for record in records if record["record_type"] == "message"]
            usage = [record for record in records if record["record_type"] == "usage"]
            self.assertEqual(2, len(messages))
            self.assertEqual("claude-test", messages[0]["model"])
            self.assertEqual(1, len(usage))
            self.assertEqual(10, usage[0]["usage"]["input_tokens"])
            self.assertEqual("assistant_message", usage[0]["usage_source"])
            self.assertEqual("msg-1", usage[0]["message_id"])

    def test_claude_deduplicates_usage_across_resumed_session_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            message = {
                "role": "assistant",
                "id": "msg-1",
                "model": "claude-test",
                "content": [{"type": "text", "text": "Result"}],
                "usage": {"input_tokens": 10, "output_tokens": 3},
            }
            for name in ("session-a.jsonl", "session-b.jsonl"):
                write_jsonl(
                    root / "projects" / name,
                    [{"type": "assistant", "timestamp": "2026-08-01T00:00:00Z", "message": message}],
                )

            records = collect_history.collect_claude(root, "test-machine")

            usage = [record for record in records if record["record_type"] == "usage"]
            self.assertEqual(1, len(usage))

    def test_codex_uses_legacy_token_count_when_response_records_are_absent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_jsonl(
                root / "sessions" / "session.jsonl",
                [
                    {
                        "type": "turn_context",
                        "timestamp": "2026-08-01T00:00:00Z",
                        "payload": {"model": "gpt-test"},
                    },
                    {
                        "type": "response_item",
                        "timestamp": "2026-08-01T00:00:01Z",
                        "payload": {
                            "type": "message",
                            "role": "assistant",
                            "content": [{"type": "output_text", "text": "Result"}],
                        },
                    },
                    {
                        "type": "event_msg",
                        "timestamp": "2026-08-01T00:00:02Z",
                        "payload": {
                            "type": "token_count",
                            "info": {
                                "last_token_usage": {
                                    "input_tokens": 20,
                                    "cached_input_tokens": 12,
                                    "output_tokens": 5,
                                    "reasoning_output_tokens": 2,
                                }
                            },
                        },
                    },
                ],
            )

            records = collect_history.collect_codex(root, "test-machine")

            self.assertEqual("gpt-test", records[0]["model"])
            self.assertEqual("usage", records[1]["record_type"])
            self.assertEqual("gpt-test", records[1]["model"])
            self.assertEqual(2, records[1]["usage"]["reasoning_output_tokens"])
            self.assertEqual("token_count", records[1]["usage_source"])

    def test_codex_prefers_response_usage_and_deduplicates_response_id(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            response_usage = {
                "input_tokens": 20,
                "cached_input_tokens": 12,
                "cache_write_input_tokens": 4,
                "output_tokens": 5,
                "reasoning_output_tokens": 2,
                "total_tokens": 25,
            }
            write_jsonl(
                root / "sessions" / "session-a.jsonl",
                [
                    {
                        "type": "session_meta",
                        "timestamp": "2026-09-01T00:00:00Z",
                        "payload": {"id": "thread-1", "source": "cli"},
                    },
                    {
                        "type": "turn_context",
                        "timestamp": "2026-09-01T00:00:01Z",
                        "payload": {"model": "gpt-test"},
                    },
                    {
                        "type": "event_msg",
                        "timestamp": "2026-09-01T00:00:02Z",
                        "payload": {
                            "type": "token_count",
                            "info": {
                                "total_token_usage": response_usage,
                                "last_token_usage": response_usage,
                            },
                        },
                    },
                    {
                        "type": "token_usage_record",
                        "timestamp": "2026-09-01T00:00:03Z",
                        "payload": {"response_id": "resp-1", "usage": response_usage},
                    },
                    {
                        "type": "token_usage_record",
                        "timestamp": "2026-09-01T00:00:04Z",
                        "payload": {"response_id": "resp-1", "usage": response_usage},
                    },
                ],
            )

            records = collect_history.collect_codex(root, "test-machine")

            usage = [record for record in records if record["record_type"] == "usage"]
            self.assertEqual(1, len(usage))
            self.assertEqual("token_usage_record", usage[0]["usage_source"])
            self.assertEqual("resp-1", usage[0]["response_id"])
            self.assertEqual("thread-1", usage[0]["thread_id"])
            self.assertEqual(4, usage[0]["usage"]["cache_write_input_tokens"])

    def test_codex_preserves_legacy_only_usage_in_mixed_format_session(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            legacy_usage = {"input_tokens": 100, "output_tokens": 10, "total_tokens": 110}
            response_usage = {"input_tokens": 200, "output_tokens": 20, "total_tokens": 220}
            write_jsonl(
                root / "sessions" / "session.jsonl",
                [
                    {
                        "type": "session_meta",
                        "timestamp": "2026-09-01T00:00:00Z",
                        "payload": {"id": "thread-1", "source": "cli"},
                    },
                    {
                        "type": "event_msg",
                        "timestamp": "2026-09-01T00:00:01Z",
                        "payload": {
                            "type": "token_count",
                            "info": {
                                "total_token_usage": legacy_usage,
                                "last_token_usage": legacy_usage,
                            },
                        },
                    },
                    {
                        "type": "token_usage_record",
                        "timestamp": "2026-09-01T00:00:02Z",
                        "payload": {"response_id": "resp-1", "usage": response_usage},
                    },
                    {
                        "type": "event_msg",
                        "timestamp": "2026-09-01T00:00:03Z",
                        "payload": {
                            "type": "token_count",
                            "info": {
                                "total_token_usage": {
                                    "input_tokens": 300,
                                    "output_tokens": 30,
                                    "total_tokens": 330,
                                },
                                "last_token_usage": response_usage,
                            },
                        },
                    },
                ],
            )

            records = collect_history.collect_codex(root, "test-machine")

            usage = [record for record in records if record["record_type"] == "usage"]
            self.assertEqual(2, len(usage))
            self.assertEqual(300, sum(record["usage"]["input_tokens"] for record in usage))
            self.assertEqual({"token_count", "token_usage_record"}, {record["usage_source"] for record in usage})

    def test_codex_deduplicates_response_usage_across_resumed_session_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("session-a.jsonl", "session-b.jsonl"):
                write_jsonl(
                    root / "sessions" / name,
                    [
                        {
                            "type": "session_meta",
                            "timestamp": "2026-09-01T00:00:00Z",
                            "payload": {"id": "thread-1", "source": "cli"},
                        },
                        {
                            "type": "token_usage_record",
                            "timestamp": "2026-09-01T00:00:01Z",
                            "payload": {
                                "response_id": "resp-1",
                                "usage": {"input_tokens": 20, "output_tokens": 5},
                            },
                        },
                    ],
                )

            records = collect_history.collect_codex(root, "test-machine")

            usage = [record for record in records if record["record_type"] == "usage"]
            self.assertEqual(1, len(usage))

    def test_codex_deduplicates_legacy_usage_across_session_copies(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            usage = {"input_tokens": 100, "output_tokens": 10, "total_tokens": 110}
            for name in ("session-a.jsonl", "session-b.jsonl"):
                write_jsonl(
                    root / "sessions" / name,
                    [
                        {
                            "type": "session_meta",
                            "timestamp": "2026-09-01T00:00:00Z",
                            "payload": {"id": "thread-1", "source": "cli"},
                        },
                        {
                            "type": "event_msg",
                            "timestamp": "2026-09-01T00:00:01Z",
                            "payload": {
                                "type": "token_count",
                                "info": {
                                    "total_token_usage": usage,
                                    "last_token_usage": usage,
                                },
                            },
                        },
                    ],
                )

            records = collect_history.collect_codex(root, "test-machine")

            usage_records = [record for record in records if record["record_type"] == "usage"]
            self.assertEqual(1, len(usage_records))

    def test_codex_reconciles_after_deduplicating_authoritative_records(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            usage = {"input_tokens": 100, "output_tokens": 10, "total_tokens": 110}
            write_jsonl(
                root / "sessions" / "session.jsonl",
                [
                    {
                        "type": "session_meta",
                        "timestamp": "2026-09-01T00:00:00Z",
                        "payload": {"id": "thread-1", "source": "cli"},
                    },
                    {
                        "type": "event_msg",
                        "timestamp": "2026-09-01T00:00:01Z",
                        "payload": {
                            "type": "token_count",
                            "info": {"total_token_usage": usage, "last_token_usage": usage},
                        },
                    },
                    {
                        "type": "token_usage_record",
                        "timestamp": "2026-09-01T01:00:00Z",
                        "payload": {"response_id": "resp-1", "usage": usage},
                    },
                    {
                        "type": "token_usage_record",
                        "timestamp": "2026-09-01T01:00:00Z",
                        "payload": {"response_id": "resp-1", "usage": usage},
                    },
                    {
                        "type": "event_msg",
                        "timestamp": "2026-09-01T01:00:01Z",
                        "payload": {
                            "type": "token_count",
                            "info": {
                                "total_token_usage": {
                                    "input_tokens": 200,
                                    "output_tokens": 20,
                                    "total_tokens": 220,
                                },
                                "last_token_usage": usage,
                            },
                        },
                    },
                ],
            )

            records = collect_history.collect_codex(root, "test-machine")

            usage_records = [record for record in records if record["record_type"] == "usage"]
            self.assertEqual(2, len(usage_records))
            self.assertEqual(200, sum(record["usage"]["input_tokens"] for record in usage_records))

    def test_codex_reconciles_mirrored_usage_across_session_copies(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            usage = {"input_tokens": 100, "output_tokens": 10, "total_tokens": 110}
            write_jsonl(
                root / "sessions" / "legacy-copy.jsonl",
                [
                    {
                        "type": "session_meta",
                        "timestamp": "2026-09-01T00:00:00Z",
                        "payload": {"id": "thread-1", "source": "cli"},
                    },
                    {
                        "type": "event_msg",
                        "timestamp": "2026-09-01T00:00:02Z",
                        "payload": {
                            "type": "token_count",
                            "info": {"total_token_usage": usage, "last_token_usage": usage},
                        },
                    },
                ],
            )
            write_jsonl(
                root / "sessions" / "complete-copy.jsonl",
                [
                    {
                        "type": "session_meta",
                        "timestamp": "2026-09-01T00:00:00Z",
                        "payload": {"id": "thread-1", "source": "cli"},
                    },
                    {
                        "type": "token_usage_record",
                        "timestamp": "2026-09-01T00:00:01Z",
                        "payload": {"response_id": "resp-1", "usage": usage},
                    },
                    {
                        "type": "event_msg",
                        "timestamp": "2026-09-01T00:00:02Z",
                        "payload": {
                            "type": "token_count",
                            "info": {"total_token_usage": usage, "last_token_usage": usage},
                        },
                    },
                ],
            )

            records = collect_history.collect_codex(root, "test-machine")

            usage_records = [record for record in records if record["record_type"] == "usage"]
            self.assertEqual(1, len(usage_records))
            self.assertEqual("token_usage_record", usage_records[0]["usage_source"])

    def test_codex_reconciliation_uses_time_for_equal_sized_responses(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            usage = {"input_tokens": 100, "output_tokens": 10, "total_tokens": 110}
            write_jsonl(
                root / "sessions" / "session.jsonl",
                [
                    {
                        "type": "session_meta",
                        "timestamp": "2026-09-01T00:00:00Z",
                        "payload": {"id": "thread-1", "source": "cli"},
                    },
                    {
                        "type": "event_msg",
                        "timestamp": "2026-09-01T00:00:01Z",
                        "payload": {
                            "type": "token_count",
                            "info": {"total_token_usage": usage, "last_token_usage": usage},
                        },
                    },
                    {
                        "type": "token_usage_record",
                        "timestamp": "2026-09-02T00:00:00Z",
                        "payload": {"response_id": "resp-1", "usage": usage},
                    },
                    {
                        "type": "event_msg",
                        "timestamp": "2026-09-02T00:00:01Z",
                        "payload": {
                            "type": "token_count",
                            "info": {
                                "total_token_usage": {
                                    "input_tokens": 200,
                                    "output_tokens": 20,
                                    "total_tokens": 220,
                                },
                                "last_token_usage": usage,
                            },
                        },
                    },
                ],
            )

            records = collect_history.collect_codex(root, "test-machine")

            usage_records = [record for record in records if record["record_type"] == "usage"]
            self.assertEqual(2, len(usage_records))
            september_first = collect_history.filter_time_range(
                usage_records,
                datetime(2026, 9, 1, tzinfo=timezone.utc),
                datetime(2026, 9, 2, tzinfo=timezone.utc),
            )
            september_second = collect_history.filter_time_range(
                usage_records,
                datetime(2026, 9, 2, tzinfo=timezone.utc),
                datetime(2026, 9, 3, tzinfo=timezone.utc),
            )
            self.assertEqual("token_count", september_first[0]["usage_source"])
            self.assertEqual("token_usage_record", september_second[0]["usage_source"])

    def test_main_does_not_reconcile_authoritative_usage_twice(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            usage = {"input_tokens": 100, "output_tokens": 10, "total_tokens": 110}
            write_jsonl(
                root / "codex" / "sessions" / "session.jsonl",
                [
                    {
                        "type": "session_meta",
                        "timestamp": "2026-09-01T00:00:00Z",
                        "payload": {"id": "thread-1", "source": "cli"},
                    },
                    {
                        "type": "event_msg",
                        "timestamp": "2026-09-01T00:00:01Z",
                        "payload": {
                            "type": "token_count",
                            "info": {"total_token_usage": usage, "last_token_usage": usage},
                        },
                    },
                    {
                        "type": "token_usage_record",
                        "timestamp": "2026-09-01T00:00:20Z",
                        "payload": {"response_id": "resp-1", "usage": usage},
                    },
                    {
                        "type": "event_msg",
                        "timestamp": "2026-09-01T00:00:21Z",
                        "payload": {
                            "type": "token_count",
                            "info": {
                                "total_token_usage": {
                                    "input_tokens": 200,
                                    "output_tokens": 20,
                                    "total_tokens": 220,
                                },
                                "last_token_usage": usage,
                            },
                        },
                    },
                ],
            )
            arguments = [
                "collect_history.py",
                "--agent",
                "codex",
                "--claude-root",
                str(root / "claude"),
                "--codex-root",
                str(root / "codex"),
                "--no-local-summary",
            ]
            output = io.StringIO()

            original_arguments = sys.argv
            try:
                sys.argv = arguments
                with redirect_stdout(output):
                    self.assertEqual(0, collect_history.main())
            finally:
                sys.argv = original_arguments

            records = [json.loads(line) for line in output.getvalue().splitlines()]
            usage_records = [record for record in records if record["record_type"] == "usage"]
            self.assertEqual(2, len(usage_records))

    def test_reconciliation_removes_mirror_from_later_synchronized_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            usage = {"input_tokens": 100, "output_tokens": 10, "total_tokens": 110}
            local_root = root / "local"
            remote_root = root / "remote"
            session_meta = {
                "type": "session_meta",
                "timestamp": "2026-09-01T00:00:00Z",
                "payload": {"id": "thread-1", "source": "cli"},
            }
            legacy = {
                "type": "event_msg",
                "timestamp": "2026-09-01T00:00:02Z",
                "payload": {
                    "type": "token_count",
                    "info": {"total_token_usage": usage, "last_token_usage": usage},
                },
            }
            write_jsonl(
                local_root / "sessions" / "session.jsonl",
                [
                    session_meta,
                    {
                        "type": "token_usage_record",
                        "timestamp": "2026-09-01T00:00:01Z",
                        "payload": {"response_id": "resp-1", "usage": usage},
                    },
                    legacy,
                ],
            )
            write_jsonl(remote_root / "sessions" / "session.jsonl", [session_meta, legacy])

            records = collect_history.collect_codex(local_root, "local")
            records.extend(collect_history.collect_codex(remote_root, "remote"))
            records = collect_history.deduplicate_usage_records(records)
            records = collect_history.reconcile_codex_usage(records)

            usage_records = [record for record in records if record["record_type"] == "usage"]
            self.assertEqual(1, len(usage_records))
            self.assertEqual("token_usage_record", usage_records[0]["usage_source"])

    def test_codex_legacy_usage_deduplicates_repeated_cumulative_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            last_usage = {"input_tokens": 20, "output_tokens": 5, "total_tokens": 25}
            write_jsonl(
                root / "sessions" / "session.jsonl",
                [
                    {
                        "type": "event_msg",
                        "timestamp": "2026-08-01T00:00:01Z",
                        "payload": {
                            "type": "token_count",
                            "info": {
                                "total_token_usage": last_usage,
                                "last_token_usage": last_usage,
                            },
                        },
                    },
                    {
                        "type": "event_msg",
                        "timestamp": "2026-08-01T00:00:02Z",
                        "payload": {
                            "type": "token_count",
                            "info": {
                                "total_token_usage": last_usage,
                                "last_token_usage": last_usage,
                            },
                        },
                    },
                    {
                        "type": "event_msg",
                        "timestamp": "2026-08-01T00:00:03Z",
                        "payload": {
                            "type": "token_count",
                            "info": {
                                "total_token_usage": {
                                    "input_tokens": 40,
                                    "output_tokens": 10,
                                    "total_tokens": 50,
                                },
                                "last_token_usage": last_usage,
                            },
                        },
                    },
                ],
            )

            records = collect_history.collect_codex(root, "test-machine")

            usage = [record for record in records if record["record_type"] == "usage"]
            self.assertEqual(2, len(usage))

    def test_codex_groups_nested_delegates_under_root_thread(self):
        records = [
            {"agent": "codex", "thread_id": "root", "parent_thread_id": None},
            {"agent": "codex", "thread_id": "child", "parent_thread_id": "root"},
            {"agent": "codex", "thread_id": "grandchild", "parent_thread_id": "child"},
        ]

        collect_history.mark_codex_thread_roots(records)

        self.assertEqual(["root", "root", "root"], [record["root_thread_id"] for record in records])

    def test_codex_does_not_classify_top_level_exec_as_delegated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_jsonl(
                root / "sessions" / "session.jsonl",
                [
                    {
                        "type": "session_meta",
                        "timestamp": "2026-09-01T00:00:00Z",
                        "payload": {"id": "thread-1", "source": {"exec": {}}},
                    },
                    {
                        "type": "response_item",
                        "timestamp": "2026-09-01T00:00:01Z",
                        "payload": {
                            "type": "message",
                            "role": "assistant",
                            "content": [{"type": "output_text", "text": "Result"}],
                        },
                    },
                ],
            )

            records = collect_history.collect_codex(root, "test-machine")

            self.assertFalse(records[0]["delegated"])
            self.assertEqual("exec", records[0]["session_source"])
            self.assertEqual(["exec"], records[0]["session_sources"])

    def test_collect_local_honors_agent_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_jsonl(
                root / "claude" / "projects" / "session.jsonl",
                [
                    {
                        "type": "user",
                        "timestamp": "2026-09-01T00:00:00Z",
                        "message": {"role": "user", "content": "Claude input"},
                    }
                ],
            )
            write_jsonl(
                root / "codex" / "sessions" / "session.jsonl",
                [
                    {
                        "type": "response_item",
                        "timestamp": "2026-09-01T00:00:00Z",
                        "payload": {
                            "type": "message",
                            "role": "user",
                            "content": [{"type": "input_text", "text": "Codex input"}],
                        },
                    }
                ],
            )
            args = SimpleNamespace(
                machine="test-machine",
                agent="codex",
                claude_root=str(root / "claude"),
                codex_root=str(root / "codex"),
            )

            records = collect_history.collect_local(args)

            self.assertTrue(records)
            self.assertEqual({"codex"}, {record["agent"] for record in records})

            args.agent = "all"
            records = collect_history.collect_local(args)

            self.assertEqual({"claude", "codex"}, {record["agent"] for record in records})

    def test_time_range_is_start_inclusive_and_end_exclusive(self):
        records = [
            {"timestamp": "2026-09-04T18:29:59Z"},
            {"timestamp": "2026-09-04T18:30:00Z"},
            {"timestamp": "2026-09-11T18:30:00Z"},
        ]

        filtered = collect_history.filter_time_range(
            records,
            datetime(2026, 9, 4, 18, 30, tzinfo=timezone.utc),
            datetime(2026, 9, 11, 18, 30, tzinfo=timezone.utc),
        )

        self.assertEqual([records[1]], filtered)


if __name__ == "__main__":
    unittest.main()
