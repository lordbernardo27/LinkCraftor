from __future__ import annotations

import re
from typing import Any, Dict, List, Set

from backend.server.stores.candidate_window_guard import candidate_window_guard
from backend.server.stores.phrase_strength_scorer import score_phrase_strength
from backend.server.stores.phrase_vertical_policy import (
    apply_vertical_policy_score,
    detect_vertical,
    get_vertical_min_score,
)


WORD_RE = re.compile(r"[a-z0-9]{2,}", re.I)
NON_ALNUM_RE = re.compile(r"[^a-z0-9\s\-\?:]")
SPACE_RE = re.compile(r"\s+")

STOPWORDS: Set[str] = {
    "the", "and", "for", "with", "that", "this", "from", "into", "your", "you", "are", "was", "were",
    "will", "can", "could", "should", "would", "have", "has", "had", "about", "over", "under", "than",
    "then", "when", "what", "where", "which", "who", "whom", "why", "how", "a", "an", "to", "of", "in",
    "on", "at", "by", "or", "as", "is", "it", "be", "not", "no", "if", "but", "so", "because", "after",
    "before", "during", "while", "through", "up", "down", "out", "off", "too", "very", "also"
}

GENERIC_HEADINGS: Set[str] = {
    "key points to remember", "other helpful tools", "your result and what it means",
    "faqs", "faq", "frequently asked questions", "conclusion", "summary",
    "final thoughts", "table of contents",
}

WEAK_STARTS: Set[str] = {
    "the", "this", "that", "these", "those", "your", "is", "are", "was", "were",
    "while", "so", "then", "with", "for", "from", "by", "after", "before"
}

WEAK_ENDINGS: Set[str] = {
    "about", "around", "roughly", "always", "usually", "often", "matter", "like",
    "such", "each", "one", "better", "works", "remember", "with", "for", "from",
    "by", "after", "before"
}

BAD_FRAGMENT_PATTERNS = (
    re.compile(r"\b(\w+)\s+\1\b", re.I),
    re.compile(r"\brather than\b", re.I),
    re.compile(r"\bthan someone\b", re.I),
    re.compile(r"\banswer depends\b", re.I),
    re.compile(r"\bresult depends\b", re.I),
    re.compile(r"\bdo this\b", re.I),
    re.compile(r"\bcan show\b", re.I),
    re.compile(r"\bend up\b", re.I),
    re.compile(r"\blean more\b", re.I),
    re.compile(r"\boften falls\b", re.I),
    re.compile(r"\boften lands\b", re.I),
    re.compile(r"\bbecause they\b", re.I),
    re.compile(r"\bbecause you\b", re.I),
    re.compile(r"\bwith \d+\b", re.I),
    re.compile(r"\bwithout an\b", re.I),
    re.compile(r"\bwithout a\b", re.I),
    re.compile(r"\bwith an\b", re.I),
    re.compile(r"\bwith a\b", re.I),
)

QUESTION_PATTERNS: List[re.Pattern[str]] = [
    re.compile(r"^what is [a-z0-9\s\-\?]+$"),
    re.compile(r"^what are [a-z0-9\s\-\?]+$"),
    re.compile(r"^why [a-z0-9\s\-\?]+$"),
    re.compile(r"^how [a-z0-9\s\-\?]+$"),
    re.compile(r"^who [a-z0-9\s\-\?]+$"),
    re.compile(r"^can [a-z0-9\s\-\?]+$"),
    re.compile(r"^should [a-z0-9\s\-\?]+$"),
]


def _canonical_phrase(s: str) -> str:
    s = (s or "").strip().lower()
    s = s.replace("â€™", "'").replace("â€œ", '"').replace("â€", '"')
    s = s.replace("_", " ").replace("/", " ").replace("\\", " ")
    s = NON_ALNUM_RE.sub(" ", s)
    s = re.sub(r"^\s*\d+[\.\)]\s*", "", s)
    return SPACE_RE.sub(" ", s).strip()


