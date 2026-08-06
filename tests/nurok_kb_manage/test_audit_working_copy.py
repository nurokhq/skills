#!/usr/bin/env python3
"""Regression tests for audit_working_copy.py."""

import json
import runpy
import tempfile
import unittest
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

STAMP = "sha256-aGVsbG8="


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

    def test_all_stamps_only_blob_kinds_are_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor_path = self.write_descriptor(
                Path(directory), descriptor_with_local_references()
            )

            errors, warnings, _ = audit(descriptor_path)

        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 6)
        self.assertEqual(
            {warning.split(":", 1)[0] for warning in warnings},
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

            errors, _, _ = audit(descriptor_path)

        self.assertTrue(any(error.startswith("/guide_uri:") for error in errors))

    def test_present_local_blobs_do_not_warn(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in (
                "AKB.md",
                "files/manual.pdf",
                "captures/website.html",
                "sections/SEC-000001/content.md",
                "sections/SEC-000001/provenance.json",
                "skill.md",
            ):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("hello", encoding="utf-8")
            descriptor_path = self.write_descriptor(
                root, descriptor_with_local_references()
            )

            errors, warnings, _ = audit(descriptor_path)

        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_non_object_descriptor_returns_a_structured_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor_path = self.write_descriptor(Path(directory), [])

            errors, warnings, summary = audit(descriptor_path)

        self.assertEqual(errors, ["/: descriptor must be an object"])
        self.assertEqual(warnings, [])
        self.assertEqual(summary, {})

    def test_parent_traversal_is_rejected_even_when_target_exists(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            working_copy = root / "working-copy"
            working_copy.mkdir()
            (root / "outside.md").write_text("hello", encoding="utf-8")
            descriptor = descriptor_with_local_references()
            descriptor["guide_uri"] = "../outside.md"
            descriptor_path = self.write_descriptor(working_copy, descriptor)

            errors, _, _ = audit(descriptor_path)

        self.assertTrue(any(error.startswith("/guide_uri:") for error in errors))

    def test_absolute_local_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor = descriptor_with_local_references()
            descriptor["guide_uri"] = "/tmp/outside.md"
            descriptor_path = self.write_descriptor(Path(directory), descriptor)

            errors, _, _ = audit(descriptor_path)

        self.assertTrue(any(error.startswith("/guide_uri:") for error in errors))

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

            errors, _, _ = audit(descriptor_path)

        self.assertTrue(any(error.startswith("/guide_uri:") for error in errors))

    def test_duplicate_source_natural_key_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor = descriptor_with_local_references()
            duplicate = dict(descriptor["sources"][1])
            duplicate["id"] = "SRC-000003"
            descriptor["sources"].append(duplicate)
            descriptor_path = self.write_descriptor(Path(directory), descriptor)

            errors, _, _ = audit(descriptor_path)

        self.assertTrue(
            any("duplicate source natural key" in error for error in errors)
        )

    def test_wrong_kind_section_id_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor = descriptor_with_local_references()
            descriptor["sections"][0]["id"] = "SRC-000001"
            descriptor_path = self.write_descriptor(Path(directory), descriptor)

            errors, _, _ = audit(descriptor_path)

        self.assertTrue(any("expected Section ID" in error for error in errors))

    def test_typed_ids_and_case_variant_source_reference_are_valid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor = descriptor_with_local_references()
            descriptor["sources"][0]["id"] = "Src-00000A"
            descriptor["sections"][0]["source_ids"] = [
                "sRC-00000a",
                "SRC-000002",
            ]
            descriptor_path = self.write_descriptor(Path(directory), descriptor)

            errors, _, _ = audit(descriptor_path)

        self.assertEqual(errors, [])

    def test_case_variant_duplicate_entity_id_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor = descriptor_with_local_references()
            duplicate = dict(descriptor["sources"][0])
            duplicate["id"] = "src-000001"
            duplicate["uri"] = "files/other.pdf"
            descriptor["sources"].append(duplicate)
            descriptor_path = self.write_descriptor(Path(directory), descriptor)

            errors, _, _ = audit(descriptor_path)

        self.assertTrue(
            any("duplicate shared ID 'src-000001'" in error for error in errors)
        )

    def test_case_variant_duplicate_source_reference_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor = descriptor_with_local_references()
            descriptor["sections"][0]["source_ids"] = [
                "SRC-000001",
                "src-000001",
            ]
            descriptor_path = self.write_descriptor(Path(directory), descriptor)

            errors, _, _ = audit(descriptor_path)

        self.assertTrue(
            any("duplicate source ID 'src-000001'" in error for error in errors)
        )

    def test_markdown_content_uses_canonical_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor = descriptor_with_local_references()
            descriptor["sections"][0]["content_uri"] = "sections/SEC-000001.md"
            descriptor_path = self.write_descriptor(Path(directory), descriptor)

            errors, _, _ = audit(descriptor_path)

        self.assertTrue(any("expected canonical path" in error for error in errors))

    def test_content_section_rejects_unresolved_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor = descriptor_with_local_references()
            descriptor["sections"][0]["source_ids"] = ["SRC-999999"]
            descriptor_path = self.write_descriptor(Path(directory), descriptor)

            errors, _, _ = audit(descriptor_path)

        self.assertTrue(
            any("unresolved source ID 'SRC-999999'" in error for error in errors)
        )

    def test_content_section_rejects_section_id_as_source_reference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            descriptor = descriptor_with_local_references()
            descriptor["sections"][0]["source_ids"] = ["SEC-999999"]
            descriptor_path = self.write_descriptor(Path(directory), descriptor)

            errors, _, _ = audit(descriptor_path)

        self.assertTrue(any("expected Source ID" in error for error in errors))

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

            errors, _, _ = audit(descriptor_path)

        self.assertTrue(any("expected Source ID" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
