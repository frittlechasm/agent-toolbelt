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
URI_PASSWORD = re.compile(
    r"(?i)(\b[a-z][a-z0-9+.-]*://[^\s/:@]+:)([^\s/@]+)(@)"
)
INJECTED_MARKERS = (
    "<local-command-caveat>",
    "<task-notification>",
    "<system-reminder>",
    "<command-name>",
)
CODEX_USAGE_MIRROR_WINDOW_SECONDS = 60


def redact(text: str) -> str:
    text = PRIVATE_KEY.sub(REDACTED, text)
    text = AUTHORIZATION.sub(lambda match: match.group(1) + REDACTED + match.group(3), text)
    text = BEARER_TOKEN.sub(lambda match: match.group(1) + REDACTED, text)
    text = ASSIGNED_SECRET.sub(lambda match: match.group(1) + REDACTED + match.group(3), text)
    text = KNOWN_TOKEN.sub(REDACTED, text)
    return URI_PASSWORD.sub(lambda match: match.group(1) + REDACTED + match.group(3), text)


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
    *,
    model: str | None = None,
    usage: dict | None = None,
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
        "record_type": "message",
        "model": model,
        "usage": usage,
        "injected": any(marker in cleaned.lower() for marker in INJECTED_MARKERS),
        "delegated": False,
    }


def normalized_usage(usage: object) -> dict | None:
    if not isinstance(usage, dict):
        return None
    fields = (
        "input_tokens",
        "cached_input_tokens",
        "cache_write_input_tokens",
        "cache_creation_input_tokens",
        "cache_read_input_tokens",
        "output_tokens",
        "reasoning_output_tokens",
        "total_tokens",
    )
    result = {field: usage[field] for field in fields if isinstance(usage.get(field), int)}
    return result or None


def codex_usage_signature(usage: object) -> tuple[int, ...] | None:
    cleaned = normalized_usage(usage)
    if cleaned is None:
        return None
    fields = (
        "input_tokens",
        "cached_input_tokens",
        "cache_write_input_tokens",
        "output_tokens",
        "reasoning_output_tokens",
    )
    return tuple(cleaned.get(field, 0) for field in fields)


