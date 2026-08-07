from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from backend.server.universal_article_body_store.body_store_lifecycle_analytics_contract_v1 import (
    BODY_STORE_LIFECYCLE_ANALYTICS_REPORT_SCHEMA,
    BODY_STORE_LIFECYCLE_ANALYTICS_SUPPORTED_STATES,
    certify_lifecycle_analytics_request_v1,
    validate_lifecycle_analytics_request_v1,
)


BODY_STORE_LIFECYCLE_ANALYTICS_ENGINE_VERSION = "1.0"

BODY_STORE_LIFECYCLE_ANALYTICS_ENGINE_SCHEMA = (
    "body_store_lifecycle_analytics_engine.v1"
)


class LifecycleAnalyticsEngineError(
    ValueError
):
    """Raised when lifecycle analytics execution cannot proceed safely."""


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
        raise LifecycleAnalyticsEngineError(
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
        raise LifecycleAnalyticsEngineError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise LifecycleAnalyticsEngineError(
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


def _utc_now() -> str:

    return (
        datetime.now(
            timezone.utc
        ).isoformat()
    )


def _parse_datetime(
    value: Any,
) -> datetime | None:

    if value is None:
        return None

    if not isinstance(
        value,
        str,
    ):
        return None

    normalized = value.strip()

    if not normalized:
        return None

    try:
        parsed = datetime.fromisoformat(
            normalized.replace(
                "Z",
                "+00:00",
            )
        )

    except ValueError:
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=timezone.utc,
        )

    return parsed.astimezone(
        timezone.utc
    )


def calculate_lifecycle_analytics_report_checksum_v1(
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
def resolve_lifecycle_store_root_v1(
    *,
    project_root: Path,
) -> Path:

    if not isinstance(
        project_root,
        Path,
    ):
        raise LifecycleAnalyticsEngineError(
            "project_root must be a Path."
        )

    return (
        project_root.resolve()
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store_lifecycle"
    ).resolve()


def resolve_archive_store_root_v1(
    *,
    project_root: Path,
) -> Path:

    if not isinstance(
        project_root,
        Path,
    ):
        raise LifecycleAnalyticsEngineError(
            "project_root must be a Path."
        )

    return (
        project_root.resolve()
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store_archive"
    ).resolve()


def resolve_tombstone_store_root_v1(
    *,
    project_root: Path,
) -> Path:

    if not isinstance(
        project_root,
        Path,
    ):
        raise LifecycleAnalyticsEngineError(
            "project_root must be a Path."
        )

    return (
        project_root.resolve()
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store_tombstones"
    ).resolve()


def _iter_json_files(
    *,
    root: Path,
) -> Iterable[Path]:

    if not root.exists():
        return ()

    return tuple(
        path
        for path in sorted(
            root.rglob("*.json"),
            key=lambda candidate: (
                candidate.as_posix()
            ),
        )
        if path.is_file()
    )


def _load_json_object(
    *,
    path: Path,
) -> dict[str, Any] | None:

    try:
        payload = json.loads(
            path.read_text(
                encoding="utf-8-sig",
            )
        )

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return None

    if not isinstance(
        payload,
        dict,
    ):
        return None

    return payload


def _extract_workspace_id(
    *,
    payload: Mapping[str, Any],
    path: Path,
    store_root: Path,
) -> str | None:

    workspace_id = payload.get(
        "workspace_id"
    )

    if (
        isinstance(
            workspace_id,
            str,
        )
        and workspace_id.strip()
    ):
        return workspace_id.strip()

    try:
        relative = path.relative_to(
            store_root
        )

    except ValueError:
        return None

    if not relative.parts:
        return None

    candidate = relative.parts[
        0
    ]

    if not candidate:
        return None

    return candidate


def _record_in_scope(
    *,
    request: Mapping[str, Any],
    workspace_id: str | None,
) -> bool:

    scope = request[
        "scope"
    ]

    if scope == "GLOBAL":
        return True

    return (
        workspace_id
        == request[
            "workspace_id"
        ]
    )


def _record_in_period(
    *,
    request: Mapping[str, Any],
    payload: Mapping[str, Any],
) -> bool:

    period_start = _parse_datetime(
        request.get(
            "period_start"
        )
    )

    period_end = _parse_datetime(
        request.get(
            "period_end"
        )
    )

    if (
        period_start is None
        and period_end is None
    ):
        return True

    timestamp_candidates = (
        payload.get(
            "updated_at"
        ),
        payload.get(
            "created_at"
        ),
        payload.get(
            "archived_at"
        ),
        payload.get(
            "restored_at"
        ),
        payload.get(
            "deleted_at"
        ),
        payload.get(
            "requested_at"
        ),
    )

    record_time = next(
        (
            parsed
            for parsed in (
                _parse_datetime(
                    candidate
                )
                for candidate in timestamp_candidates
            )
            if parsed is not None
        ),
        None,
    )

    if record_time is None:
        return False

    if (
        period_start is not None
        and record_time < period_start
    ):
        return False

    if (
        period_end is not None
        and record_time > period_end
    ):
        return False

    return True
def _normalize_lifecycle_state(
    *,
    payload: Mapping[str, Any],
) -> str | None:

    candidates = (
        payload.get(
            "lifecycle_state"
        ),
        payload.get(
            "state"
        ),
        payload.get(
            "current_state"
        ),
        payload.get(
            "target_state"
        ),
    )

    for candidate in candidates:
        if not isinstance(
            candidate,
            str,
        ):
            continue

        normalized = (
            candidate
            .strip()
            .upper()
        )

        if (
            normalized
            in BODY_STORE_LIFECYCLE_ANALYTICS_SUPPORTED_STATES
        ):
            return normalized

    return None


def collect_lifecycle_records_v1(
    *,
    project_root: Path,
    analytics_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        analytics_request,
        field_name="analytics_request",
    )

    lifecycle_root = (
        resolve_lifecycle_store_root_v1(
            project_root=project_root,
        )
    )

    counts_by_state = {
        state:
            0

        for state
        in BODY_STORE_LIFECYCLE_ANALYTICS_SUPPORTED_STATES
    }

    total_json_files = 0
    valid_records = 0
    invalid_records = 0
    out_of_scope_records = 0
    out_of_period_records = 0
    records_without_supported_state = 0

    workspace_ids: set[str] = set()
    body_ids: set[str] = set()

    for path in _iter_json_files(
        root=lifecycle_root,
    ):
        total_json_files += 1

        payload = _load_json_object(
            path=path,
        )

        if payload is None:
            invalid_records += 1
            continue

        workspace_id = (
            _extract_workspace_id(
                payload=payload,
                path=path,
                store_root=lifecycle_root,
            )
        )

        if not _record_in_scope(
            request=request,
            workspace_id=workspace_id,
        ):
            out_of_scope_records += 1
            continue

        if not _record_in_period(
            request=request,
            payload=payload,
        ):
            out_of_period_records += 1
            continue

        lifecycle_state = (
            _normalize_lifecycle_state(
                payload=payload,
            )
        )

        if lifecycle_state is None:
            records_without_supported_state += 1
            continue

        valid_records += 1
        counts_by_state[
            lifecycle_state
        ] += 1

        if workspace_id:
            workspace_ids.add(
                workspace_id
            )

        body_id = payload.get(
            "body_id"
        )

        if (
            isinstance(
                body_id,
                str,
            )
            and body_id.strip()
        ):
            body_ids.add(
                body_id.strip()
            )

    result = {
        "store_root":
            lifecycle_root.as_posix(),

        "store_present":
            lifecycle_root.exists(),

        "total_json_files":
            total_json_files,

        "valid_records":
            valid_records,

        "invalid_records":
            invalid_records,

        "out_of_scope_records":
            out_of_scope_records,

        "out_of_period_records":
            out_of_period_records,

        "records_without_supported_state":
            records_without_supported_state,

        "counts_by_state":
            counts_by_state,

        "workspace_count":
            len(
                workspace_ids
            ),

        "body_count":
            len(
                body_ids
            ),

        "workspace_ids":
            tuple(
                sorted(
                    workspace_ids
                )
            ),

        "lifecycle_records_read":
            total_json_files,

        "lifecycle_records_modified":
            0,
    }

    return _freeze(
        result
    )


def collect_archive_metrics_v1(
    *,
    project_root: Path,
    analytics_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        analytics_request,
        field_name="analytics_request",
    )

    archive_root = (
        resolve_archive_store_root_v1(
            project_root=project_root,
        )
    )

    total_json_files = 0
    valid_archive_records = 0
    invalid_archive_records = 0
    out_of_scope_records = 0
    out_of_period_records = 0

    workspace_ids: set[str] = set()
    body_ids: set[str] = set()
    archive_ids: set[str] = set()

    for path in _iter_json_files(
        root=archive_root,
    ):
        total_json_files += 1

        payload = _load_json_object(
            path=path,
        )

        if payload is None:
            invalid_archive_records += 1
            continue

        workspace_id = (
            _extract_workspace_id(
                payload=payload,
                path=path,
                store_root=archive_root,
            )
        )

        if not _record_in_scope(
            request=request,
            workspace_id=workspace_id,
        ):
            out_of_scope_records += 1
            continue

        if not _record_in_period(
            request=request,
            payload=payload,
        ):
            out_of_period_records += 1
            continue

        valid_archive_records += 1

        if workspace_id:
            workspace_ids.add(
                workspace_id
            )

        body_id = payload.get(
            "body_id"
        )

        if (
            isinstance(
                body_id,
                str,
            )
            and body_id.strip()
        ):
            body_ids.add(
                body_id.strip()
            )

        archive_id = payload.get(
            "archive_id"
        )

        if (
            isinstance(
                archive_id,
                str,
            )
            and archive_id.strip()
        ):
            archive_ids.add(
                archive_id.strip()
            )

    result = {
        "store_root":
            archive_root.as_posix(),

        "store_present":
            archive_root.exists(),

        "total_json_files":
            total_json_files,

        "valid_archive_records":
            valid_archive_records,

        "invalid_archive_records":
            invalid_archive_records,

        "out_of_scope_records":
            out_of_scope_records,

        "out_of_period_records":
            out_of_period_records,

        "unique_archive_count":
            len(
                archive_ids
            ),

        "unique_body_count":
            len(
                body_ids
            ),

        "workspace_count":
            len(
                workspace_ids
            ),

        "archive_records_read":
            total_json_files,

        "archive_records_modified":
            0,
    }

    return _freeze(
        result
    )


def collect_tombstone_metrics_v1(
    *,
    project_root: Path,
    analytics_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        analytics_request,
        field_name="analytics_request",
    )

    tombstone_root = (
        resolve_tombstone_store_root_v1(
            project_root=project_root,
        )
    )

    total_json_files = 0
    valid_tombstones = 0
    invalid_records = 0
    index_files_skipped = 0
    out_of_scope_records = 0
    out_of_period_records = 0
    content_boundary_violations = 0

    workspace_ids: set[str] = set()
    body_ids: set[str] = set()
    tombstone_ids: set[str] = set()

    forbidden_fields = {
        "content",
        "article_body",
        "body_text",
        "content_body",
        "raw_html",
        "html",
    }

    for path in _iter_json_files(
        root=tombstone_root,
    ):
        total_json_files += 1

        if path.name == "index.json":
            index_files_skipped += 1
            continue

        payload = _load_json_object(
            path=path,
        )

        if payload is None:
            invalid_records += 1
            continue

        workspace_id = (
            _extract_workspace_id(
                payload=payload,
                path=path,
                store_root=tombstone_root,
            )
        )

        if not _record_in_scope(
            request=request,
            workspace_id=workspace_id,
        ):
            out_of_scope_records += 1
            continue

        if not _record_in_period(
            request=request,
            payload=payload,
        ):
            out_of_period_records += 1
            continue

        exposed_fields = (
            forbidden_fields
            .intersection(
                payload.keys()
            )
        )

        if (
            exposed_fields
            or payload.get(
                "contains_article_body"
            )
            is not False
        ):
            content_boundary_violations += 1
            continue

        valid_tombstones += 1

        if workspace_id:
            workspace_ids.add(
                workspace_id
            )

        body_id = payload.get(
            "body_id"
        )

        if (
            isinstance(
                body_id,
                str,
            )
            and body_id.strip()
        ):
            body_ids.add(
                body_id.strip()
            )

        tombstone_id = payload.get(
            "tombstone_id"
        )

        if (
            isinstance(
                tombstone_id,
                str,
            )
            and tombstone_id.strip()
        ):
            tombstone_ids.add(
                tombstone_id.strip()
            )

    result = {
        "store_root":
            tombstone_root.as_posix(),

        "store_present":
            tombstone_root.exists(),

        "total_json_files":
            total_json_files,

        "index_files_skipped":
            index_files_skipped,

        "valid_tombstones":
            valid_tombstones,

        "invalid_records":
            invalid_records,

        "out_of_scope_records":
            out_of_scope_records,

        "out_of_period_records":
            out_of_period_records,

        "content_boundary_violations":
            content_boundary_violations,

        "unique_tombstone_count":
            len(
                tombstone_ids
            ),

        "unique_body_count":
            len(
                body_ids
            ),

        "workspace_count":
            len(
                workspace_ids
            ),

        "tombstone_records_read":
            total_json_files,

        "tombstone_records_modified":
            0,
    }

    return _freeze(
        result
    )
def collect_restore_metrics_v1(
    *,
    lifecycle_metrics: Mapping[str, Any],
) -> Mapping[str, Any]:

    metrics = _require_mapping(
        lifecycle_metrics,
        field_name="lifecycle_metrics",
    )

    counts_by_state = _require_mapping(
        metrics[
            "counts_by_state"
        ],
        field_name="counts_by_state",
    )

    restored_count = int(
        counts_by_state.get(
            "RESTORED",
            0,
        )
    )

    result = {
        "restored_count":
            restored_count,

        "restore_events_inferred_from_lifecycle":
            restored_count,

        "restore_records_read":
            metrics[
                "lifecycle_records_read"
            ],

        "restore_records_modified":
            0,
    }

    return _freeze(
        result
    )


def collect_deletion_metrics_v1(
    *,
    lifecycle_metrics: Mapping[str, Any],
    tombstone_metrics: Mapping[str, Any],
) -> Mapping[str, Any]:

    lifecycle = _require_mapping(
        lifecycle_metrics,
        field_name="lifecycle_metrics",
    )

    tombstones = _require_mapping(
        tombstone_metrics,
        field_name="tombstone_metrics",
    )

    counts_by_state = _require_mapping(
        lifecycle[
            "counts_by_state"
        ],
        field_name="counts_by_state",
    )

    permanently_deleted_count = int(
        counts_by_state.get(
            "PERMANENTLY_DELETED",
            0,
        )
    )

    tombstone_count = int(
        tombstones.get(
            "valid_tombstones",
            0,
        )
    )

    result = {
        "permanently_deleted_count":
            permanently_deleted_count,

        "certified_tombstone_count":
            tombstone_count,

        "deletion_tombstone_gap":
            max(
                permanently_deleted_count
                - tombstone_count,
                0,
            ),

        "deletion_records_read":
            lifecycle[
                "lifecycle_records_read"
            ]
            + tombstones[
                "tombstone_records_read"
            ],

        "deletion_records_modified":
            0,
    }

    return _freeze(
        result
    )


def collect_retention_metrics_v1(
    *,
    project_root: Path,
    analytics_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        analytics_request,
        field_name="analytics_request",
    )

    archive_root = (
        resolve_archive_store_root_v1(
            project_root=project_root,
        )
    )

    retention_expired_count = 0
    retention_active_count = 0
    retention_unknown_count = 0
    records_considered = 0
    out_of_scope_records = 0
    out_of_period_records = 0

    for path in _iter_json_files(
        root=archive_root,
    ):
        payload = _load_json_object(
            path=path,
        )

        if payload is None:
            continue

        workspace_id = (
            _extract_workspace_id(
                payload=payload,
                path=path,
                store_root=archive_root,
            )
        )

        if not _record_in_scope(
            request=request,
            workspace_id=workspace_id,
        ):
            out_of_scope_records += 1
            continue

        if not _record_in_period(
            request=request,
            payload=payload,
        ):
            out_of_period_records += 1
            continue

        records_considered += 1

        retention_expired = payload.get(
            "retention_expired"
        )

        if retention_expired is True:
            retention_expired_count += 1

        elif retention_expired is False:
            retention_active_count += 1

        else:
            retention_unknown_count += 1

    result = {
        "records_considered":
            records_considered,

        "retention_expired_count":
            retention_expired_count,

        "retention_active_count":
            retention_active_count,

        "retention_unknown_count":
            retention_unknown_count,

        "out_of_scope_records":
            out_of_scope_records,

        "out_of_period_records":
            out_of_period_records,

        "retention_records_read":
            records_considered,

        "retention_records_modified":
            0,
    }

    return _freeze(
        result
    )


def build_lifecycle_analytics_report_v1(
    *,
    project_root: Path,
    analytics_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        analytics_request,
        field_name="analytics_request",
    )

    validation = (
        validate_lifecycle_analytics_request_v1(
            analytics_request=request,
        )
    )

    if validation[
        "request_valid"
    ] is not True:
        raise LifecycleAnalyticsEngineError(
            "Lifecycle analytics request validation failed."
        )

    certification = (
        certify_lifecycle_analytics_request_v1(
            analytics_request=request,
        )
    )

    if certification[
        "certified"
    ] is not True:
        raise LifecycleAnalyticsEngineError(
            "Lifecycle analytics request certification failed."
        )

    lifecycle_metrics = (
        collect_lifecycle_records_v1(
            project_root=project_root,
            analytics_request=request,
        )
    )

    archive_metrics = (
        collect_archive_metrics_v1(
            project_root=project_root,
            analytics_request=request,
        )
    )

    tombstone_metrics = (
        collect_tombstone_metrics_v1(
            project_root=project_root,
            analytics_request=request,
        )
    )

    restore_metrics = (
        collect_restore_metrics_v1(
            lifecycle_metrics=lifecycle_metrics,
        )
    )

    deletion_metrics = (
        collect_deletion_metrics_v1(
            lifecycle_metrics=lifecycle_metrics,
            tombstone_metrics=tombstone_metrics,
        )
    )

    retention_metrics = (
        collect_retention_metrics_v1(
            project_root=project_root,
            analytics_request=request,
        )
    )

    selected_metrics = request[
        "metrics"
    ]

    report_metrics: dict[str, Any] = {}

    if selected_metrics[
        "include_state_counts"
    ] is True:
        report_metrics[
            "state_counts"
        ] = lifecycle_metrics

    if selected_metrics[
        "include_archive_metrics"
    ] is True:
        report_metrics[
            "archive_metrics"
        ] = archive_metrics

    if selected_metrics[
        "include_restore_metrics"
    ] is True:
        report_metrics[
            "restore_metrics"
        ] = restore_metrics

    if selected_metrics[
        "include_deletion_metrics"
    ] is True:
        report_metrics[
            "deletion_metrics"
        ] = deletion_metrics

    if selected_metrics[
        "include_tombstone_metrics"
    ] is True:
        report_metrics[
            "tombstone_metrics"
        ] = tombstone_metrics

    if selected_metrics[
        "include_retention_metrics"
    ] is True:
        report_metrics[
            "retention_metrics"
        ] = retention_metrics

    report = {
        "schema":
            BODY_STORE_LIFECYCLE_ANALYTICS_REPORT_SCHEMA,

        "engine_schema":
            BODY_STORE_LIFECYCLE_ANALYTICS_ENGINE_SCHEMA,

        "engine_version":
            BODY_STORE_LIFECYCLE_ANALYTICS_ENGINE_VERSION,

        "analytics_request_id":
            request[
                "analytics_request_id"
            ],

        "scope":
            request[
                "scope"
            ],

        "workspace_id":
            request[
                "workspace_id"
            ],

        "period_start":
            request[
                "period_start"
            ],

        "period_end":
            request[
                "period_end"
            ],

        "generated_at":
            _utc_now(),

        "metrics":
            report_metrics,

        "metric_group_count":
            len(
                report_metrics
            ),

        "analytics_executed":
            True,

        "report_generated":
            True,

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

    report_checksum = (
        calculate_lifecycle_analytics_report_checksum_v1(
            payload=report,
        )
    )

    report[
        "report_checksum"
    ] = report_checksum

    return _freeze(
        report
    )
def summarize_lifecycle_analytics_report_v1(
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

    state_counts = metrics.get(
        "state_counts",
        {},
    )

    archive_metrics = metrics.get(
        "archive_metrics",
        {},
    )

    restore_metrics = metrics.get(
        "restore_metrics",
        {},
    )

    deletion_metrics = metrics.get(
        "deletion_metrics",
        {},
    )

    tombstone_metrics = metrics.get(
        "tombstone_metrics",
        {},
    )

    retention_metrics = metrics.get(
        "retention_metrics",
        {},
    )

    counts_by_state = (
        state_counts.get(
            "counts_by_state",
            {},
        )
        if isinstance(
            state_counts,
            Mapping,
        )
        else {}
    )

    summary = {
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

        "generated_at":
            report[
                "generated_at"
            ],

        "metric_group_count":
            report[
                "metric_group_count"
            ],

        "active_count":
            int(
                counts_by_state.get(
                    "ACTIVE",
                    0,
                )
            ),

        "archived_count":
            int(
                counts_by_state.get(
                    "ARCHIVED",
                    0,
                )
            ),

        "restored_count":
            int(
                counts_by_state.get(
                    "RESTORED",
                    0,
                )
            ),

        "permanently_deleted_count":
            int(
                counts_by_state.get(
                    "PERMANENTLY_DELETED",
                    0,
                )
            ),

        "unique_archive_count":
            int(
                archive_metrics.get(
                    "unique_archive_count",
                    0,
                )
            )
            if isinstance(
                archive_metrics,
                Mapping,
            )
            else 0,

        "restore_event_count":
            int(
                restore_metrics.get(
                    "restore_events_inferred_from_lifecycle",
                    0,
                )
            )
            if isinstance(
                restore_metrics,
                Mapping,
            )
            else 0,

        "certified_tombstone_count":
            int(
                deletion_metrics.get(
                    "certified_tombstone_count",
                    0,
                )
            )
            if isinstance(
                deletion_metrics,
                Mapping,
            )
            else 0,

        "deletion_tombstone_gap":
            int(
                deletion_metrics.get(
                    "deletion_tombstone_gap",
                    0,
                )
            )
            if isinstance(
                deletion_metrics,
                Mapping,
            )
            else 0,

        "valid_tombstone_count":
            int(
                tombstone_metrics.get(
                    "valid_tombstones",
                    0,
                )
            )
            if isinstance(
                tombstone_metrics,
                Mapping,
            )
            else 0,

        "retention_expired_count":
            int(
                retention_metrics.get(
                    "retention_expired_count",
                    0,
                )
            )
            if isinstance(
                retention_metrics,
                Mapping,
            )
            else 0,

        "retention_active_count":
            int(
                retention_metrics.get(
                    "retention_active_count",
                    0,
                )
            )
            if isinstance(
                retention_metrics,
                Mapping,
            )
            else 0,

        "retention_unknown_count":
            int(
                retention_metrics.get(
                    "retention_unknown_count",
                    0,
                )
            )
            if isinstance(
                retention_metrics,
                Mapping,
            )
            else 0,

        "analytics_executed":
            report[
                "analytics_executed"
            ],

        "report_generated":
            report[
                "report_generated"
            ],

        "read_only":
            report[
                "read_only"
            ],

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


def verify_lifecycle_analytics_report_v1(
    *,
    analytics_report: Mapping[str, Any],
) -> Mapping[str, Any]:

    report = _require_mapping(
        analytics_report,
        field_name="analytics_report",
    )

    required_fields = (
        "schema",
        "engine_schema",
        "engine_version",
        "analytics_request_id",
        "scope",
        "workspace_id",
        "period_start",
        "period_end",
        "generated_at",
        "metrics",
        "metric_group_count",
        "analytics_executed",
        "report_generated",
        "read_only",
        "lifecycle_modified",
        "archive_modified",
        "tombstone_modified",
        "body_store_modified",
        "runtime_job_created",
        "queue_job_created",
        "report_checksum",
    )

    missing_fields = tuple(
        field_name
        for field_name in required_fields
        if field_name not in report
    )

    schema_valid = (
        report.get(
            "schema"
        )
        == BODY_STORE_LIFECYCLE_ANALYTICS_REPORT_SCHEMA
    )

    engine_schema_valid = (
        report.get(
            "engine_schema"
        )
        == BODY_STORE_LIFECYCLE_ANALYTICS_ENGINE_SCHEMA
    )

    engine_version_valid = (
        report.get(
            "engine_version"
        )
        == BODY_STORE_LIFECYCLE_ANALYTICS_ENGINE_VERSION
    )

    metrics = report.get(
        "metrics"
    )

    metrics_valid = isinstance(
        metrics,
        Mapping,
    )

    metric_group_count_valid = (
        metrics_valid
        and report.get(
            "metric_group_count"
        )
        == len(
            metrics
        )
    )

    execution_valid = all(
        (
            report.get(
                "analytics_executed"
            )
            is True,
            report.get(
                "report_generated"
            )
            is True,
            report.get(
                "read_only"
            )
            is True,
        )
    )

    safety_boundaries_valid = all(
        (
            report.get(
                "lifecycle_modified"
            )
            is False,
            report.get(
                "archive_modified"
            )
            is False,
            report.get(
                "tombstone_modified"
            )
            is False,
            report.get(
                "body_store_modified"
            )
            is False,
            report.get(
                "runtime_job_created"
            )
            is False,
            report.get(
                "queue_job_created"
            )
            is False,
        )
    )

    checksum_source = {
        key:
            value

        for key, value
        in report.items()

        if key != "report_checksum"
    }

    calculated_checksum = (
        calculate_lifecycle_analytics_report_checksum_v1(
            payload=checksum_source,
        )
    )

    checksum_valid = (
        calculated_checksum
        == report.get(
            "report_checksum"
        )
    )

    report_valid = all(
        (
            not missing_fields,
            schema_valid,
            engine_schema_valid,
            engine_version_valid,
            metrics_valid,
            metric_group_count_valid,
            execution_valid,
            safety_boundaries_valid,
            checksum_valid,
        )
    )

    verification = {
        "report_valid":
            report_valid,

        "missing_fields":
            missing_fields,

        "schema_valid":
            schema_valid,

        "engine_schema_valid":
            engine_schema_valid,

        "engine_version_valid":
            engine_version_valid,

        "metrics_valid":
            metrics_valid,

        "metric_group_count_valid":
            metric_group_count_valid,

        "execution_valid":
            execution_valid,

        "safety_boundaries_valid":
            safety_boundaries_valid,

        "checksum_valid":
            checksum_valid,

        "calculated_checksum":
            calculated_checksum,

        "stored_checksum":
            report.get(
                "report_checksum"
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
def build_lifecycle_analytics_engine_bundle_v1(
    *,
    project_root: Path,
    analytics_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        analytics_request,
        field_name="analytics_request",
    )

    report = (
        build_lifecycle_analytics_report_v1(
            project_root=project_root,
            analytics_request=request,
        )
    )

    report_verification = (
        verify_lifecycle_analytics_report_v1(
            analytics_report=report,
        )
    )

    if report_verification[
        "report_valid"
    ] is not True:
        raise LifecycleAnalyticsEngineError(
            "Lifecycle analytics report verification failed."
        )

    report_summary = (
        summarize_lifecycle_analytics_report_v1(
            analytics_report=report,
        )
    )

    bundle = {
        "schema":
            BODY_STORE_LIFECYCLE_ANALYTICS_ENGINE_SCHEMA,

        "engine_version":
            BODY_STORE_LIFECYCLE_ANALYTICS_ENGINE_VERSION,

        "analytics_request":
            request,

        "analytics_report":
            report,

        "report_verification":
            report_verification,

        "report_summary":
            report_summary,

        "analytics_request_id":
            request[
                "analytics_request_id"
            ],

        "scope":
            request[
                "scope"
            ],

        "workspace_id":
            request[
                "workspace_id"
            ],

        "analytics_executed":
            report[
                "analytics_executed"
            ]
            is True,

        "report_generated":
            report[
                "report_generated"
            ]
            is True,

        "report_verified":
            report_verification[
                "report_valid"
            ]
            is True,

        "bundle_complete":
            all(
                (
                    report[
                        "analytics_executed"
                    ]
                    is True,
                    report[
                        "report_generated"
                    ]
                    is True,
                    report_verification[
                        "report_valid"
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
        bundle
    )


def verify_lifecycle_analytics_engine_bundle_v1(
    *,
    engine_bundle: Mapping[str, Any],
) -> Mapping[str, Any]:

    bundle = _require_mapping(
        engine_bundle,
        field_name="engine_bundle",
    )

    required_sections = (
        "analytics_request",
        "analytics_report",
        "report_verification",
        "report_summary",
    )

    missing_sections = tuple(
        section
        for section in required_sections
        if section not in bundle
    )

    request = bundle.get(
        "analytics_request",
        {},
    )

    report = bundle.get(
        "analytics_report",
        {},
    )

    report_verification = bundle.get(
        "report_verification",
        {},
    )

    report_summary = bundle.get(
        "report_summary",
        {},
    )

    request_id_matches = (
        isinstance(
            request,
            Mapping,
        )
        and isinstance(
            report,
            Mapping,
        )
        and isinstance(
            report_summary,
            Mapping,
        )
        and request.get(
            "analytics_request_id"
        )
        == report.get(
            "analytics_request_id"
        )
        == report_summary.get(
            "analytics_request_id"
        )
        == bundle.get(
            "analytics_request_id"
        )
    )

    scope_matches = (
        isinstance(
            request,
            Mapping,
        )
        and isinstance(
            report,
            Mapping,
        )
        and request.get(
            "scope"
        )
        == report.get(
            "scope"
        )
        == bundle.get(
            "scope"
        )
    )

    workspace_matches = (
        isinstance(
            request,
            Mapping,
        )
        and isinstance(
            report,
            Mapping,
        )
        and request.get(
            "workspace_id"
        )
        == report.get(
            "workspace_id"
        )
        == bundle.get(
            "workspace_id"
        )
    )

    execution_confirmed = (
        bundle.get(
            "analytics_executed"
        )
        is True
        and bundle.get(
            "report_generated"
        )
        is True
    )

    verification_confirmed = (
        isinstance(
            report_verification,
            Mapping,
        )
        and report_verification.get(
            "report_valid"
        )
        is True
        and bundle.get(
            "report_verified"
        )
        is True
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

    verification = {
        "bundle_valid":
            all(
                (
                    not missing_sections,
                    bundle.get(
                        "bundle_complete"
                    )
                    is True,
                    request_id_matches,
                    scope_matches,
                    workspace_matches,
                    execution_confirmed,
                    verification_confirmed,
                    safety_boundaries_valid,
                )
            ),

        "missing_sections":
            missing_sections,

        "request_id_matches":
            request_id_matches,

        "scope_matches":
            scope_matches,

        "workspace_matches":
            workspace_matches,

        "execution_confirmed":
            execution_confirmed,

        "verification_confirmed":
            verification_confirmed,

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
        verification
    )


__all__ = [
    "BODY_STORE_LIFECYCLE_ANALYTICS_ENGINE_VERSION",
    "BODY_STORE_LIFECYCLE_ANALYTICS_ENGINE_SCHEMA",
    "LifecycleAnalyticsEngineError",
    "calculate_lifecycle_analytics_report_checksum_v1",
    "resolve_lifecycle_store_root_v1",
    "resolve_archive_store_root_v1",
    "resolve_tombstone_store_root_v1",
    "collect_lifecycle_records_v1",
    "collect_archive_metrics_v1",
    "collect_tombstone_metrics_v1",
    "collect_restore_metrics_v1",
    "collect_deletion_metrics_v1",
    "collect_retention_metrics_v1",
    "build_lifecycle_analytics_report_v1",
    "summarize_lifecycle_analytics_report_v1",
    "verify_lifecycle_analytics_report_v1",
    "build_lifecycle_analytics_engine_bundle_v1",
    "verify_lifecycle_analytics_engine_bundle_v1",
]
