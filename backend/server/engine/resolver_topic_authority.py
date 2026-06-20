from __future__ import annotations

from typing import Any, Dict


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _boolish(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def analyze_topic_authority_v1(target: Dict[str, Any]) -> Dict[str, Any]:
    """
    Universal Topic Authority Layer.

    Scores how central/authoritative a target appears to be using
    generic graph and metadata signals only.
    """
    target = target or {}
    metadata = target.get("metadata") if isinstance(target.get("metadata"), dict) else {}

    authority_score = _to_float(target.get("authority_score"), 0.0)
    topic_graph_score = _to_float(target.get("topic_graph_score"), 0.0)
    semantic_route_score = _to_float(target.get("semantic_route_score"), 0.0)

    cluster_size = _to_float(
        target.get("cluster_size")
        or metadata.get("cluster_size")
        or metadata.get("topic_cluster_size"),
        0.0,
    )

    incoming_links = _to_float(
        target.get("incoming_links")
        or metadata.get("incoming_links")
        or metadata.get("internal_inlinks"),
        0.0,
    )

    priority_bucket = str(
        target.get("priority_bucket")
        or metadata.get("priority_bucket")
        or ""
    ).lower()

    page_type_hint = str(
        target.get("page_type_hint")
        or metadata.get("page_type_hint")
        or ""
    ).lower()

    pillar_like = (
        _boolish(target.get("pillar"))
        or _boolish(metadata.get("pillar"))
        or priority_bucket in {"pillar", "hub", "primary", "core", "high"}
        or page_type_hint in {"pillar", "hub", "guide", "overview", "category"}
    )

    score = 0.0
    reasons = []

    if authority_score > 0:
        score += min(30.0, authority_score / 3.0)
        reasons.append("authority_score_signal")

    if topic_graph_score > 0:
        score += min(25.0, topic_graph_score / 4.0)
        reasons.append("topic_graph_signal")

    if semantic_route_score > 0:
        score += min(15.0, semantic_route_score / 8.0)
        reasons.append("semantic_route_signal")

    if cluster_size > 0:
        score += min(15.0, cluster_size * 1.5)
        reasons.append("cluster_size_signal")

    if incoming_links > 0:
        score += min(10.0, incoming_links * 0.5)
        reasons.append("incoming_link_signal")

    if pillar_like:
        score += 15.0
        reasons.append("pillar_or_central_page_signal")

    score = max(0.0, min(100.0, score))

    if score >= 70:
        level = "high"
        boost = 30.0
    elif score >= 35:
        level = "medium"
        boost = 15.0
    elif score > 0:
        level = "low"
        boost = 5.0
    else:
        level = "none"
        boost = 0.0

    return {
        "has_topic_authority_analysis": True,
        "topic_authority_score": round(score, 4),
        "topic_authority_level": level,
        "topic_authority_boost": boost,
        "topic_authority_reasons": reasons,
        "pillar_like": pillar_like,
        "signals": {
            "authority_score": authority_score,
            "topic_graph_score": topic_graph_score,
            "semantic_route_score": semantic_route_score,
            "cluster_size": cluster_size,
            "incoming_links": incoming_links,
            "priority_bucket": priority_bucket,
            "page_type_hint": page_type_hint,
        },
    }


def explain_topic_authority_v1() -> Dict[str, Any]:
    return {
        "layer": "topic_authority_v1",
        "purpose": "Prefer central, authoritative, pillar-like targets using universal graph and metadata signals.",
        "universal": True,
        "uses": [
            "authority score",
            "topic graph score",
            "semantic route score",
            "cluster size",
            "incoming links",
            "priority bucket",
            "page type hint",
        ],
        "does_not_use": [
            "health terms",
            "finance terms",
            "legal terms",
            "industry-specific hardcoded rules",
        ],
    }
