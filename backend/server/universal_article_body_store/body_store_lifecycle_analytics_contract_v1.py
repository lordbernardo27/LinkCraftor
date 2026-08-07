from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping


BODY_STORE_LIFECYCLE_ANALYTICS_CONTRACT_VERSION = "1.0"

BODY_STORE_LIFECYCLE_ANALYTICS_CONTRACT_SCHEMA = (
    "body_store_lifecycle_analytics_contract.v1"
)

BODY_STORE_LIFECYCLE_ANALYTICS_REPORT_SCHEMA = (
    "body_store_lifecycle_analytics_report.v1"
)

BODY_STORE_LIFECYCLE_ANALYTICS_SUPPORTED_STATES = (
    "ACTIVE",
    "ARCHIVED",
    "RESTORED",
    "PERMANENTLY_DELETED",
)

BODY_STORE_LIFECYCLE_ANALYTICS_SUPPORTED_SCOPES = (
    "WORKSPACE",
    "GLOBAL",
)


class LifecycleAnalyticsContractError(
    ValueError
):
    """Raised when a lifecycle analytics contract is invalid."""


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


def _require_string(
    value: Any,
    *,
    field_name: str,
) -> str:

    if not isinstance(
        value,
        str,
    ):
        raise LifecycleAnalyticsContractError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise LifecycleAnalyticsContractError(
            field_name
            + " must not be empty."
        )

    return normalized


def _require_optional_string(
    value: Any,
    *,
    field_name: str,
) -> str | None:

    if value is None:
        return None

    return _require_string(
        value,
        field_name=field_name,
    )


def _require_boolean(
    value: Any,
    *,
    field_name: str,
) -> bool:

    if not isinstance(
        value,
        bool,
    ):
        raise LifecycleAnalyticsContractError(
            field_name
            + " must be a boolean."
        )

    return value


def _utc_now() -> str:

    return (
        datetime.now(
            timezone.utc
        ).isoformat()
    )


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


