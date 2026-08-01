"""
Uploaded Document-to-Highlight Pipeline

Entry-point scope only:

UPLOADED DOCUMENT
    -> Uploaded Document-to-Highlight Pipeline
    -> Smart Phrase Extractor

Downstream stages remain in their existing production locations and are not
executed or migrated by this coordinator during the pipeline-separation phase.
"""

from __future__ import annotations

from typing import Any, Dict

from backend.server.stores.smart_phrase_extractor import (
    extract_smart_phrases,
)


def _read_string(
    extraction_result: Dict[str, Any],
    *keys: str,
) -> str:
    for key in keys:
        value = extraction_result.get(key)

        if value is None:
            continue

        cleaned = str(value).strip()

        if cleaned:
            return cleaned

    return ""


def run_uploaded_document_to_highlight_pipeline(
    *,
    workspace_id: str,
    document_id: str,
    extraction_result: Dict[str, Any] | None = None,
    max_candidates: int = 500,
    vertical: str = "general",
) -> Dict[str, Any]:
    """
    Canonical entry point for the Uploaded Document-to-Highlight Pipeline.

    This coordinator delegates only to the existing Smart Phrase Extractor.
    """

    clean_workspace_id = str(workspace_id or "").strip()
    clean_document_id = str(document_id or "").strip()

    if not clean_workspace_id:
        raise ValueError("workspace_id is required.")

    if not clean_document_id:
        raise ValueError("document_id is required.")

    if not isinstance(extraction_result, dict):
        raise TypeError("extraction_result must be a dictionary.")

    text = _read_string(
        extraction_result,
        "text",
        "content_text",
        "body_text",
        "content_body",
        "extracted_text",
    )

    html = _read_string(
        extraction_result,
        "html",
        "content_html",
        "body_html",
        "extracted_html",
    )

    title = _read_string(
        extraction_result,
        "title",
        "document_title",
        "extracted_title",
        "h1",
    )

    if not text and not html and not title:
        raise ValueError(
            "extraction_result contains no usable text, HTML, or title."
        )

    safe_max_candidates = max(
        1,
        min(int(max_candidates or 500), 5000),
    )

    safe_vertical = str(
        vertical or "general"
    ).strip() or "general"

    phrase_candidates = extract_smart_phrases(
        text=text,
        html=html,
        title=title,
        doc_id=clean_document_id,
        max_candidates=safe_max_candidates,
        workspace_id=clean_workspace_id,
        vertical=safe_vertical,
    )

    if not isinstance(phrase_candidates, list):
        raise RuntimeError(
            "Smart Phrase Extractor returned a non-list result."
        )

    return {
        "ok": True,
        "pipeline": "uploaded_document_to_highlight_pipeline",
        "workspace_id": clean_workspace_id,
        "document_id": clean_document_id,
        "status": "SMART_PHRASE_EXTRACTOR_COMPLETED",
        "executed": True,
        "entry_point": "smart_phrase_extractor",
        "phrase_candidates": phrase_candidates,
        "phrase_candidate_count": len(phrase_candidates),
    }


__all__ = [
    "run_uploaded_document_to_highlight_pipeline",
]
