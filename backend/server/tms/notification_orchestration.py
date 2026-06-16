
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List


ORCH_DIR = Path("backend/server/data/tms")

OUTBOUND_EMAIL_QUEUE_PATH = ORCH_DIR / "outbound_email_jobs.jsonl"
NOTIFICATION_QUEUE_PATH = ORCH_DIR / "notification_dispatch_queue.jsonl"
SLA_TIMER_QUEUE_PATH = ORCH_DIR / "sla_timer_jobs.jsonl"
ESCALATION_TIMER_QUEUE_PATH = ORCH_DIR / "escalation_timer_jobs.jsonl"
FOLLOW_UP_QUEUE_PATH = ORCH_DIR / "delayed_follow_up_jobs.jsonl"
NOTIFICATION_AUDIT_PATH = ORCH_DIR / "notification_job_audit.jsonl"
NOTIFICATION_DEAD_LETTER_PATH = ORCH_DIR / "notification_dead_letter_queue.jsonl"


MAX_NOTIFICATION_RETRY_ATTEMPTS = 3


@dataclass(frozen=True)
class NotificationJob:
    job_id: str
    job_type: str
    ticket_id: str | None = None
    workspace_id: str | None = None
    channel: str = "in_app"
    recipient: str | None = None
    subject: str | None = None
    message: str | None = None
    status: str = "queued"
    retry_count: int = 0
    run_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    payload: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class NotificationAuditEvent:
    event_type: str
    job_id: str
    job_type: str
    status: str
    ticket_id: str | None = None
    workspace_id: str | None = None
    message: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _ensure_notification_store() -> None:
    ORCH_DIR.mkdir(parents=True, exist_ok=True)

    for path in (
        OUTBOUND_EMAIL_QUEUE_PATH,
        NOTIFICATION_QUEUE_PATH,
        SLA_TIMER_QUEUE_PATH,
        ESCALATION_TIMER_QUEUE_PATH,
        FOLLOW_UP_QUEUE_PATH,
        NOTIFICATION_AUDIT_PATH,
        NOTIFICATION_DEAD_LETTER_PATH,
    ):
        if not path.exists():
            path.write_text("", encoding="utf-8")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _job_id(prefix: str, ticket_id: str | None, job_type: str) -> str:
    timestamp = _utc_now().strftime("%Y%m%d%H%M%S%f")
    safe_ticket = str(ticket_id or "general").replace(" ", "_")
    safe_type = str(job_type or "job").replace(" ", "_")
    return f"{prefix}_{safe_ticket}_{safe_type}_{timestamp}"


def log_notification_audit(event: NotificationAuditEvent) -> None:
    _ensure_notification_store()

    with NOTIFICATION_AUDIT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")


def _append_job(path: Path, job: NotificationJob, audit_type: str, audit_message: str) -> None:
    _ensure_notification_store()

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(job), ensure_ascii=False) + "\n")

    log_notification_audit(
        NotificationAuditEvent(
            event_type=audit_type,
            job_id=job.job_id,
            job_type=job.job_type,
            ticket_id=job.ticket_id,
            workspace_id=job.workspace_id,
            status=job.status,
            message=audit_message,
        )
    )


