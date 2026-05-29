
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


EMAIL_DATA_DIR = Path("backend/server/data/tms")
EMAIL_QUEUE_PATH = EMAIL_DATA_DIR / "outbound_email_queue.jsonl"
EMAIL_DELIVERY_LOG_PATH = EMAIL_DATA_DIR / "email_delivery_log.jsonl"


@dataclass(frozen=True)
class OutboundEmail:
    email_type: str
    to_email: str
    subject: str
    body: str
    ticket_id: str | None = None
    workspace_id: str | None = None
    cc: List[str] = field(default_factory=list)
    bcc: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass(frozen=True)
class EmailDeliveryLog:
    email_type: str
    to_email: str
    subject: str
    status: str
    ticket_id: str | None = None
    workspace_id: str | None = None
    provider_message_id: str | None = None
    error: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class EmailProvider:
    def send(self, email: OutboundEmail) -> EmailDeliveryLog:
        raise NotImplementedError


class LocalEmailProvider(EmailProvider):
    def send(self, email: OutboundEmail) -> EmailDeliveryLog:
        return EmailDeliveryLog(
            email_type=email.email_type,
            to_email=email.to_email,
            subject=email.subject,
            status="queued_local",
            ticket_id=email.ticket_id,
            workspace_id=email.workspace_id,
            provider_message_id=None,
            metadata={"provider": "local_dev"},
        )


def _ensure_email_store() -> None:
    EMAIL_DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not EMAIL_QUEUE_PATH.exists():
        EMAIL_QUEUE_PATH.write_text("", encoding="utf-8")

    if not EMAIL_DELIVERY_LOG_PATH.exists():
        EMAIL_DELIVERY_LOG_PATH.write_text("", encoding="utf-8")


def enqueue_outbound_email(email: OutboundEmail) -> None:
    _ensure_email_store()

    with EMAIL_QUEUE_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(email), ensure_ascii=False) + "\n")


def log_email_delivery(event: EmailDeliveryLog) -> None:
    _ensure_email_store()

    with EMAIL_DELIVERY_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")


def send_email_via_provider(
    email: OutboundEmail,
    provider: EmailProvider | None = None,
) -> EmailDeliveryLog:
    provider = provider or LocalEmailProvider()
    delivery_log = provider.send(email)
    log_email_delivery(delivery_log)
    return delivery_log


def build_staff_reply_email(
    ticket_id: str,
    to_email: str,
    reply_body: str,
    workspace_id: str | None = None,
) -> OutboundEmail:
    return OutboundEmail(
        email_type="staff_reply",
        to_email=to_email,
        subject=f"Update on your LinkCraftor support ticket {ticket_id}",
        body=reply_body,
        ticket_id=ticket_id,
        workspace_id=workspace_id,
    )


def build_ticket_notification_email(
    ticket_id: str,
    to_email: str,
    notification_body: str,
    workspace_id: str | None = None,
) -> OutboundEmail:
    return OutboundEmail(
        email_type="ticket_notification",
        to_email=to_email,
        subject=f"LinkCraftor support ticket notification: {ticket_id}",
        body=notification_body,
        ticket_id=ticket_id,
        workspace_id=workspace_id,
    )


def build_sla_breach_email_alert(
    ticket_id: str,
    to_email: str,
    breach_summary: str,
    workspace_id: str | None = None,
) -> OutboundEmail:
    return OutboundEmail(
        email_type="sla_breach_alert",
        to_email=to_email,
        subject=f"SLA breach alert for ticket {ticket_id}",
        body=breach_summary,
        ticket_id=ticket_id,
        workspace_id=workspace_id,
    )


def build_escalation_email_alert(
    ticket_id: str,
    to_email: str,
    escalation_summary: str,
    workspace_id: str | None = None,
) -> OutboundEmail:
    return OutboundEmail(
        email_type="escalation_alert",
        to_email=to_email,
        subject=f"Escalation alert for ticket {ticket_id}",
        body=escalation_summary,
        ticket_id=ticket_id,
        workspace_id=workspace_id,
    )


def read_outbound_email_queue(limit: int = 100) -> List[Dict[str, Any]]:
    _ensure_email_store()

    lines = EMAIL_QUEUE_PATH.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[-limit:] if line.strip()]


def read_email_delivery_log(limit: int = 100) -> List[Dict[str, Any]]:
    _ensure_email_store()

    lines = EMAIL_DELIVERY_LOG_PATH.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[-limit:] if line.strip()]
