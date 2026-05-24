# backend/server/pools/target_pools/draft_target_intelligence.py

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


def _data_dir() -> Path:
    here = Path(__file__).resolve()
    server_dir = here.parents[2]  # .../backend/server
    return server_dir / "data"


def _pool_path(workspace_id: str) -> Path:
    return _data_dir() / "target_pools" / "draft" / f"draft_target_pool_{workspace_id}.json"


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _tokenize(value: Any) -> List[str]:
    text = _clean_text(value).lower()
    return re.findall(r"[a-z0-9]+", text)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default

def load_draft_targets(workspace_id: str) -> List[Dict[str, Any]]:
    ws = _clean_text(workspace_id)
    if not ws:
        return []

    fp = _pool_path(ws)
    if not fp.exists():
        return []

    try:
        obj = json.loads(fp.read_text(encoding="utf-8"))
    except Exception:
        return []

    items = obj.get("items") if isinstance(obj, dict) else []
    if not isinstance(items, list):
        return []

    return [item for item in items if isinstance(item, dict)]


def semantic_route_score(phrase: str, target: Dict[str, Any]) -> float:
    phrase_tokens = set(_tokenize(phrase))
    if not phrase_tokens:
        return 0.0

    title_tokens = set(_tokenize(target.get("title") or ""))
    label_tokens = set(_tokenize(target.get("label") or ""))
    h1_tokens = set(_tokenize(target.get("h1") or ""))

    target_tokens = title_tokens | label_tokens | h1_tokens
    if not target_tokens:
        return 0.0

    overlap = len(phrase_tokens & target_tokens)
    return round(min(1.0, overlap / max(len(phrase_tokens), 1)), 4)


def authority_score(target: Dict[str, Any]) -> float:
    priority_bucket = target.get("priority_bucket") or "supporting"
    page_type_hint = target.get("page_type_hint") or "general_article"
    publish_readiness = target.get("publish_readiness") or "planned"

    score = 0.2

    priority_weights = {
        "critical": 0.5,
        "strong": 0.35,
        "supporting": 0.2,
        "long_tail": 0.05,
    }

    page_type_weights = {
        "how_to": 0.2,
        "guide": 0.2,
        "comparison": 0.15,
        "explainer": 0.1,
        "listicle": 0.08,
        "general_article": 0.05,
    }

    readiness_weights = {
        "ready": 0.2,
        "review": 0.12,
        "planned": 0.05,
    }

    score += priority_weights.get(priority_bucket, 0.1)
    score += page_type_weights.get(page_type_hint, 0.05)
    score += readiness_weights.get(publish_readiness, 0.05)

    return round(min(score, 1.0), 4)


def topic_graph_score(target: Dict[str, Any]) -> float:
    title = _clean_text(target.get("title"))
    tokens = _tokenize(title)

    if not tokens:
        return 0.0

    unique_tokens = set(tokens)
    score = 0.2

    # Universal semantic breadth.
    if len(unique_tokens) >= 5:
        score += 0.2
    if len(unique_tokens) >= 8:
        score += 0.15

    # Universal cross-topic connectors.
    connectors = {
        "and",
        "or",
        "with",
        "without",
        "during",
        "while",
        "before",
        "after",
        "between",
        "among",
        "vs",
        "versus",
        "for",
        "to",
    }
    connector_hits = len(unique_tokens & connectors)
    score += min(connector_hits * 0.04, 0.16)

    # Universal intent/action terms.
    intent_terms = {
        "how",
        "why",
        "what",
        "when",
        "guide",
        "steps",
        "plan",
        "strategy",
        "checklist",
        "tips",
        "ideas",
        "best",
        "avoid",
        "improve",
        "reduce",
        "increase",
        "choose",
        "compare",
        "understand",
        "explained",
    }
    intent_hits = len(unique_tokens & intent_terms)
    score += min(intent_hits * 0.05, 0.20)

    # Universal specificity markers.
    specificity_terms = {
        "safe",
        "practical",
        "advanced",
        "beginner",
        "complete",
        "common",
        "early",
        "future",
        "technical",
        "local",
        "enterprise",
        "personal",
        "professional",
    }
    specificity_hits = len(unique_tokens & specificity_terms)
    score += min(specificity_hits * 0.04, 0.12)

    # Slight boost for non-trivial multi-word targets.
    if len(tokens) >= 6:
        score += 0.07

    return round(min(score, 1.0), 4)


