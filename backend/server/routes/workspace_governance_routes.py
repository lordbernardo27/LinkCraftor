from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(
    prefix="/api/workspace-governance",
    tags=["workspace-governance"],
)


@router.get("/ping")
def workspace_governance_ping():
    return {
        "ok": True,
        "module": "workspace_governance",
        "status": "available",
    }

from backend.server.stores.workspace_governance import (
    get_workspace_governance_rules,
    load_workspace_state,
    generate_workspace_drift_report,
    generate_workspace_stale_report,
    generate_workspace_auto_repair_report,
    queue_rebuild_repair,
)


@router.get("/rules")
def get_workspace_governance_rules_route():
    return get_workspace_governance_rules()


@router.get("/state/{workspace_id}")
def get_workspace_governance_state_route(
    workspace_id: str,
):
    return load_workspace_state(workspace_id)


@router.get("/health/{workspace_id}")
def get_workspace_governance_health_route(
    workspace_id: str,
):
    state = load_workspace_state(workspace_id)

    return {
        "workspace_id": workspace_id,
        "status": state.get("current_status"),
        "health_score": state.get("health_score"),
        "last_checked_at": state.get("last_checked_at"),
        "last_validation_at": state.get("last_validation_at"),
    }


@router.get("/drift/{workspace_id}")
def get_workspace_governance_drift_route(
    workspace_id: str,
):
    return generate_workspace_drift_report(workspace_id)


@router.get("/stale/{workspace_id}")
def get_workspace_governance_stale_route(
    workspace_id: str,
):
    return generate_workspace_stale_report(workspace_id)


@router.post("/repair/{workspace_id}")
def post_workspace_governance_repair_route(
    workspace_id: str,
):
    repair_item = queue_rebuild_repair(
        workspace_id=workspace_id,
        reason="Repair requested via Workspace Governance API.",
    )

    return {
        "success": True,
        "workspace_id": workspace_id,
        "repair": repair_item,
    }


@router.get("/repair/{workspace_id}")
def get_workspace_governance_repair_report_route(
    workspace_id: str,
):
    return generate_workspace_auto_repair_report(workspace_id)

