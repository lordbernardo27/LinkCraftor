
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data/tms")

NOTIFICATION_STORE_PATH = DATA_DIR / "notifications.jsonl"
NOTIFICATION_AUDIT_PATH = DATA_DIR / "notification_engine_audit.jsonl"


NOTIFICATION_TYPES = {
    "ticket_created": {
        "label": "Ticket Created",
        "description": "A new support ticket was created.",
        "default_priority": "normal",
        "category": "ticket",
    },
    "ticket_updated": {
        "label": "Ticket Updated",
        "description": "A support ticket was updated.",
        "default_priority": "normal",
        "category": "ticket",
    },
    "ticket_assigned": {
        "label": "Ticket Assigned",
        "description": "A ticket was assigned to a staff member.",
        "default_priority": "normal",
        "category": "ticket",
    },
    "ticket_escalated": {
        "label": "Ticket Escalated",
        "description": "A support ticket was escalated.",
        "default_priority": "high",
        "category": "escalation",
    },
    "sla_warning": {
        "label": "SLA Warning",
        "description": "A ticket is approaching its SLA deadline.",
        "default_priority": "high",
        "category": "sla",
    },
    "sla_breached": {
        "label": "SLA Breached",
        "description": "A ticket has breached its SLA deadline.",
        "default_priority": "urgent",
        "category": "sla",
    },
    "customer_reply": {
        "label": "Customer Reply",
        "description": "A customer replied to a support ticket.",
        "default_priority": "normal",
        "category": "message",
    },
    "staff_mention": {
        "label": "Staff Mention",
        "description": "A staff member was mentioned.",
        "default_priority": "normal",
        "category": "collaboration",
    },
    "system_alert": {
        "label": "System Alert",
        "description": "A system-level support notification.",
        "default_priority": "high",
        "category": "system",
    },
}


NOTIFICATION_PRIORITIES = {
    "low": {
        "rank": 1,
        "label": "Low",
        "requires_immediate_attention": False,
    },
    "normal": {
        "rank": 2,
        "label": "Normal",
        "requires_immediate_attention": False,
    },
    "high": {
        "rank": 3,
        "label": "High",
        "requires_immediate_attention": True,
    },
    "urgent": {
        "rank": 4,
        "label": "Urgent",
        "requires_immediate_attention": True,
    },
}


NOTIFICATION_STATUSES = {
    "created": {
        "label": "Created",
        "terminal": False,
    },
    "queued": {
        "label": "Queued",
        "terminal": False,
    },
    "delivered": {
        "label": "Delivered",
        "terminal": False,
    },
    "read": {
        "label": "Read",
        "terminal": False,
    },
    "dismissed": {
        "label": "Dismissed",
        "terminal": True,
    },
    "failed": {
        "label": "Failed",
        "terminal": True,
    },
}


VALID_STATUS_TRANSITIONS = {
    "created": {"queued", "delivered", "failed"},
    "queued": {"delivered", "failed"},
    "delivered": {"read", "dismissed"},
    "read": {"dismissed"},
    "dismissed": set(),
    "failed": set(),
}


@dataclass(frozen=True)
class Notification:
    notification_id: str
    notification_type: str
    title: str
    message: str
    recipient_id: str | None = None
    recipient_type: str = "staff"
    workspace_id: str | None = None
    ticket_id: str | None = None
    priority: str = "normal"
    status: str = "created"
    channels: List[str] = field(default_factory=lambda: ["in_app"])
    payload: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class NotificationAuditEvent:
    event_type: str
    notification_id: str | None = None
    notification_type: str | None = None
    status: str = "recorded"
    workspace_id: str | None = None
    ticket_id: str | None = None
    recipient_id: str | None = None
    message: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _ensure_notification_engine_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for path in (
        NOTIFICATION_STORE_PATH,
        NOTIFICATION_AUDIT_PATH,
    ):
        if not path.exists():
            path.write_text("", encoding="utf-8")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    _ensure_notification_engine_store()

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _read_jsonl(path: Path, limit: int = 1000) -> List[Dict[str, Any]]:
    _ensure_notification_engine_store()

    lines = path.read_text(encoding="utf-8").splitlines()
    records: List[Dict[str, Any]] = []

    for line in lines[-limit:]:
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            records.append(
                {
                    "parse_error": True,
                    "raw_line": line,
                    "source_path": str(path),
                }
            )

    return records


def _notification_id(notification_type: str, ticket_id: str | None = None) -> str:
    timestamp = _utc_now().strftime("%Y%m%d%H%M%S%f")
    safe_type = str(notification_type or "notification").replace(" ", "_")
    safe_ticket = str(ticket_id or "general").replace(" ", "_")
    return f"notification_{safe_ticket}_{safe_type}_{timestamp}"


def log_notification_engine_audit(event: NotificationAuditEvent) -> Dict[str, Any]:
    payload = asdict(event)
    _append_jsonl(NOTIFICATION_AUDIT_PATH, payload)
    return payload


def list_notification_types() -> Dict[str, Any]:
    return NOTIFICATION_TYPES


