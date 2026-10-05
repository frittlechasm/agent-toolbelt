# agent-toolbelt

Reusable agent skills and supporting utilities.

## Skills

| Skill | What it does | Runtime |
| --- | --- | --- |
| `agent-history-audit` | Reviews Claude and Codex history for repeated problems and workflow improvements. | Local: history files, Python, optional SSH. |
| `architecture-diagram` | Creates source-grounded architecture maps with optional animation of all supported flows. | Shared: supplied evidence, HTML/SVG and browser tools. |
| `bitbucket-pr-fetch` | Fetches and reviews a Bitbucket Cloud PR without changing it. | Local: POSIX Python, Bitbucket `.env`, persistent review cache. |
| `code-change-explainer-html` | Creates an HTML explainer for code changes. | Shared: supplied diff/source, HTML tools. |
| `codebase-architecture-report` | Creates source-backed architecture reports. | Shared: repository sources and relevant history supplied or accessible. |
| `commit-msg` | Writes conventional commit messages from Git changes. | Local: actual Git working tree and staged index. |
| `declutter` | Reviews code for simplification and performance improvements. | Shared: source/callers/tests; project runtime for verified edits. |
| `eli5` | Creates illustrated HTML explanations for beginners. | Shared: HTML/SVG and browser tools. |
| `erd-diagram` | Creates source-grounded interactive database ERDs. | Shared: supplied schema, bundled Python renderer, browser tools. |
| `flow-diagram` | Creates process flows with optional animation of all supported scenarios. | Shared: supplied process, HTML/SVG and browser tools. |
| `html-document` | Creates standalone HTML documents. | Shared: HTML and browser tools; `erd-diagram` for database content. |
| `jira-issue-write` | Creates and updates Jira Cloud issues with a preview before each write. | Local: Python, Jira configuration and credentials, network access. |
| `sync-upstream` | Syncs all branches in a fork with upstream. | Local: Git checkout, authenticated `gh`, Git remote credentials. |
| `table-cleanup` | Converts Markdown tables into aligned plain text. | Shared: supplied table; optional standard-library Python helper. |
| `ui-mocks` | Creates HTML UI mockups, stacked vertically by default. | Shared: HTML/CSS and browser tools. |
| `visual-design-review` | Reviews rendered UI for visual quality and polish. | Shared: supplied screenshots; browser for URL review. |

### Runtime classification

**Shared** means suitable for ChatGPT cloud and local Claude Code/Codex when the listed capabilities are available.
**Local** means the current workflow depends on a configured execution environment or local state and is excluded from standalone ChatGPT uploads.
This classification covers the skills as written, not a rewritten connector version or a cloud agent connected to your computer.
It does not claim that the skills were executed or accepted by ChatGPT's upload scanner.

The routing metadata in each `SKILL.md` is the source of truth:

- `agents: all`: shared across local Claude Code, local Codex, and ChatGPT cloud exports.
- `agents: claude, codex`: local to both agents; retains the shared installation paths and is excluded from ChatGPT exports.
- `agents: claude` or `agents: codex`: installed only for that local agent.
- `agents: chatgpt`: ChatGPT export only.
- `machines`: installation/export selection by machine, not a replacement for runtime compatibility.

Evaluate required dependencies transitively. Supplied files, self-contained templates, and standard-library scripts can be portable.
Credentials, private services, machine-specific paths, installed CLIs, persistent local history, and required sibling skills need an available runtime.
Script presence alone is not a local-only criterion: [ChatGPT skills can include code and scripts][chatgpt-upload].
Browser verification remains required where the skill specifies it; generating HTML alone does not satisfy that requirement.
Upload dependent skills together when required, and connect the necessary tools before using them.

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

Edit public skills in `skills/<name>/` and private skills in the separate `skills/private/` Git repository.
Check the owning Git root before staging. Global agent instructions belong to dotfiles.

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
Local installs link to this checkout.
SSH installs copy skills with `rsync` (required on both machines) and preserve machine-local `.env` and `.env.local` files.
Source edits do not refresh remote copies; run `check` for the target host before and after `apply`.

For ChatGPT, export one ZIP per skill,
then upload each one under **Skills** → **Create** → **Upload from your computer** ([guide][chatgpt-upload]):

```bash
./scripts/sync-skills apply --target chatgpt   # writes Git-ignored .chatgpt/skills/; --output-dir overrides
```

- Export uses the same `machines` filter as local installs and includes skills whose `agents` is `all` or includes `chatgpt`.
- Skills whose `agents` is only `chatgpt` are export-only; local and SSH installs skip them.
- ZIPs leave out `.env` files (except `.env.example`), caches, and Git internals. Skills containing symlinks are rejected.
- The script only builds ZIPs. It never uploads them or checks what ChatGPT has installed.
- Export selection follows the runtime classification above. A ZIP does not provision credentials, tools, or an execution environment.
- Existing ZIPs for skills no longer selected are not removed. Use an empty `--output-dir` for a fresh upload set after changing metadata.

[chatgpt-upload]: https://help.openai.com/en/articles/20001066-skills-in-chatgpt
