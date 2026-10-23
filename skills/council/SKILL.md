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

- Launch one Opus and one Sol delegate, both at `xhigh` effort, whatever model is coordinating.
- In T3 Code, resolve models with `orchestrator_capabilities` and launch with `delegate_task`. Set `target.options` to
  `{"effort":"xhigh"}` for Opus and `{"reasoningEffort":"xhigh"}` for Sol, then check the returned provider, model, and options.
- If a model or effort setting is unavailable, report it; never substitute silently.

## Review and debate

1. State the models, effort, and scope, then launch both reviews in parallel (`delegate_task` with `mode: "async"`).
    - Delegates are read-only: no file writes (including temporary snapshots or generated tests) and no further delegation.
      They keep verification data in memory.
    - Give both the same request, constraints, target, context, and checks run.
      For code, include the [audit](../audit/SKILL.md) criteria; otherwise derive criteria from the task.
    - For code, share staged, unstaged, and untracked work through the read-only checkout or a full snapshot.
      A worktree from the parent commit misses uncommitted edits.
    - Ask for findings with reasoning, evidence, impact, locations, and a verdict.
      Separate demonstrated problems from assumptions, risks, and preferences.
    - Keep the material unchanged, and share neither review until both finish.
2. Verify each finding against the evidence.
    - Send conflicting findings to both reviewers and ask them to address the opposing evidence. Challenge unsupported claims and scope creep.
    - Accept supported findings, drop disproven ones, and keep unresolved objections. Do not force agreement.
3. For follow-up rounds, send the original brief, current material, prior findings, responses, and check results.
    - In T3 Code, call `delegate_task` again for each round with a distinct, retry-stable `clientRequestId`, and keep the task IDs.
    - Stop when findings are resolved, disagreement stalls, or work is blocked.

## Result

Report both models and effort, scope, rounds, verified findings, each reviewer's verdict, unresolved objections, checks run,
and any next steps the task asked for.
