from __future__ import annotations

from typing import Any


VERIFIER_VERSION = (
    "website_unified_content_verifier_v2"
)


def verify_website_unified_content_document_v2(
    *,
    document: dict[str, Any],
) -> dict[str, Any]:
    """
    Verify a Website Unified Content document
    before it is written to the WUC store.
    """

    errors: list[str] = []

    required_fields = (
        "workspace_id",
        "url",
        "title",
        "article_body",
        "content_hash",
    )

    for field in required_fields:
        value = document.get(field)

        if not str(value or "").strip():
            errors.append(
                f"missing_{field}"
            )

    headings = document.get(
        "headings",
        []
    )

    if not isinstance(
        headings,
        list,
    ):
        errors.append(
            "invalid_headings"
        )

    passed = (
        len(errors) == 0
    )

    return {
        "passed": passed,
        "errors": errors,
        "verification_version":
            VERIFIER_VERSION,
    }
