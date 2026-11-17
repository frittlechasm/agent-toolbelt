---
name: audit
description: Review code or changes for blast radius, correctness, performance, and security. Not for simplification-only or visual UI critique.
metadata:
    scope: global
    agents: claude, codex
    machines: all
---

# Audit

Review the requested code, diff, or PR, including affected code outside the diff. Edit only when asked.

## Check

- Blast radius: callers, contracts, schemas and migrations, config, other tenants, duplicate copies of the pattern, compatibility, rollback.
- New members: find every list, group, filter, and switch; compare sibling validations and guards.
- Migrations: compare database copies with each other and the newest similar migration.
- Comments and docs: check facts (lifetime, order, "always") against related code and the full change set, including later commits.
- Correctness: edge cases, error paths, concurrency, retry safety.
- Retries and scheduled work: what happens if an item never succeeds, and can it block the batch?
- Background work: check per-run assumptions with all deployed instances running together; compare sibling locks. Normal deployment is not a rare race.
- Callee failures: if logic relies on throws or returns, read the callee and check a test covers the real call, not just a mock.
- Reused keys: follow restore, reopen, and retry paths; check that saved state and affected callers agree.
- Dependencies: check behavior in the resolved version's source; ask what else each category includes.
- UI lifecycle: check cleanup in development or strict mode and when a parent remounts the component.
- New tests: would each fail if its named behavior were removed? Require an assertion unique to the intended outcome.
- Performance: N+1 queries, unbounded work, missing indexes, blocking hot paths, leaks.
- New or changed queries: map filters to indexes and check call frequency; verify index claims with a plan at realistic data size.

## Security

Use the current OWASP Top 10. Check at least:

- Authorization at endpoint and object level, mass assignment, and tenant isolation across data, caches, queues, and jobs.
- Injection: SQL, NoSQL, LDAP, command, template, XSS, headers, and logs.
- SSRF, open redirects, path traversal, and file uploads.
- Unsafe parsing or deserialization of untrusted data.
- Authentication: token and assertion validation, sessions, replay, brute force, enumeration, MFA bypass.
- Cryptography: randomness, algorithms, password hashing, constant-time comparison.
- Browser: CSRF, CORS, cookie flags.
- Secrets and sensitive data in code, logs, responses, and errors; leaked secrets need rotation.
- Error handling that leaks details or fails open.
- Audit logging of security-relevant events.
- Dependencies, build changes, and leftover debug or test code.
- Claimed mitigations actually work, and fixes do not reintroduce the issue.

## Report

- Rank confirmed findings by severity with file references, impact, and the smallest effective fix.
- Verify reachability and existing controls; separate confirmed defects, validation blockers, and hardening advice.
- State what you did not inspect and give a verdict.
