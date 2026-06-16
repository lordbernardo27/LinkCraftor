
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ORCH_DIR = Path("backend/server/data/tms")

GOVERNANCE_AUDIT_PATH = ORCH_DIR / "orchestration_governance_audit.jsonl"
QUEUE_HEALTH_PATH = ORCH_DIR / "queue_health_snapshots.jsonl"
WORKER_STATUS_PATH = ORCH_DIR / "worker_status_snapshots.jsonl"
ORCHESTRATION_METRICS_PATH = ORCH_DIR / "orchestration_metrics.jsonl"
FAILED_JOB_RECOVERY_PATH = ORCH_DIR / "failed_job_recovery_actions.jsonl"


QUEUE_PATHS = {
    "ticket_jobs": ORCH_DIR / "ticket_job_queue.jsonl",
    "ticket_dead_letter": ORCH_DIR / "ticket_dead_letter_queue.jsonl",
    "outbound_email_jobs": ORCH_DIR / "outbound_email_jobs.jsonl",
    "notification_dispatch": ORCH_DIR / "notification_dispatch_queue.jsonl",
    "sla_timer_jobs": ORCH_DIR / "sla_timer_jobs.jsonl",
    "escalation_timer_jobs": ORCH_DIR / "escalation_timer_jobs.jsonl",
    "delayed_follow_up_jobs": ORCH_DIR / "delayed_follow_up_jobs.jsonl",
    "notification_dead_letter": ORCH_DIR / "notification_dead_letter_queue.jsonl",
    "attachment_processing": ORCH_DIR / "attachment_processing_jobs.jsonl",
    "malware_scan_jobs": ORCH_DIR / "malware_scan_jobs.jsonl",
    "attachment_cleanup_jobs": ORCH_DIR / "attachment_cleanup_jobs.jsonl",
    "preview_generation_jobs": ORCH_DIR / "preview_generation_jobs.jsonl",
    "retention_lifecycle_jobs": ORCH_DIR / "retention_lifecycle_jobs.jsonl",
    "attachment_dead_letter": ORCH_DIR / "attachment_dead_letter_queue.jsonl",
    "support_intelligence_jobs": ORCH_DIR / "support_intelligence_jobs.jsonl",
    "context_aggregation_jobs": ORCH_DIR / "context_aggregation_jobs.jsonl",
    "churn_risk_analysis_jobs": ORCH_DIR / "churn_risk_analysis_jobs.jsonl",
    "incident_detection_jobs": ORCH_DIR / "incident_detection_jobs.jsonl",
    "analytics_aggregation_jobs": ORCH_DIR / "analytics_aggregation_jobs.jsonl",
    "intelligence_dead_letter": ORCH_DIR / "intelligence_dead_letter_queue.jsonl",
}


@dataclass(frozen=True)
class GovernanceAuditEvent:
    event_type: str
    status: str = "recorded"
    queue_name: str | None = None
    worker_id: str | None = None
    job_id: str | None = None
    message: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class WorkerStatus:
    worker_id: str
    worker_type: str
    status: str
    current_job_id: str | None = None
    queue_name: str | None = None
    processed_count: int = 0
    failed_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    heartbeat_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class FailedJobRecoveryAction:
    action_id: str
    job_id: str
    queue_name: str
    action_type: str
    status: str = "queued"
    reason: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _ensure_governance_store() -> None:
    ORCH_DIR.mkdir(parents=True, exist_ok=True)

    for path in (
        GOVERNANCE_AUDIT_PATH,
        QUEUE_HEALTH_PATH,
        WORKER_STATUS_PATH,
        ORCHESTRATION_METRICS_PATH,
        FAILED_JOB_RECOVERY_PATH,
        *QUEUE_PATHS.values(),
    ):
        if not path.exists():
            path.write_text("", encoding="utf-8")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    _ensure_governance_store()

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _read_jsonl(path: Path, limit: int = 500) -> List[Dict[str, Any]]:
    _ensure_governance_store()

    lines = path.read_text(encoding="utf-8").splitlines()
    records: List[Dict[str, Any]] = []

    for line in lines[-limit:]:
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            records.append(
                {
                    "parse_error": True,
                    "raw_line": line,
                    "source_path": str(path),
                }
            )

    return records


def log_governance_audit(event: GovernanceAuditEvent) -> Dict[str, Any]:
    payload = asdict(event)
    _append_jsonl(GOVERNANCE_AUDIT_PATH, payload)
    return payload


def get_queue_health_snapshot() -> Dict[str, Any]:
    _ensure_governance_store()

    queues: Dict[str, Any] = {}

    for queue_name, path in QUEUE_PATHS.items():
        records = _read_jsonl(path, limit=100000)

        queued = sum(1 for r in records if str(r.get("status") or "queued") == "queued")
        failed = sum(1 for r in records if str(r.get("status") or "") == "failed")
        dead_lettered = sum(
            1
            for r in records
            if "dead_letter" in queue_name or str(r.get("status") or "") == "dead_lettered"
        )

        queues[queue_name] = {
            "path": str(path),
            "total_records": len(records),
            "queued": queued,
            "failed": failed,
            "dead_lettered": dead_lettered,
            "exists": path.exists(),
        }

    snapshot = {
        "snapshot_type": "queue_health",
        "queue_count": len(queues),
        "queues": queues,
        "created_at": _utc_now().isoformat(),
    }

    _append_jsonl(QUEUE_HEALTH_PATH, snapshot)

    log_governance_audit(
        GovernanceAuditEvent(
            event_type="queue_health_snapshot_recorded",
            status="recorded",
            message="Queue health snapshot recorded.",
            metadata={
                "queue_count": len(queues),
            },
        )
    )

    return snapshot


