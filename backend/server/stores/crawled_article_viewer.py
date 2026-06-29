from __future__ import annotations

from typing import Any, Dict

from backend.server.stores.website_unified_content_store import (
    get_website_unified_content_document_v1,
)


def build_crawled_article_view_v1(
    *,
    workspace_id: str,
    url: str | None = None,
    content_id: str | None = None,
) -> Dict[str, Any]:
    document = get_website_unified_content_document_v1(
        workspace_id=workspace_id,
        url=url,
        content_id=content_id,
    )

    if not document:
        return {
            "status": "not_found",
            "workspace_id": workspace_id,
            "url": url,
            "content_id": content_id,
            "message": "No stored crawled article body found for this page.",
        }

    article_body = document.get("primary_content") or document.get("article_body") or ""

    return {
        "status": "found",
        "workspace_id": workspace_id,
        "content_id": document.get("content_id"),
        "url": document.get("url"),
        "title": document.get("title"),
        "h1": document.get("h1"),
        "headings": document.get("headings", []),
        "article_body": article_body,
        "word_count": document.get("word_count", len(str(article_body).split())),
        "content_length": document.get("content_length", len(str(article_body))),
        "source_type": document.get("source_type", "website_crawl"),
        "metadata": document.get("metadata", {}),
        "quality": document.get("quality", {}),
        "semantic_features": document.get("semantic_features", {}),
        "display": {
            "title": document.get("title") or document.get("h1") or document.get("url"),
            "subtitle": document.get("url"),
            "body": article_body,
            "stats": {
                "word_count": document.get("word_count", len(str(article_body).split())),
                "content_length": document.get("content_length", len(str(article_body))),
                "heading_count": len(document.get("headings", []) or []),
            },
        },
    }
