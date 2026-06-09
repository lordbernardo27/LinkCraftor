from __future__ import annotations

import re
from typing import Any, Dict, List


def _norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").lower()).strip()


def _tokens(value: Any) -> set[str]:
    return {
        t for t in re.findall(r"[a-z0-9]+", _norm(value))
        if len(t) >= 3
    }


# Universal starter concept map.
# This is intentionally cross-niche-capable:
# domain-specific concepts can be added later per workspace, but the structure is universal.
CONCEPT_ALIASES: Dict[str, List[str]] = {
    # fertility / cycle examples used for current test
    "basal body temperature": [
        "bbt",
        "bbt chart",
        "temperature each morning",
        "morning temperature",
        "temperature tracking",
        "basal temperature",
    ],
    "last menstrual period": [
        "lmp",
        "last period started",
        "first day of last period",
        "cycle start date",
        "period start date",
    ],
    "fertile window": [
        "fertile window begins",
        "fertile days",
        "most fertile days",
        "fertility window",
        "ovulation window",
    ],
    "timed intercourse": [
        "exact instructions for timed intercourse",
        "timed intercourse",
        "when to have sex to get pregnant",
        "sex timing",
        "fertility timing",
    ],
    "luteal phase": [
        "personal luteal phase",
        "true luteal length",
        "true luteal length sharpens",
        "luteal phase length",
    ],
    "cycle length": [
        "real cycle length",
        "shortest and longest cycle",
        "typical cycle length",
        "cycle duration",
        "menstrual cycle length",
    ],
    "cervical mucus": [
        "cervical mucus clues",
        "egg white cervical mucus",
        "fertile cervical mucus",
        "cervical mucus patterns",
        "mucus observation",
    ],
    "calendar method": [
        "refine the calendar method",
        "calendar method",
        "rhythm method",
        "fertility awareness method",
        "natural family planning",
    ],
    "hormonal birth control": [
        "stopping hormonal birth control",
        "months after stopping hormonal birth",
        "stopping birth control",
        "after hormonal contraception",
    ],
}


def expand_anchor_concepts(anchor_phrase: str, limit: int = 20) -> Dict[str, Any]:
    anchor = _norm(anchor_phrase)
    anchor_tokens = _tokens(anchor)

    concepts: List[str] = []
    expansions: List[str] = []

    for concept, aliases in CONCEPT_ALIASES.items():
        terms = [concept] + aliases
        matched = False

        for term in terms:
            term_norm = _norm(term)
            term_tokens = _tokens(term_norm)

            if not term_tokens:
                continue

            overlap = anchor_tokens & term_tokens
            overlap_ratio = len(overlap) / max(1, len(term_tokens))

            if anchor == term_norm or anchor in term_norm or term_norm in anchor or overlap_ratio >= 0.60:
                matched = True
                break

        if matched:
            concepts.append(concept)
            for term in terms:
                t = _norm(term)
                if t and t not in expansions:
                    expansions.append(t)

    return {
        "anchor_phrase": anchor,
        "concepts": concepts[:limit],
        "expansions": expansions[:limit],
        "concept_count": len(concepts),
        "expansion_count": len(expansions),
    }


def concept_match_score(anchor_phrase: str, target_text: str) -> Dict[str, Any]:
    expanded = expand_anchor_concepts(anchor_phrase)
    target = _norm(target_text)
    target_tokens = _tokens(target)

    matched_terms: List[str] = []

    for term in expanded.get("expansions", []):
        term_norm = _norm(term)
        term_tokens = _tokens(term_norm)

        if not term_tokens:
            continue

        overlap = term_tokens & target_tokens
        ratio = len(overlap) / max(1, len(term_tokens))

        if term_norm in target or ratio >= 0.60:
            matched_terms.append(term_norm)

    score = min(1.0, 0.25 * len(set(matched_terms)))

    return {
        "score": round(score, 4),
        "matched_terms": sorted(set(matched_terms)),
        "concepts": expanded.get("concepts", []),
        "expansions": expanded.get("expansions", []),
    }
