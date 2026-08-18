#!/usr/bin/env python3
"""Audit deterministic Nurok OpenAKB working-copy invariants before push."""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any
from urllib.parse import urlsplit

SOURCE_ID_PATTERN = re.compile(r"^SRC-[0-9A-Z]{6}$", re.ASCII | re.IGNORECASE)
SECTION_ID_PATTERN = re.compile(r"^SEC-[0-9A-Z]{6}$", re.ASCII | re.IGNORECASE)
SOURCE_BLOCK_PATTERN = re.compile(
    r"<!--\s*source-block:\s*(SRC-[0-9A-Z]{6})\s*-->",
    re.ASCII | re.IGNORECASE,
)
CITATION_PATTERN = re.compile(
    r"\[cite:\s*(SRC-[0-9A-Z]{6})\s*\]", re.ASCII | re.IGNORECASE
)
SOURCE_BLOCK_PAIR_PATTERN = re.compile(
    r"<!--\s*source-block:\s*(SRC-[0-9A-Z]{6})\s*-->"
    r"[ \t]*(?:\r?\n)[ \t]*"
    r"\[cite:\s*\1\s*\]",
    re.ASCII | re.IGNORECASE,
)
SOURCE_TYPES = {"feed", "file", "firsthand", "redacted", "url"}


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    pointer: str
    message: str
    expected: Any | None = None
    actual: Any | None = None

    def render(self) -> str:
        details = []
        if self.expected is not None:
            details.append(f"expected {self.expected!r}")
        if self.actual is not None:
            details.append(f"actual {self.actual!r}")
        suffix = f" ({', '.join(details)})" if details else ""
        return f"{self.pointer}: {self.message}{suffix}"


def add_finding(
    findings: list[Finding],
    code: str,
    severity: str,
    pointer: str,
    message: str,
    *,
    expected: Any | None = None,
    actual: Any | None = None,
) -> None:
    findings.append(
        Finding(code, severity, pointer, message, expected=expected, actual=actual)
    )


def find_descriptor(value: Path) -> Path:
    return value / "openakb.json" if value.is_dir() else value


def resolve_local_uri(root: Path, value: str) -> Path | None:
    parsed = urlsplit(value)
    windows_path = PureWindowsPath(value)
    if parsed.scheme.lower() == "file" or value.startswith("/") or windows_path.drive:
        raise ValueError("local URI must not use an absolute filesystem form")
    if parsed.scheme or parsed.netloc:
        return None
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


def complete_stamps(
    value: dict[str, object], hash_key: str, length_key: str
) -> tuple[str, int] | None:
    content_hash = value.get(hash_key)
    content_length = value.get(length_key)
    if (
        valid_sha256_stamp(content_hash)
        and isinstance(content_length, int)
        and not isinstance(content_length, bool)
        and content_length >= 0
    ):
        return content_hash, content_length
    return None


def valid_sha256_stamp(value: object) -> bool:
    if not isinstance(value, str) or not value.startswith("sha256-"):
        return False
    try:
        digest = base64.b64decode(value.removeprefix("sha256-"), validate=True)
    except (ValueError, binascii.Error):
        return False
    return len(digest) == hashlib.sha256().digest_size


def sha256_stamp(contents: bytes) -> str:
    digest = base64.b64encode(hashlib.sha256(contents).digest()).decode("ascii")
    return f"sha256-{digest}"


def iter_local_uri_values(descriptor: dict[str, object]) -> list[str]:
    values = []
    guide_uri = descriptor.get("guide_uri")
    if isinstance(guide_uri, str):
        values.append(guide_uri)

    sources = descriptor.get("sources")
    if isinstance(sources, list):
        for source in sources:
            if not isinstance(source, dict):
                continue
            if source.get("type") == "file" and isinstance(source.get("uri"), str):
                values.append(source["uri"])
            capture_uri = source.get("capture_uri")
            if isinstance(capture_uri, str):
                values.append(capture_uri)

    sections = descriptor.get("sections")
    if isinstance(sections, list):
        for section in sections:
            if not isinstance(section, dict):
                continue
            for key in ("content_uri", "provenance_uri"):
                uri = section.get(key)
                if isinstance(uri, str):
                    values.append(uri)

    extensions = descriptor.get("x")
    nurok = extensions.get("ai.nurok") if isinstance(extensions, dict) else None
    if isinstance(nurok, dict) and isinstance(nurok.get("skill_uri"), str):
        values.append(nurok["skill_uri"])
    return values


