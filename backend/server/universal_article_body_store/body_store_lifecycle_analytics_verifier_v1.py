from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.universal_article_body_store.body_store_lifecycle_analytics_contract_v1 import (
    BODY_STORE_LIFECYCLE_ANALYTICS_REPORT_SCHEMA,
    validate_lifecycle_analytics_request_v1,
)

from backend.server.universal_article_body_store.body_store_lifecycle_analytics_engine_v1 import (
    BODY_STORE_LIFECYCLE_ANALYTICS_ENGINE_SCHEMA,
    BODY_STORE_LIFECYCLE_ANALYTICS_ENGINE_VERSION,
    build_lifecycle_analytics_report_v1,
    calculate_lifecycle_analytics_report_checksum_v1,
    summarize_lifecycle_analytics_report_v1,
    verify_lifecycle_analytics_report_v1,
)


BODY_STORE_LIFECYCLE_ANALYTICS_VERIFIER_VERSION = "1.0"

BODY_STORE_LIFECYCLE_ANALYTICS_VERIFIER_SCHEMA = (
    "body_store_lifecycle_analytics_verifier.v1"
)


class LifecycleAnalyticsVerificationError(
    ValueError
):
    """Raised when independent lifecycle analytics verification fails."""


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
        raise LifecycleAnalyticsVerificationError(
            field_name
            + " must be a mapping."
        )

    return value


def _require_string(
    value: Any,
    *,
    field_name: str,
) -> str:

    if not isinstance(
        value,
        str,
    ):
        raise LifecycleAnalyticsVerificationError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise LifecycleAnalyticsVerificationError(
            field_name
            + " must not be empty."
        )

    return normalized


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


