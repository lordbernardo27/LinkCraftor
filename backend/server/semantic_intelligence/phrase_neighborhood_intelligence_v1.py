"""Canonical Phrase Neighborhood Intelligence v1.

Phase 4.6.3.

Consumes only the certified Phase 4.6.2 Entity & Concept Intelligence
result and builds article-local structural co-occurrence neighborhoods.

This component does not infer topic intent, perform reasoning, write
Semantic Memory, perform ontology alignment, score links, resolve
targets, or create highlights.
"""

from __future__ import annotations

import hashlib
from itertools import combinations
from typing import Any, Mapping


PHRASE_NEIGHBORHOOD_INTELLIGENCE_VERSION = (
    "phrase_neighborhood_intelligence_v1"
)


class PhraseNeighborhoodIntelligenceError(RuntimeError):
    """Base fail-closed error for Phase 4.6.3."""



def _stable_neighborhood_id(
    article_id: str,
    left_text: str,
    right_text: str,
) -> str:
    payload = "|".join(
        sorted([
            article_id.strip(),
            left_text.strip().casefold(),
            right_text.strip().casefold(),
        ])
    )

    return (
        "phrase_neighborhood_"
        + hashlib.sha256(
            payload.encode("utf-8")
        ).hexdigest()[:16]
    )


def _evidence_values(
    evidence: list[Mapping[str, Any]],
    key: str,
) -> set[str]:
    return {
        str(item.get(key))
        for item in evidence
        if item.get(key)
    }


def _minimum_char_distance(
    left_evidence: list[Mapping[str, Any]],
    right_evidence: list[Mapping[str, Any]],
) -> int | None:
    distances: list[int] = []

    for left in left_evidence:
        left_start = left.get("article_start_char")

        if not isinstance(left_start, int):
            continue

        for right in right_evidence:
            right_start = right.get("article_start_char")

            if not isinstance(right_start, int):
                continue

            distances.append(
                abs(left_start - right_start)
            )

    return min(distances) if distances else None


