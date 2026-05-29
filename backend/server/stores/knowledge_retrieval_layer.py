
from __future__ import annotations

from typing import Any, Dict, List


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize(text: str) -> str:
    return " ".join(_safe_text(text).lower().split())


def _score_text(text: str) -> float:
    text = _safe_text(text)

    score = 0.0

    words = len(text.split())

    if 2 <= words <= 12:
        score += 0.25

    if any(
        x in text.lower()
        for x in [
            "how",
            "why",
            "cause",
            "effect",
            "benefit",
            "risk",
            "guide",
            "method",
            "strategy",
            "optimization",
        ]
    ):
        score += 0.35

    if len(text) > 40:
        score += 0.20

    return round(score, 4)


def _make_response(
    layer: str,
    name: str,
    summary: str,
    actions: List[str],
) -> Dict[str, Any]:
    return {
        "layer": layer,
        "name": name,
        "status": "active",
        "summary": summary,
        "actions": actions,
        "safety": {
            "retrieval_only": True,
            "runtime_support_only": True,
            "does_not_modify_uploaded_article": True,
            "does_not_create_runtime_router": True,
            "does_not_create_new_linking_engine": True,
            "does_not_replace_existing_scoring": True,
        },
    }


def retrieve_semantic_support_v1(
    candidates: List[Dict[str, Any]],
    max_results: int = 25,
) -> Dict[str, Any]:
    """
    1.8.1 Retrieval-Based Semantic Support.
    """

    scored: List[Dict[str, Any]] = []

    for item in candidates or []:
        text = _safe_text(
            item.get("text")
            or item.get("phrase")
            or item.get("label")
            if isinstance(item, dict)
            else item
        )

        if not text:
            continue

        score = _score_text(text)

        scored.append({
            "text": text,
            "support_score": score,
            "retrieval_reason": "semantic_support",
        })

    scored.sort(key=lambda x: x["support_score"], reverse=True)

    return _make_response(
        "1.8.1",
        "Retrieval-Based Semantic Support",
        "Retrieves high-value semantic support context for runtime reasoning.",
        [
            "semantic_support_retrieval",
            "semantic_support_prioritization",
            "semantic_support_governance",
            "support_retrieval_explainability",
            "support_retrieval_safety_audit",
        ],
    ) | {
        "results": scored[:max_results],
    }


def retrieve_runtime_knowledge_v1(
    runtime_context: List[Dict[str, Any]],
    max_results: int = 40,
) -> Dict[str, Any]:
    """
    1.8.2 Runtime Knowledge Retrieval.
    """

    active: List[Dict[str, Any]] = []

    for item in runtime_context or []:
        text = _safe_text(
            item.get("text")
            or item.get("phrase")
            if isinstance(item, dict)
            else item
        )

        if not text:
            continue

        active.append({
            "text": text,
            "runtime_score": _score_text(text),
            "retrieval_role": "runtime_context",
        })

    active.sort(key=lambda x: x["runtime_score"], reverse=True)

    return _make_response(
        "1.8.2",
        "Runtime Knowledge Retrieval",
        "Retrieves active runtime knowledge context for semantic processing.",
        [
            "runtime_knowledge_retrieval",
            "active_runtime_retrieval_windows",
            "runtime_retrieval_prioritization",
            "runtime_retrieval_optimization",
            "runtime_retrieval_explainability",
            "runtime_retrieval_safety_audit",
        ],
    ) | {
        "results": active[:max_results],
    }


