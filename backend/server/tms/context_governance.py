
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List


CONTEXT_GOVERNANCE_DIR = Path("backend/server/data/tms")
CONTEXT_ACCESS_LOG_PATH = CONTEXT_GOVERNANCE_DIR / "context_access_log.jsonl"

SENSITIVE_FIELDS = {
    "email",
    "owner_email",
    "customer_email",
    "billing_status",
    "failed_payment_count",
    "renewal_date",
    "amount",
    "currency",
}

ROLE_CONTEXT_VISIBILITY = {
    "support_agent": {"basic", "product", "support"},
    "senior_agent": {"basic", "product", "support", "risk"},
    "billing_agent": {"basic", "product", "support", "risk", "billing"},
    "engineering": {"basic", "product", "support", "technical"},
    "manager_admin": {"basic", "product", "support", "risk", "billing", "technical", "internal"},
    "owner": {"basic", "product", "support", "risk", "billing", "technical", "internal", "restricted"},
}


@dataclass(frozen=True)
class ContextAccessEvent:
    event_type: str
    actor_id: str
    actor_role: str
    context_type: str
    workspace_id: str | None = None
    ticket_id: str | None = None
    allowed: bool = True
    reason: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass(frozen=True)
class InternalIntelligenceNote:
    note_id: str
    ticket_id: str
    workspace_id: str
    note_type: str
    body: str
    visibility: str = "internal"
    created_by: str | None = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def _ensure_context_governance_store() -> None:
    CONTEXT_GOVERNANCE_DIR.mkdir(parents=True, exist_ok=True)

    if not CONTEXT_ACCESS_LOG_PATH.exists():
        CONTEXT_ACCESS_LOG_PATH.write_text("", encoding="utf-8")


def can_view_context(actor_role: str, context_level: str) -> bool:
    allowed_levels = ROLE_CONTEXT_VISIBILITY.get(actor_role, set())
    return context_level in allowed_levels


def mask_sensitive_context(
    context: Dict[str, Any],
    actor_role: str,
) -> Dict[str, Any]:
    if actor_role in {"billing_agent", "manager_admin", "owner"}:
        return dict(context)

    masked = {}

    for key, value in context.items():
        if key in SENSITIVE_FIELDS:
            masked[key] = "***MASKED***"
        else:
            masked[key] = value

    return masked


def log_context_access(event: ContextAccessEvent) -> None:
    _ensure_context_governance_store()

    with CONTEXT_ACCESS_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")


def build_context_access_response(
    actor_id: str,
    actor_role: str,
    context_type: str,
    context_level: str,
    context: Dict[str, Any],
    workspace_id: str | None = None,
    ticket_id: str | None = None,
) -> Dict[str, Any]:
    allowed = can_view_context(actor_role, context_level)

    log_context_access(
        ContextAccessEvent(
            event_type="context_access",
            actor_id=actor_id,
            actor_role=actor_role,
            context_type=context_type,
            workspace_id=workspace_id,
            ticket_id=ticket_id,
            allowed=allowed,
            reason="allowed" if allowed else "role_visibility_restricted",
        )
    )

    if not allowed:
        return {
            "allowed": False,
            "context_type": context_type,
            "reason": "role_visibility_restricted",
            "context": {},
        }

    return {
        "allowed": True,
        "context_type": context_type,
        "reason": "allowed",
        "context": mask_sensitive_context(context, actor_role),
    }


def build_internal_intelligence_note(
    note_id: str,
    ticket_id: str,
    workspace_id: str,
    note_type: str,
    body: str,
    created_by: str | None = None,
) -> Dict[str, Any]:
    note = InternalIntelligenceNote(
        note_id=note_id,
        ticket_id=ticket_id,
        workspace_id=workspace_id,
        note_type=note_type,
        body=body,
        created_by=created_by,
    )

    return asdict(note)


def should_retain_context(
    context: Dict[str, Any],
    retention_days: int = 365,
    now: datetime | None = None,
) -> bool:
    created_at_raw = context.get("created_at") or context.get("generated_at")

    if not created_at_raw:
        return True

    created_at = datetime.fromisoformat(str(created_at_raw).replace("Z", "+00:00"))

    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    current_time = now or datetime.now(timezone.utc)
    expires_at = created_at + timedelta(days=retention_days)

    return current_time <= expires_at


def read_context_access_log(limit: int = 500) -> List[Dict[str, Any]]:
    _ensure_context_governance_store()

    lines = CONTEXT_ACCESS_LOG_PATH.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[-limit:] if line.strip()]
