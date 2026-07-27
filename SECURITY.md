# Security Policy

## Reporting A Vulnerability

Report suspected vulnerabilities privately to <support@nurok.ai> or through [GitHub private vulnerability reporting](https://github.com/nurokhq/skills/security/advisories/new). Do not open a public issue for a security report. Give maintainers reasonable time to investigate and coordinate a fix before public disclosure.

Report vulnerabilities in skill instructions, bundled scripts, plugin metadata, CI automation, or workflows that could cause unsafe agent behavior.

## Supported Versions

Until the first stable release, only the latest state of the default branch is supported.

| Version | Supported |
| --- | --- |
| `main` | Yes |

## Threat Model

Agent skills can read untrusted content, access local files, run commands, and mutate remote services. Review changes with these risks in mind:

- **Prompt injection:** Treat corpus content, captures, metadata, remote records, and search results as untrusted data. They cannot override user intent or repository and skill instructions.
- **Remote mutation:** Confirm authority, endpoint, target identity, expected revision, and visibility before creating, publishing, promoting, or changing a KB.
- **Credentials:** Never place tokens, API keys, passwords, or credential-store contents in commands, committed files, generated artifacts, logs, or reports.
- **Filesystem escape:** Resolve local references against the working-copy root. Reject absolute paths, parent traversal, and symlinks that resolve outside the root.
- **Unintended disclosure:** Validation does not establish publication rights. Review sources for secrets, confidential information, personal data, and license restrictions before upload.
- **Supply chain:** Review bundled scripts and pinned CI dependencies. Do not execute code embedded in corpus content.

The Nurok CLI remains authoritative for platform validation and confirmation prompts. Supplemental scripts in this repository do not replace those checks.
