
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


DATA_DIR = Path("backend/server/data/tms")
AI_SAFETY_AUDIT_PATH = DATA_DIR / "ai_safety_constraints_audit.jsonl"


@dataclass(frozen=True)
class AISafetyDecision:
    constraint_type: str
    ticket_id: str | None = None
    workspace_id: str | None = None
    allowed: bool = False
    requires_human_approval: bool = True
    escalation_required: bool = False
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not AI_SAFETY_AUDIT_PATH.exists():
        AI_SAFETY_AUDIT_PATH.write_text("", encoding="utf-8")


def _append_audit(payload: Dict[str, Any]) -> None:
    _ensure_store()

    with AI_SAFETY_AUDIT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def record_ai_safety_decision(decision: AISafetyDecision) -> Dict[str, Any]:
    payload = asdict(decision)
    _append_audit(payload)
    return payload


# ============================================================
# 15.2.1 BILLING PROTECTION RULES
# ============================================================

def enforce_billing_protection(ticket: Dict[str, Any]) -> Dict[str, Any]:
    text = f"{ticket.get('subject', '')} {ticket.get('description', '')}".lower()

    billing_sensitive = any(
        word in text
        for word in ["charge", "payment", "invoice", "subscription", "plan", "billing"]
    )

    decision = AISafetyDecision(
        constraint_type="billing_protection",
        ticket_id=str(ticket.get("id")),
        workspace_id=ticket.get("workspace_id"),
        allowed=not billing_sensitive,
        requires_human_approval=billing_sensitive,
        reason=(
            "Billing-related request requires human review."
            if billing_sensitive
            else "No billing-sensitive request detected."
        ),
        metadata={
            "billing_sensitive": billing_sensitive,
        },
    )

    return record_ai_safety_decision(decision)


# ============================================================
# 15.2.2 REFUND APPROVAL GUARDRAILS
# ============================================================

def enforce_refund_guardrails(ticket: Dict[str, Any]) -> Dict[str, Any]:
    text = f"{ticket.get('subject', '')} {ticket.get('description', '')}".lower()

    refund_related = any(
        word in text
        for word in ["refund", "chargeback", "money back", "reversal", "cancel and refund"]
    )

    decision = AISafetyDecision(
        constraint_type="refund_guardrail",
        ticket_id=str(ticket.get("id")),
        workspace_id=ticket.get("workspace_id"),
        allowed=False if refund_related else True,
        requires_human_approval=refund_related,
        reason=(
            "AI must not approve refunds without human approval."
            if refund_related
            else "No refund approval risk detected."
        ),
        metadata={
            "refund_related": refund_related,
        },
    )

    return record_ai_safety_decision(decision)


# ============================================================
# 15.2.3 LEGAL RESPONSE RESTRICTIONS
# ============================================================

def enforce_legal_response_restrictions(ticket: Dict[str, Any]) -> Dict[str, Any]:
    text = f"{ticket.get('subject', '')} {ticket.get('description', '')}".lower()

    legal_sensitive = any(
        word in text
        for word in ["lawyer", "legal", "lawsuit", "sue", "court", "contract", "liability"]
    )

    decision = AISafetyDecision(
        constraint_type="legal_response_restriction",
        ticket_id=str(ticket.get("id")),
        workspace_id=ticket.get("workspace_id"),
        allowed=not legal_sensitive,
        requires_human_approval=legal_sensitive,
        escalation_required=legal_sensitive,
        reason=(
            "Legal-sensitive support request must be escalated for human handling."
            if legal_sensitive
            else "No legal-sensitive request detected."
        ),
        metadata={
            "legal_sensitive": legal_sensitive,
        },
    )

    return record_ai_safety_decision(decision)


# ============================================================
# 15.2.4 SECURITY ESCALATION ENFORCEMENT
# ============================================================

def enforce_security_escalation(ticket: Dict[str, Any]) -> Dict[str, Any]:
    text = f"{ticket.get('subject', '')} {ticket.get('description', '')}".lower()

    security_sensitive = any(
        word in text
        for word in [
            "security",
            "breach",
            "hacked",
            "compromised",
            "unauthorized",
            "data leak",
            "vulnerability",
        ]
    )

    decision = AISafetyDecision(
        constraint_type="security_escalation",
        ticket_id=str(ticket.get("id")),
        workspace_id=ticket.get("workspace_id"),
        allowed=not security_sensitive,
        requires_human_approval=security_sensitive,
        escalation_required=security_sensitive,
        reason=(
            "Security-sensitive support request requires escalation."
            if security_sensitive
            else "No security-sensitive request detected."
        ),
        metadata={
            "security_sensitive": security_sensitive,
        },
    )

    return record_ai_safety_decision(decision)


# ============================================================
# 15.2.5 HUMAN APPROVAL WORKFLOWS
# ============================================================

def require_human_approval(
    *,
    ticket: Dict[str, Any],
    action_type: str,
    reason: str,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    decision = AISafetyDecision(
        constraint_type="human_approval_workflow",
        ticket_id=str(ticket.get("id")),
        workspace_id=ticket.get("workspace_id"),
        allowed=False,
        requires_human_approval=True,
        escalation_required=False,
        reason=reason,
        metadata={
            "action_type": action_type,
            **(metadata or {}),
        },
    )

    return record_ai_safety_decision(decision)


def build_ai_safety_constraint_package(ticket: Dict[str, Any]) -> Dict[str, Any]:
    billing = enforce_billing_protection(ticket)
    refund = enforce_refund_guardrails(ticket)
    legal = enforce_legal_response_restrictions(ticket)
    security = enforce_security_escalation(ticket)

    requires_approval = any(
        item.get("requires_human_approval")
        for item in [billing, refund, legal, security]
    )

    escalation_required = any(
        item.get("escalation_required")
        for item in [billing, refund, legal, security]
    )

    return {
        "billing": billing,
        "refund": refund,
        "legal": legal,
        "security": security,
        "requires_human_approval": requires_approval,
        "escalation_required": escalation_required,
    }


def read_ai_safety_audit(limit: int = 1000) -> list[Dict[str, Any]]:
    _ensure_store()

    lines = AI_SAFETY_AUDIT_PATH.read_text(encoding="utf-8").splitlines()

    return [
        json.loads(line)
        for line in lines[-limit:]
        if line.strip()
    ]
