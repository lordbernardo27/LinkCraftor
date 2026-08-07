from __future__ import annotations

import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping


from backend.server.universal_article_body_store.body_store_permanent_deletion_tombstone_verifier_v1 import (
    BODY_STORE_PERMANENT_DELETION_TOMBSTONE_VERIFIER_VERSION,
    certify_permanent_deletion_tombstone_verification_v1,
)


BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CERTIFICATION_VERSION = "1.0"

BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CERTIFICATION_SCHEMA = (
    "body_store_permanent_deletion_tombstone_certification.v1"
)


class PermanentDeletionTombstoneCertificationError(
    ValueError,
):
    """Raised when certification cannot be completed."""


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
                key: _freeze(item)
                for key, item in value.items()
            }
        )

    if isinstance(
        value,
        list,
    ):
        return tuple(
            _freeze(item)
            for item in value
        )

    if isinstance(
        value,
        tuple,
    ):
        return tuple(
            _freeze(item)
            for item in value
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
        raise PermanentDeletionTombstoneCertificationError(
            f"{field_name} must be a mapping."
        )

    return value


def calculate_tombstone_certification_checksum_v1(
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
        separators=(",", ":"),
        default=str,
    )

    return hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()
def build_permanent_deletion_tombstone_certification_v1(
    *,
    verification_result: Mapping[str, Any],
) -> Mapping[str, Any]:

    verification = _require_mapping(
        verification_result,
        field_name="verification_result",
    )

    verifier_certification = (
        certify_permanent_deletion_tombstone_verification_v1(
            verification_result=verification,
        )
    )

    if (
        verifier_certification[
            "certified"
        ]
        is not True
    ):
        raise PermanentDeletionTombstoneCertificationError(
            "Tombstone verification is not certified."
        )

    certification_material = {
        "verification_id":
            verifier_certification[
                "verification_id"
            ],

        "tombstone_id":
            verifier_certification[
                "tombstone_id"
            ],

        "body_id":
            verifier_certification[
                "body_id"
            ],

        "workspace_id":
            verifier_certification[
                "workspace_id"
            ],

        "archive_id":
            verifier_certification[
                "archive_id"
            ],

        "deletion_request_id":
            verifier_certification[
                "deletion_request_id"
            ],

        "deletion_execution_id":
            verifier_certification[
                "deletion_execution_id"
            ],
    }

    certification_id = (
        "body_store_permanent_deletion_tombstone_certification_"
        + calculate_tombstone_certification_checksum_v1(
            payload=certification_material,
        )
    )

    certification = {
        "schema":
            BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CERTIFICATION_SCHEMA,

        "certification_version":
            BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CERTIFICATION_VERSION,

        "verifier_version":
            BODY_STORE_PERMANENT_DELETION_TOMBSTONE_VERIFIER_VERSION,

        "certification_id":
            certification_id,

        "verification_id":
            verifier_certification[
                "verification_id"
            ],

        "tombstone_id":
            verifier_certification[
                "tombstone_id"
            ],

        "body_id":
            verifier_certification[
                "body_id"
            ],

        "workspace_id":
            verifier_certification[
                "workspace_id"
            ],

        "archive_id":
            verifier_certification[
                "archive_id"
            ],

        "lifecycle_record_id":
            verifier_certification[
                "lifecycle_record_id"
            ],

        "deletion_request_id":
            verifier_certification[
                "deletion_request_id"
            ],

        "deletion_execution_id":
            verifier_certification[
                "deletion_execution_id"
            ],

        "certified":
            True,

        "tombstone_verified":
            verifier_certification[
                "tombstone_verified"
            ],

        "verifier_certification":
            verifier_certification,

        "summary":
            verifier_certification[
                "summary"
            ],

        "record_integrity":
            verifier_certification[
                "record_integrity"
            ],

        "index_integrity":
            verifier_certification[
                "index_integrity"
            ],

        "workspace_isolation":
            verifier_certification[
                "workspace_isolation"
            ],

        "article_body_exposed":
            False,

        "lifecycle_modified":
            False,

        "archive_modified":
            False,

        "body_store_modified":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,

        "read_only":
            True,
    }

    return _freeze(
        certification
    )


def summarize_permanent_deletion_tombstone_certification_v1(
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

        "tombstone_id":
            cert[
                "tombstone_id"
            ],

        "body_id":
            cert[
                "body_id"
            ],

        "workspace_id":
            cert[
                "workspace_id"
            ],

        "certified":
            cert[
                "certified"
            ],

        "tombstone_verified":
            cert[
                "tombstone_verified"
            ],

        "record_integrity_verified":
            cert[
                "record_integrity"
            ][
                "record_integrity_verified"
            ],

        "index_integrity_verified":
            cert[
                "index_integrity"
            ][
                "index_integrity_verified"
            ],

        "workspace_isolation_verified":
            cert[
                "workspace_isolation"
            ][
                "workspace_isolation_verified"
            ],

        "article_body_exposed":
            False,

        "lifecycle_modified":
            False,

        "archive_modified":
            False,

        "body_store_modified":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,

        "read_only":
            True,
    }

    return _freeze(
        summary
    )
def validate_permanent_deletion_tombstone_certification_v1(
    *,
    certification: Mapping[str, Any],
) -> Mapping[str, Any]:

    cert = _require_mapping(
        certification,
        field_name="certification",
    )

    required_fields = (
        "schema",
        "certification_version",
        "verifier_version",
        "certification_id",
        "verification_id",
        "tombstone_id",
        "body_id",
        "workspace_id",
        "archive_id",
        "lifecycle_record_id",
        "deletion_request_id",
        "deletion_execution_id",
        "certified",
        "tombstone_verified",
        "verifier_certification",
        "record_integrity",
        "index_integrity",
        "workspace_isolation",
        "read_only",
    )

    missing_fields = tuple(
        field_name
        for field_name in required_fields
        if field_name not in cert
    )

    schema_valid = (
        cert.get(
            "schema"
        )
        == BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CERTIFICATION_SCHEMA
    )

    certification_version_valid = (
        cert.get(
            "certification_version"
        )
        == BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CERTIFICATION_VERSION
    )

    verifier_version_valid = (
        cert.get(
            "verifier_version"
        )
        == BODY_STORE_PERMANENT_DELETION_TOMBSTONE_VERIFIER_VERSION
    )

    verifier_certification = cert.get(
        "verifier_certification",
        {},
    )

    verifier_certified = (
        isinstance(
            verifier_certification,
            Mapping,
        )
        and verifier_certification.get(
            "certified"
        )
        is True
    )

    tombstone_verified = (
        cert.get(
            "tombstone_verified"
        )
        is True
    )

    verification_id_matches = (
        cert.get(
            "verification_id"
        )
        == verifier_certification.get(
            "verification_id"
        )
    )

    tombstone_id_matches = (
        cert.get(
            "tombstone_id"
        )
        == verifier_certification.get(
            "tombstone_id"
        )
    )

    body_id_matches = (
        cert.get(
            "body_id"
        )
        == verifier_certification.get(
            "body_id"
        )
    )

    workspace_id_matches = (
        cert.get(
            "workspace_id"
        )
        == verifier_certification.get(
            "workspace_id"
        )
    )

    archive_id_matches = (
        cert.get(
            "archive_id"
        )
        == verifier_certification.get(
            "archive_id"
        )
    )

    lifecycle_record_id_matches = (
        cert.get(
            "lifecycle_record_id"
        )
        == verifier_certification.get(
            "lifecycle_record_id"
        )
    )

    deletion_request_id_matches = (
        cert.get(
            "deletion_request_id"
        )
        == verifier_certification.get(
            "deletion_request_id"
        )
    )

    deletion_execution_id_matches = (
        cert.get(
            "deletion_execution_id"
        )
        == verifier_certification.get(
            "deletion_execution_id"
        )
    )

    record_integrity_verified = (
        cert.get(
            "record_integrity",
            {},
        ).get(
            "record_integrity_verified"
        )
        is True
    )

    index_integrity_verified = (
        cert.get(
            "index_integrity",
            {},
        ).get(
            "index_integrity_verified"
        )
        is True
    )

    workspace_isolation_verified = (
        cert.get(
            "workspace_isolation",
            {},
        ).get(
            "workspace_isolation_verified"
        )
        is True
    )

    safety_boundaries_valid = all(
        (
            cert.get(
                "article_body_exposed"
            )
            is False,
            cert.get(
                "lifecycle_modified"
            )
            is False,
            cert.get(
                "archive_modified"
            )
            is False,
            cert.get(
                "body_store_modified"
            )
            is False,
            cert.get(
                "runtime_job_created"
            )
            is False,
            cert.get(
                "queue_job_created"
            )
            is False,
            cert.get(
                "read_only"
            )
            is True,
        )
    )

    certification_valid = all(
        (
            not missing_fields,
            schema_valid,
            certification_version_valid,
            verifier_version_valid,
            cert.get(
                "certified"
            )
            is True,
            verifier_certified,
            tombstone_verified,
            verification_id_matches,
            tombstone_id_matches,
            body_id_matches,
            workspace_id_matches,
            archive_id_matches,
            lifecycle_record_id_matches,
            deletion_request_id_matches,
            deletion_execution_id_matches,
            record_integrity_verified,
            index_integrity_verified,
            workspace_isolation_verified,
            safety_boundaries_valid,
        )
    )

    validation = {
        "certification_valid":
            certification_valid,

        "missing_fields":
            missing_fields,

        "schema_valid":
            schema_valid,

        "certification_version_valid":
            certification_version_valid,

        "verifier_version_valid":
            verifier_version_valid,

        "verifier_certified":
            verifier_certified,

        "tombstone_verified":
            tombstone_verified,

        "verification_id_matches":
            verification_id_matches,

        "tombstone_id_matches":
            tombstone_id_matches,

        "body_id_matches":
            body_id_matches,

        "workspace_id_matches":
            workspace_id_matches,

        "archive_id_matches":
            archive_id_matches,

        "lifecycle_record_id_matches":
            lifecycle_record_id_matches,

        "deletion_request_id_matches":
            deletion_request_id_matches,

        "deletion_execution_id_matches":
            deletion_execution_id_matches,

        "record_integrity_verified":
            record_integrity_verified,

        "index_integrity_verified":
            index_integrity_verified,

        "workspace_isolation_verified":
            workspace_isolation_verified,

        "safety_boundaries_valid":
            safety_boundaries_valid,

        "article_body_exposed":
            False,

        "lifecycle_modified":
            False,

        "archive_modified":
            False,

        "body_store_modified":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,

        "read_only":
            True,
    }

    return _freeze(
        validation
    )


def build_permanent_deletion_tombstone_certification_bundle_v1(
    *,
    verification_result: Mapping[str, Any],
) -> Mapping[str, Any]:

    certification = (
        build_permanent_deletion_tombstone_certification_v1(
            verification_result=verification_result,
        )
    )

    validation = (
        validate_permanent_deletion_tombstone_certification_v1(
            certification=certification,
        )
    )

    if validation[
        "certification_valid"
    ] is not True:
        raise PermanentDeletionTombstoneCertificationError(
            "Tombstone certification validation failed."
        )

    summary = (
        summarize_permanent_deletion_tombstone_certification_v1(
            certification=certification,
        )
    )

    bundle = {
        "schema":
            "body_store_permanent_deletion_tombstone_certification_bundle.v1",

        "certification_version":
            BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CERTIFICATION_VERSION,

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
            ]
            is True,

        "tombstone_verified":
            certification[
                "tombstone_verified"
            ]
            is True,

        "record_integrity_verified":
            validation[
                "record_integrity_verified"
            ]
            is True,

        "index_integrity_verified":
            validation[
                "index_integrity_verified"
            ]
            is True,

        "workspace_isolation_verified":
            validation[
                "workspace_isolation_verified"
            ]
            is True,

        "article_body_exposed":
            False,

        "lifecycle_modified":
            False,

        "archive_modified":
            False,

        "body_store_modified":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,

        "read_only":
            True,
    }

    return _freeze(
        bundle
    )


__all__ = [
    "BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CERTIFICATION_VERSION",
    "BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CERTIFICATION_SCHEMA",
    "PermanentDeletionTombstoneCertificationError",
    "calculate_tombstone_certification_checksum_v1",
    "build_permanent_deletion_tombstone_certification_v1",
    "summarize_permanent_deletion_tombstone_certification_v1",
    "validate_permanent_deletion_tombstone_certification_v1",
    "build_permanent_deletion_tombstone_certification_bundle_v1",
]
