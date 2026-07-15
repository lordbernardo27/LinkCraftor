from __future__ import annotations

import html
import re
from typing import Any, Dict, List

from backend.server.stores.raw_website_html_store import (
    load_raw_website_html_store_v1,
)
from backend.server.stores.main_content_extraction_engine import (
    extract_main_content_from_html_v1,
)
from backend.server.stores.website_article_integrity_validator import (
    build_website_article_integrity_result_v1,
)
from backend.server.stores.article_validation_engine import (
    validate_article_v1,
)
from backend.server.stores.website_unified_content_store import (
    upsert_website_unified_content_document_v1,
)
from backend.server.stores.universal_unified_content_document_convergence import (
    build_and_write_uucd_from_wuc_v1,
)


WORKER_VERSION = (
    "website_unified_content_batch_worker_v2_raw_html_udare"
)


def _plain_html_text_v1(value: str) -> str:
    value = re.sub(
        r"(?is)<[^>]+>",
        " ",
        str(value or ""),
    )

    value = html.unescape(value)

    return re.sub(
        r"\s+",
        " ",
        value,
    ).strip()


def _extract_title_from_html_v1(
    html_text: str,
) -> str:
    match = re.search(
        r"(?is)<title\b[^>]*>(.*?)</title>",
        str(html_text or ""),
    )

    return (
        _plain_html_text_v1(match.group(1))
        if match
        else ""
    )


def _extract_h1_from_html_v1(
    html_text: str,
) -> str:
    match = re.search(
        r"(?is)<h1\b[^>]*>(.*?)</h1>",
        str(html_text or ""),
    )

    return (
        _plain_html_text_v1(match.group(1))
        if match
        else ""
    )


