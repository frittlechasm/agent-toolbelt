# agent-toolbelt

Reusable agent skills and supporting utilities.

## Skills

| Skill | What it does | Runtime |
| --- | --- | --- |
| `architecture` | Creates source-backed architecture reports. | Local |
| `audit` | Reviews changes for blast radius, correctness, performance, and security issues. | Local |
| `bitbucket` | Fetches and reviews a Bitbucket Cloud PR without changing it. | Local |
| `commit` | Writes conventional commit messages from Git changes. | Local |
| `council` | Reviews code, findings, approaches, or ideas through independent Opus and Sol reviews and debate. | Local |
| `critique` | Reviews rendered UI for visual quality and polish. | Shared |
| `declutter` | Reviews code and skills for simplification, performance improvements, and low-value or flaky tests. | Local |
| `eli5` | Creates illustrated HTML explanations for beginners. | Shared |
| `erd` | Creates source-grounded interactive database ERDs. | Shared |
| `evidence` | Prepares manual cases, records UI/API/SQL proof, and drafts concise test results. | Local |
| `flowchart` | Creates process flows with optional animation of all supported scenarios. | Shared |
| `html` | Creates standalone HTML documents. | Shared |
| `jira` | Searches, reads, creates, and updates Jira Cloud issues. | Local |
| `linkify` | Resolves and formats repository and Jira identifier links. | Local |
| `mockups` | Creates HTML UI mockups, stacked vertically by default. | Local |
| `retro` | Reviews Claude and Codex history for recurring problems, navigation friction, stale docs, and workflow improvements. | Local |
| `topology` | Creates source-grounded architecture maps with optional animation of all supported flows. | Shared |
| `upstream` | Syncs all branches in a fork with upstream. | Local |
| `walkthrough` | Creates an HTML explainer for code changes. | Local |

**Shared** skills support ChatGPT, Claude Code, and Codex when the required tools are available.
**Local** skills require local tools or state.

The `metadata` block in each `SKILL.md` controls where a skill goes:

- `agents: all`: Claude Code, Codex, and ChatGPT export.
- `agents: claude, codex`: both local agents.
- `agents: claude` or `agents: codex`: only that agent.
- `agents: chatgpt`: ChatGPT export only.
- `machines`: machine names allowed for installs or exports, or `all`.

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

For a maintained checkout, edit `skills/<name>/` and use `sync-skills` below.
Do not sync unfinished changes to remote hosts or ChatGPT ZIPs.

## Scripts

| Command | What it does |
| --- | --- |
| `./scripts/check` | Validates skills and evals, then runs Python unit tests. |
| `./scripts/eval triggers [skill ...]` | Prepares trigger evals for the calling agent. |
| `./scripts/eval workflows [skill ...]` | Prepares workflow evals and isolated workspaces. |
| `./scripts/sync-skills check [--host <host>] [--skill <name>]` | Reports missing, changed, mislinked, or stale installs. |
| `./scripts/sync-skills apply [--host <host>] [--skill <name>]` | Installs skills for the selected machine and removes stale installs. |

`scripts/eval` prepares cases but does not invoke a model. Follow its JSON manifest to run subjects, record results, and clean up workspaces.

A folder without its own `SKILL.md` groups related skills one level deep; grouped skills keep their own names when installed or exported.
Local installs link to this checkout; SSH installs use `rsync` (required on both machines) and preserve machine-local `.env` files.
Remote copies need syncing after source edits. Run `check` for the target host before `apply`; `apply` verifies the installs.

- Pruning removes installs of skills this checkout ships or once shipped at paths no longer selected by metadata.
  It preserves unknown entries and `npx skills` installs tracked in `~/.agents/.skill-lock.json`.
- Stale copies holding a machine-local `.env` file are reported as `KEPT`; remove them by hand.
- `--skill <name>` limits a run to the named skills and skips pruning.

### ChatGPT export

Export one ZIP per selected skill, then upload them using the [ChatGPT skill upload guide][chatgpt-upload]:

```bash
./scripts/sync-skills apply --target chatgpt   # writes Git-ignored .chatgpt/skills/; --output-dir overrides
```

- Use `check --target chatgpt` to compare local ZIPs with source. Neither command uploads or checks installed ChatGPT skills.
- ZIPs exclude `.env` and `.env.*` (except `.env.example`), caches, and Git internals. Symlinks are rejected.
- Unselected ZIPs are kept. Use an empty `--output-dir` for a fresh export after changing metadata.

[chatgpt-upload]: https://help.openai.com/en/articles/20001066-skills-in-chatgpt
