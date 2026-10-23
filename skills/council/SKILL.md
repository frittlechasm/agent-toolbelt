---
name: council
description: Review code, findings, approaches, or ideas with independent Opus and Sol delegates, then debate their conclusions. Use for council reviews.
metadata:
    scope: t3code
    agents: claude, codex
    machines: all
---

# Council

## Reviewers

- Launch two delegates: one Opus and one Sol, both at `xhigh` effort, regardless of the coordinating model.
- Resolve model aliases and supported options through the live catalog.
    - In T3 Code, use `orchestrator_capabilities` and `delegate_task`.
    - Set `target.options` explicitly: `{"effort":"xhigh"}` for Opus and `{"reasoningEffort":"xhigh"}` for Sol.
    - Check the returned provider, model, and options against the requested selection.
- Report unavailable models or unsupported effort settings rather than silently substituting.

## Review and Debate

1. State the models, effort, and scope, then launch both reviews in parallel.
    - Keep both delegates read-only and prohibit further delegation.
      Explicitly prohibit file writes, including temporary snapshots; keep verification data in memory and disable generated test files.
    - Give each the same original request, constraints, review target, supporting context, and checks run.
    - For code reviews, give both delegates the [audit](../audit/SKILL.md) skill's review criteria.
      For other material, derive review criteria from the task.
    - Do not share either delegate's initial review until both finish. Keep the reviewed material stable during those reviews.
    - For code reviews, include relevant staged, unstaged, and untracked work through the shared checkout read-only or a complete snapshot.
      A worktree based on the parent commit omits uncommitted edits.
    - Request findings or objections with reasoning, evidence, impact, relevant locations where applicable, and a verdict.
    - Distinguish demonstrated problems from assumptions, risks, and preferences, especially when reviewing approaches or ideas.

2. Verify each review's findings against available evidence and checks.
    - Argue disputed findings with the reviewer using concrete evidence; challenge unsupported claims and scope expansion.
    - Share conflicting findings after both independent reviews finish, and ask the reviewers to address the opposing evidence.
    - Accept supported findings, discard disproven ones, and preserve unresolved objections. Do not force agreement.

3. For follow-up discussion or re-review, supply the original brief, current material, prior findings, responses, and check results.
    - In T3 Code, call `delegate_task` again for each round; retain task IDs and use a distinct, retry-stable `clientRequestId` per task.
    - Stop discussion when the findings are resolved, disagreement stalls, or execution is blocked; report anything unresolved.

## Result

- Report both models and effort settings, scope, rounds, verified findings, and each reviewer's verdict.
- Include unresolved objections, checks run, and next steps required by the task prompt.
