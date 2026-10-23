#!/usr/bin/env python3
"""Select tasks and summarize normalized collect_history.py output without emitting message text."""

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

import collect_history as collector


def event_time(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.astimezone(timezone.utc) if parsed.tzinfo else None
    except (AttributeError, TypeError, ValueError):
        return None


def session_id(record):
    return f"{record['agent']}:{record['machine']}:{record['session_path']}"


def aliases(record):
    return {value for value in (session_id(record), record["session_path"], record.get("session"),
                                record.get("thread_id"), record.get("session_id")) if isinstance(value, str)}


def task_id(record):
    root = record.get("root_thread_id") or record.get("parent_thread_id") or record.get("thread_id")
    return (record["agent"], root or session_id(record))


def last_interaction(records):
    times = [event_time(row.get("timestamp")) for row in records
             if row["record_type"] == "message" and not row.get("injected")
             and row.get("role") in {"user", "assistant"}]
    return max((value for value in times if value is not None), default=None)


def usage_totals(records):
    grouped = defaultdict(Counter)
    invalid_fields = 0
    for row in records:
        if row["record_type"] != "usage":
            continue
        totals = grouped[(row["agent"], row.get("model") or "unknown")]
        totals["records"] += 1
        usage = row.get("usage") or {}
        known_fields = collector.normalized_usage(dict.fromkeys(usage, 0)) or {}
        for field in known_fields:
            value = usage[field]
            if type(value) is int and value >= 0:
                totals[field] += value
            else:
                invalid_fields += 1
    return ([{"agent": agent, "model": model, **dict(totals)}
             for (agent, model), totals in sorted(grouped.items())], invalid_fields)


def coverage(log):
    roots, remote_failures, invalid_lines = [], None, 0
    if log is not None:
        for line in log.splitlines():
            summary = re.fullmatch(r"collected [0-9]+ events; remote failures: ([0-9]+)", line.strip())
            if summary:
                remote_failures = int(summary[1])
                continue
            if not line.lstrip().startswith("{"):
                continue
            try:
                row = json.loads(line)
                if row.get("record_type") == "collection_diagnostics":
                    roots.append({key: row.get(key) for key in (
                        "machine", "agent", "complete", "files_seen", "files_read", "invalid_records")})
            except (ValueError, AttributeError):
                invalid_lines += 1
    if remote_failures or invalid_lines or any(row.get("complete") is False for row in roots):
        status = "partial"
    elif roots and remote_failures == 0 and all(row.get("complete") is True for row in roots):
        status = "complete_for_reported_roots"
    else:
        status = "unknown"
    return {"status": status, "roots": roots, "remote_failures": remote_failures,
            "invalid_diagnostic_lines": invalid_lines}


def manifest(key, rows):
    sessions = defaultdict(list)
    for row in rows:
        sessions[session_id(row)].append(row)
    latest = last_interaction(rows)
    listed = []
    for name, items in sorted(sessions.items()):
        interaction = last_interaction(items)
        listed.append({"id": name, "last_interaction_at": interaction.isoformat() if interaction else None})
    return {"agent": key[0], "root_or_session_id": key[1],
            "last_interaction_at": latest.isoformat() if latest else None,
            "sessions": listed}


def summarize(records, *, last=None, include=(), exclude=(), diagnostics=None):
    # Normalized usage and message IDs are separate. Content fingerprints never discard records here.
    records = collector.deduplicate_message_records(records)
    records = collector.deduplicate_usage_records(records)
    records = collector.reconcile_codex_usage(records)
    groups = defaultdict(list)
    for row in records:
        groups[task_id(row)].append(row)
    retained, excluded_records = {}, 0
    for key, rows in groups.items():
        root_aliases = {key[1]}
        for row in rows:
            if row.get("thread_id") == key[1]:
                root_aliases.update(aliases(row))
        if root_aliases.intersection(exclude):
            excluded_records += len(rows)
            continue
        kept = [row for row in rows if not aliases(row).intersection(exclude)]
        excluded_records += len(rows) - len(kept)
        if kept and (not include or key[1] in include or any(aliases(row).intersection(include) for row in kept)):
            retained[key] = kept
    ranked, unranked = [], []
    for key, rows in retained.items():
        latest = last_interaction(rows)
        orphan = any(row.get("delegated") for row in rows) and not any(
            row.get("parent_thread_id") or row.get("root_thread_id") not in (None, row.get("thread_id"))
            for row in rows)
        (ranked if latest is not None and not orphan else unranked).append((key, rows))
    ranked.sort(key=lambda pair: (-last_interaction(pair[1]).timestamp(), pair[0]))
    selected = ranked if last is None else ranked[:last]
    selected_rows = [row for _, rows in selected for row in rows]
    unranked_rows = [row for _, rows in unranked for row in rows]
    selected_usage, bad_selected = usage_totals(selected_rows)
    unranked_usage, bad_unranked = usage_totals(unranked_rows)
    origins = Counter(row.get("message_origin") or "unknown" for row in selected_rows
                      if row["record_type"] == "message" and row.get("role") == "user")
    return {
        "coverage": coverage(diagnostics),
        "selection": {"order": "parsed non-injected message time, descending; ID breaks ties",
                      "requested_tasks": last, "selected_tasks": len(selected),
                      "shortfall": max(0, last - len(selected)) if last is not None else 0,
                      "excluded_records": excluded_records},
        "selected": [manifest(key, rows) for key, rows in selected],
        "unranked": [manifest(key, rows) for key, rows in sorted(unranked)],
        "unranked_reason": "No orderable message time, or delegated work without known parent lineage.",
        "sessions_without_orderable_messages": sum(
            item["last_interaction_at"] is None
            for key, rows in retained.items() for item in manifest(key, rows)["sessions"]),
        "selected_user_message_origins": dict(sorted(origins.items())),
        "selected_usage_by_agent_model": selected_usage,
        "unranked_usage_by_agent_model": unranked_usage,
        "invalid_usage_fields": bad_selected + bad_unranked,
    }


def read_records(path):
    records, invalid = [], []
    with path.open() as source:
        for line_number, line in enumerate(source, 1):
            try:
                row = json.loads(line)
                if (not isinstance(row, dict) or row.get("record_type") not in {"message", "usage"}
                        or any(not isinstance(row.get(key), str) for key in ("agent", "machine", "session_path"))
                        or (row.get("usage") is not None and not isinstance(row["usage"], dict))):
                    raise ValueError("not normalized history")
                records.append(row)
            except (ValueError, TypeError):
                invalid.append(line_number)
    return records, invalid


def positive(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def main():
    cli = argparse.ArgumentParser(description=__doc__, epilog=(
        "Use collector time bounds first; this command does not infer repository or human provenance. "
        "Session filters accept a thread ID or exact agent:machine:session_path (also printed in the manifest). "
        "Excluding a root removes known descendants; excluding a child removes that session only. "
        "Unranked usage stays separate under --last. Vendor token fields are separate and may contain subsets. "
        "Without diagnostics and the collector summary line, collection coverage is unknown. "
        "Exit 1 means partial collection/input or invalid usage fields; the JSON retains usable results."))
    cli.add_argument("history", type=Path)
    cli.add_argument("--diagnostics", type=Path)
    cli.add_argument("--last", type=positive)
    cli.add_argument("--include-session", action="append", default=[])
    cli.add_argument("--exclude-session", action="append", default=[])
    args = cli.parse_args()
    try:
        records, invalid = read_records(args.history)
        result = summarize(records, last=args.last, include=set(args.include_session),
                           exclude=set(args.exclude_session),
                           diagnostics=args.diagnostics.read_text() if args.diagnostics else None)
        result["input"] = {"valid_records": len(records), "invalid_record_lines": invalid}
        if invalid:
            result["coverage"]["status"] = "partial"
        print(json.dumps(result, ensure_ascii=False))
        return int(result["coverage"]["status"] == "partial" or bool(result["invalid_usage_fields"]))
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        print("error: unreadable or invalid normalized history/diagnostics; no data changed", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
