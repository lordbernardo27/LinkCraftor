from __future__ import annotations

import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.universal_article_body_store.body_store_lifecycle_analytics_verifier_v1 import (
    BODY_STORE_LIFECYCLE_ANALYTICS_VERIFIER_VERSION,
    verify_lifecycle_analytics_v1,
)


BODY_STORE_LIFECYCLE_ANALYTICS_CERTIFICATION_VERSION = "1.0"

BODY_STORE_LIFECYCLE_ANALYTICS_CERTIFICATION_SCHEMA = (
    "body_store_lifecycle_analytics_certification.v1"
)

BODY_STORE_LIFECYCLE_ANALYTICS_CERTIFICATION_BUNDLE_SCHEMA = (
    "body_store_lifecycle_analytics_certification_bundle.v1"
)


class LifecycleAnalyticsCertificationError(
    ValueError
):
    """Raised when lifecycle analytics certification cannot proceed."""


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

            for item in value
        )

    if isinstance(
        value,
        tuple,
    ):
        return tuple(
            _freeze(
                item
            )

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
        raise LifecycleAnalyticsCertificationError(
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

            for item in value
        ]

    return value


def calculate_lifecycle_analytics_certification_checksum_v1(
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
def build_lifecycle_analytics_certification_v1(
    *,
    project_root,
    analytics_request: Mapping[str, Any],
    analytics_report: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        analytics_request,
        field_name="analytics_request",
    )

    report = _require_mapping(
        analytics_report,
        field_name="analytics_report",
    )

    verification = (
        verify_lifecycle_analytics_v1(
            project_root=project_root,
            analytics_request=request,
            analytics_report=report,
        )
    )

    if verification[
        "analytics_verified"
    ] is not True:
        raise LifecycleAnalyticsCertificationError(
            "Lifecycle analytics verification did not pass."
        )

    certification_material = {
        "verification_id":
            verification[
                "verification_id"
            ],

        "analytics_request_id":
            verification[
                "analytics_request_id"
            ],

        "scope":
            verification[
                "scope"
            ],

        "workspace_id":
            verification[
                "workspace_id"
            ],

        "period_start":
            verification[
                "period_start"
            ],

        "period_end":
            verification[
                "period_end"
            ],

        "report_checksum":
            verification[
                "report_checksum"
            ],

        "analytics_verified":
            verification[
                "analytics_verified"
            ],
    }

    certification_id = (
        "body_store_lifecycle_analytics_certification_"
        + calculate_lifecycle_analytics_certification_checksum_v1(
            payload=certification_material,
        )
    )

    certification = {
        "schema":
            BODY_STORE_LIFECYCLE_ANALYTICS_CERTIFICATION_SCHEMA,

        "certification_version":
            BODY_STORE_LIFECYCLE_ANALYTICS_CERTIFICATION_VERSION,

        "verifier_version":
            BODY_STORE_LIFECYCLE_ANALYTICS_VERIFIER_VERSION,

        "certification_id":
            certification_id,

        "verification_id":
            verification[
                "verification_id"
            ],

        "analytics_request_id":
            verification[
                "analytics_request_id"
            ],

        "scope":
            verification[
                "scope"
            ],

        "workspace_id":
            verification[
                "workspace_id"
            ],

        "period_start":
            verification[
                "period_start"
            ],

        "period_end":
            verification[
                "period_end"
            ],

        "report_checksum":
            verification[
                "report_checksum"
            ],

        "analytics_verified":
            verification[
                "analytics_verified"
            ],

        "certified":
            True,

        "verification":
            verification,

        "request_identity":
            verification[
                "request_identity"
            ],

        "report_structure":
            verification[
                "report_structure"
            ],

        "metric_accuracy":
            verification[
                "metric_accuracy"
            ],

        "reproducibility":
            verification[
                "reproducibility"
            ],

        "safety_boundaries":
            verification[
                "safety_boundaries"
            ],

        "report_summary":
            verification[
                "report_summary"
            ],

        "read_only":
            True,

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


def summarize_lifecycle_analytics_certification_v1(
    *,
    certification: Mapping[str, Any],
) -> Mapping[str, Any]:

    cert = _require_mapping(
        certification,
        field_name="certification",
    )

    report_summary = _require_mapping(
        cert[
            "report_summary"
        ],
        field_name="report_summary",
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

        "analytics_request_id":
            cert[
                "analytics_request_id"
            ],

        "scope":
            cert[
                "scope"
            ],

        "workspace_id":
            cert[
                "workspace_id"
            ],

        "period_start":
            cert[
                "period_start"
            ],

        "period_end":
            cert[
                "period_end"
            ],

        "certified":
            cert[
                "certified"
            ],

        "analytics_verified":
            cert[
                "analytics_verified"
            ],

        "active_count":
            report_summary[
                "active_count"
            ],

        "archived_count":
            report_summary[
                "archived_count"
            ],

        "restored_count":
            report_summary[
                "restored_count"
            ],

        "permanently_deleted_count":
            report_summary[
                "permanently_deleted_count"
            ],

        "unique_archive_count":
            report_summary[
                "unique_archive_count"
            ],

        "valid_tombstone_count":
            report_summary[
                "valid_tombstone_count"
            ],

        "deletion_tombstone_gap":
            report_summary[
                "deletion_tombstone_gap"
            ],

        "retention_expired_count":
            report_summary[
                "retention_expired_count"
            ],

        "retention_active_count":
            report_summary[
                "retention_active_count"
            ],

        "read_only":
            True,

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
def validate_lifecycle_analytics_certification_v1(
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
        "analytics_request_id",
        "scope",
        "workspace_id",
        "period_start",
        "period_end",
        "report_checksum",
        "analytics_verified",
        "certified",
        "verification",
        "request_identity",
        "report_structure",
        "metric_accuracy",
        "reproducibility",
        "safety_boundaries",
        "report_summary",
        "read_only",
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
        == BODY_STORE_LIFECYCLE_ANALYTICS_CERTIFICATION_SCHEMA
    )

    certification_version_valid = (
        cert.get(
            "certification_version"
        )
        == BODY_STORE_LIFECYCLE_ANALYTICS_CERTIFICATION_VERSION
    )

    verifier_version_valid = (
        cert.get(
            "verifier_version"
        )
        == BODY_STORE_LIFECYCLE_ANALYTICS_VERIFIER_VERSION
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
            "analytics_verified"
        )
        is True
    )

    verification_id_matches = (
        verification_mapping_valid
        and cert.get(
            "verification_id"
        )
        == verification.get(
            "verification_id"
        )
    )

    request_id_matches = (
        verification_mapping_valid
        and cert.get(
            "analytics_request_id"
        )
        == verification.get(
            "analytics_request_id"
        )
    )

    scope_matches = (
        verification_mapping_valid
        and cert.get(
            "scope"
        )
        == verification.get(
            "scope"
        )
    )

    workspace_matches = (
        verification_mapping_valid
        and cert.get(
            "workspace_id"
        )
        == verification.get(
            "workspace_id"
        )
    )

    period_start_matches = (
        verification_mapping_valid
        and cert.get(
            "period_start"
        )
        == verification.get(
            "period_start"
        )
    )

    period_end_matches = (
        verification_mapping_valid
        and cert.get(
            "period_end"
        )
        == verification.get(
            "period_end"
        )
    )

    report_checksum_matches = (
        verification_mapping_valid
        and cert.get(
            "report_checksum"
        )
        == verification.get(
            "report_checksum"
        )
    )

    request_identity_verified = (
        cert.get(
            "request_identity",
            {},
        ).get(
            "request_identity_verified"
        )
        is True
    )

    report_structure_verified = (
        cert.get(
            "report_structure",
            {},
        ).get(
            "report_structure_verified"
        )
        is True
    )

    metric_accuracy_verified = (
        cert.get(
            "metric_accuracy",
            {},
        ).get(
            "metric_accuracy_verified"
        )
        is True
    )

    reproducibility_verified = (
        cert.get(
            "reproducibility",
            {},
        ).get(
            "reproducibility_verified"
        )
        is True
    )

    safety_boundaries_verified = (
        cert.get(
            "safety_boundaries",
            {},
        ).get(
            "safety_boundaries_verified"
        )
        is True
    )

    report_summary_valid = isinstance(
        cert.get(
            "report_summary"
        ),
        Mapping,
    )

    safety_boundaries_valid = all(
        (
            cert.get(
                "read_only"
            )
            is True,
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
                "analytics_verified"
            )
            is True,
            cert.get(
                "certified"
            )
            is True,
            verification_passed,
            verification_id_matches,
            request_id_matches,
            scope_matches,
            workspace_matches,
            period_start_matches,
            period_end_matches,
            report_checksum_matches,
            request_identity_verified,
            report_structure_verified,
            metric_accuracy_verified,
            reproducibility_verified,
            safety_boundaries_verified,
            report_summary_valid,
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

        "verification_id_matches":
            verification_id_matches,

        "request_id_matches":
            request_id_matches,

        "scope_matches":
            scope_matches,

        "workspace_matches":
            workspace_matches,

        "period_start_matches":
            period_start_matches,

        "period_end_matches":
            period_end_matches,

        "report_checksum_matches":
            report_checksum_matches,

        "request_identity_verified":
            request_identity_verified,

        "report_structure_verified":
            report_structure_verified,

        "metric_accuracy_verified":
            metric_accuracy_verified,

        "reproducibility_verified":
            reproducibility_verified,

        "safety_boundaries_verified":
            safety_boundaries_verified,

        "report_summary_valid":
            report_summary_valid,

        "safety_boundaries_valid":
            safety_boundaries_valid,

        "read_only":
            True,

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
def build_lifecycle_analytics_certification_bundle_v1(
    *,
    project_root,
    analytics_request: Mapping[str, Any],
    analytics_report: Mapping[str, Any],
) -> Mapping[str, Any]:

    certification = (
        build_lifecycle_analytics_certification_v1(
            project_root=project_root,
            analytics_request=analytics_request,
            analytics_report=analytics_report,
        )
    )

    validation = (
        validate_lifecycle_analytics_certification_v1(
            certification=certification,
        )
    )

    if validation[
        "certification_valid"
    ] is not True:
        raise LifecycleAnalyticsCertificationError(
            "Lifecycle analytics certification validation failed."
        )

    summary = (
        summarize_lifecycle_analytics_certification_v1(
            certification=certification,
        )
    )

    bundle = {
        "schema":
            BODY_STORE_LIFECYCLE_ANALYTICS_CERTIFICATION_BUNDLE_SCHEMA,

        "certification_version":
            BODY_STORE_LIFECYCLE_ANALYTICS_CERTIFICATION_VERSION,

        "certification":
            certification,

        "validation":
            validation,

        "summary":
            summary,

        "certification_id":
            certification[
                "certification_id"
            ],

        "verification_id":
            certification[
                "verification_id"
            ],

        "analytics_request_id":
            certification[
                "analytics_request_id"
            ],

        "scope":
            certification[
                "scope"
            ],

        "workspace_id":
            certification[
                "workspace_id"
            ],

        "certified":
            certification[
                "certified"
            ]
            is True,

        "analytics_verified":
            certification[
                "analytics_verified"
            ]
            is True,

        "request_identity_verified":
            validation[
                "request_identity_verified"
            ]
            is True,

        "report_structure_verified":
            validation[
                "report_structure_verified"
            ]
            is True,

        "metric_accuracy_verified":
            validation[
                "metric_accuracy_verified"
            ]
            is True,

        "reproducibility_verified":
            validation[
                "reproducibility_verified"
            ]
            is True,

        "safety_boundaries_verified":
            validation[
                "safety_boundaries_verified"
            ]
            is True,

        "bundle_complete":
            all(
                (
                    certification[
                        "certified"
                    ]
                    is True,
                    certification[
                        "analytics_verified"
                    ]
                    is True,
                    validation[
                        "certification_valid"
                    ]
                    is True,
                    validation[
                        "request_identity_verified"
                    ]
                    is True,
                    validation[
                        "report_structure_verified"
                    ]
                    is True,
                    validation[
                        "metric_accuracy_verified"
                    ]
                    is True,
                    validation[
                        "reproducibility_verified"
                    ]
                    is True,
                    validation[
                        "safety_boundaries_verified"
                    ]
                    is True,
                )
            ),

        "read_only":
            True,

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

    bundle_checksum_source = {
        key:
            value

        for key, value
        in bundle.items()

        if key != "bundle_checksum"
    }

    bundle[
        "bundle_checksum"
    ] = (
        calculate_lifecycle_analytics_certification_checksum_v1(
            payload=bundle_checksum_source,
        )
    )

    return _freeze(
        bundle
    )


def verify_lifecycle_analytics_certification_bundle_v1(
    *,
    certification_bundle: Mapping[str, Any],
) -> Mapping[str, Any]:

    bundle = _require_mapping(
        certification_bundle,
        field_name="certification_bundle",
    )

    required_sections = (
        "certification",
        "validation",
        "summary",
    )

    missing_sections = tuple(
        section
        for section in required_sections
        if section not in bundle
    )

    certification = bundle.get(
        "certification",
        {},
    )

    validation = bundle.get(
        "validation",
        {},
    )

    summary = bundle.get(
        "summary",
        {},
    )

    certification_mapping_valid = isinstance(
        certification,
        Mapping,
    )

    validation_mapping_valid = isinstance(
        validation,
        Mapping,
    )

    summary_mapping_valid = isinstance(
        summary,
        Mapping,
    )

    certification_id_matches = (
        certification_mapping_valid
        and summary_mapping_valid
        and bundle.get(
            "certification_id"
        )
        == certification.get(
            "certification_id"
        )
        == summary.get(
            "certification_id"
        )
    )

    verification_id_matches = (
        certification_mapping_valid
        and summary_mapping_valid
        and bundle.get(
            "verification_id"
        )
        == certification.get(
            "verification_id"
        )
        == summary.get(
            "verification_id"
        )
    )

    request_id_matches = (
        certification_mapping_valid
        and summary_mapping_valid
        and bundle.get(
            "analytics_request_id"
        )
        == certification.get(
            "analytics_request_id"
        )
        == summary.get(
            "analytics_request_id"
        )
    )

    scope_matches = (
        certification_mapping_valid
        and summary_mapping_valid
        and bundle.get(
            "scope"
        )
        == certification.get(
            "scope"
        )
        == summary.get(
            "scope"
        )
    )

    workspace_matches = (
        certification_mapping_valid
        and summary_mapping_valid
        and bundle.get(
            "workspace_id"
        )
        == certification.get(
            "workspace_id"
        )
        == summary.get(
            "workspace_id"
        )
    )

    certification_confirmed = (
        certification_mapping_valid
        and certification.get(
            "certified"
        )
        is True
        and bundle.get(
            "certified"
        )
        is True
    )

    analytics_verification_confirmed = (
        certification_mapping_valid
        and certification.get(
            "analytics_verified"
        )
        is True
        and bundle.get(
            "analytics_verified"
        )
        is True
    )

    validation_confirmed = (
        validation_mapping_valid
        and validation.get(
            "certification_valid"
        )
        is True
    )

    evidence_confirmed = all(
        (
            bundle.get(
                "request_identity_verified"
            )
            is True,
            bundle.get(
                "report_structure_verified"
            )
            is True,
            bundle.get(
                "metric_accuracy_verified"
            )
            is True,
            bundle.get(
                "reproducibility_verified"
            )
            is True,
            bundle.get(
                "safety_boundaries_verified"
            )
            is True,
        )
    )

    safety_boundaries_valid = all(
        (
            bundle.get(
                "read_only"
            )
            is True,
            bundle.get(
                "lifecycle_modified"
            )
            is False,
            bundle.get(
                "archive_modified"
            )
            is False,
            bundle.get(
                "tombstone_modified"
            )
            is False,
            bundle.get(
                "body_store_modified"
            )
            is False,
            bundle.get(
                "runtime_job_created"
            )
            is False,
            bundle.get(
                "queue_job_created"
            )
            is False,
        )
    )

    checksum_source = {
        key:
            value

        for key, value
        in bundle.items()

        if key != "bundle_checksum"
    }

    calculated_checksum = (
        calculate_lifecycle_analytics_certification_checksum_v1(
            payload=checksum_source,
        )
    )

    bundle_checksum_valid = (
        calculated_checksum
        == bundle.get(
            "bundle_checksum"
        )
    )

    bundle_valid = all(
        (
            not missing_sections,
            certification_mapping_valid,
            validation_mapping_valid,
            summary_mapping_valid,
            bundle.get(
                "schema"
            )
            == BODY_STORE_LIFECYCLE_ANALYTICS_CERTIFICATION_BUNDLE_SCHEMA,
            bundle.get(
                "certification_version"
            )
            == BODY_STORE_LIFECYCLE_ANALYTICS_CERTIFICATION_VERSION,
            bundle.get(
                "bundle_complete"
            )
            is True,
            certification_id_matches,
            verification_id_matches,
            request_id_matches,
            scope_matches,
            workspace_matches,
            certification_confirmed,
            analytics_verification_confirmed,
            validation_confirmed,
            evidence_confirmed,
            safety_boundaries_valid,
            bundle_checksum_valid,
        )
    )

    result = {
        "bundle_valid":
            bundle_valid,

        "missing_sections":
            missing_sections,

        "certification_mapping_valid":
            certification_mapping_valid,

        "validation_mapping_valid":
            validation_mapping_valid,

        "summary_mapping_valid":
            summary_mapping_valid,

        "schema_valid":
            bundle.get(
                "schema"
            )
            == BODY_STORE_LIFECYCLE_ANALYTICS_CERTIFICATION_BUNDLE_SCHEMA,

        "certification_version_valid":
            bundle.get(
                "certification_version"
            )
            == BODY_STORE_LIFECYCLE_ANALYTICS_CERTIFICATION_VERSION,

        "bundle_complete":
            bundle.get(
                "bundle_complete"
            )
            is True,

        "certification_id_matches":
            certification_id_matches,

        "verification_id_matches":
            verification_id_matches,

        "request_id_matches":
            request_id_matches,

        "scope_matches":
            scope_matches,

        "workspace_matches":
            workspace_matches,

        "certification_confirmed":
            certification_confirmed,

        "analytics_verification_confirmed":
            analytics_verification_confirmed,

        "validation_confirmed":
            validation_confirmed,

        "evidence_confirmed":
            evidence_confirmed,

        "safety_boundaries_valid":
            safety_boundaries_valid,

        "bundle_checksum_valid":
            bundle_checksum_valid,

        "calculated_checksum":
            calculated_checksum,

        "stored_checksum":
            bundle.get(
                "bundle_checksum"
            ),

        "read_only":
            True,

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
        result
    )


__all__ = [
    "BODY_STORE_LIFECYCLE_ANALYTICS_CERTIFICATION_VERSION",
    "BODY_STORE_LIFECYCLE_ANALYTICS_CERTIFICATION_SCHEMA",
    "BODY_STORE_LIFECYCLE_ANALYTICS_CERTIFICATION_BUNDLE_SCHEMA",
    "LifecycleAnalyticsCertificationError",
    "calculate_lifecycle_analytics_certification_checksum_v1",
    "build_lifecycle_analytics_certification_v1",
    "summarize_lifecycle_analytics_certification_v1",
    "validate_lifecycle_analytics_certification_v1",
    "build_lifecycle_analytics_certification_bundle_v1",
    "verify_lifecycle_analytics_certification_bundle_v1",
]