def _tokenize(text: str) -> List[str]:
    return [t.lower() for t in WORD_RE.findall(text or "")]


def _content_tokens(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t not in STOPWORDS]


def _looks_like_question_or_intent(p: str) -> bool:
    p = _canonical_phrase(p)
    return any(rx.match(p) for rx in QUESTION_PATTERNS)


def _has_bad_fragment_pattern(p: str) -> bool:
    p = _canonical_phrase(p)
    return any(rx.search(p) for rx in BAD_FRAGMENT_PATTERNS)


def _compress_wrapper_phrase(phrase: str) -> str:
    p = _canonical_phrase(phrase)
    if not p:
        return ""

    wrappers = (
        r"^how to\s+",
        r"^how do you\s+",
        r"^how can you\s+",
        r"^what is\s+",
        r"^what are\s+",
        r"^why does\s+",
        r"^why do\s+",
        r"^best way to\s+",
        r"^best time to\s+",
        r"^guide to\s+",
        r"^complete guide to\s+",
        r"^beginner guide to\s+",
        r"^faqs about\s+",
    )

    compressed = p
    for rx in wrappers:
        compressed = re.sub(rx, "", compressed).strip()

    compressed = _canonical_phrase(compressed)
    original_tokens = _tokenize(p)
    compressed_tokens = _tokenize(compressed)

    if len(compressed_tokens) >= 2 and len(compressed_tokens) < len(original_tokens):
        if len(_content_tokens(compressed_tokens)) >= 2:
            return compressed

    return p


def _is_generic_heading(p: str) -> bool:
    p = _canonical_phrase(p)
    if p in GENERIC_HEADINGS:
        return True
    if p.startswith("key points"):
        return True
    if p.startswith("other helpful"):
        return True
    if p.startswith("faqs about") and len(_tokenize(p)) <= 4:
        return True
    return False


def _is_low_value_single_word(p: str) -> bool:
    toks = _tokenize(p)
    if len(toks) != 1:
        return False

    keep = {
        "pregnancy", "ovulation", "fertility", "conception", "implantation",
        "ivf", "lmp", "ultrasound", "miscarriage", "postpartum",
        "seo", "cashflow", "revenue", "analytics", "marketing",
    }

    return toks[0] not in keep


def _is_link_worthy_shape(p: str) -> bool:
    p = _compress_wrapper_phrase(p)
    if not p:
        return False

    if _is_generic_heading(p):
        return False

    if _is_low_value_single_word(p):
        return False

    if _has_bad_fragment_pattern(p):
        return False

    toks = _tokenize(p)

    if len(toks) < 2 or len(toks) > 10:
        return False

    if len(set(toks)) < len(toks):
        return False

    content = _content_tokens(toks)
    if len(content) < 2 and not _looks_like_question_or_intent(p):
        return False

    if toks[0] in WEAK_STARTS and not _looks_like_question_or_intent(p):
        return False

    if toks[-1] in WEAK_ENDINGS and not _looks_like_question_or_intent(p):
        return False

    return True


def _reject_live_phrase(
    phrase: str,
    phrase_type: str = "",
    bucket: str = "",
    confidence: float = 0.0,
) -> bool:
    p = _compress_wrapper_phrase(phrase)
    toks = _tokenize(p)

    if not p:
        return True

    if _is_generic_heading(p):
        return True

    if re.match(r"^\d+[\.\)]\s*", phrase or ""):
        return True

    if p in {"other helpful tools", "key points to remember", "your result and what it means"}:
        return True

    if p.endswith("to remember"):
        return True

    if p.startswith("faqs about"):
        return True

    if p == "what you need to calculate":
        return True

    if phrase_type in {"heading_h2", "heading_h3"} and len(toks) < 3 and not _looks_like_question_or_intent(p):
        return True

    if phrase_type == "live_url_slug" and len(toks) == 1:
        return True

    if phrase_type == "live_url_slug" and p.endswith(("due", "pregnancy", "calculate")):
        return True

    if bucket == "semantic_optional" and confidence < 0.60 and not _looks_like_question_or_intent(p):
        return True

    if not _is_link_worthy_shape(p):
        return True

    return False


