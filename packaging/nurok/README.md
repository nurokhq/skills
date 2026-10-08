# Nurok Plugin Release

This release combines the canonical `nurok-kb` skill with the existing remote Nurok MCP service in one public plugin named **Nurok**. Supported mobile, web, Mac, Windows, and Codex hosts use the same remote read workflow. The core workflow needs no local CLI, Python, shell, filesystem, or always-on personal computer.

The first release supports discovery, metadata, revision history, search, section reads, and evidence-backed answers. Capture, construction, publication, deletion, and other writes remain in the independently installed management/capture plugins; they are not advertised or bundled here.

## Ownership And Packaging

| Source | Responsibility |
| --- | --- |
| `plugins/nurok-kb/skills/nurok-kb/` | The single canonical read skill and references |
| `packaging/nurok/` | Public manifest, remote MCP configuration, brand assets, and review materials |
| `scripts/release/` | Build, verify, and publish GitHub artifacts |
| Existing Nurok MCP deployment | Tools, authentication, authorization, and remote data access |

The release template alone is not an installable plugin. Build the complete ZIP; canonical skill bytes are copied at build time, not edited in a second source directory. Existing standalone Codex and Claude plugins stay independently installable. Enable either Nurok or the overlapping standalone Nurok KB plugin to avoid duplicate skill discovery.

The icon is the [Nurok GitHub organization avatar](https://github.com/nurokhq), retrieved on 2026-10-08, reused for the logo and composer icon. Optional dark-mode variants are omitted.

## Build And Validate

Stage newly added package files before building: only Git-tracked paths are packaged, using their current working-tree bytes. Untracked local files and caches are excluded, and symlinks, tracked hidden skill files, and bytecode are rejected.

```bash
uv sync --locked
uv run python scripts/ci/validate_repository.py
uv run python scripts/ci/verify_skill_distribution.py
uv run python scripts/release/build_plugin.py --version 0.1.0
```

The ignored `dist/` directory receives:

- `nurok-0.1.0.zip`: one self-contained `nurok/` directory with `plugin.json`, `mcp.json`, the canonical skill, icon, and license.
- `nurok-0.1.0.zip.sha256`: archive checksum.
- `nurok-0.1.0.build.json`: source commit, dirty-state flag, and per-file hashes.

The builder checks every archive byte against its canonical input. Stable ordering, timestamps, and modes make repeated builds with the same inputs, version, and compression runtime reproducible. The public package rejects local MCP commands, inline credentials, private app bindings, and lifecycle hooks.

## Automatic GitHub Releases

Every PR and `main` push produces a reviewable `nurok-plugin` Actions artifact. Only a `main` push with successful docs, Python checks, tests, and package validation can create a GitHub Release. PR jobs have read-only permissions and never publish.

The aggregate version is `0.1.<CI run number>` and the tag is `nurok-v0.1.<CI run number>`. Gaps from PR runs are expected; reruns keep the version. CI replaces the template's `0.1.0` only in the generated manifest. Change the workflow version expression and this guide together when changing the major/minor line. The standalone Nurok KB plugin retains its own semantic version and existing version-bump checks.

Publication compares the bundled read skill, template, release scripts, and license against the newest aggregate release tag. Unrelated management/capture changes or repository-only docs do not trigger a release. Comparing with the last release catches changes from skipped or failed earlier runs. Older runs cannot supersede a newer commit's release. Serialized publication uploads through a draft and can resume an interrupted draft only for the same source commit; published assets are immutable.

The release job alone uses `GITHUB_TOKEN` with `contents: write`. No additional publishing secret is required, but organization policies can still restrict release creation. Merging this workflow enables future GitHub publication; opening its PR does not publish anything.

## Connection And Cross-Device Behavior

The packaged endpoint is `https://mcp.nurok.ai/mcp` over Streamable HTTP. Anonymous public reads are supported. Private access must use whatever authenticated connection the service and host actually support; CLI login does not transfer to mobile or establish an MCP identity. No credential or OAuth endpoint is invented in the package.

The bundled skill defaults to MCP. Explicit CLI reads remain an optional path for a host that has an installed CLI and shell. A missing remote connection on mobile is reported as a connection prerequisite, not a request to install local software.

The current tool set is read-only. Review [the submission record](submission.md) for verified behavior, missing server annotations, and unverified device/authentication paths. Platform support does not substitute for end-to-end installation tests on each target client.

## Public Directory Publication

A GitHub Release is a distribution artifact, not an OpenAI directory publication. Upload the ZIP through the [plugin portal](https://platform.openai.com/plugins), connect and scan its MCP service, resolve findings, submit for review, and publish after approval. Skills or listing changes require a new ZIP. The workflow does not automate dashboard attestations or claim directory availability. See the [official submission guide](https://developers.openai.com/plugins/deploy/submission).

Include MCP from the first submission: the current portal does not support adding MCP to an existing skills-only plugin. This package includes five positive and three negative review cases. Complete the remaining [submission materials and device checks](submission.md) before calling a build ready for public review.
