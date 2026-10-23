---
name: architecture
description: Create source-grounded codebase architecture reports or explain its systems and flows. Use only for architecture documentation or onboarding.
metadata:
    scope: global
    agents: claude, codex
    machines: all
---

# Codebase Architecture Report

Explain the system's purpose, major parts, runtime flows, and boundaries from repository evidence.

## Scope

- Infer the repository, audience, format, focus, and depth from the request. Ask only when a missing choice would change the report.
- For a large repository, map it at a high level and sample the important flows. Say what you covered, sampled, or skipped.
- For requested improvement recommendations without other direction, skim the last ~20 commit messages; use churn only to pick where to look deeper.

## Gather evidence

Start with the README, project guidance, `CONTEXT.md`, architecture docs, and ADRs. Then read only what the scope needs:
build and runtime config, entry points, routes, schemas, migrations, jobs, integrations, auth, storage, messaging, deployment, CI, and tests.
For onboarding, include setup, run, and test instructions.

## Explain

- Start with a practical mental model and the most important conclusions, then add detail.
- Use real module and symbol names. Define unfamiliar terms once, near first use, and keep terms stable.
- Cover what the scope needs: purpose and users, runtime boundaries, modules and their dependencies, data stores and who reads or writes them,
  external services, deployment, and cross-cutting concerns. For onboarding, include the shortest verified way to run it locally.
- Trace important flows from trigger through entry point, modules, data access, external calls, failure handling, and tests. Mark unverified steps.
- Use diagrams only when they clarify. Use the `topology` skill for system maps and the `erd` skill for database relationships.
  Every node, connection, protocol label, and deployment boundary must be source-backed or marked inferred.

## Evidence and confidence

- Make confidence clear without labeling every sentence: **source-backed**, **inferred**, **unclear**, or **gap**
  (missing, inconsistent, or risky, with a stated reason).
- Cite important claims with file paths and lines.
- Configured state is not observed runtime state; a replica count in a manifest does not prove how many replicas run.
- When you conclude something is absent, list where you searched.
- Recheck high-impact claims before finishing and downgrade anything the source does not support.

## Decisions, security, and gaps

- Prefer documented decisions from Git history, PRs, issues, and ADRs. Code shape alone does not prove why; label inferred rationale and its evidence.
- When the scope calls for security, use [references/security-controls.md](references/security-controls.md).
  Describe concrete controls and remaining gaps; never claim the system is secure. Run a vulnerability review only when asked.
- Separate unclear areas from demonstrated gaps. For each important gap, give evidence, impact, and the smallest next step,
  unless the user asked for findings only.

## Report

Use the smallest structure that works, with a source-reference trail and a standalone summary for full reports. Omit unsupported sections.
For HTML, hand the finished content and diagrams to the `html` skill.
