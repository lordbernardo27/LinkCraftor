
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SLA_DATA_DIR = Path("backend/server/data/tms")
SLA_EVENT_LOG_PATH = SLA_DATA_DIR / "sla_events.jsonl"


@dataclass(frozen=True)
class SLAEvent:
    event_type: str
    ticket_id: str
    workspace_id: str | None = None
    priority: str | None = None
    severity: str | None = None
    status: str | None = None
    breached: bool = False
    escalation_level: str | None = None
    route_to: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def _ensure_sla_store() -> None:
    SLA_DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not SLA_EVENT_LOG_PATH.exists():
        SLA_EVENT_LOG_PATH.write_text("", encoding="utf-8")


def log_sla_event(event: SLAEvent) -> None:
    _ensure_sla_store()

    with SLA_EVENT_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")


def log_escalation_audit_trail(
    ticket_id: str,
    escalation_level: str,
    route_to: str,
    reason: str,
    workspace_id: str | None = None,
    priority: str | None = None,
    severity: str | None = None,
) -> None:
    log_sla_event(
        SLAEvent(
            event_type="escalation_audit_trail",
            ticket_id=ticket_id,
            workspace_id=workspace_id,
            priority=priority,
            severity=severity,
            escalation_level=escalation_level,
            route_to=route_to,
            metadata={"reason": reason},
        )
    )


def read_sla_events(limit: int = 500) -> List[Dict[str, Any]]:
    _ensure_sla_store()

    lines = SLA_EVENT_LOG_PATH.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[-limit:] if line.strip()]


def build_sla_breach_analytics(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    breach_events = [
        event for event in events
        if event.get("breached") or event.get("event_type") == "sla_breach"
    ]

    by_priority: Dict[str, int] = {}
    by_workspace: Dict[str, int] = {}

    for event in breach_events:
        priority = str(event.get("priority") or "unknown")
        workspace_id = str(event.get("workspace_id") or "unknown")

        by_priority[priority] = by_priority.get(priority, 0) + 1
        by_workspace[workspace_id] = by_workspace.get(workspace_id, 0) + 1

    return {
        "total_breaches": len(breach_events),
        "breaches_by_priority": by_priority,
        "breaches_by_workspace": by_workspace,
    }


def build_sla_dashboard_metrics(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_events = len(events)
    breach_analytics = build_sla_breach_analytics(events)

    escalation_events = [
        event for event in events
        if event.get("event_type") == "escalation_audit_trail"
    ]

    return {
        "total_sla_events": total_events,
        "total_breaches": breach_analytics["total_breaches"],
        "total_escalations": len(escalation_events),
        "breaches_by_priority": breach_analytics["breaches_by_priority"],
        "breaches_by_workspace": breach_analytics["breaches_by_workspace"],
    }


def build_sla_compliance_report(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    metrics = build_sla_dashboard_metrics(events)

    total_events = max(metrics["total_sla_events"], 1)
    total_breaches = metrics["total_breaches"]

    compliance_rate = round(((total_events - total_breaches) / total_events) * 100, 2)

    return {
        "compliance_rate_percent": compliance_rate,
        "total_sla_events": metrics["total_sla_events"],
        "total_breaches": total_breaches,
        "total_escalations": metrics["total_escalations"],
        "breaches_by_priority": metrics["breaches_by_priority"],
        "breaches_by_workspace": metrics["breaches_by_workspace"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
