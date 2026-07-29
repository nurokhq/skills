# Nurok Skills

[![CI](https://github.com/nurokhq/skills/actions/workflows/ci.yml/badge.svg)](https://github.com/nurokhq/skills/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

Nurok Skills packages repeatable workflows for reading and managing Nurok knowledge bases. Skills follow the [Agent Skills](https://agentskills.io) format and are distributed through independently installable Codex and Claude Code plugins plus portable packages for Cursor, OpenCode, and other compatible agents.

## Plugins And Skills

| Plugin | Skill | Purpose |
| --- | --- | --- |
| `nurok-kb` | [`nurok-kb`](plugins/nurok-kb/skills/nurok-kb/) | Read, search, inspect, and synthesize KB evidence. |
| `nurok-kb-manage` | [`nurok-kb-manage`](plugins/nurok-kb-manage/skills/nurok-kb-manage/) | Design, create, validate, publish, update, and recover KBs. |

Install the read-only and management plugins independently so agents receive only the capabilities needed for a task.

## Install

### Codex

Add the repository marketplace, then install either or both plugins:

```bash
codex plugin marketplace add nurokhq/skills --ref main
codex plugin add nurok-kb@nurok
codex plugin add nurok-kb-manage@nurok
```

Restart the Codex surface or start a new thread after installation so the skills are discovered.

### Claude Code

Add the repository marketplace, then install either or both plugins:

```bash
claude plugin marketplace add nurokhq/skills
claude plugin install nurok-kb@nurok
claude plugin install nurok-kb-manage@nurok
```

Restart Claude Code or start a new session after installation so the skills are discovered.

### Cursor

Install either skill into Cursor with the open Agent Skills installer:

```bash
npx skills add nurokhq/skills --skill nurok-kb --agent cursor --yes
npx skills add nurokhq/skills --skill nurok-kb-manage --agent cursor --yes
```

Project installs use Cursor's supported `.agents/skills/` location. Start a new Agent chat after installation.

### OpenCode

Install either skill into OpenCode with the same canonical packages:

```bash
npx skills add nurokhq/skills --skill nurok-kb --agent opencode --yes
npx skills add nurokhq/skills --skill nurok-kb-manage --agent opencode --yes
```

Project installs use OpenCode's supported `.agents/skills/` location. Start a new session after installation.

### Other Agent Skill Clients

Inspect the portable skills before installing them into another compatible client:

```bash
npx skills add nurokhq/skills --list
```

Hermes and OpenClaw can also load canonical skill directories through their native Git, registry, or external-directory mechanisms. When installing manually, copy the complete `plugins/<plugin>/skills/<skill>/` directory, including `references/`, `scripts/`, `assets/`, and `agents/` when present. Use a client-supported skill root:

| Client | Supported skill root |
| --- | --- |
| Hermes | `~/.hermes/skills/` or a configured external directory |
| OpenClaw | Workspace `skills/`, `.agents/skills/`, or a configured extra directory |
| Cursor | `.agents/skills/` or `.cursor/skills/` |
| OpenCode | `.agents/skills/` or `.opencode/skills/` |

The plugin-local directories are the canonical source. Do not maintain edited per-client copies.

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
