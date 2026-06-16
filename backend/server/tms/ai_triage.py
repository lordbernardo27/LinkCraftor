
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data/tms")

AI_TRIAGE_AUDIT_PATH = DATA_DIR / "ai_triage_audit.jsonl"


@dataclass(frozen=True)
class AITriageEvent:
    event_type: str
    ticket_id: str | None = None
    workspace_id: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not AI_TRIAGE_AUDIT_PATH.exists():
        AI_TRIAGE_AUDIT_PATH.write_text("", encoding="utf-8")


def _append_audit(payload: Dict[str, Any]) -> None:
    _ensure_store()

    with AI_TRIAGE_AUDIT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def log_ai_triage_event(event: AITriageEvent) -> Dict[str, Any]:
    payload = asdict(event)
    _append_audit(payload)
    return payload


# ============================================================
# 14.2.1 AUTO-CATEGORIZATION
# ============================================================

def auto_categorize_ticket(ticket: Dict[str, Any]) -> Dict[str, Any]:
    text = f"{ticket.get('subject', '')} {ticket.get('description', '')}".lower()

    if any(word in text for word in ["payment", "billing", "invoice", "subscription", "refund"]):
        category = "billing"
    elif any(word in text for word in ["login", "password", "account", "access"]):
        category = "account_access"
    elif any(word in text for word in ["bug", "error", "broken", "failed", "not working"]):
        category = "technical_issue"
    elif any(word in text for word in ["feature", "request", "suggestion", "improve"]):
        category = "feature_request"
    else:
        category = "general_support"

    return {
        "ticket_id": ticket.get("id"),
        "category": category,
        "confidence": 0.75,
        "method": "rule_based_triage",
    }


# ============================================================
# 14.2.2 PRIORITY PREDICTION
# ============================================================

def predict_ticket_priority(ticket: Dict[str, Any]) -> Dict[str, Any]:
    text = f"{ticket.get('subject', '')} {ticket.get('description', '')}".lower()

    if any(word in text for word in ["urgent", "down", "outage", "security", "breach"]):
        priority = "urgent"
    elif any(word in text for word in ["failed", "cannot", "blocked", "broken"]):
        priority = "high"
    elif any(word in text for word in ["question", "how", "help"]):
        priority = "normal"
    else:
        priority = "normal"

    return {
        "ticket_id": ticket.get("id"),
        "priority": priority,
        "confidence": 0.72,
        "method": "rule_based_priority_prediction",
    }


# ============================================================
# 14.2.3 SEVERITY PREDICTION
# ============================================================

def predict_ticket_severity(ticket: Dict[str, Any]) -> Dict[str, Any]:
    text = f"{ticket.get('subject', '')} {ticket.get('description', '')}".lower()

    if any(word in text for word in ["outage", "data loss", "security breach", "system down"]):
        severity = "critical"
    elif any(word in text for word in ["cannot use", "failed payment", "blocked"]):
        severity = "major"
    elif any(word in text for word in ["bug", "error", "slow"]):
        severity = "minor"
    else:
        severity = "low"

    return {
        "ticket_id": ticket.get("id"),
        "severity": severity,
        "confidence": 0.70,
        "method": "rule_based_severity_prediction",
    }


# ============================================================
# 14.2.4 ESCALATION PREDICTION
# ============================================================

def predict_escalation_need(ticket: Dict[str, Any]) -> Dict[str, Any]:
    priority = predict_ticket_priority(ticket).get("priority")
    severity = predict_ticket_severity(ticket).get("severity")

    should_escalate = priority in {"urgent", "high"} or severity in {"critical", "major"}

    escalation_level = "none"

    if severity == "critical":
        escalation_level = "level_3"
    elif should_escalate:
        escalation_level = "level_2"

    return {
        "ticket_id": ticket.get("id"),
        "should_escalate": should_escalate,
        "escalation_level": escalation_level,
        "confidence": 0.73,
        "method": "priority_severity_combined",
    }


# ============================================================
# 14.2.5 DUPLICATE TICKET DETECTION
# ============================================================

def detect_duplicate_ticket(
    *,
    ticket: Dict[str, Any],
    existing_tickets: List[Dict[str, Any]],
) -> Dict[str, Any]:
    subject = str(ticket.get("subject", "")).lower().strip()
    description = str(ticket.get("description", "")).lower().strip()

    matches = []

    for existing in existing_tickets:
        existing_id = existing.get("id")
        existing_subject = str(existing.get("subject", "")).lower().strip()
        existing_description = str(existing.get("description", "")).lower().strip()

        score = 0

        if subject and subject == existing_subject:
            score += 0.6

        if description and description[:120] == existing_description[:120]:
            score += 0.4

        if score >= 0.6:
            matches.append(
                {
                    "ticket_id": existing_id,
                    "similarity_score": round(score, 2),
                }
            )

    return {
        "ticket_id": ticket.get("id"),
        "possible_duplicates": matches,
        "duplicate_count": len(matches),
    }


def build_ai_triage_package(
    *,
    ticket: Dict[str, Any],
    existing_tickets: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    package = {
        "category": auto_categorize_ticket(ticket),
        "priority": predict_ticket_priority(ticket),
        "severity": predict_ticket_severity(ticket),
        "escalation": predict_escalation_need(ticket),
        "duplicates": detect_duplicate_ticket(
            ticket=ticket,
            existing_tickets=existing_tickets or [],
        ),
    }

    log_ai_triage_event(
        AITriageEvent(
            event_type="ai_triage_package_generated",
            ticket_id=str(ticket.get("id")),
            workspace_id=ticket.get("workspace_id"),
            metadata=package,
        )
    )

    return package


def read_ai_triage_audit(limit: int = 1000) -> List[Dict[str, Any]]:
    _ensure_store()

    lines = AI_TRIAGE_AUDIT_PATH.read_text(encoding="utf-8").splitlines()

    return [
        json.loads(line)
        for line in lines[-limit:]
        if line.strip()
    ]
