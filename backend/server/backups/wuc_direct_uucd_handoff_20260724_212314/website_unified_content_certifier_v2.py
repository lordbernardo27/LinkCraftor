from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


CERTIFIER_VERSION = (
    "website_unified_content_certifier_v2"
)


def certify_website_unified_content_document_v2(
    *,
    document: dict[str, Any],
    verification_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Attach certification metadata to a verified
    Website Unified Content document.
    """

    certified = dict(document)

    metadata = dict(
        certified.get("metadata")
        or {}
    )

    metadata["certification"] = {
        "status": (
            "PASS"
            if verification_result.get("passed")
            else "FAIL"
        ),
        "certifier":
            CERTIFIER_VERSION,
        "verification_version":
            verification_result.get(
                "verification_version"
            ),
        "certified_at":
            datetime.now(
                UTC
            ).isoformat(),
    }

    certified["metadata"] = metadata

    certified["certified"] = bool(
        verification_result.get(
            "passed"
        )
    )

    return certified