def run_website_unified_content_batch_v1(
    *,
    workspace_id: str,
    assigned_html_ids: List[str],
    batch_id: str = "",
    batch_index: int | None = None,
    batch_count: int | None = None,
) -> Dict[str, Any]:
    """
    Convert assigned Raw HTML Store records into WUC and UUCD.
    """

    raw_store = load_raw_website_html_store_v1(
        workspace_id
    )

    raw_pages = raw_store.get("pages") or {}

    attempted = 0
    succeeded = 0
    failed = 0
    missing_raw_record = 0
    extraction_failed = 0
    article_integrity_failed = 0
    website_store_failed = 0
    uucd_failed = 0

    successes: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    for html_id in assigned_html_ids:
        attempted += 1

        record = raw_pages.get(html_id)

        if not isinstance(record, dict):
            missing_raw_record += 1
            failed += 1

            errors.append({
                "html_id": html_id,
                "error_type":
                    "missing_raw_html_record",
            })

            continue

        url = str(
            record.get("url") or ""
        ).strip()

        raw_html = str(
            record.get("html") or ""
        )

        html_title = _extract_title_from_html_v1(
            raw_html
        )

        html_h1 = _extract_h1_from_html_v1(
            raw_html
        )

        title = str(
            record.get("title")
            or html_title
            or html_h1
            or ""
        ).strip()

        if not url or not raw_html.strip():
            missing_raw_record += 1
            failed += 1

            errors.append({
                "html_id": html_id,
                "url": url,
                "error_type":
                    "empty_raw_html_or_url",
            })

            continue

        try:
            extraction = (
                extract_main_content_from_html_v1(
                    html_text=raw_html,
                    url=url,
                    title=title,
                    metadata={
                        "html_id": html_id,
                        "source_stage":
                            "raw_website_html_store",
                        "batch_id": batch_id,
                        "batch_index": batch_index,
                        "batch_count": batch_count,
                    },
                )
            )

            main_content = str(
                extraction.get("article_body")
                or extraction.get(
                    "main_content"
                )
                or ""
            )

            if not main_content.strip():
                extraction_failed += 1
                failed += 1

                errors.append({
                    "html_id": html_id,
                    "url": url,
                    "error_type":
                        "main_content_empty",
                })

                continue

            integrity = (
                build_website_article_integrity_result_v1(
                    raw_main_html=raw_html,
                    raw_article_text=main_content,
                    headings=extraction.get(
                        "headings",
                        [],
                    ),
                    title=(
                        title
                        or extraction.get(
                            "title",
                            "",
                        )
                    ),
                    url=url,
                    metadata={
                        "html_id": html_id,
                        "source_stage":
                            WORKER_VERSION,
                        "batch_id": batch_id,
                        "batch_index": batch_index,
                        "batch_count": batch_count,
                    },
                )
            )

            article_text = str(
                integrity.get("content_body")
                or integrity.get(
                    "cleaned_article_text"
                )
                or main_content
            )

            if not article_text.strip():
                article_integrity_failed += 1
                failed += 1

                errors.append({
                    "html_id": html_id,
                    "url": url,
                    "error_type":
                        "integrity_article_text_empty",
                })

                continue

            validation = validate_article_v1(
                cleaned_article_text=
                    article_text,
                title=(
                    title
                    or extraction.get(
                        "title",
                        "",
                    )
                ),
                headings=integrity.get(
                    "headings",
                    extraction.get(
                        "headings",
                        [],
                    ),
                ),
                removed_sections=integrity.get(
                    "removed_sections",
                    [],
                ),
                metadata={
                    "html_id": html_id,
                    "source_stage":
                        WORKER_VERSION,
                    "batch_id": batch_id,
                    "batch_index": batch_index,
                    "batch_count": batch_count,
                },
            )

            try:
                website_doc = (
                    upsert_website_unified_content_document_v1(
                        workspace_id=
                            workspace_id,
                        url=url,
                        title=(
                            title
                            or extraction.get(
                                "title",
                                "",
                            )
                        ),
                        h1=str(
                            extraction.get("h1")
                            or html_h1
                            or ""
                        ),
                        article_body=
                            article_text,
                        headings=integrity.get(
                            "headings",
                            extraction.get(
                                "headings",
                                [],
                            ),
                        ),
                        metadata={
                            "html_id": html_id,
                            "source_stage":
                                "raw_website_html_store",
                            "source_pipeline":
                                WORKER_VERSION,
                            "batch_id": batch_id,
                            "batch_index":
                                batch_index,
                            "batch_count":
                                batch_count,
                            "raw_html_length":
                                len(raw_html),
                            "reconstruction": {
                                "extraction_engine":
                                    extraction.get(
                                        "engine"
                                    ),
                                "reconstruction_engine":
                                    extraction.get(
                                        "reconstruction_engine"
                                    ),
                                "selected_tag":
                                    extraction.get(
                                        "selected_tag"
                                    ),
                                "word_count":
                                    extraction.get(
                                        "word_count"
                                    ),
                                "content_length":
                                    extraction.get(
                                        "content_length"
                                    ),
                                "candidate_count":
                                    extraction.get(
                                        "candidate_count"
                                    ),
                            },
                            "integrity_statistics":
                                integrity.get(
                                    "statistics",
                                    {},
                                ),
                            "validation":
                                validation,
                        },
                        quality={
                            "validation_passed":
                                validation.get(
                                    "passed"
                                ),
                            "quality_grade":
                                validation.get(
                                    "quality_grade"
                                ),
                            "validation_score":
                                validation.get(
                                    "validation_score"
                                ),
                            "warnings":
                                validation.get(
                                    "warnings",
                                    [],
                                ),
                            "rejection_reasons":
                                validation.get(
                                    "rejection_reasons",
                                    [],
                                ),
                        },
                        semantic_features={
                            "semantic_ready": bool(
                                validation.get(
                                    "eligible_for_unified_content_document",
                                    False,
                                )
                            ),
                            "source_pipeline":
                                WORKER_VERSION,
                            "source_type":
                                "website",
                        },
                    )
                )

            except Exception as exc:
                website_store_failed += 1
                failed += 1

                errors.append({
                    "html_id": html_id,
                    "url": url,
                    "error_type":
                        "website_store_write_failed",
                    "error": str(exc),
                })

                continue

            try:
                uucd_result = (
                    build_and_write_uucd_from_wuc_v1(
                        website_doc
                    )
                )

            except Exception as exc:
                uucd_failed += 1
                failed += 1

                errors.append({
                    "html_id": html_id,
                    "url": url,
                    "error_type":
                        "uucd_write_failed",
                    "error": str(exc),
                    "website_content_id":
                        website_doc.get(
                            "content_id"
                        ),
                })

                continue

            succeeded += 1

            successes.append({
                "html_id": html_id,
                "url": url,
                "website_content_id":
                    website_doc.get(
                        "content_id"
                    ),
                "uucd_path":
                    uucd_result.get(
                        "uucd_path"
                    ),
                "semantic_ready": bool(
                    website_doc.get(
                        "semantic_features",
                        {},
                    ).get("semantic_ready")
                ),
            })

        except Exception as exc:
            failed += 1

            errors.append({
                "html_id": html_id,
                "url": url,
                "error_type":
                    "unexpected_processing_error",
                "error":
                    f"{type(exc).__name__}: {exc}",
            })

    return {
        "ok": failed == 0,
        "workspace_id": workspace_id,
        "stage":
            "raw_html_to_website_unified_content_and_uucd",
        "worker_version":
            WORKER_VERSION,
        "input_store":
            "raw_website_html_store_v1",
        "html_cleaner_used":
            False,
        "clean_html_store_used":
            False,
        "batch_id": batch_id,
        "batch_index": batch_index,
        "batch_count": batch_count,
        "processing": {
            "assigned":
                len(assigned_html_ids),
            "attempted":
                attempted,
            "succeeded":
                succeeded,
            "failed":
                failed,
            "missing_raw_record":
                missing_raw_record,
            "extraction_failed":
                extraction_failed,
            "article_integrity_failed":
                article_integrity_failed,
            "website_store_failed":
                website_store_failed,
            "uucd_failed":
                uucd_failed,
        },
        "success_sample":
            successes[:10],
        "error_sample":
            errors[:25],
    }
