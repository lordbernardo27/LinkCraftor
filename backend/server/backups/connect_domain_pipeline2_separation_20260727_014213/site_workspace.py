
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.server.jobs.universal_knowledge_orchestrator import create_universal_knowledge_job


router = APIRouter(prefix="/api/site/workspace", tags=["site-workspace"])


class ConnectDomainRequest(BaseModel):
    workspace_id: str | None = None
    domain: str | None = None
    url: str | None = None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_workspace_id(value: str | None) -> str:
    raw = str(value or "").strip()
    if not raw:
        # Temporary safe fallback so domain connection can work
        # even when the frontend has not initialized workspace_id.
        return "ws_whattoexpect_com"
    return raw


def _normalize_domain(value: str | None) -> str:
    raw = str(value or "").strip()
    if not raw:
        raise HTTPException(status_code=400, detail="domain or url is required")

    raw = raw.replace("https://", "").replace("http://", "")
    raw = raw.split("/")[0].strip().lower()

    if not raw or "." not in raw:
        raise HTTPException(status_code=400, detail="Invalid domain")

    return raw


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    import json
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


@router.post("/connect_domain")
def connect_domain(payload: ConnectDomainRequest) -> Dict[str, Any]:
    workspace_id = _safe_workspace_id(payload.workspace_id)
    domain = _normalize_domain(payload.domain or payload.url)

    live_domain_payload = {
        "schema_version": "live_domain_connection_v1",
        "workspace_id": workspace_id,
        "domain": domain,
        "source_type": "website",
        "status": "connected",
        "connected_at": _now_iso(),
    }

    _write_json(
        Path("backend/server/data/live_domains") / f"live_domain_{workspace_id}.json",
        live_domain_payload,
    )

    job = create_universal_knowledge_job(
        workspace_id=workspace_id,
        job_type="website_connection_batch",
        payload={
            "workspace_id": workspace_id,
            "domain": domain,
            "urls": [],
            "trigger": "live_connect_domain_route",
        }
    )


    return {
        "ok": True,
        "workspace_id": workspace_id,
        "domain": domain,
        "connected": False,
        "execution_status": "QUEUED_AWAITING_FRESH_WORKER",
        "job": job,
    }
