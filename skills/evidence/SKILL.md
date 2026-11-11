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
- After the planned cases, list edge cases worth running and mark them as proposed.

## Capture

- For terminal, API, or SQL checks, read [api-sql.md](references/api-sql.md).
- For recordings, read [video.md](references/video.md).
- Read only the needed configuration values; do not dump configuration or container environments.
- Redact secrets and unrelated personal data before saving evidence; sanitizing a summary does not fix the source artifact.
- Link requests, results, and clips to a case and run. Use IDs from the final run and disclose changes made by earlier attempts.
- Keep originals and edited copies separate. Before cleanup, verify delivered copies by size or checksum.
- Keep one evidence folder per ticket, with a folder per case and a README. Build it during the run and end each report with its path.
- Do not change records or repeat writes for a better recording. Use fresh fixtures for a rerun.

## Report

- Match the current comment's columns, tone, and case IDs. Show observations to the user without publishing them.
- Keep the user's edited verdicts and notes instead of replacing them unless stated otherwise.
- Follow the existing status format; otherwise use PASS, FAIL, PARTIAL, NOT RUN, BLOCKED, or N/A.
- Missing tools do not automatically make a test case N/A. Flag disputed expected results as questions, not failures.
- For a new table, use the columns Case, Steps, Status, and Evidence. Do not add Expected, Setup, or Actual columns.
- State the environment and the untested layers once, above the table. Write "same as TC n" for repeated steps.
- After the status, add one short plain sentence only when a row did not pass.
  Name the cause: product defect, environment, test data, or outdated case.
- Evidence cells hold only the matching media: embedded where the tracker supports it, otherwise one link.
- Keep sanitized logs with the evidence. Video is optional for API-only cases.
- Claim coverage only for tested layers and database vendors; an API check does not prove UI behavior.
- Report every case unless the user asks for failures only.
- Count the files before posting: one clip per case, screenshots only where a clip cannot show results, and one archive for logs and captures.
- Use `jira` for Jira posts, attachments, and inline embeds.
  Provide the target issue, comment if editing, final text, and which files belong to each case.
