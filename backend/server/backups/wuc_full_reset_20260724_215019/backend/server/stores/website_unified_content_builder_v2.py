"""Build a canonical transient Website Unified Content document."""

from __future__ import annotations

import hashlib
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any, Mapping


BUILDER_VERSION = (
    "website_unified_content_builder_v2_"
    "canonical_content_body_transient"
)


def _sha256(
    value: str,
) -> str:
    return hashlib.sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


def build_website_unified_content_document_v2(
    *,
    certified_article: Mapping[str, Any],
) -> dict[str, Any]:
    article = deepcopy(
        dict(
            certified_article
        )
    )

    content_body = str(
        article.get(
            "content_body"
        )
        or ""
    ).strip()

    if not content_body:
        raise ValueError(
            "Transient WUC source has no content_body."
        )

    title = str(
        article.get(
            "title"
        )
        or ""
    ).strip()

    h1 = str(
        article.get(
            "h1"
        )
        or title
    ).strip()

    url = str(
        article.get(
            "canonical_url"
        )
        or article.get(
            "url"
        )
        or ""
    ).strip()

    html_id = str(
        article.get(
            "html_id"
        )
        or article.get(
            "source_record_id"
        )
        or article.get(
            "document_id"
        )
        or ""
    ).strip()

    headings = list(
        article.get(
            "headings"
        )
        or []
    )

    structure = dict(
        article.get(
            "structure"
        )
        or {}
    )

    metadata = dict(
        article.get(
            "metadata"
        )
        or {}
    )

    quality = dict(
        article.get(
            "quality"
        )
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
            "builder":
                BUILDER_VERSION,

            "built_at":
                datetime.now(
                    UTC
                ).isoformat(),

            "source":
                "article_validation_pass_manifest",

            "html_id":
                html_id,

            "wuc_persistence_mode":
                "TRANSIENT",

            "intermediate_wuc_store_created":
                False,
        }
    )

    semantic.update(
        {
            "semantic_ready":
                True,

            "source_pipeline":
                BUILDER_VERSION,

            "source_type":
                "website",
        }
    )

    return {
        "content_id":
            article.get(
                "content_id"
            ),

        "document_id":
            article.get(
                "document_id"
            )
            or html_id,

        "workspace_id":
            article.get(
                "workspace_id"
            ),

        "html_id":
            html_id,

        "url":
            url,

        "canonical_url":
            url,

        "title":
            title,

        "h1":
            h1,

        "headings":
            headings,

        "content_body":
            content_body,

        "content_hash":
            _sha256(
                content_body
            ),

        "structure":
            structure,

        "metadata":
            metadata,

        "quality":
            quality,

        "semantic_features":
            semantic,
    }
