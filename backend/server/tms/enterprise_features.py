
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data/tms")
ENTERPRISE_AUDIT_PATH = DATA_DIR / "enterprise_features_audit.jsonl"
ENTERPRISE_EXPORT_DIR = DATA_DIR / "enterprise_exports"


@dataclass(frozen=True)
class EnterpriseAccountConfig:
    workspace_id: str
    account_tier: str = "enterprise"
    dedicated_account_manager_id: str | None = None
    vip_enabled: bool = True
    enterprise_queue: str | None = None
    sla_overrides: Dict[str, Any] = field(default_factory=dict)
    reporting_enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ENTERPRISE_EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    if not ENTERPRISE_AUDIT_PATH.exists():
        ENTERPRISE_AUDIT_PATH.write_text("", encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_audit(payload: Dict[str, Any]) -> None:
    _ensure_store()

    with ENTERPRISE_AUDIT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _audit(event_type: str, workspace_id: str | None, metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = {
        "event_type": event_type,
        "workspace_id": workspace_id,
        "metadata": metadata or {},
        "created_at": _utc_now(),
    }

    _append_audit(payload)
    return payload


# ============================================================
# 19.1 ENTERPRISE QUEUES
# ============================================================

def enterprise_queue_name(
    *,
    workspace_id: str,
    queue_type: str = "support",
) -> str:
    safe_workspace = str(workspace_id or "default").replace(" ", "_")
    safe_queue = str(queue_type or "support").replace(" ", "_")

    return f"enterprise_{safe_workspace}_{safe_queue}_queue"


def attach_enterprise_queue(
    *,
    ticket: Dict[str, Any],
    queue_type: str = "support",
) -> Dict[str, Any]:
    workspace_id = str(ticket.get("workspace_id") or "default")

    return {
        **ticket,
        "enterprise_queue": enterprise_queue_name(
            workspace_id=workspace_id,
            queue_type=queue_type,
        ),
        "enterprise_routing": True,
    }


# ============================================================
# 19.2 DEDICATED ACCOUNT ROUTING
# ============================================================

def route_to_dedicated_account_manager(
    *,
    ticket: Dict[str, Any],
    account_config: Dict[str, Any],
) -> Dict[str, Any]:
    account_manager_id = account_config.get("dedicated_account_manager_id")

    routed = {
        **ticket,
        "assigned_to": account_manager_id or ticket.get("assigned_to"),
        "routing_reason": "dedicated_account_manager" if account_manager_id else "default_assignment",
        "enterprise_routing": bool(account_manager_id),
    }

    _audit(
        "dedicated_account_routing_applied",
        ticket.get("workspace_id"),
        {
            "ticket_id": ticket.get("id"),
            "assigned_to": routed.get("assigned_to"),
        },
    )

    return routed


# ============================================================
# 19.3 VIP ESCALATION FLOWS
# ============================================================

def apply_vip_escalation_flow(
    *,
    ticket: Dict[str, Any],
    account_config: Dict[str, Any],
    reason: str = "enterprise_vip_support",
) -> Dict[str, Any]:
    vip_enabled = bool(account_config.get("vip_enabled", True))

    updated = {
        **ticket,
        "vip": vip_enabled,
        "escalated": vip_enabled,
        "escalation_level": "vip_level_1" if vip_enabled else ticket.get("escalation_level", "none"),
        "escalation_reason": reason if vip_enabled else ticket.get("escalation_reason"),
    }

    _audit(
        "vip_escalation_flow_applied",
        ticket.get("workspace_id"),
        {
            "ticket_id": ticket.get("id"),
            "vip_enabled": vip_enabled,
            "escalation_level": updated.get("escalation_level"),
        },
    )

    return updated


# ============================================================
# 19.4 ENTERPRISE SLA OVERRIDES
# ============================================================

def resolve_enterprise_sla(
    *,
    account_config: Dict[str, Any],
    sla_type: str,
    default_minutes: int,
) -> Dict[str, Any]:
    overrides = account_config.get("sla_overrides") or {}
    minutes = int(overrides.get(sla_type, default_minutes))

    return {
        "workspace_id": account_config.get("workspace_id"),
        "sla_type": sla_type,
        "minutes": minutes,
        "source": "enterprise_override" if sla_type in overrides else "default",
    }


# ============================================================
# 19.5 ENTERPRISE REPORTING EXPORTS
# ============================================================

def export_enterprise_report_csv(
    *,
    workspace_id: str,
    report_name: str,
    rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    _ensure_store()

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    safe_report = str(report_name or "report").replace(" ", "_")
    path = ENTERPRISE_EXPORT_DIR / f"{workspace_id}_{safe_report}_{timestamp}.csv"

    fieldnames = sorted({key for row in rows for key in row.keys()}) if rows else ["empty"]

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow(row)

    payload = {
        "workspace_id": workspace_id,
        "report_name": report_name,
        "path": str(path),
        "row_count": len(rows),
        "created_at": _utc_now(),
    }

    _audit(
        "enterprise_report_exported",
        workspace_id,
        payload,
    )

    return payload


def build_enterprise_account_config(
    *,
    workspace_id: str,
    dedicated_account_manager_id: str | None = None,
    sla_overrides: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    config = EnterpriseAccountConfig(
        workspace_id=workspace_id,
        dedicated_account_manager_id=dedicated_account_manager_id,
        enterprise_queue=enterprise_queue_name(workspace_id=workspace_id),
        sla_overrides=sla_overrides or {},
    )

    payload = asdict(config)

    _audit(
        "enterprise_account_config_built",
        workspace_id,
        payload,
    )

    return payload


def read_enterprise_audit(limit: int = 1000) -> List[Dict[str, Any]]:
    _ensure_store()

    lines = ENTERPRISE_AUDIT_PATH.read_text(encoding="utf-8").splitlines()

    return [
        json.loads(line)
        for line in lines[-limit:]
        if line.strip()
    ]
