
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ORCH_DIR = Path("backend/server/data/tms")

SUPPORT_INTELLIGENCE_QUEUE_PATH = ORCH_DIR / "support_intelligence_jobs.jsonl"
CONTEXT_AGGREGATION_QUEUE_PATH = ORCH_DIR / "context_aggregation_jobs.jsonl"
CHURN_RISK_QUEUE_PATH = ORCH_DIR / "churn_risk_analysis_jobs.jsonl"
INCIDENT_DETECTION_QUEUE_PATH = ORCH_DIR / "incident_detection_jobs.jsonl"
ANALYTICS_AGGREGATION_QUEUE_PATH = ORCH_DIR / "analytics_aggregation_jobs.jsonl"
INTELLIGENCE_AUDIT_PATH = ORCH_DIR / "intelligence_job_audit.jsonl"
INTELLIGENCE_DEAD_LETTER_PATH = ORCH_DIR / "intelligence_dead_letter_queue.jsonl"


MAX_INTELLIGENCE_RETRY_ATTEMPTS = 3


@dataclass(frozen=True)
class IntelligenceJob:
    job_id: str
    job_type: str
    scope: str = "ticket"
    ticket_id: str | None = None
    workspace_id: str | None = None
    customer_id: str | None = None
    status: str = "queued"
    retry_count: int = 0
    payload: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class IntelligenceAuditEvent:
    event_type: str
    job_id: str
    job_type: str
    status: str
    scope: str = "ticket"
    ticket_id: str | None = None
    workspace_id: str | None = None
    customer_id: str | None = None
    message: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _ensure_intelligence_store() -> None:
    ORCH_DIR.mkdir(parents=True, exist_ok=True)

    for path in (
        SUPPORT_INTELLIGENCE_QUEUE_PATH,
        CONTEXT_AGGREGATION_QUEUE_PATH,
        CHURN_RISK_QUEUE_PATH,
        INCIDENT_DETECTION_QUEUE_PATH,
        ANALYTICS_AGGREGATION_QUEUE_PATH,
        INTELLIGENCE_AUDIT_PATH,
        INTELLIGENCE_DEAD_LETTER_PATH,
    ):
        if not path.exists():
            path.write_text("", encoding="utf-8")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _job_id(prefix: str, scope_id: str | None, job_type: str) -> str:
    timestamp = _utc_now().strftime("%Y%m%d%H%M%S%f")
    safe_scope = str(scope_id or "global").replace(" ", "_")
    safe_type = str(job_type or "job").replace(" ", "_")
    return f"{prefix}_{safe_scope}_{safe_type}_{timestamp}"


def log_intelligence_audit(event: IntelligenceAuditEvent) -> None:
    _ensure_intelligence_store()

    with INTELLIGENCE_AUDIT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")


def _append_intelligence_job(
    path: Path,
    job: IntelligenceJob,
    audit_type: str,
    audit_message: str,
) -> None:
    _ensure_intelligence_store()

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(job), ensure_ascii=False) + "\n")

    log_intelligence_audit(
        IntelligenceAuditEvent(
            event_type=audit_type,
            job_id=job.job_id,
            job_type=job.job_type,
            status=job.status,
            scope=job.scope,
            ticket_id=job.ticket_id,
            workspace_id=job.workspace_id,
            customer_id=job.customer_id,
            message=audit_message,
        )
    )


