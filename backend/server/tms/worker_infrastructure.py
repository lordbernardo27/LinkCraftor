
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.server.tms.orchestration_governance import (
    record_worker_status,
    log_governance_audit,
    GovernanceAuditEvent,
)

DATA_DIR = Path("backend/server/data/tms")

WORKER_AUDIT_PATH = DATA_DIR / "worker_execution_audit.jsonl"


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not WORKER_AUDIT_PATH.exists():
        WORKER_AUDIT_PATH.write_text("", encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_audit(payload: Dict[str, Any]) -> None:
    _ensure_store()

    with WORKER_AUDIT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


# ============================================================
# 11.2.5 AUDIT WORKERS
# ============================================================

def record_worker_audit(
    *,
    worker_type: str,
    job_id: str,
    status: str,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:

    payload = {
        "worker_type": worker_type,
        "job_id": job_id,
        "status": status,
        "metadata": metadata or {},
        "created_at": _utc_now(),
    }

    _append_audit(payload)

    log_governance_audit(
        GovernanceAuditEvent(
            event_type="worker_job_processed",
            status=status,
            job_id=job_id,
            message=f"{worker_type} processed job.",
        )
    )

    return payload


def process_audit_jobs(
    jobs: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    results = []

    for job in jobs:
        results.append(
            record_worker_audit(
                worker_type="audit_worker",
                job_id=str(job.get("job_id") or "unknown"),
                status="processed",
                metadata=job,
            )
        )

    return results


# ============================================================
# 11.2.1 TICKET WORKERS
# ============================================================

def execute_ticket_workflow(
    job: Dict[str, Any],
) -> Dict[str, Any]:

    result = {
        "job_id": job.get("job_id"),
        "worker": "ticket_worker",
        "status": "completed",
        "executed_at": _utc_now(),
    }

    record_worker_audit(
        worker_type="ticket_worker",
        job_id=str(job.get("job_id")),
        status="completed",
        metadata=result,
    )

    return result


def process_ticket_jobs(
    jobs: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    record_worker_status(
        worker_id="ticket_worker_1",
        worker_type="ticket_worker",
        status="running",
    )

    results = [execute_ticket_workflow(job) for job in jobs]

    record_worker_status(
        worker_id="ticket_worker_1",
        worker_type="ticket_worker",
        status="idle",
        processed_count=len(results),
    )

    return results


# ============================================================
# 11.2.2 EMAIL WORKERS
# ============================================================

def execute_email_delivery(
    job: Dict[str, Any],
) -> Dict[str, Any]:

    result = {
        "job_id": job.get("job_id"),
        "worker": "email_worker",
        "status": "completed",
        "executed_at": _utc_now(),
    }

    record_worker_audit(
        worker_type="email_worker",
        job_id=str(job.get("job_id")),
        status="completed",
        metadata=result,
    )

    return result


def process_email_jobs(
    jobs: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    record_worker_status(
        worker_id="email_worker_1",
        worker_type="email_worker",
        status="running",
    )

    results = [execute_email_delivery(job) for job in jobs]

    record_worker_status(
        worker_id="email_worker_1",
        worker_type="email_worker",
        status="idle",
        processed_count=len(results),
    )

    return results


# ============================================================
# 11.2.3 SLA WORKERS
# ============================================================

def execute_sla_check(
    job: Dict[str, Any],
) -> Dict[str, Any]:

    result = {
        "job_id": job.get("job_id"),
        "worker": "sla_worker",
        "status": "completed",
        "executed_at": _utc_now(),
    }

    record_worker_audit(
        worker_type="sla_worker",
        job_id=str(job.get("job_id")),
        status="completed",
        metadata=result,
    )

    return result


def process_sla_jobs(
    jobs: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    record_worker_status(
        worker_id="sla_worker_1",
        worker_type="sla_worker",
        status="running",
    )

    results = [execute_sla_check(job) for job in jobs]

    record_worker_status(
        worker_id="sla_worker_1",
        worker_type="sla_worker",
        status="idle",
        processed_count=len(results),
    )

    return results


# ============================================================
# 11.2.4 AI WORKERS
# ============================================================

def process_support_intelligence_jobs(
    jobs: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    results = []

    for job in jobs:
        result = {
            "job_id": job.get("job_id"),
            "worker": "ai_worker",
            "task": "support_intelligence",
            "status": "completed",
            "executed_at": _utc_now(),
        }

        record_worker_audit(
            worker_type="ai_worker",
            job_id=str(job.get("job_id")),
            status="completed",
            metadata=result,
        )

        results.append(result)

    return results


def process_churn_jobs(
    jobs: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    results = []

    for job in jobs:
        results.append(
            {
                "job_id": job.get("job_id"),
                "worker": "ai_worker",
                "task": "churn_analysis",
                "status": "completed",
                "executed_at": _utc_now(),
            }
        )

    return results


def process_incident_jobs(
    jobs: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    results = []

    for job in jobs:
        results.append(
            {
                "job_id": job.get("job_id"),
                "worker": "ai_worker",
                "task": "incident_detection",
                "status": "completed",
                "executed_at": _utc_now(),
            }
        )

    return results


def read_worker_audit(limit: int = 1000) -> List[Dict[str, Any]]:

    _ensure_store()

    lines = WORKER_AUDIT_PATH.read_text(
        encoding="utf-8"
    ).splitlines()

    return [
        json.loads(line)
        for line in lines[-limit:]
        if line.strip()
    ]
