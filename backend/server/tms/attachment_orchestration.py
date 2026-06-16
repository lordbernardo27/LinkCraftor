
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List


ORCH_DIR = Path("backend/server/data/tms")

ATTACHMENT_PROCESSING_QUEUE_PATH = ORCH_DIR / "attachment_processing_jobs.jsonl"
MALWARE_SCAN_QUEUE_PATH = ORCH_DIR / "malware_scan_jobs.jsonl"
ATTACHMENT_CLEANUP_QUEUE_PATH = ORCH_DIR / "attachment_cleanup_jobs.jsonl"
PREVIEW_GENERATION_QUEUE_PATH = ORCH_DIR / "preview_generation_jobs.jsonl"
RETENTION_LIFECYCLE_QUEUE_PATH = ORCH_DIR / "retention_lifecycle_jobs.jsonl"
ATTACHMENT_AUDIT_PATH = ORCH_DIR / "attachment_job_audit.jsonl"
ATTACHMENT_DEAD_LETTER_PATH = ORCH_DIR / "attachment_dead_letter_queue.jsonl"


MAX_ATTACHMENT_RETRY_ATTEMPTS = 3


@dataclass(frozen=True)
class AttachmentJob:
    job_id: str
    job_type: str
    attachment_id: str
    ticket_id: str | None = None
    workspace_id: str | None = None
    file_name: str | None = None
    file_path: str | None = None
    mime_type: str | None = None
    status: str = "queued"
    retry_count: int = 0
    run_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    payload: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class AttachmentAuditEvent:
    event_type: str
    job_id: str
    job_type: str
    attachment_id: str
    status: str
    ticket_id: str | None = None
    workspace_id: str | None = None
    message: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _ensure_attachment_store() -> None:
    ORCH_DIR.mkdir(parents=True, exist_ok=True)

    for path in (
        ATTACHMENT_PROCESSING_QUEUE_PATH,
        MALWARE_SCAN_QUEUE_PATH,
        ATTACHMENT_CLEANUP_QUEUE_PATH,
        PREVIEW_GENERATION_QUEUE_PATH,
        RETENTION_LIFECYCLE_QUEUE_PATH,
        ATTACHMENT_AUDIT_PATH,
        ATTACHMENT_DEAD_LETTER_PATH,
    ):
        if not path.exists():
            path.write_text("", encoding="utf-8")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _job_id(prefix: str, attachment_id: str, job_type: str) -> str:
    timestamp = _utc_now().strftime("%Y%m%d%H%M%S%f")
    safe_attachment = str(attachment_id or "attachment").replace(" ", "_")
    safe_type = str(job_type or "job").replace(" ", "_")
    return f"{prefix}_{safe_attachment}_{safe_type}_{timestamp}"


def log_attachment_audit(event: AttachmentAuditEvent) -> None:
    _ensure_attachment_store()

    with ATTACHMENT_AUDIT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")


def _append_attachment_job(
    path: Path,
    job: AttachmentJob,
    audit_type: str,
    audit_message: str,
) -> None:
    _ensure_attachment_store()

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(job), ensure_ascii=False) + "\n")

    log_attachment_audit(
        AttachmentAuditEvent(
            event_type=audit_type,
            job_id=job.job_id,
            job_type=job.job_type,
            attachment_id=job.attachment_id,
            ticket_id=job.ticket_id,
            workspace_id=job.workspace_id,
            status=job.status,
            message=audit_message,
        )
    )


