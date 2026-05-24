from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, Optional

from .job_store import (
    create_job,
    get_job,
    list_job_events,
    load_jobs,
    update_job_progress,
    update_job_status,
)
from .models import (
    JOB_STATUS_CANCELLED,
    JOB_STATUS_COMPLETED,
    JOB_STATUS_FAILED,
    JOB_STATUS_QUEUED,
    JOB_STATUS_RUNNING,
    OrchestrationJob,
)
from .queue import enqueue_job, queue_snapshot


def create_orchestration_job(
    workspace_id: str,
    job_type: str,
    payload: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    priority: int = 5,
) -> OrchestrationJob:
    job = create_job(
        workspace_id=workspace_id,
        job_type=job_type,
        payload=payload or {},
        metadata=metadata or {},
        priority=priority,
    )
    enqueue_job(job.job_id)
    return job


def get_orchestration_job(job_id: str) -> Optional[Dict[str, Any]]:
    job = get_job(job_id)
    if job is None:
        return None

    return {
        "job": asdict(job),
        "events": list_job_events(job_id),
    }


def list_orchestration_jobs() -> Dict[str, Any]:
    jobs = load_jobs()
    return {
        "jobs": [asdict(job) for job in jobs.values()],
        "queue": queue_snapshot(),
    }


def mark_job_running(job_id: str, worker_id: str | None = None) -> OrchestrationJob:
    metadata: Dict[str, Any] = {}
    if worker_id:
        metadata["worker_id"] = worker_id
    return update_job_status(job_id, JOB_STATUS_RUNNING, metadata=metadata)


def mark_job_completed(
    job_id: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> OrchestrationJob:
    update_job_progress(job_id, 100.0, metadata=metadata or {})
    return update_job_status(job_id, JOB_STATUS_COMPLETED, metadata=metadata or {})


def mark_job_failed(
    job_id: str,
    error_message: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> OrchestrationJob:
    return update_job_status(
        job_id,
        JOB_STATUS_FAILED,
        metadata=metadata or {},
        error_message=error_message,
    )


def cancel_job(
    job_id: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> OrchestrationJob:
    return update_job_status(job_id, JOB_STATUS_CANCELLED, metadata=metadata or {})


def update_orchestration_progress(
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
    return update_job_progress(
        job_id,
        progress_percent,
        metadata=metadata or {},
        current_step=current_step,
        progress_message=progress_message,
        total_steps=total_steps,
        processed_count=processed_count,
        failed_count=failed_count,
        warning_count=warning_count,
        total_documents=total_documents,
        processed_documents=processed_documents,
        failed_documents=failed_documents,
        skipped_documents=skipped_documents,
        current_document_id=current_document_id,
        current_document_name=current_document_name,
    )


def service_health() -> Dict[str, Any]:
    jobs = load_jobs()

    counts = {
        JOB_STATUS_QUEUED: 0,
        JOB_STATUS_RUNNING: 0,
        JOB_STATUS_COMPLETED: 0,
        JOB_STATUS_FAILED: 0,
        JOB_STATUS_CANCELLED: 0,
    }

    for job in jobs.values():
        counts[job.status] = counts.get(job.status, 0) + 1

    return {
        "ok": True,
        "total_jobs": len(jobs),
        "status_counts": counts,
        "queue": queue_snapshot(),
    }


