---
name: retro
description: Audit Claude and Codex history for issues, navigation friction, stale docs, usage, instruction drift, and reusable workflows across machines.
metadata:
  scope: global
  agents: claude, codex
  machines: all
---

# Agent History Audit

Keep everything you audit read-only: code, checks, history, instructions, installed skills, and remote machines.

By default, audit both agents on the current machine over the last 30 days, following any requested scope or exclusions.
For "last N sessions" requests without dates, drop the 30-day filter.
Inventory instructions and installed skills only when recommending changes to them.

## Collect and summarize

Run the collector once, then use the summarizer for selection, coverage, and usage instead of recomputing them.
Keep audit files in a private temporary directory and remove it afterward:

```bash
audit_dir=$(mktemp -d)
chmod 700 "$audit_dir"
trap 'rm -rf "$audit_dir"' EXIT
python3 <skill-dir>/scripts/collect_history.py \
  --agent all --recent-days 30 --recent-only \
  > "$audit_dir/history.jsonl" 2> "$audit_dir/collection.log"
python3 <skill-dir>/scripts/summarize_history.py "$audit_dir/history.jsonl" \
  --diagnostics "$audit_dir/collection.log" --exclude-session <active-thread-id> \
  > "$audit_dir/summary.json"
```

- Collector: add `--ssh-host HOST` per remote and `--no-local` for remote-only audits; see `--help` for custom history roots.
- Use `--recent-only` for rolling windows and omit it for full-history or count-only requests.
  For calendar periods, pass inclusive `--since` and exclusive `--until` with a timezone; they override `--recent-only`.
- Summarizer: use `--last N` and see `--help` for session filters. Always exclude the active audit thread.
  For a repository audit, find its sessions from normalized content and pass them with `--include-session`; leave unclear ones unattributed.
- Use only collector-normalized history. Never parse, quote, expose, or link raw history, and check paraphrased evidence for leftover credentials.
- Report coverage and selection, including exclusions and shortfalls. Explain partial or unknown coverage from `collection.log`:
  affected counts are lower bounds, and excluded sources are not collection failures. Report parse diagnostics without raw snippets.
- Keep unranked usage separate from selected-task totals, and vendor cache and reasoning fields separate.
  Token totals are not comparable across vendors, and Claude subagent usage is not covered.

## Assess evidence

- Classify each issue as a model error, navigation or doc gap, user refinement, tool failure, or permission gate.
- A repeated pattern needs two independent user interactions. How often a prompt appears is not how often something failed.
- Check `message_origin`. Injected or tool-wrapper content is not evidence. Scheduled, reviewer, and delegated prompts are not human corrections,
  and unknown origin does not prove human feedback. Delegated work can support a finding; later human follow-ups are direct evidence.
- Ignore duplicate snapshots and forks, but keep independent runs even when their prompts match.
- History holds conversation text, not full tool traces or repository metadata.
  Do not infer search counts, failures, repository identity, or navigation delays from missing traces or timestamp gaps.
- For navigation or stale-doc findings, name the misleading or missing guidance and what it caused.
  Check it against current code in a known checkout and revision, and say whether it is fixed, still a gap, or unverified.
  Report unavailable repositories as validation gaps. One verified gap can justify a fix but is not a pattern.

## Recommend

- Recommend a new skill only for a repeated, stable workflow, with its trigger, boundary, inputs, verification, and non-goals.
  Compare installed skills across the machines in scope, separately from drafts, caches, and archives.
- Prefer existing skills, repository entry points, and enforcement. Keep facts that are easy to find in a repository out of global guidance.
- Before proposing a guard, check existing scripts, hooks, CI, and past failures, and leave judgment calls to the model.
  When practical, test it on synthetic failing and passing cases in a temporary workspace, never with private history or the audited repository.
  Otherwise mark it unvalidated.

## Report

- Prioritize recommendations with expected and observed behavior, classification, frequency, confidence, and evidence before and after known fixes.
- Cite machine, session basename, full event timestamp, and affected paths. Give the smallest edit, its owner, coverage gaps, and machine drift.
- Separate scan totals, usable evidence, and verified incidents; separate confirmed findings, weak signals, and deferred ideas.
- Build HTML reports with the `html` skill. Include an executive summary, what worked, recurring errors, failures by model,
  usage and waste by agent and model, collection gaps, and metric limits.
  Show unknown models, and flag repeated context, low cache reuse, correction churn, and unusually high output.
