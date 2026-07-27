"""
LinkCraftor — Canonical Connect Domain Coordinator

CONNECT DOMAIN
    ├── linking_target_pipeline_batch
    └── website_connection_batch

The coordinator queues both pipelines and returns immediately.
It contains no sitemap, target-pool, clustering, raw HTML, UDARE,
integrity, validation, WUC, UUCD, or semantic-processing logic.
"""

from __future__ import annotations

from typing import Any, Dict

from backend.server.jobs.universal_knowledge_orchestrator import (
    create_universal_knowledge_job,
)
from backend.server.pipelines.connect_domain.job_types import (
    LINKING_TARGET_PIPELINE_BATCH,
)
from backend.server.pipelines.connect_domain.linking_target_pipeline.runtime_registration import (
    ensure_linking_target_pipeline_registration,
)
from backend.server.pipelines.connect_domain.website_knowledge_pipeline.coordinator import (
    _normalize_domain,
    _resolve_workspace_id,
    run_website_knowledge_pipeline,
)


def run_connect_domain(
    *,
    workspace_id: str | None = None,
    domain: str | None = None,
    url: str | None = None,
) -> Dict[str, Any]:
    """
    Queue both canonical Connect Domain pipelines.

    Pipeline 1 is registered dynamically and queued.
    Pipeline 2 continues using the existing website_connection_batch job.
    """

    clean_domain = _normalize_domain(domain or url)

    resolved_workspace_id = _resolve_workspace_id(
        workspace_id,
        clean_domain,
    )

    registration = ensure_linking_target_pipeline_registration()

    pipeline_1_job = create_universal_knowledge_job(
        workspace_id=resolved_workspace_id,
        job_type=LINKING_TARGET_PIPELINE_BATCH,
        pipeline="linking_target_pipeline",
        stage=LINKING_TARGET_PIPELINE_BATCH,
        payload={
            "workspace_id": resolved_workspace_id,
            "domain": clean_domain,
            "source_type": "website",
            "pipeline": "linking_target_pipeline",
            "trigger": "canonical_connect_domain_coordinator",
        },
    )

    pipeline_2 = run_website_knowledge_pipeline(
        workspace_id=resolved_workspace_id,
        domain=clean_domain,
        url=url,
    )

    overall_ok = bool(
        pipeline_1_job.get("status") == "queued"
        and pipeline_2.get("ok")
    )

    return {
        "ok": overall_ok,
        "workspace_id": resolved_workspace_id,
        "domain": clean_domain,
        "connected": overall_ok,
        "connection_status": (
            "processing"
            if overall_ok
            else "queue_creation_failed"
        ),
        "execution_mode": "asynchronous",
        "pipelines": {
            "linking_target_pipeline": {
                "ok": pipeline_1_job.get("status") == "queued",
                "execution_status": "QUEUED_AWAITING_WORKER",
                "job_type": LINKING_TARGET_PIPELINE_BATCH,
                "job": pipeline_1_job,
                "runtime_registration": registration,
            },
            "website_knowledge_pipeline": pipeline_2,
        },
    }
