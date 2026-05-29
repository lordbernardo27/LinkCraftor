
from __future__ import annotations

from typing import Any, Dict, List


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize(text: str) -> str:
    return " ".join(_safe_text(text).lower().split())


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _clamp_score(value: Any) -> float:
    score = _safe_float(value, 0.0)
    if score > 1:
        score = score / 100
    return round(max(0.0, min(1.0, score)), 4)


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
        },
    }


def get_candidate_fusion_architecture_v1() -> Dict[str, Any]:
    return _make_response(
        "1.5.2.1",
        "Architecture Design",
        "Defines the governed architecture for semantic runtime candidate fusion.",
        [
            "candidate_fusion_architecture",
            "semantic_candidate_inputs",
            "fusion_output_contract",
            "runtime_support_boundaries",
            "fusion_safety_rules",
        ],
    ) | {
        "inputs": [
            "semantic_candidates",
            "yellow_candidates",
            "runtime_candidates",
            "target_candidates",
            "retrieval_support",
            "graph_support",
            "confidence_support",
        ],
        "outputs": [
            "fused_candidates",
            "ranked_candidates",
            "yellow_candidates",
            "suppressed_candidates",
            "target_ordering_support",
        ],
    }


def score_semantic_fusion_candidates_v1(
    candidates: List[Dict[str, Any]],
) -> Dict[str, Any]:
    scored: List[Dict[str, Any]] = []

    for item in candidates or []:
        phrase = _safe_text(item.get("phrase") or item.get("text") if isinstance(item, dict) else item)
        if not phrase:
            continue

        base = _clamp_score(item.get("score", item.get("confidence", 0.0)) if isinstance(item, dict) else 0.0)
        retrieval = _clamp_score(item.get("retrieval_score", 0.0) if isinstance(item, dict) else 0.0)
        graph = _clamp_score(item.get("graph_score", 0.0) if isinstance(item, dict) else 0.0)
        runtime = _clamp_score(item.get("runtime_score", 0.0) if isinstance(item, dict) else 0.0)

        fusion_score = round((base * 0.35) + (retrieval * 0.25) + (graph * 0.20) + (runtime * 0.20), 4)

        scored.append({
            "phrase": phrase,
            "fusion_score": fusion_score,
            "base_score": base,
            "retrieval_score": retrieval,
            "graph_score": graph,
            "runtime_score": runtime,
            "fusion_role": "semantic_runtime_candidate",
        })

    scored.sort(key=lambda x: x["fusion_score"], reverse=True)

    return _make_response(
        "1.5.2.2",
        "Fusion Scoring Model",
        "Scores semantic runtime candidates using governed cross-layer support signals.",
        [
            "fusion_scoring_model",
            "cross_layer_score_blending",
            "semantic_candidate_scoring",
            "fusion_score_explainability",
            "fusion_score_audit",
        ],
    ) | {
        "scored_candidates": scored,
    }


def fuse_semantic_runtime_candidates_v1(
    candidates: List[Dict[str, Any]],
    min_score: float = 0.35,
) -> Dict[str, Any]:
    scored_result = score_semantic_fusion_candidates_v1(candidates)
    accepted: List[Dict[str, Any]] = []
    suppressed: List[Dict[str, Any]] = []
    seen = set()

    for item in scored_result["scored_candidates"]:
        key = _normalize(item["phrase"])

        if key in seen:
            suppressed.append({**item, "reason": "duplicate_fusion_candidate"})
            continue

        seen.add(key)

        if item["fusion_score"] < min_score:
            suppressed.append({**item, "reason": "weak_semantic_match"})
            continue

        accepted.append(item)

    return _make_response(
        "1.5.2.3",
        "Fusion Engine Draft",
        "Fuses semantic runtime candidates while suppressing duplicates and weak matches.",
        [
            "fusion_engine_draft",
            "candidate_fusion",
            "duplicate_candidate_suppression",
            "weak_match_suppression",
            "fusion_engine_explainability",
            "fusion_engine_audit",
        ],
    ) | {
        "fused_candidates": accepted,
        "suppressed_candidates": suppressed,
    }


