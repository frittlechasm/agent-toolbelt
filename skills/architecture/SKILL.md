---
name: architecture
description: Create source-grounded codebase architecture reports or explain its systems and flows. Use only for architecture documentation or onboarding.
metadata:
    scope: global
    agents: all
    machines: all
---

# Codebase Architecture Report

Explain the system's purpose, major parts, runtime flows, and boundaries using repository evidence.

## Goal

- Begin with a practical system mental model and the conclusions that matter most, then add detail progressively.
- Define unfamiliar project or platform terms once, near first use, and keep terminology stable afterward.
- Use real module and symbol names. Include code or configuration examples only when they clarify an important mechanism or boundary.
- Keep the explanation as small as the audience and scope permit without losing important boundaries or caveats.

## Scope the report

- Determine the repository, audience, output format, focus, and desired depth from the request and available context.
- Ask only when a missing choice would materially change the report; otherwise state a reasonable assumption and proceed.
- For a large repository, begin with a high-level map and sample important flows. State what was covered, sampled, or left uninspected.
- When the user explicitly requests architecture-improvement recommendations, follow any direction they provide; absent such direction:
    - inspect roughly the last 20 commit messages
    - use recent churn only to prioritize which areas to examine more deeply

## Gather evidence

Start with repository guidance and architecture clues, then read only what the scope requires:

- README, project guidance, `CONTEXT.md` when present, architecture docs, and ADRs
- local setup, run, and test instructions when the report is for onboarding
- build, dependency, framework, and runtime configuration
- application entry points, routes, schemas, migrations, jobs, and integrations
- authentication, authorization, storage, messaging, and error-handling code when relevant
- deployment, infrastructure, CI/CD, and environment examples
- tests that confirm important behavior or boundaries

## Explain the architecture

Cover the parts that matter for the requested scope:

- system purpose and users
- the shortest verified path to run the system locally when the report is for onboarding
- runtime boundaries such as frontend, backend, workers, CLIs, scheduled jobs, and queues
- major modules, their responsibilities, interfaces, and dependencies
- data stores, schema shape, caches, and ownership of reads and writes
- external services, APIs, webhooks, and integration owners
- deployment topology and cross-cutting concerns such as configuration, logging, audit, and error handling

Trace important flows through their trigger, entry point, modules, data access, external calls, failure handling, and relevant tests.
Identify unverified steps instead of inventing behavior.

### Diagrams

- Use diagrams only when they clarify relationships or sequence; one system diagram may be enough.
- When the requested deliverable includes a system architecture map, use the `topology` skill when available.
- When an ERD is requested or database relationships are materially clearer visually, use the `erd` skill when available.
  - Include its ERD in the HTML report.
- Every node and connection must be supported by the source or explicitly marked as inferred.
- Label a connection with a protocol or transport only when the source supports it. Otherwise, leave the label out or mark it as inferred.
- Show a component inside a deployment or infrastructure boundary only when configuration or documentation confirms it.

## Handle evidence honestly

Make the confidence of important claims clear in natural language or concise labels:

- **Source-backed** — directly supported by code, documentation, configuration, tests, or deployment files.
- **Inferred** — a likely interpretation of source structure or usage.
- **Unclear** — the available repository evidence cannot confirm it.
- **Gap** — something missing, inconsistent, risky, or under-documented for a stated reason.

Do not label every sentence mechanically. Cite important claims with file paths and line numbers when practical.
Distinguish configured state from observed runtime state; a replica count in a manifest does not prove how many replicas are running.
Before finalizing, recheck high-impact claims and downgrade anything the source does not support.

When the report concludes that a requested component or flow is absent, summarize the files, directories, or search scope checked so the absence is auditable.

## Decisions, security, and gaps

Prefer documented decisions. Distinguish current mechanism from historical intent when explaining why a design exists.
Inspect local git history and, when available, linked PRs, issues, ADRs, and long-form documentation.
Code shape alone does not prove why a design was chosen. Label inferred rationale and explain its evidence, tradeoff, and consequence.

Include security controls when the request, audience, or scope calls for them.
Read [references/security-controls.md](references/security-controls.md) for that review.
Describe concrete controls and residual gaps; never claim that the system is secure.
Do not turn an architecture report into a standalone vulnerability review unless requested.

Separate unclear areas from demonstrated gaps. Explain each important gap's evidence and impact, and suggest the smallest supported next step.
Leave out recommendations only when the user asks for findings without them.

## Assemble the report

Choose the smallest structure that communicates the findings, with a source-reference trail.
Include a standalone summary for full reports.
Omit irrelevant or unsupported sections.
For HTML, pass the finished report content and useful diagrams to the `html` skill when available; let it decide the presentation.
