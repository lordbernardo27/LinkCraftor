from __future__ import annotations

from typing import Any, Dict, List, Optional


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _get_score(target: Dict[str, Any]) -> float:
    for key in (
        "final_score",
        "target_score",
        "score",
        "resolver_score",
        "confidence",
    ):
        if key in target:
            return _to_float(target.get(key), 0.0)
    return 0.0


def analyze_resolver_competition_v1(
    ranked_targets: List[Dict[str, Any]],
    *,
    strong_margin: float = 15.0,
    medium_margin: float = 7.0,
    minimum_winner_score: float = 45.0,
) -> Dict[str, Any]:
    """
    Universal competition intelligence layer.

    It compares the winning target against the runner-up and detects
    whether the resolver has a clear winner or a close call.

    This layer is niche-agnostic. It does not inspect medical, finance,
    legal, SEO, ecommerce, or industry-specific terms.
    """
    targets = list(ranked_targets or [])

    if not targets:
        return {
            "has_competition_analysis": True,
            "has_winner": False,
            "has_runner_up": False,
            "winner_score": 0.0,
            "runner_up_score": 0.0,
            "score_margin": 0.0,
            "close_call": False,
            "competition_confidence": "none",
            "competition_action": "reject",
            "competition_reason": "no_targets_available",
        }

    sorted_targets = sorted(targets, key=_get_score, reverse=True)

    winner = sorted_targets[0]
    runner_up: Optional[Dict[str, Any]] = sorted_targets[1] if len(sorted_targets) > 1 else None

    winner_score = _get_score(winner)
    runner_up_score = _get_score(runner_up) if runner_up else 0.0
    score_margin = winner_score - runner_up_score if runner_up else winner_score

    if winner_score < minimum_winner_score:
        confidence = "weak"
        action = "reject"
        reason = "winner_score_below_minimum"
        close_call = bool(runner_up and score_margin < medium_margin)
    elif not runner_up:
        confidence = "strong"
        action = "auto_link_allowed"
        reason = "single_clear_winner"
        close_call = False
    elif score_margin >= strong_margin:
        confidence = "strong"
        action = "auto_link_allowed"
        reason = "large_winner_margin"
        close_call = False
    elif score_margin >= medium_margin:
        confidence = "medium"
        action = "suggest_only"
        reason = "moderate_winner_margin"
        close_call = False
    else:
        confidence = "low"
        action = "suggest_only"
        reason = "close_call_detected"
        close_call = True

    return {
        "has_competition_analysis": True,
        "has_winner": True,
        "has_runner_up": runner_up is not None,
        "winner_score": round(winner_score, 4),
        "runner_up_score": round(runner_up_score, 4),
        "score_margin": round(score_margin, 4),
        "close_call": close_call,
        "competition_confidence": confidence,
        "competition_action": action,
        "competition_reason": reason,
        "winner_target": winner,
        "runner_up_target": runner_up,
    }


def explain_resolver_competition_v1() -> Dict[str, Any]:
    return {
        "layer": "resolver_competition_intelligence_v1",
        "purpose": "Compare winner and runner-up targets to detect close calls before auto-linking.",
        "universal": True,
        "uses": [
            "ranked target scores",
            "winner margin",
            "runner-up risk",
            "minimum winner confidence",
        ],
        "does_not_use": [
            "health terms",
            "finance terms",
            "legal terms",
            "SEO-specific terms",
            "industry-specific hardcoded rules",
        ],
        "actions": [
            "auto_link_allowed",
            "suggest_only",
            "reject",
        ],
    }
