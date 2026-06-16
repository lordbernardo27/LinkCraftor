
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data/tms")
AI_AUTOMATION_AUDIT_PATH = DATA_DIR / "ai_automation_audit.jsonl"


@dataclass(frozen=True)
class AutomationDecision:
    decision_type: str
    ticket_id: str | None = None
    workspace_id: str | None = None
    allowed: bool = False
    requires_human_approval: bool = True
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not AI_AUTOMATION_AUDIT_PATH.exists():
        AI_AUTOMATION_AUDIT_PATH.write_text("", encoding="utf-8")


def _append_audit(payload: Dict[str, Any]) -> None:
    _ensure_store()

    with AI_AUTOMATION_AUDIT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def record_automation_decision(decision: AutomationDecision) -> Dict[str, Any]:
    payload = asdict(decision)
    _append_audit(payload)
    return payload


# ============================================================
# 15.1.1 AUTO-REPLY RULES
# ============================================================

def evaluate_auto_reply_rule(ticket: Dict[str, Any]) -> Dict[str, Any]:
    text = f"{ticket.get('subject', '')} {ticket.get('description', '')}".lower()

    safe_keywords = ["how to", "where is", "documentation", "guide", "help article"]

    allowed = any(k in text for k in safe_keywords)

    decision = AutomationDecision(
        decision_type="auto_reply",
        ticket_id=str(ticket.get("id")),
        workspace_id=ticket.get("workspace_id"),
        allowed=allowed,
        requires_human_approval=not allowed,
        reason="Safe informational request detected." if allowed else "Requires staff review before reply.",
        metadata={"matched_rule": "safe_informational_auto_reply" if allowed else None},
    )

    return record_automation_decision(decision)


# ============================================================
# 15.1.2 AUTO-CLOSE RULES
# ============================================================

def evaluate_auto_close_rule(ticket: Dict[str, Any]) -> Dict[str, Any]:
    status = str(ticket.get("status", "")).lower()
    customer_confirmed = bool(ticket.get("customer_confirmed_resolution"))

    allowed = status in {"resolved", "solved"} and customer_confirmed

    decision = AutomationDecision(
        decision_type="auto_close",
        ticket_id=str(ticket.get("id")),
        workspace_id=ticket.get("workspace_id"),
        allowed=allowed,
        requires_human_approval=not allowed,
        reason="Customer confirmed resolution." if allowed else "Ticket cannot be auto-closed yet.",
        metadata={
            "status": status,
            "customer_confirmed_resolution": customer_confirmed,
        },
    )

    return record_automation_decision(decision)


# ============================================================
# 15.1.3 AUTO-ROUTING RULES
# ============================================================

def evaluate_auto_routing_rule(ticket: Dict[str, Any]) -> Dict[str, Any]:
    category = str(ticket.get("category", "")).lower()

    routing_map = {
        "billing": "billing_team",
        "account_access": "support_team",
        "technical_issue": "engineering_support",
        "feature_request": "product_team",
        "general_support": "support_team",
    }

    target_queue = routing_map.get(category, "support_team")

    decision = AutomationDecision(
        decision_type="auto_routing",
        ticket_id=str(ticket.get("id")),
        workspace_id=ticket.get("workspace_id"),
        allowed=True,
        requires_human_approval=False,
        reason=f"Ticket routed to {target_queue}.",
        metadata={
            "category": category,
            "target_queue": target_queue,
        },
    )

    return record_automation_decision(decision)


# ============================================================
# 15.1.4 AUTO-TAGGING RULES
# ============================================================

def evaluate_auto_tagging_rule(ticket: Dict[str, Any]) -> Dict[str, Any]:
    text = f"{ticket.get('subject', '')} {ticket.get('description', '')}".lower()

    tags = []

    if "billing" in text or "payment" in text or "invoice" in text:
        tags.append("billing")

    if "bug" in text or "error" in text or "broken" in text:
        tags.append("bug")

    if "urgent" in text or "outage" in text or "down" in text:
        tags.append("urgent")

    if "feature" in text or "request" in text:
        tags.append("feature_request")

    decision = AutomationDecision(
        decision_type="auto_tagging",
        ticket_id=str(ticket.get("id")),
        workspace_id=ticket.get("workspace_id"),
        allowed=True,
        requires_human_approval=False,
        reason="Tags generated from ticket text.",
        metadata={
            "tags": tags,
        },
    )

    return record_automation_decision(decision)


# ============================================================
# 15.1.5 AUTO-ASSIGNMENT RULES
# ============================================================

def evaluate_auto_assignment_rule(
    *,
    ticket: Dict[str, Any],
    available_staff: List[Dict[str, Any]],
) -> Dict[str, Any]:
    category = str(ticket.get("category", "")).lower()

    matched_staff = None

    for staff in available_staff:
        skills = [str(s).lower() for s in staff.get("skills", [])]

        if category in skills:
            matched_staff = staff
            break

    if not matched_staff and available_staff:
        matched_staff = available_staff[0]

    allowed = matched_staff is not None

    decision = AutomationDecision(
        decision_type="auto_assignment",
        ticket_id=str(ticket.get("id")),
        workspace_id=ticket.get("workspace_id"),
        allowed=allowed,
        requires_human_approval=False if allowed else True,
        reason="Ticket assigned to matched staff." if allowed else "No available staff found.",
        metadata={
            "assigned_staff_id": matched_staff.get("id") if matched_staff else None,
            "category": category,
        },
    )

    return record_automation_decision(decision)


def build_safe_automation_package(
    *,
    ticket: Dict[str, Any],
    available_staff: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    return {
        "auto_reply": evaluate_auto_reply_rule(ticket),
        "auto_close": evaluate_auto_close_rule(ticket),
        "auto_routing": evaluate_auto_routing_rule(ticket),
        "auto_tagging": evaluate_auto_tagging_rule(ticket),
        "auto_assignment": evaluate_auto_assignment_rule(
            ticket=ticket,
            available_staff=available_staff or [],
        ),
    }


def read_ai_automation_audit(limit: int = 1000) -> List[Dict[str, Any]]:
    _ensure_store()

    lines = AI_AUTOMATION_AUDIT_PATH.read_text(encoding="utf-8").splitlines()

    return [
        json.loads(line)
        for line in lines[-limit:]
        if line.strip()
    ]