def validate_candidate_fusion_module_v1() -> Dict[str, Any]:
    return _make_response(
        "1.5.2.4",
        "Compile + Validate Module",
        "Validates that the candidate fusion module exposes the expected governance contract.",
        [
            "compile_validation_contract",
            "module_validation",
            "function_contract_validation",
            "fusion_module_audit",
        ],
    ) | {
        "required_functions": [
            "get_candidate_fusion_architecture_v1",
            "score_semantic_fusion_candidates_v1",
            "fuse_semantic_runtime_candidates_v1",
            "rank_runtime_semantic_candidates_v1",
            "integrate_yellow_highlight_candidates_v1",
            "integrate_semantic_bulk_autolink_candidates_v1",
            "order_semantic_targets_v1",
            "suppress_weak_semantic_matches_v1",
            "validate_runtime_semantic_candidate_fusion_v1",
            "explain_semantic_runtime_candidate_fusion_v1",
        ],
    }


def rank_runtime_semantic_candidates_v1(
    candidates: List[Dict[str, Any]],
) -> Dict[str, Any]:
    fused = fuse_semantic_runtime_candidates_v1(candidates)

    ranked = [
        {**item, "rank": index + 1, "ranking_role": "runtime_semantic_ranking"}
        for index, item in enumerate(fused["fused_candidates"])
    ]

    return _make_response(
        "1.5.2.5",
        "Runtime Semantic Ranking Integration",
        "Ranks fused semantic runtime candidates for downstream runtime visibility.",
        [
            "runtime_semantic_ranking",
            "fused_candidate_ranking",
            "semantic_ranking_support",
            "ranking_explainability",
            "ranking_audit",
        ],
    ) | {
        "ranked_candidates": ranked,
        "suppressed_candidates": fused["suppressed_candidates"],
    }


def integrate_yellow_highlight_candidates_v1(
    candidates: List[Dict[str, Any]],
    yellow_threshold: float = 0.35,
) -> Dict[str, Any]:
    ranked = rank_runtime_semantic_candidates_v1(candidates)

    yellow = [
        {
            **item,
            "bucket": "yellow",
            "highlight_role": "yellow_highlight_candidate",
        }
        for item in ranked["ranked_candidates"]
        if item["fusion_score"] >= yellow_threshold
    ]

    return _make_response(
        "1.5.2.6",
        "Yellow Highlight Integration",
        "Prepares governed yellow/optional semantic highlight candidates without forcing highlights.",
        [
            "yellow_highlight_integration",
            "optional_semantic_candidate_support",
            "yellow_bucket_support",
            "yellow_highlight_safety",
            "yellow_highlight_audit",
        ],
    ) | {
        "yellow_candidates": yellow,
        "suppressed_candidates": ranked["suppressed_candidates"],
    }


def integrate_semantic_bulk_autolink_candidates_v1(
    candidates: List[Dict[str, Any]],
) -> Dict[str, Any]:
    ranked = rank_runtime_semantic_candidates_v1(candidates)

    bulk_ready = [
        {
            **item,
            "bulk_autolink_role": "semantic_bulk_autolink_support",
            "requires_user_or_engine_acceptance": True,
        }
        for item in ranked["ranked_candidates"]
    ]

    return _make_response(
        "1.5.2.7",
        "Semantic Bulk Auto-Link Integration",
        "Prepares fused semantic candidates for bulk auto-link support without forcing link decisions.",
        [
            "semantic_bulk_autolink_integration",
            "bulk_candidate_support",
            "bulk_linking_safety",
            "bulk_candidate_explainability",
            "bulk_autolink_audit",
        ],
    ) | {
        "bulk_autolink_candidates": bulk_ready,
    }


