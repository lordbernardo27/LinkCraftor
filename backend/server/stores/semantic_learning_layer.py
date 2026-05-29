
from __future__ import annotations

from typing import Any, Dict, List


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize(text: str) -> str:
    return " ".join(_safe_text(text).lower().split())


def _make_response(layer: str, name: str, summary: str, actions: List[str]) -> Dict[str, Any]:
    return {
        "layer": layer,
        "name": name,
        "status": "active",
        "summary": summary,
        "actions": actions,
        "safety": {
            "governance_only": True,
            "runtime_support_only": True,
            "does_not_modify_uploaded_article": True,
            "does_not_create_runtime_router": True,
            "does_not_create_new_target_selector": True,
            "does_not_replace_existing_scoring": True,
            "does_not_force_link_decisions": True,
            "does_not_force_highlights": True,
            "pattern_level_learning_only": True,
            "does_not_store_exact_phrase_as_rule": True,
        },
    }


def learn_semantic_dis_patterns_v1(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    learned = []

    for item in events or []:
        event_type = _safe_text(item.get("event_type", "semantic_decision") if isinstance(item, dict) else "semantic_decision")
        pattern = _safe_text(item.get("pattern") or item.get("signature") or item.get("reason") if isinstance(item, dict) else item)

        if not pattern:
            continue

        learned.append({
            "event_type": event_type,
            "pattern_signature": _normalize(pattern),
            "learning_role": "semantic_dis_learning",
            "stores_pattern_only": True,
        })

    return _make_response(
        "1.14.1",
        "Semantic DIS Learning",
        "Learns governed semantic decision patterns without changing runtime decisions.",
        [
            "dis_semantic_learning_support",
            "semantic_decision_learning_records",
            "semantic_pattern_learning_governance",
            "dis_learning_safety_rules",
        ],
    ) | {
        "learned_patterns": learned,
    }


def learn_semantic_rejections_v1(rejections: List[Dict[str, Any]]) -> Dict[str, Any]:
    learned = []

    for item in rejections or []:
        reason = _safe_text(item.get("reason") or item.get("rejection_reason") if isinstance(item, dict) else item)
        stage = _safe_text(item.get("stage", "semantic_runtime") if isinstance(item, dict) else "semantic_runtime")

        if not reason:
            continue

        learned.append({
            "stage": stage,
            "rejection_reason": reason,
            "pattern_signature": _normalize(reason),
            "learning_role": "semantic_rejection_learning",
            "stores_pattern_only": True,
        })

    return _make_response(
        "1.14.2",
        "Semantic Rejection Learning",
        "Learns semantic rejection patterns and rejection reasons safely.",
        [
            "semantic_rejection_learning",
            "rejection_reason_tracking",
            "rejected_pattern_governance",
            "rejection_learning_audit",
        ],
    ) | {
        "learned_rejections": learned,
    }


def learn_semantic_successes_v1(successes: List[Dict[str, Any]]) -> Dict[str, Any]:
    learned = []

    for item in successes or []:
        signal = _safe_text(item.get("signal") or item.get("success_signal") or item.get("reason") if isinstance(item, dict) else item)
        source = _safe_text(item.get("source", "semantic_runtime") if isinstance(item, dict) else "semantic_runtime")

        if not signal:
            continue

        learned.append({
            "source": source,
            "success_signal": signal,
            "pattern_signature": _normalize(signal),
            "learning_role": "semantic_success_learning",
            "stores_pattern_only": True,
        })

    return _make_response(
        "1.14.3",
        "Semantic Success Learning",
        "Learns semantic success patterns from accepted or successful support signals.",
        [
            "semantic_success_learning",
            "accepted_success_signal_tracking",
            "success_pattern_governance",
            "success_learning_audit",
        ],
    ) | {
        "learned_successes": learned,
    }


def learn_semantic_false_positives_v1(false_positives: List[Dict[str, Any]]) -> Dict[str, Any]:
    learned = []

    for item in false_positives or []:
        reason = _safe_text(item.get("reason") or item.get("false_positive_reason") if isinstance(item, dict) else item)
        source = _safe_text(item.get("source", "semantic_runtime") if isinstance(item, dict) else "semantic_runtime")

        if not reason:
            continue

        learned.append({
            "source": source,
            "false_positive_reason": reason,
            "pattern_signature": _normalize(reason),
            "learning_role": "semantic_false_positive_learning",
            "suppression_support_only": True,
        })

    return _make_response(
        "1.14.4",
        "Semantic False-Positive Learning",
        "Learns semantic false-positive patterns for future suppression support.",
        [
            "false_positive_learning",
            "false_positive_reason_tracking",
            "false_positive_suppression_support",
            "false_positive_audit",
        ],
    ) | {
        "learned_false_positives": learned,
    }


def learn_semantic_density_patterns_v1(density_events: List[Dict[str, Any]]) -> Dict[str, Any]:
    learned = []

    for item in density_events or []:
        density_signal = _safe_text(item.get("density_signal") or item.get("signal") or item.get("reason") if isinstance(item, dict) else item)
        density_type = _safe_text(item.get("density_type", "semantic_density") if isinstance(item, dict) else "semantic_density")

        if not density_signal:
            continue

        learned.append({
            "density_type": density_type,
            "density_signal": density_signal,
            "pattern_signature": _normalize(density_signal),
            "learning_role": "semantic_density_learning",
            "density_support_only": True,
        })

    return _make_response(
        "1.14.5",
        "Semantic Density Learning",
        "Learns semantic density patterns from highlight/link density signals.",
        [
            "semantic_density_learning",
            "highlight_link_density_signal_tracking",
            "density_pattern_governance",
            "density_learning_audit",
        ],
    ) | {
        "learned_density_patterns": learned,
    }


def explain_semantic_learning_layer_v1() -> Dict[str, Any]:
    return {
        "layer": "1.14",
        "name": "Semantic Learning Layer",
        "status": "active",
        "scope": "semantic_learning_governance",
        "sub_layers": [
            "1.14.1 Semantic DIS Learning",
            "1.14.2 Semantic Rejection Learning",
            "1.14.3 Semantic Success Learning",
            "1.14.4 Semantic False-Positive Learning",
            "1.14.5 Semantic Density Learning",
        ],
        "safety_rules": {
            "governance_only": True,
            "runtime_support_only": True,
            "does_not_modify_uploaded_article": True,
            "does_not_create_runtime_router": True,
            "does_not_create_new_target_selector": True,
            "does_not_replace_existing_scoring": True,
            "does_not_force_link_decisions": True,
            "does_not_force_highlights": True,
            "pattern_level_learning_only": True,
            "does_not_store_exact_phrase_as_rule": True,
        },
    }