def _base_score(phrase: str, phrase_type: str = "", bucket: str = "", confidence: float = 0.0) -> int:
    p = _canonical_phrase(phrase)
    toks = _tokenize(p)
    score = 0

    if phrase_type == "live_url_slug":
        score += 30
    elif phrase_type in {"heading_h1", "heading_h2"}:
        score += 24
    elif phrase_type == "heading_h3":
        score += 18
    elif phrase_type == "body_phrase":
        score += 12

    if bucket == "internal_strong":
        score += 20
    elif bucket == "semantic_optional":
        score += 8

    score += int(round(float(confidence or 0.0) * 20))

    if _looks_like_question_or_intent(p):
        score += 18

    if 3 <= len(toks) <= 6:
        score += 8
    elif len(toks) == 2:
        score += 4

    if "?" in (phrase or ""):
        score += 3

    return score


def _call_strength_scorer(
    phrase: str,
    source_type: str,
    vertical: str,
    confidence: float,
    bucket: str,
) -> int:
    fallback = _base_score(
        phrase=phrase,
        phrase_type=source_type,
        bucket=bucket,
        confidence=confidence,
    )

    try:
        result = score_phrase_strength(
            phrase=phrase,
            source_type=source_type,
            vertical=vertical,
            confidence=confidence,
            bucket=bucket,
            fallback_score=fallback,
        )
    except TypeError:
        try:
            result = score_phrase_strength(
                phrase=phrase,
                source_type=source_type,
                vertical=vertical,
                fallback_score=fallback,
            )
        except TypeError:
            try:
                result = score_phrase_strength(phrase, source_type, vertical)
            except Exception:
                return fallback
        except Exception:
            return fallback
    except Exception:
        return fallback

    if isinstance(result, dict):
        for key in ("score", "strength", "final_score", "quality_score"):
            if key in result:
                try:
                    return int(float(result[key]))
                except Exception:
                    return fallback

    try:
        return int(float(result))
    except Exception:
        return fallback


def _call_candidate_window_guard(
    candidates: List[Dict[str, Any]],
    vertical: str,
    max_keep: int = 80,
) -> List[Dict[str, Any]]:
    if not candidates:
        return []

    try:
        guarded = candidate_window_guard(
            candidates=candidates,
            vertical=vertical,
            max_keep=max_keep,
        )
    except TypeError:
        try:
            guarded = candidate_window_guard(candidates, vertical, max_keep)
        except TypeError:
            try:
                guarded = candidate_window_guard(candidates)
            except Exception:
                return candidates[:max_keep]
        except Exception:
            return candidates[:max_keep]
    except Exception:
        return candidates[:max_keep]

    if isinstance(guarded, dict):
        for key in ("candidates", "selected", "phrases", "items", "kept"):
            value = guarded.get(key)
            if isinstance(value, list):
                return value[:max_keep]
        return candidates[:max_keep]

    if isinstance(guarded, list):
        return guarded[:max_keep]

    return candidates[:max_keep]


def _final_quality_gate(item: Dict[str, Any], vertical: str) -> bool:
    phrase = _compress_wrapper_phrase(str(item.get("phrase") or ""))
    if not phrase:
        return False

    toks = _tokenize(phrase)

    if len(toks) < 2 or len(toks) > 10:
        return False

    if len(set(toks)) < len(toks):
        return False

    if _is_generic_heading(phrase):
        return False

    if _has_bad_fragment_pattern(phrase):
        return False

    if toks[0] in WEAK_STARTS and not _looks_like_question_or_intent(phrase):
        return False

    if toks[-1] in WEAK_ENDINGS and not _looks_like_question_or_intent(phrase):
        return False

    content = _content_tokens(toks)
    if len(content) < 2 and not _looks_like_question_or_intent(phrase):
        return False

    try:
        score = int(float(item.get("score") or 0))
    except Exception:
        score = 0

    if score < get_vertical_min_score(vertical):
        return False

    return True


