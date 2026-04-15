from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .models import Ticket, TicketMessage

BASE_DIR = Path(__file__).resolve().parent.parent
TMS_DATA_DIR = BASE_DIR / "data" / "tms"
TICKETS_FP = TMS_DATA_DIR / "tickets.json"
MESSAGES_FP = TMS_DATA_DIR / "messages.json"
META_FP = TMS_DATA_DIR / "meta.json"


def _ensure_dir() -> None:
    TMS_DATA_DIR.mkdir(parents=True, exist_ok=True)


def _json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Type not serializable: {type(value)!r}")


def _write_json(fp: Path, data: Any) -> None:
    _ensure_dir()
    fp.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, default=_json_default),
        encoding="utf-8",
    )


def _read_json(fp: Path, default: Any) -> Any:
    if not fp.is_file():
        return default
    try:
        return json.loads(fp.read_text(encoding="utf-8"))
    except Exception:
        return default


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def save_tickets(tickets: Dict[str, Ticket]) -> None:
    payload = {ticket_id: asdict(ticket) for ticket_id, ticket in tickets.items()}
    _write_json(TICKETS_FP, payload)


def load_tickets() -> Dict[str, Ticket]:
    raw = _read_json(TICKETS_FP, {})
    out: Dict[str, Ticket] = {}

    for ticket_id, obj in raw.items():
        out[ticket_id] = Ticket(
            ticket_id=obj["ticket_id"],
            ticket_number=obj["ticket_number"],
            subject=obj["subject"],
            description=obj["description"],
            status=obj.get("status", "new"),
            priority=obj.get("priority", "normal"),
            severity=obj.get("severity", "minor"),
            category=obj.get("category", "general"),
            source=obj.get("source", "app"),
            channel=obj.get("channel", "web"),
            requester_user_id=obj.get("requester_user_id"),
            requester_email=obj.get("requester_email"),
            requester_name=obj.get("requester_name"),
            workspace_id=obj.get("workspace_id"),
            plan_tier=obj.get("plan_tier"),
            assigned_team=obj.get("assigned_team"),
            assigned_staff_id=obj.get("assigned_staff_id"),
            resolution_code=obj.get("resolution_code"),
            created_at=_parse_dt(obj.get("created_at")) or datetime.now(),
            updated_at=_parse_dt(obj.get("updated_at")) or datetime.now(),
            closed_at=_parse_dt(obj.get("closed_at")),
        )
    return out


def save_messages(messages: Dict[str, List[TicketMessage]]) -> None:
    payload = {
        ticket_id: [asdict(message) for message in items]
        for ticket_id, items in messages.items()
    }
    _write_json(MESSAGES_FP, payload)


def load_messages() -> Dict[str, List[TicketMessage]]:
    raw = _read_json(MESSAGES_FP, {})
    out: Dict[str, List[TicketMessage]] = {}

    for ticket_id, items in raw.items():
        out[ticket_id] = [
            TicketMessage(
                message_id=obj["message_id"],
                ticket_id=obj["ticket_id"],
                author_type=obj["author_type"],
                author_id=obj.get("author_id"),
                body=obj["body"],
                is_customer_visible=obj.get("is_customer_visible", True),
                created_at=_parse_dt(obj.get("created_at")) or datetime.now(),
            )
            for obj in items
        ]
    return out


def save_meta(ticket_counter: int) -> None:
    _write_json(META_FP, {"ticket_counter": ticket_counter})


def load_meta() -> int:
    raw = _read_json(META_FP, {})
    return int(raw.get("ticket_counter", 0))