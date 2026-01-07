# backend/app/schemas.py
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class EngineItem(BaseModel):
    anchor: str
    target_title: str
    target_url: str = ""
    score: float = Field(ge=0.0, le=1.0, default=0.5)
    kind: str = "published"  # published | draft | same-doc | external


class InternalRequest(BaseModel):
    html: Optional[str] = ""
    text: Optional[str] = ""


class InternalResponse(BaseModel):
    recommended: List[EngineItem] = []
    optional: List[EngineItem] = []


class ExternalRequest(BaseModel):
    anchor: str
    context: Optional[str] = ""
    limit: int = 8


class ExternalRef(BaseModel):
    title: str
    url: str
    domain: Optional[str] = ""
    abstract: Optional[str] = ""
    year: Optional[int] = None
    score: float = 0.75


class ExternalResponse(BaseModel):
    items: List[ExternalRef] = []
