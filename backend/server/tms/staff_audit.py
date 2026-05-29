
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


AUDIT_DIR = Path("backend/server/data/tms")
AUDIT_LOG_PATH = AUDIT_DIR / "staff_audit_log.jsonl"


@dataclass(frozen=True)
class StaffAuditEvent:
    event_type: str
    staff_id: str
    staff_role: str
    ticket_id: str | None = None
    workspace_id: str | None = None
    action: str | None = None
    previous_value: Any | None = None
    new_value: Any | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def _ensure_audit_store() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    if not AUDIT_LOG_PATH.exists():
        AUDIT_LOG_PATH.write_text("", encoding="utf-8")


def log_staff_action(event: StaffAuditEvent) -> None:
    _ensure_audit_store()

    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")


def log_assignment_change(
    staff_id: str,
    staff_role: str,
    ticket_id: str,
    previous_assignee: str | None,
    new_assignee: str | None,
    workspace_id: str | None = None,
) -> None:
    log_staff_action(
        StaffAuditEvent(
            event_type="assignment_audit_trail",
            staff_id=staff_id,
            staff_role=staff_role,
            ticket_id=ticket_id,
            workspace_id=workspace_id,
            action="assignment_change",
            previous_value=previous_assignee,
            new_value=new_assignee,
        )
    )


def log_internal_note_event(
    staff_id: str,
    staff_role: str,
    ticket_id: str,
    note_id: str,
    workspace_id: str | None = None,
) -> None:
    log_staff_action(
        StaffAuditEvent(
            event_type="internal_note_audit_trail",
            staff_id=staff_id,
            staff_role=staff_role,
            ticket_id=ticket_id,
            workspace_id=workspace_id,
            action="internal_note_added",
            metadata={"note_id": note_id},
        )
    )


def log_ticket_lifecycle_event(
    staff_id: str,
    staff_role: str,
    ticket_id: str,
    previous_status: str | None,
    new_status: str,
    workspace_id: str | None = None,
) -> None:
    log_staff_action(
        StaffAuditEvent(
            event_type="ticket_lifecycle_audit_trail",
            staff_id=staff_id,
            staff_role=staff_role,
            ticket_id=ticket_id,
            workspace_id=workspace_id,
            action="status_change",
            previous_value=previous_status,
            new_value=new_status,
        )
    )


def detect_suspicious_staff_activity(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []

    close_events_by_staff: Dict[str, int] = {}
    restricted_attempts_by_staff: Dict[str, int] = {}

    for event in events:
        staff_id = str(event.get("staff_id") or "unknown")
        action = event.get("action")
        event_type = event.get("event_type")

        if action == "close_ticket":
            close_events_by_staff[staff_id] = close_events_by_staff.get(staff_id, 0) + 1

        if event_type == "permission_denied":
            restricted_attempts_by_staff[staff_id] = (
                restricted_attempts_by_staff.get(staff_id, 0) + 1
            )

    for staff_id, count in close_events_by_staff.items():
        if count >= 10:
            findings.append(
                {
                    "type": "high_close_volume",
                    "staff_id": staff_id,
                    "count": count,
                    "severity": "medium",
                }
            )

    for staff_id, count in restricted_attempts_by_staff.items():
        if count >= 3:
            findings.append(
                {
                    "type": "repeated_permission_denials",
                    "staff_id": staff_id,
                    "count": count,
                    "severity": "high",
                }
            )

    return findings


def read_staff_audit_events(limit: int = 100) -> List[Dict[str, Any]]:
    _ensure_audit_store()

    lines = AUDIT_LOG_PATH.read_text(encoding="utf-8").splitlines()
    rows = [json.loads(line) for line in lines[-limit:] if line.strip()]
    return rows
