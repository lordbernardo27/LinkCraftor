from __future__ import annotations

import hashlib
from typing import Any, Dict

from backend.server.stores.website_unified_content_store import (
    get_website_unified_content_document_v1,
)


def _normalize_for_integrity_v1(text: str) -> str:
    return "\n".join(
        line.strip()
        for line in str(text or "").replace("\r\n", "\n").replace("\r", "\n").split("\n")
        if line.strip()
    )


def content_hash_v1(text: str) -> str:
    normalized = _normalize_for_integrity_v1(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def check_website_article_integrity_v1(
    *,
    workspace_id: str,
    extracted_article_body: str,
    url: str | None = None,
    content_id: str | None = None,
) -> Dict[str, Any]:
    stored = get_website_unified_content_document_v1(
        workspace_id=workspace_id,
        url=url,
        content_id=content_id,
    )

    if not stored:
        return {
            "status": "not_found",
            "passed": False,
            "workspace_id": workspace_id,
            "url": url,
            "content_id": content_id,
            "message": "No stored crawled article body found.",
        }

    stored_body = stored.get("primary_content") or stored.get("article_body") or ""

    extracted_norm = _normalize_for_integrity_v1(extracted_article_body)
    stored_norm = _normalize_for_integrity_v1(stored_body)

    extracted_hash = content_hash_v1(extracted_article_body)
    stored_hash = content_hash_v1(stored_body)

    exact_match = extracted_norm == stored_norm

    return {
        "status": "checked",
        "passed": exact_match,
        "workspace_id": workspace_id,
        "url": stored.get("url"),
        "content_id": stored.get("content_id"),
        "extracted_hash": extracted_hash,
        "stored_hash": stored_hash,
        "hash_match": extracted_hash == stored_hash,
        "exact_match": exact_match,
        "extracted_word_count": len(extracted_norm.split()),
        "stored_word_count": len(stored_norm.split()),
        "extracted_content_length": len(extracted_norm),
        "stored_content_length": len(stored_norm),
        "length_delta": abs(len(extracted_norm) - len(stored_norm)),
        "message": "Stored article body matches extracted article body." if exact_match else "Stored article body differs from extracted article body.",
    }
