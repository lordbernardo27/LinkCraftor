"""Certify a transient WUC document for immediate UUCD convergence."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Mapping


CERTIFIER_VERSION = (
    "website_unified_content_certifier_v2_"
    "transient_direct_uucd"
)


def certify_website_unified_content_document_v2(
    *,
    document: Mapping[str, Any],
    verification_result: Mapping[str, Any],
) -> dict[str, Any]:
    if (
        verification_result.get(
            "passed"
        )
        is not True
    ):
        raise ValueError(
            "Cannot certify a WUC document that failed verification."
        )

    certified = dict(
        document
    )

    metadata = dict(
        certified.get(
            "metadata"
        )
        or {}
    )

    metadata.update(
        {
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

            "status":
                "CERTIFIED_FOR_UUCD",

            "persistence_mode":
                "TRANSIENT",

            "next_stage":
                "universal_unified_content_document",

            "intermediate_wuc_store_created":
                False,
        }
    )

    certified[
        "metadata"
    ] = metadata

    certified[
        "wuc_certification_status"
    ] = "CERTIFIED_FOR_UUCD"

    return certified
