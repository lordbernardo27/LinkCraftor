from __future__ import annotations

import hashlib
from typing import Any, Dict

from backend.server.stores.unified_content_document_convergence import (
    get_unified_content_document_v1,
)


def normalize_content_for_integrity_v1(text: str) -> str:
    return "\n".join(
        line.strip()
        for line in str(text or "").replace("\r\n", "\n").replace("\r", "\n").split("\n")
        if line.strip()
    )


def unified_content_hash_v1(text: str) -> str:
    normalized = normalize_content_for_integrity_v1(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def check_unified_content_integrity_v1(
    *,
    workspace_id: str,
    extracted_content: str,
    document_id: str | None = None,
    source_identifier: str | None = None,
    source_type: str | None = None,
) -> Dict[str, Any]:
    document = get_unified_content_document_v1(
        workspace_id=workspace_id,
        document_id=document_id,
        source_identifier=source_identifier,
        source_type=source_type,
    )

    if not document:
        return {
            "status": "not_found",
            "passed": False,
            "workspace_id": workspace_id,
            "document_id": document_id,
            "source_identifier": source_identifier,
            "source_type": source_type,
            "message": "No stored Unified Content Document found.",
        }

    stored_content = document.get("primary_content", "")

    extracted_norm = normalize_content_for_integrity_v1(extracted_content)
    stored_norm = normalize_content_for_integrity_v1(stored_content)

    extracted_hash = unified_content_hash_v1(extracted_content)
    stored_hash = unified_content_hash_v1(stored_content)

    exact_match = extracted_norm == stored_norm

    return {
        "status": "checked",
        "passed": exact_match,
        "document_id": document.get("document_id"),
        "workspace_id": workspace_id,
        "source_identifier": document.get("source_identifier"),
        "source_type": document.get("source_type"),
        "schema_version": document.get("schema_version"),
        "extracted_hash": extracted_hash,
        "stored_hash": stored_hash,
        "hash_match": extracted_hash == stored_hash,
        "exact_match": exact_match,
        "extracted_word_count": len(extracted_norm.split()),
        "stored_word_count": len(stored_norm.split()),
        "extracted_content_length": len(extracted_norm),
        "stored_content_length": len(stored_norm),
        "length_delta": abs(len(extracted_norm) - len(stored_norm)),
        "message": "Stored Unified Content Document matches extracted content." if exact_match else "Stored Unified Content Document differs from extracted content.",
    }
