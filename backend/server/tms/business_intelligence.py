
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data/tms")
BUSINESS_INTELLIGENCE_AUDIT_PATH = DATA_DIR / "business_intelligence_audit.jsonl"


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not BUSINESS_INTELLIGENCE_AUDIT_PATH.exists():
        BUSINESS_INTELLIGENCE_AUDIT_PATH.write_text("", encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_audit(payload: Dict[str, Any]) -> None:
    _ensure_store()

    with BUSINESS_INTELLIGENCE_AUDIT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _audit(metric_type: str, result: Dict[str, Any]) -> Dict[str, Any]:
    payload = {
        "metric_type": metric_type,
        "result": result,
        "created_at": _utc_now(),
    }

    _append_audit(payload)
    return result


def churn_risk_detection(customers: List[Dict[str, Any]]) -> Dict[str, Any]:
    at_risk = []

    for customer in customers:
        risk_score = 0

        if int(customer.get("open_tickets") or 0) >= 3:
            risk_score += 30

        if int(customer.get("sla_breaches") or 0) >= 1:
            risk_score += 25

        if int(customer.get("days_since_last_login") or 0) >= 30:
            risk_score += 20

        if str(customer.get("plan_status") or "").lower() in {"past_due", "trial_ending"}:
            risk_score += 25

        if risk_score >= 50:
            at_risk.append({
                "customer_id": customer.get("id"),
                "workspace_id": customer.get("workspace_id"),
                "risk_score": risk_score,
            })

    result = {
        "customers_scanned": len(customers),
        "at_risk_customers": at_risk,
        "at_risk_count": len(at_risk),
        "generated_at": _utc_now(),
    }

    return _audit("churn_risk_detection", result)


def revenue_risk_analysis(customers: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_risk_revenue = 0.0
    risky_accounts = []

    for customer in customers:
        status = str(customer.get("plan_status") or "").lower()
        mrr = float(customer.get("mrr") or 0)

        if status in {"past_due", "canceling", "trial_ending"}:
            total_risk_revenue += mrr
            risky_accounts.append({
                "customer_id": customer.get("id"),
                "workspace_id": customer.get("workspace_id"),
                "plan_status": status,
                "mrr": mrr,
            })

    result = {
        "risky_account_count": len(risky_accounts),
        "monthly_revenue_at_risk": round(total_risk_revenue, 2),
        "risky_accounts": risky_accounts,
        "generated_at": _utc_now(),
    }

    return _audit("revenue_risk_analysis", result)


def product_pain_point_analysis(tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    pain_points = Counter()

    for ticket in tickets:
        area = (
            ticket.get("product_area")
            or ticket.get("module")
            or ticket.get("category")
            or "unknown"
        )

        pain_points[str(area)] += 1

    result = {
        "total_tickets": len(tickets),
        "pain_points": dict(pain_points),
        "top_pain_points": pain_points.most_common(10),
        "generated_at": _utc_now(),
    }

    return _audit("product_pain_point_analysis", result)


def escalation_trend_analysis(tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    escalations = [
        t for t in tickets
        if bool(t.get("escalated")) or str(t.get("escalation_level") or "none") != "none"
    ]

    by_level = Counter(str(t.get("escalation_level") or "unknown") for t in escalations)
    by_category = Counter(str(t.get("category") or "uncategorized") for t in escalations)

    result = {
        "total_tickets": len(tickets),
        "escalated_tickets": len(escalations),
        "escalation_rate_percent": round((len(escalations) / len(tickets)) * 100, 2) if tickets else 0,
        "by_level": dict(by_level),
        "by_category": dict(by_category),
        "generated_at": _utc_now(),
    }

    return _audit("escalation_trend_analysis", result)


def feature_request_analytics(tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    feature_tickets = []

    for ticket in tickets:
        category = str(ticket.get("category") or "").lower()
        text = f"{ticket.get('subject', '')} {ticket.get('description', '')}".lower()

        if category == "feature_request" or "feature request" in text or "suggestion" in text:
            feature_tickets.append(ticket)

    requested_terms = Counter()

    for ticket in feature_tickets:
        for word in str(ticket.get("subject") or "").lower().split():
            if len(word) >= 4:
                requested_terms[word] += 1

    result = {
        "total_tickets": len(tickets),
        "feature_request_count": len(feature_tickets),
        "feature_request_rate_percent": round((len(feature_tickets) / len(tickets)) * 100, 2) if tickets else 0,
        "top_feature_terms": requested_terms.most_common(20),
        "generated_at": _utc_now(),
    }

    return _audit("feature_request_analytics", result)


def build_business_intelligence_report(
    *,
    tickets: List[Dict[str, Any]],
    customers: List[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "churn_risk": churn_risk_detection(customers),
        "revenue_risk": revenue_risk_analysis(customers),
        "product_pain_points": product_pain_point_analysis(tickets),
        "escalation_trends": escalation_trend_analysis(tickets),
        "feature_requests": feature_request_analytics(tickets),
        "generated_at": _utc_now(),
    }


def read_business_intelligence_audit(limit: int = 1000) -> List[Dict[str, Any]]:
    _ensure_store()

    lines = BUSINESS_INTELLIGENCE_AUDIT_PATH.read_text(encoding="utf-8").splitlines()

    return [
        json.loads(line)
        for line in lines[-limit:]
        if line.strip()
    ]
