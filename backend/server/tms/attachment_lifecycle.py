
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List


ATTACHMENT_LIFECYCLE_DIR = Path("backend/server/data/tms")
ATTACHMENT_LIFECYCLE_LOG_PATH = ATTACHMENT_LIFECYCLE_DIR / "attachment_lifecycle_log.jsonl"

DEFAULT_RETENTION_DAYS = 365
INTERNAL_RETENTION_DAYS = 730
DELETED_RECOVERY_DAYS = 30


@dataclass(frozen=True)
class AttachmentLifecycleEvent:
    event_type: str
    attachment_id: str
    action: str
    status: str
    actor_id: str | None = None
    ticket_id: str | None = None
    workspace_id: str | None = None
    reason: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def _ensure_lifecycle_store() -> None:
    ATTACHMENT_LIFECYCLE_DIR.mkdir(parents=True, exist_ok=True)

    if not ATTACHMENT_LIFECYCLE_LOG_PATH.exists():
        ATTACHMENT_LIFECYCLE_LOG_PATH.write_text("", encoding="utf-8")


def log_attachment_lifecycle_event(event: AttachmentLifecycleEvent) -> None:
    _ensure_lifecycle_store()

    with ATTACHMENT_LIFECYCLE_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")


def get_attachment_retention_days(attachment: Dict[str, Any]) -> int:
    visibility = str(attachment.get("visibility") or "customer_visible")

    if visibility == "internal":
        return INTERNAL_RETENTION_DAYS

    return DEFAULT_RETENTION_DAYS


def is_attachment_expired(
    attachment: Dict[str, Any],
    now: datetime | None = None,
) -> bool:
    current_time = now or datetime.now(timezone.utc)
    created_at_raw = str(attachment.get("created_at") or "")

    if not created_at_raw:
        return False

    created_at = datetime.fromisoformat(created_at_raw.replace("Z", "+00:00"))

    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    retention_days = get_attachment_retention_days(attachment)
    expires_at = created_at + timedelta(days=retention_days)

    return current_time > expires_at


def build_attachment_cleanup_candidates(
    attachments: List[Dict[str, Any]],
    now: datetime | None = None,
) -> List[Dict[str, Any]]:
    return [
        attachment
        for attachment in attachments
        if is_attachment_expired(attachment, now=now)
        and not attachment.get("deleted_at")
    ]


def soft_delete_attachment(
    attachment: Dict[str, Any],
    actor_id: str | None = None,
    reason: str | None = None,
) -> Dict[str, Any]:
    updated = dict(attachment)
    updated["deleted_at"] = datetime.now(timezone.utc).isoformat()
    updated["delete_status"] = "soft_deleted"
    updated["recoverable_until"] = (
        datetime.now(timezone.utc) + timedelta(days=DELETED_RECOVERY_DAYS)
    ).isoformat()

    log_attachment_lifecycle_event(
        AttachmentLifecycleEvent(
            event_type="attachment_soft_deleted",
            attachment_id=str(updated.get("attachment_id")),
            action="soft_delete",
            status="soft_deleted",
            actor_id=actor_id,
            ticket_id=updated.get("ticket_id"),
            workspace_id=updated.get("workspace_id"),
            reason=reason,
        )
    )

    return updated


def can_recover_attachment(
    attachment: Dict[str, Any],
    now: datetime | None = None,
) -> bool:
    recoverable_until_raw = attachment.get("recoverable_until")

    if not recoverable_until_raw:
        return False

    current_time = now or datetime.now(timezone.utc)
    recoverable_until = datetime.fromisoformat(
        str(recoverable_until_raw).replace("Z", "+00:00")
    )

    if recoverable_until.tzinfo is None:
        recoverable_until = recoverable_until.replace(tzinfo=timezone.utc)

    return current_time <= recoverable_until


def recover_soft_deleted_attachment(
    attachment: Dict[str, Any],
    actor_id: str | None = None,
) -> Dict[str, Any]:
    if not can_recover_attachment(attachment):
        raise ValueError("Attachment is no longer recoverable.")

    updated = dict(attachment)
    updated.pop("deleted_at", None)
    updated.pop("recoverable_until", None)
    updated["delete_status"] = "active"

    log_attachment_lifecycle_event(
        AttachmentLifecycleEvent(
            event_type="attachment_recovered",
            attachment_id=str(updated.get("attachment_id")),
            action="recover",
            status="active",
            actor_id=actor_id,
            ticket_id=updated.get("ticket_id"),
            workspace_id=updated.get("workspace_id"),
        )
    )

    return updated


def permanently_delete_attachment(
    attachment: Dict[str, Any],
    actor_id: str | None = None,
    reason: str | None = None,
) -> Dict[str, Any]:
    updated = dict(attachment)
    storage_path = updated.get("storage_path")

    if storage_path and Path(storage_path).exists():
        Path(storage_path).unlink()

    updated["delete_status"] = "permanently_deleted"
    updated["permanently_deleted_at"] = datetime.now(timezone.utc).isoformat()

    log_attachment_lifecycle_event(
        AttachmentLifecycleEvent(
            event_type="attachment_permanently_deleted",
            attachment_id=str(updated.get("attachment_id")),
            action="permanent_delete",
            status="permanently_deleted",
            actor_id=actor_id,
            ticket_id=updated.get("ticket_id"),
            workspace_id=updated.get("workspace_id"),
            reason=reason,
        )
    )

    return updated


def read_attachment_lifecycle_events(limit: int = 500) -> List[Dict[str, Any]]:
    _ensure_lifecycle_store()

    lines = ATTACHMENT_LIFECYCLE_LOG_PATH.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[-limit:] if line.strip()]
