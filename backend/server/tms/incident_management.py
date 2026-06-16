
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data/tms")

INCIDENTS_PATH = DATA_DIR / "incidents.jsonl"
INCIDENT_TIMELINE_PATH = DATA_DIR / "incident_timeline.jsonl"
INCIDENT_AUDIT_PATH = DATA_DIR / "incident_audit.jsonl"


INCIDENT_STATUSES = {
    "detected",
    "investigating",
    "identified",
    "monitoring",
    "resolved",
    "closed",
}


VALID_INCIDENT_STATUS_TRANSITIONS = {
    "detected": {"investigating", "identified", "resolved"},
    "investigating": {"identified", "monitoring", "resolved"},
    "identified": {"monitoring", "resolved"},
    "monitoring": {"resolved"},
    "resolved": {"closed", "monitoring"},
    "closed": set(),
}


INCIDENT_SEVERITIES = {
    "sev_0": {
        "label": "Critical",
        "rank": 0,
        "description": "Major outage or business-critical failure.",
        "requires_immediate_response": True,
    },
    "sev_1": {
        "label": "High",
        "rank": 1,
        "description": "Severe customer impact or degraded core service.",
        "requires_immediate_response": True,
    },
    "sev_2": {
        "label": "Medium",
        "rank": 2,
        "description": "Partial degradation or limited customer impact.",
        "requires_immediate_response": False,
    },
    "sev_3": {
        "label": "Low",
        "rank": 3,
        "description": "Minor issue with low operational impact.",
        "requires_immediate_response": False,
    },
}


@dataclass(frozen=True)
class Incident:
    incident_id: str
    title: str
    description: str = ""
    incident_type: str = "operational"
    severity: str = "sev_2"
    status: str = "detected"
    owner_id: str | None = None
    incident_commander_id: str | None = None
    affected_services: List[str] = field(default_factory=list)
    affected_workspaces: List[str] = field(default_factory=list)
    source: str = "manual"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved_at: str | None = None


