"""
LinkCraftor Linking Scorer.

Phase 2.3.8 — canonical input validation foundation.

Consumes the isolated canonical Phrase Selector handoff.
Does not modify upstream candidates.
Does not score, classify, resolve targets, or insert links.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional


SCORER_CONTRACT_VERSION = "2.5"
MAX_HIGHLIGHT_SETS = 3


class LinkingScorerInputError(ValueError):
    """Invalid or incomplete canonical Linking Scorer input."""


def _required_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LinkingScorerInputError(
            f"{field} must be a non-empty string."
        )
    return value.strip()


def prepare_linking_scorer_input(
    *,
    workspace_id: str,
    document_id: str,
    content_version: str,
    article_text: str,
    selected_candidates: List[Dict[str, Any]],
    existing_links: List[Dict[str, Any]],
    article_html: Optional[str] = None,
    article_sections: Optional[List[Dict[str, Any]]] = None,
    semantic_enrichment: Optional[Dict[str, Any]] = None,
    selection_stats: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Validate and isolate the inputs for the future Linking Scorer.

    Existing links must be provided explicitly, even when empty.
    Unverified section information may be omitted.
    Missing semantic evidence is not treated as negative evidence.

    The caller is responsible for supplying an authoritative
    content version and an accurate existing-link inventory.
    """

    workspace_id = _required_string(
        workspace_id, "workspace_id"
    )
    document_id = _required_string(
        document_id, "document_id"
    )
    content_version = _required_string(
        content_version, "content_version"
    )

    if not isinstance(article_text, str) or not article_text.strip():
        raise LinkingScorerInputError(
            "article_text must contain article content."
        )

    if article_html is not None and not isinstance(article_html, str):
        raise LinkingScorerInputError(
            "article_html must be a string or None."
        )

    if not isinstance(selected_candidates, list):
        raise LinkingScorerInputError(
            "selected_candidates must be a list."
        )

    if not isinstance(existing_links, list):
        raise LinkingScorerInputError(
            "existing_links must be an explicit list."
        )

    if article_sections is not None and not isinstance(
        article_sections, list
    ):
        raise LinkingScorerInputError(
            "article_sections must be a list or None."
        )

    if semantic_enrichment is not None and not isinstance(
        semantic_enrichment, dict
    ):
        raise LinkingScorerInputError(
            "semantic_enrichment must be a dict or None."
        )

    if selection_stats is not None and not isinstance(
        selection_stats, dict
    ):
        raise LinkingScorerInputError(
            "selection_stats must be a dict or None."
        )

    for index, candidate in enumerate(selected_candidates):
        if not isinstance(candidate, dict):
            raise LinkingScorerInputError(
                f"Candidate {index} must be a dictionary."
            )

        if not isinstance(candidate.get("phrase"), str) or not (
            candidate["phrase"].strip()
        ):
            raise LinkingScorerInputError(
                f"Candidate {index} has no valid phrase."
            )

    for index, link in enumerate(existing_links):
        if not isinstance(link, dict):
            raise LinkingScorerInputError(
                f"Existing link {index} must be a dictionary."
            )

    if article_sections is not None:
        for index, section in enumerate(article_sections):
            if not isinstance(section, dict):
                raise LinkingScorerInputError(
                    f"Article section {index} must be a dictionary."
                )

    return {
        "contract_version": SCORER_CONTRACT_VERSION,
        "document_context": {
            "workspace_id": workspace_id,
            "document_id": document_id,
            "content_version": content_version,
        },
        "article": {
            "text": article_text,
            "html": article_html,
            "existing_links": copy.deepcopy(existing_links),
            "sections": copy.deepcopy(article_sections),
        },
        "candidates": copy.deepcopy(selected_candidates),
        "semantic_enrichment": copy.deepcopy(semantic_enrichment),
        "semantic_evidence_status": (
            "provided"
            if semantic_enrichment is not None
            else "not_provided"
        ),
        "selection_stats": copy.deepcopy(selection_stats or {}),
        "policy": {
            "max_highlight_sets": MAX_HIGHLIGHT_SETS,
            "minimum_highlights": 0,
            "allow_weak_padding": False,
        },
    }


