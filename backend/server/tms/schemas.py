from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TicketCreateRequest(BaseModel):
    subject: str = Field(..., min_length=1, max_length=300)
    description: str = Field(..., min_length=1)
    category: str = Field(default="general", min_length=1, max_length=100)
    source: str = Field(default="app", min_length=1, max_length=50)
    channel: str = Field(default="web", min_length=1, max_length=50)
    requester_user_id: Optional[str] = None
    requester_email: Optional[str] = None
    requester_name: Optional[str] = None
    workspace_id: Optional[str] = None
    plan_tier: Optional[str] = None


class TicketCreateResponse(BaseModel):
    ok: bool = True
    ticket_id: str
    ticket_number: str
    status: str
    priority: str
    severity: str
    category: str
    subject: str
    description: str
    requester_user_id: Optional[str] = None
    requester_email: Optional[str] = None
    requester_name: Optional[str] = None
    workspace_id: Optional[str] = None
    plan_tier: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TicketMessageCreateRequest(BaseModel):
    body: str = Field(..., min_length=1)
    author_type: str = Field(..., min_length=1, max_length=20)
    author_id: Optional[str] = None
    is_customer_visible: bool = True


class TicketMessageResponse(BaseModel):
    ok: bool = True
    message_id: str
    ticket_id: str
    author_type: str
    author_id: Optional[str] = None
    body: str
    is_customer_visible: bool
    created_at: datetime