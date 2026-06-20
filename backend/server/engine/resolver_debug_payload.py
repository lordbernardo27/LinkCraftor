from __future__ import annotations

from typing import Any, Dict


def build_resolver_debug_payload_v1(result: Dict[str, Any]) -> Dict[str, Any]:
    result = result or {}

    score_calibration = result.get("score_calibration") or {}
    decision = result.get("decision_intelligence") or {}
    competition = result.get("competition_intelligence") or {}
    entity = result.get("entity_intelligence") or {}
    authority = result.get("topic_authority_intelligence") or {}
    explainability = result.get("explainability") or {}
    learning_booster = result.get("learning_booster_signal") or {}

    return {
        "has_resolver_debug": True,
        "phrase": result.get("phrase"),
        "url": result.get("url"),
        "title": result.get("title"),
        "target_score": result.get("target_score"),
        "resolver_decision": result.get("resolver_decision"),
        "auto_link_allowed": result.get("auto_link_allowed"),

        "learning": {
            "has_learning_signal": bool(learning_booster),
            "learning_adjustment_applied": result.get("learning_adjustment_applied"),
            "phrase_signal_found": learning_booster.get("phrase_signal_found"),
            "target_signal_found": learning_booster.get("target_signal_found"),
            "phrase_boost": learning_booster.get("phrase_boost"),
            "phrase_penalty": learning_booster.get("phrase_penalty"),
            "target_boost": learning_booster.get("target_boost"),
            "target_penalty": learning_booster.get("target_penalty"),
            "positive_adjustment": learning_booster.get("positive_adjustment"),
            "negative_adjustment": learning_booster.get("negative_adjustment"),
            "net_learning_adjustment": learning_booster.get("net_learning_adjustment"),
            "evidence_total": learning_booster.get("evidence_total"),
            "evidence_multiplier": learning_booster.get("evidence_multiplier"),
            "min_events_for_full_effect": learning_booster.get("min_events_for_full_effect"),
            "base_score": learning_booster.get("base_score"),
            "adjusted_score": learning_booster.get("adjusted_score"),
        },

        "confidence": {
            "calibrated_confidence": score_calibration.get("calibrated_confidence"),
            "confidence_band": score_calibration.get("confidence_band"),
            "normalized_score": score_calibration.get("normalized_score"),
        },

        "decision": {
            "decision": decision.get("decision"),
            "decision_confidence": decision.get("decision_confidence"),
            "decision_reason": decision.get("decision_reason"),
            "decision_reasons": decision.get("decision_reasons"),
        },

        "competition": {
            "close_call": competition.get("close_call"),
            "score_margin": competition.get("score_margin"),
            "competition_confidence": competition.get("competition_confidence"),
            "competition_action": competition.get("competition_action"),
            "competition_reason": competition.get("competition_reason"),
        },

        "entity": {
            "overlap_terms": entity.get("entity_overlap_terms"),
            "overlap_count": entity.get("entity_overlap_count"),
            "overlap_ratio": entity.get("entity_overlap_ratio"),
            "entity_confidence": entity.get("entity_confidence"),
        },

        "authority": {
            "topic_authority_score": authority.get("topic_authority_score"),
            "topic_authority_level": authority.get("topic_authority_level"),
            "topic_authority_reasons": authority.get("topic_authority_reasons"),
        },

        "explainability": {
            "summary": explainability.get("summary"),
            "reasons": explainability.get("reasons"),
            "strengths": explainability.get("strengths"),
        },
    }


def explain_resolver_debug_payload_v1() -> Dict[str, Any]:
    return {
        "layer": "resolver_debug_payload_v1",
        "purpose": "Provide clean resolver debugging fields for UI and Owner Console.",
        "universal": True,
        "includes_learning_visibility": True,
    }
