#!/usr/bin/env python3
"""Regression tests for skill distribution consistency."""

import json
import runpy
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "ci"
    / "verify_skill_distribution.py"
)
distribution = runpy.run_path(str(SCRIPT_PATH))
SkillPackage = distribution["SkillPackage"]
compare_skill_trees = distribution["compare_skill_trees"]
discover_packages = distribution["discover_packages"]
install_portable_skills = distribution["install_portable_skills"]
verify_plugin_cache = distribution["verify_plugin_cache"]
verify_portable_root = distribution["verify_portable_root"]
validate_version_bumps = distribution["validate_version_bumps"]


class SkillDistributionTests(unittest.TestCase):
    def make_package(self, root: Path) -> object:
        canonical = root / "canonical" / "example-skill"
        (canonical / "references").mkdir(parents=True)
        (canonical / "SKILL.md").write_bytes(b"canonical skill\n")
        (canonical / "references" / "guide.md").write_bytes(b"guide\x00bytes\n")
        return SkillPackage("example-plugin", "example-skill", "1.2.3", canonical)

    def test_temporary_portable_install_is_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = self.make_package(root)
            installed_root = root / "installed"

            install_portable_skills([package], installed_root)
            errors = verify_portable_root([package], installed_root)

        self.assertEqual(errors, [])

    def test_missing_installed_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = self.make_package(root)
            installed_root = root / "installed"
            install_portable_skills([package], installed_root)
            (installed_root / "example-skill" / "SKILL.md").unlink()

            errors = verify_portable_root([package], installed_root)

        self.assertTrue(any("missing installed path" in error for error in errors))

    def test_unexpected_installed_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = self.make_package(root)
            installed_root = root / "installed"
            install_portable_skills([package], installed_root)
            (installed_root / "example-skill" / "stale.md").write_text(
                "stale\n", encoding="utf-8"
            )

            errors = verify_portable_root([package], installed_root)

        self.assertTrue(any("unexpected installed path" in error for error in errors))

    def test_changed_installed_bytes_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = self.make_package(root)
            installed_root = root / "installed"
            install_portable_skills([package], installed_root)
            (installed_root / "example-skill" / "SKILL.md").write_bytes(b"changed\n")

            errors = compare_skill_trees(
                package.canonical_root, installed_root / "example-skill"
            )

        self.assertTrue(any("file bytes differ" in error for error in errors))

    def test_versioned_plugin_cache_is_checked(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = self.make_package(root)
            installed_root = (
                root / "cache" / package.plugin_name / package.version / "skills"
            )
            install_portable_skills([package], installed_root)

            errors = verify_plugin_cache([package], root / "cache")

        self.assertEqual(errors, [])

    def test_repository_packages_are_discovered_with_manifest_versions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            plugin_root = Path(directory) / "plugins"
            plugin = plugin_root / "example-plugin"
            manifest_root = plugin / ".codex-plugin"
            skill_root = plugin / "skills" / "example-skill"
            manifest_root.mkdir(parents=True)
            skill_root.mkdir(parents=True)
            (manifest_root / "plugin.json").write_text(
                json.dumps({"version": "1.2.3"}), encoding="utf-8"
            )

            packages = discover_packages(plugin_root)

        self.assertEqual(
            [
                (package.plugin_name, package.skill_name, package.version)
                for package in packages
            ],
            [("example-plugin", "example-skill", "1.2.3")],
        )

    def test_changed_skill_requires_greater_plugin_version(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = self.make_package(Path(directory))

            errors = validate_version_bumps(
                [package],
                [Path("plugins/example-plugin/skills/example-skill/SKILL.md")],
                {"example-plugin": "1.2.3"},
            )

        self.assertTrue(any("is not greater" in error for error in errors))

    def test_changed_skill_accepts_greater_plugin_version(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = self.make_package(Path(directory))

            errors = validate_version_bumps(
                [package],
                [Path("plugins/example-plugin/skills/example-skill/SKILL.md")],
                {"example-plugin": "1.2.2"},
            )

        self.assertEqual(errors, [])

    def test_non_skill_change_does_not_require_plugin_version_bump(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = self.make_package(Path(directory))

            errors = validate_version_bumps(
                [package],
                [Path("tests/test_example.py")],
                {"example-plugin": "1.2.3"},
            )

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
