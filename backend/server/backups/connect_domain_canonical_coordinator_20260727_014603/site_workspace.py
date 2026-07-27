from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel

from backend.server.pipelines.connect_domain.website_knowledge_pipeline.coordinator import (
    run_website_knowledge_pipeline,
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
    Connect Domain API entry point for Pipeline 2.

    The route contains no Website Knowledge Pipeline implementation.
    It delegates all Pipeline 2 work to its coordinator.
    """

    return run_website_knowledge_pipeline(
        workspace_id=payload.workspace_id,
        domain=payload.domain,
        url=payload.url,
    )
