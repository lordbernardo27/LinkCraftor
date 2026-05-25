from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, HTTPException

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

from .service import ticket_service


router = APIRouter(prefix="/api/tms", tags=["tms"])


@router.post("/tickets", response_model=TicketCreateResponse)
def create_ticket(payload: TicketCreateRequest) -> TicketCreateResponse:
    return ticket_service.create_ticket(payload)


@router.get("/tickets")
def list_tickets(
    status: str | None = None,
    category: str | None = None,
    priority: str | None = None,
    limit: int | None = None,
    offset: int = 0,
) -> dict:
    tickets = ticket_service.list_tickets()

    if status:
        normalized_status = status.strip().lower()
        tickets = [
            ticket for ticket in tickets
            if ticket.status.lower() == normalized_status
        ]

    if category:
        normalized_category = category.strip().lower()
        tickets = [
            ticket for ticket in tickets
            if ticket.category.lower() == normalized_category
        ]

    if priority:
        normalized_priority = priority.strip().lower()
        tickets = [
            ticket for ticket in tickets
            if ticket.priority.lower() == normalized_priority
        ]

    total = len(tickets)

    safe_offset = max(0, offset)

    if limit is not None:
        safe_limit = max(0, min(limit, 500))
    else:
        safe_limit = 50

    tickets = tickets[safe_offset:safe_offset + safe_limit]

    return {
        "ok": True,
        "count": len(tickets),
        "total": total,
        "filters": {
            "status": status,
            "category": category,
            "priority": priority,
            "limit": safe_limit,
            "offset": safe_offset,
        },
        "tickets": [asdict(ticket) for ticket in tickets],
    }

@router.patch("/tickets/{ticket_id}/status", response_model=TicketStatusUpdateResponse)
def update_ticket_status(
    ticket_id: str,
    payload: TicketStatusUpdateRequest,
) -> TicketStatusUpdateResponse:
    try:
        return ticket_service.update_ticket_status(ticket_id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/tickets/{ticket_id}/assignment", response_model=TicketAssignmentResponse)
def assign_ticket(
    ticket_id: str,
    payload: TicketAssignmentRequest,
) -> TicketAssignmentResponse:
    try:
        return ticket_service.assign_ticket(ticket_id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

@router.patch("/tickets/{ticket_id}/priority-severity", response_model=TicketPrioritySeverityUpdateResponse)
def update_ticket_priority_severity(
    ticket_id: str,
    payload: TicketPrioritySeverityUpdateRequest,
) -> TicketPrioritySeverityUpdateResponse:
    try:
        return ticket_service.update_ticket_priority_severity(ticket_id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@router.post("/tickets/{ticket_id}/internal-notes", response_model=TicketInternalNoteResponse)
def add_internal_note(
    ticket_id: str,
    payload: TicketInternalNoteCreateRequest,
) -> TicketInternalNoteResponse:
    try:
        return ticket_service.add_internal_note(ticket_id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/tickets/{ticket_id}/internal-notes")
def list_internal_notes(ticket_id: str) -> dict:
    ticket = ticket_service.get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail=f"ticket_not_found: {ticket_id}")

    notes = ticket_service.list_internal_notes(ticket_id)
    return {
        "ok": True,
        "ticket_id": ticket_id,
        "notes": [asdict(note) for note in notes],
        "count": len(notes),
    }

@router.get("/customers/{requester_user_id}/tickets")
def list_customer_tickets(requester_user_id: str) -> dict:
    tickets = ticket_service.list_tickets()
    customer_tickets = [
        ticket for ticket in tickets
        if ticket.requester_user_id == requester_user_id
    ]

    return {
        "ok": True,
        "requester_user_id": requester_user_id,
        "count": len(customer_tickets),
        "tickets": [asdict(ticket) for ticket in customer_tickets],
    }

@router.get("/customers/{requester_user_id}/tickets/{ticket_id}")
def get_customer_ticket_thread(
    requester_user_id: str,
    ticket_id: str,
) -> dict:
    ticket = ticket_service.get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail=f"ticket_not_found: {ticket_id}")

    if ticket.requester_user_id != requester_user_id:
        raise HTTPException(status_code=403, detail="ticket_access_denied")

    messages = ticket_service.list_messages(ticket_id)

    customer_visible_messages = [
        message for message in messages
        if message.is_customer_visible
    ]

    return {
        "ok": True,
        "requester_user_id": requester_user_id,
        "ticket": asdict(ticket),
        "messages": [asdict(message) for message in customer_visible_messages],
        "message_count": len(customer_visible_messages),
    }

@router.post("/customers/{requester_user_id}/tickets/{ticket_id}/messages", response_model=TicketMessageResponse)
def add_customer_ticket_message(
    requester_user_id: str,
    ticket_id: str,
    payload: TicketMessageCreateRequest,
) -> TicketMessageResponse:
    ticket = ticket_service.get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail=f"ticket_not_found: {ticket_id}")

    if ticket.requester_user_id != requester_user_id:
        raise HTTPException(status_code=403, detail="ticket_access_denied")

    safe_payload = TicketMessageCreateRequest(
        body=payload.body,
        author_type="customer",
        author_id=requester_user_id,
        is_customer_visible=True,
    )

    try:
        return ticket_service.add_message(ticket_id, safe_payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

@router.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: str) -> dict[str, Any]:
    ticket = ticket_service.get_ticket(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail=f"ticket_not_found: {ticket_id}",
        )

    return {
        "ok": True,
        "ticket": asdict(ticket),
    }


@router.post("/tickets/{ticket_id}/messages", response_model=TicketMessageResponse)
def add_ticket_message(
    ticket_id: str,
    payload: TicketMessageCreateRequest,
) -> TicketMessageResponse:
    try:
        return ticket_service.add_message(ticket_id, payload)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=f"ticket_not_found: {ticket_id}",
        ) from exc


@router.get("/tickets/{ticket_id}/messages")
def list_ticket_messages(ticket_id: str) -> dict[str, Any]:
    ticket = ticket_service.get_ticket(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail=f"ticket_not_found: {ticket_id}",
        )

    messages = ticket_service.list_messages(ticket_id)

    return {
        "ok": True,
        "ticket_id": ticket_id,
        "messages": [asdict(message) for message in messages],
        "count": len(messages),
    }





