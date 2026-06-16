
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.server.tms.internal_notifications import notify_staff
from backend.server.tms.customer_notifications import notify_customer_email


DATA_DIR = Path("backend/server/data/tms")

INCIDENT_COMMUNICATIONS_PATH = DATA_DIR / "incident_communications.jsonl"
INCIDENT_COMMUNICATION_AUDIT_PATH = DATA_DIR / "incident_communication_audit.jsonl"


@dataclass(frozen=True)
class IncidentCommunication:
    communication_id: str
    incident_id: str
    audience: str
    channel: str
    title: str
    message: str
    recipient_id: str | None = None
    workspace_id: str | None = None
    status: str = "queued"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for path in (
        INCIDENT_COMMUNICATIONS_PATH,
        INCIDENT_COMMUNICATION_AUDIT_PATH,
    ):
        if not path.exists():
            path.write_text("", encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _id(prefix: str) -> str:
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


def _audit(event_type: str, incident_id: str, metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = {
        "event_type": event_type,
        "incident_id": incident_id,
        "metadata": metadata or {},
        "created_at": _utc_now(),
    }

    _append_jsonl(INCIDENT_COMMUNICATION_AUDIT_PATH, payload)
    return payload


def record_incident_communication(
    *,
    incident_id: str,
    audience: str,
    channel: str,
    title: str,
    message: str,
    recipient_id: str | None = None,
    workspace_id: str | None = None,
    status: str = "queued",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    communication = IncidentCommunication(
        communication_id=_id("incident_comm"),
        incident_id=incident_id,
        audience=audience,
        channel=channel,
        title=title,
        message=message,
        recipient_id=recipient_id,
        workspace_id=workspace_id,
        status=status,
        metadata=metadata or {},
    )

    payload = asdict(communication)
    _append_jsonl(INCIDENT_COMMUNICATIONS_PATH, payload)

    _audit(
        "incident_communication_recorded",
        incident_id,
        {
            "communication_id": communication.communication_id,
            "audience": audience,
            "channel": channel,
            "recipient_id": recipient_id,
            "status": status,
        },
    )

    return payload


def send_internal_incident_update(
    *,
    incident_id: str,
    staff_id: str,
    title: str,
    message: str,
    workspace_id: str | None = None,
    priority: str = "high",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    communication = record_incident_communication(
        incident_id=incident_id,
        audience="internal_staff",
        channel="in_app",
        title=title,
        message=message,
        recipient_id=staff_id,
        workspace_id=workspace_id,
        status="queued",
        metadata=metadata,
    )

    delivery = notify_staff(
        staff_id=staff_id,
        title=title,
        message=message,
        workspace_id=workspace_id,
        ticket_id=incident_id,
        notification_type="system_alert",
        priority=priority,
        payload={
            "incident_id": incident_id,
            **(metadata or {}),
        },
    )

    communication["status"] = "sent"
    communication["delivery"] = delivery

    _audit(
        "internal_incident_update_sent",
        incident_id,
        {
            "staff_id": staff_id,
            "communication_id": communication.get("communication_id"),
        },
    )

    return communication


def send_customer_incident_notification(
    *,
    incident_id: str,
    customer_email: str,
    title: str,
    message: str,
    workspace_id: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    communication = record_incident_communication(
        incident_id=incident_id,
        audience="customer",
        channel="email",
        title=title,
        message=message,
        recipient_id=customer_email,
        workspace_id=workspace_id,
        status="queued",
        metadata=metadata,
    )

    delivery = notify_customer_email(
        customer_email=customer_email,
        title=title,
        message=message,
        workspace_id=workspace_id,
        ticket_id=incident_id,
        notification_type="system_alert",
        priority="high",
        payload={
            "incident_id": incident_id,
            **(metadata or {}),
        },
    )

    communication["status"] = "sent"
    communication["delivery"] = delivery

    _audit(
        "customer_incident_notification_sent",
        incident_id,
        {
            "customer_email": customer_email,
            "communication_id": communication.get("communication_id"),
        },
    )

    return communication


def send_stakeholder_notification(
    *,
    incident_id: str,
    stakeholder_id: str,
    title: str,
    message: str,
    workspace_id: str | None = None,
    channel: str = "in_app",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    communication = record_incident_communication(
        incident_id=incident_id,
        audience="stakeholder",
        channel=channel,
        title=title,
        message=message,
        recipient_id=stakeholder_id,
        workspace_id=workspace_id,
        status="sent",
        metadata=metadata,
    )

    _audit(
        "stakeholder_incident_notification_sent",
        incident_id,
        {
            "stakeholder_id": stakeholder_id,
            "channel": channel,
            "communication_id": communication.get("communication_id"),
        },
    )

    return communication


def read_incident_communication_history(
    *,
    incident_id: str,
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    records = _read_jsonl(INCIDENT_COMMUNICATIONS_PATH, limit=100000)

    filtered = [
        record
        for record in records
        if str(record.get("incident_id")) == str(incident_id)
    ]

    return filtered[-limit:]


def read_incident_communication_audit(limit: int = 1000) -> List[Dict[str, Any]]:
    return _read_jsonl(INCIDENT_COMMUNICATION_AUDIT_PATH, limit)
