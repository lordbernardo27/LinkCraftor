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
        "medium": {"min": 10, "max": 20},
        "long": {"min": 20, "max": 35},
        "very_long": {"min": 35, "max": 60},
    }

    return ranges.get(article_length_class, {"min": 5, "max": 10})


def apply_highlight_density(
    *,
    article_text: str,
    selected_candidates: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Apply highlight density rules to already-ranked selected candidates.

    This is intentionally minimal in Step 1.
    """
    word_count = count_article_words(article_text)
    article_length_class = classify_article_length(word_count)
    density_range = get_density_range(article_length_class)
    candidates = selected_candidates or []
    max_allowed = density_range["max"]
    final_highlights = candidates[:max_allowed]

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
        "density_reason": "quality_first_candidates_capped_by_article_length",
    },
}