
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data/tms")
SUPPORT_ANALYTICS_AUDIT_PATH = DATA_DIR / "support_analytics_audit.jsonl"


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not SUPPORT_ANALYTICS_AUDIT_PATH.exists():
        SUPPORT_ANALYTICS_AUDIT_PATH.write_text("", encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_audit(payload: Dict[str, Any]) -> None:
    _ensure_store()

    with SUPPORT_ANALYTICS_AUDIT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _audit(metric_type: str, result: Dict[str, Any]) -> Dict[str, Any]:
    payload = {
        "metric_type": metric_type,
        "result": result,
        "created_at": _utc_now(),
    }

    _append_audit(payload)
    return result


# ============================================================
# 16.1.1 TICKET VOLUME ANALYTICS
# ============================================================

def ticket_volume_analytics(tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_status = Counter(str(t.get("status") or "unknown") for t in tickets)
    by_workspace = Counter(str(t.get("workspace_id") or "default") for t in tickets)

    result = {
        "total_tickets": len(tickets),
        "by_status": dict(by_status),
        "by_workspace": dict(by_workspace),
        "generated_at": _utc_now(),
    }

    return _audit("ticket_volume_analytics", result)


# ============================================================
# 16.1.2 SLA ANALYTICS
# ============================================================

def sla_analytics(tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    breached = 0
    at_risk = 0
    healthy = 0

    for ticket in tickets:
        sla_status = str(ticket.get("sla_status") or "unknown").lower()

        if sla_status in {"breached", "missed"}:
            breached += 1
        elif sla_status in {"at_risk", "warning"}:
            at_risk += 1
        else:
            healthy += 1

    result = {
        "total_tickets": len(tickets),
        "sla_breached": breached,
        "sla_at_risk": at_risk,
        "sla_healthy_or_unknown": healthy,
        "breach_rate_percent": round((breached / len(tickets)) * 100, 2) if tickets else 0,
        "generated_at": _utc_now(),
    }

    return _audit("sla_analytics", result)


# ============================================================
# 16.1.3 RESOLUTION ANALYTICS
# ============================================================

def resolution_analytics(tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    resolved = [
        t for t in tickets
        if str(t.get("status") or "").lower() in {"resolved", "closed", "solved"}
    ]

    unresolved = len(tickets) - len(resolved)

    result = {
        "total_tickets": len(tickets),
        "resolved_tickets": len(resolved),
        "unresolved_tickets": unresolved,
        "resolution_rate_percent": round((len(resolved) / len(tickets)) * 100, 2) if tickets else 0,
        "generated_at": _utc_now(),
    }

    return _audit("resolution_analytics", result)


# ============================================================
# 16.1.4 CATEGORY ANALYTICS
# ============================================================

def category_analytics(tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_category = Counter(str(t.get("category") or "uncategorized") for t in tickets)

    result = {
        "total_tickets": len(tickets),
        "by_category": dict(by_category),
        "top_categories": by_category.most_common(10),
        "generated_at": _utc_now(),
    }

    return _audit("category_analytics", result)


# ============================================================
# 16.1.5 STAFF PERFORMANCE ANALYTICS
# ============================================================

def staff_performance_analytics(tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    assigned = defaultdict(lambda: {"assigned": 0, "resolved": 0})

    for ticket in tickets:
        staff_id = str(ticket.get("assigned_to") or "unassigned")
        status = str(ticket.get("status") or "").lower()

        assigned[staff_id]["assigned"] += 1

        if status in {"resolved", "closed", "solved"}:
            assigned[staff_id]["resolved"] += 1

    result = {
        "staff": {
            staff_id: {
                **values,
                "resolution_rate_percent": round((values["resolved"] / values["assigned"]) * 100, 2)
                if values["assigned"]
                else 0,
            }
            for staff_id, values in assigned.items()
        },
        "generated_at": _utc_now(),
    }

    return _audit("staff_performance_analytics", result)


def build_support_analytics_report(tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "ticket_volume": ticket_volume_analytics(tickets),
        "sla": sla_analytics(tickets),
        "resolution": resolution_analytics(tickets),
        "category": category_analytics(tickets),
        "staff_performance": staff_performance_analytics(tickets),
        "generated_at": _utc_now(),
    }


def read_support_analytics_audit(limit: int = 1000) -> List[Dict[str, Any]]:
    _ensure_store()

    lines = SUPPORT_ANALYTICS_AUDIT_PATH.read_text(encoding="utf-8").splitlines()

    return [
        json.loads(line)
        for line in lines[-limit:]
        if line.strip()
    ]
