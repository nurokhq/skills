#!/usr/bin/env python3
"""Regression tests for repository validation policies."""

import runpy
import tempfile
import unittest
from pathlib import Path

VALIDATOR_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "ci" / "validate_repository.py"
)
validator = runpy.run_path(str(VALIDATOR_PATH))
validate_read_only_skill = validator["validate_read_only_skill"]
validate_skill_links = validator["validate_skill_links"]


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


if __name__ == "__main__":
    unittest.main()
