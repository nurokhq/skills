#!/usr/bin/env python3
"""Validate repository plugin and skill metadata."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = ROOT / "plugins"
MARKETPLACE_PATH = ROOT / ".agents" / "plugins" / "marketplace.json"
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def load_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{path.relative_to(ROOT)}: {error}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{path.relative_to(ROOT)}: expected a JSON object")
        return None
    return value


def load_skill_frontmatter(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        contents = path.read_text(encoding="utf-8")
    except OSError as error:
        errors.append(f"{path.relative_to(ROOT)}: {error}")
        return None
    parts = contents.split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        errors.append(f"{path.relative_to(ROOT)}: invalid YAML frontmatter")
        return None
    try:
        frontmatter = yaml.safe_load(parts[1])
    except yaml.YAMLError as error:
        errors.append(f"{path.relative_to(ROOT)}: {error}")
        return None
    if not isinstance(frontmatter, dict):
        errors.append(f"{path.relative_to(ROOT)}: frontmatter must be an object")
        return None
    if len(contents.splitlines()) > 500:
        errors.append(f"{path.relative_to(ROOT)}: SKILL.md exceeds 500 lines")
    return frontmatter


def validate_agent_yaml(skill_root: Path, skill_name: str, errors: list[str]) -> None:
    path = skill_root / "agents" / "openai.yaml"
    if not path.is_file():
        return
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        errors.append(f"{path.relative_to(ROOT)}: {error}")
        return
    interface = value.get("interface") if isinstance(value, dict) else None
    if not isinstance(interface, dict):
        errors.append(f"{path.relative_to(ROOT)}: interface must be an object")
        return
    short_description = interface.get("short_description")
    if not isinstance(short_description, str) or not 25 <= len(short_description) <= 64:
        errors.append(
            f"{path.relative_to(ROOT)}: short_description must be 25-64 characters"
        )
    default_prompt = interface.get("default_prompt")
    if not isinstance(default_prompt, str) or f"${skill_name}" not in default_prompt:
        errors.append(
            f"{path.relative_to(ROOT)}: default_prompt must mention ${skill_name}"
        )


def validate_skill(skill_root: Path, errors: list[str]) -> None:
    path = skill_root / "SKILL.md"
    if not path.is_file():
        errors.append(f"{skill_root.relative_to(ROOT)}: missing SKILL.md")
        return
    frontmatter = load_skill_frontmatter(path, errors)
    if frontmatter is None:
        return
    unknown_fields = sorted(set(frontmatter) - {"name", "description"})
    if unknown_fields:
        errors.append(f"{path.relative_to(ROOT)}: unsupported fields {unknown_fields}")
    name = frontmatter.get("name")
    if (
        name != skill_root.name
        or not isinstance(name, str)
        or not NAME_PATTERN.fullmatch(name)
    ):
        errors.append(f"{path.relative_to(ROOT)}: name must match the skill directory")
        return
    description = frontmatter.get("description")
    if not isinstance(description, str) or not 1 <= len(description) <= 1024:
        errors.append(
            f"{path.relative_to(ROOT)}: description must be 1-1024 characters"
        )
    validate_agent_yaml(skill_root, name, errors)
    if any((skill_root / "scripts").glob("test_*.py")):
        errors.append(
            f"{skill_root.relative_to(ROOT)}: keep tests under repository tests/"
        )


def validate_plugin(plugin_root: Path, errors: list[str]) -> None:
    path = plugin_root / ".codex-plugin" / "plugin.json"
    manifest = load_json(path, errors)
    if manifest is None:
        return
    if manifest.get("name") != plugin_root.name:
        errors.append(f"{path.relative_to(ROOT)}: name must match the plugin directory")
    version = manifest.get("version")
    if not isinstance(version, str) or not SEMVER_PATTERN.fullmatch(version):
        errors.append(f"{path.relative_to(ROOT)}: version must be strict semver")
    description = manifest.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append(f"{path.relative_to(ROOT)}: missing description")
    author = manifest.get("author")
    if (
        not isinstance(author, dict)
        or not isinstance(author.get("name"), str)
        or not author["name"].strip()
    ):
        errors.append(f"{path.relative_to(ROOT)}: invalid author")
    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        errors.append(f"{path.relative_to(ROOT)}: invalid interface")
        return
    for field in (
        "displayName",
        "shortDescription",
        "longDescription",
        "developerName",
        "category",
    ):
        if not isinstance(interface.get(field), str) or not interface[field].strip():
            errors.append(f"{path.relative_to(ROOT)}: invalid interface.{field}")
    if manifest.get("skills") != "./skills/":
        errors.append(f"{path.relative_to(ROOT)}: skills must be ./skills/")
    capabilities = interface.get("capabilities")
    if not isinstance(capabilities, list) or not all(
        isinstance(capability, str) and capability for capability in capabilities
    ):
        errors.append(f"{path.relative_to(ROOT)}: invalid interface.capabilities")
    prompts = interface.get("defaultPrompt")
    if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3:
        errors.append(
            f"{path.relative_to(ROOT)}: defaultPrompt must contain 1-3 prompts"
        )
    elif any(
        not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 128
        for prompt in prompts
    ):
        errors.append(f"{path.relative_to(ROOT)}: invalid defaultPrompt entry")
    skills_root = plugin_root / "skills"
    for skill_root in sorted(skills_root.iterdir() if skills_root.is_dir() else []):
        if skill_root.is_dir() and not skill_root.name.startswith("."):
            validate_skill(skill_root, errors)


def validate_marketplace(errors: list[str]) -> None:
    marketplace = load_json(MARKETPLACE_PATH, errors)
    if marketplace is None:
        return
    if marketplace.get("name") != "nurok":
        errors.append(f"{MARKETPLACE_PATH.relative_to(ROOT)}: name must be nurok")
    entries = marketplace.get("plugins")
    if not isinstance(entries, list) or not entries:
        errors.append(
            f"{MARKETPLACE_PATH.relative_to(ROOT)}: plugins must be non-empty"
        )
        return
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append(f"{MARKETPLACE_PATH.relative_to(ROOT)}: invalid plugin entry")
            continue
        name = entry.get("name")
        source = entry.get("source")
        policy = entry.get("policy")
        source_path = source.get("path") if isinstance(source, dict) else None
        candidate = (
            (ROOT / source_path).resolve() if isinstance(source_path, str) else None
        )
        if (
            not isinstance(name, str)
            or not isinstance(source, dict)
            or source.get("source") != "local"
            or source_path != f"./plugins/{name}"
            or candidate is None
            or not candidate.is_relative_to(ROOT.resolve())
            or not candidate.is_dir()
            or candidate.name != name
        ):
            errors.append(
                f"{MARKETPLACE_PATH.relative_to(ROOT)}: invalid plugin source"
            )
        if not isinstance(policy, dict) or policy.get("installation") not in {
            "AVAILABLE",
            "INSTALLED_BY_DEFAULT",
            "NOT_AVAILABLE",
        }:
            errors.append(
                f"{MARKETPLACE_PATH.relative_to(ROOT)}: invalid install policy"
            )
        if not isinstance(policy, dict) or policy.get("authentication") not in {
            "ON_INSTALL",
            "ON_USE",
        }:
            errors.append(f"{MARKETPLACE_PATH.relative_to(ROOT)}: invalid auth policy")
        if not isinstance(entry.get("category"), str) or not entry["category"].strip():
            errors.append(f"{MARKETPLACE_PATH.relative_to(ROOT)}: invalid category")


def main() -> int:
    errors: list[str] = []
    for plugin_root in sorted(PLUGIN_ROOT.iterdir() if PLUGIN_ROOT.is_dir() else []):
        if plugin_root.is_dir() and not plugin_root.name.startswith("."):
            validate_plugin(plugin_root, errors)
    validate_marketplace(errors)
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"repository validation failed with {len(errors)} error(s)")
        return 1
    print("repository validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