def rb2_weight_score(target: Dict[str, Any]) -> float:
    score = 0.1

    priority_bucket = target.get("priority_bucket") or "supporting"
    page_type_hint = target.get("page_type_hint") or "general_article"

    if target.get("future_content"):
        score += 0.12

    if target.get("planned_content"):
        score += 0.10

    priority_weights = {
        "critical": 0.34,
        "strong": 0.24,
        "supporting": 0.12,
        "long_tail": 0.04,
    }
    score += priority_weights.get(priority_bucket, 0.08)

    page_type_weights = {
        "how_to": 0.16,
        "guide": 0.16,
        "comparison": 0.12,
        "explainer": 0.10,
        "listicle": 0.08,
        "general_article": 0.05,
    }
    score += page_type_weights.get(page_type_hint, 0.05)

    return round(min(score, 1.0), 4)



def freshness_score(target: Dict[str, Any]) -> float:
    status = str(target.get("draft_status") or "planned").lower()
    readiness = str(target.get("publish_readiness") or "planned").lower()

    score = 0.35

    if status == "published":
        score += 0.35
    elif status in {"ready", "ready_to_publish"}:
        score += 0.25
    elif status in {"review", "in_review"}:
        score += 0.18
    elif status in {"in_progress", "drafting"}:
        score += 0.12
    elif status == "planned":
        score += 0.08

    if readiness in {"ready", "ready_to_publish"}:
        score += 0.18
    elif readiness in {"review", "in_review"}:
        score += 0.12
    elif readiness == "planned":
        score += 0.05

    if target.get("published_url"):
        score += 0.12

    return round(min(score, 1.0), 4)


def semantic_intent_score(phrase: str, target: Dict[str, Any]) -> float:
    phrase_tokens = set(_tokenize(phrase))
    title_tokens = set(_tokenize(target.get("title") or ""))
    if not phrase_tokens or not title_tokens:
        return 0.0

    score = 0.2

    direct_overlap = len(phrase_tokens & title_tokens) / max(len(phrase_tokens), 1)
    score += min(direct_overlap * 0.45, 0.45)

    page_type = target.get("page_type_hint") or "general_article"
    if page_type in {"how_to", "guide"} and phrase_tokens & {"how", "guide", "steps", "plan", "strategy"}:
        score += 0.15
    if page_type == "comparison" and phrase_tokens & {"vs", "versus", "compare", "comparison"}:
        score += 0.15
    if page_type == "explainer" and phrase_tokens & {"what", "why", "explained", "understanding"}:
        score += 0.15

    signals = target.get("draft_priority_signals") or {}
    if signals.get("has_practical_intent") and phrase_tokens & {"how", "steps", "plan", "practical", "guide"}:
        score += 0.10
    if signals.get("has_comparison_intent") and phrase_tokens & {"vs", "compare", "versus"}:
        score += 0.10

    return round(min(score, 1.0), 4)


def publish_transition_score(target: Dict[str, Any]) -> float:
    score = 0.2

    if target.get("planned_url"):
        score += 0.18
    if target.get("placeholder_url"):
        score += 0.18
    if target.get("published_url"):
        score += 0.30
    if target.get("placeholder_generated"):
        score += 0.08
    if target.get("document_id"):
        score += 0.06

    return round(min(score, 1.0), 4)