def calculate_article_link_capacity(
    prepared_input: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Calculate the approved provisional article-level link capacity.

    One total link per 200 eligible words; maximum 40.
    Existing eligible-body hyperlinks consume capacity.

    This is a ceiling, never a minimum or fill target.
    """

    if not isinstance(prepared_input, dict):
        raise LinkingScorerInputError(
            "prepared_input must be a dictionary."
        )

    article = prepared_input.get("article")

    if not isinstance(article, dict):
        raise LinkingScorerInputError(
            "Prepared input has no valid article."
        )

    text = article.get("text")
    links = article.get("existing_links")

    if not isinstance(text, str) or not text.strip():
        raise LinkingScorerInputError(
            "Article text is missing or invalid."
        )

    if not isinstance(links, list):
        raise LinkingScorerInputError(
            "Existing-link inventory is missing or invalid."
        )

    if any(not isinstance(link, dict) for link in links):
        raise LinkingScorerInputError(
            "Existing-link inventory contains invalid records."
        )

    # The prepared article text must contain eligible article-body
    # content only. Its authoritative extraction is owned upstream.
    eligible_word_count = len(text.split())

    gross_capacity = min(
        40,
        eligible_word_count // 200,
    )

    # Each record represents one actual hyperlink occurrence
    # in the eligible article body, not one unique destination.
    existing_link_count = len(links)

    remaining_capacity = max(
        0,
        gross_capacity - existing_link_count,
    )

    return {
        "eligible_word_count": eligible_word_count,
        "gross_article_capacity": gross_capacity,
        "existing_link_count": existing_link_count,
        "remaining_article_capacity": remaining_capacity,
        "minimum_required_highlights": 0,
        "capacity_is_ceiling_only": True,
        "capacity_policy": "provisional_200_words_max_40",
    }


def calculate_section_link_capacity(
    *,
    section_word_count: int,
    existing_section_links: int,
    article_remaining_capacity: int,
) -> Dict[str, Any]:
    """
    Calculate capacity for a verified section or verified
    logically grouped short sections.

    Uses the approved provisional 1-link-per-200-word
    section ceiling, rounded upward.

    Counts actual existing hyperlink occurrences.
    Never forces a minimum number of new highlights.

    Section ownership, short-section grouping, and
    existing-link counts must be verified upstream.
    """

    values = {
        "section_word_count": section_word_count,
        "existing_section_links": existing_section_links,
        "article_remaining_capacity": article_remaining_capacity,
    }

    for name, value in values.items():
        if type(value) is not int or value < 0:
            raise LinkingScorerInputError(
                f"{name} must be a non-negative integer."
            )

    gross_section_capacity = (
        (section_word_count + 199) // 200
        if section_word_count > 0
        else 0
    )

    remaining_section_capacity = max(
        0,
        gross_section_capacity - existing_section_links,
    )

    maximum_new_links = min(
        remaining_section_capacity,
        article_remaining_capacity,
    )

    return {
        "section_word_count": section_word_count,
        "gross_section_capacity": gross_section_capacity,
        "existing_section_links": existing_section_links,
        "remaining_section_capacity": remaining_section_capacity,
        "article_remaining_capacity": article_remaining_capacity,
        "maximum_new_links": maximum_new_links,
        "minimum_required_links": 0,
        "capacity_is_ceiling_only": True,
        "capacity_policy": "provisional_section_200_words",
    }


def calculate_unified_link_capacity(
    prepared_input: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Combine approved article and section capacity calculations.

    Section ceilings are used only when all section evidence
    is verified, covers the eligible article, and reconciles
    with its existing-link inventory.

    Short sections must already be logically grouped and
    verified upstream. No grouping is invented here.
    """

    article_capacity = calculate_article_link_capacity(
        prepared_input
    )

    result = {
        "article_capacity": article_capacity,
        "section_capacity_status": "unavailable",
        "section_capacities": [],
        "maximum_new_links": article_capacity[
            "remaining_article_capacity"
        ],
        "minimum_required_links": 0,
        "capacity_is_ceiling_only": True,
    }

    article = prepared_input["article"]
    sections = article.get("sections")

    if not isinstance(sections, list) or not sections:
        return result

    required_fields = (
        "section_id",
        "eligible_word_count",
        "existing_link_count",
    )

    verified = []
    seen_ids = set()

    for section in sections:
        if not isinstance(section, dict):
            return result

        if section.get("verified") is not True:
            return result

        if any(field not in section for field in required_fields):
            return result

        section_id = section["section_id"]
        words = section["eligible_word_count"]
        links = section["existing_link_count"]

        if not isinstance(section_id, str) or not section_id.strip():
            return result

        if section_id in seen_ids:
            return result

        if type(words) is not int or words < 0:
            return result

        if type(links) is not int or links < 0:
            return result

        # Short sections require verified upstream grouping.
        if 0 < words < 100:
            return result

        seen_ids.add(section_id)

        verified.append({
            "section_id": section_id,
            "eligible_word_count": words,
            "existing_link_count": links,
        })

    if sum(s["eligible_word_count"] for s in verified) != (
        article_capacity["eligible_word_count"]
    ):
        return result

    if sum(s["existing_link_count"] for s in verified) != (
        article_capacity["existing_link_count"]
    ):
        return result

    for section in verified:
        capacity = calculate_section_link_capacity(
            section_word_count=section["eligible_word_count"],
            existing_section_links=section["existing_link_count"],
            article_remaining_capacity=article_capacity[
                "remaining_article_capacity"
            ],
        )

        result["section_capacities"].append({
            "section_id": section["section_id"],
            **capacity,
        })

    result["section_capacity_status"] = "verified"

    return result


def verify_linking_candidate_occurrence(
    candidate: Dict[str, Any],
    article_text: str,
) -> Dict[str, Any]:
    """
    Verify a Selector-owned occurrence against the exact
    original article representation.

    This validates occurrence identity and location only.
    It does not authorize linking or verify HTML mapping.
    """
    import hashlib

    def fail(reason: str) -> Dict[str, Any]:
        return {
            "verified": False,
            "reason": reason,
            "occurrence_span": None,
        }

    if not isinstance(candidate, dict):
        return fail("invalid_candidate")

    if not isinstance(article_text, str):
        return fail("invalid_article_text")

    if candidate.get("selection_source_span_status") != "verified":
        return fail("unverified_source_span")

    expected_hash = candidate.get("selection_article_text_sha256")

    if not isinstance(expected_hash, str) or not expected_hash:
        return fail("missing_article_fingerprint")

    actual_hash = hashlib.sha256(
        article_text.encode("utf-8")
    ).hexdigest()

    if actual_hash != expected_hash:
        return fail("article_fingerprint_mismatch")

    span = candidate.get("selection_source_span")

    if not isinstance(span, dict):
        return fail("missing_source_span")

    if span.get("coordinate_space") != "original_article":
        return fail("invalid_coordinate_space")

    start = span.get("start")
    end = span.get("end")

    if (
        type(start) is not int
        or type(end) is not int
        or start < 0
        or end <= start
        or end > len(article_text)
    ):
        return fail("invalid_source_coordinates")

    actual_text = article_text[start:end]

    if actual_text != span.get("text"):
        return fail("source_span_text_mismatch")

    phrase = candidate.get("phrase")

    if not isinstance(phrase, str) or not phrase.strip():
        return fail("invalid_phrase")

    def normalize(value: str) -> str:
        return " ".join(value.casefold().split())

    if normalize(actual_text) != normalize(phrase):
        return fail("phrase_span_mismatch")

    return {
        "verified": True,
        "reason": "verified_original_article_occurrence",
        "occurrence_span": {
            "start": start,
            "end": end,
            "coordinate_space": "original_article",
            "text": actual_text,
        },
    }


def evaluate_linking_candidate_preconditions(
    candidate: Dict[str, Any],
    prepared_input: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Validate prerequisites for comparative linking ranking.

    Does not calculate new phrase quality scores, subtract
    DIS penalties, approve destination URLs, or insert links.

    Existing-link coordinates must be verifiable before
    declaring an occurrence free from link conflicts.
    """
    import math

    def result(status: str, reason: str, span=None):
        return {
            "eligible_for_ranking": status == "passed",
            "status": status,
            "reason": reason,
            "occurrence_span": copy.deepcopy(span),
        }

    if not isinstance(candidate, dict):
        return result("rejected", "invalid_candidate")

    if not isinstance(prepared_input, dict):
        return result("rejected", "invalid_prepared_input")

    article = prepared_input.get("article")
    if not isinstance(article, dict):
        return result("rejected", "invalid_article_context")

    text = article.get("text")
    links = article.get("existing_links")

    if not isinstance(text, str) or not isinstance(links, list):
        return result("rejected", "invalid_article_evidence")

    for field in (
        "selection_phrase_id",
        "selection_occurrence_id",
    ):
        value = candidate.get(field)
        if not isinstance(value, str) or not value.strip():
            return result("rejected", f"missing_{field}")

    if candidate.get("selection_status") != "ranked_candidate":
        return result("rejected", "invalid_selector_status")

    score = candidate.get("selection_score")
    if (
        isinstance(score, bool)
        or not isinstance(score, (int, float))
        or not math.isfinite(score)
        or not 0 <= score <= 100
    ):
        return result("rejected", "invalid_selection_score")

    occurrence = verify_linking_candidate_occurrence(
        candidate, text
    )

    if not occurrence["verified"]:
        return result("rejected", occurrence["reason"])

    span = occurrence["occurrence_span"]
    start, end = span["start"], span["end"]

    for index, link in enumerate(links):
        if not isinstance(link, dict):
            return result("deferred", "invalid_existing_link_inventory")

        if link.get("coordinate_space") != "original_article":
            return result(
                "deferred",
                "existing_link_coordinates_unverified",
            )

        a, b = link.get("start"), link.get("end")
        if (
            type(a) is not int
            or type(b) is not int
            or a < 0
            or b <= a
            or b > len(text)
        ):
            return result(
                "deferred",
                "existing_link_coordinates_unverified",
            )

        if start < b and a < end:
            return result(
                "rejected",
                "existing_link_overlap",
                span,
            )

    return result(
        "passed",
        "candidate_preconditions_verified",
        span,
    )


def rank_linking_candidates(
    prepared_input: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Produce a stable, eligibility-filtered comparative ranking.

    Preserve Selector ranking and all upstream evidence.
    Do not reapply DIS or quality-dominance penalties.
    Do not invent semantic scores or final linking weights.

    This is NOT final highlight allocation or URL approval.
    """

    if not isinstance(prepared_input, dict):
        raise LinkingScorerInputError(
            "prepared_input must be a dictionary."
        )

    candidates = prepared_input.get("candidates")

    if not isinstance(candidates, list):
        raise LinkingScorerInputError(
            "Canonical candidates are missing or invalid."
        )

    ranked = []
    deferred = []
    rejected = []

    for index, candidate in enumerate(candidates):
        evaluation = evaluate_linking_candidate_preconditions(
            candidate,
            prepared_input,
        )

        record = {
            "selection_phrase_id": candidate.get(
                "selection_phrase_id"
            ) if isinstance(candidate, dict) else None,
            "selection_occurrence_id": candidate.get(
                "selection_occurrence_id"
            ) if isinstance(candidate, dict) else None,
            "phrase": candidate.get(
                "phrase"
            ) if isinstance(candidate, dict) else None,
            "selection_score": candidate.get(
                "selection_score"
            ) if isinstance(candidate, dict) else None,
            "selector_input_order": index,
            "status": evaluation["status"],
            "reason": evaluation["reason"],
            "occurrence_span": copy.deepcopy(
                evaluation["occurrence_span"]
            ),
            "candidate_evidence": copy.deepcopy(candidate),
        }

        if evaluation["eligible_for_ranking"]:
            ranked.append(record)
        elif evaluation["status"] == "deferred":
            deferred.append(record)
        else:
            rejected.append(record)

    # Python sort is stable: equal scores retain Selector order.
    ranked.sort(
        key=lambda item: item["selection_score"],
        reverse=True,
    )

    for position, record in enumerate(ranked, start=1):
        record["comparative_rank"] = position
        record["status"] = "eligible_ranked"
        record["reason"] = "upstream_score_order_preserved"

    return {
        "ok": True,
        "ranking_stage": "preliminary_comparative",
        "semantic_evidence_status": prepared_input.get(
            "semantic_evidence_status",
            "not_provided",
        ),
        "ranked_opportunities": ranked,
        "deferred_opportunities": deferred,
        "rejected_opportunities": rejected,
        "stats": {
            "input_candidate_count": len(candidates),
            "ranked_count": len(ranked),
            "deferred_count": len(deferred),
            "rejected_count": len(rejected),
        },
        "final_highlights_selected": False,
        "resolver_authorization_performed": False,
    }


def assess_ranked_linking_quality(
    prepared_input: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Assess candidates using the approved Selector ranking
    and already-verified contextual evidence.

    Do not rescore phrase strength, reapply DIS penalties,
    invent semantic scores, or select final highlights.

    Final selection and article-wide diversity follow later.
    """

    ranked_result = rank_linking_candidates(prepared_input)

    assessed = []

    for record in ranked_result["ranked_opportunities"]:
        candidate = record["candidate_evidence"]

        sentence_verified = (
            candidate.get("selection_sentence_context_status")
            == "derived_from_verified_span"
        )

        paragraph_verified = (
            candidate.get("selection_paragraph_context_status")
            == "derived_from_verified_span"
        )

        section_status = candidate.get(
            "selection_section_context_status"
        )

        section_available = (
            isinstance(
                candidate.get("selection_section_context"),
                dict,
            )
            and bool(section_status)
            and section_status != "unverified"
        )

        assessed_record = copy.deepcopy(record)

        assessed_record["quality_assessment"] = {
            "upstream_selection_score": record[
                "selection_score"
            ],
            "selection_score_reused": True,
            "dis_penalty_reapplied": False,
            "quality_dominance_penalty_reapplied": False,
            "source_occurrence_verified": True,
            "sentence_context_verified": sentence_verified,
            "paragraph_context_verified": paragraph_verified,
            "section_context_available": section_available,
            "semantic_evidence_status": prepared_input.get(
                "semantic_evidence_status",
                "not_provided",
            ),
            "semantic_score_invented": False,
            "final_linking_score": None,
            "final_highlight_selected": False,
            "resolver_authorized": False,
        }

        assessed_record["status"] = "quality_ranked"
        assessed_record["reason"] = (
            "eligible_with_preserved_upstream_quality"
        )

        assessed.append(assessed_record)

    return {
        "ok": True,
        "assessment_stage": "upstream_quality_and_context",
        "quality_ranked_opportunities": assessed,
        "deferred_opportunities": copy.deepcopy(
            ranked_result["deferred_opportunities"]
        ),
        "rejected_opportunities": copy.deepcopy(
            ranked_result["rejected_opportunities"]
        ),
        "stats": {
            **ranked_result["stats"],
            "quality_assessed_count": len(assessed),
        },
        "final_highlights_selected": False,
        "resolver_authorization_performed": False,
    }


def enforce_article_wide_diversity(
    prepared_input: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Apply article-wide capacity, occurrence overlap, and
    duplicate-anchor safeguards to quality-assessed candidates.

    Does not invent numeric spacing or family limits.
    Does not perform final semantic approval, section allocation,
    target resolution, or actual document insertion.
    """

    quality_result = assess_ranked_linking_quality(
        prepared_input
    )

    capacity = calculate_unified_link_capacity(
        prepared_input
    )

    article_limit = capacity["maximum_new_links"]

    selected = []
    deferred = []
    selected_spans = []
    selected_phrases = set()

    def defer(record, reason):
        item = copy.deepcopy(record)
        item["status"] = "deferred_diversity"
        item["reason"] = reason
        deferred.append(item)

    for record in quality_result[
        "quality_ranked_opportunities"
    ]:
        span = record.get("occurrence_span")

        if not isinstance(span, dict):
            defer(record, "missing_verified_occurrence")
            continue

        start = span.get("start")
        end = span.get("end")

        if (
            type(start) is not int
            or type(end) is not int
            or start < 0
            or end <= start
        ):
            defer(record, "invalid_verified_occurrence")
            continue

        phrase_key = " ".join(
            str(record.get("phrase") or "").casefold().split()
        )

        if not phrase_key:
            defer(record, "empty_anchor")
            continue

        if phrase_key in selected_phrases:
            defer(record, "duplicate_anchor")
            continue

        if any(
            start < existing_end and existing_start < end
            for existing_start, existing_end in selected_spans
        ):
            defer(record, "highlight_overlap")
            continue

        if len(selected) >= article_limit:
            defer(record, "article_capacity_reached")
            continue

        item = copy.deepcopy(record)
        item["status"] = "diversity_qualified"
        item["reason"] = "article_diversity_checks_passed"

        selected.append(item)
        selected_spans.append((start, end))
        selected_phrases.add(phrase_key)

    return {
        "ok": True,
        "selection_stage": "article_diversity_preliminary",
        "diversity_qualified_opportunities": selected,
        "diversity_deferred_opportunities": deferred,
        "precondition_deferred_opportunities": copy.deepcopy(
            quality_result["deferred_opportunities"]
        ),
        "rejected_opportunities": copy.deepcopy(
            quality_result["rejected_opportunities"]
        ),
        "allocation": capacity,
        "stats": {
            "quality_assessed_count": len(
                quality_result["quality_ranked_opportunities"]
            ),
            "diversity_qualified_count": len(selected),
            "diversity_deferred_count": len(deferred),
            "article_capacity": article_limit,
        },
        "final_highlights_selected": False,
        "resolver_authorization_performed": False,
    }


def enforce_section_aware_diversity(
    prepared_input: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Enforce approved article and verified section capacities.

    Uses original-article section spans when available.
    Falls back to article safeguards if verified section
    mapping is unavailable.

    Does not invent spacing limits or select final links.
    """

    capacity = calculate_unified_link_capacity(
        prepared_input
    )

    sections = prepared_input["article"].get("sections")
    text = prepared_input["article"]["text"]

    section_map = {}

    if capacity["section_capacity_status"] == "verified":
        valid = True
        ranges = []

        for section in sections:
            span = section.get("source_span")

            if not isinstance(span, dict):
                valid = False
                break

            start = span.get("start")
            end = span.get("end")

            if (
                span.get("coordinate_space") != "original_article"
                or type(start) is not int
                or type(end) is not int
                or start < 0
                or end <= start
                or end > len(text)
            ):
                valid = False
                break

            ranges.append((start, end, section["section_id"]))

        if valid:
            ordered = sorted(ranges)
            if any(
                ordered[i][0] < ordered[i - 1][1]
                for i in range(1, len(ordered))
            ):
                valid = False

        if valid:
            limits = {
                item["section_id"]: item["remaining_section_capacity"]
                for item in capacity["section_capacities"]
            }
            section_map = {
                section_id: {
                    "start": start,
                    "end": end,
                    "limit": limits[section_id],
                }
                for start, end, section_id in ranges
            }

    if not section_map:
        fallback = enforce_article_wide_diversity(
            prepared_input
        )
        fallback["section_enforcement"] = (
            "article_fallback_unverified_section_spans"
        )
        return fallback

    quality = assess_ranked_linking_quality(
        prepared_input
    )

    selected = []
    deferred = []
    selected_spans = []
    selected_phrases = set()
    section_counts = {
        section_id: 0 for section_id in section_map
    }

    article_limit = capacity["maximum_new_links"]

    def defer(record, reason):
        item = copy.deepcopy(record)
        item["status"] = "deferred_diversity"
        item["reason"] = reason
        deferred.append(item)

    for record in quality["quality_ranked_opportunities"]:
        span = record["occurrence_span"]
        start = span["start"]
        end = span["end"]

        owners = [
            section_id
            for section_id, section in section_map.items()
            if section["start"] <= start
            and end <= section["end"]
        ]

        if len(owners) != 1:
            defer(record, "section_ownership_unverified")
            continue

        section_id = owners[0]

        phrase_key = " ".join(
            str(record.get("phrase") or "").casefold().split()
        )

        if phrase_key in selected_phrases:
            defer(record, "duplicate_anchor")
            continue

        if any(
            start < previous_end and previous_start < end
            for previous_start, previous_end in selected_spans
        ):
            defer(record, "highlight_overlap")
            continue

        if len(selected) >= article_limit:
            defer(record, "article_capacity_reached")
            continue

        if section_counts[section_id] >= (
            section_map[section_id]["limit"]
        ):
            defer(record, "section_capacity_reached")
            continue

        item = copy.deepcopy(record)
        item["section_id"] = section_id
        item["status"] = "diversity_qualified"
        item["reason"] = "article_and_section_checks_passed"

        selected.append(item)
        selected_spans.append((start, end))
        selected_phrases.add(phrase_key)
        section_counts[section_id] += 1

    return {
        "ok": True,
        "selection_stage": "section_aware_diversity",
        "section_enforcement": "verified",
        "diversity_qualified_opportunities": selected,
        "diversity_deferred_opportunities": deferred,
        "precondition_deferred_opportunities": copy.deepcopy(
            quality["deferred_opportunities"]
        ),
        "rejected_opportunities": copy.deepcopy(
            quality["rejected_opportunities"]
        ),
        "allocation": capacity,
        "section_selected_counts": section_counts,
        "stats": {
            "quality_assessed_count": len(
                quality["quality_ranked_opportunities"]
            ),
            "diversity_qualified_count": len(selected),
            "diversity_deferred_count": len(deferred),
            "article_capacity": article_limit,
        },
        "final_highlights_selected": False,
        "resolver_authorization_performed": False,
    }


def filter_linking_candidates_by_placement(
    prepared_input: Dict[str, Any],
    placement_regions: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Admit candidates only inside verified body paragraphs.

    Protected article regions never produce link highlights.
    Unknown, missing, or unverified structural evidence
    must not be interpreted as eligible body text.

    This function performs placement filtering only.
    It does not allocate capacity or authorize insertion.
    """

    article = prepared_input.get("article", {})
    text = article.get("text")
    candidates = prepared_input.get("candidates")

    if not isinstance(text, str) or not isinstance(candidates, list):
        raise LinkingScorerInputError(
            "Invalid canonical article or candidates."
        )

    excluded_kinds = {
        "title",
        "heading",
        "faq",
        "faq_question",
        "faq_answer",
        "reference",
        "references",
        "bibliography",
        "citation",
        "footnote",
        "conclusion",
        "final_thoughts",
        "closing_paragraph",
    }

    eligible_kinds = {"body_paragraph"}

    valid_regions = []
    structure_valid = (
        isinstance(placement_regions, list)
        and bool(placement_regions)
    )

    if structure_valid:
        for region in placement_regions:
            if not isinstance(region, dict):
                structure_valid = False
                break

            span = region.get("source_span")
            kind = region.get("kind")

            if not isinstance(span, dict):
                structure_valid = False
                break

            start = span.get("start")
            end = span.get("end")

            if (
                region.get("verified") is not True
                or not isinstance(kind, str)
                or span.get("coordinate_space")
                    != "original_article"
                or type(start) is not int
                or type(end) is not int
                or start < 0
                or end <= start
                or end > len(text)
                or not isinstance(span.get("text"), str)
                or text[start:end] != span["text"]
            ):
                structure_valid = False
                break

            valid_regions.append({
                "kind": kind.strip().casefold(),
                "start": start,
                "end": end,
            })

    passed = []
    deferred = []
    rejected = []

    for candidate in candidates:
        record = copy.deepcopy(candidate)

        if not structure_valid:
            deferred.append({
                "candidate": record,
                "reason": "article_structure_unverified",
            })
            continue

        occurrence = verify_linking_candidate_occurrence(
            candidate, text
        )

        if not occurrence["verified"]:
            rejected.append({
                "candidate": record,
                "reason": occurrence["reason"],
            })
            continue

        span = occurrence["occurrence_span"]
        start = span["start"]
        end = span["end"]

        overlapping = [
            region for region in valid_regions
            if start < region["end"]
            and region["start"] < end
        ]

        protected = [
            region for region in overlapping
            if region["kind"] in excluded_kinds
        ]

        if protected:
            rejected.append({
                "candidate": record,
                "reason": "excluded_article_region",
                "region_kind": protected[0]["kind"],
            })
            continue

        unknown = [
            region for region in overlapping
            if region["kind"] not in (
                excluded_kinds | eligible_kinds
            )
        ]

        if unknown:
            deferred.append({
                "candidate": record,
                "reason": "unclassified_article_region",
            })
            continue

        containing_body = [
            region for region in overlapping
            if region["kind"] == "body_paragraph"
            and region["start"] <= start
            and end <= region["end"]
        ]

        if len(containing_body) != 1:
            deferred.append({
                "candidate": record,
                "reason": "eligible_body_location_unverified",
            })
            continue

        passed.append(record)

    return {
        "ok": True,
        "stage": "highlight_placement_guard",
        "structure_verified": structure_valid,
        "placement_eligible_candidates": passed,
        "placement_deferred_candidates": deferred,
        "placement_rejected_candidates": rejected,
        "stats": {
            "input": len(candidates),
            "eligible": len(passed),
            "deferred": len(deferred),
            "rejected": len(rejected),
        },
        "final_highlights_selected": False,
    }


def calculate_eligible_body_link_capacity(
    prepared_input: Dict[str, Any],
    placement_regions: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Calculate provisional link capacity from verified eligible
    body paragraphs only.

    Excluded regions never contribute words.
    Existing hyperlinks inside eligible body count against capacity.
    Unverifiable structure or link coordinates fail closed.

    Does not modify article text or original source coordinates.
    """

    article = prepared_input["article"]
    text = article["text"]
    links = article["existing_links"]

    guard = filter_linking_candidates_by_placement(
        prepared_input,
        placement_regions,
    )

    def unavailable(reason):
        return {
            "verified": False,
            "reason": reason,
            "eligible_word_count": 0,
            "gross_article_capacity": 0,
            "existing_eligible_links": 0,
            "maximum_new_links": 0,
        }

    if not guard["structure_verified"]:
        return unavailable("article_structure_unverified")

    safe_body_spans = []

    for region in placement_regions:
        if region["kind"].strip().casefold() != "body_paragraph":
            continue

        span = region["source_span"]
        start, end = span["start"], span["end"]

        # An overlapping protected, unknown, or other body region
        # makes this entire paragraph ineligible for budgeting.
        overlaps_other = any(
            other is not region
            and start < other["source_span"]["end"]
            and other["source_span"]["start"] < end
            for other in placement_regions
        )

        if not overlaps_other:
            safe_body_spans.append((start, end))

    safe_body_spans.sort()

    eligible_words = sum(
        len(text[start:end].split())
        for start, end in safe_body_spans
    )

    existing_eligible = 0

    for link in links:
        if not isinstance(link, dict):
            return unavailable("existing_link_inventory_unverified")

        start, end = link.get("start"), link.get("end")

        if (
            link.get("coordinate_space") != "original_article"
            or type(start) is not int
            or type(end) is not int
            or start < 0
            or end <= start
            or end > len(text)
        ):
            return unavailable("existing_link_coordinates_unverified")

        containing = [
            (a, b)
            for a, b in safe_body_spans
            if a <= start and end <= b
        ]

        if containing:
            existing_eligible += 1
            continue

        # A hyperlink crossing an eligible-body boundary
        # cannot safely be classified as inside or outside.
        if any(
            start < b and a < end
            for a, b in safe_body_spans
        ):
            return unavailable("existing_link_crosses_body_boundary")

    gross = min(40, eligible_words // 200)

    return {
        "verified": True,
        "reason": "eligible_body_capacity_verified",
        "eligible_word_count": eligible_words,
        "gross_article_capacity": gross,
        "existing_eligible_links": existing_eligible,
        "maximum_new_links": max(
            0, gross - existing_eligible
        ),
    }


def allocate_placement_safe_linking_candidates(
    prepared_input: Dict[str, Any],
    placement_regions: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Combine verified placement, eligible-body capacity,
    candidate ranking, article diversity and section limits.

    Returns provisional opportunities only. Does not authorize
    destination URLs, insert hyperlinks or create final sets.
    """
    guard = filter_linking_candidates_by_placement(
        prepared_input, placement_regions
    )
    budget = calculate_eligible_body_link_capacity(
        prepared_input, placement_regions
    )

    def empty_result(reason):
        return {
            "ok": True,
            "allocation_stage": "placement_safe",
            "status": reason,
            "section_enforcement": "not_available",
            "qualified_opportunities": [],
            "deferred_opportunities": copy.deepcopy(
                guard["placement_deferred_candidates"]
            ),
            "rejected_opportunities": copy.deepcopy(
                guard["placement_rejected_candidates"]
            ),
            "eligible_body_capacity": budget,
            "final_highlights_selected": False,
            "resolver_authorization_performed": False,
        }

    if not budget["verified"]:
        return empty_result(budget["reason"])

    filtered = copy.deepcopy(prepared_input)
    filtered["candidates"] = copy.deepcopy(
        guard["placement_eligible_candidates"]
    )

    quality = assess_ranked_linking_quality(filtered)
    article = prepared_input["article"]
    text = article["text"]
    sections = article.get("sections") or []
    links = article["existing_links"]

    # Reconstruct exactly the safe paragraphs counted by
    # the already-verified eligible-body capacity function.
    body_regions = [
        region for region in placement_regions
        if region["kind"].strip().casefold() == "body_paragraph"
    ]
    safe_body = []

    for region in body_regions:
        span = region["source_span"]
        start, end = span["start"], span["end"]

        if not any(
            other is not region
            and start < other["source_span"]["end"]
            and other["source_span"]["start"] < end
            for other in placement_regions
        ):
            safe_body.append((start, end))

    safe_body.sort()

    # Section enforcement is enabled only when source
    # boundaries and eligible-body ownership are verified.
    section_map = {}
    section_enforcement = "article_fallback"

    if sections and isinstance(sections, list):
        valid = True
        observed_ids = set()
        ranges = []

        for section in sections:
            if not isinstance(section, dict):
                valid = False
                break

            sid = section.get("section_id")
            span = section.get("source_span")

            if not isinstance(span, dict):
                valid = False
                break

            a, b = span.get("start"), span.get("end")

            if (
                section.get("verified") is not True
                or not isinstance(sid, str)
                or not sid.strip()
                or sid in observed_ids
                or span.get("coordinate_space") != "original_article"
                or type(a) is not int
                or type(b) is not int
                or a < 0
                or b <= a
                or b > len(text)
            ):
                valid = False
                break

            observed_ids.add(sid)
            ranges.append((a, b, sid))

        if valid:
            ordered = sorted(ranges)

            if any(
                ordered[i][0] < ordered[i - 1][1]
                for i in range(1, len(ordered))
            ):
                valid = False

        ownership = {}

        if valid:
            for a, b in safe_body:
                owners = [
                    sid for x, y, sid in ranges
                    if x <= a and b <= y
                ]
                if len(owners) != 1:
                    valid = False
                    break
                ownership[(a, b)] = owners[0]

        if valid:
            for a, b, sid in ranges:
                paragraphs = [
                    (x, y) for x, y in safe_body
                    if ownership[(x, y)] == sid
                ]
                words = sum(
                    len(text[x:y].split())
                    for x, y in paragraphs
                )

                # Short sections require upstream grouping.
                if 0 < words < 100:
                    valid = False
                    break

                existing = sum(
                    1 for link in links
                    if any(
                        x <= link["start"]
                        and link["end"] <= y
                        for x, y in paragraphs
                    )
                )

                section_capacity = calculate_section_link_capacity(
                    section_word_count=words,
                    existing_section_links=existing,
                    article_remaining_capacity=budget[
                        "maximum_new_links"
                    ],
                )

                section_map[sid] = {
                    "start": a,
                    "end": b,
                    "limit": section_capacity[
                        "remaining_section_capacity"
                    ],
                    "selected": 0,
                }

        if valid:
            section_enforcement = "verified"
        else:
            section_map = {}

    chosen = []
    deferred = []
    selected_spans = []
    selected_phrases = set()
    article_limit = budget["maximum_new_links"]

    def defer(record, reason):
        item = copy.deepcopy(record)
        item["status"] = "deferred_diversity"
        item["reason"] = reason
        deferred.append(item)

    for record in quality["quality_ranked_opportunities"]:
        span = record["occurrence_span"]
        start, end = span["start"], span["end"]

        phrase_key = " ".join(
            str(record.get("phrase") or "").casefold().split()
        )

        # The occurrence must be within a safe paragraph
        # counted by the verified eligible-body budget.
        if not any(
            a <= start and end <= b for a, b in safe_body
        ):
            defer(record, "eligible_body_budget_location_unverified")
            continue

        if phrase_key in selected_phrases:
            defer(record, "duplicate_anchor")
            continue

        if any(
            start < b and a < end
            for a, b in selected_spans
        ):
            defer(record, "highlight_overlap")
            continue

        if len(chosen) >= article_limit:
            defer(record, "article_capacity_reached")
            continue

        owner = None

        if section_enforcement == "verified":
            owners = [
                sid for sid, section in section_map.items()
                if section["start"] <= start
                and end <= section["end"]
            ]

            if len(owners) != 1:
                defer(record, "section_ownership_unverified")
                continue

            owner = owners[0]

            if section_map[owner]["selected"] >= (
                section_map[owner]["limit"]
            ):
                defer(record, "section_capacity_reached")
                continue

        item = copy.deepcopy(record)
        item["status"] = "allocation_qualified"
        item["reason"] = "placement_and_capacity_verified"
        item["section_id"] = owner

        chosen.append(item)
        selected_spans.append((start, end))
        selected_phrases.add(phrase_key)

        if owner is not None:
            section_map[owner]["selected"] += 1

    return {
        "ok": True,
        "allocation_stage": "placement_safe",
        "status": "provisional",
        "section_enforcement": section_enforcement,
        "qualified_opportunities": chosen,
        "deferred_opportunities": (
            deferred
            + copy.deepcopy(quality["deferred_opportunities"])
            + copy.deepcopy(guard["placement_deferred_candidates"])
        ),
        "rejected_opportunities": (
            copy.deepcopy(quality["rejected_opportunities"])
            + copy.deepcopy(guard["placement_rejected_candidates"])
        ),
        "eligible_body_capacity": budget,
        "section_selected_counts": {
            sid: entry["selected"]
            for sid, entry in section_map.items()
        },
        "stats": {
            "placement_eligible": guard["stats"]["eligible"],
            "qualified": len(chosen),
            "article_limit": article_limit,
        },
        "final_highlights_selected": False,
        "resolver_authorization_performed": False,
    }


def generate_alternative_linking_highlight_sets(
    prepared_input: Dict[str, Any],
    placement_regions: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Generate up to three distinct, independently allocated
    provisional highlight sets.

    Set 1 uses the best currently qualified opportunities.
    Additional sets replace an occurrence by excluding it
    and rerunning all placement and allocation safeguards.

    No new quality weights, weak padding, destination approval,
    hyperlink insertion or final Editor selection.
    """

    baseline = allocate_placement_safe_linking_candidates(
        prepared_input,
        placement_regions,
    )

    maximum_sets = 3
    initial = baseline["qualified_opportunities"]

    sets = []
    seen_signatures = set()

    def signature(opportunities):
        return frozenset(
            item["selection_occurrence_id"]
            for item in opportunities
        )

    def add_set(allocation, variant, excluded_id=None):
        opportunities = allocation["qualified_opportunities"]

        if not opportunities:
            return False

        key = signature(opportunities)

        if key in seen_signatures:
            return False

        seen_signatures.add(key)

        sets.append({
            "set_id": f"set_{len(sets) + 1}",
            "set_number": len(sets) + 1,
            "variant": variant,
            "excluded_occurrence_id": excluded_id,
            "opportunities": copy.deepcopy(opportunities),
            "opportunity_count": len(opportunities),
            "allocation_status": allocation["status"],
            "section_enforcement": allocation[
                "section_enforcement"
            ],
            "eligible_body_capacity": copy.deepcopy(
                allocation["eligible_body_capacity"]
            ),
            "independently_allocated": True,
            "final_editor_selection": False,
            "resolver_authorized": False,
        })

        return True

    if initial:
        add_set(baseline, "initial")

    baseline_ids = signature(initial)

    if initial:
        for selected in initial:
            if len(sets) >= maximum_sets:
                break

            excluded_id = selected[
                "selection_occurrence_id"
            ]

            # Exclude only this occurrence from the input.
            # All remaining candidates are independently
            # re-evaluated using the complete allocation path.
            variant_input = copy.deepcopy(prepared_input)

            variant_input["candidates"] = [
                copy.deepcopy(candidate)
                for candidate in prepared_input["candidates"]
                if candidate.get("selection_occurrence_id")
                != excluded_id
            ]

            allocation = (
                allocate_placement_safe_linking_candidates(
                    variant_input,
                    placement_regions,
                )
            )

            alternative = allocation["qualified_opportunities"]
            alternative_ids = signature(alternative)

            # A shorter subset is not a meaningful alternative.
            # Require at least one newly selected occurrence.
            if not (alternative_ids - baseline_ids):
                continue

            add_set(
                allocation,
                "replacement_alternative",
                excluded_id,
            )

    return {
        "ok": True,
        "stage": "provisional_alternative_highlight_sets",
        "sets": sets,
        "set_count": len(sets),
        "maximum_sets": maximum_sets,
        "baseline_allocation": copy.deepcopy(baseline),
        "canonical_candidates_unchanged": True,
        "all_sets_independently_allocated": True,
        "final_highlights_selected": False,
        "resolver_authorization_performed": False,
    }


def build_canonical_linking_scorer_output(
    prepared_input: Dict[str, Any],
    placement_regions: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Build the canonical provisional Linking Scorer response.

    Preserve verified original-article coordinates, source
    evidence, article identity, and independent set identities.

    This function does not perform Resolver authorization,
    link-category approval, Editor selection or insertion.
    """
    import hashlib

    generated = generate_alternative_linking_highlight_sets(
        prepared_input,
        placement_regions,
    )

    article = prepared_input["article"]
    text = article["text"]
    context = prepared_input["document_context"]
    fingerprint = hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()

    canonical_sets = []
    seen_set_signatures = set()

    if generated["set_count"] > 3:
        raise LinkingScorerInputError(
            "Maximum three highlight sets permitted."
        )

    for index, item in enumerate(generated["sets"], start=1):
        opportunities = copy.deepcopy(item["opportunities"])
        seen_occurrences = set()
        seen_phrases = set()
        spans = []

        limit = item["eligible_body_capacity"][
            "maximum_new_links"
        ]

        if len(opportunities) > limit:
            raise LinkingScorerInputError(
                "Highlight set exceeds article capacity."
            )

        for opportunity in opportunities:
            occurrence_id = opportunity.get(
                "selection_occurrence_id"
            )
            phrase_id = opportunity.get("selection_phrase_id")
            phrase = opportunity.get("phrase")
            span = opportunity.get("occurrence_span")

            if (
                not isinstance(occurrence_id, str)
                or not occurrence_id.strip()
                or not isinstance(phrase_id, str)
                or not phrase_id.strip()
                or not isinstance(phrase, str)
                or not phrase.strip()
                or not isinstance(span, dict)
            ):
                raise LinkingScorerInputError(
                    "Incomplete canonical occurrence evidence."
                )

            start, end = span.get("start"), span.get("end")

            if (
                type(start) is not int
                or type(end) is not int
                or start < 0
                or end <= start
                or end > len(text)
                or span.get("coordinate_space")
                    != "original_article"
                or text[start:end] != span.get("text")
            ):
                raise LinkingScorerInputError(
                    "Invalid original-article occurrence."
                )

            phrase_key = " ".join(phrase.casefold().split())

            if occurrence_id in seen_occurrences:
                raise LinkingScorerInputError(
                    "Duplicate occurrence in highlight set."
                )

            if phrase_key in seen_phrases:
                raise LinkingScorerInputError(
                    "Duplicate anchor phrase in highlight set."
                )

            if any(
                start < previous_end
                and previous_start < end
                for previous_start, previous_end in spans
            ):
                raise LinkingScorerInputError(
                    "Overlapping highlight spans."
                )

            seen_occurrences.add(occurrence_id)
            seen_phrases.add(phrase_key)
            spans.append((start, end))

        signature = frozenset(seen_occurrences)

        if signature in seen_set_signatures:
            raise LinkingScorerInputError(
                "Duplicate alternative highlight set."
            )

        seen_set_signatures.add(signature)

        canonical_sets.append({
            "set_id": f"set_{index}",
            "set_number": index,
            "variant": item["variant"],
            "excluded_occurrence_id": item[
                "excluded_occurrence_id"
            ],
            "status": "provisional",
            "opportunity_count": len(opportunities),
            "opportunities": opportunities,
            "section_enforcement": item[
                "section_enforcement"
            ],
            "eligible_body_capacity": copy.deepcopy(
                item["eligible_body_capacity"]
            ),
            "resolver_authorized": False,
            "editor_committed": False,
        })

    return {
        "ok": True,
        "contract_version": "2.5",
        "component": "linking_scorer",
        "status": "provisional",
        "document_context": copy.deepcopy(context),
        "article_identity": {
            "sha256": fingerprint,
            "character_count": len(text),
        },
        "highlight_sets": canonical_sets,
        "highlight_set_count": len(canonical_sets),
        "maximum_highlight_sets": 3,
        "initial_set_id": (
            canonical_sets[0]["set_id"]
            if canonical_sets else None
        ),
        "baseline_allocation": copy.deepcopy(
            generated["baseline_allocation"]
        ),
        "link_category_authorization": "pending",
        "resolver_authorization": "pending",
        "editor_commit": "not_performed",
        "final_highlights_selected": False,
        "canonical_candidates_unchanged": True,
    }


def run_guarded_linking_scorer_bridge(
    *,
    workspace_id: str,
    document_id: str,
    article_text: str,
    canonical_candidates: List[Dict[str, Any]],
    content_version=None,
    placement_regions=None,
    existing_links=None,
    article_sections=None,
    structure_complete: bool = False,
    link_inventory_complete: bool = False,
) -> Dict[str, Any]:
    """
    Guarded internal integration entry point.

    Completeness assertions must come from trusted server-side
    source processing, never unverified client declarations.

    Missing evidence blocks replacement execution.
    Legacy routing remains a separate concern.
    """
    import hashlib

    def blocked(reason):
        return {
            "ok": False,
            "bridge_status": "blocked",
            "reason": reason,
            "replacement_executed": False,
            "legacy_routing_modified": False,
        }

    if not isinstance(article_text, str) or not article_text:
        return blocked("article_text_missing")

    if (
        not isinstance(workspace_id, str)
        or not workspace_id.strip()
        or not isinstance(document_id, str)
        or not document_id.strip()
    ):
        return blocked("document_identity_missing")

    if (
        not isinstance(content_version, str)
        or not content_version.strip()
    ):
        return blocked("content_version_unverified")

    if not isinstance(canonical_candidates, list):
        return blocked("canonical_candidates_missing")

    if any(
        not isinstance(candidate, dict)
        for candidate in canonical_candidates
    ):
        return blocked("invalid_canonical_candidates")

    fingerprint = hashlib.sha256(
        article_text.encode("utf-8")
    ).hexdigest()

    for candidate in canonical_candidates:
        if candidate.get(
            "selection_article_text_sha256"
        ) != fingerprint:
            return blocked("canonical_article_fingerprint_mismatch")

    if (
        structure_complete is not True
        or not isinstance(placement_regions, list)
        or not placement_regions
    ):
        return blocked("verified_placement_structure_missing")

    if (
        link_inventory_complete is not True
        or not isinstance(existing_links, list)
    ):
        return blocked("verified_existing_link_inventory_missing")

    # Empty existing_links is legitimate only when the trusted
    # server-side extractor confirms the inventory is complete.

    prepared = prepare_linking_scorer_input(
        workspace_id=workspace_id,
        document_id=document_id,
        content_version=content_version,
        article_text=article_text,
        selected_candidates=canonical_candidates,
        existing_links=existing_links,
        article_sections=(
            article_sections
            if isinstance(article_sections, list)
            else []
        ),
    )

    capacity = calculate_eligible_body_link_capacity(
        prepared,
        placement_regions,
    )

    if capacity["verified"] is not True:
        return blocked(capacity["reason"])

    output = build_canonical_linking_scorer_output(
        prepared,
        placement_regions,
    )

    # The canonical output must remain provisional.
    if (
        output["final_highlights_selected"] is not False
        or output["resolver_authorization"] != "pending"
        or output["editor_commit"] != "not_performed"
    ):
        raise LinkingScorerInputError(
            "Guarded bridge received unauthorized final output."
        )

    return {
        "ok": True,
        "bridge_status": "provisional_output_ready",
        "reason": "verified_inputs_accepted",
        "replacement_executed": True,
        "legacy_routing_modified": False,
        "canonical_output": output,
    }
