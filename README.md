# Nurok Skills

[![CI](https://github.com/nurokhq/skills/actions/workflows/ci.yml/badge.svg)](https://github.com/nurokhq/skills/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

Nurok Skills packages repeatable agent workflows for building and operating Nurok knowledge bases. Skills follow the [Agent Skills](https://agentskills.io) format and are also distributed as a Codex skill-only plugin.

## Available Skills

| Skill | Purpose |
| --- | --- |
| [`nurok-manage-akb`](plugins/nurok-skills/skills/nurok-manage-akb/) | Design, create, validate, publish, update, and recover Nurok OpenAKB knowledge bases. |

## Install

### Codex Plugin

Add this repository as a marketplace, then install the plugin:

```bash
codex plugin marketplace add nurokhq/skills --ref main
codex plugin add nurok-skills@nurok
```

Start a new Codex thread after installation so the skill is discovered.

### Agent Skills Installer

Install the skill from the repository with a compatible Agent Skills client:

```bash
npx skills add nurokhq/skills --skill nurok-manage-akb
```

Codex users can also ask `$skill-installer` to install the skill directly from:

```text
https://github.com/nurokhq/skills/tree/main/plugins/nurok-skills/skills/nurok-manage-akb
```

## Prerequisites

The `nurok-manage-akb` skill requires:

- Nurok CLI 0.2.0 or later;
- Python 3.9 or later for the bundled supplemental audit;
- a Nurok login or `NUROK_API_KEY` for authenticated remote operations.

Install the Nurok CLI:

```bash
curl -fsSL https://static.nurok.ai/cli/install.sh | bash
```

Local authoring and the audit script do not require remote credentials. Publishing, pulling private KBs, source-registry changes, visibility changes, and snapshot operations can modify remote state. The skill requires explicit publish authority and endpoint confirmation before those operations.

## Repository Layout

- `plugins/nurok-skills/` contains the Codex plugin and distributable skills.
- `tests/` contains repository-only tests that are not installed with a skill.
- `scripts/ci/` contains repository validation and DCO checks.
- `.agents/plugins/marketplace.json` publishes the Codex marketplace entry.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. All commits must include a [Developer Certificate of Origin](https://developercertificate.org/) sign-off.

Report security issues privately as described in [SECURITY.md](SECURITY.md).

## License

The repository is licensed under [Apache-2.0](LICENSE).
