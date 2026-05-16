"""
Highlight Density Engine v1

Purpose:
Decide how many selected phrase candidates should finally appear as highlights
based on article length, candidate quality, and safe link-density principles.

C.5.4 responsibility:
- Count article words
- Classify article length
- Set safe highlight range
- Apply final highlight limit to ranked candidates

C.5.4 does NOT:
- Choose phrase quality
- Reject noisy phrases
- Paint highlights
- Insert links
"""

from __future__ import annotations

import re
from typing import Any, Dict, List

from backend.server.stores.dis_rejection_pattern_store import get_rejection_pattern_knowledge


def count_article_words(article_text: str) -> int:
    """
    Count article words using a simple word-token pattern.
    """
    if not article_text:
        return 0

    return len(re.findall(r"\b\w+\b", article_text))

def classify_article_length(word_count: int) -> str:
    """
    Classify article length for highlight density control.
    """
    if word_count < 800:
        return "short"

    if word_count < 1500:
        return "medium"

    if word_count < 2500:
        return "long"

    return "very_long"

def get_density_range(article_length_class: str) -> Dict[str, int]:
    """
    Return safe min/max highlight range by article length.
    """
    ranges = {
        "short": {"min": 5, "max": 10},
        "medium": {"min": 10, "max": 18},
        "long": {"min": 18, "max": 32},
        "very_long": {"min": 18, "max": 50},
    }

    return ranges.get(article_length_class, {"min": 5, "max": 10})

def _balance_short_anchors(
    candidates: List[Dict[str, Any]],
    max_items: int,
    max_short_ratio: float = 0.40,
) -> List[Dict[str, Any]]:
    """
    Prevent ultra-short 2-word anchors from dominating final highlights.
    """
    if not candidates or max_items <= 0:
        return []

    max_short = max(1, int(max_items * max_short_ratio))

    short_kept = 0
    balanced: List[Dict[str, Any]] = []
    delayed_short: List[Dict[str, Any]] = []

    for item in candidates:
        phrase = str(item.get("phrase") or "")
        token_count = len(re.findall(r"\b\w+\b", phrase.lower()))

        if token_count <= 2:
            if short_kept < max_short:
                balanced.append(item)
                short_kept += 1
            else:
                delayed_short.append(item)
        else:
            balanced.append(item)

        if len(balanced) >= max_items:
            break

    if len(balanced) < max_items:
        balanced.extend(delayed_short[: max_items - len(balanced)])

    return balanced[:max_items]

def _balance_high_frequency_phrases(
    candidates: List[Dict[str, Any]],
    max_items: int,
    max_high_frequency_ratio: float = 0.35,
) -> List[Dict[str, Any]]:
    """
    Prevent phrases with high occurrence counts from dominating final highlights.
    Pattern-based balancing, not phrase-specific.
    """
    if not candidates or max_items <= 0:
        return []

    max_high_frequency = max(1, int(max_items * max_high_frequency_ratio))

    high_frequency_kept = 0
    balanced: List[Dict[str, Any]] = []
    delayed_high_frequency: List[Dict[str, Any]] = []

    for item in candidates:
        occurrence_count = int(item.get("occurrence_count") or 0)

        if occurrence_count >= 5:
            if high_frequency_kept < max_high_frequency:
                balanced.append(item)
                high_frequency_kept += 1
            else:
                delayed_high_frequency.append(item)
        else:
            balanced.append(item)

        if len(balanced) >= max_items:
            break

    if len(balanced) < max_items:
        balanced.extend(delayed_high_frequency[: max_items - len(balanced)])

    return balanced[:max_items]

def candidate_matches_density_rc2_pattern(
    phrase: str,
    rc2_patterns: List[Dict[str, Any]],
) -> Dict[str, Any]:
    normalized_phrase = str(phrase or "").strip().lower()
    word_count = len(re.findall(r"\b\w+\b", normalized_phrase))

    for pattern in rc2_patterns:
        latest_event = pattern.get("latest_event", {}) if isinstance(pattern, dict) else {}
        signature = latest_event.get("pattern_signature", {}) if isinstance(latest_event, dict) else {}

        if not isinstance(signature, dict):
            continue

        signature_word_count = int(signature.get("word_count_band") or 0)
        failure_category = str(signature.get("failure_category") or "")
        failure_reasons = pattern.get("failure_reasons", []) if isinstance(pattern, dict) else []

        if signature_word_count and signature_word_count != word_count:
            continue

        if failure_category in {
            "term_order_validity_failure",
            "fragment_validity_failure",
            "boundary_validity_failure",
            "candidate_signal_failure",
            "semantic_cohesion_failure",
            "candidate_window_failure",
            "general_rejection_pattern",
        }:
            return {
                "matched": True,
                "pattern_id": pattern.get("pattern_id"),
                "failure_category": failure_category,
                "failure_reasons": failure_reasons,
            }

    return {
        "matched": False,
        "pattern_id": "",
        "failure_category": "",
        "failure_reasons": [],
    }

