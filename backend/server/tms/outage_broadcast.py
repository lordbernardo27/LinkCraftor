
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.server.tms.incident_communications import (
    send_internal_incident_update,
    send_customer_incident_notification,
    send_stakeholder_notification,
)


DATA_DIR = Path("backend/server/data/tms")

OUTAGE_BROADCASTS_PATH = DATA_DIR / "outage_broadcasts.jsonl"
OUTAGE_BROADCAST_AUDIT_PATH = DATA_DIR / "outage_broadcast_audit.jsonl"


@dataclass(frozen=True)
class OutageBroadcast:
    broadcast_id: str
    incident_id: str
    title: str
    message: str
    severity: str = "high"
    channels: List[str] = field(default_factory=list)
    audience: List[str] = field(default_factory=list)
    workspace_id: str | None = None
    status: str = "queued"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for path in (
        OUTAGE_BROADCASTS_PATH,
        OUTAGE_BROADCAST_AUDIT_PATH,
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

    _append_jsonl(OUTAGE_BROADCAST_AUDIT_PATH, payload)
    return payload


def create_outage_broadcast(
    *,
    incident_id: str,
    title: str,
    message: str,
    severity: str = "high",
    channels: List[str] | None = None,
    audience: List[str] | None = None,
    workspace_id: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    broadcast = OutageBroadcast(
        broadcast_id=_id("outage_broadcast"),
        incident_id=incident_id,
        title=title,
        message=message,
        severity=severity,
        channels=channels or ["in_app", "email"],
        audience=audience or ["internal_staff", "customers", "stakeholders"],
        workspace_id=workspace_id,
        metadata=metadata or {},
    )

    payload = asdict(broadcast)
    _append_jsonl(OUTAGE_BROADCASTS_PATH, payload)

    _audit(
        "outage_broadcast_created",
        incident_id,
        {
            "broadcast_id": broadcast.broadcast_id,
            "channels": broadcast.channels,
            "audience": broadcast.audience,
            "severity": severity,
        },
    )

    return payload


def send_outage_broadcast(
    *,
    broadcast: Dict[str, Any],
    staff_ids: List[str] | None = None,
    customer_emails: List[str] | None = None,
    stakeholder_ids: List[str] | None = None,
) -> Dict[str, Any]:
    incident_id = str(broadcast.get("incident_id"))
    title = str(broadcast.get("title"))
    message = str(broadcast.get("message"))
    workspace_id = broadcast.get("workspace_id")

    deliveries: List[Dict[str, Any]] = []

    for staff_id in staff_ids or []:
        deliveries.append(
            send_internal_incident_update(
                incident_id=incident_id,
                staff_id=staff_id,
                title=title,
                message=message,
                workspace_id=workspace_id,
                priority="urgent",
                metadata={
                    "broadcast_id": broadcast.get("broadcast_id"),
                    "broadcast_type": "outage",
                },
            )
        )

    for customer_email in customer_emails or []:
        deliveries.append(
            send_customer_incident_notification(
                incident_id=incident_id,
                customer_email=customer_email,
                title=title,
                message=message,
                workspace_id=workspace_id,
                metadata={
                    "broadcast_id": broadcast.get("broadcast_id"),
                    "broadcast_type": "outage",
                },
            )
        )

    for stakeholder_id in stakeholder_ids or []:
        deliveries.append(
            send_stakeholder_notification(
                incident_id=incident_id,
                stakeholder_id=stakeholder_id,
                title=title,
                message=message,
                workspace_id=workspace_id,
                channel="in_app",
                metadata={
                    "broadcast_id": broadcast.get("broadcast_id"),
                    "broadcast_type": "outage",
                },
            )
        )

    updated = {
        **broadcast,
        "status": "sent",
        "delivery_count": len(deliveries),
        "deliveries": deliveries,
        "sent_at": _utc_now(),
    }

    _append_jsonl(OUTAGE_BROADCASTS_PATH, updated)

    _audit(
        "outage_broadcast_sent",
        incident_id,
        {
            "broadcast_id": broadcast.get("broadcast_id"),
            "delivery_count": len(deliveries),
        },
    )

    return updated


def broadcast_outage_to_channels(
    *,
    incident_id: str,
    title: str,
    message: str,
    workspace_id: str | None = None,
    staff_ids: List[str] | None = None,
    customer_emails: List[str] | None = None,
    stakeholder_ids: List[str] | None = None,
    severity: str = "high",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    broadcast = create_outage_broadcast(
        incident_id=incident_id,
        title=title,
        message=message,
        severity=severity,
        workspace_id=workspace_id,
        metadata=metadata,
    )

    return send_outage_broadcast(
        broadcast=broadcast,
        staff_ids=staff_ids or [],
        customer_emails=customer_emails or [],
        stakeholder_ids=stakeholder_ids or [],
    )


def read_outage_broadcasts(limit: int = 1000) -> List[Dict[str, Any]]:
    return _read_jsonl(OUTAGE_BROADCASTS_PATH, limit)


def read_outage_broadcast_audit(limit: int = 1000) -> List[Dict[str, Any]]:
    return _read_jsonl(OUTAGE_BROADCAST_AUDIT_PATH, limit)
