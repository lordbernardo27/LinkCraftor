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

from backend.server.stores.dis_rejection_pattern_store import get_rejection_pattern_knowledge


def normalize_phrase(text: Any) -> str:
    """
    Normalize a phrase for comparison and deduplication.
    """
    s = str(text or "").strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"^[\"'â€œâ€â€˜â€™\(\[\{]+|[\"'â€œâ€â€˜â€™\)\]\}:;,\.\!\?]+$", "", s)
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
    r"\b(thanks\s+for\s+(watching|reading)|quick\s+reminder|read\s+further)\b",
    r"\b(search|searched|searching|looked|looking)\s+for\s+(how|what|when|why|where)\b",
    r"\b(derail|ruin|wreck|confuse|frustrate)\s+(many|some|your|the)?\s*\w+\b",
    r"\b(drop\s+dead|dead\s+day)\b",
    r"\b(timeline|plan|strategy)\s+for\s+(healthy|safe|better|general)\s+\w+\b",
    r"\b(aren|isn|wasn|weren|doesn|don)\s+(for|with|to|from|about)\s+\w+\b",
    r"\b(later|refining|refine)\s+with\s+calculator\b",
    r"^(add|adding|allow|allowing|calculate|calculating|read|reading)\s+(that|this|those|these|many|more|safe|further)$",
    r"^(add|adding|calculate|calculating)\s+(that|this|those|these)\s+(many|much)\s+(days|weeks|months|years)$",
    r"^(easiest|easy|simple|best|better|called|known|considered)\s+\w+$",
    r"^(themselves|yourself|ourselves|himself|herself|itself)\s+\w+$",
    r"^(well|although|however|therefore|meanwhile)\s+\w+$",
    r"^\w+\s+(said|says|noted|mentioned|explained)$",
    r"^\w+\s+(invest|allow|allows|allowing)\s+\w+$",
        # conditional clause fragments
    r"^\w+\s+(if|when|while|because|although|unless)\s+\w+(\s+\w+)?$",

    # weak noun + preposition fragment
    r"^\w+\s+(about|for|with|without|during|before|after|into|around)\s+\w+(\s+\w+)?$",

    # vague action/object tail fragments
    r"^\w+\s+(starting|ending|resulted|resulting|matters|matter|compared|influence)\s+\w*$",

    # incomplete instruction fragments
    r"^(exact|clear|simple|specific|proper)\s+(instructions?|steps?|method|way)\s+(for|to)\s+\w+$",

    # partial duration/context fragments
    r"^\w+\s+\w+\s+(during|before|after|around)\s+(the|a|an|few|many)$",
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
            return "rejected_universal_noise_pattern"

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


def candidate_matches_rc2_pattern(
    phrase: str,
    rc2_patterns: List[Dict[str, Any]],
) -> Dict[str, Any]:
    normalized_phrase = normalize_phrase(phrase)
    word_count = len(normalized_phrase.split())

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


def _is_bad_overlap(phrase: str, kept_phrase: str) -> bool:
    """
    Reject only true duplicate/wrapper overlap.
    Preserve useful related anchors unless one is clearly a weak wrapper.

    Examples to preserve:
    - blood pressure
    - blood pressure medication
    - high blood pressure

    Examples to suppress:
    - elevated calcium levels / calcium levels
    - higher calcium levels / calcium levels
    - simple bmi formula / bmi formula
    """
    a = normalize_phrase(phrase)
    b = normalize_phrase(kept_phrase)

    if not a or not b:
        return False

    if a == b:
        return True

    a_words = a.split()
    b_words = b.split()

    if len(a_words) < 2 or len(b_words) < 2:
        return False

    set_a = set(a_words)
    set_b = set(b_words)

    shorter_words = a_words if len(a_words) <= len(b_words) else b_words
    longer_words = b_words if len(a_words) <= len(b_words) else a_words

    shorter_text = " ".join(shorter_words)
    longer_text = " ".join(longer_words)

    weak_wrapper_words = {
        "this", "that", "these", "those", "your", "their",
        "about", "with", "for", "from", "into", "around",
        "simple", "easy", "best", "better", "quick", "general",
        "higher", "lower", "elevated", "reduced", "increased",
        "decreased", "potential", "possible", "common",
    }

    strong_modifier_words = {
        "medication", "medicine", "symptoms", "treatment", "calculator",
        "guide", "formula", "chart", "risk", "risks", "dosage",
        "pregnancy", "ovulation", "bmi", "pressure", "deficiency",
    }

    # If shorter phrase is fully inside longer phrase, reject only weak wrappers.
    if shorter_text in longer_text:
        extra_words = [w for w in longer_words if w not in shorter_words]

        if extra_words and all(w in weak_wrapper_words for w in extra_words):
            return True

        if extra_words and any(w in strong_modifier_words for w in extra_words):
            return False

    # High token overlap with only weak modifier difference.
    overlap_ratio = len(set_a & set_b) / max(1, min(len(set_a), len(set_b)))

    if overlap_ratio >= 0.80:
        diff_words = list((set_a ^ set_b))

        if diff_words and all(w in weak_wrapper_words for w in diff_words):
            return True

    return False


