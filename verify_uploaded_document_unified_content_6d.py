from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

from backend.server.stores.uploaded_document_unified_content import (
    build_and_write_uduc_from_extraction_result,
    explain_uploaded_document_unified_content_v1,
)


@dataclass
class FakeUploadExtractionResult:
    source_path: str = "backend/server/data/docs/ws_verification_6d/DOC_TEST__sample.md"
    source_type: str = "markdown"
    title: str = "Sample Uploaded Article"
    text: str = "This is the exact editor extracted content body.\n\nIt must not be cleaned or rewritten."
    headings: List[str] = field(default_factory=lambda: ["Sample Uploaded Article", "Main Section"])
    metadata: Dict[str, Any] = field(default_factory=lambda: {
        "filename": "sample.md",
        "extension": ".md",
        "extractor": "extract_markdown_upload_v1",
        "paragraph_count": 2,
        "heading_count": 2,
        "line_count": 3,
    })
    extraction_status: str = "success"
    extraction_confidence: float = 0.91
    created_at: str = datetime.now(timezone.utc).isoformat()


def fail(msg: str):
    raise AssertionError(msg)


def main():
    result = build_and_write_uduc_from_extraction_result(
        extraction_result=FakeUploadExtractionResult(),
        workspace_id="ws_verification_6d",
        document_id="DOC_TEST_6D",
        original_filename="sample.md",
        stored_filename="DOC_TEST__sample.md",
        stored_path="backend/server/data/docs/ws_verification_6d/DOC_TEST__sample.md",
        source_metadata={
            "doc_id": "DOC_TEST_6D",
            "bytes": 88,
        },
    )

    if not result.get("ok"):
        fail("UDUC builder returned ok=false")

    uduc = result.get("uduc") or {}

    required = [
        "schema_version",
        "pipeline_version",
        "workspace_id",
        "document_id",
        "source_type",
        "source_format",
        "original_filename",
        "stored_filename",
        "stored_path",
        "title",
        "h1",
        "headings",
        "content_body",
        "structure",
        "metadata",
        "extraction_status",
        "extraction_confidence",
        "created_at",
    ]

    missing = [k for k in required if k not in uduc]
    if missing:
        fail(f"Missing required UDUC fields: {missing}")

    expected_body = "This is the exact editor extracted content body.\n\nIt must not be cleaned or rewritten."
    if uduc["content_body"] != expected_body:
        fail("content_body was changed")

    forbidden_phrase_fields = [
        "phrase_pool",
        "upload_phrase_pool",
        "active_phrases",
        "candidate_phrases",
        "phrase_strength",
        "phrase_scores",
        "selected_phrases",
    ]

    for forbidden in forbidden_phrase_fields:
        if forbidden in uduc:
            fail(f"Forbidden phrase field present in UDUC root: {forbidden}")

    source_meta = ((uduc.get("metadata") or {}).get("source_metadata") or {})

    for forbidden in forbidden_phrase_fields:
        if isinstance(source_meta, dict) and forbidden in source_meta:
            fail(f"Forbidden phrase field present in source_metadata: {forbidden}")

    structure = uduc.get("structure") or {}
    if not isinstance(structure, dict):
        fail("structure must be a dictionary")

    for key in ["paragraphs", "heading_map", "section_count", "paragraph_count", "document_order", "structure_version", "boundary"]:
        if key not in structure:
            fail(f"Missing structure field: {key}")

    if structure.get("paragraph_count", 0) < 1:
        fail("structure.paragraph_count must be at least 1")

    if structure.get("boundary", {}).get("modifies_content_body") is not False:
        fail("structure boundary must confirm content_body is not modified")
    boundary = ((uduc.get("metadata") or {}).get("boundary") or {})
    for key in [
        "performs_extraction",
        "performs_cleaning",
        "performs_phrase_extraction",
        "performs_semantic_analysis",
        "creates_uucd",
    ]:
        if boundary.get(key) is not False:
            fail(f"Boundary violation: {key} is not false")

    explanation = explain_uploaded_document_unified_content_v1()

    print("VERIFICATION 6D UDUC BUILD PASSED")
    print("UDUC path:", result.get("uduc_path"))
    print("Canonical content field:", explanation.get("canonical_content_field"))
    print("Document ID:", uduc.get("document_id"))
    print("Content body length:", len(uduc.get("content_body") or ""))


if __name__ == "__main__":
    main()


