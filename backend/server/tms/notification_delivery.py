
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data/tms")

DELIVERY_LOG_PATH = DATA_DIR / "notification_delivery_log.jsonl"
DELIVERY_AUDIT_PATH = DATA_DIR / "notification_delivery_audit.jsonl"
DELIVERY_FAILURE_PATH = DATA_DIR / "notification_delivery_failures.jsonl"


DELIVERY_CHANNELS = {
    "in_app": {
        "enabled": True,
        "implemented": True,
    },
    "email": {
        "enabled": True,
        "implemented": False,
    },
    "sms": {
        "enabled": False,
        "implemented": False,
    },
}


MAX_DELIVERY_RETRY_ATTEMPTS = 3


@dataclass(frozen=True)
class DeliveryRecord:
    delivery_id: str
    notification_id: str
    channel: str
    recipient_id: str | None = None
    workspace_id: str | None = None
    status: str = "queued"
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    delivered_at: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class DeliveryAuditEvent:
    event_type: str
    delivery_id: str | None = None
    notification_id: str | None = None
    channel: str | None = None
    status: str = "recorded"
    message: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _ensure_delivery_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for path in (
        DELIVERY_LOG_PATH,
        DELIVERY_AUDIT_PATH,
        DELIVERY_FAILURE_PATH,
    ):
        if not path.exists():
            path.write_text("", encoding="utf-8")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    _ensure_delivery_store()

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _read_jsonl(path: Path, limit: int = 1000) -> List[Dict[str, Any]]:
    _ensure_delivery_store()

    lines = path.read_text(encoding="utf-8").splitlines()
    rows: List[Dict[str, Any]] = []

    for line in lines[-limit:]:
        if not line.strip():
            continue

        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            rows.append(
                {
                    "parse_error": True,
                    "raw_line": line,
                }
            )

    return rows


def _delivery_id(notification_id: str, channel: str) -> str:
    ts = _utc_now().strftime("%Y%m%d%H%M%S%f")
    return f"delivery_{notification_id}_{channel}_{ts}"


def log_delivery_audit(event: DeliveryAuditEvent) -> Dict[str, Any]:
    payload = asdict(event)
    _append_jsonl(DELIVERY_AUDIT_PATH, payload)
    return payload


def create_delivery_record(
    *,
    notification_id: str,
    channel: str,
    recipient_id: str | None = None,
    workspace_id: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    record = DeliveryRecord(
        delivery_id=_delivery_id(notification_id, channel),
        notification_id=notification_id,
        channel=channel,
        recipient_id=recipient_id,
        workspace_id=workspace_id,
        metadata=metadata or {},
    )

    payload = asdict(record)

    _append_jsonl(DELIVERY_LOG_PATH, payload)

    log_delivery_audit(
        DeliveryAuditEvent(
            event_type="delivery_record_created",
            delivery_id=record.delivery_id,
            notification_id=notification_id,
            channel=channel,
            status="queued",
            message="Delivery record created.",
        )
    )

    return payload


def deliver_in_app_notification(
    *,
    notification_id: str,
    recipient_id: str,
    workspace_id: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    record = create_delivery_record(
        notification_id=notification_id,
        channel="in_app",
        recipient_id=recipient_id,
        workspace_id=workspace_id,
        metadata=metadata,
    )

    record["status"] = "delivered"
    record["delivered_at"] = _utc_now().isoformat()

    _append_jsonl(DELIVERY_LOG_PATH, record)

    log_delivery_audit(
        DeliveryAuditEvent(
            event_type="in_app_notification_delivered",
            delivery_id=record["delivery_id"],
            notification_id=notification_id,
            channel="in_app",
            status="delivered",
        )
    )

    return record


def deliver_email_notification(
    *,
    notification_id: str,
    recipient_email: str,
    workspace_id: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    record = create_delivery_record(
        notification_id=notification_id,
        channel="email",
        recipient_id=recipient_email,
        workspace_id=workspace_id,
        metadata={
            "delivery_mode": "email_stub",
            **(metadata or {}),
        },
    )

    record["status"] = "pending_provider"

    _append_jsonl(DELIVERY_LOG_PATH, record)

    log_delivery_audit(
        DeliveryAuditEvent(
            event_type="email_notification_queued",
            delivery_id=record["delivery_id"],
            notification_id=notification_id,
            channel="email",
            status="pending_provider",
            message="Waiting for email provider integration.",
        )
    )

    return record


def deliver_sms_notification(
    *,
    notification_id: str,
    phone_number: str,
    workspace_id: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    record = create_delivery_record(
        notification_id=notification_id,
        channel="sms",
        recipient_id=phone_number,
        workspace_id=workspace_id,
        metadata={
            "delivery_mode": "sms_stub",
            **(metadata or {}),
        },
    )

    record["status"] = "pending_provider"

    _append_jsonl(DELIVERY_LOG_PATH, record)

    log_delivery_audit(
        DeliveryAuditEvent(
            event_type="sms_notification_queued",
            delivery_id=record["delivery_id"],
            notification_id=notification_id,
            channel="sms",
            status="pending_provider",
            message="Waiting for SMS provider integration.",
        )
    )

    return record


def mark_delivery_failed(
    *,
    delivery_record: Dict[str, Any],
    reason: str,
) -> Dict[str, Any]:
    failed = {
        **delivery_record,
        "status": "failed",
        "failure_reason": reason,
        "failed_at": _utc_now().isoformat(),
    }

    _append_jsonl(DELIVERY_FAILURE_PATH, failed)

    log_delivery_audit(
        DeliveryAuditEvent(
            event_type="delivery_failed",
            delivery_id=str(delivery_record.get("delivery_id")),
            notification_id=str(delivery_record.get("notification_id")),
            channel=str(delivery_record.get("channel")),
            status="failed",
            message=reason,
        )
    )

    return failed


def should_retry_delivery(record: Dict[str, Any]) -> bool:
    retry_count = int(record.get("retry_count") or 0)
    status = str(record.get("status") or "")

    return (
        status == "failed"
        and retry_count < MAX_DELIVERY_RETRY_ATTEMPTS
    )


def build_delivery_retry(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        **record,
        "status": "queued",
        "retry_count": int(record.get("retry_count") or 0) + 1,
        "retry_requested_at": _utc_now().isoformat(),
    }


def read_delivery_logs(limit: int = 1000) -> List[Dict[str, Any]]:
    return _read_jsonl(DELIVERY_LOG_PATH, limit)


def read_delivery_failures(limit: int = 1000) -> List[Dict[str, Any]]:
    return _read_jsonl(DELIVERY_FAILURE_PATH, limit)


def read_delivery_audit(limit: int = 1000) -> List[Dict[str, Any]]:
    return _read_jsonl(DELIVERY_AUDIT_PATH, limit)


def delivery_metrics() -> Dict[str, Any]:
    records = read_delivery_logs(limit=100000)

    delivered = 0
    queued = 0
    failed = 0
    pending = 0

    for r in records:
        status = str(r.get("status") or "")

        if status == "delivered":
            delivered += 1
        elif status == "queued":
            queued += 1
        elif status == "failed":
            failed += 1
        elif status == "pending_provider":
            pending += 1

    return {
        "delivered": delivered,
        "queued": queued,
        "failed": failed,
        "pending_provider": pending,
        "total": len(records),
        "generated_at": _utc_now().isoformat(),
    }