def build_phrase_neighborhoods_v1(
    entity_concept_result: Mapping[str, Any],
    *,
    max_neighborhoods: int = 200,
) -> dict[str, Any]:
    """Build structural neighborhoods between certified semantic objects."""

    intake = validate_phrase_neighborhood_intake_v1(
        entity_concept_result
    )

    if (
        not isinstance(max_neighborhoods, int)
        or max_neighborhoods < 1
    ):
        raise PhraseNeighborhoodIntelligenceError(
            "max_neighborhoods must be a positive integer."
        )

    semantic_objects = entity_concept_result[
        "semantic_objects"
    ]

    article_id = str(
        entity_concept_result.get("article_id") or ""
    ).strip()

    if not article_id:
        raise PhraseNeighborhoodIntelligenceError(
            "Canonical article_id is missing."
        )

    neighborhoods: list[dict[str, Any]] = []

    for left, right in combinations(
        semantic_objects,
        2,
    ):
        left_text = left["canonical_text"]
        right_text = right["canonical_text"]

        if left_text == right_text:
            continue

        left_evidence = left["evidence"]
        right_evidence = right["evidence"]

        left_sections = _evidence_values(
            left_evidence,
            "section_id",
        )
        right_sections = _evidence_values(
            right_evidence,
            "section_id",
        )

        left_blocks = _evidence_values(
            left_evidence,
            "block_id",
        )
        right_blocks = _evidence_values(
            right_evidence,
            "block_id",
        )

        left_paragraphs = _evidence_values(
            left_evidence,
            "paragraph_id",
        )
        right_paragraphs = _evidence_values(
            right_evidence,
            "paragraph_id",
        )

        shared_sections = sorted(
            left_sections & right_sections
        )
        shared_blocks = sorted(
            left_blocks & right_blocks
        )
        shared_paragraphs = sorted(
            left_paragraphs & right_paragraphs
        )

        minimum_char_distance = _minimum_char_distance(
            left_evidence,
            right_evidence,
        )

        # An article-level pair is not a neighborhood merely because both
        # objects occur somewhere in the same article. There must be
        # structural overlap or close textual proximity.
        # Canonical neighborhood boundary:
        # two semantic objects must co-occur in at least one canonical
        # paragraph. Block, section, and character-distance evidence may
        # strengthen that neighborhood but cannot create one independently.
        if not shared_paragraphs:
            continue

        proximity_bonus = 0

        if isinstance(minimum_char_distance, int):
            if minimum_char_distance <= 100:
                proximity_bonus = 4
            elif minimum_char_distance <= 200:
                proximity_bonus = 3
            elif minimum_char_distance <= 350:
                proximity_bonus = 2
            else:
                proximity_bonus = 1

        strength_score = (
            len(shared_paragraphs) * 6
            + len(shared_blocks) * 4
            + len(shared_sections) * 2
            + proximity_bonus
        )

        evidence_dimensions = sum([
            bool(shared_paragraphs),
            bool(shared_blocks),
            bool(shared_sections),
            proximity_bonus > 0,
        ])

        confidence = 0.30
        confidence += min(
            len(shared_paragraphs),
            3,
        ) * 0.10
        confidence += min(
            len(shared_blocks),
            4,
        ) * 0.06
        confidence += min(
            len(shared_sections),
            4,
        ) * 0.025
        confidence += proximity_bonus * 0.035

        confidence = round(
            min(confidence, 0.99),
            3,
        )

        neighborhoods.append({
            "neighborhood_id":
                _stable_neighborhood_id(
                    article_id,
                    left_text,
                    right_text,
                ),
            "left_canonical_text":
                left_text,
            "right_canonical_text":
                right_text,
            "left_semantic_kind":
                left["semantic_kind"],
            "right_semantic_kind":
                right["semantic_kind"],
            "shared_section_ids":
                shared_sections,
            "shared_block_ids":
                shared_blocks,
            "shared_paragraph_ids":
                shared_paragraphs,
            "shared_section_count":
                len(shared_sections),
            "shared_block_count":
                len(shared_blocks),
            "shared_paragraph_count":
                len(shared_paragraphs),
            "minimum_char_distance":
                minimum_char_distance,
            "proximity_bonus":
                proximity_bonus,
            "neighborhood_strength":
                strength_score,
            "neighborhood_confidence":
                confidence,
            "evidence_dimensions":
                evidence_dimensions,
            "relationship_semantics_inferred":
                False,
        })

    neighborhoods.sort(
        key=lambda item: (
            -item["neighborhood_strength"],
            -item["neighborhood_confidence"],
            item["left_canonical_text"],
            item["right_canonical_text"],
        )
    )

    neighborhoods = neighborhoods[
        :max_neighborhoods
    ]

    neighbor_map: dict[str, list[dict[str, Any]]] = {}

    for neighborhood in neighborhoods:
        left = neighborhood[
            "left_canonical_text"
        ]
        right = neighborhood[
            "right_canonical_text"
        ]

        neighbor_map.setdefault(
            left,
            [],
        ).append({
            "neighbor":
                right,
            "neighborhood_id":
                neighborhood["neighborhood_id"],
            "strength":
                neighborhood["neighborhood_strength"],
            "confidence":
                neighborhood["neighborhood_confidence"],
        })

        neighbor_map.setdefault(
            right,
            [],
        ).append({
            "neighbor":
                left,
            "neighborhood_id":
                neighborhood["neighborhood_id"],
            "strength":
                neighborhood["neighborhood_strength"],
            "confidence":
                neighborhood["neighborhood_confidence"],
        })

    object_neighborhoods = []

    for item in semantic_objects:
        canonical = item["canonical_text"]

        neighbors = sorted(
            neighbor_map.get(canonical, []),
            key=lambda value: (
                -value["strength"],
                -value["confidence"],
                value["neighbor"],
            ),
        )

        object_neighborhoods.append({
            "canonical_text":
                canonical,
            "semantic_kind":
                item["semantic_kind"],
            "neighbor_count":
                len(neighbors),
            "neighbors":
                neighbors,
        })

    object_neighborhoods.sort(
        key=lambda item: (
            -item["neighbor_count"],
            item["canonical_text"],
        )
    )

    return {
        "schema_version":
            "phrase_neighborhood_model_v1",
        "phase":
            "4.6.3",
        "status":
            "PHRASE_NEIGHBORHOODS_BUILT",
        "article_id":
            article_id,
        "semantic_object_count":
            len(semantic_objects),
        "neighborhood_count":
            len(neighborhoods),
        "neighborhoods":
            neighborhoods,
        "object_neighborhoods":
            object_neighborhoods,
        "relationship_semantics_inferred":
            False,
        "topic_intent_inferred":
            False,
        "reasoning_performed":
            False,
        "semantic_memory_write_performed":
            False,
        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        "next_stage":
            "phrase_neighborhood_output_consolidation",
    }



