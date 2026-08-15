from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .models import (
    JOB_STATUS_FAILED,
    VALID_JOB_STATUSES,
    JobStatusEvent,
    OrchestrationJob,
    utc_now,
)


DATA_DIR = Path("backend/server/data/orchestration")
JOBS_FILE = DATA_DIR / "jobs.json"
EVENTS_FILE = DATA_DIR / "job_events.json"


def _ensure_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _read_json(path: Path, default: Any) -> Any:
    _ensure_dir()
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: Path, data: Any) -> None:
    _ensure_dir()
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=_json_default),
        encoding="utf-8",
    )


def _parse_datetime(value: Any) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value))
    except Exception:
        return None


def _job_from_dict(data: Dict[str, Any]) -> OrchestrationJob:
    return OrchestrationJob(
        job_id=str(data.get("job_id", "")),
        workspace_id=str(data.get("workspace_id", "")),
        job_type=str(data.get("job_type", "")),
        status=str(data.get("status", "queued")),
        priority=int(data.get("priority", 5)),
        created_at=_parse_datetime(data.get("created_at")) or utc_now(),
        updated_at=_parse_datetime(data.get("updated_at")) or utc_now(),
        payload=data.get("payload") or {},
        metadata=data.get("metadata") or {},
        assigned_worker_id=data.get("assigned_worker_id"),
        progress_percent=float(data.get("progress_percent", 0.0)),
        current_step=str(data.get("current_step", "")),
        total_steps=int(data.get("total_steps", 0)),
        processed_count=int(data.get("processed_count", 0)),
        failed_count=int(data.get("failed_count", 0)),
        warning_count=int(data.get("warning_count", 0)),

        total_documents=int(data.get("total_documents", 0)),
        processed_documents=int(data.get("processed_documents", 0)),
        failed_documents=int(data.get("failed_documents", 0)),
        skipped_documents=int(data.get("skipped_documents", 0)),

        current_document_id=str(data.get("current_document_id", "")),
        current_document_name=str(data.get("current_document_name", "")),

        progress_message=str(data.get("progress_message", "")),
        started_at=_parse_datetime(data.get("started_at")),
        completed_at=_parse_datetime(data.get("completed_at")),
        error_message=data.get("error_message"),
    )


def load_jobs() -> Dict[str, OrchestrationJob]:
    raw = _read_json(JOBS_FILE, {})
    if not isinstance(raw, dict):
        return {}
    return {
        job_id: _job_from_dict(item)
        for job_id, item in raw.items()
        if isinstance(item, dict)
    }


def save_jobs(jobs: Dict[str, OrchestrationJob]) -> None:
    _write_json(JOBS_FILE, {job_id: asdict(job) for job_id, job in jobs.items()})


def get_job(job_id: str) -> Optional[OrchestrationJob]:
    return load_jobs().get(job_id)


def create_job(
    workspace_id: str,
    job_type: str,
    payload: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    priority: int = 5,
    *,
    job_id: Optional[str] = None,
) -> OrchestrationJob:
    """Persist one orchestration job.

    ``job_id`` is optional for backward compatibility.

    When omitted, this function preserves the historical orchestration
    behaviour and allocates a local ``job_*`` identity.

    When supplied, the caller owns the canonical job identity.  This is the
    ingress required by Universal Job / Runtime Registration integrations:
    the orchestration layer MUST persist that exact identity rather than
    minting a second job ID.
    """
    jobs = load_jobs()

    canonical_job_id = str(
        job_id
        or f"job_{uuid4().hex[:16]}"
    ).strip()

    if not canonical_job_id:
        raise ValueError(
            "job_id must be a non-empty string when supplied"
        )

    existing = jobs.get(
        canonical_job_id
    )

    if existing is not None:
        raise ValueError(
            "Job already exists: "
            + canonical_job_id
        )

    job = OrchestrationJob(
        job_id=canonical_job_id,
        workspace_id=workspace_id,
        job_type=job_type,
        payload=payload or {},
        metadata=metadata or {},
        priority=priority,
    )

    jobs[
        canonical_job_id
    ] = job

    save_jobs(
        jobs
    )

    append_job_event(
        canonical_job_id,
        "none",
        job.status,
        {
            "reason": "job_created",
            "caller_supplied_job_id": (
                job_id is not None
            ),
        },
    )

    return job


