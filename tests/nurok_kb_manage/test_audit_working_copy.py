#!/usr/bin/env python3
"""Regression tests for audit_working_copy.py."""

import json
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from base64 import b64encode
from hashlib import sha256
from pathlib import Path

AUDIT_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "plugins"
    / "nurok-kb-manage"
    / "skills"
    / "nurok-kb-manage"
    / "scripts"
    / "audit_working_copy.py"
)
audit = runpy.run_path(str(AUDIT_SCRIPT))["audit"]


def stamp(contents: bytes) -> str:
    return f"sha256-{b64encode(sha256(contents).digest()).decode('ascii')}"


STAMP = stamp(b"hello")


def errors(findings: list[object]) -> list[str]:
    return [finding.render() for finding in findings if finding.severity == "error"]


def warnings(findings: list[object]) -> list[str]:
    return [finding.render() for finding in findings if finding.severity == "warning"]


def descriptor_with_local_references() -> dict[str, object]:
    return {
        "$schema": "https://schema.openakb.org/v1/openakb.schema.json",
        "id": "notes",
        "title": "Notes",
        "description": "Test knowledge base",
        "guide_uri": "AKB.md",
        "guide_hash": STAMP,
        "guide_length": 5,
        "sources": [
            {
                "id": "SRC-000001",
                "type": "file",
                "uri": "files/manual.pdf",
                "captured_at": "2026-07-24T00:00:00Z",
                "content_hash": STAMP,
                "content_length": 5,
            },
            {
                "id": "SRC-000002",
                "type": "url",
                "uri": "https://example.com/",
                "capture_uri": "captures/website.html",
                "captured_at": "2026-07-24T00:00:00Z",
                "content_hash": STAMP,
                "content_length": 5,
            },
        ],
        "sections": [
            {
                "id": "SEC-000001",
                "title": "Introduction",
                "description": "Introduction section",
                "content_uri": "sections/SEC-000001/content.md",
                "content_hash": STAMP,
                "content_length": 5,
                "provenance_uri": "sections/SEC-000001/provenance.json",
                "provenance_hash": STAMP,
                "provenance_length": 5,
                "source_ids": ["SRC-000001", "SRC-000002"],
            }
        ],
        "x": {
            "ai.nurok": {
                "skill_uri": "skill.md",
                "skill_hash": STAMP,
                "skill_length": 5,
            }
        },
    }