def calculate_lifecycle_analytics_contract_checksum_v1(
    *,
    payload: Mapping[str, Any],
) -> str:

    if not isinstance(
        payload,
        Mapping,
    ):
        raise LifecycleAnalyticsContractError(
            "payload must be a mapping."
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
def create_lifecycle_analytics_request_v1(
    *,
    analytics_request_id: str,
    scope: str,
    workspace_id: str | None,
    include_state_counts: bool,
    include_archive_metrics: bool,
    include_restore_metrics: bool,
    include_deletion_metrics: bool,
    include_tombstone_metrics: bool,
    include_retention_metrics: bool,
    period_start: str | None = None,
    period_end: str | None = None,
    requested_at: str | None = None,
) -> Mapping[str, Any]:

    normalized_request_id = _require_string(
        analytics_request_id,
        field_name="analytics_request_id",
    )

    normalized_scope = _require_string(
        scope,
        field_name="scope",
    ).upper()

    if (
        normalized_scope
        not in BODY_STORE_LIFECYCLE_ANALYTICS_SUPPORTED_SCOPES
    ):
        raise LifecycleAnalyticsContractError(
            "scope must be WORKSPACE or GLOBAL."
        )

    normalized_workspace_id = _require_optional_string(
        workspace_id,
        field_name="workspace_id",
    )

    if (
        normalized_scope == "WORKSPACE"
        and normalized_workspace_id is None
    ):
        raise LifecycleAnalyticsContractError(
            "workspace_id is required for WORKSPACE scope."
        )

    if (
        normalized_scope == "GLOBAL"
        and normalized_workspace_id is not None
    ):
        raise LifecycleAnalyticsContractError(
            "workspace_id must be omitted for GLOBAL scope."
        )

    normalized_period_start = _require_optional_string(
        period_start,
        field_name="period_start",
    )

    normalized_period_end = _require_optional_string(
        period_end,
        field_name="period_end",
    )

    normalized_requested_at = (
        _require_string(
            requested_at,
            field_name="requested_at",
        )
        if requested_at is not None
        else _utc_now()
    )

    request = {
        "schema":
            BODY_STORE_LIFECYCLE_ANALYTICS_CONTRACT_SCHEMA,

        "contract_version":
            BODY_STORE_LIFECYCLE_ANALYTICS_CONTRACT_VERSION,

        "analytics_request_id":
            normalized_request_id,

        "scope":
            normalized_scope,

        "workspace_id":
            normalized_workspace_id,

        "period_start":
            normalized_period_start,

        "period_end":
            normalized_period_end,

        "requested_at":
            normalized_requested_at,

        "metrics": {
            "include_state_counts":
                _require_boolean(
                    include_state_counts,
                    field_name="include_state_counts",
                ),

            "include_archive_metrics":
                _require_boolean(
                    include_archive_metrics,
                    field_name="include_archive_metrics",
                ),

            "include_restore_metrics":
                _require_boolean(
                    include_restore_metrics,
                    field_name="include_restore_metrics",
                ),

            "include_deletion_metrics":
                _require_boolean(
                    include_deletion_metrics,
                    field_name="include_deletion_metrics",
                ),

            "include_tombstone_metrics":
                _require_boolean(
                    include_tombstone_metrics,
                    field_name="include_tombstone_metrics",
                ),

            "include_retention_metrics":
                _require_boolean(
                    include_retention_metrics,
                    field_name="include_retention_metrics",
                ),
        },

        "supported_states":
            BODY_STORE_LIFECYCLE_ANALYTICS_SUPPORTED_STATES,

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

    checksum = (
        calculate_lifecycle_analytics_contract_checksum_v1(
            payload=request,
        )
    )

    request["checksum"] = checksum

    return _freeze(
        request
    )
def validate_lifecycle_analytics_request_v1(
    *,
    analytics_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    if not isinstance(
        analytics_request,
        Mapping,
    ):
        raise LifecycleAnalyticsContractError(
            "analytics_request must be a mapping."
        )

    required_fields = (
        "schema",
        "contract_version",
        "analytics_request_id",
        "scope",
        "workspace_id",
        "period_start",
        "period_end",
        "requested_at",
        "metrics",
        "supported_states",
        "read_only",
        "lifecycle_modified",
        "archive_modified",
        "tombstone_modified",
        "body_store_modified",
        "runtime_job_created",
        "queue_job_created",
        "checksum",
    )

    missing_fields = tuple(
        field_name
        for field_name in required_fields
        if field_name not in analytics_request
    )

    schema_valid = (
        analytics_request.get(
            "schema"
        )
        == BODY_STORE_LIFECYCLE_ANALYTICS_CONTRACT_SCHEMA
    )

    contract_version_valid = (
        analytics_request.get(
            "contract_version"
        )
        == BODY_STORE_LIFECYCLE_ANALYTICS_CONTRACT_VERSION
    )

    scope = analytics_request.get(
        "scope"
    )

    scope_valid = (
        scope
        in BODY_STORE_LIFECYCLE_ANALYTICS_SUPPORTED_SCOPES
    )

    workspace_id = analytics_request.get(
        "workspace_id"
    )

    workspace_scope_valid = (
        (
            scope == "WORKSPACE"
            and isinstance(
                workspace_id,
                str,
            )
            and bool(
                workspace_id.strip()
            )
        )
        or (
            scope == "GLOBAL"
            and workspace_id is None
        )
    )

    metrics = analytics_request.get(
        "metrics"
    )

    required_metrics = (
        "include_state_counts",
        "include_archive_metrics",
        "include_restore_metrics",
        "include_deletion_metrics",
        "include_tombstone_metrics",
        "include_retention_metrics",
    )

    metrics_mapping_valid = isinstance(
        metrics,
        Mapping,
    )

    missing_metrics = tuple(
        metric_name
        for metric_name in required_metrics
        if (
            not metrics_mapping_valid
            or metric_name not in metrics
        )
    )

    metric_flags_valid = (
        metrics_mapping_valid
        and not missing_metrics
        and all(
            isinstance(
                metrics[
                    metric_name
                ],
                bool,
            )
            for metric_name in required_metrics
        )
    )

    at_least_one_metric_selected = (
        metric_flags_valid
        and any(
            metrics[
                metric_name
            ]
            is True
            for metric_name in required_metrics
        )
    )

    supported_states_valid = (
        tuple(
            analytics_request.get(
                "supported_states",
                (),
            )
        )
        == BODY_STORE_LIFECYCLE_ANALYTICS_SUPPORTED_STATES
    )

    period_start = analytics_request.get(
        "period_start"
    )

    period_end = analytics_request.get(
        "period_end"
    )

    period_values_valid = all(
        (
            (
                period_start is None
                or (
                    isinstance(
                        period_start,
                        str,
                    )
                    and bool(
                        period_start.strip()
                    )
                )
            ),
            (
                period_end is None
                or (
                    isinstance(
                        period_end,
                        str,
                    )
                    and bool(
                        period_end.strip()
                    )
                )
            ),
        )
    )

    period_pair_valid = (
        (
            period_start is None
            and period_end is None
        )
        or (
            period_start is not None
            and period_end is not None
        )
    )

    safety_boundaries_valid = all(
        (
            analytics_request.get(
                "read_only"
            )
            is True,
            analytics_request.get(
                "lifecycle_modified"
            )
            is False,
            analytics_request.get(
                "archive_modified"
            )
            is False,
            analytics_request.get(
                "tombstone_modified"
            )
            is False,
            analytics_request.get(
                "body_store_modified"
            )
            is False,
            analytics_request.get(
                "runtime_job_created"
            )
            is False,
            analytics_request.get(
                "queue_job_created"
            )
            is False,
        )
    )

    checksum_source = {
        key:
            value

        for key, value
        in analytics_request.items()

        if key != "checksum"
    }

    calculated_checksum = (
        calculate_lifecycle_analytics_contract_checksum_v1(
            payload=checksum_source,
        )
    )

    checksum_valid = (
        calculated_checksum
        == analytics_request.get(
            "checksum"
        )
    )

    request_valid = all(
        (
            not missing_fields,
            schema_valid,
            contract_version_valid,
            scope_valid,
            workspace_scope_valid,
            metric_flags_valid,
            at_least_one_metric_selected,
            supported_states_valid,
            period_values_valid,
            period_pair_valid,
            safety_boundaries_valid,
            checksum_valid,
        )
    )

    validation = {
        "request_valid":
            request_valid,

        "missing_fields":
            missing_fields,

        "schema_valid":
            schema_valid,

        "contract_version_valid":
            contract_version_valid,

        "scope_valid":
            scope_valid,

        "workspace_scope_valid":
            workspace_scope_valid,

        "metrics_mapping_valid":
            metrics_mapping_valid,

        "missing_metrics":
            missing_metrics,

        "metric_flags_valid":
            metric_flags_valid,

        "at_least_one_metric_selected":
            at_least_one_metric_selected,

        "supported_states_valid":
            supported_states_valid,

        "period_values_valid":
            period_values_valid,

        "period_pair_valid":
            period_pair_valid,

        "safety_boundaries_valid":
            safety_boundaries_valid,

        "checksum_valid":
            checksum_valid,

        "calculated_checksum":
            calculated_checksum,

        "stored_checksum":
            analytics_request.get(
                "checksum"
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
        validation
    )
def certify_lifecycle_analytics_request_v1(
    *,
    analytics_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    if not isinstance(
        analytics_request,
        Mapping,
    ):
        raise LifecycleAnalyticsContractError(
            "analytics_request must be a mapping."
        )

    validation = (
        validate_lifecycle_analytics_request_v1(
            analytics_request=analytics_request,
        )
    )

    certification = {
        "schema":
            "body_store_lifecycle_analytics_contract_certification.v1",

        "contract_version":
            BODY_STORE_LIFECYCLE_ANALYTICS_CONTRACT_VERSION,

        "analytics_request_id":
            analytics_request[
                "analytics_request_id"
            ],

        "scope":
            analytics_request[
                "scope"
            ],

        "workspace_id":
            analytics_request[
                "workspace_id"
            ],

        "certified":
            validation[
                "request_valid"
            ]
            is True,

        "request_valid":
            validation[
                "request_valid"
            ],

        "validation":
            validation,

        "request_checksum":
            analytics_request[
                "checksum"
            ],

        "read_only":
            True,

        "analytics_executed":
            False,

        "report_generated":
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


def summarize_lifecycle_analytics_request_v1(
    *,
    analytics_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    if not isinstance(
        analytics_request,
        Mapping,
    ):
        raise LifecycleAnalyticsContractError(
            "analytics_request must be a mapping."
        )

    metrics = analytics_request[
        "metrics"
    ]

    selected_metrics = tuple(
        metric_name
        for metric_name, selected
        in metrics.items()
        if selected is True
    )

    summary = {
        "analytics_request_id":
            analytics_request[
                "analytics_request_id"
            ],

        "scope":
            analytics_request[
                "scope"
            ],

        "workspace_id":
            analytics_request[
                "workspace_id"
            ],

        "period_start":
            analytics_request[
                "period_start"
            ],

        "period_end":
            analytics_request[
                "period_end"
            ],

        "selected_metrics":
            selected_metrics,

        "selected_metric_count":
            len(
                selected_metrics
            ),

        "supported_states":
            analytics_request[
                "supported_states"
            ],

        "read_only":
            analytics_request[
                "read_only"
            ],

        "analytics_executed":
            False,

        "report_generated":
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


__all__ = [
    "BODY_STORE_LIFECYCLE_ANALYTICS_CONTRACT_VERSION",
    "BODY_STORE_LIFECYCLE_ANALYTICS_CONTRACT_SCHEMA",
    "BODY_STORE_LIFECYCLE_ANALYTICS_REPORT_SCHEMA",
    "BODY_STORE_LIFECYCLE_ANALYTICS_SUPPORTED_STATES",
    "BODY_STORE_LIFECYCLE_ANALYTICS_SUPPORTED_SCOPES",
    "LifecycleAnalyticsContractError",
    "calculate_lifecycle_analytics_contract_checksum_v1",
    "create_lifecycle_analytics_request_v1",
    "validate_lifecycle_analytics_request_v1",
    "certify_lifecycle_analytics_request_v1",
    "summarize_lifecycle_analytics_request_v1",
]