def descriptor_projection(
    descriptor_path: Path, descriptor: dict[str, object]
) -> dict[str, Path] | None:
    projection = {"openakb.json": descriptor_path}
    root = descriptor_path.parent
    for uri in iter_local_uri_values(descriptor):
        try:
            path = resolve_local_uri(root, uri)
        except ValueError:
            return None
        if path is None:
            continue
        if not path.is_file():
            return None
        projection[uri] = path
    return projection


def aggregate_projection_digest(projection: dict[str, Path]) -> str:
    aggregate = hashlib.sha256()
    for relative, path in sorted(projection.items()):
        relative_bytes = relative.encode("utf-8")
        contents = path.read_bytes()
        aggregate.update(len(relative_bytes).to_bytes(8, "big"))
        aggregate.update(relative_bytes)
        aggregate.update(len(contents).to_bytes(8, "big"))
        aggregate.update(contents)
    digest = base64.b64encode(aggregate.digest()).decode("ascii")
    return f"sha256-{digest}"


def compare_projections(
    primary: dict[str, Path], compared: dict[str, Path]
) -> list[Finding]:
    findings = []
    primary_paths = set(primary)
    compared_paths = set(compared)
    for relative in sorted(primary_paths - compared_paths):
        add_finding(
            findings,
            "AKBA060",
            "error",
            f"/projection/{relative}",
            "referenced file is missing from the compared projection",
        )
    for relative in sorted(compared_paths - primary_paths):
        add_finding(
            findings,
            "AKBA061",
            "error",
            f"/projection/{relative}",
            "compared projection contains an unexpected referenced file",
        )
    for relative in sorted(primary_paths & compared_paths):
        primary_contents = primary[relative].read_bytes()
        compared_contents = compared[relative].read_bytes()
        if primary_contents != compared_contents:
            add_finding(
                findings,
                "AKBA062",
                "error",
                f"/projection/{relative}",
                "referenced file bytes differ between projections",
                expected=sha256_stamp(primary_contents),
                actual=sha256_stamp(compared_contents),
            )
    return findings


def invalid_descriptor_result(
    descriptor_path: Path, pointer: str, message: str
) -> tuple[list[Finding], dict[str, object]]:
    finding = Finding("AKBA000", "error", pointer, message)
    return [finding], {
        "descriptor": str(descriptor_path),
        "identity": "",
        "sources": 0,
        "sections": 0,
        "content_sections": 0,
        "errors": 1,
        "warnings": 0,
        "projected_files": None,
        "aggregate_digest": None,
    }


def audit_local_reference(
    *,
    root: Path,
    value: dict[str, object],
    uri_key: str,
    hash_key: str,
    length_key: str,
    pointer: str,
    findings: list[Finding],
) -> Path | None:
    uri = value.get(uri_key)
    if not isinstance(uri, str):
        return None
    try:
        local_path = resolve_local_uri(root, uri)
    except ValueError as error:
        add_finding(
            findings,
            "AKBA001",
            "error",
            pointer,
            str(error),
            actual=uri,
        )
        return None
    if local_path is None:
        return None

    stamps = complete_stamps(value, hash_key, length_key)
    if not local_path.is_file():
        if stamps is not None:
            add_finding(
                findings,
                "AKBA002",
                "warning",
                pointer,
                (
                    f"{uri!r} is stamps-only; restore it unless the target or "
                    "base snapshot already has the blob"
                ),
            )
        else:
            add_finding(
                findings,
                "AKBA003",
                "error",
                pointer,
                (
                    f"local file {uri!r} is missing without complete "
                    f"{hash_key}/{length_key} stamps"
                ),
            )
        return None

    if stamps is None:
        add_finding(
            findings,
            "AKBA004",
            "error",
            pointer,
            f"present local file requires complete {hash_key}/{length_key} stamps",
        )
        return local_path

    expected_hash, expected_length = stamps
    contents = local_path.read_bytes()
    actual_length = len(contents)
    if expected_length != actual_length:
        add_finding(
            findings,
            "AKBA005",
            "error",
            f"{pointer.rsplit('/', 1)[0]}/{length_key}",
            "local file byte length differs from its descriptor stamp",
            expected=expected_length,
            actual=actual_length,
        )
    actual_hash = sha256_stamp(contents)
    if expected_hash != actual_hash:
        add_finding(
            findings,
            "AKBA006",
            "error",
            f"{pointer.rsplit('/', 1)[0]}/{hash_key}",
            "local file SHA-256 differs from its descriptor stamp",
            expected=expected_hash,
            actual=actual_hash,
        )
    return local_path


