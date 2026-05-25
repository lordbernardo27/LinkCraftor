from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List
from uuid import uuid4

from .models import Ticket, TicketMessage, TicketStatusEvent, TicketAssignment, TicketNote
from .schemas import (
    TicketCreateRequest,
    TicketCreateResponse,
    TicketMessageCreateRequest,
    TicketMessageResponse,
    TicketStatusUpdateRequest,
    TicketStatusUpdateResponse,
    TicketAssignmentRequest,
    TicketAssignmentResponse,
    TicketPrioritySeverityUpdateRequest,
    TicketPrioritySeverityUpdateResponse,
    TicketInternalNoteCreateRequest,
    TicketInternalNoteResponse,
)
from .ticket_store import (
    load_messages,
    load_meta,
    load_tickets,
    load_status_events,
    load_assignments,
    load_notes,
    save_messages,
    save_meta,
    save_tickets,
    save_status_events,
    save_assignments,
    save_notes,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


ALLOWED_TICKET_STATUSES = {
    "new",
    "open",
    "in_review",
    "waiting_on_customer",
    "waiting_on_linkcraftor",
    "pending_engineering",
    "pending_billing",
    "pending_qa",
    "resolved",
    "closed",
}


ALLOWED_TICKET_PRIORITIES = {
    "low",
    "normal",
    "high",
    "urgent",
    "critical",
}


ALLOWED_TICKET_SEVERITIES = {
    "cosmetic",
    "minor",
    "major",
    "workspace_blocked",
    "billing_risk",
    "security_risk",
    "system_wide",
}


class TicketService:
    """
    JSON-backed TMS service.
    """

    def __init__(self) -> None:
        self._tickets: Dict[str, Ticket] = load_tickets()
        self._messages: Dict[str, List[TicketMessage]] = load_messages()
        self._status_events: Dict[str, List[TicketStatusEvent]] = load_status_events()
        self._assignments: Dict[str, List[TicketAssignment]] = load_assignments()
        self._notes: Dict[str, List[TicketNote]] = load_notes()
        self._ticket_counter: int = load_meta()

    def _persist(self) -> None:
        save_tickets(self._tickets)
        save_messages(self._messages)
        save_status_events(self._status_events)
        save_assignments(self._assignments)
        save_notes(self._notes)
        save_meta(self._ticket_counter)

    def _next_ticket_number(self) -> str:
        self._ticket_counter += 1
        return f"LC-{utc_now().year}-{self._ticket_counter:06d}"

    def create_ticket(self, payload: TicketCreateRequest) -> TicketCreateResponse:
        ticket_id = f"tkt_{uuid4().hex}"
        ticket_number = self._next_ticket_number()

        ticket = Ticket(
            ticket_id=ticket_id,
            ticket_number=ticket_number,
            subject=payload.subject,
            description=payload.description,
            category=payload.category,
            source=payload.source,
            channel=payload.channel,
            requester_user_id=payload.requester_user_id,
            requester_email=payload.requester_email,
            requester_name=payload.requester_name,
            workspace_id=payload.workspace_id,
            plan_tier=payload.plan_tier,
        )

        self._tickets[ticket_id] = ticket
        self._messages.setdefault(ticket_id, [])
        self._status_events.setdefault(ticket_id, [])
        self._assignments.setdefault(ticket_id, [])
        self._notes.setdefault(ticket_id, [])
        self._persist()

        return TicketCreateResponse(
            ticket_id=ticket.ticket_id,
            ticket_number=ticket.ticket_number,
            status=ticket.status,
            priority=ticket.priority,
            severity=ticket.severity,
            category=ticket.category,
            subject=ticket.subject,
            description=ticket.description,
            requester_user_id=ticket.requester_user_id,
            requester_email=ticket.requester_email,
            requester_name=ticket.requester_name,
            workspace_id=ticket.workspace_id,
            plan_tier=ticket.plan_tier,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
        )

    def add_message(
        self,
        ticket_id: str,
        payload: TicketMessageCreateRequest,
    ) -> TicketMessageResponse:
        ticket = self._tickets.get(ticket_id)
        if ticket is None:
            raise KeyError(f"ticket_not_found: {ticket_id}")

        message = TicketMessage(
            message_id=f"msg_{uuid4().hex}",
            ticket_id=ticket_id,
            author_type=payload.author_type,
            author_id=payload.author_id,
            body=payload.body,
            is_customer_visible=payload.is_customer_visible,
        )

        self._messages.setdefault(ticket_id, []).append(message)
        ticket.updated_at = utc_now()
        self._persist()

        return TicketMessageResponse(
            message_id=message.message_id,
            ticket_id=message.ticket_id,
            author_type=message.author_type,
            author_id=message.author_id,
            body=message.body,
            is_customer_visible=message.is_customer_visible,
            created_at=message.created_at,
        )

    def update_ticket_status(
        self,
        ticket_id: str,
        payload: TicketStatusUpdateRequest,
    ) -> TicketStatusUpdateResponse:
        ticket = self._tickets.get(ticket_id)
        if ticket is None:
            raise KeyError(f"ticket_not_found: {ticket_id}")

        new_status = payload.status.strip().lower()

        if new_status not in ALLOWED_TICKET_STATUSES:
            raise ValueError(f"invalid_ticket_status: {new_status}")

        old_status = ticket.status
        ticket.status = new_status
        ticket.updated_at = utc_now()

        status_event = TicketStatusEvent(
            event_id=f"status_{uuid4().hex}",
            ticket_id=ticket_id,
            from_status=old_status,
            to_status=new_status,
            changed_by_staff_id=payload.changed_by_staff_id,
            reason=payload.reason,
        )

        self._status_events.setdefault(ticket_id, []).append(status_event)

        if new_status in {"resolved", "closed"}:
            ticket.closed_at = ticket.updated_at
        else:
            ticket.closed_at = None

        self._persist()

        return TicketStatusUpdateResponse(
            ticket_id=ticket.ticket_id,
            from_status=old_status,
            to_status=ticket.status,
            changed_by_staff_id=payload.changed_by_staff_id,
            reason=payload.reason,
            updated_at=ticket.updated_at,
        )

    def assign_ticket(
        self,
        ticket_id: str,
        payload: TicketAssignmentRequest,
    ) -> TicketAssignmentResponse:
        ticket = self._tickets.get(ticket_id)
        if ticket is None:
            raise KeyError(f"ticket_not_found: {ticket_id}")

        assignment = TicketAssignment(
            assignment_id=f"assign_{uuid4().hex}",
            ticket_id=ticket_id,
            assigned_team=payload.assigned_team,
            assigned_staff_id=payload.assigned_staff_id,
            assigned_by_staff_id=payload.assigned_by_staff_id,
        )

        self._assignments.setdefault(ticket_id, [])
        self._notes.setdefault(ticket_id, []).append(assignment)

        ticket.assigned_team = payload.assigned_team
        ticket.assigned_staff_id = payload.assigned_staff_id
        ticket.updated_at = utc_now()

        self._persist()

        return TicketAssignmentResponse(
            ticket_id=ticket.ticket_id,
            assignment_id=assignment.assignment_id,
            assigned_team=ticket.assigned_team,
            assigned_staff_id=ticket.assigned_staff_id,
            assigned_by_staff_id=assignment.assigned_by_staff_id,
            updated_at=ticket.updated_at,
        )

    def update_ticket_priority_severity(
        self,
        ticket_id: str,
        payload: TicketPrioritySeverityUpdateRequest,
    ) -> TicketPrioritySeverityUpdateResponse:
        ticket = self._tickets.get(ticket_id)
        if ticket is None:
            raise KeyError(f"ticket_not_found: {ticket_id}")

        if payload.priority is not None:
            new_priority = payload.priority.strip().lower()
            if new_priority not in ALLOWED_TICKET_PRIORITIES:
                raise ValueError(f"invalid_ticket_priority: {new_priority}")
            ticket.priority = new_priority

        if payload.severity is not None:
            new_severity = payload.severity.strip().lower()
            if new_severity not in ALLOWED_TICKET_SEVERITIES:
                raise ValueError(f"invalid_ticket_severity: {new_severity}")
            ticket.severity = new_severity

        ticket.updated_at = utc_now()
        self._persist()

        return TicketPrioritySeverityUpdateResponse(
            ticket_id=ticket.ticket_id,
            priority=ticket.priority,
            severity=ticket.severity,
            changed_by_staff_id=payload.changed_by_staff_id,
            reason=payload.reason,
            updated_at=ticket.updated_at,
        )

    def add_internal_note(
        self,
        ticket_id: str,
        payload: TicketInternalNoteCreateRequest,
    ) -> TicketInternalNoteResponse:
        ticket = self._tickets.get(ticket_id)
        if ticket is None:
            raise KeyError(f"ticket_not_found: {ticket_id}")

        note = TicketNote(
            note_id=f"note_{uuid4().hex}",
            ticket_id=ticket_id,
            author_staff_id=payload.author_staff_id,
            body=payload.body,
        )

        self._notes.setdefault(ticket_id, []).append(note)
        ticket.updated_at = utc_now()
        self._persist()

        return TicketInternalNoteResponse(
            note_id=note.note_id,
            ticket_id=note.ticket_id,
            author_staff_id=note.author_staff_id,
            body=note.body,
            created_at=note.created_at,
        )
    def list_tickets(self) -> List[Ticket]:
        return sorted(
            self._tickets.values(),
            key=lambda t: t.created_at,
            reverse=True,
        )

    def get_ticket(self, ticket_id: str) -> Ticket | None:
        return self._tickets.get(ticket_id)

    def list_status_events(self, ticket_id: str) -> List[TicketStatusEvent]:
        return list(self._status_events.get(ticket_id, []))

    def list_assignments(self, ticket_id: str) -> List[TicketAssignment]:
        return list(self._assignments.get(ticket_id, []))

    def list_internal_notes(self, ticket_id: str) -> List[TicketNote]:
        return list(self._notes.get(ticket_id, []))

    def list_messages(self, ticket_id: str) -> List[TicketMessage]:
        return list(self._messages.get(ticket_id, []))


ticket_service = TicketService()
