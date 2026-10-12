from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.server.stores.phrase_discovery_engine import _DocumentModel

MERGER_VERSION = "phrase_merger/1.0"



def _recover_extractor_occurrence(
    model: _DocumentModel,
    candidate: Dict[str, Any],
) -> Dict[str, Any]:
    """Recover the literal document occurrence for one Extractor candidate.

    Prefer the candidate's section_id so repeated phrases are mapped to the
    sentence that actually produced the Extractor record. Fall back to the
    model-wide literal-position index only when section-local recovery is not
    possible. Never fabricate offsets.
    """

    phrase = str(candidate.get("phrase", "") or "")
    section_id = str(candidate.get("section_id", "") or "").strip()
    snippet = str(candidate.get("snippet", "") or "")

    result: Dict[str, Any] = {
        "literal_span_verified": False,
        "first_position": -1,
        "all_positions": [],
        "occurrence_count": 0,
        "matched_occurrence": None,
        "position_source": "",
        "section_id": section_id,
    }

    if not phrase or not model.verify_literal(phrase):
        return result

    global_pos = model.positions(phrase)
    result["first_position"] = global_pos["first_position"]
    result["all_positions"] = list(global_pos["all_positions"])
    result["occurrence_count"] = global_pos["occurrence_count"]

    phrase_cf = phrase.casefold()

    for sent in model.sentences:
        if section_id and sent.section_id != section_id:
            continue

        sent_cf = sent.text.casefold()
        local_start = sent_cf.find(phrase_cf)
        if local_start < 0:
            continue

        local_end = local_start + len(phrase)

        if sent.text[local_start:local_end].casefold() != phrase_cf:
            continue

        abs_start = sent.start + local_start
        abs_end = sent.start + local_end

        if model.surface[abs_start:abs_end].casefold() != phrase_cf:
            continue

        result["literal_span_verified"] = True
        result["matched_occurrence"] = {
            "start": abs_start,
            "end": abs_end,
            "sentence_index": sent.index,
            "section_index": sent.section,
            "section_id": sent.section_id,
            "sentence_role": sent.role,
            "block_index": sent.block,
        }
        result["position_source"] = "section_id"
        return result

    if snippet:
        snippet_cf = snippet.casefold()
        local_start = snippet_cf.find(phrase_cf)
        if local_start >= 0 and global_pos["all_positions"]:
            result["literal_span_verified"] = True
            result["position_source"] = "global_literal_fallback"
            start = global_pos["all_positions"][0]
            result["matched_occurrence"] = {
                "start": start,
                "end": start + len(phrase),
            }

    return result

