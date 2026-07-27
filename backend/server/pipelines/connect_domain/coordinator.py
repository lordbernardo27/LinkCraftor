"""
LinkCraftor — Canonical Connect Domain Coordinator

CONNECT DOMAIN
    ├── linking_target_pipeline_batch
    └── website_connection_batch

The coordinator:

1. validates the complete Domain Workspace modal identity;
2. persists the canonical workspace profile;
3. queues both pipelines;
4. returns immediately.

The pipeline implementation remains outside this coordinator.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from fastapi import HTTPException

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


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_workspace_name(
    workspace_name: str | None,
    domain: str,
) -> str:
    supplied = str(workspace_name or "").strip()

    if supplied:
        return supplied

    return (
        domain
        .replace("www.", "")
        .replace(".", " ")
        .replace("-", " ")
        .strip()
        .title()
    )


def _persist_workspace_profile(
    *,
    workspace_id: str,
    workspace_name: str,
    workspace_mode: str,
    domain: str,
    site_url: str | None,
) -> Path:
    profile_dir = (
        Path("backend/server/data/workspaces")
        / workspace_id
    )

    profile_path = profile_dir / "workspace_profile.json"
    profile_dir.mkdir(parents=True, exist_ok=True)

    existing: Dict[str, Any] = {}

    if profile_path.exists():
        try:
            loaded = json.loads(
                profile_path.read_text(encoding="utf-8-sig")
            )

            if isinstance(loaded, dict):
                existing = loaded
        except Exception:
            existing = {}

    now = _now_iso()

    profile = {
        **existing,
        "schema_version": "workspace_profile_v2",
        "workspace_id": workspace_id,
        "workspace_name": workspace_name,
        "workspace_mode": workspace_mode,
        "domain": domain,
        "site_url": str(site_url or "").strip(),
        "source_type": "domain",
        "connection_status": "processing",
        "created_at": existing.get("created_at") or now,
        "connected_at": existing.get("connected_at") or now,
        "updated_at": now,
    }

    temporary_path = profile_path.with_suffix(".json.tmp")

    temporary_path.write_text(
        json.dumps(
            profile,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    temporary_path.replace(profile_path)

    return profile_path


def run_connect_domain(
    *,
    workspace_id: str | None = None,
    workspace_name: str | None = None,
    workspace_mode: str = "domain",
    domain: str | None = None,
    site_url: str | None = None,
    url: str | None = None,
) -> Dict[str, Any]:
    """
    Persist the Domain Workspace identity and queue both pipelines.
    """

    normalized_mode = str(
        workspace_mode or "domain"
    ).strip().lower()

    if normalized_mode != "domain":
        raise HTTPException(
            status_code=400,
            detail=(
                "The Connect Domain endpoint accepts only "
                "workspace_mode='domain'."
            ),
        )

    clean_domain = _normalize_domain(
        domain or url or site_url
    )

    resolved_workspace_id = _resolve_workspace_id(
        workspace_id,
        clean_domain,
    )

    resolved_workspace_name = _normalize_workspace_name(
        workspace_name,
        clean_domain,
    )

    profile_path = _persist_workspace_profile(
        workspace_id=resolved_workspace_id,
        workspace_name=resolved_workspace_name,
        workspace_mode=normalized_mode,
        domain=clean_domain,
        site_url=site_url,
    )

    registration = ensure_linking_target_pipeline_registration()

    pipeline_1_job = create_universal_knowledge_job(
        workspace_id=resolved_workspace_id,
        job_type=LINKING_TARGET_PIPELINE_BATCH,
        pipeline="linking_target_pipeline",
        stage=LINKING_TARGET_PIPELINE_BATCH,
        payload={
            "workspace_id": resolved_workspace_id,
            "workspace_name": resolved_workspace_name,
            "workspace_mode": normalized_mode,
            "domain": clean_domain,
            "site_url": str(site_url or "").strip(),
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

    pipeline_1_queued = (
        pipeline_1_job.get("status") == "queued"
    )

    overall_ok = bool(
        pipeline_1_queued
        and pipeline_2.get("ok")
    )

    return {
        "ok": overall_ok,
        "workspace_id": resolved_workspace_id,
        "workspace_name": resolved_workspace_name,
        "workspace_mode": normalized_mode,
        "domain": clean_domain,
        "site_url": str(site_url or "").strip(),
        "connected": overall_ok,
        "connection_status": (
            "processing"
            if overall_ok
            else "queue_creation_failed"
        ),
        "execution_mode": "asynchronous",
        "workspace_profile": str(profile_path),
        "pipelines": {
            "linking_target_pipeline": {
                "ok": pipeline_1_queued,
                "execution_status": "QUEUED_AWAITING_WORKER",
                "job_type": LINKING_TARGET_PIPELINE_BATCH,
                "job": pipeline_1_job,
                "runtime_registration": registration,
            },
            "website_knowledge_pipeline": pipeline_2,
        },
    }