def select_live_phrases(
    workspace_id: str,
    source_url: str,
    entries: List[Dict[str, Any]],
    page_text: str = "",
) -> Dict[str, Any]:
    source_url = str(source_url or "").strip()
    page_text = str(page_text or "").strip()

    candidates: List[Dict[str, Any]] = []
    combined_parts: List[str] = [source_url, page_text]

    for i, entry in enumerate(entries or []):
        if not isinstance(entry, dict):
            continue

        raw_phrase = str(entry.get("phrase") or entry.get("norm") or "").strip()
        phrase = _compress_wrapper_phrase(raw_phrase)
        phrase_type = str(entry.get("type") or "").strip()
        bucket = str(entry.get("bucket") or "").strip()
        confidence = float(entry.get("confidence") or 0.0)
        aliases = entry.get("aliases") if isinstance(entry.get("aliases"), list) else []

        if raw_phrase:
            combined_parts.append(raw_phrase)

        if _reject_live_phrase(
            phrase=raw_phrase,
            phrase_type=phrase_type,
            bucket=bucket,
            confidence=confidence,
        ):
            continue

        candidates.append({
            "phrase": phrase,
            "source_type": phrase_type or "unknown",
            "bucket": bucket or "unknown",
            "confidence": confidence,
            "section_id": f"live_{i}",
            "snippet": raw_phrase,
            "aliases": aliases,
        })

    combined_text = "\n".join(x for x in combined_parts if x).lower()
    vertical = detect_vertical(combined_text)
    min_keep = get_vertical_min_score(vertical)

    best: Dict[str, Dict[str, Any]] = {}

    for c in candidates:
        phrase = _compress_wrapper_phrase(c["phrase"])
        if not phrase:
            continue

        base_score = _call_strength_scorer(
            phrase=phrase,
            source_type=str(c.get("source_type") or ""),
            vertical=vertical,
            confidence=float(c.get("confidence") or 0.0),
            bucket=str(c.get("bucket") or ""),
        )

        final_score = apply_vertical_policy_score(phrase, base_score, vertical)

        if final_score < min_keep:
            continue

        item = {
            "phrase": phrase,
            "norm": phrase,
            "source_url": source_url,
            "type": c.get("source_type") or "unknown",
            "bucket": c.get("bucket") or "unknown",
            "confidence": c.get("confidence") or 0.0,
            "score": int(final_score),
            "aliases": c.get("aliases") or [],
            "section_id": c.get("section_id") or "",
            "snippet": c.get("snippet") or "",
        }

        if not _final_quality_gate(item, vertical):
            continue

        existing = best.get(phrase)
        if existing is None or int(item["score"]) > int(existing["score"]):
            best[phrase] = item

    ranked = sorted(best.values(), key=lambda x: (-int(x["score"]), x["phrase"]))
    guarded = _call_candidate_window_guard(ranked, vertical=vertical, max_keep=80)

    final: List[Dict[str, Any]] = []
    seen: Set[str] = set()

    for item in guarded:
        phrase = _compress_wrapper_phrase(str(item.get("phrase") or ""))
        if not phrase or phrase in seen:
            continue

        item = dict(item)
        item["phrase"] = phrase
        item["norm"] = phrase

        if not _final_quality_gate(item, vertical):
            continue

        seen.add(phrase)
        final.append(item)

    selected = sorted(final, key=lambda x: (-int(x["score"]), x["phrase"]))

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "source_url": source_url,
        "vertical": vertical,
        "candidate_count": len(entries or []),
        "raw_candidate_count": len(candidates),
        "selected_count": len(selected),
        "phrases": selected,
    }
