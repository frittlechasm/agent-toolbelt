---
name: agent-history-audit
description: Audit Claude and Codex session histories for usage, recurring failures, and reusable workflows across a requested period or machines.
metadata:
  scope: global
  agents: all
  machines: all
disable-model-invocation: true
---

# Agent History Audit

Audit Claude and Codex history for repeated failures, corrections, and reusable workflows.
Never modify history, global instructions, installed skills, or remote machines.

## Scope and collect

- Review the last 30 days for regressions unless the user specifies another window.
- Use full history to identify skill candidates.
- Match the requested agent, period, and machines. If unspecified, use both agents on the current machine and the last 30 days.
- If the user supplies history roots, machine limits, or exclusions, use exactly that scope.
- Treat excluded sources as out of scope, not collection failures.
- Inventory global instructions and installed skills only when the user asks for instruction or skill recommendations.

Run the collector once into a `0700` temporary directory, then remove the directory:

```bash
audit_dir=$(mktemp -d)
chmod 700 "$audit_dir"
trap 'rm -rf "$audit_dir"' EXIT
python3 /absolute/path/to/agent-history-audit/scripts/collect_history.py --agent all --recent-days 30 --recent-only > "$audit_dir/history.jsonl"
```

- The collector redacts credentials, marks injected messages, omits Claude subagents, fingerprints duplicates, and normalizes usage.
- Use `--recent-only` for bounded audits. Omit it only when full history is required.
- For calendar periods, use inclusive `--since` and exclusive `--until` ISO-8601 timestamps with an explicit timezone. Exact bounds take precedence over `--recent-only`.
- Run the collector even for supplied local roots and use its normalized output as the only history evidence.
- Never parse, link to, quote, or expose raw history.
- If parsing fails, report the files and inspect a minimal redacted sample before changing the collector.

Count Claude usage once per message ID across session files.
For Codex, prefer `token_usage_record`, deduplicate by thread and response ID, and retain unmatched `token_count` records from legacy or mixed-format sessions.
Group delegated Codex usage by `root_thread_id` when comparing task-level cost.
Keep vendor-specific cache and reasoning fields separate; cross-vendor token totals are not equivalent.

## Analyze

- A repeated pattern needs at least two independent user interactions. For each finding, report:
  - expected versus observed behavior
  - classification: model error, user refinement, external/tool failure, or policy/permission gate
  - machine, session basename, and full event timestamp rather than a date-only summary
  - evidence before and after any later instruction or skill fix

- Use normalized collector output as evidence and identify sessions by basename.
- Prefer direct corrections and observed failures.
- Ignore injected messages, command caveats, tool wrappers, Claude subagent records, and duplicate snapshots or forks.
- Delegated sessions are supporting evidence, not direct feedback.

- A skill candidate must be a repeated, stable workflow that would reduce prompting or prevent a demonstrated mistake.
- Prefer updating an existing skill. Keep broad preferences in global instructions.
- Record recurring preferences in the relevant global instructions, not workspace instructions.
- Reject one-offs and discoverable facts. Define the trigger, boundary, inputs, verification, and non-goals; compare these with every machine's inventory.

## Report

Lead with prioritized recommendations.
Give each recommendation's evidence, frequency, classification, confidence, smallest change, owner, current coverage gap, and machine drift.
Owners are Claude instructions, Codex instructions, an existing skill, or a new skill.

Separate confirmed findings from weak signals. Include a deferred list so low-value ideas do not look approved.

HTML reports also need:
  - an executive summary
  - successful patterns
  - recurring errors
  - failure counts by model
  - token and inefficiency metrics by agent and model
  - collection gaps
  - metric limits
Show unknown models and flag repeated context, low cache reuse, correction churn, and unusually high output.
