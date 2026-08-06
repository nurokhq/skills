#!/usr/bin/env python3
"""Audit Nurok-specific OpenAKB working-copy invariants before push."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

SOURCE_ID_PATTERN = re.compile(r"^SRC-[0-9A-Z]{6}$", re.ASCII | re.IGNORECASE)
SECTION_ID_PATTERN = re.compile(r"^SEC-[0-9A-Z]{6}$", re.ASCII | re.IGNORECASE)
SOURCE_TYPES = {"feed", "file", "firsthand", "redacted", "url"}


def find_descriptor(value: Path) -> Path:
    return value / "openakb.json" if value.is_dir() else value


def resolve_local_uri(root: Path, value: str) -> Path | None:
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc:
        return None
    if value.startswith("/"):
        raise ValueError("local URI must not be absolute")
    if not parsed.path or parsed.query or parsed.fragment or "\\" in parsed.path:
        raise ValueError("local URI must be a canonical relative path")

    raw_parts = parsed.path.split("/")
    if any(part in {"", ".", ".."} for part in raw_parts):
        raise ValueError(
            "local URI must not contain empty, current, or parent segments"
        )
    relative_path = PurePosixPath(*raw_parts)

    resolved_root = root.resolve()
    resolved_path = (resolved_root / Path(*relative_path.parts)).resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as error:
        raise ValueError("local URI resolves outside the working-copy root") from error
    return resolved_path


def has_complete_stamps(
    value: dict[str, object], hash_key: str, length_key: str
) -> bool:
    content_hash = value.get(hash_key)
    content_length = value.get(length_key)
    return (
        isinstance(content_hash, str)
        and bool(content_hash)
        and isinstance(content_length, int)
        and not isinstance(content_length, bool)
        and content_length >= 0
    )


def audit_local_reference(
    *,
    root: Path,
    value: dict[str, object],
    uri_key: str,
    hash_key: str,
    length_key: str,
    pointer: str,
    errors: list[str],
    warnings: list[str],
) -> None:
    uri = value.get(uri_key)
    if not isinstance(uri, str):
        return
    try:
        local_path = resolve_local_uri(root, uri)
    except ValueError as error:
        errors.append(f"{pointer}: {error}")
        return
    if local_path is None:
        return
    if local_path.is_file():
        return
    if has_complete_stamps(value, hash_key, length_key):
        warnings.append(
            f"{pointer}: {uri!r} is stamps-only; restore it unless the target "
            "or base snapshot already has the blob"
        )
        return
    errors.append(
        f"{pointer}: local file {uri!r} is missing without complete "
        f"{hash_key}/{length_key} stamps"
    )


def audit(descriptor_path: Path) -> tuple[list[str], list[str], dict[str, object]]:
    descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
    if not isinstance(descriptor, dict):
        return ["/: descriptor must be an object"], [], {}
    root = descriptor_path.parent
    sources = descriptor.get("sources", [])
    sections = descriptor.get("sections", [])
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(sources, list):
        return ["/sources must be an array"], warnings, {}
    if not isinstance(sections, list):
        return ["/sections must be an array"], warnings, {}

    entities: dict[str, str] = {}
    natural_keys: dict[tuple[str, str], list[str]] = defaultdict(list)
    source_ids: set[str] = set()

    for index, source in enumerate(sources):
        pointer = f"/sources/{index}"
        if not isinstance(source, dict):
            errors.append(f"{pointer}: source must be an object")
            continue

        source_id = source.get("id")
        if not isinstance(source_id, str) or not SOURCE_ID_PATTERN.fullmatch(source_id):
            errors.append(
                f"{pointer}/id: expected Source ID 'SRC-' plus 6 ASCII base36 "
                "characters"
            )
            continue
        normalized_source_id = source_id.lower()
        if normalized_source_id in entities:
            errors.append(
                f"{pointer}/id: duplicate shared ID {source_id!r}; "
                f"first used by {entities[normalized_source_id]}"
            )
        else:
            entities[normalized_source_id] = pointer
        source_ids.add(normalized_source_id)

        source_type = source.get("type")
        if source_type not in SOURCE_TYPES:
            errors.append(
                f"{pointer}/type: unsupported Nurok source type {source_type!r}"
            )
        if source_type != "redacted" and not source.get("captured_at"):
            errors.append(f"{pointer}/captured_at: required for non-redacted sources")

        uri = source.get("uri")
        if isinstance(source_type, str) and isinstance(uri, str):
            natural_keys[(source_type, uri)].append(source_id)
        if source_type == "file":
            audit_local_reference(
                root=root,
                value=source,
                uri_key="uri",
                hash_key="content_hash",
                length_key="content_length",
                pointer=f"{pointer}/uri",
                errors=errors,
                warnings=warnings,
            )
        audit_local_reference(
            root=root,
            value=source,
            uri_key="capture_uri",
            hash_key="content_hash",
            length_key="content_length",
            pointer=f"{pointer}/capture_uri",
            errors=errors,
            warnings=warnings,
        )

    for (source_type, uri), ids in natural_keys.items():
        if len(ids) > 1:
            errors.append(
                f"duplicate source natural key type={source_type!r}, uri={uri!r}: "
                f"{', '.join(ids)}"
            )

    content_count = 0
    for index, section in enumerate(sections):
        pointer = f"/sections/{index}"
        if not isinstance(section, dict):
            errors.append(f"{pointer}: section must be an object")
            continue

        section_id = section.get("id")
        if not isinstance(section_id, str) or not SECTION_ID_PATTERN.fullmatch(
            section_id
        ):
            errors.append(
                f"{pointer}/id: expected Section ID 'SEC-' plus 6 ASCII base36 "
                "characters"
            )
            continue
        normalized_section_id = section_id.lower()
        if normalized_section_id in entities:
            errors.append(
                f"{pointer}/id: duplicate shared ID {section_id!r}; "
                f"first used by {entities[normalized_section_id]}"
            )
        else:
            entities[normalized_section_id] = pointer

        audit_local_reference(
            root=root,
            value=section,
            uri_key="provenance_uri",
            hash_key="provenance_hash",
            length_key="provenance_length",
            pointer=f"{pointer}/provenance_uri",
            errors=errors,
            warnings=warnings,
        )

        content_uri = section.get("content_uri")
        cited = section.get("source_ids")
        if isinstance(content_uri, str) and (not isinstance(cited, list) or not cited):
            errors.append(f"{pointer}/source_ids: content section must cite a source")
        if cited is not None and not isinstance(cited, list):
            if not isinstance(content_uri, str):
                errors.append(f"{pointer}/source_ids: expected an array")
        elif isinstance(cited, list):
            normalized_citations: set[str] = set()
            for cited_id in cited:
                if not isinstance(cited_id, str) or not SOURCE_ID_PATTERN.fullmatch(
                    cited_id
                ):
                    errors.append(
                        f"{pointer}/source_ids: expected Source ID 'SRC-' plus 6 "
                        f"ASCII base36 characters, got {cited_id!r}"
                    )
                    continue
                normalized_cited_id = cited_id.lower()
                if normalized_cited_id in normalized_citations:
                    errors.append(
                        f"{pointer}/source_ids: duplicate source ID {cited_id!r} "
                        "under case-insensitive comparison"
                    )
                else:
                    normalized_citations.add(normalized_cited_id)
                if normalized_cited_id not in source_ids:
                    errors.append(
                        f"{pointer}/source_ids: unresolved source ID {cited_id!r}"
                    )

        if not isinstance(content_uri, str):
            continue
        content_count += 1

        content_type = section.get("content_type", "text/markdown")
        if content_type == "text/markdown":
            expected = f"sections/{section_id}/content.md"
            if content_uri != expected:
                errors.append(
                    f"{pointer}/content_uri: expected canonical path {expected!r}, "
                    f"got {content_uri!r}"
                )

        audit_local_reference(
            root=root,
            value=section,
            uri_key="content_uri",
            hash_key="content_hash",
            length_key="content_length",
            pointer=f"{pointer}/content_uri",
            errors=errors,
            warnings=warnings,
        )

    audit_local_reference(
        root=root,
        value=descriptor,
        uri_key="guide_uri",
        hash_key="guide_hash",
        length_key="guide_length",
        pointer="/guide_uri",
        errors=errors,
        warnings=warnings,
    )

    extensions = descriptor.get("x")
    nurok = extensions.get("ai.nurok") if isinstance(extensions, dict) else None
    if isinstance(nurok, dict):
        audit_local_reference(
            root=root,
            value=nurok,
            uri_key="skill_uri",
            hash_key="skill_hash",
            length_key="skill_length",
            pointer="/x/ai.nurok/skill_uri",
            errors=errors,
            warnings=warnings,
        )

    summary = {
        "descriptor": str(descriptor_path),
        "identity": "/".join(
            part
            for part in (descriptor.get("namespace"), descriptor.get("id"))
            if isinstance(part, str) and part
        ),
        "sources": len(sources),
        "sections": len(sections),
        "content_sections": content_count,
    }
    return errors, warnings, summary


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit Nurok-specific OpenAKB working-copy invariants"
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path("."),
        help="Working-copy directory or openakb.json path",
    )
    args = parser.parse_args()
    descriptor_path = find_descriptor(args.dir)

    try:
        errors, warnings, summary = audit(descriptor_path)
    except (OSError, json.JSONDecodeError) as error:
        print(f"ERROR: cannot load {descriptor_path}: {error}", file=sys.stderr)
        return 1

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    print(f"audit: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