def enqueue_attachment_processing_job(
    *,
    attachment_id: str,
    ticket_id: str | None = None,
    workspace_id: str | None = None,
    file_name: str | None = None,
    file_path: str | None = None,
    mime_type: str | None = None,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    job = AttachmentJob(
        job_id=_job_id("attachment_job", attachment_id, "process_attachment"),
        job_type="process_attachment",
        attachment_id=attachment_id,
        ticket_id=ticket_id,
        workspace_id=workspace_id,
        file_name=file_name,
        file_path=file_path,
        mime_type=mime_type,
        payload=payload or {},
    )

    _append_attachment_job(
        ATTACHMENT_PROCESSING_QUEUE_PATH,
        job,
        "attachment_processing_job_enqueued",
        "Attachment processing job added to queue.",
    )

    return asdict(job)


def enqueue_malware_scan_job(
    *,
    attachment_id: str,
    ticket_id: str | None = None,
    workspace_id: str | None = None,
    file_name: str | None = None,
    file_path: str | None = None,
    mime_type: str | None = None,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    job = AttachmentJob(
        job_id=_job_id("malware_scan_job", attachment_id, "malware_scan"),
        job_type="malware_scan",
        attachment_id=attachment_id,
        ticket_id=ticket_id,
        workspace_id=workspace_id,
        file_name=file_name,
        file_path=file_path,
        mime_type=mime_type,
        payload=payload or {},
    )

    _append_attachment_job(
        MALWARE_SCAN_QUEUE_PATH,
        job,
        "malware_scan_job_enqueued",
        "Malware scan job added to queue.",
    )

    return asdict(job)


def enqueue_attachment_cleanup_job(
    *,
    attachment_id: str,
    ticket_id: str | None = None,
    workspace_id: str | None = None,
    file_name: str | None = None,
    file_path: str | None = None,
    cleanup_reason: str = "scheduled_cleanup",
    due_in_minutes: int = 0,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    run_at = (_utc_now() + timedelta(minutes=max(0, int(due_in_minutes)))).isoformat()

    job = AttachmentJob(
        job_id=_job_id("attachment_cleanup_job", attachment_id, cleanup_reason),
        job_type="attachment_cleanup",
        attachment_id=attachment_id,
        ticket_id=ticket_id,
        workspace_id=workspace_id,
        file_name=file_name,
        file_path=file_path,
        run_at=run_at,
        payload={
            "cleanup_reason": cleanup_reason,
            "due_in_minutes": due_in_minutes,
            **(payload or {}),
        },
    )

    _append_attachment_job(
        ATTACHMENT_CLEANUP_QUEUE_PATH,
        job,
        "attachment_cleanup_job_enqueued",
        "Attachment cleanup job added to queue.",
    )

    return asdict(job)


def enqueue_preview_generation_job(
    *,
    attachment_id: str,
    ticket_id: str | None = None,
    workspace_id: str | None = None,
    file_name: str | None = None,
    file_path: str | None = None,
    mime_type: str | None = None,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    job = AttachmentJob(
        job_id=_job_id("preview_generation_job", attachment_id, "preview_generation"),
        job_type="preview_generation",
        attachment_id=attachment_id,
        ticket_id=ticket_id,
        workspace_id=workspace_id,
        file_name=file_name,
        file_path=file_path,
        mime_type=mime_type,
        payload=payload or {},
    )

    _append_attachment_job(
        PREVIEW_GENERATION_QUEUE_PATH,
        job,
        "preview_generation_job_enqueued",
        "Preview-generation job added to queue.",
    )

    return asdict(job)


def enqueue_retention_lifecycle_job(
    *,
    attachment_id: str,
    ticket_id: str | None = None,
    workspace_id: str | None = None,
    retention_action: str,
    due_in_minutes: int,
    file_name: str | None = None,
    file_path: str | None = None,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    run_at = (_utc_now() + timedelta(minutes=max(0, int(due_in_minutes)))).isoformat()

    job = AttachmentJob(
        job_id=_job_id("retention_lifecycle_job", attachment_id, retention_action),
        job_type="retention_lifecycle",
        attachment_id=attachment_id,
        ticket_id=ticket_id,
        workspace_id=workspace_id,
        file_name=file_name,
        file_path=file_path,
        run_at=run_at,
        payload={
            "retention_action": retention_action,
            "due_in_minutes": due_in_minutes,
            **(payload or {}),
        },
    )

    _append_attachment_job(
        RETENTION_LIFECYCLE_QUEUE_PATH,
        job,
        "retention_lifecycle_job_enqueued",
        "Lifecycle retention job added to queue.",
    )

    return asdict(job)


def orchestrate_attachment_upload(
    *,
    attachment_id: str,
    ticket_id: str | None = None,
    workspace_id: str | None = None,
    file_name: str | None = None,
    file_path: str | None = None,
    mime_type: str | None = None,
    payload: Dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    jobs = [
        enqueue_attachment_processing_job(
            attachment_id=attachment_id,
            ticket_id=ticket_id,
            workspace_id=workspace_id,
            file_name=file_name,
            file_path=file_path,
            mime_type=mime_type,
            payload=payload,
        ),
        enqueue_malware_scan_job(
            attachment_id=attachment_id,
            ticket_id=ticket_id,
            workspace_id=workspace_id,
            file_name=file_name,
            file_path=file_path,
            mime_type=mime_type,
            payload=payload,
        ),
        enqueue_preview_generation_job(
            attachment_id=attachment_id,
            ticket_id=ticket_id,
            workspace_id=workspace_id,
            file_name=file_name,
            file_path=file_path,
            mime_type=mime_type,
            payload=payload,
        ),
    ]

    return jobs


def should_retry_attachment_job(job: Dict[str, Any]) -> bool:
    retry_count = int(job.get("retry_count") or 0)
    status = str(job.get("status") or "")

    return status in {"failed", "timeout", "temporary_failure"} and retry_count < MAX_ATTACHMENT_RETRY_ATTEMPTS


def build_retry_attachment_job(job: Dict[str, Any]) -> AttachmentJob:
    retry_count = int(job.get("retry_count") or 0) + 1

    return AttachmentJob(
        job_id=str(job.get("job_id")),
        job_type=str(job.get("job_type")),
        attachment_id=str(job.get("attachment_id")),
        ticket_id=job.get("ticket_id"),
        workspace_id=job.get("workspace_id"),
        file_name=job.get("file_name"),
        file_path=job.get("file_path"),
        mime_type=job.get("mime_type"),
        status="queued",
        retry_count=retry_count,
        run_at=str(job.get("run_at") or _utc_now().isoformat()),
        payload=dict(job.get("payload") or {}),
    )


def move_attachment_job_to_dead_letter(
    job: Dict[str, Any],
    reason: str,
) -> None:
    _ensure_attachment_store()

    dead_letter_payload = {
        **job,
        "dead_letter_reason": reason,
        "moved_at": _utc_now().isoformat(),
    }

    with ATTACHMENT_DEAD_LETTER_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(dead_letter_payload, ensure_ascii=False) + "\n")

    log_attachment_audit(
        AttachmentAuditEvent(
            event_type="attachment_job_dead_lettered",
            job_id=str(job.get("job_id")),
            job_type=str(job.get("job_type")),
            attachment_id=str(job.get("attachment_id")),
            ticket_id=job.get("ticket_id"),
            workspace_id=job.get("workspace_id"),
            status="dead_lettered",
            message=reason,
        )
    )


def read_attachment_queue(path: Path, limit: int = 500) -> List[Dict[str, Any]]:
    _ensure_attachment_store()

    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[-limit:] if line.strip()]


def read_attachment_processing_jobs(limit: int = 500) -> List[Dict[str, Any]]:
    return read_attachment_queue(ATTACHMENT_PROCESSING_QUEUE_PATH, limit)


def read_malware_scan_jobs(limit: int = 500) -> List[Dict[str, Any]]:
    return read_attachment_queue(MALWARE_SCAN_QUEUE_PATH, limit)


def read_attachment_cleanup_jobs(limit: int = 500) -> List[Dict[str, Any]]:
    return read_attachment_queue(ATTACHMENT_CLEANUP_QUEUE_PATH, limit)


def read_preview_generation_jobs(limit: int = 500) -> List[Dict[str, Any]]:
    return read_attachment_queue(PREVIEW_GENERATION_QUEUE_PATH, limit)


def read_retention_lifecycle_jobs(limit: int = 500) -> List[Dict[str, Any]]:
    return read_attachment_queue(RETENTION_LIFECYCLE_QUEUE_PATH, limit)


def read_attachment_dead_letter_queue(limit: int = 500) -> List[Dict[str, Any]]:
    return read_attachment_queue(ATTACHMENT_DEAD_LETTER_PATH, limit)
