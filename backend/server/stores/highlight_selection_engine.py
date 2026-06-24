"""
Highlight Selection Engine v2  (corrected)

ROLE (frozen):
    The Smart Phrase Extractor is the single authority for phrase QUALITY.
    This engine RANKS extractor-approved phrases and tags link opportunity.
    It does NOT re-decide whether a phrase is "good".

What v2 does:
    - extract candidates from the active phrase pool
    - confirm the phrase physically occurs in the article (a fact, not a quality call)
    - attach resolver/target signals as METADATA + ranking input (never a delete gate)
    - tag each phrase  link_status = "linked" | "unlinked_opportunity"
    - compute ONE normalized ranking score (extractor score is the base)
    - sort, and emit EVERY article-present candidate

What v2 deliberately REMOVED (these were hidden phrase validators):
    - weak_phrase_reason / WEAK_PHRASE_PATTERNS            (re-validation by regex)
    - link_worthiness_score + suppress_low_link_worthiness (quality opinion)
    - contextual_naturalness_score + suppression           (quality opinion)
    - phrase_quality_score < 66 hard reject                (re-gating the authority)
    - resolver "no target" / "weak evidence" deletions     (now demoted, not dropped)
    - overwriting item["phrase"] with the normalized form  (mutation)
    Spacing / zone / family-cap now live in the DENSITY engine as display
    selection (deferral), not as deletion of valid opportunities.

Output contract:
    candidates[]  -> every article-present, extractor-approved phrase, ranked,
                     each carrying link_status and a family_root for the density
                     engine. Nothing here is dropped for "quality".
    rejected[]    -> only: empty phrase, exact duplicate, or not-present-in-article.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

try:  # advisory only; never blocks
    from backend.server.stores.dis_rejection_pattern_store import (
        get_rejection_pattern_knowledge,
    )
except Exception:  # pragma: no cover - keeps the module importable standalone
    def get_rejection_pattern_knowledge(*_a: Any, **_k: Any) -> Dict[str, Any]:
        return {"patterns": []}


# ---------------------------------------------------------------------------
# Normalization — produces a KEY for matching/dedupe. Never overwrites display.
# ---------------------------------------------------------------------------
_WS_RE = re.compile(r"\s+")
_WRAP_RE = re.compile(r"^[\"'\u201c\u201d\u2018\u2019(\[{]+|[\"'\u201c\u201d\u2018\u2019)\]};:,.!?]+$")


def normalize_phrase_key(text: Any) -> str:
    """Lowercased, whitespace-collapsed, wrapper-punct-stripped KEY. For
    comparison only — the displayed phrase keeps the extractor's exact text."""
    s = str(text or "").strip().lower()
    s = s.replace("\u2019", "'").replace("\u2018", "'")
    s = _WS_RE.sub(" ", s)
    s = _WRAP_RE.sub("", s)
    return s.strip()


# back-compat alias (some callers imported this name)
normalize_phrase = normalize_phrase_key


def extract_phrase_candidates(active_phrase_pool: Any) -> List[Dict[str, Any]]:
    """Extract candidate dicts from any of the known active-pool shapes."""
    candidates: List[Dict[str, Any]] = []
    if not active_phrase_pool:
        return candidates

    raw = None
    if isinstance(active_phrase_pool, dict):
        raw = (active_phrase_pool.get("phrases")
               or active_phrase_pool.get("items")
               or active_phrase_pool.get("candidates"))
    elif isinstance(active_phrase_pool, list):
        raw = active_phrase_pool

    if isinstance(raw, dict):
        for key, payload in raw.items():
            if isinstance(payload, dict):
                item = dict(payload)
                item.setdefault("phrase", key)
                candidates.append(item)
            else:
                candidates.append({"phrase": key, "value": payload})
    elif isinstance(raw, list):
        for payload in raw:
            if isinstance(payload, dict):
                candidates.append(dict(payload))
            elif isinstance(payload, str):
                candidates.append({"phrase": payload})
    return candidates


# ---------------------------------------------------------------------------
# One article view -> existence, count, position all use the SAME normalization
# (fixes the v1 bug where a phrase could "exist" but report no position).
# ---------------------------------------------------------------------------
def _normalized_article(article_text: str) -> str:
    return _WS_RE.sub(" ", str(article_text or "").lower())


def _finditer_positions(phrase_key: str, norm_article: str) -> List[int]:
    if not phrase_key or not norm_article:
        return []
    pattern = r"(?<!\w)" + re.escape(phrase_key) + r"(?!\w)"
    return [m.start() for m in re.finditer(pattern, norm_article)]


