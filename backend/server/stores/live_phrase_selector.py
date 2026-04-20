from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set

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
    "key points to remember",
    "other helpful tools",
    "your result and what it means",
    "faqs",
    "faq",
    "frequently asked questions",
    "conclusion",
    "summary",
    "final thoughts",
    "table of contents",
}

WEAK_STARTS: Set[str] = {
    "the", "this", "that", "these", "those", "your", "is", "are", "was", "were",
    "while", "so", "then"
}

WEAK_ENDINGS: Set[str] = {
    "about", "around", "roughly", "always", "usually", "often", "matter", "like",
    "such", "each", "one", "better", "works", "remember"
}

QUESTION_PATTERNS: List[re.Pattern[str]] = [
    re.compile(r"^what is [a-z0-9\s\-\?]+$"),
    re.compile(r"^why [a-z0-9\s\-\?]+$"),
    re.compile(r"^how [a-z0-9\s\-\?]+$"),
    re.compile(r"^who [a-z0-9\s\-\?]+$"),
    re.compile(r"^can [a-z0-9\s\-\?]+$"),
    re.compile(r"^should [a-z0-9\s\-\?]+$"),
]


def _canonical_phrase(s: str) -> str:
    s = (s or "").strip().lower()
    s = s.replace("’", "'").replace("“", '"').replace("”", '"')
    s = s.replace("_", " ").replace("/", " ").replace("\\", " ")
    s = NON_ALNUM_RE.sub(" ", s)
    s = re.sub(r"^\s*\d+[\.\)]\s*", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _tokenize(text: str) -> List[str]:
    return [t.lower() for t in WORD_RE.findall(text or "")]


def _content_tokens(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t not in STOPWORDS]


def _looks_like_question_or_intent(p: str) -> bool:
    p = _canonical_phrase(p)
    return any(rx.match(p) for rx in QUESTION_PATTERNS)


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
        "ivf", "lmp", "ultrasound", "miscarriage", "postpartum"
    }
    # single words are usually too broad for live phrase pool unless clearly high-signal
    return toks[0] not in keep


def _is_link_worthy_shape(p: str) -> bool:
    p = _canonical_phrase(p)
    if not p:
        return False

    if _is_generic_heading(p):
        return False

    if _is_low_value_single_word(p):
        return False

    toks = _tokenize(p)
    if len(toks) < 2 or len(toks) > 10:
        return False

    content = _content_tokens(toks)
    if len(content) < 2 and not _looks_like_question_or_intent(p):
        return False

    if toks[0] in WEAK_STARTS and not _looks_like_question_or_intent(p):
        return False

    if toks[-1] in WEAK_ENDINGS and not _looks_like_question_or_intent(p):
        return False

    return True


def _reject_live_phrase(phrase: str, phrase_type: str = "", bucket: str = "", confidence: float = 0.0) -> bool:
    p = _canonical_phrase(phrase)
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

    if p == "what you need to calculate?":
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
        phrase = _canonical_phrase(raw_phrase)
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
        phrase = c["phrase"]
        base = _base_score(
            phrase=phrase,
            phrase_type=str(c.get("source_type") or ""),
            bucket=str(c.get("bucket") or ""),
            confidence=float(c.get("confidence") or 0.0),
        )
        final_score = apply_vertical_policy_score(phrase, base, vertical)

        if final_score < min_keep:
            continue

        item = {
            "phrase": phrase,
            "norm": phrase,
            "source_url": source_url,
            "type": c.get("source_type") or "unknown",
            "bucket": c.get("bucket") or "unknown",
            "confidence": c.get("confidence") or 0.0,
            "score": final_score,
            "aliases": c.get("aliases") or [],
            "section_id": c.get("section_id") or "",
            "snippet": c.get("snippet") or "",
        }

        existing = best.get(phrase)
        if existing is None or int(item["score"]) > int(existing["score"]):
            best[phrase] = item

    selected = sorted(best.values(), key=lambda x: (-int(x["score"]), x["phrase"]))

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "source_url": source_url,
        "vertical": vertical,
        "candidate_count": len(entries or []),
        "selected_count": len(selected),
        "phrases": selected,
    }