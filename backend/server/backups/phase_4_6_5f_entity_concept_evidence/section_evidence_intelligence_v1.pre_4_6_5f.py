from __future__ import annotations

import hashlib
import re
from collections import Counter, defaultdict
from typing import Any, Mapping


SECTION_EVIDENCE_INTELLIGENCE_VERSION = (
    "section_evidence_intelligence_v1"
)


class SectionEvidenceIntelligenceError(ValueError):
    """Raised when canonical Section Evidence Intelligence cannot proceed."""


def _stable_id(prefix: str, *parts: Any) -> str:
    raw = "|".join(str(part) for part in parts)
    digest = hashlib.sha1(
        raw.encode("utf-8")
    ).hexdigest()[:12]
    return f"{prefix}_{digest}"


def validate_section_evidence_intake_v1(
    topic_intent_result: Mapping[str, Any],
    phrase_neighborhood_result: Mapping[str, Any],
    entity_concept_result: Mapping[str, Any],
    runtime_reader_result: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate the certified 4.6.1-4.6.4 -> 4.6.5 handoff."""

    if not isinstance(topic_intent_result, Mapping):
        raise SectionEvidenceIntelligenceError(
            "topic_intent_result must be a mapping."
        )

    if not isinstance(phrase_neighborhood_result, Mapping):
        raise SectionEvidenceIntelligenceError(
            "phrase_neighborhood_result must be a mapping."
        )

    if not isinstance(entity_concept_result, Mapping):
        raise SectionEvidenceIntelligenceError(
            "entity_concept_result must be a mapping."
        )

    if not isinstance(runtime_reader_result, Mapping):
        raise SectionEvidenceIntelligenceError(
            "runtime_reader_result must be a mapping."
        )

    if (
        topic_intent_result.get("schema_version")
        != "topic_intent_intelligence_result_v1"
    ):
        raise SectionEvidenceIntelligenceError(
            "Unsupported Topic Intent Intelligence result schema."
        )

    if (
        topic_intent_result.get("status")
        != "TOPIC_INTENT_INTELLIGENCE_COMPLETE"
    ):
        raise SectionEvidenceIntelligenceError(
            "Topic Intent Intelligence is not complete."
        )

    if topic_intent_result.get("phase") != "4.6.4":
        raise SectionEvidenceIntelligenceError(
            "Topic Intent Intelligence phase is invalid."
        )

    if (
        topic_intent_result.get("next_stage")
        != "section_evidence_intelligence"
    ):
        raise SectionEvidenceIntelligenceError(
            "Topic Intent Intelligence is not authorized to hand off "
            "to Section Evidence Intelligence."
        )

    boundaries = topic_intent_result.get(
        "processing_boundaries"
    )

    if not isinstance(boundaries, Mapping):
        raise SectionEvidenceIntelligenceError(
            "Topic Intent Intelligence boundary evidence is missing."
        )

    if boundaries.get("article_local_only") is not True:
        raise SectionEvidenceIntelligenceError(
            "Topic Intent Intelligence is not article-local."
        )

    if (
        boundaries.get(
            "section_evidence_intelligence_performed"
        )
        is not False
    ):
        raise SectionEvidenceIntelligenceError(
            "Section Evidence Intelligence was already performed."
        )

    if (
        topic_intent_result.get("persistence_policy")
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise SectionEvidenceIntelligenceError(
            "Unsupported Topic Intent persistence policy."
        )

    if (
        phrase_neighborhood_result.get("schema_version")
        != "phrase_neighborhood_intelligence_result_v1"
    ):
        raise SectionEvidenceIntelligenceError(
            "Unsupported Phrase Neighborhood Intelligence result schema."
        )

    if (
        phrase_neighborhood_result.get("status")
        != "PHRASE_NEIGHBORHOOD_INTELLIGENCE_COMPLETE"
    ):
        raise SectionEvidenceIntelligenceError(
            "Phrase Neighborhood Intelligence is not complete."
        )

    if (
        entity_concept_result.get("schema_version")
        != "entity_concept_intelligence_result_v1"
    ):
        raise SectionEvidenceIntelligenceError(
            "Unsupported Entity & Concept Intelligence result schema."
        )

    if (
        entity_concept_result.get("status")
        != "ENTITY_CONCEPT_INTELLIGENCE_COMPLETE"
    ):
        raise SectionEvidenceIntelligenceError(
            "Entity & Concept Intelligence is not complete."
        )

    if (
        runtime_reader_result.get("schema_version")
        != "semantic_intelligence_runtime_reader_result_v1"
    ):
        raise SectionEvidenceIntelligenceError(
            "Unsupported Runtime Reader result schema."
        )

    if (
        runtime_reader_result.get("status")
        != "SEMANTIC_RUNTIME_READING_COMPLETE"
    ):
        raise SectionEvidenceIntelligenceError(
            "Semantic Intelligence Runtime Reader is not complete."
        )

    runtime_model = runtime_reader_result.get(
        "semantic_reading_model"
    )

    if not isinstance(runtime_model, Mapping):
        raise SectionEvidenceIntelligenceError(
            "Semantic reading model is missing."
        )

    if runtime_model.get("structure_source") != "canonical_uucd":
        raise SectionEvidenceIntelligenceError(
            "Semantic reading model is not based on canonical UUCD structure."
        )

    validation = runtime_model.get("validation")

    if (
        not isinstance(validation, Mapping)
        or validation.get("valid") is not True
    ):
        raise SectionEvidenceIntelligenceError(
            "Semantic reading structure is not certified valid."
        )

    sections = runtime_model.get("sections")

    if not isinstance(sections, list) or not sections:
        raise SectionEvidenceIntelligenceError(
            "Canonical section structure is missing."
        )

    identity_fields = (
        "workspace_id",
        "document_id",
        "source_type",
        "source_id",
        "content_hash",
        "body_ref",
    )

    for field in identity_fields:
        expected = topic_intent_result.get(field)

        for name, model in (
            ("phrase_neighborhood", phrase_neighborhood_result),
            ("entity_concept", entity_concept_result),
            ("runtime_reader", runtime_reader_result),
        ):
            if model.get(field) != expected:
                raise SectionEvidenceIntelligenceError(
                    f"Identity mismatch for {field} in {name}."
                )

    article_id = str(
        topic_intent_result.get("article_id") or ""
    ).strip()

    runtime_article = runtime_model.get("article")

    if not isinstance(runtime_article, Mapping):
        raise SectionEvidenceIntelligenceError(
            "Runtime article identity is missing."
        )

    runtime_article_id = str(
        runtime_article.get("article_id") or ""
    ).strip()

    if (
        not article_id
        or not runtime_article_id
        or article_id != runtime_article_id
    ):
        raise SectionEvidenceIntelligenceError(
            "Topic Intent and Runtime Reader article identities "
            "do not match."
        )

    section_intents = topic_intent_result.get(
        "section_content_intents"
    )

    if (
        not isinstance(section_intents, list)
        or len(section_intents) != len(sections)
    ):
        raise SectionEvidenceIntelligenceError(
            "Topic Intent section coverage does not match "
            "canonical section structure."
        )

    return {
        "schema_version":
            "section_evidence_intake_v1",
        "phase":
            "4.6.5",
        "status":
            "SECTION_EVIDENCE_INTAKE_ACCEPTED",
        "workspace_id":
            topic_intent_result.get("workspace_id"),
        "document_id":
            topic_intent_result.get("document_id"),
        "source_type":
            topic_intent_result.get("source_type"),
        "source_id":
            topic_intent_result.get("source_id"),
        "content_hash":
            topic_intent_result.get("content_hash"),
        "body_ref":
            topic_intent_result.get("body_ref"),
        "article_id":
            article_id,
        "title":
            topic_intent_result.get("title"),
        "section_count":
            len(sections),
        "intake_authorized":
            True,
        "next_stage":
            "section_evidence_unit_construction",
    }


def build_section_evidence_units_v1(
    topic_intent_result: Mapping[str, Any],
    phrase_neighborhood_result: Mapping[str, Any],
    entity_concept_result: Mapping[str, Any],
    runtime_reader_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Build one article-local Section Evidence Unit per canonical section.

    4.6.5D responsibility:
    - preserve canonical Runtime Reader section identity
    - preserve canonical section ordering and hierarchy
    - establish stable Section Evidence Unit identities
    - establish structural source references for later evidence attachment

    This stage does not:
    - attach structural evidence details
    - attach entity/concept evidence
    - attach phrase-neighborhood evidence
    - attach topic-intent evidence
    - extract claims
    - score evidence
    - infer contradictions
    - perform reasoning
    - persist semantic intelligence
    """

    intake = validate_section_evidence_intake_v1(
        topic_intent_result,
        phrase_neighborhood_result,
        entity_concept_result,
        runtime_reader_result,
    )

    runtime_model = runtime_reader_result.get(
        "semantic_reading_model"
    )

    if not isinstance(runtime_model, Mapping):
        raise SectionEvidenceIntelligenceError(
            "Semantic reading model is missing."
        )

    sections = runtime_model.get("sections")

    if not isinstance(sections, list) or not sections:
        raise SectionEvidenceIntelligenceError(
            "Canonical section structure is missing."
        )

    article_id = str(
        intake.get("article_id") or ""
    ).strip()

    if not article_id:
        raise SectionEvidenceIntelligenceError(
            "Section Evidence intake is missing article_id."
        )

    section_intents = topic_intent_result.get(
        "section_content_intents"
    )

    if not isinstance(section_intents, list):
        raise SectionEvidenceIntelligenceError(
            "Topic Intent section collection is invalid."
        )

    intent_ids = []

    for item in section_intents:
        if not isinstance(item, Mapping):
            raise SectionEvidenceIntelligenceError(
                "Invalid Topic Intent section record."
            )

        section_id = str(
            item.get("section_id") or ""
        ).strip()

        if not section_id:
            raise SectionEvidenceIntelligenceError(
                "Topic Intent section record is missing section_id."
            )

        intent_ids.append(section_id)

    if len(intent_ids) != len(set(intent_ids)):
        raise SectionEvidenceIntelligenceError(
            "Duplicate section_id detected in Topic Intent output."
        )

    units: list[dict[str, Any]] = []
    canonical_section_ids: list[str] = []

    for section in sections:
        if not isinstance(section, Mapping):
            raise SectionEvidenceIntelligenceError(
                "Invalid canonical section record."
            )

        section_id = str(
            section.get("section_id") or ""
        ).strip()

        if not section_id:
            raise SectionEvidenceIntelligenceError(
                "Canonical section is missing section_id."
            )

        if section_id in canonical_section_ids:
            raise SectionEvidenceIntelligenceError(
                "Duplicate canonical section_id detected."
            )

        canonical_section_ids.append(
            section_id
        )

        block_ids = section.get(
            "block_ids"
        )
        paragraph_ids = section.get(
            "paragraph_ids"
        )
        children_section_ids = section.get(
            "children_section_ids"
        )

        if not isinstance(block_ids, list):
            raise SectionEvidenceIntelligenceError(
                f"Canonical section {section_id} "
                "has invalid block_ids."
            )

        if not isinstance(paragraph_ids, list):
            raise SectionEvidenceIntelligenceError(
                f"Canonical section {section_id} "
                "has invalid paragraph_ids."
            )

        if not isinstance(
            children_section_ids,
            list,
        ):
            raise SectionEvidenceIntelligenceError(
                f"Canonical section {section_id} "
                "has invalid children_section_ids."
            )

        unit_id = _stable_id(
            "section_evidence_unit",
            article_id,
            section_id,
        )

        units.append({
            "section_evidence_unit_id":
                unit_id,

            "article_id":
                article_id,

            "section_id":
                section_id,

            "section_index":
                section.get("section_index"),

            "section_title":
                section.get("section_title"),

            "heading_level":
                section.get("heading_level"),

            "section_depth":
                section.get("section_depth"),

            "parent_section_id":
                section.get("parent_section_id"),

            "children_section_ids":
                list(children_section_ids),

            "canonical_source": {
                "source":
                    "semantic_intelligence_runtime_reader_v1",
                "structure_source":
                    runtime_model.get("structure_source"),
                "block_ids":
                    list(block_ids),
                "paragraph_ids":
                    list(paragraph_ids),
                "start_line":
                    section.get("start_line"),
                "end_line":
                    section.get("end_line"),
                "start_char":
                    section.get("start_char"),
                "end_char":
                    section.get("end_char"),
            },

            "evidence_attachment_state": {
                "structural_evidence":
                    "PENDING",
                "entity_concept_evidence":
                    "PENDING",
                "phrase_neighborhood_evidence":
                    "PENDING",
                "topic_intent_evidence":
                    "PENDING",
                "claim_evidence":
                    "PENDING",
                "evidence_strength":
                    "PENDING",
                "coverage":
                    "PENDING",
                "contradiction_analysis":
                    "PENDING",
            },
        })

    if set(canonical_section_ids) != set(intent_ids):
        raise SectionEvidenceIntelligenceError(
            "Canonical Runtime Reader section identities "
            "do not exactly match Topic Intent section identities."
        )

    if len(units) != intake.get("section_count"):
        raise SectionEvidenceIntelligenceError(
            "Section Evidence Unit count does not match "
            "certified intake section count."
        )

    return {
        "schema_version":
            "section_evidence_units_v1",

        "section_evidence_version":
            SECTION_EVIDENCE_INTELLIGENCE_VERSION,

        "phase":
            "4.6.5",

        "patch":
            "4.6.5D",

        "status":
            "SECTION_EVIDENCE_UNITS_BUILT",

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
            article_id,

        "title":
            intake.get("title"),

        "section_count":
            len(units),

        "section_evidence_units":
            units,

        "canonical_section_order":
            canonical_section_ids,

        "processing_boundaries": {
            "article_local_only":
                True,
            "canonical_runtime_structure_consumed":
                True,
            "raw_article_reparsed":
                False,
            "structural_evidence_attached":
                False,
            "entity_concept_evidence_attached":
                False,
            "phrase_neighborhood_evidence_attached":
                False,
            "topic_intent_evidence_attached":
                False,
            "claim_extraction_performed":
                False,
            "evidence_scoring_performed":
                False,
            "contradiction_analysis_performed":
                False,
            "reasoning_performed":
                False,
            "semantic_memory_write_performed":
                False,
            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "structural_evidence_mapping",
    }


def map_structural_evidence_v1(
    section_units_result: Mapping[str, Any],
    runtime_reader_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Attach canonical structural evidence to each Section Evidence Unit.

    4.6.5E performs structural evidence mapping only.
    It does not attach semantic-object, phrase-neighborhood,
    topic-intent, claim, scoring, contradiction, or reasoning evidence.
    """

    if not isinstance(section_units_result, Mapping):
        raise SectionEvidenceIntelligenceError(
            "section_units_result must be a mapping."
        )

    if (
        section_units_result.get("schema_version")
        != "section_evidence_units_v1"
        or section_units_result.get("status")
        != "SECTION_EVIDENCE_UNITS_BUILT"
        or section_units_result.get("phase")
        != "4.6.5"
    ):
        raise SectionEvidenceIntelligenceError(
            "Section Evidence Unit input is not certified 4.6.5D output."
        )

    if not isinstance(runtime_reader_result, Mapping):
        raise SectionEvidenceIntelligenceError(
            "runtime_reader_result must be a mapping."
        )

    if (
        runtime_reader_result.get("schema_version")
        != "semantic_intelligence_runtime_reader_result_v1"
        or runtime_reader_result.get("status")
        != "SEMANTIC_RUNTIME_READING_COMPLETE"
    ):
        raise SectionEvidenceIntelligenceError(
            "Runtime Reader result is not complete."
        )

    identity_fields = (
        "workspace_id",
        "document_id",
        "source_type",
        "source_id",
        "content_hash",
        "body_ref",
    )

    for field in identity_fields:
        if (
            section_units_result.get(field)
            != runtime_reader_result.get(field)
        ):
            raise SectionEvidenceIntelligenceError(
                f"Identity mismatch for {field}."
            )

    runtime_model = runtime_reader_result.get(
        "semantic_reading_model"
    )

    if not isinstance(runtime_model, Mapping):
        raise SectionEvidenceIntelligenceError(
            "Semantic Reading Model is missing."
        )

    runtime_article = runtime_model.get("article")

    if not isinstance(runtime_article, Mapping):
        raise SectionEvidenceIntelligenceError(
            "Runtime article identity is missing."
        )

    if (
        section_units_result.get("article_id")
        != runtime_article.get("article_id")
    ):
        raise SectionEvidenceIntelligenceError(
            "Identity mismatch for article_id."
        )

    if (
        runtime_model.get("structure_source")
        != "canonical_uucd"
    ):
        raise SectionEvidenceIntelligenceError(
            "Structural evidence must come from canonical UUCD structure."
        )

    validation = runtime_model.get("validation")

    if (
        not isinstance(validation, Mapping)
        or validation.get("valid") is not True
    ):
        raise SectionEvidenceIntelligenceError(
            "Canonical Runtime Reader structure is not valid."
        )

    sections = runtime_model.get("sections")
    blocks = runtime_model.get("blocks")
    units = section_units_result.get(
        "section_evidence_units"
    )

    if not isinstance(sections, list):
        raise SectionEvidenceIntelligenceError(
            "Runtime section collection is invalid."
        )

    if not isinstance(blocks, list):
        raise SectionEvidenceIntelligenceError(
            "Runtime block collection is invalid."
        )

    if not isinstance(units, list):
        raise SectionEvidenceIntelligenceError(
            "Section Evidence Unit collection is invalid."
        )

    sections_by_id: dict[str, Mapping[str, Any]] = {}

    for section in sections:
        if not isinstance(section, Mapping):
            raise SectionEvidenceIntelligenceError(
                "Invalid canonical section record."
            )

        section_id = str(
            section.get("section_id") or ""
        ).strip()

        if not section_id:
            raise SectionEvidenceIntelligenceError(
                "Canonical section is missing section_id."
            )

        sections_by_id[section_id] = section

    blocks_by_section: dict[
        str,
        list[Mapping[str, Any]],
    ] = defaultdict(list)

    for block in blocks:
        if not isinstance(block, Mapping):
            raise SectionEvidenceIntelligenceError(
                "Invalid canonical block record."
            )

        section_id = str(
            block.get("section_id") or ""
        ).strip()

        if not section_id:
            raise SectionEvidenceIntelligenceError(
                "Canonical block is missing section_id."
            )

        blocks_by_section[
            section_id
        ].append(block)

    mapped_units: list[dict[str, Any]] = []

    for unit in units:
        if not isinstance(unit, Mapping):
            raise SectionEvidenceIntelligenceError(
                "Invalid Section Evidence Unit."
            )

        section_id = str(
            unit.get("section_id") or ""
        ).strip()

        section = sections_by_id.get(
            section_id
        )

        if not isinstance(section, Mapping):
            raise SectionEvidenceIntelligenceError(
                f"Section Evidence Unit {section_id} "
                "has no matching canonical section."
            )

        section_blocks = blocks_by_section.get(
            section_id,
            [],
        )

        expected_block_ids = list(
            section.get("block_ids") or []
        )

        observed_block_ids = [
            block.get("block_id")
            for block in section_blocks
        ]

        if observed_block_ids != expected_block_ids:
            raise SectionEvidenceIntelligenceError(
                f"Canonical block order mismatch for section {section_id}."
            )

        block_type_counts = Counter(
            str(
                block.get("block_type")
                or "unknown"
            )
            for block in section_blocks
        )

        block_evidence = []

        for block in section_blocks:
            metadata = block.get(
                "metadata"
            )

            if not isinstance(metadata, Mapping):
                metadata = {}

            sentences = block.get(
                "sentences"
            )

            if not isinstance(sentences, list):
                sentences = []

            block_evidence.append({
                "block_id":
                    block.get("block_id"),
                "paragraph_id":
                    block.get("paragraph_id"),
                "block_index":
                    block.get("block_index"),
                "block_type":
                    block.get("block_type"),
                "heading_depth":
                    block.get("heading_depth"),
                "section_depth":
                    block.get("section_depth"),
                "start_line":
                    block.get("start_line"),
                "end_line":
                    block.get("end_line"),
                "start_char":
                    block.get("start_char"),
                "end_char":
                    block.get("end_char"),
                "word_count":
                    metadata.get("word_count"),
                "character_count":
                    metadata.get("character_count"),
                "sentence_count":
                    len(sentences),
            })

        section_metadata = section.get(
            "metadata"
        )

        if not isinstance(
            section_metadata,
            Mapping,
        ):
            section_metadata = {}

        structural_evidence = {
            "evidence_source":
                "canonical_semantic_reading_model",

            "structure_source":
                runtime_model.get("structure_source"),

            "section_id":
                section_id,

            "section_index":
                section.get("section_index"),

            "section_title":
                section.get("section_title"),

            "heading_level":
                section.get("heading_level"),

            "section_depth":
                section.get("section_depth"),

            "parent_section_id":
                section.get("parent_section_id"),

            "children_section_ids":
                list(
                    section.get(
                        "children_section_ids"
                    )
                    or []
                ),

            "start_line":
                section.get("start_line"),

            "end_line":
                section.get("end_line"),

            "start_char":
                section.get("start_char"),

            "end_char":
                section.get("end_char"),

            "block_count":
                len(section_blocks),

            "paragraph_count":
                len(
                    section.get(
                        "paragraph_ids"
                    )
                    or []
                ),

            "sentence_count":
                section_metadata.get(
                    "section_sentence_count",
                    section_metadata.get(
                        "sentence_count",
                        0,
                    ),
                ),

            "word_count":
                section_metadata.get(
                    "section_word_count",
                    section_metadata.get(
                        "word_count",
                        0,
                    ),
                ),

            "character_count":
                section_metadata.get(
                    "character_count",
                    0,
                ),

            "block_type_counts":
                dict(block_type_counts),

            "block_ids":
                expected_block_ids,

            "paragraph_ids":
                list(
                    section.get(
                        "paragraph_ids"
                    )
                    or []
                ),

            "blocks":
                block_evidence,
        }

        mapped_unit = dict(unit)

        mapped_unit[
            "structural_evidence"
        ] = structural_evidence

        state = dict(
            unit.get(
                "evidence_attachment_state"
            )
            or {}
        )

        state[
            "structural_evidence"
        ] = "ATTACHED"

        mapped_unit[
            "evidence_attachment_state"
        ] = state

        mapped_units.append(
            mapped_unit
        )

    canonical_order = list(
        section_units_result.get(
            "canonical_section_order"
        )
        or []
    )

    mapped_order = [
        unit.get("section_id")
        for unit in mapped_units
    ]

    if mapped_order != canonical_order:
        raise SectionEvidenceIntelligenceError(
            "Structural evidence mapping changed canonical section order."
        )

    return {
        "schema_version":
            "section_structural_evidence_v1",

        "section_evidence_version":
            SECTION_EVIDENCE_INTELLIGENCE_VERSION,

        "phase":
            "4.6.5",

        "patch":
            "4.6.5E",

        "status":
            "STRUCTURAL_EVIDENCE_MAPPED",

        "workspace_id":
            section_units_result.get("workspace_id"),

        "document_id":
            section_units_result.get("document_id"),

        "source_type":
            section_units_result.get("source_type"),

        "source_id":
            section_units_result.get("source_id"),

        "content_hash":
            section_units_result.get("content_hash"),

        "body_ref":
            section_units_result.get("body_ref"),

        "article_id":
            section_units_result.get("article_id"),

        "title":
            section_units_result.get("title"),

        "section_count":
            len(mapped_units),

        "section_evidence_units":
            mapped_units,

        "canonical_section_order":
            canonical_order,

        "processing_boundaries": {
            "article_local_only":
                True,
            "canonical_runtime_structure_consumed":
                True,
            "raw_article_reparsed":
                False,
            "structural_evidence_attached":
                True,
            "entity_concept_evidence_attached":
                False,
            "phrase_neighborhood_evidence_attached":
                False,
            "topic_intent_evidence_attached":
                False,
            "claim_extraction_performed":
                False,
            "evidence_scoring_performed":
                False,
            "contradiction_analysis_performed":
                False,
            "reasoning_performed":
                False,
            "semantic_memory_write_performed":
                False,
            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "entity_concept_evidence_attachment",
    }


__all__ = [
    "SECTION_EVIDENCE_INTELLIGENCE_VERSION",
    "SectionEvidenceIntelligenceError",
    "validate_section_evidence_intake_v1",
    "build_section_evidence_units_v1",
    "map_structural_evidence_v1",
]
