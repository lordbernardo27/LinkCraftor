"""
LinkCraftor Connect Domain — Pipeline 2

WEBSITE KNOWLEDGE PIPELINE

CONNECT DOMAIN
    -> Site Sources
    -> Site Pages
    -> Enterprise Raw HTML Acquisition
    -> Raw HTML Store
    -> UDARE
    -> Website Article Integrity
    -> Article Validation
    -> Website Unified Content
    -> UUCD
    -> Universal Article Body Store
    -> Certification
    -> Semantic Ready

This coordinator currently creates the existing
website_connection_batch job.

Runtime-foundation expansion is intentionally deferred.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from fastapi import HTTPException

from backend.server.jobs.universal_knowledge_orchestrator import (
    create_universal_knowledge_job,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_domain(value: str | None) -> str:
    raw = str(value or "").strip().lower()

    if not raw:
        raise HTTPException(
            status_code=400,
            detail="domain or url is required",
        )

    raw = re.sub(r"^https?://", "", raw, flags=re.IGNORECASE)
    raw = raw.split("/", 1)[0].strip()
    raw = raw.rstrip(".")

    if raw.startswith("www."):
        raw = raw[4:]

    if not raw or "." not in raw:
        raise HTTPException(
            status_code=400,
            detail="Invalid domain",
        )

    return raw


def _workspace_id_from_domain(domain: str) -> str:
    normalized = re.sub(
        r"[^a-z0-9]+",
        "_",
        str(domain or "").lower(),
    ).strip("_")

    if not normalized:
        raise HTTPException(
            status_code=400,
            detail="Could not derive workspace_id from domain",
        )

    return f"ws_{normalized}"


def _resolve_workspace_id(
    workspace_id: str | None,
    domain: str,
) -> str:
    supplied = str(workspace_id or "").strip()

    if supplied:
        if not supplied.startswith("ws_"):
            raise HTTPException(
                status_code=400,
                detail="workspace_id must start with ws_",
            )

        return supplied

    return _workspace_id_from_domain(domain)


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def run_website_knowledge_pipeline(
    *,
    workspace_id: str | None = None,
    domain: str | None = None,
    url: str | None = None,
) -> Dict[str, Any]:
    """
    Start Connect Domain Pipeline 2 — Website Knowledge Pipeline.

    This function records the domain connection and creates the existing
    website_connection_batch job without executing the full workload inside
    the HTTP route.
    """

    clean_domain = _normalize_domain(domain or url)

    resolved_workspace_id = _resolve_workspace_id(
        workspace_id,
        clean_domain,
    )

    connected_at = _now_iso()

    live_domain_payload = {
        "schema_version": "live_domain_connection_v1",
        "workspace_id": resolved_workspace_id,
        "domain": clean_domain,
        "source_type": "website",
        "status": "queued",
        "connection_status": "processing",
        "connected_at": connected_at,
        "updated_at": connected_at,
        "pipeline": "website_knowledge_pipeline",
    }

    live_domain_path = (
        Path("backend/server/data/live_domains")
        / f"live_domain_{resolved_workspace_id}.json"
    )

    _write_json(
        live_domain_path,
        live_domain_payload,
    )

    job = create_universal_knowledge_job(
        workspace_id=resolved_workspace_id,
        job_type="website_connection_batch",
        payload={
            "workspace_id": resolved_workspace_id,
            "domain": clean_domain,
            "urls": [],
            "source_type": "website",
            "pipeline": "website_knowledge_pipeline",
            "trigger": "live_connect_domain_route",
        },
    )

    return {
        "ok": True,
        "workspace_id": resolved_workspace_id,
        "domain": clean_domain,
        "connected": True,
        "connection_status": "processing",
        "execution_status": "QUEUED_AWAITING_WORKER",
        "pipeline": "website_knowledge_pipeline",
        "live_domain_record": str(live_domain_path),
        "job": job,
    }