def run_phrase_neighborhood_intelligence_v1(
    entity_concept_result: Mapping[str, Any],
    *,
    max_neighborhoods: int = 200,
) -> dict[str, Any]:
    """Run canonical Phase 4.6.3 Phrase Neighborhood Intelligence."""

    intake = validate_phrase_neighborhood_intake_v1(
        entity_concept_result
    )

    model = build_phrase_neighborhoods_v1(
        entity_concept_result,
        max_neighborhoods=max_neighborhoods,
    )

    if (
        model.get("status")
        != "PHRASE_NEIGHBORHOODS_BUILT"
    ):
        raise PhraseNeighborhoodIntelligenceError(
            "Phrase neighborhoods were not successfully built."
        )

    neighborhoods = model.get("neighborhoods")

    if not isinstance(neighborhoods, list):
        raise PhraseNeighborhoodIntelligenceError(
            "Phrase neighborhood collection is invalid."
        )

    for item in neighborhoods:
        if not isinstance(item, Mapping):
            raise PhraseNeighborhoodIntelligenceError(
                "Invalid phrase neighborhood record."
            )

        left = item.get("left_canonical_text")
        right = item.get("right_canonical_text")
        confidence = item.get("neighborhood_confidence")
        strength = item.get("neighborhood_strength")
        shared_paragraph_count = item.get(
            "shared_paragraph_count"
        )

        if (
            not isinstance(left, str)
            or not left.strip()
            or not isinstance(right, str)
            or not right.strip()
        ):
            raise PhraseNeighborhoodIntelligenceError(
                "Neighborhood is missing canonical object text."
            )

        if left == right:
            raise PhraseNeighborhoodIntelligenceError(
                "Neighborhood cannot relate an object to itself."
            )

        if (
            not isinstance(shared_paragraph_count, int)
            or shared_paragraph_count < 1
        ):
            raise PhraseNeighborhoodIntelligenceError(
                "Neighborhood lacks canonical paragraph co-occurrence."
            )

        if (
            not isinstance(strength, int)
            or strength < 1
        ):
            raise PhraseNeighborhoodIntelligenceError(
                "Neighborhood has invalid strength."
            )

        if (
            not isinstance(confidence, (int, float))
            or confidence < 0.0
            or confidence > 1.0
        ):
            raise PhraseNeighborhoodIntelligenceError(
                "Neighborhood has invalid confidence."
            )

        if (
            item.get("relationship_semantics_inferred")
            is not False
        ):
            raise PhraseNeighborhoodIntelligenceError(
                "4.6.3 must not infer relationship semantics."
            )

    return {
        "schema_version":
            "phrase_neighborhood_intelligence_result_v1",
        "engine_version":
            PHRASE_NEIGHBORHOOD_INTELLIGENCE_VERSION,
        "phase":
            "4.6.3",
        "status":
            "PHRASE_NEIGHBORHOOD_INTELLIGENCE_COMPLETE",
        "workspace_id":
            intake.get("workspace_id"),
        "document_id":
            intake.get("document_id"),
        "source_type":
            intake.get("source_type"),
        "source_id":
            intake.get("source_id"),
        "content_hash":
            intake.get("content_hash"),
        "body_ref":
            intake.get("body_ref"),
        "article_id":
            intake.get("article_id"),
        "title":
            intake.get("title"),
        "final_primary_topic":
            intake.get("final_primary_topic"),
        "semantic_object_count":
            model["semantic_object_count"],
        "neighborhood_count":
            model["neighborhood_count"],
        "neighborhoods":
            neighborhoods,
        "object_neighborhoods":
            model["object_neighborhoods"],
        "canonical_neighborhood_rule":
            "SHARED_CANONICAL_PARAGRAPH_REQUIRED",
        "processing_boundaries": {
            "article_local_only":
                True,
            "relationship_semantics_inferred":
                False,
            "topic_intent_intelligence_performed":
                False,
            "section_evidence_intelligence_performed":
                False,
            "reasoning_performed":
                False,
            "ontology_alignment_performed":
                False,
            "semantic_memory_write_performed":
                False,
            "learning_performed":
                False,
            "link_scoring_performed":
                False,
            "target_resolution_performed":
                False,
            "highlighting_performed":
                False,
        },
        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        "next_stage":
            "topic_intent_intelligence",
    }


