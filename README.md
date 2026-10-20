# agent-toolbelt

Reusable agent skills and supporting utilities.

## Skills

| Skill | What it does | Runtime |
| --- | --- | --- |
| `architecture` | Creates source-backed architecture reports. | Shared |
| `bitbucket` | Fetches and reviews a Bitbucket Cloud PR without changing it. | Local |
| `commit` | Writes conventional commit messages from Git changes. | Local |
| `critique` | Reviews rendered UI for visual quality and polish. | Shared |
| `declutter` | Reviews code for simplification and performance improvements. | Shared |
| `eli5` | Creates illustrated HTML explanations for beginners. | Shared |
| `erd` | Creates source-grounded interactive database ERDs. | Shared |
| `flowchart` | Creates process flows with optional animation of all supported scenarios. | Shared |
| `html` | Creates standalone HTML documents. | Shared |
| `jira` | Searches, reads, creates, and updates Jira Cloud issues; every write previews first. | Local |
| `linkify` | Resolves and formats repository and Jira identifier links. | Shared |
| `mockups` | Creates HTML UI mockups, stacked vertically by default. | Shared |
| `retro` | Reviews Claude and Codex history for repeated problems and workflow improvements. | Local |
| `topology` | Creates source-grounded architecture maps with optional animation of all supported flows. | Shared |
| `upstream` | Syncs all branches in a fork with upstream. | Local |
| `walkthrough` | Creates an HTML explainer for code changes. | Shared |

**Shared** skills work in ChatGPT and in local Claude Code and Codex when their tools are available.
**Local** skills need local state and work only in Claude Code and Codex.

The `metadata` block in each `SKILL.md` controls where a skill goes:

- `agents: all`: Shared; installed for Claude Code and Codex and exported for ChatGPT.
- `agents: claude, codex`: Local to both agents.
- `agents: claude` or `agents: codex`: installed only for that agent.
- `agents: chatgpt`: ChatGPT export only.
- `machines`: the machine names that receive the skill, or `all`.

Mark a skill Local when it, or a skill it requires, needs credentials, private services, machine-specific paths, installed CLIs,
or local history. Bundled scripts alone do not make a skill Local; [ChatGPT skills can include scripts][chatgpt-upload].

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

Edit skills in `skills/<name>/`. `sync-skills` also picks up skills in a Git-ignored `skills/private/` folder.

## Scripts

| Command | What it does |
| --- | --- |
| `./scripts/check` | Validates skills and evals, then runs Python unit tests. |
| `./scripts/eval triggers [skill ...]` | Prepares trigger evals for the calling agent. |
| `./scripts/eval workflows [skill ...]` | Prepares workflow evals and isolated workspaces. |
| `./scripts/sync-skills check [--host <host>] [--skill <name>]` | Reports missing, changed, mislinked, or stale installs. |
| `./scripts/sync-skills apply [--host <host>] [--skill <name>]` | Installs skills for the selected machine and removes stale installs. |
| `./scripts/sync-skills check --target chatgpt` | Checks whether local ChatGPT upload ZIPs match the selected skills. |
| `./scripts/sync-skills apply --target chatgpt` | Creates or updates one upload ZIP per selected ChatGPT skill. |

`scripts/eval` prints a JSON manifest and does not invoke a model. The calling agent runs each subject, checks the result, and removes workflow workspaces.
It must record the model, reasoning effort, and available capabilities declared by the manifest.

`sync-skills` selects skills by `agents` and `machines` metadata.
A folder without its own `SKILL.md` groups related skills one level deep; grouped skills keep their own names when installed or exported.
Local installs link to this checkout.
SSH installs copy skills with `rsync` (required on both machines) and preserve machine-local `.env` files.
Source edits do not refresh remote copies; run `check` for the target host before and after `apply`.

- A stale install is a skill this checkout ships, or once shipped, at a path the metadata no longer selects.
- Pruning leaves `npx skills` installs (listed in `~/.agents/.skill-lock.json`) and unknown entries alone.
- Stale copies holding a machine-local `.env` file are reported as `KEPT`; remove them by hand.
- `--skill <name>` limits a run to the named skills and skips pruning.

For ChatGPT, export one ZIP per skill,
then upload each one under **Skills** → **Create** → **Upload from your computer** ([guide][chatgpt-upload]):

```bash
./scripts/sync-skills apply --target chatgpt   # writes Git-ignored .chatgpt/skills/; --output-dir overrides
```

- Export uses the same `machines` filter as local installs.
- ZIPs leave out `.env` files (except `.env.example`), caches, and Git internals. Skills containing symlinks are rejected.
- The script only builds ZIPs. It never uploads them or checks what ChatGPT has installed.
- Existing ZIPs for skills no longer selected are not removed. Use an empty `--output-dir` for a fresh upload set after changing metadata.

[chatgpt-upload]: https://help.openai.com/en/articles/20001066-skills-in-chatgpt
