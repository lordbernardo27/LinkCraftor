
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


EMAIL_MONITORING_DIR = Path("backend/server/data/tms")
EMAIL_EVENT_LOG_PATH = EMAIL_MONITORING_DIR / "email_events.jsonl"


@dataclass(frozen=True)
class EmailEvent:
    event_type: str
    email_type: str
    status: str
    to_email: str | None = None
    ticket_id: str | None = None
    workspace_id: str | None = None
    provider_message_id: str | None = None
    retry_count: int = 0
    error: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def _ensure_email_monitoring_store() -> None:
    EMAIL_MONITORING_DIR.mkdir(parents=True, exist_ok=True)

    if not EMAIL_EVENT_LOG_PATH.exists():
        EMAIL_EVENT_LOG_PATH.write_text("", encoding="utf-8")


def log_email_event(event: EmailEvent) -> None:
    _ensure_email_monitoring_store()

    with EMAIL_EVENT_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")


def detect_email_bounce(event: Dict[str, Any]) -> bool:
    status = str(event.get("status") or "").lower()
    error = str(event.get("error") or "").lower()
    event_type = str(event.get("event_type") or "").lower()

    bounce_signals = [
        "bounce",
        "bounced",
        "mailbox unavailable",
        "undeliverable",
        "recipient rejected",
    ]

    return any(signal in status or signal in error or signal in event_type for signal in bounce_signals)


def should_retry_email_delivery(event: Dict[str, Any], max_retries: int = 3) -> bool:
    status = str(event.get("status") or "").lower()
    retry_count = int(event.get("retry_count") or 0)

    if retry_count >= max_retries:
        return False

    retryable_statuses = {
        "failed",
        "timeout",
        "temporary_failure",
        "rate_limited",
        "queued_local",
    }

    return status in retryable_statuses and not detect_email_bounce(event)


def build_email_retry_event(event: Dict[str, Any]) -> EmailEvent:
    return EmailEvent(
        event_type="email_retry_scheduled",
        email_type=str(event.get("email_type") or "unknown"),
        status="retry_scheduled",
        to_email=event.get("to_email"),
        ticket_id=event.get("ticket_id"),
        workspace_id=event.get("workspace_id"),
        provider_message_id=event.get("provider_message_id"),
        retry_count=int(event.get("retry_count") or 0) + 1,
        error=event.get("error"),
        metadata={
            "source_event_type": event.get("event_type"),
            "previous_status": event.get("status"),
        },
    )


def build_email_analytics_metrics(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_events = len(events)
    by_status: Dict[str, int] = {}
    by_email_type: Dict[str, int] = {}

    bounce_count = 0
    retry_count = 0
    failure_count = 0

    for event in events:
        status = str(event.get("status") or "unknown")
        email_type = str(event.get("email_type") or "unknown")

        by_status[status] = by_status.get(status, 0) + 1
        by_email_type[email_type] = by_email_type.get(email_type, 0) + 1

        if detect_email_bounce(event):
            bounce_count += 1

        if str(event.get("event_type")) == "email_retry_scheduled":
            retry_count += 1

        if status.lower() in {"failed", "timeout", "temporary_failure", "rate_limited"}:
            failure_count += 1

    return {
        "total_email_events": total_events,
        "failure_count": failure_count,
        "bounce_count": bounce_count,
        "retry_count": retry_count,
        "events_by_status": by_status,
        "events_by_email_type": by_email_type,
    }


def read_email_events(limit: int = 500) -> List[Dict[str, Any]]:
    _ensure_email_monitoring_store()

    lines = EMAIL_EVENT_LOG_PATH.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[-limit:] if line.strip()]


def build_email_audit_trail(
    ticket_id: str,
    events: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    ticket_events = [
        event for event in events
        if str(event.get("ticket_id") or "") == ticket_id
    ]

    return sorted(
        ticket_events,
        key=lambda item: str(item.get("created_at") or ""),
    )
