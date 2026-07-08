from __future__ import annotations

from pathlib import Path

from backend.server.stores.universal_article_body_store import (
    build_universal_article_body_store_from_uucd_payload_v2,
    explain_universal_article_body_store_v2,
)


def fail(msg: str):
    raise AssertionError(msg)


def main():
    workspace_id = "ws_verification_6g"

    website_body = "Website body for the universal article body store."
    upload_body = "Uploaded document body for the universal article body store."

    uucd_payload = {
        "schema_version": "uucd_collection_v1",
        "workspace_id": workspace_id,
        "documents": [
            {
                "schema_version": "universal_unified_content_document_v1",
                "pipeline_version": "verification_6e_uucd_convergence_v1",
                "workspace_id": workspace_id,
                "document_id": "WEB_DOC_6G",
                "source_type": "website",
                "source_format": "html",
                "source_identity": {"url": "https://example.com/page"},
                "title": "Website Body Test",
                "content_body": website_body,
                "metadata": {},
            },
            {
                "schema_version": "universal_unified_content_document_v1",
                "pipeline_version": "verification_6e_uucd_convergence_v1",
                "workspace_id": workspace_id,
                "document_id": "UPLOAD_DOC_6G",
                "source_type": "uploaded_document",
                "source_format": "docx",
                "source_identity": {"original_filename": "sample.docx"},
                "title": "Uploaded Body Test",
                "content_body": upload_body,
                "metadata": {},
            },
        ],
    }

    result = build_universal_article_body_store_from_uucd_payload_v2(
        workspace_id=workspace_id,
        uucd_payload=uucd_payload,
    )

    if not result.get("ok"):
        fail("Body store builder returned ok=false")

    index = result.get("index") or {}
    bodies = index.get("bodies") or []

    if len(bodies) != 2:
        fail(f"Expected 2 bodies, got {len(bodies)}")

    by_doc = {b.get("document_id"): b for b in bodies}

    for doc_id, expected in {
        "WEB_DOC_6G": website_body,
        "UPLOAD_DOC_6G": upload_body,
    }.items():
        rec = by_doc.get(doc_id)
        if not rec:
            fail(f"Missing body record: {doc_id}")

        ref = Path(rec.get("body_ref") or "")
        if not ref.exists():
            fail(f"Missing body file: {ref}")

        stored = ref.read_text(encoding="utf-8")
        if stored != expected:
            fail(f"Body text was modified for {doc_id}")

        if rec.get("body_length") != len(expected):
            fail(f"Wrong body_length for {doc_id}")

        if not rec.get("content_hash"):
            fail(f"Missing content_hash for {doc_id}")

        if rec.get("uucd_document_id") != doc_id:
            fail(f"Bad UUCD mapping for {doc_id}")

    counts = index.get("counts", {}).get("by_source_type", {})
    if counts.get("website") != 1:
        fail("Website source count incorrect")

    if counts.get("uploaded_document") != 1:
        fail("Uploaded document source count incorrect")

    boundary = index.get("boundary") or {}
    for key in [
        "performs_extraction",
        "performs_cleaning",
        "performs_phrase_extraction",
        "performs_semantic_analysis",
        "modifies_content_body",
    ]:
        if boundary.get(key) is not False:
            fail(f"Boundary violation: {key}")

    explanation = explain_universal_article_body_store_v2()

    print("VERIFICATION 6G UNIVERSAL ARTICLE BODY STORE PATCH PASSED")
    print("Body index path:", result.get("body_index_path"))
    print("Bodies written:", result.get("bodies_written"))
    print("Missing bodies:", result.get("missing_bodies"))
    print("Duplicate hashes:", result.get("duplicate_hashes"))
    print("Next stage:", explanation.get("next_stage"))


if __name__ == "__main__":
    main()
