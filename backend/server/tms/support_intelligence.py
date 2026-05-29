
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass(frozen=True)
class SupportIntelligenceResult:
    ticket_id: str
    workspace_id: str
    linked_product_context: List[Dict[str, Any]] = field(default_factory=list)
    incident_detected: bool = False
    repeated_issue_detected: bool = False
    escalation_score: int = 0
    churn_risk_signal: str = "low"
    support_priority: str = "normal"
    reasons: List[str] = field(default_factory=list)
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def link_ticket_to_product_context(
    ticket: Dict[str, Any],
    product_events: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    workspace_id = ticket.get("workspace_id") or ticket.get("workspace")
    ticket_keywords = " ".join(
        [
            str(ticket.get("title") or ""),
            str(ticket.get("description") or ""),
            str(ticket.get("category") or ""),
        ]
    ).lower()

    linked: List[Dict[str, Any]] = []

    for event in product_events:
        if workspace_id and event.get("workspace_id") != workspace_id:
            continue

        event_text = " ".join(
            [
                str(event.get("title") or ""),
                str(event.get("description") or ""),
                str(event.get("event_type") or ""),
                str(event.get("source") or ""),
            ]
        ).lower()

        if any(token in event_text for token in ticket_keywords.split() if len(token) >= 5):
            linked.append(event)

    return linked[:10]


def detect_workspace_incident(product_events: List[Dict[str, Any]]) -> bool:
    severe_events = [
        event for event in product_events
        if str(event.get("severity")) in {"error", "critical", "warning"}
    ]

    return len(severe_events) >= 3


def detect_repeated_issue(
    ticket: Dict[str, Any],
    previous_tickets: List[Dict[str, Any]],
) -> bool:
    workspace_id = ticket.get("workspace_id") or ticket.get("workspace")
    category = ticket.get("category")
    title = str(ticket.get("title") or "").lower()

    matches = 0

    for previous in previous_tickets:
        if previous.get("id") == ticket.get("id"):
            continue

        same_workspace = (previous.get("workspace_id") or previous.get("workspace")) == workspace_id
        same_category = previous.get("category") == category
        previous_title = str(previous.get("title") or "").lower()

        shared_title_terms = {
            token for token in title.split()
            if len(token) >= 5 and token in previous_title
        }

        if same_workspace and (same_category or len(shared_title_terms) >= 2):
            matches += 1

    return matches >= 2


def calculate_escalation_intelligence_score(
    ticket: Dict[str, Any],
    linked_events: List[Dict[str, Any]],
    repeated_issue: bool,
) -> int:
    score = 0

    priority = str(ticket.get("priority") or "Medium")
    severity = str(ticket.get("severity") or "Normal")
    status = str(ticket.get("status") or "Open")

    if priority == "Urgent":
        score += 35
    elif priority == "High":
        score += 25
    elif priority == "Medium":
        score += 10

    if severity == "Critical":
        score += 35
    elif severity == "Major":
        score += 20

    if status in {"Escalated", "Open"}:
        score += 10

    if repeated_issue:
        score += 20

    critical_events = [
        event for event in linked_events
        if str(event.get("severity")) in {"critical", "error"}
    ]

    score += min(30, len(critical_events) * 10)

    return max(0, min(100, score))


def calculate_churn_risk_support_signal(
    ticket: Dict[str, Any],
    repeated_issue: bool,
    escalation_score: int,
) -> str:
    priority = str(ticket.get("priority") or "Medium")
    status = str(ticket.get("status") or "Open")

    if escalation_score >= 80 or repeated_issue and priority in {"High", "Urgent"}:
        return "high"

    if escalation_score >= 50 or status == "Waiting on Customer":
        return "medium"

    return "low"


def calculate_support_priority(
    ticket: Dict[str, Any],
    incident_detected: bool,
    repeated_issue: bool,
    escalation_score: int,
    churn_risk_signal: str,
) -> str:
    if incident_detected or escalation_score >= 85 or churn_risk_signal == "high":
        return "critical"

    if repeated_issue or escalation_score >= 60:
        return "high"

    if escalation_score >= 35 or churn_risk_signal == "medium":
        return "elevated"

    return "normal"


def build_support_intelligence(
    ticket: Dict[str, Any],
    product_events: List[Dict[str, Any]],
    previous_tickets: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    previous_tickets = previous_tickets or []

    ticket_id = str(ticket.get("id") or ticket.get("ticket_id") or "unknown")
    workspace_id = str(ticket.get("workspace_id") or ticket.get("workspace") or "unknown")

    linked_events = link_ticket_to_product_context(ticket, product_events)
    incident_detected = detect_workspace_incident(linked_events)
    repeated_issue = detect_repeated_issue(ticket, previous_tickets)

    escalation_score = calculate_escalation_intelligence_score(
        ticket=ticket,
        linked_events=linked_events,
        repeated_issue=repeated_issue,
    )

    churn_risk_signal = calculate_churn_risk_support_signal(
        ticket=ticket,
        repeated_issue=repeated_issue,
        escalation_score=escalation_score,
    )

    support_priority = calculate_support_priority(
        ticket=ticket,
        incident_detected=incident_detected,
        repeated_issue=repeated_issue,
        escalation_score=escalation_score,
        churn_risk_signal=churn_risk_signal,
    )

    reasons: List[str] = []

    if linked_events:
        reasons.append("linked_product_activity_found")

    if incident_detected:
        reasons.append("workspace_incident_detected")

    if repeated_issue:
        reasons.append("repeated_issue_detected")

    if escalation_score >= 60:
        reasons.append("high_escalation_score")

    if churn_risk_signal != "low":
        reasons.append("churn_risk_support_signal")

    result = SupportIntelligenceResult(
        ticket_id=ticket_id,
        workspace_id=workspace_id,
        linked_product_context=linked_events,
        incident_detected=incident_detected,
        repeated_issue_detected=repeated_issue,
        escalation_score=escalation_score,
        churn_risk_signal=churn_risk_signal,
        support_priority=support_priority,
        reasons=reasons,
    )

    return asdict(result)
