"""
Highlight Selection Engine v3

ROLE:
    Receives canonical Phrase Strength Scorer survivors from the certified
    Extractor + Discovery -> Merger -> Guard -> Scorer pipeline.

    This engine does NOT re-decide phrase quality. Its responsibilities are:
    - preserve the complete canonical upstream candidate envelope
    - normalize phrase text only for comparison/matching keys
    - remove exact normalized duplicates
    - confirm that a candidate physically occurs in the article
    - attach resolver signals as ranking metadata only
    - compute selection/ranking scores
    - classify link_status
    - emit every article-present surviving candidate for downstream Density

RANKING AUTHORITY:
    - strength_score from Phrase Strength Scorer is the primary ranking base
      for canonical candidates
    - extractor_intelligence.score remains a backward-compatible fallback
    - resolver and occurrence signals may influence ranking but do not
      independently invalidate phrase quality

POSITION CONTRACT:
    Canonical literal/source positions from upstream remain inside:
        position_intelligence

    Selection Engine article-matching positions use NORMALIZED article space
    and are stored explicitly inside:
        selection_position_intelligence

    For backward compatibility with Highlight Density and existing consumers,
    these normalized selection positions are also exposed as:
        first_position
        all_positions
        occurrence_count

    These top-level aliases MUST NOT be confused with canonical upstream
    position_intelligence.

OUTPUT CONTRACT:
    selected/candidates:
        complete canonical upstream records plus Selection Engine metadata.

    rejected:
        only factual selection-stage exclusions such as empty phrase,
        exact normalized duplicate, or phrase not physically present in article.

    No valid candidate is rejected here merely because resolver evidence is
    absent or because this engine has a separate opinion about phrase quality.
"""

from __future__ import annotations

import copy
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
# Normalization â€” produces a KEY for matching/dedupe. Never overwrites display.
# ---------------------------------------------------------------------------
_WS_RE = re.compile(r"\s+")
_WRAP_RE = re.compile(r"^[\"'\u201c\u201d\u2018\u2019(\[{]+|[\"'\u201c\u201d\u2018\u2019)\]};:,.!?]+$")


def normalize_phrase_key(text: Any) -> str:
    """Lowercased, whitespace-collapsed, wrapper-punct-stripped KEY. For
    comparison only â€” the displayed phrase keeps the extractor's exact text."""
    s = str(text or "").strip().lower()
    s = s.replace("\u2019", "'").replace("\u2018", "'")
    s = _WS_RE.sub(" ", s)
    s = _WRAP_RE.sub("", s)
    return s.strip()


# back-compat alias (some callers imported this name)
normalize_phrase = normalize_phrase_key
def _dis_structure_type(phrase_key: str) -> str:
    """Mirror DIS structural bucketing for pattern compatibility only.

    This does not re-judge candidate quality; it only maps the already-surviving
    candidate into the same structural vocabulary used by DIS signatures.
    """
    count = len(str(phrase_key or "").split())
    if count <= 0:
        return "empty_candidate"
    if count == 1:
        return "single_term_candidate"
    if count == 2:
        return "two_term_candidate"
    if count <= 5:
        return "multi_term_candidate"
    return "extended_candidate_window"



def _display_text(item: Dict[str, Any]) -> str:
    """Extractor's exact display text, tried across the known field names."""
    return (item.get("phrase") or item.get("text")
            or item.get("phrase_text") or item.get("label") or "")


