
from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List


ATTACHMENT_SECURITY_DIR = Path("backend/server/data/tms")
ATTACHMENT_ACCESS_LOG_PATH = ATTACHMENT_SECURITY_DIR / "attachment_access_log.jsonl"

SIGNED_URL_SECRET = "local-dev-attachment-secret"


@dataclass(frozen=True)
class AttachmentAccessEvent:
    event_type: str
    attachment_id: str
    actor_id: str
    actor_type: str
    allowed: bool
    reason: str
    ticket_id: str | None = None
    workspace_id: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


STAFF_ATTACHMENT_PERMISSIONS = {
    "support_agent": {"customer_visible"},
    "senior_agent": {"customer_visible", "internal"},
    "billing_agent": {"customer_visible", "internal"},
    "engineering": {"customer_visible", "internal"},
    "manager_admin": {"customer_visible", "internal", "restricted"},
    "owner": {"customer_visible", "internal", "restricted"},
}


CUSTOMER_ATTACHMENT_PERMISSIONS = {
    "customer_visible",
}


def _ensure_attachment_security_store() -> None:
    ATTACHMENT_SECURITY_DIR.mkdir(parents=True, exist_ok=True)

    if not ATTACHMENT_ACCESS_LOG_PATH.exists():
        ATTACHMENT_ACCESS_LOG_PATH.write_text("", encoding="utf-8")


def can_staff_access_attachment(staff_role: str, attachment: Dict[str, Any]) -> bool:
    visibility = str(attachment.get("visibility") or "customer_visible")
    allowed_visibility = STAFF_ATTACHMENT_PERMISSIONS.get(staff_role, set())

    return visibility in allowed_visibility


def can_customer_access_attachment(customer_key: str, attachment: Dict[str, Any]) -> bool:
    visibility = str(attachment.get("visibility") or "customer_visible")
    attachment_customer_key = attachment.get("customer_key")

    if visibility not in CUSTOMER_ATTACHMENT_PERMISSIONS:
        return False

    if attachment_customer_key and attachment_customer_key != customer_key:
        return False

    return True


def mark_attachment_internal_only(attachment: Dict[str, Any]) -> Dict[str, Any]:
    updated = dict(attachment)
    updated["visibility"] = "internal"
    return updated


def build_signed_attachment_url(
    attachment_id: str,
    expires_in_minutes: int = 15,
) -> Dict[str, Any]:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
    expires_ts = int(expires_at.timestamp())

    payload = f"{attachment_id}:{expires_ts}".encode("utf-8")
    signature = hmac.new(
        SIGNED_URL_SECRET.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return {
        "attachment_id": attachment_id,
        "url": f"/api/tms/attachments/{attachment_id}/download?expires={expires_ts}&signature={signature}",
        "expires_at": expires_at.isoformat(),
        "signature": signature,
    }


def verify_signed_attachment_url(
    attachment_id: str,
    expires: int,
    signature: str,
) -> bool:
    if datetime.now(timezone.utc).timestamp() > expires:
        return False

    payload = f"{attachment_id}:{expires}".encode("utf-8")
    expected_signature = hmac.new(
        SIGNED_URL_SECRET.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)


def log_attachment_access(event: AttachmentAccessEvent) -> None:
    _ensure_attachment_security_store()

    with ATTACHMENT_ACCESS_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")


def build_attachment_audit_event(
    attachment_id: str,
    actor_id: str,
    actor_type: str,
    allowed: bool,
    reason: str,
    ticket_id: str | None = None,
    workspace_id: str | None = None,
) -> AttachmentAccessEvent:
    return AttachmentAccessEvent(
        event_type="attachment_access_audit",
        attachment_id=attachment_id,
        actor_id=actor_id,
        actor_type=actor_type,
        allowed=allowed,
        reason=reason,
        ticket_id=ticket_id,
        workspace_id=workspace_id,
    )


def read_attachment_access_log(limit: int = 500) -> List[Dict[str, Any]]:
    _ensure_attachment_security_store()

    lines = ATTACHMENT_ACCESS_LOG_PATH.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[-limit:] if line.strip()]