# ---------------------------------------------------------------------------
# Ranking inputs (bounded, explainable). NONE of these can delete a phrase.
# ---------------------------------------------------------------------------
def _extractor_score_0_100(item: Dict[str, Any]) -> float:
    """Carry the extractor's own score forward as the ranking base."""
    ei = item.get("extractor_intelligence") if isinstance(item.get("extractor_intelligence"), dict) else {}
    raw = (ei.get("score")
           if ei.get("score") is not None
           else item.get("strength_score")
           if item.get("strength_score") is not None
           else item.get("quality_score")
           if item.get("quality_score") is not None
           else item.get("score")
           if item.get("score") is not None
           else item.get("phrase_score"))
    try:
        v = float(raw)
    except (TypeError, ValueError):
        return 0.0
    if v <= 1.0:          # 0..1 scale
        v *= 100.0
    return max(0.0, min(100.0, v))


def _occurrence_relevance_0_100(count: int) -> float:
    if count <= 0:
        return 0.0
    if count == 1:
        return 50.0
    if count <= 3:
        return 80.0
    return 100.0


def _resolver_relevance_0_100(sig: Dict[str, Any]) -> float:
    if not sig or not sig.get("resolver_found_target"):
        return 0.0
    def pct(x: float) -> float:
        return x * 100.0 if x is not None and x <= 1.0 else (x or 0.0)
    return max(0.0, min(100.0, max(
        pct(_safe_float(sig.get("resolver_confidence"))),
        pct(_safe_float(sig.get("target_score"))),
        pct(_safe_float(sig.get("cluster_score"))),
        pct(_safe_float(sig.get("section_score"))),
    )))


def _family_root(phrase_key: str) -> str:
    """Last two meaningful tokens -> a family for the density engine to cap.
    Pattern-based, niche-neutral; used for capping, never deletion."""
    weak = {"the", "and", "for", "with", "from", "into", "about", "this",
            "that", "these", "those", "your", "their", "high", "higher",
            "lower", "increased", "reduced", "elevated", "best", "top",
            "simple", "easy", "common", "general", "of", "to", "a", "an"}
    toks = [w for w in phrase_key.split() if w not in weak]
    if len(toks) >= 2:
        return " ".join(toks[-2:])
    if toks:
        return toks[0]
    return phrase_key


# ---------------------------------------------------------------------------
# RC2 advisory (kept exactly as advisory — never blocks)
# ---------------------------------------------------------------------------
_RC2_CATEGORIES = {
    "term_order_validity_failure", "fragment_validity_failure",
    "boundary_validity_failure", "candidate_signal_failure",
    "semantic_cohesion_failure", "candidate_window_failure",
    "general_rejection_pattern",
}


