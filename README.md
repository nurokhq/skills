# Nurok Skills

[![CI](https://github.com/nurokhq/skills/actions/workflows/ci.yml/badge.svg)](https://github.com/nurokhq/skills/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

Nurok Skills packages repeatable workflows for capturing, reading, and managing Nurok knowledge bases. Skills follow the [Agent Skills](https://agentskills.io) format and are distributed through independently installable Codex and Claude Code plugins plus portable packages for Hermes, OpenClaw, Cursor, OpenCode, and other compatible agents.

## Plugins And Skills

| Plugin | Skill | Purpose |
| --- | --- | --- |
| `nurok-kb` | [`nurok-kb`](plugins/nurok-kb/skills/nurok-kb/) | Read, search, inspect, and synthesize KB evidence. |
| `nurok-kb-manage` | [`nurok-kb-manage`](plugins/nurok-kb-manage/skills/nurok-kb-manage/) | Design, create, validate, publish, update, and recover KBs. |
| `nurok-kb-capture` | [`nurok-kb-capture`](plugins/nurok-kb-capture/skills/nurok-kb-capture/) | Capture, refresh, and assess source evidence. |

Each plugin is standalone and declares no dependency on either of the others. Install only the capture, read-only, or management capabilities needed for a task; cross-skill handoffs are conditional.

## Install

### Ask An Agent

Give a compatible coding agent this prompt, replacing the skill name when needed:

```text
Install the nurok-kb-capture skill from https://github.com/nurokhq/skills
```

The agent can use its native installer or a compatible Agent Skills installer.

### Native Installers

Use a client's native installer when it supports this repository layout. These commands are client-specific and do not use the portable Skills CLI.

#### Codex

Add the Codex marketplace, then install the required plugins:

```bash
codex plugin marketplace add nurokhq/skills --ref main
codex plugin add nurok-kb@nurok
codex plugin add nurok-kb-manage@nurok
codex plugin add nurok-kb-capture@nurok
```

Restart the Codex surface or start a new thread after installation.

#### Claude Code

Add the Claude Code marketplace, then install the required plugins:

```bash
claude plugin marketplace add nurokhq/skills
claude plugin install nurok-kb@nurok
claude plugin install nurok-kb-manage@nurok
claude plugin install nurok-kb-capture@nurok
```

Claude Code follows the repository's default branch. Restart Claude Code or start a new session after installation.

#### Hermes

Hermes can install each canonical skill directory directly from GitHub:

```bash
hermes skills install nurokhq/skills/plugins/nurok-kb/skills/nurok-kb
hermes skills install nurokhq/skills/plugins/nurok-kb-manage/skills/nurok-kb-manage
hermes skills install nurokhq/skills/plugins/nurok-kb-capture/skills/nurok-kb-capture
```

These commands follow the repository's default branch and install into Hermes' managed skills directory. Use the Skills CLI method below for portable project or global installations.

### Portable Skills CLI

The open [Skills CLI](https://github.com/vercel-labs/skills) provides common `npx` commands for compatible agents. The following examples use `nurok-kb-capture`; substitute `nurok-kb` or `nurok-kb-manage` for another skill.

For a project installation, run both commands from the target workspace root:

```bash
npx skills add nurokhq/skills --skill nurok-kb-capture
npx skills update --project nurok-kb-capture
```

For a global installation, use the global scope explicitly for both commands:

```bash
npx skills add nurokhq/skills --skill nurok-kb-capture --global
npx skills update --global nurok-kb-capture
```

The add command prompts for a target agent when needed. See the [Skills CLI documentation](https://github.com/vercel-labs/skills) for supported agents and options. Restart the client or start a new session after adding or updating a skill.

The plugin-local directories remain the canonical source. Do not commit generated client-specific copies.

## Upgrade

After a skill update is published, upgrade it with the same installation method.

For Codex, refresh the marketplace snapshot and reinstall each installed plugin:

```bash
codex plugin marketplace upgrade nurok
codex plugin add nurok-kb@nurok
codex plugin add nurok-kb-manage@nurok
codex plugin add nurok-kb-capture@nurok
```

For Claude Code, update the marketplace and each installed plugin:

```bash
claude plugin marketplace update nurok
claude plugin update nurok-kb@nurok
claude plugin update nurok-kb-manage@nurok
claude plugin update nurok-kb-capture@nurok
```

For a native Hermes installation, check for and apply upstream changes:

```bash
hermes skills check
hermes skills update nurok-kb
hermes skills update nurok-kb-manage
hermes skills update nurok-kb-capture
```

## Prerequisites

The read-only and management skills require the Nurok CLI. The management skill requires Nurok CLI 0.2.0 or later and Python 3.9 or later for its supplemental audit:

```bash
curl -fsSL https://static.nurok.ai/cli/install.sh | bash
```

Public reads may work anonymously. Private reads and remote management require a Nurok login or `NUROK_API_KEY`. Local authoring and the audit script do not require remote credentials.

The capture skill accepts any authorized method suitable for the source and available tools. It neither prescribes a crawler nor builds or publishes KB revisions.

The `nurok-kb` plugin does not change remote state. The management plugin can publish, change source registries or visibility, and operate snapshots; its skill requires explicit authority plus endpoint, identity, visibility, and target confirmation before remote mutations.

## Repository Layout

- `plugins/nurok-kb/` contains the read-only plugin and its canonical skills.
- `plugins/nurok-kb-manage/` contains the lifecycle-management plugin and skill.
- `plugins/nurok-kb-capture/` contains the source-capture plugin and skill.
- `.agents/plugins/marketplace.json` publishes the Codex marketplace entries.
- `.claude-plugin/marketplace.json` publishes the Claude Code marketplace entries.
- `tests/` contains repository-only tests that are not installed with a skill.
- `scripts/ci/` contains repository validation and DCO checks.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. All commits must include a [Developer Certificate of Origin](https://developercertificate.org/) sign-off.

Report security issues privately as described in [SECURITY.md](SECURITY.md).

## License

The repository is licensed under [Apache-2.0](LICENSE).
