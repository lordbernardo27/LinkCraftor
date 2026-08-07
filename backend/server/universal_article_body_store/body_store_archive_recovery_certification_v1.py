from __future__ import annotations

import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.universal_article_body_store.body_store_archive_recovery_verifier_v1 import (
    certify_archive_recovery_verification_v1,
)


BODY_STORE_ARCHIVE_RECOVERY_CERTIFICATION_SCHEMA = (
    "body_store_archive_recovery_certification.v1"
)

BODY_STORE_ARCHIVE_RECOVERY_CERTIFICATION_VERSION = (
    "1.0"
)


class ArchiveRecoveryCertificationError(
    ValueError,
):
    """Raised when archive recovery certification fails."""


def _freeze(
    value: Any,
) -> Any:

    if isinstance(
        value,
        MappingProxyType,
    ):
        return value

    if isinstance(
        value,
        dict,
    ):
        return MappingProxyType(
            {
                key:
                    _freeze(item)
                for key, item
                in value.items()
            }
        )

    if isinstance(
        value,
        list,
    ):
        return tuple(
            _freeze(item)
            for item
            in value
        )

    if isinstance(
        value,
        tuple,
    ):
        return tuple(
            _freeze(item)
            for item
            in value
        )

    return value


def _require_mapping(
    value: Any,
    *,
    field_name: str,
) -> Mapping[str, Any]:

    if not isinstance(
        value,
        Mapping,
    ):
        raise ArchiveRecoveryCertificationError(
            field_name
            + " must be a mapping."
        )

    return value


def calculate_archive_recovery_certification_checksum_v1(
    *,
    payload: Mapping[str, Any],
) -> str:

    _require_mapping(
        payload,
        field_name="payload",
    )

    serialized = json.dumps(
        dict(payload),
        ensure_ascii=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        default=str,
    )

    return hashlib.sha256(
        serialized.encode(
            "utf-8"
        )
    ).hexdigest()
def build_archive_recovery_certification_v1(
    *,
    verification_result: Mapping[str, Any],
) -> Mapping[str, Any]:

    verification = _require_mapping(
        verification_result,
        field_name="verification_result",
    )

    verifier_certification = (
        certify_archive_recovery_verification_v1(
            verification_result=verification,
        )
    )

    if (
        verifier_certification[
            "certified"
        ]
        is not True
    ):
        raise ArchiveRecoveryCertificationError(
            "Archive recovery verification is not certified."
        )

    summary = verifier_certification[
        "summary"
    ]

    certification_material = {
        "verification_id":
            verifier_certification[
                "verification_id"
            ],

        "recovery_verified":
            verifier_certification[
                "recovery_verified"
            ],

        "summary":
            dict(summary),
    }

    certification_id = (
        "body_store_archive_recovery_certification_"
        + calculate_archive_recovery_certification_checksum_v1(
            payload=certification_material,
        )
    )

    certification = {
        "schema_version":
            BODY_STORE_ARCHIVE_RECOVERY_CERTIFICATION_SCHEMA,

        "certification_version":
            BODY_STORE_ARCHIVE_RECOVERY_CERTIFICATION_VERSION,

        "certification_id":
            certification_id,

        "verification_id":
            verifier_certification[
                "verification_id"
            ],

        "verified":
            verifier_certification[
                "recovery_verified"
            ],

        "certified":
            True,

        "summary":
            summary,

        "verifier_certification":
            verifier_certification,

        "archive_read_performed":
            verifier_certification[
                "archive_read_performed"
            ],

        "body_store_write_performed":
            False,

        "lifecycle_transition_performed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,

        "content_body_included":
            False,

        "read_only":
            True,
    }

    return _freeze(
        certification
    )


def summarize_archive_recovery_certification_v1(
    *,
    certification: Mapping[str, Any],
) -> Mapping[str, Any]:

    cert = _require_mapping(
        certification,
        field_name="certification",
    )

    summary = {
        "certification_id":
            cert[
                "certification_id"
            ],

        "verification_id":
            cert[
                "verification_id"
            ],

        "verified":
            cert[
                "verified"
            ],

        "certified":
            cert[
                "certified"
            ],

        "archive_read_performed":
            cert[
                "archive_read_performed"
            ],

        "body_store_write_performed":
            False,

        "lifecycle_transition_performed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,

        "content_body_included":
            False,
    }

    return _freeze(
        summary
    )
