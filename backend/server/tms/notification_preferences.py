
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, time, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data/tms")

USER_NOTIFICATION_PREFERENCES_PATH = DATA_DIR / "user_notification_preferences.jsonl"
WORKSPACE_NOTIFICATION_PREFERENCES_PATH = DATA_DIR / "workspace_notification_preferences.jsonl"
NOTIFICATION_PREFERENCES_AUDIT_PATH = DATA_DIR / "notification_preferences_audit.jsonl"


SUPPORTED_CHANNELS = {
    "in_app": {
        "label": "In-App",
        "enabled_by_default": True,
    },
    "email": {
        "label": "Email",
        "enabled_by_default": True,
    },
    "sms": {
        "label": "SMS",
        "enabled_by_default": False,
    },
}


DEFAULT_NOTIFICATION_TYPE_PREFERENCES = {
    "ticket_created": {
        "in_app": True,
        "email": True,
        "sms": False,
    },
    "ticket_updated": {
        "in_app": True,
        "email": False,
        "sms": False,
    },
    "ticket_assigned": {
        "in_app": True,
        "email": True,
        "sms": False,
    },
    "ticket_escalated": {
        "in_app": True,
        "email": True,
        "sms": False,
    },
    "sla_warning": {
        "in_app": True,
        "email": True,
        "sms": False,
    },
    "sla_breached": {
        "in_app": True,
        "email": True,
        "sms": False,
    },
    "customer_reply": {
        "in_app": True,
        "email": True,
        "sms": False,
    },
    "staff_mention": {
        "in_app": True,
        "email": True,
        "sms": False,
    },
    "system_alert": {
        "in_app": True,
        "email": True,
        "sms": False,
    },
}


@dataclass(frozen=True)
class QuietHours:
    enabled: bool = False
    start_time: str = "22:00"
    end_time: str = "07:00"
    timezone_name: str = "UTC"


@dataclass(frozen=True)
class NotificationPreference:
    owner_id: str
    owner_type: str
    workspace_id: str | None = None
    channel_preferences: Dict[str, bool] = field(default_factory=dict)
    type_preferences: Dict[str, Dict[str, bool]] = field(default_factory=dict)
    quiet_hours: Dict[str, Any] = field(default_factory=lambda: asdict(QuietHours()))
    inherit_workspace_defaults: bool = True
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class NotificationPreferenceAuditEvent:
    event_type: str
    owner_id: str | None = None
    owner_type: str | None = None
    workspace_id: str | None = None
    status: str = "recorded"
    message: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _ensure_preferences_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for path in (
        USER_NOTIFICATION_PREFERENCES_PATH,
        WORKSPACE_NOTIFICATION_PREFERENCES_PATH,
        NOTIFICATION_PREFERENCES_AUDIT_PATH,
    ):
        if not path.exists():
            path.write_text("", encoding="utf-8")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    _ensure_preferences_store()

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _read_jsonl(path: Path, limit: int = 1000) -> List[Dict[str, Any]]:
    _ensure_preferences_store()

    lines = path.read_text(encoding="utf-8").splitlines()
    records: List[Dict[str, Any]] = []

    for line in lines[-limit:]:
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            records.append(
                {
                    "parse_error": True,
                    "raw_line": line,
                    "source_path": str(path),
                }
            )

    return records


def log_notification_preferences_audit(
    event: NotificationPreferenceAuditEvent,
) -> Dict[str, Any]:
    payload = asdict(event)
    _append_jsonl(NOTIFICATION_PREFERENCES_AUDIT_PATH, payload)
    return payload


def default_channel_preferences() -> Dict[str, bool]:
    return {
        channel: bool(config.get("enabled_by_default"))
        for channel, config in SUPPORTED_CHANNELS.items()
    }


def default_type_preferences() -> Dict[str, Dict[str, bool]]:
    return {
        notification_type: dict(channels)
        for notification_type, channels in DEFAULT_NOTIFICATION_TYPE_PREFERENCES.items()
    }


def normalize_channel_preferences(
    channel_preferences: Dict[str, bool] | None = None,
) -> Dict[str, bool]:
    result = default_channel_preferences()

    for channel, enabled in (channel_preferences or {}).items():
        if channel in SUPPORTED_CHANNELS:
            result[channel] = bool(enabled)

    return result


