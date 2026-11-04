from __future__ import annotations

from fastapi import Request, HTTPException

from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel

from backend.server.pipelines.connect_domain.coordinator import (
    run_connect_domain,
)


router = APIRouter(
    prefix="/api/site/workspace",
    tags=["site-workspace"],
)


class ConnectDomainRequest(BaseModel):
    workspace_id: str | None = None
    workspace_name: str | None = None
    workspace_mode: str = "domain"
    domain: str | None = None
    site_url: str | None = None
    url: str | None = None


@router.post("/connect_domain")
def connect_domain(
    payload: ConnectDomainRequest,
    request: Request,
) -> Dict[str, Any]:
    """Submit one Connected Domain workflow through the canonical runtime."""
    runtime_gateway = getattr(
        request.app.state,
        "runtime_coordination_gateway",
        None,
    )
    if runtime_gateway is None:
        raise HTTPException(
            status_code=503,
            detail="Runtime Coordination Gateway is unavailable.",
        )
    from backend.server.pipelines.connect_domain.activation import (
        activate_connected_domain_pipeline,
    )
    return activate_connected_domain_pipeline(
        runtime_gateway=runtime_gateway,
        workspace_id=payload.workspace_id,
        workspace_name=payload.workspace_name,
        domain=payload.domain,
        site_url=payload.site_url,
        url=payload.url,
    )