def normalized_source_ids(value: object) -> list[str] | None:
    if not isinstance(value, list):
        return None
    result = []
    for source_id in value:
        if not isinstance(source_id, str) or not SOURCE_ID_PATTERN.fullmatch(source_id):
            return None
        result.append(source_id.lower())
    return result


def audit_content_markers(
    *,
    content_path: Path,
    section_pointer: str,
    descriptor_source_ids: list[str],
    findings: list[Finding],
) -> list[str]:
    content = content_path.read_text(encoding="utf-8")
    block_ids = [
        match.group(1).lower() for match in SOURCE_BLOCK_PATTERN.finditer(content)
    ]
    citation_ids = [
        match.group(1).lower() for match in CITATION_PATTERN.finditer(content)
    ]
    paired_ids = [
        match.group(1).lower() for match in SOURCE_BLOCK_PAIR_PATTERN.finditer(content)
    ]

    if block_ids != citation_ids or paired_ids != block_ids:
        add_finding(
            findings,
            "AKBA020",
            "error",
            f"{section_pointer}/content_uri",
            (
                "each Source block marker must be immediately followed by its "
                "matching inline citation"
            ),
            expected=block_ids,
            actual=citation_ids,
        )
    if block_ids != descriptor_source_ids:
        add_finding(
            findings,
            "AKBA021",
            "error",
            f"{section_pointer}/source_ids",
            "descriptor source_ids must match Source blocks in content order",
            expected=block_ids,
            actual=descriptor_source_ids,
        )
    return block_ids


def audit_provenance_source_ids(
    *,
    provenance: dict[str, object],
    pointer: str,
    key: str,
    expected_ids: list[str],
    findings: list[Finding],
) -> None:
    actual = normalized_source_ids(provenance.get(key))
    if actual is None:
        add_finding(
            findings,
            "AKBA030",
            "error",
            f"{pointer}/{key}",
            "expected an array of Source IDs",
        )
    elif actual != expected_ids:
        add_finding(
            findings,
            "AKBA031",
            "error",
            f"{pointer}/{key}",
            "provenance Source IDs must match content Source blocks in order",
            expected=expected_ids,
            actual=actual,
        )


