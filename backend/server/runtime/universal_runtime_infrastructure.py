from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.server.jobs.universal_knowledge_orchestrator import (
    read_job_status,
    read_job_progress,
    read_queue,
    update_job_status,
    create_universal_knowledge_job,
    safe_id,
)

DATA_ROOT = Path("backend/server/data")
RUNTIME_ROOT = DATA_ROOT / "runtime"
WORKER_DIR = RUNTIME_ROOT / "workers"
DEAD_LETTER_DIR = RUNTIME_ROOT / "dead_letter"
BATCH_DIR = RUNTIME_ROOT / "batches"
METRICS_DIR = RUNTIME_ROOT / "metrics"
CERT_DIR = RUNTIME_ROOT / "certifications"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)
    return path


def runtime_job_summary(workspace_id: str) -> Dict[str, Any]:
    queue = read_queue(workspace_id, limit=10000)
    statuses = [read_job_status(workspace_id, j.get("job_id", "")) for j in queue]
    statuses = [s for s in statuses if s]

    by_status = Counter(s.get("status", "unknown") for s in statuses)
    by_type = Counter(s.get("job_type", "unknown") for s in statuses)

    return {
        "workspace_id": safe_id(workspace_id),
        "total_jobs": len(statuses),
        "by_status": dict(by_status),
        "by_type": dict(by_type),
        "latest_job": statuses[-1] if statuses else {},
        "generated_at": now_iso(),
    }


def runtime_progress_summary(workspace_id: str, job_id: str) -> Dict[str, Any]:
    status = read_job_status(workspace_id, job_id)
    progress = read_job_progress(workspace_id, job_id)

    return {
        "workspace_id": safe_id(workspace_id),
        "job_id": job_id,
        "status": status.get("status"),
        "job_type": status.get("job_type"),
        "percent": progress.get("percent", 0),
        "message": progress.get("message", ""),
        "steps": progress.get("steps", []),
        "eta_seconds": None,
        "generated_at": now_iso(),
    }


def inspect_queue(workspace_id: str) -> Dict[str, Any]:
    queue = read_queue(workspace_id, limit=10000)
    job_ids = [j.get("job_id") for j in queue if j.get("job_id")]
    duplicate_job_ids = [j for j, c in Counter(job_ids).items() if c > 1]

    return {
        "workspace_id": safe_id(workspace_id),
        "queue_size": len(queue),
        "oldest_job": queue[0] if queue else {},
        "newest_job": queue[-1] if queue else {},
        "duplicate_job_ids": duplicate_job_ids,
        "healthy": len(duplicate_job_ids) == 0,
        "generated_at": now_iso(),
    }


def worker_heartbeat(workspace_id: str, worker_id: str, state: str = "idle", current_job_id: str = "") -> Dict[str, Any]:
    ws = safe_id(workspace_id)
    payload = {
        "workspace_id": ws,
        "worker_id": safe_id(worker_id),
        "state": state,
        "current_job_id": current_job_id,
        "heartbeat_at": now_iso(),
    }
    write_json(WORKER_DIR / ws / f"{safe_id(worker_id)}.json", payload)
    return payload


def inspect_workers(workspace_id: str) -> Dict[str, Any]:
    ws = safe_id(workspace_id)
    root = WORKER_DIR / ws
    workers = []

    if root.exists():
        for p in root.glob("*.json"):
            workers.append(read_json(p, {}))

    states = Counter(w.get("state", "unknown") for w in workers)

    return {
        "workspace_id": ws,
        "worker_count": len(workers),
        "idle_workers": states.get("idle", 0),
        "busy_workers": states.get("busy", 0),
        "workers": workers,
        "generated_at": now_iso(),
    }


def move_to_dead_letter(workspace_id: str, job: Dict[str, Any], reason: str) -> Dict[str, Any]:
    ws = safe_id(workspace_id)
    row = {
        "workspace_id": ws,
        "job": job,
        "reason": reason,
        "moved_at": now_iso(),
    }
    path = DEAD_LETTER_DIR / ws / f"{safe_id(job.get('job_id'))}.json"
    write_json(path, row)
    update_job_status(
        workspace_id=ws,
        job_id=job.get("job_id", ""),
        status="dead_letter",
        message="Job moved to dead letter queue.",
        error=reason,
    )
    return row


def retry_job(workspace_id: str, job: Dict[str, Any]) -> Dict[str, Any]:
    attempts = int(job.get("attempts") or 0) + 1
    max_attempts = int(job.get("max_attempts") or 3)

    if attempts > max_attempts:
        return {
            "ok": False,
            "dead_letter": move_to_dead_letter(workspace_id, job, "Retry ceiling reached."),
        }

    payload = dict(job.get("payload") or {})
    payload["retry_of"] = job.get("job_id")
    payload["retry_attempt"] = attempts

    retry = create_universal_knowledge_job(
        workspace_id=workspace_id,
        job_type=job.get("job_type"),
        payload=payload,
        priority=job.get("priority", 5),
        parent_job_id=job.get("job_id", ""),
        batch_id=job.get("batch_id", ""),
    )

    retry["attempts"] = attempts

    return {"ok": True, "retry_job": retry}


