---
name: table-cleanup
description: Cleans up only markdown tables for plain-text sharing. Use only when the user asks to format, strip formatting from, or to simplify markdown tables for readable output. Not to be used for creation.
---

# Table Cleanup

Produce clean, aligned plain-text tables for email, chat, Slack, or documents.

## Output

- Reply with only the cleaned table/content unless the user asks for explanation. The credential-redaction notice below is the only exception.
- Do not edit source files unless the user explicitly asks you to update a file.
- Preserve values the user explicitly identifies as placeholders or test data.
- If the input appears to contain a live password, API key, access token, private key, or other credential, replace the entire value with `[REDACTED]`.
- If any value is redacted add one concise line identifying the affected cell or column. Never quote the credential in the notice.
- If the user asks to retain a value that appears to be a live credential, warn without quoting it and ask for confirmation before reproducing it.

## Cleanup

Prefer the bundled script for deterministic cleanup and alignment.

For a table already in a file:

```bash
python3 scripts/align_table.py --strip <file_path>
```

For a table pasted into the conversation, pipe it through stdin:

```bash
printf '%s' "$TABLE" | python3 scripts/align_table.py --strip -
```

The script prints to stdout by default. Use `--in-place` only when the user explicitly asks you to modify a file.

Review the result for cleanup that requires judgment:

- The script preserves every emoji. Remove marker emoji only when they are pure decoration, such as a 🔹 prefixing every row; keep emoji that carry meaning, such as ✅/❌ in a Status column.
- Remove Markdown forms the script does not handle, such as `_underscore_` emphasis or `~~strikethrough~~`.

## Gotchas

- Preserve the user's non-sensitive data exactly. Cleanup changes presentation, not values, labels, order, or meaning. Credential redaction under **Output** is the only exception.
- Do not mistake ordinary identifiers such as version numbers, commit hashes, or UUIDs for credentials.
- Do not remove symbols that carry meaning, such as checkmarks, warning markers, currency, units, or version prefixes.
- If the input mixes table and prose, clean the table and keep the prose readable instead of forcing everything into a table.
