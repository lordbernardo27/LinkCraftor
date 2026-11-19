# backend/server/orchestration/service.py
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
    *,
    job_id: Optional[str] = None,
) -> OrchestrationJob:
    """Create and enqueue a job.

    When ``job_id`` is supplied, orchestration preserves that exact
    caller-owned canonical identity. This is the ingress used by the
    Universal Job Creation Engine so orchestration does not mint a
    second runtime identity.

    NOTE on priority: jobs are served in ascending (priority, created_at)
    order — a LOWER number means served sooner. The default of 5 leaves
    room on both sides (e.g. 1 for urgent user-facing work, 9 for bulk
    background rebuilds).
    """
    job = create_job(
        workspace_id=workspace_id,
        job_type=job_type,
        payload=payload or {},
        metadata=metadata or {},
        priority=priority,
        job_id=job_id,
    )
    # Enqueueing is implicit (queue membership == persisted "queued" status);
    # enqueue_job is retained as a sanity check that the job landed in the
    # store correctly.
    if not enqueue_job(job.job_id):
        print(f"[ORCHESTRATION_ENQUEUE_WARNING] job {job.job_id} not visible as queued after create")
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
    """Transition a job to RUNNING.

    FIX: made idempotent. dequeue_job() now claims jobs by flipping them to
    RUNNING atomically, so by the time the worker calls this the job is
    usually already running. Re-issuing the transition would be harmless in
    most stores but is wasteful and can clobber claim metadata; if the job is
    already RUNNING we just return it (merging in the worker_id if it wasn't
    recorded yet).
    """
    job = get_job(job_id)
    if job is None:
        raise KeyError(f"unknown job: {job_id}")

    if job.status == JOB_STATUS_RUNNING:
        if worker_id and (job.metadata or {}).get("worker_id") != worker_id:
            # Record the worker identity without re-transitioning status.
            return update_job_status(
                job_id, JOB_STATUS_RUNNING, metadata={"worker_id": worker_id}
            )
        return job

    metadata: Dict[str, Any] = {}
    if worker_id:
        metadata["worker_id"] = worker_id
    return update_job_status(job_id, JOB_STATUS_RUNNING, metadata=metadata)


def mark_job_completed(
    job_id: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> OrchestrationJob:
    # FIX: metadata was previously passed to BOTH the progress update and the
    # status update, merging the same dict twice. Progress just records 100%;
    # metadata rides on the terminal status change.
    update_job_progress(job_id, 100.0)
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