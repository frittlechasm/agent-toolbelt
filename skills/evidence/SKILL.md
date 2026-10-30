---
name: evidence
description: Plan and run UI/API/SQL checks, save evidence and recordings, and draft test-result comments. Not for code review.
metadata:
    scope: global
    agents: claude, codex
    machines: all
---

# Evidence

## Plan

- Read supplied criteria and relevant GitHub or Jira discussion. Base expected results on agreed rules; flag conflicts.
- Use `jira` for Jira and the `gh` CLI for GitHub.
- For each case, list the actor, preconditions, test data, steps, and expected result. Distinguish planned cases from executed cases.
- Record the tested build, environment, database vendor, date, and roles once per run. A checkout does not identify the deployed build.
- Identify affected records and use disposable data within scope. Permission to test locally does not cover writes to shared environments.

## Capture

- For terminal, API, or SQL checks, read [api-sql.md](references/api-sql.md).
- For recordings, read [video.md](references/video.md).
- Read only the needed configuration values; do not dump configuration or container environments.
- Redact secrets and unrelated personal data before saving evidence; sanitizing a summary does not fix the source artifact.
- Link requests, results, and clips to a case and run. Use IDs from the final run and disclose changes made by earlier attempts.
- Keep originals and edited copies separate. Before cleanup, verify delivered copies by size or checksum.
- Do not change records or repeat writes for a better recording. Use fresh fixtures for a rerun.

## Report

- Match the current comment's columns, tone, and case IDs. Show observations to the user without publishing them.
- Keep the user's edited verdicts and notes instead of replacing them unless stated otherwise.
- Follow the existing status format; otherwise use PASS, FAIL, PARTIAL, NOT RUN, BLOCKED, or N/A.
- Missing tools do not automatically make a test case N/A. Flag disputed expected results as questions, not failures.
- Briefly state what happened, which layer was checked, and what remains untested. Link the matching evidence.
- Keep sanitized logs with the evidence. Video is optional for API-only cases.
- Claim coverage only for tested layers and database vendors; an API check does not prove UI behavior.
- Report every case unless the user asks for failures only.
- Use `jira` for Jira posts, attachments, and inline embeds.
  Provide the target issue, comment if editing, final text, and which files belong to each case.
