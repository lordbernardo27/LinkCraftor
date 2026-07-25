from __future__ import annotations

import hashlib
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any


BUILDER_VERSION = (
    "website_unified_content_builder_v2"
)


def _sha256(value: str) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def build_website_unified_content_document_v2(
    *,
    certified_article: dict[str, Any],
) -> dict[str, Any]:
    """
    Build a canonical Website Unified Content document
    from a certified Article Validation v2 record.

    This builder performs no extraction,
    no reconstruction,
    no validation,
    and no UUCD generation.
    """

    article = deepcopy(
        certified_article
    )

    content_body = str(
        article.get("content_body")
        or ""
    ).strip()

    title = str(
        article.get("title")
        or ""
    ).strip()

    h1 = str(
        article.get("h1")
        or ""
    ).strip()

    url = str(
        article.get("url")
        or ""
    ).strip()

    html_id = str(
        article.get("html_id")
        or ""
    ).strip()

    headings = list(
        article.get("headings")
        or []
    )

    metadata = dict(
        article.get("metadata")
        or {}
    )

    quality = dict(
        article.get("quality")
        or {}
    )

    semantic = dict(
        article.get(
            "semantic_features"
        )
        or {}
    )

    metadata.update(
        {
            "builder": BUILDER_VERSION,
            "built_at": datetime.now(
                UTC
            ).isoformat(),
            "source": "article_validation_v2",
            "html_id": html_id,
        }
    )

    semantic.update(
        {
            "semantic_ready": True,
            "source_pipeline":
                BUILDER_VERSION,
            "source_type":
                "website",
        }
    )

    return {
        "content_id":
            article.get("content_id"),
        "document_id":
            article.get("document_id"),
        "workspace_id":
            article.get("workspace_id"),
        "html_id":
            html_id,
        "url":
            url,
        "title":
            title,
        "h1":
            h1,
        "headings":
            headings,
        "article_body":
            content_body,
        "content_hash":
            _sha256(
                content_body
            ),
        "metadata":
            metadata,
        "quality":
            quality,
        "semantic_features":
            semantic,
    }
