
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict

from backend.server.tms.sla_policy import SLAPolicy, get_sla_policy_for_ticket


PAUSED_STATUSES = {
    "Waiting on Customer",
    "Resolved",
    "Closed",
}


@dataclass(frozen=True)
class SLATimerState:
    ticket_id: str
    priority: str
    status: str
    created_at: str
    first_response_due_at: str
    resolution_due_at: str
    escalation_due_at: str
    first_response_breached: bool
    resolution_breached: bool
    escalation_due: bool
    paused: bool
    remaining_first_response_minutes: int
    remaining_resolution_minutes: int
    remaining_escalation_minutes: int


def _parse_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


def _minutes_between(start: datetime, end: datetime) -> int:
    return int((end - start).total_seconds() // 60)


def _add_minutes(start: datetime, minutes: int) -> datetime:
    return start.timestamp() and start + __import__("datetime").timedelta(minutes=minutes)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def should_pause_sla(status: str) -> bool:
    return status in PAUSED_STATUSES


def should_exclude_waiting_on_customer(status: str) -> bool:
    return status == "Waiting on Customer"


def calculate_sla_timer_state(
    ticket: Dict[str, Any],
    workspace_tier: str = "default",
    now: datetime | None = None,
) -> Dict[str, Any]:
    current_time = now or datetime.now(timezone.utc)

    priority = str(ticket.get("priority") or "Medium")
    status = str(ticket.get("status") or "Open")
    ticket_id = str(ticket.get("id") or ticket.get("ticket_id") or "unknown")
    created_at_raw = str(ticket.get("created_at") or ticket.get("createdAt"))
    workspace_id = ticket.get("workspace_id") or ticket.get("workspace")

    created_at = _parse_datetime(created_at_raw)
    policy: SLAPolicy = get_sla_policy_for_ticket(
        priority=priority,
        workspace_tier=workspace_tier,
        workspace_id=workspace_id,
    )

    first_response_due_at = created_at + __import__("datetime").timedelta(
        minutes=policy.first_response_minutes
    )
    resolution_due_at = created_at + __import__("datetime").timedelta(
        minutes=policy.resolution_minutes
    )
    escalation_due_at = created_at + __import__("datetime").timedelta(
        minutes=policy.escalation_minutes
    )

    paused = should_pause_sla(status)
    waiting_customer_excluded = should_exclude_waiting_on_customer(status)

    if paused:
      first_response_breached = False
      resolution_breached = False
      escalation_due = False
    else:
      first_response_breached = current_time > first_response_due_at
      resolution_breached = current_time > resolution_due_at
      escalation_due = current_time > escalation_due_at

    state = SLATimerState(
        ticket_id=ticket_id,
        priority=priority,
        status=status,
        created_at=_iso(created_at),
        first_response_due_at=_iso(first_response_due_at),
        resolution_due_at=_iso(resolution_due_at),
        escalation_due_at=_iso(escalation_due_at),
        first_response_breached=first_response_breached,
        resolution_breached=resolution_breached,
        escalation_due=escalation_due,
        paused=paused or waiting_customer_excluded,
        remaining_first_response_minutes=max(
            0, _minutes_between(current_time, first_response_due_at)
        ),
        remaining_resolution_minutes=max(
            0, _minutes_between(current_time, resolution_due_at)
        ),
        remaining_escalation_minutes=max(
            0, _minutes_between(current_time, escalation_due_at)
        ),
    )

    return asdict(state)


def detect_sla_breaches(
    tickets: list[Dict[str, Any]],
    workspace_tier: str = "default",
) -> list[Dict[str, Any]]:
    breached: list[Dict[str, Any]] = []

    for ticket in tickets:
        state = calculate_sla_timer_state(ticket, workspace_tier=workspace_tier)

        if state["first_response_breached"] or state["resolution_breached"]:
            breached.append(
                {
                    "ticket_id": state["ticket_id"],
                    "priority": state["priority"],
                    "status": state["status"],
                    "first_response_breached": state["first_response_breached"],
                    "resolution_breached": state["resolution_breached"],
                    "escalation_due": state["escalation_due"],
                }
            )

    return breached
