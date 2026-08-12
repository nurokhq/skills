#!/usr/bin/env python3
"""Install and byte-compare canonical skills with distribution copies."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = ROOT / "plugins"


@dataclass(frozen=True)
class SkillPackage:
    plugin_name: str
    skill_name: str
    version: str
    canonical_root: Path


def discover_packages(plugin_root: Path = PLUGIN_ROOT) -> list[SkillPackage]:
    packages: list[SkillPackage] = []
    for root in sorted(plugin_root.iterdir()):
        if not root.is_dir() or root.name.startswith("."):
            continue
        manifest_path = root / ".codex-plugin" / "plugin.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        version = manifest["version"]
        skills_root = root / "skills"
        for skill_root in sorted(skills_root.iterdir()):
            if skill_root.is_dir() and not skill_root.name.startswith("."):
                packages.append(
                    SkillPackage(root.name, skill_root.name, version, skill_root)
                )
    return packages


def install_portable_skills(
    packages: Iterable[SkillPackage], destination_root: Path
) -> None:
    destination_root.mkdir(parents=True, exist_ok=True)
    for package in packages:
        destination = destination_root / package.skill_name
        if destination.exists() or destination.is_symlink():
            raise FileExistsError(f"installation target already exists: {destination}")
        shutil.copytree(package.canonical_root, destination, symlinks=True)


def tree_entries(root: Path) -> dict[Path, str]:
    entries: dict[Path, str] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if path.is_symlink():
            entries[relative] = "symlink"
        elif path.is_dir():
            entries[relative] = "directory"
        elif path.is_file():
            entries[relative] = "file"
        else:
            entries[relative] = "other"
    return entries


def compare_skill_trees(canonical_root: Path, installed_root: Path) -> list[str]:
    if not installed_root.is_dir():
        return [f"missing installed skill directory: {installed_root}"]

    canonical_entries = tree_entries(canonical_root)
    installed_entries = tree_entries(installed_root)
    errors: list[str] = []

    for relative in sorted(canonical_entries.keys() - installed_entries.keys()):
        errors.append(f"missing installed path: {installed_root / relative}")
    for relative in sorted(installed_entries.keys() - canonical_entries.keys()):
        errors.append(f"unexpected installed path: {installed_root / relative}")

    for relative in sorted(canonical_entries.keys() & installed_entries.keys()):
        canonical_kind = canonical_entries[relative]
        installed_kind = installed_entries[relative]
        if canonical_kind != installed_kind:
            errors.append(
                f"path type differs: {installed_root / relative} "
                f"({canonical_kind} != {installed_kind})"
            )
            continue
        canonical_path = canonical_root / relative
        installed_path = installed_root / relative
        if canonical_kind == "file":
            if canonical_path.read_bytes() != installed_path.read_bytes():
                errors.append(f"file bytes differ: {installed_path}")
        elif canonical_kind == "symlink":
            if os.readlink(canonical_path) != os.readlink(installed_path):
                errors.append(f"symlink target differs: {installed_path}")
        elif canonical_kind == "other":
            errors.append(f"unsupported installed path type: {installed_path}")
    return errors


def verify_portable_root(
    packages: Iterable[SkillPackage], installed_root: Path
) -> list[str]:
    errors: list[str] = []
    for package in packages:
        errors.extend(
            compare_skill_trees(
                package.canonical_root, installed_root / package.skill_name
            )
        )
    return errors


def verify_plugin_cache(
    packages: Iterable[SkillPackage], cache_root: Path
) -> list[str]:
    errors: list[str] = []
    for package in packages:
        installed_root = (
            cache_root
            / package.plugin_name
            / package.version
            / "skills"
            / package.skill_name
        )
        errors.extend(compare_skill_trees(package.canonical_root, installed_root))
    return errors


def verify_temporary_install(packages: list[SkillPackage]) -> list[str]:
    with tempfile.TemporaryDirectory(prefix="nurok-skills-") as directory:
        installed_root = Path(directory) / "skills"
        install_portable_skills(packages, installed_root)
        return verify_portable_root(packages, installed_root)


def validate_version_bumps(
    packages: Iterable[SkillPackage],
    changed_paths: Iterable[Path],
    base_versions: dict[str, str],
) -> list[str]:
    changed = set(changed_paths)
    errors: list[str] = []
    checked_plugins: set[str] = set()
    for package in packages:
        skill_root = (
            Path("plugins") / package.plugin_name / "skills" / package.skill_name
        )
        if not any(
            path == skill_root or path.is_relative_to(skill_root) for path in changed
        ):
            continue
        if package.plugin_name in checked_plugins:
            continue
        checked_plugins.add(package.plugin_name)
        base_version = base_versions.get(package.plugin_name)
        if base_version is None:
            continue
        current = tuple(int(part) for part in package.version.split("."))
        base = tuple(int(part) for part in base_version.split("."))
        if current <= base:
            errors.append(
                f"{package.plugin_name}: canonical skill changed but manifest "
                f"version {package.version} is not greater than {base_version}"
            )
    return errors


def verify_version_bumps(packages: Iterable[SkillPackage], base_ref: str) -> list[str]:
    try:
        changed_output = subprocess.run(
            [
                "git",
                "diff",
                "--name-only",
                "--diff-filter=ACDMRTUXB",
                f"{base_ref}...HEAD",
                "--",
                "plugins",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    except subprocess.CalledProcessError as error:
        return [
            f"could not compare plugin changes with {base_ref}: {error.stderr.strip()}"
        ]

    package_list = list(packages)
    base_versions: dict[str, str] = {}
    for plugin_name in sorted({package.plugin_name for package in package_list}):
        manifest_path = f"plugins/{plugin_name}/.codex-plugin/plugin.json"
        result = subprocess.run(
            ["git", "show", f"{base_ref}:{manifest_path}"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            continue
        try:
            base_versions[plugin_name] = json.loads(result.stdout)["version"]
        except (json.JSONDecodeError, KeyError, TypeError):
            return [f"could not read base manifest version: {manifest_path}"]

    changed_paths = [Path(line) for line in changed_output.splitlines() if line]
    return validate_version_bumps(package_list, changed_paths, base_versions)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skill",
        action="append",
        default=[],
        help="verify only this skill; repeat to select multiple installed skills",
    )
    parser.add_argument(
        "--base-ref",
        help="require a plugin version bump when its canonical skill changed",
    )
    parser.add_argument(
        "--portable-root",
        action="append",
        type=Path,
        default=[],
        help="compare canonical skills with <root>/<skill-name>",
    )
    parser.add_argument(
        "--plugin-cache-root",
        action="append",
        type=Path,
        default=[],
        help=("compare with <root>/<plugin>/<manifest-version>/skills/<skill-name>"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    packages = discover_packages()
    if args.skill:
        requested = set(args.skill)
        known = {package.skill_name for package in packages}
        unknown = sorted(requested - known)
        if unknown:
            for skill_name in unknown:
                print(f"ERROR: unknown skill: {skill_name}")
            return 2
        packages = [package for package in packages if package.skill_name in requested]
    errors = verify_temporary_install(packages)
    if args.base_ref:
        errors.extend(verify_version_bumps(packages, args.base_ref))
    for root in args.portable_root:
        errors.extend(verify_portable_root(packages, root.expanduser()))
    for root in args.plugin_cache_root:
        errors.extend(verify_plugin_cache(packages, root.expanduser()))

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"skill distribution verification failed with {len(errors)} error(s)")
        return 1
    print(f"skill distribution verification passed for {len(packages)} skill(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
