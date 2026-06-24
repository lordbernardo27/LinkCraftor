from __future__ import annotations

from typing import Any, Dict


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def decide_resolver_action_v1(
    target: Dict[str, Any],
    *,
    minimum_auto_confidence: float = 0.70,
    minimum_suggest_confidence: float = 0.45,
) -> Dict[str, Any]:
    """
    Universal resolver decision layer.

    Converts resolver signals into one final action:
    AUTO_LINK, SUGGEST_ONLY, or REJECT.

    This layer is niche-agnostic.
    """
    target = target or {}

    resolver_confidence = _to_float(target.get("resolver_confidence"), 0.0)
    target_score = _to_float(target.get("target_score"), 0.0)
    auto_link_allowed = bool(target.get("auto_link_allowed"))

    competition = target.get("competition_intelligence") or {}
    competition_action = competition.get("competition_action")
    close_call = bool(competition.get("close_call"))

    weak_reason = str(target.get("weak_reason") or "").strip()
    resolver_reason = str(target.get("resolver_reason") or "").strip()

    entity = target.get("entity_intelligence") or {}
    entity_overlap_count = int(entity.get("entity_overlap_count") or 0)
    entity_overlap_ratio = _to_float(entity.get("entity_overlap_ratio"), 0.0)

    entity_terms = set(entity.get("entity_overlap_terms") or [])

    generic_bridge_terms = {
        "guide", "option", "options", "tips", "best", "top", "how",
        "what", "when", "where", "why", "home", "page", "article",
        "calculator", "tool", "tools", "basic", "basics", "overview",
    }

    meaningful_entity_terms = {
        t for t in entity_terms
        if str(t).lower() not in generic_bridge_terms
    }

    wrong_intent_terms = {
        "risk", "risks", "mistake", "mistakes", "myth", "myths",
        "error", "errors", "problem", "problems", "warning", "warnings",
        "danger", "dangers", "avoid", "failure", "failures",
    }

    target_text = str(target.get("title") or "") + " " + str(target.get("url") or "")
    target_terms = {
        t.strip().lower()
        for t in target_text.replace("-", " ").replace("/", " ").split()
        if t.strip()
    }

    wrong_intent_risk = bool(target_terms & wrong_intent_terms)

    false_positive_risk = (
        entity_overlap_count == 0
        or entity_overlap_ratio < 0.34
        or (
            entity_overlap_count < 3
            and len(meaningful_entity_terms) < 2
        )
        or wrong_intent_risk
    )

    reasons = []

    if target_score <= 0:
        return {
            "decision": "REJECT",
            "decision_confidence": "none",
            "decision_reason": "no_target_score",
            "decision_reasons": ["no_target_score"],
        }

    if weak_reason:
        reasons.append("weak_match_signal")

    if close_call:
        reasons.append("close_competition")

    if competition_action == "reject":
        reasons.append("competition_reject")

    if competition_action == "suggest_only":
        reasons.append("competition_suggest_only")

    if not auto_link_allowed:
        reasons.append("auto_link_not_allowed")

    if resolver_confidence >= minimum_auto_confidence:
        reasons.append("high_resolver_confidence")
    elif resolver_confidence >= minimum_suggest_confidence:
        reasons.append("medium_resolver_confidence")
    else:
        reasons.append("low_resolver_confidence")

    if false_positive_risk:
        reasons.append("false_positive_entity_risk")
        decision = "SUGGEST_ONLY" if resolver_confidence >= minimum_suggest_confidence else "REJECT"
        decision_confidence = "medium" if decision == "SUGGEST_ONLY" else "low"
        decision_reason = "entity_overlap_too_weak_for_autolink"
    elif competition_action == "reject" or weak_reason:
        decision = "REJECT"
        decision_confidence = "low"
        decision_reason = "unsafe_or_weak_match"
    elif (
        auto_link_allowed
        and not close_call
        and competition_action == "auto_link_allowed"
        and resolver_confidence >= minimum_auto_confidence
    ):
        decision = "AUTO_LINK"
        decision_confidence = "high"
        decision_reason = "high_confidence_clear_winner"
    elif resolver_confidence >= minimum_suggest_confidence:
        decision = "SUGGEST_ONLY"
        decision_confidence = "medium"
        decision_reason = "safe_suggestion_not_autolink"
    else:
        decision = "REJECT"
        decision_confidence = "low"
        decision_reason = "confidence_below_suggestion_threshold"

    return {
        "decision": decision,
        "decision_confidence": decision_confidence,
        "decision_reason": decision_reason,
        "decision_reasons": reasons,
        "resolver_confidence": round(resolver_confidence, 4),
        "target_score": round(target_score, 4),
        "auto_link_allowed": auto_link_allowed,
        "competition_action": competition_action,
        "close_call": close_call,
        "resolver_reason": resolver_reason,
    }


def explain_resolver_decision_intelligence_v1() -> Dict[str, Any]:
    return {
        "layer": "resolver_decision_intelligence_v1",
        "purpose": "Convert resolver confidence, competition risk, and safety signals into a final universal action.",
        "universal": True,
        "actions": ["AUTO_LINK", "SUGGEST_ONLY", "REJECT"],
        "uses": [
            "resolver confidence",
            "target score",
            "auto-link eligibility",
            "competition action",
            "close-call status",
            "weak match signals",
        ],
        "does_not_use": [
            "health terms",
            "finance terms",
            "legal terms",
            "industry-specific hardcoded rules",
        ],
    }
