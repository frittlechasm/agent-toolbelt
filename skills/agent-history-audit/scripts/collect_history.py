#!/usr/bin/env python3
"""Collect redacted, normalized Claude and Codex conversation events."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import socket
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


REDACTED = "[REDACTED]"
PRIVATE_KEY = re.compile(
    r"-----BEGIN [^-]+ PRIVATE KEY-----.*?-----END [^-]+ PRIVATE KEY-----",
    re.DOTALL,
)
# Preserve quotes and separators so redacted snippets remain readable and valid-looking.
ASSIGNED_SECRET = re.compile(
    r"(?i)([\"']?(?:password|passwd|token|api[_-]?key|secret)[\"']?\s*[:=]\s*[\"']?)"
    r"([^\s,;\"']+)([\"']?)"
)
AUTHORIZATION = re.compile(
    r"(?i)([\"']?authorization[\"']?\s*[:=]\s*[\"']?(?:(?:Bearer|Basic)\s+)?)"
    r"([^\s,;\"']+)([\"']?)"
)
BEARER_TOKEN = re.compile(r"(?i)\b(Bearer\s+)([A-Za-z0-9._~+/=-]{12,})")
KNOWN_TOKEN = re.compile(r"\b(sk-[A-Za-z0-9_-]{12,}|gh[oprsu]_[A-Za-z0-9_]{12,}|xox[baprs]-[A-Za-z0-9-]{12,})\b")
URL_PASSWORD = re.compile(r"(?i)(https?://[^\s/:@]+:)([^\s/@]+)(@)")
INJECTED_MARKERS = (
    "<local-command-caveat>",
    "<task-notification>",
    "<system-reminder>",
    "<command-name>",
)


def redact(text: str) -> str:
    text = PRIVATE_KEY.sub(REDACTED, text)
    text = AUTHORIZATION.sub(lambda match: match.group(1) + REDACTED + match.group(3), text)
    text = BEARER_TOKEN.sub(lambda match: match.group(1) + REDACTED, text)
    text = ASSIGNED_SECRET.sub(lambda match: match.group(1) + REDACTED + match.group(3), text)
    text = KNOWN_TOKEN.sub(REDACTED, text)
    return URL_PASSWORD.sub(lambda match: match.group(1) + REDACTED + match.group(3), text)


def content_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts = []
    for item in content:
        if not isinstance(item, dict):
            continue
        if item.get("type") in {"text", "input_text", "output_text"} and isinstance(item.get("text"), str):
            parts.append(item["text"])
    return "\n".join(parts)


def parse_time(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def read_jsonl(path: Path):
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle, 1):
            try:
                yield line_number, json.loads(line)
            except json.JSONDecodeError:
                continue


def make_record(
    agent: str,
    machine: str,
    path: Path,
    history_root: Path,
    line_number: int,
    timestamp: object,
    role: str,
    text: str,
) -> dict:
    cleaned = redact(text)
    return {
        "agent": agent,
        "machine": machine,
        "session": path.name,
        "session_path": path.relative_to(history_root).as_posix(),
        "line": line_number,
        "timestamp": timestamp,
        "role": role,
        "text": cleaned,
        "injected": any(marker in cleaned.lower() for marker in INJECTED_MARKERS),
        "delegated": False,
    }


def collect_claude(root: Path, machine: str) -> list[dict]:
    records = []
    projects = root / "projects"
    if not projects.exists():
        return records
    for path in projects.rglob("*.jsonl"):
        if "subagents" in path.parts:
            continue
        for line_number, item in read_jsonl(path):
            if item.get("type") not in {"user", "assistant"} or item.get("isMeta") is True:
                continue
            message = item.get("message")
            if not isinstance(message, dict) or message.get("role") not in {"user", "assistant"}:
                continue
            text = content_text(message.get("content"))
            if text:
                records.append(
                    make_record("claude", machine, path, root, line_number, item.get("timestamp"), message["role"], text)
                )
    return records


def collect_codex(root: Path, machine: str) -> list[dict]:
    records = []
    sessions = root / "sessions"
    if not sessions.exists():
        return records
    for path in sessions.rglob("*.jsonl"):
        delegated = False
        # session_meta may appear after messages, so apply delegation after reading the whole file.
        pending = []
        for line_number, item in read_jsonl(path):
            payload = item.get("payload")
            if not isinstance(payload, dict):
                continue
            if item.get("type") == "session_meta":
                source_text = json.dumps(payload.get("source", "")).lower()
                delegated = '"exec"' in source_text or "codex_exec" in source_text or "subagent" in source_text
                continue
            if item.get("type") != "response_item" or payload.get("type") != "message":
                continue
            if payload.get("role") not in {"user", "assistant"}:
                continue
            text = content_text(payload.get("content"))
            if text:
                pending.append(
                    make_record("codex", machine, path, root, line_number, item.get("timestamp"), payload["role"], text)
                )
        for record in pending:
            record["delegated"] = delegated
        records.extend(pending)
    return records


def mark_sessions(records: list[dict], recent_days: int) -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(days=recent_days)
    grouped: dict[tuple[str, str, str], list[dict]] = {}
    for record in records:
        key = (record["agent"], record["machine"], record["session_path"])
        grouped.setdefault(key, []).append(record)
        event_time = parse_time(record["timestamp"])
        record["recent"] = event_time is not None and event_time >= cutoff

    seen: dict[str, str] = {}
    for session_records in grouped.values():
        material = "\n".join(f"{r['role']}:{r['text']}" for r in session_records)
        fingerprint = hashlib.sha256(material.encode()).hexdigest()
        session_name = session_records[0]["session"]
        duplicate_of = seen.get(fingerprint)
        seen.setdefault(fingerprint, session_name)
        for record in session_records:
            record["session_fingerprint"] = fingerprint
            record["duplicate_of"] = duplicate_of


def collect_local(args: argparse.Namespace) -> list[dict]:
    machine = args.machine or socket.gethostname().split(".")[0]
    records = collect_claude(Path(args.claude_root).expanduser(), machine)
    records.extend(collect_codex(Path(args.codex_root).expanduser(), machine))
    return records


def collect_remote(host: str) -> list[dict]:
    command = [
        "ssh", "--", host, "python3", "-", "--machine", host, "--no-local-summary",
    ]
    try:
        # Send this script over stdin so the remote machine needs only Python and SSH access.
        result = subprocess.run(
            command,
            input=Path(__file__).read_bytes(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as error:
        raise RuntimeError(f"{host}: could not start SSH: {error}") from error
    if result.returncode != 0:
        error = result.stderr.decode(errors="replace").strip()
        raise RuntimeError(f"{host}: history collection failed: {error}")
    try:
        return [json.loads(line) for line in result.stdout.decode(errors="replace").splitlines() if line.strip()]
    except json.JSONDecodeError as error:
        raise RuntimeError(f"{host}: history collection returned invalid JSON") from error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recent-days", type=int, default=14)
    parser.add_argument("--ssh-host", action="append", default=[])
    parser.add_argument("--machine")
    parser.add_argument("--claude-root", default="~/.claude")
    parser.add_argument("--codex-root", default="~/.codex")
    parser.add_argument("--no-local-summary", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.recent_days < 1:
        parser.error("--recent-days must be positive")

    records = collect_local(args)
    failures = []
    for host in args.ssh_host:
        try:
            records.extend(collect_remote(host))
        except RuntimeError as error:
            failures.append(str(error))

    mark_sessions(records, args.recent_days)
    records.sort(key=lambda item: (str(item.get("timestamp")), item["machine"], item["session"], item["line"]))
    for record in records:
        print(json.dumps(record, ensure_ascii=False))

    if not args.no_local_summary:
        print(f"collected {len(records)} events; remote failures: {len(failures)}", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
