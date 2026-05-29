
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass(frozen=True)
class EmailThreadEvent:
    event_type: str
    ticket_id: str
    visibility: str
    body: str
    sender: str | None = None
    to: List[str] = field(default_factory=list)
    cc: List[str] = field(default_factory=list)
    bcc: List[str] = field(default_factory=list)
    message_id: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


EMAIL_VISIBLE_EVENT_TYPES = {
    "customer_email",
    "staff_email_reply",
    "ticket_notification",
    "sla_breach_alert",
    "escalation_alert",
}


INTERNAL_ONLY_EVENT_TYPES = {
    "internal_note",
    "staff_audit",
    "permission_event",
}


def build_unified_ticket_email_timeline(
    ticket_events: List[Dict[str, Any]],
    email_events: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    merged = []

    for event in ticket_events:
        merged.append(
            {
                **event,
                "source": "ticket",
            }
        )

    for event in email_events:
        merged.append(
            {
                **event,
                "source": "email",
            }
        )

    return sorted(
        merged,
        key=lambda item: str(item.get("created_at") or ""),
    )


def build_staff_reply_sync_event(
    ticket_id: str,
    staff_email: str,
    customer_email: str,
    body: str,
    cc: List[str] | None = None,
    bcc: List[str] | None = None,
) -> Dict[str, Any]:
    event = EmailThreadEvent(
        event_type="staff_email_reply",
        ticket_id=ticket_id,
        visibility="customer_visible",
        sender=staff_email,
        to=[customer_email],
        cc=cc or [],
        bcc=bcc or [],
        body=body,
    )

    return asdict(event)


def build_multi_recipient_thread_event(
    ticket_id: str,
    sender: str,
    to: List[str],
    body: str,
    cc: List[str] | None = None,
    bcc: List[str] | None = None,
    message_id: str | None = None,
) -> Dict[str, Any]:
    event = EmailThreadEvent(
        event_type="customer_email",
        ticket_id=ticket_id,
        visibility="customer_visible",
        sender=sender,
        to=to,
        cc=cc or [],
        bcc=bcc or [],
        body=body,
        message_id=message_id,
    )

    return asdict(event)


def normalize_recipient_list(values: List[str] | None) -> List[str]:
    if not values:
        return []

    return sorted({value.strip().lower() for value in values if value.strip()})


def apply_cc_bcc_handling(event: Dict[str, Any]) -> Dict[str, Any]:
    event["to"] = normalize_recipient_list(event.get("to") or [])
    event["cc"] = normalize_recipient_list(event.get("cc") or [])
    event["bcc"] = normalize_recipient_list(event.get("bcc") or [])

    return event


def should_exclude_internal_note_from_email(event: Dict[str, Any]) -> bool:
    event_type = str(event.get("event_type") or "")

    return event_type in INTERNAL_ONLY_EVENT_TYPES or event.get("visibility") == "internal"


def can_staff_view_email_event(staff_role: str, event: Dict[str, Any]) -> bool:
    visibility = str(event.get("visibility") or "customer_visible")

    if visibility == "customer_visible":
        return True

    if visibility == "internal":
        return staff_role in {
            "senior_agent",
            "manager_admin",
            "owner",
            "engineering",
            "billing_agent",
        }

    if visibility == "restricted":
        return staff_role in {
            "manager_admin",
            "owner",
        }

    return False


def filter_email_timeline_for_staff(
    staff_role: str,
    events: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    return [
        event
        for event in events
        if can_staff_view_email_event(staff_role, event)
    ]