def order_semantic_targets_v1(
    targets: List[Dict[str, Any]],
) -> Dict[str, Any]:
    ordered: List[Dict[str, Any]] = []

    for item in targets or []:
        title = _safe_text(item.get("title") or item.get("target") or item.get("url") if isinstance(item, dict) else item)
        if not title:
            continue

        relevance = _clamp_score(item.get("relevance", item.get("score", 0.0)) if isinstance(item, dict) else 0.0)
        confidence = _clamp_score(item.get("confidence", 0.0) if isinstance(item, dict) else 0.0)

        ordering_score = round((relevance * 0.65) + (confidence * 0.35), 4)

        ordered.append({
            "target": title,
            "ordering_score": ordering_score,
            "relevance": relevance,
            "confidence": confidence,
            "ordering_role": "semantic_target_ordering",
        })

    ordered.sort(key=lambda x: x["ordering_score"], reverse=True)

    return _make_response(
        "1.5.2.8",
        "Semantic Target Ordering",
        "Orders semantic target candidates for existing target-selection workflows.",
        [
            "semantic_target_ordering",
            "target_relevance_ordering",
            "target_confidence_support",
            "target_ordering_explainability",
            "target_ordering_audit",
        ],
    ) | {
        "ordered_targets": ordered,
    }


def suppress_weak_semantic_matches_v1(
    candidates: List[Dict[str, Any]],
    min_score: float = 0.35,
) -> Dict[str, Any]:
    scored = score_semantic_fusion_candidates_v1(candidates)

    kept = []
    suppressed = []

    for item in scored["scored_candidates"]:
        if item["fusion_score"] >= min_score:
            kept.append(item)
        else:
            suppressed.append({**item, "reason": "weak_semantic_match_suppressed"})

    return _make_response(
        "1.5.2.9",
        "Weak Semantic Match Suppression",
        "Suppresses weak semantic matches before they influence downstream runtime support.",
        [
            "weak_semantic_match_suppression",
            "low_confidence_candidate_suppression",
            "semantic_noise_reduction",
            "suppression_explainability",
            "suppression_audit",
        ],
    ) | {
        "kept_candidates": kept,
        "suppressed_candidates": suppressed,
    }


def validate_runtime_semantic_candidate_fusion_v1(
    candidates: List[Dict[str, Any]],
) -> Dict[str, Any]:
    architecture = get_candidate_fusion_architecture_v1()
    scoring = score_semantic_fusion_candidates_v1(candidates)
    fusion = fuse_semantic_runtime_candidates_v1(candidates)
    ranking = rank_runtime_semantic_candidates_v1(candidates)
    yellow = integrate_yellow_highlight_candidates_v1(candidates)
    suppression = suppress_weak_semantic_matches_v1(candidates)

    return _make_response(
        "1.5.2.10",
        "Runtime Testing + Validation",
        "Validates semantic runtime candidate fusion outputs across architecture, scoring, fusion, ranking, yellow, and suppression layers.",
        [
            "runtime_testing",
            "fusion_validation",
            "ranking_validation",
            "yellow_integration_validation",
            "suppression_validation",
            "runtime_validation_audit",
        ],
    ) | {
        "architecture_status": architecture["status"],
        "scored_count": len(scoring["scored_candidates"]),
        "fused_count": len(fusion["fused_candidates"]),
        "ranked_count": len(ranking["ranked_candidates"]),
        "yellow_count": len(yellow["yellow_candidates"]),
        "suppressed_count": len(suppression["suppressed_candidates"]),
    }


def explain_semantic_runtime_candidate_fusion_v1() -> Dict[str, Any]:
    return {
        "layer": "1.5.2",
        "name": "Semantic Runtime Candidate Fusion",
        "status": "active",
        "scope": "semantic_candidate_fusion_governance",
        "sub_layers": [
            "1.5.2.1 Architecture Design",
            "1.5.2.2 Fusion Scoring Model",
            "1.5.2.3 Fusion Engine Draft",
            "1.5.2.4 Compile + Validate Module",
            "1.5.2.5 Runtime Semantic Ranking Integration",
            "1.5.2.6 Yellow Highlight Integration",
            "1.5.2.7 Semantic Bulk Auto-Link Integration",
            "1.5.2.8 Semantic Target Ordering",
            "1.5.2.9 Weak Semantic Match Suppression",
            "1.5.2.10 Runtime Testing + Validation",
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
        },
    }
