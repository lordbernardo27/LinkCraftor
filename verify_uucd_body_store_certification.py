from __future__ import annotations

from pathlib import Path

from backend.server.stores.universal_article_body_store import (
    build_universal_article_body_store_from_uucd_payload_v2,
)
from backend.server.stores.uucd_body_store_certification import (
    certify_uucd_body_store_v1,
    explain_uucd_body_store_certification_v1,
)


def fail(msg: str):
    raise AssertionError(msg)


def main():
    workspace_id = "ws_verification_6i"

    website_body = "Certified website body."
    upload_body = "Certified uploaded document body."

    uucd_payload = {
        "schema_version": "uucd_collection_v1",
        "workspace_id": workspace_id,
        "documents": [
            {
                "schema_version": "universal_unified_content_document_v1",
                "workspace_id": workspace_id,
                "document_id": "WEB_DOC_6I",
                "source_type": "website",
                "source_format": "html",
                "title": "Website Certified",
                "content_body": website_body,
                "metadata": {},
            },
            {
                "schema_version": "universal_unified_content_document_v1",
                "workspace_id": workspace_id,
                "document_id": "UPLOAD_DOC_6I",
                "source_type": "uploaded_document",
                "source_format": "docx",
                "title": "Upload Certified",
                "content_body": upload_body,
                "metadata": {},
            },
        ],
    }

    body_result = build_universal_article_body_store_from_uucd_payload_v2(
        workspace_id=workspace_id,
        uucd_payload=uucd_payload,
    )

    body_index = body_result["index"]

    lifecycle_registry = {
        "schema_version": "source_lifecycle_control_v1",
        "workspace_id": workspace_id,
        "sources": {
            "website::example.com": {
                "source_type": "website",
                "source_id": "example.com",
                "status": "active",
                "document_ids": ["WEB_DOC_6I"],
            },
            "uploaded_document::upload": {
                "source_type": "uploaded_document",
                "source_id": "upload",
                "status": "active",
                "document_ids": ["UPLOAD_DOC_6I"],
            },
        },
        "events": [],
    }

    asset_version_registry = {
        "schema_version": "source_asset_versions_v1",
        "workspace_id": workspace_id,
        "assets": [
            {"asset_id": "asset_web_6i", "document_id": "WEB_DOC_6I"},
            {"asset_id": "asset_upload_6i", "document_id": "UPLOAD_DOC_6I"},
        ],
    }

    authorization_payload = {
        "schema_version": "source_authorization_v1",
        "workspace_id": workspace_id,
        "counts": {
            "unauthorized_documents_quarantined": 0,
        },
    }

    result = certify_uucd_body_store_v1(
        workspace_id=workspace_id,
        uucd_payload=uucd_payload,
        body_index=body_index,
        lifecycle_registry=lifecycle_registry,
        asset_version_registry=asset_version_registry,
        authorization_payload=authorization_payload,
    )

    cert = result["certification"]

    if not cert.get("certified"):
        fail(f"Certification failed: {cert.get('problems')}")

    if not cert.get("semantic_ready"):
        fail("Certification did not mark semantic_ready=true")

    if cert.get("certification_level") != "gold":
        fail("Certification level should be gold")

    if cert.get("next_stage") != "Phase 4.6.1 Semantic Article Reader":
        fail("Wrong next stage")

    for key in ["uucd", "body_store", "authorization", "lifecycle", "version_registry", "duplicates"]:
        if not cert.get("verification", {}).get(key, {}).get("ok"):
            fail(f"Verification key failed: {key}")

    explanation = explain_uucd_body_store_certification_v1()

    print("VERIFICATION 6I UUCD / BODY STORE CERTIFICATION PASSED")
    print("Certification path:", result.get("certification_path"))
    print("Certified:", cert.get("certified"))
    print("Semantic ready:", cert.get("semantic_ready"))
    print("Certification level:", cert.get("certification_level"))
    print("Next stage:", explanation.get("next_stage_when_certified"))


if __name__ == "__main__":
    main()
