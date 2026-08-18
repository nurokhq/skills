# Contributing To Nurok Skills

Thank you for improving Nurok's public agent workflows. Small fixes can go directly to a pull request. Discuss new skills, broad workflow changes, or new remote-mutation behavior in a GitHub issue first.

## Developer Certificate Of Origin

All commits must be signed off under the [Developer Certificate of Origin](https://developercertificate.org/). The sign-off certifies that you wrote the contribution or have the right to submit it under Apache-2.0.

```bash
git commit -s -m "Describe the change"
```

Amend an unsigned commit with `git commit --amend -s`. CI enforces sign-off; this project does not use a CLA.

## Skill Requirements

Each skill must be self-contained under a plugin's `skills/<skill-name>/` directory and include:

- `SKILL.md` with only `name` and `description` in YAML frontmatter;
- concise imperative instructions, with details moved to directly linked `references/` files;
- deterministic scripts only when they add repeatable value;
- runtime assets only when the skill uses them;
- `agents/openai.yaml` kept consistent with the skill when Codex metadata is provided.

Skill names must be globally unique across plugins. Keep canonical skills portable: do not add host-specific frontmatter, cross-plugin paths, symlinks, or separately edited copies for each agent client.

Keep tests outside the distributable skill under `tests/`. Add or update tests for every script behavior change. Do not add a README, changelog, installation guide, or other repository documentation inside a skill directory.

Treat remote mutations as security-sensitive. Skills must distinguish analysis, local changes, and publication authority; confirm the endpoint and target identity; protect credentials; and treat external content as untrusted data.

Keep skills in the read-only plugin limited to the documented list, show, search, section list/get, cat, and changelog operations. A read-only skill must not imply local-write or remote-mutation authority.

## Run The Checks

Install the locked development environment and run the same checks used by CI:

```bash
uv sync --locked
uv run python scripts/ci/validate_repository.py
uv run python scripts/ci/verify_skill_distribution.py
uv run ruff format --check plugins tests scripts
uv run ruff check plugins tests scripts
uv run python -m unittest discover -s tests -p "test_*.py" -v
npx --yes markdownlint-cli2 "**/*.md"
lychee --offline --config lychee.toml .
actionlint
```

Also run the bundled supplemental audit and relevant Nurok CLI validation against a representative working copy when changing KB behavior.

When preparing a release, pass the merge base with `--base-ref` so every changed canonical skill requires a plugin version increase. Pass each maintained portable installation root with `--portable-root` and each Codex or Claude plugin cache root with `--plugin-cache-root`. Use a repeated `--skill` argument when an installation intentionally contains only a subset. The verification must report byte-identical copies before release.

## Pull Requests

Use short, imperative English commit summaries. In the pull request, explain the behavior change, safety impact, and validation performed. Keep unrelated refactors out of the change.

Do not commit credentials, private KB content, local agent state, generated caches, or the ignored `docs/superpowers/`, `.superpowers/`, and `.worktrees/` directories.

Report vulnerabilities privately to <support@nurok.ai> instead of opening a public issue.
