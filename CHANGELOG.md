# Changelog

All notable changes to Nurok Skills are documented here. The project follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial open-source repository scaffold with Apache-2.0 licensing, DCO, contributor and security policies, GitHub templates, dependency updates, and CI checks.
- Initial `0.1.0` releases of the independent `nurok-kb`, `nurok-kb-manage`, and `nurok-kb-capture` plugins with Codex and Claude Code marketplace metadata.
- Read-only `nurok-kb` skill for discovery, retrieval, inspection, and evidence-backed synthesis.
- `nurok-kb-manage` skill for the full Nurok OpenAKB lifecycle, including scoped references, an AKB guide template, and a supplemental working-copy audit.
- `nurok-kb-capture` skill for retaining immutable canonical original evidence without transforming content or publishing KB revisions.
- Portable Agent Skills distribution guidance for Hermes, OpenClaw, Cursor, and OpenCode.
- Repository-level regression tests for working-copy validation and filesystem containment.
- Temporary-install and installed-copy byte verification for canonical skills.
- Pull request checks for skill validation, version bumps, tests, lint, links, workflows, and DCO sign-offs.
- Deterministic `nurok-kb-manage` audit checks for local blob stamps, ordered Source citations and provenance, aggregate projection digests, and working/publishing byte equality.

### Fixed

- Reject malformed SHA-256 values before treating missing local blobs as stamps-only references.
- Preserve primary audit findings when comparison setup cannot load a descriptor.
