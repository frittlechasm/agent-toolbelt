---
name: council
description: Review code, findings, approaches, or ideas with independent Opus and Sol delegates, then debate their conclusions. Use for council reviews.
metadata:
    scope: t3code
    agents: claude, codex
    machines: all
---

# Council

Only review. Never make fixes.

## Reviewers

- Start one Opus and one Sol reviewer at the same time with `delegate_task`, both at `xhigh` effort. Do this even if you are Opus or Sol.
- Check that each reviewer runs the right model and effort. If one is not available, say so. Do not swap in another.

## Review

1. Brief both reviewers.
    - Tell them not to change any files, including temporary files and new tests.
    - Give both the same brief and any check results. For code, include the [audit](../audit/SKILL.md) checklist.
    - For code, note the base commit and what you reviewed, including uncommitted work.
      Use the same base and scope every round, so later fixes do not hide earlier changes.
    - Ask for a verdict and findings with IDs, severity, and evidence. Ask them to mark what is proven and what is a guess or preference.
    - For changes, ask them to flag code that the request or accepted findings do not need.
    - Do not change what they are reviewing, and do not share either review until both are done.
2. Check each finding against the evidence. Write down whether you accept or reject it, and why.
    - When reviewers disagree, send both findings to both reviewers and ask them to answer the other side's evidence.
    - Push back on claims without evidence. Turn down suggestions outside the scope and list them as follow-ups.
    - Keep open disagreements open. Do not force agreement.
3. Run another round when an important finding is still open, or when something changed after the last verdicts.
    - Reviewers do not remember earlier rounds. Send the original brief, each finding with its ID and status, check results, and what changed.
      Ask them to focus on open findings and changes.
    - Stop when the latest changes are reviewed and important findings are settled, when the same disagreement repeats with no new evidence,
      or when you are blocked. A failed or missing review is not an approval.

## Result

Report both models and effort, the base and what was reviewed, the number of rounds and why you stopped, each finding and its status,
each reviewer's verdict, and open disagreements. Say which changes no reviewer has approved.
