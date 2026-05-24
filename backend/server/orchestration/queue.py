from __future__ import annotations

from typing import Dict, List, Optional

from .job_store import get_job, load_jobs
from .models import JOB_STATUS_QUEUED, OrchestrationJob


_queue_job_ids: List[str] = []


def enqueue_job(job_id: str) -> None:
    if job_id not in _queue_job_ids:
        _queue_job_ids.append(job_id)


def dequeue_job(worker_id: str | None = None) -> Optional[OrchestrationJob]:
    refresh_queue_from_store()

    if not _queue_job_ids:
        return None

    jobs = load_jobs()

    queued_jobs = [
        jobs[job_id]
        for job_id in _queue_job_ids
        if job_id in jobs and jobs[job_id].status == JOB_STATUS_QUEUED
    ]

    if not queued_jobs:
        _queue_job_ids.clear()
        return None

    queued_jobs.sort(key=lambda job: (job.priority, job.created_at))

    selected = queued_jobs[0]

    if selected.job_id in _queue_job_ids:
        _queue_job_ids.remove(selected.job_id)

    return selected


def queue_length() -> int:
    refresh_queue_from_store()
    return len(_queue_job_ids)


def refresh_queue_from_store() -> None:
    jobs = load_jobs()

    for job_id, job in jobs.items():
        if job.status == JOB_STATUS_QUEUED and job_id not in _queue_job_ids:
            _queue_job_ids.append(job_id)

    stale_ids = [
        job_id
        for job_id in _queue_job_ids
        if job_id not in jobs or jobs[job_id].status != JOB_STATUS_QUEUED
    ]

    for job_id in stale_ids:
        if job_id in _queue_job_ids:
            _queue_job_ids.remove(job_id)


def queue_snapshot() -> Dict[str, object]:
    refresh_queue_from_store()

    jobs = load_jobs()
    queued = [
        jobs[job_id]
        for job_id in _queue_job_ids
        if job_id in jobs and jobs[job_id].status == JOB_STATUS_QUEUED
    ]

    queued.sort(key=lambda job: (job.priority, job.created_at))

    return {
        "queue_length": len(queued),
        "queued_job_ids": [job.job_id for job in queued],
        "queued_jobs": [
            {
                "job_id": job.job_id,
                "workspace_id": job.workspace_id,
                "job_type": job.job_type,
                "priority": job.priority,
                "created_at": job.created_at.isoformat(),
            }
            for job in queued
        ],
    }


def is_job_queued(job_id: str) -> bool:
    refresh_queue_from_store()
    return job_id in _queue_job_ids and get_job(job_id) is not None