def _apply_quality_floor(
    candidates: List[Dict[str, Any]],
    minimum_score: int = 80,
) -> List[Dict[str, Any]]:
    """
    Remove low-confidence runtime highlights.
    Pattern-based quality floor.
    """
    filtered: List[Dict[str, Any]] = []

    for item in candidates:
        score = int(item.get("selection_score") or 0)

        if score >= minimum_score:
            filtered.append(item)

    return filtered

def calculate_adaptive_density_limit(
    candidates: List[Dict[str, Any]],
    base_max: int,
) -> Dict[str, Any]:
    """
    Dynamically adjust highlight density based on runtime quality.
    Pattern-based adaptive density logic.
    """
    if not candidates:
        return {
            "adaptive_max": max(8, int(base_max * 0.5)),
            "quality_pressure_score": 0,
        }

    scores = [
        int(x.get("selection_score") or 0)
        for x in candidates
    ]

    avg_score = sum(scores) / max(len(scores), 1)

    strong_candidates = len([
        x for x in candidates
        if int(x.get("selection_score") or 0) >= 100
    ])

    long_phrases = len([
        x for x in candidates
        if len(str(x.get("phrase") or "").split()) >= 3
    ])

    diversity_ratio = long_phrases / max(len(candidates), 1)

    quality_pressure_score = (
        (avg_score * 0.45)
        + (strong_candidates * 0.35)
        + (diversity_ratio * 100 * 0.20)
    )

    multiplier = 1.0

    if quality_pressure_score >= 120:
        multiplier = 1.25
    elif quality_pressure_score >= 95:
        multiplier = 1.10
    elif quality_pressure_score < 70:
        multiplier = 0.75
    elif quality_pressure_score < 50:
        multiplier = 0.55

    adaptive_max = max(
        8,
        int(base_max * multiplier),
    )

    adaptive_max = min(
        adaptive_max,
        max(base_max + 12, 40),
    )

    return {
        "adaptive_max": adaptive_max,
        "quality_pressure_score": round(quality_pressure_score, 2),
        "average_selection_score": round(avg_score, 2),
        "strong_candidate_count": strong_candidates,
        "diversity_ratio": round(diversity_ratio, 2),
        "density_multiplier": multiplier,
    }

def apply_highlight_density(
    *,
    article_text: str,
    selected_candidates: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Apply highlight density rules to already-ranked selected candidates.
    """
    word_count = count_article_words(article_text)
    article_length_class = classify_article_length(word_count)
    density_range = get_density_range(article_length_class)

    vertical = "general"
    rc2_knowledge = get_rejection_pattern_knowledge("default", vertical)
    rc2_patterns = rc2_knowledge.get("patterns", []) if isinstance(rc2_knowledge, dict) else []

    candidates = selected_candidates or []
    base_max = density_range["max"]

    adaptive_density = calculate_adaptive_density_limit(
    selected_candidates,
    base_max=base_max,
)

    max_allowed = adaptive_density["adaptive_max"]

    quality_filtered = _apply_quality_floor(
        candidates,
        minimum_score=80,
    )

    length_balanced = _balance_short_anchors(
        quality_filtered,
        max_items=max_allowed,
        max_short_ratio=0.40,
    )

    density_rc2_filtered: List[Dict[str, Any]] = []
    density_rc2_advisory: List[Dict[str, Any]] = []

    for item in length_balanced:
        phrase = str(item.get("phrase") or "")
        rc2_match = candidate_matches_density_rc2_pattern(phrase, rc2_patterns)

        item["dis_density_checked"] = True
        item["dis_density_pattern_match"] = bool(rc2_match.get("matched"))
        item["removed_by_dis_pattern_knowledge"] = False
        item["dis_density_can_block"] = False
        item["dis_density_advisory_only"] = True
        item["final_density_quality_status"] = "passed_density_with_rc2_advisory"

        if rc2_match.get("matched"):
            density_rc2_advisory.append({
                "phrase": phrase,
                "reason": "density_rc2_advisory_signal",
                "rc2_failure_category": rc2_match.get("failure_category"),
                "rc2_failure_reasons": rc2_match.get("failure_reasons", []),
                "item": item,
            })

        density_rc2_filtered.append(item)

    final_highlights = _balance_high_frequency_phrases(
        density_rc2_filtered,
        max_items=max_allowed,
        max_high_frequency_ratio=0.35,
    )

    return {
        "ok": True,
        "final_highlights": final_highlights,
        "stats": {
            "article_word_count": word_count,
            "article_length_class": article_length_class,
            "available_candidates": len(candidates),
            "recommended_min": density_range["min"],
            "recommended_max": density_range["max"],
            "final_highlight_count": len(final_highlights),
            "rc2_patterns_loaded": len(rc2_patterns),
            "rc2_density_advisory_signals": len(density_rc2_advisory),
            "density_rc2_advisory": density_rc2_advisory,
            "adaptive_density": adaptive_density,
            "density_reason": "quality_first_candidates_capped_by_article_length",
        },
    }












