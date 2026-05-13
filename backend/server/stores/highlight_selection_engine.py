"""
Highlight Selection Engine v1

Purpose:
Select and rank phrase candidates from the document-isolated active phrase pool
before the density engine decides how many highlights should appear.

C.5.3 responsibility:
- Normalize phrase candidates
- Confirm phrase exists in the active article
- Reject weak/noisy candidates
- Rank surviving phrases by quality, relevance, and link opportunity

C.5.3 does NOT:
- Decide final highlight count
- Apply density limits
- Paint highlights in the editor
- Insert links
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple


def normalize_phrase(text: Any) -> str:
    """
    Normalize a phrase for comparison and deduplication.
    """
    s = str(text or "").strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"^[\"'“”‘’\(\[\{]+|[\"'“”‘’\)\]\}:;,\.\!\?]+$", "", s)
    return s.strip()


def extract_phrase_candidates(active_phrase_pool: Any) -> List[Dict[str, Any]]:
    """
    Extract phrase candidates from possible active phrase pool shapes.

    Supported shapes:
    - {"phrases": {"phrase text": {...}}}
    - {"phrases": [{...}, {...}]}
    - {"items": [{...}, {...}]}
    - direct list of phrase dicts
    """
    candidates: List[Dict[str, Any]] = []

    if not active_phrase_pool:
        return candidates

    raw_phrases = None

    if isinstance(active_phrase_pool, dict):
        raw_phrases = (
            active_phrase_pool.get("phrases")
            or active_phrase_pool.get("items")
            or active_phrase_pool.get("candidates")
        )
    elif isinstance(active_phrase_pool, list):
        raw_phrases = active_phrase_pool

    if isinstance(raw_phrases, dict):
        iterable = raw_phrases.items()
        for phrase_key, payload in iterable:
            if isinstance(payload, dict):
                item = dict(payload)
                item.setdefault("phrase", phrase_key)
                candidates.append(item)
            else:
                candidates.append({"phrase": phrase_key, "value": payload})

    elif isinstance(raw_phrases, list):
        for payload in raw_phrases:
            if isinstance(payload, dict):
                candidates.append(dict(payload))
            elif isinstance(payload, str):
                candidates.append({"phrase": payload})

    return candidates

def normalize_and_dedupe_candidates(
    candidates: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Normalize phrase text and remove duplicates.

    Returns:
    - unique normalized candidates
    - rejected duplicate/empty candidates
    """
    seen = set()
    unique: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []

    for item in candidates:
        raw_phrase = (
            item.get("phrase")
            or item.get("text")
            or item.get("phrase_text")
            or item.get("label")
        )

        phrase = normalize_phrase(raw_phrase)

        if not phrase:
            rejected.append({
                "phrase": str(raw_phrase or ""),
                "reason": "rejected_empty_phrase",
                "item": item,
            })
            continue

        if phrase in seen:
            rejected.append({
                "phrase": phrase,
                "reason": "rejected_duplicate",
                "item": item,
            })
            continue

        seen.add(phrase)

        cleaned = dict(item)
        cleaned["phrase"] = phrase
        cleaned["raw_phrase"] = raw_phrase
        unique.append(cleaned)

    return unique, rejected

def phrase_exists_in_article(phrase: str, article_text: str) -> bool:
    """
    Confirm phrase appears naturally in the article using word-boundary matching.
    """
    if not phrase or not article_text:
        return False

    pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
    return re.search(pattern, article_text.lower()) is not None

WEAK_SINGLE_WORDS = {
    "and", "or", "the", "a", "an", "to", "of", "in", "on", "for", "with",
    "from", "by", "as", "at", "is", "are", "was", "were", "be", "being",
    "been", "this", "that", "these", "those", "it", "its",
}

WEAK_PHRASE_PATTERNS = [
    r"\bderail many plans\b",
    r"\bdrop dead day\b",
    r"\blater with calculator\b",
    r"\btimeline for healthy care\b",
    r"\baren for due date\b",
]


def weak_phrase_reason(phrase: str) -> str:
    """
    Return rejection reason if phrase is weak/noisy.
    Return empty string if phrase is acceptable.
    """
    if not phrase:
        return "rejected_empty_phrase"

    words = phrase.split()

    if len(words) == 1 and phrase in WEAK_SINGLE_WORDS:
        return "rejected_too_generic"

    if len(words) > 8:
        return "rejected_too_long"

    if len(words) == 1 and len(phrase) < 4:
        return "rejected_too_short"

    for pattern in WEAK_PHRASE_PATTERNS:
        if re.search(pattern, phrase):
            return "rejected_known_noisy_phrase"

    stop_count = sum(1 for w in words if w in WEAK_SINGLE_WORDS)
    if len(words) >= 3 and stop_count / max(len(words), 1) > 0.6:
        return "rejected_stopword_heavy"

    return ""

