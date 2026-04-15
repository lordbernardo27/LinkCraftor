from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class Ticket:
    ticket_id: str
    ticket_number: str
    subject: str
    description: str
    status: str = "new"
    priority: str = "normal"
    severity: str = "minor"
    category: str = "general"
    source: str = "app"
    channel: str = "web"
    requester_user_id: Optional[str] = None
    requester_email: Optional[str] = None
    requester_name: Optional[str] = None
    workspace_id: Optional[str] = None
    plan_tier: Optional[str] = None
    assigned_team: Optional[str] = None
    assigned_staff_id: Optional[str] = None
    resolution_code: Optional[str] = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    closed_at: Optional[datetime] = None


@dataclass(slots=True)
class TicketMessage:
    message_id: str
    ticket_id: str
    author_type: str  # customer | staff | system
    author_id: Optional[str]
    body: str
    is_customer_visible: bool = True
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class TicketNote:
    note_id: str
    ticket_id: str
    author_staff_id: str
    body: str
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class TicketAssignment:
    assignment_id: str
    ticket_id: str
    assigned_team: Optional[str] = None
    assigned_staff_id: Optional[str] = None
    assigned_by_staff_id: Optional[str] = None
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class TicketStatusEvent:
    event_id: str
    ticket_id: str
    from_status: Optional[str]
    to_status: str
    changed_by_staff_id: Optional[str] = None
    reason: Optional[str] = None
    created_at: datetime = field(default_factory=utc_now)