def validate_archive_recovery_certification_v1(
    *,
    certification: Mapping[str, Any],
) -> Mapping[str, Any]:

    cert = _require_mapping(
        certification,
        field_name="certification",
    )

    required_fields = (
        "schema_version",
        "certification_version",
        "certification_id",
        "verification_id",
        "verified",
        "certified",
        "verifier_certification",
        "read_only",
    )

    missing_fields = tuple(
        field
        for field in required_fields
        if field not in cert
    )

    schema_valid = (
        cert.get(
            "schema_version"
        )
        == BODY_STORE_ARCHIVE_RECOVERY_CERTIFICATION_SCHEMA
    )

    version_valid = (
        cert.get(
            "certification_version"
        )
        == BODY_STORE_ARCHIVE_RECOVERY_CERTIFICATION_VERSION
    )

    verified = (
        cert.get(
            "verified"
        )
        is True
    )

    certified = (
        cert.get(
            "certified"
        )
        is True
    )

    verifier_certified = (
        cert.get(
            "verifier_certification",
            {},
        ).get(
            "certified"
        )
        is True
    )

    verification_id_matches = (
        cert.get(
            "verification_id"
        )
        == cert.get(
            "verifier_certification",
            {},
        ).get(
            "verification_id"
        )
    )

    safety_boundaries_valid = (
        cert.get(
            "body_store_write_performed"
        )
        is False
        and cert.get(
            "lifecycle_transition_performed"
        )
        is False
        and cert.get(
            "runtime_job_created"
        )
        is False
        and cert.get(
            "queue_job_created"
        )
        is False
        and cert.get(
            "content_body_included"
        )
        is False
        and cert.get(
            "read_only"
        )
        is True
    )

    result = {
        "certification_valid":
            all(
                (
                    not missing_fields,
                    schema_valid,
                    version_valid,
                    verified,
                    certified,
                    verifier_certified,
                    verification_id_matches,
                    safety_boundaries_valid,
                )
            ),

        "missing_fields":
            missing_fields,

        "schema_valid":
            schema_valid,

        "version_valid":
            version_valid,

        "verified":
            verified,

        "certified":
            certified,

        "verifier_certified":
            verifier_certified,

        "verification_id_matches":
            verification_id_matches,

        "safety_boundaries_valid":
            safety_boundaries_valid,

        "body_store_write_performed":
            False,

        "lifecycle_transition_performed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,

        "content_body_included":
            False,
    }

    return _freeze(
        result
    )


def build_archive_recovery_certification_bundle_v1(
    *,
    verification_result: Mapping[str, Any],
) -> Mapping[str, Any]:

    certification = (
        build_archive_recovery_certification_v1(
            verification_result=verification_result,
        )
    )

    validation = (
        validate_archive_recovery_certification_v1(
            certification=certification,
        )
    )

    if validation[
        "certification_valid"
    ] is not True:
        raise ArchiveRecoveryCertificationError(
            "Archive recovery certification validation failed."
        )

    summary = (
        summarize_archive_recovery_certification_v1(
            certification=certification,
        )
    )

    bundle = {
        "bundle_version":
            "body_store_archive_recovery_certification_bundle.v1",

        "certification":
            certification,

        "validation":
            validation,

        "summary":
            summary,

        "bundle_complete":
            True,

        "certified":
            certification[
                "certified"
            ],

        "verified":
            certification[
                "verified"
            ],

        "archive_read_performed":
            certification[
                "archive_read_performed"
            ],

        "body_store_write_performed":
            False,

        "lifecycle_transition_performed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,

        "content_body_included":
            False,

        "read_only":
            True,
    }

    return _freeze(
        bundle
    )


__all__ = [
    "BODY_STORE_ARCHIVE_RECOVERY_CERTIFICATION_SCHEMA",
    "BODY_STORE_ARCHIVE_RECOVERY_CERTIFICATION_VERSION",
    "ArchiveRecoveryCertificationError",
    "calculate_archive_recovery_certification_checksum_v1",
    "build_archive_recovery_certification_v1",
    "summarize_archive_recovery_certification_v1",
    "validate_archive_recovery_certification_v1",
    "build_archive_recovery_certification_bundle_v1",
]
