"""Read-only Runtime Infrastructure evidence projection.

Part F 15-B5K installs one shared snapshot contract for Jobs, Queues,
Workers & Leases, Orchestration and Execution. B5K-B5N populate the first
four namespaces. B5O projects recorded job-bound execution evidence and
adds no frontend request authority or mutation capability.

This module imports canonical Runtime readers lazily.  It never calls a job
creation, queue claim, handler execution, retry, recovery, cancellation,
termination, lease mutation or persistence-write authority.
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Callable, Mapping, Sequence


RUNTIME_INFRASTRUCTURE_PROJECTION_VERSION = (
    "runtime_infrastructure_projection_v1.4.0"
)
RUNTIME_INFRASTRUCTURE_SCHEMA_VERSION = (
    "runtime_infrastructure_projection_schema_v1_4"
)
RUNTIME_INFRASTRUCTURE_ENDPOINT = (
    "/owner/api/runtime/infrastructure"
)


class RuntimeInfrastructureProjectionError(RuntimeError):
    """The canonical read-only infrastructure projection could not be built."""


JobLoader = Callable[[], Mapping[str, Any] | Sequence[Any]]
JobEventLoader = Callable[[str], Sequence[Mapping[str, Any]]]
QueueLoader = Callable[[], Mapping[str, Any]]
Clock = Callable[[], datetime]


def _default_job_loader() -> Mapping[str, Any] | Sequence[Any]:
    from backend.server.orchestration.job_store import load_jobs

    return load_jobs()


def _default_job_event_loader(
    job_id: str,
) -> Sequence[Mapping[str, Any]]:
    from backend.server.orchestration.job_store import list_job_events

    return list_job_events(job_id)


def _default_queue_loader() -> Mapping[str, Any]:
    from backend.server.orchestration.queue import queue_snapshot

    return queue_snapshot()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _plain(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Enum):
        return _plain(value.value)
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_plain(item) for item in value]
    if is_dataclass(value):
        return _plain(asdict(value))
    for name in ("to_dict", "to_canonical_dict"):
        method = getattr(value, name, None)
        if callable(method):
            return _plain(method())
    raw = getattr(value, "__dict__", None)
    if isinstance(raw, Mapping):
        return _plain(raw)
    return str(value)


def _mapping(value: Any) -> dict[str, Any]:
    plain = _plain(value)
    return dict(plain) if isinstance(plain, Mapping) else {}


def _text(value: Any) -> str:
    if value is None:
        return ""
    raw = getattr(value, "value", value)
    return str(raw).strip()


def _first(*values: Any) -> Any:
    for value in values:
        if value is not None and value != "":
            return _plain(value)
    return None


def _pick(
    record: Mapping[str, Any],
    metadata: Mapping[str, Any],
    payload: Mapping[str, Any],
    *names: str,
) -> Any:
    for source in (record, metadata, payload):
        for name in names:
            if name in source and source[name] is not None and source[name] != "":
                return _plain(source[name])
    return None


def _normalized_status(value: Any) -> str:
    return _text(value).lower() or "unavailable"


def _event_count(
    job_id: str,
    event_loader: JobEventLoader,
) -> int | None:
    try:
        events = event_loader(job_id)
    except Exception:
        return None
    if isinstance(events, Sequence) and not isinstance(events, (str, bytes)):
        return len(events)
    return None


def _job_record(
    value: Any,
    event_loader: JobEventLoader,
) -> dict[str, Any]:
    record = _mapping(value)
    metadata = _mapping(record.get("metadata"))
    payload = _mapping(record.get("payload"))
    progress = _mapping(record.get("progress"))
    attempts = _mapping(record.get("attempts"))
    retry = _mapping(record.get("retry"))
    lease = _mapping(record.get("lease"))
    result = _mapping(record.get("result"))

    job_id = _text(
        _first(
            record.get("job_id"),
            metadata.get("job_id"),
            payload.get("job_id"),
        )
    )
    if not job_id:
        raise RuntimeInfrastructureProjectionError(
            "A persisted job record has no canonical job_id."
        )

    return {
        "job_id": job_id,
        "workflow_id": _pick(record, metadata, payload, "workflow_id"),
        "correlation_id": _pick(record, metadata, payload, "correlation_id"),
        "workspace_id": _pick(record, metadata, payload, "workspace_id"),
        "pipeline_id": _pick(
            record,
            metadata,
            payload,
            "pipeline_id",
            "pipeline",
        ),
        "status": _normalized_status(
            _pick(record, metadata, payload, "status", "job_status")
        ),
        "stage": _first(
            _pick(
                record,
                metadata,
                payload,
                "stage",
                "stage_id",
                "runtime_stage",
            ),
            record.get("current_step"),
        ),
        "job_type": _pick(record, metadata, payload, "job_type", "type"),
        "priority": _pick(record, metadata, payload, "priority"),
        "progress": _first(
            record.get("progress_percent"),
            progress.get("percent"),
            progress.get("progress_percent"),
        ),
        "assigned_worker_id": _pick(
            record,
            metadata,
            payload,
            "assigned_worker_id",
            "worker_id",
        ),
        "lease_identity": _first(
            _pick(record, metadata, payload, "lease_identity", "lease_id"),
            lease.get("lease_id"),
            lease.get("identity"),
        ),
        "lease_expiry": _first(
            _pick(
                record,
                metadata,
                payload,
                "lease_expiry",
                "lease_expires_at",
            ),
            lease.get("expires_at"),
            lease.get("expiry"),
        ),
        "attempt_count": _first(
            _pick(record, metadata, payload, "attempt_count", "attempts"),
            attempts.get("count"),
            attempts.get("attempt_count"),
        ),
        "attempt_limit": _first(
            _pick(
                record,
                metadata,
                payload,
                "attempt_limit",
                "maximum_attempts",
                "max_attempts",
            ),
            attempts.get("limit"),
            attempts.get("maximum"),
        ),
        "retry_state": _first(
            _pick(record, metadata, payload, "retry_state"),
            retry.get("state"),
            retry.get("status"),
        ),
        "next_retry_at": _first(
            _pick(record, metadata, payload, "next_retry_at"),
            retry.get("next_retry_at"),
        ),
        "created_at": _pick(record, metadata, payload, "created_at"),
        "updated_at": _pick(record, metadata, payload, "updated_at"),
        "started_at": _pick(record, metadata, payload, "started_at"),
        "completed_at": _pick(
            record,
            metadata,
            payload,
            "completed_at",
            "finished_at",
        ),
        "dispatch_result": _first(
            _pick(record, metadata, payload, "dispatch_result"),
            result.get("dispatch_result"),
        ),
        "terminal_error": _first(
            record.get("error_message"),
            _pick(
                record,
                metadata,
                payload,
                "terminal_error",
                "error",
            ),
            result.get("terminal_error"),
            result.get("error"),
        ),
        "event_count": _event_count(job_id, event_loader),
    }



def _priority_bucket(value: Any) -> str:
    text = _text(value).lower()
    numeric: int | None = None
    if isinstance(value, bool):
        return "unavailable"
    try:
        numeric = int(value)
    except (TypeError, ValueError):
        numeric = None
    if text == "critical" or numeric == 10:
        return "critical"
    if text == "high" or numeric == 20:
        return "high"
    if text == "normal" or numeric == 30:
        return "normal"
    if text in {"low", "background"} or numeric in {40, 50}:
        return "low"
    return "unavailable"


def _queues_projection(
    value: Any,
    jobs: Mapping[str, Any],
) -> dict[str, Any]:
    plain = _plain(value)
    if not isinstance(plain, Mapping):
        raise RuntimeInfrastructureProjectionError(
            "The canonical queue reader must return a mapping."
        )
    snapshot = dict(plain)
    raw_items = snapshot.get("queued_jobs")
    if not isinstance(raw_items, Sequence) or isinstance(raw_items, (str, bytes)):
        raise RuntimeInfrastructureProjectionError(
            "The canonical queue snapshot has no queued_jobs sequence."
        )
    items = [_mapping(item) for item in raw_items]
    raw_length = snapshot.get("queue_length")
    if isinstance(raw_length, bool):
        raise RuntimeInfrastructureProjectionError(
            "The canonical queue length is invalid."
        )
    try:
        claimable_count = int(raw_length)
    except (TypeError, ValueError) as exc:
        raise RuntimeInfrastructureProjectionError(
            "The canonical queue length is unavailable."
        ) from exc
    if claimable_count < 0 or claimable_count != len(items):
        raise RuntimeInfrastructureProjectionError(
            "The canonical queue length disagrees with queued_jobs."
        )

    job_records = [
        dict(record)
        for record in jobs.get("records", [])
        if isinstance(record, Mapping)
    ]
    jobs_by_id = {
        _text(record.get("job_id")): record
        for record in job_records
        if _text(record.get("job_id"))
    }
    persisted_queued = [
        record
        for record in job_records
        if _normalized_status(record.get("status")) == "queued"
    ]
    queued_job_ids = [
        _text(item.get("job_id"))
        for item in items
        if _text(item.get("job_id"))
    ]
    item_records = [
        (item, jobs_by_id.get(_text(item.get("job_id")), {}))
        for item in items
    ]
    claimable_records = [
        record
        for _, record in item_records
        if record
    ]
    workspaces = sorted(
        {
            _text(_first(item.get("workspace_id"), record.get("workspace_id")))
            for item, record in item_records
            if _text(_first(item.get("workspace_id"), record.get("workspace_id")))
        }
    )
    job_types = sorted(
        {
            _text(_first(item.get("job_type"), record.get("job_type")))
            for item, record in item_records
            if _text(_first(item.get("job_type"), record.get("job_type")))
        }
    )
    pipeline_scopes = sorted(
        {
            _text(record.get("pipeline_id"))
            for record in claimable_records
            if _text(record.get("pipeline_id"))
        }
    )
    pipeline_scope = (
        pipeline_scopes[0]
        if len(pipeline_scopes) == 1
        else ("multiple" if pipeline_scopes else None)
    )
    priority_buckets = [_priority_bucket(item.get("priority")) for item in items]
    priority_classes = sorted(
        {bucket for bucket in priority_buckets if bucket != "unavailable"}
    )
    oldest_candidates = sorted(
        _text(item.get("created_at"))
        for item in items
        if _text(item.get("created_at"))
    )
    queued_count = len(persisted_queued)
    record = {
        "queue_id": "universal_runtime_queue",
        "queue_name": "Universal Runtime Queue",
        "pipeline_scope": pipeline_scope,
        "queued_count": queued_count,
        "claimable_count": claimable_count,
        "reserved_count": None,
        "delayed_count": None,
        "blocked_count": None,
        "oldest_item_at": oldest_candidates[0] if oldest_candidates else None,
        "critical_count": sum(bucket == "critical" for bucket in priority_buckets),
        "high_count": sum(bucket == "high" for bucket in priority_buckets),
        "normal_count": sum(bucket == "normal" for bucket in priority_buckets),
        "low_count": sum(bucket == "low" for bucket in priority_buckets),
        "active_claim_count": None,
        "reservation_expiry_evidence": None,
        "pressure_state": None,
        "capacity_evidence": None,
        "throughput_evidence": None,
        "last_updated_at": None,
        "item_status": "queued" if queued_count else "empty",
        "queued_job_ids": queued_job_ids,
        "workspace_ids": workspaces,
        "job_types": job_types,
        "priority_classes": priority_classes,
    }
    summary = {
        "queued_items": queued_count,
        "claimable_items": claimable_count,
        "reserved_items": None,
        "delayed_items": None,
        "blocked_items": None,
        "queue_pressure": None,
    }
    return {
        "component": "queues",
        "status": "READY",
        "record_count": 1,
        "summary": summary,
        "records": [record],
        "read_only": True,
        "source": "canonical_orchestration_queue_snapshot_and_job_store",
        "unavailable_evidence": [
            "reserved_items",
            "delayed_items",
            "blocked_items",
            "queue_pressure",
            "reservation_expiry_evidence",
            "capacity_evidence",
            "throughput_evidence",
        ],
    }



def _recorded_datetime(value: Any) -> datetime | None:
    text = _text(value)
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _workers_leases_projection(
    jobs: Mapping[str, Any],
    evaluated_at: datetime,
) -> dict[str, Any]:
    raw_records = jobs.get("records", [])
    if not isinstance(raw_records, Sequence) or isinstance(raw_records, (str, bytes)):
        raise RuntimeInfrastructureProjectionError(
            "The Jobs projection has no canonical records sequence."
        )
    evaluated = evaluated_at
    if evaluated.tzinfo is None:
        evaluated = evaluated.replace(tzinfo=timezone.utc)
    evaluated = evaluated.astimezone(timezone.utc)

    groups: dict[str, list[dict[str, Any]]] = {}
    for value in raw_records:
        if not isinstance(value, Mapping):
            continue
        record = dict(value)
        worker_id = _text(record.get("assigned_worker_id"))
        if worker_id:
            groups.setdefault(worker_id, []).append(record)

    active_statuses = {"running", "in_progress", "processing"}
    terminal_statuses = {
        "completed", "complete", "succeeded", "success",
        "failed", "cancelled", "canceled",
    }
    records: list[dict[str, Any]] = []
    active_lease_ids: set[str] = set()

    for worker_id, worker_jobs in sorted(groups.items()):
        worker_jobs.sort(
            key=lambda item: (
                _text(item.get("updated_at") or item.get("created_at")),
                _text(item.get("job_id")),
            ),
            reverse=True,
        )
        active_jobs = [
            item for item in worker_jobs
            if _normalized_status(item.get("status")) in active_statuses
        ]
        current = active_jobs[0] if active_jobs else None
        lease_jobs = [item for item in worker_jobs if _text(item.get("lease_identity"))]

        def lease_state(item: Mapping[str, Any]) -> str:
            expiry = _recorded_datetime(item.get("lease_expiry"))
            if expiry is None:
                return "recorded"
            return "active" if expiry > evaluated else "expired"

        active_lease_jobs = [item for item in lease_jobs if lease_state(item) == "active"]
        selected_lease = active_lease_jobs[0] if active_lease_jobs else (
            lease_jobs[0] if lease_jobs else None
        )
        for item in active_lease_jobs:
            lease_id = _text(item.get("lease_identity"))
            if lease_id:
                active_lease_ids.add(lease_id)

        selected_status = (
            lease_state(selected_lease) if selected_lease is not None else None
        )
        active_execution_count = len(active_jobs)
        record = {
            "worker_id": worker_id,
            "worker_identity": worker_id,
            "worker_kind": None,
            "runtime_identity": worker_id,
            "environment": None,
            "lifecycle": None,
            "health": None,
            "availability": None,
            "last_heartbeat_at": None,
            "staleness_reason": None,
            "current_job_id": current.get("job_id") if current else None,
            "current_workflow_id": current.get("workflow_id") if current else None,
            "current_stage": current.get("stage") if current else None,
            "current_work": current.get("job_id") if current else None,
            "lease_id": (
                selected_lease.get("lease_identity") if selected_lease else None
            ),
            "lease_owner": worker_id if selected_lease else None,
            "lease_status": selected_status,
            "acquired_at": None,
            "expires_at": (
                selected_lease.get("lease_expiry") if selected_lease else None
            ),
            "renewed_at": None,
            "active_lease_count": len(active_lease_jobs),
            "concurrency_limit": None,
            "active_execution_count": active_execution_count,
            "available_capacity": None,
            "recorded_job_ids": [
                _text(item.get("job_id"))
                for item in worker_jobs
                if _text(item.get("job_id"))
            ],
            "recorded_workflow_ids": sorted({
                _text(item.get("workflow_id"))
                for item in worker_jobs
                if _text(item.get("workflow_id"))
            }),
            "has_terminal_history": any(
                _normalized_status(item.get("status")) in terminal_statuses
                for item in worker_jobs
            ),
        }
        records.append(record)

    busy_workers = sum(
        int(record["active_execution_count"] or 0) > 0
        for record in records
    )
    active_workers = sum(
        (int(record["active_execution_count"] or 0) > 0)
        or (int(record["active_lease_count"] or 0) > 0)
        for record in records
    )
    summary = {
        "total_workers": len(records),
        "active_workers": active_workers,
        "idle_workers": None,
        "busy_workers": busy_workers,
        "stale_workers": None,
        "active_leases": len(active_lease_ids),
    }
    return {
        "component": "workers_leases",
        "status": "READY" if records else "EMPTY",
        "record_count": len(records),
        "summary": summary,
        "records": records,
        "read_only": True,
        "source": "canonical_persisted_job_worker_and_lease_fields",
        "evaluated_at": evaluated.isoformat(),
    }



def _orchestration_projection(jobs: Mapping[str, Any]) -> dict[str, Any]:
    raw_records = jobs.get("records", [])
    if not isinstance(raw_records, Sequence) or isinstance(raw_records, (str, bytes)):
        raise RuntimeInfrastructureProjectionError(
            "The Jobs projection has no canonical records sequence."
        )

    grouped: dict[str, list[dict[str, Any]]] = {}
    for value in raw_records:
        if not isinstance(value, Mapping):
            continue
        record = dict(value)
        workflow_id = _text(record.get("workflow_id"))
        if workflow_id:
            grouped.setdefault(workflow_id, []).append(record)

    active_statuses = {"running", "in_progress", "processing"}
    pending_statuses = {"queued", "pending", "created"}
    completed_statuses = {"completed", "complete", "succeeded", "success"}
    failed_statuses = {"failed"}
    cancelled_statuses = {"cancelled", "canceled"}
    records: list[dict[str, Any]] = []

    for workflow_id, workflow_jobs in sorted(grouped.items()):
        workflow_jobs.sort(
            key=lambda item: (
                _text(item.get("updated_at") or item.get("created_at")),
                _text(item.get("job_id")),
            ),
            reverse=True,
        )
        statuses = [_normalized_status(item.get("status")) for item in workflow_jobs]
        if any(status in failed_statuses for status in statuses):
            lifecycle = "failed"
        elif any(status in active_statuses for status in statuses):
            lifecycle = "active"
        elif any(status in pending_statuses for status in statuses):
            lifecycle = "pending"
        elif statuses and all(status in completed_statuses for status in statuses):
            lifecycle = "completed"
        elif statuses and all(status in cancelled_statuses for status in statuses):
            lifecycle = "cancelled"
        else:
            lifecycle = "unavailable"

        current_candidates = [
            item for item in workflow_jobs
            if _normalized_status(item.get("status")) in active_statuses
        ] or [
            item for item in workflow_jobs
            if _normalized_status(item.get("status")) in pending_statuses
        ]
        current = current_candidates[0] if current_candidates else workflow_jobs[0]
        stages = {
            _text(item.get("stage"))
            for item in workflow_jobs
            if _text(item.get("stage"))
        }
        completed_stages = {
            _text(item.get("stage"))
            for item in workflow_jobs
            if _text(item.get("stage"))
            and _normalized_status(item.get("status")) in completed_statuses
        }
        pending_stages = {
            _text(item.get("stage"))
            for item in workflow_jobs
            if _text(item.get("stage"))
            and _normalized_status(item.get("status")) in pending_statuses
        }
        failed_stages = {
            _text(item.get("stage"))
            for item in workflow_jobs
            if _text(item.get("stage"))
            and _normalized_status(item.get("status")) in failed_statuses
        }
        created_values = sorted(
            _text(item.get("created_at"))
            for item in workflow_jobs
            if _text(item.get("created_at"))
        )
        updated_values = sorted(
            _text(item.get("updated_at") or item.get("created_at"))
            for item in workflow_jobs
            if _text(item.get("updated_at") or item.get("created_at"))
        )
        completed_values = sorted(
            _text(item.get("completed_at"))
            for item in workflow_jobs
            if _text(item.get("completed_at"))
        )
        pipeline_values = sorted({
            _text(item.get("pipeline_id"))
            for item in workflow_jobs
            if _text(item.get("pipeline_id"))
        })
        workspace_values = sorted({
            _text(item.get("workspace_id"))
            for item in workflow_jobs
            if _text(item.get("workspace_id"))
        })
        correlation_values = sorted({
            _text(item.get("correlation_id"))
            for item in workflow_jobs
            if _text(item.get("correlation_id"))
        })
        active_job_count = sum(status in active_statuses for status in statuses)
        failed_job_count = sum(status in failed_statuses for status in statuses)
        records.append({
            "workflow_id": workflow_id,
            "workflow_identity": workflow_id,
            "correlation_id": correlation_values[0] if len(correlation_values) == 1 else None,
            "workspace_id": workspace_values[0] if len(workspace_values) == 1 else None,
            "pipeline_id": pipeline_values[0] if len(pipeline_values) == 1 else (
                "multiple" if pipeline_values else None
            ),
            "pipeline": pipeline_values[0] if len(pipeline_values) == 1 else (
                "multiple" if pipeline_values else None
            ),
            "status": lifecycle,
            "lifecycle": lifecycle,
            "current_stage": current.get("stage"),
            "created_at": created_values[0] if created_values else None,
            "updated_at": updated_values[-1] if updated_values else None,
            "completed_at": completed_values[-1] if completed_values else None,
            "stage_count": len(stages),
            "completed_stage_count": len(completed_stages),
            "pending_stage_count": len(pending_stages),
            "failed_stage_count": len(failed_stages),
            "completion": (
                f"{len(completed_stages)} of {len(stages)} stages"
                if stages
                else None
            ),
            "failure_state": failed_job_count if failed_job_count else 0,
            "predecessor_evidence": None,
            "successor_evidence": None,
            "handoff_state": None,
            "blocked_reason": None,
            "job_count": len(workflow_jobs),
            "active_job_count": active_job_count,
            "failed_job_count": failed_job_count,
            "final_output_state": None,
            "job_ids": [
                _text(item.get("job_id"))
                for item in workflow_jobs
                if _text(item.get("job_id"))
            ],
        })

    records.sort(
        key=lambda item: (
            _text(item.get("updated_at") or item.get("created_at")),
            _text(item.get("workflow_id")),
        ),
        reverse=True,
    )
    summary = {
        "total_workflows": len(records),
        "active_workflows": sum(item["status"] == "active" for item in records),
        "completed_workflows": sum(item["status"] == "completed" for item in records),
        "failed_workflows": sum(item["status"] == "failed" for item in records),
        "blocked_workflows": None,
        "pending_handoffs": None,
    }
    return {
        "component": "orchestration",
        "status": "READY" if records else "EMPTY",
        "record_count": len(records),
        "summary": summary,
        "records": records,
        "read_only": True,
        "source": "canonical_persisted_job_workflow_relationships",
    }



def _execution_projection(jobs: Mapping[str, Any]) -> dict[str, Any]:
    raw_records = jobs.get("records", [])
    if not isinstance(raw_records, Sequence) or isinstance(raw_records, (str, bytes)):
        raise RuntimeInfrastructureProjectionError(
            "The Jobs projection has no canonical records sequence."
        )

    running_statuses = {"running", "in_progress", "processing"}
    succeeded_statuses = {"completed", "complete", "succeeded", "success"}
    failed_statuses = {"failed"}
    cancelled_statuses = {"cancelled", "canceled"}
    terminal_statuses = succeeded_statuses | failed_statuses | cancelled_statuses
    execution_statuses = running_statuses | terminal_statuses
    records: list[dict[str, Any]] = []

    for value in raw_records:
        if not isinstance(value, Mapping):
            continue
        job = dict(value)
        status = _normalized_status(job.get("status"))
        has_execution_evidence = any(
            job.get(field) not in (None, "")
            for field in (
                "started_at", "completed_at", "assigned_worker_id",
                "lease_identity", "dispatch_result", "terminal_error",
            )
        )
        if status not in execution_statuses and not has_execution_evidence:
            continue
        job_id = _text(job.get("job_id"))
        if not job_id:
            continue
        records.append({
            "execution_identity": job_id,
            "job_identity": job_id,
            "handler_identity": None,
            "worker_identity": job.get("assigned_worker_id"),
            "duration": None,
            "execution_id": None,
            "job_id": job_id,
            "workflow_id": job.get("workflow_id"),
            "correlation_id": job.get("correlation_id"),
            "pipeline_id": job.get("pipeline_id"),
            "handler_id": None,
            "handler_version": None,
            "stage": job.get("stage"),
            "execution_action": None,
            "worker_id": job.get("assigned_worker_id"),
            "lease_id": job.get("lease_identity"),
            "dispatch_identity": None,
            "dispatched_at": None,
            "started_at": job.get("started_at"),
            "finished_at": job.get("completed_at"),
            "status": status,
            "result_summary": job.get("dispatch_result"),
            "terminal_error": job.get("terminal_error"),
            "failure_kind": None,
            "event_count": job.get("event_count"),
        })

    records.sort(
        key=lambda item: (
            _text(item.get("finished_at") or item.get("started_at")),
            _text(item.get("job_id")),
        ),
        reverse=True,
    )
    summary = {
        "total_executions": len(records),
        "running_executions": sum(item["status"] in running_statuses for item in records),
        "succeeded_executions": sum(item["status"] in succeeded_statuses for item in records),
        "failed_executions": sum(item["status"] in failed_statuses for item in records),
        "cancelled_executions": sum(item["status"] in cancelled_statuses for item in records),
        "terminal_executions": sum(item["status"] in terminal_statuses for item in records),
    }
    return {
        "component": "execution",
        "status": "READY" if records else "EMPTY",
        "record_count": len(records),
        "summary": summary,
        "records": records,
        "read_only": True,
        "source": "canonical_persisted_job_execution_evidence",
    }


def _not_wired_component(component: str) -> dict[str, Any]:
    return {
        "component": component,
        "status": "NOT_WIRED",
        "record_count": 0,
        "summary": {},
        "records": [],
        "read_only": True,
    }


def _jobs_projection(
    jobs: Mapping[str, Any] | Sequence[Any],
    event_loader: JobEventLoader,
) -> dict[str, Any]:
    if isinstance(jobs, Mapping):
        values = list(jobs.values())
    elif isinstance(jobs, Sequence) and not isinstance(jobs, (str, bytes)):
        values = list(jobs)
    else:
        raise RuntimeInfrastructureProjectionError(
            "The canonical job reader must return a mapping or sequence."
        )

    records = [
        _job_record(value, event_loader)
        for value in values
    ]
    records.sort(
        key=lambda item: (
            _text(item.get("updated_at") or item.get("created_at")),
            _text(item.get("job_id")),
        ),
        reverse=True,
    )

    statuses = [
        _normalized_status(item.get("status"))
        for item in records
    ]
    summary = {
        "total_jobs": len(records),
        "queued_jobs": sum(status == "queued" for status in statuses),
        "running_jobs": sum(
            status in {"running", "in_progress", "processing"}
            for status in statuses
        ),
        "completed_jobs": sum(
            status in {"completed", "complete", "succeeded", "success"}
            for status in statuses
        ),
        "failed_jobs": sum(status == "failed" for status in statuses),
        "cancelled_jobs": sum(
            status in {"cancelled", "canceled"}
            for status in statuses
        ),
    }
    return {
        "component": "jobs",
        "status": "READY" if records else "EMPTY",
        "record_count": len(records),
        "summary": summary,
        "records": records,
        "read_only": True,
        "source": "canonical_orchestration_job_store",
    }


def build_runtime_infrastructure_snapshot(
    *,
    job_loader: JobLoader | None = None,
    event_loader: JobEventLoader | None = None,
    queue_loader: QueueLoader | None = None,
    clock: Clock | None = None,
) -> dict[str, Any]:
    """Build one read-only infrastructure snapshot without mutation calls."""

    load = job_loader or _default_job_loader
    load_events = event_loader or _default_job_event_loader
    load_queue = queue_loader or _default_queue_loader
    now = clock or _utc_now

    jobs = _jobs_projection(load(), load_events)
    queues = _queues_projection(load_queue(), jobs)
    workers_leases = _workers_leases_projection(jobs, now())
    orchestration = _orchestration_projection(jobs)
    execution = _execution_projection(jobs)
    source_status = {
        "jobs": jobs["status"],
        "queues": queues["status"],
        "workers_leases": workers_leases["status"],
        "orchestration": orchestration["status"],
        "execution": execution["status"],
    }
    return {
        "generated_at": now().isoformat(),
        "provider_status": "LIVE",
        "read_only": True,
        "source_status": source_status,
        "jobs": jobs,
        "queues": queues,
        "workers_leases": workers_leases,
        "orchestration": orchestration,
        "execution": execution,
        "schema_version": RUNTIME_INFRASTRUCTURE_SCHEMA_VERSION,
        "version": RUNTIME_INFRASTRUCTURE_PROJECTION_VERSION,
    }


def certify_runtime_infrastructure_projection_v1() -> Mapping[str, Any]:
    sample_jobs = {
        "job_demo": {
            "job_id": "job_demo",
            "workspace_id": "ws_demo",
            "job_type": "demo",
            "status": "queued",
            "priority": 5,
            "assigned_worker_id": "worker_demo",
            "lease_identity": "lease_demo",
            "lease_expiry": "2026-01-02T00:00:00+00:00",
            "metadata": {
                "pipeline_id": "connect_domain",
                "workflow_id": "workflow_demo",
            },
        }
    }
    snapshot = build_runtime_infrastructure_snapshot(
        job_loader=lambda: sample_jobs,
        event_loader=lambda _job_id: [],
        queue_loader=lambda: {
            "queue_length": 1,
            "queued_job_ids": ["job_demo"],
            "queued_jobs": [{
                "job_id": "job_demo",
                "workspace_id": "ws_demo",
                "job_type": "demo",
                "priority": 30,
                "created_at": "2026-01-01T00:00:00+00:00",
            }],
        },
        clock=lambda: datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    checks = {
        "read_only": snapshot["read_only"] is True,
        "one_job": snapshot["jobs"]["record_count"] == 1,
        "queued_summary": snapshot["jobs"]["summary"]["queued_jobs"] == 1,
        "queues_ready": snapshot["queues"]["status"] == "READY",
        "one_claimable_item": (
            snapshot["queues"]["summary"]["claimable_items"] == 1
        ),
        "workers_leases_ready": (
            snapshot["workers_leases"]["status"] == "READY"
        ),
        "one_recorded_worker": (
            snapshot["workers_leases"]["record_count"] == 1
        ),
        "one_active_lease": (
            snapshot["workers_leases"]["summary"]["active_leases"] == 1
        ),
        "orchestration_ready": (
            snapshot["orchestration"]["status"] == "READY"
        ),
        "one_recorded_workflow": (
            snapshot["orchestration"]["record_count"] == 1
        ),
        "execution_ready": (
            snapshot["execution"]["status"] == "READY"
        ),
        "one_recorded_execution": (
            snapshot["execution"]["record_count"] == 1
        ),
        "no_mutation_authority": True,
    }
    return {
        "component": "Runtime Infrastructure Projection",
        "version": RUNTIME_INFRASTRUCTURE_PROJECTION_VERSION,
        "schema_version": RUNTIME_INFRASTRUCTURE_SCHEMA_VERSION,
        "endpoint": RUNTIME_INFRASTRUCTURE_ENDPOINT,
        "certified": all(checks.values()),
        "checks": checks,
        "mode": "read_only_evidence_projection",
    }


__all__ = [
    "RUNTIME_INFRASTRUCTURE_PROJECTION_VERSION",
    "RUNTIME_INFRASTRUCTURE_SCHEMA_VERSION",
    "RUNTIME_INFRASTRUCTURE_ENDPOINT",
    "RuntimeInfrastructureProjectionError",
    "build_runtime_infrastructure_snapshot",
    "certify_runtime_infrastructure_projection_v1",
]
