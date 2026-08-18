#!/usr/bin/env python3
"""Regression tests for repository validation policies."""

import runpy
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = REPOSITORY_ROOT / "scripts" / "ci" / "validate_repository.py"
validator = runpy.run_path(str(VALIDATOR_PATH))
validate_read_only_skill = validator["validate_read_only_skill"]
validate_skill_links = validator["validate_skill_links"]
validate_portable_skill_markdown = validator["validate_portable_skill_markdown"]
validate_management_guardrails = validator["validate_management_guardrails"]
validate_original_content_guardrails = validator["validate_original_content_guardrails"]


class RepositoryValidationTests(unittest.TestCase):
    def write_skill(self, root: Path, contents: str) -> Path:
        skill_root = root / "nurok-kb-test"
        skill_root.mkdir()
        (skill_root / "SKILL.md").write_text(contents, encoding="utf-8")
        return skill_root

    def test_read_only_command_and_output_flag_are_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skill_root = self.write_skill(
                Path(directory),
                "`nurok kb search --output json query`\n",
            )
            errors: list[str] = []

            validate_read_only_skill(skill_root, errors)

        self.assertEqual(errors, [])

    def test_ci_runs_distribution_checks_against_pull_request_base(self) -> None:
        workflow = (REPOSITORY_ROOT / ".github" / "workflows" / "ci.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("scripts/ci/verify_skill_distribution.py", workflow)
        self.assertIn("github.event.pull_request.base.sha", workflow)
        self.assertIn("--base-ref", workflow)
        self.assertIn("fetch-depth: 0", workflow)

    def test_mutating_command_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skill_root = self.write_skill(
                Path(directory),
                "`nurok kb push --dir ./working-copy`\n",
            )
            errors: list[str] = []

            validate_read_only_skill(skill_root, errors)

        self.assertTrue(any("disallowed nurok kb push" in error for error in errors))

    def test_local_artifact_output_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skill_root = self.write_skill(
                Path(directory),
                "`nurok kb cat --out ./artifacts`\n",
            )
            errors: list[str] = []

            validate_read_only_skill(skill_root, errors)

        self.assertTrue(any("reads to stdout" in error for error in errors))

    def test_relative_link_must_stay_inside_skill(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill_root = self.write_skill(root, "[outside](../outside.md)\n")
            (root / "outside.md").write_text("outside\n", encoding="utf-8")
            errors: list[str] = []

            validate_skill_links(skill_root, errors)

        self.assertTrue(any("link escapes the skill root" in error for error in errors))

    def test_host_specific_skill_mention_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skill_root = self.write_skill(
                Path(directory),
                "Route the request to `$nurok-kb-manage`.\n",
            )
            errors: list[str] = []

            validate_portable_skill_markdown(skill_root, errors)

        self.assertTrue(any("host-specific mention" in error for error in errors))

    def test_host_neutral_skill_name_and_schema_variable_are_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skill_root = self.write_skill(
                Path(directory),
                "Use `nurok-kb-manage` when available and preserve `$schema`.\n",
            )
            errors: list[str] = []

            validate_portable_skill_markdown(skill_root, errors)

        self.assertEqual(errors, [])

    def test_runtime_discovered_create_prevention_guard_is_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            plugin_root = Path(directory) / "nurok-kb-manage"
            skill_root = plugin_root / "skills" / "nurok-kb-manage"
            skill_root.mkdir(parents=True)
            (skill_root / "SKILL.md").write_text(
                "Confirm authority, endpoint, identity, visibility, and target. "
                "Require the current CLI's create-prevention guard. "
                "Inspect `nurok kb <command> --help`.\n",
                encoding="utf-8",
            )
            errors: list[str] = []

            validate_management_guardrails(plugin_root, errors)

        self.assertEqual(errors, [])

    def test_literal_no_create_does_not_replace_runtime_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            plugin_root = Path(directory) / "nurok-kb-manage"
            skill_root = plugin_root / "skills" / "nurok-kb-manage"
            skill_root.mkdir(parents=True)
            (skill_root / "SKILL.md").write_text(
                "Confirm authority, endpoint, identity, visibility, and target. "
                "Always use `--no-create`.\n",
                encoding="utf-8",
            )
            errors: list[str] = []

            validate_management_guardrails(plugin_root, errors)

        self.assertTrue(any("create-prevention" in error for error in errors))
        self.assertTrue(any("runtime CLI discovery" in error for error in errors))

    def test_capture_requires_original_content_guardrails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skill_root = self.write_skill(
                Path(directory),
                "Preserve canonical original evidence and original content.\n",
            )
            errors: list[str] = []

            validate_original_content_guardrails(skill_root, "nurok-kb-capture", errors)

        self.assertTrue(
            any("one source document per capture" in error for error in errors)
        )
        self.assertTrue(any("do not summarize" in error for error in errors))

    def test_manage_original_content_guardrails_are_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skill_root = self.write_skill(
                Path(directory),
                "Use original-only and article-body-only rules for each Source block. "
                "Allow presentation-only Markdown.\n",
            )
            errors: list[str] = []

            validate_original_content_guardrails(skill_root, "nurok-kb-manage", errors)

        self.assertEqual(errors, [])

    def test_manage_requires_article_body_and_source_block_guardrails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skill_root = self.write_skill(
                Path(directory),
                "Preserve original-only content with presentation-only Markdown.\n",
            )
            errors: list[str] = []

            validate_original_content_guardrails(skill_root, "nurok-kb-manage", errors)

        self.assertTrue(any("article-body-only" in error for error in errors))
        self.assertTrue(any("source block" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
