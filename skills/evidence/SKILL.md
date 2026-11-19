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
- For UI cases, name the expected visible content, such as translated text, counts, or links.
- Give each visible variant a trigger: language, success or failure, read or unread, first or repeat visit. Use a `[Dev]` step if the UI cannot trigger it.
- Before testing, raise open QA questions with the user.
- Record the tested build, environment, database vendor, date, and roles once per run. A checkout does not identify the deployed build.
- Identify affected records and use disposable data within scope. Permission to test locally does not cover writes to shared environments.
- After the planned cases, list edge cases worth running and mark them as proposed.
- Before testing, check that records match the case and were made the way a user would make them. Fix any gaps.

## Capture

- For terminal, API, or SQL checks, read [api-sql.md](references/api-sql.md).
- For recordings, read [video.md](references/video.md).
- Read only the needed configuration values; do not dump configuration or container environments.
- Redact secrets and unrelated personal data before saving evidence; sanitizing a summary does not fix the source artifact.
- Link requests, results, and clips to a case and run. Use final-run IDs and note earlier attempts' changes in the README.
- Keep originals and edited copies separate. Before cleanup, verify delivered copies by size or checksum.
- Keep one evidence folder per ticket, with a folder per case and a README. Build it during the run and end each report with its path.
- Do not change records or repeat writes for a better recording. Use fresh fixtures for a rerun.
- After navigation, check that popups and menus close, one control on the new page works, and no new console errors appear.
- Run navigation cases once in a fresh session with network throttling to catch slow first loads.

## Report

- Match the current comment's columns, tone, and case IDs. Show observations to the user without publishing them.
- Keep the user's edited verdicts and notes instead of replacing them unless stated otherwise.
- Follow the existing status format; otherwise use PASS, FAIL, PARTIAL, NOT RUN, BLOCKED, or N/A.
- Missing tools do not automatically make a test case N/A. Flag disputed expected results as questions, not failures.
- For a new table, use the columns Case, Steps, Status, and Evidence. Do not add Expected, Setup, or Actual columns.
- Write only each case's result, what failed or is untested, and its evidence. No footer that repeats the table.
- State the environment and the untested layers once, above the table. Write "same as TC n" for repeated steps.
- Add one short sentence after the status only when a row did not pass or a limitation changes its result.
  Name a failure's cause (product defect, environment, test data, or outdated case) or the limitation.
- Never mark PARTIAL or FAIL as PASS, or hide missing coverage, to keep it short.
- Mark a case FAIL or PARTIAL if it exposes a defect, even one that predates the change.
- Raise a question about the defect before handoff. Correct any posted result that day.
- Before reporting, have a second agent check each expected result against the raw screenshots and clips. Leave out your summary.
- Keep run history, scheduling, restored settings, webhook totals and retries, email capture, and video review in the README, not the comment.
- Evidence cells hold only the matching media: embedded where the tracker supports it, otherwise one link.
- Keep sanitized logs with the evidence. Video is optional for API-only cases.
- Claim coverage only for tested layers and database vendors; an API check does not prove UI behavior.
- Report every case unless the user asks for failures only.
- Count the files before posting: one clip per case, screenshots only where a clip cannot show results, and one archive for logs and captures.
- Use `jira` for Jira posts, attachments, and inline embeds.
  Provide the target issue, comment if editing, final text, and which files belong to each case.
