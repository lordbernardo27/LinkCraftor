from __future__ import annotations

from backend.server.stores.universal_unified_content_document_convergence import (
    build_and_write_uucd_from_uduc_v1,
    build_and_write_uucd_from_wuc_v1,
    explain_uucd_convergence_v1,
)


def fail(msg: str):
    raise AssertionError(msg)


def verify_uucd(uucd: dict, expected_body: str, expected_source_type: str):
    required = [
        "schema_version",
        "pipeline_version",
        "workspace_id",
        "document_id",
        "source_type",
        "source_format",
        "source_identity",
        "title",
        "h1",
        "headings",
        "content_body",
        "structure",
        "metadata",
        "created_at",
    ]

    missing = [k for k in required if k not in uucd]
    if missing:
        fail(f"Missing UUCD fields: {missing}")

    if uucd["content_body"] != expected_body:
        fail("UUCD content_body was modified")

    if uucd["source_type"] != expected_source_type:
        fail(f"Wrong source_type: {uucd['source_type']}")

    boundary = ((uucd.get("metadata") or {}).get("boundary") or {})
    for key in [
        "performs_extraction",
        "performs_cleaning",
        "performs_phrase_extraction",
        "performs_semantic_analysis",
        "modifies_content_body",
    ]:
        if boundary.get(key) is not False:
            fail(f"Boundary violation: {key} is not false")


def main():
    upload_body = "Uploaded document body.\n\nThis must pass unchanged into the UUCD."

    uduc = {
        "schema_version": "uploaded_document_unified_content_v1",
        "pipeline_version": "verification_6d_uduc_v1",
        "workspace_id": "ws_uucd_upload_test",
        "document_id": "DOC_UPLOAD_TEST",
        "source_type": "uploaded_document",
        "source_format": "docx",
        "original_filename": "sample.docx",
        "stored_filename": "DOC_UPLOAD_TEST__sample.docx",
        "stored_path": "backend/server/data/docs/ws_uucd_upload_test/DOC_UPLOAD_TEST__sample.docx",
        "title": "Uploaded Test",
        "h1": "Uploaded Test",
        "headings": ["Uploaded Test"],
        "content_body": upload_body,
        "structure": {
            "paragraph_count": 2,
            "estimated_character_count": len(upload_body),
        },
        "metadata": {
            "extension": ".docx",
        },
        "extraction_status": "success",
        "extraction_confidence": 0.91,
    }

    upload_result = build_and_write_uucd_from_uduc_v1(uduc)
    upload_uucd = upload_result["uucd"]
    verify_uucd(upload_uucd, upload_body, "uploaded_document")

    website_body = "Website article body.\n\nThis must also pass unchanged into the UUCD."

    wuc = {
        "schema_version": "website_unified_content_v1",
        "pipeline_version": "website_pipeline_v1",
        "workspace_id": "ws_uucd_website_test",
        "document_id": "WEB_TEST",
        "source_format": "html",
        "url": "https://example.com/test",
        "canonical_url": "https://example.com/test",
        "title": "Website Test",
        "h1": "Website Test",
        "headings": ["Website Test"],
        "content_body": website_body,
        "structure": {
            "paragraph_count": 2,
            "estimated_character_count": len(website_body),
        },
        "metadata": {},
    }

    website_result = build_and_write_uucd_from_wuc_v1(wuc)
    website_uucd = website_result["uucd"]
    verify_uucd(website_uucd, website_body, "website")

    explanation = explain_uucd_convergence_v1()

    print("VERIFICATION 6E UUCD PATCH PASSED")
    print("Canonical content field:", explanation.get("canonical_content_field"))
    print("Upload UUCD path:", upload_result.get("uucd_path"))
    print("Website UUCD path:", website_result.get("uucd_path"))
    print("Next stage:", explanation.get("next_stage"))


if __name__ == "__main__":
    main()