def score_anchor_quality(phrase: str) -> int:
    """
    Score how good the phrase is as anchor text.
    Higher = better.
    """
    words = phrase.split()
    score = 0

    if 2 <= len(words) <= 6:
        score += 30
    elif len(words) == 1:
        score += 8
    elif 7 <= len(words) <= 8:
        score += 15

    if len(phrase) >= 8:
        score += 10

    if any(w in phrase for w in [
        "calculator", "guide", "symptom", "symptoms", "treatment",
        "medication", "medicine", "pregnancy", "ovulation", "bmi",
        "blood pressure", "due date", "fertile window",
    ]):
        score += 25

    stop_count = sum(1 for w in words if w in WEAK_SINGLE_WORDS)
    if words:
        stop_ratio = stop_count / len(words)
        if stop_ratio <= 0.25:
            score += 15
        elif stop_ratio <= 0.4:
            score += 5

    return score

def count_phrase_occurrences(phrase: str, article_text: str) -> int:
    """
    Count natural phrase occurrences in article text.
    """
    if not phrase or not article_text:
        return 0

    pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
    return len(re.findall(pattern, article_text.lower()))


def score_article_relevance(phrase: str, article_text: str) -> int:
    """
    Score phrase relevance based on natural occurrence frequency.
    """
    count = count_phrase_occurrences(phrase, article_text)

    if count <= 0:
        return 0

    if count == 1:
        return 15

    if 2 <= count <= 3:
        return 25

    return 30

def score_link_opportunity(phrase: str) -> int:
    """
    Score whether a phrase is useful for internal linking.
    """
    score = 0

    high_value_terms = [
        "calculator", "guide", "symptom", "symptoms", "treatment",
        "medication", "medicine", "pregnancy", "ovulation", "bmi",
        "blood pressure", "due date", "fertile window", "gestational age",
        "basal body temperature", "side effects", "dosage", "causes",
        "risk", "risks", "normal range",
    ]

    for term in high_value_terms:
        if term in phrase:
            score += 20
            break

    if 2 <= len(phrase.split()) <= 5:
        score += 10

    return score

def remove_overlapping_candidates(
    ranked_candidates: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Remove weaker overlapping phrases after ranking.
    Keeps the higher-ranked phrase.
    """
    kept: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []

    kept_phrases: List[str] = []

    for item in ranked_candidates:
        phrase = item.get("phrase", "")

        overlaps_existing = any(
            phrase in kept_phrase or kept_phrase in phrase
            for kept_phrase in kept_phrases
        )

        if overlaps_existing:
            rejected.append({
                "phrase": phrase,
                "reason": "rejected_duplicate_overlap",
                "item": item,
            })
            continue

        kept.append(item)
        kept_phrases.append(phrase)

    return kept, rejected

def select_highlight_candidates(
    *,
    workspace_id: str,
    doc_id: str,
    article_text: str,
    active_phrase_pool: Any,
) -> Dict[str, Any]:
    """
    Select and rank highlight candidates from the active phrase pool.

    This is intentionally minimal in Step 1.
    The scoring/rejection logic will be added in the next steps.
    """
    candidates = extract_phrase_candidates(active_phrase_pool)
    unique_candidates, rejected = normalize_and_dedupe_candidates(candidates)

    article_matched: List[Dict[str, Any]] = []

    for item in unique_candidates:
        phrase = item.get("phrase", "")

        if not phrase_exists_in_article(phrase, article_text):
            rejected.append({
                "phrase": phrase,
                "reason": "rejected_not_in_article",
                "item": item,
            })
            continue

        weak_reason = weak_phrase_reason(phrase)
        if weak_reason:
            rejected.append({
                "phrase": phrase,
                "reason": weak_reason,
                "item": item,
            })
            continue

        item["anchor_quality_score"] = score_anchor_quality(phrase)

        item["article_relevance_score"] = score_article_relevance(phrase, article_text)
        item["occurrence_count"] = count_phrase_occurrences(phrase, article_text)

        item["link_opportunity_score"] = score_link_opportunity(phrase)
        item["selection_score"] = (
            item["anchor_quality_score"]
            + item["article_relevance_score"]
            + item["link_opportunity_score"]
        )

        article_matched.append(item)

        item["selection_status"] = "selected_candidate"
        item["selection_reason"] = "selected_quality_relevance_link_opportunity"


        article_matched.sort(
        key=lambda x: (
            x.get("selection_score", 0),
            x.get("anchor_quality_score", 0),
            len(x.get("phrase", "")),
        ),
        reverse=True,
    )

    selected, overlap_rejected = remove_overlapping_candidates(article_matched)
    rejected.extend(overlap_rejected)

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "doc_id": doc_id,
        "selected": selected,
        "rejected": rejected,
        "stats": {
            "total_candidates": len(candidates),
            "unique_candidates": len(unique_candidates),
            "article_matched": len(article_matched),
            "selected_count": len(selected),
            "rejected_count": len(rejected),
        },
    }