@dataclass(frozen=True)
class IncidentTimelineEvent:
    timeline_id: str
    incident_id: str
    event_type: str
    message: str
    actor_id: str | None = None
    status: str | None = None
    severity: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class IncidentAuditEvent:
    audit_id: str
    incident_id: str
    event_type: str
    actor_id: str | None = None
    message: str = ""
    previous_value: Any | None = None
    new_value: Any | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for path in (
        INCIDENTS_PATH,
        INCIDENT_TIMELINE_PATH,
        INCIDENT_AUDIT_PATH,
    ):
        if not path.exists():
            path.write_text("", encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _timestamp_id(prefix: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"{prefix}_{ts}"


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


# ============================================================
# 21.1.3 INCIDENT SEVERITY LEVELS
# ============================================================

def list_incident_severities() -> Dict[str, Any]:
    return INCIDENT_SEVERITIES


def validate_incident_severity(severity: str | None) -> str:
    if severity in INCIDENT_SEVERITIES:
        return str(severity)

    return "sev_2"


def get_incident_severity_metadata(severity: str) -> Dict[str, Any]:
    return dict(
        INCIDENT_SEVERITIES.get(
            severity,
            INCIDENT_SEVERITIES["sev_2"],
        )
    )


# ============================================================
# 21.1.2 INCIDENT STATUS LIFECYCLE
# ============================================================

def list_incident_statuses() -> List[str]:
    return sorted(INCIDENT_STATUSES)


def validate_incident_status(status: str | None) -> str:
    if status in INCIDENT_STATUSES:
        return str(status)

    return "detected"


def can_transition_incident_status(
    *,
    previous_status: str,
    new_status: str,
) -> bool:
    if previous_status == new_status:
        return True

    allowed = VALID_INCIDENT_STATUS_TRANSITIONS.get(previous_status, set())

    return new_status in allowed


# ============================================================
# 21.1.5 INCIDENT AUDIT TRAIL
# ============================================================

def log_incident_audit(
    *,
    incident_id: str,
    event_type: str,
    actor_id: str | None = None,
    message: str = "",
    previous_value: Any | None = None,
    new_value: Any | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    event = IncidentAuditEvent(
        audit_id=_timestamp_id("incident_audit"),
        incident_id=incident_id,
        event_type=event_type,
        actor_id=actor_id,
        message=message,
        previous_value=previous_value,
        new_value=new_value,
        metadata=metadata or {},
    )

    payload = asdict(event)
    _append_jsonl(INCIDENT_AUDIT_PATH, payload)

    return payload


# ============================================================
# 21.1.4 INCIDENT TIMELINE
# ============================================================

def add_incident_timeline_event(
    *,
    incident_id: str,
    event_type: str,
    message: str,
    actor_id: str | None = None,
    status: str | None = None,
    severity: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    event = IncidentTimelineEvent(
        timeline_id=_timestamp_id("incident_timeline"),
        incident_id=incident_id,
        event_type=event_type,
        message=message,
        actor_id=actor_id,
        status=status,
        severity=severity,
        metadata=metadata or {},
    )

    payload = asdict(event)
    _append_jsonl(INCIDENT_TIMELINE_PATH, payload)

    log_incident_audit(
        incident_id=incident_id,
        event_type=f"timeline_{event_type}",
        actor_id=actor_id,
        message=message,
        metadata=metadata or {},
    )

    return payload


def read_incident_timeline(
    *,
    incident_id: str,
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    events = _read_jsonl(INCIDENT_TIMELINE_PATH, limit=100000)

    filtered = [
        event
        for event in events
        if str(event.get("incident_id")) == str(incident_id)
    ]

    return sorted(
        filtered[-limit:],
        key=lambda item: str(item.get("created_at") or ""),
    )


# ============================================================
# 21.1.1 INCIDENT OBJECTS
# ============================================================

def create_incident(
    *,
    title: str,
    description: str = "",
    incident_type: str = "operational",
    severity: str = "sev_2",
    status: str = "detected",
    owner_id: str | None = None,
    incident_commander_id: str | None = None,
    affected_services: List[str] | None = None,
    affected_workspaces: List[str] | None = None,
    source: str = "manual",
    metadata: Dict[str, Any] | None = None,
    actor_id: str | None = None,
) -> Dict[str, Any]:
    clean_severity = validate_incident_severity(severity)
    clean_status = validate_incident_status(status)

    incident = Incident(
        incident_id=_timestamp_id("incident"),
        title=title,
        description=description,
        incident_type=incident_type,
        severity=clean_severity,
        status=clean_status,
        owner_id=owner_id,
        incident_commander_id=incident_commander_id,
        affected_services=affected_services or [],
        affected_workspaces=affected_workspaces or [],
        source=source,
        metadata=metadata or {},
    )

    payload = asdict(incident)
    _append_jsonl(INCIDENTS_PATH, payload)

    add_incident_timeline_event(
        incident_id=incident.incident_id,
        event_type="incident_created",
        message=f"Incident created: {title}",
        actor_id=actor_id,
        status=clean_status,
        severity=clean_severity,
        metadata={
            "source": source,
            "affected_services": affected_services or [],
            "affected_workspaces": affected_workspaces or [],
        },
    )

    log_incident_audit(
        incident_id=incident.incident_id,
        event_type="incident_created",
        actor_id=actor_id,
        message=f"Incident created: {title}",
        new_value=payload,
    )

    return payload


def read_incidents(limit: int = 1000) -> List[Dict[str, Any]]:
    return _read_jsonl(INCIDENTS_PATH, limit)


def find_incident_by_id(incident_id: str) -> Dict[str, Any] | None:
    for incident in reversed(read_incidents(limit=100000)):
        if str(incident.get("incident_id")) == str(incident_id):
            return incident

    return None


def update_incident(
    *,
    incident: Dict[str, Any],
    actor_id: str | None = None,
    **updates: Any,
) -> Dict[str, Any]:
    previous = dict(incident)

    updated = {
        **incident,
        **updates,
        "updated_at": _utc_now(),
    }

    if str(updated.get("status")) == "resolved" and not updated.get("resolved_at"):
        updated["resolved_at"] = _utc_now()

    _append_jsonl(INCIDENTS_PATH, updated)

    add_incident_timeline_event(
        incident_id=str(updated.get("incident_id")),
        event_type="incident_updated",
        message="Incident updated.",
        actor_id=actor_id,
        status=updated.get("status"),
        severity=updated.get("severity"),
        metadata={
            "updates": updates,
        },
    )

    log_incident_audit(
        incident_id=str(updated.get("incident_id")),
        event_type="incident_updated",
        actor_id=actor_id,
        message="Incident updated.",
        previous_value=previous,
        new_value=updated,
        metadata={"updates": updates},
    )

    return updated


def transition_incident_status(
    *,
    incident: Dict[str, Any],
    new_status: str,
    actor_id: str | None = None,
    reason: str = "",
) -> Dict[str, Any]:
    previous_status = str(incident.get("status") or "detected")
    clean_status = validate_incident_status(new_status)

    if not can_transition_incident_status(
        previous_status=previous_status,
        new_status=clean_status,
    ):
        raise ValueError(
            f"Invalid incident status transition: {previous_status} -> {clean_status}"
        )

    updated = update_incident(
        incident=incident,
        actor_id=actor_id,
        status=clean_status,
        resolved_at=_utc_now() if clean_status == "resolved" else incident.get("resolved_at"),
    )

    add_incident_timeline_event(
        incident_id=str(updated.get("incident_id")),
        event_type="status_changed",
        message=reason or f"Incident status changed from {previous_status} to {clean_status}.",
        actor_id=actor_id,
        status=clean_status,
        severity=updated.get("severity"),
        metadata={
            "previous_status": previous_status,
            "new_status": clean_status,
        },
    )

    log_incident_audit(
        incident_id=str(updated.get("incident_id")),
        event_type="incident_status_changed",
        actor_id=actor_id,
        message=reason or f"Incident status changed from {previous_status} to {clean_status}.",
        previous_value=previous_status,
        new_value=clean_status,
    )

    return updated


def assign_incident_commander(
    *,
    incident: Dict[str, Any],
    commander_id: str,
    actor_id: str | None = None,
) -> Dict[str, Any]:
    previous_commander = incident.get("incident_commander_id")

    updated = update_incident(
        incident=incident,
        actor_id=actor_id,
        incident_commander_id=commander_id,
    )

    add_incident_timeline_event(
        incident_id=str(updated.get("incident_id")),
        event_type="commander_assigned",
        message=f"Incident commander assigned: {commander_id}",
        actor_id=actor_id,
        metadata={
            "previous_commander": previous_commander,
            "new_commander": commander_id,
        },
    )

    log_incident_audit(
        incident_id=str(updated.get("incident_id")),
        event_type="incident_commander_assigned",
        actor_id=actor_id,
        message=f"Incident commander assigned: {commander_id}",
        previous_value=previous_commander,
        new_value=commander_id,
    )

    return updated


def read_incident_audit(limit: int = 1000) -> List[Dict[str, Any]]:
    return _read_jsonl(INCIDENT_AUDIT_PATH, limit)
