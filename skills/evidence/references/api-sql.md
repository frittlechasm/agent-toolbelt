# API and SQL checks

- Run API requests and SQL queries in a terminal. A recording of that terminal is enough; prefer computer use when available.
- Follow [video.md](video.md) for pace and framing.
- Choose the environment, tenant, actor, and target records explicitly; do not default to a personal or production host.
- Load curl credentials from a protected header or config file (`-H @file` or `-K file`). Disable shell tracing and verbose HTTP output.
- Show the request or query, timestamp, status, and relevant output, including errors. Filter sensitive output before it reaches the recorded terminal.
- Check the expected result and stored state. HTTP 200 or exit 0 alone is not a pass; an expected 4xx denial may pass.
- Use database-enforced read-only access for SQL checks; keep setup writes separate.
  Show before/after values and check data that should stay unchanged.
- After a timeout, read the affected record before retrying a write; the first attempt may have succeeded.
- State whether you checked the schema or ran the application, and whether the database was fresh or upgraded with existing data.
