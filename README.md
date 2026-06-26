# agent-toolbelt

Skills and related utilities. 

## Install

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

## Skills

| Skill | What it helps with |
| --- | --- |
| `code-change-explainer-html` | Creates a standalone HTML walkthrough of a code change, explaining what changed line by line in terms of a language the reader already knows. |
| `codebase-architecture-report` | Maps an existing codebase into a source-aware architecture report with evidence labels, key flows, decisions, controls, and gaps. |
| `commit-msg` | Generates concise conventional commit messages from staged or unstaged git changes. |
| `html-document` | Creates polished standalone HTML documents for reports, explainers, proposals, plans, and other document-like outputs. |
| `sync-repos` | Mirrors tracked files from one local git repo to another while preserving the target repo's `deploy.yml`. |
| `sync-upstream` | Keeps a fork current with its upstream parent, rebases feature branches, and rebuilds `dev`. |
| `table-cleanup` | Strips markdown formatting from tables and aligns them for readable plain-text sharing. |
