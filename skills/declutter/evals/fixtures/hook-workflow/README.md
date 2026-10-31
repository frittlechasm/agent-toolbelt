# Forge tools

Skill source lives under `skills/`.
Run `scripts/evaluate.py` to prepare an evaluation workspace.

`hooks/pre-commit` runs secret scanning and repository checks.
`hooks/post-commit` synchronizes skill source to the local installation directory.
