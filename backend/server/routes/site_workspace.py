from __future__ import annotations

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
) -> Dict[str, Any]:
    """
    Canonical Domain-mode workspace creation and Connect Domain entry point.

    The complete modal identity is submitted atomically:
    - workspace_name
    - workspace_mode
    - domain
    - site_url
    - optional existing workspace_id
    """

    return run_connect_domain(
        workspace_id=payload.workspace_id,
        workspace_name=payload.workspace_name,
        workspace_mode=payload.workspace_mode,
        domain=payload.domain,
        site_url=payload.site_url,
        url=payload.url,
    )
