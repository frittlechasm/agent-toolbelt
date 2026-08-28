# agent-toolbelt

Skills and related utilities. 

## Install

For a checkout you control, prefer the metadata-aware sync script. It avoids stale copies made by `npx skills`:

```bash
./scripts/sync-skills check
./scripts/sync-skills apply
./scripts/sync-skills check --host mowork
./scripts/sync-skills apply --host mowork
```

`check` is read-only.
`apply` updates only skills whose `machines` metadata includes the target machine. It does not remove unrelated installed skills.
Commit and push source changes separately when Git should remain the source of record.
Remote checks and applies require `rsync` on both machines and stop before making changes when it is unavailable.

On the current machine, `apply` links the agent skill directories to this checkout.
For an SSH host, it copies selected skills and creates Claude links for shared skills.
Credential files such as `.env` and `.env.local` remain machine-local; committed `.env.example` files are synchronized.
Codex reads shared skills from `~/.agents/skills`; remove older same-named copies under `~/.codex/skills` separately.
Use `--machine <name>` only when the SSH alias or local hostname does not match the skill metadata.

For one-off installation without a checkout, use `npx skills`:

List the skills provided by this repository:

```bash
npx skills add frittlechasm/agent-toolbelt --list
```

Install every skill into the current project:

```bash
npx skills add frittlechasm/agent-toolbelt --skill '*' -y
```

To install one skill:

```bash
npx skills add frittlechasm/agent-toolbelt --skill <skill-name> -y
```

## Check

Run the repository's deterministic checks with:

```bash
./scripts/check
```

The command validates skill metadata and eval JSON, then discovers and runs every nested Python unit test.
Workflow and trigger evals require model execution, so the command reports those definitions without claiming to have run their behavior.

Run trigger-routing evals explicitly with an authenticated Codex CLI and a chosen model:

```bash
./scripts/eval-triggers --model <model> [skill-name ...]
```

The runner makes one isolated, read-only model call per skill and compares the structured classifications with `trigger-evals.json`.
It is intentionally separate from `./scripts/check` because model evals have latency and usage costs.

Run isolated workflow cases with separate subject and judge models when desired:

```bash
./scripts/eval-workflows --model <model> --judge-model <judge-model> <skill-name>
```

Workflow evals may declare a trusted `setup` command array whose first item is a Python script relative to the skill's `evals` directory.
The runner executes setup in a temporary workspace, runs the skill with write access only to that workspace, and grades the final response and resulting artifacts read-only.
When setup creates `.eval/bin`, the runner prepends it to the subject's `PATH` so fixtures can replace external commands without affecting the judge or the host machine.

## Skills

| Skill | What it helps with |
| --- | --- |
| `agent-history-audit` | Audits recent and full Claude and Codex history for repeated friction and evidence-backed instruction or skill improvements. |
| `code-change-explainer-html` | Creates a standalone HTML walkthrough of a code change, explaining what changed line by line in terms of a language the reader already knows. |
| `codebase-architecture-report` | Maps an existing codebase into a source-aware architecture report with evidence labels, key flows, decisions, controls, and gaps. |
| `commit-msg` | Generates concise conventional commit messages from staged or unstaged git changes. |
| `html-document` | Creates polished standalone HTML documents for reports, explainers, proposals, plans, and other document-like outputs. |
| `sync-upstream` | Keeps a fork current with its upstream parent, rebases feature branches, and rebuilds `dev`. |
| `table-cleanup` | Strips markdown formatting from tables and aligns them for readable plain-text sharing. |
| `ui-mocks` | Creates standalone HTML comparisons of distinct, fully styled UI mock variants. |
