import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "collect_history.py"
SPEC = importlib.util.spec_from_file_location("collect_history", MODULE_PATH)
collect_history = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(collect_history)


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True)
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

    def test_codex_captures_turn_model_and_each_usage_event(self):
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


if __name__ == "__main__":
    unittest.main()