class AuditWorkingCopyTests(unittest.TestCase):
    def write_descriptor(self, root: Path, descriptor: object) -> Path:
        path = root / "openakb.json"
        path.write_text(json.dumps(descriptor), encoding="utf-8")
        return path

    def materialize_valid_references(
        self, root: Path, descriptor: dict[str, object]
    ) -> Path:
        content = (
            b"<!-- source-block:SRC-000001 -->\n"
            b"[cite:SRC-000001]\n\nFirst source.\n\n"
            b"<!-- source-block:SRC-000002 -->\n"
            b"[cite:SRC-000002]\n\nSecond source.\n"
        )
        provenance = {
            "section_id": "SEC-000001",
            "source_ids": ["SRC-000001", "SRC-000002"],
            "claims": [{"text": "First", "source_ids": ["SRC-000001"]}],
            "source_blocks": [
                {
                    "source_id": "SRC-000001",
                    "capture": {
                        "sha256": sha256(b"hello").hexdigest(),
                        "content_length": 5,
                    },
                    "section_byte_range": {"start": 0, "end": 62},
                },
                {
                    "source_id": "SRC-000002",
                    "capture": {
                        "sha256": sha256(b"hello").hexdigest(),
                        "content_length": 5,
                    },
                    "section_byte_range": {"start": 62, "end": len(content)},
                },
            ],
        }
        provenance_bytes = json.dumps(provenance, separators=(",", ":")).encode()
        blobs = {
            "AKB.md": b"hello",
            "files/manual.pdf": b"hello",
            "captures/website.html": b"hello",
            "skill.md": b"hello",
            "sections/SEC-000001/content.md": content,
            "sections/SEC-000001/provenance.json": provenance_bytes,
        }
        for relative, contents in blobs.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(contents)

        hello_stamp = stamp(b"hello")
        descriptor["guide_hash"] = hello_stamp
        descriptor["guide_length"] = 5
        for source in descriptor["sources"]:
            source["content_hash"] = hello_stamp
            source["content_length"] = 5
        descriptor["x"]["ai.nurok"]["skill_hash"] = hello_stamp
        descriptor["x"]["ai.nurok"]["skill_length"] = 5
        section = descriptor["sections"][0]
        section["content_hash"] = stamp(content)
        section["content_length"] = len(content)
        section["provenance_hash"] = stamp(provenance_bytes)
        section["provenance_length"] = len(provenance_bytes)
        return self.write_descriptor(root, descriptor)

    def test_all_stamps_only_blob_kinds_are_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor_path = self.write_descriptor(
                Path(directory), descriptor_with_local_references()
            )

            findings, _ = audit(descriptor_path)

        self.assertEqual(errors(findings), [])
        self.assertEqual(len(warnings(findings)), 6)
        self.assertEqual(
            {finding.pointer for finding in findings},
            {
                "/guide_uri",
                "/sources/0/uri",
                "/sources/1/capture_uri",
                "/sections/0/content_uri",
                "/sections/0/provenance_uri",
                "/x/ai.nurok/skill_uri",
            },
        )

    def test_missing_guide_without_stamps_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            descriptor = descriptor_with_local_references()
            descriptor.pop("guide_hash")
            descriptor.pop("guide_length")
            descriptor_path = self.write_descriptor(root, descriptor)

            findings, _ = audit(descriptor_path)

        self.assertTrue(
            any(error.startswith("/guide_uri:") for error in errors(findings))
        )

    def test_missing_guide_requires_valid_sha256_stamp(self) -> None:
        invalid_stamps = (
            "not-a-sha256",
            "sha256-!!!!",
            "sha256-aGVsbG8=",
        )
        for invalid_stamp in invalid_stamps:
            with self.subTest(invalid_stamp=invalid_stamp):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    descriptor = descriptor_with_local_references()
                    descriptor["guide_hash"] = invalid_stamp
                    descriptor_path = self.write_descriptor(root, descriptor)

                    findings, _ = audit(descriptor_path)

                self.assertTrue(
                    any(
                        finding.code == "AKBA003" and finding.pointer == "/guide_uri"
                        for finding in findings
                    )
                )

    def test_present_local_blobs_pass_all_checks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor_path = self.materialize_valid_references(
                Path(directory), descriptor_with_local_references()
            )

            findings, _ = audit(descriptor_path)

        self.assertEqual(findings, [])

    def test_non_object_descriptor_returns_a_structured_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor_path = self.write_descriptor(Path(directory), [])

            findings, summary = audit(descriptor_path)

        self.assertEqual(errors(findings), ["/: descriptor must be an object"])
        self.assertEqual(summary["errors"], 1)
        self.assertEqual(summary["descriptor"], str(descriptor_path))

    def test_parent_traversal_is_rejected_even_when_target_exists(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            working_copy = root / "working-copy"
            working_copy.mkdir()
            (root / "outside.md").write_text("hello", encoding="utf-8")
            descriptor = descriptor_with_local_references()
            descriptor["guide_uri"] = "../outside.md"
            descriptor_path = self.write_descriptor(working_copy, descriptor)

            findings, _ = audit(descriptor_path)

        self.assertTrue(
            any(error.startswith("/guide_uri:") for error in errors(findings))
        )

    def test_absolute_local_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor = descriptor_with_local_references()
            descriptor["guide_uri"] = "/tmp/outside.md"
            descriptor_path = self.write_descriptor(Path(directory), descriptor)

            findings, _ = audit(descriptor_path)

        self.assertTrue(
            any(error.startswith("/guide_uri:") for error in errors(findings))
        )

    def test_absolute_filesystem_uri_forms_are_rejected(self) -> None:
        values = (
            "file:///etc/passwd",
            r"C:\outside.txt",
            r"\\server\share\outside.txt",
            "//server/share/outside.txt",
        )
        for value in values:
            with self.subTest(value=value):
                with tempfile.TemporaryDirectory() as directory:
                    descriptor = descriptor_with_local_references()
                    descriptor["guide_uri"] = value
                    descriptor_path = self.write_descriptor(Path(directory), descriptor)

                    findings, _ = audit(descriptor_path)

                self.assertTrue(
                    any(
                        finding.code == "AKBA001" and finding.pointer == "/guide_uri"
                        for finding in findings
                    )
                )

    def test_symlink_outside_working_copy_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            working_copy = root / "working-copy"
            working_copy.mkdir()
            outside = root / "outside.md"
            outside.write_text("hello", encoding="utf-8")
            try:
                (working_copy / "AKB.md").symlink_to(outside)
            except OSError as error:
                self.skipTest(f"symlinks are unavailable: {error}")
            descriptor_path = self.write_descriptor(
                working_copy, descriptor_with_local_references()
            )

            findings, _ = audit(descriptor_path)

        self.assertTrue(
            any(error.startswith("/guide_uri:") for error in errors(findings))
        )

    def test_duplicate_source_natural_key_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor = descriptor_with_local_references()
            duplicate = dict(descriptor["sources"][1])
            duplicate["id"] = "SRC-000003"
            descriptor["sources"].append(duplicate)
            descriptor_path = self.write_descriptor(Path(directory), descriptor)

            findings, _ = audit(descriptor_path)

        self.assertTrue(
            any("duplicate source natural key" in error for error in errors(findings))
        )

    def test_non_string_source_type_returns_structured_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            descriptor = descriptor_with_local_references()
            descriptor["sources"][0]["type"] = []
            descriptor_path = self.write_descriptor(root, descriptor)

            result = subprocess.run(
                [
                    sys.executable,
                    str(AUDIT_SCRIPT),
                    "--dir",
                    str(descriptor_path),
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(
            any(finding["code"] == "AKBA013" for finding in payload["findings"])
        )

    def test_wrong_kind_section_id_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor = descriptor_with_local_references()
            descriptor["sections"][0]["id"] = "SRC-000001"
            descriptor_path = self.write_descriptor(Path(directory), descriptor)

            findings, _ = audit(descriptor_path)

        self.assertTrue(
            any("expected Section ID" in error for error in errors(findings))
        )

    def test_typed_ids_and_case_variant_source_reference_are_valid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor = descriptor_with_local_references()
            descriptor["sources"][0]["id"] = "Src-00000A"
            descriptor["sections"][0]["source_ids"] = ["sRC-00000a", "SRC-000002"]
            descriptor_path = self.write_descriptor(Path(directory), descriptor)

            findings, _ = audit(descriptor_path)

        self.assertEqual(errors(findings), [])

    def test_case_variant_duplicate_entity_id_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor = descriptor_with_local_references()
            duplicate = dict(descriptor["sources"][0])
            duplicate["id"] = "src-000001"
            duplicate["uri"] = "files/other.pdf"
            descriptor["sources"].append(duplicate)
            descriptor_path = self.write_descriptor(Path(directory), descriptor)

            findings, _ = audit(descriptor_path)

        self.assertTrue(
            any("duplicate shared ID" in error for error in errors(findings))
        )

    def test_case_variant_duplicate_source_reference_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor = descriptor_with_local_references()
            descriptor["sections"][0]["source_ids"] = ["SRC-000001", "src-000001"]
            descriptor_path = self.write_descriptor(Path(directory), descriptor)

            findings, _ = audit(descriptor_path)

        self.assertTrue(
            any("duplicate source ID" in error for error in errors(findings))
        )

    def test_markdown_content_uses_canonical_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor = descriptor_with_local_references()
            descriptor["sections"][0]["content_uri"] = "sections/SEC-000001.md"
            descriptor_path = self.write_descriptor(Path(directory), descriptor)

            findings, _ = audit(descriptor_path)

        self.assertTrue(any("canonical path" in error for error in errors(findings)))

    def test_content_section_rejects_unresolved_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor = descriptor_with_local_references()
            descriptor["sections"][0]["source_ids"] = ["SRC-999999"]
            descriptor_path = self.write_descriptor(Path(directory), descriptor)

            findings, _ = audit(descriptor_path)

        self.assertTrue(
            any("unresolved source ID" in error for error in errors(findings))
        )

    def test_content_section_rejects_section_id_as_source_reference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor = descriptor_with_local_references()
            descriptor["sections"][0]["source_ids"] = ["SEC-999999"]
            descriptor_path = self.write_descriptor(Path(directory), descriptor)

            findings, _ = audit(descriptor_path)

        self.assertTrue(
            any("expected Source ID" in error for error in errors(findings))
        )

    def test_source_ids_on_contentless_section_still_require_source_kind(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor = descriptor_with_local_references()
            descriptor["sections"].append(
                {
                    "id": "SEC-000002",
                    "title": "Category",
                    "description": "Category section",
                    "source_ids": ["SEC-000001"],
                }
            )
            descriptor_path = self.write_descriptor(Path(directory), descriptor)

            findings, _ = audit(descriptor_path)

        self.assertTrue(
            any("expected Source ID" in error for error in errors(findings))
        )

    def test_content_and_provenance_must_be_one_to_one(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor = descriptor_with_local_references()
            content_section = descriptor["sections"][0]
            content_section.pop("provenance_uri")
            content_section.pop("provenance_hash")
            content_section.pop("provenance_length")
            descriptor["sections"].append(
                {
                    "id": "SEC-000002",
                    "title": "Category",
                    "description": "Category section",
                    "provenance_uri": "sections/SEC-000002/provenance.json",
                    "provenance_hash": STAMP,
                    "provenance_length": 5,
                }
            )
            descriptor_path = self.write_descriptor(Path(directory), descriptor)

            findings, _ = audit(descriptor_path)

        self.assertTrue(any(finding.code == "AKBA058" for finding in findings))
        self.assertTrue(any(finding.code == "AKBA059" for finding in findings))

    def test_cli_handles_non_object_descriptor_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor_path = self.write_descriptor(Path(directory), [])

            result = subprocess.run(
                [
                    sys.executable,
                    str(AUDIT_SCRIPT),
                    "--dir",
                    str(descriptor_path),
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["summary"]["errors"], 1)
        self.assertEqual(payload["findings"][0]["code"], "AKBA000")

    def test_cli_descriptor_load_failure_has_complete_summary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor_path = Path(directory) / "openakb.json"
            descriptor_path.write_text("{", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(AUDIT_SCRIPT),
                    "--dir",
                    str(descriptor_path),
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["summary"]["errors"], 1)
        self.assertEqual(payload["summary"]["warnings"], 0)
        self.assertEqual(payload["findings"][0]["code"], "AKBA000")

    def test_present_local_blob_hash_and_length_are_recomputed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            descriptor_path = self.materialize_valid_references(
                root, descriptor_with_local_references()
            )
            (root / "AKB.md").write_bytes(b"tampered")

            findings, _ = audit(descriptor_path)

        self.assertEqual(
            {
                finding.code
                for finding in findings
                if finding.pointer.startswith("/guide")
            },
            {"AKBA005", "AKBA006"},
        )

    def test_present_local_blob_requires_complete_stamps(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            descriptor = descriptor_with_local_references()
            self.materialize_valid_references(root, descriptor)
            descriptor.pop("guide_hash")
            descriptor.pop("guide_length")
            descriptor_path = self.write_descriptor(root, descriptor)

            findings, _ = audit(descriptor_path)

        self.assertTrue(any(finding.code == "AKBA004" for finding in findings))

    def test_source_block_and_citation_order_must_match(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            descriptor_path = self.materialize_valid_references(
                root, descriptor_with_local_references()
            )
            content_path = root / "sections/SEC-000001/content.md"
            content = content_path.read_text(encoding="utf-8")
            content_path.write_text(
                content.replace("[cite:SRC-000002]", "[cite:SRC-000001]"),
                encoding="utf-8",
            )

            findings, _ = audit(descriptor_path)

        self.assertTrue(any(finding.code == "AKBA020" for finding in findings))

    def test_source_block_marker_and_citation_must_be_adjacent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            descriptor_path = self.materialize_valid_references(
                root, descriptor_with_local_references()
            )
            content_path = root / "sections/SEC-000001/content.md"
            content = content_path.read_text(encoding="utf-8")
            content_path.write_text(
                content.replace(
                    "<!-- source-block:SRC-000001 -->\n[cite:SRC-000001]",
                    "<!-- source-block:SRC-000001 -->\nUnexpected.\n[cite:SRC-000001]",
                ),
                encoding="utf-8",
            )

            findings, _ = audit(descriptor_path)

        self.assertTrue(any(finding.code == "AKBA020" for finding in findings))

    def test_descriptor_source_order_must_match_content_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            descriptor = descriptor_with_local_references()
            descriptor["sections"][0]["source_ids"].reverse()
            descriptor_path = self.materialize_valid_references(root, descriptor)

            findings, _ = audit(descriptor_path)

        self.assertTrue(any(finding.code == "AKBA021" for finding in findings))

    def test_provenance_section_and_source_ids_must_match(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            descriptor_path = self.materialize_valid_references(
                root, descriptor_with_local_references()
            )
            path = root / "sections/SEC-000001/provenance.json"
            provenance = json.loads(path.read_text(encoding="utf-8"))
            provenance["section_id"] = "SEC-000099"
            provenance["source_ids"].reverse()
            path.write_text(json.dumps(provenance), encoding="utf-8")

            findings, _ = audit(descriptor_path)

        self.assertTrue(any(finding.code == "AKBA034" for finding in findings))
        self.assertTrue(any(finding.code == "AKBA031" for finding in findings))

    def test_provenance_capture_and_byte_range_must_match(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            descriptor_path = self.materialize_valid_references(
                root, descriptor_with_local_references()
            )
            path = root / "sections/SEC-000001/provenance.json"
            provenance = json.loads(path.read_text(encoding="utf-8"))
            block = provenance["source_blocks"][0]
            block["capture"]["sha256"] = "0" * 64
            block["capture"]["content_length"] = 6
            block["section_byte_range"] = {"start": 0, "end": 1000}
            path.write_text(json.dumps(provenance), encoding="utf-8")

            findings, _ = audit(descriptor_path)

        self.assertTrue(any(finding.code == "AKBA038" for finding in findings))
        self.assertTrue(any(finding.code == "AKBA039" for finding in findings))
        self.assertTrue(any(finding.code == "AKBA040" for finding in findings))

    def test_provenance_requires_capture_stamps_and_byte_range(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            descriptor_path = self.materialize_valid_references(
                root, descriptor_with_local_references()
            )
            path = root / "sections/SEC-000001/provenance.json"
            provenance = json.loads(path.read_text(encoding="utf-8"))
            block = provenance["source_blocks"][0]
            block.pop("capture")
            block.pop("section_byte_range")
            path.write_text(json.dumps(provenance), encoding="utf-8")

            findings, _ = audit(descriptor_path)

        self.assertTrue(any(finding.code == "AKBA044" for finding in findings))
        self.assertTrue(any(finding.code == "AKBA048" for finding in findings))

    def test_non_utf8_provenance_returns_structured_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            descriptor_path = self.materialize_valid_references(
                root, descriptor_with_local_references()
            )
            provenance_path = root / "sections/SEC-000001/provenance.json"
            provenance_bytes = b"\xff"
            provenance_path.write_bytes(provenance_bytes)
            descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
            section = descriptor["sections"][0]
            section["provenance_hash"] = stamp(provenance_bytes)
            section["provenance_length"] = len(provenance_bytes)
            descriptor_path = self.write_descriptor(root, descriptor)

            result = subprocess.run(
                [
                    sys.executable,
                    str(AUDIT_SCRIPT),
                    "--dir",
                    str(descriptor_path),
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(
            any(finding["code"] == "AKBA032" for finding in payload["findings"])
        )

    def test_stamps_only_content_still_validates_byte_ranges(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            descriptor_path = self.materialize_valid_references(
                root, descriptor_with_local_references()
            )
            (root / "sections/SEC-000001/content.md").unlink()
            provenance_path = root / "sections/SEC-000001/provenance.json"
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            provenance["source_blocks"][0]["section_byte_range"] = {
                "start": "bad",
                "end": -9,
            }
            provenance_bytes = json.dumps(provenance, separators=(",", ":")).encode()
            provenance_path.write_bytes(provenance_bytes)
            descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
            section = descriptor["sections"][0]
            section["provenance_hash"] = stamp(provenance_bytes)
            section["provenance_length"] = len(provenance_bytes)
            descriptor_path = self.write_descriptor(root, descriptor)

            findings, _ = audit(descriptor_path)

        self.assertTrue(any(finding.code == "AKBA040" for finding in findings))

    def test_json_output_is_structured_and_stable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor_path = self.materialize_valid_references(
                Path(directory), descriptor_with_local_references()
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(AUDIT_SCRIPT),
                    "--dir",
                    str(descriptor_path),
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["summary"]["errors"], 0)
        self.assertEqual(payload["summary"]["projected_files"], 7)
        self.assertTrue(payload["summary"]["aggregate_digest"].startswith("sha256-"))
        self.assertEqual(payload["findings"], [])

    def test_compare_dir_accepts_identical_descriptor_projection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            primary = root / "primary"
            compared = root / "compared"
            primary.mkdir()
            self.materialize_valid_references(
                primary, descriptor_with_local_references()
            )
            shutil.copytree(primary, compared)

            result = subprocess.run(
                [
                    sys.executable,
                    str(AUDIT_SCRIPT),
                    "--dir",
                    str(primary),
                    "--compare-dir",
                    str(compared),
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(
            payload["summary"]["aggregate_digest"],
            payload["summary"]["compared_aggregate_digest"],
        )
        self.assertEqual(payload["findings"], [])

    def test_compare_dir_detects_referenced_file_byte_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            primary = root / "primary"
            compared = root / "compared"
            primary.mkdir()
            self.materialize_valid_references(
                primary, descriptor_with_local_references()
            )
            shutil.copytree(primary, compared)
            (compared / "AKB.md").write_bytes(b"tampered")

            result = subprocess.run(
                [
                    sys.executable,
                    str(AUDIT_SCRIPT),
                    "--dir",
                    str(primary),
                    "--compare-dir",
                    str(compared),
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(
            any(finding["code"] == "AKBA062" for finding in payload["findings"])
        )

    def test_compare_dir_load_failure_preserves_primary_findings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            primary = root / "primary"
            primary.mkdir()
            descriptor = descriptor_with_local_references()
            descriptor.pop("guide_hash")
            descriptor.pop("guide_length")
            self.write_descriptor(primary, descriptor)

            result = subprocess.run(
                [
                    sys.executable,
                    str(AUDIT_SCRIPT),
                    "--dir",
                    str(primary),
                    "--compare-dir",
                    str(root / "missing"),
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["summary"]["errors"], 2)
        self.assertEqual(
            {finding["code"] for finding in payload["findings"]},
            {"AKBA002", "AKBA003", "AKBA063"},
        )


if __name__ == "__main__":
    unittest.main()
