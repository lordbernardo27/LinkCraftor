from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, HTTPException

from .schemas import (
    TicketCreateRequest,
    TicketCreateResponse,
    TicketMessageCreateRequest,
    TicketMessageResponse,
)
from .service import ticket_service


router = APIRouter(prefix="/api/tms", tags=["tms"])


@router.post("/tickets", response_model=TicketCreateResponse)
def create_ticket(payload: TicketCreateRequest) -> TicketCreateResponse:
    return ticket_service.create_ticket(payload)


@router.post("/tickets/{ticket_id}/messages", response_model=TicketMessageResponse)
def add_ticket_message(
    ticket_id: str,
    payload: TicketMessageCreateRequest,
) -> TicketMessageResponse:
    try:
        return ticket_service.add_message(ticket_id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: str) -> dict:
    ticket = ticket_service.get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail=f"ticket_not_found: {ticket_id}")
    return {"ok": True, "ticket": asdict(ticket)}


@router.get("/tickets/{ticket_id}/messages")
def list_ticket_messages(ticket_id: str) -> dict:
    ticket = ticket_service.get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail=f"ticket_not_found: {ticket_id}")

    messages = ticket_service.list_messages(ticket_id)
    return {
        "ok": True,
        "ticket_id": ticket_id,
        "messages": [asdict(m) for m in messages],
        "count": len(messages),
    }