def _recover_discovery_occurrence(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """Preserve the certified positional metadata already emitted by Discovery."""

    intelligence = candidate.get("discovery_intelligence")
    if not isinstance(intelligence, dict):
        intelligence = {}

    span = intelligence.get("span")
    if not isinstance(span, dict):
        span = {}

    try:
        start = int(span.get("start", -1))
        end = int(span.get("end", -1))
    except (TypeError, ValueError):
        start, end = -1, -1

    all_positions = intelligence.get("all_positions")
    if not isinstance(all_positions, list):
        all_positions = []

    clean_positions: List[int] = []
    for value in all_positions:
        try:
            clean_positions.append(int(value))
        except (TypeError, ValueError):
            continue

    try:
        first_position = int(intelligence.get("first_position", -1))
    except (TypeError, ValueError):
        first_position = -1

    try:
        occurrence_count = int(
            intelligence.get("occurrence_count", len(clean_positions))
        )
    except (TypeError, ValueError):
        occurrence_count = len(clean_positions)

    matched = None
    if start >= 0 and end > start:
        matched = {
            "start": start,
            "end": end,
            "sentence_index": span.get("sentence_index"),
            "section_index": span.get("section_index"),
            "section_id": str(candidate.get("section_id", "") or "").strip(),
            "sentence_role": span.get("sentence_role"),
            "block_index": span.get("block_index"),
            "block_kind": span.get("block_kind"),
        }

    return {
        "literal_span_verified": intelligence.get("literal_span_verified") is True,
        "first_position": first_position,
        "all_positions": clean_positions,
        "occurrence_count": occurrence_count,
        "matched_occurrence": matched,
        "position_source": str(
            intelligence.get("position_source", "phrase_discovery") or
            "phrase_discovery"
        ),
        "position_basis": str(intelligence.get("position_basis", "") or ""),
        "section_id": str(candidate.get("section_id", "") or "").strip(),
    }



def _certify_original_article_position(
    position: Dict[str, Any],
    *,
    model_surface: str,
    article_text: str,
    phrase: str,
) -> Dict[str, Any]:
    """Keep model-surface evidence separate from original-article coordinates."""
    from copy import deepcopy

    result = deepcopy(position)
    occurrence = position.get("matched_occurrence")

    if not isinstance(occurrence, dict):
        occurrence = {}

    start = occurrence.get("start")
    end = occurrence.get("end")

    identical_surface = model_surface == article_text

    verified = (
        identical_surface
        and position.get("literal_span_verified") is True
        and type(start) is int
        and type(end) is int
        and 0 <= start < end <= len(article_text)
        and article_text[start:end].casefold() == phrase.casefold()
    )

    # Retain the upstream evidence without treating its coordinates
    # as original-article offsets.
    result["surface_position_intelligence"] = deepcopy(position)
    result["source_coordinate_space"] = "phrase_discovery_surface_v1"
    result["original_article_span_verified"] = verified

    if verified:
        result["original_article_alignment_status"] = (
            "verified_identical_surface"
        )
        result["coordinate_space"] = "original_article"
    else:
        result["original_article_alignment_status"] = (
            "unverified_span"
            if identical_surface
            else "surface_mismatch"
        )
        result["coordinate_space"] = "unverified_original_article"
        result["literal_span_verified"] = False
        result["matched_occurrence"] = None
        result["first_position"] = -1
        result["all_positions"] = []
        result["occurrence_count"] = 0

    return result




def _matched_occurrence_for_merging(
    position: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Return usable occurrence evidence in its actual coordinate space."""
    if not isinstance(position, dict):
        return None

    matched = position.get("matched_occurrence")
    if isinstance(matched, dict):
        return {
            "matched_occurrence": matched,
            "coordinate_space": str(
                position.get("coordinate_space", "original_article")
                or "original_article"
            ),
        }

    upstream = position.get("surface_position_intelligence")
    if not isinstance(upstream, dict):
        return None

    matched = upstream.get("matched_occurrence")
    if not isinstance(matched, dict):
        return None

    return {
        "matched_occurrence": matched,
        "coordinate_space": str(
            position.get(
                "source_coordinate_space",
                "phrase_discovery_surface_v1",
            )
            or "phrase_discovery_surface_v1"
        ),
    }


def _build_merger_section_intelligence(
    model: _DocumentModel,
    position: Dict[str, Any],
    phrase: str,
) -> Dict[str, Any]:
    """Preserve section hierarchy and distinguish coordinate spaces."""
    evidence = {
        "status": "unresolved",
        "original_article_verified": False,
        "section_index": None,
        "source_section_id": None,
        "section_heading": "",
        "heading_level": None,
        "parent_section_index": None,
        "section_path": [],
        "section_span": None,
        "direct_section_span": None,
        "heading_span": None,
    }

    upstream = position.get("surface_position_intelligence")
    if not isinstance(upstream, dict):
        upstream = position

    occurrence = upstream.get("matched_occurrence")
    if not isinstance(occurrence, dict):
        return evidence

    start = occurrence.get("start")
    end = occurrence.get("end")
    sentence_index = occurrence.get("sentence_index")
    section_index = occurrence.get("section_index")

    if not all(
        type(value) is int
        for value in (start, end, sentence_index, section_index)
    ):
        return evidence

    if not (0 <= start < end <= len(model.surface)):
        return evidence
    if not (0 <= sentence_index < len(model.sentences)):
        return evidence
    if not (0 <= section_index < len(model.sections)):
        return evidence

    sentence = model.sentences[sentence_index]
    section = model.sections[section_index]

    if sentence.section != section_index:
        return evidence
    if not (sentence.start <= start < end <= sentence.end):
        return evidence
    if model.surface[start:end].casefold() != phrase.casefold():
        return evidence

    claimed_id = str(upstream.get("section_id") or "").strip()
    if claimed_id and claimed_id != sentence.section_id:
        return evidence

    verified = position.get("original_article_span_verified") is True
    space = (
        "original_article"
        if verified
        else "phrase_discovery_surface_v1"
    )

    def heading_details(sec):
        if sec.heading is None:
            return "", None
        if not (0 <= sec.heading < len(model.sentences)):
            return "", None

        sent = model.sentences[sec.heading]
        return sent.text, {
            "start": sent.start,
            "end": sent.end,
            "coordinate_space": space,
        }

    hierarchy = []
    visited = set()
    cursor = section_index

    while cursor is not None:
        if cursor in visited:
            return evidence
        if not (0 <= cursor < len(model.sections)):
            return evidence

        visited.add(cursor)
        ancestor = model.sections[cursor]
        heading_text, heading_span = heading_details(ancestor)

        hierarchy.append({
            "section_index": ancestor.index,
            "parent_section_index": ancestor.parent,
            "heading_level": ancestor.level,
            "heading_text": heading_text,
            "heading_span": heading_span,
        })

        cursor = ancestor.parent

    hierarchy.reverse()
    heading_text, heading_span = heading_details(section)

    if section_index == 0:
        section_start = 0
    else:
        if heading_span is None:
            return evidence
        section_start = heading_span["start"]

    # Hierarchical scope includes nested child sections.
    scope_end = len(model.surface)

    # Direct scope stops at the next heading, including a child heading.
    direct_end = len(model.surface)

    for next_section in model.sections[section_index + 1:]:
        _, next_heading = heading_details(next_section)
        if next_heading is None:
            return evidence

        next_start = next_heading["start"]
        direct_end = min(direct_end, next_start)

        if next_section.level <= section.level:
            scope_end = next_start
            break

    if not (
        0 <= section_start <= start < end <= scope_end
        <= len(model.surface)
    ):
        return evidence

    if not (section_start <= direct_end <= scope_end):
        return evidence

    evidence.update({
        "status": (
            "verified_original_article"
            if verified
            else "unverified_original_article"
        ),
        "original_article_verified": verified,
        "section_index": section.index,
        "source_section_id": sentence.section_id,
        "source_sentence_index": sentence.index,
        "section_heading": heading_text,
        "heading_level": section.level,
        "parent_section_index": section.parent,
        "section_path": hierarchy,
        "section_span": {
            "start": section_start,
            "end": scope_end,
            "coordinate_space": space,
            "includes_nested_sections": True,
        },
        "direct_section_span": {
            "start": section_start,
            "end": direct_end,
            "coordinate_space": space,
            "includes_nested_sections": False,
        },
        "heading_span": heading_span,
    })

    return evidence


def _build_canonical_candidate(
    candidate: Dict[str, Any],
    *,
    origin: str,
    position_intelligence: Dict[str, Any],
    document_id: str = "",
) -> Dict[str, Any]:
    """Build one canonical Phrase Merger candidate without losing source data."""

    clean_origin = str(origin or "").strip()

    provenance: List[str] = []
    existing_provenance = candidate.get("provenance")

    if isinstance(existing_provenance, list):
        for value in existing_provenance:
            clean_value = str(value or "").strip()
            if clean_value and clean_value not in provenance:
                provenance.append(clean_value)
    elif existing_provenance:
        clean_value = str(existing_provenance).strip()
        if clean_value:
            provenance.append(clean_value)

    if clean_origin and clean_origin not in provenance:
        provenance.append(clean_origin)

    record: Dict[str, Any] = dict(candidate)
    record.update({
        "phrase": str(candidate.get("phrase", "") or ""),
        "source_type": str(candidate.get("source_type", "") or ""),
        "section_id": str(candidate.get("section_id", "") or "").strip(),
        "doc_id": str(
            candidate.get("doc_id", "") or document_id or ""
        ).strip(),
        "snippet": str(candidate.get("snippet", "") or ""),
        "provenance": provenance,
        "position_intelligence": dict(position_intelligence or {}),
        "merger_intelligence": {
            "merger_version": MERGER_VERSION,
            "origins": list(provenance),
            "merged_cross_source": False,
        },
    })

    extractor_intelligence = candidate.get("extractor_intelligence")
    if isinstance(extractor_intelligence, dict):
        record["extractor_intelligence"] = dict(extractor_intelligence)

    discovery_intelligence = candidate.get("discovery_intelligence")
    if isinstance(discovery_intelligence, dict):
        record["discovery_intelligence"] = dict(discovery_intelligence)

    return record
def merge_phrase_candidates(
    *,
    text: str = "",
    html: str = "",
    title: str = "",
    extractor_candidates: Optional[List[Dict[str, Any]]] = None,
    discovery_candidates: Optional[List[Dict[str, Any]]] = None,
    document_id: str = "",
    diagnostics: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Combine Smart Phrase Extractor and Phrase Discovery candidates.

    Hard boundaries:
    - no phrase-quality filtering;
    - no semantic rewriting or synonym generation;
    - preserve literal phrases and provenance;
    - exact cross-source overlaps may merge;
    - related-but-different phrases remain distinct.
    """

    clean_text = str(text or "")
    clean_html = str(html or "")
    clean_title = str(title or "")
    clean_doc = str(document_id or "").strip()

    clean_extractor = [
        dict(c) for c in (extractor_candidates or [])
        if isinstance(c, dict)
    ]
    clean_discovery = [
        dict(c) for c in (discovery_candidates or [])
        if isinstance(c, dict)
    ]

    model = _DocumentModel(
        text=clean_text,
        html=clean_html,
        title=clean_title,
        extractor_candidates=clean_extractor,
    )

    diag: Dict[str, Any] = {
        "merger_version": MERGER_VERSION,
        "document_id": clean_doc,
        "extractor_input_count": len(clean_extractor),
        "discovery_input_count": len(clean_discovery),
        "merged_output_count": 0,
        "exact_cross_source_overlaps": 0,
        "extractor_only": 0,
        "discovery_only": 0,
        "position_recovery_failures": 0,
        "original_article_position_unverified": 0,
        "errors": [],
    }

    extractor_records: List[Dict[str, Any]] = []
    for candidate in clean_extractor:
        position = _recover_extractor_occurrence(model, candidate)

        position = _certify_original_article_position(
            position,
            model_surface=model.surface,
            article_text=clean_text,
            phrase=str(candidate.get("phrase", "") or ""),
        )

        if _matched_occurrence_for_merging(position) is None:
            diag["position_recovery_failures"] += 1
        if position.get("original_article_span_verified") is not True:
            diag["original_article_position_unverified"] += 1

        section_candidate = dict(candidate)
        section_candidate["merger_section_intelligence"] = (
            _build_merger_section_intelligence(
                model,
                position,
                str(candidate.get("phrase", "") or ""),
            )
        )

        extractor_records.append(
            _build_canonical_candidate(
                section_candidate,
                origin="smart_phrase_extractor",
                position_intelligence=position,
                document_id=clean_doc,
            )
        )

    discovery_records: List[Dict[str, Any]] = []
    for candidate in clean_discovery:
        position = _recover_discovery_occurrence(candidate)

        position = _certify_original_article_position(
            position,
            model_surface=model.surface,
            article_text=clean_text,
            phrase=str(candidate.get("phrase", "") or ""),
        )

        if _matched_occurrence_for_merging(position) is None:
            diag["position_recovery_failures"] += 1
        if position.get("original_article_span_verified") is not True:
            diag["original_article_position_unverified"] += 1

        section_candidate = dict(candidate)
        section_candidate["merger_section_intelligence"] = (
            _build_merger_section_intelligence(
                model,
                position,
                str(candidate.get("phrase", "") or ""),
            )
        )

        discovery_records.append(
            _build_canonical_candidate(
                section_candidate,
                origin="phrase_discovery",
                position_intelligence=position,
                document_id=clean_doc,
            )
        )

    merged: List[Dict[str, Any]] = []
    used_discovery_indexes = set()
    used_extractor_indexes = set()

    for extractor_index, extractor_record in enumerate(extractor_records):
        extractor_phrase = str(
            extractor_record.get("phrase", "") or ""
        ).casefold()

        extractor_position = extractor_record.get(
            "position_intelligence", {}
        )
        extractor_match_info = _matched_occurrence_for_merging(
            extractor_position
        )
        if not isinstance(extractor_match_info, dict):
            continue

        extractor_match = extractor_match_info["matched_occurrence"]
        extractor_space = extractor_match_info["coordinate_space"]
        extractor_start = extractor_match.get("start")
        extractor_end = extractor_match.get("end")

        for discovery_index, discovery_record in enumerate(discovery_records):
            if discovery_index in used_discovery_indexes:
                continue

            discovery_phrase = str(
                discovery_record.get("phrase", "") or ""
            ).casefold()

            if extractor_phrase != discovery_phrase:
                continue

            discovery_position = discovery_record.get(
                "position_intelligence", {}
            )
            discovery_match_info = _matched_occurrence_for_merging(
                discovery_position
            )
            if not isinstance(discovery_match_info, dict):
                continue

            discovery_match = discovery_match_info["matched_occurrence"]
            discovery_space = discovery_match_info["coordinate_space"]

            if extractor_space != discovery_space:
                continue

            discovery_start = discovery_match.get("start")
            discovery_end = discovery_match.get("end")

            if (
                extractor_start != discovery_start
                or extractor_end != discovery_end
            ):
                continue

            combined = dict(extractor_record)

            from copy import deepcopy

            # Preserve each upstream source independently.
            excluded_fields = {
                "position_intelligence",
                "merger_intelligence",
                "provenance",
                "extractor_intelligence",
                "discovery_intelligence",
            }

            source_metadata = {
                source_name: {
                    field: deepcopy(value)
                    for field, value in record.items()
                    if field not in excluded_fields
                }
                for source_name, record in (
                    ("smart_phrase_extractor", extractor_record),
                    ("phrase_discovery", discovery_record),
                )
            }

            # Retain discovery-only metadata without overwriting
            # the established canonical top-level values.
            for field, value in discovery_record.items():
                if field not in excluded_fields:
                    combined.setdefault(field, deepcopy(value))

            provenance: List[str] = []
            for source_record in (extractor_record, discovery_record):
                for value in source_record.get("provenance", []):
                    clean_value = str(value or "").strip()
                    if clean_value and clean_value not in provenance:
                        provenance.append(clean_value)

            combined["provenance"] = provenance

            discovery_intelligence = discovery_record.get(
                "discovery_intelligence"
            )
            if isinstance(discovery_intelligence, dict):
                combined["discovery_intelligence"] = dict(
                    discovery_intelligence
                )

            # Position and primary section evidence must describe
            # the same discovery occurrence. Independent source
            # evidence remains in merger_intelligence.source_metadata.
            combined["position_intelligence"] = dict(discovery_position)
            combined["merger_section_intelligence"] = deepcopy(
                discovery_record.get("merger_section_intelligence", {})
            )

            combined["merger_intelligence"] = {
                "merger_version": MERGER_VERSION,
                "origins": list(provenance),
                "merged_cross_source": True,
                "overlap_type": "exact_phrase_exact_occurrence",

                "source_metadata": source_metadata,
                "source_position_intelligence": {
                    "smart_phrase_extractor": deepcopy(extractor_position),
                    "phrase_discovery": deepcopy(discovery_position),
                },
            }

            merged.append(combined)
            used_extractor_indexes.add(extractor_index)
            used_discovery_indexes.add(discovery_index)
            diag["exact_cross_source_overlaps"] += 1
            break

    for extractor_index, extractor_record in enumerate(extractor_records):
        if extractor_index in used_extractor_indexes:
            continue

        merged.append(dict(extractor_record))
        diag["extractor_only"] += 1

    for discovery_index, discovery_record in enumerate(discovery_records):
        if discovery_index in used_discovery_indexes:
            continue

        merged.append(dict(discovery_record))
        diag["discovery_only"] += 1

    def _deterministic_sort_key(record: Dict[str, Any]):
        position = record.get("position_intelligence")
        if not isinstance(position, dict):
            position = {}

        match_info = _matched_occurrence_for_merging(position)
        matched = (
            match_info.get("matched_occurrence", {})
            if isinstance(match_info, dict)
            else {}
        )

        try:
            start = int(matched.get("start", -1))
        except (TypeError, ValueError):
            start = -1

        try:
            end = int(matched.get("end", -1))
        except (TypeError, ValueError):
            end = -1

        has_valid_position = start >= 0 and end > start

        provenance = record.get("provenance")
        if not isinstance(provenance, list):
            provenance = []

        clean_provenance = tuple(
            sorted(
                str(value or "").strip().casefold()
                for value in provenance
                if str(value or "").strip()
            )
        )

        return (
            0 if has_valid_position else 1,
            start if has_valid_position else 0,
            end if has_valid_position else 0,
            str(record.get("phrase", "") or "").casefold(),
            str(record.get("section_id", "") or "").casefold(),
            str(record.get("source_type", "") or "").casefold(),
            clean_provenance,
        )

    merged.sort(key=_deterministic_sort_key)

    diag["merged_output_count"] = len(merged)

    if diagnostics is not None:
        diagnostics.update(diag)

    return merged
__all__ = ["merge_phrase_candidates", "MERGER_VERSION"]








