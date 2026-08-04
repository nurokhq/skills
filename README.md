# Nurok Skills

[![CI](https://github.com/nurokhq/skills/actions/workflows/ci.yml/badge.svg)](https://github.com/nurokhq/skills/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

Nurok Skills packages repeatable workflows for reading and managing Nurok knowledge bases. Skills follow the [Agent Skills](https://agentskills.io) format and are distributed through independently installable Codex and Claude Code plugins plus portable packages for Hermes, OpenClaw, Cursor, OpenCode, and other compatible agents.

## Plugins And Skills

| Plugin | Skill | Purpose |
| --- | --- | --- |
| `nurok-kb` | [`nurok-kb`](plugins/nurok-kb/skills/nurok-kb/) | Read, search, inspect, and synthesize KB evidence. |
| `nurok-kb-manage` | [`nurok-kb-manage`](plugins/nurok-kb-manage/skills/nurok-kb-manage/) | Design, create, validate, publish, update, and recover KBs. |

Install the read-only and management plugins independently so agents receive only the capabilities needed for a task.

## Install

### Direct Installation

Use a client's native installer when it supports this repository layout. These commands are client-specific and do not use the portable Skills CLI.

#### Codex

Add the Codex marketplace, then install either or both plugins:

```bash
codex plugin marketplace add nurokhq/skills --ref main
codex plugin add nurok-kb@nurok
codex plugin add nurok-kb-manage@nurok
```

Restart the Codex surface or start a new thread after installation.

#### Claude Code

Add the Claude Code marketplace, then install either or both plugins:

```bash
claude plugin marketplace add nurokhq/skills
claude plugin install nurok-kb@nurok
claude plugin install nurok-kb-manage@nurok
```

Claude Code follows the repository's default branch. Restart Claude Code or start a new session after installation.

#### Hermes

Hermes can install either canonical skill directory directly from GitHub:

```bash
hermes skills install nurokhq/skills/plugins/nurok-kb/skills/nurok-kb
hermes skills install nurokhq/skills/plugins/nurok-kb-manage/skills/nurok-kb-manage
```

These commands follow the repository's default branch and install into Hermes' managed skills directory. Use the Skills CLI method below when a branch or release tag must be explicit.

### Install with the Skills CLI

Use the open [Skills CLI](https://github.com/vercel-labs/skills) for one portable installation flow across Hermes, OpenClaw, Cursor, and OpenCode. This installs Agent Skills rather than Codex or Claude Code plugins.

Choose the target agent and scope:

| Client | `--agent` value | Recommended scope option | Expected target |
| --- | --- | --- | --- |
| Hermes | `hermes-agent` | `--global` | `~/.hermes/skills/` |
| OpenClaw | `openclaw` | None | `<project>/skills/` |
| Cursor | `cursor` | None | `<project>/.agents/skills/` |
| OpenCode | `opencode` | None | `<project>/.agents/skills/` |

The following examples target Cursor. Replace `cursor` with the required `--agent` value, and add `--global` for the recommended Hermes installation.

Use the simplified GitHub source to follow the repository's default branch:

```bash
npx skills add nurokhq/skills --skill nurok-kb --agent cursor --yes
npx skills add nurokhq/skills --skill nurok-kb-manage --agent cursor --yes
```

Use full GitHub `tree` URLs to pin a branch or release tag:

```bash
npx skills add https://github.com/nurokhq/skills/tree/main/plugins/nurok-kb/skills/nurok-kb --agent cursor --yes
npx skills add https://github.com/nurokhq/skills/tree/main/plugins/nurok-kb-manage/skills/nurok-kb-manage --agent cursor --yes
```

The Skills CLI does not have a `--ref` option. Replace `main` in the `tree` URLs with the required branch name or release tag when an exact revision is needed. Do not use the `owner/repo@ref` form for a Git ref because the `@` suffix can select a skill.

List the skills available from the repository before installation:

```bash
npx skills add nurokhq/skills --list
```

After installation, verify that the expected target contains the complete skill directory and its `SKILL.md`; current Skills CLI versions may include other detected clients in `skills list --agent` output. Start a new client session so it discovers the installed skills.

OpenClaw's native Git installer requires `SKILL.md` at the Git source root, which does not match this multi-plugin repository. Use the Skills CLI for OpenClaw unless the skills are published separately through ClawHub. Cursor provides a GitHub import UI but no equivalent native installation command, and OpenCode does not document a native skill installation command.

The plugin-local directories remain the canonical source. Do not commit generated client-specific copies.

## Upgrade

After a skill update is published to the branch or release you installed, upgrade it with the same installation method.

For Codex, refresh the marketplace snapshot and reinstall each installed plugin:

```bash
codex plugin marketplace upgrade nurok
codex plugin add nurok-kb@nurok
codex plugin add nurok-kb-manage@nurok
```

For Claude Code, update the marketplace and each installed plugin:

```bash
claude plugin marketplace update nurok
claude plugin update nurok-kb@nurok
claude plugin update nurok-kb-manage@nurok
```

For a native Hermes installation, check for and apply upstream changes:

```bash
hermes skills check
hermes skills update nurok-kb
hermes skills update nurok-kb-manage
```

For a portable Skills CLI installation, update the tracked skills in the current scope:

```bash
npx skills update nurok-kb nurok-kb-manage
```

Use `--global` or `--project` to select the original Skills CLI installation scope. Only run the commands for plugins or skills you installed, then restart the client or start a new session so it loads the updated instructions.

## Prerequisites

All skills require the Nurok CLI. The management skill requires Nurok CLI 0.2.0 or later and Python 3.9 or later for its supplemental audit:

```bash
curl -fsSL https://static.nurok.ai/cli/install.sh | bash
```

Public reads may work anonymously. Private reads and remote management require a Nurok login or `NUROK_API_KEY`. Local authoring and the audit script do not require remote credentials.

The `nurok-kb` plugin does not change remote state. The management plugin can publish, change source registries or visibility, and operate snapshots; its skill requires explicit authority plus endpoint, identity, visibility, and target confirmation before remote mutations.

## Repository Layout

- `plugins/nurok-kb/` contains the read-only plugin and its canonical skills.
- `plugins/nurok-kb-manage/` contains the lifecycle-management plugin and skill.
- `.agents/plugins/marketplace.json` publishes the Codex marketplace entries.
- `.claude-plugin/marketplace.json` publishes the Claude Code marketplace entries.
- `tests/` contains repository-only tests that are not installed with a skill.
- `scripts/ci/` contains repository validation and DCO checks.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. All commits must include a [Developer Certificate of Origin](https://developercertificate.org/) sign-off.

Report security issues privately as described in [SECURITY.md](SECURITY.md).

## License

The repository is licensed under [Apache-2.0](LICENSE).
