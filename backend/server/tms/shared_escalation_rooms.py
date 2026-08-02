
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data/tms")

ESCALATION_ROOMS_PATH = DATA_DIR / "shared_escalation_rooms.jsonl"
ESCALATION_ROOM_MEMBERS_PATH = DATA_DIR / "escalation_room_members.jsonl"
ESCALATION_ROOM_ACTIVITY_PATH = DATA_DIR / "escalation_room_activity.jsonl"
ESCALATION_ROOM_AUDIT_PATH = DATA_DIR / "shared_escalation_rooms_audit.jsonl"


@dataclass(frozen=True)
class EscalationRoom:
    room_id: str
    workspace_id: str
    ticket_id: str
    created_by: str
    title: str
    description: str = ""
    escalation_level: str = "level_1"
    status: str = "active"
    visibility: str = "internal"
    department: str | None = None
    incident_id: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    closed_at: str | None = None
    archived_at: str | None = None


@dataclass(frozen=True)
class EscalationRoomMember:
    membership_id: str
    room_id: str
    workspace_id: str
    user_id: str
    role: str = "member"
    status: str = "active"
    added_by: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    joined_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass(frozen=True)
class EscalationRoomActivity:
    activity_id: str
    room_id: str
    workspace_id: str
    activity_type: str
    actor_id: str
    message: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    sequence_number: int = 1
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for path in (
        ESCALATION_ROOMS_PATH,
        ESCALATION_ROOM_MEMBERS_PATH,
        ESCALATION_ROOM_ACTIVITY_PATH,
        ESCALATION_ROOM_AUDIT_PATH,
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


def _audit(
    *,
    event_type: str,
    room_id: str,
    workspace_id: str,
    actor_id: str | None = None,
    ticket_id: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    payload = {
        "event_type": event_type,
        "room_id": room_id,
        "workspace_id": workspace_id,
        "ticket_id": ticket_id,
        "actor_id": actor_id,
        "metadata": metadata or {},
        "created_at": _utc_now(),
    }

    _append_jsonl(
        ESCALATION_ROOM_AUDIT_PATH,
        payload,
    )

    return payload


def read_escalation_room_events(
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    return _read_jsonl(
        ESCALATION_ROOMS_PATH,
        limit,
    )


def _latest_rooms_by_id(
    *,
    workspace_id: str | None = None,
    ticket_id: str | None = None,
) -> Dict[str, Dict[str, Any]]:
    events = read_escalation_room_events(
        limit=100000,
    )

    latest: Dict[str, Dict[str, Any]] = {}

    for event in events:
        if (
            workspace_id is not None
            and str(event.get("workspace_id"))
            != str(workspace_id)
        ):
            continue

        if (
            ticket_id is not None
            and str(event.get("ticket_id"))
            != str(ticket_id)
        ):
            continue

        room_id = str(event.get("room_id") or "")

        if room_id:
            latest[room_id] = event

    return latest


def get_escalation_room(
    *,
    room_id: str,
    workspace_id: str,
) -> Dict[str, Any] | None:
    normalized_room_id = _validate_required_text(
        room_id,
        "room_id",
    )
    normalized_workspace_id = _validate_required_text(
        workspace_id,
        "workspace_id",
    )

    return _latest_rooms_by_id(
        workspace_id=normalized_workspace_id,
    ).get(normalized_room_id)


# ============================================================
# 22.5.1 ESCALATION-ROOM MODEL
# ============================================================

def build_escalation_room(
    *,
    workspace_id: str,
    ticket_id: str,
    created_by: str,
    title: str,
    description: str = "",
    escalation_level: str = "level_1",
    visibility: str = "internal",
    department: str | None = None,
    incident_id: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> EscalationRoom:
    normalized_workspace_id = _validate_required_text(
        workspace_id,
        "workspace_id",
    )
    normalized_ticket_id = _validate_required_text(
        ticket_id,
        "ticket_id",
    )
    normalized_created_by = _validate_required_text(
        created_by,
        "created_by",
    )
    normalized_title = _validate_required_text(
        title,
        "title",
    )
    normalized_level = _validate_required_text(
        escalation_level,
        "escalation_level",
    )
    normalized_visibility = _validate_required_text(
        visibility,
        "visibility",
    )

    allowed_levels = {
        "level_1",
        "level_2",
        "level_3",
        "critical",
        "vip",
    }

    if normalized_level not in allowed_levels:
        raise ValueError(
            "Unsupported escalation level."
        )

    allowed_visibility = {
        "internal",
        "restricted",
        "private",
    }

    if normalized_visibility not in allowed_visibility:
        raise ValueError(
            "visibility must be internal, restricted, or private."
        )

    return EscalationRoom(
        room_id=_new_id("escalation_room"),
        workspace_id=normalized_workspace_id,
        ticket_id=normalized_ticket_id,
        created_by=normalized_created_by,
        title=normalized_title,
        description=str(description or "").strip(),
        escalation_level=normalized_level,
        visibility=normalized_visibility,
        department=department,
        incident_id=incident_id,
        metadata=dict(metadata or {}),
    )


# ============================================================
# 22.5.2 CREATE TICKET-LINKED ROOMS
# ============================================================

def create_ticket_escalation_room(
    *,
    workspace_id: str,
    ticket_id: str,
    created_by: str,
    title: str,
    description: str = "",
    escalation_level: str = "level_1",
    visibility: str = "internal",
    department: str | None = None,
    incident_id: str | None = None,
    initial_member_ids: List[str] | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    room = build_escalation_room(
        workspace_id=workspace_id,
        ticket_id=ticket_id,
        created_by=created_by,
        title=title,
        description=description,
        escalation_level=escalation_level,
        visibility=visibility,
        department=department,
        incident_id=incident_id,
        metadata=metadata,
    )

    payload = asdict(room)

    _append_jsonl(
        ESCALATION_ROOMS_PATH,
        payload,
    )

    add_room_member(
        room_id=room.room_id,
        workspace_id=room.workspace_id,
        user_id=room.created_by,
        role="owner",
        added_by=room.created_by,
    )

    for member_id in initial_member_ids or []:
        if str(member_id) == str(room.created_by):
            continue

        add_room_member(
            room_id=room.room_id,
            workspace_id=room.workspace_id,
            user_id=member_id,
            role="member",
            added_by=room.created_by,
        )

    publish_room_activity(
        room_id=room.room_id,
        workspace_id=room.workspace_id,
        activity_type="room_created",
        actor_id=room.created_by,
        message=f"Escalation room created for ticket {room.ticket_id}.",
        payload={
            "ticket_id": room.ticket_id,
            "escalation_level": room.escalation_level,
            "incident_id": room.incident_id,
        },
    )

    _audit(
        event_type="escalation_room_created",
        room_id=room.room_id,
        workspace_id=room.workspace_id,
        actor_id=room.created_by,
        ticket_id=room.ticket_id,
        metadata={
            "title": room.title,
            "escalation_level": room.escalation_level,
            "visibility": room.visibility,
            "department": room.department,
            "incident_id": room.incident_id,
        },
    )

    return payload


def list_ticket_escalation_rooms(
    *,
    workspace_id: str,
    ticket_id: str,
    include_closed: bool = False,
    include_archived: bool = False,
) -> List[Dict[str, Any]]:
    rooms = list(
        _latest_rooms_by_id(
            workspace_id=workspace_id,
            ticket_id=ticket_id,
        ).values()
    )

    results = []

    for room in rooms:
        status = str(room.get("status") or "active")

        if status == "closed" and not include_closed:
            continue

        if status == "archived" and not include_archived:
            continue

        results.append(room)

    return sorted(
        results,
        key=lambda item: str(
            item.get("updated_at")
            or item.get("created_at")
            or ""
        ),
        reverse=True,
    )


# ============================================================
# 22.5.3 ROOM MEMBERSHIP MANAGEMENT
# ============================================================

def read_room_member_events(
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    return _read_jsonl(
        ESCALATION_ROOM_MEMBERS_PATH,
        limit,
    )


def _latest_room_members(
    *,
    room_id: str,
    workspace_id: str,
) -> Dict[str, Dict[str, Any]]:
    events = read_room_member_events(
        limit=100000,
    )

    latest: Dict[str, Dict[str, Any]] = {}

    for event in events:
        if str(event.get("room_id")) != str(room_id):
            continue

        if (
            str(event.get("workspace_id"))
            != str(workspace_id)
        ):
            continue

        user_id = str(event.get("user_id") or "")

        if user_id:
            latest[user_id] = event

    return latest


def add_room_member(
    *,
    room_id: str,
    workspace_id: str,
    user_id: str,
    role: str = "member",
    added_by: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    room = get_escalation_room(
        room_id=room_id,
        workspace_id=workspace_id,
    )

    if room is None:
        raise LookupError(
            f"Escalation room not found: {room_id}"
        )

    if str(room.get("status")) in {"closed", "archived"}:
        raise ValueError(
            "Members cannot be added to a closed or archived room."
        )

    normalized_user_id = _validate_required_text(
        user_id,
        "user_id",
    )
    normalized_role = _validate_required_text(
        role,
        "role",
    )

    allowed_roles = {
        "owner",
        "commander",
        "manager",
        "specialist",
        "member",
        "observer",
    }

    if normalized_role not in allowed_roles:
        raise ValueError(
            "Unsupported escalation room role."
        )

    member = EscalationRoomMember(
        membership_id=_new_id("room_membership"),
        room_id=str(room_id),
        workspace_id=str(workspace_id),
        user_id=normalized_user_id,
        role=normalized_role,
        status="active",
        added_by=added_by,
        metadata=dict(metadata or {}),
    )

    payload = asdict(member)

    _append_jsonl(
        ESCALATION_ROOM_MEMBERS_PATH,
        payload,
    )

    _audit(
        event_type="escalation_room_member_added",
        room_id=str(room_id),
        workspace_id=str(workspace_id),
        actor_id=added_by,
        ticket_id=str(room.get("ticket_id")),
        metadata={
            "user_id": normalized_user_id,
            "role": normalized_role,
            "membership_id": member.membership_id,
        },
    )

    return payload


def remove_room_member(
    *,
    room_id: str,
    workspace_id: str,
    user_id: str,
    removed_by: str,
    reason: str = "removed_by_staff",
) -> Dict[str, Any]:
    members = _latest_room_members(
        room_id=room_id,
        workspace_id=workspace_id,
    )

    existing = members.get(str(user_id))

    if existing is None:
        raise LookupError(
            f"Room member not found: {user_id}"
        )

    if str(existing.get("status")) == "inactive":
        return existing

    payload = {
        **existing,
        "membership_id": _new_id("room_membership_update"),
        "status": "inactive",
        "removed_by": removed_by,
        "remove_reason": reason,
        "updated_at": _utc_now(),
    }

    _append_jsonl(
        ESCALATION_ROOM_MEMBERS_PATH,
        payload,
    )

    room = get_escalation_room(
        room_id=room_id,
        workspace_id=workspace_id,
    )

    _audit(
        event_type="escalation_room_member_removed",
        room_id=str(room_id),
        workspace_id=str(workspace_id),
        actor_id=removed_by,
        ticket_id=(
            str(room.get("ticket_id"))
            if room
            else None
        ),
        metadata={
            "user_id": user_id,
            "reason": reason,
        },
    )

    return payload


def update_room_member_role(
    *,
    room_id: str,
    workspace_id: str,
    user_id: str,
    new_role: str,
    updated_by: str,
) -> Dict[str, Any]:
    members = _latest_room_members(
        room_id=room_id,
        workspace_id=workspace_id,
    )

    existing = members.get(str(user_id))

    if existing is None:
        raise LookupError(
            f"Room member not found: {user_id}"
        )

    if str(existing.get("status")) != "active":
        raise ValueError(
            "Inactive room members cannot have their role updated."
        )

    normalized_role = _validate_required_text(
        new_role,
        "new_role",
    )

    allowed_roles = {
        "owner",
        "commander",
        "manager",
        "specialist",
        "member",
        "observer",
    }

    if normalized_role not in allowed_roles:
        raise ValueError(
            "Unsupported escalation room role."
        )

    payload = {
        **existing,
        "membership_id": _new_id("room_membership_update"),
        "role": normalized_role,
        "updated_by": updated_by,
        "updated_at": _utc_now(),
    }

    _append_jsonl(
        ESCALATION_ROOM_MEMBERS_PATH,
        payload,
    )

    room = get_escalation_room(
        room_id=room_id,
        workspace_id=workspace_id,
    )

    _audit(
        event_type="escalation_room_member_role_updated",
        room_id=str(room_id),
        workspace_id=str(workspace_id),
        actor_id=updated_by,
        ticket_id=(
            str(room.get("ticket_id"))
            if room
            else None
        ),
        metadata={
            "user_id": user_id,
            "previous_role": existing.get("role"),
            "new_role": normalized_role,
        },
    )

    return payload


def list_active_room_members(
    *,
    room_id: str,
    workspace_id: str,
) -> List[Dict[str, Any]]:
    members = _latest_room_members(
        room_id=room_id,
        workspace_id=workspace_id,
    )

    active = [
        member
        for member in members.values()
        if str(member.get("status")) == "active"
    ]

    return sorted(
        active,
        key=lambda item: (
            str(item.get("role") or ""),
            str(item.get("joined_at") or ""),
        ),
    )


def can_access_escalation_room(
    *,
    room_id: str,
    workspace_id: str,
    user_id: str,
) -> bool:
    room = get_escalation_room(
        room_id=room_id,
        workspace_id=workspace_id,
    )

    if room is None:
        return False

    if (
        str(room.get("workspace_id"))
        != str(workspace_id)
    ):
        return False

    members = _latest_room_members(
        room_id=room_id,
        workspace_id=workspace_id,
    )

    membership = members.get(str(user_id))

    return bool(
        membership
        and str(membership.get("status")) == "active"
    )


# ============================================================
# 22.5.4 LIVE ROOM ACTIVITY STREAM
# ============================================================

def read_room_activity_events(
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    return _read_jsonl(
        ESCALATION_ROOM_ACTIVITY_PATH,
        limit,
    )


def _next_room_sequence(
    *,
    room_id: str,
    workspace_id: str,
) -> int:
    events = read_room_activity_events(
        limit=100000,
    )

    scoped = [
        event
        for event in events
        if str(event.get("room_id")) == str(room_id)
        and str(event.get("workspace_id"))
        == str(workspace_id)
    ]

    if not scoped:
        return 1

    return max(
        int(event.get("sequence_number") or 0)
        for event in scoped
    ) + 1


def publish_room_activity(
    *,
    room_id: str,
    workspace_id: str,
    activity_type: str,
    actor_id: str,
    message: str = "",
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    room = get_escalation_room(
        room_id=room_id,
        workspace_id=workspace_id,
    )

    if room is None:
        raise LookupError(
            f"Escalation room not found: {room_id}"
        )

    normalized_activity_type = _validate_required_text(
        activity_type,
        "activity_type",
    )
    normalized_actor_id = _validate_required_text(
        actor_id,
        "actor_id",
    )

    activity = EscalationRoomActivity(
        activity_id=_new_id("room_activity"),
        room_id=str(room_id),
        workspace_id=str(workspace_id),
        activity_type=normalized_activity_type,
        actor_id=normalized_actor_id,
        message=str(message or "").strip(),
        payload=dict(payload or {}),
        sequence_number=_next_room_sequence(
            room_id=room_id,
            workspace_id=workspace_id,
        ),
    )

    activity_payload = asdict(activity)

    _append_jsonl(
        ESCALATION_ROOM_ACTIVITY_PATH,
        activity_payload,
    )

    _audit(
        event_type="escalation_room_activity_published",
        room_id=str(room_id),
        workspace_id=str(workspace_id),
        actor_id=normalized_actor_id,
        ticket_id=str(room.get("ticket_id")),
        metadata={
            "activity_id": activity.activity_id,
            "activity_type": normalized_activity_type,
            "sequence_number": activity.sequence_number,
        },
    )

    return activity_payload


def publish_room_message(
    *,
    room_id: str,
    workspace_id: str,
    actor_id: str,
    message: str,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    normalized_message = _validate_required_text(
        message,
        "message",
    )

    return publish_room_activity(
        room_id=room_id,
        workspace_id=workspace_id,
        activity_type="message_posted",
        actor_id=actor_id,
        message=normalized_message,
        payload=metadata,
    )


def get_room_activity_stream(
    *,
    room_id: str,
    workspace_id: str,
    limit: int = 500,
    after_sequence: int | None = None,
) -> List[Dict[str, Any]]:
    events = read_room_activity_events(
        limit=100000,
    )

    scoped = [
        event
        for event in events
        if str(event.get("room_id")) == str(room_id)
        and str(event.get("workspace_id"))
        == str(workspace_id)
    ]

    if after_sequence is not None:
        scoped = [
            event
            for event in scoped
            if int(event.get("sequence_number") or 0)
            > int(after_sequence)
        ]

    return scoped[-limit:]


# ============================================================
# 22.5.5 ESCALATION-ROOM CLOSURE AND ARCHIVE
# ============================================================

def close_escalation_room(
    *,
    room_id: str,
    workspace_id: str,
    actor_id: str,
    resolution_summary: str,
) -> Dict[str, Any]:
    existing = get_escalation_room(
        room_id=room_id,
        workspace_id=workspace_id,
    )

    if existing is None:
        raise LookupError(
            f"Escalation room not found: {room_id}"
        )

    if str(existing.get("status")) == "archived":
        raise ValueError(
            "Archived rooms cannot be closed."
        )

    if str(existing.get("status")) == "closed":
        return existing

    normalized_summary = _validate_required_text(
        resolution_summary,
        "resolution_summary",
    )

    now = _utc_now()

    updated = EscalationRoom(
        room_id=str(existing.get("room_id")),
        workspace_id=str(
            existing.get("workspace_id")
        ),
        ticket_id=str(existing.get("ticket_id")),
        created_by=str(existing.get("created_by")),
        title=str(existing.get("title")),
        description=str(
            existing.get("description") or ""
        ),
        escalation_level=str(
            existing.get("escalation_level")
            or "level_1"
        ),
        status="closed",
        visibility=str(
            existing.get("visibility")
            or "internal"
        ),
        department=existing.get("department"),
        incident_id=existing.get("incident_id"),
        metadata={
            **dict(existing.get("metadata") or {}),
            "closed_by": actor_id,
            "resolution_summary": normalized_summary,
        },
        created_at=str(existing.get("created_at")),
        updated_at=now,
        closed_at=now,
        archived_at=existing.get("archived_at"),
    )

    payload = asdict(updated)

    _append_jsonl(
        ESCALATION_ROOMS_PATH,
        payload,
    )

    publish_room_activity(
        room_id=room_id,
        workspace_id=workspace_id,
        activity_type="room_closed",
        actor_id=actor_id,
        message=normalized_summary,
        payload={
            "resolution_summary": normalized_summary,
        },
    )

    _audit(
        event_type="escalation_room_closed",
        room_id=room_id,
        workspace_id=workspace_id,
        actor_id=actor_id,
        ticket_id=updated.ticket_id,
        metadata={
            "resolution_summary": normalized_summary,
        },
    )

    return payload


def archive_escalation_room(
    *,
    room_id: str,
    workspace_id: str,
    actor_id: str,
    reason: str = "room_archived",
) -> Dict[str, Any]:
    existing = get_escalation_room(
        room_id=room_id,
        workspace_id=workspace_id,
    )

    if existing is None:
        raise LookupError(
            f"Escalation room not found: {room_id}"
        )

    if str(existing.get("status")) == "archived":
        return existing

    if str(existing.get("status")) != "closed":
        raise ValueError(
            "Escalation rooms must be closed before archival."
        )

    now = _utc_now()

    archived = EscalationRoom(
        room_id=str(existing.get("room_id")),
        workspace_id=str(
            existing.get("workspace_id")
        ),
        ticket_id=str(existing.get("ticket_id")),
        created_by=str(existing.get("created_by")),
        title=str(existing.get("title")),
        description=str(
            existing.get("description") or ""
        ),
        escalation_level=str(
            existing.get("escalation_level")
            or "level_1"
        ),
        status="archived",
        visibility=str(
            existing.get("visibility")
            or "internal"
        ),
        department=existing.get("department"),
        incident_id=existing.get("incident_id"),
        metadata={
            **dict(existing.get("metadata") or {}),
            "archived_by": actor_id,
            "archive_reason": reason,
        },
        created_at=str(existing.get("created_at")),
        updated_at=now,
        closed_at=existing.get("closed_at"),
        archived_at=now,
    )

    payload = asdict(archived)

    _append_jsonl(
        ESCALATION_ROOMS_PATH,
        payload,
    )

    publish_room_activity(
        room_id=room_id,
        workspace_id=workspace_id,
        activity_type="room_archived",
        actor_id=actor_id,
        message=reason,
        payload={
            "archive_reason": reason,
        },
    )

    _audit(
        event_type="escalation_room_archived",
        room_id=room_id,
        workspace_id=workspace_id,
        actor_id=actor_id,
        ticket_id=archived.ticket_id,
        metadata={
            "reason": reason,
        },
    )

    return payload


def get_escalation_room_history(
    *,
    room_id: str,
    workspace_id: str,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    events = read_escalation_room_events(
        limit=100000,
    )

    history = [
        event
        for event in events
        if str(event.get("room_id")) == str(room_id)
        and str(event.get("workspace_id"))
        == str(workspace_id)
    ]

    return history[-limit:]


def read_shared_escalation_room_audit(
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    return _read_jsonl(
        ESCALATION_ROOM_AUDIT_PATH,
        limit,
    )


def build_escalation_room_snapshot(
    *,
    room_id: str,
    workspace_id: str,
) -> Dict[str, Any]:
    room = get_escalation_room(
        room_id=room_id,
        workspace_id=workspace_id,
    )

    if room is None:
        raise LookupError(
            f"Escalation room not found: {room_id}"
        )

    members = list_active_room_members(
        room_id=room_id,
        workspace_id=workspace_id,
    )

    activity = get_room_activity_stream(
        room_id=room_id,
        workspace_id=workspace_id,
        limit=500,
    )

    return {
        "room": room,
        "active_member_count": len(members),
        "active_members": members,
        "activity_count": len(activity),
        "activity": activity,
        "generated_at": _utc_now(),
    }
