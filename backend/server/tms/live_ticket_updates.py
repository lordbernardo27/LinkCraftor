
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data/tms")

LIVE_TICKET_UPDATES_PATH = DATA_DIR / "live_ticket_updates.jsonl"
TICKET_SUBSCRIBERS_PATH = DATA_DIR / "ticket_subscribers.jsonl"
LIVE_TICKET_UPDATE_AUDIT_PATH = DATA_DIR / "live_ticket_update_audit.jsonl"


@dataclass(frozen=True)
class TicketUpdateEvent:
    event_id: str
    ticket_id: str
    workspace_id: str
    event_type: str
    actor_id: str | None = None
    previous_state: Dict[str, Any] = field(default_factory=dict)
    current_state: Dict[str, Any] = field(default_factory=dict)
    changed_fields: List[str] = field(default_factory=list)
    payload: Dict[str, Any] = field(default_factory=dict)
    sequence_number: int = 1
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass(frozen=True)
class TicketSubscriber:
    subscription_id: str
    subscriber_id: str
    workspace_id: str
    ticket_id: str | None = None
    connection_id: str | None = None
    channel: str = "ticket_updates"
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)
    subscribed_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for path in (
        LIVE_TICKET_UPDATES_PATH,
        TICKET_SUBSCRIBERS_PATH,
        LIVE_TICKET_UPDATE_AUDIT_PATH,
    ):
        if not path.exists():
            path.write_text("", encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"{prefix}_{timestamp}"


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    _ensure_store()

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _read_jsonl(
    path: Path,
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    _ensure_store()

    if limit <= 0:
        return []

    lines = path.read_text(encoding="utf-8").splitlines()

    return [
        json.loads(line)
        for line in lines[-limit:]
        if line.strip()
    ]


def _audit(
    *,
    event_type: str,
    workspace_id: str,
    ticket_id: str | None = None,
    actor_id: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    payload = {
        "event_type": event_type,
        "workspace_id": workspace_id,
        "ticket_id": ticket_id,
        "actor_id": actor_id,
        "metadata": metadata or {},
        "created_at": _utc_now(),
    }

    _append_jsonl(
        LIVE_TICKET_UPDATE_AUDIT_PATH,
        payload,
    )

    return payload


def _validate_required_text(
    value: str,
    field_name: str,
) -> str:
    normalized = str(value or "").strip()

    if not normalized:
        raise ValueError(
            f"{field_name} must be a non-empty string."
        )

    return normalized


def _calculate_changed_fields(
    previous_state: Dict[str, Any],
    current_state: Dict[str, Any],
) -> List[str]:
    keys = set(previous_state) | set(current_state)

    return sorted(
        key
        for key in keys
        if previous_state.get(key) != current_state.get(key)
    )


def _next_ticket_sequence(
    *,
    ticket_id: str,
    workspace_id: str,
) -> int:
    events = read_live_ticket_updates(limit=100000)

    ticket_events = [
        event
        for event in events
        if str(event.get("ticket_id")) == str(ticket_id)
        and str(event.get("workspace_id")) == str(workspace_id)
    ]

    if not ticket_events:
        return 1

    return max(
        int(event.get("sequence_number") or 0)
        for event in ticket_events
    ) + 1


# ============================================================
# 22.2.1 TICKET UPDATE EVENT MODEL
# ============================================================

def build_ticket_update_event(
    *,
    ticket_id: str,
    workspace_id: str,
    event_type: str,
    actor_id: str | None = None,
    previous_state: Dict[str, Any] | None = None,
    current_state: Dict[str, Any] | None = None,
    payload: Dict[str, Any] | None = None,
) -> TicketUpdateEvent:
    normalized_ticket_id = _validate_required_text(
        ticket_id,
        "ticket_id",
    )
    normalized_workspace_id = _validate_required_text(
        workspace_id,
        "workspace_id",
    )
    normalized_event_type = _validate_required_text(
        event_type,
        "event_type",
    )

    previous = dict(previous_state or {})
    current = dict(current_state or {})

    return TicketUpdateEvent(
        event_id=_new_id("ticket_update"),
        ticket_id=normalized_ticket_id,
        workspace_id=normalized_workspace_id,
        event_type=normalized_event_type,
        actor_id=actor_id,
        previous_state=previous,
        current_state=current,
        changed_fields=_calculate_changed_fields(
            previous,
            current,
        ),
        payload=dict(payload or {}),
        sequence_number=_next_ticket_sequence(
            ticket_id=normalized_ticket_id,
            workspace_id=normalized_workspace_id,
        ),
    )


# ============================================================
# 22.2.2 REAL-TIME TICKET CHANGE PUBLISHING
# ============================================================

def publish_ticket_update(
    *,
    ticket_id: str,
    workspace_id: str,
    event_type: str,
    actor_id: str | None = None,
    previous_state: Dict[str, Any] | None = None,
    current_state: Dict[str, Any] | None = None,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    event = build_ticket_update_event(
        ticket_id=ticket_id,
        workspace_id=workspace_id,
        event_type=event_type,
        actor_id=actor_id,
        previous_state=previous_state,
        current_state=current_state,
        payload=payload,
    )

    event_payload = asdict(event)

    subscribers = get_ticket_update_subscribers(
        workspace_id=event.workspace_id,
        ticket_id=event.ticket_id,
        active_only=True,
    )

    published_payload = {
        **event_payload,
        "subscriber_count": len(subscribers),
        "subscriber_ids": [
            subscriber.get("subscriber_id")
            for subscriber in subscribers
        ],
        "delivery_status": "published",
        "published_at": _utc_now(),
    }

    _append_jsonl(
        LIVE_TICKET_UPDATES_PATH,
        published_payload,
    )

    _audit(
        event_type="ticket_update_published",
        workspace_id=event.workspace_id,
        ticket_id=event.ticket_id,
        actor_id=actor_id,
        metadata={
            "event_id": event.event_id,
            "ticket_event_type": event.event_type,
            "sequence_number": event.sequence_number,
            "changed_fields": event.changed_fields,
            "subscriber_count": len(subscribers),
        },
    )

    return published_payload


def publish_ticket_created(
    *,
    ticket: Dict[str, Any],
    workspace_id: str,
    actor_id: str | None = None,
) -> Dict[str, Any]:
    ticket_id = str(
        ticket.get("id")
        or ticket.get("ticket_id")
        or ""
    )

    return publish_ticket_update(
        ticket_id=ticket_id,
        workspace_id=workspace_id,
        event_type="ticket_created",
        actor_id=actor_id,
        previous_state={},
        current_state=dict(ticket),
        payload={
            "source": "ticket_creation",
        },
    )


def publish_ticket_state_change(
    *,
    ticket_id: str,
    workspace_id: str,
    previous_state: Dict[str, Any],
    current_state: Dict[str, Any],
    actor_id: str | None = None,
) -> Dict[str, Any]:
    return publish_ticket_update(
        ticket_id=ticket_id,
        workspace_id=workspace_id,
        event_type="ticket_state_changed",
        actor_id=actor_id,
        previous_state=previous_state,
        current_state=current_state,
        payload={
            "change_type": "state_transition",
        },
    )


def publish_ticket_assignment_change(
    *,
    ticket_id: str,
    workspace_id: str,
    previous_assignee_id: str | None,
    new_assignee_id: str | None,
    actor_id: str | None = None,
) -> Dict[str, Any]:
    return publish_ticket_update(
        ticket_id=ticket_id,
        workspace_id=workspace_id,
        event_type="ticket_assignment_changed",
        actor_id=actor_id,
        previous_state={
            "assigned_to": previous_assignee_id,
        },
        current_state={
            "assigned_to": new_assignee_id,
        },
        payload={
            "previous_assignee_id": previous_assignee_id,
            "new_assignee_id": new_assignee_id,
        },
    )


def publish_ticket_message_added(
    *,
    ticket_id: str,
    workspace_id: str,
    message_id: str,
    sender_id: str,
    message_type: str = "reply",
    actor_id: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return publish_ticket_update(
        ticket_id=ticket_id,
        workspace_id=workspace_id,
        event_type="ticket_message_added",
        actor_id=actor_id or sender_id,
        payload={
            "message_id": message_id,
            "sender_id": sender_id,
            "message_type": message_type,
            **(metadata or {}),
        },
    )


# ============================================================
# 22.2.3 TICKET SUBSCRIBER REGISTRY
# ============================================================

def register_ticket_subscriber(
    *,
    subscriber_id: str,
    workspace_id: str,
    ticket_id: str | None = None,
    connection_id: str | None = None,
    channel: str = "ticket_updates",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    normalized_subscriber_id = _validate_required_text(
        subscriber_id,
        "subscriber_id",
    )
    normalized_workspace_id = _validate_required_text(
        workspace_id,
        "workspace_id",
    )
    normalized_channel = _validate_required_text(
        channel,
        "channel",
    )

    subscription = TicketSubscriber(
        subscription_id=_new_id("ticket_subscription"),
        subscriber_id=normalized_subscriber_id,
        workspace_id=normalized_workspace_id,
        ticket_id=(
            str(ticket_id).strip()
            if ticket_id is not None
            else None
        ),
        connection_id=connection_id,
        channel=normalized_channel,
        status="active",
        metadata=dict(metadata or {}),
    )

    payload = asdict(subscription)

    _append_jsonl(
        TICKET_SUBSCRIBERS_PATH,
        payload,
    )

    _audit(
        event_type="ticket_subscriber_registered",
        workspace_id=normalized_workspace_id,
        ticket_id=subscription.ticket_id,
        actor_id=normalized_subscriber_id,
        metadata={
            "subscription_id": subscription.subscription_id,
            "connection_id": connection_id,
            "channel": normalized_channel,
        },
    )

    return payload


def unregister_ticket_subscriber(
    *,
    subscriber_id: str,
    workspace_id: str,
    ticket_id: str | None = None,
    connection_id: str | None = None,
    reason: str = "subscriber_disconnected",
) -> Dict[str, Any]:
    payload = {
        "subscription_id": _new_id("ticket_unsubscribe"),
        "subscriber_id": _validate_required_text(
            subscriber_id,
            "subscriber_id",
        ),
        "workspace_id": _validate_required_text(
            workspace_id,
            "workspace_id",
        ),
        "ticket_id": ticket_id,
        "connection_id": connection_id,
        "channel": "ticket_updates",
        "status": "inactive",
        "reason": reason,
        "metadata": {},
        "subscribed_at": None,
        "updated_at": _utc_now(),
    }

    _append_jsonl(
        TICKET_SUBSCRIBERS_PATH,
        payload,
    )

    _audit(
        event_type="ticket_subscriber_unregistered",
        workspace_id=payload["workspace_id"],
        ticket_id=ticket_id,
        actor_id=payload["subscriber_id"],
        metadata={
            "connection_id": connection_id,
            "reason": reason,
        },
    )

    return payload


def read_ticket_subscriber_events(
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    return _read_jsonl(
        TICKET_SUBSCRIBERS_PATH,
        limit,
    )


def get_ticket_update_subscribers(
    *,
    workspace_id: str,
    ticket_id: str | None = None,
    active_only: bool = True,
) -> List[Dict[str, Any]]:
    normalized_workspace_id = _validate_required_text(
        workspace_id,
        "workspace_id",
    )

    events = read_ticket_subscriber_events(
        limit=100000,
    )

    latest_by_identity: Dict[str, Dict[str, Any]] = {}

    for event in events:
        if (
            str(event.get("workspace_id"))
            != normalized_workspace_id
        ):
            continue

        event_ticket_id = event.get("ticket_id")

        if (
            ticket_id is not None
            and event_ticket_id not in {
                None,
                "",
                ticket_id,
            }
        ):
            continue

        identity_key = "|".join(
            [
                str(event.get("subscriber_id") or ""),
                str(event.get("connection_id") or ""),
                str(event_ticket_id or "*"),
                str(event.get("channel") or ""),
            ]
        )

        latest_by_identity[identity_key] = event

    subscribers = list(
        latest_by_identity.values()
    )

    if active_only:
        subscribers = [
            subscriber
            for subscriber in subscribers
            if str(subscriber.get("status")) == "active"
        ]

    return subscribers


def build_ticket_subscriber_snapshot(
    *,
    workspace_id: str,
    ticket_id: str | None = None,
) -> Dict[str, Any]:
    active_subscribers = get_ticket_update_subscribers(
        workspace_id=workspace_id,
        ticket_id=ticket_id,
        active_only=True,
    )

    all_subscribers = get_ticket_update_subscribers(
        workspace_id=workspace_id,
        ticket_id=ticket_id,
        active_only=False,
    )

    return {
        "workspace_id": workspace_id,
        "ticket_id": ticket_id,
        "active_subscriber_count": len(
            active_subscribers
        ),
        "tracked_subscription_count": len(
            all_subscribers
        ),
        "active_subscribers": active_subscribers,
        "all_subscriptions": all_subscribers,
        "generated_at": _utc_now(),
    }


# ============================================================
# 22.2.4 WORKSPACE-SCOPED TICKET STREAMS
# ============================================================

def read_live_ticket_updates(
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    return _read_jsonl(
        LIVE_TICKET_UPDATES_PATH,
        limit,
    )


def get_workspace_ticket_stream(
    *,
    workspace_id: str,
    limit: int = 500,
    after_sequence: int | None = None,
) -> List[Dict[str, Any]]:
    normalized_workspace_id = _validate_required_text(
        workspace_id,
        "workspace_id",
    )

    events = read_live_ticket_updates(
        limit=100000,
    )

    scoped = [
        event
        for event in events
        if str(event.get("workspace_id"))
        == normalized_workspace_id
    ]

    if after_sequence is not None:
        scoped = [
            event
            for event in scoped
            if int(event.get("sequence_number") or 0)
            > int(after_sequence)
        ]

    return scoped[-limit:]


def get_ticket_update_stream(
    *,
    ticket_id: str,
    workspace_id: str,
    limit: int = 500,
    after_sequence: int | None = None,
) -> List[Dict[str, Any]]:
    normalized_ticket_id = _validate_required_text(
        ticket_id,
        "ticket_id",
    )
    normalized_workspace_id = _validate_required_text(
        workspace_id,
        "workspace_id",
    )

    events = read_live_ticket_updates(
        limit=100000,
    )

    scoped = [
        event
        for event in events
        if str(event.get("ticket_id"))
        == normalized_ticket_id
        and str(event.get("workspace_id"))
        == normalized_workspace_id
    ]

    if after_sequence is not None:
        scoped = [
            event
            for event in scoped
            if int(event.get("sequence_number") or 0)
            > int(after_sequence)
        ]

    return scoped[-limit:]


def get_latest_ticket_update(
    *,
    ticket_id: str,
    workspace_id: str,
) -> Dict[str, Any] | None:
    events = get_ticket_update_stream(
        ticket_id=ticket_id,
        workspace_id=workspace_id,
        limit=1,
    )

    return events[-1] if events else None


def build_workspace_ticket_stream_snapshot(
    *,
    workspace_id: str,
    limit: int = 500,
) -> Dict[str, Any]:
    events = get_workspace_ticket_stream(
        workspace_id=workspace_id,
        limit=limit,
    )

    active_subscribers = get_ticket_update_subscribers(
        workspace_id=workspace_id,
        active_only=True,
    )

    tickets = sorted(
        {
            str(event.get("ticket_id"))
            for event in events
            if event.get("ticket_id")
        }
    )

    return {
        "workspace_id": workspace_id,
        "event_count": len(events),
        "ticket_count": len(tickets),
        "active_subscriber_count": len(
            active_subscribers
        ),
        "tickets": tickets,
        "events": events,
        "generated_at": _utc_now(),
    }


# ============================================================
# 22.2.5 TICKET UPDATE AUDIT LOG
# ============================================================

def read_live_ticket_update_audit(
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    return _read_jsonl(
        LIVE_TICKET_UPDATE_AUDIT_PATH,
        limit,
    )


def get_ticket_update_audit(
    *,
    ticket_id: str,
    workspace_id: str,
    limit: int = 500,
) -> List[Dict[str, Any]]:
    normalized_ticket_id = _validate_required_text(
        ticket_id,
        "ticket_id",
    )
    normalized_workspace_id = _validate_required_text(
        workspace_id,
        "workspace_id",
    )

    events = read_live_ticket_update_audit(
        limit=100000,
    )

    scoped = [
        event
        for event in events
        if str(event.get("ticket_id"))
        == normalized_ticket_id
        and str(event.get("workspace_id"))
        == normalized_workspace_id
    ]

    return scoped[-limit:]


def build_live_ticket_update_health_snapshot(
    *,
    workspace_id: str,
) -> Dict[str, Any]:
    stream = get_workspace_ticket_stream(
        workspace_id=workspace_id,
        limit=100000,
    )

    subscribers = get_ticket_update_subscribers(
        workspace_id=workspace_id,
        active_only=True,
    )

    failed_events = [
        event
        for event in stream
        if str(event.get("delivery_status"))
        not in {"published", "delivered"}
    ]

    return {
        "workspace_id": workspace_id,
        "published_event_count": len(stream),
        "active_subscriber_count": len(subscribers),
        "failed_event_count": len(failed_events),
        "healthy": len(failed_events) == 0,
        "latest_event": (
            stream[-1]
            if stream
            else None
        ),
        "generated_at": _utc_now(),
    }