def remove_overlapping_candidates(
    ranked_candidates: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Remove only bad duplicate/wrapper overlap.
    Preserve semantically useful related anchors.
    """
    kept: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []

    kept_phrases: List[str] = []

    for item in ranked_candidates:
        phrase = item.get("phrase", "")

        bad_overlap = any(
            _is_bad_overlap(phrase, kept_phrase)
            for kept_phrase in kept_phrases
        )

        if bad_overlap:
            rejected.append({
                "phrase": phrase,
                "reason": "rejected_bad_wrapper_overlap",
                "item": item,
            })
            continue

        kept.append(item)
        kept_phrases.append(phrase)

    return kept, rejected

def suppress_duplicate_semantic_roots(
    ranked_candidates: List[Dict[str, Any]],
    max_per_root: int = 3,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Limit over-selection from the same semantic root.
    Pattern-based, not phrase-specific.
    """
    kept: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    root_counts: Dict[str, int] = {}

    weak_root_words = {
        "the", "and", "for", "with", "from", "into", "about",
        "this", "that", "these", "those", "your", "their",
        "high", "higher", "lower", "increased", "reduced",
        "elevated", "potential", "possible", "common",
    }

    for item in ranked_candidates:
        phrase = normalize_phrase(item.get("phrase", ""))
        words = [w for w in phrase.split() if w not in weak_root_words]

        if len(words) >= 2:
            root = " ".join(words[-2:])
        elif words:
            root = words[0]
        else:
            root = phrase

        current_count = root_counts.get(root, 0)

        if current_count >= max_per_root:
            rejected.append({
                "phrase": phrase,
                "reason": "rejected_duplicate_semantic_root",
                "semantic_root": root,
                "item": item,
            })
            continue

        root_counts[root] = current_count + 1
        kept.append(item)

    return kept, rejected

def _first_phrase_position(phrase: str, article_text: str) -> int:
    if not phrase or not article_text:
        return -1

    pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
    match = re.search(pattern, article_text.lower())

    if not match:
        return -1

    return int(match.start())


def suppress_close_highlight_spacing(
    ranked_candidates: List[Dict[str, Any]],
    article_text: str,
    min_char_distance: int = 180,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Prevent final highlight candidates from clustering too closely.
    Pattern-based spacing control, not phrase-specific.
    """
    kept: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    kept_positions: List[int] = []

    for item in ranked_candidates:
        phrase = normalize_phrase(item.get("phrase", ""))
        pos = _first_phrase_position(phrase, article_text)

        if pos < 0:
            rejected.append({
                "phrase": phrase,
                "reason": "rejected_spacing_position_missing",
                "item": item,
            })
            continue

        too_close = any(abs(pos - kept_pos) < min_char_distance for kept_pos in kept_positions)

        if too_close:
            rejected.append({
                "phrase": phrase,
                "reason": "rejected_close_highlight_spacing",
                "position": pos,
                "item": item,
            })
            continue

        item["first_position"] = pos
        kept.append(item)
        kept_positions.append(pos)

    return kept, rejected

def _position_zone(position: int, article_length: int) -> str:
    if article_length <= 0 or position < 0:
        return "unknown"

    ratio = position / max(article_length, 1)

    if ratio < 0.25:
        return "beginning"
    if ratio < 0.50:
        return "early_middle"
    if ratio < 0.75:
        return "late_middle"

    return "ending"


def suppress_zone_overcrowding(
    ranked_candidates: List[Dict[str, Any]],
    article_text: str,
    max_zone_ratio: float = 0.40,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Prevent too many highlights from concentrating in one article zone.
    Pattern-based section distribution.
    """
    if not ranked_candidates:
        return [], []

    article_length = len(article_text or "")
    max_total = len(ranked_candidates)
    max_per_zone = max(3, int(max_total * max_zone_ratio))

    kept: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    zone_counts: Dict[str, int] = {}

    for item in ranked_candidates:
        phrase = normalize_phrase(item.get("phrase", ""))
        pos = int(item.get("first_position") or _first_phrase_position(phrase, article_text))
        zone = _position_zone(pos, article_length)

        current_count = zone_counts.get(zone, 0)

        if zone != "unknown" and current_count >= max_per_zone:
            rejected.append({
                "phrase": phrase,
                "reason": "rejected_zone_overcrowding",
                "zone": zone,
                "position": pos,
                "item": item,
            })
            continue

        item["runtime_zone"] = zone
        item["first_position"] = pos
        zone_counts[zone] = current_count + 1
        kept.append(item)

    return kept, rejected

def extract_context_window(
    article_text: str,
    phrase: str,
    window_size: int = 120,
) -> str:
    """
    Extract nearby sentence context around a phrase.
    """
    if not article_text or not phrase:
        return ""

    text_lower = article_text.lower()
    phrase_lower = phrase.lower()

    idx = text_lower.find(phrase_lower)

    if idx < 0:
        return ""

    start = max(0, idx - window_size)
    end = min(len(article_text), idx + len(phrase) + window_size)

    return article_text[start:end]


def contextual_naturalness_score(
    phrase: str,
    context: str,
) -> int:
    """
    Estimate whether a phrase sounds naturally highlightable
    in sentence context.
    Pattern-based editorial scoring.
    """
    score = 100

    phrase_tokens = phrase.split()
    lower_phrase = phrase.lower()

    weak_endings = {
        "function",
        "affect",
        "more",
        "both",
        "many",
        "various",
        "certain",
    }

    weak_starts = {
        "and",
        "or",
        "with",
        "for",
        "to",
        "by",
    }

    if len(phrase_tokens) <= 1:
        score -= 20

    if phrase_tokens:
        if phrase_tokens[0].lower() in weak_starts:
            score -= 35

        if phrase_tokens[-1].lower() in weak_endings:
            score -= 40

    if lower_phrase.endswith("ing"):
        score -= 15

    if re.search(r"\b(this|these|those|them)\b", lower_phrase):
        score -= 15

    if re.search(r"\b(is|are|was|were|be|been)\b", lower_phrase):
        score -= 20

    if len(context.strip()) < 25:
        score -= 15

    return max(score, 0)


def suppress_contextually_awkward_phrases(
    ranked_candidates: List[Dict[str, Any]],
    article_text: str,
    minimum_naturalness: int = 65,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Remove contextually awkward highlight anchors.
    """
    kept: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []

    for item in ranked_candidates:
        phrase = normalize_phrase(item.get("phrase", ""))

        context = extract_context_window(
            article_text,
            phrase,
        )

        naturalness = contextual_naturalness_score(
            phrase,
            context,
        )

        item["contextual_naturalness_score"] = naturalness

        if naturalness < minimum_naturalness:
            rejected.append({
                "phrase": phrase,
                "reason": "rejected_contextual_naturalness",
                "naturalness": naturalness,
                "item": item,
            })
            continue

        kept.append(item)

    return kept, rejected

def link_worthiness_score(
    phrase: str,
) -> int:
    """
    Estimate whether a phrase is genuinely worth linking.
    Pattern-based editorial/SEO scoring.
    """
    score = 50

    lower_phrase = phrase.lower()
    tokens = phrase.split()

    high_value_terms = {
        "disease",
        "syndrome",
        "treatment",
        "therapy",
        "deficiency",
        "blockers",
        "pressure",
        "osteoporosis",
        "fractures",
        "medications",
        "vitamin",
        "absorption",
        "calcium",
        "electrolyte",
        "regulation",
        "disorder",
        "infection",
        "diabetes",
        "hypertension",
    }

    weak_value_terms = {
        "thing",
        "various",
        "many",
        "certain",
        "more",
        "levels",
        "effects",
        "issues",
        "problems",
        "risk",
    }

    for token in tokens:
        token_lower = token.lower()

        if token_lower in high_value_terms:
            score += 12

        if token_lower in weak_value_terms:
            score -= 10

    if len(tokens) >= 3:
        score += 10

    if len(tokens) == 1:
        score -= 20

    if re.search(r"\b(how|why|when|what)\b", lower_phrase):
        score += 8

    if re.search(r"\b(of|with|for|in)\b", lower_phrase):
        score += 5

    return max(score, 0)


def suppress_low_link_worthiness(
    ranked_candidates: List[Dict[str, Any]],
    minimum_link_worthiness: int = 55,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Remove phrases with weak editorial link value.
    """
    kept: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []

    for item in ranked_candidates:
        phrase = normalize_phrase(item.get("phrase", ""))

        worthiness = link_worthiness_score(phrase)

        item["link_worthiness_score"] = worthiness

        if worthiness < minimum_link_worthiness:
            rejected.append({
                "phrase": phrase,
                "reason": "rejected_link_worthiness",
                "link_worthiness": worthiness,
                "item": item,
            })
            continue

        kept.append(item)

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
    """
    vertical = ""
    rc2_knowledge = get_rejection_pattern_knowledge(workspace_id, vertical)
    rc2_patterns = rc2_knowledge.get("patterns", []) if isinstance(rc2_knowledge, dict) else []

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

        rc2_match = candidate_matches_rc2_pattern(phrase, rc2_patterns)

        item["dis_checked"] = True
        item["dis_pattern_match"] = rc2_match.get("matched", False)
        item["dis_rejection_reason"] = rc2_match.get("failure_category", "")

        item["dis_signal_reasons"] = rc2_match.get("failure_reasons", [])
        item["dis_can_block"] = False
        item["dis_advisory_only"] = True
        item["anchor_quality_score"] = score_anchor_quality(phrase)
        item["article_relevance_score"] = score_article_relevance(phrase, article_text)
        item["occurrence_count"] = count_phrase_occurrences(phrase, article_text)
        item["link_opportunity_score"] = score_link_opportunity(phrase)
        item["selection_score"] = (
            item["anchor_quality_score"]
            + item["article_relevance_score"]
            + item["link_opportunity_score"]
        )

        item["selection_status"] = "selected_candidate"
        item["selection_reason"] = "selected_quality_relevance_link_opportunity"

        article_matched.append(item)

    article_matched.sort(
        key=lambda x: (
            x.get("selection_score", 0),
            x.get("anchor_quality_score", 0),
            len(x.get("phrase", "")),
        ),
        reverse=True,
    )

    overlap_selected, overlap_rejected = remove_overlapping_candidates(article_matched)
    rejected.extend(overlap_rejected)

    root_selected, root_rejected = suppress_duplicate_semantic_roots(
        overlap_selected,
        max_per_root=3,
    )
    rejected.extend(root_rejected)

    spacing_selected, spacing_rejected = suppress_close_highlight_spacing(
        root_selected,
        article_text=article_text,
        min_char_distance=180,
    )
    rejected.extend(spacing_rejected)

    zone_selected, zone_rejected = suppress_zone_overcrowding(
        spacing_selected,
        article_text=article_text,
        max_zone_ratio=0.40,
    )
    rejected.extend(zone_rejected)

    contextual_selected, contextual_rejected = suppress_contextually_awkward_phrases(
        zone_selected,
        article_text=article_text,
        minimum_naturalness=65,
    )
    rejected.extend(contextual_rejected)

    selected, worthiness_rejected = suppress_low_link_worthiness(
        contextual_selected,
        minimum_link_worthiness=55,
    )
    rejected.extend(worthiness_rejected)

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
            "rc2_patterns_loaded": len(rc2_patterns),
            "rc2_advisory_signals": len([
                row for row in article_matched
                if row.get("dis_pattern_match") is True
            ]),
        },
    }















