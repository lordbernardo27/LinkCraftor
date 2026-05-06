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