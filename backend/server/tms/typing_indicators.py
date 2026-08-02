
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data/tms")

TYPING_EVENTS_PATH = DATA_DIR / "typing_events.jsonl"
TYPING_AUDIT_PATH = DATA_DIR / "typing_indicator_audit.jsonl"


@dataclass(frozen=True)
class TypingEvent:
    event_id: str
    user_id: str
    workspace_id: str
    scope_type: str
    scope_id: str
    event_type: str
    display_name: str | None = None
    connection_id: str | None = None
    expires_at: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for path in (
        TYPING_EVENTS_PATH,
        TYPING_AUDIT_PATH,
    ):
        if not path.exists():
            path.write_text("", encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%d%H%M%S%f"
    )
    return f"{prefix}_{timestamp}"


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


def _append_jsonl(
    path: Path,
    payload: Dict[str, Any],
) -> None:
    _ensure_store()

    with path.open("a", encoding="utf-8") as f:
        f.write(
            json.dumps(payload, ensure_ascii=False)
            + "\n"
        )


def _read_jsonl(
    path: Path,
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    _ensure_store()

    if limit <= 0:
        return []

    lines = path.read_text(
        encoding="utf-8"
    ).splitlines()

    return [
        json.loads(line)
        for line in lines[-limit:]
        if line.strip()
    ]


def _parse_datetime(
    value: str | None,
) -> datetime | None:
    if not value:
        return None

    try:
        parsed = datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        return parsed.astimezone(timezone.utc)

    except (TypeError, ValueError):
        return None


def _audit(
    *,
    event_type: str,
    user_id: str,
    workspace_id: str,
    scope_type: str,
    scope_id: str,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    payload = {
        "event_type": event_type,
        "user_id": user_id,
        "workspace_id": workspace_id,
        "scope_type": scope_type,
        "scope_id": scope_id,
        "metadata": metadata or {},
        "created_at": _utc_now(),
    }

    _append_jsonl(
        TYPING_AUDIT_PATH,
        payload,
    )

    return payload


def _build_typing_event(
    *,
    user_id: str,
    workspace_id: str,
    scope_type: str,
    scope_id: str,
    event_type: str,
    display_name: str | None = None,
    connection_id: str | None = None,
    expires_in_seconds: int = 15,
    metadata: Dict[str, Any] | None = None,
) -> TypingEvent:
    normalized_user_id = _validate_required_text(
        user_id,
        "user_id",
    )
    normalized_workspace_id = _validate_required_text(
        workspace_id,
        "workspace_id",
    )
    normalized_scope_type = _validate_required_text(
        scope_type,
        "scope_type",
    )
    normalized_scope_id = _validate_required_text(
        scope_id,
        "scope_id",
    )
    normalized_event_type = _validate_required_text(
        event_type,
        "event_type",
    )

    allowed_scope_types = {
        "ticket",
        "collaboration_room",
    }

    if normalized_scope_type not in allowed_scope_types:
        raise ValueError(
            "scope_type must be 'ticket' or "
            "'collaboration_room'."
        )

    allowed_event_types = {
        "typing_started",
        "typing_stopped",
        "typing_expired",
    }

    if normalized_event_type not in allowed_event_types:
        raise ValueError(
            "Unsupported typing event type."
        )

    expires_at = None

    if normalized_event_type == "typing_started":
        safe_seconds = max(
            1,
            int(expires_in_seconds),
        )

        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(seconds=safe_seconds)
        ).isoformat()

    return TypingEvent(
        event_id=_new_id("typing_event"),
        user_id=normalized_user_id,
        workspace_id=normalized_workspace_id,
        scope_type=normalized_scope_type,
        scope_id=normalized_scope_id,
        event_type=normalized_event_type,
        display_name=display_name,
        connection_id=connection_id,
        expires_at=expires_at,
        metadata=dict(metadata or {}),
    )


def _write_typing_event(
    event: TypingEvent,
) -> Dict[str, Any]:
    payload = asdict(event)

    _append_jsonl(
        TYPING_EVENTS_PATH,
        payload,
    )

    _audit(
        event_type=event.event_type,
        user_id=event.user_id,
        workspace_id=event.workspace_id,
        scope_type=event.scope_type,
        scope_id=event.scope_id,
        metadata={
            "event_id": event.event_id,
            "connection_id": event.connection_id,
            "expires_at": event.expires_at,
        },
    )

    return payload


# ============================================================
# 22.3.1 TYPING-START EVENTS
# ============================================================

def start_typing(
    *,
    user_id: str,
    workspace_id: str,
    scope_type: str,
    scope_id: str,
    display_name: str | None = None,
    connection_id: str | None = None,
    expires_in_seconds: int = 15,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    event = _build_typing_event(
        user_id=user_id,
        workspace_id=workspace_id,
        scope_type=scope_type,
        scope_id=scope_id,
        event_type="typing_started",
        display_name=display_name,
        connection_id=connection_id,
        expires_in_seconds=expires_in_seconds,
        metadata=metadata,
    )

    return _write_typing_event(event)


# ============================================================
# 22.3.2 TYPING-STOP EVENTS
# ============================================================

def stop_typing(
    *,
    user_id: str,
    workspace_id: str,
    scope_type: str,
    scope_id: str,
    display_name: str | None = None,
    connection_id: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    event = _build_typing_event(
        user_id=user_id,
        workspace_id=workspace_id,
        scope_type=scope_type,
        scope_id=scope_id,
        event_type="typing_stopped",
        display_name=display_name,
        connection_id=connection_id,
        metadata=metadata,
    )

    return _write_typing_event(event)


def read_typing_events(
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    return _read_jsonl(
        TYPING_EVENTS_PATH,
        limit,
    )


def _latest_typing_events(
    *,
    workspace_id: str,
    scope_type: str,
    scope_id: str,
) -> List[Dict[str, Any]]:
    normalized_workspace_id = _validate_required_text(
        workspace_id,
        "workspace_id",
    )
    normalized_scope_type = _validate_required_text(
        scope_type,
        "scope_type",
    )
    normalized_scope_id = _validate_required_text(
        scope_id,
        "scope_id",
    )

    events = read_typing_events(
        limit=100000,
    )

    latest_by_user: Dict[str, Dict[str, Any]] = {}

    for event in events:
        if (
            str(event.get("workspace_id"))
            != normalized_workspace_id
        ):
            continue

        if (
            str(event.get("scope_type"))
            != normalized_scope_type
        ):
            continue

        if (
            str(event.get("scope_id"))
            != normalized_scope_id
        ):
            continue

        identity_key = "|".join(
            [
                str(event.get("user_id") or ""),
                str(event.get("connection_id") or ""),
            ]
        )

        latest_by_user[identity_key] = event

    return list(latest_by_user.values())


def get_active_typing_users(
    *,
    workspace_id: str,
    scope_type: str,
    scope_id: str,
    exclude_user_id: str | None = None,
) -> List[Dict[str, Any]]:
    now = datetime.now(timezone.utc)

    latest = _latest_typing_events(
        workspace_id=workspace_id,
        scope_type=scope_type,
        scope_id=scope_id,
    )

    active = []

    for event in latest:
        if event.get("event_type") != "typing_started":
            continue

        if (
            exclude_user_id is not None
            and str(event.get("user_id"))
            == str(exclude_user_id)
        ):
            continue

        expires_at = _parse_datetime(
            event.get("expires_at")
        )

        if expires_at is None or expires_at <= now:
            continue

        active.append(event)

    return sorted(
        active,
        key=lambda item: str(
            item.get("created_at") or ""
        ),
        reverse=True,
    )


# ============================================================
# 22.3.3 TICKET TYPING INDICATORS
# ============================================================

def start_ticket_typing(
    *,
    user_id: str,
    workspace_id: str,
    ticket_id: str,
    display_name: str | None = None,
    connection_id: str | None = None,
    expires_in_seconds: int = 15,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return start_typing(
        user_id=user_id,
        workspace_id=workspace_id,
        scope_type="ticket",
        scope_id=ticket_id,
        display_name=display_name,
        connection_id=connection_id,
        expires_in_seconds=expires_in_seconds,
        metadata=metadata,
    )


def stop_ticket_typing(
    *,
    user_id: str,
    workspace_id: str,
    ticket_id: str,
    display_name: str | None = None,
    connection_id: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return stop_typing(
        user_id=user_id,
        workspace_id=workspace_id,
        scope_type="ticket",
        scope_id=ticket_id,
        display_name=display_name,
        connection_id=connection_id,
        metadata=metadata,
    )


def get_ticket_typing_indicators(
    *,
    workspace_id: str,
    ticket_id: str,
    exclude_user_id: str | None = None,
) -> List[Dict[str, Any]]:
    return get_active_typing_users(
        workspace_id=workspace_id,
        scope_type="ticket",
        scope_id=ticket_id,
        exclude_user_id=exclude_user_id,
    )


# ============================================================
# 22.3.4 COLLABORATION-ROOM TYPING INDICATORS
# ============================================================

def start_room_typing(
    *,
    user_id: str,
    workspace_id: str,
    room_id: str,
    display_name: str | None = None,
    connection_id: str | None = None,
    expires_in_seconds: int = 15,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return start_typing(
        user_id=user_id,
        workspace_id=workspace_id,
        scope_type="collaboration_room",
        scope_id=room_id,
        display_name=display_name,
        connection_id=connection_id,
        expires_in_seconds=expires_in_seconds,
        metadata=metadata,
    )


def stop_room_typing(
    *,
    user_id: str,
    workspace_id: str,
    room_id: str,
    display_name: str | None = None,
    connection_id: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return stop_typing(
        user_id=user_id,
        workspace_id=workspace_id,
        scope_type="collaboration_room",
        scope_id=room_id,
        display_name=display_name,
        connection_id=connection_id,
        metadata=metadata,
    )


def get_room_typing_indicators(
    *,
    workspace_id: str,
    room_id: str,
    exclude_user_id: str | None = None,
) -> List[Dict[str, Any]]:
    return get_active_typing_users(
        workspace_id=workspace_id,
        scope_type="collaboration_room",
        scope_id=room_id,
        exclude_user_id=exclude_user_id,
    )


# ============================================================
# 22.3.5 TYPING-EVENT EXPIRATION AND CLEANUP
# ============================================================

def expire_stale_typing_events(
    *,
    workspace_id: str | None = None,
) -> List[Dict[str, Any]]:
    now = datetime.now(timezone.utc)

    events = read_typing_events(
        limit=100000,
    )

    latest_by_identity: Dict[str, Dict[str, Any]] = {}

    for event in events:
        if (
            workspace_id is not None
            and str(event.get("workspace_id"))
            != str(workspace_id)
        ):
            continue

        identity_key = "|".join(
            [
                str(event.get("workspace_id") or ""),
                str(event.get("scope_type") or ""),
                str(event.get("scope_id") or ""),
                str(event.get("user_id") or ""),
                str(event.get("connection_id") or ""),
            ]
        )

        latest_by_identity[identity_key] = event

    expired_events = []

    for event in latest_by_identity.values():
        if event.get("event_type") != "typing_started":
            continue

        expires_at = _parse_datetime(
            event.get("expires_at")
        )

        if expires_at is None or expires_at > now:
            continue

        expired = _build_typing_event(
            user_id=str(event.get("user_id")),
            workspace_id=str(
                event.get("workspace_id")
            ),
            scope_type=str(
                event.get("scope_type")
            ),
            scope_id=str(
                event.get("scope_id")
            ),
            event_type="typing_expired",
            display_name=event.get("display_name"),
            connection_id=event.get(
                "connection_id"
            ),
            metadata={
                "expired_event_id": event.get(
                    "event_id"
                ),
                "original_expires_at": event.get(
                    "expires_at"
                ),
            },
        )

        expired_events.append(
            _write_typing_event(expired)
        )

    return expired_events


def build_typing_indicator_snapshot(
    *,
    workspace_id: str,
    scope_type: str,
    scope_id: str,
) -> Dict[str, Any]:
    active = get_active_typing_users(
        workspace_id=workspace_id,
        scope_type=scope_type,
        scope_id=scope_id,
    )

    return {
        "workspace_id": workspace_id,
        "scope_type": scope_type,
        "scope_id": scope_id,
        "active_typing_count": len(active),
        "active_typing_users": active,
        "generated_at": _utc_now(),
    }


def read_typing_indicator_audit(
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    return _read_jsonl(
        TYPING_AUDIT_PATH,
        limit,
    )