def extract_phrase_candidates(phrase_candidates: Any) -> List[Dict[str, Any]]:
    """Extract candidate dicts from any of the known active-pool shapes."""
    candidates: List[Dict[str, Any]] = []
    if not phrase_candidates:
        return candidates

    raw = None
    if isinstance(phrase_candidates, dict):
        raw = (phrase_candidates.get("phrases")
               or phrase_candidates.get("items")
               or phrase_candidates.get("candidates"))
    elif isinstance(phrase_candidates, list):
        raw = phrase_candidates

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
    raw = (item.get("strength_score")
           if item.get("strength_score") is not None
           else ei.get("score")
           if ei.get("score") is not None
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
        # _safe_float never returns None, so x is always a float here.
        return x * 100.0 if x <= 1.0 else x

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
# RC2 advisory (kept exactly as advisory â€” never blocks)
# ---------------------------------------------------------------------------
_QUALITY_DOMINANCE_MARGIN = 4.0


def _selection_verified_span(item: Dict[str, Any]) -> tuple[int, int] | None:
    """Return Selector-certified original-article span, or None."""
    if item.get("selection_source_span_status") != "verified":
        return None

    span = item.get("selection_source_span")
    if not isinstance(span, dict):
        return None

    start = span.get("start")
    end = span.get("end")

    if type(start) is not int or type(end) is not int:
        return None

    if start < 0 or end <= start:
        return None

    return start, end


def _quality_dominance_adjustment(
    child: Dict[str, Any],
    all_candidates: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Compute bounded ranking-only dominance for one verified occurrence."""
    neutral = {
        "quality_dominance_applied": False,
        "quality_dominance_advisory_only": True,
        "quality_dominance_can_block": False,
        "quality_dominance_penalty": 0.0,
        "quality_dominance_relation": "",
        "quality_dominance_parent_phrase": "",
        "quality_dominance_parent_occurrence_id": "",
        "quality_dominance_reason": "",
    }

    scorer = child.get("scorer_intelligence")
    if not isinstance(scorer, dict):
        return neutral

    containment = scorer.get("containment_quality")
    if not isinstance(containment, dict):
        return neutral

    # Consume only the certified B4 advisory contract.
    if containment.get("advisory_only") is not True:
        return neutral

    if containment.get("can_reject") is not False:
        return neutral

    independence = containment.get("child_independence")
    if not isinstance(independence, dict):
        return neutral

    # Known structurally independent concepts keep full ranking authority.
    if independence.get("has_structural_signal") is True:
        return neutral

    child_span = _selection_verified_span(child)
    if child_span is None:
        return neutral

    child_key = normalize_phrase_key(
        child.get("phrase_key") or _display_text(child)
    )
    if not child_key:
        return neutral

    comparisons = containment.get("comparisons")
    if not isinstance(comparisons, list):
        return neutral

    for comparison in comparisons:
        if not isinstance(comparison, dict):
            continue

        if comparison.get("relation") != "right_extension":
            continue

        try:
            left_added = int(comparison.get("left_added") or 0)
            right_added = int(comparison.get("right_added") or 0)
        except (TypeError, ValueError):
            continue

        if left_added != 0 or right_added != 1:
            continue

        if comparison.get("parent_in_current_snippet") is not True:
            continue

        parent_key = normalize_phrase_key(
            comparison.get("parent_phrase")
        )
        if not parent_key or parent_key == child_key:
            continue

        # Independently verify one-token terminal extension.
        if len(parent_key.split()) != len(child_key.split()) + 1:
            continue

        for parent in all_candidates:
            if parent is child:
                continue

            candidate_parent_key = normalize_phrase_key(
                parent.get("phrase_key") or _display_text(parent)
            )
            if candidate_parent_key != parent_key:
                continue

            parent_span = _selection_verified_span(parent)
            if parent_span is None:
                continue

            # Exact occurrence ownership:
            # right-extension parent must begin exactly where this child begins.
            if parent_span[0] != child_span[0]:
                continue

            if parent_span[1] <= child_span[1]:
                continue

            # Compensate only the incomplete child's inherited phrase-strength
            # advantage. Occurrence and resolver advantages remain untouched.
            child_phrase_score = _extractor_score_0_100(child)
            parent_phrase_score = _extractor_score_0_100(parent)

            phrase_strength_advantage = (
                max(0.0, child_phrase_score - parent_phrase_score) * 0.55
            )

            dominance_penalty = round(
                phrase_strength_advantage + _QUALITY_DOMINANCE_MARGIN,
                4,
            )

            return {
                "quality_dominance_applied": True,
                "quality_dominance_advisory_only": True,
                "quality_dominance_can_block": False,
                "quality_dominance_penalty": dominance_penalty,
                "quality_dominance_relation": "right_extension",
                "quality_dominance_parent_phrase": _display_text(parent),
                "quality_dominance_parent_occurrence_id": str(
                    parent.get("selection_occurrence_id") or ""
                ),
                "quality_dominance_reason": (
                    "verified_same_occurrence_one_token_right_extension"
                ),
            }

    return neutral


_DIS_MAX_PENALTY = 8.0

_RC2_CATEGORIES = {
    "term_order_validity_failure", "fragment_validity_failure",
    "boundary_validity_failure", "candidate_signal_failure",
    "semantic_cohesion_failure", "candidate_window_failure",
    "general_rejection_pattern",
}


def candidate_matches_rc2_pattern(
    phrase_key: str,
    candidate: Dict[str, Any],
    rc2_patterns: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Conservative DIS advisory matcher.

    Exact rejected phrases are never used. A pattern must be structurally
    compatible with the current survivor, and stage-specific provenance is
    used when the canonical candidate envelope actually contains it.
    """
    wc = len(str(phrase_key or "").split())
    structure_type = _dis_structure_type(phrase_key)
    best: Dict[str, Any] | None = None
    best_effective_risk = 0.0

    discovery = candidate.get("discovery_intelligence")
    if not isinstance(discovery, dict):
        discovery = {}

    discovery_component = str(discovery.get("component") or "").strip()
    discovery_capabilities = {
        str(x or "").strip()
        for x in (discovery.get("capabilities") or [])
        if str(x or "").strip()
    }
    single_capability = str(discovery.get("capability") or "").strip()
    if single_capability:
        discovery_capabilities.add(single_capability)

    has_extractor_intelligence = isinstance(
        candidate.get("extractor_intelligence"), dict
    )
    has_guard_intelligence = isinstance(
        candidate.get("guard_intelligence"), dict
    )
    has_scorer_intelligence = isinstance(
        candidate.get("scorer_intelligence"), dict
    )

    for pattern in rc2_patterns or []:
        if not isinstance(pattern, dict):
            continue

        latest_event = pattern.get("latest_event") or {}
        if not isinstance(latest_event, dict):
            continue

        sig = latest_event.get("pattern_signature") or {}
        if not isinstance(sig, dict):
            continue

        failure_category = str(sig.get("failure_category") or "")
        if failure_category not in _RC2_CATEGORIES:
            continue

        sig_wc = int(sig.get("word_count_band") or 0)
        if sig_wc and sig_wc != wc:
            continue

        sig_structure = str(sig.get("structure_type") or "").strip()
        if sig_structure and sig_structure != structure_type:
            continue

        source_stage = str(
            sig.get("source_stage")
            or latest_event.get("pipeline_stage")
            or ""
        ).strip()

        match_confidence = 0.0
        match_basis = ""

        if source_stage == "phrase_discovery_engine":
            evidence = latest_event.get("evidence") or {}
            if not isinstance(evidence, dict):
                evidence = {}

            historical_component = str(
                evidence.get("discovery_component") or ""
            ).strip()
            historical_capability = str(
                evidence.get("discovery_capability") or ""
            ).strip()

            if not discovery_component:
                continue
            if historical_component and historical_component != discovery_component:
                continue
            if historical_capability and historical_capability not in discovery_capabilities:
                continue

            if historical_component and historical_capability:
                match_confidence = 0.70
                match_basis = "discovery_component_capability_structure"
            elif historical_component:
                match_confidence = 0.55
                match_basis = "discovery_component_structure"
            else:
                continue

        elif source_stage == "smart_extractor":
            if not has_extractor_intelligence:
                continue
            match_confidence = 0.45
            match_basis = "extractor_provenance_structure"

        elif source_stage == "candidate_window_guard":
            if not has_guard_intelligence:
                continue
            match_confidence = 0.20
            match_basis = "guard_structure_only_low_specificity"

        elif source_stage == "phrase_strength_scorer":
            if not has_scorer_intelligence:
                continue
            match_confidence = 0.20
            match_basis = "scorer_structure_only_low_specificity"

        else:
            continue

        historical_risk = max(
            0.0,
            min(1.0, _safe_float(pattern.get("historical_risk"))),
        )
        effective_risk = historical_risk * match_confidence

        if effective_risk <= best_effective_risk:
            continue

        best_effective_risk = effective_risk
        best = {
            "matched": True,
            "failure_category": failure_category,
            "failure_reason": str(sig.get("failure_reason") or ""),
            "failure_reasons": pattern.get("failure_reasons", []),
            "source_stage": source_stage,
            "structure_type": sig_structure,
            "word_count_band": sig_wc,
            "historical_risk": round(historical_risk, 4),
            "historical_confidence": round(
                max(0.0, min(1.0, _safe_float(pattern.get("historical_confidence")))),
                4,
            ),
            "match_confidence": round(match_confidence, 4),
            "effective_risk": round(effective_risk, 4),
            "match_basis": match_basis,
            "pattern_id": str(pattern.get("pattern_id") or ""),
        }

    if best is not None:
        return best

    return {
        "matched": False,
        "failure_category": "",
        "failure_reason": "",
        "failure_reasons": [],
        "source_stage": "",
        "structure_type": structure_type,
        "word_count_band": wc,
        "historical_risk": 0.0,
        "historical_confidence": 0.0,
        "match_confidence": 0.0,
        "effective_risk": 0.0,
        "match_basis": "",
        "pattern_id": "",
    }


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
# Public API â€” same signature as v1 (drop-in)
# ---------------------------------------------------------------------------

def _selection_sentence_boundaries(article_text: str) -> list[int]:
    """Compute sentence boundaries once, in original article coordinates."""
    boundaries = [0]

    abbreviations = {
        "dr", "mr", "mrs", "ms", "prof",
        "sr", "jr", "st", "vs", "etc",
        "fig", "no",
    }

    pattern = r'[.!?]+(?:["\u201d\u2019)\]]+)?(?=\s|$)'

    for match in re.finditer(pattern, article_text):
        marker = match.group(0)

        if marker.startswith(".") and marker.count(".") == 1:
            prefix = article_text[
                max(0, match.start() - 24):match.start() + 1
            ]

            token = re.search(r"([A-Za-z]+)\.$", prefix)

            if token and token.group(1).casefold() in abbreviations:
                continue

            if re.search(r"(?:\b[A-Za-z]\.){2,}$", prefix):
                continue

        boundaries.append(match.end())

    boundaries.append(len(article_text))
    return sorted(set(boundaries))


def _selection_sentence_from_span(
    article_text: str,
    source_span: tuple[int, int],
    boundaries: list[int],
) -> dict:
    """Return original-text sentence containing the verified occurrence."""
    from bisect import bisect_left, bisect_right

    start, end = source_span

    left_index = max(0, bisect_right(boundaries, start) - 1)
    right_index = min(
        bisect_left(boundaries, end),
        len(boundaries) - 1,
    )

    sentence_start = boundaries[left_index]
    sentence_end = boundaries[right_index]

    while (
        sentence_start < start
        and article_text[sentence_start].isspace()
    ):
        sentence_start += 1

    while (
        sentence_end > end
        and article_text[sentence_end - 1].isspace()
    ):
        sentence_end -= 1

    return {
        "start": sentence_start,
        "end": sentence_end,
        "coordinate_space": "original_article",
        "text": article_text[sentence_start:sentence_end],
    }



def _selection_paragraph_ranges(article_text: str) -> list[tuple[int, int]]:
    """Find explicit blank-line-separated paragraphs in original coordinates."""
    ranges = []
    cursor = 0

    separators = re.finditer(
        r"\r?\n[ \t]*\r?\n(?:[ \t]*\r?\n)*",
        article_text,
    )

    def add_paragraph(start: int, end: int) -> None:
        while start < end and article_text[start].isspace():
            start += 1

        while end > start and article_text[end - 1].isspace():
            end -= 1

        if start < end:
            ranges.append((start, end))

    for separator in separators:
        add_paragraph(cursor, separator.start())
        cursor = separator.end()

    add_paragraph(cursor, len(article_text))
    return ranges


def _selection_paragraph_from_span(
    article_text: str,
    source_span: tuple[int, int],
    paragraph_ranges: list[tuple[int, int]],
) -> dict | None:
    """Resolve a verified occurrence to one explicit paragraph."""
    from bisect import bisect_right

    if not paragraph_ranges:
        return None

    start, end = source_span
    starts = [paragraph_start for paragraph_start, _ in paragraph_ranges]

    index = bisect_right(starts, start) - 1

    if index < 0:
        return None

    paragraph_start, paragraph_end = paragraph_ranges[index]

    if not (paragraph_start <= start < end <= paragraph_end):
        return None

    return {
        "start": paragraph_start,
        "end": paragraph_end,
        "coordinate_space": "original_article",
        "text": article_text[paragraph_start:paragraph_end],
    }



def _selection_section_context_from_merger(
    item,
    source_span,
    article_text,
):
    """Certify section context against the selected original occurrence."""
    from copy import deepcopy

    evidence = item.get("merger_section_intelligence")

    if not isinstance(evidence, dict):
        return None, "missing_section_evidence"

    section_index = evidence.get("section_index")
    section_path = evidence.get("section_path")

    if (
        evidence.get("status") == "unresolved"
        or type(section_index) is not int
        or not isinstance(section_path, list)
        or not section_path
    ):
        return None, "unresolved"

    # Descriptive hierarchy may be retained as advisory evidence.
    # Do not copy reconstructed heading offsets into original space.
    safe_path = []

    for entry in section_path:
        if not isinstance(entry, dict):
            return None, "unresolved"

        safe_entry = {
            key: deepcopy(value)
            for key, value in entry.items()
            if key != "heading_span"
        }
        safe_entry["heading_span"] = None
        safe_path.append(safe_entry)

    if safe_path[-1].get("section_index") != section_index:
        return None, "unresolved"

    context = {
        "section_index": section_index,
        "source_section_id": evidence.get("source_section_id"),
        "source_sentence_index": evidence.get("source_sentence_index"),
        "section_heading": evidence.get("section_heading", ""),
        "heading_level": evidence.get("heading_level"),
        "parent_section_index": evidence.get("parent_section_index"),
        "section_path": safe_path,
        "section_span": None,
        "direct_section_span": None,
        "heading_span": None,
        "coordinate_space": "unverified_original_article",
    }

    if (
        source_span is None
        or evidence.get("original_article_verified") is not True
        or evidence.get("status") != "verified_original_article"
    ):
        return context, "unverified_original_article"

    def valid_span(span):
        if not isinstance(span, dict):
            return False

        start = span.get("start")
        end = span.get("end")

        return (
            span.get("coordinate_space") == "original_article"
            and type(start) is int
            and type(end) is int
            and 0 <= start < end <= len(article_text)
        )

    section_span = evidence.get("section_span")
    direct_span = evidence.get("direct_section_span")
    heading_span = evidence.get("heading_span")

    if not valid_span(section_span) or not valid_span(direct_span):
        return context, "invalid_section_alignment"

    if not (
        section_span["start"]
        <= direct_span["start"]
        <= source_span[0]
        < source_span[1]
        <= direct_span["end"]
        <= section_span["end"]
    ):
        return context, "invalid_section_alignment"

    if heading_span is not None:
        if not valid_span(heading_span):
            return context, "invalid_section_alignment"

        if not (
            section_span["start"]
            <= heading_span["start"]
            < heading_span["end"]
            <= section_span["end"]
        ):
            return context, "invalid_section_alignment"

        heading_text = str(evidence.get("section_heading") or "")

        if (
            article_text[
                heading_span["start"]:heading_span["end"]
            ] != heading_text
        ):
            return context, "invalid_section_alignment"

    verified_path = deepcopy(section_path)

    for index, entry in enumerate(verified_path):
        if not isinstance(entry, dict):
            return context, "invalid_section_alignment"

        if index > 0:
            if (
                entry.get("parent_section_index")
                != verified_path[index - 1].get("section_index")
            ):
                return context, "invalid_section_alignment"

        ancestor_span = entry.get("heading_span")

        if ancestor_span is not None:
            if not valid_span(ancestor_span):
                return context, "invalid_section_alignment"

            ancestor_text = str(entry.get("heading_text") or "")

            if (
                article_text[
                    ancestor_span["start"]:ancestor_span["end"]
                ] != ancestor_text
            ):
                return context, "invalid_section_alignment"

    context.update({
        "section_path": verified_path,
        "section_span": deepcopy(section_span),
        "direct_section_span": deepcopy(direct_span),
        "heading_span": deepcopy(heading_span),
        "coordinate_space": "original_article",
    })

    return context, "verified_original_article"



def _selection_source_hash_status(
    candidate,
    article_text_sha256,
):
    """Compare only hashes explicitly bound to exact Selector text."""
    import re

    declared = candidate.get("source_hash")

    if declared is None or str(declared).strip() == "":
        return "not_provided"

    basis = str(
        candidate.get("source_hash_basis") or ""
    ).strip().lower()

    if basis != "article_text_utf8_sha256":
        return "unverified_hash_basis"

    supplied = str(declared).strip().lower()

    if re.fullmatch(r"[0-9a-f]{64}", supplied) is None:
        return "invalid_declared_hash"

    if supplied != article_text_sha256:
        return "stale_source_mismatch"

    return "verified_match"


def select_highlight_candidates(
    *,
    workspace_id: str,
    doc_id: str,
    article_text: str,
    phrase_candidates: Any,
    resolved_targets: Any = None,
    vertical: str = "",
) -> Dict[str, Any]:
    rc2_knowledge = get_rejection_pattern_knowledge(workspace_id, vertical)
    rc2_patterns = rc2_knowledge.get("patterns", []) if isinstance(rc2_knowledge, dict) else []

    norm_article = _normalized_article(article_text)
    sentence_boundaries = _selection_sentence_boundaries(article_text)
    paragraph_ranges = _selection_paragraph_ranges(article_text)
    resolver_map = build_resolver_signal_map(resolved_targets)

    raw_candidates = extract_phrase_candidates(phrase_candidates)

    import hashlib
    import json

    selection_source_fingerprint = hashlib.sha256(
        article_text.encode("utf-8")
    ).hexdigest()

    # Validate every incoming candidate BEFORE deduplication or rejection.
    for item in raw_candidates:
        incoming_workspace_id = str(item.get("workspace_id") or "").strip()
        incoming_doc_id = str(item.get("doc_id") or "").strip()

        if incoming_workspace_id and incoming_workspace_id != str(workspace_id).strip():
            raise ValueError("Selected phrase candidate workspace identity mismatch")

        if incoming_doc_id and incoming_doc_id != str(doc_id).strip():
            raise ValueError("Selected phrase candidate document identity mismatch")
        source_hash_status = _selection_source_hash_status(
            item,
            selection_source_fingerprint,
        )

        if source_hash_status == "stale_source_mismatch":
            raise ValueError(
                "Selected phrase candidate source hash mismatch"
            )

        if source_hash_status == "invalid_declared_hash":
            raise ValueError(
                "Selected phrase candidate invalid declared source hash"
            )


    candidates: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []

    # Preserve distinct verified source occurrences.
    # Candidates without a verified span remain phrase-level candidates.
    def _verified_source_span(item):
        info = item.get("position_intelligence")
        if not isinstance(info, dict):
            return None

        if info.get("original_article_span_verified") is False:
            return None

        if (
            info.get("source_coordinate_space")
            == "phrase_discovery_surface_v1"
            or info.get("position_basis")
            == "phrase_discovery_surface_v1"
        ) and info.get("original_article_span_verified") is not True:
            return None

        if info.get("literal_span_verified") is not True:
            return None

        occurrence = info.get("matched_occurrence")
        if not isinstance(occurrence, dict):
            return None

        start = occurrence.get("start")
        end = occurrence.get("end")

        if type(start) is not int or type(end) is not int:
            return None
        if not (0 <= start < end <= len(article_text)):
            return None

        original_phrase = str(_display_text(item))
        if article_text[start:end].casefold() != original_phrase.casefold():
            return None

        return (start, end)

    best_by_occurrence = {}

    for item in raw_candidates:
        original = _display_text(item)
        key = normalize_phrase_key(original)

        if not key:
            rejected.append({
                "phrase": str(original or ""),
                "reason": "rejected_empty_phrase",
            })
            continue

        source_span = _verified_source_span(item)
        identity = (key, source_span)
        incumbent = best_by_occurrence.get(identity)

        if incumbent is None:
            best_by_occurrence[identity] = item
            continue

        # Only a verified original-article span establishes an occurrence.
        duplicate_reason = (
            "rejected_duplicate_occurrence"
            if source_span is not None
            else "rejected_duplicate"
        )

        if _extractor_score_0_100(item) > _extractor_score_0_100(incumbent):
            rejected.append({
                "phrase": _display_text(incumbent),
                "reason": duplicate_reason,
            })
            best_by_occurrence[identity] = item
        else:
            rejected.append({
                "phrase": original,
                "reason": duplicate_reason,
            })

    positioned_keys = {
        key for key, span in best_by_occurrence if span is not None
    }

    for (key, source_span), item in best_by_occurrence.items():
        # An unlocated record is not evidence of an additional occurrence.
        if source_span is None and key in positioned_keys:
            rejected.append({
                "phrase": _display_text(item),
                "reason": "rejected_unlocated_duplicate_of_positioned_phrase",
            })
            continue
        original = _display_text(item)

        positions = _finditer_positions(key, norm_article)
        if not positions:
            # Physical fact, not a quality judgment: can't highlight absent text.
            rejected.append({"phrase": original, "reason": "rejected_not_in_article"})
            continue


        # Map verified original-text span to normalized article coordinates.
        selected_position = positions[0]

        if source_span is not None:
            estimated = len(_normalized_article(article_text[:source_span[0]]))
            nearby = [pos for pos in positions if abs(pos - estimated) <= 2]

            if not nearby:
                rejected.append({
                    "phrase": original,
                    "reason": "rejected_unmapped_source_occurrence",
                    "source_span": {
                        "start": source_span[0],
                        "end": source_span[1],
                    },
                })
                continue

            selected_position = min(
                nearby,
                key=lambda pos: (abs(pos - estimated), pos),
            )

        incoming_workspace_id = str(item.get("workspace_id") or "").strip()
        incoming_doc_id = str(item.get("doc_id") or "").strip()

        if incoming_workspace_id and incoming_workspace_id != str(workspace_id).strip():
            raise ValueError("Selected phrase candidate workspace identity mismatch")
        if incoming_doc_id and incoming_doc_id != str(doc_id).strip():
            raise ValueError("Selected phrase candidate document identity mismatch")

        from copy import deepcopy
        rec = deepcopy(item)

        # Preserve inherited values before Selector-owned assignments.
        # Keep legacy outward fields and ranking behavior unchanged.
        inherited_overwrites = {
            field: deepcopy(item[field])
            for field in (
                'all_positions',
                'article_relevance_score',
                'base_selection_score',
                'cluster_score',
                'dis_advisory_only',
                'dis_can_block',
                'dis_effective_risk',
                'dis_failure_reason',
                'dis_historical_confidence',
                'dis_historical_risk',
                'dis_match_basis',
                'dis_match_confidence',
                'dis_pattern_id',
                'dis_pattern_match',
                'dis_penalty',
                'dis_rejection_reason',
                'dis_signal_reasons',
                'dis_source_stage',
                'doc_id',
                'extractor_score',
                'family_root',
                'first_position',
                'link_status',
                'occurrence_count',
                'phrase',
                'phrase_key',
                'quality_dominance_advisory_only',
                'quality_dominance_applied',
                'quality_dominance_can_block',
                'quality_dominance_parent_occurrence_id',
                'quality_dominance_parent_phrase',
                'quality_dominance_penalty',
                'quality_dominance_reason',
                'quality_dominance_relation',
                'resolver_confidence',
                'resolver_found_target',
                'resolver_relevance_score',
                'section_score',
                'selection_article_text_hash_basis',
                'selection_article_text_sha256',
                'selection_occurrence_id',
                'selection_paragraph_context',
                'selection_paragraph_context_status',
                'selection_phrase_id',
                'selection_position_intelligence',
                'selection_score',
                'selection_section_context',
                'selection_section_context_status',
                'selection_sentence_context',
                'selection_sentence_context_status',
                'selection_source_hash_status',
                'selection_source_span',
                'selection_source_span_status',
                'selection_source_version_status',
                'selection_status',
                'target_score',
                'target_title',
                'target_url',
                'workspace_id',
            )
            if field in item
        }
        if inherited_overwrites:
            rec['selection_inherited_overwrites'] = inherited_overwrites
        rec["workspace_id"] = str(workspace_id).strip()
        rec["doc_id"] = str(doc_id).strip()
        rec["phrase"] = original          # display text, UNMUTATED
        rec["phrase_key"] = key           # matching/dedupe key

        # Preserve authoritative original article-text coordinates.
        # Never substitute normalized offsets for an unverified span.
        if source_span is None:
            rec["selection_source_span"] = None
            rec["selection_source_span_status"] = "unverified"
        else:
            rec["selection_source_span"] = {
                "start": source_span[0],
                "end": source_span[1],
                "coordinate_space": "original_article",
                "text": article_text[source_span[0]:source_span[1]],
            }
            rec["selection_source_span_status"] = "verified"

        # Sentence context is derived only from a verified original span.
        # Keep any upstream sentence_context field unchanged.
        if source_span is None:
            rec["selection_sentence_context"] = None
            rec["selection_sentence_context_status"] = "unverified"
        else:
            rec["selection_sentence_context"] = (
                _selection_sentence_from_span(
                    article_text,
                    source_span,
                    sentence_boundaries,
                )
            )
            rec["selection_sentence_context_status"] = (
                "derived_from_verified_span"
            )

        # Selector-owned deterministic identities.
        # Preserve any upstream phrase_id, candidate_id or occurrence_id.
        identity_base = [
            str(workspace_id).strip(),
            str(doc_id).strip(),
            key,
        ]

        phrase_payload = json.dumps(
            identity_base,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")

        occurrence_payload = json.dumps(
            identity_base + [
                selection_source_fingerprint,
                list(source_span) if source_span is not None else None,
            ],
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")

        # Hash the exact article representation received by Selector.
        # Preserve canonical UUCD and lifecycle metadata independently.
        rec["selection_article_text_sha256"] = (
            selection_source_fingerprint
        )
        rec["selection_article_text_hash_basis"] = (
            "article_text_utf8_sha256"
        )
        rec["selection_source_hash_status"] = (
            _selection_source_hash_status(
                rec,
                selection_source_fingerprint,
            )
        )
        rec["selection_source_version_status"] = (
            "provided_unverified"
            if str(rec.get("source_version") or "").strip()
            else "not_provided"
        )

        rec["selection_phrase_id"] = (
            "sp_" + hashlib.sha256(phrase_payload).hexdigest()[:24]
        )
        rec["selection_occurrence_id"] = (
            "so_" + hashlib.sha256(occurrence_payload).hexdigest()[:24]
        )
        rec["occurrence_count"] = len(positions)
        rec["all_positions"] = positions  # backward-compatible alias: NORMALIZED article space
        rec["first_position"] = selected_position  # backward-compatible alias: NORMALIZED article space
        rec["selection_position_intelligence"] = {
            "coordinate_space": "normalized_article",
            "normalization": "lowercase_whitespace_collapsed",
            "first_position": selected_position,
            "all_positions": list(positions),
            "occurrence_count": len(positions),
            "canonical_position_intelligence_preserved": isinstance(
                rec.get("position_intelligence"), dict
            ),
        }

        # Preserve paragraph context independently of upstream metadata.
        # Only verified source spans can establish paragraph ownership.
        if source_span is None:
            rec["selection_paragraph_context"] = None
            rec["selection_paragraph_context_status"] = "unverified"
        else:
            paragraph_context = _selection_paragraph_from_span(
                article_text,
                source_span,
                paragraph_ranges,
            )

            rec["selection_paragraph_context"] = paragraph_context
            rec["selection_paragraph_context_status"] = (
                "derived_from_verified_span"
                if paragraph_context is not None
                else "unresolved_paragraph_boundary"
            )

        # Selector-owned section context, certified against this
        # selected occurrence. Preserve upstream section evidence.
        (
            rec["selection_section_context"],
            rec["selection_section_context_status"],
        ) = _selection_section_context_from_merger(
            rec,
            source_span,
            article_text,
        )

        rec["family_root"] = _family_root(key)

        # advisory only
        rc2 = candidate_matches_rc2_pattern(key, rec, rc2_patterns)
        rec["dis_pattern_match"] = rc2["matched"]
        rec["dis_rejection_reason"] = rc2["failure_category"]
        rec["dis_failure_reason"] = rc2.get("failure_reason", "")
        rec["dis_signal_reasons"] = rc2["failure_reasons"]
        rec["dis_source_stage"] = rc2.get("source_stage", "")
        rec["dis_pattern_id"] = rc2.get("pattern_id", "")
        rec["dis_match_basis"] = rc2.get("match_basis", "")
        rec["dis_historical_risk"] = _safe_float(rc2.get("historical_risk"))
        rec["dis_historical_confidence"] = _safe_float(rc2.get("historical_confidence"))
        rec["dis_match_confidence"] = _safe_float(rc2.get("match_confidence"))
        rec["dis_effective_risk"] = max(
            0.0,
            min(1.0, _safe_float(rc2.get("effective_risk"))),
        )
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
        base_selection_score = 0.55 * extractor + 0.20 * occ + 0.25 * resolver
        dis_penalty = min(
            _DIS_MAX_PENALTY,
            rec["dis_effective_risk"] * _DIS_MAX_PENALTY,
        )
        rec["base_selection_score"] = round(base_selection_score, 4)
        rec["dis_penalty"] = round(dis_penalty, 4)
        rec["selection_score"] = round(
            max(0.0, base_selection_score - dis_penalty),
            4,
        )
        rec["selection_status"] = "ranked_candidate"

        candidates.append(rec)

    # Resolve relative quality dominance only after every surviving candidate
    # has its Selector-certified occurrence metadata.
    for rec in candidates:
        dominance = _quality_dominance_adjustment(
            rec,
            candidates,
        )
        rec.update(dominance)

        # Ranking-only adjustment. Upstream strength_score remains untouched.
        rec["selection_score"] = round(
            max(
                0.0,
                _safe_float(rec.get("base_selection_score"))
                - _safe_float(rec.get("dis_penalty"))
                - _safe_float(rec.get("quality_dominance_penalty")),
            ),
            4,
        )

    # Highest opportunity first. Linked outranks unlinked at equal score so the
    # density engine paints real links before bare opportunities.
    # FIX (tie-break): at equal score and link_status, prefer the LONGER (more
    # specific) anchor â€” len(phrase_key), not -len(phrase_key).
    candidates.sort(
        key=lambda x: (
            x.get("selection_score", 0.0),
            1 if x.get("link_status") == "linked" else 0,
            len(x.get("phrase_key", "")),
        ),
        reverse=True,
    )

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "doc_id": doc_id,
        # NOTE: "selected" and "candidates" intentionally alias the SAME list of
        # the SAME dicts. Downstream stages (e.g. the density engine) annotate
        # these records in place for frontend metadata; both views reflect that.
        # Deep-copy here if a caller needs an isolated snapshot.
        "selected": candidates,          # every valid opportunity, ranked
        "candidates": candidates,        # alias for clarity
        "all_selected_phrase_candidates": copy.deepcopy(candidates),  # isolated canonical handoff snapshot
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



