from __future__ import annotations

from typing import Any, Dict, List

from backend.server.stores.universal_unified_content_document_convergence import (
    from_crawled_web_page_v1,
    upsert_universal_unified_content_document_v1,
)


def build_ucd_from_validated_article_v1(
    *,
    workspace_id: str,
    url: str,
    title: str,
    cleaned_article_text: str,
    headings: List[str] | None = None,
    cleaning_result: Dict[str, Any] | None = None,
    validation_result: Dict[str, Any] | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:

    validation_result = validation_result or {}

    validation_passed = bool(
        validation_result.get("eligible_for_universal_unified_content_document", False)
    )

    validation_score = float(validation_result.get("validation_score", 0.0) or 0.0)

    if validation_passed and validation_score >= 90:
        certification_level = "gold"
    elif validation_score >= 75:
        certification_level = "silver"
    elif validation_score >= 50:
        certification_level = "bronze"
    else:
        certification_level = "rejected"

    semantic_ready = certification_level in {"gold", "silver", "bronze"}

    document = from_crawled_web_page_v1(
        workspace_id=workspace_id,
        url=url,
        title=title,
        primary_content=cleaned_article_text,
        headings=headings or [],
        metadata={
            **(metadata or {}),
            "uucd_bridge_version": "validated_article_uucd_bridge_v1",
            "validation": validation_result,
            "cleaning_statistics": (cleaning_result or {}).get("statistics", {}),
            "cleaning_report": (cleaning_result or {}).get("cleaning_report", {}),
        },
        quality={
            "validation_passed": validation_result.get("passed"),
            "quality_grade": validation_result.get("quality_grade"),
            "validation_score": validation_result.get("validation_score"),
            "warnings": validation_result.get("warnings", []),
            "rejection_reasons": validation_result.get("rejection_reasons", []),
        },
        semantic_features={
            "semantic_ready": semantic_ready,
          "certification_level": certification_level,
            "source_pipeline": "website_html_to_validated_ucd",
        },
    )

    return document


def upsert_ucd_from_validated_article_v1(
    *,
    workspace_id: str,
    url: str,
    title: str,
    cleaned_article_text: str,
    headings: List[str] | None = None,
    cleaning_result: Dict[str, Any] | None = None,
    validation_result: Dict[str, Any] | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:

    document = build_ucd_from_validated_article_v1(
        workspace_id=workspace_id,
        url=url,
        title=title,
        cleaned_article_text=cleaned_article_text,
        headings=headings or [],
        cleaning_result=cleaning_result or {},
        validation_result=validation_result or {},
        metadata=metadata or {},
    )

    upsert_universal_unified_content_document_v1(document)

    return document
