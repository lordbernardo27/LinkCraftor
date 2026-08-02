
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data/tms")
LIVE_PRESENCE_PATH = DATA_DIR / "live_presence.jsonl"
LIVE_PRESENCE_AUDIT_PATH = DATA_DIR / "live_presence_audit.jsonl"


@dataclass(frozen=True)
class StaffPresence:
    staff_id: str
    workspace_id: str | None = None
    status: str = "online"
    active_ticket_id: str | None = None
    active_channel_id: str | None = None
    device_id: str | None = None
    connection_id: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_seen_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for path in (
        LIVE_PRESENCE_PATH,
        LIVE_PRESENCE_AUDIT_PATH,
    ):
        if not path.exists():
            path.write_text("", encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    _ensure_store()

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _read_jsonl(path: Path, limit: int = 1000) -> List[Dict[str, Any]]:
    _ensure_store()

    lines = path.read_text(encoding="utf-8").splitlines()

    return [
        json.loads(line)
        for line in lines[-limit:]
        if line.strip()
    ]


def _audit(
    *,
    event_type: str,
    staff_id: str,
    workspace_id: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    payload = {
        "event_type": event_type,
        "staff_id": staff_id,
        "workspace_id": workspace_id,
        "metadata": metadata or {},
        "created_at": _utc_now(),
    }

    _append_jsonl(LIVE_PRESENCE_AUDIT_PATH, payload)
    return payload


def _write_presence(presence: StaffPresence) -> Dict[str, Any]:
    payload = asdict(presence)
    _append_jsonl(LIVE_PRESENCE_PATH, payload)
    return payload


# ============================================================
# 22.1.1 STAFF ONLINE TRACKING
# ============================================================

def mark_staff_online(
    *,
    staff_id: str,
    workspace_id: str | None = None,
    active_ticket_id: str | None = None,
    active_channel_id: str | None = None,
    device_id: str | None = None,
    connection_id: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    presence = StaffPresence(
        staff_id=staff_id,
        workspace_id=workspace_id,
        status="online",
        active_ticket_id=active_ticket_id,
        active_channel_id=active_channel_id,
        device_id=device_id,
        connection_id=connection_id,
        metadata=metadata or {},
    )

    payload = _write_presence(presence)

    _audit(
        event_type="staff_marked_online",
        staff_id=staff_id,
        workspace_id=workspace_id,
        metadata={
            "active_ticket_id": active_ticket_id,
            "active_channel_id": active_channel_id,
            "device_id": device_id,
            "connection_id": connection_id,
        },
    )

    return payload


# ============================================================
# 22.1.2 STAFF OFFLINE TRACKING
# ============================================================

def mark_staff_offline(
    *,
    staff_id: str,
    workspace_id: str | None = None,
    device_id: str | None = None,
    connection_id: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    presence = StaffPresence(
        staff_id=staff_id,
        workspace_id=workspace_id,
        status="offline",
        device_id=device_id,
        connection_id=connection_id,
        metadata=metadata or {},
    )

    payload = _write_presence(presence)

    _audit(
        event_type="staff_marked_offline",
        staff_id=staff_id,
        workspace_id=workspace_id,
        metadata={
            "device_id": device_id,
            "connection_id": connection_id,
        },
    )

    return payload


# ============================================================
# 22.1.3 PRESENCE HEARTBEAT
# ============================================================

def record_presence_heartbeat(
    *,
    staff_id: str,
    workspace_id: str | None = None,
    active_ticket_id: str | None = None,
    active_channel_id: str | None = None,
    device_id: str | None = None,
    connection_id: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    now = _utc_now()

    presence = StaffPresence(
        staff_id=staff_id,
        workspace_id=workspace_id,
        status="online",
        active_ticket_id=active_ticket_id,
        active_channel_id=active_channel_id,
        device_id=device_id,
        connection_id=connection_id,
        metadata=metadata or {},
        last_seen_at=now,
        updated_at=now,
    )

    payload = _write_presence(presence)

    _audit(
        event_type="presence_heartbeat_recorded",
        staff_id=staff_id,
        workspace_id=workspace_id,
        metadata={
            "active_ticket_id": active_ticket_id,
            "active_channel_id": active_channel_id,
            "device_id": device_id,
            "connection_id": connection_id,
        },
    )

    return payload


# ============================================================
# 22.1.4 ACTIVE WORKSPACE PRESENCE
# ============================================================

def read_presence_events(limit: int = 1000) -> List[Dict[str, Any]]:
    return _read_jsonl(LIVE_PRESENCE_PATH, limit)


def get_latest_presence_by_staff(
    *,
    staff_id: str,
    workspace_id: str | None = None,
) -> Dict[str, Any] | None:
    events = read_presence_events(limit=100000)

    for event in reversed(events):
        if str(event.get("staff_id")) != str(staff_id):
            continue

        if (
            workspace_id is not None
            and str(event.get("workspace_id")) != str(workspace_id)
        ):
            continue

        return event

    return None


def get_active_workspace_presence(
    *,
    workspace_id: str,
    include_offline: bool = False,
) -> List[Dict[str, Any]]:
    events = read_presence_events(limit=100000)
    latest_by_staff: Dict[str, Dict[str, Any]] = {}

    for event in events:
        if str(event.get("workspace_id")) != str(workspace_id):
            continue

        staff_id = str(event.get("staff_id") or "")
        if staff_id:
            latest_by_staff[staff_id] = event

    results = []

    for event in latest_by_staff.values():
        if not include_offline and str(event.get("status")) == "offline":
            continue

        results.append(event)

    return sorted(
        results,
        key=lambda item: str(
            item.get("last_seen_at")
            or item.get("updated_at")
            or ""
        ),
        reverse=True,
    )


def get_active_ticket_presence(
    *,
    ticket_id: str,
    workspace_id: str | None = None,
) -> List[Dict[str, Any]]:
    events = read_presence_events(limit=100000)
    latest_by_staff: Dict[str, Dict[str, Any]] = {}

    for event in events:
        if str(event.get("active_ticket_id")) != str(ticket_id):
            continue

        if (
            workspace_id is not None
            and str(event.get("workspace_id")) != str(workspace_id)
        ):
            continue

        staff_id = str(event.get("staff_id") or "")
        if staff_id:
            latest_by_staff[staff_id] = event

    return [
        event
        for event in latest_by_staff.values()
        if str(event.get("status")) == "online"
    ]


# ============================================================
# 22.1.5 PRESENCE AUDIT LOG
# ============================================================

def read_live_presence_audit(limit: int = 1000) -> List[Dict[str, Any]]:
    return _read_jsonl(LIVE_PRESENCE_AUDIT_PATH, limit)


def build_presence_snapshot(
    *,
    workspace_id: str,
) -> Dict[str, Any]:
    active = get_active_workspace_presence(
        workspace_id=workspace_id,
        include_offline=False,
    )

    all_presence = get_active_workspace_presence(
        workspace_id=workspace_id,
        include_offline=True,
    )

    return {
        "workspace_id": workspace_id,
        "online_staff_count": len(active),
        "tracked_staff_count": len(all_presence),
        "online_staff": active,
        "all_staff_presence": all_presence,
        "generated_at": _utc_now(),
    }
