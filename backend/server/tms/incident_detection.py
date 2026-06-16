
from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.server.tms.incident_management import create_incident


DATA_DIR = Path("backend/server/data/tms")

INCIDENT_DETECTION_AUDIT_PATH = DATA_DIR / "incident_detection_audit.jsonl"


@dataclass(frozen=True)
class IncidentDetectionSignal:
    signal_type: str
    detected: bool
    severity: str = "sev_2"
    confidence: float = 0.0
    affected_services: List[str] = field(default_factory=list)
    affected_workspaces: List[str] = field(default_factory=list)
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not INCIDENT_DETECTION_AUDIT_PATH.exists():
        INCIDENT_DETECTION_AUDIT_PATH.write_text("", encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_audit(payload: Dict[str, Any]) -> None:
    _ensure_store()

    with INCIDENT_DETECTION_AUDIT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def record_detection_signal(signal: IncidentDetectionSignal) -> Dict[str, Any]:
    payload = asdict(signal)
    _append_audit(payload)
    return payload


# ============================================================
# 21.2.1 OUTAGE DETECTION
# ============================================================

def detect_outage(
    *,
    tickets: List[Dict[str, Any]],
    threshold: int = 3,
) -> Dict[str, Any]:
    outage_terms = ["outage", "down", "system down", "not loading", "unavailable", "cannot access"]

    matched = []

    for ticket in tickets:
        text = f"{ticket.get('subject', '')} {ticket.get('description', '')}".lower()

        if any(term in text for term in outage_terms):
            matched.append(ticket)

    detected = len(matched) >= threshold

    signal = IncidentDetectionSignal(
        signal_type="outage_detection",
        detected=detected,
        severity="sev_0" if detected else "sev_2",
        confidence=0.85 if detected else 0.25,
        affected_services=list({str(t.get("service") or "unknown") for t in matched}),
        affected_workspaces=list({str(t.get("workspace_id") or "default") for t in matched}),
        message="Outage signal detected." if detected else "No outage signal detected.",
        metadata={
            "matched_ticket_count": len(matched),
            "threshold": threshold,
            "sample_ticket_ids": [t.get("id") for t in matched[:10]],
        },
    )

    return record_detection_signal(signal)


# ============================================================
# 21.2.2 SPIKE DETECTION
# ============================================================

def detect_ticket_spike(
    *,
    tickets: List[Dict[str, Any]],
    baseline_count: int,
    spike_multiplier: float = 2.0,
) -> Dict[str, Any]:
    current_count = len(tickets)
    threshold = max(1, int(baseline_count * spike_multiplier))
    detected = current_count >= threshold

    signal = IncidentDetectionSignal(
        signal_type="ticket_spike_detection",
        detected=detected,
        severity="sev_1" if detected else "sev_3",
        confidence=0.8 if detected else 0.2,
        affected_workspaces=list({str(t.get("workspace_id") or "default") for t in tickets}),
        message="Ticket volume spike detected." if detected else "No ticket spike detected.",
        metadata={
            "current_count": current_count,
            "baseline_count": baseline_count,
            "threshold": threshold,
            "spike_multiplier": spike_multiplier,
        },
    )

    return record_detection_signal(signal)


# ============================================================
# 21.2.3 ERROR RATE MONITORING
# ============================================================

def monitor_error_rate(
    *,
    service_metrics: Dict[str, Any],
    error_rate_threshold: float = 5.0,
) -> Dict[str, Any]:
    service_name = str(service_metrics.get("service") or "unknown")
    error_rate = float(service_metrics.get("error_rate_percent") or 0)
    detected = error_rate >= error_rate_threshold

    signal = IncidentDetectionSignal(
        signal_type="error_rate_monitoring",
        detected=detected,
        severity="sev_1" if error_rate >= 20 else "sev_2" if detected else "sev_3",
        confidence=0.82 if detected else 0.2,
        affected_services=[service_name],
        message="High error rate detected." if detected else "Error rate is within threshold.",
        metadata={
            "service": service_name,
            "error_rate_percent": error_rate,
            "error_rate_threshold": error_rate_threshold,
        },
    )

    return record_detection_signal(signal)


# ============================================================
# 21.2.4 CUSTOMER IMPACT ASSESSMENT
# ============================================================

def assess_customer_impact(
    *,
    tickets: List[Dict[str, Any]],
    affected_workspaces: List[str] | None = None,
) -> Dict[str, Any]:
    workspaces = affected_workspaces or list({str(t.get("workspace_id") or "default") for t in tickets})
    impacted_customers = list({str(t.get("customer_id") or t.get("email") or "unknown") for t in tickets})

    severity = "sev_0" if len(impacted_customers) >= 50 else "sev_1" if len(impacted_customers) >= 10 else "sev_2"

    signal = IncidentDetectionSignal(
        signal_type="customer_impact_assessment",
        detected=len(impacted_customers) > 0,
        severity=severity,
        confidence=0.75,
        affected_workspaces=workspaces,
        message=f"{len(impacted_customers)} impacted customer(s) estimated.",
        metadata={
            "impacted_customer_count": len(impacted_customers),
            "impacted_customers_sample": impacted_customers[:20],
            "ticket_count": len(tickets),
        },
    )

    return record_detection_signal(signal)


# ============================================================
# 21.2.5 AUTO INCIDENT CREATION
# ============================================================

def auto_create_incident_from_signal(
    *,
    signal: Dict[str, Any],
    title: str | None = None,
    description: str | None = None,
    actor_id: str | None = "system",
) -> Dict[str, Any] | None:
    if not bool(signal.get("detected")):
        return None

    incident = create_incident(
        title=title or signal.get("message") or "Auto-detected incident",
        description=description or json.dumps(signal.get("metadata", {}), ensure_ascii=False),
        incident_type=str(signal.get("signal_type") or "auto_detected"),
        severity=str(signal.get("severity") or "sev_2"),
        status="detected",
        affected_services=list(signal.get("affected_services") or []),
        affected_workspaces=list(signal.get("affected_workspaces") or []),
        source="auto_detection",
        metadata={
            "detection_signal": signal,
        },
        actor_id=actor_id,
    )

    record_detection_signal(
        IncidentDetectionSignal(
            signal_type="auto_incident_created",
            detected=True,
            severity=str(signal.get("severity") or "sev_2"),
            confidence=float(signal.get("confidence") or 0),
            affected_services=list(signal.get("affected_services") or []),
            affected_workspaces=list(signal.get("affected_workspaces") or []),
            message="Auto incident created from detection signal.",
            metadata={
                "incident_id": incident.get("incident_id"),
                "source_signal_type": signal.get("signal_type"),
            },
        )
    )

    return incident


def run_incident_detection_package(
    *,
    tickets: List[Dict[str, Any]],
    service_metrics: Dict[str, Any] | None = None,
    baseline_count: int = 5,
) -> Dict[str, Any]:
    outage = detect_outage(tickets=tickets)
    spike = detect_ticket_spike(tickets=tickets, baseline_count=baseline_count)
    error_rate = monitor_error_rate(service_metrics=service_metrics or {})
    impact = assess_customer_impact(tickets=tickets)

    created_incidents = []

    for signal in [outage, spike, error_rate]:
        incident = auto_create_incident_from_signal(signal=signal)

        if incident:
            created_incidents.append(incident)

    return {
        "outage": outage,
        "spike": spike,
        "error_rate": error_rate,
        "impact": impact,
        "created_incidents": created_incidents,
        "created_incident_count": len(created_incidents),
        "generated_at": _utc_now(),
    }


def read_incident_detection_audit(limit: int = 1000) -> List[Dict[str, Any]]:
    _ensure_store()

    lines = INCIDENT_DETECTION_AUDIT_PATH.read_text(encoding="utf-8").splitlines()

    return [
        json.loads(line)
        for line in lines[-limit:]
        if line.strip()
    ]
