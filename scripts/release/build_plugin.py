#!/usr/bin/env python3
"""Build a deterministic Nurok plugin ZIP from tracked, canonical skill files."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = Path("packaging/nurok")
SKILLS = ("nurok-kb",)
SEMVER = re.compile(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)")
# The provided public OAuth client must match api-server's curated client.
EXPECTED_MCP = {
    "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
    "mcpServers": {
        "nurok": {
            "type": "streamable-http",
            "url": "https://mcp.nurok.ai/mcp",
            "extensions": {
                "com.openai": {
                    "auth": {
                        "type": "mixed",
                        "client": {
                            "mode": "provided",
                            "clientId": "nurok-chatgpt-prod",
                            "tokenEndpointAuthMethod": "none",
                        },
                        "baseScopes": ["kb:read"],
                    }
                }
            },
        }
    },
}


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()


def tracked_files(root: Path, source: Path) -> list[Path]:
    output = git(root, "ls-files", "-z", "--", source.as_posix())
    files = [Path(name) for name in output.split("\0") if name]
    if not files:
        raise ValueError(f"no tracked package files: {source}; stage new files first")
    return sorted(files)


def read_source(root: Path, relative: Path) -> bytes:
    for part in (relative, *relative.parents):
        if (root / part).is_symlink():
            raise ValueError(f"symlink in package source: {relative}")
    if any(part.startswith(".") or part == "__pycache__" for part in relative.parts):
        raise ValueError(f"hidden file or cache in package source: {relative}")
    if relative.suffix in {".pyc", ".pyo"}:
        raise ValueError(f"bytecode in package source: {relative}")
    return (root / relative).read_bytes()


def json_bytes(value: dict) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()


def package_files(root: Path, version: str) -> dict[str, bytes]:
    if not SEMVER.fullmatch(version):
        raise ValueError("version must be strict numeric MAJOR.MINOR.PATCH")
    files: dict[str, bytes] = {}
    for source in tracked_files(root, TEMPLATE):
        relative = source.relative_to(TEMPLATE)
        if relative.parts[0] not in {"plugin.json", "mcp.json", "assets"}:
            continue
        files[relative.as_posix()] = read_source(root, source)
    manifest = json.loads(files["plugin.json"])
    if manifest.get("name") != "nurok":
        raise ValueError("plugin name must be nurok")
    if manifest.get("$schema") != (
        "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
    ):
        raise ValueError("expected Agent Plugins 1.0 manifest")
    extension = manifest["extensions"]["com.openai"]
    for settings in (manifest, extension):
        if any(key in settings for key in ("apps", "mcpServers", "hooks", "skills")):
            raise ValueError(
                "declare remote MCP in mcp.json; "
                "local hooks and app bindings are forbidden"
            )
    interface = extension["interface"]
    for field in ("displayName", "shortDescription"):
        if not 1 <= len(interface[field]) <= 30:
            raise ValueError(f"{field} must contain 1-30 characters")
    for key in ("logo", "composerIcon"):
        if interface[key] != "./assets/icon.png" or "assets/icon.png" not in files:
            raise ValueError(f"missing packaged {key}")
    if json.loads(files["mcp.json"]) != EXPECTED_MCP:
        raise ValueError("expected the remote Nurok MCP with no local credentials")
    manifest["version"] = version
    files["plugin.json"] = json_bytes(manifest)
    for skill in SKILLS:
        source_root = Path("plugins") / skill / "skills" / skill
        for source in tracked_files(root, source_root):
            destination = Path("skills") / skill / source.relative_to(source_root)
            files[destination.as_posix()] = read_source(root, source)
        if f"skills/{skill}/SKILL.md" not in files:
            raise ValueError(f"missing canonical skill: {skill}")
    files["LICENSE"] = read_source(root, Path("LICENSE"))
    return files


def verify_archive(archive: Path, expected: dict[str, bytes]) -> None:
    with zipfile.ZipFile(archive) as bundle:
        names = bundle.namelist()
        wanted = {f"nurok/{name}" for name in expected}
        if len(names) != len(set(names)) or set(names) != wanted:
            raise ValueError("archive inventory differs from canonical package")
        for name, contents in expected.items():
            if bundle.read(f"nurok/{name}") != contents:
                raise ValueError(f"archive bytes differ from source: {name}")


def build(root: Path, output: Path, version: str) -> Path:
    files = package_files(root, version)
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"nurok-{version}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for name, contents in sorted(files.items()):
            entry = zipfile.ZipInfo(f"nurok/{name}", date_time=(1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            bundle.writestr(entry, contents)
    verify_archive(archive, files)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix(".zip.sha256").write_text(
        f"{digest}  {archive.name}\n", encoding="utf-8"
    )
    provenance = {
        "version": version,
        "source_commit": git(root, "rev-parse", "HEAD"),
        "dirty": bool(git(root, "status", "--porcelain", "--untracked-files=no")),
        "archive_sha256": digest,
        "files": {
            name: hashlib.sha256(data).hexdigest()
            for name, data in sorted(files.items())
        },
    }
    archive.with_suffix(".build.json").write_bytes(json_bytes(provenance))
    return archive


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    try:
        archive = build(ROOT, args.output, args.version)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"ERROR: {error}\n")
    print(f"Verified plugin archive: {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
