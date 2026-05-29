
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

from backend.server.tms.sla_timers import calculate_sla_timer_state


@dataclass(frozen=True)
class EscalationDecision:
    ticket_id: str
    should_escalate: bool
    escalation_level: str
    route_to: str
    reason: str
    severity: str
    created_at: str


TECHNICAL_CATEGORIES = {"Technical", "Import", "Engine", "Upload", "Runtime"}
BILLING_CATEGORIES = {"Billing", "Invoice", "Payment", "Subscription"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def route_escalation_by_severity(ticket: Dict[str, Any]) -> tuple[str, str]:
    category = str(ticket.get("category") or "")
    severity = str(ticket.get("severity") or "Normal")
    priority = str(ticket.get("priority") or "Medium")

    if severity == "Critical" or priority == "Urgent":
        return "owner", "owner_escalation"

    if category in TECHNICAL_CATEGORIES:
        return "engineering", "engineering_escalation"

    if category in BILLING_CATEGORIES:
        return "billing", "billing_escalation"

    if severity == "Major" or priority == "High":
        return "manager", "manager_escalation"

    return "support", "support_review"


def evaluate_escalation(
    ticket: Dict[str, Any],
    workspace_tier: str = "default",
) -> Dict[str, Any]:
    ticket_id = str(ticket.get("id") or ticket.get("ticket_id") or "unknown")
    severity = str(ticket.get("severity") or "Normal")

    sla_state = calculate_sla_timer_state(
        ticket=ticket,
        workspace_tier=workspace_tier,
    )

    route_to, escalation_level = route_escalation_by_severity(ticket)

    should_escalate = bool(
        sla_state.get("escalation_due")
        or sla_state.get("resolution_breached")
        or severity == "Critical"
        or str(ticket.get("priority")) == "Urgent"
    )

    reason = "No escalation required."

    if sla_state.get("resolution_breached"):
        reason = "Resolution SLA breached."
    elif sla_state.get("escalation_due"):
        reason = "Escalation countdown reached."
    elif severity == "Critical":
        reason = "Critical severity requires escalation."
    elif str(ticket.get("priority")) == "Urgent":
        reason = "Urgent priority requires escalation."

    decision = EscalationDecision(
        ticket_id=ticket_id,
        should_escalate=should_escalate,
        escalation_level=escalation_level if should_escalate else "none",
        route_to=route_to if should_escalate else "none",
        reason=reason,
        severity=severity,
        created_at=_now_iso(),
    )

    return asdict(decision)


def evaluate_escalations_for_tickets(
    tickets: List[Dict[str, Any]],
    workspace_tier: str = "default",
) -> List[Dict[str, Any]]:
    decisions: List[Dict[str, Any]] = []

    for ticket in tickets:
        decision = evaluate_escalation(ticket, workspace_tier=workspace_tier)

        if decision["should_escalate"]:
            decisions.append(decision)

    return decisions


def build_engineering_escalation(ticket: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "ticket_id": ticket.get("id") or ticket.get("ticket_id"),
        "route_to": "engineering",
        "queue": "pending_engineering",
        "reason": "Technical issue requires engineering investigation.",
    }


def build_billing_escalation(ticket: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "ticket_id": ticket.get("id") or ticket.get("ticket_id"),
        "route_to": "billing",
        "queue": "billing_escalation",
        "reason": "Billing or subscription issue requires billing review.",
    }


def build_manager_escalation(ticket: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "ticket_id": ticket.get("id") or ticket.get("ticket_id"),
        "route_to": "manager",
        "queue": "manager_escalation",
        "reason": "High-severity operational issue requires manager review.",
    }


def build_owner_escalation(ticket: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "ticket_id": ticket.get("id") or ticket.get("ticket_id"),
        "route_to": "owner",
        "queue": "owner_escalation",
        "reason": "Critical, urgent, or founder-level issue requires owner visibility.",
    }


def build_escalation_payload(ticket: Dict[str, Any]) -> Dict[str, Any]:
    route_to, escalation_level = route_escalation_by_severity(ticket)

    if route_to == "engineering":
        payload = build_engineering_escalation(ticket)
    elif route_to == "billing":
        payload = build_billing_escalation(ticket)
    elif route_to == "manager":
        payload = build_manager_escalation(ticket)
    elif route_to == "owner":
        payload = build_owner_escalation(ticket)
    else:
        payload = {
            "ticket_id": ticket.get("id") or ticket.get("ticket_id"),
            "route_to": "support",
            "queue": "support_review",
            "reason": "Ticket remains in support review.",
        }

    payload["escalation_level"] = escalation_level
    payload["created_at"] = _now_iso()

    return payload
