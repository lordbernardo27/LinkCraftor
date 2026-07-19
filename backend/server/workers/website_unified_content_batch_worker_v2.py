from __future__ import annotations

from typing import Any

from backend.server.stores.article_validation_store import (
    load_article_validation_store_v2,
)

from backend.server.stores.website_unified_content_builder_v2 import (
    build_website_unified_content_document_v2,
)

from backend.server.stores.website_unified_content_verifier_v2 import (
    verify_website_unified_content_document_v2,
)

from backend.server.stores.website_unified_content_certifier_v2 import (
    certify_website_unified_content_document_v2,
)

from backend.server.stores.website_unified_content_store import (
    upsert_website_unified_content_document_v1,
)


WORKER_VERSION = (
    "website_unified_content_batch_worker_v2"
)


def run_website_unified_content_batch_v2(
    *,
    workspace_id: str,
    assigned_html_ids: list[str],
    batch_id: str = "",
    batch_index: int | None = None,
    batch_count: int | None = None,
) -> dict[str, Any]:
    """
    Build Website Unified Content from certified
    Article Validation v2 records.
    """

    validation_store = (
        load_article_validation_store_v2(
            workspace_id
        )
    )

    articles = (
        validation_store.get("articles")
        or {}
    )

    attempted = 0
    succeeded = 0
    failed = 0

    successes: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for html_id in assigned_html_ids:

        attempted += 1

        article = articles.get(
            html_id
        )

        if not isinstance(
            article,
            dict,
        ):

            failed += 1

            errors.append({
                "html_id":
                    html_id,

                "error_type":
                    "missing_certified_article",
            })

            continue

        if not article.get(
            "eligible_for_wuc",
            False,
        ):
            continue

        try:

            document = (
                build_website_unified_content_document_v2(
                    certified_article=article,
                )
            )

            verification = (
                verify_website_unified_content_document_v2(
                    document=document,
                )
            )

            if not verification.get(
                "passed",
                False,
            ):

                failed += 1

                errors.append({
                    "html_id":
                        html_id,

                    "error_type":
                        "verification_failed",

                    "errors":
                        verification.get(
                            "errors",
                            [],
                        ),
                })

                continue

            certified_document = (
                certify_website_unified_content_document_v2(
                    document=document,
                    verification_result=verification,
                )
            )

            stored = (
                upsert_website_unified_content_document_v1(
                    workspace_id=workspace_id,
                    **certified_document,
                )
            )

            succeeded += 1

            successes.append({
                "html_id":
                    html_id,

                "content_id":
                    stored.get(
                        "content_id"
                    ),

                "url":
                    stored.get(
                        "url"
                    ),
            })

        except Exception as exc:

            failed += 1

            errors.append({
                "html_id":
                    html_id,

                "error_type":
                    "worker_exception",

                "error":
                    f"{type(exc).__name__}: {exc}",
            })

    return {
        "ok":
            failed == 0,

        "worker_version":
            WORKER_VERSION,

        "workspace_id":
            workspace_id,

        "batch_id":
            batch_id,

        "batch_index":
            batch_index,

        "batch_count":
            batch_count,

        "processing": {
            "assigned":
                len(
                    assigned_html_ids
                ),

            "attempted":
                attempted,

            "succeeded":
                succeeded,

            "failed":
                failed,
        },

        "success_sample":
            successes[:10],

        "error_sample":
            errors[:25],
    }
