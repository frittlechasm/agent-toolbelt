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
    - For code, list rules the change must preserve; use relevant audit checks to ask one realistic failure question per rule before the final verdict.
    - For code, keep the same base and full scope each round, including uncommitted work, so fixes do not hide earlier changes.
    - Name unchanged code the change depends on or supplies data to, including pages and consumers.
    - For test results, share the original screenshots, clips, and output.
    - Ask for a verdict and findings with IDs, severity, and evidence. Ask them to mark what is proven and what is a guess or preference.
    - For changes, ask them to flag code that the request or accepted findings do not need.
    - Do not change what they are reviewing, and do not share either review until both are done.
2. Check each finding against the evidence. Write down whether you accept or reject it, and why.
    - When reviewers disagree, send both findings to both reviewers and ask them to answer the other side's evidence.
    - Push back on claims without evidence. Turn down suggestions outside the scope and list them as follow-ups.
    - Verify reviewers' claims about behavior or missing requirements in code or at runtime before including them in tickets.
    - Keep open disagreements open. Do not force agreement.
3. Run another round when an important finding is still open, or when something changed after the last verdicts.
    - Resend the original brief, findings with IDs and status, check results, and changes; focus reviewers on open findings and changes.
    - Stop when the latest changes are reviewed and important findings settled, disagreement repeats without new evidence, or work is blocked.
    - A failed or missing review is not an approval.

## Result

Report models, effort, base, scope, rounds, stop reason, findings and status, each reviewer's verdict, open disagreements, and unapproved changes.