def get_notification_type_config(notification_type: str) -> Dict[str, Any]:
    return dict(
        NOTIFICATION_TYPES.get(
            notification_type,
            {
                "label": "Custom Notification",
                "description": "Custom support notification.",
                "default_priority": "normal",
                "category": "custom",
            },
        )
    )


def list_notification_priorities() -> Dict[str, Any]:
    return NOTIFICATION_PRIORITIES


def validate_notification_priority(priority: str | None, notification_type: str) -> str:
    if priority and priority in NOTIFICATION_PRIORITIES:
        return priority

    type_config = get_notification_type_config(notification_type)
    default_priority = str(type_config.get("default_priority") or "normal")

    if default_priority in NOTIFICATION_PRIORITIES:
        return default_priority

    return "normal"


def list_notification_statuses() -> Dict[str, Any]:
    return NOTIFICATION_STATUSES


def can_transition_notification_status(previous_status: str, new_status: str) -> bool:
    allowed = VALID_STATUS_TRANSITIONS.get(previous_status, set())
    return new_status in allowed


def create_notification(
    *,
    notification_type: str,
    title: str,
    message: str,
    recipient_id: str | None = None,
    recipient_type: str = "staff",
    workspace_id: str | None = None,
    ticket_id: str | None = None,
    priority: str | None = None,
    status: str = "created",
    channels: List[str] | None = None,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    clean_priority = validate_notification_priority(priority, notification_type)

    clean_status = status if status in NOTIFICATION_STATUSES else "created"

    notification = Notification(
        notification_id=_notification_id(notification_type, ticket_id),
        notification_type=notification_type,
        title=title,
        message=message,
        recipient_id=recipient_id,
        recipient_type=recipient_type,
        workspace_id=workspace_id,
        ticket_id=ticket_id,
        priority=clean_priority,
        status=clean_status,
        channels=channels or ["in_app"],
        payload=payload or {},
    )

    notification_payload = asdict(notification)
    _append_jsonl(NOTIFICATION_STORE_PATH, notification_payload)

    log_notification_engine_audit(
        NotificationAuditEvent(
            event_type="notification_created",
            notification_id=notification.notification_id,
            notification_type=notification.notification_type,
            status=notification.status,
            workspace_id=workspace_id,
            ticket_id=ticket_id,
            recipient_id=recipient_id,
            message="Notification created.",
            metadata={
                "priority": clean_priority,
                "channels": channels or ["in_app"],
            },
        )
    )

    return notification_payload


def create_ticket_notification(
    *,
    notification_type: str,
    ticket_id: str,
    title: str,
    message: str,
    workspace_id: str | None = None,
    recipient_id: str | None = None,
    priority: str | None = None,
    channels: List[str] | None = None,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return create_notification(
        notification_type=notification_type,
        title=title,
        message=message,
        recipient_id=recipient_id,
        recipient_type="staff",
        workspace_id=workspace_id,
        ticket_id=ticket_id,
        priority=priority,
        channels=channels or ["in_app"],
        payload=payload,
    )


def transition_notification_status(
    *,
    notification: Dict[str, Any],
    new_status: str,
    reason: str | None = None,
) -> Dict[str, Any]:
    previous_status = str(notification.get("status") or "created")

    if new_status not in NOTIFICATION_STATUSES:
        raise ValueError(f"Unknown notification status: {new_status}")

    if previous_status != new_status and not can_transition_notification_status(previous_status, new_status):
        raise ValueError(
            f"Invalid notification status transition: {previous_status} -> {new_status}"
        )

    updated = {
        **notification,
        "status": new_status,
        "updated_at": _utc_now().isoformat(),
    }

    log_notification_engine_audit(
        NotificationAuditEvent(
            event_type="notification_status_transitioned",
            notification_id=str(updated.get("notification_id")),
            notification_type=str(updated.get("notification_type")),
            status=new_status,
            workspace_id=updated.get("workspace_id"),
            ticket_id=updated.get("ticket_id"),
            recipient_id=updated.get("recipient_id"),
            message=reason or f"Notification status changed from {previous_status} to {new_status}.",
            metadata={
                "previous_status": previous_status,
                "new_status": new_status,
            },
        )
    )

    return updated


def read_notifications(limit: int = 1000) -> List[Dict[str, Any]]:
    return _read_jsonl(NOTIFICATION_STORE_PATH, limit)


def read_notification_engine_audit(limit: int = 1000) -> List[Dict[str, Any]]:
    return _read_jsonl(NOTIFICATION_AUDIT_PATH, limit)


def filter_notifications(
    *,
    workspace_id: str | None = None,
    ticket_id: str | None = None,
    recipient_id: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    records = read_notifications(limit=limit)
    results: List[Dict[str, Any]] = []

    for item in records:
        if workspace_id and item.get("workspace_id") != workspace_id:
            continue
        if ticket_id and item.get("ticket_id") != ticket_id:
            continue
        if recipient_id and item.get("recipient_id") != recipient_id:
            continue
        if status and item.get("status") != status:
            continue
        if priority and item.get("priority") != priority:
            continue

        results.append(item)

    return results
