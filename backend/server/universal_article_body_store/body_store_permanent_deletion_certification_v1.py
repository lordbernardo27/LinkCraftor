from __future__ import annotations

import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.universal_article_body_store.body_store_permanent_deletion_verifier_v1 import (
    certify_permanent_deletion_verification_v1,
)


BODY_STORE_PERMANENT_DELETION_CERTIFICATION_VERSION = "1.0"

BODY_STORE_PERMANENT_DELETION_CERTIFICATION_SCHEMA = (
    "body_store_permanent_deletion_certification.v1"
)


class PermanentDeletionCertificationError(
    ValueError
):
    """Raised when permanent deletion certification fails."""


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
        raise PermanentDeletionCertificationError(
            field_name
            + " must be a mapping."
        )

    return value


def calculate_permanent_deletion_certification_checksum_v1(
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
def build_permanent_deletion_certification_v1(
    *,
    verification_result: Mapping[str, Any],
) -> Mapping[str, Any]:

    verification = _require_mapping(
        verification_result,
        field_name="verification_result",
    )

    verifier_certification = (
        certify_permanent_deletion_verification_v1(
            verification_result=verification,
        )
    )

    if verifier_certification[
        "certified"
    ] is not True:
        raise PermanentDeletionCertificationError(
            "Permanent deletion verification is not certified."
        )

    summary = verifier_certification[
        "summary"
    ]

    certification_material = {
        "verification_id":
            verifier_certification[
                "verification_id"
            ],

        "deletion_execution_id":
            verifier_certification[
                "deletion_execution_id"
            ],

        "deletion_plan_id":
            verifier_certification[
                "deletion_plan_id"
            ],

        "deletion_request_id":
            verifier_certification[
                "deletion_request_id"
            ],

        "deletion_verified":
            verifier_certification[
                "deletion_verified"
            ],
    }

    certification_id = (
        "body_store_permanent_deletion_certification_"
        + calculate_permanent_deletion_certification_checksum_v1(
            payload=certification_material,
        )
    )

    certification = {
        "schema_version":
            BODY_STORE_PERMANENT_DELETION_CERTIFICATION_SCHEMA,

        "certification_version":
            BODY_STORE_PERMANENT_DELETION_CERTIFICATION_VERSION,

        "certification_id":
            certification_id,

        "verification_id":
            verifier_certification[
                "verification_id"
            ],

        "deletion_execution_id":
            verifier_certification[
                "deletion_execution_id"
            ],

        "deletion_plan_id":
            verifier_certification[
                "deletion_plan_id"
            ],

        "deletion_request_id":
            verifier_certification[
                "deletion_request_id"
            ],

        "archive_id":
            verifier_certification[
                "archive_id"
            ],

        "workspace_id":
            verifier_certification[
                "workspace_id"
            ],

        "body_id":
            verifier_certification[
                "body_id"
            ],

        "lifecycle_record_id":
            verifier_certification[
                "lifecycle_record_id"
            ],

        "verified":
            verifier_certification[
                "deletion_verified"
            ],

        "certified":
            True,

        "summary":
            summary,

        "verifier_certification":
            verifier_certification,

        "archive_delete_performed":
            verifier_certification[
                "archive_delete_performed"
            ],

        "body_store_delete_performed":
            verifier_certification[
                "body_store_delete_performed"
            ],

        "lifecycle_transition_performed":
            verifier_certification[
                "lifecycle_transition_performed"
            ],

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


def summarize_permanent_deletion_certification_v1(
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

        "deletion_execution_id":
            cert[
                "deletion_execution_id"
            ],

        "deletion_plan_id":
            cert[
                "deletion_plan_id"
            ],

        "deletion_request_id":
            cert[
                "deletion_request_id"
            ],

        "archive_id":
            cert[
                "archive_id"
            ],

        "workspace_id":
            cert[
                "workspace_id"
            ],

        "body_id":
            cert[
                "body_id"
            ],

        "lifecycle_record_id":
            cert[
                "lifecycle_record_id"
            ],

        "verified":
            cert[
                "verified"
            ],

        "certified":
            cert[
                "certified"
            ],

        "archive_delete_performed":
            cert[
                "archive_delete_performed"
            ],

        "body_store_delete_performed":
            cert[
                "body_store_delete_performed"
            ],

        "lifecycle_transition_performed":
            cert[
                "lifecycle_transition_performed"
            ],

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
def validate_permanent_deletion_certification_v1(
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
        "deletion_execution_id",
        "deletion_plan_id",
        "deletion_request_id",
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
        == BODY_STORE_PERMANENT_DELETION_CERTIFICATION_SCHEMA
    )

    version_valid = (
        cert.get(
            "certification_version"
        )
        == BODY_STORE_PERMANENT_DELETION_CERTIFICATION_VERSION
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

    verifier_certification = cert.get(
        "verifier_certification",
        {},
    )

    verifier_certified = (
        verifier_certification.get(
            "certified"
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

    execution_id_matches = (
        cert.get(
            "deletion_execution_id"
        )
        == verifier_certification.get(
            "deletion_execution_id"
        )
    )

    plan_id_matches = (
        cert.get(
            "deletion_plan_id"
        )
        == verifier_certification.get(
            "deletion_plan_id"
        )
    )

    request_id_matches = (
        cert.get(
            "deletion_request_id"
        )
        == verifier_certification.get(
            "deletion_request_id"
        )
    )

    deletion_evidence_valid = (
        cert.get(
            "archive_delete_performed"
        )
        is True
        and cert.get(
            "lifecycle_transition_performed"
        )
        is True
    )

    safety_boundaries_valid = (
        cert.get(
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
                    execution_id_matches,
                    plan_id_matches,
                    request_id_matches,
                    deletion_evidence_valid,
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

        "execution_id_matches":
            execution_id_matches,

        "plan_id_matches":
            plan_id_matches,

        "request_id_matches":
            request_id_matches,

        "deletion_evidence_valid":
            deletion_evidence_valid,

        "safety_boundaries_valid":
            safety_boundaries_valid,

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


def build_permanent_deletion_certification_bundle_v1(
    *,
    verification_result: Mapping[str, Any],
) -> Mapping[str, Any]:

    certification = (
        build_permanent_deletion_certification_v1(
            verification_result=verification_result,
        )
    )

    validation = (
        validate_permanent_deletion_certification_v1(
            certification=certification,
        )
    )

    if validation[
        "certification_valid"
    ] is not True:
        raise PermanentDeletionCertificationError(
            "Permanent deletion certification validation failed."
        )

    summary = (
        summarize_permanent_deletion_certification_v1(
            certification=certification,
        )
    )

    bundle = {
        "bundle_version":
            "body_store_permanent_deletion_certification_bundle.v1",

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

        "archive_delete_performed":
            certification[
                "archive_delete_performed"
            ],

        "body_store_delete_performed":
            certification[
                "body_store_delete_performed"
            ],

        "lifecycle_transition_performed":
            certification[
                "lifecycle_transition_performed"
            ],

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
    "BODY_STORE_PERMANENT_DELETION_CERTIFICATION_VERSION",
    "BODY_STORE_PERMANENT_DELETION_CERTIFICATION_SCHEMA",
    "PermanentDeletionCertificationError",
    "calculate_permanent_deletion_certification_checksum_v1",
    "build_permanent_deletion_certification_v1",
    "summarize_permanent_deletion_certification_v1",
    "validate_permanent_deletion_certification_v1",
    "build_permanent_deletion_certification_bundle_v1",
]
