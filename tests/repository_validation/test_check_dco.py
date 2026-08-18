#!/usr/bin/env python3
"""Regression tests for the repository DCO verifier."""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

DCO_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "ci" / "check-dco.sh"


class CheckDcoTests(unittest.TestCase):
    def git(
        self, root: Path, *args: str, env: dict[str, str] | None = None
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )

    def initialize_repository(self, root: Path) -> str:
        self.git(root, "init", "--quiet")
        self.git(root, "config", "user.name", "DCO Test")
        self.git(root, "config", "user.email", "dco@example.com")
        self.git(root, "commit", "--allow-empty", "--signoff", "-m", "Base")
        return self.git(root, "rev-parse", "HEAD").stdout.strip()

    def run_check(self, root: Path, base: str) -> subprocess.CompletedProcess[str]:
        head = self.git(root, "rev-parse", "HEAD").stdout.strip()
        return subprocess.run(
            ["bash", str(DCO_SCRIPT), base, head],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_forged_bot_author_does_not_bypass_signoff(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base = self.initialize_repository(root)
            env = os.environ.copy()
            env["GIT_AUTHOR_NAME"] = "forged[bot]"
            env["GIT_AUTHOR_EMAIL"] = "forged@example.com"
            self.git(root, "commit", "--allow-empty", "-m", "Unsigned", env=env)

            result = self.run_check(root, base)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("missing a Signed-off-by", result.stdout)

    def test_signed_commit_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base = self.initialize_repository(root)
            self.git(root, "commit", "--allow-empty", "--signoff", "-m", "Signed")

            result = self.run_check(root, base)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
