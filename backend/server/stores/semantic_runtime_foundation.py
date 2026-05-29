
from __future__ import annotations

from typing import Any, Dict, List


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize(text: str) -> str:
    return " ".join(_safe_text(text).lower().split())


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
            "governance_only": True,
            "runtime_support_only": True,
            "does_not_modify_uploaded_article": True,
            "does_not_create_runtime_router": True,
            "does_not_create_new_target_selector": True,
            "does_not_replace_existing_scoring": True,
            "does_not_force_link_decisions": True,
        },
    }


def establish_semantic_runtime_foundations_v1(
    runtime_items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.5.1.1 Semantic Runtime Foundations.
    """

    foundations: List[Dict[str, Any]] = []

    for item in runtime_items or []:
        text = _safe_text(item.get("text") or item.get("phrase") or item.get("topic") if isinstance(item, dict) else item)

        if not text:
            continue

        foundations.append({
            "text": text,
            "normalized": _normalize(text),
            "runtime_role": "semantic_runtime_foundation",
        })

    return _make_response(
        "1.5.1.1",
        "Semantic Runtime Foundations",
        "Provides governed semantic runtime foundation metadata without changing runtime routing.",
        [
            "semantic_runtime_foundations",
            "runtime_semantic_metadata_support",
            "runtime_semantic_normalization",
            "semantic_runtime_governance",
            "semantic_runtime_explainability",
            "semantic_runtime_audit",
        ],
    ) | {
        "semantic_runtime_foundations": foundations,
    }


def establish_semantic_highlight_foundations_v1(
    highlights: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.5.1.2 Semantic Highlight Foundations.
    """

    governed: List[Dict[str, Any]] = []

    for item in highlights or []:
        phrase = _safe_text(item.get("phrase") or item.get("text") if isinstance(item, dict) else item)
        bucket = _safe_text(item.get("bucket", "semantic") if isinstance(item, dict) else "semantic")

        if not phrase:
            continue

        governed.append({
            "phrase": phrase,
            "bucket": bucket,
            "highlight_role": "semantic_highlight_foundation",
        })

    return _make_response(
        "1.5.1.2",
        "Semantic Highlight Foundations",
        "Provides semantic highlight foundation support without painting or forcing highlights.",
        [
            "semantic_highlight_foundations",
            "highlight_bucket_support",
            "highlight_metadata_governance",
            "semantic_highlight_explainability",
            "highlight_foundation_audit",
        ],
    ) | {
        "semantic_highlight_foundations": governed,
    }


def register_semantic_runtime_hooks_v1(
    hooks: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.5.1.3 Semantic Runtime Hooks.
    """

    registered: List[Dict[str, Any]] = []

    for hook in hooks or []:
        name = _safe_text(hook.get("name") or hook.get("hook") if isinstance(hook, dict) else hook)
        hook_type = _safe_text(hook.get("type", "runtime_support") if isinstance(hook, dict) else "runtime_support")

        if not name:
            continue

        registered.append({
            "hook": name,
            "type": hook_type,
            "hook_role": "semantic_runtime_hook",
            "active": True,
        })

    return _make_response(
        "1.5.1.3",
        "Semantic Runtime Hooks",
        "Registers semantic runtime hook metadata without creating a new runtime engine.",
        [
            "semantic_runtime_hooks",
            "runtime_hook_metadata",
            "semantic_hook_governance",
            "runtime_hook_explainability",
            "runtime_hook_audit",
        ],
    ) | {
        "semantic_runtime_hooks": registered,
    }


def support_semantic_match_infrastructure_v1(
    matches: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.5.1.4 Semantic Match Infrastructure.
    """

    supported: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    seen = set()

    for match in matches or []:
        source = _safe_text(match.get("source") or match.get("phrase") if isinstance(match, dict) else match)
        target = _safe_text(match.get("target") or match.get("candidate") if isinstance(match, dict) else "")

        if not source:
            continue

        key = (_normalize(source), _normalize(target))

        if key in seen:
            rejected.append({
                "source": source,
                "target": target,
                "reason": "duplicate_semantic_match",
            })
            continue

        seen.add(key)

        supported.append({
            "source": source,
            "target": target,
            "match_role": "semantic_match_infrastructure",
        })

    return _make_response(
        "1.5.1.4",
        "Semantic Match Infrastructure",
        "Supports semantic match infrastructure without replacing existing scoring or selection.",
        [
            "semantic_match_infrastructure",
            "semantic_candidate_support",
            "semantic_match_deduplication",
            "match_governance",
            "semantic_match_explainability",
            "semantic_match_audit",
        ],
    ) | {
        "supported_matches": supported,
        "rejected_matches": rejected,
    }


def establish_yellow_highlight_foundations_v1(
    candidates: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.5.1.5 Yellow Highlight Foundations.
    """

    yellow: List[Dict[str, Any]] = []

    for item in candidates or []:
        phrase = _safe_text(item.get("phrase") or item.get("text") if isinstance(item, dict) else item)
        reason = _safe_text(item.get("reason", "semantic_optional_candidate") if isinstance(item, dict) else "semantic_optional_candidate")

        if not phrase:
            continue

        yellow.append({
            "phrase": phrase,
            "bucket": "yellow",
            "reason": reason,
            "highlight_role": "yellow_highlight_foundation",
        })

    return _make_response(
        "1.5.1.5",
        "Yellow Highlight Foundations",
        "Defines governed yellow/optional semantic highlight foundations without forcing highlights.",
        [
            "yellow_highlight_foundations",
            "optional_semantic_candidate_support",
            "yellow_bucket_governance",
            "yellow_highlight_explainability",
            "yellow_highlight_audit",
        ],
    ) | {
        "yellow_highlight_foundations": yellow,
    }


def explain_semantic_runtime_foundation_v1() -> Dict[str, Any]:
    return {
        "layer": "1.5.1",
        "name": "Semantic Runtime Foundation",
        "status": "active",
        "scope": "semantic_runtime_governance",
        "sub_layers": [
            "1.5.1.1 Semantic Runtime Foundations",
            "1.5.1.2 Semantic Highlight Foundations",
            "1.5.1.3 Semantic Runtime Hooks",
            "1.5.1.4 Semantic Match Infrastructure",
            "1.5.1.5 Yellow Highlight Foundations",
        ],
        "safety_rules": {
            "governance_only": True,
            "runtime_support_only": True,
            "does_not_modify_uploaded_article": True,
            "does_not_create_runtime_router": True,
            "does_not_create_new_target_selector": True,
            "does_not_replace_existing_scoring": True,
            "does_not_force_link_decisions": True,
        },
    }