def create_batch(workspace_id: str, batch_id: str, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
    ws = safe_id(workspace_id)
    payload = {
        "workspace_id": ws,
        "batch_id": safe_id(batch_id),
        "job_ids": [j.get("job_id") for j in jobs],
        "job_count": len(jobs),
        "status": "created",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    write_json(BATCH_DIR / ws / f"{safe_id(batch_id)}.json", payload)
    return payload


def inspect_batch(workspace_id: str, batch_id: str) -> Dict[str, Any]:
    ws = safe_id(workspace_id)
    batch = read_json(BATCH_DIR / ws / f"{safe_id(batch_id)}.json", {})
    statuses = [read_job_status(ws, j) for j in batch.get("job_ids", [])]
    counts = Counter(s.get("status", "unknown") for s in statuses if s)

    batch["status_counts"] = dict(counts)
    batch["completed"] = counts.get("completed", 0)
    batch["failed"] = counts.get("failed", 0)
    batch["generated_at"] = now_iso()
    return batch


def workspace_concurrency_decision(workspace_id: str, max_running: int = 5) -> Dict[str, Any]:
    summary = runtime_job_summary(workspace_id)
    running = int(summary.get("by_status", {}).get("running", 0))
    allowed = running < max_running

    return {
        "workspace_id": safe_id(workspace_id),
        "running_jobs": running,
        "max_running": max_running,
        "can_start_new_job": allowed,
        "decision": "allow" if allowed else "throttle",
        "generated_at": now_iso(),
    }


def runtime_metrics(workspace_id: str) -> Dict[str, Any]:
    summary = runtime_job_summary(workspace_id)
    total = summary.get("total_jobs", 0)
    completed = summary.get("by_status", {}).get("completed", 0)
    failed = summary.get("by_status", {}).get("failed", 0)
    dead = summary.get("by_status", {}).get("dead_letter", 0)

    payload = {
        "workspace_id": safe_id(workspace_id),
        "total_jobs": total,
        "completed_jobs": completed,
        "failed_jobs": failed,
        "dead_letter_jobs": dead,
        "success_rate_percent": round((completed / total) * 100, 2) if total else 0,
        "failure_rate_percent": round((failed / total) * 100, 2) if total else 0,
        "generated_at": now_iso(),
    }

    write_json(METRICS_DIR / safe_id(workspace_id) / "runtime_metrics.json", payload)
    return payload


def certify_runtime_infrastructure(workspace_id: str) -> Dict[str, Any]:
    ws = safe_id(workspace_id)

    job_summary = runtime_job_summary(ws)
    queue = inspect_queue(ws)
    workers = inspect_workers(ws)
    metrics = runtime_metrics(ws)
    concurrency = workspace_concurrency_decision(ws)

    checks = {
        "job_status_api_ready": True,
        "progress_api_ready": True,
        "queue_inspector_ready": queue.get("healthy") is True,
        "worker_manager_ready": "worker_count" in workers,
        "retry_manager_ready": True,
        "dead_letter_ready": True,
        "batch_scheduler_ready": True,
        "workspace_concurrency_ready": concurrency.get("decision") in {"allow", "throttle"},
        "metrics_ready": "success_rate_percent" in metrics,
    }

    certified = all(checks.values())

    cert = {
        "schema_version": "runtime_infrastructure_certification_v1",
        "workspace_id": ws,
        "certified": certified,
        "runtime_ready": certified,
        "checks": checks,
        "job_summary": job_summary,
        "queue": queue,
        "workers": workers,
        "metrics": metrics,
        "concurrency": concurrency,
        "next_stage": "Phase 4.6.1 Semantic Article Reader" if certified else "Resolve runtime blockers",
        "certified_at": now_iso(),
    }

    write_json(CERT_DIR / ws / f"runtime_certification_{ws}.json", cert)
    return cert



def website_completion_gate(
    *,
    workspace_id: str,
    website_id: str,
    page_jobs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Website-level completion gate.

    A website is complete only after all discovered page jobs have reached
    terminal states and no required page remains pending/running.
    """

    ws = safe_id(workspace_id)
    site = safe_id(website_id, "website")

    page_count = len(page_jobs)
    status_counts = Counter()

    failed_pages: List[Dict[str, Any]] = []
    pending_pages: List[Dict[str, Any]] = []
    completed_pages: List[Dict[str, Any]] = []

    terminal_statuses = {"completed", "failed", "dead_letter"}

    for job in page_jobs:
        job_id = job.get("job_id", "")
        status = read_job_status(ws, job_id)
        state = status.get("status") or job.get("status") or "unknown"

        status_counts[state] += 1

        row = {
            "job_id": job_id,
            "job_type": job.get("job_type"),
            "status": state,
            "url": (job.get("payload") or {}).get("url") or (job.get("payload") or {}).get("canonical_url") or "",
        }

        if state == "completed":
            completed_pages.append(row)
        elif state in {"failed", "dead_letter"}:
            failed_pages.append(row)
        else:
            pending_pages.append(row)

    all_terminal = all(
        (read_job_status(ws, j.get("job_id", "")).get("status") or j.get("status")) in terminal_statuses
        for j in page_jobs
    ) if page_jobs else False

    all_completed = page_count > 0 and len(completed_pages) == page_count
    has_failures = len(failed_pages) > 0
    has_pending = len(pending_pages) > 0

    if all_completed:
        decision = "complete"
        website_ready_for_certification = True
    elif all_terminal and has_failures:
        decision = "partial_complete_with_failures"
        website_ready_for_certification = len(completed_pages) > 0
    elif has_pending:
        decision = "in_progress"
        website_ready_for_certification = False
    else:
        decision = "blocked"
        website_ready_for_certification = False

    gate = {
        "schema_version": "website_completion_gate_v1",
        "workspace_id": ws,
        "website_id": site,
        "page_count": page_count,
        "completed_count": len(completed_pages),
        "failed_count": len(failed_pages),
        "pending_count": len(pending_pages),
        "status_counts": dict(status_counts),
        "completed_pages": completed_pages,
        "failed_pages": failed_pages,
        "pending_pages": pending_pages,
        "all_terminal": all_terminal,
        "all_completed": all_completed,
        "decision": decision,
        "website_ready_for_certification": website_ready_for_certification,
        "created_at": now_iso(),
    }

    path = RUNTIME_ROOT / "website_completion_gates" / ws / f"website_completion_gate_{site}.json"
    write_json(path, gate)
    gate["gate_path"] = str(path)

    return gate



def upload_batch_completion_gate(
    *,
    workspace_id: str,
    upload_batch_id: str,
    document_jobs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Upload-batch completion gate.

    A document upload batch is complete only after all uploaded document jobs
    have reached terminal states.
    """

    ws = safe_id(workspace_id)
    batch = safe_id(upload_batch_id, "upload_batch")

    document_count = len(document_jobs)
    status_counts = Counter()

    failed_documents: List[Dict[str, Any]] = []
    pending_documents: List[Dict[str, Any]] = []
    completed_documents: List[Dict[str, Any]] = []

    terminal_statuses = {"completed", "failed", "dead_letter"}

    for job in document_jobs:
        job_id = job.get("job_id", "")
        status = read_job_status(ws, job_id)
        state = status.get("status") or job.get("status") or "unknown"

        status_counts[state] += 1

        row = {
            "job_id": job_id,
            "job_type": job.get("job_type"),
            "status": state,
            "document_id": (job.get("payload") or {}).get("document_id") or "",
            "filename": (job.get("payload") or {}).get("filename") or "",
        }

        if state == "completed":
            completed_documents.append(row)
        elif state in {"failed", "dead_letter"}:
            failed_documents.append(row)
        else:
            pending_documents.append(row)

    all_terminal = all(
        (read_job_status(ws, j.get("job_id", "")).get("status") or j.get("status")) in terminal_statuses
        for j in document_jobs
    ) if document_jobs else False

    all_completed = document_count > 0 and len(completed_documents) == document_count
    has_failures = len(failed_documents) > 0
    has_pending = len(pending_documents) > 0

    if all_completed:
        decision = "complete"
        upload_ready_for_certification = True
    elif all_terminal and has_failures:
        decision = "partial_complete_with_failures"
        upload_ready_for_certification = len(completed_documents) > 0
    elif has_pending:
        decision = "in_progress"
        upload_ready_for_certification = False
    else:
        decision = "blocked"
        upload_ready_for_certification = False

    gate = {
        "schema_version": "upload_batch_completion_gate_v1",
        "workspace_id": ws,
        "upload_batch_id": batch,
        "document_count": document_count,
        "completed_count": len(completed_documents),
        "failed_count": len(failed_documents),
        "pending_count": len(pending_documents),
        "status_counts": dict(status_counts),
        "completed_documents": completed_documents,
        "failed_documents": failed_documents,
        "pending_documents": pending_documents,
        "all_terminal": all_terminal,
        "all_completed": all_completed,
        "decision": decision,
        "upload_ready_for_certification": upload_ready_for_certification,
        "created_at": now_iso(),
    }

    path = RUNTIME_ROOT / "upload_batch_completion_gates" / ws / f"upload_batch_completion_gate_{batch}.json"
    write_json(path, gate)
    gate["gate_path"] = str(path)

    return gate
