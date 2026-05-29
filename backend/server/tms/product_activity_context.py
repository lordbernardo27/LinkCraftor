
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass(frozen=True)
class ProductActivityEvent:
    event_type: str
    workspace_id: str
    title: str
    description: str
    severity: str = "info"
    source: str = "product"
    ticket_id: str | None = None
    document_id: str | None = None
    job_id: str | None = None
    api_key_id: str | None = None
    billing_event_id: str | None = None
    error_code: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def build_document_activity_context(payload: Dict[str, Any]) -> Dict[str, Any]:
    event = ProductActivityEvent(
        event_type="document_activity",
        workspace_id=str(payload.get("workspace_id") or "unknown"),
        document_id=payload.get("document_id"),
        title=str(payload.get("title") or "Document activity"),
        description=str(payload.get("description") or "Document activity recorded."),
        severity=str(payload.get("severity") or "info"),
        source="documents",
        metadata=dict(payload.get("metadata") or {}),
    )

    return asdict(event)


def build_engine_event_context(payload: Dict[str, Any]) -> Dict[str, Any]:
    event = ProductActivityEvent(
        event_type="engine_event",
        workspace_id=str(payload.get("workspace_id") or "unknown"),
        job_id=payload.get("job_id"),
        title=str(payload.get("title") or "Engine event"),
        description=str(payload.get("description") or "Engine event recorded."),
        severity=str(payload.get("severity") or "info"),
        source="engine",
        metadata=dict(payload.get("metadata") or {}),
    )

    return asdict(event)


def build_api_usage_context(payload: Dict[str, Any]) -> Dict[str, Any]:
    event = ProductActivityEvent(
        event_type="api_usage",
        workspace_id=str(payload.get("workspace_id") or "unknown"),
        api_key_id=payload.get("api_key_id"),
        title=str(payload.get("title") or "API usage activity"),
        description=str(payload.get("description") or "API usage recorded."),
        severity=str(payload.get("severity") or "info"),
        source="api",
        metadata={
            "endpoint": payload.get("endpoint"),
            "method": payload.get("method"),
            "status_code": payload.get("status_code"),
            "au_used": payload.get("au_used"),
            **dict(payload.get("metadata") or {}),
        },
    )

    return asdict(event)


def build_billing_activity_context(payload: Dict[str, Any]) -> Dict[str, Any]:
    event = ProductActivityEvent(
        event_type="billing_activity",
        workspace_id=str(payload.get("workspace_id") or "unknown"),
        billing_event_id=payload.get("billing_event_id"),
        title=str(payload.get("title") or "Billing activity"),
        description=str(payload.get("description") or "Billing activity recorded."),
        severity=str(payload.get("severity") or "info"),
        source="billing",
        metadata={
            "plan": payload.get("plan"),
            "amount": payload.get("amount"),
            "currency": payload.get("currency"),
            "billing_status": payload.get("billing_status"),
            **dict(payload.get("metadata") or {}),
        },
    )

    return asdict(event)


def build_error_event_context(payload: Dict[str, Any]) -> Dict[str, Any]:
    event = ProductActivityEvent(
        event_type="error_event",
        workspace_id=str(payload.get("workspace_id") or "unknown"),
        job_id=payload.get("job_id"),
        error_code=payload.get("error_code"),
        title=str(payload.get("title") or "Product error event"),
        description=str(payload.get("description") or "Product error recorded."),
        severity=str(payload.get("severity") or "warning"),
        source=str(payload.get("source") or "system"),
        metadata={
            "trace_id": payload.get("trace_id"),
            "module": payload.get("module"),
            "recoverable": payload.get("recoverable"),
            **dict(payload.get("metadata") or {}),
        },
    )

    return asdict(event)


def correlate_error_events(
    events: List[Dict[str, Any]],
    workspace_id: str | None = None,
) -> Dict[str, Any]:
    scoped_events = [
        event for event in events
        if not workspace_id or event.get("workspace_id") == workspace_id
    ]

    error_events = [
        event for event in scoped_events
        if event.get("event_type") == "error_event"
        or str(event.get("severity")) in {"warning", "error", "critical"}
    ]

    by_module: Dict[str, int] = {}
    by_error_code: Dict[str, int] = {}

    for event in error_events:
        metadata = event.get("metadata") or {}
        module = str(metadata.get("module") or event.get("source") or "unknown")
        error_code = str(event.get("error_code") or "unknown")

        by_module[module] = by_module.get(module, 0) + 1
        by_error_code[error_code] = by_error_code.get(error_code, 0) + 1

    return {
        "workspace_id": workspace_id,
        "total_events": len(scoped_events),
        "total_error_events": len(error_events),
        "errors_by_module": by_module,
        "errors_by_code": by_error_code,
    }


def build_recent_product_activity_timeline(
    events: List[Dict[str, Any]],
    limit: int = 25,
) -> List[Dict[str, Any]]:
    sorted_events = sorted(
        events,
        key=lambda item: str(item.get("created_at") or ""),
        reverse=True,
    )

    return sorted_events[:limit]
