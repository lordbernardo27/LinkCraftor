from __future__ import annotations

from typing import Dict, List, Any, Set
from collections import defaultdict
from datetime import datetime
import re


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _norm_text(text: Any) -> str:

    text = str(text or "").lower().strip()

    text = re.sub(r"[^a-z0-9\s\-]", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def _tokenize(text: str) -> List[str]:

    return [
        t for t in _norm_text(text).split()
        if t
    ]


def _phrase_similarity(
    a: str,
    b: str,
) -> float:

    ta = set(_tokenize(a))
    tb = set(_tokenize(b))

    if not ta or not tb:
        return 0.0

    overlap = ta.intersection(tb)

    union = ta.union(tb)

    return len(overlap) / max(len(union), 1)


def _choose_canonical_topic(
    phrases: List[str],
) -> str:

    if not phrases:
        return ""

    ranked = sorted(
        phrases,
        key=lambda x: (
            -len(_tokenize(x)),
            x,
        )
    )

    return ranked[0]


def build_canonical_topic_map_v2(
    phrases: List[str],
) -> Dict[str, Any]:

    normalized = []

    seen = set()

    for p in phrases:

        np = _norm_text(p)

        if not np:
            continue

        if np in seen:
            continue

        seen.add(np)

        normalized.append(np)

    topic_groups = []

    used = set()

    for phrase in normalized:

        if phrase in used:
            continue

        family = [phrase]

        used.add(phrase)

        for other in normalized:

            if other == phrase:
                continue

            if other in used:
                continue

            score = _phrase_similarity(
                phrase,
                other,
            )

            if score >= 0.50:

                family.append(other)

                used.add(other)

        topic_groups.append(family)

    canonical_topics = {}

    for family in topic_groups:

        canonical = _choose_canonical_topic(
            family
        )

        canonical_topics[canonical] = {

            "canonical_topic":
                canonical,

            "aliases":
                sorted([
                    x for x in family
                    if x != canonical
                ]),

            "topic_size":
                len(family),

            "generated_at":
                _now_iso(),
        }

    return {

        "generated_at":
            _now_iso(),

        "topic_count":
            len(canonical_topics),

        "canonical_topics":
            canonical_topics,
    }
def _canonical_phrase_score(
    phrase: str,
) -> float:

    tokens = _tokenize(phrase)

    if not tokens:
        return 0.0

    score = 0.0

    token_count = len(tokens)

    if token_count <= 4:
        score += 3.0

    elif token_count <= 6:
        score += 1.5

    else:
        score -= 1.0

    avg_token_len = (
        sum(len(t) for t in tokens)
        / max(token_count, 1)
    )

    if avg_token_len <= 10:
        score += 1.0

    stop_heavy = {
        "of",
        "for",
        "the",
        "and",
        "with",
        "to",
        "in",
    }

    stop_count = sum(
        1 for t in tokens
        if t in stop_heavy
    )

    score -= (
        stop_count * 0.25
    )

    unique_ratio = (
        len(set(tokens))
        / max(token_count, 1)
    )

    score += unique_ratio

    return round(score, 4)


def _choose_canonical_topic(
    phrases: List[str],
) -> str:

    if not phrases:
        return ""

    ranked = sorted(
        phrases,
        key=lambda x: (
            _canonical_phrase_score(x),
            -len(_tokenize(x)),
            x,
        ),
        reverse=True,
    )

    return ranked[0]


def _semantic_normalize(
    text: str,
) -> str:

    text = _norm_text(text)

    text = text.replace("-", " ")

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    tokens = [
        t.strip()
        for t in text.split()
        if t.strip()
    ]

    normalized = " ".join(tokens)

    return normalized.strip()


def build_semantic_normalization_map_v2(
    phrases: List[str],
) -> Dict[str, Any]:

    normalization_map = {}

    grouped = defaultdict(list)

    for phrase in phrases:

        display = str(
            phrase or ""
        ).strip()

        if not display:
            continue

        normalized = _semantic_normalize(
            display
        )

        if not normalized:
            continue

        grouped[
            normalized
        ].append(display)

    for normalized, variants in grouped.items():

        clean_variants = sorted(
            list(set(variants))
        )

        normalization_map[
            normalized
        ] = {

            "normalized_phrase":
                normalized,

            "display_variants":
                clean_variants,

            "variant_count":
                len(clean_variants),

            "generated_at":
                _now_iso(),
        }

    return {

        "generated_at":
            _now_iso(),

        "normalized_phrase_count":
            len(normalization_map),

        "semantic_normalization_map":
            normalization_map,
    }


def _seo_canonical_score(
    phrase: str,
) -> float:

    tokens = _tokenize(phrase)

    if not tokens:
        return 0.0

    score = _canonical_phrase_score(phrase)

    token_count = len(tokens)

    # SEO-friendly phrases are usually compact but descriptive.
    if 2 <= token_count <= 4:
        score += 2.0

    if token_count > 6:
        score -= 2.0

    weak_words = {
        "operational",
        "mechanisms",
        "issues",
        "things",
        "stuff",
        "various",
        "different",
        "general",
    }

    score -= sum(
        0.6 for t in tokens
        if t in weak_words
    )

    query_starters = {
        "how",
        "what",
        "why",
        "when",
        "where",
    }

    if tokens[0] in query_starters:
        score -= 0.8

    strong_topic_words = {
        "management",
        "strategy",
        "guide",
        "checklist",
        "calculator",
        "cost",
        "price",
        "benefits",
        "risks",
        "prevention",
        "optimization",
        "contract",
        "mortgage",
        "security",
        "compliance",
        "software",
        "platform",
    }

    if any(t in strong_topic_words for t in tokens):
        score += 0.8

    return round(score, 4)


def choose_seo_canonical_topic_v2(
    phrases: List[str],
) -> Dict[str, Any]:

    cleaned = []

    seen = set()

    for phrase in phrases:

        p = _semantic_normalize(str(phrase or ""))

        if not p:
            continue

        if p in seen:
            continue

        seen.add(p)
        cleaned.append(p)

    if not cleaned:
        return {
            "canonical_topic": "",
            "candidates": [],
            "reason": "no_valid_phrases",
        }

    ranked = sorted(
        cleaned,
        key=lambda x: (
            _seo_canonical_score(x),
            _canonical_phrase_score(x),
            -len(_tokenize(x)),
            x,
        ),
        reverse=True,
    )

    candidates = [
        {
            "phrase": p,
            "seo_score": _seo_canonical_score(p),
            "canonical_quality_score": _canonical_phrase_score(p),
            "token_count": len(_tokenize(p)),
        }
        for p in ranked
    ]

    return {
        "canonical_topic": ranked[0],
        "candidates": candidates,
        "reason": "seo_canonical_selected",
        "runtime_effect": "read_only_no_runtime_injection",
        "layer": "1.7.4_seo_canonical_selection",
    }

