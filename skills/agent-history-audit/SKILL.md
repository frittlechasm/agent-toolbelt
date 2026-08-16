---
name: agent-history-audit
description: Audit Claude and Codex session history. Use for recent regression reviews, full-history workflow mining, or comparisons across machines.
metadata:
  scope: global
  agents: all
  machines: all
disable-model-invocation: true
---

# Agent History Audit

Audit agent history without changing session files, global instructions, installed skills, or remote machines.
Find repeated model mistakes, recurring user corrections, and workflows that deserve better global instructions or reusable skills.

## Set the scope

- Use the last 30 days for repeated errors and regressions unless the user gives another window.
- Use full history to find repeated workflows that could become skills.
- Include each named machine. If remote access is unavailable, report that gap instead of treating the missing history as clean.
- Record the current global instruction files and installed skill inventories before making recommendations.

## Collect safely

Create a temporary directory with mode `0700` and remove it when the audit is complete.
Run the bundled collector once; it uses event timestamps, redacts common credential forms, marks likely injected messages, excludes Claude subagent logs, and fingerprints duplicate sessions.

```bash
audit_dir=$(mktemp -d)
chmod 700 "$audit_dir"
trap 'rm -rf "$audit_dir"' EXIT
python3 /absolute/path/to/agent-history-audit/scripts/collect_history.py --recent-days 14 --ssh-host mowork > "$audit_dir/history.jsonl"
```

Do not display raw history or unredacted command output. Inspect only the fields needed for the audit.
If the collector cannot parse a history format, report the affected files and inspect a small redacted sample before changing it.

## Review recent history

Look for a pattern in at least two independent user interactions before calling it repeated. For every candidate:

1. State the expected behavior and what happened instead.
2. Classify it as a model error, user refinement, external/tool failure, or policy/permission gate.
3. Check whether a later instruction or skill update already fixed it. Split evidence before and after that date.
4. Cite the machine, session basename, and event timestamp. Do not cite only a filename date.
5. Prefer direct user corrections and observable failed outcomes over inferred dissatisfaction.

Do not count injected task notifications, local-command caveats, tool wrappers, Claude `subagents/` records, or duplicated snapshot/fork sessions as independent evidence.
Treat sessions marked `delegated` as supporting evidence, not direct user feedback.

## Mine full history for skills

Look for workflows the user repeats, especially those with stable inputs, ordered steps, verification, and predictable output.
A new skill is justified when it would remove repeated prompting or prevent a demonstrated mistake.
A one-off task or a discoverable fact is not enough.

Before proposing a skill:

- compare it with current global instructions and installed skills on every audited machine
- prefer improving an existing skill when ownership is clear
- keep broad preferences in global instructions and task-specific procedures in skills
- name the trigger, boundary, required inputs, verification, and non-goals

## Report

Lead with a short prioritized list. For each recommendation include:

- evidence and frequency
- classification and confidence
- the smallest proposed change and its owner: Claude instructions, Codex instructions, an existing skill, or a new skill
- why the change is not already covered
- any machine drift that would prevent the fix from taking effect

Separate confirmed findings from weak signals. Include a deferred list so low-value ideas do not look approved.