def audit_provenance(
    *,
    provenance_path: Path,
    pointer: str,
    section_id: str,
    block_ids: list[str],
    content_length: int | None,
    source_stamps: dict[str, tuple[str, int]],
    findings: list[Finding],
) -> None:
    try:
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        add_finding(
            findings,
            "AKBA032",
            "error",
            pointer,
            f"cannot load provenance sidecar: {error}",
        )
        return
    if not isinstance(provenance, dict):
        add_finding(
            findings,
            "AKBA033",
            "error",
            pointer,
            "provenance sidecar must be an object",
        )
        return

    provenance_section_id = provenance.get("section_id")
    if not isinstance(provenance_section_id, str) or (
        provenance_section_id.lower() != section_id.lower()
    ):
        add_finding(
            findings,
            "AKBA034",
            "error",
            f"{pointer}/section_id",
            "provenance Section ID must match its descriptor Section",
            expected=section_id,
            actual=provenance_section_id,
        )

    audit_provenance_source_ids(
        provenance=provenance,
        pointer=pointer,
        key="source_ids",
        expected_ids=block_ids,
        findings=findings,
    )

    source_blocks = provenance.get("source_blocks")
    provenance_block_ids: list[str] = []
    if not isinstance(source_blocks, list):
        add_finding(
            findings,
            "AKBA035",
            "error",
            f"{pointer}/source_blocks",
            "expected an array",
        )
        return

    for index, block in enumerate(source_blocks):
        block_pointer = f"{pointer}/source_blocks/{index}"
        if not isinstance(block, dict):
            add_finding(
                findings,
                "AKBA036",
                "error",
                block_pointer,
                "Source block provenance must be an object",
            )
            continue
        source_id = block.get("source_id")
        if not isinstance(source_id, str) or not SOURCE_ID_PATTERN.fullmatch(source_id):
            add_finding(
                findings,
                "AKBA037",
                "error",
                f"{block_pointer}/source_id",
                "expected a Source ID",
                actual=source_id,
            )
            continue
        normalized_source_id = source_id.lower()
        provenance_block_ids.append(normalized_source_id)

        capture = block.get("capture")
        stamps = source_stamps.get(normalized_source_id)
        if not isinstance(capture, dict):
            add_finding(
                findings,
                "AKBA044",
                "error",
                f"{block_pointer}/capture",
                "Source block provenance requires capture stamps",
            )
        elif stamps is None:
            add_finding(
                findings,
                "AKBA045",
                "error",
                f"{block_pointer}/capture",
                "cannot verify capture without complete Descriptor Source stamps",
            )
        else:
            expected_hash, expected_length = stamps
            capture_hash = capture.get("sha256")
            if not isinstance(capture_hash, str):
                add_finding(
                    findings,
                    "AKBA046",
                    "error",
                    f"{block_pointer}/capture/sha256",
                    "expected a hexadecimal SHA-256 digest",
                    actual=capture_hash,
                )
            else:
                actual_hash = expected_hash.removeprefix("sha256-")
                try:
                    actual_hash = base64.b64decode(actual_hash, validate=True).hex()
                except ValueError:
                    actual_hash = ""
                if capture_hash.lower() != actual_hash:
                    add_finding(
                        findings,
                        "AKBA038",
                        "error",
                        f"{block_pointer}/capture/sha256",
                        "provenance capture SHA-256 must match the Source stamp",
                        expected=actual_hash,
                        actual=capture_hash,
                    )
            capture_length = capture.get("content_length")
            if not isinstance(capture_length, int) or isinstance(capture_length, bool):
                add_finding(
                    findings,
                    "AKBA047",
                    "error",
                    f"{block_pointer}/capture/content_length",
                    "expected a non-negative integer byte length",
                    actual=capture_length,
                )
            elif capture_length != expected_length:
                add_finding(
                    findings,
                    "AKBA039",
                    "error",
                    f"{block_pointer}/capture/content_length",
                    "provenance capture length must match the Source stamp",
                    expected=expected_length,
                    actual=capture_length,
                )

        byte_range = block.get("section_byte_range")
        if not isinstance(byte_range, dict):
            add_finding(
                findings,
                "AKBA048",
                "error",
                f"{block_pointer}/section_byte_range",
                "Source block provenance requires a Section byte range",
            )
        else:
            start = byte_range.get("start")
            end = byte_range.get("end")
            valid_range = not (
                not isinstance(start, int)
                or isinstance(start, bool)
                or not isinstance(end, int)
                or isinstance(end, bool)
                or not 0 <= start <= end
            )
            if valid_range and content_length is not None:
                valid_range = end <= content_length
            if not valid_range:
                expected = "0 <= start <= end"
                if content_length is not None:
                    expected += f" <= {content_length}"
                add_finding(
                    findings,
                    "AKBA040",
                    "error",
                    f"{block_pointer}/section_byte_range",
                    "Section byte range must be ordered and within content bytes",
                    expected=expected,
                    actual=byte_range,
                )

    if provenance_block_ids != block_ids:
        add_finding(
            findings,
            "AKBA041",
            "error",
            f"{pointer}/source_blocks",
            "provenance Source blocks must match content Source blocks in order",
            expected=block_ids,
            actual=provenance_block_ids,
        )

    claims = provenance.get("claims")
    if isinstance(claims, list):
        allowed = set(block_ids)
        for index, claim in enumerate(claims):
            if not isinstance(claim, dict):
                continue
            claim_ids = normalized_source_ids(claim.get("source_ids"))
            if claim_ids is None:
                add_finding(
                    findings,
                    "AKBA042",
                    "error",
                    f"{pointer}/claims/{index}/source_ids",
                    "expected an array of Source IDs",
                )
            elif not set(claim_ids).issubset(allowed):
                add_finding(
                    findings,
                    "AKBA043",
                    "error",
                    f"{pointer}/claims/{index}/source_ids",
                    "claim Source IDs must belong to the Section Source blocks",
                    expected=sorted(allowed),
                    actual=claim_ids,
                )


