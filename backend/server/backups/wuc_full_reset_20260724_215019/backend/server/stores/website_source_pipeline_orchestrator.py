from __future__ import annotations

from typing import Any, Dict

from backend.server.stores.raw_website_html_store import (
    upsert_raw_website_html_v1,
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


PIPELINE_VERSION = (
    "website_source_pipeline_orchestrator_v2_raw_html_udare"
)


def process_website_html_to_ucd_v1(
    *,
    workspace_id: str,
    url: str,
    html: str,
    title: str = "",
    h1: str = "",
    status_code: int | None = None,
    content_type: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Canonical website ingestion chain:

    Raw HTML Store
      -> UDARE
      -> Website Article Integrity Validator
      -> Article Validation
      -> Website Unified Content
      -> UUCD
    """

    metadata = dict(metadata or {})
    raw_html = str(html or "")

    raw_record = upsert_raw_website_html_v1(
        workspace_id=workspace_id,
        url=url,
        html=raw_html,
        title=title,
        status_code=status_code,
        content_type=content_type,
        metadata={
            **metadata,
            "source_pipeline": PIPELINE_VERSION,
            "stage": "raw_website_html_store",
        },
    )

    extraction = extract_main_content_from_html_v1(
        html_text=raw_html,
        url=url,
        title=title,
        metadata={
            **metadata,
            "html_id": raw_record.get("html_id"),
            "raw_html_length": raw_record.get("html_length"),
            "source_pipeline": PIPELINE_VERSION,
            "source_stage": "raw_website_html_store",
            "stage": "udare_article_reconstruction",
        },
    )

    article_body = str(
        extraction.get("article_body")
        or extraction.get("main_content")
        or ""
    )

    integrity = build_website_article_integrity_result_v1(
        raw_main_html=raw_html,
        raw_article_text=article_body,
        headings=extraction.get("headings", []),
        title=(
            title
            or h1
            or extraction.get("title", "")
        ),
        url=url,
        metadata={
            **metadata,
            "html_id": raw_record.get("html_id"),
            "source_pipeline": PIPELINE_VERSION,
            "source_stage": "udare_article_reconstruction",
            "stage": "website_article_integrity_validation",
        },
    
        content_blocks=extraction.get("content_blocks", []),
    )

    validated_body = str(
        integrity.get("content_body")
        or integrity.get("cleaned_article_text")
        or article_body
    )

    validation = validate_article_v1(
        cleaned_article_text=validated_body,
        title=(
            title
            or h1
            or extraction.get("title", "")
        ),
        headings=integrity.get(
            "headings",
            extraction.get("headings", []),
        ),
        removed_sections=integrity.get(
            "removed_sections",
            [],
        ),
        metadata={
            **metadata,
            "html_id": raw_record.get("html_id"),
            "source_pipeline": PIPELINE_VERSION,
            "stage": "article_validation",
            "integrity_passed":
                bool(
                    integrity.get("passed")
                ),
        },
    )

    website_doc = (
        upsert_website_unified_content_document_v1(
            workspace_id=workspace_id,
            url=url,
            title=(
                title
                or h1
                or extraction.get("title", "")
            ),
            h1=(
                h1
                or extraction.get("h1", "")
            ),
            article_body=validated_body,
            headings=integrity.get(
                "headings",
                extraction.get("headings", []),
            ),
            metadata={
                **metadata,
                "html_id":
                    raw_record.get("html_id"),
                "raw_html_length":
                    raw_record.get("html_length"),
                "source_pipeline":
                    PIPELINE_VERSION,
                "source_stage":
                    "raw_website_html_store",
                "stage":
                    "website_unified_content_store",
                "reconstruction": {
                    "extraction_engine":
                        extraction.get("engine"),
                    "reconstruction_engine":
                        extraction.get(
                            "reconstruction_engine"
                        ),
                    "selected_tag":
                        extraction.get("selected_tag"),
                    "word_count":
                        extraction.get("word_count"),
                    "content_length":
                        extraction.get("content_length"),
                    "candidate_count":
                        extraction.get("candidate_count"),
                },
                "integrity_statistics":
                    integrity.get("statistics", {}),
                "removed_sections":
                    integrity.get(
                        "removed_sections",
                        [],
                    ),
                "validation":
                    validation,
            },
            quality={
                "validation_passed":
                    validation.get("passed"),
                "quality_grade":
                    validation.get("quality_grade"),
                "validation_score":
                    validation.get(
                        "validation_score"
                    ),
                "warnings":
                    validation.get("warnings", []),
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
                    PIPELINE_VERSION,
                "source_type":
                    "website",
            },
        )
    )

    uucd_document = None
    uucd_error = None

    try:
        uucd_result = (
            build_and_write_uucd_from_wuc_v1(
                website_doc
            )
        )

        uucd_document = (
            uucd_result.get("uucd")
        )

    except Exception as exc:
        uucd_error = str(exc)

    return {
        "ok": bool(
            extraction.get("ok")
            and validated_body.strip()
        ),
        "workspace_id": workspace_id,
        "url": url,
        "pipeline": PIPELINE_VERSION,
        "source_boundary": {
            "source_type": "website",
            "input_store":
                "raw_website_html_store_v1",
            "html_cleaner_used": False,
            "clean_html_store_used": False,
            "upload_document_pipeline_used":
                False,
            "merges_at":
                "universal_unified_content_document",
        },
        "raw_record": raw_record,
        "extraction": extraction,
        "integrity": integrity,
        "cleaning": integrity,
        "validation": validation,
        "website_unified_content_document":
            website_doc,
        "universal_unified_content_document":
            uucd_document,
        "uucd_error": uucd_error,
        "status": {
            "raw_html_stored": True,
            "udare_reconstructed":
                bool(article_body.strip()),
            "article_integrity_passed":
                bool(integrity.get("passed")),
            "article_validated":
                bool(validation.get("passed")),
            "website_content_stored": True,
            "uucd_stored":
                uucd_document is not None
                and not uucd_error,
        },
    }


def explain_website_source_pipeline_orchestrator_v1(
) -> Dict[str, Any]:
    return {
        "name":
            "Website Source Pipeline Orchestrator",
        "version":
            PIPELINE_VERSION,
        "source_type":
            "website_only",
        "pipeline": [
            "Raw HTML Store",
            "UDARE v1.4",
            "Website Article Integrity Validator",
            "Article Validation",
            "Website Unified Content Store",
            "Universal Unified Content Document Store",
        ],
        "html_cleaner":
            "removed",
        "clean_html_store":
            "removed",
        "does_not_process": [
            "uploaded documents",
            "PDF uploads",
            "DOCX uploads",
            "TXT uploads",
        ],
        "merge_point":
            "Universal Unified Content Document",
    }
