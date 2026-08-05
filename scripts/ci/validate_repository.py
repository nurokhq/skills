#!/usr/bin/env python3
"""Validate repository plugin, marketplace, and portable skill metadata."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = ROOT / "plugins"
CODEX_MARKETPLACE_PATH = ROOT / ".agents" / "plugins" / "marketplace.json"
CLAUDE_MARKETPLACE_PATH = ROOT / ".claude-plugin" / "marketplace.json"
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
NUROK_KB_COMMAND_PATTERN = re.compile(r"\bnurok\s+kb\s+([a-z]+)(?:\s+([a-z]+))?")
LOCAL_OUTPUT_PATTERN = re.compile(r"(?<![\w-])--out(?:\s|=|`)")
EXPECTED_PLUGIN_SKILLS = {
    "nurok-kb": {"nurok-kb"},
    "nurok-kb-capture": {"nurok-kb-capture"},
    "nurok-kb-manage": {"nurok-kb-manage"},
}
KNOWN_SKILL_NAMES = frozenset(
    skill_name
    for skill_names in EXPECTED_PLUGIN_SKILLS.values()
    for skill_name in skill_names
)
HOST_SKILL_MENTION_PATTERN = re.compile(
    r"(?<![\w-])\$("
    + "|".join(re.escape(name) for name in sorted(KNOWN_SKILL_NAMES, reverse=True))
    + r")(?![\w-])"
)
READ_ONLY_COMMANDS = {
    ("cat", None),
    ("changelog", None),
    ("list", None),
    ("search", None),
    ("section", "get"),
    ("section", "list"),
    ("show", None),
}


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{relative(path)}: {error}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{relative(path)}: expected a JSON object")
        return None
    return value


def load_skill_frontmatter(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        contents = path.read_text(encoding="utf-8")
    except OSError as error:
        errors.append(f"{relative(path)}: {error}")
        return None
    parts = contents.split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        errors.append(f"{relative(path)}: invalid YAML frontmatter")
        return None
    try:
        frontmatter = yaml.safe_load(parts[1])
    except yaml.YAMLError as error:
        errors.append(f"{relative(path)}: {error}")
        return None
    if not isinstance(frontmatter, dict):
        errors.append(f"{relative(path)}: frontmatter must be an object")
        return None
    if len(contents.splitlines()) > 500:
        errors.append(f"{relative(path)}: SKILL.md exceeds 500 lines")
    return frontmatter


def validate_agent_yaml(skill_root: Path, skill_name: str, errors: list[str]) -> None:
    path = skill_root / "agents" / "openai.yaml"
    if not path.is_file():
        return
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        errors.append(f"{relative(path)}: {error}")
        return
    interface = value.get("interface") if isinstance(value, dict) else None
    if not isinstance(interface, dict):
        errors.append(f"{relative(path)}: interface must be an object")
        return
    short_description = interface.get("short_description")
    if not isinstance(short_description, str) or not 25 <= len(short_description) <= 64:
        errors.append(f"{relative(path)}: short_description must be 25-64 characters")
    default_prompt = interface.get("default_prompt")
    if not isinstance(default_prompt, str) or f"${skill_name}" not in default_prompt:
        errors.append(f"{relative(path)}: default_prompt must mention ${skill_name}")


def validate_skill_links(skill_root: Path, errors: list[str]) -> None:
    resolved_root = skill_root.resolve()
    for path in sorted(skill_root.rglob("*")):
        if path.is_symlink():
            errors.append(f"{relative(path)}: skill packages must not contain symlinks")
        if not path.is_file() or path.suffix.lower() != ".md":
            continue
        try:
            contents = path.read_text(encoding="utf-8")
        except OSError as error:
            errors.append(f"{relative(path)}: {error}")
            continue
        for raw_target in MARKDOWN_LINK_PATTERN.findall(contents):
            target = raw_target.split(maxsplit=1)[0]
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            candidate = (path.parent / unquote(parsed.path)).resolve()
            if not candidate.is_relative_to(resolved_root):
                errors.append(
                    f"{relative(path)}: link escapes the skill root: {target}"
                )
            elif not candidate.exists():
                errors.append(f"{relative(path)}: broken relative link: {target}")


def validate_portable_skill_markdown(skill_root: Path, errors: list[str]) -> None:
    paths = [skill_root / "SKILL.md", *sorted((skill_root / "references").glob("*.md"))]
    for path in paths:
        if not path.is_file():
            continue
        try:
            contents = path.read_text(encoding="utf-8")
        except OSError as error:
            errors.append(f"{relative(path)}: {error}")
            continue
        for match in HOST_SKILL_MENTION_PATTERN.finditer(contents):
            errors.append(
                f"{relative(path)}: canonical skill instructions use host-specific "
                f"mention ${match.group(1)}"
            )


def validate_read_only_skill(skill_root: Path, errors: list[str]) -> None:
    for path in sorted(skill_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {
            ".md",
            ".py",
            ".sh",
            ".yaml",
            ".yml",
        }:
            continue
        try:
            contents = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            errors.append(f"{relative(path)}: {error}")
            continue
        for match in NUROK_KB_COMMAND_PATTERN.finditer(contents):
            command = (
                match.group(1).lower(),
                match.group(2).lower() if match.group(2) else None,
            )
            if command not in READ_ONLY_COMMANDS:
                rendered = " ".join(part for part in command if part)
                errors.append(
                    f"{relative(path)}: read-only skill uses disallowed "
                    f"nurok kb {rendered}"
                )
        if LOCAL_OUTPUT_PATTERN.search(contents):
            errors.append(
                f"{relative(path)}: read-only skills must default artifact "
                "reads to stdout"
            )


def validate_skill(
    skill_root: Path,
    plugin_name: str,
    skill_owners: dict[str, Path],
    errors: list[str],
) -> None:
    path = skill_root / "SKILL.md"
    if not path.is_file():
        errors.append(f"{relative(skill_root)}: missing SKILL.md")
        return
    frontmatter = load_skill_frontmatter(path, errors)
    if frontmatter is None:
        return
    unknown_fields = sorted(set(frontmatter) - {"name", "description"})
    if unknown_fields:
        errors.append(f"{relative(path)}: unsupported fields {unknown_fields}")
    name = frontmatter.get("name")
    if (
        name != skill_root.name
        or not isinstance(name, str)
        or not NAME_PATTERN.fullmatch(name)
    ):
        errors.append(f"{relative(path)}: name must match the skill directory")
        return
    previous_owner = skill_owners.get(name)
    if previous_owner is not None:
        errors.append(
            f"{relative(path)}: duplicate skill name; first owned by "
            f"{relative(previous_owner)}"
        )
    else:
        skill_owners[name] = skill_root
    description = frontmatter.get("description")
    if not isinstance(description, str) or not 1 <= len(description) <= 1024:
        errors.append(f"{relative(path)}: description must be 1-1024 characters")
    validate_agent_yaml(skill_root, name, errors)
    validate_skill_links(skill_root, errors)
    validate_portable_skill_markdown(skill_root, errors)
    if any((skill_root / "scripts").glob("test_*.py")):
        errors.append(f"{relative(skill_root)}: keep tests under repository tests/")
    if plugin_name == "nurok-kb":
        validate_read_only_skill(skill_root, errors)


def validate_codex_manifest(
    plugin_root: Path, errors: list[str]
) -> dict[str, Any] | None:
    path = plugin_root / ".codex-plugin" / "plugin.json"
    manifest = load_json(path, errors)
    if manifest is None:
        return None
    if manifest.get("name") != plugin_root.name:
        errors.append(f"{relative(path)}: name must match the plugin directory")
    version = manifest.get("version")
    if not isinstance(version, str) or not SEMVER_PATTERN.fullmatch(version):
        errors.append(f"{relative(path)}: version must be strict semver")
    description = manifest.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append(f"{relative(path)}: missing description")
    author = manifest.get("author")
    if (
        not isinstance(author, dict)
        or author.get("name") != "Nurok"
        or author.get("email") != "support@nurok.ai"
    ):
        errors.append(f"{relative(path)}: invalid Nurok author metadata")
    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        errors.append(f"{relative(path)}: invalid interface")
        return manifest
    for field in (
        "displayName",
        "shortDescription",
        "longDescription",
        "developerName",
        "category",
    ):
        if not isinstance(interface.get(field), str) or not interface[field].strip():
            errors.append(f"{relative(path)}: invalid interface.{field}")
    if manifest.get("skills") != "./skills/":
        errors.append(f"{relative(path)}: skills must be ./skills/")
    capabilities = interface.get("capabilities")
    if not isinstance(capabilities, list) or not all(
        isinstance(capability, str) and capability for capability in capabilities
    ):
        errors.append(f"{relative(path)}: invalid interface.capabilities")
    prompts = interface.get("defaultPrompt")
    if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3:
        errors.append(f"{relative(path)}: defaultPrompt must contain 1-3 prompts")
    elif any(
        not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 128
        for prompt in prompts
    ):
        errors.append(f"{relative(path)}: invalid defaultPrompt entry")
    return manifest


def validate_claude_manifest(
    plugin_root: Path, codex_manifest: dict[str, Any] | None, errors: list[str]
) -> None:
    path = plugin_root / ".claude-plugin" / "plugin.json"
    manifest = load_json(path, errors)
    if manifest is None:
        return
    if manifest.get("name") != plugin_root.name:
        errors.append(f"{relative(path)}: name must match the plugin directory")
    version = manifest.get("version")
    if not isinstance(version, str) or not SEMVER_PATTERN.fullmatch(version):
        errors.append(f"{relative(path)}: version must be strict semver")
    if codex_manifest is not None and version != codex_manifest.get("version"):
        errors.append(f"{relative(path)}: version must match the Codex manifest")
    if (
        not isinstance(manifest.get("description"), str)
        or not manifest["description"].strip()
    ):
        errors.append(f"{relative(path)}: missing description")
    author = manifest.get("author")
    if (
        not isinstance(author, dict)
        or author.get("name") != "Nurok"
        or author.get("email") != "support@nurok.ai"
    ):
        errors.append(f"{relative(path)}: invalid Nurok author metadata")


def validate_management_guardrails(plugin_root: Path, errors: list[str]) -> None:
    skill_root = plugin_root / "skills" / "nurok-kb-manage"
    paths = [skill_root / "SKILL.md", *sorted((skill_root / "references").glob("*.md"))]
    try:
        contents = "\n".join(path.read_text(encoding="utf-8") for path in paths).lower()
    except OSError as error:
        errors.append(f"{relative(skill_root)}: {error}")
        return
    for term in ("authority", "endpoint", "identity", "visibility", "target"):
        if term not in contents:
            errors.append(f"{relative(skill_root)}: missing {term} guardrail")
    if "--no-create" not in contents:
        errors.append(
            f"{relative(skill_root)}: missing existing-KB --no-create guardrail"
        )


def validate_plugin(
    plugin_root: Path, skill_owners: dict[str, Path], errors: list[str]
) -> None:
    codex_manifest = validate_codex_manifest(plugin_root, errors)
    validate_claude_manifest(plugin_root, codex_manifest, errors)
    skills_root = plugin_root / "skills"
    skill_names = (
        {
            path.name
            for path in skills_root.iterdir()
            if path.is_dir() and not path.name.startswith(".")
        }
        if skills_root.is_dir()
        else set()
    )
    expected = EXPECTED_PLUGIN_SKILLS.get(plugin_root.name, set())
    if skill_names != expected:
        errors.append(
            f"{relative(skills_root)}: expected skills {sorted(expected)}, "
            f"got {sorted(skill_names)}"
        )
    for skill_name in sorted(skill_names):
        validate_skill(skills_root / skill_name, plugin_root.name, skill_owners, errors)
    if plugin_root.name == "nurok-kb-manage":
        validate_management_guardrails(plugin_root, errors)


def validate_codex_marketplace(plugin_names: set[str], errors: list[str]) -> None:
    marketplace = load_json(CODEX_MARKETPLACE_PATH, errors)
    if marketplace is None:
        return
    if marketplace.get("name") != "nurok":
        errors.append(f"{relative(CODEX_MARKETPLACE_PATH)}: name must be nurok")
    interface = marketplace.get("interface")
    if not isinstance(interface, dict) or interface.get("displayName") != "Nurok":
        errors.append(f"{relative(CODEX_MARKETPLACE_PATH)}: invalid interface")
    entries = marketplace.get("plugins")
    if not isinstance(entries, list) or not entries:
        errors.append(f"{relative(CODEX_MARKETPLACE_PATH)}: plugins must be non-empty")
        return
    entry_names: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append(f"{relative(CODEX_MARKETPLACE_PATH)}: invalid plugin entry")
            continue
        name = entry.get("name")
        if not isinstance(name, str) or name in entry_names:
            errors.append(
                f"{relative(CODEX_MARKETPLACE_PATH)}: duplicate or invalid plugin name"
            )
            continue
        entry_names.add(name)
        source = entry.get("source")
        policy = entry.get("policy")
        source_path = source.get("path") if isinstance(source, dict) else None
        candidate = (
            (ROOT / source_path).resolve() if isinstance(source_path, str) else None
        )
        if (
            not isinstance(source, dict)
            or source.get("source") != "local"
            or source_path != f"./plugins/{name}"
            or candidate is None
            or not candidate.is_relative_to(ROOT.resolve())
            or not candidate.is_dir()
            or candidate.name != name
        ):
            errors.append(
                f"{relative(CODEX_MARKETPLACE_PATH)}: invalid source for {name}"
            )
        if not isinstance(policy, dict) or policy.get("installation") not in {
            "AVAILABLE",
            "INSTALLED_BY_DEFAULT",
            "NOT_AVAILABLE",
        }:
            errors.append(
                f"{relative(CODEX_MARKETPLACE_PATH)}: invalid install policy for {name}"
            )
        if not isinstance(policy, dict) or policy.get("authentication") not in {
            "ON_INSTALL",
            "ON_USE",
        }:
            errors.append(
                f"{relative(CODEX_MARKETPLACE_PATH)}: invalid auth policy for {name}"
            )
        if not isinstance(entry.get("category"), str) or not entry["category"].strip():
            errors.append(
                f"{relative(CODEX_MARKETPLACE_PATH)}: invalid category for {name}"
            )
    if entry_names != plugin_names:
        errors.append(
            f"{relative(CODEX_MARKETPLACE_PATH)}: expected plugins "
            f"{sorted(plugin_names)}, got {sorted(entry_names)}"
        )


def validate_claude_marketplace(plugin_names: set[str], errors: list[str]) -> None:
    marketplace = load_json(CLAUDE_MARKETPLACE_PATH, errors)
    if marketplace is None:
        return
    if marketplace.get("name") != "nurok":
        errors.append(f"{relative(CLAUDE_MARKETPLACE_PATH)}: name must be nurok")
    owner = marketplace.get("owner")
    if (
        not isinstance(owner, dict)
        or owner.get("name") != "Nurok"
        or owner.get("email") != "support@nurok.ai"
    ):
        errors.append(f"{relative(CLAUDE_MARKETPLACE_PATH)}: invalid owner metadata")
    entries = marketplace.get("plugins")
    if not isinstance(entries, list) or not entries:
        errors.append(f"{relative(CLAUDE_MARKETPLACE_PATH)}: plugins must be non-empty")
        return
    entry_names: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append(f"{relative(CLAUDE_MARKETPLACE_PATH)}: invalid plugin entry")
            continue
        name = entry.get("name")
        source = entry.get("source")
        candidate = (ROOT / source).resolve() if isinstance(source, str) else None
        if not isinstance(name, str) or name in entry_names:
            errors.append(
                f"{relative(CLAUDE_MARKETPLACE_PATH)}: duplicate or invalid plugin name"
            )
            continue
        entry_names.add(name)
        if (
            source != f"./plugins/{name}"
            or candidate is None
            or not candidate.is_relative_to(ROOT.resolve())
            or not candidate.is_dir()
            or not (candidate / ".claude-plugin" / "plugin.json").is_file()
        ):
            errors.append(
                f"{relative(CLAUDE_MARKETPLACE_PATH)}: invalid source for {name}"
            )
        expected_skills = [f"./skills/{name}"]
        if entry.get("skills") != expected_skills:
            errors.append(
                f"{relative(CLAUDE_MARKETPLACE_PATH)}: expected skills "
                f"{expected_skills} for {name}"
            )
    if entry_names != plugin_names:
        errors.append(
            f"{relative(CLAUDE_MARKETPLACE_PATH)}: expected plugins "
            f"{sorted(plugin_names)}, got {sorted(entry_names)}"
        )


def main() -> int:
    errors: list[str] = []
    plugin_roots = (
        {
            path.name: path
            for path in PLUGIN_ROOT.iterdir()
            if path.is_dir() and not path.name.startswith(".")
        }
        if PLUGIN_ROOT.is_dir()
        else {}
    )
    expected_plugins = set(EXPECTED_PLUGIN_SKILLS)
    plugin_names = set(plugin_roots)
    if plugin_names != expected_plugins:
        errors.append(
            f"plugins: expected {sorted(expected_plugins)}, got {sorted(plugin_names)}"
        )
    skill_owners: dict[str, Path] = {}
    for plugin_name in sorted(plugin_roots):
        validate_plugin(plugin_roots[plugin_name], skill_owners, errors)
    validate_codex_marketplace(plugin_names, errors)
    validate_claude_marketplace(plugin_names, errors)
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"repository validation failed with {len(errors)} error(s)")
        return 1
    print("repository validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
