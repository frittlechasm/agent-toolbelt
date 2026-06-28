# Security Controls Checklist

Read this only when the architecture report includes security posture, audit/client readiness, or explicitly requested security coverage. This is not a standalone vulnerability scan; it is a source-backed inventory of controls and gaps.

Assess evidence for:

- authentication and session handling
- authorization and role/permission checks
- tenant/account isolation
- secrets and config handling
- input validation and output encoding
- CSRF/CORS and browser security controls
- audit logging and observability
- rate limits, abuse controls, and replay protections
- dependency, build, and deployment hardening
- sensitive data storage, logging, and export
- tests covering security-sensitive paths

For each area, report only what the source supports:

- `Source-backed`: concrete controls in code, config, tests, or deployment files
- `Inferred`: likely behavior from structure or naming, with uncertainty stated
- `Unclear`: source is missing or ambiguous
- `Gap`: missing or inconsistent control with a reason it matters

Do not claim the system is secure. Say which controls exist, which were not found, and what evidence supports that conclusion.
