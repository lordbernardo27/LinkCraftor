from __future__ import annotations

import html
import re
from typing import Any

from backend.server.stores.raw_website_html_store import (
    load_raw_website_html_store_v1,
)
from backend.server.stores.universal_dom_article_reconstruction_engine import (
    reconstruct_universal_dom_article_v1,
)
from backend.server.stores.website_article_integrity_validator import (
    build_website_article_integrity_result_v1,
)
from backend.server.stores.article_validation_engine import (
    validate_article_v1,
)
from backend.server.stores.certified_website_article_store import (
    build_certified_website_article_v1,
    load_certified_website_article_store_v1,
    save_certified_website_article_store_v1,
)


WORKER_VERSION = (
    "certified_website_article_batch_worker_v1"
)

EXPECTED_UDARE_ENGINE = (
    "universal_dom_article_reconstruction_engine_v1_8"
)

EXPECTED_INTEGRITY_ENGINE = (
    "website_article_integrity_validator_v1_1_"
    "structured_non_mutating"
)

EXPECTED_VALIDATION_VERSION = (
    "article_validation_engine_v2_integrity_aware"
)


def _plain_html_text(
    value: str,
) -> str:
    value = re.sub(
        r"(?is)<[^>]+>",
        " ",
        str(value or ""),
    )

    value = html.unescape(
        value
    )

    return re.sub(
        r"\s+",
        " ",
        value,
    ).strip()


def _html_title(
    html_text: str,
) -> str:
    match = re.search(
        r"(?is)<title\b[^>]*>(.*?)</title>",
        str(html_text or ""),
    )

    return (
        _plain_html_text(
            match.group(1)
        )
        if match
        else ""
    )


def _html_h1(
    html_text: str,
) -> str:
    match = re.search(
        r"(?is)<h1\b[^>]*>(.*?)</h1>",
        str(html_text or ""),
    )

    return (
        _plain_html_text(
            match.group(1)
        )
        if match
        else ""
    )


def _result_passed(
    result: dict[str, Any],
) -> bool:
    value = result.get(
        "passed"
    )

    if isinstance(
        value,
        bool,
    ):
        return value

    checks = result.get(
        "checks"
    )

    return bool(
        isinstance(
            checks,
            dict,
        )
        and checks
        and all(
            item is True
            for item in checks.values()
        )
    )