def normalize_type_preferences(
    type_preferences: Dict[str, Dict[str, bool]] | None = None,
) -> Dict[str, Dict[str, bool]]:
    result = default_type_preferences()

    for notification_type, channel_map in (type_preferences or {}).items():
        if notification_type not in result:
            result[notification_type] = default_channel_preferences()

        for channel, enabled in channel_map.items():
            if channel in SUPPORTED_CHANNELS:
                result[notification_type][channel] = bool(enabled)

    return result


def build_notification_preference(
    *,
    owner_id: str,
    owner_type: str,
    workspace_id: str | None = None,
    channel_preferences: Dict[str, bool] | None = None,
    type_preferences: Dict[str, Dict[str, bool]] | None = None,
    quiet_hours: Dict[str, Any] | None = None,
    inherit_workspace_defaults: bool = True,
) -> Dict[str, Any]:
    preference = NotificationPreference(
        owner_id=owner_id,
        owner_type=owner_type,
        workspace_id=workspace_id,
        channel_preferences=normalize_channel_preferences(channel_preferences),
        type_preferences=normalize_type_preferences(type_preferences),
        quiet_hours={
            **asdict(QuietHours()),
            **(quiet_hours or {}),
        },
        inherit_workspace_defaults=inherit_workspace_defaults,
    )

    return asdict(preference)


def save_user_notification_preferences(
    *,
    user_id: str,
    workspace_id: str | None = None,
    channel_preferences: Dict[str, bool] | None = None,
    type_preferences: Dict[str, Dict[str, bool]] | None = None,
    quiet_hours: Dict[str, Any] | None = None,
    inherit_workspace_defaults: bool = True,
) -> Dict[str, Any]:
    preference = build_notification_preference(
        owner_id=user_id,
        owner_type="user",
        workspace_id=workspace_id,
        channel_preferences=channel_preferences,
        type_preferences=type_preferences,
        quiet_hours=quiet_hours,
        inherit_workspace_defaults=inherit_workspace_defaults,
    )

    _append_jsonl(USER_NOTIFICATION_PREFERENCES_PATH, preference)

    log_notification_preferences_audit(
        NotificationPreferenceAuditEvent(
            event_type="user_notification_preferences_saved",
            owner_id=user_id,
            owner_type="user",
            workspace_id=workspace_id,
            message="User notification preferences saved.",
            metadata={
                "inherit_workspace_defaults": inherit_workspace_defaults,
            },
        )
    )

    return preference