def enqueue_outbound_email_job(
    *,
    ticket_id: str | None = None,
    workspace_id: str | None = None,
    recipient: str,
    subject: str,
    body: str,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    job = NotificationJob(
        job_id=_job_id("email_job", ticket_id, "outbound_email"),
        job_type="outbound_email",
        ticket_id=ticket_id,
        workspace_id=workspace_id,
        channel="email",
        recipient=recipient,
        subject=subject,
        message=body,
        payload=payload or {},
    )

    _append_job(
        OUTBOUND_EMAIL_QUEUE_PATH,
        job,
        "outbound_email_job_enqueued",
        "Async outbound email job added to queue.",
    )

    return asdict(job)


def enqueue_notification_dispatch_job(
    *,
    ticket_id: str | None = None,
    workspace_id: str | None = None,
    channel: str = "in_app",
    recipient: str | None = None,
    message: str,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    job = NotificationJob(
        job_id=_job_id("notification_job", ticket_id, "dispatch"),
        job_type="notification_dispatch",
        ticket_id=ticket_id,
        workspace_id=workspace_id,
        channel=channel,
        recipient=recipient,
        message=message,
        payload=payload or {},
    )

    _append_job(
        NOTIFICATION_QUEUE_PATH,
        job,
        "notification_dispatch_job_enqueued",
        "Notification dispatch job added to queue.",
    )

    return asdict(job)


def enqueue_sla_timer_job(
    *,
    ticket_id: str,
    workspace_id: str | None = None,
    sla_type: str,
    due_in_minutes: int,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    run_at = (_utc_now() + timedelta(minutes=max(0, int(due_in_minutes)))).isoformat()

    job = NotificationJob(
        job_id=_job_id("sla_timer_job", ticket_id, sla_type),
        job_type="sla_timer",
        ticket_id=ticket_id,
        workspace_id=workspace_id,
        channel="system",
        run_at=run_at,
        payload={
            "sla_type": sla_type,
            "due_in_minutes": due_in_minutes,
            **(payload or {}),
        },
    )

    _append_job(
        SLA_TIMER_QUEUE_PATH,
        job,
        "sla_timer_job_enqueued",
        "SLA timer job added to queue.",
    )

    return asdict(job)


def enqueue_escalation_timer_job(
    *,
    ticket_id: str,
    workspace_id: str | None = None,
    escalation_level: str,
    due_in_minutes: int,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    run_at = (_utc_now() + timedelta(minutes=max(0, int(due_in_minutes)))).isoformat()

    job = NotificationJob(
        job_id=_job_id("escalation_timer_job", ticket_id, escalation_level),
        job_type="escalation_timer",
        ticket_id=ticket_id,
        workspace_id=workspace_id,
        channel="system",
        run_at=run_at,
        payload={
            "escalation_level": escalation_level,
            "due_in_minutes": due_in_minutes,
            **(payload or {}),
        },
    )

    _append_job(
        ESCALATION_TIMER_QUEUE_PATH,
        job,
        "escalation_timer_job_enqueued",
        "Escalation timer job added to queue.",
    )

    return asdict(job)


def enqueue_delayed_follow_up_job(
    *,
    ticket_id: str,
    workspace_id: str | None = None,
    recipient: str | None = None,
    message: str,
    due_in_minutes: int,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    run_at = (_utc_now() + timedelta(minutes=max(0, int(due_in_minutes)))).isoformat()

    job = NotificationJob(
        job_id=_job_id("follow_up_job", ticket_id, "delayed_follow_up"),
        job_type="delayed_follow_up",
        ticket_id=ticket_id,
        workspace_id=workspace_id,
        channel="email" if recipient else "in_app",
        recipient=recipient,
        message=message,
        run_at=run_at,
        payload=payload or {},
    )

    _append_job(
        FOLLOW_UP_QUEUE_PATH,
        job,
        "delayed_follow_up_job_enqueued",
        "Delayed follow-up job added to queue.",
    )

    return asdict(job)


def should_retry_notification_job(job: Dict[str, Any]) -> bool:
    retry_count = int(job.get("retry_count") or 0)
    status = str(job.get("status") or "")

    return status in {"failed", "timeout", "temporary_failure"} and retry_count < MAX_NOTIFICATION_RETRY_ATTEMPTS


def build_retry_notification_job(job: Dict[str, Any]) -> NotificationJob:
    retry_count = int(job.get("retry_count") or 0) + 1

    return NotificationJob(
        job_id=str(job.get("job_id")),
        job_type=str(job.get("job_type")),
        ticket_id=job.get("ticket_id"),
        workspace_id=job.get("workspace_id"),
        channel=str(job.get("channel") or "in_app"),
        recipient=job.get("recipient"),
        subject=job.get("subject"),
        message=job.get("message"),
        status="queued",
        retry_count=retry_count,
        run_at=str(job.get("run_at") or _utc_now().isoformat()),
        payload=dict(job.get("payload") or {}),
    )


def move_notification_job_to_dead_letter(
    job: Dict[str, Any],
    reason: str,
) -> None:
    _ensure_notification_store()

    dead_letter_payload = {
        **job,
        "dead_letter_reason": reason,
        "moved_at": _utc_now().isoformat(),
    }

    with NOTIFICATION_DEAD_LETTER_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(dead_letter_payload, ensure_ascii=False) + "\n")

    log_notification_audit(
        NotificationAuditEvent(
            event_type="notification_job_dead_lettered",
            job_id=str(job.get("job_id")),
            job_type=str(job.get("job_type")),
            ticket_id=job.get("ticket_id"),
            workspace_id=job.get("workspace_id"),
            status="dead_lettered",
            message=reason,
        )
    )


def read_notification_queue(path: Path, limit: int = 500) -> List[Dict[str, Any]]:
    _ensure_notification_store()

    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[-limit:] if line.strip()]


def read_outbound_email_jobs(limit: int = 500) -> List[Dict[str, Any]]:
    return read_notification_queue(OUTBOUND_EMAIL_QUEUE_PATH, limit)


def read_notification_dispatch_jobs(limit: int = 500) -> List[Dict[str, Any]]:
    return read_notification_queue(NOTIFICATION_QUEUE_PATH, limit)


def read_sla_timer_jobs(limit: int = 500) -> List[Dict[str, Any]]:
    return read_notification_queue(SLA_TIMER_QUEUE_PATH, limit)


def read_escalation_timer_jobs(limit: int = 500) -> List[Dict[str, Any]]:
    return read_notification_queue(ESCALATION_TIMER_QUEUE_PATH, limit)


def read_delayed_follow_up_jobs(limit: int = 500) -> List[Dict[str, Any]]:
    return read_notification_queue(FOLLOW_UP_QUEUE_PATH, limit)


def read_notification_dead_letter_queue(limit: int = 500) -> List[Dict[str, Any]]:
    return read_notification_queue(NOTIFICATION_DEAD_LETTER_PATH, limit)
