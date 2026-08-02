
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data/tms")

CONVERSATIONS_PATH = DATA_DIR / "conversations.jsonl"
CHANNELS_PATH = DATA_DIR / "channels.jsonl"
CONVERSATION_AUDIT_PATH = DATA_DIR / "conversation_audit.jsonl"


@dataclass(frozen=True)
class Conversation:
    conversation_id: str
    workspace_id: str
    channel_id: str
    title: str
    conversation_type: str = "channel"
    archived: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class Channel:
    channel_id: str
    workspace_id: str
    name: str
    visibility: str = "public"
    archived: bool = False
    members: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _ensure_store():

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    for path in (
        CONVERSATIONS_PATH,
        CHANNELS_PATH,
        CONVERSATION_AUDIT_PATH,
    ):
        if not path.exists():
            path.write_text(
                "",
                encoding="utf-8",
            )


def _utc_now():

    return datetime.now(
        timezone.utc,
    ).isoformat()


def _id(prefix: str):

    return (
        prefix
        + "_"
        + datetime.now(
            timezone.utc
        ).strftime(
            "%Y%m%d%H%M%S%f"
        )
    )


def _append(path: Path, payload: Dict[str, Any]):

    _ensure_store()

    with path.open(
        "a",
        encoding="utf-8",
    ) as f:
        f.write(
            json.dumps(
                payload,
                ensure_ascii=False,
            )
            + "\n"
        )


def _read(path: Path, limit: int = 1000):

    _ensure_store()

    return [
        json.loads(line)
        for line in path.read_text(
            encoding="utf-8"
        ).splitlines()[-limit:]
        if line.strip()
    ]


def _audit(
    event_type: str,
    workspace_id: str,
    metadata: Dict[str, Any] | None = None,
):

    _append(
        CONVERSATION_AUDIT_PATH,
        {
            "event_type": event_type,
            "workspace_id": workspace_id,
            "metadata": metadata or {},
            "created_at": _utc_now(),
        },
    )


def create_channel(
    *,
    workspace_id: str,
    name: str,
    visibility: str = "public",
    members: List[str] | None = None,
) -> Dict[str, Any]:

    channel = Channel(
        channel_id=_id("channel"),
        workspace_id=workspace_id,
        name=name,
        visibility=visibility,
        members=members or [],
    )

    payload = asdict(channel)

    _append(
        CHANNELS_PATH,
        payload,
    )

    _audit(
        "channel_created",
        workspace_id,
        {
            "channel_id": channel.channel_id,
        },
    )

    return payload


def create_conversation(
    *,
    workspace_id: str,
    channel_id: str,
    title: str,
) -> Dict[str, Any]:

    conversation = Conversation(
        conversation_id=_id("conversation"),
        workspace_id=workspace_id,
        channel_id=channel_id,
        title=title,
    )

    payload = asdict(
        conversation,
    )

    _append(
        CONVERSATIONS_PATH,
        payload,
    )

    _audit(
        "conversation_created",
        workspace_id,
        {
            "conversation_id": conversation.conversation_id,
        },
    )

    return payload


# ============================================================
# MEMBERSHIP MANAGEMENT
# ============================================================

def add_channel_member(
    *,
    channel: Dict[str, Any],
    member_id: str,
) -> Dict[str, Any]:

    members = list(channel.get("members") or [])

    if member_id not in members:
        members.append(member_id)

    updated = {
        **channel,
        "members": members,
    }

    _append(
        CHANNELS_PATH,
        updated,
    )

    _audit(
        "channel_member_added",
        channel["workspace_id"],
        {
            "channel_id": channel["channel_id"],
            "member_id": member_id,
        },
    )

    return updated


def remove_channel_member(
    *,
    channel: Dict[str, Any],
    member_id: str,
) -> Dict[str, Any]:

    members = [
        m
        for m in channel.get("members", [])
        if m != member_id
    ]

    updated = {
        **channel,
        "members": members,
    }

    _append(
        CHANNELS_PATH,
        updated,
    )

    _audit(
        "channel_member_removed",
        channel["workspace_id"],
        {
            "channel_id": channel["channel_id"],
            "member_id": member_id,
        },
    )

    return updated


# ============================================================
# ARCHIVE
# ============================================================

def archive_channel(
    *,
    channel: Dict[str, Any],
) -> Dict[str, Any]:

    updated = {
        **channel,
        "archived": True,
    }

    _append(
        CHANNELS_PATH,
        updated,
    )

    _audit(
        "channel_archived",
        channel["workspace_id"],
        {
            "channel_id": channel["channel_id"],
        },
    )

    return updated


def restore_channel(
    *,
    channel: Dict[str, Any],
) -> Dict[str, Any]:

    updated = {
        **channel,
        "archived": False,
    }

    _append(
        CHANNELS_PATH,
        updated,
    )

    _audit(
        "channel_restored",
        channel["workspace_id"],
        {
            "channel_id": channel["channel_id"],
        },
    )

    return updated


# ============================================================
# READERS
# ============================================================

def read_channels(
    limit: int = 1000,
) -> List[Dict[str, Any]]:

    return _read(
        CHANNELS_PATH,
        limit,
    )


def read_conversations(
    limit: int = 1000,
) -> List[Dict[str, Any]]:

    return _read(
        CONVERSATIONS_PATH,
        limit,
    )


def read_conversation_audit(
    limit: int = 1000,
) -> List[Dict[str, Any]]:

    return _read(
        CONVERSATION_AUDIT_PATH,
        limit,
    )


# ============================================================
# SUMMARY
# ============================================================

def build_conversation_summary() -> Dict[str, Any]:

    channels = read_channels(
        limit=100000,
    )

    conversations = read_conversations(
        limit=100000,
    )

    return {
        "channel_count": len(channels),
        "conversation_count": len(conversations),
        "channels": channels,
        "conversations": conversations,
        "generated_at": _utc_now(),
    }

