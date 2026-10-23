---
name: retro
description: Audit Claude and Codex history for issues, navigation friction, stale docs, usage, instruction drift, and reusable workflows across machines.
metadata:
  scope: global
  agents: claude, codex
  machines: all
---

# Agent History Audit

Keep the audited environment read-only, including code, checks, history, instructions, installed skills, and remote machines.

Default to both agents on the current machine over the last 30 days; honor requested scope and exclusions.
For last-N requests without explicit time bounds, omit the default 30-day filter.
Inventory instructions and installed skills only for instruction or skill recommendations.

## Collect and summarize

Run the collector once, then use the consumer for selection, coverage, and usage; do not recreate these calculations.
Keep all audit files in the private temporary directory and remove it afterward:

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

- Adjust collector inputs to scope: `--ssh-host HOST` for each remote, `--no-local` for remote-only, and `--help` for supplied roots.
- Use `--recent-only` for rolling windows; omit it for full-history/count-only requests.
  Calendar periods use inclusive `--since` and exclusive `--until` timestamps with a timezone; these override `--recent-only`.
- Use consumer `--last N` and `--help` for session filters. Exclude the active audit thread.
  For repository audits, identify membership from normalized content and pass matching IDs with `--include-session`; leave ambiguity unattributed.
- Use only collector-normalized history. Never parse, quote, expose, or link raw history; check paraphrased evidence for residual credentials.
- Report summary coverage and selection, including exclusions and shortfalls. Explain partial/unknown coverage from `collection.log`;
  affected counts are lower bounds, and excluded sources are not collection failures. Report parsing diagnostics without raw snippets.
- Keep unranked usage separate from selected-task totals and vendor cache/reasoning fields separate.
  Cross-vendor token totals are not equivalent; Claude subagent usage is outside coverage.

## Assess evidence

- Distinguish model errors, navigation/documentation gaps, user refinements, tool failures, and permission gates.
  Repeated patterns require two independent user interactions; prompt frequency alone is not failure frequency.
- Use `message_origin`: injected/tool-wrapper content is not evidence; scheduled, reviewer, and delegated prompts are not human corrections.
  Unknown origin is not proof of human feedback. Delegated work can support findings; later human follow-ups can supply direct evidence.
  Ignore duplicate snapshots/forks, without discarding independent runs just because their prompts match.
- The collector retains conversation text, not full tool traces or repository metadata.
  Do not infer search counts, failures, repository identity, or navigation delay from missing traces or timestamp gaps.
- For navigation/stale-doc findings, identify the misleading or missing guidance and observed consequence.
  Check implicated files against current code in an identified checkout/revision; distinguish fixed history, current gaps, and unverified claims.
  Report unavailable repositories as validation gaps. One verified gap may justify repair, but is not a recurring pattern.

## Recommend improvements

- Recommend skills only for repeated, stable workflows; define trigger, boundary, inputs, verification, and non-goals.
  Compare active contents across scoped machines, distinguishing installed skills from drafts/caches/archives.
- Prefer existing skills, repository entry points, and enforcement. Keep discoverable repository facts out of global guidance.
  Check relevant scripts, hooks, CI, and prior failures before proposing a guard; leave judgment to the model.
- Validate proposed guards with synthetic failure and valid cases in an isolated temporary workspace, when practical.
  Never use private history or mutate the audited repository; otherwise mark the proposal unvalidated.

## Report

- Prioritize recommendations with expected/observed behavior, classification, frequency, confidence, and evidence before/after known fixes.
  Cite machine, session basename, full event timestamp, and affected paths; give the smallest edit, owner, coverage gap, and machine drift.
- Separate scan totals, usable/supporting evidence, and verified incidents; distinguish confirmed findings, weak signals, and deferred ideas.
- HTML reports include an executive summary, successful patterns, recurring errors, failures by model, usage/inefficiency by agent/model,
  collection gaps, and metric limits. Show unknown models; flag repeated context, low cache reuse, correction churn, and unusually high output.
