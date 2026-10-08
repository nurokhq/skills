"""Exercise the distributable archive, source isolation, and reproducibility."""

import hashlib
import json
import os
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
release = runpy.run_path(str(ROOT / "scripts/release/build_plugin.py"))
build = release["build"]
package_files = release["package_files"]
verify_archive = release["verify_archive"]


class PluginReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "repo"
        self.root.mkdir()
        shutil.copytree(ROOT / "packaging/nurok", self.root / "packaging/nurok")
        for name in release["SKILLS"]:
            source = Path("plugins") / name / "skills" / name
            shutil.copytree(
                ROOT / source,
                self.root / source,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
        shutil.copyfile(ROOT / "LICENSE", self.root / "LICENSE")
        self.git("init", "-q")
        self.git("add", ".")
        self.git(
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-qm",
            "Fixture",
        )
        self.output = Path(self.directory.name) / "output"

    def git(self, *args: str) -> None:
        subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)

    def test_bundle_contains_canonical_bytes_and_remote_mcp(self) -> None:
        archive = build(self.root, self.output, "0.1.23")
        with zipfile.ZipFile(archive) as bundle:
            manifest = json.loads(bundle.read("nurok/plugin.json"))
            self.assertEqual(manifest["version"], "0.1.23")
            for name in release["SKILLS"]:
                source = self.root / "plugins" / name / "skills" / name
                for path in source.rglob("*"):
                    if path.is_file():
                        member = f"nurok/skills/{name}/{path.relative_to(source)}"
                        self.assertEqual(bundle.read(member), path.read_bytes())
            self.assertIn("nurok/assets/icon.png", bundle.namelist())
            self.assertIn("nurok/LICENSE", bundle.namelist())
            mcp = json.loads(bundle.read("nurok/mcp.json"))
            server = mcp["mcpServers"]["nurok"]
            self.assertEqual(server["type"], "streamable-http")
            self.assertEqual(server["url"], "https://mcp.nurok.ai/mcp")
            self.assertEqual(
                {
                    name.split("/")[2]
                    for name in bundle.namelist()
                    if name.startswith("nurok/skills/")
                },
                {"nurok-kb"},
            )
        checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
        self.assertEqual(
            archive.with_suffix(".zip.sha256").read_text(),
            f"{checksum}  {archive.name}\n",
        )
        provenance = json.loads(archive.with_suffix(".build.json").read_bytes())
        self.assertFalse(provenance["dirty"])
        self.assertEqual(provenance["archive_sha256"], checksum)

    def test_repeated_builds_are_byte_identical(self) -> None:
        first = build(self.root, self.output / "first", "0.1.23")
        second = build(self.root, self.output / "second", "0.1.23")
        self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_untracked_credentials_and_cache_are_excluded(self) -> None:
        source = self.root / "plugins/nurok-kb/skills/nurok-kb"
        (source / ".env").write_text("private credential")
        (source / "__pycache__").mkdir()
        (source / "__pycache__/example.pyc").write_bytes(b"cache")
        files = package_files(self.root, "0.1.23")
        self.assertFalse(any(".env" in name or "__pycache__" in name for name in files))

    def test_tracked_symlink_is_rejected(self) -> None:
        source = self.root / "plugins/nurok-kb/skills/nurok-kb/leak.txt"
        source.symlink_to(self.root / "LICENSE")
        self.git("add", ".")
        with self.assertRaisesRegex(ValueError, "symlink"):
            package_files(self.root, "0.1.23")

    def test_symlinked_skill_directory_is_rejected(self) -> None:
        source = self.root / "plugins/nurok-kb/skills/nurok-kb"
        external = Path(self.directory.name) / "external"
        source.rename(external)
        source.symlink_to(external, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            package_files(self.root, "0.1.23")

    def test_tracked_hidden_file_is_rejected(self) -> None:
        source = self.root / "plugins/nurok-kb/skills/nurok-kb/.env"
        source.write_text("private credential")
        self.git("add", ".")
        with self.assertRaisesRegex(ValueError, "hidden file"):
            package_files(self.root, "0.1.23")

    def test_missing_canonical_file_fails_instead_of_shipping_partial_bundle(self):
        source = self.root / "plugins/nurok-kb/skills/nurok-kb/SKILL.md"
        source.unlink()
        with self.assertRaises(FileNotFoundError):
            package_files(self.root, "0.1.23")

    def test_version_cannot_escape_output_directory(self) -> None:
        for version in ("../escape", "v1.2.3", "1.2", "01.2.3", "1.2.3-beta"):
            with self.subTest(version=version), self.assertRaises(ValueError):
                package_files(self.root, version)

    def test_public_bundle_rejects_app_bindings_and_hooks(self) -> None:
        path = self.root / "packaging/nurok/plugin.json"
        original = json.loads(path.read_bytes())
        for key in ("apps", "hooks", "mcpServers"):
            with self.subTest(key=key):
                manifest = dict(original, **{key: "./unexpected.json"})
                path.write_text(json.dumps(manifest))
                with self.assertRaisesRegex(ValueError, "hooks and app bindings"):
                    package_files(self.root, "0.1.23")

    def test_remote_mcp_cannot_be_replaced_with_a_local_command(self) -> None:
        path = self.root / "packaging/nurok/mcp.json"
        value = json.loads(path.read_bytes())
        value["mcpServers"]["nurok"] = {"command": "nurok", "args": ["mcp"]}
        path.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, "remote Nurok MCP"):
            package_files(self.root, "0.1.23")

    def test_credentials_cannot_be_embedded_in_mcp_config(self) -> None:
        path = self.root / "packaging/nurok/mcp.json"
        value = json.loads(path.read_bytes())
        value["mcpServers"]["nurok"]["headers"] = {"Authorization": "Bearer secret"}
        path.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, "no local credentials"):
            package_files(self.root, "0.1.23")

    def test_corrupted_archive_is_rejected(self) -> None:
        files = package_files(self.root, "0.1.23")
        archive = build(self.root, self.output, "0.1.23")
        with zipfile.ZipFile(archive, "w") as bundle:
            for name, contents in files.items():
                bundle.writestr(
                    f"nurok/{name}", b"changed" if name == "LICENSE" else contents
                )
        with self.assertRaisesRegex(ValueError, "bytes differ"):
            verify_archive(archive, files)

    def test_unexpected_archive_member_is_rejected(self) -> None:
        files = package_files(self.root, "0.1.23")
        archive = build(self.root, self.output, "0.1.23")
        with zipfile.ZipFile(archive, "a") as bundle:
            bundle.writestr("nurok/private.txt", "unexpected")
        with self.assertRaisesRegex(ValueError, "inventory"):
            verify_archive(archive, files)

    def prepare_publication(self) -> dict[str, str]:
        remote = Path(self.directory.name) / "remote.git"
        subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
        self.git("remote", "add", "origin", str(remote))
        self.git("push", "-q", "origin", "HEAD:refs/heads/main")
        binary = Path(self.directory.name) / "bin"
        binary.mkdir()
        fake_gh = binary / "gh"
        fake_gh.write_text(
            f"#!{sys.executable}\n"
            + r"""
import json
import os
import sys
from pathlib import Path

args = sys.argv[1:]
with Path(os.environ["FAKE_GH_LOG"]).open("a") as stream:
    stream.write(json.dumps(args) + "\n")
if args[:2] == ["release", "view"]:
    state = os.environ.get("FAKE_RELEASE_STATE")
    if not state:
        sys.exit(1)
    print(state)
"""
        )
        fake_gh.chmod(0o755)
        sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=self.root, text=True
        ).strip()
        return {
            **os.environ,
            "PATH": f"{binary}:{os.environ['PATH']}",
            "PLUGIN_VERSION": "0.1.23",
            "GITHUB_SHA": sha,
            "GITHUB_REPOSITORY": "example/skills",
            "GITHUB_REF": "refs/heads/main",
            "GITHUB_EVENT_NAME": "push",
            "FAKE_GH_LOG": str(Path(self.directory.name) / "gh.jsonl"),
        }

    def publish(self, environment: dict[str, str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["bash", str(ROOT / "scripts/release/publish_plugin.sh")],
            cwd=self.root,
            env=environment,
            capture_output=True,
            text=True,
        )

    def gh_calls(self, environment: dict[str, str]) -> list[list[str]]:
        log = Path(environment["FAKE_GH_LOG"])
        return [json.loads(line) for line in log.read_text().splitlines()]

    def commit_change(self, relative: str) -> None:
        path = self.root / relative
        path.write_text(
            path.read_text() + "\nChanged.\n" if path.exists() else "Docs\n"
        )
        self.git("add", ".")
        self.git(
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-qm",
            "Change",
        )

    def test_first_publication_uses_draft_then_upload_then_publish(self) -> None:
        environment = self.prepare_publication()
        build(self.root, self.root / "dist", "0.1.23")
        result = self.publish(environment)
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.gh_calls(environment)
        self.assertEqual(
            [call[1] for call in calls], ["view", "create", "upload", "edit"]
        )
        self.assertIn("--draft", calls[1])
        self.assertIn(environment["GITHUB_SHA"], calls[1])
        self.assertIn("--draft=false", calls[3])

    def test_unchanged_release_does_not_call_github(self) -> None:
        environment = self.prepare_publication()
        self.git("tag", "nurok-v0.1.22")
        result = self.publish(environment)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("unchanged", result.stdout)
        self.assertFalse(Path(environment["FAKE_GH_LOG"]).exists())

    def test_docs_push_catches_unreleased_skill_change(self) -> None:
        self.git("tag", "nurok-v0.1.22")
        self.commit_change("plugins/nurok-kb/skills/nurok-kb/SKILL.md")
        self.commit_change("README.md")
        environment = self.prepare_publication()
        build(self.root, self.root / "dist", "0.1.23")
        result = self.publish(environment)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("create", [call[1] for call in self.gh_calls(environment)])

    def test_unrelated_docs_change_does_not_publish(self) -> None:
        self.git("tag", "nurok-v0.1.22")
        self.commit_change("README.md")
        environment = self.prepare_publication()
        result = self.publish(environment)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(Path(environment["FAKE_GH_LOG"]).exists())

    def test_old_run_cannot_replace_a_newer_release(self) -> None:
        self.commit_change("plugins/nurok-kb/skills/nurok-kb/SKILL.md")
        self.git("tag", "nurok-v0.1.24")
        self.git("checkout", "-q", "HEAD~1")
        environment = self.prepare_publication()
        result = self.publish(environment)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("newer or divergent", result.stdout)
        self.assertFalse(Path(environment["FAKE_GH_LOG"]).exists())

    def test_interrupted_draft_resumes_without_creating_another_release(self) -> None:
        environment = self.prepare_publication()
        environment["FAKE_RELEASE_STATE"] = json.dumps(
            {"isDraft": True, "targetCommitish": environment["GITHUB_SHA"]}
        )
        build(self.root, self.root / "dist", "0.1.23")
        result = self.publish(environment)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            [call[1] for call in self.gh_calls(environment)], ["view", "upload", "edit"]
        )

    def test_published_release_assets_are_not_overwritten(self) -> None:
        environment = self.prepare_publication()
        environment["FAKE_RELEASE_STATE"] = json.dumps(
            {"isDraft": False, "targetCommitish": environment["GITHUB_SHA"]}
        )
        build(self.root, self.root / "dist", "0.1.23")
        result = self.publish(environment)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual([call[1] for call in self.gh_calls(environment)], ["view"])

    def test_invalid_archive_checksum_prevents_upload(self) -> None:
        environment = self.prepare_publication()
        archive = build(self.root, self.root / "dist", "0.1.23")
        archive.write_bytes(b"corrupted")
        result = self.publish(environment)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("checksum", result.stderr)
        self.assertFalse(Path(environment["FAKE_GH_LOG"]).exists())

    def test_pull_requests_cannot_publish(self) -> None:
        environment = self.prepare_publication()
        environment["GITHUB_EVENT_NAME"] = "pull_request"
        result = self.publish(environment)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("main-branch push", result.stderr)
        self.assertFalse(Path(environment["FAKE_GH_LOG"]).exists())


if __name__ == "__main__":
    unittest.main()
