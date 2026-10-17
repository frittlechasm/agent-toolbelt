---
name: agent-history-audit
description: Audit Claude and Codex history for recurring issues, usage, instruction changes, and reusable workflows across machines.
metadata:
  scope: global
  agents: claude, codex
  machines: all
---

# Agent History Audit

- Audit Claude and Codex history for repeated failures, corrections, and reusable workflows.
- Never modify history, global instructions, installed skills, or remote machines.

## Audit scope

- Default to both agents on the current machine over the last 30 days.
- Honor the requested agents, period, machines, history roots, and exclusions.
- Identify skill candidates within the requested window; do not widen a bounded audit to full history.
- Treat excluded sources as out of scope, not collection failures.
- Inventory global instructions and installed skills only when the user asks for instruction or skill recommendations.

## Collect history

- Run the collector once into a `0700` temporary directory, then remove the directory:

```bash
audit_dir=$(mktemp -d)
chmod 700 "$audit_dir"
trap 'rm -rf "$audit_dir"' EXIT
python3 /absolute/path/to/agent-history-audit/scripts/collect_history.py \
  --agent all --recent-days 30 --recent-only \
  > "$audit_dir/history.jsonl" 2> "$audit_dir/collection.log"
```

- Collect all requested machines in one run with `--ssh-host HOST`. Use `--no-local` for a remote-only audit.
- The collector applies best-effort credential redaction and labels message origin and injected content.
  - It omits Claude subagents, removes duplicates, fingerprints sessions, and normalizes usage.
- Use `--recent-only` for bounded audits. Omit it only when full history is required.
- For calendar periods, use inclusive `--since` and exclusive `--until` ISO-8601 timestamps with an explicit timezone.
  - Exact bounds take precedence over `--recent-only`.
- Run the collector even for supplied local roots and use its normalized output as the only history evidence.

## Check collection and privacy

- Never parse, link to, quote, or expose raw history.
- Read `collection.log` before analysis. Each requested local or remote root emits `collection_diagnostics`.
  - Check file counts, missing roots, read failures, and invalid-record counts and line numbers.
  - Inspect `complete`, not just the exit code. Partial collection retains valid records and can exit successfully.
  - Report gaps and treat affected counts as lower bounds.
- If parsing fails, report diagnostic paths and counts. Reproduce collector fixes with synthetic fixtures, not raw history snippets.
- Use minimal paraphrased evidence. Check excerpts for residual credentials; redaction does not guarantee safe output.
  - Keep normalized history and diagnostics inside the temporary directory.

## Count usage

- Count Claude usage once per message ID across session files.
- For Codex, prefer `token_usage_record` and deduplicate by thread and response ID.
  - Retain unmatched `token_count` records from legacy or mixed-format sessions.
  - Group delegated usage by `root_thread_id` when comparing task-level cost.
- Keep vendor-specific cache and reasoning fields separate; cross-vendor token totals are not equivalent.
- Count `record_type: usage` records independently of message/session fingerprints.
  - An empty-message fingerprint does not make usage a duplicate.

## Analyze findings

- A repeated pattern needs at least two independent user interactions. For each finding, report:
  - expected versus observed behavior
  - classification: model error, user refinement, external/tool failure, or policy/permission gate
  - machine, session basename, and full event timestamp rather than a date-only summary
  - evidence before and after any later instruction or skill fix

- Use normalized collector output as evidence and identify sessions by basename.
- Prefer direct corrections and observed failures.
- Ignore injected messages, command caveats, tool wrappers, Claude subagent records, and duplicate snapshots or forks.
- Use `message_origin` to separate injected, scheduled, reviewer, and delegated prompts from direct or unknown interaction.
  - Scheduled prompts and generated handoffs are not independent human corrections.
  - A later human follow-up in the same session can still be evidence.
- Treat delegated sessions as supporting evidence. Do not assume an unknown CLI origin is direct feedback, especially for reviewer prompts.
- Report prompt frequency separately from verified failures. Repetition alone does not prove failure.
- Exclude the active audit's own session from findings and record that exclusion.
  - Keep scan totals, usable evidence, supporting evidence, and verified incident counts distinct.

## Recommend improvements

- A skill candidate must be a repeated, stable workflow that would reduce prompting or prevent a demonstrated mistake.
- Prefer updating an existing skill. Keep broad preferences in global instructions.
- Record recurring preferences in the relevant global instructions, not workspace instructions.
- Reject one-offs and discoverable facts. Define the trigger, boundary, inputs, verification, and non-goals; compare these with every machine's inventory.
- Compare active instruction and skill contents, not just names. Separate installed skills from drafts, caches, archived copies, and trash.

## Report

- Lead with prioritized recommendations. For each, give:
  - Evidence, frequency, classification, and confidence.
  - The smallest change, owner, current coverage gap, and machine drift.
  - Owner: Claude instructions, Codex instructions, an existing skill, or a new skill.
- Separate confirmed findings from weak signals. Include a deferred list so low-value ideas do not look approved.
- HTML reports also need:
  - an executive summary
  - successful patterns
  - recurring errors
  - failure counts by model
  - token and inefficiency metrics by agent and model
  - collection gaps
  - metric limits
- Show unknown models and flag repeated context, low cache reuse, correction churn, and unusually high output.
