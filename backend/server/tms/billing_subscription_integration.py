
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data/tms")
BILLING_SUPPORT_AUDIT_PATH = DATA_DIR / "billing_support_audit.jsonl"
REFUND_WORKFLOW_PATH = DATA_DIR / "refund_workflows.jsonl"


@dataclass(frozen=True)
class BillingSupportDecision:
    decision_type: str
    ticket_id: str | None = None
    workspace_id: str | None = None
    customer_id: str | None = None
    allowed: bool = True
    requires_billing_review: bool = False
    requires_human_approval: bool = False
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class RefundWorkflow:
    refund_id: str
    ticket_id: str
    customer_id: str | None = None
    workspace_id: str | None = None
    amount: float = 0.0
    currency: str = "USD"
    status: str = "pending_review"
    reason: str = ""
    requires_human_approval: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for path in (BILLING_SUPPORT_AUDIT_PATH, REFUND_WORKFLOW_PATH):
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


def record_billing_support_decision(decision: BillingSupportDecision) -> Dict[str, Any]:
    payload = asdict(decision)
    _append_jsonl(BILLING_SUPPORT_AUDIT_PATH, payload)
    return payload


# ============================================================
# 20.1 BILLING-AWARE SUPPORT LOGIC
# ============================================================

def evaluate_billing_aware_support_logic(
    *,
    ticket: Dict[str, Any],
    subscription: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    text = f"{ticket.get('subject', '')} {ticket.get('description', '')}".lower()
    subscription_status = str((subscription or {}).get("status") or "unknown").lower()

    billing_related = any(
        term in text
        for term in ["billing", "invoice", "payment", "charge", "subscription", "plan", "refund"]
    )

    requires_review = billing_related or subscription_status in {"past_due", "canceled", "canceling"}

    decision = BillingSupportDecision(
        decision_type="billing_aware_support_logic",
        ticket_id=str(ticket.get("id")),
        workspace_id=ticket.get("workspace_id"),
        customer_id=ticket.get("customer_id"),
        allowed=True,
        requires_billing_review=requires_review,
        requires_human_approval=requires_review,
        reason="Billing-sensitive support context detected." if requires_review else "No billing-sensitive support context detected.",
        metadata={
            "billing_related": billing_related,
            "subscription_status": subscription_status,
        },
    )

    return record_billing_support_decision(decision)


# ============================================================
# 20.2 FAILED PAYMENT ALERTS
# ============================================================

def build_failed_payment_alert(
    *,
    customer_id: str,
    workspace_id: str | None = None,
    invoice_id: str | None = None,
    amount_due: float = 0.0,
    currency: str = "USD",
) -> Dict[str, Any]:
    alert = {
        "alert_type": "failed_payment",
        "customer_id": customer_id,
        "workspace_id": workspace_id,
        "invoice_id": invoice_id,
        "amount_due": amount_due,
        "currency": currency,
        "severity": "high",
        "created_at": _utc_now(),
    }

    record_billing_support_decision(
        BillingSupportDecision(
            decision_type="failed_payment_alert_created",
            workspace_id=workspace_id,
            customer_id=customer_id,
            allowed=True,
            requires_billing_review=True,
            requires_human_approval=True,
            reason="Failed payment alert created.",
            metadata=alert,
        )
    )

    return alert


# ============================================================
# 20.3 SUBSCRIPTION METADATA LINKAGE
# ============================================================

def link_subscription_metadata_to_ticket(
    *,
    ticket: Dict[str, Any],
    subscription: Dict[str, Any],
) -> Dict[str, Any]:
    linked = {
        **ticket,
        "subscription": {
            "subscription_id": subscription.get("id"),
            "status": subscription.get("status"),
            "plan": subscription.get("plan"),
            "mrr": subscription.get("mrr"),
            "renewal_date": subscription.get("renewal_date"),
        },
    }

    record_billing_support_decision(
        BillingSupportDecision(
            decision_type="subscription_metadata_linked",
            ticket_id=str(ticket.get("id")),
            workspace_id=ticket.get("workspace_id"),
            customer_id=ticket.get("customer_id"),
            allowed=True,
            reason="Subscription metadata linked to ticket.",
            metadata=linked.get("subscription", {}),
        )
    )

    return linked


# ============================================================
# 20.4 PLAN-AWARE ROUTING
# ============================================================

def plan_aware_routing(
    *,
    ticket: Dict[str, Any],
    subscription: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    plan = str((subscription or {}).get("plan") or ticket.get("plan") or "standard").lower()

    if plan in {"enterprise", "business"}:
        target_queue = "priority_support"
    elif plan in {"pro"}:
        target_queue = "standard_support"
    else:
        target_queue = "general_support"

    routed = {
        **ticket,
        "support_plan": plan,
        "target_queue": target_queue,
        "routing_reason": "plan_aware_routing",
    }

    record_billing_support_decision(
        BillingSupportDecision(
            decision_type="plan_aware_routing_applied",
            ticket_id=str(ticket.get("id")),
            workspace_id=ticket.get("workspace_id"),
            customer_id=ticket.get("customer_id"),
            allowed=True,
            reason=f"Ticket routed to {target_queue}.",
            metadata={
                "plan": plan,
                "target_queue": target_queue,
            },
        )
    )

    return routed


# ============================================================
# 20.5 REFUND WORKFLOW SYSTEM
# ============================================================

def create_refund_workflow(
    *,
    ticket_id: str,
    customer_id: str | None = None,
    workspace_id: str | None = None,
    amount: float = 0.0,
    currency: str = "USD",
    reason: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    refund_id = f"refund_{ticket_id}_{timestamp}"

    workflow = RefundWorkflow(
        refund_id=refund_id,
        ticket_id=ticket_id,
        customer_id=customer_id,
        workspace_id=workspace_id,
        amount=amount,
        currency=currency,
        reason=reason,
        metadata=metadata or {},
    )

    payload = asdict(workflow)
    _append_jsonl(REFUND_WORKFLOW_PATH, payload)

    record_billing_support_decision(
        BillingSupportDecision(
            decision_type="refund_workflow_created",
            ticket_id=ticket_id,
            workspace_id=workspace_id,
            customer_id=customer_id,
            allowed=False,
            requires_billing_review=True,
            requires_human_approval=True,
            reason="Refund workflow created and requires human approval.",
            metadata=payload,
        )
    )

    return payload


def read_refund_workflows(limit: int = 1000) -> List[Dict[str, Any]]:
    return _read_jsonl(REFUND_WORKFLOW_PATH, limit)


def read_billing_support_audit(limit: int = 1000) -> List[Dict[str, Any]]:
    return _read_jsonl(BILLING_SUPPORT_AUDIT_PATH, limit)
