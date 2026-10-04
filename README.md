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
| `declutter` | Reviews code for simplification and performance improvements. |
| `eli5` | Creates illustrated HTML explanations for beginners. |
| `erd-diagram` | Creates source-grounded interactive database ERDs. |
| `flow-diagram` | Creates process flows with optional animation of all supported scenarios. |
| `html-document` | Creates standalone HTML documents. |
| `sync-upstream` | Syncs all branches in a fork with upstream. |
| `table-cleanup` | Converts Markdown tables into aligned plain text. |
| `ui-mocks` | Creates HTML UI mockups, stacked vertically by default. |
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

Edit public skills in `skills/<name>/` and private skills in the separate `skills/private/` Git repository. Check the owning Git root before staging. Global agent instructions belong to dotfiles.

## Scripts

| Command | What it does |
| --- | --- |
| `./scripts/check` | Validates skills and evals, then runs Python unit tests. |
| `./scripts/eval triggers [skill ...]` | Prepares trigger evals for the calling agent. |
| `./scripts/eval workflows [skill ...]` | Prepares workflow evals and isolated workspaces. |
| `./scripts/sync-skills check [--host <host>]` | Reports missing skills, changed remote content, and incorrect installation links. |
| `./scripts/sync-skills apply [--host <host>]` | Installs skills for the selected machine. |
| `./scripts/sync-skills check --target chatgpt` | Checks whether local ChatGPT upload ZIPs match the selected skills. |
| `./scripts/sync-skills apply --target chatgpt` | Creates or updates one upload ZIP per selected ChatGPT skill. |

`./scripts/check` validates public and private skills without requiring PyYAML.

`scripts/eval` prints a JSON manifest and does not invoke a model. The calling agent runs each subject, checks the result, and removes workflow workspaces.
It must record the model, reasoning effort, and available capabilities declared by the manifest.

`sync-skills` selects skills by `agents` and `machines` metadata.
A folder without its own `SKILL.md` groups related skills one level deep; grouped skills keep their own names when installed or exported.
Local installs link to this checkout; SSH installs copy skills with `rsync` (required on both machines) and preserve machine-local `.env` and `.env.local` files.
Source edits do not refresh remote copies; run `check` for the target host before and after `apply`.

For ChatGPT, export one ZIP per skill,
then upload each one under **Skills** → **New Skill** → **Upload from your computer** ([guide][chatgpt-upload]):

```bash
./scripts/sync-skills apply --target chatgpt   # writes Git-ignored .chatgpt/skills/; --output-dir overrides
```

- Export uses the same `machines` filter as local installs and includes skills whose `agents` is `all` or includes `chatgpt`.
- Skills whose `agents` is only `chatgpt` are export-only; local and SSH installs skip them.
- ZIPs leave out `.env` files (except `.env.example`), caches, and Git internals. Skills containing symlinks are rejected.
- The script only builds ZIPs. It never uploads them or checks what ChatGPT has installed.
- Skills that need local scripts or credentials will not work in ChatGPT without them.

[chatgpt-upload]: https://developers.openai.com/cookbook/examples/chatgpt/chatgpt_prompt_guide/chatgpt_prompt_guide
