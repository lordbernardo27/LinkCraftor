"""
Uploaded Document Registry-to-Active Target Set Pipeline
Document Pre-validation Entry

Entry-point scope only:

UPLOADED DOCUMENT
    -> Uploaded Document Registry-to-Active Target Set Pipeline
    -> Document Pre-validation

This component validates that the uploaded document has the minimum identity
and canonical-content information required before later registry processing.

It does not execute:
- Document Ingestion
- Document Normalization
- Document Identity Generation
- Document Metadata Building
- Document Target Record Generation
- Document Registry persistence
- Active Target Set mutation
- Resolver execution
"""

from __future__ import annotations

from typing import Any, Dict


def _read_string(
    source: Dict[str, Any],
    *keys: str,
) -> str:
    for key in keys:
        value = source.get(key)

        if value is None:
            continue

        cleaned = str(value).strip()

        if cleaned:
            return cleaned

    return ""


def run_document_pre_validation(
    *,
    workspace_id: str,
    document_id: str,
    unified_content: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Validate the Pipeline 3 entry contract without executing downstream stages.
    """

    clean_workspace_id = str(workspace_id or "").strip()
    clean_document_id = str(document_id or "").strip()

    if not clean_workspace_id:
        raise ValueError("workspace_id is required.")

    if not clean_document_id:
        raise ValueError("document_id is required.")

    if not isinstance(unified_content, dict):
        raise TypeError("unified_content must be a dictionary.")

    content_body = _read_string(
        unified_content,
        "content_body",
        "body_text",
        "content_text",
        "text",
        "extracted_text",
    )

    content_html = _read_string(
        unified_content,
        "content_html",
        "body_html",
        "html",
        "extracted_html",
    )

    title = _read_string(
        unified_content,
        "title",
        "document_title",
        "h1",
    )

    source_format = _read_string(
        unified_content,
        "source_format",
        "format",
        "extension",
        "ext",
    )

    validation_errors = []

    if not content_body and not content_html:
        validation_errors.append(
            "Unified content contains no usable body text or HTML."
        )

    valid = len(validation_errors) == 0

    return {
        "ok": valid,
        "pipeline": (
            "uploaded_document_registry_to_active_target_set_pipeline"
        ),
        "stage": "document_pre_validation",
        "workspace_id": clean_workspace_id,
        "document_id": clean_document_id,
        "status": (
            "DOCUMENT_PRE_VALIDATION_PASSED"
            if valid
            else "DOCUMENT_PRE_VALIDATION_FAILED"
        ),
        "executed": True,
        "valid": valid,
        "validation_errors": validation_errors,
        "observed_fields": {
            "has_content_body": bool(content_body),
            "has_content_html": bool(content_html),
            "has_title": bool(title),
            "has_source_format": bool(source_format),
        },
    }


__all__ = [
    "run_document_pre_validation",
]