def calculate_lifecycle_analytics_verification_checksum_v1(
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
def verify_lifecycle_analytics_request_identity_v1(
    *,
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

    request_validation = (
        validate_lifecycle_analytics_request_v1(
            analytics_request=request,
        )
    )

    request_id_matches = (
        request.get(
            "analytics_request_id"
        )
        == report.get(
            "analytics_request_id"
        )
    )

    scope_matches = (
        request.get(
            "scope"
        )
        == report.get(
            "scope"
        )
    )

    workspace_matches = (
        request.get(
            "workspace_id"
        )
        == report.get(
            "workspace_id"
        )
    )

    period_start_matches = (
        request.get(
            "period_start"
        )
        == report.get(
            "period_start"
        )
    )

    period_end_matches = (
        request.get(
            "period_end"
        )
        == report.get(
            "period_end"
        )
    )

    result = {
        "request_valid":
            request_validation[
                "request_valid"
            ]
            is True,

        "request_checksum_valid":
            request_validation[
                "checksum_valid"
            ]
            is True,

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

        "request_identity_verified":
            all(
                (
                    request_validation[
                        "request_valid"
                    ]
                    is True,
                    request_validation[
                        "checksum_valid"
                    ]
                    is True,
                    request_id_matches,
                    scope_matches,
                    workspace_matches,
                    period_start_matches,
                    period_end_matches,
                )
            ),
    }

    return _freeze(
        result
    )


def verify_lifecycle_analytics_report_structure_v1(
    *,
    analytics_report: Mapping[str, Any],
) -> Mapping[str, Any]:

    report = _require_mapping(
        analytics_report,
        field_name="analytics_report",
    )

    engine_verification = (
        verify_lifecycle_analytics_report_v1(
            analytics_report=report,
        )
    )

    metrics = report.get(
        "metrics",
        {},
    )

    metric_groups = (
        tuple(
            sorted(
                metrics.keys()
            )
        )
        if isinstance(
            metrics,
            Mapping,
        )
        else ()
    )

    required_metric_groups = (
        "archive_metrics",
        "deletion_metrics",
        "restore_metrics",
        "retention_metrics",
        "state_counts",
        "tombstone_metrics",
    )

    metric_groups_complete = (
        metric_groups
        == required_metric_groups
    )

    result = {
        "report_schema_valid":
            report.get(
                "schema"
            )
            == BODY_STORE_LIFECYCLE_ANALYTICS_REPORT_SCHEMA,

        "engine_schema_valid":
            report.get(
                "engine_schema"
            )
            == BODY_STORE_LIFECYCLE_ANALYTICS_ENGINE_SCHEMA,

        "engine_version_valid":
            report.get(
                "engine_version"
            )
            == BODY_STORE_LIFECYCLE_ANALYTICS_ENGINE_VERSION,

        "engine_report_valid":
            engine_verification[
                "report_valid"
            ]
            is True,

        "report_checksum_valid":
            engine_verification[
                "checksum_valid"
            ]
            is True,

        "metrics_mapping_valid":
            isinstance(
                metrics,
                Mapping,
            ),

        "metric_group_count_valid":
            report.get(
                "metric_group_count"
            )
            == len(
                metric_groups
            ),

        "metric_groups_complete":
            metric_groups_complete,

        "metric_groups":
            metric_groups,

        "report_structure_verified":
            all(
                (
                    report.get(
                        "schema"
                    )
                    == BODY_STORE_LIFECYCLE_ANALYTICS_REPORT_SCHEMA,
                    report.get(
                        "engine_schema"
                    )
                    == BODY_STORE_LIFECYCLE_ANALYTICS_ENGINE_SCHEMA,
                    report.get(
                        "engine_version"
                    )
                    == BODY_STORE_LIFECYCLE_ANALYTICS_ENGINE_VERSION,
                    engine_verification[
                        "report_valid"
                    ]
                    is True,
                    engine_verification[
                        "checksum_valid"
                    ]
                    is True,
                    isinstance(
                        metrics,
                        Mapping,
                    ),
                    report.get(
                        "metric_group_count"
                    )
                    == len(
                        metric_groups
                    ),
                    metric_groups_complete,
                )
            ),
    }

    return _freeze(
        result
    )
def verify_lifecycle_analytics_metric_accuracy_v1(
    *,
    analytics_report: Mapping[str, Any],
) -> Mapping[str, Any]:

    report = _require_mapping(
        analytics_report,
        field_name="analytics_report",
    )

    metrics = _require_mapping(
        report[
            "metrics"
        ],
        field_name="metrics",
    )

    state_counts = _require_mapping(
        metrics[
            "state_counts"
        ],
        field_name="state_counts",
    )

    archive_metrics = _require_mapping(
        metrics[
            "archive_metrics"
        ],
        field_name="archive_metrics",
    )

    restore_metrics = _require_mapping(
        metrics[
            "restore_metrics"
        ],
        field_name="restore_metrics",
    )

    deletion_metrics = _require_mapping(
        metrics[
            "deletion_metrics"
        ],
        field_name="deletion_metrics",
    )

    tombstone_metrics = _require_mapping(
        metrics[
            "tombstone_metrics"
        ],
        field_name="tombstone_metrics",
    )

    retention_metrics = _require_mapping(
        metrics[
            "retention_metrics"
        ],
        field_name="retention_metrics",
    )

    counts_by_state = _require_mapping(
        state_counts[
            "counts_by_state"
        ],
        field_name="counts_by_state",
    )

    state_counts_non_negative = all(
        isinstance(
            counts_by_state.get(
                state
            ),
            int,
        )
        and counts_by_state.get(
            state
        )
        >= 0

        for state in (
            "ACTIVE",
            "ARCHIVED",
            "RESTORED",
            "PERMANENTLY_DELETED",
        )
    )

    lifecycle_total_matches = (
        sum(
            int(
                counts_by_state.get(
                    state,
                    0,
                )
            )

            for state in (
                "ACTIVE",
                "ARCHIVED",
                "RESTORED",
                "PERMANENTLY_DELETED",
            )
        )
        == state_counts.get(
            "valid_records"
        )
    )

    restore_count_matches = (
        restore_metrics.get(
            "restored_count"
        )
        == counts_by_state.get(
            "RESTORED"
        )
        and restore_metrics.get(
            "restore_events_inferred_from_lifecycle"
        )
        == counts_by_state.get(
            "RESTORED"
        )
    )

    deletion_count_matches = (
        deletion_metrics.get(
            "permanently_deleted_count"
        )
        == counts_by_state.get(
            "PERMANENTLY_DELETED"
        )
    )

    tombstone_count_matches = (
        deletion_metrics.get(
            "certified_tombstone_count"
        )
        == tombstone_metrics.get(
            "valid_tombstones"
        )
    )

    expected_deletion_tombstone_gap = max(
        int(
            counts_by_state.get(
                "PERMANENTLY_DELETED",
                0,
            )
        )
        - int(
            tombstone_metrics.get(
                "valid_tombstones",
                0,
            )
        ),
        0,
    )

    deletion_tombstone_gap_valid = (
        deletion_metrics.get(
            "deletion_tombstone_gap"
        )
        == expected_deletion_tombstone_gap
    )

    archive_counts_valid = all(
        (
            isinstance(
                archive_metrics.get(
                    "valid_archive_records"
                ),
                int,
            ),
            isinstance(
                archive_metrics.get(
                    "unique_archive_count"
                ),
                int,
            ),
            isinstance(
                archive_metrics.get(
                    "unique_body_count"
                ),
                int,
            ),
            archive_metrics.get(
                "valid_archive_records",
                0,
            )
            >= archive_metrics.get(
                "unique_archive_count",
                0,
            ),
            archive_metrics.get(
                "valid_archive_records",
                0,
            )
            >= archive_metrics.get(
                "unique_body_count",
                0,
            ),
        )
    )

    retention_total_matches = (
        retention_metrics.get(
            "records_considered"
        )
        == (
            int(
                retention_metrics.get(
                    "retention_expired_count",
                    0,
                )
            )
            + int(
                retention_metrics.get(
                    "retention_active_count",
                    0,
                )
            )
            + int(
                retention_metrics.get(
                    "retention_unknown_count",
                    0,
                )
            )
        )
    )

    source_read_counts_valid = all(
        (
            state_counts.get(
                "lifecycle_records_read",
                0,
            )
            >= state_counts.get(
                "valid_records",
                0,
            ),
            archive_metrics.get(
                "archive_records_read",
                0,
            )
            >= archive_metrics.get(
                "valid_archive_records",
                0,
            ),
            tombstone_metrics.get(
                "tombstone_records_read",
                0,
            )
            >= tombstone_metrics.get(
                "valid_tombstones",
                0,
            ),
        )
    )

    source_mutation_counts_zero = all(
        (
            state_counts.get(
                "lifecycle_records_modified"
            )
            == 0,
            archive_metrics.get(
                "archive_records_modified"
            )
            == 0,
            restore_metrics.get(
                "restore_records_modified"
            )
            == 0,
            deletion_metrics.get(
                "deletion_records_modified"
            )
            == 0,
            tombstone_metrics.get(
                "tombstone_records_modified"
            )
            == 0,
            retention_metrics.get(
                "retention_records_modified"
            )
            == 0,
        )
    )

    result = {
        "state_counts_non_negative":
            state_counts_non_negative,

        "lifecycle_total_matches":
            lifecycle_total_matches,

        "restore_count_matches":
            restore_count_matches,

        "deletion_count_matches":
            deletion_count_matches,

        "tombstone_count_matches":
            tombstone_count_matches,

        "deletion_tombstone_gap_valid":
            deletion_tombstone_gap_valid,

        "archive_counts_valid":
            archive_counts_valid,

        "retention_total_matches":
            retention_total_matches,

        "source_read_counts_valid":
            source_read_counts_valid,

        "source_mutation_counts_zero":
            source_mutation_counts_zero,

        "metric_accuracy_verified":
            all(
                (
                    state_counts_non_negative,
                    lifecycle_total_matches,
                    restore_count_matches,
                    deletion_count_matches,
                    tombstone_count_matches,
                    deletion_tombstone_gap_valid,
                    archive_counts_valid,
                    retention_total_matches,
                    source_read_counts_valid,
                    source_mutation_counts_zero,
                )
            ),
    }

    return _freeze(
        result
    )


def verify_lifecycle_analytics_reproducibility_v1(
    *,
    project_root: Path,
    analytics_request: Mapping[str, Any],
    analytics_report: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        analytics_request,
        field_name="analytics_request",
    )

    original_report = _require_mapping(
        analytics_report,
        field_name="analytics_report",
    )

    reproduced_report = (
        build_lifecycle_analytics_report_v1(
            project_root=project_root,
            analytics_request=request,
        )
    )

    excluded_fields = {
        "generated_at",
        "report_checksum",
    }

    original_comparable = {
        key:
            value

        for key, value
        in original_report.items()

        if key not in excluded_fields
    }

    reproduced_comparable = {
        key:
            value

        for key, value
        in reproduced_report.items()

        if key not in excluded_fields
    }

    content_matches = (
        _json_ready(
            original_comparable
        )
        == _json_ready(
            reproduced_comparable
        )
    )

    original_checksum_source = {
        key:
            value

        for key, value
        in original_report.items()

        if key != "report_checksum"
    }

    original_checksum_valid = (
        calculate_lifecycle_analytics_report_checksum_v1(
            payload=original_checksum_source,
        )
        == original_report.get(
            "report_checksum"
        )
    )

    reproduced_checksum_source = {
        key:
            value

        for key, value
        in reproduced_report.items()

        if key != "report_checksum"
    }

    reproduced_checksum_valid = (
        calculate_lifecycle_analytics_report_checksum_v1(
            payload=reproduced_checksum_source,
        )
        == reproduced_report.get(
            "report_checksum"
        )
    )

    result = {
        "content_matches":
            content_matches,

        "original_checksum_valid":
            original_checksum_valid,

        "reproduced_checksum_valid":
            reproduced_checksum_valid,

        "reproducibility_verified":
            all(
                (
                    content_matches,
                    original_checksum_valid,
                    reproduced_checksum_valid,
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
    }

    return _freeze(
        result
    )
def verify_lifecycle_analytics_safety_boundaries_v1(
    *,
    analytics_report: Mapping[str, Any],
) -> Mapping[str, Any]:

    report = _require_mapping(
        analytics_report,
        field_name="analytics_report",
    )

    report_read_only = (
        report.get(
            "read_only"
        )
        is True
    )

    lifecycle_not_modified = (
        report.get(
            "lifecycle_modified"
        )
        is False
    )

    archive_not_modified = (
        report.get(
            "archive_modified"
        )
        is False
    )

    tombstone_not_modified = (
        report.get(
            "tombstone_modified"
        )
        is False
    )

    body_store_not_modified = (
        report.get(
            "body_store_modified"
        )
        is False
    )

    no_runtime_job_created = (
        report.get(
            "runtime_job_created"
        )
        is False
    )

    no_queue_job_created = (
        report.get(
            "queue_job_created"
        )
        is False
    )

    result = {
        "report_read_only":
            report_read_only,

        "lifecycle_not_modified":
            lifecycle_not_modified,

        "archive_not_modified":
            archive_not_modified,

        "tombstone_not_modified":
            tombstone_not_modified,

        "body_store_not_modified":
            body_store_not_modified,

        "no_runtime_job_created":
            no_runtime_job_created,

        "no_queue_job_created":
            no_queue_job_created,

        "safety_boundaries_verified":
            all(
                (
                    report_read_only,
                    lifecycle_not_modified,
                    archive_not_modified,
                    tombstone_not_modified,
                    body_store_not_modified,
                    no_runtime_job_created,
                    no_queue_job_created,
                )
            ),
    }

    return _freeze(
        result
    )


def verify_lifecycle_analytics_v1(
    *,
    project_root: Path,
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

    request_identity = (
        verify_lifecycle_analytics_request_identity_v1(
            analytics_request=request,
            analytics_report=report,
        )
    )

    report_structure = (
        verify_lifecycle_analytics_report_structure_v1(
            analytics_report=report,
        )
    )

    metric_accuracy = (
        verify_lifecycle_analytics_metric_accuracy_v1(
            analytics_report=report,
        )
    )

    reproducibility = (
        verify_lifecycle_analytics_reproducibility_v1(
            project_root=project_root,
            analytics_request=request,
            analytics_report=report,
        )
    )

    safety_boundaries = (
        verify_lifecycle_analytics_safety_boundaries_v1(
            analytics_report=report,
        )
    )

    report_summary = (
        summarize_lifecycle_analytics_report_v1(
            analytics_report=report,
        )
    )

    verification_material = {
        "analytics_request_id":
            report[
                "analytics_request_id"
            ],

        "scope":
            report[
                "scope"
            ],

        "workspace_id":
            report[
                "workspace_id"
            ],

        "period_start":
            report[
                "period_start"
            ],

        "period_end":
            report[
                "period_end"
            ],

        "report_checksum":
            report[
                "report_checksum"
            ],

        "request_identity_verified":
            request_identity[
                "request_identity_verified"
            ],

        "report_structure_verified":
            report_structure[
                "report_structure_verified"
            ],

        "metric_accuracy_verified":
            metric_accuracy[
                "metric_accuracy_verified"
            ],

        "reproducibility_verified":
            reproducibility[
                "reproducibility_verified"
            ],

        "safety_boundaries_verified":
            safety_boundaries[
                "safety_boundaries_verified"
            ],
    }

    verification_id = (
        "body_store_lifecycle_analytics_verification_"
        + calculate_lifecycle_analytics_verification_checksum_v1(
            payload=verification_material,
        )
    )

    verification = {
        "schema":
            BODY_STORE_LIFECYCLE_ANALYTICS_VERIFIER_SCHEMA,

        "verifier_version":
            BODY_STORE_LIFECYCLE_ANALYTICS_VERIFIER_VERSION,

        "verification_id":
            verification_id,

        "analytics_request_id":
            report[
                "analytics_request_id"
            ],

        "scope":
            report[
                "scope"
            ],

        "workspace_id":
            report[
                "workspace_id"
            ],

        "period_start":
            report[
                "period_start"
            ],

        "period_end":
            report[
                "period_end"
            ],

        "report_checksum":
            report[
                "report_checksum"
            ],

        "request_identity":
            request_identity,

        "report_structure":
            report_structure,

        "metric_accuracy":
            metric_accuracy,

        "reproducibility":
            reproducibility,

        "safety_boundaries":
            safety_boundaries,

        "report_summary":
            report_summary,

        "analytics_verified":
            all(
                (
                    request_identity[
                        "request_identity_verified"
                    ]
                    is True,
                    report_structure[
                        "report_structure_verified"
                    ]
                    is True,
                    metric_accuracy[
                        "metric_accuracy_verified"
                    ]
                    is True,
                    reproducibility[
                        "reproducibility_verified"
                    ]
                    is True,
                    safety_boundaries[
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

    return _freeze(
        verification
    )
