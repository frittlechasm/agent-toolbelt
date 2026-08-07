---
name: codebase-architecture-report
description: Creates source-aware architecture reports explaining a codebase's structure, flows, design decisions, and security controls. Use only for architecture documentation and onboarding.
---

# Codebase Architecture Report

Create a clear architecture report that explains how a codebase works using evidence from the repository.

## Goal

- Use the simplest language that remains accurate for the intended audience.
- Explain the system's purpose, major parts, important runtime flows, and boundaries.
- Support important claims with source files. Clearly distinguish facts from inference or missing information.
- Focus on what helps the reader understand the system. Do not force sections, labels, tables, or diagrams that add no value.
- Do not invent components, integrations, controls, decisions, or failure behavior.

## Scope the report

- Determine the repository, audience, output format, focus, and desired depth from the request and available context.
- Ask only when a missing choice would materially change the report; otherwise state a reasonable assumption and proceed.
- For a large repository, begin with a high-level map and inspect a representative set of important flows. State what was covered, sampled, or left uninspected.
- When the user explicitly requests architecture-improvement recommendations, follow any direction they provide; absent such direction, inspect roughly the last 20 commit messages and use recent churn only to prioritize which areas to examine more deeply.

## Gather evidence

Start with repository guidance and architecture clues, then read only what the scope requires:
- README, project guidance, `CONTEXT.md` when present, architecture docs, and ADRs
- build, dependency, framework, and runtime configuration
- application entry points, routes, schemas, migrations, jobs, and integrations
- authentication, authorization, storage, messaging, and error-handling code when relevant
- deployment, infrastructure, CI/CD, and environment examples
- tests that confirm important behavior or boundaries

Use fast file discovery and targeted searches. Keep a working list of the files read and what each one supports.

## Explain the architecture

Cover the parts that matter for the requested scope:
- system purpose and users
- runtime boundaries such as frontend, backend, workers, CLIs, scheduled jobs, and queues
- major modules, their responsibilities, interfaces, and dependencies
- data stores, schema shape, caches, and ownership of reads and writes
- external services, APIs, webhooks, and integration owners
- deployment topology and cross-cutting concerns such as configuration, logging, audit, and error handling

Trace important flows from real source. When evidence exists, cover the trigger, entry point, main modules, data access, external calls, failure handling, and relevant tests.
If a step cannot be verified, say so.

### Diagrams
- Use a diagram only when relationships or sequence are materially clearer visually.
- Every node and connection must be supported by the source or explicitly marked as inferred.
- One system diagram may be enough; add flow diagrams only when they improve understanding.

## Handle evidence honestly

Make the confidence of important claims clear in natural language or concise labels:
- **Source-backed** — directly supported by code, documentation, configuration, tests, or deployment files.
- **Inferred** — a likely interpretation of source structure or usage.
- **Unclear** — the available repository evidence cannot confirm it.
- **Gap** — something missing, inconsistent, risky, or under-documented for a stated reason.

Do not label every sentence mechanically. Cite important source-backed claims with file paths and line numbers when practical.
Before finalizing, recheck high-impact claims and downgrade anything the source does not support.

When the report concludes that a requested component or flow is absent, summarize the files, directories, or search scope checked so the absence is auditable.

## Decisions, security, and gaps

Prefer documented architecture decisions. When a decision is inferred from code, say so and explain the evidence, tradeoff, and consequence without inventing intent.

Include security controls when the request, audience, or scope calls for them. Read [references/security-controls.md](references/security-controls.md) for that review. Describe concrete controls and residual gaps; never claim that the system is secure. Do not turn an architecture report into a standalone vulnerability review unless requested.

Separate unclear areas from demonstrated gaps. Explain why each gap matters and the evidence or absence behind it. Keep recommendations narrow, actionable, and tied to a specific observed gap.

## Assemble the report

Choose the smallest structure that communicates the findings. A complete report commonly includes:

- an executive summary that stands on its own
- system purpose and scope
- architecture map and major modules
- data and external integration boundaries
- selected key flows
- important architecture decisions
- security controls when in scope
- gaps, risks, and corresponding recommendations
- an evidence index or equivalent source-reference trail

Omit sections that are irrelevant or unsupported. Do not pad the report with generic architecture advice.

For Markdown, use a clean heading hierarchy and only the tables or code blocks that aid comparison. For HTML, pass the finished report content and useful diagrams to the `html-document` skill when available; let it decide the presentation.