def update_job_status(
    job_id: str,
    new_status: str,
    metadata: Optional[Dict[str, Any]] = None,
    error_message: Optional[str] = None,
) -> OrchestrationJob:
    if new_status not in VALID_JOB_STATUSES:
        raise ValueError(f"Invalid job status: {new_status}")

    jobs = load_jobs()
    if job_id not in jobs:
        raise KeyError(f"Job not found: {job_id}")

    job = jobs[job_id]
    old_status = job.status
    job.status = new_status
    job.updated_at = utc_now()

    normalized_metadata = (
        dict(metadata)
        if isinstance(
            metadata,
            dict,
        )
        else {}
    )

    if normalized_metadata:

        existing_metadata = (
            job.metadata
            if isinstance(
                job.metadata,
                dict,
            )
            else {}
        )

        job.metadata = {
            **existing_metadata,
            **normalized_metadata,
        }

    if error_message:
        job.error_message = error_message

        if new_status == JOB_STATUS_FAILED:
            job.progress_percent = min(
                job.progress_percent,
                99.0,
            )

    jobs[job_id] = job

    save_jobs(
        jobs
    )

    append_job_event(
        job_id,
        old_status,
        new_status,
        normalized_metadata,
    )

    return job


def update_job_progress(
    job_id: str,
    progress_percent: float,
    metadata: Optional[Dict[str, Any]] = None,
    current_step: Optional[str] = None,
    progress_message: Optional[str] = None,
    total_steps: Optional[int] = None,
    processed_count: Optional[int] = None,
    failed_count: Optional[int] = None,
    warning_count: Optional[int] = None,
    total_documents: Optional[int] = None,
    processed_documents: Optional[int] = None,
    failed_documents: Optional[int] = None,
    skipped_documents: Optional[int] = None,
    current_document_id: Optional[str] = None,
    current_document_name: Optional[str] = None,
) -> OrchestrationJob:
    jobs = load_jobs()
    if job_id not in jobs:
        raise KeyError(f"Job not found: {job_id}")

    job = jobs[job_id]
    job.progress_percent = max(0.0, min(100.0, float(progress_percent)))
    job.updated_at = utc_now()

    if current_step is not None:
        job.current_step = str(current_step)

    if progress_message is not None:
        job.progress_message = str(progress_message)

    if total_steps is not None:
        job.total_steps = max(0, int(total_steps))

    if processed_count is not None:
        job.processed_count = max(0, int(processed_count))

    if failed_count is not None:
        job.failed_count = max(0, int(failed_count))

    if warning_count is not None:
        job.warning_count = max(0, int(warning_count))

    if total_documents is not None:
        job.total_documents = max(0, int(total_documents))

    if processed_documents is not None:
        job.processed_documents = max(0, int(processed_documents))

    if failed_documents is not None:
        job.failed_documents = max(0, int(failed_documents))

    if skipped_documents is not None:
        job.skipped_documents = max(0, int(skipped_documents))

    if current_document_id is not None:
        job.current_document_id = str(current_document_id)

    if current_document_name is not None:
        job.current_document_name = str(current_document_name)

    if metadata:
        job.metadata.update(metadata)

    jobs[job_id] = job
    save_jobs(jobs)
    return job


def append_job_event(
    job_id: str,
    old_status: str,
    new_status: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> JobStatusEvent:
    events = _read_json(EVENTS_FILE, {})
    if not isinstance(events, dict):
        events = {}

    event = JobStatusEvent(
        event_id=f"evt_{uuid4().hex[:16]}",
        job_id=job_id,
        old_status=old_status,
        new_status=new_status,
        metadata=metadata or {},
    )

    events.setdefault(job_id, [])
    events[job_id].append(asdict(event))
    _write_json(EVENTS_FILE, events)
    return event


def list_job_events(job_id: str) -> List[Dict[str, Any]]:
    events = _read_json(EVENTS_FILE, {})
    if not isinstance(events, dict):
        return []
    return events.get(job_id, [])




