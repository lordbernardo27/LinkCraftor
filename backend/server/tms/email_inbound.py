
from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


SPAM_KEYWORDS = {
    "casino",
    "crypto giveaway",
    "free money",
    "loan approved",
    "miracle cure",
    "winner",
}


@dataclass(frozen=True)
class InboundEmailPayload:
    from_email: str
    subject: str
    body: str
    to_email: str | None = None
    message_id: str | None = None
    in_reply_to: str | None = None
    cc: List[str] = field(default_factory=list)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    received_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass(frozen=True)
class ParsedInboundEmail:
    message_id: str
    from_email: str
    customer_key: str
    subject: str
    body: str
    ticket_id: str | None
    is_reply: bool
    is_spam: bool
    attachments: List[Dict[str, Any]]
    created_at: str


def normalize_email_address(email: str) -> str:
    return email.strip().lower()


def build_customer_identity_key(email: str) -> str:
    normalized = normalize_email_address(email)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def extract_ticket_id_from_subject(subject: str) -> str | None:
    match = re.search(r"(TKT-\d+)", subject or "", flags=re.IGNORECASE)

    if not match:
        return None

    return match.group(1).upper()


def detect_spam_email(subject: str, body: str) -> bool:
    combined = f"{subject} {body}".lower()

    return any(keyword in combined for keyword in SPAM_KEYWORDS)


def extract_email_attachments(payload: InboundEmailPayload) -> List[Dict[str, Any]]:
    extracted: List[Dict[str, Any]] = []

    for item in payload.attachments:
        extracted.append(
            {
                "filename": item.get("filename"),
                "content_type": item.get("content_type") or item.get("mime_type"),
                "size_bytes": item.get("size_bytes"),
                "source": "inbound_email",
            }
        )

    return extracted


def parse_inbound_email(payload: InboundEmailPayload) -> ParsedInboundEmail:
    message_id = payload.message_id or hashlib.sha256(
        f"{payload.from_email}:{payload.subject}:{payload.received_at}".encode("utf-8")
    ).hexdigest()

    ticket_id = extract_ticket_id_from_subject(payload.subject)
    is_reply = bool(payload.in_reply_to or ticket_id)
    is_spam = detect_spam_email(payload.subject, payload.body)

    return ParsedInboundEmail(
        message_id=message_id,
        from_email=normalize_email_address(payload.from_email),
        customer_key=build_customer_identity_key(payload.from_email),
        subject=payload.subject,
        body=payload.body,
        ticket_id=ticket_id,
        is_reply=is_reply,
        is_spam=is_spam,
        attachments=extract_email_attachments(payload),
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def build_ticket_from_inbound_email(parsed: ParsedInboundEmail) -> Dict[str, Any]:
    if parsed.ticket_id:
        return {
            "mode": "thread_reply",
            "ticket_id": parsed.ticket_id,
            "message_id": parsed.message_id,
            "from_email": parsed.from_email,
            "body": parsed.body,
            "attachments": parsed.attachments,
        }

    generated_ticket_id = "TKT-EMAIL-" + parsed.message_id[:8].upper()

    return {
        "mode": "new_ticket",
        "ticket_id": generated_ticket_id,
        "customer_key": parsed.customer_key,
        "from_email": parsed.from_email,
        "subject": parsed.subject,
        "body": parsed.body,
        "status": "Open",
        "priority": "Medium",
        "category": "Email",
        "attachments": parsed.attachments,
    }


def handle_inbound_email_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    inbound_payload = InboundEmailPayload(
        from_email=str(payload.get("from_email") or payload.get("from") or ""),
        to_email=payload.get("to_email") or payload.get("to"),
        subject=str(payload.get("subject") or ""),
        body=str(payload.get("body") or payload.get("text") or ""),
        message_id=payload.get("message_id"),
        in_reply_to=payload.get("in_reply_to"),
        cc=list(payload.get("cc") or []),
        attachments=list(payload.get("attachments") or []),
    )

    parsed = parse_inbound_email(inbound_payload)

    if parsed.is_spam:
        return {
            "accepted": False,
            "reason": "spam_detected",
            "message_id": parsed.message_id,
        }

    ticket_payload = build_ticket_from_inbound_email(parsed)

    return {
        "accepted": True,
        "parsed": asdict(parsed),
        "ticket_payload": ticket_payload,
    }


def match_customer_identity(payload: InboundEmailPayload) -> Dict[str, str]:
    return {
        "email": normalize_email_address(payload.from_email),
        "customer_key": build_customer_identity_key(payload.from_email),
    }