def validate_phrase_neighborhood_intake_v1(
    entity_concept_result: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate the canonical 4.6.2 -> 4.6.3 handoff."""

    if not isinstance(entity_concept_result, Mapping):
        raise PhraseNeighborhoodIntelligenceError(
            "entity_concept_result must be a mapping."
        )

    if (
        entity_concept_result.get("schema_version")
        != "entity_concept_intelligence_result_v1"
    ):
        raise PhraseNeighborhoodIntelligenceError(
            "Unsupported Entity & Concept Intelligence result schema."
        )

    if (
        entity_concept_result.get("status")
        != "ENTITY_CONCEPT_INTELLIGENCE_COMPLETE"
    ):
        raise PhraseNeighborhoodIntelligenceError(
            "Entity & Concept Intelligence is not complete."
        )

    if (
        entity_concept_result.get("phase")
        != "4.6.2"
    ):
        raise PhraseNeighborhoodIntelligenceError(
            "Entity & Concept Intelligence phase is invalid."
        )

    if (
        entity_concept_result.get("next_stage")
        != "phrase_neighborhood_intelligence"
    ):
        raise PhraseNeighborhoodIntelligenceError(
            "Entity & Concept Intelligence is not authorized to hand off "
            "to Phrase Neighborhood Intelligence."
        )

    semantic_objects = entity_concept_result.get(
        "semantic_objects"
    )

    if (
        not isinstance(semantic_objects, list)
        or not semantic_objects
    ):
        raise PhraseNeighborhoodIntelligenceError(
            "No certified semantic objects are available."
        )

    boundaries = entity_concept_result.get(
        "processing_boundaries"
    )

    if not isinstance(boundaries, Mapping):
        raise PhraseNeighborhoodIntelligenceError(
            "Entity & Concept Intelligence boundary evidence is missing."
        )

    if boundaries.get("article_local_only") is not True:
        raise PhraseNeighborhoodIntelligenceError(
            "Entity & Concept Intelligence is not article-local."
        )

    if (
        boundaries.get(
            "phrase_neighborhood_intelligence_performed"
        )
        is not False
    ):
        raise PhraseNeighborhoodIntelligenceError(
            "Phrase Neighborhood Intelligence was already performed."
        )

    if (
        entity_concept_result.get("persistence_policy")
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise PhraseNeighborhoodIntelligenceError(
            "Unsupported semantic intelligence persistence policy."
        )

    for item in semantic_objects:
        if not isinstance(item, Mapping):
            raise PhraseNeighborhoodIntelligenceError(
                "Invalid semantic object in 4.6.2 result."
            )

        canonical_text = item.get("canonical_text")
        semantic_kind = item.get("semantic_kind")
        evidence = item.get("evidence")

        if (
            not isinstance(canonical_text, str)
            or not canonical_text.strip()
        ):
            raise PhraseNeighborhoodIntelligenceError(
                "Semantic object is missing canonical_text."
            )

        if semantic_kind not in {"entity", "concept"}:
            raise PhraseNeighborhoodIntelligenceError(
                "Semantic object has invalid semantic_kind."
            )

        if not isinstance(evidence, list) or not evidence:
            raise PhraseNeighborhoodIntelligenceError(
                "Semantic object is missing mention evidence."
            )

    return {
        "schema_version":
            "phrase_neighborhood_intake_v1",
        "phase":
            "4.6.3",
        "status":
            "PHRASE_NEIGHBORHOOD_INTAKE_ACCEPTED",
        "workspace_id":
            entity_concept_result.get("workspace_id"),
        "document_id":
            entity_concept_result.get("document_id"),
        "source_type":
            entity_concept_result.get("source_type"),
        "source_id":
            entity_concept_result.get("source_id"),
        "content_hash":
            entity_concept_result.get("content_hash"),
        "body_ref":
            entity_concept_result.get("body_ref"),
        "article_id":
            entity_concept_result.get("article_id"),
        "title":
            entity_concept_result.get("title"),
        "final_primary_topic":
            entity_concept_result.get("final_primary_topic"),
        "semantic_object_count":
            len(semantic_objects),
        "intake_authorized":
            True,
        "next_stage":
            "structural_cooccurrence_detection",
    }


__all__ = [
    "PHRASE_NEIGHBORHOOD_INTELLIGENCE_VERSION",
    "PhraseNeighborhoodIntelligenceError",
    "build_phrase_neighborhoods_v1",
    "run_phrase_neighborhood_intelligence_v1",
    "validate_phrase_neighborhood_intake_v1",
]
