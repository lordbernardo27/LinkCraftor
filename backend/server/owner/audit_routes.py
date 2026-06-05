
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query

from backend.server.owner.audit_registry import (
    collect_unified_audit_events,
    export_unified_audit_events,
    get_unified_audit_filters,
    get_unified_audit_summary,
    get_unified_audit_timeline,
)


router = APIRouter(prefix="/owner/api/audit", tags=["owner-audit"])


@router.get("/summary")
def audit_summary():
    return get_unified_audit_summary()


@router.get("/events")
def audit_events(
    limit: int = Query(250, ge=1, le=1000),
    source: Optional[str] = None,
    severity: Optional[str] = None,
    event_type: Optional[str] = None,
    query: Optional[str] = None,
):
    return {
        "events": collect_unified_audit_events(
            limit=limit,
            source=source,
            severity=severity,
            event_type=event_type,
            query=query,
        )
    }


@router.get("/filters")
def audit_filters():
    return get_unified_audit_filters()


@router.get("/timeline")
def audit_timeline(limit: int = Query(100, ge=1, le=1000)):
    return get_unified_audit_timeline(limit=limit)


@router.get("/export")
def audit_export(
    limit: int = Query(1000, ge=1, le=5000),
    source: Optional[str] = None,
    severity: Optional[str] = None,
    event_type: Optional[str] = None,
    query: Optional[str] = None,
):
    return export_unified_audit_events(
        limit=limit,
        source=source,
        severity=severity,
        event_type=event_type,
        query=query,
    )
