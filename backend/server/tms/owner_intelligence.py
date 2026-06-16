
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data/tms")
OWNER_INTELLIGENCE_AUDIT_PATH = DATA_DIR / "owner_intelligence_audit.jsonl"


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not OWNER_INTELLIGENCE_AUDIT_PATH.exists():
        OWNER_INTELLIGENCE_AUDIT_PATH.write_text("", encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_audit(payload: Dict[str, Any]) -> None:
    _ensure_store()

    with OWNER_INTELLIGENCE_AUDIT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _audit(metric_type: str, result: Dict[str, Any]) -> Dict[str, Any]:
    payload = {
        "metric_type": metric_type,
        "result": result,
        "created_at": _utc_now(),
    }

    _append_audit(payload)
    return result


def global_support_health_dashboard(tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    open_tickets = sum(1 for t in tickets if str(t.get("status") or "").lower() in {"open", "pending", "in_progress"})
    resolved_tickets = sum(1 for t in tickets if str(t.get("status") or "").lower() in {"resolved", "closed", "solved"})
    escalated = sum(1 for t in tickets if bool(t.get("escalated")))

    result = {
        "total_tickets": len(tickets),
        "open_tickets": open_tickets,
        "resolved_tickets": resolved_tickets,
        "escalated_tickets": escalated,
        "generated_at": _utc_now(),
    }

    return _audit("global_support_health_dashboard", result)


def cross_workspace_support_intelligence(tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    workspace_counts = Counter(str(t.get("workspace_id") or "default") for t in tickets)

    result = {
        "workspace_count": len(workspace_counts),
        "tickets_by_workspace": dict(workspace_counts),
        "top_workspaces_by_ticket_volume": workspace_counts.most_common(10),
        "generated_at": _utc_now(),
    }

    return _audit("cross_workspace_support_intelligence", result)


def staff_performance_intelligence(tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    staff = defaultdict(lambda: {"assigned": 0, "resolved": 0, "escalated": 0})

    for ticket in tickets:
        staff_id = str(ticket.get("assigned_to") or "unassigned")
        status = str(ticket.get("status") or "").lower()

        staff[staff_id]["assigned"] += 1

        if status in {"resolved", "closed", "solved"}:
            staff[staff_id]["resolved"] += 1

        if bool(ticket.get("escalated")):
            staff[staff_id]["escalated"] += 1

    result = {
        "staff": dict(staff),
        "generated_at": _utc_now(),
    }

    return _audit("staff_performance_intelligence", result)


def ai_support_quality_monitoring(ai_events: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_type = Counter(str(e.get("event_type") or "unknown") for e in ai_events)

    result = {
        "total_ai_events": len(ai_events),
        "events_by_type": dict(by_type),
        "generated_at": _utc_now(),
    }

    return _audit("ai_support_quality_monitoring", result)


def revenue_impact_intelligence(customers: List[Dict[str, Any]]) -> Dict[str, Any]:
    revenue_at_risk = 0.0
    affected_accounts = 0

    for customer in customers:
        mrr = float(customer.get("mrr") or 0)
        status = str(customer.get("plan_status") or "").lower()

        if status in {"past_due", "canceling", "trial_ending"}:
            revenue_at_risk += mrr
            affected_accounts += 1

    result = {
        "revenue_at_risk": round(revenue_at_risk, 2),
        "affected_accounts": affected_accounts,
        "generated_at": _utc_now(),
    }

    return _audit("revenue_impact_intelligence", result)


def escalation_intelligence(tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    escalated = [
        t for t in tickets
        if bool(t.get("escalated")) or str(t.get("escalation_level") or "none") != "none"
    ]

    by_level = Counter(str(t.get("escalation_level") or "unknown") for t in escalated)

    result = {
        "total_tickets": len(tickets),
        "escalated_count": len(escalated),
        "escalation_rate_percent": round((len(escalated) / len(tickets)) * 100, 2) if tickets else 0,
        "by_level": dict(by_level),
        "generated_at": _utc_now(),
    }

    return _audit("escalation_intelligence", result)


def outage_intelligence(tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    outage_terms = ["outage", "down", "system down", "not loading", "unavailable"]

    outage_tickets = []

    for ticket in tickets:
        text = f"{ticket.get('subject', '')} {ticket.get('description', '')}".lower()

        if any(term in text for term in outage_terms):
            outage_tickets.append(ticket)

    result = {
        "outage_ticket_count": len(outage_tickets),
        "outage_signal_detected": len(outage_tickets) >= 3,
        "sample_ticket_ids": [t.get("id") for t in outage_tickets[:10]],
        "generated_at": _utc_now(),
    }

    return _audit("outage_intelligence", result)


def support_bottleneck_analysis(tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    status_counts = Counter(str(t.get("status") or "unknown") for t in tickets)
    category_counts = Counter(str(t.get("category") or "uncategorized") for t in tickets)

    bottlenecks = []

    for status, count in status_counts.items():
        if count >= 5:
            bottlenecks.append({
                "type": "status_backlog",
                "name": status,
                "count": count,
            })

    for category, count in category_counts.items():
        if count >= 5:
            bottlenecks.append({
                "type": "category_pressure",
                "name": category,
                "count": count,
            })

    result = {
        "bottlenecks": bottlenecks,
        "bottleneck_count": len(bottlenecks),
        "generated_at": _utc_now(),
    }

    return _audit("support_bottleneck_analysis", result)


def build_owner_intelligence_report(
    *,
    tickets: List[Dict[str, Any]],
    customers: List[Dict[str, Any]] | None = None,
    ai_events: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    return {
        "global_support_health": global_support_health_dashboard(tickets),
        "cross_workspace": cross_workspace_support_intelligence(tickets),
        "staff_performance": staff_performance_intelligence(tickets),
        "ai_support_quality": ai_support_quality_monitoring(ai_events or []),
        "revenue_impact": revenue_impact_intelligence(customers or []),
        "escalation": escalation_intelligence(tickets),
        "outage": outage_intelligence(tickets),
        "bottlenecks": support_bottleneck_analysis(tickets),
        "generated_at": _utc_now(),
    }


def read_owner_intelligence_audit(limit: int = 1000) -> List[Dict[str, Any]]:
    _ensure_store()

    lines = OWNER_INTELLIGENCE_AUDIT_PATH.read_text(encoding="utf-8").splitlines()

    return [
        json.loads(line)
        for line in lines[-limit:]
        if line.strip()
    ]