def make_usage_record(
    agent: str,
    machine: str,
    path: Path,
    history_root: Path,
    line_number: int,
    timestamp: object,
    model: str | None,
    usage: object,
) -> dict | None:
    cleaned_usage = normalized_usage(usage)
    if cleaned_usage is None:
        return None
    return {
        "agent": agent,
        "machine": machine,
        "session": path.name,
        "session_path": path.relative_to(history_root).as_posix(),
        "line": line_number,
        "timestamp": timestamp,
        "role": "usage",
        "text": "",
        "record_type": "usage",
        "model": model,
        "usage": cleaned_usage,
        "injected": False,
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
        seen_usage_ids = set()
        for line_number, item in read_jsonl(path):
            if item.get("type") not in {"user", "assistant"} or item.get("isMeta") is True:
                continue
            message = item.get("message")
            if not isinstance(message, dict) or message.get("role") not in {"user", "assistant"}:
                continue
            text = content_text(message.get("content"))
            if text:
                records.append(
                    make_record(
                        "claude",
                        machine,
                        path,
                        root,
                        line_number,
                        item.get("timestamp"),
                        message["role"],
                        text,
                        model=message.get("model") if isinstance(message.get("model"), str) else None,
                    )
                )
            message_id = message.get("id")
            if message["role"] == "assistant" and message_id not in seen_usage_ids:
                usage_record = make_usage_record(
                    "claude",
                    machine,
                    path,
                    root,
                    line_number,
                    item.get("timestamp"),
                    message.get("model") if isinstance(message.get("model"), str) else None,
                    message.get("usage"),
                )
                if usage_record is not None:
                    usage_record["usage_source"] = "assistant_message"
                    usage_record["message_id"] = message_id if isinstance(message_id, str) else None
                    records.append(usage_record)
                    if message_id is not None:
                        seen_usage_ids.add(message_id)
    return deduplicate_usage_records(records)


def collect_codex(root: Path, machine: str) -> list[dict]:
    records = []
    sessions = root / "sessions"
    if not sessions.exists():
        return records
    for path in sessions.rglob("*.jsonl"):
        delegated = False
        current_model = None
        thread_id = None
        parent_thread_id = None
        agent_path = None
        originator = None
        session_source = None
        session_sources = []
        # session_meta may appear after messages or repeat, so accumulate delegation across the file.
        message_records = []
        response_usage_records = []
        legacy_usage_records = []
        seen_legacy_snapshots = set()
        for line_number, item in read_jsonl(path):
            payload = item.get("payload")
            if not isinstance(payload, dict):
                continue
            if item.get("type") == "session_meta":
                session_id = payload.get("id")
                if isinstance(session_id, str):
                    thread_id = session_id
                source = payload.get("source")
                if isinstance(source, str):
                    session_source = source
                    session_sources = [source]
                if isinstance(source, dict):
                    session_sources = sorted(str(key) for key in source)
                    if session_sources:
                        session_source = session_sources[0]
                    subagent = source.get("subagent")
                    thread_spawn = subagent.get("thread_spawn") if isinstance(subagent, dict) else None
                    if isinstance(thread_spawn, dict):
                        session_source = "subagent"
                        parent = thread_spawn.get("parent_thread_id")
                        if isinstance(parent, str):
                            parent_thread_id = parent
                        path_value = thread_spawn.get("agent_path")
                        if isinstance(path_value, str):
                            agent_path = path_value
                originator_value = payload.get("originator")
                if isinstance(originator_value, str):
                    originator = originator_value
                source_text = json.dumps(payload.get("source", "")).lower()
                delegated = delegated or (
                    "codex_exec" in source_text or "subagent" in source_text
                )
                continue
            if item.get("type") == "turn_context":
                model = payload.get("model")
                if isinstance(model, str):
                    current_model = model
                continue
            if item.get("type") == "token_usage_record":
                usage_record = make_usage_record(
                    "codex",
                    machine,
                    path,
                    root,
                    line_number,
                    item.get("timestamp"),
                    current_model,
                    payload.get("usage"),
                )
                if usage_record is not None:
                    usage_record["usage_source"] = "token_usage_record"
                    response_id = payload.get("response_id")
                    usage_record["response_id"] = response_id if isinstance(response_id, str) else None
                    response_usage_records.append(usage_record)
                continue
            if item.get("type") == "event_msg" and payload.get("type") == "token_count":
                info = payload.get("info")
                usage = info.get("last_token_usage") if isinstance(info, dict) else None
                total_usage = info.get("total_token_usage") if isinstance(info, dict) else None
                total_snapshot = normalized_usage(total_usage)
                if total_snapshot is not None:
                    snapshot_key = json.dumps(total_snapshot, sort_keys=True)
                    if snapshot_key in seen_legacy_snapshots:
                        continue
                    seen_legacy_snapshots.add(snapshot_key)
                usage_record = make_usage_record(
                    "codex",
                    machine,
                    path,
                    root,
                    line_number,
                    item.get("timestamp"),
                    current_model,
                    usage,
                )
                if usage_record is not None:
                    usage_record["usage_source"] = "token_count"
                    usage_record["response_id"] = None
                    snapshot_material = {
                        "timestamp": item.get("timestamp"),
                        "total_usage": total_snapshot,
                        "usage": usage_record["usage"] if total_snapshot is None else None,
                    }
                    usage_record["legacy_snapshot_id"] = hashlib.sha256(
                        json.dumps(snapshot_material, sort_keys=True).encode()
                    ).hexdigest()
                    legacy_usage_records.append(usage_record)
                continue
            if item.get("type") != "response_item" or payload.get("type") != "message":
                continue
            if payload.get("role") not in {"user", "assistant"}:
                continue
            text = content_text(payload.get("content"))
            if text:
                message_records.append(
                    make_record(
                        "codex",
                        machine,
                        path,
                        root,
                        line_number,
                        item.get("timestamp"),
                        payload["role"],
                        text,
                        model=current_model if payload["role"] == "assistant" else None,
                    )
                )
        usage_records = response_usage_records + legacy_usage_records
        pending = message_records + usage_records
        delegated = delegated or parent_thread_id is not None
        for record in pending:
            record["delegated"] = delegated
            record["thread_id"] = thread_id
            record["parent_thread_id"] = parent_thread_id
            record["agent_path"] = agent_path
            record["originator"] = originator
            record["session_source"] = session_source
            record["session_sources"] = session_sources
        records.extend(sorted(pending, key=lambda record: record["line"]))
    mark_codex_thread_roots(records)
    records = deduplicate_usage_records(records)
    return reconcile_codex_usage(records)


def mark_codex_thread_roots(records: list[dict]) -> None:
    parents = {
        record["thread_id"]: record.get("parent_thread_id")
        for record in records
        if record.get("agent") == "codex" and isinstance(record.get("thread_id"), str)
    }
    for record in records:
        thread_id = record.get("thread_id")
        if record.get("agent") != "codex" or not isinstance(thread_id, str):
            continue
        root_thread_id = thread_id
        seen = {thread_id}
        parent_thread_id = parents.get(thread_id)
        while isinstance(parent_thread_id, str) and parent_thread_id not in seen:
            root_thread_id = parent_thread_id
            seen.add(parent_thread_id)
            parent_thread_id = parents.get(parent_thread_id)
        record["root_thread_id"] = root_thread_id


def deduplicate_usage_records(records: list[dict]) -> list[dict]:
    """Count each response once, including resumed or synchronized session files."""
    result = []
    seen = {}
    for record in records:
        response_id = record.get("response_id")
        message_id = record.get("message_id")
        if (
            record.get("agent") == "codex"
            and record.get("record_type") == "usage"
            and record.get("usage_source") == "token_usage_record"
            and isinstance(response_id, str)
        ):
            thread_scope = record.get("thread_id")
            if not isinstance(thread_scope, str):
                thread_scope = (record.get("machine"), record.get("session_path"))
            key = ("codex-response", thread_scope, response_id)
        elif (
            record.get("agent") == "claude"
            and record.get("record_type") == "usage"
            and isinstance(message_id, str)
        ):
            key = ("claude", message_id)
        elif (
            record.get("agent") == "codex"
            and record.get("record_type") == "usage"
            and record.get("usage_source") == "token_count"
            and isinstance(record.get("legacy_snapshot_id"), str)
        ):
            thread_scope = record.get("thread_id")
            if not isinstance(thread_scope, str):
                thread_scope = (record.get("machine"), record.get("session_path"))
            key = ("codex-legacy", thread_scope, record["legacy_snapshot_id"])
        else:
            key = None
        if key is not None:
            if key in seen:
                existing_ids = seen[key].get("legacy_mirror_ids", [])
                incoming_ids = record.get("legacy_mirror_ids", [])
                if isinstance(existing_ids, list) and isinstance(incoming_ids, list):
                    seen[key]["legacy_mirror_ids"] = list(dict.fromkeys(existing_ids + incoming_ids))
                continue
            seen[key] = record
        result.append(record)
    return result


def reconcile_codex_usage(records: list[dict]) -> list[dict]:
    """Remove legacy token-count mirrors of authoritative response records."""
    authoritative = {}
    legacy = {}
    consumed_legacy = set()
    for record in records:
        if record.get("agent") != "codex" or record.get("usage_source") != "token_usage_record":
            continue
        thread_scope = record.get("thread_id")
        if not isinstance(thread_scope, str):
            thread_scope = (record.get("machine"), record.get("session_path"))
        mirror_ids = record.get("legacy_mirror_ids", [])
        if isinstance(mirror_ids, list):
            consumed_legacy.update(
                (thread_scope, mirror_id) for mirror_id in mirror_ids if isinstance(mirror_id, str)
            )

    previously_consumed_legacy = set()
    for index, record in enumerate(records):
        if record.get("agent") != "codex" or record.get("record_type") != "usage":
            continue
        signature = codex_usage_signature(record.get("usage"))
        event_time = parse_time(record.get("timestamp"))
        if signature is None or event_time is None:
            continue
        thread_scope = record.get("thread_id")
        if not isinstance(thread_scope, str):
            thread_scope = (record.get("machine"), record.get("session_path"))
        key = (thread_scope, signature)
        item = (index, event_time, record.get("session_path"))
        mirror_ids = record.get("legacy_mirror_ids", [])
        if record.get("usage_source") == "token_usage_record" and not mirror_ids:
            authoritative.setdefault(key, []).append(item)
        elif record.get("usage_source") == "token_count":
            snapshot_id = record.get("legacy_snapshot_id")
            if isinstance(snapshot_id, str) and (thread_scope, snapshot_id) in consumed_legacy:
                previously_consumed_legacy.add(index)
                continue
            legacy.setdefault(key, []).append(item)

    candidates = []
    for key, legacy_items in legacy.items():
        for legacy_index, legacy_time, legacy_path in legacy_items:
            for response_index, response_time, response_path in authoritative.get(key, []):
                delta_seconds = (legacy_time - response_time).total_seconds()
                if abs(delta_seconds) > CODEX_USAGE_MIRROR_WINDOW_SECONDS:
                    continue
                candidates.append(
                    (
                        0 if delta_seconds >= 0 else 1,
                        abs(delta_seconds),
                        0 if legacy_path == response_path else 1,
                        legacy_index,
                        response_index,
                    )
                )

    matched_legacy = set()
    matched_authoritative = set()
    for _, _, _, legacy_index, response_index in sorted(candidates):
        if legacy_index in matched_legacy or response_index in matched_authoritative:
            continue
        matched_legacy.add(legacy_index)
        matched_authoritative.add(response_index)
        snapshot_id = records[legacy_index].get("legacy_snapshot_id")
        if isinstance(snapshot_id, str):
            records[response_index]["legacy_mirror_ids"] = [snapshot_id]

    removed_legacy = matched_legacy | previously_consumed_legacy
    return [record for index, record in enumerate(records) if index not in removed_legacy]


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
        material = "\n".join(
            f"{r['role']}:{r['text']}" for r in session_records if r["record_type"] == "message"
        )
        fingerprint = hashlib.sha256(material.encode()).hexdigest()
        session_name = session_records[0]["session"]
        duplicate_of = seen.get(fingerprint)
        seen.setdefault(fingerprint, session_name)
        for record in session_records:
            record["session_fingerprint"] = fingerprint
            record["duplicate_of"] = duplicate_of


def filter_time_range(
    records: list[dict],
    since: datetime | None,
    until: datetime | None,
) -> list[dict]:
    result = []
    for record in records:
        event_time = parse_time(record.get("timestamp"))
        if event_time is None:
            continue
        if since is not None and event_time < since:
            continue
        if until is not None and event_time >= until:
            continue
        result.append(record)
    return result


def collect_local(args: argparse.Namespace) -> list[dict]:
    machine = args.machine or socket.gethostname().split(".")[0]
    records = []
    if args.agent in {"all", "claude"}:
        records.extend(collect_claude(Path(args.claude_root).expanduser(), machine))
    if args.agent in {"all", "codex"}:
        records.extend(collect_codex(Path(args.codex_root).expanduser(), machine))
    return records


def collect_remote(host: str, agent: str) -> list[dict]:
    command = [
        "ssh", "--", host, "python3", "-", "--machine", host, "--agent", agent,
        "--no-local-summary",
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
    parser.add_argument("--recent-days", type=int, default=30)
    parser.add_argument("--recent-only", action="store_true")
    parser.add_argument("--since", help="inclusive ISO-8601 timestamp")
    parser.add_argument("--until", help="exclusive ISO-8601 timestamp")
    parser.add_argument("--ssh-host", action="append", default=[])
    parser.add_argument("--machine")
    parser.add_argument("--agent", choices=("all", "claude", "codex"), default="all")
    parser.add_argument("--claude-root", default="~/.claude")
    parser.add_argument("--codex-root", default="~/.codex")
    parser.add_argument("--no-local-summary", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.recent_days < 1:
        parser.error("--recent-days must be positive")
    since = parse_time(args.since) if args.since else None
    until = parse_time(args.until) if args.until else None
    if args.since and since is None:
        parser.error("--since must be an ISO-8601 timestamp")
    if args.until and until is None:
        parser.error("--until must be an ISO-8601 timestamp")
    if since is not None and until is not None and since >= until:
        parser.error("--since must be earlier than --until")

    records = collect_local(args)
    failures = []
    for host in args.ssh_host:
        try:
            records.extend(collect_remote(host, args.agent))
        except RuntimeError as error:
            failures.append(str(error))

    mark_codex_thread_roots(records)
    records = deduplicate_usage_records(records)
    records = reconcile_codex_usage(records)
    mark_sessions(records, args.recent_days)
    if since is not None or until is not None:
        records = filter_time_range(records, since, until)
    elif args.recent_only:
        records = [record for record in records if record["recent"]]
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
