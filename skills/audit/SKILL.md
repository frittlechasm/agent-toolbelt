---
name: audit
description: Review code or changes for blast radius, correctness, performance, and security. Not for simplification-only or visual UI critique.
metadata:
    scope: global
    agents: claude, codex
    machines: all
---

# Audit

Review the requested code, diff, or PR. Report findings; edit only when asked.

## Check

- Blast radius: callers, contracts, schemas and migrations, config, other tenants, duplicate copies of the pattern, compatibility, rollback.
- Correctness: edge cases, error paths, concurrency, retry safety.
- Performance: N+1 queries, unbounded work, missing indexes, blocking hot paths, leaks.

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
