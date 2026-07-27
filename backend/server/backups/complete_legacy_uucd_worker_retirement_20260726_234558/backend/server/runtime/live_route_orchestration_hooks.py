from __future__ import annotations

from typing import Any, Dict

from backend.server.jobs.universal_knowledge_orchestrator import create_universal_knowledge_job
from backend.server.workers.universal_knowledge_worker import execute_universal_knowledge_job_v1


def enqueue_and_run_upload_ingestion_job_v1(
    *,
    workspace_id: str,
    upload_meta: Dict[str, Any],
) -> Dict[str, Any]:
    job = create_universal_knowledge_job(
        workspace_id=workspace_id,
        job_type="upload_document_batch",
        payload={
            "trigger": "live_upload_route",
            "document_id": upload_meta.get("doc_id") or upload_meta.get("document_id"),
            "filename": upload_meta.get("filename"),
            "stored_name": upload_meta.get("stored_name"),
            "stored_path": upload_meta.get("stored_path"),
            "source_type": "uploaded_document",
            "automatic": True,
        },
    )

    result = execute_universal_knowledge_job_v1(job)

    return {
        "ok": bool(result.get("ok")),
        "job_id": job.get("job_id"),
        "job_type": job.get("job_type"),
        "status": "executed" if result.get("ok") else "failed",
        "result": result,
    }


def enqueue_and_run_website_ingestion_job_v1(
    *,
    workspace_id: str,
    domain: str = "",
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    job = create_universal_knowledge_job(
        workspace_id=workspace_id,
        job_type="website_connection_batch",
        payload={
            "trigger": "live_connect_domain_route",
            "domain": domain,
            "source_type": "website",
            "automatic": True,
            **(payload or {}),
        },
    )

    result = execute_universal_knowledge_job_v1(job)

    return {
        "ok": bool(result.get("ok")),
        "job_id": job.get("job_id"),
        "job_type": job.get("job_type"),
        "status": "executed" if result.get("ok") else "failed",
        "result": result,
    }