def enqueue_support_intelligence_job(
    *,
    ticket_id: str,
    workspace_id: str | None = None,
    customer_id: str | None = None,
    intelligence_type: str = "support_summary",
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    job = IntelligenceJob(
        job_id=_job_id("support_intelligence_job", ticket_id, intelligence_type),
        job_type="support_intelligence",
        scope="ticket",
        ticket_id=ticket_id,
        workspace_id=workspace_id,
        customer_id=customer_id,
        payload={
            "intelligence_type": intelligence_type,
            **(payload or {}),
        },
    )

    _append_intelligence_job(
        SUPPORT_INTELLIGENCE_QUEUE_PATH,
        job,
        "support_intelligence_job_enqueued",
        "Support intelligence job added to queue.",
    )

    return asdict(job)


def enqueue_context_aggregation_job(
    *,
    ticket_id: str,
    workspace_id: str | None = None,
    customer_id: str | None = None,
    context_sources: List[str] | None = None,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    job = IntelligenceJob(
        job_id=_job_id("context_aggregation_job", ticket_id, "context_aggregation"),
        job_type="context_aggregation",
        scope="ticket",
        ticket_id=ticket_id,
        workspace_id=workspace_id,
        customer_id=customer_id,
        payload={
            "context_sources": context_sources or [],
            **(payload or {}),
        },
    )

    _append_intelligence_job(
        CONTEXT_AGGREGATION_QUEUE_PATH,
        job,
        "context_aggregation_job_enqueued",
        "Context aggregation job added to queue.",
    )

    return asdict(job)


def enqueue_churn_risk_analysis_job(
    *,
    customer_id: str,
    workspace_id: str | None = None,
    ticket_id: str | None = None,
    risk_window_days: int = 30,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    job = IntelligenceJob(
        job_id=_job_id("churn_risk_job", customer_id, "churn_risk_analysis"),
        job_type="churn_risk_analysis",
        scope="customer",
        ticket_id=ticket_id,
        workspace_id=workspace_id,
        customer_id=customer_id,
        payload={
            "risk_window_days": risk_window_days,
            **(payload or {}),
        },
    )

    _append_intelligence_job(
        CHURN_RISK_QUEUE_PATH,
        job,
        "churn_risk_analysis_job_enqueued",
        "Churn-risk analysis job added to queue.",
    )

    return asdict(job)


def enqueue_incident_detection_job(
    *,
    workspace_id: str | None = None,
    ticket_id: str | None = None,
    signal_type: str = "support_pattern",
    severity_hint: str | None = None,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    scope_id = ticket_id or workspace_id or "global"

    job = IntelligenceJob(
        job_id=_job_id("incident_detection_job", scope_id, signal_type),
        job_type="incident_detection",
        scope="workspace" if workspace_id else "global",
        ticket_id=ticket_id,
        workspace_id=workspace_id,
        payload={
            "signal_type": signal_type,
            "severity_hint": severity_hint,
            **(payload or {}),
        },
    )

    _append_intelligence_job(
        INCIDENT_DETECTION_QUEUE_PATH,
        job,
        "incident_detection_job_enqueued",
        "Incident-detection job added to queue.",
    )

    return asdict(job)


def enqueue_analytics_aggregation_job(
    *,
    workspace_id: str | None = None,
    aggregation_type: str = "support_metrics",
    period: str = "daily",
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    scope_id = workspace_id or "global"

    job = IntelligenceJob(
        job_id=_job_id("analytics_aggregation_job", scope_id, aggregation_type),
        job_type="analytics_aggregation",
        scope="workspace" if workspace_id else "global",
        workspace_id=workspace_id,
        payload={
            "aggregation_type": aggregation_type,
            "period": period,
            **(payload or {}),
        },
    )

    _append_intelligence_job(
        ANALYTICS_AGGREGATION_QUEUE_PATH,
        job,
        "analytics_aggregation_job_enqueued",
        "Analytics aggregation job added to queue.",
    )

    return asdict(job)


def orchestrate_ticket_intelligence(
    *,
    ticket_id: str,
    workspace_id: str | None = None,
    customer_id: str | None = None,
    ticket_payload: Dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    jobs = [
        enqueue_context_aggregation_job(
            ticket_id=ticket_id,
            workspace_id=workspace_id,
            customer_id=customer_id,
            context_sources=[
                "ticket_history",
                "product_activity",
                "billing_context",
                "workspace_context",
            ],
            payload=ticket_payload,
        ),
        enqueue_support_intelligence_job(
            ticket_id=ticket_id,
            workspace_id=workspace_id,
            customer_id=customer_id,
            intelligence_type="ticket_summary_and_recommendations",
            payload=ticket_payload,
        ),
        enqueue_incident_detection_job(
            workspace_id=workspace_id,
            ticket_id=ticket_id,
            signal_type="ticket_pattern_signal",
            payload=ticket_payload,
        ),
    ]

    if customer_id:
        jobs.append(
            enqueue_churn_risk_analysis_job(
                customer_id=customer_id,
                workspace_id=workspace_id,
                ticket_id=ticket_id,
                risk_window_days=30,
                payload=ticket_payload,
            )
        )

    return jobs


def should_retry_intelligence_job(job: Dict[str, Any]) -> bool:
    retry_count = int(job.get("retry_count") or 0)
    status = str(job.get("status") or "")

    return status in {"failed", "timeout", "temporary_failure"} and retry_count < MAX_INTELLIGENCE_RETRY_ATTEMPTS


def build_retry_intelligence_job(job: Dict[str, Any]) -> IntelligenceJob:
    retry_count = int(job.get("retry_count") or 0) + 1

    return IntelligenceJob(
        job_id=str(job.get("job_id")),
        job_type=str(job.get("job_type")),
        scope=str(job.get("scope") or "ticket"),
        ticket_id=job.get("ticket_id"),
        workspace_id=job.get("workspace_id"),
        customer_id=job.get("customer_id"),
        status="queued",
        retry_count=retry_count,
        payload=dict(job.get("payload") or {}),
    )


def move_intelligence_job_to_dead_letter(
    job: Dict[str, Any],
    reason: str,
) -> None:
    _ensure_intelligence_store()

    dead_letter_payload = {
        **job,
        "dead_letter_reason": reason,
        "moved_at": _utc_now().isoformat(),
    }

    with INTELLIGENCE_DEAD_LETTER_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(dead_letter_payload, ensure_ascii=False) + "\n")

    log_intelligence_audit(
        IntelligenceAuditEvent(
            event_type="intelligence_job_dead_lettered",
            job_id=str(job.get("job_id")),
            job_type=str(job.get("job_type")),
            status="dead_lettered",
            scope=str(job.get("scope") or "ticket"),
            ticket_id=job.get("ticket_id"),
            workspace_id=job.get("workspace_id"),
            customer_id=job.get("customer_id"),
            message=reason,
        )
    )


def read_intelligence_queue(path: Path, limit: int = 500) -> List[Dict[str, Any]]:
    _ensure_intelligence_store()

    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[-limit:] if line.strip()]


def read_support_intelligence_jobs(limit: int = 500) -> List[Dict[str, Any]]:
    return read_intelligence_queue(SUPPORT_INTELLIGENCE_QUEUE_PATH, limit)


def read_context_aggregation_jobs(limit: int = 500) -> List[Dict[str, Any]]:
    return read_intelligence_queue(CONTEXT_AGGREGATION_QUEUE_PATH, limit)


def read_churn_risk_analysis_jobs(limit: int = 500) -> List[Dict[str, Any]]:
    return read_intelligence_queue(CHURN_RISK_QUEUE_PATH, limit)


def read_incident_detection_jobs(limit: int = 500) -> List[Dict[str, Any]]:
    return read_intelligence_queue(INCIDENT_DETECTION_QUEUE_PATH, limit)


def read_analytics_aggregation_jobs(limit: int = 500) -> List[Dict[str, Any]]:
    return read_intelligence_queue(ANALYTICS_AGGREGATION_QUEUE_PATH, limit)


def read_intelligence_dead_letter_queue(limit: int = 500) -> List[Dict[str, Any]]:
    return read_intelligence_queue(INTELLIGENCE_DEAD_LETTER_PATH, limit)
