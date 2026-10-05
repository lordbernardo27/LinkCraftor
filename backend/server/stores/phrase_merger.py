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

    record: Dict[str, Any] = {
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
    }

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
        "errors": [],
    }

    extractor_records: List[Dict[str, Any]] = []
    for candidate in clean_extractor:
        position = _recover_extractor_occurrence(model, candidate)

        if not position.get("literal_span_verified"):
            diag["position_recovery_failures"] += 1

        extractor_records.append(
            _build_canonical_candidate(
                candidate,
                origin="smart_phrase_extractor",
                position_intelligence=position,
                document_id=clean_doc,
            )
        )

    discovery_records: List[Dict[str, Any]] = []
    for candidate in clean_discovery:
        position = _recover_discovery_occurrence(candidate)

        if not position.get("literal_span_verified"):
            diag["position_recovery_failures"] += 1

        discovery_records.append(
            _build_canonical_candidate(
                candidate,
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
        extractor_match = extractor_position.get("matched_occurrence")

        if not isinstance(extractor_match, dict):
            continue

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
            discovery_match = discovery_position.get("matched_occurrence")

            if not isinstance(discovery_match, dict):
                continue

            discovery_start = discovery_match.get("start")
            discovery_end = discovery_match.get("end")

            if (
                extractor_start != discovery_start
                or extractor_end != discovery_end
            ):
                continue

            combined = dict(extractor_record)

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

            combined["position_intelligence"] = dict(discovery_position)

            combined["merger_intelligence"] = {
                "merger_version": MERGER_VERSION,
                "origins": list(provenance),
                "merged_cross_source": True,
                "overlap_type": "exact_phrase_exact_occurrence",
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

        matched = position.get("matched_occurrence")
        if not isinstance(matched, dict):
            matched = {}

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








