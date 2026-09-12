# agent-toolbelt

Reusable agent skills and supporting utilities.

## Skills

| Skill | What it does |
| --- | --- |
| `agent-history-audit` | Reviews Claude and Codex history for repeated problems and workflow improvements. |
| `architecture-diagram` | Creates source-grounded architecture maps with optional animation of all supported flows. |
| `bitbucket-pr-fetch` | Fetches and reviews a Bitbucket Cloud PR without changing it. |
| `code-change-explainer-html` | Creates an HTML explainer for code changes. |
| `codebase-architecture-report` | Creates source-backed architecture reports. |
| `commit-msg` | Writes conventional commit messages from Git changes. |
| `eli5` | Creates illustrated HTML explanations for beginners. |
| `erd-diagram` | Creates source-grounded interactive database ERDs. |
| `flow-diagram` | Creates process flows with optional animation of all supported scenarios. |
| `html-document` | Creates standalone HTML documents. |
| `sync-upstream` | Syncs all branches in a fork with upstream. |
| `table-cleanup` | Converts Markdown tables into aligned plain text. |
| `ui-mocks` | Creates side-by-side HTML UI mockups. |
| `visual-design-review` | Reviews rendered UI for visual quality and polish. |

## Install

Use `npx skills` for a one-off installation:

```bash
# List available skills
npx skills add frittlechasm/agent-toolbelt --list

# Install one skill
npx skills add frittlechasm/agent-toolbelt --skill <skill-name> -y

# Install every skill
npx skills add frittlechasm/agent-toolbelt --skill '*' -y
```

For a checkout you control, use `sync-skills` below.

## Scripts

| Command | What it does |
| --- | --- |
| `./scripts/check` | Validates skills and evals, then runs Python unit tests. |
| `./scripts/eval triggers [skill ...]` | Prepares trigger evals for the calling agent. |
| `./scripts/eval workflows [skill ...]` | Prepares workflow evals and isolated workspaces. |
| `./scripts/sync-skills check [--host <host>]` | Shows which skills would be installed. |
| `./scripts/sync-skills apply [--host <host>]` | Installs skills for the selected machine. |

`scripts/eval` prints a JSON manifest and does not invoke a model.
The calling agent runs each subject, checks the result, and removes workflow workspaces.
It must record the model, reasoning effort, and available capabilities declared by the manifest.

`sync-skills apply` follows each skill's `machines` metadata and preserves machine-local `.env` and `.env.local` files.
Remote operations require `rsync` on both machines.