def save_workspace_notification_preferences(
    *,
    workspace_id: str,
    channel_preferences: Dict[str, bool] | None = None,
    type_preferences: Dict[str, Dict[str, bool]] | None = None,
    quiet_hours: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    preference = build_notification_preference(
        owner_id=workspace_id,
        owner_type="workspace",
        workspace_id=workspace_id,
        channel_preferences=channel_preferences,
        type_preferences=type_preferences,
        quiet_hours=quiet_hours,
        inherit_workspace_defaults=False,
    )

    _append_jsonl(WORKSPACE_NOTIFICATION_PREFERENCES_PATH, preference)

    log_notification_preferences_audit(
        NotificationPreferenceAuditEvent(
            event_type="workspace_notification_preferences_saved",
            owner_id=workspace_id,
            owner_type="workspace",
            workspace_id=workspace_id,
            message="Workspace notification preferences saved.",
        )
    )

    return preference


def read_user_notification_preferences(limit: int = 1000) -> List[Dict[str, Any]]:
    return _read_jsonl(USER_NOTIFICATION_PREFERENCES_PATH, limit)


def read_workspace_notification_preferences(limit: int = 1000) -> List[Dict[str, Any]]:
    return _read_jsonl(WORKSPACE_NOTIFICATION_PREFERENCES_PATH, limit)


def read_notification_preferences_audit(limit: int = 1000) -> List[Dict[str, Any]]:
    return _read_jsonl(NOTIFICATION_PREFERENCES_AUDIT_PATH, limit)


def get_latest_user_notification_preferences(
    *,
    user_id: str,
    workspace_id: str | None = None,
) -> Dict[str, Any] | None:
    records = read_user_notification_preferences(limit=100000)

    for item in reversed(records):
        if item.get("owner_id") != user_id:
            continue
        if workspace_id and item.get("workspace_id") != workspace_id:
            continue
        return item

    return None


def get_latest_workspace_notification_preferences(
    *,
    workspace_id: str,
) -> Dict[str, Any] | None:
    records = read_workspace_notification_preferences(limit=100000)

    for item in reversed(records):
        if item.get("workspace_id") == workspace_id:
            return item

    return None


def merge_preferences(
    *,
    workspace_preferences: Dict[str, Any] | None,
    user_preferences: Dict[str, Any] | None,
) -> Dict[str, Any]:
    base = build_notification_preference(
        owner_id=str((workspace_preferences or {}).get("owner_id") or "default"),
        owner_type="resolved",
        workspace_id=(workspace_preferences or {}).get("workspace_id"),
    )

    if workspace_preferences:
        base["channel_preferences"] = {
            **base.get("channel_preferences", {}),
            **workspace_preferences.get("channel_preferences", {}),
        }
        base["type_preferences"] = {
            **base.get("type_preferences", {}),
            **workspace_preferences.get("type_preferences", {}),
        }
        base["quiet_hours"] = {
            **base.get("quiet_hours", {}),
            **workspace_preferences.get("quiet_hours", {}),
        }

    if user_preferences:
        base["owner_id"] = str(user_preferences.get("owner_id") or base.get("owner_id"))
        base["workspace_id"] = user_preferences.get("workspace_id") or base.get("workspace_id")

        if bool(user_preferences.get("inherit_workspace_defaults", True)):
            base["channel_preferences"] = {
                **base.get("channel_preferences", {}),
                **user_preferences.get("channel_preferences", {}),
            }
            base["type_preferences"] = {
                **base.get("type_preferences", {}),
                **user_preferences.get("type_preferences", {}),
            }
            base["quiet_hours"] = {
                **base.get("quiet_hours", {}),
                **user_preferences.get("quiet_hours", {}),
            }
        else:
            base["channel_preferences"] = user_preferences.get("channel_preferences", default_channel_preferences())
            base["type_preferences"] = user_preferences.get("type_preferences", default_type_preferences())
            base["quiet_hours"] = user_preferences.get("quiet_hours", asdict(QuietHours()))

    base["owner_type"] = "resolved"
    base["updated_at"] = _utc_now().isoformat()

    return base


def resolve_notification_preferences(
    *,
    user_id: str | None = None,
    workspace_id: str | None = None,
) -> Dict[str, Any]:
    workspace_preferences = (
        get_latest_workspace_notification_preferences(workspace_id=workspace_id)
        if workspace_id
        else None
    )

    user_preferences = (
        get_latest_user_notification_preferences(user_id=user_id, workspace_id=workspace_id)
        if user_id
        else None
    )

    return merge_preferences(
        workspace_preferences=workspace_preferences,
        user_preferences=user_preferences,
    )


def is_channel_enabled_for_notification(
    *,
    notification_type: str,
    channel: str,
    user_id: str | None = None,
    workspace_id: str | None = None,
) -> bool:
    if channel not in SUPPORTED_CHANNELS:
        return False

    preferences = resolve_notification_preferences(
        user_id=user_id,
        workspace_id=workspace_id,
    )

    channel_enabled = bool(
        preferences.get("channel_preferences", {}).get(channel, False)
    )

    type_enabled = bool(
        preferences.get("type_preferences", {})
        .get(notification_type, {})
        .get(channel, channel_enabled)
    )

    return channel_enabled and type_enabled


def _parse_hhmm(value: str) -> time | None:
    try:
        hour, minute = str(value).split(":", 1)
        return time(hour=int(hour), minute=int(minute))
    except Exception:
        return None


def is_quiet_hours_active(
    *,
    quiet_hours: Dict[str, Any],
    current_time: datetime | None = None,
) -> bool:
    if not bool(quiet_hours.get("enabled")):
        return False

    now = current_time or _utc_now()
    current = now.time()

    start = _parse_hhmm(str(quiet_hours.get("start_time") or "22:00"))
    end = _parse_hhmm(str(quiet_hours.get("end_time") or "07:00"))

    if not start or not end:
        return False

    if start < end:
        return start <= current <= end

    return current >= start or current <= end


def should_suppress_for_quiet_hours(
    *,
    user_id: str | None = None,
    workspace_id: str | None = None,
    priority: str = "normal",
    current_time: datetime | None = None,
) -> bool:
    if priority in {"urgent", "high"}:
        return False

    preferences = resolve_notification_preferences(
        user_id=user_id,
        workspace_id=workspace_id,
    )

    return is_quiet_hours_active(
        quiet_hours=preferences.get("quiet_hours", {}),
        current_time=current_time,
    )
