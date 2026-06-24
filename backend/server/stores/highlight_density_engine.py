"""
Highlight Density Engine v2  (corrected)

ROLE (frozen):
    Control how MANY ranked phrases are painted as highlights, and how they are
    SPACED / DISTRIBUTED. It does not decide phrase quality and it does not
    delete opportunities.

What v2 does:
    - count words, classify article length, derive a [min, max] paint budget
    - run ONE greedy painter over the already-ranked candidates that jointly
      handles: final count, char spacing, article-zone balance, phrase-family
      caps, short-anchor balance, high-frequency balance
    - everything not painted is kept and tagged display_status="deferred_opportunity"
      so linked links AND unlinked opportunities both survive into frontend metadata

What v2 deliberately REMOVED:
    - _apply_quality_floor (a quality gate in the wrong layer; was also dead)
    - the double truncation (short-balance cap THEN high-freq cap) that could
      silently land the final count below recommended_min
    - the wide 0.55..1.25 adaptive multiplier (now a gentle, bounded nudge)
    RC2 stays advisory; it annotates, it never removes.

Output:
    final_highlights -> the painted set (links + opportunities chosen to show)
    all_candidates   -> every candidate with display_status painted|deferred
"""

from __future__ import annotations

import re
from typing import Any, Dict, List

try:  # advisory only
    from backend.server.stores.dis_rejection_pattern_store import (
        get_rejection_pattern_knowledge,
    )
except Exception:  # pragma: no cover
    def get_rejection_pattern_knowledge(*_a: Any, **_k: Any) -> Dict[str, Any]:
        return {"patterns": []}


_WORD_RE = re.compile(r"\b\w+\b")


def count_article_words(article_text: str) -> int:
    return len(_WORD_RE.findall(article_text)) if article_text else 0


def classify_article_length(word_count: int) -> str:
    if word_count < 800:
        return "short"
    if word_count < 1500:
        return "medium"
    if word_count < 2500:
        return "long"
    return "very_long"


def get_density_range(article_length_class: str) -> Dict[str, int]:
    return {
        "short": {"min": 5, "max": 10},
        "medium": {"min": 10, "max": 18},
        "long": {"min": 18, "max": 32},
        "very_long": {"min": 18, "max": 50},
    }.get(article_length_class, {"min": 5, "max": 10})


# ---------------------------------------------------------------------------
# Gentle, bounded density nudge (replaces the 0.55..1.25 swing)
# ---------------------------------------------------------------------------
def calculate_adaptive_density_limit(candidates: List[Dict[str, Any]], base_max: int,
                                     base_min: int) -> Dict[str, Any]:
    if not candidates:
        return {"adaptive_max": base_min, "density_multiplier": 1.0,
                "average_selection_score": 0.0}

    scores = [float(c.get("selection_score") or 0.0) for c in candidates]
    avg = sum(scores) / max(len(scores), 1)

    # Nudge within a narrow band so density never collapses or explodes.
    if avg >= 70:
        mult = 1.15
    elif avg >= 50:
        mult = 1.0
    else:
        mult = 0.85

    adaptive_max = int(round(base_max * mult))
    adaptive_max = max(base_min, min(adaptive_max, base_max + 6))
    return {"adaptive_max": adaptive_max,
            "density_multiplier": mult,
            "average_selection_score": round(avg, 2)}


def _zone(position: int, article_len: int) -> str:
    if article_len <= 0 or position < 0:
        return "unknown"
    r = position / max(article_len, 1)
    if r < 0.25:
        return "beginning"
    if r < 0.50:
        return "early_middle"
    if r < 0.75:
        return "late_middle"
    return "ending"


def _token_count(phrase: str) -> int:
    return len(_WORD_RE.findall(str(phrase or "").lower()))


# ---------------------------------------------------------------------------
# RC2 advisory annotation (no removal)
# ---------------------------------------------------------------------------
_RC2_CATEGORIES = {
    "term_order_validity_failure", "fragment_validity_failure",
    "boundary_validity_failure", "candidate_signal_failure",
    "semantic_cohesion_failure", "candidate_window_failure",
    "general_rejection_pattern",
}


