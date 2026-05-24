from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


JOB_STATUS_PENDING = "pending"
JOB_STATUS_QUEUED = "queued"
JOB_STATUS_RUNNING = "running"
JOB_STATUS_COMPLETED = "completed"
JOB_STATUS_FAILED = "failed"
JOB_STATUS_CANCELLED = "cancelled"

VALID_JOB_STATUSES = {
    JOB_STATUS_PENDING,
    JOB_STATUS_QUEUED,
    JOB_STATUS_RUNNING,
    JOB_STATUS_COMPLETED,
    JOB_STATUS_FAILED,
    JOB_STATUS_CANCELLED,
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class OrchestrationJob:
    job_id: str
    workspace_id: str
    job_type: str
    status: str = JOB_STATUS_QUEUED
    priority: int = 5
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    assigned_worker_id: Optional[str] = None
    progress_percent: float = 0.0
    current_step: str = ""
    total_steps: int = 0
    processed_count: int = 0
    failed_count: int = 0
    warning_count: int = 0

    total_documents: int = 0
    processed_documents: int = 0
    failed_documents: int = 0
    skipped_documents: int = 0

    current_document_id: str = ""
    current_document_name: str = ""

    progress_message: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class JobStep:
    step_id: str
    job_id: str
    step_name: str

    status: str = JOB_STATUS_PENDING
    progress_percent: float = 0.0

    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class JobStatusEvent:
    event_id: str
    job_id: str
    old_status: str
    new_status: str
    created_at: datetime = field(default_factory=utc_now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class JobWorkerAssignment:
    assignment_id: str
    job_id: str
    worker_id: str
    assigned_at: datetime = field(default_factory=utc_now)
    released_at: Optional[datetime] = None


@dataclass
class JobResult:
    result_id: str
    job_id: str
    success: bool = True
    output: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utc_now)


@dataclass
class QueueStats:
    total_jobs: int = 0
    queued_jobs: int = 0
    running_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0


@dataclass
class WorkerHeartbeat:
    worker_id: str
    last_seen_at: datetime = field(default_factory=utc_now)
    status: str = "online"
    metadata: Dict[str, Any] = field(default_factory=dict)



