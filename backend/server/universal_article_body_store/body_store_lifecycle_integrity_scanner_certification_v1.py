from __future__ import annotations

import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.universal_article_body_store.body_store_lifecycle_integrity_scanner_verifier_v1 import (
    BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_VERIFIER_VERSION,
    verify_lifecycle_integrity_scanner_v1,
)


BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CERTIFICATION_VERSION = "1.0"

BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CERTIFICATION_SCHEMA = (
    "body_store_lifecycle_integrity_scanner_certification.v1"
)

BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CERTIFICATION_BUNDLE_SCHEMA = (
    "body_store_lifecycle_integrity_scanner_certification_bundle.v1"
)


class LifecycleIntegrityScannerCertificationError(
    ValueError
):
    """Raised when lifecycle integrity scanner certification cannot proceed."""


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
                    _freeze(
                        item
                    )

                for key, item
                in value.items()
            }
        )

    if isinstance(
        value,
        list,
    ):
        return tuple(
            _freeze(
                item
            )

            for item
            in value
        )

    if isinstance(
        value,
        tuple,
    ):
        return tuple(
            _freeze(
                item
            )

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
        raise LifecycleIntegrityScannerCertificationError(
            field_name
            + " must be a mapping."
        )

    return value


def _json_ready(
    value: Any,
) -> Any:

    if isinstance(
        value,
        Mapping,
    ):
        return {
            str(
                key
            ):
                _json_ready(
                    item
                )

            for key, item
            in value.items()
        }

    if isinstance(
        value,
        (
            tuple,
            list,
        ),
    ):
        return [
            _json_ready(
                item
            )

            for item
            in value
        ]

    return value


def calculate_lifecycle_integrity_scanner_certification_checksum_v1(
    *,
    payload: Mapping[str, Any],
) -> str:

    _require_mapping(
        payload,
        field_name="payload",
    )

    serialized = json.dumps(
        _json_ready(
            payload
        ),
        ensure_ascii=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    )

    return hashlib.sha256(
        serialized.encode(
            "utf-8"
        )
    ).hexdigest()
def build_lifecycle_integrity_scanner_certification_v1(
    *,
    project_root,
    scan_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        scan_request,
        field_name="scan_request",
    )

    verification = (
        verify_lifecycle_integrity_scanner_v1(
            project_root=project_root,
            scan_request=request,
        )
    )

    if (
        verification[
            "verification_passed"
        ]
        is not True
    ):
        raise LifecycleIntegrityScannerCertificationError(
            "Lifecycle Integrity Scanner verification did not pass."
        )

    certification_material = {
        "verification_checksum":
            verification[
                "verification_checksum"
            ],

        "scan_request_id":
            verification[
                "scan_request_id"
            ],

        "workspace_id":
            verification[
                "workspace_id"
            ],

        "request_identity_verified":
            verification[
                "request"
            ][
                "request_identity_verified"
            ],

        "report_structure_verified":
            verification[
                "structure"
            ][
                "report_structure_verified"
            ],

        "findings_verified":
            verification[
                "findings"
            ][
                "findings_verified"
            ],

        "cross_store_accuracy_verified":
            verification[
                "cross_store_accuracy"
            ][
                "cross_store_accuracy_verified"
            ],

        "reproducibility_verified":
            verification[
                "reproducibility"
            ][
                "reproducibility_verified"
            ],
    }

    certification_id = (
        "body_store_lifecycle_integrity_scanner_certification_"
        + calculate_lifecycle_integrity_scanner_certification_checksum_v1(
            payload=certification_material,
        )
    )

    certification = {
        "schema":
            BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CERTIFICATION_SCHEMA,

        "certification_version":
            BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CERTIFICATION_VERSION,

        "verifier_version":
            BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_VERIFIER_VERSION,

        "certification_id":
            certification_id,

        "verification_checksum":
            verification[
                "verification_checksum"
            ],

        "scan_request_id":
            verification[
                "scan_request_id"
            ],

        "workspace_id":
            verification[
                "workspace_id"
            ],

        "certified":
            True,

        "verification_passed":
            verification[
                "verification_passed"
            ],

        "verification":
            verification,

        "request_identity":
            verification[
                "request"
            ],

        "report_structure":
            verification[
                "structure"
            ],

        "findings":
            verification[
                "findings"
            ],

        "cross_store_accuracy":
            verification[
                "cross_store_accuracy"
            ],

        "reproducibility":
            verification[
                "reproducibility"
            ],

        "read_only":
            True,

        "repair_planned":
            False,

        "repair_executed":
            False,

        "lifecycle_modified":
            False,

        "archive_modified":
            False,

        "tombstone_modified":
            False,

        "body_store_modified":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    return _freeze(
        certification
    )


def summarize_lifecycle_integrity_scanner_certification_v1(
    *,
    certification: Mapping[str, Any],
) -> Mapping[str, Any]:

    cert = _require_mapping(
        certification,
        field_name="certification",
    )

    findings = _require_mapping(
        cert[
            "findings"
        ],
        field_name="findings",
    )

    summary = {
        "certification_id":
            cert[
                "certification_id"
            ],

        "verification_checksum":
            cert[
                "verification_checksum"
            ],

        "scan_request_id":
            cert[
                "scan_request_id"
            ],

        "workspace_id":
            cert[
                "workspace_id"
            ],

        "certified":
            cert[
                "certified"
            ],

        "verification_passed":
            cert[
                "verification_passed"
            ],

        "request_identity_verified":
            cert[
                "request_identity"
            ][
                "request_identity_verified"
            ],

        "report_structure_verified":
            cert[
                "report_structure"
            ][
                "report_structure_verified"
            ],

        "findings_verified":
            findings[
                "findings_verified"
            ],

        "cross_store_accuracy_verified":
            cert[
                "cross_store_accuracy"
            ][
                "cross_store_accuracy_verified"
            ],

        "reproducibility_verified":
            cert[
                "reproducibility"
            ][
                "reproducibility_verified"
            ],

        "finding_type_counts":
            findings[
                "finding_type_counts"
            ],

        "severity_counts":
            findings[
                "severity_counts"
            ],

        "read_only":
            True,

        "repair_planned":
            False,

        "repair_executed":
            False,

        "lifecycle_modified":
            False,

        "archive_modified":
            False,

        "tombstone_modified":
            False,

        "body_store_modified":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    return _freeze(
        summary
    )
def validate_lifecycle_integrity_scanner_certification_v1(
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
        "verification_checksum",
        "scan_request_id",
        "workspace_id",
        "certified",
        "verification_passed",
        "verification",
        "request_identity",
        "report_structure",
        "findings",
        "cross_store_accuracy",
        "reproducibility",
        "read_only",
        "repair_planned",
        "repair_executed",
        "lifecycle_modified",
        "archive_modified",
        "tombstone_modified",
        "body_store_modified",
        "runtime_job_created",
        "queue_job_created",
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
        == BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CERTIFICATION_SCHEMA
    )

    certification_version_valid = (
        cert.get(
            "certification_version"
        )
        == BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CERTIFICATION_VERSION
    )

    verifier_version_valid = (
        cert.get(
            "verifier_version"
        )
        == BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_VERIFIER_VERSION
    )

    verification = cert.get(
        "verification",
        {},
    )

    verification_mapping_valid = isinstance(
        verification,
        Mapping,
    )

    verification_passed = (
        verification_mapping_valid
        and verification.get(
            "verification_passed"
        )
        is True
        and cert.get(
            "verification_passed"
        )
        is True
    )

    verification_checksum_matches = (
        verification_mapping_valid
        and cert.get(
            "verification_checksum"
        )
        == verification.get(
            "verification_checksum"
        )
    )

    scan_request_id_matches = (
        verification_mapping_valid
        and cert.get(
            "scan_request_id"
        )
        == verification.get(
            "scan_request_id"
        )
    )

    workspace_id_matches = (
        verification_mapping_valid
        and cert.get(
            "workspace_id"
        )
        == verification.get(
            "workspace_id"
        )
    )

    request_identity = cert.get(
        "request_identity",
        {},
    )

    report_structure = cert.get(
        "report_structure",
        {},
    )

    findings = cert.get(
        "findings",
        {},
    )

    cross_store_accuracy = cert.get(
        "cross_store_accuracy",
        {},
    )

    reproducibility = cert.get(
        "reproducibility",
        {},
    )

    request_identity_verified = (
        isinstance(
            request_identity,
            Mapping,
        )
        and request_identity.get(
            "request_identity_verified"
        )
        is True
    )

    report_structure_verified = (
        isinstance(
            report_structure,
            Mapping,
        )
        and report_structure.get(
            "report_structure_verified"
        )
        is True
    )

    findings_verified = (
        isinstance(
            findings,
            Mapping,
        )
        and findings.get(
            "findings_verified"
        )
        is True
    )

    cross_store_accuracy_verified = (
        isinstance(
            cross_store_accuracy,
            Mapping,
        )
        and cross_store_accuracy.get(
            "cross_store_accuracy_verified"
        )
        is True
    )

    reproducibility_verified = (
        isinstance(
            reproducibility,
            Mapping,
        )
        and reproducibility.get(
            "reproducibility_verified"
        )
        is True
    )

    safety_boundaries_valid = all(
        (
            cert.get(
                "read_only"
            )
            is True,

            cert.get(
                "repair_planned"
            )
            is False,

            cert.get(
                "repair_executed"
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
                "tombstone_modified"
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
            verification_mapping_valid,
            verification_passed,
            verification_checksum_matches,
            scan_request_id_matches,
            workspace_id_matches,
            request_identity_verified,
            report_structure_verified,
            findings_verified,
            cross_store_accuracy_verified,
            reproducibility_verified,
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

        "verification_mapping_valid":
            verification_mapping_valid,

        "verification_passed":
            verification_passed,

        "verification_checksum_matches":
            verification_checksum_matches,

        "scan_request_id_matches":
            scan_request_id_matches,

        "workspace_id_matches":
            workspace_id_matches,

        "request_identity_verified":
            request_identity_verified,

        "report_structure_verified":
            report_structure_verified,

        "findings_verified":
            findings_verified,

        "cross_store_accuracy_verified":
            cross_store_accuracy_verified,

        "reproducibility_verified":
            reproducibility_verified,

        "safety_boundaries_valid":
            safety_boundaries_valid,

        "read_only":
            True,

        "repair_planned":
            False,

        "repair_executed":
            False,

        "lifecycle_modified":
            False,

        "archive_modified":
            False,

        "tombstone_modified":
            False,

        "body_store_modified":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    return _freeze(
        validation
    )
def build_lifecycle_integrity_scanner_certification_bundle_v1(
    *,
    project_root,
    scan_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    certification = (
        build_lifecycle_integrity_scanner_certification_v1(
            project_root=project_root,
            scan_request=scan_request,
        )
    )

    validation = (
        validate_lifecycle_integrity_scanner_certification_v1(
            certification=certification,
        )
    )

    summary = (
        summarize_lifecycle_integrity_scanner_certification_v1(
            certification=certification,
        )
    )

    bundle = {
        "schema":
            BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CERTIFICATION_BUNDLE_SCHEMA,

        "bundle_version":
            BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CERTIFICATION_VERSION,

        "certification":
            certification,

        "validation":
            validation,

        "summary":
            summary,

        "bundle_certified":
            validation[
                "certification_valid"
            ],

        "bundle_read_only":
            True,

        "repair_planned":
            False,

        "repair_executed":
            False,

        "lifecycle_modified":
            False,

        "archive_modified":
            False,

        "tombstone_modified":
            False,

        "body_store_modified":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    checksum_source = {
        key: value
        for key, value in bundle.items()
        if key != "bundle_checksum"
    }

    bundle["bundle_checksum"] = (
        calculate_lifecycle_integrity_scanner_certification_checksum_v1(
            payload=checksum_source,
        )
    )

    return _freeze(
        bundle
    )


__all__ = [
    "BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CERTIFICATION_SCHEMA",
    "BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CERTIFICATION_BUNDLE_SCHEMA",
    "BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CERTIFICATION_VERSION",
    "calculate_lifecycle_integrity_scanner_certification_checksum_v1",
    "build_lifecycle_integrity_scanner_certification_v1",
    "summarize_lifecycle_integrity_scanner_certification_v1",
    "validate_lifecycle_integrity_scanner_certification_v1",
    "build_lifecycle_integrity_scanner_certification_bundle_v1",
]
