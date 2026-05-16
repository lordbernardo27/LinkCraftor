from __future__ import annotations

import hashlib
import re
from typing import Any, Dict


def _clean_text(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def _word_count(text: str) -> int:
    return len([w for w in text.split(" ") if w.strip()])


def _normalize_reason(reason: Any) -> str:
    value = _clean_text(reason)

    if not value:
        return "unspecified_rejection_reason"

    value = re.sub(r"[^a-z0-9_]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")

    return value or "unspecified_rejection_reason"


def _infer_structure_type(candidate_text: str) -> str:
    count = _word_count(candidate_text)

    if count <= 0:
        return "empty_candidate"

    if count == 1:
        return "single_term_candidate"

    if count == 2:
        return "two_term_candidate"

    if 3 <= count <= 5:
        return "multi_term_candidate"

    return "extended_candidate_window"


def _infer_failure_category(rejection_reason: str) -> str:
    reason = _normalize_reason(rejection_reason)

    if "boundary" in reason:
        return "boundary_validity_failure"

    if "cohesion" in reason or "semantic" in reason:
        return "semantic_cohesion_failure"

    if "fragment" in reason:
        return "fragment_validity_failure"

    if "order" in reason or "reversed" in reason:
        return "term_order_validity_failure"

    if "noise" in reason or "generic" in reason:
        return "candidate_signal_failure"

    if "length" in reason or "window" in reason:
        return "candidate_window_failure"

    return "general_rejection_pattern"


def _infer_semantic_cohesion(rejection_reason: str) -> str:
    reason = _normalize_reason(rejection_reason)

    if "cohesion" in reason or "semantic" in reason:
        return "low"

    if "noise" in reason or "generic" in reason:
        return "low"

    return "undetermined"


def _infer_boundary_quality(rejection_reason: str) -> str:
    reason = _normalize_reason(rejection_reason)

    if "boundary" in reason:
        return "failed"

    if "leak" in reason:
        return "failed"

    return "undetermined"


def _infer_standalone_phrase_quality(rejection_reason: str) -> str:
    reason = _normalize_reason(rejection_reason)

    if "fragment" in reason:
        return "failed"

    if "standalone" in reason:
        return "failed"

    if "noise" in reason or "generic" in reason:
        return "low"

    return "undetermined"


def _pattern_id_from_parts(
    *,
    pipeline_stage: str,
    vertical: str,
    structure_type: str,
    failure_category: str,
    failure_reason: str,
) -> str:
    raw = "|".join([
        _clean_text(pipeline_stage),
        _clean_text(vertical),
        _clean_text(structure_type),
        _clean_text(failure_category),
        _clean_text(failure_reason),
    ])

    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]
    return f"rc2_{failure_category}_{digest}"


def build_rejection_pattern_signature(
    *,
    candidate: Any,
    rejection_reason: Any,
    pipeline_stage: str,
    vertical: str = "general",
) -> Dict[str, Any]:
    """
    Build a reusable RC2 rejection-pattern signature.

    Important:
    - The candidate text is used only to infer structure.
    - The candidate text is NOT returned as a rule.
    - Matching must use the pattern signature, not the exact phrase.
    """
    if isinstance(candidate, dict):
        candidate_text = _clean_text(
            candidate.get("phrase")
            or candidate.get("text")
            or candidate.get("candidate")
            or candidate.get("value")
            or ""
        )
    else:
        candidate_text = _clean_text(candidate)

    normalized_reason = _normalize_reason(rejection_reason)
    structure_type = _infer_structure_type(candidate_text)
    failure_category = _infer_failure_category(normalized_reason)
    semantic_cohesion = _infer_semantic_cohesion(normalized_reason)
    boundary_quality = _infer_boundary_quality(normalized_reason)
    standalone_phrase_quality = _infer_standalone_phrase_quality(normalized_reason)

    pattern_id = _pattern_id_from_parts(
        pipeline_stage=pipeline_stage,
        vertical=vertical,
        structure_type=structure_type,
        failure_category=failure_category,
        failure_reason=normalized_reason,
    )

    return {
        "pattern_id": pattern_id,
        "structure_type": structure_type,
        "failure_category": failure_category,
        "failure_reason": normalized_reason,
        "semantic_cohesion": semantic_cohesion,
        "boundary_quality": boundary_quality,
        "standalone_phrase_quality": standalone_phrase_quality,
        "vertical": _clean_text(vertical) or "general",
        "source_stage": _clean_text(pipeline_stage),
        "word_count_band": _word_count(candidate_text),
        "stores_exact_phrase_as_rule": False,
    }