def _rc2_advisory(phrase: str, rc2_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
    wc = len(_WORD_RE.findall(str(phrase or "").lower()))
    for pattern in rc2_patterns or []:
        if not isinstance(pattern, dict):
            continue
        sig = (pattern.get("latest_event") or {}).get("pattern_signature") or {}
        if not isinstance(sig, dict):
            continue
        sig_wc = int(sig.get("word_count_band") or 0)
        if sig_wc and sig_wc != wc:
            continue
        if str(sig.get("failure_category") or "") in _RC2_CATEGORIES:
            return {"matched": True, "failure_category": str(sig.get("failure_category") or ""),
                    "failure_reasons": pattern.get("failure_reasons", [])}
    return {"matched": False, "failure_category": "", "failure_reasons": []}


# ---------------------------------------------------------------------------
# The single greedy painter
# ---------------------------------------------------------------------------
def _paint(
    candidates: List[Dict[str, Any]],
    *,
    article_len: int,
    max_allowed: int,
    min_target: int,
    min_char_distance: int,
    max_family: int,
    max_short_ratio: float,
    max_high_freq_ratio: float,
) -> None:
    """Mutates each candidate's display_status to painted|deferred in rank order,
    honoring spacing/zone/family/short/high-freq budgets. A relaxation pass then
    fills up to min_target from the best deferred items so we never undershoot."""
    max_short = max(1, int(max_allowed * max_short_ratio))
    max_high_freq = max(1, int(max_allowed * max_high_freq_ratio))
    max_per_zone = max(2, int(max_allowed * 0.40))

    painted = 0
    short_painted = 0
    high_freq_painted = 0
    family_counts: Dict[str, int] = {}
    zone_counts: Dict[str, int] = {}
    painted_positions: List[int] = []

    def first_pos(c: Dict[str, Any]) -> int:
        p = c.get("first_position")
        return int(p) if isinstance(p, int) or (isinstance(p, str) and str(p).lstrip("-").isdigit()) else -1

    # ---- primary pass: strict budgets ----
    for c in candidates:
        if painted >= max_allowed:
            c.setdefault("display_status", "deferred_opportunity")
            c.setdefault("deferred_reason", "max_density_reached")
            continue

        pos = first_pos(c)
        zone = _zone(pos, article_len)
        fam = str(c.get("family_root") or c.get("phrase_key") or "")
        toks = _token_count(c.get("phrase"))
        freq = int(c.get("occurrence_count") or 0)

        too_close = any(abs(pos - p) < min_char_distance for p in painted_positions) if pos >= 0 else False
        family_full = family_counts.get(fam, 0) >= max_family
        zone_full = zone != "unknown" and zone_counts.get(zone, 0) >= max_per_zone
        short_full = toks <= 2 and short_painted >= max_short
        high_freq_full = freq >= 5 and high_freq_painted >= max_high_freq

        reason = ("too_close" if too_close else
                  "family_cap" if family_full else
                  "zone_balance" if zone_full else
                  "short_anchor_balance" if short_full else
                  "high_frequency_balance" if high_freq_full else "")

        if reason:
            c["display_status"] = "deferred_opportunity"
            c["deferred_reason"] = reason
            continue

        c["display_status"] = "painted"
        c["runtime_zone"] = zone
        painted += 1
        if pos >= 0:
            painted_positions.append(pos)
        family_counts[fam] = family_counts.get(fam, 0) + 1
        if zone != "unknown":
            zone_counts[zone] = zone_counts.get(zone, 0) + 1
        if toks <= 2:
            short_painted += 1
        if freq >= 5:
            high_freq_painted += 1

    # ---- relaxation pass: reach min_target without breaking the hard cap ----
    if painted < min_target:
        for c in candidates:
            if painted >= min_target or painted >= max_allowed:
                break
            if c.get("display_status") == "painted":
                continue
            # relax spacing/zone/short/freq, but still respect the family cap so
            # one phrase family can't carpet the article.
            fam = str(c.get("family_root") or c.get("phrase_key") or "")
            if family_counts.get(fam, 0) >= max_family:
                continue
            c["display_status"] = "painted"
            c["promoted_to_meet_min"] = True
            painted += 1
            family_counts[fam] = family_counts.get(fam, 0) + 1


def apply_highlight_density(
    *,
    article_text: str,
    selected_candidates: List[Dict[str, Any]],
    workspace_id: str = "default",
    vertical: str = "",
) -> Dict[str, Any]:
    word_count = count_article_words(article_text)
    length_class = classify_article_length(word_count)
    density_range = get_density_range(length_class)
    base_min, base_max = density_range["min"], density_range["max"]

    candidates = list(selected_candidates or [])
    article_len = len(article_text or "")

    rc2_knowledge = get_rejection_pattern_knowledge(workspace_id, vertical)
    rc2_patterns = rc2_knowledge.get("patterns", []) if isinstance(rc2_knowledge, dict) else []

    adaptive = calculate_adaptive_density_limit(candidates, base_max=base_max, base_min=base_min)
    max_allowed = adaptive["adaptive_max"]
    min_target = min(base_min, len(candidates))   # can't paint more than we have

    # RC2 annotation only (never removes)
    rc2_advisory: List[Dict[str, Any]] = []
    for c in candidates:
        adv = _rc2_advisory(c.get("phrase"), rc2_patterns)
        c["dis_density_pattern_match"] = adv["matched"]
        c["dis_density_advisory_only"] = True
        c["dis_density_can_block"] = False
        c["removed_by_dis_pattern_knowledge"] = False
        if adv["matched"]:
            rc2_advisory.append({"phrase": c.get("phrase"),
                                 "rc2_failure_category": adv["failure_category"],
                                 "rc2_failure_reasons": adv["failure_reasons"]})

    # single painter — assigns display_status to every candidate
    _paint(
        candidates,
        article_len=article_len,
        max_allowed=max_allowed,
        min_target=min_target,
        min_char_distance=180,
        max_family=3,
        max_short_ratio=0.40,
        max_high_freq_ratio=0.35,
    )

    painted = [c for c in candidates if c.get("display_status") == "painted"]
    deferred = [c for c in candidates if c.get("display_status") != "painted"]

    return {
        "ok": True,
        "final_highlights": painted,        # what to render as highlights
        "all_candidates": candidates,       # everything, with display_status
        "deferred_opportunities": deferred,  # survive into frontend metadata
        "stats": {
            "article_word_count": word_count,
            "article_length_class": length_class,
            "available_candidates": len(candidates),
            "recommended_min": base_min,
            "recommended_max": base_max,
            "max_allowed": max_allowed,
            "final_highlight_count": len(painted),
            "deferred_count": len(deferred),
            "painted_linked": sum(1 for c in painted if c.get("link_status") == "linked"),
            "painted_unlinked_opportunity": sum(1 for c in painted if c.get("link_status") == "unlinked_opportunity"),
            "adaptive_density": adaptive,
            "rc2_patterns_loaded": len(rc2_patterns),
            "rc2_density_advisory_signals": len(rc2_advisory),
            "density_reason": "rank_first_then_spaced_paint_capped_by_article_length",
        },
    }