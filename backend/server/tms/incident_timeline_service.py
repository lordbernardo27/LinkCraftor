
from __future__ import annotations

from typing import Any, Dict, List

from backend.server.tms.incident_management import (
    add_incident_timeline_event,
    read_incident_timeline,
)


def record_status_change_event(
    *,
    incident_id: str,
    previous_status: str,
    new_status: str,
    actor_id: str | None = None,
    reason: str = "",
) -> Dict[str, Any]:
    return add_incident_timeline_event(
        incident_id=incident_id,
        event_type="status_change",
        message=reason or f"Incident status changed from {previous_status} to {new_status}.",
        actor_id=actor_id,
        status=new_status,
        metadata={
            "previous_status": previous_status,
            "new_status": new_status,
        },
    )


def record_investigation_event(
    *,
    incident_id: str,
    message: str,
    actor_id: str | None = None,
    findings: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return add_incident_timeline_event(
        incident_id=incident_id,
        event_type="investigation_update",
        message=message,
        actor_id=actor_id,
        metadata={
            "findings": findings or {},
        },
    )


def record_root_cause_event(
    *,
    incident_id: str,
    root_cause: str,
    actor_id: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return add_incident_timeline_event(
        incident_id=incident_id,
        event_type="root_cause_identified",
        message=f"Root cause identified: {root_cause}",
        actor_id=actor_id,
        status="identified",
        metadata={
            "root_cause": root_cause,
            **(metadata or {}),
        },
    )


def record_resolution_event(
    *,
    incident_id: str,
    resolution_summary: str,
    actor_id: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return add_incident_timeline_event(
        incident_id=incident_id,
        event_type="resolution_update",
        message=resolution_summary,
        actor_id=actor_id,
        status="resolved",
        metadata=metadata or {},
    )


def build_incident_timeline_payload(
    *,
    incident_id: str,
    limit: int = 1000,
) -> Dict[str, Any]:
    events = read_incident_timeline(
        incident_id=incident_id,
        limit=limit,
    )

    return {
        "incident_id": incident_id,
        "timeline": events,
        "event_count": len(events),
    }


def record_incident_timeline_event(
    *,
    incident_id: str,
    event_type: str,
    message: str,
    actor_id: str | None = None,
    status: str | None = None,
    severity: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return add_incident_timeline_event(
        incident_id=incident_id,
        event_type=event_type,
        message=message,
        actor_id=actor_id,
        status=status,
        severity=severity,
        metadata=metadata or {},
    )