def audit(descriptor_path: Path) -> tuple[list[Finding], dict[str, object]]:
    descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
    if not isinstance(descriptor, dict):
        return invalid_descriptor_result(
            descriptor_path, "/", "descriptor must be an object"
        )
    root = descriptor_path.parent
    sources = descriptor.get("sources", [])
    sections = descriptor.get("sections", [])
    findings: list[Finding] = []

    if not isinstance(sources, list):
        return invalid_descriptor_result(
            descriptor_path, "/sources", "must be an array"
        )
    if not isinstance(sections, list):
        return invalid_descriptor_result(
            descriptor_path, "/sections", "must be an array"
        )

    entities: dict[str, str] = {}
    natural_keys: dict[tuple[str, str], list[str]] = defaultdict(list)
    source_ids: set[str] = set()
    source_stamps: dict[str, tuple[str, int]] = {}

    for index, source in enumerate(sources):
        pointer = f"/sources/{index}"
        if not isinstance(source, dict):
            add_finding(
                findings, "AKBA010", "error", pointer, "source must be an object"
            )
            continue

        source_id = source.get("id")
        if not isinstance(source_id, str) or not SOURCE_ID_PATTERN.fullmatch(source_id):
            add_finding(
                findings,
                "AKBA011",
                "error",
                f"{pointer}/id",
                "expected Source ID 'SRC-' plus 6 ASCII base36 characters",
                actual=source_id,
            )
            continue
        normalized_source_id = source_id.lower()
        if normalized_source_id in entities:
            add_finding(
                findings,
                "AKBA012",
                "error",
                f"{pointer}/id",
                f"duplicate shared ID; first used by {entities[normalized_source_id]}",
                actual=source_id,
            )
        else:
            entities[normalized_source_id] = pointer
        source_ids.add(normalized_source_id)
        stamps = complete_stamps(source, "content_hash", "content_length")
        if stamps is not None:
            source_stamps[normalized_source_id] = stamps

        source_type = source.get("type")
        if not isinstance(source_type, str) or source_type not in SOURCE_TYPES:
            add_finding(
                findings,
                "AKBA013",
                "error",
                f"{pointer}/type",
                "unsupported Nurok source type",
                actual=source_type,
            )
        if source_type != "redacted" and not source.get("captured_at"):
            add_finding(
                findings,
                "AKBA014",
                "error",
                f"{pointer}/captured_at",
                "required for non-redacted sources",
            )

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
                findings=findings,
            )
        audit_local_reference(
            root=root,
            value=source,
            uri_key="capture_uri",
            hash_key="content_hash",
            length_key="content_length",
            pointer=f"{pointer}/capture_uri",
            findings=findings,
        )

    for (source_type, uri), ids in natural_keys.items():
        if len(ids) > 1:
            add_finding(
                findings,
                "AKBA015",
                "error",
                "/sources",
                f"duplicate source natural key type={source_type!r}, uri={uri!r}",
                actual=ids,
            )

    content_count = 0
    for index, section in enumerate(sections):
        pointer = f"/sections/{index}"
        if not isinstance(section, dict):
            add_finding(
                findings, "AKBA050", "error", pointer, "section must be an object"
            )
            continue

        section_id = section.get("id")
        if not isinstance(section_id, str) or not SECTION_ID_PATTERN.fullmatch(
            section_id
        ):
            add_finding(
                findings,
                "AKBA051",
                "error",
                f"{pointer}/id",
                "expected Section ID 'SEC-' plus 6 ASCII base36 characters",
                actual=section_id,
            )
            continue
        normalized_section_id = section_id.lower()
        if normalized_section_id in entities:
            add_finding(
                findings,
                "AKBA012",
                "error",
                f"{pointer}/id",
                f"duplicate shared ID; first used by {entities[normalized_section_id]}",
                actual=section_id,
            )
        else:
            entities[normalized_section_id] = pointer

        provenance_path = audit_local_reference(
            root=root,
            value=section,
            uri_key="provenance_uri",
            hash_key="provenance_hash",
            length_key="provenance_length",
            pointer=f"{pointer}/provenance_uri",
            findings=findings,
        )

        content_uri = section.get("content_uri")
        provenance_uri = section.get("provenance_uri")
        if isinstance(content_uri, str) and not isinstance(provenance_uri, str):
            add_finding(
                findings,
                "AKBA058",
                "error",
                f"{pointer}/provenance_uri",
                "content Section requires a provenance sidecar",
            )
        elif not isinstance(content_uri, str) and isinstance(provenance_uri, str):
            add_finding(
                findings,
                "AKBA059",
                "error",
                f"{pointer}/provenance_uri",
                "contentless Section must not declare a provenance sidecar",
            )
        cited = section.get("source_ids")
        if isinstance(content_uri, str) and (not isinstance(cited, list) or not cited):
            add_finding(
                findings,
                "AKBA052",
                "error",
                f"{pointer}/source_ids",
                "content section must cite a source",
            )
        if cited is not None and not isinstance(cited, list):
            if not isinstance(content_uri, str):
                add_finding(
                    findings,
                    "AKBA053",
                    "error",
                    f"{pointer}/source_ids",
                    "expected an array",
                )
            normalized_citations = None
        elif isinstance(cited, list):
            normalized_citations = []
            seen_citations: set[str] = set()
            for cited_id in cited:
                if not isinstance(cited_id, str) or not SOURCE_ID_PATTERN.fullmatch(
                    cited_id
                ):
                    add_finding(
                        findings,
                        "AKBA054",
                        "error",
                        f"{pointer}/source_ids",
                        "expected Source ID 'SRC-' plus 6 ASCII base36 characters",
                        actual=cited_id,
                    )
                    continue
                normalized_cited_id = cited_id.lower()
                normalized_citations.append(normalized_cited_id)
                if normalized_cited_id in seen_citations:
                    add_finding(
                        findings,
                        "AKBA055",
                        "error",
                        f"{pointer}/source_ids",
                        "duplicate source ID under case-insensitive comparison",
                        actual=cited_id,
                    )
                else:
                    seen_citations.add(normalized_cited_id)
                if normalized_cited_id not in source_ids:
                    add_finding(
                        findings,
                        "AKBA056",
                        "error",
                        f"{pointer}/source_ids",
                        "unresolved source ID",
                        actual=cited_id,
                    )
        else:
            normalized_citations = None

        if not isinstance(content_uri, str):
            continue
        content_count += 1

        content_type = section.get("content_type", "text/markdown")
        if content_type == "text/markdown":
            expected = f"sections/{section_id}/content.md"
            if content_uri != expected:
                add_finding(
                    findings,
                    "AKBA057",
                    "error",
                    f"{pointer}/content_uri",
                    "Markdown content must use its canonical path",
                    expected=expected,
                    actual=content_uri,
                )

        content_path = audit_local_reference(
            root=root,
            value=section,
            uri_key="content_uri",
            hash_key="content_hash",
            length_key="content_length",
            pointer=f"{pointer}/content_uri",
            findings=findings,
        )

        block_ids = normalized_citations or []
        content_length = None
        if content_path is not None:
            content_length = content_path.stat().st_size
            if content_type == "text/markdown" and normalized_citations is not None:
                try:
                    block_ids = audit_content_markers(
                        content_path=content_path,
                        section_pointer=pointer,
                        descriptor_source_ids=normalized_citations,
                        findings=findings,
                    )
                except UnicodeDecodeError as error:
                    add_finding(
                        findings,
                        "AKBA022",
                        "error",
                        f"{pointer}/content_uri",
                        f"Markdown content must be UTF-8: {error}",
                    )

        if provenance_path is not None:
            audit_provenance(
                provenance_path=provenance_path,
                pointer=f"{pointer}/provenance_uri",
                section_id=section_id,
                block_ids=block_ids,
                content_length=content_length,
                source_stamps=source_stamps,
                findings=findings,
            )

    audit_local_reference(
        root=root,
        value=descriptor,
        uri_key="guide_uri",
        hash_key="guide_hash",
        length_key="guide_length",
        pointer="/guide_uri",
        findings=findings,
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
            findings=findings,
        )

    findings.sort(
        key=lambda item: (item.pointer, item.severity, item.code, item.message)
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
        "errors": sum(finding.severity == "error" for finding in findings),
        "warnings": sum(finding.severity == "warning" for finding in findings),
    }
    projection = descriptor_projection(descriptor_path, descriptor)
    summary["projected_files"] = len(projection) if projection is not None else None
    summary["aggregate_digest"] = (
        aggregate_projection_digest(projection) if projection is not None else None
    )
    return findings, summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path("."),
        help="Working-copy directory or openakb.json path",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--compare-dir",
        type=Path,
        help="Compare all Descriptor-projected file bytes with another working copy",
    )
    return parser.parse_args()