def run_certified_website_article_batch_v1(
    *,
    workspace_id: str,
    assigned_html_ids: list[str],
    batch_id: str = "",
    batch_index: int | None = None,
    batch_count: int | None = None,
) -> dict[str, Any]:
    """
    Build and persist complete certified website articles.

    Pipeline boundary:
    Raw HTML -> UDARE -> Integrity -> Article Validation
    -> Certified Website Article Store -> STOP.
    """

    raw_store = load_raw_website_html_store_v1(
        workspace_id
    )

    raw_pages = (
        raw_store.get(
            "pages"
        )
        or {}
    )

    certified_store = (
        load_certified_website_article_store_v1(
            workspace_id
        )
    )

    certified_articles = (
        certified_store[
            "articles"
        ]
    )

    attempted = 0
    certified = 0
    quarantined = 0
    failed = 0

    missing_raw_record = 0
    reconstruction_failed = 0
    integrity_failed = 0
    validation_failed = 0
    store_build_failed = 0

    successes: list[
        dict[str, Any]
    ] = []

    quarantines: list[
        dict[str, Any]
    ] = []

    errors: list[
        dict[str, Any]
    ] = []

    for html_id in assigned_html_ids:
        attempted += 1

        record = raw_pages.get(
            html_id
        )

        if not isinstance(
            record,
            dict,
        ):
            missing_raw_record += 1
            failed += 1

            errors.append({
                "html_id":
                    html_id,

                "error_type":
                    "missing_raw_html_record",
            })

            continue

        url = str(
            record.get(
                "url"
            )
            or ""
        ).strip()

        raw_html = str(
            record.get(
                "html"
            )
            or ""
        )

        source_title = str(
            record.get(
                "title"
            )
            or _html_title(
                raw_html
            )
            or _html_h1(
                raw_html
            )
            or ""
        ).strip()

        if (
            not url
            or not raw_html.strip()
        ):
            missing_raw_record += 1
            failed += 1

            errors.append({
                "html_id":
                    html_id,

                "url":
                    url,

                "error_type":
                    "empty_raw_html_or_url",
            })

            continue

        try:
            reconstruction = (
                reconstruct_universal_dom_article_v1(
                    html_text=
                        raw_html,

                    url=
                        url,

                    title=
                        source_title,

                    metadata={
                        "workspace_id":
                            workspace_id,

                        "html_id":
                            html_id,

                        "batch_id":
                            batch_id,

                        "batch_index":
                            batch_index,

                        "batch_count":
                            batch_count,

                        "source_stage":
                            "raw_website_html_store",

                        "target_stage":
                            (
                                "certified_website_"
                                "article_store"
                            ),
                    },
                )
            )

        except Exception as exc:
            reconstruction_failed += 1
            failed += 1

            errors.append({
                "html_id":
                    html_id,

                "url":
                    url,

                "error_type":
                    "udare_exception",

                "error":
                    (
                        f"{type(exc).__name__}: "
                        f"{exc}"
                    ),
            })

            continue

        if not isinstance(
            reconstruction,
            dict,
        ):
            reconstruction_failed += 1
            failed += 1

            errors.append({
                "html_id":
                    html_id,

                "url":
                    url,

                "error_type":
                    "udare_non_dictionary_result",
            })

            continue

        reconstruction_engine = str(
            reconstruction.get(
                "engine"
            )
            or ""
        )

        article_body = str(
            reconstruction.get(
                "article_body"
            )
            or ""
        )

        content_blocks = (
            reconstruction.get(
                "content_blocks"
            )
            or []
        )

        headings = (
            reconstruction.get(
                "headings"
            )
            or []
        )

        title = str(
            reconstruction.get(
                "title"
            )
            or source_title
            or ""
        ).strip()

        h1 = str(
            reconstruction.get(
                "h1"
            )
            or _html_h1(
                raw_html
            )
            or ""
        ).strip()

        if (
            reconstruction_engine
            != EXPECTED_UDARE_ENGINE
            or not article_body.strip()
            or not isinstance(
                content_blocks,
                list,
            )
            or not isinstance(
                headings,
                list,
            )
        ):
            reconstruction_failed += 1
            failed += 1

            errors.append({
                "html_id":
                    html_id,

                "url":
                    url,

                "error_type":
                    "invalid_udare_output",

                "engine":
                    reconstruction_engine,

                "body_present":
                    bool(
                        article_body.strip()
                    ),

                "content_blocks_type":
                    type(
                        content_blocks
                    ).__name__,

                "headings_type":
                    type(
                        headings
                    ).__name__,
            })

            continue

        try:
            integrity = (
                build_website_article_integrity_result_v1(
                    raw_main_html=str(
                        reconstruction.get(
                            "selected_html"
                        )
                        or reconstruction.get(
                            "raw_main_html"
                        )
                        or raw_html
                    ),

                    raw_article_text=
                        article_body,

                    headings=
                        headings,

                    title=
                        title,

                    url=
                        url,

                    metadata={
                        "workspace_id":
                            workspace_id,

                        "html_id":
                            html_id,

                        "batch_id":
                            batch_id,

                        "batch_index":
                            batch_index,

                        "batch_count":
                            batch_count,

                        "source_stage":
                            EXPECTED_UDARE_ENGINE,
                    },

                    content_blocks=
                        content_blocks,
                )
            )

        except Exception as exc:
            integrity_failed += 1
            failed += 1

            errors.append({
                "html_id":
                    html_id,

                "url":
                    url,

                "error_type":
                    "integrity_exception",

                "error":
                    (
                        f"{type(exc).__name__}: "
                        f"{exc}"
                    ),
            })

            continue

        if (
            not isinstance(
                integrity,
                dict,
            )
            or not _result_passed(
                integrity
            )
        ):
            integrity_failed += 1
            failed += 1

            errors.append({
                "html_id":
                    html_id,

                "url":
                    url,

                "error_type":
                    "integrity_failed",

                "checks":
                    (
                        integrity.get(
                            "checks"
                        )
                        if isinstance(
                            integrity,
                            dict,
                        )
                        else None
                    ),
            })

            continue

        certified_body = str(
            integrity.get(
                "content_body"
            )
            or integrity.get(
                "cleaned_article_text"
            )
            or article_body
        )

        final_headings = (
            integrity.get(
                "headings"
            )
            or headings
        )

        removed_sections = (
            integrity.get(
                "removed_sections"
            )
            or []
        )

        if not isinstance(
            final_headings,
            list,
        ):
            final_headings = []

        if not isinstance(
            removed_sections,
            list,
        ):
            removed_sections = []

        try:
            validation = (
                validate_article_v1(
                    cleaned_article_text=
                        certified_body,

                    title=
                        title,

                    headings=
                        final_headings,

                    removed_sections=
                        removed_sections,

                    metadata={
                        "workspace_id":
                            workspace_id,

                        "html_id":
                            html_id,

                        "url":
                            url,

                        "batch_id":
                            batch_id,

                        "batch_index":
                            batch_index,

                        "batch_count":
                            batch_count,

                        "integrity_passed":
                            True,

                        "source_stage":
                            EXPECTED_INTEGRITY_ENGINE,
                    },
                )
            )

        except Exception as exc:
            validation_failed += 1
            failed += 1

            errors.append({
                "html_id":
                    html_id,

                "url":
                    url,

                "error_type":
                    "article_validation_exception",

                "error":
                    (
                        f"{type(exc).__name__}: "
                        f"{exc}"
                    ),
            })

            continue

        if not isinstance(
            validation,
            dict,
        ):
            validation_failed += 1
            failed += 1

            errors.append({
                "html_id":
                    html_id,

                "url":
                    url,

                "error_type":
                    "article_validation_non_dictionary",
            })

            continue

        validation_version = str(
            validation.get(
                "validation_version"
            )
            or ""
        )

        validation_passed = (
            _result_passed(
                validation
            )
        )

        eligible_for_wuc = bool(
            validation.get(
                "eligible_for_unified_content_document"
            )
            or validation.get(
                "eligible_for_wuc"
            )
        )

        if (
            not validation_passed
            or not eligible_for_wuc
        ):
            validation_failed += 1
            quarantined += 1

            certified_articles.pop(
                html_id,
                None,
            )

            quarantines.append({
                "html_id":
                    html_id,

                "url":
                    url,

                "title":
                    title,

                "validation_version":
                    validation_version,

                "checks":
                    validation.get(
                        "checks"
                    )
                    or {},

                "warnings":
                    validation.get(
                        "warnings"
                    )
                    or [],

                "errors":
                    validation.get(
                        "errors"
                    )
                    or [],

                "rejection_reasons":
                    validation.get(
                        "rejection_reasons"
                    )
                    or [],
            })

            continue

        try:
            certified_article = (
                build_certified_website_article_v1(
                    workspace_id=
                        workspace_id,

                    html_id=
                        html_id,

                    url=
                        url,

                    title=
                        title,

                    h1=
                        h1,

                    headings=
                        final_headings,

                    content_blocks=
                        content_blocks,

                    article_body=
                        certified_body,

                    reconstruction=
                        reconstruction,

                    integrity=
                        integrity,

                    validation=
                        validation,

                    metadata={
                        "worker_version":
                            WORKER_VERSION,

                        "batch_id":
                            batch_id,

                        "batch_index":
                            batch_index,

                        "batch_count":
                            batch_count,

                        "raw_html_length":
                            len(
                                raw_html
                            ),

                        "udare_engine":
                            reconstruction_engine,

                        "integrity_engine":
                            EXPECTED_INTEGRITY_ENGINE,

                        "validation_version":
                            validation_version,

                        "wuc_written":
                            False,

                        "uucd_written":
                            False,

                        "body_store_written":
                            False,
                    },
                )
            )

        except Exception as exc:
            store_build_failed += 1
            failed += 1

            errors.append({
                "html_id":
                    html_id,

                "url":
                    url,

                "error_type":
                    "certified_article_build_failed",

                "error":
                    (
                        f"{type(exc).__name__}: "
                        f"{exc}"
                    ),
            })

            continue

        previous = certified_articles.get(
            html_id
        )

        if isinstance(
            previous,
            dict,
        ):
            certified_article[
                "created_at"
            ] = previous.get(
                "created_at"
            ) or certified_article.get(
                "created_at"
            )

        certified_articles[
            html_id
        ] = certified_article

        certified += 1

        successes.append({
            "html_id":
                html_id,

            "url":
                url,

            "title":
                title,

            "article_body_hash":
                certified_article.get(
                    "article_body_hash"
                ),

            "article_word_count":
                certified_article.get(
                    "article_word_count"
                ),

            "validation_version":
                validation_version,
        })

    certified_store[
        "article_count"
    ] = len(
        certified_articles
    )

    saved_path = (
        save_certified_website_article_store_v1(
            workspace_id,
            certified_store,
        )
    )

    return {
        "ok":
            failed == 0,

        "workspace_id":
            workspace_id,

        "stage":
            (
                "article_validation_to_"
                "certified_website_article_store"
            ),

        "worker_version":
            WORKER_VERSION,

        "batch_id":
            batch_id,

        "batch_index":
            batch_index,

        "batch_count":
            batch_count,

        "store_path":
            str(
                saved_path
            ),

        "store_article_count":
            len(
                certified_articles
            ),

        "processing": {
            "assigned":
                len(
                    assigned_html_ids
                ),

            "attempted":
                attempted,

            "certified":
                certified,

            "quarantined":
                quarantined,

            "failed":
                failed,

            "missing_raw_record":
                missing_raw_record,

            "reconstruction_failed":
                reconstruction_failed,

            "integrity_failed":
                integrity_failed,

            "validation_failed":
                validation_failed,

            "store_build_failed":
                store_build_failed,
        },

        "success_sample":
            successes[
                :10
            ],

        "quarantine_sample":
            quarantines[
                :10
            ],

        "error_sample":
            errors[
                :25
            ],

        "wuc_written":
            False,

        "uucd_written":
            False,

        "body_store_written":
            False,
    }
