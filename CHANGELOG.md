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
- Return structured audit findings for non-string Source types.
- Validate provenance byte ranges even when Section content is available only by stamp.
- Require DCO sign-offs regardless of the commit's user-controlled author name.
- Reject file URIs and platform-absolute filesystem paths outside the working root.
- Report non-UTF-8 provenance sidecars as structured audit findings.
- Preserve complete summary counts when a descriptor cannot be loaded.
- Run distribution and plugin-version checks against the pull request base in CI.
- Return a structured comparison finding when a compared descriptor is not UTF-8.
- Keep the Nurok CLI optional for read-only workflows that use bundled MCP tools.
- Require each DCO sign-off to match its commit author.
- Reject local references occupied by directories or other non-file entries.
- Require provenance byte ranges to cover complete ordered, non-overlapping Section Source blocks.
- Reject malformed provenance claim collections and entries.
- Reject symlinked canonical skill roots before traversal.
- Reject repository-only tests anywhere inside a distributable skill tree.