def record_worker_status(
    *,
    worker_id: str,
    worker_type: str,
    status: str,
    current_job_id: str | None = None,
    queue_name: str | None = None,
    processed_count: int = 0,
    failed_count: int = 0,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    worker = WorkerStatus(
        worker_id=worker_id,
        worker_type=worker_type,
        status=status,
        current_job_id=current_job_id,
        queue_name=queue_name,
        processed_count=processed_count,
        failed_count=failed_count,
        metadata=metadata or {},
    )

    payload = asdict(worker)
    _append_jsonl(WORKER_STATUS_PATH, payload)

    log_governance_audit(
        GovernanceAuditEvent(
            event_type="worker_status_recorded",
            status=status,
            worker_id=worker_id,
            queue_name=queue_name,
            job_id=current_job_id,
            message="Worker status heartbeat recorded.",
            metadata={
                "worker_type": worker_type,
                "processed_count": processed_count,
                "failed_count": failed_count,
            },
        )
    )

    return payload


def get_latest_worker_statuses(limit: int = 500) -> List[Dict[str, Any]]:
    return _read_jsonl(WORKER_STATUS_PATH, limit)


def calculate_orchestration_metrics() -> Dict[str, Any]:
    queue_snapshot = get_queue_health_snapshot()
    workers = get_latest_worker_statuses(limit=1000)

    total_records = 0
    total_queued = 0
    total_failed = 0
    total_dead_lettered = 0

    for item in queue_snapshot.get("queues", {}).values():
        total_records += int(item.get("total_records") or 0)
        total_queued += int(item.get("queued") or 0)
        total_failed += int(item.get("failed") or 0)
        total_dead_lettered += int(item.get("dead_lettered") or 0)

    active_workers = sum(1 for w in workers if str(w.get("status") or "") in {"running", "active", "busy"})
    idle_workers = sum(1 for w in workers if str(w.get("status") or "") == "idle")
    failed_workers = sum(1 for w in workers if str(w.get("status") or "") in {"failed", "offline"})

    metrics = {
        "metrics_type": "tms_orchestration_metrics",
        "queue_count": len(queue_snapshot.get("queues", {})),
        "total_records": total_records,
        "total_queued": total_queued,
        "total_failed": total_failed,
        "total_dead_lettered": total_dead_lettered,
        "worker_heartbeat_count": len(workers),
        "active_workers": active_workers,
        "idle_workers": idle_workers,
        "failed_workers": failed_workers,
        "created_at": _utc_now().isoformat(),
    }

    _append_jsonl(ORCHESTRATION_METRICS_PATH, metrics)

    log_governance_audit(
        GovernanceAuditEvent(
            event_type="orchestration_metrics_recorded",
            status="recorded",
            message="Orchestration metrics calculated and recorded.",
            metadata=metrics,
        )
    )

    return metrics


def register_failed_job_recovery_action(
    *,
    job_id: str,
    queue_name: str,
    action_type: str,
    reason: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    timestamp = _utc_now().strftime("%Y%m%d%H%M%S%f")
    safe_job_id = str(job_id or "unknown").replace(" ", "_")
    action_id = f"failed_job_recovery_{safe_job_id}_{timestamp}"

    action = FailedJobRecoveryAction(
        action_id=action_id,
        job_id=job_id,
        queue_name=queue_name,
        action_type=action_type,
        reason=reason,
        metadata=metadata or {},
    )

    payload = asdict(action)
    _append_jsonl(FAILED_JOB_RECOVERY_PATH, payload)

    log_governance_audit(
        GovernanceAuditEvent(
            event_type="failed_job_recovery_action_registered",
            status="queued",
            queue_name=queue_name,
            job_id=job_id,
            message=reason or "Failed-job recovery action registered.",
            metadata={
                "action_id": action_id,
                "action_type": action_type,
            },
        )
    )

    return payload


def suggest_failed_job_recovery_actions() -> List[Dict[str, Any]]:
    _ensure_governance_store()

    actions: List[Dict[str, Any]] = []

    for queue_name, path in QUEUE_PATHS.items():
        if "dead_letter" not in queue_name:
            continue

        jobs = _read_jsonl(path, limit=1000)

        for job in jobs:
            job_id = str(job.get("job_id") or "unknown")
            reason = str(job.get("dead_letter_reason") or "dead-lettered job requires review")

            action_type = "manual_review"

            if int(job.get("retry_count") or 0) < 3:
                action_type = "retry_candidate"

            actions.append(
                register_failed_job_recovery_action(
                    job_id=job_id,
                    queue_name=queue_name,
                    action_type=action_type,
                    reason=reason,
                    metadata={
                        "source": "suggest_failed_job_recovery_actions",
                        "job_type": job.get("job_type"),
                        "ticket_id": job.get("ticket_id"),
                        "workspace_id": job.get("workspace_id"),
                    },
                )
            )

    return actions


def read_governance_audit(limit: int = 500) -> List[Dict[str, Any]]:
    return _read_jsonl(GOVERNANCE_AUDIT_PATH, limit)


def read_queue_health_snapshots(limit: int = 500) -> List[Dict[str, Any]]:
    return _read_jsonl(QUEUE_HEALTH_PATH, limit)


def read_orchestration_metrics(limit: int = 500) -> List[Dict[str, Any]]:
    return _read_jsonl(ORCHESTRATION_METRICS_PATH, limit)


def read_failed_job_recovery_actions(limit: int = 500) -> List[Dict[str, Any]]:
    return _read_jsonl(FAILED_JOB_RECOVERY_PATH, limit)
