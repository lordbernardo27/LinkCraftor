from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def _data_dir() -> Path:
    here = Path(__file__).resolve()
    return here.parents[1] / "data"


def _performance_dir() -> Path:
    p = _data_dir() / "resolver_performance"
    p.mkdir(parents=True, exist_ok=True)
    return p


def performance_store_path(workspace_id: str) -> Path:
    return _performance_dir() / f"{workspace_id}.json"


def load_performance_store(workspace_id: str) -> Dict[str, Any]:
    p = performance_store_path(workspace_id)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_performance_store(workspace_id: str, store: Dict[str, Any]) -> None:
    p = performance_store_path(workspace_id)
    p.write_text(json.dumps(store, indent=2), encoding="utf-8")


def record_performance_event_v1(
    *,
    workspace_id: str,
    target_url: str,
    clicks: int = 0,
    impressions: int = 0,
    engagements: int = 0,
    conversions: int = 0,
) -> Dict[str, Any]:

    store = load_performance_store(workspace_id)

    record = store.setdefault(
        target_url,
        {
            "clicks": 0,
            "impressions": 0,
            "engagements": 0,
            "conversions": 0,
        },
    )

    record["clicks"] += int(clicks or 0)
    record["impressions"] += int(impressions or 0)
    record["engagements"] += int(engagements or 0)
    record["conversions"] += int(conversions or 0)

    save_performance_store(workspace_id, store)
    return record


def analyze_performance_v1(
    *,
    workspace_id: str,
    target_url: str,
) -> Dict[str, Any]:

    store = load_performance_store(workspace_id)
    record = store.get(
        target_url,
        {
            "clicks": 0,
            "impressions": 0,
            "engagements": 0,
            "conversions": 0,
        },
    )

    clicks = int(record.get("clicks", 0))
    impressions = int(record.get("impressions", 0))
    engagements = int(record.get("engagements", 0))
    conversions = int(record.get("conversions", 0))

    ctr = clicks / impressions if impressions > 0 else 0.0
    engagement_rate = engagements / clicks if clicks > 0 else 0.0
    conversion_rate = conversions / clicks if clicks > 0 else 0.0

    weighted_score = (
        min(40.0, ctr * 400)
        + min(30.0, engagement_rate * 60)
        + min(30.0, conversion_rate * 100)
    )

    if weighted_score >= 60:
        level = "high"
        boost = 20.0
    elif weighted_score >= 30:
        level = "medium"
        boost = 10.0
    elif impressions > 0:
        level = "low"
        boost = -5.0
    else:
        level = "none"
        boost = 0.0

    return {
        "has_performance_analysis": True,
        "clicks": clicks,
        "impressions": impressions,
        "engagements": engagements,
        "conversions": conversions,
        "ctr": round(ctr, 4),
        "engagement_rate": round(engagement_rate, 4),
        "conversion_rate": round(conversion_rate, 4),
        "performance_score": round(weighted_score, 4),
        "performance_level": level,
        "performance_boost": boost,
    }


def explain_performance_v1() -> Dict[str, Any]:
    return {
        "layer": "resolver_historical_performance_v1",
        "purpose": "Use historical target performance to influence future resolver ranking.",
        "universal": True,
        "uses": [
            "clicks",
            "impressions",
            "CTR",
            "engagements",
            "conversions",
        ],
        "does_not_use": [
            "health rules",
            "finance rules",
            "legal rules",
            "industry-specific hardcoding",
        ],
    }
