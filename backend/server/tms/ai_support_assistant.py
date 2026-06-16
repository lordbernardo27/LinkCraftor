
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data/tms")

AI_ASSISTANT_AUDIT_PATH = DATA_DIR / "ai_support_assistant_audit.jsonl"


@dataclass(frozen=True)
class AIAssistantEvent:
    event_type: str
    ticket_id: str | None = None
    workspace_id: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not AI_ASSISTANT_AUDIT_PATH.exists():
        AI_ASSISTANT_AUDIT_PATH.write_text(
            "",
            encoding="utf-8",
        )


def _append_audit(
    payload: Dict[str, Any],
) -> None:
    _ensure_store()

    with AI_ASSISTANT_AUDIT_PATH.open(
        "a",
        encoding="utf-8",
    ) as f:
        f.write(
            json.dumps(payload, ensure_ascii=False)
            + "\n"
        )


def log_ai_assistant_event(
    event: AIAssistantEvent,
) -> Dict[str, Any]:

    payload = asdict(event)

    _append_audit(payload)

    return payload


# ============================================================
# 14.1.1 AI REPLY DRAFTING
# ============================================================

def draft_ai_reply(
    *,
    ticket: Dict[str, Any],
    tone: str = "professional",
) -> Dict[str, Any]:

    subject = str(ticket.get("subject", "Support Request"))

    reply = (
        f"Thank you for contacting support regarding "
        f"'{subject}'. We are reviewing your request "
        f"and will provide an update shortly."
    )

    return {
        "reply": reply,
        "tone": tone,
        "generated": True,
    }


# ============================================================
# 14.1.2 TONE-AWARE REPLIES
# ============================================================

def build_tone_aware_reply(
    *,
    ticket: Dict[str, Any],
    tone: str = "professional",
) -> Dict[str, Any]:

    base = draft_ai_reply(
        ticket=ticket,
        tone=tone,
    )

    tone_prefix = {
        "professional": "",
        "friendly": "Hi there! ",
        "empathetic": "We understand your concern. ",
        "urgent": "This issue is receiving priority attention. ",
    }

    return {
        **base,
        "reply": tone_prefix.get(
            tone,
            ""
        ) + base["reply"],
    }


# ============================================================
# 14.1.3 CONTEXT-AWARE SUMMARIES
# ============================================================

def generate_ticket_summary(
    *,
    ticket: Dict[str, Any],
) -> Dict[str, Any]:

    subject = str(ticket.get("subject", ""))
    description = str(
        ticket.get("description", "")
    )

    summary = (
        description[:300]
        if description
        else subject
    )

    return {
        "ticket_id": ticket.get("id"),
        "summary": summary,
    }


# ============================================================
# 14.1.4 SUGGESTED NEXT ACTIONS
# ============================================================

def suggest_next_actions(
    *,
    ticket: Dict[str, Any],
) -> Dict[str, Any]:

    actions = [
        "Review ticket details",
        "Verify customer account",
        "Check related product logs",
        "Respond to customer",
    ]

    return {
        "ticket_id": ticket.get("id"),
        "actions": actions,
    }


# ============================================================
# 14.1.5 MULTI-MESSAGE SUMMARIZATION
# ============================================================

def summarize_messages(
    messages: List[Dict[str, Any]],
) -> Dict[str, Any]:

    combined = []

    for msg in messages:
        text = str(
            msg.get("message", "")
        ).strip()

        if text:
            combined.append(text)

    summary = " ".join(combined)

    if len(summary) > 500:
        summary = summary[:500] + "..."

    return {
        "message_count": len(messages),
        "summary": summary,
    }


def build_ai_assistant_package(
    *,
    ticket: Dict[str, Any],
    messages: List[Dict[str, Any]] | None = None,
    tone: str = "professional",
) -> Dict[str, Any]:

    package = {
        "reply_draft": build_tone_aware_reply(
            ticket=ticket,
            tone=tone,
        ),
        "summary": generate_ticket_summary(
            ticket=ticket,
        ),
        "next_actions": suggest_next_actions(
            ticket=ticket,
        ),
        "conversation_summary": summarize_messages(
            messages or [],
        ),
    }

    log_ai_assistant_event(
        AIAssistantEvent(
            event_type="ai_assistant_package_generated",
            ticket_id=str(
                ticket.get("id")
            ),
            workspace_id=ticket.get(
                "workspace_id"
            ),
            metadata={
                "tone": tone,
            },
        )
    )

    return package


def read_ai_assistant_audit(
    limit: int = 1000,
) -> List[Dict[str, Any]]:

    _ensure_store()

    lines = AI_ASSISTANT_AUDIT_PATH.read_text(
        encoding="utf-8"
    ).splitlines()

    return [
        json.loads(line)
        for line in lines[-limit:]
        if line.strip()
    ]
