"""Persistent Universal Article Body Store Queue Core.

This queue manages Body Store job state only.

It does not:

- execute the Body Store Worker;
- execute the Body Store Runtime;
- call the Repository, Writer, or Management Layer;
- access the Universal Article Body Store;
- persist article content bodies;
- perform Runtime Registration;
- perform semantic processing.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4


BODY_STORE_QUEUE_VERSION = (
    "universal_article_body_store_queue_v1"
)

BODY_STORE_QUEUE_JOB_SCHEMA_VERSION = (
    "body_store_queue_job_v1"
)

BODY_STORE_QUEUE_PRIORITIES = (
    "CRITICAL",
    "HIGH",
    "NORMAL",
    "LOW",
)

BODY_STORE_QUEUE_PRIORITY_RANK = {
    "CRITICAL": 0,
    "HIGH": 1,
    "NORMAL": 2,
    "LOW": 3,
}

BODY_STORE_QUEUE_STATUSES = (
    "QUEUED",
    "LEASED",
    "COMPLETED",
    "FAILED",
    "CANCELLED",
)

BODY_STORE_QUEUE_JOB_TYPES = (
    "body_store.store",
    "body_store.read",
    "body_store.verify",
    "body_store.metadata",
    "body_store.list",
)

_STATUS_DIRECTORIES = {
    "QUEUED": "queued",
    "LEASED": "leased",
    "COMPLETED": "completed",
    "FAILED": "failed",
    "CANCELLED": "cancelled",
}


class BodyStoreQueueContractError(
    ValueError
):
    """Raised when queue input violates the frozen contract."""


class BodyStoreQueueStateError(
    RuntimeError
):
    """Raised when a queue state transition is invalid."""


class BodyStoreQueueNotFoundError(
    FileNotFoundError
):
    """Raised when a queue job cannot be located."""


def _now() -> datetime:
    return datetime.now(
        timezone.utc
    )


def _now_iso() -> str:
    return _now().isoformat()


def _parse_iso(
    value: str | None,
) -> datetime | None:
    if not value:
        return None

    parsed = datetime.fromisoformat(
        value
    )

    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=timezone.utc
        )

    return parsed


def _require_string(
    value: Any,
    *,
    field_name: str,
) -> str:
    if not isinstance(
        value,
        str,
    ):
        raise BodyStoreQueueContractError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise BodyStoreQueueContractError(
            field_name
            + " must not be empty."
        )

    return normalized


def _require_mapping(
    value: Any,
    *,
    field_name: str,
) -> Mapping[str, Any]:
    if not isinstance(
        value,
        Mapping,
    ):
        raise BodyStoreQueueContractError(
            field_name
            + " must be a mapping."
        )

    return value


def _require_positive_integer(
    value: Any,
    *,
    field_name: str,
) -> int:
    if (
        not isinstance(
            value,
            int,
        )
        or isinstance(
            value,
            bool,
        )
        or value < 1
    ):
        raise BodyStoreQueueContractError(
            field_name
            + " must be a positive integer."
        )

    return value


def _contains_article_body(
    value: Any,
) -> bool:
    if isinstance(
        value,
        Mapping,
    ):
        for key, item in value.items():
            if str(
                key
            ).casefold() in {
                "content_body",
                "article_body",
                "body_payload",
            }:
                return True

            if _contains_article_body(
                item
            ):
                return True

        return False

    if isinstance(
        value,
        (
            list,
            tuple,
            set,
        ),
    ):
        return any(
            _contains_article_body(
                item
            )
            for item in value
        )

    return False


def _queue_root(
    *,
    project_root: str | Path,
) -> Path:
    return (
        Path(
            project_root
        ).resolve()
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_queue"
    )


def _ensure_layout(
    *,
    project_root: str | Path,
) -> Path:
    root = _queue_root(
        project_root=project_root
    )

    for directory in (
        "queued",
        "leased",
        "completed",
        "failed",
        "cancelled",
        "indexes",
        "statistics",
        "certification",
    ):
        (
            root
            / directory
        ).mkdir(
            parents=True,
            exist_ok=True,
        )

    return root


def _job_path(
    *,
    project_root: str | Path,
    status: str,
    queue_job_id: str,
) -> Path:
    directory = _STATUS_DIRECTORIES[
        status
    ]

    return (
        _queue_root(
            project_root=project_root
        )
        / directory
        / (
            queue_job_id
            + ".json"
        )
    )


def _write_json_atomic(
    path: Path,
    value: Mapping[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = path.with_suffix(
        path.suffix
        + ".tmp"
    )

    temporary.write_text(
        json.dumps(
            dict(
                value
            ),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    os.replace(
        temporary,
        path,
    )


def _load_job_path(
    path: Path,
) -> dict[str, Any]:
    value = json.loads(
        path.read_text(
            encoding="utf-8-sig"
        )
    )

    if not isinstance(
        value,
        dict,
    ):
        raise BodyStoreQueueContractError(
            "Queue job record must be a JSON object."
        )

    return value


def _find_job(
    *,
    project_root: str | Path,
    queue_job_id: str,
) -> tuple[Path, dict[str, Any]]:
    normalized_job_id = _require_string(
        queue_job_id,
        field_name="queue_job_id",
    )

    for status in BODY_STORE_QUEUE_STATUSES:
        path = _job_path(
            project_root=project_root,
            status=status,
            queue_job_id=normalized_job_id,
        )

        if path.is_file():
            return (
                path,
                _load_job_path(
                    path
                ),
            )

    raise BodyStoreQueueNotFoundError(
        "Body Store queue job not found: "
        + normalized_job_id
    )


def _move_job(
    *,
    project_root: str | Path,
    source_path: Path,
    job: Mapping[str, Any],
    target_status: str,
) -> dict[str, Any]:
    target_path = _job_path(
        project_root=project_root,
        status=target_status,
        queue_job_id=str(
            job[
                "queue_job_id"
            ]
        ),
    )

    _write_json_atomic(
        target_path,
        job,
    )

    if (
        source_path.resolve()
        != target_path.resolve()
        and source_path.exists()
    ):
        source_path.unlink()

    return dict(
        job
    )


def enqueue_body_store_job(
    *,
    project_root: str | Path,
    workspace_id: str,
    job_type: str,
    runtime_request: Mapping[str, Any],
    priority: str = "NORMAL",
    max_attempts: int = 3,
    metadata: Mapping[str, Any] | None = None,
    queue_job_id: str | None = None,
) -> dict[str, Any]:
    """Persist one Body Store queue job in QUEUED state."""

    _ensure_layout(
        project_root=project_root
    )

    normalized_workspace = _require_string(
        workspace_id,
        field_name="workspace_id",
    )

    normalized_job_type = _require_string(
        job_type,
        field_name="job_type",
    )

    if (
        normalized_job_type
        not in BODY_STORE_QUEUE_JOB_TYPES
    ):
        raise BodyStoreQueueContractError(
            "Unsupported Body Store queue job type: "
            + normalized_job_type
        )

    runtime_mapping = _require_mapping(
        runtime_request,
        field_name="runtime_request",
    )

    if _contains_article_body(
        runtime_mapping
    ):
        raise BodyStoreQueueContractError(
            "Queue records must not contain article content bodies."
        )

    normalized_priority = _require_string(
        priority,
        field_name="priority",
    ).upper()

    if (
        normalized_priority
        not in BODY_STORE_QUEUE_PRIORITIES
    ):
        raise BodyStoreQueueContractError(
            "Unsupported queue priority: "
            + normalized_priority
        )

    normalized_max_attempts = (
        _require_positive_integer(
            max_attempts,
            field_name="max_attempts",
        )
    )

    metadata_mapping = (
        {}
        if metadata is None
        else dict(
            _require_mapping(
                metadata,
                field_name="metadata",
            )
        )
    )

    if _contains_article_body(
        metadata_mapping
    ):
        raise BodyStoreQueueContractError(
            "Queue metadata must not contain article content bodies."
        )

    normalized_job_id = (
        _require_string(
            queue_job_id,
            field_name="queue_job_id",
        )
        if queue_job_id is not None
        else (
            "body_store_queue_"
            + uuid4().hex
        )
    )

    try:
        _find_job(
            project_root=project_root,
            queue_job_id=normalized_job_id,
        )

    except BodyStoreQueueNotFoundError:
        pass

    else:
        raise BodyStoreQueueContractError(
            "Queue job ID already exists: "
            + normalized_job_id
        )

    operation = runtime_mapping.get(
        "operation"
    )

    if not isinstance(
        operation,
        str,
    ):
        raise BodyStoreQueueContractError(
            "runtime_request.operation must be a string."
        )

    record = {
        "queue_schema_version":
            BODY_STORE_QUEUE_JOB_SCHEMA_VERSION,

        "queue_version":
            BODY_STORE_QUEUE_VERSION,

        "queue_job_id":
            normalized_job_id,

        "workspace_id":
            normalized_workspace,

        "job_type":
            normalized_job_type,

        "operation":
            operation.strip().casefold(),

        "runtime_request":
            dict(
                runtime_mapping
            ),

        "priority":
            normalized_priority,

        "priority_rank":
            BODY_STORE_QUEUE_PRIORITY_RANK[
                normalized_priority
            ],

        "status":
            "QUEUED",

        "attempt":
            0,

        "max_attempts":
            normalized_max_attempts,

        "created_at":
            _now_iso(),

        "leased_at":
            None,

        "lease_expiration":
            None,

        "lease_id":
            None,

        "worker_id":
            None,

        "completed_at":
            None,

        "cancelled_at":
            None,

        "failure":
            None,

        "completion":
            None,

        "metadata":
            metadata_mapping,
    }

    path = _job_path(
        project_root=project_root,
        status="QUEUED",
        queue_job_id=normalized_job_id,
    )

    _write_json_atomic(
        path,
        record,
    )

    return record


def list_body_store_jobs(
    *,
    project_root: str | Path,
    workspace_id: str | None = None,
    statuses: list[str] | tuple[str, ...] | None = None,
) -> list[dict[str, Any]]:
    """List queue records with optional workspace and status filtering."""

    _ensure_layout(
        project_root=project_root
    )

    normalized_workspace = (
        _require_string(
            workspace_id,
            field_name="workspace_id",
        )
        if workspace_id is not None
        else None
    )

    selected_statuses = (
        list(
            BODY_STORE_QUEUE_STATUSES
        )
        if statuses is None
        else [
            _require_string(
                status,
                field_name="status",
            ).upper()
            for status in statuses
        ]
    )

    for status in selected_statuses:
        if (
            status
            not in BODY_STORE_QUEUE_STATUSES
        ):
            raise BodyStoreQueueContractError(
                "Unsupported queue status: "
                + status
            )

    records = []

    root = _queue_root(
        project_root=project_root
    )

    for status in selected_statuses:
        directory = (
            root
            / _STATUS_DIRECTORIES[
                status
            ]
        )

        for path in directory.glob(
            "*.json"
        ):
            job = _load_job_path(
                path
            )

            if (
                normalized_workspace is not None
                and job.get(
                    "workspace_id"
                )
                != normalized_workspace
            ):
                continue

            records.append(
                job
            )

    records.sort(
        key=lambda item: (
            int(
                item.get(
                    "priority_rank",
                    999,
                )
            ),
            str(
                item.get(
                    "created_at",
                    "",
                )
            ),
            str(
                item.get(
                    "queue_job_id",
                    "",
                )
            ),
        )
    )

    return records


def peek_body_store_job(
    *,
    project_root: str | Path,
    workspace_id: str | None = None,
) -> dict[str, Any] | None:
    """Return the next eligible queued job without changing state."""

    records = list_body_store_jobs(
        project_root=project_root,
        workspace_id=workspace_id,
        statuses=[
            "QUEUED",
        ],
    )

    return (
        records[
            0
        ]
        if records
        else None
    )


def lease_body_store_job(
    *,
    project_root: str | Path,
    queue_job_id: str,
    worker_id: str,
    lease_seconds: int = 300,
) -> dict[str, Any]:
    """Lease one specifically identified QUEUED job."""

    source_path, job = _find_job(
        project_root=project_root,
        queue_job_id=queue_job_id,
    )

    if job.get(
        "status"
    ) != "QUEUED":
        raise BodyStoreQueueStateError(
            "Only QUEUED jobs may be leased."
        )

    normalized_worker = _require_string(
        worker_id,
        field_name="worker_id",
    )

    normalized_lease_seconds = (
        _require_positive_integer(
            lease_seconds,
            field_name="lease_seconds",
        )
    )

    current_attempt = int(
        job.get(
            "attempt",
            0,
        )
    )

    max_attempts = int(
        job.get(
            "max_attempts",
            1,
        )
    )

    if current_attempt >= max_attempts:
        raise BodyStoreQueueStateError(
            "Maximum attempts have already been reached."
        )

    leased_at = _now()

    updated = {
        **job,

        "status":
            "LEASED",

        "attempt":
            current_attempt
            + 1,

        "leased_at":
            leased_at.isoformat(),

        "lease_expiration":
            (
                leased_at
                + timedelta(
                    seconds=normalized_lease_seconds
                )
            ).isoformat(),

        "lease_id":
            (
                "body_store_lease_"
                + uuid4().hex
            ),

        "worker_id":
            normalized_worker,
    }

    return _move_job(
        project_root=project_root,
        source_path=source_path,
        job=updated,
        target_status="LEASED",
    )


def claim_body_store_job(
    *,
    project_root: str | Path,
    worker_id: str,
    workspace_id: str | None = None,
    lease_seconds: int = 300,
) -> dict[str, Any] | None:
    """Claim and lease the highest-priority eligible queued job."""

    candidate = peek_body_store_job(
        project_root=project_root,
        workspace_id=workspace_id,
    )

    if candidate is None:
        return None

    return lease_body_store_job(
        project_root=project_root,
        queue_job_id=str(
            candidate[
                "queue_job_id"
            ]
        ),
        worker_id=worker_id,
        lease_seconds=lease_seconds,
    )


def complete_body_store_job(
    *,
    project_root: str | Path,
    queue_job_id: str,
    worker_id: str,
    worker_execution_id: str,
    runtime_execution_id: str,
    runtime_success: bool,
    runtime_result_hash: str,
) -> dict[str, Any]:
    """Transition one LEASED job to COMPLETED."""

    source_path, job = _find_job(
        project_root=project_root,
        queue_job_id=queue_job_id,
    )

    if job.get(
        "status"
    ) != "LEASED":
        raise BodyStoreQueueStateError(
            "Only LEASED jobs may be completed."
        )

    normalized_worker = _require_string(
        worker_id,
        field_name="worker_id",
    )

    if job.get(
        "worker_id"
    ) != normalized_worker:
        raise BodyStoreQueueStateError(
            "Worker does not own this lease."
        )

    if runtime_success is not True:
        raise BodyStoreQueueContractError(
            "A completed job must have runtime_success=True."
        )

    completed_at = _now_iso()

    updated = {
        **job,

        "status":
            "COMPLETED",

        "completed_at":
            completed_at,

        "lease_expiration":
            None,

        "completion": {
            "completed_at":
                completed_at,

            "worker_execution_id":
                _require_string(
                    worker_execution_id,
                    field_name="worker_execution_id",
                ),

            "runtime_execution_id":
                _require_string(
                    runtime_execution_id,
                    field_name="runtime_execution_id",
                ),

            "runtime_success":
                True,

            "runtime_result_hash":
                _require_string(
                    runtime_result_hash,
                    field_name="runtime_result_hash",
                ),
        },
    }

    return _move_job(
        project_root=project_root,
        source_path=source_path,
        job=updated,
        target_status="COMPLETED",
    )


def fail_body_store_job(
    *,
    project_root: str | Path,
    queue_job_id: str,
    worker_id: str,
    error_type: str,
    error_message: str,
    retry_allowed: bool,
) -> dict[str, Any]:
    """Fail a LEASED job or requeue it when retry is allowed."""

    source_path, job = _find_job(
        project_root=project_root,
        queue_job_id=queue_job_id,
    )

    if job.get(
        "status"
    ) != "LEASED":
        raise BodyStoreQueueStateError(
            "Only LEASED jobs may fail."
        )

    normalized_worker = _require_string(
        worker_id,
        field_name="worker_id",
    )

    if job.get(
        "worker_id"
    ) != normalized_worker:
        raise BodyStoreQueueStateError(
            "Worker does not own this lease."
        )

    if not isinstance(
        retry_allowed,
        bool,
    ):
        raise BodyStoreQueueContractError(
            "retry_allowed must be a boolean."
        )

    attempt = int(
        job.get(
            "attempt",
            0,
        )
    )

    max_attempts = int(
        job.get(
            "max_attempts",
            1,
        )
    )

    may_retry = (
        retry_allowed
        and attempt < max_attempts
    )

    target_status = (
        "QUEUED"
        if may_retry
        else "FAILED"
    )

    failure_time = _now_iso()

    updated = {
        **job,

        "status":
            target_status,

        "leased_at":
            None,

        "lease_expiration":
            None,

        "lease_id":
            None,

        "worker_id":
            None,

        "failure": {
            "failure_time":
                failure_time,

            "error_type":
                _require_string(
                    error_type,
                    field_name="error_type",
                ),

            "error_message":
                _require_string(
                    error_message,
                    field_name="error_message",
                ),

            "attempt":
                attempt,

            "retry_allowed":
                may_retry,
        },
    }

    return _move_job(
        project_root=project_root,
        source_path=source_path,
        job=updated,
        target_status=target_status,
    )


def cancel_body_store_job(
    *,
    project_root: str | Path,
    queue_job_id: str,
) -> dict[str, Any]:
    """Cancel one QUEUED job."""

    source_path, job = _find_job(
        project_root=project_root,
        queue_job_id=queue_job_id,
    )

    if job.get(
        "status"
    ) != "QUEUED":
        raise BodyStoreQueueStateError(
            "Only QUEUED jobs may be cancelled."
        )

    updated = {
        **job,

        "status":
            "CANCELLED",

        "cancelled_at":
            _now_iso(),
    }

    return _move_job(
        project_root=project_root,
        source_path=source_path,
        job=updated,
        target_status="CANCELLED",
    )


def get_body_store_queue_statistics(
    *,
    project_root: str | Path,
    workspace_id: str | None = None,
) -> dict[str, Any]:
    """Compute queue statistics without reading article bodies."""

    records = list_body_store_jobs(
        project_root=project_root,
        workspace_id=workspace_id,
    )

    counts = {
        status:
            0
        for status in BODY_STORE_QUEUE_STATUSES
    }

    for record in records:
        status = str(
            record.get(
                "status",
                "",
            )
        )

        if status in counts:
            counts[
                status
            ] += 1

    queued_records = [
        record
        for record in records
        if record.get(
            "status"
        )
        == "QUEUED"
    ]

    oldest_queue_time = (
        min(
            str(
                record.get(
                    "created_at"
                )
            )
            for record in queued_records
        )
        if queued_records
        else None
    )

    wait_seconds = []

    for record in records:
        created = _parse_iso(
            record.get(
                "created_at"
            )
        )

        leased = _parse_iso(
            record.get(
                "leased_at"
            )
        )

        if (
            created is not None
            and leased is not None
        ):
            wait_seconds.append(
                max(
                    0.0,
                    (
                        leased
                        - created
                    ).total_seconds(),
                )
            )

    return {
        "queue_version":
            BODY_STORE_QUEUE_VERSION,

        "workspace_id":
            workspace_id,

        "total_jobs":
            len(
                records
            ),

        "queued_jobs":
            counts[
                "QUEUED"
            ],

        "leased_jobs":
            counts[
                "LEASED"
            ],

        "completed_jobs":
            counts[
                "COMPLETED"
            ],

        "failed_jobs":
            counts[
                "FAILED"
            ],

        "cancelled_jobs":
            counts[
                "CANCELLED"
            ],

        "oldest_queue_time":
            oldest_queue_time,

        "average_wait_time_seconds":
            (
                sum(
                    wait_seconds
                )
                / len(
                    wait_seconds
                )
                if wait_seconds
                else 0.0
            ),
    }


def purge_completed_body_store_jobs(
    *,
    project_root: str | Path,
    older_than_seconds: int,
) -> dict[str, Any]:
    """Delete completed queue records older than the supplied age."""

    normalized_age = _require_positive_integer(
        older_than_seconds,
        field_name="older_than_seconds",
    )

    threshold = (
        _now()
        - timedelta(
            seconds=normalized_age
        )
    )

    removed = []

    completed_directory = (
        _queue_root(
            project_root=project_root
        )
        / "completed"
    )

    _ensure_layout(
        project_root=project_root
    )

    for path in completed_directory.glob(
        "*.json"
    ):
        job = _load_job_path(
            path
        )

        completed_at = _parse_iso(
            job.get(
                "completed_at"
            )
        )

        if (
            completed_at is not None
            and completed_at < threshold
        ):
            removed.append(
                str(
                    job[
                        "queue_job_id"
                    ]
                )
            )

            path.unlink()

    return {
        "purged_count":
            len(
                removed
            ),

        "purged_queue_job_ids":
            sorted(
                removed
            ),
    }
