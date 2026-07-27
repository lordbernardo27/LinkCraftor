from __future__ import annotations

from typing import Any, Dict

from backend.server.stores.universal_unified_content_document_convergence import (
    get_universal_unified_content_document_v1,
)


def build_universal_unified_content_document_view_v1(
    *,
    workspace_id: str,
    document_id: str | None = None,
    source_identifier: str | None = None,
    source_type: str | None = None,
) -> Dict[str, Any]:
    document = get_universal_unified_content_document_v1(
        workspace_id=workspace_id,
        document_id=document_id,
        source_identifier=source_identifier,
        source_type=source_type,
    )

    if not document:
        return {
            "status": "not_found",
            "workspace_id": workspace_id,
            "document_id": document_id,
            "source_identifier": source_identifier,
            "source_type": source_type,
            "message": "No stored Universal Unified Content Document found.",
        }

    content = document.get("primary_content", "")
    metadata = document.get("metadata", {}) or {}
    headings = document.get("headings", []) or []

    return {
        "status": "found",
        "workspace_id": workspace_id,
        "document_id": document.get("document_id"),
        "schema_version": document.get("schema_version"),
        "source_identifier": document.get("source_identifier"),
        "source_type": document.get("source_type"),
        "title": document.get("title"),
        "page_type": document.get("page_type"),
        "headings": headings,
        "primary_content": content,
        "metadata": metadata,
        "quality": document.get("quality", {}),
        "semantic_features": document.get("semantic_features", {}),
        "display": {
            "title": document.get("title") or document.get("source_identifier"),
            "subtitle": document.get("source_identifier"),
            "source_type": document.get("source_type"),
            "body": content,
            "stats": {
                "word_count": metadata.get("word_count", len(str(content).split())),
                "content_length": metadata.get("content_length", len(str(content))),
                "heading_count": metadata.get("heading_count", len(headings)),
            },
        },
    }
