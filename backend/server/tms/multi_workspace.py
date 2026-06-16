
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data/tms")
WORKSPACE_AUDIT_PATH = DATA_DIR / "multi_workspace_audit.jsonl"
WORKSPACE_CONFIG_PATH = DATA_DIR / "workspace_configs.jsonl"


@dataclass(frozen=True)
class WorkspaceConfig:
    workspace_id: str
    name: str = ""
    isolated: bool = True
    queue_namespace: str | None = None
    permissions: Dict[str, List[str]] = field(default_factory=dict)
    sla_overrides: Dict[str, Any] = field(default_factory=dict)
    analytics_isolation: bool = True
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for path in (WORKSPACE_AUDIT_PATH, WORKSPACE_CONFIG_PATH):
        if not path.exists():
            path.write_text("", encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    _ensure_store()

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _read_jsonl(path: Path, limit: int = 1000) -> List[Dict[str, Any]]:
    _ensure_store()

    lines = path.read_text(encoding="utf-8").splitlines()

    return [
        json.loads(line)
        for line in lines[-limit:]
        if line.strip()
    ]


def _audit(event_type: str, workspace_id: str | None, metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = {
        "event_type": event_type,
        "workspace_id": workspace_id,
        "metadata": metadata or {},
        "created_at": _utc_now(),
    }

    _append_jsonl(WORKSPACE_AUDIT_PATH, payload)
    return payload


def create_workspace_config(
    *,
    workspace_id: str,
    name: str = "",
    permissions: Dict[str, List[str]] | None = None,
    sla_overrides: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    config = WorkspaceConfig(
        workspace_id=workspace_id,
        name=name,
        queue_namespace=f"workspace_{workspace_id}",
        permissions=permissions or {},
        sla_overrides=sla_overrides or {},
    )

    payload = asdict(config)
    _append_jsonl(WORKSPACE_CONFIG_PATH, payload)

    _audit(
        "workspace_config_created",
        workspace_id,
        {
            "name": name,
            "queue_namespace": config.queue_namespace,
        },
    )

    return payload


# ============================================================
# 18.1 WORKSPACE ISOLATION
# ============================================================

def assert_workspace_isolation(
    *,
    item: Dict[str, Any],
    workspace_id: str,
) -> bool:
    return str(item.get("workspace_id") or "") == str(workspace_id)


def filter_items_for_workspace(
    *,
    items: List[Dict[str, Any]],
    workspace_id: str,
) -> List[Dict[str, Any]]:
    return [
        item
        for item in items
        if assert_workspace_isolation(item=item, workspace_id=workspace_id)
    ]


# ============================================================
# 18.2 WORKSPACE-AWARE QUEUES
# ============================================================

def workspace_queue_name(
    *,
    workspace_id: str,
    queue_type: str,
) -> str:
    safe_workspace = str(workspace_id or "default").replace(" ", "_")
    safe_queue = str(queue_type or "general").replace(" ", "_")

    return f"workspace_{safe_workspace}_{safe_queue}"


def attach_workspace_queue_metadata(
    *,
    job: Dict[str, Any],
    workspace_id: str,
    queue_type: str,
) -> Dict[str, Any]:
    return {
        **job,
        "workspace_id": workspace_id,
        "workspace_queue": workspace_queue_name(
            workspace_id=workspace_id,
            queue_type=queue_type,
        ),
    }


# ============================================================
# 18.3 WORKSPACE-LEVEL PERMISSIONS
# ============================================================

def has_workspace_permission(
    *,
    user_id: str,
    action: str,
    workspace_config: Dict[str, Any],
) -> bool:
    permissions = workspace_config.get("permissions") or {}

    allowed_actions = permissions.get(user_id) or permissions.get("*") or []

    return action in allowed_actions or "admin" in allowed_actions


def enforce_workspace_permission(
    *,
    user_id: str,
    action: str,
    workspace_config: Dict[str, Any],
) -> Dict[str, Any]:
    allowed = has_workspace_permission(
        user_id=user_id,
        action=action,
        workspace_config=workspace_config,
    )

    return {
        "workspace_id": workspace_config.get("workspace_id"),
        "user_id": user_id,
        "action": action,
        "allowed": allowed,
        "checked_at": _utc_now(),
    }


# ============================================================
# 18.4 WORKSPACE SLA OVERRIDES
# ============================================================

def resolve_workspace_sla(
    *,
    workspace_config: Dict[str, Any],
    sla_type: str,
    default_minutes: int,
) -> Dict[str, Any]:
    overrides = workspace_config.get("sla_overrides") or {}

    minutes = int(overrides.get(sla_type, default_minutes))

    return {
        "workspace_id": workspace_config.get("workspace_id"),
        "sla_type": sla_type,
        "minutes": minutes,
        "source": "workspace_override" if sla_type in overrides else "default",
    }


# ============================================================
# 18.5 WORKSPACE ANALYTICS ISOLATION
# ============================================================

def workspace_analytics_scope(
    *,
    workspace_id: str,
    analytics_payload: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "workspace_id": workspace_id,
        "analytics_isolated": True,
        "payload": analytics_payload,
        "generated_at": _utc_now(),
    }


def build_workspace_context_package(
    *,
    workspace_id: str,
    tickets: List[Dict[str, Any]] | None = None,
    jobs: List[Dict[str, Any]] | None = None,
    workspace_config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    filtered_tickets = filter_items_for_workspace(
        items=tickets or [],
        workspace_id=workspace_id,
    )

    filtered_jobs = filter_items_for_workspace(
        items=jobs or [],
        workspace_id=workspace_id,
    )

    return {
        "workspace_id": workspace_id,
        "ticket_count": len(filtered_tickets),
        "job_count": len(filtered_jobs),
        "tickets": filtered_tickets,
        "jobs": filtered_jobs,
        "config": workspace_config,
        "generated_at": _utc_now(),
    }


def read_workspace_configs(limit: int = 1000) -> List[Dict[str, Any]]:
    return _read_jsonl(WORKSPACE_CONFIG_PATH, limit)


def read_multi_workspace_audit(limit: int = 1000) -> List[Dict[str, Any]]:
    return _read_jsonl(WORKSPACE_AUDIT_PATH, limit)
