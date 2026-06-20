from __future__ import annotations

from typing import Any, Dict, List


def _num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value or default)
    except Exception:
        return default


def _candidate_quality_v1(item: Dict[str, Any]) -> float:
    score = 0.0

    score += min(1.0, _num(item.get("runtime_normalized_score"))) * 35.0
    score += min(1.0, _num(item.get("alias_match_score"))) * 20.0
    score += min(1.0, _num(item.get("topic_match_percent")) / 100.0) * 15.0

    intent = item.get("intent_intelligence") or {}
    score += min(1.0, _num(intent.get("intent_match_score"))) * 15.0

    journey = item.get("topic_intent_graph") or {}
    score += min(1.0, _num(journey.get("journey_confidence"))) * 10.0

    if item.get("auto_link_allowed"):
        score += 5.0

    if item.get("false_positive_blocked"):
        score -= 30.0

    if item.get("clear_intent_mismatch"):
        score -= 25.0

    return round(max(0.0, score), 4)


def apply_cross_target_competition_v1(
    *,
    candidates: List[Dict[str, Any]],
    dominance_margin: float = 12.0,
) -> List[Dict[str, Any]]:

    items = [dict(c or {}) for c in (candidates or [])]

    for item in items:
        item["cross_target_quality_score"] = _candidate_quality_v1(item)

    ranked = sorted(
        items,
        key=lambda x: x.get("cross_target_quality_score", 0),
        reverse=True,
    )

    if not ranked:
        return ranked

    winner = ranked[0]
    winner_score = _num(winner.get("cross_target_quality_score"))

    for idx, item in enumerate(ranked):
        item["cross_target_rank"] = idx + 1
        item["cross_target_winner"] = idx == 0
        item["cross_target_winner_url"] = winner.get("url")
        item["cross_target_winner_title"] = winner.get("title")
        item["cross_target_margin_from_winner"] = round(
            winner_score - _num(item.get("cross_target_quality_score")),
            4,
        )

        suppress = bool(
            idx > 0
            and winner_score >= 60
            and (winner_score - _num(item.get("cross_target_quality_score"))) >= dominance_margin
        )

        item["cross_target_suppressed"] = suppress

        if suppress:
            item["auto_link_allowed"] = False
            item["suggest_only"] = True
            item["resolver_decision"] = "SUGGEST_ONLY"
            item["cross_target_suppression_reason"] = "stronger_candidate_won"
        else:
            item["cross_target_suppression_reason"] = ""

    return ranked


def explain_cross_target_competition_v1() -> Dict[str, Any]:
    return {
        "layer": "resolver_cross_target_competition_v1",
        "purpose": "Rank competing resolver candidates universally and suppress weaker candidates when a stronger target clearly wins.",
        "universal": True,
        "uses": [
            "runtime_normalized_score",
            "alias_match_score",
            "topic_match_percent",
            "intent_match_score",
            "journey_confidence",
            "false_positive_blocked",
            "clear_intent_mismatch",
        ],
    }
