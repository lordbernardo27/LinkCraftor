
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.server.tms.help_center import (
    read_articles,
)


DATA_DIR = Path("backend/server/data/tms")

TICKET_DEFLECTION_ANALYTICS_PATH = DATA_DIR / "ticket_deflection_analytics.jsonl"


@dataclass(frozen=True)
class DeflectionEvent:
    event_type: str
    ticket_id: str
    article_id: str | None = None
    workspace_id: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not TICKET_DEFLECTION_ANALYTICS_PATH.exists():
        TICKET_DEFLECTION_ANALYTICS_PATH.write_text(
            "",
            encoding="utf-8",
        )


def _append_jsonl(
    payload: Dict[str, Any],
) -> None:
    _ensure_store()

    with TICKET_DEFLECTION_ANALYTICS_PATH.open(
        "a",
        encoding="utf-8",
    ) as f:
        f.write(
            json.dumps(payload, ensure_ascii=False)
            + "\n"
        )


def _read_jsonl(
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    _ensure_store()

    lines = TICKET_DEFLECTION_ANALYTICS_PATH.read_text(
        encoding="utf-8"
    ).splitlines()

    return [
        json.loads(line)
        for line in lines[-limit:]
        if line.strip()
    ]


# ============================================================
# 13.2.1 SUGGESTED ARTICLES
# ============================================================

def suggest_articles_for_ticket(
    *,
    ticket_subject: str,
    ticket_body: str = "",
    limit: int = 5,
) -> List[Dict[str, Any]]:

    query = (
        f"{ticket_subject} {ticket_body}"
    ).lower()

    scored = []

    for article in read_articles(limit=100000):

        text = " ".join([
            str(article.get("title", "")),
            str(article.get("summary", "")),
            str(article.get("content", "")),
        ]).lower()

        score = 0

        for token in query.split():
            if len(token) < 3:
                continue

            if token in text:
                score += 1

        if score > 0:
            scored.append(
                {
                    "score": score,
                    "article": article,
                }
            )

    scored.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    return [
        item["article"]
        for item in scored[:limit]
    ]


# ============================================================
# 13.2.2 CONTEXTUAL RECOMMENDATIONS
# ============================================================

def build_contextual_recommendations(
    *,
    ticket: Dict[str, Any],
    limit: int = 5,
) -> Dict[str, Any]:

    suggestions = suggest_articles_for_ticket(
        ticket_subject=str(
            ticket.get("subject", "")
        ),
        ticket_body=str(
            ticket.get("description", "")
        ),
        limit=limit,
    )

    return {
        "ticket_id": ticket.get("id"),
        "recommendations": suggestions,
        "recommendation_count": len(
            suggestions
        ),
    }


# ============================================================
# 13.2.3 AI ARTICLE MATCHING
# ============================================================

def ai_match_help_articles(
    *,
    ticket: Dict[str, Any],
    limit: int = 5,
) -> List[Dict[str, Any]]:

    matches = []

    for article in suggest_articles_for_ticket(
        ticket_subject=str(
            ticket.get("subject", "")
        ),
        ticket_body=str(
            ticket.get("description", "")
        ),
        limit=limit,
    ):
        matches.append(
            {
                "article_id": article.get(
                    "article_id"
                ),
                "title": article.get(
                    "title"
                ),
                "confidence": 0.75,
                "reason": "keyword_similarity",
            }
        )

    return matches


# ============================================================
# 13.2.4 TICKET REDUCTION ANALYTICS
# ============================================================

def record_deflection_event(
    *,
    event_type: str,
    ticket_id: str,
    article_id: str | None = None,
    workspace_id: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:

    event = DeflectionEvent(
        event_type=event_type,
        ticket_id=ticket_id,
        article_id=article_id,
        workspace_id=workspace_id,
        metadata=metadata or {},
    )

    payload = asdict(event)

    _append_jsonl(payload)

    return payload


def ticket_deflection_analytics() -> Dict[str, Any]:

    events = _read_jsonl(limit=100000)

    suggested = 0
    viewed = 0
    deflected = 0

    for event in events:

        et = str(
            event.get("event_type", "")
        )

        if et == "article_suggested":
            suggested += 1

        elif et == "article_viewed":
            viewed += 1

        elif et == "ticket_deflected":
            deflected += 1

    rate = (
        round(
            (deflected / suggested) * 100,
            2,
        )
        if suggested
        else 0
    )

    return {
        "articles_suggested": suggested,
        "articles_viewed": viewed,
        "tickets_deflected": deflected,
        "deflection_rate_percent": rate,
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }


def read_ticket_deflection_events(
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    return _read_jsonl(limit)
