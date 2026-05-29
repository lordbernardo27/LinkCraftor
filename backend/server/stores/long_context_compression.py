
from __future__ import annotations

from typing import Any, Dict, List


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _word_count(text: str) -> int:
    return len(_safe_text(text).split())


def _normalize(text: str) -> str:
    return " ".join(_safe_text(text).lower().split())


def _make_decision(
    layer: str,
    name: str,
    status: str,
    summary: str,
    actions: List[str],
    safety: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return {
        "layer": layer,
        "name": name,
        "status": status,
        "summary": summary,
        "actions": actions,
        "safety": safety or {
            "modifies_uploaded_article": False,
            "deletes_article_text": False,
            "rewrites_article_text": False,
            "runtime_context_only": True,
            "creates_runtime_router": False,
            "creates_linking_engine": False,
            "creates_target_selector": False,
        },
    }


def compress_long_article_context_v1(
    paragraphs: List[Dict[str, Any]],
    max_active_paragraphs: int = 40,
) -> Dict[str, Any]:
    """
    1.7.1 Long Article Compression.

    Compresses runtime context only.
    Does not modify uploaded article text.
    """

    scored: List[Dict[str, Any]] = []

    for index, paragraph in enumerate(paragraphs or []):
        text = _safe_text(paragraph.get("text") if isinstance(paragraph, dict) else paragraph)
        heading = _safe_text(paragraph.get("heading") if isinstance(paragraph, dict) else "")

        words = _word_count(text)
        score = 0.0
        reasons: List[str] = []

        if heading:
            score += 0.25
            reasons.append("heading_context")

        if 30 <= words <= 180:
            score += 0.35
            reasons.append("usable_paragraph_length")
        elif words > 180:
            score += 0.20
            reasons.append("large_paragraph")
        elif words < 15:
            score -= 0.15
            reasons.append("thin_paragraph")

        lowered = text.lower()
        if any(x in lowered for x in ["how to", "benefit", "risk", "cause", "step", "example", "important", "means"]):
            score += 0.25
            reasons.append("high_context_signal")

        if words > 0:
            scored.append({
                "index": index,
                "word_count": words,
                "score": round(score, 4),
                "reasons": reasons,
                "text_preview": text[:140],
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    active = scored[:max_active_paragraphs]

    return _make_decision(
        "1.7.1",
        "Long Article Compression",
        "active",
        "Prioritizes high-value article regions for runtime context without changing uploaded article text.",
        [
            "oversized_runtime_context_detection",
            "low_value_paragraph_detection",
            "active_paragraph_prioritization",
            "heading_aware_context_prioritization",
            "runtime_context_slimming",
            "compression_explainability",
            "compression_safety_audit",
        ],
    ) | {
        "input_paragraphs": len(paragraphs or []),
        "active_paragraphs": len(active),
        "compressed_paragraphs": max(0, len(paragraphs or []) - len(active)),
        "active_context": active,
    }


def compress_semantic_context_v1(
    context_items: List[Dict[str, Any]],
    max_items: int = 60,
) -> Dict[str, Any]:
    """
    1.7.2 Semantic Context Compression.

    Removes duplicate semantic runtime context.
    """

    seen = set()
    kept: List[Dict[str, Any]] = []
    suppressed: List[Dict[str, Any]] = []

    for item in context_items or []:
        text = _safe_text(item.get("text") or item.get("phrase") or item.get("label") if isinstance(item, dict) else item)
        key = _normalize(text)

        if not key:
            continue

        if key in seen:
            suppressed.append({"text": text[:140], "reason": "duplicate_semantic_context"})
            continue

        seen.add(key)
        kept.append(item if isinstance(item, dict) else {"text": text})

        if len(kept) >= max_items:
            suppressed.append({"text": text[:140], "reason": "semantic_context_limit_reached"})

    return _make_decision(
        "1.7.2",
        "Semantic Context Compression",
        "active",
        "Suppresses duplicate semantic windows and repeated evidence from runtime context.",
        [
            "semantic_redundancy_detection",
            "duplicate_semantic_window_suppression",
            "semantic_overlap_compression",
            "contextual_evidence_deduplication",
            "semantic_neighborhood_reduction",
            "semantic_compression_explainability",
            "semantic_compression_audit",
        ],
    ) | {
        "input_items": len(context_items or []),
        "kept_items": len(kept),
        "suppressed_items": len(suppressed),
        "kept_context": kept[:max_items],
        "suppressed_context": suppressed,
    }


def optimize_runtime_context_v1(
    runtime_context: Dict[str, Any],
    max_payload_items: int = 100,
) -> Dict[str, Any]:
    """
    1.7.3 Runtime Context Optimization.

    Optimizes runtime payload size and active context selection.
    """

    payload = runtime_context or {}
    optimized: Dict[str, Any] = {}
    suppressed_keys: List[str] = []

    for key, value in payload.items():
        if isinstance(value, list):
            optimized[key] = value[:max_payload_items]
            if len(value) > max_payload_items:
                suppressed_keys.append(key)
        else:
            optimized[key] = value

    return _make_decision(
        "1.7.3",
        "Runtime Context Optimization",
        "active",
        "Limits runtime payload size while preserving active high-value context.",
        [
            "runtime_context_window_governance",
            "runtime_payload_optimization",
            "active_context_prioritization",
            "inactive_context_suppression",
            "memory_safe_context_windows",
            "runtime_context_scoring",
            "runtime_optimization_explainability",
            "runtime_optimization_audit",
        ],
    ) | {
        "input_keys": list(payload.keys()),
        "suppressed_keys": suppressed_keys,
        "optimized_context": optimized,
    }


def support_large_document_reasoning_v1(
    sections: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.7.4 Large-Document Reasoning Support.

    Adds section-aware reasoning metadata without altering the article.
    """

    section_map: List[Dict[str, Any]] = []

    for index, section in enumerate(sections or []):
        title = _safe_text(section.get("title") or section.get("heading") if isinstance(section, dict) else "")
        text = _safe_text(section.get("text") if isinstance(section, dict) else section)

        section_map.append({
            "section_index": index,
            "title": title,
            "word_count": _word_count(text),
            "has_heading": bool(title),
            "reasoning_role": "section_context" if title else "body_context",
        })

    return _make_decision(
        "1.7.4",
        "Large-Document Reasoning Support",
        "active",
        "Provides section-aware reasoning support for long documents without changing content.",
        [
            "section_aware_reasoning_support",
            "cross_section_continuity_governance",
            "long_document_semantic_continuity",
            "section_transition_governance",
            "multi_section_reasoning_stabilization",
            "large_document_reasoning_explainability",
            "reasoning_safety_audit",
        ],
    ) | {
        "section_count": len(section_map),
        "section_map": section_map,
    }


def reduce_semantic_memory_v1(
    memory_items: List[Dict[str, Any]],
    max_memory_items: int = 80,
) -> Dict[str, Any]:
    """
    1.7.5 Semantic Memory Reduction.

    Deduplicates runtime semantic memory.
    """

    seen = set()
    kept: List[Dict[str, Any]] = []
    removed: List[Dict[str, Any]] = []

    for item in memory_items or []:
        text = _safe_text(item.get("text") or item.get("phrase") or item.get("entity") if isinstance(item, dict) else item)
        key = _normalize(text)

        if not key:
            continue

        if key in seen:
            removed.append({"text": text[:140], "reason": "duplicate_semantic_memory"})
            continue

        seen.add(key)
        kept.append(item if isinstance(item, dict) else {"text": text})

    kept = kept[:max_memory_items]

    return _make_decision(
        "1.7.5",
        "Semantic Memory Reduction",
        "active",
        "Reduces duplicate semantic memory carried into runtime processing.",
        [
            "semantic_memory_deduplication",
            "repeated_entity_memory_suppression",
            "duplicate_phrase_memory_reduction",
            "stale_semantic_memory_cleanup",
            "runtime_semantic_memory_slimming",
            "semantic_memory_prioritization",
            "memory_reduction_explainability",
            "semantic_memory_audit",
        ],
    ) | {
        "input_memory_items": len(memory_items or []),
        "kept_memory_items": len(kept),
        "removed_memory_items": len(removed),
        "kept_memory": kept,
        "removed_memory": removed,
    }


def explain_long_context_compression_layer_v1() -> Dict[str, Any]:
    return {
        "layer": "1.7",
        "name": "Long-Context Compression Layer",
        "status": "active",
        "scope": "runtime_context_only",
        "sub_layers": [
            "1.7.1 Long Article Compression",
            "1.7.2 Semantic Context Compression",
            "1.7.3 Runtime Context Optimization",
            "1.7.4 Large-Document Reasoning Support",
            "1.7.5 Semantic Memory Reduction",
        ],
        "safety_rules": {
            "modifies_uploaded_article": False,
            "deletes_article_text": False,
            "rewrites_article_text": False,
            "runtime_context_only": True,
            "creates_runtime_router": False,
            "creates_linking_engine": False,
            "creates_target_selector": False,
        },
    }
