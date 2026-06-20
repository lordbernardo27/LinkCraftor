from __future__ import annotations

from typing import Any, Dict, List


def build_explainability_v1(
    *,
    phrase_evidence_value: float = 0.0,
    intent_score: float = 0.0,
    concept_alignment_value: float = 0.0,
    entity_intelligence: Dict[str, Any] | None = None,
    topic_authority_intelligence: Dict[str, Any] | None = None,
    competition_intelligence: Dict[str, Any] | None = None,
    decision_intelligence: Dict[str, Any] | None = None,
) -> Dict[str, Any]:

    reasons: List[str] = []
    strengths: List[str] = []

    entity_intelligence = entity_intelligence or {}
    topic_authority_intelligence = topic_authority_intelligence or {}
    competition_intelligence = competition_intelligence or {}
    decision_intelligence = decision_intelligence or {}

    if phrase_evidence_value >= 0.60:
        reasons.append("high_phrase_evidence")
        strengths.append("phrase_evidence")

    if intent_score >= 0.60:
        reasons.append("high_intent_alignment")
        strengths.append("intent")

    if concept_alignment_value >= 0.60:
        reasons.append("high_concept_alignment")
        strengths.append("concept_alignment")

    if entity_intelligence.get("entity_confidence") in {"high", "medium"}:
        reasons.append("entity_overlap_detected")
        strengths.append("entities")

    if topic_authority_intelligence.get("topic_authority_level") in {"high", "medium"}:
        reasons.append("authoritative_target")
        strengths.append("authority")

    if not competition_intelligence.get("close_call"):
        reasons.append("clear_competition_winner")
        strengths.append("competition")

    decision = decision_intelligence.get("decision")
    if decision:
        reasons.append(f"decision_{str(decision).lower()}")

    summary = ", ".join(reasons[:5]) if reasons else "limited_supporting_signals"

    return {
        "has_explainability": True,
        "summary": summary,
        "reasons": reasons,
        "strengths": strengths,
        "decision": decision,
    }


def explain_explainability_v1() -> Dict[str, Any]:
    return {
        "layer": "resolver_explainability_v1",
        "purpose": "Generate universal explanations describing why a target was selected.",
        "universal": True,
        "uses": [
            "phrase evidence",
            "intent alignment",
            "concept alignment",
            "entity overlap",
            "topic authority",
            "competition analysis",
            "decision intelligence",
        ],
        "does_not_use": [
            "health rules",
            "finance rules",
            "legal rules",
            "industry-specific hardcoding",
        ],
    }
