
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data/tms")

INTERNAL_NOTES_PATH = DATA_DIR / "internal_collaboration_notes.jsonl"
INTERNAL_NOTES_AUDIT_PATH = DATA_DIR / "internal_collaboration_notes_audit.jsonl"


@dataclass(frozen=True)
class InternalCollaborationNote:
    note_id: str
    workspace_id: str
    ticket_id: str
    author_id: str
    content: str
    visibility: str = "internal"
    allowed_roles: List[str] = field(default_factory=list)
    allowed_user_ids: List[str] = field(default_factory=list)
    status: str = "active"
    version: int = 1
    parent_note_id: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    deleted_at: str | None = None
    restored_at: str | None = None


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for path in (
        INTERNAL_NOTES_PATH,
        INTERNAL_NOTES_AUDIT_PATH,
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
    note_id: str,
    workspace_id: str,
    ticket_id: str,
    actor_id: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    payload = {
        "event_type": event_type,
        "note_id": note_id,
        "workspace_id": workspace_id,
        "ticket_id": ticket_id,
        "actor_id": actor_id,
        "metadata": metadata or {},
        "created_at": _utc_now(),
    }

    _append_jsonl(
        INTERNAL_NOTES_AUDIT_PATH,
        payload,
    )

    return payload


def _write_note(
    note: InternalCollaborationNote,
) -> Dict[str, Any]:
    payload = asdict(note)

    _append_jsonl(
        INTERNAL_NOTES_PATH,
        payload,
    )

    return payload


def read_internal_note_events(
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    return _read_jsonl(
        INTERNAL_NOTES_PATH,
        limit,
    )


def _latest_notes_by_id(
    *,
    workspace_id: str | None = None,
    ticket_id: str | None = None,
) -> Dict[str, Dict[str, Any]]:
    events = read_internal_note_events(
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

        note_id = str(
            event.get("note_id") or ""
        )

        if note_id:
            latest[note_id] = event

    return latest


def get_internal_note(
    *,
    note_id: str,
    workspace_id: str,
) -> Dict[str, Any] | None:
    normalized_note_id = _validate_required_text(
        note_id,
        "note_id",
    )
    normalized_workspace_id = _validate_required_text(
        workspace_id,
        "workspace_id",
    )

    note = _latest_notes_by_id(
        workspace_id=normalized_workspace_id,
    ).get(normalized_note_id)

    return note


# ============================================================
# 22.4.1 INTERNAL NOTE MODEL
# ============================================================

def build_internal_note(
    *,
    workspace_id: str,
    ticket_id: str,
    author_id: str,
    content: str,
    visibility: str = "internal",
    allowed_roles: List[str] | None = None,
    allowed_user_ids: List[str] | None = None,
    parent_note_id: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> InternalCollaborationNote:
    normalized_workspace_id = _validate_required_text(
        workspace_id,
        "workspace_id",
    )
    normalized_ticket_id = _validate_required_text(
        ticket_id,
        "ticket_id",
    )
    normalized_author_id = _validate_required_text(
        author_id,
        "author_id",
    )
    normalized_content = _validate_required_text(
        content,
        "content",
    )
    normalized_visibility = _validate_required_text(
        visibility,
        "visibility",
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

    if (
        normalized_visibility == "restricted"
        and not allowed_roles
        and not allowed_user_ids
    ):
        raise ValueError(
            "restricted notes require allowed_roles "
            "or allowed_user_ids."
        )

    if (
        normalized_visibility == "private"
        and not allowed_user_ids
    ):
        raise ValueError(
            "private notes require allowed_user_ids."
        )

    return InternalCollaborationNote(
        note_id=_new_id("internal_note"),
        workspace_id=normalized_workspace_id,
        ticket_id=normalized_ticket_id,
        author_id=normalized_author_id,
        content=normalized_content,
        visibility=normalized_visibility,
        allowed_roles=list(allowed_roles or []),
        allowed_user_ids=list(
            allowed_user_ids or []
        ),
        parent_note_id=parent_note_id,
        metadata=dict(metadata or {}),
    )


# ============================================================
# 22.4.2 CREATE INTERNAL NOTES
# ============================================================

def create_internal_note(
    *,
    workspace_id: str,
    ticket_id: str,
    author_id: str,
    content: str,
    visibility: str = "internal",
    allowed_roles: List[str] | None = None,
    allowed_user_ids: List[str] | None = None,
    parent_note_id: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    note = build_internal_note(
        workspace_id=workspace_id,
        ticket_id=ticket_id,
        author_id=author_id,
        content=content,
        visibility=visibility,
        allowed_roles=allowed_roles,
        allowed_user_ids=allowed_user_ids,
        parent_note_id=parent_note_id,
        metadata=metadata,
    )

    payload = _write_note(note)

    _audit(
        event_type="internal_note_created",
        note_id=note.note_id,
        workspace_id=note.workspace_id,
        ticket_id=note.ticket_id,
        actor_id=author_id,
        metadata={
            "visibility": note.visibility,
            "version": note.version,
            "parent_note_id": parent_note_id,
        },
    )

    return payload


# ============================================================
# 22.4.3 EDIT INTERNAL NOTES
# ============================================================

def edit_internal_note(
    *,
    note_id: str,
    workspace_id: str,
    editor_id: str,
    content: str,
    visibility: str | None = None,
    allowed_roles: List[str] | None = None,
    allowed_user_ids: List[str] | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    existing = get_internal_note(
        note_id=note_id,
        workspace_id=workspace_id,
    )

    if existing is None:
        raise LookupError(
            f"Internal note not found: {note_id}"
        )

    if str(existing.get("status")) == "deleted":
        raise ValueError(
            "Deleted notes must be restored before editing."
        )

    normalized_content = _validate_required_text(
        content,
        "content",
    )

    next_visibility = (
        visibility
        if visibility is not None
        else str(existing.get("visibility") or "internal")
    )

    next_roles = (
        list(allowed_roles)
        if allowed_roles is not None
        else list(existing.get("allowed_roles") or [])
    )

    next_users = (
        list(allowed_user_ids)
        if allowed_user_ids is not None
        else list(existing.get("allowed_user_ids") or [])
    )

    if (
        next_visibility == "restricted"
        and not next_roles
        and not next_users
    ):
        raise ValueError(
            "restricted notes require allowed_roles "
            "or allowed_user_ids."
        )

    if (
        next_visibility == "private"
        and not next_users
    ):
        raise ValueError(
            "private notes require allowed_user_ids."
        )

    updated_note = InternalCollaborationNote(
        note_id=str(existing.get("note_id")),
        workspace_id=str(
            existing.get("workspace_id")
        ),
        ticket_id=str(existing.get("ticket_id")),
        author_id=str(existing.get("author_id")),
        content=normalized_content,
        visibility=next_visibility,
        allowed_roles=next_roles,
        allowed_user_ids=next_users,
        status="active",
        version=int(
            existing.get("version") or 1
        ) + 1,
        parent_note_id=existing.get(
            "parent_note_id"
        ),
        metadata={
            **dict(existing.get("metadata") or {}),
            **dict(metadata or {}),
            "last_editor_id": editor_id,
        },
        created_at=str(existing.get("created_at")),
        updated_at=_utc_now(),
        deleted_at=None,
        restored_at=existing.get("restored_at"),
    )

    payload = _write_note(updated_note)

    _audit(
        event_type="internal_note_edited",
        note_id=updated_note.note_id,
        workspace_id=updated_note.workspace_id,
        ticket_id=updated_note.ticket_id,
        actor_id=editor_id,
        metadata={
            "previous_version": existing.get(
                "version"
            ),
            "new_version": updated_note.version,
            "visibility": updated_note.visibility,
        },
    )

    return payload


# ============================================================
# 22.4.4 DELETE AND RESTORE INTERNAL NOTES
# ============================================================

def delete_internal_note(
    *,
    note_id: str,
    workspace_id: str,
    actor_id: str,
    reason: str = "deleted_by_staff",
) -> Dict[str, Any]:
    existing = get_internal_note(
        note_id=note_id,
        workspace_id=workspace_id,
    )

    if existing is None:
        raise LookupError(
            f"Internal note not found: {note_id}"
        )

    if str(existing.get("status")) == "deleted":
        return existing

    deleted_note = InternalCollaborationNote(
        note_id=str(existing.get("note_id")),
        workspace_id=str(
            existing.get("workspace_id")
        ),
        ticket_id=str(existing.get("ticket_id")),
        author_id=str(existing.get("author_id")),
        content=str(existing.get("content")),
        visibility=str(
            existing.get("visibility") or "internal"
        ),
        allowed_roles=list(
            existing.get("allowed_roles") or []
        ),
        allowed_user_ids=list(
            existing.get("allowed_user_ids") or []
        ),
        status="deleted",
        version=int(
            existing.get("version") or 1
        ) + 1,
        parent_note_id=existing.get(
            "parent_note_id"
        ),
        metadata={
            **dict(existing.get("metadata") or {}),
            "deleted_by": actor_id,
            "delete_reason": reason,
        },
        created_at=str(existing.get("created_at")),
        updated_at=_utc_now(),
        deleted_at=_utc_now(),
        restored_at=existing.get("restored_at"),
    )

    payload = _write_note(deleted_note)

    _audit(
        event_type="internal_note_deleted",
        note_id=deleted_note.note_id,
        workspace_id=deleted_note.workspace_id,
        ticket_id=deleted_note.ticket_id,
        actor_id=actor_id,
        metadata={
            "reason": reason,
            "version": deleted_note.version,
        },
    )

    return payload


def restore_internal_note(
    *,
    note_id: str,
    workspace_id: str,
    actor_id: str,
    reason: str = "restored_by_staff",
) -> Dict[str, Any]:
    existing = get_internal_note(
        note_id=note_id,
        workspace_id=workspace_id,
    )

    if existing is None:
        raise LookupError(
            f"Internal note not found: {note_id}"
        )

    if str(existing.get("status")) != "deleted":
        return existing

    restored_note = InternalCollaborationNote(
        note_id=str(existing.get("note_id")),
        workspace_id=str(
            existing.get("workspace_id")
        ),
        ticket_id=str(existing.get("ticket_id")),
        author_id=str(existing.get("author_id")),
        content=str(existing.get("content")),
        visibility=str(
            existing.get("visibility") or "internal"
        ),
        allowed_roles=list(
            existing.get("allowed_roles") or []
        ),
        allowed_user_ids=list(
            existing.get("allowed_user_ids") or []
        ),
        status="active",
        version=int(
            existing.get("version") or 1
        ) + 1,
        parent_note_id=existing.get(
            "parent_note_id"
        ),
        metadata={
            **dict(existing.get("metadata") or {}),
            "restored_by": actor_id,
            "restore_reason": reason,
        },
        created_at=str(existing.get("created_at")),
        updated_at=_utc_now(),
        deleted_at=None,
        restored_at=_utc_now(),
    )

    payload = _write_note(restored_note)

    _audit(
        event_type="internal_note_restored",
        note_id=restored_note.note_id,
        workspace_id=restored_note.workspace_id,
        ticket_id=restored_note.ticket_id,
        actor_id=actor_id,
        metadata={
            "reason": reason,
            "version": restored_note.version,
        },
    )

    return payload


# ============================================================
# 22.4.5 NOTE VISIBILITY AND AUDIT CONTROLS
# ============================================================

def can_view_internal_note(
    *,
    note: Dict[str, Any],
    user_id: str,
    user_roles: List[str] | None = None,
    workspace_id: str,
    include_deleted: bool = False,
) -> bool:
    if (
        str(note.get("workspace_id"))
        != str(workspace_id)
    ):
        return False

    if (
        not include_deleted
        and str(note.get("status")) == "deleted"
    ):
        return False

    visibility = str(
        note.get("visibility") or "internal"
    )

    if visibility == "internal":
        return True

    allowed_users = {
        str(value)
        for value in note.get(
            "allowed_user_ids",
            [],
        )
    }

    if str(user_id) in allowed_users:
        return True

    if str(note.get("author_id")) == str(user_id):
        return True

    if visibility == "private":
        return False

    allowed_roles = {
        str(value)
        for value in note.get(
            "allowed_roles",
            [],
        )
    }

    current_roles = {
        str(value)
        for value in (user_roles or [])
    }

    return bool(
        allowed_roles.intersection(
            current_roles
        )
    )


def list_ticket_internal_notes(
    *,
    workspace_id: str,
    ticket_id: str,
    user_id: str,
    user_roles: List[str] | None = None,
    include_deleted: bool = False,
) -> List[Dict[str, Any]]:
    latest = _latest_notes_by_id(
        workspace_id=workspace_id,
        ticket_id=ticket_id,
    )

    visible = [
        note
        for note in latest.values()
        if can_view_internal_note(
            note=note,
            user_id=user_id,
            user_roles=user_roles,
            workspace_id=workspace_id,
            include_deleted=include_deleted,
        )
    ]

    return sorted(
        visible,
        key=lambda item: str(
            item.get("updated_at")
            or item.get("created_at")
            or ""
        ),
    )


def get_internal_note_history(
    *,
    note_id: str,
    workspace_id: str,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    events = read_internal_note_events(
        limit=100000,
    )

    history = [
        event
        for event in events
        if str(event.get("note_id"))
        == str(note_id)
        and str(event.get("workspace_id"))
        == str(workspace_id)
    ]

    return history[-limit:]


def read_internal_notes_audit(
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    return _read_jsonl(
        INTERNAL_NOTES_AUDIT_PATH,
        limit,
    )


def build_internal_notes_snapshot(
    *,
    workspace_id: str,
    ticket_id: str,
) -> Dict[str, Any]:
    latest = list(
        _latest_notes_by_id(
            workspace_id=workspace_id,
            ticket_id=ticket_id,
        ).values()
    )

    active = [
        note
        for note in latest
        if str(note.get("status")) == "active"
    ]

    deleted = [
        note
        for note in latest
        if str(note.get("status")) == "deleted"
    ]

    restricted = [
        note
        for note in active
        if str(note.get("visibility"))
        in {"restricted", "private"}
    ]

    return {
        "workspace_id": workspace_id,
        "ticket_id": ticket_id,
        "total_note_count": len(latest),
        "active_note_count": len(active),
        "deleted_note_count": len(deleted),
        "restricted_note_count": len(
            restricted
        ),
        "latest_notes": latest,
        "generated_at": _utc_now(),
    }
