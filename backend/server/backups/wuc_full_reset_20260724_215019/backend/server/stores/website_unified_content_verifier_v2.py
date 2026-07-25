"""Verify a canonical transient Website Unified Content document."""

from __future__ import annotations

from typing import Any, Mapping


VERIFIER_VERSION = (
    "website_unified_content_verifier_v2_"
    "canonical_content_body"
)


def verify_website_unified_content_document_v2(
    *,
    document: Mapping[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []

    required_text_fields = (
        "document_id",
        "workspace_id",
        "content_body",
        "content_hash",
    )

    for field in required_text_fields:
        value = document.get(
            field
        )

        if not str(
            value or ""
        ).strip():
            errors.append(
                f"missing_{field}"
            )

    headings = document.get(
        "headings",
        [],
    )

    if not isinstance(
        headings,
        list,
    ):
        errors.append(
            "invalid_headings"
        )

    structure = document.get(
        "structure",
        {},
    )

    if not isinstance(
        structure,
        dict,
    ):
        errors.append(
            "invalid_structure"
        )

    if "article_body" in document:
        errors.append(
            "legacy_article_body_field_present"
        )

    passed = (
        len(
            errors
        )
        == 0
    )

    return {
        "passed":
            passed,

        "errors":
            errors,

        "verification_version":
            VERIFIER_VERSION,

        "intermediate_store_required":
            False,
    }
