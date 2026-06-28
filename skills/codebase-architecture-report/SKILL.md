---
name: codebase-architecture-report
description: Generate source-aware architecture reports for existing codebases — system structure, key flows, design decisions, security controls, and gaps, with every claim tagged by an evidence label (source-backed, inferred, unclear, gap). Use this whenever the user wants to understand, explain, document, or report on how a codebase works — architecture overviews, onboarding docs, client- or audit-facing implementation write-ups, "map the auth/billing/sync flows", "document our architecture decisions", "how does this repo work and what are the risks", or a source-aware HTML architecture report. Triggers even when the user never says "architecture" — any request to map a system's moving parts, trace flows through real code, or surface decisions and gaps with file-level evidence. Use improve-codebase-architecture instead for finding refactoring opportunities, and a dedicated security scan/review workflow for a standalone security audit with no architecture report.
---

# Codebase Architecture Report

Gather source-backed evidence from a codebase and produce an architecture report that explains how the system works, what decisions shaped it, what controls exist, and where the gaps are.

## Boundaries and dependencies

- This skill owns **content and evidence**: what was read, what was found, what is claimed, what is gap, what is recommendation.
- It does **not** own presentation. For HTML output, delegate to [`html-document`](../html-document/SKILL.md) with the report content, evidence, diagrams to include, and document type `ARCHITECTURE REPORT · <project>`.
- Use `improve-codebase-architecture` instead when the primary task is to find refactoring opportunities or propose deeper modules.
- Use the relevant security scan/review workflow instead when the user asks for a standalone security review without needing an architecture report.

## Principles

- Separate **source-backed facts** from **inferences**, **unclear areas**, and **gaps**.
- Prefer repo-local evidence over generic architecture assumptions.
- Keep scope explicit. For large repos, produce a high-level map first, then deep-dive selected flows.
- Do not claim a system is secure; identify concrete controls and residual gaps.
- Cite files for important claims using file path and line number when possible.
- Do not invent components, controls, integrations, or diagrams not present in the source.

## Evidence Labels

Tag claims throughout the report:

- `Source-backed` — directly supported by code, docs, config, tests, or deployment files.
- `Inferred` — likely based on source structure, naming, or usage, but not explicitly documented.
- `Unclear` — needs human confirmation or missing source context.
- `Gap` — missing, inconsistent, risky, or under-documented based on evidence.

## Workflow

### 1. Scope

Identify:

- repo path
- audience: internal, onboarding, client, audit, proposal, or engineering review
- output format: Markdown or HTML
- focus: whole system, subsystem, security posture, architecture decisions, or selected flows

If any of these are missing and materially affect the report, collect them with `request_user_input` or the environment's equivalent user-input tool when available; otherwise make a reasonable default explicit and proceed.

For large repos, say what will be covered and what will only be sampled.

### 2. Discover Source Material

Read only what is needed for the scope. Start with:

- `README*`, `CONTEXT.md`, `AGENTS.md`
- `docs/`, `docs/adr/`, architecture/security/design docs
- package/build/framework config files
- route/API entrypoints
- database schemas and migrations
- auth, billing, sync, provisioning, webhook, import/export, job, and integration modules
- deployment files: Dockerfile, compose, Helm, Terraform, CI/CD, env examples
- relevant tests

Use fast file discovery and content search tools available in the environment, then read targeted files. Build an evidence index as you go — track every file you read and what you found in it.

### 3. Map Architecture

Identify (marking each as source-backed or inferred):

- system purpose
- runtime boundaries: frontend, backend, workers, CLIs, cron/jobs, queues
- major modules and ownership boundaries
- data stores and schema shape
- external integrations and APIs
- deployment topology
- cross-cutting concerns: auth, audit, logging, config, error handling

### 4. Trace Key Flows

Trace real flows from source, not generic ones. Good candidates:

- authentication and authorization
- tenant/account selection
- provisioning or SCIM sync
- billing, seat, pricing, and usage calculation
- CSV/import/export
- webhook handling
- background jobs
- document/report generation
- deployment/build pipeline

For each flow, capture: trigger, entrypoints, main modules, data writes/reads, external calls, failure paths, and tests.

### 5. Capture Decisions

Prefer explicit ADRs and docs. If decisions are inferred from code, label them `Inferred`.

For each decision:

- decision summary
- evidence (files, commits, docs)
- tradeoff or consequence
- related gaps if any

### 6. Review Security Controls (when scope includes security)

Skip this step if the user asked for a pure architecture overview. Include it when the audience is audit, client, or security-oriented, or when the user explicitly requests security coverage.

When included, read `references/security-controls.md` for the checklist. Keep the architecture-report posture: identify source-backed controls and residual gaps; do not run a standalone vulnerability scan unless the user asks for one.

### 7. Validate Claims

Before assembling the report:

- re-check high-impact facts against source files
- downgrade unsupported claims to `Inferred` or `Unclear`
- ensure gaps include evidence or a clear reason why the absence matters
- ensure the evidence index has enough file references for a reviewer to audit the report

## Report Content

The report should contain these sections. Omit sections that have no relevant content for the scope.

### Executive Summary

2-3 sentences on what the system does, key architectural characteristics, and the most important findings. This should stand alone — a reader who only reads this paragraph should get the essential picture.

### System Purpose

What the system does, who uses it, and what problem it solves. Source-backed from README, docs, or code.

### Architecture Map

Runtime boundaries, major modules, data stores, and how they connect. This section should include a diagram — an architecture map showing the system's moving parts and their relationships.

### Major Modules

For each significant module or subsystem: purpose, interface surface, key files, and what it depends on. Flag modules that are tightly coupled or have unclear boundaries.

### Data Model and Storage

Database tables/collections, key schemas, migration state, and how data flows between stores. Include the storage technology and any caching layers.

### External Integrations

Third-party services, APIs, webhooks, and OAuth providers. For each: what it does, how it connects, and which modules own the integration.

### Key Flows

Each traced flow gets its own subsection with: trigger, step-by-step path through the code, data reads/writes, external calls, failure handling, and test coverage. Flows should have diagrams showing the request/data path.

### Architecture Decisions

Each decision as a card-like block: summary, evidence, tradeoff, and related gaps. Prefer ADRs when they exist; label inferred decisions clearly.

### Security Controls (when in scope)

Source-backed controls and residual gaps organized by category. Do not claim the system is secure — list what exists and what is missing.

### Gaps and Risks

Separate from unclear areas. Each gap should include: what is missing, why it matters, evidence for the absence, and suggested severity.

### Recommendations

Narrow, actionable items tied to specific gaps or risks. Each recommendation should reference the gap it addresses.

### Evidence Index

A list of all files read during the investigation, grouped by area (docs, config, auth, billing, deployment, tests, etc.). This is the provenance trail that lets a reviewer verify the report.

## Output Formats

**Markdown**: clean heading hierarchy, fenced code blocks for file references, and tables for structured data (decisions, controls, gaps). The document should read well in any Markdown renderer.

**HTML**: invoke `html-document` for presentation. Pass it the report content and document type (`ARCHITECTURE REPORT · <project>`). Use its *Architecture report* scaffold; do not redefine presentation patterns here.

## Large Codebases

For large repos:

- inventory first; do not read every file
- select 2-5 key flows unless the user requests full coverage
- create a subsystem map and mark uninspected areas
- validate high-impact claims with direct source reads
- label broad claims as `Inferred` unless backed by docs/code

## Gotchas

- Do not fill gaps with generic architecture knowledge. If the repo does not show a component, integration, or control, label it `Unclear` or `Gap`.
- File names can imply intent, but source-backed claims need code, docs, config, tests, or deployment evidence.
- Keep recommendations tied to observed gaps. Broad best-practice advice belongs only when it addresses something found in this repo.
