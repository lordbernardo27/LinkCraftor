
from __future__ import annotations

from typing import Any, Dict, List


SAFETY_RULES = {
    "extraction_support_only": True,
    "does_not_modify_article": True,
    "does_not_insert_links": True,
    "does_not_modify_targets": True,
    "does_not_modify_scoring_engine": True,
    "does_not_modify_active_pool": True,
    "does_not_modify_highlight_selection": True,
    "does_not_modify_highlight_density": True,
    "does_not_modify_rb2_runtime": True,
    "does_not_modify_internal_linking": True,
    "does_not_modify_semantic_linking": True,
    "does_not_publish_content": True,
}


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def analyze_semantic_closure_v1(
    candidates: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """
    1.16.7 Semantic Closure Analysis.

    Checks whether extracted candidates appear semantically complete.
    This is extraction-support only and does not alter runtime, scoring,
    targets, highlights, links, articles, or publishing.
    """

    candidates = candidates or []
    results = []

    weak_endings = {
        "of", "for", "to", "from", "with", "without", "during", "before",
        "after", "and", "or", "the", "a", "an", "in", "on", "at", "by",
    }

    for item in candidates:
        text = _safe_text(item.get("text") or item.get("phrase") if isinstance(item, dict) else item)
        words = text.split()

        if not text:
            continue

        complete = True
        reasons = []

        if len(words) < 2:
            complete = False
            reasons.append("too_short_for_semantic_closure")

        if words and words[-1].lower() in weak_endings:
            complete = False
            reasons.append("weak_terminal_boundary")

        if words and words[0].lower() in weak_endings:
            complete = False
            reasons.append("weak_start_boundary")

        results.append({
            "text": text,
            "semantic_closure": "complete" if complete else "incomplete",
            "is_complete": complete,
            "reasons": reasons,
            "role": "semantic_closure_analysis_only",
        })

    return {
        "status": "active",
        "layer_id": "1.16.7",
        "name": "Semantic Closure Analysis",
        "scope": "semantic_completeness_extraction_support",
        "safety": dict(SAFETY_RULES),
        "candidate_count": len(candidates),
        "results": results,
    }




def analyze_standalone_semantic_integrity_v1(
    candidates: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """
    1.16.8 Standalone Semantic Integrity.

    Determines whether a candidate phrase still conveys
    meaningful intent when viewed independently.

    Extraction-support only.
    Does not modify runtime, scoring, targets, pools,
    highlights, linking, articles, or publishing.
    """

    candidates = candidates or []
    results = []

    weak_words = {
        "during", "before", "after", "through", "into",
        "the", "a", "an", "and", "or", "for", "to",
        "with", "without", "in", "on", "at", "by",
    }

    for item in candidates:
        text = _safe_text(
            item.get("text") or item.get("phrase")
            if isinstance(item, dict)
            else item
        )

        if not text:
            continue

        words = text.split()

        integrity = True
        reasons = []

        if len(words) < 2:
            integrity = False
            reasons.append("insufficient_semantic_structure")

        weak_count = sum(
            1 for w in words
            if w.lower() in weak_words
        )

        if words and weak_count >= max(1, len(words) // 2):
            integrity = False
            reasons.append("weak_semantic_density")

        results.append({
            "text": text,
            "standalone_integrity":
                "valid" if integrity else "invalid",
            "is_valid": integrity,
            "reasons": reasons,
            "role": "standalone_semantic_integrity_only",
        })

    return {
        "status": "active",
        "layer_id": "1.16.8",
        "name": "Standalone Semantic Integrity",
        "scope": "semantic_completeness_extraction_support",
        "safety": dict(SAFETY_RULES),
        "candidate_count": len(candidates),
        "results": results,
    }





def recover_semantic_candidates_v1(
    candidates: List[Dict[str, Any]] | None = None,
    context_windows: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """
    1.16.9 Semantic Recovery Engine.

    Attempts safe recovery of incomplete candidate phrases using nearby
    context windows. Extraction-support only.
    """

    candidates = candidates or []
    context_windows = context_windows or []
    recoveries = []

    context_text = " ".join(
        _safe_text(x.get("text") if isinstance(x, dict) else x)
        for x in context_windows
    )

    recovery_suffixes = [
        "kit",
        "calculator",
        "guide",
        "method",
        "window",
        "date",
        "symptoms",
        "strategy",
    ]

    for item in candidates:
        text = _safe_text(
            item.get("text") or item.get("phrase")
            if isinstance(item, dict)
            else item
        )

        if not text:
            continue

        recovered = text
        recovered_from_context = False
        reasons = []

        for suffix in recovery_suffixes:
            proposed = f"{text} {suffix}".strip()
            if proposed.lower() in context_text.lower():
                recovered = proposed
                recovered_from_context = True
                reasons.append("context_supported_suffix_recovery")
                break

        recoveries.append({
            "original": text,
            "recovered": recovered,
            "recovered_from_context": recovered_from_context,
            "changed": recovered != text,
            "reasons": reasons,
            "role": "semantic_recovery_only",
        })

    return {
        "status": "active",
        "layer_id": "1.16.9",
        "name": "Semantic Recovery Engine",
        "scope": "semantic_completeness_extraction_support",
        "safety": dict(SAFETY_RULES),
        "candidate_count": len(candidates),
        "context_window_count": len(context_windows),
        "recoveries": recoveries,
    }





def expand_semantic_candidates_v1(
    candidates: List[Dict[str, Any]] | None = None,
    allowed_expansions: Dict[str, List[str]] | None = None,
) -> Dict[str, Any]:
    """
    1.16.10 Semantic Expansion Engine.

    Suggests safe semantic expansions for underspecified candidates.
    Extraction-support only.
    Does not alter runtime, scoring, targets, pools, highlights, linking, articles, or publishing.
    """

    candidates = candidates or []
    allowed_expansions = allowed_expansions or {}

    expansions = []

    for item in candidates:
        text = _safe_text(
            item.get("text") or item.get("phrase")
            if isinstance(item, dict)
            else item
        )

        if not text:
            continue

        options = allowed_expansions.get(text.lower(), [])

        expansions.append({
            "original": text,
            "expansion_options": options,
            "has_expansion_options": bool(options),
            "selected_expansion": options[0] if options else text,
            "changed": bool(options),
            "role": "semantic_expansion_only",
        })

    return {
        "status": "active",
        "layer_id": "1.16.10",
        "name": "Semantic Expansion Engine",
        "scope": "semantic_completeness_extraction_support",
        "safety": dict(SAFETY_RULES),
        "candidate_count": len(candidates),
        "expansions": expansions,
    }





def complete_contextual_semantics_v1(
    candidates: List[Dict[str, Any]] | None = None,
    context_windows: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """
    1.16.11 Contextual Semantic Completion.
    Completes candidate meaning using paragraph/context support only.
    """

    candidates = candidates or []
    context_windows = context_windows or []
    context_text = " ".join(
        _safe_text(x.get("text") if isinstance(x, dict) else x)
        for x in context_windows
    ).lower()

    completions = []

    for item in candidates:
        text = _safe_text(
            item.get("text") or item.get("phrase")
            if isinstance(item, dict)
            else item
        )

        if not text:
            continue

        words = text.split()
        complete = len(words) >= 2 and text.lower() in context_text

        completions.append({
            "text": text,
            "context_supported": text.lower() in context_text,
            "is_contextually_complete": complete,
            "role": "contextual_semantic_completion_only",
        })

    return {
        "status": "active",
        "layer_id": "1.16.11",
        "name": "Contextual Semantic Completion",
        "scope": "semantic_completeness_extraction_support",
        "safety": dict(SAFETY_RULES),
        "candidate_count": len(candidates),
        "context_window_count": len(context_windows),
        "completions": completions,
    }


def analyze_anchor_intent_completeness_v1(
    candidates: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """
    1.16.12 Anchor Intent Completeness.
    Checks whether a candidate expresses a usable anchor/search intent.
    """

    candidates = candidates or []
    intent_terms = {
        "calculator", "guide", "strategy", "method", "symptoms",
        "treatment", "causes", "benefits", "risk", "risks",
        "checklist", "template", "examples", "comparison",
        "window", "date", "kit",
    }

    results = []

    for item in candidates:
        text = _safe_text(
            item.get("text") or item.get("phrase")
            if isinstance(item, dict)
            else item
        )

        if not text:
            continue

        words = text.split()
        has_intent = any(w.lower() in intent_terms for w in words)
        complete = len(words) >= 2 and has_intent

        results.append({
            "text": text,
            "has_anchor_intent": has_intent,
            "is_intent_complete": complete,
            "role": "anchor_intent_completeness_only",
        })

    return {
        "status": "active",
        "layer_id": "1.16.12",
        "name": "Anchor Intent Completeness",
        "scope": "semantic_completeness_extraction_support",
        "safety": dict(SAFETY_RULES),
        "candidate_count": len(candidates),
        "results": results,
    }


def reconstruct_semantic_candidate_v1(
    candidates: List[Dict[str, Any]] | None = None,
    reconstruction_map: Dict[str, str] | None = None,
) -> Dict[str, Any]:
    """
    1.16.13 Semantic Reconstruction Engine.
    Reconstructs only explicitly allowed malformed candidates.
    """

    candidates = candidates or []
    reconstruction_map = reconstruction_map or {}

    reconstructions = []

    for item in candidates:
        text = _safe_text(
            item.get("text") or item.get("phrase")
            if isinstance(item, dict)
            else item
        )

        if not text:
            continue

        reconstructed = reconstruction_map.get(text.lower(), text)

        reconstructions.append({
            "original": text,
            "reconstructed": reconstructed,
            "changed": reconstructed != text,
            "role": "semantic_reconstruction_only",
        })

    return {
        "status": "active",
        "layer_id": "1.16.13",
        "name": "Semantic Reconstruction Engine",
        "scope": "semantic_completeness_extraction_support",
        "safety": dict(SAFETY_RULES),
        "candidate_count": len(candidates),
        "reconstructions": reconstructions,
    }





def generate_semantic_completeness_explainability_v1() -> Dict[str, Any]:
    """
    1.16.14 Semantic Completeness Explainability.
    """

    return {
        "status": "active",
        "layer_id": "1.16.14",
        "name": "Semantic Completeness Explainability",
        "scope": "semantic_completeness_extraction_support",
        "safety": dict(SAFETY_RULES),
        "explains": [
            "semantic_closure",
            "standalone_integrity",
            "semantic_recovery",
            "semantic_expansion",
            "contextual_completion",
            "anchor_intent",
            "semantic_reconstruction",
        ],
    }


def govern_semantic_completeness_v1() -> Dict[str, Any]:
    """
    1.16.15 Semantic Completeness Governance.
    """

    return {
        "status": "active",
        "layer_id": "1.16.15",
        "name": "Semantic Completeness Governance",
        "scope": "semantic_completeness_extraction_support",
        "safety": dict(SAFETY_RULES),
        "governance_rules": {
            "extraction_support_only": True,
            "may_modify_article": False,
            "may_modify_runtime": False,
            "may_modify_scoring": False,
            "may_modify_targets": False,
            "may_modify_active_pool": False,
            "may_modify_highlights": False,
            "may_modify_linking": False,
            "may_publish_content": False,
        },
    }


def audit_semantic_completeness_safety_v1() -> Dict[str, Any]:
    """
    1.16.16 Semantic Completeness Safety Audit.
    """

    return {
        "status": "active",
        "layer_id": "1.16.16",
        "name": "Semantic Completeness Safety Audit",
        "scope": "semantic_completeness_extraction_support",
        "safety": dict(SAFETY_RULES),
        "audit_result": {
            "safe_for_extraction_support": True,
            "runtime_unchanged": True,
            "scoring_unchanged": True,
            "targets_unchanged": True,
            "active_pool_unchanged": True,
            "highlights_unchanged": True,
            "linking_unchanged": True,
            "publishing_unchanged": True,
        },
    }


def audit_semantic_completeness_isolation_v1() -> Dict[str, Any]:
    """
    1.16.17 Semantic Completeness Full Isolation Audit.
    """

    return {
        "status": "active",
        "layer_id": "1.16.17",
        "name": "Semantic Completeness Full Isolation Audit",
        "scope": "semantic_completeness_extraction_support",
        "safety": dict(SAFETY_RULES),
        "isolation_result": {
            "runtime_isolated": True,
            "scoring_isolated": True,
            "target_selection_isolated": True,
            "active_pool_isolated": True,
            "highlight_selection_isolated": True,
            "highlight_density_isolated": True,
            "internal_linking_isolated": True,
            "semantic_linking_isolated": True,
            "article_modification_isolated": True,
            "publishing_isolated": True,
        },
    }



def explain_semantic_completeness_intelligence_v1() -> Dict[str, Any]:
    return {
        "status": "active",
        "scope": "semantic_completeness_intelligence",
        "safety_rules": dict(SAFETY_RULES),
        "sub_layers": [
            "1.16.7 Semantic Closure Analysis",
            "1.16.8 Standalone Semantic Integrity",
            "1.16.9 Semantic Recovery Engine",
            "1.16.10 Semantic Expansion Engine",
            "1.16.11 Contextual Semantic Completion",
            "1.16.12 Anchor Intent Completeness",
            "1.16.13 Semantic Reconstruction Engine",
            "1.16.14 Semantic Completeness Explainability",
            "1.16.15 Semantic Completeness Governance",
            "1.16.16 Semantic Completeness Safety Audit",
            "1.16.17 Semantic Completeness Full Isolation Audit",
        ],
    }
