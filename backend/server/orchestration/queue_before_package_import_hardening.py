# backend/server/orchestration/queue.py
from __future__ import annotations

import os
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Iterator, List, Optional

from .job_store import get_job, load_jobs, update_job_status
from .models import JOB_STATUS_QUEUED, JOB_STATUS_RUNNING, OrchestrationJob

# ---------------------------------------------------------------------------
# Design notes (what changed and why)
#
# The previous implementation kept a module-level list (_queue_job_ids) that
# was rebuilt from the job store on every call via refresh_queue_from_store().
# Because the store was always authoritative, the list carried no information
# of its own — but it created two real problems:
#
#   1. NON-ATOMIC DEQUEUE: dequeue_job() removed a job from the local list
#      while its status in the store remained "queued" until the worker later
#      called mark_job_running(). Any concurrent worker (thread OR separate
#      process) refreshing from the store in that window would re-discover the
#      job and dequeue it again -> duplicate processing.
#
#   2. STATE DRIFT: two sources of truth that had to be defended against each
#      other in multiple places (dead "clear()" branch, redundant existence
#      checks, 2-3 load_jobs() calls per operation).
#
# This version deletes the in-memory list entirely. The job store IS the
# queue: a job is "queued" iff its persisted status is JOB_STATUS_QUEUED.
# dequeue_job() now CLAIMS the job atomically — it transitions the job to
# JOB_STATUS_RUNNING inside a cross-process lock before returning it — so a
# job can be handed to exactly one worker. This also means the queue trivially
# survives process restarts: anything persisted as "queued" is picked up.
#
# Ordering is unchanged: ascending (priority, created_at) — i.e. LOWER
# priority number is served first, ties broken oldest-first (FIFO). job_id is
# appended as a final tie-breaker so ordering is fully deterministic.
# ---------------------------------------------------------------------------

# Cross-process lock file guarding the dequeue critical section
# (read store -> pick job -> flip status). Lives next to this module by
# default; override with ORCHESTRATION_QUEUE_LOCK_PATH if the package
# directory is read-only in your deployment.
_LOCK_PATH = Path(
    os.environ.get(
        "ORCHESTRATION_QUEUE_LOCK_PATH",
        str(Path(__file__).resolve().parent / ".queue.lock"),
    )
)

# In-process lock: cheaper than the file lock for threads within one process,
# and required anyway because fcntl/msvcrt locks are per-process, not
# per-thread.
_thread_lock = threading.Lock()

try:
    import fcntl  # POSIX

    def _flock(fh) -> None:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)

    def _funlock(fh) -> None:
        fcntl.flock(fh.fileno(), fcntl.LOCK_UN)

except ImportError:  # Windows
    import msvcrt

    def _flock(fh) -> None:
        msvcrt.locking(fh.fileno(), msvcrt.LK_LOCK, 1)

    def _funlock(fh) -> None:
        fh.seek(0)
        msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)


@contextmanager
def _dequeue_lock() -> Iterator[None]:
    """Serialize the select-and-claim critical section across threads and
    processes on this machine."""
    with _thread_lock:
        _LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(_LOCK_PATH, "a+") as fh:
            _flock(fh)
            try:
                yield
            finally:
                _funlock(fh)


def _sort_key(job: OrchestrationJob):
    return (job.priority, job.created_at, job.job_id)


def _queued_jobs(jobs: Optional[Dict[str, OrchestrationJob]] = None) -> List[OrchestrationJob]:
    """All jobs currently persisted as queued, in service order."""
    if jobs is None:
        jobs = load_jobs()
    queued = [job for job in jobs.values() if job.status == JOB_STATUS_QUEUED]
    queued.sort(key=_sort_key)
    return queued


def enqueue_job(job_id: str) -> bool:
    """Kept for API compatibility.

    Enqueueing is now implicit: create_job persists the job with status
    JOB_STATUS_QUEUED, and that persisted status is the queue membership.
    This function only verifies the job actually exists in a queued state,
    which catches caller bugs (e.g. enqueueing an ID that was never created).
    """
    job = get_job(job_id)
    return job is not None and job.status == JOB_STATUS_QUEUED


def dequeue_job(worker_id: str | None = None) -> Optional[OrchestrationJob]:
    """Atomically claim and return the highest-priority queued job.

    The returned job has ALREADY been transitioned to JOB_STATUS_RUNNING
    (with claim metadata) under a cross-process lock, so no other worker
    can receive the same job. Returns None when nothing is queued.

    Workers may still call mark_job_running() afterwards; with the
    corrected service.py that call is idempotent.
    """
    with _dequeue_lock():
        for candidate in _queued_jobs():
            metadata: Dict[str, object] = {"claimed_by_dequeue": True}
            if worker_id:
                metadata["worker_id"] = worker_id
            try:
                claimed = update_job_status(
                    candidate.job_id,
                    JOB_STATUS_RUNNING,
                    metadata=metadata,
                )
            except Exception:
                # Job vanished or store hiccuped between read and write —
                # skip it and try the next candidate rather than failing
                # the whole dequeue.
                continue
            return claimed
        return None


def queue_length() -> int:
    return len(_queued_jobs())


def refresh_queue_from_store() -> None:
    """Kept for API compatibility.

    There is no longer any in-memory queue state to refresh — every read
    goes straight to the job store — so this is a no-op.
    """
    return None


def queue_snapshot() -> Dict[str, object]:
    queued = _queued_jobs()

    return {
        "queue_length": len(queued),
        "queued_job_ids": [job.job_id for job in queued],
        "queued_jobs": [
            {
                "job_id": job.job_id,
                "workspace_id": job.workspace_id,
                "job_type": job.job_type,
                "priority": job.priority,
                "created_at": (
                    job.created_at.isoformat()
                    if hasattr(job.created_at, "isoformat")
                    else str(job.created_at)
                ),
            }
            for job in queued
        ],
    }


def is_job_queued(job_id: str) -> bool:
    job = get_job(job_id)
    return job is not None and job.status == JOB_STATUS_QUEUED