def retrieve_semantic_evidence_v1(
    evidence_items: List[Dict[str, Any]],
    max_results: int = 30,
) -> Dict[str, Any]:
    """
    1.8.3 Semantic Evidence Retrieval.
    """

    seen = set()
    evidence: List[Dict[str, Any]] = []

    for item in evidence_items or []:
        text = _safe_text(
            item.get("text")
            or item.get("evidence")
            or item.get("phrase")
            if isinstance(item, dict)
            else item
        )

        key = _normalize(text)

        if not key or key in seen:
            continue

        seen.add(key)

        evidence.append({
            "evidence": text,
            "evidence_score": _score_text(text),
            "evidence_role": "semantic_evidence",
        })

    evidence.sort(key=lambda x: x["evidence_score"], reverse=True)

    return _make_response(
        "1.8.3",
        "Semantic Evidence Retrieval",
        "Retrieves semantic evidence for runtime support and explainability.",
        [
            "semantic_evidence_retrieval",
            "evidence_confidence_governance",
            "duplicate_evidence_suppression",
            "cross_document_evidence_retrieval",
            "evidence_explainability",
            "evidence_safety_audit",
        ],
    ) | {
        "results": evidence[:max_results],
    }


def score_retrieved_knowledge_v1(
    retrieved_items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.8.4 Retrieval Scoring Engine.
    """

    scored: List[Dict[str, Any]] = []

    for item in retrieved_items or []:
        text = _safe_text(
            item.get("text")
            or item.get("evidence")
            or item.get("phrase")
            if isinstance(item, dict)
            else item
        )

        score = _score_text(text)

        scored.append({
            "text": text,
            "retrieval_relevance_score": score,
            "retrieval_confidence_score": round(min(1.0, score + 0.2), 4),
        })

    scored.sort(
        key=lambda x: (
            x["retrieval_relevance_score"],
            x["retrieval_confidence_score"],
        ),
        reverse=True,
    )

    return _make_response(
        "1.8.4",
        "Retrieval Scoring Engine",
        "Scores retrieved runtime knowledge and semantic evidence.",
        [
            "retrieval_relevance_scoring",
            "retrieval_confidence_scoring",
            "semantic_evidence_scoring",
            "cross_source_retrieval_scoring",
            "retrieval_ranking_governance",
            "retrieval_scoring_explainability",
            "retrieval_scoring_audit",
        ],
    ) | {
        "results": scored,
    }


def assist_linking_with_retrieval_v1(
    link_candidates: List[Dict[str, Any]],
    max_results: int = 25,
) -> Dict[str, Any]:
    """
    1.8.5 Retrieval-Assisted Linking.
    """

    assisted: List[Dict[str, Any]] = []

    for item in link_candidates or []:
        text = _safe_text(
            item.get("text")
            or item.get("phrase")
            if isinstance(item, dict)
            else item
        )

        if not text:
            continue

        assisted.append({
            "text": text,
            "retrieval_support_score": _score_text(text),
            "linking_support_role": "retrieval_assisted_linking",
        })

    assisted.sort(
        key=lambda x: x["retrieval_support_score"],
        reverse=True,
    )

    return _make_response(
        "1.8.5",
        "Retrieval-Assisted Linking",
        "Provides retrieval-assisted support for semantic linking workflows.",
        [
            "retrieval_assisted_semantic_linking",
            "retrieval_assisted_target_support",
            "retrieval_assisted_contextual_transitions",
            "retrieval_assisted_evidence_validation",
            "retrieval_assisted_relevance_support",
            "retrieval_assisted_linking_explainability",
            "retrieval_assisted_linking_audit",
        ],
    ) | {
        "results": assisted[:max_results],
    }


def explain_knowledge_retrieval_layer_v1() -> Dict[str, Any]:
    return {
        "layer": "1.8",
        "name": "Knowledge Retrieval Layer",
        "status": "active",
        "scope": "retrieval_governance",
        "sub_layers": [
            "1.8.1 Retrieval-Based Semantic Support",
            "1.8.2 Runtime Knowledge Retrieval",
            "1.8.3 Semantic Evidence Retrieval",
            "1.8.4 Retrieval Scoring Engine",
            "1.8.5 Retrieval-Assisted Linking",
        ],
        "safety_rules": {
            "retrieval_only": True,
            "runtime_support_only": True,
            "does_not_modify_uploaded_article": True,
            "does_not_create_runtime_router": True,
            "does_not_create_new_linking_engine": True,
            "does_not_replace_existing_scoring": True,
        },
    }
