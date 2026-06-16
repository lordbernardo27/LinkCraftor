
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ORCH_DIR = Path("backend/server/data/tms")
TICKET_JOB_QUEUE_PATH = ORCH_DIR / "ticket_job_queue.jsonl"
TICKET_DEAD_LETTER_PATH = ORCH_DIR / "ticket_dead_letter_queue.jsonl"
TICKET_JOB_AUDIT_PATH = ORCH_DIR / "ticket_job_audit.jsonl"


MAX_RETRY_ATTEMPTS = 3


@dataclass(frozen=True)
class TicketJob:
    job_id: str
    job_type: str
    ticket_id: str
    workspace_id: str | None = None
    status: str = "queued"
    retry_count: int = 0
    payload: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass(frozen=True)
class TicketJobAuditEvent:
    event_type: str
    job_id: str
    job_type: str
    ticket_id: str
    status: str
    workspace_id: str | None = None
    message: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def _ensure_orchestration_store() -> None:
    ORCH_DIR.mkdir(parents=True, exist_ok=True)

    for path in (TICKET_JOB_QUEUE_PATH, TICKET_DEAD_LETTER_PATH, TICKET_JOB_AUDIT_PATH):
        if not path.exists():
            path.write_text("", encoding="utf-8")


def enqueue_ticket_job(job: TicketJob) -> None:
    _ensure_orchestration_store()

    with TICKET_JOB_QUEUE_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(job), ensure_ascii=False) + "\n")

    log_ticket_job_audit(
        TicketJobAuditEvent(
            event_type="ticket_job_enqueued",
            job_id=job.job_id,
            job_type=job.job_type,
            ticket_id=job.ticket_id,
            workspace_id=job.workspace_id,
            status=job.status,
            message="Ticket job added to queue.",
        )
    )


def log_ticket_job_audit(event: TicketJobAuditEvent) -> None:
    _ensure_orchestration_store()

    with TICKET_JOB_AUDIT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")


def build_ticket_processing_job(
    job_type: str,
    ticket_id: str,
    workspace_id: str | None = None,
    payload: Dict[str, Any] | None = None,
) -> TicketJob:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    job_id = f"ticket_job_{ticket_id}_{job_type}_{timestamp}"

    return TicketJob(
        job_id=job_id,
        job_type=job_type,
        ticket_id=ticket_id,
        workspace_id=workspace_id,
        payload=payload or {},
    )


def orchestrate_ticket_workflow(
    ticket: Dict[str, Any],
    workflow_type: str,
) -> List[Dict[str, Any]]:
    ticket_id = str(ticket.get("id") or ticket.get("ticket_id") or "unknown")
    workspace_id = ticket.get("workspace_id") or ticket.get("workspace")

    jobs: List[TicketJob] = []

    if workflow_type == "ticket_created":
        jobs.extend(
            [
                build_ticket_processing_job("classify_ticket", ticket_id, workspace_id, ticket),
                build_ticket_processing_job("build_product_context", ticket_id, workspace_id, ticket),
                build_ticket_processing_job("schedule_sla_timers", ticket_id, workspace_id, ticket),
            ]
        )

    elif workflow_type == "ticket_updated":
        jobs.extend(
            [
                build_ticket_processing_job("recalculate_priority", ticket_id, workspace_id, ticket),
                build_ticket_processing_job("audit_state_transition", ticket_id, workspace_id, ticket),
            ]
        )

    elif workflow_type == "ticket_escalated":
        jobs.extend(
            [
                build_ticket_processing_job("route_escalation", ticket_id, workspace_id, ticket),
                build_ticket_processing_job("notify_escalation_targets", ticket_id, workspace_id, ticket),
            ]
        )

    else:
        jobs.append(
            build_ticket_processing_job("generic_ticket_workflow", ticket_id, workspace_id, ticket)
        )

    for job in jobs:
        enqueue_ticket_job(job)

    return [asdict(job) for job in jobs]


def build_ticket_state_transition_job(
    ticket_id: str,
    previous_status: str,
    new_status: str,
    workspace_id: str | None = None,
    actor_id: str | None = None,
) -> TicketJob:
    return build_ticket_processing_job(
        job_type="ticket_state_transition",
        ticket_id=ticket_id,
        workspace_id=workspace_id,
        payload={
            "previous_status": previous_status,
            "new_status": new_status,
            "actor_id": actor_id,
        },
    )


def should_retry_ticket_job(job: Dict[str, Any]) -> bool:
    retry_count = int(job.get("retry_count") or 0)
    status = str(job.get("status") or "")

    return status in {"failed", "timeout", "temporary_failure"} and retry_count < MAX_RETRY_ATTEMPTS


def build_retry_ticket_job(job: Dict[str, Any]) -> TicketJob:
    retry_count = int(job.get("retry_count") or 0) + 1

    return TicketJob(
        job_id=str(job.get("job_id")),
        job_type=str(job.get("job_type")),
        ticket_id=str(job.get("ticket_id")),
        workspace_id=job.get("workspace_id"),
        status="queued",
        retry_count=retry_count,
        payload=dict(job.get("payload") or {}),
    )


def move_ticket_job_to_dead_letter(
    job: Dict[str, Any],
    reason: str,
) -> None:
    _ensure_orchestration_store()

    dead_letter_payload = {
        **job,
        "dead_letter_reason": reason,
        "moved_at": datetime.now(timezone.utc).isoformat(),
    }

    with TICKET_DEAD_LETTER_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(dead_letter_payload, ensure_ascii=False) + "\n")

    log_ticket_job_audit(
        TicketJobAuditEvent(
            event_type="ticket_job_dead_lettered",
            job_id=str(job.get("job_id")),
            job_type=str(job.get("job_type")),
            ticket_id=str(job.get("ticket_id")),
            workspace_id=job.get("workspace_id"),
            status="dead_lettered",
            message=reason,
        )
    )


def read_ticket_job_queue(limit: int = 500) -> List[Dict[str, Any]]:
    _ensure_orchestration_store()

    lines = TICKET_JOB_QUEUE_PATH.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[-limit:] if line.strip()]


def read_ticket_dead_letter_queue(limit: int = 500) -> List[Dict[str, Any]]:
    _ensure_orchestration_store()

    lines = TICKET_DEAD_LETTER_PATH.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[-limit:] if line.strip()]
