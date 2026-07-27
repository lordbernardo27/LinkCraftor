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
    domain: str | None = None
    url: str | None = None


@router.post("/connect_domain")
def connect_domain(
    payload: ConnectDomainRequest,
) -> Dict[str, Any]:
    """
    Canonical Connect Domain API entry point.

    One request starts both:

    Pipeline 1 — Linking Target Pipeline
    Pipeline 2 — Website Knowledge Pipeline
    """

    return run_connect_domain(
        workspace_id=payload.workspace_id,
        domain=payload.domain,
        url=payload.url,
    )
