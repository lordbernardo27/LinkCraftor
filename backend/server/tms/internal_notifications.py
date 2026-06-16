
from __future__ import annotations

from typing import Any, Dict

from backend.server.tms.notification_engine import create_ticket_notification
from backend.server.tms.notification_delivery import deliver_in_app_notification


def notify_staff(
    *,
    staff_id: str,
    title: str,
    message: str,
    workspace_id: str | None = None,
    ticket_id: str | None = None,
    notification_type: str = "system_alert",
    priority: str = "normal",
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    notification = create_ticket_notification(
        notification_type=notification_type,
        ticket_id=ticket_id or "general",
        title=title,
        message=message,
        workspace_id=workspace_id,
        recipient_id=staff_id,
        priority=priority,
        channels=["in_app"],
        payload=payload or {},
    )

    delivery = deliver_in_app_notification(
        notification_id=str(notification.get("notification_id")),
        recipient_id=staff_id,
        workspace_id=workspace_id,
        metadata={
            "notification_type": notification_type,
            "ticket_id": ticket_id,
        },
    )

    return {
        "notification": notification,
        "delivery": delivery,
    }


def send_staff_notification(
    *,
    staff_id: str,
    workspace_id: str | None = None,
    ticket_id: str | None = None,
    title: str,
    message: str,
    priority: str = "normal",
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return notify_staff(
        staff_id=staff_id,
        workspace_id=workspace_id,
        ticket_id=ticket_id,
        title=title,
        message=message,
        notification_type="system_alert",
        priority=priority,
        payload=payload,
    )


def send_assignment_alert(
    *,
    staff_id: str,
    ticket_id: str,
    workspace_id: str | None = None,
    assigned_by: str | None = None,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return notify_staff(
        staff_id=staff_id,
        workspace_id=workspace_id,
        ticket_id=ticket_id,
        title="New ticket assigned",
        message=f"Ticket {ticket_id} has been assigned to you.",
        notification_type="ticket_assigned",
        priority="normal",
        payload={
            "assigned_by": assigned_by,
            **(payload or {}),
        },
    )


def send_escalation_alert(
    *,
    staff_id: str,
    ticket_id: str,
    workspace_id: str | None = None,
    escalation_level: str = "level_1",
    reason: str | None = None,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return notify_staff(
        staff_id=staff_id,
        workspace_id=workspace_id,
        ticket_id=ticket_id,
        title="Ticket escalated",
        message=f"Ticket {ticket_id} has been escalated to {escalation_level}.",
        notification_type="ticket_escalated",
        priority="high",
        payload={
            "escalation_level": escalation_level,
            "reason": reason,
            **(payload or {}),
        },
    )


def send_sla_breach_alert(
    *,
    staff_id: str,
    ticket_id: str,
    workspace_id: str | None = None,
    sla_type: str = "first_response",
    breached_at: str | None = None,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return notify_staff(
        staff_id=staff_id,
        workspace_id=workspace_id,
        ticket_id=ticket_id,
        title="SLA breach detected",
        message=f"Ticket {ticket_id} has breached the {sla_type} SLA.",
        notification_type="sla_breached",
        priority="urgent",
        payload={
            "sla_type": sla_type,
            "breached_at": breached_at,
            **(payload or {}),
        },
    )


def send_mention_alert(
    *,
    staff_id: str,
    mentioned_by: str,
    ticket_id: str,
    workspace_id: str | None = None,
    comment_id: str | None = None,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return notify_staff(
        staff_id=staff_id,
        workspace_id=workspace_id,
        ticket_id=ticket_id,
        title="You were mentioned",
        message=f"{mentioned_by} mentioned you on ticket {ticket_id}.",
        notification_type="staff_mention",
        priority="normal",
        payload={
            "mentioned_by": mentioned_by,
            "comment_id": comment_id,
            **(payload or {}),
        },
    )
