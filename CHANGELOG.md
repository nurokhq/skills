# Changelog

All notable changes to Nurok Skills are documented here. The project follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial open-source repository scaffold with Apache-2.0 licensing, DCO, contributor and security policies, GitHub templates, dependency updates, and CI checks.
- Independent `nurok-kb` and `nurok-kb-manage` plugins with Codex and Claude Code marketplace metadata.
- Read-only `nurok-kb` skill for discovery, retrieval, inspection, and evidence-backed synthesis.
- `nurok-kb-manage` skill for the full Nurok OpenAKB lifecycle, including scoped references, an AKB guide template, and a supplemental working-copy audit.
- Portable Agent Skills distribution guidance for Hermes, OpenClaw, Cursor, and OpenCode.
- Repository-level regression tests for working-copy validation and filesystem containment.
- Temporary-install and installed-copy byte verification for canonical skills.
- Pull request checks for skill validation, version bumps, tests, lint, links, workflows, and DCO sign-offs.
- Deterministic `nurok-kb-manage` audit checks for local blob stamps, ordered Source citations and provenance, aggregate projection digests, and working/publishing byte equality.

### Changed

- Bumped all Codex and Claude plugin manifests to `0.1.1` after skill behavior changes.
- Bumped the `nurok-kb-manage` Codex and Claude plugin manifests to `0.1.2` for the expanded audit contract.