def update_summary_counts(findings: list[Finding], summary: dict[str, object]) -> None:
    findings.sort(
        key=lambda item: (item.pointer, item.severity, item.code, item.message)
    )
    summary["errors"] = sum(finding.severity == "error" for finding in findings)
    summary["warnings"] = sum(finding.severity == "warning" for finding in findings)


def print_report(
    findings: list[Finding], summary: dict[str, object], output_format: str
) -> None:
    if output_format == "json":
        print(
            json.dumps(
                {
                    "summary": summary,
                    "findings": [asdict(finding) for finding in findings],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        for finding in findings:
            print(f"{finding.severity.upper()} {finding.code} {finding.render()}")
        print(f"audit: {summary['errors']} error(s), {summary['warnings']} warning(s)")


def main() -> int:
    args = parse_args()
    descriptor_path = find_descriptor(args.dir)

    try:
        findings, summary = audit(descriptor_path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        findings, summary = invalid_descriptor_result(
            descriptor_path, "/", f"cannot load descriptor: {error}"
        )
        print_report(findings, summary, args.format)
        return 2

    if args.compare_dir is not None:
        compared_path = find_descriptor(args.compare_dir)
        try:
            primary_descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
            compared_descriptor = json.loads(compared_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            add_finding(
                findings,
                "AKBA063",
                "error",
                "/compare_dir",
                f"cannot load compared descriptor: {error}",
            )
            update_summary_counts(findings, summary)
            print_report(findings, summary, args.format)
            return 2
        if not isinstance(primary_descriptor, dict) or not isinstance(
            compared_descriptor, dict
        ):
            add_finding(
                findings,
                "AKBA063",
                "error",
                "/compare_dir",
                "both compared descriptors must be objects",
            )
            update_summary_counts(findings, summary)
            print_report(findings, summary, args.format)
            return 2
        primary_projection = descriptor_projection(descriptor_path, primary_descriptor)
        compared_projection = descriptor_projection(compared_path, compared_descriptor)
        if primary_projection is None or compared_projection is None:
            add_finding(
                findings,
                "AKBA063",
                "error",
                "/compare_dir",
                "both projections must contain every valid referenced local file",
            )
        else:
            findings.extend(
                compare_projections(primary_projection, compared_projection)
            )
            summary["compared_descriptor"] = str(compared_path)
            summary["compared_files"] = len(compared_projection)
            summary["compared_aggregate_digest"] = aggregate_projection_digest(
                compared_projection
            )
        update_summary_counts(findings, summary)

    print_report(findings, summary, args.format)
    return 1 if summary["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