def candidate_matches_rc2_pattern(phrase_key: str, rc2_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
    wc = len(phrase_key.split())
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
            return {"matched": True,
                    "failure_category": str(sig.get("failure_category") or ""),
                    "failure_reasons": pattern.get("failure_reasons", [])}
    return {"matched": False, "failure_category": "", "failure_reasons": []}


# ---------------------------------------------------------------------------
# Resolver signal map (read-only; demote-not-delete is enforced by the caller)
# ---------------------------------------------------------------------------
def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return default if value is None else float(value)
    except (TypeError, ValueError):
        return default


def build_resolver_signal_map(resolved_targets: Any) -> Dict[str, Dict[str, Any]]:
    signal_map: Dict[str, Dict[str, Any]] = {}
    if not resolved_targets:
        return signal_map

    if isinstance(resolved_targets, dict):
        raw = (resolved_targets.get("items") or resolved_targets.get("resolved_targets")
               or resolved_targets.get("targets") or resolved_targets.get("results") or [])
    elif isinstance(resolved_targets, list):
        raw = resolved_targets
    else:
        raw = []

    for rec in raw:
        if not isinstance(rec, dict):
            continue
        phrase = (rec.get("phrase") or rec.get("anchor") or rec.get("anchor_text")
                  or rec.get("source_phrase") or rec.get("matched_phrase") or "")
        key = normalize_phrase_key(phrase)
        if not key:
            continue
        target = rec.get("target") or rec.get("best_target") or rec.get("resolved_target") or rec
        if not isinstance(target, dict):
            target = rec
        signal_map[key] = {
            "resolver_found_target": bool(rec.get("url") or rec.get("target_url")
                                          or target.get("url") or target.get("target_url")),
            "resolver_confidence": max(_safe_float(rec.get("resolver_confidence")),
                                       _safe_float(rec.get("confidence")),
                                       _safe_float(rec.get("score")),
                                       _safe_float(target.get("resolver_confidence"))),
            "target_score": max(_safe_float(rec.get("target_score")),
                                _safe_float(target.get("target_score")),
                                _safe_float(target.get("semantic_route_score"))),
            "cluster_score": max(_safe_float(rec.get("cluster_score")),
                                 _safe_float(target.get("cluster_score")),
                                 1.0 if (target.get("cluster_names") or target.get("cluster_keywords")) else 0.0),
            "section_score": max(_safe_float(rec.get("section_score")),
                                 _safe_float(target.get("section_score")),
                                 1.0 if (target.get("section_names") or target.get("section_keywords")) else 0.0),
            "target_url": rec.get("target_url") or rec.get("url") or target.get("url") or "",
            "target_title": rec.get("target_title") or target.get("title") or target.get("label") or "",
        }
    return signal_map


# ---------------------------------------------------------------------------
# Public API — same signature as v1 (drop-in)
# ---------------------------------------------------------------------------
def select_highlight_candidates(
    *,
    workspace_id: str,
    doc_id: str,
    article_text: str,
    active_phrase_pool: Any,
    resolved_targets: Any = None,
    vertical: str = "",
) -> Dict[str, Any]:
    rc2_knowledge = get_rejection_pattern_knowledge(workspace_id, vertical)
    rc2_patterns = rc2_knowledge.get("patterns", []) if isinstance(rc2_knowledge, dict) else []

    norm_article = _normalized_article(article_text)
    resolver_map = build_resolver_signal_map(resolved_targets)

    raw_candidates = extract_phrase_candidates(active_phrase_pool)

    candidates: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    seen: set = set()

    for item in raw_candidates:
        original = (item.get("phrase") or item.get("text")
                    or item.get("phrase_text") or item.get("label") or "")
        key = normalize_phrase_key(original)

        if not key:
            rejected.append({"phrase": str(original or ""), "reason": "rejected_empty_phrase"})
            continue
        if key in seen:
            rejected.append({"phrase": original, "reason": "rejected_duplicate"})
            continue
        seen.add(key)

        positions = _finditer_positions(key, norm_article)
        if not positions:
            # Physical fact, not a quality judgment: can't highlight absent text.
            rejected.append({"phrase": original, "reason": "rejected_not_in_article"})
            continue

        rec = dict(item)
        rec["phrase"] = original          # display text, UNMUTATED
        rec["phrase_key"] = key           # matching/dedupe key
        rec["occurrence_count"] = len(positions)
        rec["all_positions"] = positions
        rec["first_position"] = positions[0]
        rec["family_root"] = _family_root(key)

        # advisory only
        rc2 = candidate_matches_rc2_pattern(key, rc2_patterns)
        rec["dis_pattern_match"] = rc2["matched"]
        rec["dis_rejection_reason"] = rc2["failure_category"]
        rec["dis_signal_reasons"] = rc2["failure_reasons"]
        rec["dis_advisory_only"] = True
        rec["dis_can_block"] = False

        # resolver signals -> metadata + ranking input, NEVER a delete gate
        sig = resolver_map.get(key, {})
        rec["resolver_found_target"] = bool(sig.get("resolver_found_target"))
        rec["resolver_confidence"] = _safe_float(sig.get("resolver_confidence"))
        rec["target_score"] = _safe_float(sig.get("target_score"))
        rec["cluster_score"] = _safe_float(sig.get("cluster_score"))
        rec["section_score"] = _safe_float(sig.get("section_score"))
        rec["target_url"] = sig.get("target_url", "")
        rec["target_title"] = sig.get("target_title", "")
        rec["link_status"] = "linked" if rec["resolver_found_target"] else "unlinked_opportunity"

        # ONE normalized ranking score (no term re-judges validity)
        extractor = _extractor_score_0_100(rec)
        occ = _occurrence_relevance_0_100(rec["occurrence_count"])
        resolver = _resolver_relevance_0_100(sig)
        rec["extractor_score"] = round(extractor, 2)
        rec["article_relevance_score"] = round(occ, 2)
        rec["resolver_relevance_score"] = round(resolver, 2)
        rec["selection_score"] = round(0.55 * extractor + 0.20 * occ + 0.25 * resolver, 4)
        rec["selection_status"] = "ranked_candidate"

        candidates.append(rec)

    # Highest opportunity first. Linked outranks unlinked at equal score so the
    # density engine paints real links before bare opportunities.
    candidates.sort(
        key=lambda x: (
            x.get("selection_score", 0.0),
            1 if x.get("link_status") == "linked" else 0,
            -len(x.get("phrase_key", "")),
        ),
        reverse=True,
    )

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "doc_id": doc_id,
        "selected": candidates,          # every valid opportunity, ranked
        "candidates": candidates,        # alias for clarity
        "rejected": rejected,            # only empty / duplicate / not-in-article
        "stats": {
            "total_candidates": len(raw_candidates),
            "ranked_count": len(candidates),
            "linked_count": sum(1 for c in candidates if c["link_status"] == "linked"),
            "unlinked_opportunity_count": sum(1 for c in candidates if c["link_status"] == "unlinked_opportunity"),
            "rejected_count": len(rejected),
            "rc2_patterns_loaded": len(rc2_patterns),
            "rc2_advisory_signals": sum(1 for c in candidates if c.get("dis_pattern_match")),
        },
    }