def score_draft_target(
    phrase: str,
    target: Dict[str, Any],
) -> Dict[str, Any]:

    title = target.get("title") or ""
    page_type_hint = target.get("page_type_hint") or "general_article"
    priority_bucket = target.get("priority_bucket") or "supporting"

    route = semantic_route_score(phrase, target)
    authority = authority_score(target)
    graph = topic_graph_score(target)
    rb2 = rb2_weight_score(target)
    fresh = freshness_score(target)
    intent = semantic_intent_score(phrase, target)
    transition = publish_transition_score(target)

    priority_weights = {
        "critical": 1.0,
        "strong": 0.8,
        "supporting": 0.5,
        "long_tail": 0.2,
    }
    priority = priority_weights.get(priority_bucket, 0.3)

    page_type_weights = {
        "how_to": 0.9,
        "guide": 0.9,
        "comparison": 0.8,
        "explainer": 0.7,
        "listicle": 0.6,
        "general_article": 0.5,
    }
    page_type = page_type_weights.get(page_type_hint, 0.5)

    # =========================================================
    # SEMANTIC GATE CORRECTION
    # =========================================================
    # Universal rule:
    # Non-semantic targets must never dominate ranking simply
    # because of authority/RB2/graph strength.
    #
    # semantic_route_score is the PRIMARY gatekeeper.
    # =========================================================

    semantic_gate_multiplier = 1.0

    if route <= 0.0:
        semantic_gate_multiplier = 0.08
    elif route < 0.15:
        semantic_gate_multiplier = 0.18
    elif route < 0.30:
        semantic_gate_multiplier = 0.35
    elif route < 0.50:
        semantic_gate_multiplier = 0.60
    else:
        semantic_gate_multiplier = 1.0

    base_score = (
        route * 0.42
        + intent * 0.20
        + priority * 0.08
        + authority * 0.08
        + graph * 0.06
        + rb2 * 0.06
        + fresh * 0.05
        + transition * 0.03
        + page_type * 0.02
    )

    target_score = round(
        base_score * semantic_gate_multiplier,
        4,
    )

    explanation = {
        "best_signal": max(
            {
                "semantic_route": route,
                "semantic_intent": intent,
                "priority": priority,
                "authority": authority,
                "topic_graph": graph,
                "rb2_weight": rb2,
                "freshness": fresh,
                "publish_transition": transition,
                "page_type": page_type,
            }.items(),
            key=lambda kv: kv[1],
        )[0],
        "reason": "Draft target scored using universal route, intent, authority, graph, RB2, freshness, and publish-transition signals.",
    }

    audit = {
        "source_type": "draft",
        "source_origin": target.get("source_origin") or "draft_pool",
        "draft_status": target.get("draft_status"),
        "publish_readiness": target.get("publish_readiness"),
        "future_content": bool(target.get("future_content")),
        "planned_content": bool(target.get("planned_content")),
        "placeholder_generated": bool(target.get("placeholder_generated")),
    }

    return {
        "draft_id": target.get("draft_id"),
        "title": title,
        "url": target.get("url"),
        "planned_url": target.get("planned_url"),
        "placeholder_url": target.get("placeholder_url"),
        "published_url": target.get("published_url"),
        "page_type_hint": page_type_hint,
        "priority_bucket": priority_bucket,
        "semantic_route_score": round(route, 4),
        "semantic_intent_score": round(intent, 4),
        "priority_score": round(priority, 4),
        "authority_score": round(authority, 4),
        "topic_graph_score": round(graph, 4),
        "rb2_weight_score": round(rb2, 4),
        "freshness_score": round(fresh, 4),
        "publish_transition_score": round(transition, 4),
        "page_type_score": round(page_type, 4),
        "semantic_gate_multiplier": round(semantic_gate_multiplier, 4),
        "target_score": target_score,
        "score_explanation": explanation,
        "intelligence_audit": audit,
    }


def _dedupe_ranked_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: set[str] = set()
    out: List[Dict[str, Any]] = []

    for item in results:
        key = str(item.get("url") or item.get("draft_id") or item.get("title") or "").lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(item)

    return out


def _semantic_tie_break_key(item: Dict[str, Any]) -> tuple:
    return (
        _safe_float(item.get("target_score")),
        _safe_float(item.get("semantic_route_score")),
        _safe_float(item.get("semantic_intent_score")),
        _safe_float(item.get("authority_score")),
        _safe_float(item.get("rb2_weight_score")),
        _safe_float(item.get("topic_graph_score")),
    )


def draft_target_ranker(
    phrase: str,
    targets: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    scored = [
        score_draft_target(phrase, target)
        for target in targets
        if isinstance(target, dict)
    ]

    scored = _dedupe_ranked_results(scored)
    scored.sort(key=_semantic_tie_break_key, reverse=True)
    return scored


def rank_draft_targets(
    workspace_id: str,
    phrase: str,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    targets = load_draft_targets(workspace_id)
    ranked = draft_target_ranker(phrase, targets)
    return ranked[: max(int(limit or 10), 1)]


def best_draft_target(
    workspace_id: str,
    phrase: str,
) -> Optional[Dict[str, Any]]:
    ranked = rank_draft_targets(workspace_id, phrase, limit=1)
    return ranked[0] if ranked else None

