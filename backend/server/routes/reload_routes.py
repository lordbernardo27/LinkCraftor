
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.server.stores.reload_governance import (
    RELOAD_RULES_V1,
    get_reload_state,
    load_reload_queue,
    process_reload_queue,
    queue_reload_event,
)


router = APIRouter(prefix="/api/reload", tags=["reload"])


class ReloadQueueRequest(BaseModel):
    workspace_id: str = Field(default="default")
    trigger: str = Field(default="workspace_opened")
    metadata: Dict[str, Any] = Field(default_factory=dict)


@router.get("/rules")
def get_reload_rules() -> Dict[str, Any]:
    return {
        "ok": True,
        "rules": RELOAD_RULES_V1,
    }


@router.get("/state/{workspace_id}")
def read_reload_state(workspace_id: str) -> Dict[str, Any]:
    return {
        "ok": True,
        "state": get_reload_state(workspace_id),
    }


@router.get("/queue/{workspace_id}")
def read_reload_queue(workspace_id: str) -> Dict[str, Any]:
    queue = load_reload_queue(workspace_id)
    return {
        "ok": True,
        "workspace_id": workspace_id,
        "count": len(queue),
        "queue": queue,
    }


@router.post("/queue")
def queue_reload(req: ReloadQueueRequest) -> Dict[str, Any]:
    event = queue_reload_event(
        workspace_id=req.workspace_id,
        trigger=req.trigger,
        metadata=req.metadata,
    )

    return {
        "ok": True,
        "event": event,
    }


@router.post("/process/{workspace_id}")
def process_reload_events(workspace_id: str, limit: int = 20) -> Dict[str, Any]:
    return {
        "ok": True,
        "result": process_reload_queue(workspace_id, limit=limit),
    }
