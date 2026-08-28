# agent-toolbelt

Reusable agent skills and supporting utilities.

## Install

### From a checkout

Use the metadata-aware sync script when this repository should remain the source of record:

```bash
./scripts/sync-skills check
./scripts/sync-skills apply
./scripts/sync-skills check --host mowork
./scripts/sync-skills apply --host mowork
```

`check` is read-only. `apply` installs only skills whose `machines` metadata includes the target
machine and preserves machine-local files such as `.env` and `.env.local`. Remote operations require
`rsync` on both machines.

Use `--machine <name>` only when the SSH alias or local hostname does not match the skill metadata.

### With `npx skills`

```bash
# List available skills
npx skills add frittlechasm/agent-toolbelt --list

# Install one skill
npx skills add frittlechasm/agent-toolbelt --skill <skill-name> -y

# Install every skill
npx skills add frittlechasm/agent-toolbelt --skill '*' -y
```

## Check

```bash
./scripts/check
```

This validates skill metadata and eval definitions, then runs all Python unit tests. It does not run
model-dependent evals.

## Evals

Prepare trigger evals:

```bash
./scripts/eval triggers [skill-name ...]
```

Prepare workflow evals:

```bash
./scripts/eval workflows [skill-name ...]
./scripts/eval workflows commit-msg --case 1 --case 3
```

`scripts/eval` validates the definitions and prints a JSON manifest. It does not invoke a model or
judge. The calling agent gives each subject only its subject input, compares the result with the
supplied expectations, and removes workflow workspaces afterward.

Workflow fixtures are created only when a case needs controlled data or state. When a fixture
provides command shims, the calling agent must use the exact executable paths in the manifest.
