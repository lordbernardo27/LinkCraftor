
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.server.stores.rebuild_governance import (
    REBUILD_RULES_V2,
    detect_stale_layers,
    get_rebuild_state,
    load_rebuild_queue,
    mark_layer_rebuilt,
    queue_rebuild_event,
    queue_stale_repair_if_needed,
    run_stale_safety_sweep,
    process_rebuild_queue,
)


router = APIRouter(prefix="/api/rebuild", tags=["rebuild"])


class RebuildQueueRequest(BaseModel):
    workspace_id: str = Field(default="default")
    trigger: str = Field(default="document_changed")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MarkLayerRebuiltRequest(BaseModel):
    workspace_id: str = Field(default="default")
    layer: str


@router.get("/rules")
def get_rebuild_rules() -> Dict[str, Any]:
    return {
        "ok": True,
        "rules": REBUILD_RULES_V2,
    }


@router.get("/state/{workspace_id}")
def read_rebuild_state(workspace_id: str) -> Dict[str, Any]:
    return {
        "ok": True,
        "state": get_rebuild_state(workspace_id),
    }


@router.get("/queue/{workspace_id}")
def read_rebuild_queue(workspace_id: str) -> Dict[str, Any]:
    queue = load_rebuild_queue(workspace_id)
    return {
        "ok": True,
        "workspace_id": workspace_id,
        "count": len(queue),
        "queue": queue,
    }


@router.get("/stale/{workspace_id}")
def read_stale_report(workspace_id: str) -> Dict[str, Any]:
    return {
        "ok": True,
        "report": detect_stale_layers(workspace_id),
    }


@router.post("/queue")
def queue_rebuild(req: RebuildQueueRequest) -> Dict[str, Any]:
    event = queue_rebuild_event(
        workspace_id=req.workspace_id,
        trigger=req.trigger,
        metadata=req.metadata,
    )

    return {
        "ok": True,
        "event": event,
    }


@router.post("/manual")
def manual_workspace_rebuild(req: RebuildQueueRequest) -> Dict[str, Any]:
    event = queue_rebuild_event(
        workspace_id=req.workspace_id,
        trigger=req.trigger or "document_changed",
        metadata={
            **(req.metadata or {}),
            "source": "manual_rebuild",
            "mode": "force_workspace_rebuild",
        },
    )

    return {
        "ok": True,
        "event": event,
    }


@router.post("/stale-repair/{workspace_id}")
def queue_stale_repair(workspace_id: str) -> Dict[str, Any]:
    return {
        "ok": True,
        "result": queue_stale_repair_if_needed(workspace_id),
    }


@router.post("/mark-layer")
def mark_rebuilt(req: MarkLayerRebuiltRequest) -> Dict[str, Any]:
    state = mark_layer_rebuilt(
        workspace_id=req.workspace_id,
        layer=req.layer,
    )

    return {
        "ok": True,
        "state": state,
    }



@router.post("/sweep/{workspace_id}")
def run_rebuild_sweep(workspace_id: str) -> Dict[str, Any]:
    return {
        "ok": True,
        "sweep": run_stale_safety_sweep(workspace_id),
    }



@router.post("/process/{workspace_id}")
def process_rebuild_events(workspace_id: str, limit: int = 20) -> Dict[str, Any]:
    return {
        "ok": True,
        "result": process_rebuild_queue(workspace_id, limit=limit),
    }
