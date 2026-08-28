#!/usr/bin/env python3
"""Create synthetic Claude and Codex histories for workflow evals."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")


def claude_user(timestamp: str, text: str) -> dict:
    return {
        "type": "user",
        "timestamp": timestamp,
        "message": {"role": "user", "content": [{"type": "text", "text": text}]},
    }


def claude_assistant(timestamp: str, message_id: str, text: str) -> dict:
    return {
        "type": "assistant",
        "timestamp": timestamp,
        "message": {
            "id": message_id,
            "role": "assistant",
            "model": "claude-fixture",
            "content": [{"type": "text", "text": text}],
            "usage": {"input_tokens": 20, "output_tokens": 8},
        },
    }


def main() -> None:
    workspace = Path(sys.argv[1])
    claude_root = workspace / "history" / "claude"
    codex_root = workspace / "history" / "codex"

    write_jsonl(
        claude_root / "projects" / "session-alpha.jsonl",
        [
            claude_user(
                "2026-08-25T10:00:00Z",
                "Commit this change after the parent commit while keeping the date on August 28 IST.",
            ),
            claude_assistant(
                "2026-08-25T10:01:00Z",
                "msg-alpha",
                "Committed the change using the current date.",
            ),
            claude_user(
                "2026-08-25T10:02:00Z",
                "The commit moved to August 29. Rewrite it after the parent but still on August 28 IST.",
            ),
        ],
    )
    write_jsonl(
        claude_root / "projects" / "session-beta.jsonl",
        [
            claude_user(
                "2026-08-26T11:00:00Z",
                "Make the follow-up commit chronologically after its parent on August 28 IST.",
            ),
            claude_assistant(
                "2026-08-26T11:01:00Z",
                "msg-beta",
                "Created the follow-up commit with today's timestamp.",
            ),
            claude_user(
                "2026-08-26T11:02:00Z",
                "That is August 29 again. Preserve August 28 and place it after the parent timestamp.",
            ),
        ],
    )
    write_jsonl(
        codex_root / "sessions" / "session-gamma.jsonl",
        [
            {
                "type": "turn_context",
                "timestamp": "2026-08-27T12:00:00Z",
                "payload": {"model": "codex-fixture"},
            },
            {
                "type": "response_item",
                "timestamp": "2026-08-27T12:00:01Z",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Keep this commit on August 28 IST and after its parent.",
                        }
                    ],
                },
            },
            {
                "type": "response_item",
                "timestamp": "2026-08-27T12:01:00Z",
                "payload": {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": "Committed at 2026-08-28T20:00:00+05:30 after the parent.",
                        }
                    ],
                },
            },
        ],
    )


if __name__ == "__main__":
    main()
