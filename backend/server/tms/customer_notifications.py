
from __future__ import annotations

from typing import Any, Dict

from backend.server.tms.notification_engine import create_ticket_notification
from backend.server.tms.notification_delivery import deliver_email_notification


def notify_customer_email(
    *,
    customer_email: str,
    title: str,
    message: str,
    workspace_id: str | None = None,
    ticket_id: str | None = None,
    notification_type: str = "customer_reply",
    priority: str = "normal",
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    notification = create_ticket_notification(
        notification_type=notification_type,
        ticket_id=ticket_id or "general",
        title=title,
        message=message,
        workspace_id=workspace_id,
        recipient_id=customer_email,
        priority=priority,
        channels=["email"],
        payload=payload or {},
    )

    delivery = deliver_email_notification(
        notification_id=str(notification.get("notification_id")),
        recipient_email=customer_email,
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


def send_ticket_created_email(
    *,
    customer_email: str,
    ticket_id: str,
    workspace_id: str | None = None,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return notify_customer_email(
        customer_email=customer_email,
        workspace_id=workspace_id,
        ticket_id=ticket_id,
        title="We received your support ticket",
        message=f"Your support ticket {ticket_id} has been created. Our team will review it shortly.",
        notification_type="ticket_created",
        priority="normal",
        payload=payload,
    )


def send_staff_reply_email(
    *,
    customer_email: str,
    ticket_id: str,
    staff_name: str | None = None,
    workspace_id: str | None = None,
    reply_preview: str | None = None,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    sender = staff_name or "Our support team"

    return notify_customer_email(
        customer_email=customer_email,
        workspace_id=workspace_id,
        ticket_id=ticket_id,
        title="New reply on your support ticket",
        message=f"{sender} replied to your ticket {ticket_id}."
        + (f" Preview: {reply_preview}" if reply_preview else ""),
        notification_type="customer_reply",
        priority="normal",
        payload={
            "staff_name": staff_name,
            "reply_preview": reply_preview,
            **(payload or {}),
        },
    )


def send_status_change_email(
    *,
    customer_email: str,
    ticket_id: str,
    previous_status: str,
    new_status: str,
    workspace_id: str | None = None,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return notify_customer_email(
        customer_email=customer_email,
        workspace_id=workspace_id,
        ticket_id=ticket_id,
        title="Your support ticket status changed",
        message=f"Ticket {ticket_id} changed from {previous_status} to {new_status}.",
        notification_type="ticket_updated",
        priority="normal",
        payload={
            "previous_status": previous_status,
            "new_status": new_status,
            **(payload or {}),
        },
    )


def send_resolution_email(
    *,
    customer_email: str,
    ticket_id: str,
    workspace_id: str | None = None,
    resolution_summary: str | None = None,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return notify_customer_email(
        customer_email=customer_email,
        workspace_id=workspace_id,
        ticket_id=ticket_id,
        title="Your support ticket has been resolved",
        message=f"Ticket {ticket_id} has been marked as resolved."
        + (f" Summary: {resolution_summary}" if resolution_summary else ""),
        notification_type="ticket_updated",
        priority="normal",
        payload={
            "resolution_summary": resolution_summary,
            **(payload or {}),
        },
    )


def send_satisfaction_email(
    *,
    customer_email: str,
    ticket_id: str,
    workspace_id: str | None = None,
    survey_url: str | None = None,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return notify_customer_email(
        customer_email=customer_email,
        workspace_id=workspace_id,
        ticket_id=ticket_id,
        title="How was your support experience?",
        message="Please rate your support experience."
        + (f" Survey: {survey_url}" if survey_url else ""),
        notification_type="ticket_updated",
        priority="low",
        payload={
            "survey_url": survey_url,
            **(payload or {}),
        },
    )
