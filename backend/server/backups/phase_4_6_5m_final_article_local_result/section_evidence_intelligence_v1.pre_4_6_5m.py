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


def attach_entity_concept_evidence_v1(
    structural_evidence_result: Mapping[str, Any],
    entity_concept_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Attach certified article-local Entity & Concept Intelligence
    evidence to the matching Section Evidence Units.

    4.6.5F performs evidence attachment only.
    It does not perform new entity extraction, relationship inference,
    phrase-neighborhood analysis, topic-intent analysis, reasoning,
    scoring, contradiction analysis, linking, or persistence.
    """

    if not isinstance(
        structural_evidence_result,
        Mapping,
    ):
        raise SectionEvidenceIntelligenceError(
            "structural_evidence_result must be a mapping."
        )

    if (
        structural_evidence_result.get("schema_version")
        != "section_structural_evidence_v1"
        or structural_evidence_result.get("status")
        != "STRUCTURAL_EVIDENCE_MAPPED"
        or structural_evidence_result.get("phase")
        != "4.6.5"
    ):
        raise SectionEvidenceIntelligenceError(
            "Entity/Concept attachment requires certified "
            "4.6.5E structural evidence."
        )

    if not isinstance(entity_concept_result, Mapping):
        raise SectionEvidenceIntelligenceError(
            "entity_concept_result must be a mapping."
        )

    if (
        entity_concept_result.get("schema_version")
        != "entity_concept_intelligence_result_v1"
        or entity_concept_result.get("status")
        != "ENTITY_CONCEPT_INTELLIGENCE_COMPLETE"
    ):
        raise SectionEvidenceIntelligenceError(
            "Entity & Concept Intelligence result is not complete."
        )

    identity_fields = (
        "workspace_id",
        "document_id",
        "source_type",
        "source_id",
        "content_hash",
        "body_ref",
        "article_id",
    )

    for field in identity_fields:
        if (
            structural_evidence_result.get(field)
            != entity_concept_result.get(field)
        ):
            raise SectionEvidenceIntelligenceError(
                f"Identity mismatch for {field}."
            )

    units = structural_evidence_result.get(
        "section_evidence_units"
    )

    semantic_objects = entity_concept_result.get(
        "semantic_objects"
    )

    if not isinstance(units, list):
        raise SectionEvidenceIntelligenceError(
            "Section Evidence Unit collection is invalid."
        )

    if not isinstance(semantic_objects, list):
        raise SectionEvidenceIntelligenceError(
            "Entity/Concept semantic object collection is invalid."
        )

    attached_units: list[dict[str, Any]] = []

    total_section_object_references = 0
    total_section_mentions = 0

    for unit in units:
        if not isinstance(unit, Mapping):
            raise SectionEvidenceIntelligenceError(
                "Invalid Section Evidence Unit."
            )

        section_id = str(
            unit.get("section_id") or ""
        ).strip()

        if not section_id:
            raise SectionEvidenceIntelligenceError(
                "Section Evidence Unit is missing section_id."
            )

        section_objects: list[dict[str, Any]] = []

        for semantic_object in semantic_objects:
            if not isinstance(
                semantic_object,
                Mapping,
            ):
                raise SectionEvidenceIntelligenceError(
                    "Invalid Entity/Concept semantic object."
                )

            object_section_ids = (
                semantic_object.get("section_ids")
            )

            if not isinstance(
                object_section_ids,
                list,
            ):
                object_section_ids = []

            if section_id not in object_section_ids:
                continue

            raw_evidence = semantic_object.get(
                "evidence"
            )

            if not isinstance(raw_evidence, list):
                raw_evidence = []

            section_mentions = [
                dict(mention)
                for mention in raw_evidence
                if (
                    isinstance(mention, Mapping)
                    and str(
                        mention.get("section_id")
                        or ""
                    ).strip()
                    == section_id
                )
            ]

            if not section_mentions:
                raise SectionEvidenceIntelligenceError(
                    "Semantic object references a section but "
                    "contains no matching section evidence."
                )

            section_block_ids = sorted({
                str(
                    mention.get("block_id")
                )
                for mention in section_mentions
                if mention.get("block_id")
            })

            section_paragraph_ids = sorted({
                str(
                    mention.get("paragraph_id")
                )
                for mention in section_mentions
                if mention.get("paragraph_id")
            })

            section_objects.append({
                "canonical_text":
                    semantic_object.get(
                        "canonical_text"
                    ),

                "semantic_kind":
                    semantic_object.get(
                        "semantic_kind"
                    ),

                "surface_forms":
                    list(
                        semantic_object.get(
                            "surface_forms"
                        )
                        or []
                    ),

                "extraction_confidence":
                    semantic_object.get(
                        "extraction_confidence"
                    ),

                "registry_backed":
                    semantic_object.get(
                        "registry_backed"
                    ),

                "registry_domain":
                    semantic_object.get(
                        "registry_domain"
                    ),

                "registry_category":
                    semantic_object.get(
                        "registry_category"
                    ),

                "section_mention_count":
                    len(section_mentions),

                "section_block_ids":
                    section_block_ids,

                "section_paragraph_ids":
                    section_paragraph_ids,

                "mentions":
                    section_mentions,
            })

        entity_count = sum(
            1
            for item in section_objects
            if item.get("semantic_kind")
            == "entity"
        )

        concept_count = sum(
            1
            for item in section_objects
            if item.get("semantic_kind")
            == "concept"
        )

        mention_count = sum(
            int(
                item.get(
                    "section_mention_count"
                )
                or 0
            )
            for item in section_objects
        )

        total_section_object_references += len(
            section_objects
        )
        total_section_mentions += mention_count

        mapped_unit = dict(unit)

        mapped_unit[
            "entity_concept_evidence"
        ] = {
            "evidence_source":
                "entity_concept_intelligence_v1",

            "article_local_only":
                True,

            "section_id":
                section_id,

            "semantic_object_count":
                len(section_objects),

            "entity_count":
                entity_count,

            "concept_count":
                concept_count,

            "mention_count":
                mention_count,

            "semantic_objects":
                section_objects,
        }

        state = dict(
            unit.get(
                "evidence_attachment_state"
            )
            or {}
        )

        if state.get(
            "structural_evidence"
        ) != "ATTACHED":
            raise SectionEvidenceIntelligenceError(
                "Entity/Concept evidence cannot be attached "
                "before structural evidence."
            )

        state[
            "entity_concept_evidence"
        ] = "ATTACHED"

        mapped_unit[
            "evidence_attachment_state"
        ] = state

        attached_units.append(
            mapped_unit
        )

    canonical_order = list(
        structural_evidence_result.get(
            "canonical_section_order"
        )
        or []
    )

    attached_order = [
        unit.get("section_id")
        for unit in attached_units
    ]

    if attached_order != canonical_order:
        raise SectionEvidenceIntelligenceError(
            "Entity/Concept evidence attachment changed "
            "canonical section order."
        )

    return {
        "schema_version":
            "section_entity_concept_evidence_v1",

        "section_evidence_version":
            SECTION_EVIDENCE_INTELLIGENCE_VERSION,

        "phase":
            "4.6.5",

        "patch":
            "4.6.5F",

        "status":
            "ENTITY_CONCEPT_EVIDENCE_ATTACHED",

        "workspace_id":
            structural_evidence_result.get(
                "workspace_id"
            ),

        "document_id":
            structural_evidence_result.get(
                "document_id"
            ),

        "source_type":
            structural_evidence_result.get(
                "source_type"
            ),

        "source_id":
            structural_evidence_result.get(
                "source_id"
            ),

        "content_hash":
            structural_evidence_result.get(
                "content_hash"
            ),

        "body_ref":
            structural_evidence_result.get(
                "body_ref"
            ),

        "article_id":
            structural_evidence_result.get(
                "article_id"
            ),

        "title":
            structural_evidence_result.get(
                "title"
            ),

        "section_count":
            len(attached_units),

        "section_evidence_units":
            attached_units,

        "canonical_section_order":
            canonical_order,

        "entity_concept_summary": {
            "source_semantic_object_count":
                len(semantic_objects),

            "section_object_reference_count":
                total_section_object_references,

            "section_mention_count":
                total_section_mentions,
        },

        "processing_boundaries": {
            "article_local_only":
                True,
            "canonical_runtime_structure_consumed":
                True,
            "raw_article_reparsed":
                False,
            "new_entity_extraction_performed":
                False,
            "structural_evidence_attached":
                True,
            "entity_concept_evidence_attached":
                True,
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
            "phrase_neighborhood_evidence_attachment",
    }


def attach_phrase_neighborhood_evidence_v1(
    entity_evidence_result: Mapping[str, Any],
    phrase_neighborhood_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Attach certified article-local Phrase Neighborhood Intelligence
    evidence to matching Section Evidence Units.

    4.6.5G performs evidence attachment only.
    It does not infer new relationships, rerun phrase analysis,
    perform topic-intent analysis, reasoning, scoring,
    contradiction analysis, linking, or persistence.
    """

    if not isinstance(
        entity_evidence_result,
        Mapping,
    ):
        raise SectionEvidenceIntelligenceError(
            "entity_evidence_result must be a mapping."
        )

    if (
        entity_evidence_result.get("schema_version")
        != "section_entity_concept_evidence_v1"
        or entity_evidence_result.get("status")
        != "ENTITY_CONCEPT_EVIDENCE_ATTACHED"
        or entity_evidence_result.get("phase")
        != "4.6.5"
    ):
        raise SectionEvidenceIntelligenceError(
            "Phrase-Neighborhood attachment requires certified "
            "4.6.5F Entity/Concept evidence."
        )

    if not isinstance(
        phrase_neighborhood_result,
        Mapping,
    ):
        raise SectionEvidenceIntelligenceError(
            "phrase_neighborhood_result must be a mapping."
        )

    if (
        phrase_neighborhood_result.get("schema_version")
        != "phrase_neighborhood_intelligence_result_v1"
        or phrase_neighborhood_result.get("status")
        != "PHRASE_NEIGHBORHOOD_INTELLIGENCE_COMPLETE"
    ):
        raise SectionEvidenceIntelligenceError(
            "Phrase Neighborhood Intelligence result is not complete."
        )

    identity_fields = (
        "workspace_id",
        "document_id",
        "source_type",
        "source_id",
        "content_hash",
        "body_ref",
        "article_id",
    )

    for field in identity_fields:
        if (
            entity_evidence_result.get(field)
            != phrase_neighborhood_result.get(field)
        ):
            raise SectionEvidenceIntelligenceError(
                f"Identity mismatch for {field}."
            )

    units = entity_evidence_result.get(
        "section_evidence_units"
    )

    neighborhoods = phrase_neighborhood_result.get(
        "neighborhoods"
    )

    if not isinstance(units, list):
        raise SectionEvidenceIntelligenceError(
            "Section Evidence Unit collection is invalid."
        )

    if not isinstance(neighborhoods, list):
        raise SectionEvidenceIntelligenceError(
            "Phrase Neighborhood collection is invalid."
        )

    canonical_section_order = list(
        entity_evidence_result.get(
            "canonical_section_order"
        )
        or []
    )

    canonical_section_ids = set(
        canonical_section_order
    )

    section_neighborhoods: dict[
        str,
        list[dict[str, Any]],
    ] = {
        section_id: []
        for section_id in canonical_section_order
    }

    total_section_references = 0

    for neighborhood in neighborhoods:
        if not isinstance(
            neighborhood,
            Mapping,
        ):
            raise SectionEvidenceIntelligenceError(
                "Invalid Phrase Neighborhood record."
            )

        neighborhood_id = str(
            neighborhood.get(
                "neighborhood_id"
            )
            or ""
        ).strip()

        if not neighborhood_id:
            raise SectionEvidenceIntelligenceError(
                "Phrase Neighborhood is missing neighborhood_id."
            )

        shared_section_ids = neighborhood.get(
            "shared_section_ids"
        )

        shared_block_ids = neighborhood.get(
            "shared_block_ids"
        )

        shared_paragraph_ids = neighborhood.get(
            "shared_paragraph_ids"
        )

        if not isinstance(
            shared_section_ids,
            list,
        ):
            raise SectionEvidenceIntelligenceError(
                "Phrase Neighborhood has invalid shared_section_ids."
            )

        if not isinstance(
            shared_block_ids,
            list,
        ):
            raise SectionEvidenceIntelligenceError(
                "Phrase Neighborhood has invalid shared_block_ids."
            )

        if not isinstance(
            shared_paragraph_ids,
            list,
        ):
            raise SectionEvidenceIntelligenceError(
                "Phrase Neighborhood has invalid shared_paragraph_ids."
            )

        for section_id in shared_section_ids:
            section_id = str(
                section_id or ""
            ).strip()

            if section_id not in canonical_section_ids:
                raise SectionEvidenceIntelligenceError(
                    "Phrase Neighborhood references a non-canonical "
                    f"section_id: {section_id}"
                )

            evidence = {
                "neighborhood_id":
                    neighborhood_id,

                "left_canonical_text":
                    neighborhood.get(
                        "left_canonical_text"
                    ),

                "right_canonical_text":
                    neighborhood.get(
                        "right_canonical_text"
                    ),

                "left_semantic_kind":
                    neighborhood.get(
                        "left_semantic_kind"
                    ),

                "right_semantic_kind":
                    neighborhood.get(
                        "right_semantic_kind"
                    ),

                "shared_section_ids":
                    list(shared_section_ids),

                "shared_block_ids":
                    list(shared_block_ids),

                "shared_paragraph_ids":
                    list(shared_paragraph_ids),

                "shared_section_count":
                    neighborhood.get(
                        "shared_section_count"
                    ),

                "shared_block_count":
                    neighborhood.get(
                        "shared_block_count"
                    ),

                "shared_paragraph_count":
                    neighborhood.get(
                        "shared_paragraph_count"
                    ),

                "minimum_char_distance":
                    neighborhood.get(
                        "minimum_char_distance"
                    ),

                "proximity_bonus":
                    neighborhood.get(
                        "proximity_bonus"
                    ),

                "neighborhood_strength":
                    neighborhood.get(
                        "neighborhood_strength"
                    ),

                "neighborhood_confidence":
                    neighborhood.get(
                        "neighborhood_confidence"
                    ),

                "evidence_dimensions":
                    neighborhood.get(
                        "evidence_dimensions"
                    ),

                "relationship_semantics_inferred":
                    neighborhood.get(
                        "relationship_semantics_inferred"
                    ),
            }

            section_neighborhoods[
                section_id
            ].append(evidence)

            total_section_references += 1

    attached_units: list[dict[str, Any]] = []

    for unit in units:
        if not isinstance(unit, Mapping):
            raise SectionEvidenceIntelligenceError(
                "Invalid Section Evidence Unit."
            )

        section_id = str(
            unit.get("section_id") or ""
        ).strip()

        if section_id not in canonical_section_ids:
            raise SectionEvidenceIntelligenceError(
                "Section Evidence Unit has non-canonical section_id."
            )

        state = dict(
            unit.get(
                "evidence_attachment_state"
            )
            or {}
        )

        if (
            state.get("structural_evidence")
            != "ATTACHED"
            or state.get("entity_concept_evidence")
            != "ATTACHED"
        ):
            raise SectionEvidenceIntelligenceError(
                "Phrase-Neighborhood evidence cannot be attached "
                "before structural and Entity/Concept evidence."
            )

        neighborhood_evidence = list(
            section_neighborhoods.get(
                section_id,
                [],
            )
        )

        mapped_unit = dict(unit)

        mapped_unit[
            "phrase_neighborhood_evidence"
        ] = {
            "evidence_source":
                "phrase_neighborhood_intelligence_v1",

            "article_local_only":
                True,

            "relationship_semantics_inferred":
                False,

            "section_id":
                section_id,

            "neighborhood_count":
                len(neighborhood_evidence),

            "neighborhoods":
                neighborhood_evidence,
        }

        state[
            "phrase_neighborhood_evidence"
        ] = "ATTACHED"

        mapped_unit[
            "evidence_attachment_state"
        ] = state

        attached_units.append(
            mapped_unit
        )

    attached_order = [
        unit.get("section_id")
        for unit in attached_units
    ]

    if attached_order != canonical_section_order:
        raise SectionEvidenceIntelligenceError(
            "Phrase-Neighborhood evidence attachment changed "
            "canonical section order."
        )

    return {
        "schema_version":
            "section_phrase_neighborhood_evidence_v1",

        "section_evidence_version":
            SECTION_EVIDENCE_INTELLIGENCE_VERSION,

        "phase":
            "4.6.5",

        "patch":
            "4.6.5G",

        "status":
            "PHRASE_NEIGHBORHOOD_EVIDENCE_ATTACHED",

        "workspace_id":
            entity_evidence_result.get(
                "workspace_id"
            ),

        "document_id":
            entity_evidence_result.get(
                "document_id"
            ),

        "source_type":
            entity_evidence_result.get(
                "source_type"
            ),

        "source_id":
            entity_evidence_result.get(
                "source_id"
            ),

        "content_hash":
            entity_evidence_result.get(
                "content_hash"
            ),

        "body_ref":
            entity_evidence_result.get(
                "body_ref"
            ),

        "article_id":
            entity_evidence_result.get(
                "article_id"
            ),

        "title":
            entity_evidence_result.get(
                "title"
            ),

        "section_count":
            len(attached_units),

        "section_evidence_units":
            attached_units,

        "canonical_section_order":
            canonical_section_order,

        "phrase_neighborhood_summary": {
            "source_neighborhood_count":
                len(neighborhoods),

            "section_neighborhood_reference_count":
                total_section_references,
        },

        "processing_boundaries": {
            "article_local_only":
                True,
            "canonical_runtime_structure_consumed":
                True,
            "raw_article_reparsed":
                False,
            "new_phrase_analysis_performed":
                False,
            "relationship_semantics_inferred":
                False,
            "structural_evidence_attached":
                True,
            "entity_concept_evidence_attached":
                True,
            "phrase_neighborhood_evidence_attached":
                True,
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
            "topic_intent_evidence_attachment",
    }


def attach_topic_intent_evidence_v1(
    phrase_evidence_result: Mapping[str, Any],
    topic_intent_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Attach certified article-local Topic Intent Intelligence evidence
    to matching Section Evidence Units.

    4.6.5H performs evidence attachment only.
    It does not select phrases, targets, URLs, link types,
    highlight colors, or perform linking/reasoning/persistence.
    """

    if not isinstance(
        phrase_evidence_result,
        Mapping,
    ):
        raise SectionEvidenceIntelligenceError(
            "phrase_evidence_result must be a mapping."
        )

    if (
        phrase_evidence_result.get("schema_version")
        != "section_phrase_neighborhood_evidence_v1"
        or phrase_evidence_result.get("status")
        != "PHRASE_NEIGHBORHOOD_EVIDENCE_ATTACHED"
        or phrase_evidence_result.get("phase")
        != "4.6.5"
    ):
        raise SectionEvidenceIntelligenceError(
            "Topic-Intent attachment requires certified "
            "4.6.5G Phrase-Neighborhood evidence."
        )

    if not isinstance(
        topic_intent_result,
        Mapping,
    ):
        raise SectionEvidenceIntelligenceError(
            "topic_intent_result must be a mapping."
        )

    if (
        topic_intent_result.get("schema_version")
        != "topic_intent_intelligence_result_v1"
        or topic_intent_result.get("status")
        != "TOPIC_INTENT_INTELLIGENCE_COMPLETE"
    ):
        raise SectionEvidenceIntelligenceError(
            "Topic Intent Intelligence result is not complete."
        )

    identity_fields = (
        "workspace_id",
        "document_id",
        "source_type",
        "source_id",
        "content_hash",
        "body_ref",
        "article_id",
    )

    for field in identity_fields:
        if (
            phrase_evidence_result.get(field)
            != topic_intent_result.get(field)
        ):
            raise SectionEvidenceIntelligenceError(
                f"Identity mismatch for {field}."
            )

    units = phrase_evidence_result.get(
        "section_evidence_units"
    )

    section_content_intents = topic_intent_result.get(
        "section_content_intents"
    )

    link_intents = topic_intent_result.get(
        "link_intents"
    )

    anchor_purposes = topic_intent_result.get(
        "anchor_purposes"
    )

    if not isinstance(units, list):
        raise SectionEvidenceIntelligenceError(
            "Section Evidence Unit collection is invalid."
        )

    if not isinstance(
        section_content_intents,
        list,
    ):
        raise SectionEvidenceIntelligenceError(
            "Section Content Intent collection is invalid."
        )

    if not isinstance(link_intents, list):
        raise SectionEvidenceIntelligenceError(
            "Link Intent collection is invalid."
        )

    if not isinstance(anchor_purposes, list):
        raise SectionEvidenceIntelligenceError(
            "Anchor Purpose collection is invalid."
        )

    canonical_order = list(
        phrase_evidence_result.get(
            "canonical_section_order"
        )
        or []
    )

    canonical_ids = set(
        canonical_order
    )

    content_by_section: dict[
        str,
        dict[str, Any],
    ] = {}

    for record in section_content_intents:
        if not isinstance(record, Mapping):
            raise SectionEvidenceIntelligenceError(
                "Invalid Section Content Intent record."
            )

        section_id = str(
            record.get("section_id") or ""
        ).strip()

        if section_id not in canonical_ids:
            raise SectionEvidenceIntelligenceError(
                "Section Content Intent references "
                "a non-canonical section."
            )

        if section_id in content_by_section:
            raise SectionEvidenceIntelligenceError(
                "Duplicate Section Content Intent detected."
            )

        content_by_section[
            section_id
        ] = dict(record)

    if set(content_by_section) != canonical_ids:
        raise SectionEvidenceIntelligenceError(
            "Section Content Intent coverage does not "
            "exactly match canonical sections."
        )

    links_by_section: dict[
        str,
        list[dict[str, Any]],
    ] = {
        section_id: []
        for section_id in canonical_order
    }

    for record in link_intents:
        if not isinstance(record, Mapping):
            raise SectionEvidenceIntelligenceError(
                "Invalid Link Intent record."
            )

        section_id = str(
            record.get("section_id") or ""
        ).strip()

        if section_id not in canonical_ids:
            raise SectionEvidenceIntelligenceError(
                "Link Intent references a non-canonical section."
            )

        links_by_section[
            section_id
        ].append(dict(record))

    anchors_by_section: dict[
        str,
        list[dict[str, Any]],
    ] = {
        section_id: []
        for section_id in canonical_order
    }

    for record in anchor_purposes:
        if not isinstance(record, Mapping):
            raise SectionEvidenceIntelligenceError(
                "Invalid Anchor Purpose record."
            )

        section_id = str(
            record.get("section_id") or ""
        ).strip()

        if section_id not in canonical_ids:
            raise SectionEvidenceIntelligenceError(
                "Anchor Purpose references a non-canonical section."
            )

        anchors_by_section[
            section_id
        ].append(dict(record))

    # Phase 4.6.4 must remain pre-linking intelligence.
    for record in link_intents:
        for field in (
            "target_selected",
            "url_selected",
            "link_type_selected",
            "highlight_color_selected",
        ):
            if record.get(field) is not False:
                raise SectionEvidenceIntelligenceError(
                    "Topic Intent output crossed the "
                    f"pre-linking boundary: {field}."
                )

    for record in anchor_purposes:
        for field in (
            "phrase_selected_for_linking",
            "target_selected",
            "url_selected",
            "link_type_selected",
            "highlight_color_selected",
        ):
            if record.get(field) is not False:
                raise SectionEvidenceIntelligenceError(
                    "Anchor Purpose output crossed the "
                    f"pre-linking boundary: {field}."
                )

    attached_units: list[dict[str, Any]] = []

    for unit in units:
        if not isinstance(unit, Mapping):
            raise SectionEvidenceIntelligenceError(
                "Invalid Section Evidence Unit."
            )

        section_id = str(
            unit.get("section_id") or ""
        ).strip()

        if section_id not in canonical_ids:
            raise SectionEvidenceIntelligenceError(
                "Section Evidence Unit has non-canonical section_id."
            )

        state = dict(
            unit.get(
                "evidence_attachment_state"
            )
            or {}
        )

        required_prior = (
            "structural_evidence",
            "entity_concept_evidence",
            "phrase_neighborhood_evidence",
        )

        if any(
            state.get(name) != "ATTACHED"
            for name in required_prior
        ):
            raise SectionEvidenceIntelligenceError(
                "Topic-Intent evidence cannot be attached "
                "before D-G evidence is complete."
            )

        content_intent = content_by_section[
            section_id
        ]

        section_links = list(
            links_by_section.get(
                section_id,
                [],
            )
        )

        section_anchors = list(
            anchors_by_section.get(
                section_id,
                [],
            )
        )

        mapped_unit = dict(unit)

        mapped_unit[
            "topic_intent_evidence"
        ] = {
            "evidence_source":
                "topic_intent_intelligence_v1",

            "article_local_only":
                True,

            "section_id":
                section_id,

            "content_intent":
                content_intent,

            "link_intent_count":
                len(section_links),

            "link_intents":
                section_links,

            "anchor_purpose_count":
                len(section_anchors),

            "anchor_purposes":
                section_anchors,

            "linking_decisions_performed":
                False,
        }

        state[
            "topic_intent_evidence"
        ] = "ATTACHED"

        mapped_unit[
            "evidence_attachment_state"
        ] = state

        attached_units.append(
            mapped_unit
        )

    attached_order = [
        unit.get("section_id")
        for unit in attached_units
    ]

    if attached_order != canonical_order:
        raise SectionEvidenceIntelligenceError(
            "Topic-Intent evidence attachment changed "
            "canonical section order."
        )

    attached_link_count = sum(
        (
            unit.get("topic_intent_evidence")
            or {}
        ).get("link_intent_count", 0)
        for unit in attached_units
    )

    attached_anchor_count = sum(
        (
            unit.get("topic_intent_evidence")
            or {}
        ).get("anchor_purpose_count", 0)
        for unit in attached_units
    )

    if attached_link_count != len(link_intents):
        raise SectionEvidenceIntelligenceError(
            "Link Intent attachment count mismatch."
        )

    if attached_anchor_count != len(anchor_purposes):
        raise SectionEvidenceIntelligenceError(
            "Anchor Purpose attachment count mismatch."
        )

    return {
        "schema_version":
            "section_topic_intent_evidence_v1",

        "section_evidence_version":
            SECTION_EVIDENCE_INTELLIGENCE_VERSION,

        "phase":
            "4.6.5",

        "patch":
            "4.6.5H",

        "status":
            "TOPIC_INTENT_EVIDENCE_ATTACHED",

        "workspace_id":
            phrase_evidence_result.get(
                "workspace_id"
            ),

        "document_id":
            phrase_evidence_result.get(
                "document_id"
            ),

        "source_type":
            phrase_evidence_result.get(
                "source_type"
            ),

        "source_id":
            phrase_evidence_result.get(
                "source_id"
            ),

        "content_hash":
            phrase_evidence_result.get(
                "content_hash"
            ),

        "body_ref":
            phrase_evidence_result.get(
                "body_ref"
            ),

        "article_id":
            phrase_evidence_result.get(
                "article_id"
            ),

        "title":
            phrase_evidence_result.get(
                "title"
            ),

        "section_count":
            len(attached_units),

        "section_evidence_units":
            attached_units,

        "canonical_section_order":
            canonical_order,

        "topic_intent_summary": {
            "section_content_intent_count":
                len(section_content_intents),

            "link_intent_count":
                len(link_intents),

            "anchor_purpose_count":
                len(anchor_purposes),

            "linking_decisions_performed":
                False,
        },

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
                True,
            "phrase_neighborhood_evidence_attached":
                True,
            "topic_intent_evidence_attached":
                True,
            "phrase_selected_for_linking":
                False,
            "target_selected":
                False,
            "url_selected":
                False,
            "link_type_selected":
                False,
            "highlight_color_selected":
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
            "statement_claim_evidence_extraction",
    }


def extract_statement_claim_evidence_v1(
    topic_evidence_result: Mapping[str, Any],
    runtime_reader_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Extract canonical section-local statement evidence and conservative
    claim candidates from Runtime Reader sentence records.

    4.6.5I does not score evidence, verify truth, infer contradiction,
    reason across claims, select links, or persist intelligence.
    """

    if not isinstance(
        topic_evidence_result,
        Mapping,
    ):
        raise SectionEvidenceIntelligenceError(
            "topic_evidence_result must be a mapping."
        )

    if (
        topic_evidence_result.get("schema_version")
        != "section_topic_intent_evidence_v1"
        or topic_evidence_result.get("status")
        != "TOPIC_INTENT_EVIDENCE_ATTACHED"
        or topic_evidence_result.get("phase")
        != "4.6.5"
    ):
        raise SectionEvidenceIntelligenceError(
            "Statement/Claim extraction requires certified "
            "4.6.5H Topic-Intent evidence."
        )

    if not isinstance(
        runtime_reader_result,
        Mapping,
    ):
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
            topic_evidence_result.get(field)
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

    if (
        runtime_model.get("structure_source")
        != "canonical_uucd"
    ):
        raise SectionEvidenceIntelligenceError(
            "Statement/Claim extraction requires "
            "canonical UUCD structural evidence."
        )

    validation = runtime_model.get(
        "validation"
    )

    if (
        not isinstance(validation, Mapping)
        or validation.get("valid") is not True
    ):
        raise SectionEvidenceIntelligenceError(
            "Runtime Reader canonical structure is not valid."
        )

    runtime_article = runtime_model.get(
        "article"
    )

    if not isinstance(runtime_article, Mapping):
        raise SectionEvidenceIntelligenceError(
            "Runtime article identity is missing."
        )

    if (
        topic_evidence_result.get("article_id")
        != runtime_article.get("article_id")
    ):
        raise SectionEvidenceIntelligenceError(
            "Identity mismatch for article_id."
        )

    units = topic_evidence_result.get(
        "section_evidence_units"
    )

    blocks = runtime_model.get(
        "blocks"
    )

    if not isinstance(units, list):
        raise SectionEvidenceIntelligenceError(
            "Section Evidence Unit collection is invalid."
        )

    if not isinstance(blocks, list):
        raise SectionEvidenceIntelligenceError(
            "Runtime block collection is invalid."
        )

    canonical_order = list(
        topic_evidence_result.get(
            "canonical_section_order"
        )
        or []
    )

    canonical_ids = set(
        canonical_order
    )

    statements_by_section: dict[
        str,
        list[dict[str, Any]],
    ] = {
        section_id: []
        for section_id in canonical_order
    }

    seen_sentence_ids: set[str] = set()

    total_statement_count = 0
    total_claim_candidate_count = 0
    total_nonclaim_statement_count = 0

    for block in blocks:
        if not isinstance(block, Mapping):
            raise SectionEvidenceIntelligenceError(
                "Invalid Runtime Reader block."
            )

        block_id = str(
            block.get("block_id") or ""
        ).strip()

        section_id = str(
            block.get("section_id") or ""
        ).strip()

        if not block_id:
            raise SectionEvidenceIntelligenceError(
                "Runtime block is missing block_id."
            )

        if section_id not in canonical_ids:
            raise SectionEvidenceIntelligenceError(
                "Runtime block references a non-canonical section."
            )

        sentences = block.get(
            "sentences"
        )

        if sentences is None:
            sentences = []

        if not isinstance(sentences, list):
            raise SectionEvidenceIntelligenceError(
                "Runtime block has invalid sentence collection."
            )

        for sentence in sentences:
            if not isinstance(sentence, Mapping):
                raise SectionEvidenceIntelligenceError(
                    "Invalid canonical sentence record."
                )

            sentence_id = str(
                sentence.get("sentence_id") or ""
            ).strip()

            if not sentence_id:
                raise SectionEvidenceIntelligenceError(
                    "Canonical sentence is missing sentence_id."
                )

            if sentence_id in seen_sentence_ids:
                raise SectionEvidenceIntelligenceError(
                    "Duplicate canonical sentence_id detected."
                )

            seen_sentence_ids.add(
                sentence_id
            )

            sentence_section_id = str(
                sentence.get("section_id") or ""
            ).strip()

            if sentence_section_id != section_id:
                raise SectionEvidenceIntelligenceError(
                    "Sentence section_id does not match "
                    "its canonical block section_id."
                )

            sentence_paragraph_id = (
                sentence.get("paragraph_id")
            )

            block_paragraph_id = (
                block.get("paragraph_id")
            )

            if (
                sentence_paragraph_id
                != block_paragraph_id
            ):
                raise SectionEvidenceIntelligenceError(
                    "Sentence paragraph_id does not match "
                    "its canonical block paragraph_id."
                )

            text = str(
                sentence.get("text") or ""
            ).strip()

            if not text:
                raise SectionEvidenceIntelligenceError(
                    "Canonical sentence text is empty."
                )

            # Remove closing quote/bracket characters only for
            # punctuation-form inspection. Exact source text is preserved.
            punctuation_probe = text.rstrip(
                "\"'??)]}"
            ).rstrip()

            is_question = punctuation_probe.endswith("?")
            is_exclamation = punctuation_probe.endswith("!")
            is_period_terminated = punctuation_probe.endswith(".")

            complete_sentence = (
                is_question
                or is_exclamation
                or is_period_terminated
            )

            # Conservative claim-candidate rule:
            # - must be a complete canonical sentence
            # - questions are not claims
            #
            # No truth/support/strength judgment occurs here.
            claim_candidate = (
                complete_sentence
                and not is_question
            )

            if is_question:
                statement_form = "QUESTION"
            elif complete_sentence:
                statement_form = "COMPLETE_STATEMENT"
            else:
                statement_form = "FRAGMENT_OR_CAPTION_LIKE"

            metadata = sentence.get(
                "metadata"
            )

            if not isinstance(metadata, Mapping):
                metadata = {}

            statement_record = {
                "statement_evidence_id":
                    _stable_id(
                        "statement_evidence",
                        topic_evidence_result.get(
                            "article_id"
                        ),
                        sentence_id,
                    ),

                "sentence_id":
                    sentence_id,

                "article_id":
                    sentence.get("article_id"),

                "section_id":
                    section_id,

                "block_id":
                    block_id,

                "paragraph_id":
                    sentence_paragraph_id,

                "block_type":
                    block.get("block_type"),

                "block_index":
                    block.get("block_index"),

                "sentence_index":
                    sentence.get("sentence_index"),

                "sentence_global_index":
                    sentence.get(
                        "sentence_global_index"
                    ),

                "article_position":
                    sentence.get("article_position"),

                "text":
                    text,

                "word_count":
                    metadata.get("word_count"),

                "character_count":
                    metadata.get(
                        "character_count"
                    ),

                "statement_form":
                    statement_form,

                "complete_sentence":
                    complete_sentence,

                "claim_candidate":
                    claim_candidate,

                "claim_truth_assessed":
                    False,

                "claim_support_assessed":
                    False,

                "claim_strength_assessed":
                    False,

                "contradiction_assessed":
                    False,
            }

            statements_by_section[
                section_id
            ].append(statement_record)

            total_statement_count += 1

            if claim_candidate:
                total_claim_candidate_count += 1
            else:
                total_nonclaim_statement_count += 1

    attached_units: list[dict[str, Any]] = []

    for unit in units:
        if not isinstance(unit, Mapping):
            raise SectionEvidenceIntelligenceError(
                "Invalid Section Evidence Unit."
            )

        section_id = str(
            unit.get("section_id") or ""
        ).strip()

        if section_id not in canonical_ids:
            raise SectionEvidenceIntelligenceError(
                "Section Evidence Unit has non-canonical section_id."
            )

        state = dict(
            unit.get(
                "evidence_attachment_state"
            )
            or {}
        )

        required_prior = (
            "structural_evidence",
            "entity_concept_evidence",
            "phrase_neighborhood_evidence",
            "topic_intent_evidence",
        )

        if any(
            state.get(name) != "ATTACHED"
            for name in required_prior
        ):
            raise SectionEvidenceIntelligenceError(
                "Statement/Claim evidence cannot be extracted "
                "before D-H evidence is complete."
            )

        section_statements = list(
            statements_by_section.get(
                section_id,
                [],
            )
        )

        section_claims = [
            statement
            for statement in section_statements
            if statement.get(
                "claim_candidate"
            ) is True
        ]

        section_nonclaims = [
            statement
            for statement in section_statements
            if statement.get(
                "claim_candidate"
            ) is not True
        ]

        mapped_unit = dict(unit)

        mapped_unit[
            "claim_evidence"
        ] = {
            "evidence_source":
                "semantic_intelligence_runtime_reader_v1",

            "article_local_only":
                True,

            "canonical_sentence_evidence_only":
                True,

            "section_id":
                section_id,

            "statement_count":
                len(section_statements),

            "claim_candidate_count":
                len(section_claims),

            "nonclaim_statement_count":
                len(section_nonclaims),

            "statements":
                section_statements,

            "claim_candidates":
                section_claims,

            "truth_assessment_performed":
                False,

            "support_assessment_performed":
                False,

            "strength_scoring_performed":
                False,

            "contradiction_analysis_performed":
                False,
        }

        state[
            "claim_evidence"
        ] = "ATTACHED"

        mapped_unit[
            "evidence_attachment_state"
        ] = state

        attached_units.append(
            mapped_unit
        )

    attached_order = [
        unit.get("section_id")
        for unit in attached_units
    ]

    if attached_order != canonical_order:
        raise SectionEvidenceIntelligenceError(
            "Statement/Claim extraction changed "
            "canonical section order."
        )

    attached_statement_count = sum(
        (
            unit.get("claim_evidence")
            or {}
        ).get("statement_count", 0)
        for unit in attached_units
    )

    attached_claim_count = sum(
        (
            unit.get("claim_evidence")
            or {}
        ).get("claim_candidate_count", 0)
        for unit in attached_units
    )

    if (
        attached_statement_count
        != total_statement_count
    ):
        raise SectionEvidenceIntelligenceError(
            "Statement attachment count mismatch."
        )

    if (
        attached_claim_count
        != total_claim_candidate_count
    ):
        raise SectionEvidenceIntelligenceError(
            "Claim candidate attachment count mismatch."
        )

    return {
        "schema_version":
            "section_statement_claim_evidence_v1",

        "section_evidence_version":
            SECTION_EVIDENCE_INTELLIGENCE_VERSION,

        "phase":
            "4.6.5",

        "patch":
            "4.6.5I",

        "status":
            "STATEMENT_CLAIM_EVIDENCE_EXTRACTED",

        "workspace_id":
            topic_evidence_result.get(
                "workspace_id"
            ),

        "document_id":
            topic_evidence_result.get(
                "document_id"
            ),

        "source_type":
            topic_evidence_result.get(
                "source_type"
            ),

        "source_id":
            topic_evidence_result.get(
                "source_id"
            ),

        "content_hash":
            topic_evidence_result.get(
                "content_hash"
            ),

        "body_ref":
            topic_evidence_result.get(
                "body_ref"
            ),

        "article_id":
            topic_evidence_result.get(
                "article_id"
            ),

        "title":
            topic_evidence_result.get(
                "title"
            ),

        "section_count":
            len(attached_units),

        "section_evidence_units":
            attached_units,

        "canonical_section_order":
            canonical_order,

        "statement_claim_summary": {
            "statement_count":
                total_statement_count,

            "claim_candidate_count":
                total_claim_candidate_count,

            "nonclaim_statement_count":
                total_nonclaim_statement_count,

            "truth_assessment_performed":
                False,

            "support_assessment_performed":
                False,

            "strength_scoring_performed":
                False,

            "contradiction_analysis_performed":
                False,
        },

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
                True,
            "phrase_neighborhood_evidence_attached":
                True,
            "topic_intent_evidence_attached":
                True,
            "claim_extraction_performed":
                True,
            "truth_assessment_performed":
                False,
            "support_assessment_performed":
                False,
            "evidence_scoring_performed":
                False,
            "contradiction_analysis_performed":
                False,
            "reasoning_performed":
                False,
            "phrase_selected_for_linking":
                False,
            "target_selected":
                False,
            "url_selected":
                False,
            "link_type_selected":
                False,
            "highlight_color_selected":
                False,
            "semantic_memory_write_performed":
                False,
            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "evidence_strength_scoring",
    }


def score_evidence_strength_v1(
    claim_evidence_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Score article-local evidence richness for each claim candidate.

    This is NOT factual-truth verification.

    Evidence dimensions:
    - canonical structural grounding
    - section Topic-Intent grounding
    - claim-local Entity/Concept grounding
    - claim-local Phrase-Neighborhood grounding

    4.6.5J does not assess truth, external authority,
    contradiction, coverage, reasoning, linking, or persistence.
    """

    if not isinstance(
        claim_evidence_result,
        Mapping,
    ):
        raise SectionEvidenceIntelligenceError(
            "claim_evidence_result must be a mapping."
        )

    if (
        claim_evidence_result.get("schema_version")
        != "section_statement_claim_evidence_v1"
        or claim_evidence_result.get("status")
        != "STATEMENT_CLAIM_EVIDENCE_EXTRACTED"
        or claim_evidence_result.get("phase")
        != "4.6.5"
    ):
        raise SectionEvidenceIntelligenceError(
            "Evidence-strength scoring requires certified "
            "4.6.5I Statement/Claim evidence."
        )

    units = claim_evidence_result.get(
        "section_evidence_units"
    )

    if not isinstance(units, list):
        raise SectionEvidenceIntelligenceError(
            "Section Evidence Unit collection is invalid."
        )

    canonical_order = list(
        claim_evidence_result.get(
            "canonical_section_order"
        )
        or []
    )

    scored_units: list[dict[str, Any]] = []

    total_claims = 0

    band_counts = {
        "STRONG": 0,
        "MODERATE": 0,
        "LIMITED": 0,
    }

    total_score = 0.0

    for unit in units:
        if not isinstance(unit, Mapping):
            raise SectionEvidenceIntelligenceError(
                "Invalid Section Evidence Unit."
            )

        state = dict(
            unit.get(
                "evidence_attachment_state"
            )
            or {}
        )

        required_prior = (
            "structural_evidence",
            "entity_concept_evidence",
            "phrase_neighborhood_evidence",
            "topic_intent_evidence",
            "claim_evidence",
        )

        if any(
            state.get(name) != "ATTACHED"
            for name in required_prior
        ):
            raise SectionEvidenceIntelligenceError(
                "Evidence-strength scoring cannot run "
                "before D-I evidence is complete."
            )

        section_id = str(
            unit.get("section_id") or ""
        ).strip()

        structural = unit.get(
            "structural_evidence"
        ) or {}

        entity_evidence = unit.get(
            "entity_concept_evidence"
        ) or {}

        phrase_evidence = unit.get(
            "phrase_neighborhood_evidence"
        ) or {}

        topic_evidence = unit.get(
            "topic_intent_evidence"
        ) or {}

        claim_evidence = unit.get(
            "claim_evidence"
        ) or {}

        structural_block_ids = set(
            structural.get("block_ids")
            or []
        )

        structural_paragraph_ids = set(
            structural.get("paragraph_ids")
            or []
        )

        semantic_objects = (
            entity_evidence.get(
                "semantic_objects"
            )
            or []
        )

        neighborhoods = (
            phrase_evidence.get(
                "neighborhoods"
            )
            or []
        )

        content_intent = (
            topic_evidence.get(
                "content_intent"
            )
            or {}
        )

        topic_block_ids = set(
            content_intent.get(
                "source_block_ids"
            )
            or []
        )

        topic_paragraph_ids = set(
            content_intent.get(
                "source_paragraph_ids"
            )
            or []
        )

        claim_scores: list[
            dict[str, Any]
        ] = []

        for claim in (
            claim_evidence.get(
                "claim_candidates"
            )
            or []
        ):
            if not isinstance(claim, Mapping):
                raise SectionEvidenceIntelligenceError(
                    "Invalid claim candidate."
                )

            block_id = claim.get(
                "block_id"
            )

            paragraph_id = claim.get(
                "paragraph_id"
            )

            structural_grounded = (
                block_id in structural_block_ids
                and (
                    paragraph_id is None
                    or paragraph_id
                    in structural_paragraph_ids
                )
            )

            topic_grounded = (
                block_id in topic_block_ids
                or paragraph_id
                in topic_paragraph_ids
            )

            entity_matches = []

            for obj in semantic_objects:
                if not isinstance(
                    obj,
                    Mapping,
                ):
                    continue

                object_block_ids = set(
                    obj.get(
                        "section_block_ids"
                    )
                    or []
                )

                object_paragraph_ids = set(
                    obj.get(
                        "section_paragraph_ids"
                    )
                    or []
                )

                if (
                    block_id in object_block_ids
                    or paragraph_id
                    in object_paragraph_ids
                ):
                    entity_matches.append({
                        "canonical_text":
                            obj.get(
                                "canonical_text"
                            ),
                        "semantic_kind":
                            obj.get(
                                "semantic_kind"
                            ),
                    })

            neighborhood_matches = []

            for neighborhood in neighborhoods:
                if not isinstance(
                    neighborhood,
                    Mapping,
                ):
                    continue

                shared_blocks = set(
                    neighborhood.get(
                        "shared_block_ids"
                    )
                    or []
                )

                shared_paragraphs = set(
                    neighborhood.get(
                        "shared_paragraph_ids"
                    )
                    or []
                )

                if (
                    block_id in shared_blocks
                    or paragraph_id
                    in shared_paragraphs
                ):
                    neighborhood_matches.append({
                        "neighborhood_id":
                            neighborhood.get(
                                "neighborhood_id"
                            ),
                        "left_canonical_text":
                            neighborhood.get(
                                "left_canonical_text"
                            ),
                        "right_canonical_text":
                            neighborhood.get(
                                "right_canonical_text"
                            ),
                        "neighborhood_strength":
                            neighborhood.get(
                                "neighborhood_strength"
                            ),
                        "neighborhood_confidence":
                            neighborhood.get(
                                "neighborhood_confidence"
                            ),
                    })

            entity_match_count = len(
                entity_matches
            )

            neighborhood_match_count = len(
                neighborhood_matches
            )

            structural_component = (
                1.0
                if structural_grounded
                else 0.0
            )

            topic_component = (
                1.0
                if topic_grounded
                else 0.0
            )

            # Saturating evidence-density components prevent
            # very dense sections from overwhelming the score.
            entity_component = min(
                entity_match_count / 5.0,
                1.0,
            )

            neighborhood_component = min(
                neighborhood_match_count / 10.0,
                1.0,
            )

            score = round(
                (
                    0.25 * structural_component
                    + 0.25 * topic_component
                    + 0.25 * entity_component
                    + 0.25 * neighborhood_component
                ),
                3,
            )

            if score >= 0.80:
                strength_band = "STRONG"
            elif score >= 0.60:
                strength_band = "MODERATE"
            else:
                strength_band = "LIMITED"

            band_counts[
                strength_band
            ] += 1

            total_claims += 1
            total_score += score

            claim_scores.append({
                "evidence_strength_id":
                    _stable_id(
                        "evidence_strength",
                        claim_evidence_result.get(
                            "article_id"
                        ),
                        claim.get(
                            "sentence_id"
                        ),
                    ),

                "statement_evidence_id":
                    claim.get(
                        "statement_evidence_id"
                    ),

                "sentence_id":
                    claim.get(
                        "sentence_id"
                    ),

                "section_id":
                    section_id,

                "block_id":
                    block_id,

                "paragraph_id":
                    paragraph_id,

                "text":
                    claim.get("text"),

                "evidence_strength_score":
                    score,

                "evidence_strength_band":
                    strength_band,

                "score_scope":
                    "ARTICLE_LOCAL_EVIDENCE_RICHNESS_NOT_TRUTH",

                "dimension_scores": {
                    "structural_grounding":
                        structural_component,

                    "topic_intent_grounding":
                        topic_component,

                    "entity_concept_grounding":
                        round(
                            entity_component,
                            3,
                        ),

                    "phrase_neighborhood_grounding":
                        round(
                            neighborhood_component,
                            3,
                        ),
                },

                "raw_support_counts": {
                    "entity_concept_matches":
                        entity_match_count,

                    "phrase_neighborhood_matches":
                        neighborhood_match_count,
                },

                "entity_concept_matches":
                    entity_matches,

                "phrase_neighborhood_matches":
                    neighborhood_matches,

                "truth_assessed":
                    False,

                "external_authority_checked":
                    False,

                "contradiction_assessed":
                    False,
            })

        mapped_unit = dict(unit)

        mapped_unit[
            "evidence_strength"
        ] = {
            "score_scope":
                "ARTICLE_LOCAL_EVIDENCE_RICHNESS_NOT_TRUTH",

            "section_id":
                section_id,

            "claim_score_count":
                len(claim_scores),

            "claim_scores":
                claim_scores,

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
                False,

            "contradiction_analysis_performed":
                False,
        }

        state[
            "evidence_strength"
        ] = "ATTACHED"

        mapped_unit[
            "evidence_attachment_state"
        ] = state

        scored_units.append(
            mapped_unit
        )

    scored_order = [
        unit.get("section_id")
        for unit in scored_units
    ]

    if scored_order != canonical_order:
        raise SectionEvidenceIntelligenceError(
            "Evidence-strength scoring changed "
            "canonical section order."
        )

    source_claim_count = (
        claim_evidence_result.get(
            "statement_claim_summary",
            {}
        ).get(
            "claim_candidate_count"
        )
    )

    if total_claims != source_claim_count:
        raise SectionEvidenceIntelligenceError(
            "Evidence-strength claim count mismatch."
        )

    average_score = (
        round(
            total_score / total_claims,
            3,
        )
        if total_claims
        else 0.0
    )

    return {
        "schema_version":
            "section_evidence_strength_v1",

        "section_evidence_version":
            SECTION_EVIDENCE_INTELLIGENCE_VERSION,

        "phase":
            "4.6.5",

        "patch":
            "4.6.5J",

        "status":
            "EVIDENCE_STRENGTH_SCORED",

        "workspace_id":
            claim_evidence_result.get(
                "workspace_id"
            ),

        "document_id":
            claim_evidence_result.get(
                "document_id"
            ),

        "source_type":
            claim_evidence_result.get(
                "source_type"
            ),

        "source_id":
            claim_evidence_result.get(
                "source_id"
            ),

        "content_hash":
            claim_evidence_result.get(
                "content_hash"
            ),

        "body_ref":
            claim_evidence_result.get(
                "body_ref"
            ),

        "article_id":
            claim_evidence_result.get(
                "article_id"
            ),

        "title":
            claim_evidence_result.get(
                "title"
            ),

        "section_count":
            len(scored_units),

        "section_evidence_units":
            scored_units,

        "canonical_section_order":
            canonical_order,

        "evidence_strength_summary": {
            "claim_score_count":
                total_claims,

            "average_evidence_strength_score":
                average_score,

            "strength_band_counts":
                band_counts,

            "score_scope":
                "ARTICLE_LOCAL_EVIDENCE_RICHNESS_NOT_TRUTH",

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
                False,

            "contradiction_analysis_performed":
                False,
        },

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
                True,
            "phrase_neighborhood_evidence_attached":
                True,
            "topic_intent_evidence_attached":
                True,
            "claim_extraction_performed":
                True,
            "evidence_scoring_performed":
                True,
            "truth_assessment_performed":
                False,
            "external_authority_check_performed":
                False,
            "coverage_analysis_performed":
                False,
            "contradiction_analysis_performed":
                False,
            "reasoning_performed":
                False,
            "phrase_selected_for_linking":
                False,
            "target_selected":
                False,
            "url_selected":
                False,
            "link_type_selected":
                False,
            "highlight_color_selected":
                False,
            "semantic_memory_write_performed":
                False,
            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "evidence_coverage",
    }


def measure_evidence_coverage_v1(
    strength_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Measure completeness of Section Evidence coverage.

    Coverage is distinct from evidence strength:
    - 4.6.5J measures richness/strength.
    - 4.6.5K measures whether required evidence layers
      and claim scores are present.

    No contradiction, insufficiency, truth, reasoning,
    linking, or persistence decisions occur here.
    """

    if not isinstance(
        strength_result,
        Mapping,
    ):
        raise SectionEvidenceIntelligenceError(
            "strength_result must be a mapping."
        )

    if (
        strength_result.get("schema_version")
        != "section_evidence_strength_v1"
        or strength_result.get("status")
        != "EVIDENCE_STRENGTH_SCORED"
        or strength_result.get("phase")
        != "4.6.5"
    ):
        raise SectionEvidenceIntelligenceError(
            "Evidence coverage requires certified "
            "4.6.5J Evidence-Strength output."
        )

    units = strength_result.get(
        "section_evidence_units"
    )

    if not isinstance(units, list):
        raise SectionEvidenceIntelligenceError(
            "Section Evidence Unit collection is invalid."
        )

    canonical_order = list(
        strength_result.get(
            "canonical_section_order"
        )
        or []
    )

    required_layers = (
        "structural_evidence",
        "entity_concept_evidence",
        "phrase_neighborhood_evidence",
        "topic_intent_evidence",
        "claim_evidence",
        "evidence_strength",
    )

    covered_units: list[dict[str, Any]] = []

    fully_covered_sections = 0
    partially_covered_sections = 0
    uncovered_sections = 0

    total_claim_candidates = 0
    total_claim_scores = 0

    section_coverage_scores = []

    for unit in units:
        if not isinstance(unit, Mapping):
            raise SectionEvidenceIntelligenceError(
                "Invalid Section Evidence Unit."
            )

        section_id = str(
            unit.get("section_id") or ""
        ).strip()

        state = dict(
            unit.get(
                "evidence_attachment_state"
            )
            or {}
        )

        layer_presence = {
            layer:
                (
                    state.get(layer)
                    == "ATTACHED"
                    and isinstance(
                        unit.get(layer),
                        Mapping,
                    )
                )
            for layer in required_layers
        }

        covered_layer_count = sum(
            1
            for present in layer_presence.values()
            if present
        )

        required_layer_count = len(
            required_layers
        )

        layer_coverage_ratio = round(
            covered_layer_count
            / required_layer_count,
            3,
        )

        claim_evidence = (
            unit.get("claim_evidence")
            or {}
        )

        strength = (
            unit.get("evidence_strength")
            or {}
        )

        claim_candidate_count = int(
            claim_evidence.get(
                "claim_candidate_count"
            )
            or 0
        )

        claim_score_count = int(
            strength.get(
                "claim_score_count"
            )
            or 0
        )

        if claim_score_count > claim_candidate_count:
            raise SectionEvidenceIntelligenceError(
                "Claim score count exceeds "
                "claim candidate count."
            )

        if claim_candidate_count > 0:
            claim_score_coverage_ratio = round(
                claim_score_count
                / claim_candidate_count,
                3,
            )
        else:
            claim_score_coverage_ratio = 1.0

        total_claim_candidates += (
            claim_candidate_count
        )

        total_claim_scores += (
            claim_score_count
        )

        coverage_score = round(
            (
                0.75 * layer_coverage_ratio
                + 0.25 * claim_score_coverage_ratio
            ),
            3,
        )

        section_coverage_scores.append(
            coverage_score
        )

        if (
            layer_coverage_ratio == 1.0
            and claim_score_coverage_ratio == 1.0
        ):
            coverage_status = "COMPLETE"
            fully_covered_sections += 1

        elif (
            covered_layer_count == 0
            and claim_score_count == 0
        ):
            coverage_status = "UNCOVERED"
            uncovered_sections += 1

        else:
            coverage_status = "PARTIAL"
            partially_covered_sections += 1

        mapped_unit = dict(unit)

        mapped_unit[
            "coverage"
        ] = {
            "section_id":
                section_id,

            "coverage_scope":
                "EVIDENCE_COMPLETENESS_NOT_STRENGTH",

            "required_layer_count":
                required_layer_count,

            "covered_layer_count":
                covered_layer_count,

            "layer_presence":
                layer_presence,

            "layer_coverage_ratio":
                layer_coverage_ratio,

            "claim_candidate_count":
                claim_candidate_count,

            "claim_score_count":
                claim_score_count,

            "claim_score_coverage_ratio":
                claim_score_coverage_ratio,

            "coverage_score":
                coverage_score,

            "coverage_status":
                coverage_status,

            "evidence_strength_reclassified":
                False,

            "truth_assessment_performed":
                False,

            "insufficiency_flagging_performed":
                False,

            "contradiction_analysis_performed":
                False,
        }

        state[
            "coverage"
        ] = "ATTACHED"

        mapped_unit[
            "evidence_attachment_state"
        ] = state

        covered_units.append(
            mapped_unit
        )

    covered_order = [
        unit.get("section_id")
        for unit in covered_units
    ]

    if covered_order != canonical_order:
        raise SectionEvidenceIntelligenceError(
            "Evidence coverage changed "
            "canonical section order."
        )

    source_claim_count = (
        strength_result.get(
            "evidence_strength_summary",
            {}
        ).get(
            "claim_score_count"
        )
    )

    if total_claim_scores != source_claim_count:
        raise SectionEvidenceIntelligenceError(
            "Evidence coverage claim-score count mismatch."
        )

    overall_claim_score_coverage = (
        round(
            total_claim_scores
            / total_claim_candidates,
            3,
        )
        if total_claim_candidates
        else 1.0
    )

    average_section_coverage = (
        round(
            sum(section_coverage_scores)
            / len(section_coverage_scores),
            3,
        )
        if section_coverage_scores
        else 0.0
    )

    return {
        "schema_version":
            "section_evidence_coverage_v1",

        "section_evidence_version":
            SECTION_EVIDENCE_INTELLIGENCE_VERSION,

        "phase":
            "4.6.5",

        "patch":
            "4.6.5K",

        "status":
            "EVIDENCE_COVERAGE_MEASURED",

        "workspace_id":
            strength_result.get(
                "workspace_id"
            ),

        "document_id":
            strength_result.get(
                "document_id"
            ),

        "source_type":
            strength_result.get(
                "source_type"
            ),

        "source_id":
            strength_result.get(
                "source_id"
            ),

        "content_hash":
            strength_result.get(
                "content_hash"
            ),

        "body_ref":
            strength_result.get(
                "body_ref"
            ),

        "article_id":
            strength_result.get(
                "article_id"
            ),

        "title":
            strength_result.get(
                "title"
            ),

        "section_count":
            len(covered_units),

        "section_evidence_units":
            covered_units,

        "canonical_section_order":
            canonical_order,

        "coverage_summary": {
            "section_count":
                len(covered_units),

            "fully_covered_sections":
                fully_covered_sections,

            "partially_covered_sections":
                partially_covered_sections,

            "uncovered_sections":
                uncovered_sections,

            "average_section_coverage":
                average_section_coverage,

            "claim_candidate_count":
                total_claim_candidates,

            "claim_score_count":
                total_claim_scores,

            "overall_claim_score_coverage":
                overall_claim_score_coverage,

            "coverage_scope":
                "EVIDENCE_COMPLETENESS_NOT_STRENGTH",

            "insufficiency_flagging_performed":
                False,

            "contradiction_analysis_performed":
                False,
        },

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
                True,
            "phrase_neighborhood_evidence_attached":
                True,
            "topic_intent_evidence_attached":
                True,
            "claim_extraction_performed":
                True,
            "evidence_scoring_performed":
                True,
            "coverage_analysis_performed":
                True,
            "truth_assessment_performed":
                False,
            "external_authority_check_performed":
                False,
            "insufficiency_flagging_performed":
                False,
            "contradiction_analysis_performed":
                False,
            "reasoning_performed":
                False,
            "phrase_selected_for_linking":
                False,
            "target_selected":
                False,
            "url_selected":
                False,
            "link_type_selected":
                False,
            "highlight_color_selected":
                False,
            "semantic_memory_write_performed":
                False,
            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "contradiction_insufficient_evidence_flags",
    }


def flag_contradiction_insufficient_evidence_v1(
    coverage_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Apply conservative article-local insufficiency and contradiction flags.

    Insufficiency:
    - LIMITED evidence-strength claim
    - incomplete section/claim coverage

    Contradiction:
    - same canonical section
    - opposite negation polarity
    - strong lexical overlap after removing negation terms

    This is conservative candidate detection only.
    It does not perform logical reasoning, factual verification,
    external-source validation, or Claim Integrity adjudication.
    """

    import re

    if not isinstance(
        coverage_result,
        Mapping,
    ):
        raise SectionEvidenceIntelligenceError(
            "coverage_result must be a mapping."
        )

    if (
        coverage_result.get("schema_version")
        != "section_evidence_coverage_v1"
        or coverage_result.get("status")
        != "EVIDENCE_COVERAGE_MEASURED"
        or coverage_result.get("phase")
        != "4.6.5"
    ):
        raise SectionEvidenceIntelligenceError(
            "Contradiction/insufficiency flagging requires "
            "certified 4.6.5K Evidence Coverage output."
        )

    units = coverage_result.get(
        "section_evidence_units"
    )

    if not isinstance(units, list):
        raise SectionEvidenceIntelligenceError(
            "Section Evidence Unit collection is invalid."
        )

    canonical_order = list(
        coverage_result.get(
            "canonical_section_order"
        )
        or []
    )

    negation_terms = {
        "not",
        "no",
        "never",
        "neither",
        "nor",
        "without",
        "isn't",
        "aren't",
        "wasn't",
        "weren't",
        "don't",
        "doesn't",
        "didn't",
        "can't",
        "cannot",
        "won't",
        "wouldn't",
        "shouldn't",
        "couldn't",
    }

    stop_terms = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "been",
        "being",
        "but",
        "by",
        "for",
        "from",
        "has",
        "have",
        "if",
        "in",
        "into",
        "is",
        "it",
        "its",
        "of",
        "on",
        "or",
        "that",
        "the",
        "their",
        "then",
        "there",
        "these",
        "this",
        "to",
        "was",
        "were",
        "will",
        "with",
        "your",
    }

    def _tokens(text: str) -> list[str]:
        return re.findall(
            r"[a-z0-9]+(?:'[a-z0-9]+)?",
            text.lower(),
        )

    def _has_negation(text: str) -> bool:
        return any(
            token in negation_terms
            for token in _tokens(text)
        )

    def _content_tokens(text: str) -> set[str]:
        return {
            token
            for token in _tokens(text)
            if token not in negation_terms
            and token not in stop_terms
            and len(token) > 2
        }

    def _jaccard(
        left: set[str],
        right: set[str],
    ) -> float:
        if not left or not right:
            return 0.0

        union = left | right

        if not union:
            return 0.0

        return len(left & right) / len(union)

    flagged_units: list[dict[str, Any]] = []

    total_claims = 0
    insufficient_count = 0
    contradiction_candidate_count = 0

    contradiction_pairs: list[
        dict[str, Any]
    ] = []

    for unit in units:
        if not isinstance(unit, Mapping):
            raise SectionEvidenceIntelligenceError(
                "Invalid Section Evidence Unit."
            )

        state = dict(
            unit.get(
                "evidence_attachment_state"
            )
            or {}
        )

        required_prior = (
            "structural_evidence",
            "entity_concept_evidence",
            "phrase_neighborhood_evidence",
            "topic_intent_evidence",
            "claim_evidence",
            "evidence_strength",
            "coverage",
        )

        if any(
            state.get(name) != "ATTACHED"
            for name in required_prior
        ):
            raise SectionEvidenceIntelligenceError(
                "4.6.5L cannot run before D-K "
                "evidence is complete."
            )

        section_id = str(
            unit.get("section_id") or ""
        ).strip()

        coverage = (
            unit.get("coverage")
            or {}
        )

        strength = (
            unit.get("evidence_strength")
            or {}
        )

        claim_scores = (
            strength.get("claim_scores")
            or []
        )

        if not isinstance(
            claim_scores,
            list,
        ):
            raise SectionEvidenceIntelligenceError(
                "Invalid claim score collection."
            )

        coverage_complete = (
            coverage.get("coverage_status")
            == "COMPLETE"
            and coverage.get(
                "layer_coverage_ratio"
            )
            == 1.0
            and coverage.get(
                "claim_score_coverage_ratio"
            )
            == 1.0
        )

        claim_flags = []

        for score in claim_scores:
            if not isinstance(score, Mapping):
                raise SectionEvidenceIntelligenceError(
                    "Invalid claim score record."
                )

            total_claims += 1

            band = score.get(
                "evidence_strength_band"
            )

            insufficient_reasons = []

            if band == "LIMITED":
                insufficient_reasons.append(
                    "LIMITED_ARTICLE_LOCAL_EVIDENCE_STRENGTH"
                )

            if not coverage_complete:
                insufficient_reasons.append(
                    "INCOMPLETE_EVIDENCE_COVERAGE"
                )

            insufficient = bool(
                insufficient_reasons
            )

            if insufficient:
                insufficient_count += 1

            claim_flags.append({
                "sentence_id":
                    score.get("sentence_id"),

                "statement_evidence_id":
                    score.get(
                        "statement_evidence_id"
                    ),

                "section_id":
                    section_id,

                "text":
                    score.get("text"),

                "evidence_strength_score":
                    score.get(
                        "evidence_strength_score"
                    ),

                "evidence_strength_band":
                    band,

                "insufficient_evidence_flag":
                    insufficient,

                "insufficient_evidence_reasons":
                    insufficient_reasons,

                "negation_present":
                    _has_negation(
                        str(
                            score.get("text")
                            or ""
                        )
                    ),

                "contradiction_candidate":
                    False,

                "contradiction_pair_ids":
                    [],

                "truth_assessed":
                    False,

                "logical_contradiction_adjudicated":
                    False,
            })

        # Conservative pair scan only inside this canonical section.
        for left_index in range(
            len(claim_flags)
        ):
            for right_index in range(
                left_index + 1,
                len(claim_flags),
            ):
                left = claim_flags[
                    left_index
                ]

                right = claim_flags[
                    right_index
                ]

                left_text = str(
                    left.get("text")
                    or ""
                )

                right_text = str(
                    right.get("text")
                    or ""
                )

                left_negated = (
                    left.get(
                        "negation_present"
                    )
                    is True
                )

                right_negated = (
                    right.get(
                        "negation_present"
                    )
                    is True
                )

                if (
                    left_negated
                    == right_negated
                ):
                    continue

                left_tokens = (
                    _content_tokens(
                        left_text
                    )
                )

                right_tokens = (
                    _content_tokens(
                        right_text
                    )
                )

                overlap = _jaccard(
                    left_tokens,
                    right_tokens,
                )

                # Deliberately high threshold:
                # negation alone is never enough.
                if overlap < 0.75:
                    continue

                shared_token_count = len(
                    left_tokens
                    & right_tokens
                )

                if shared_token_count < 4:
                    continue

                pair_id = _stable_id(
                    "contradiction_candidate",
                    coverage_result.get(
                        "article_id"
                    ),
                    section_id,
                    left.get(
                        "sentence_id"
                    ),
                    right.get(
                        "sentence_id"
                    ),
                )

                pair = {
                    "contradiction_candidate_id":
                        pair_id,

                    "section_id":
                        section_id,

                    "left_sentence_id":
                        left.get(
                            "sentence_id"
                        ),

                    "right_sentence_id":
                        right.get(
                            "sentence_id"
                        ),

                    "left_text":
                        left_text,

                    "right_text":
                        right_text,

                    "opposite_negation_polarity":
                        True,

                    "lexical_overlap":
                        round(
                            overlap,
                            3,
                        ),

                    "shared_content_token_count":
                        shared_token_count,

                    "candidate_only":
                        True,

                    "logical_contradiction_adjudicated":
                        False,

                    "truth_assessed":
                        False,
                }

                contradiction_pairs.append(
                    pair
                )

                contradiction_candidate_count += 1

                left[
                    "contradiction_candidate"
                ] = True

                right[
                    "contradiction_candidate"
                ] = True

                left[
                    "contradiction_pair_ids"
                ].append(
                    pair_id
                )

                right[
                    "contradiction_pair_ids"
                ].append(
                    pair_id
                )

        mapped_unit = dict(unit)

        section_insufficient_count = sum(
            1
            for item in claim_flags
            if item.get(
                "insufficient_evidence_flag"
            )
            is True
        )

        section_contradiction_count = sum(
            1
            for item in claim_flags
            if item.get(
                "contradiction_candidate"
            )
            is True
        )

        mapped_unit[
            "contradiction_analysis"
        ] = {
            "section_id":
                section_id,

            "analysis_scope":
                (
                    "CONSERVATIVE_ARTICLE_LOCAL_FLAGS_"
                    "NOT_LOGICAL_ADJUDICATION"
                ),

            "claim_count":
                len(claim_flags),

            "insufficient_evidence_claim_count":
                section_insufficient_count,

            "contradiction_candidate_claim_count":
                section_contradiction_count,

            "claim_flags":
                claim_flags,

            "insufficiency_rule": {
                "limited_strength_flagged":
                    True,

                "moderate_strength_automatically_flagged":
                    False,

                "incomplete_coverage_flagged":
                    True,
            },

            "contradiction_rule": {
                "same_section_required":
                    True,

                "opposite_negation_polarity_required":
                    True,

                "minimum_lexical_overlap":
                    0.75,

                "minimum_shared_content_tokens":
                    4,

                "negation_alone_sufficient":
                    False,

                "candidate_detection_only":
                    True,
            },

            "truth_assessment_performed":
                False,

            "logical_reasoning_performed":
                False,

            "claim_integrity_adjudication_performed":
                False,
        }

        state[
            "contradiction_analysis"
        ] = "ATTACHED"

        mapped_unit[
            "evidence_attachment_state"
        ] = state

        flagged_units.append(
            mapped_unit
        )

    flagged_order = [
        unit.get("section_id")
        for unit in flagged_units
    ]

    if flagged_order != canonical_order:
        raise SectionEvidenceIntelligenceError(
            "4.6.5L changed canonical section order."
        )

    source_claim_count = (
        coverage_result.get(
            "coverage_summary",
            {}
        ).get(
            "claim_candidate_count"
        )
    )

    if total_claims != source_claim_count:
        raise SectionEvidenceIntelligenceError(
            "4.6.5L claim count mismatch."
        )

    return {
        "schema_version":
            "section_contradiction_insufficient_flags_v1",

        "section_evidence_version":
            SECTION_EVIDENCE_INTELLIGENCE_VERSION,

        "phase":
            "4.6.5",

        "patch":
            "4.6.5L",

        "status":
            "CONTRADICTION_INSUFFICIENT_FLAGS_COMPLETE",

        "workspace_id":
            coverage_result.get(
                "workspace_id"
            ),

        "document_id":
            coverage_result.get(
                "document_id"
            ),

        "source_type":
            coverage_result.get(
                "source_type"
            ),

        "source_id":
            coverage_result.get(
                "source_id"
            ),

        "content_hash":
            coverage_result.get(
                "content_hash"
            ),

        "body_ref":
            coverage_result.get(
                "body_ref"
            ),

        "article_id":
            coverage_result.get(
                "article_id"
            ),

        "title":
            coverage_result.get(
                "title"
            ),

        "section_count":
            len(flagged_units),

        "section_evidence_units":
            flagged_units,

        "canonical_section_order":
            canonical_order,

        "contradiction_insufficient_summary": {
            "claim_count":
                total_claims,

            "insufficient_evidence_claim_count":
                insufficient_count,

            "contradiction_candidate_pair_count":
                contradiction_candidate_count,

            "contradiction_candidates":
                contradiction_pairs,

            "moderate_strength_automatically_insufficient":
                False,

            "negation_alone_treated_as_contradiction":
                False,

            "truth_assessment_performed":
                False,

            "logical_contradiction_adjudication_performed":
                False,

            "claim_integrity_adjudication_performed":
                False,
        },

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
                True,
            "phrase_neighborhood_evidence_attached":
                True,
            "topic_intent_evidence_attached":
                True,
            "claim_extraction_performed":
                True,
            "evidence_scoring_performed":
                True,
            "coverage_analysis_performed":
                True,
            "insufficiency_flagging_performed":
                True,
            "contradiction_candidate_detection_performed":
                True,
            "truth_assessment_performed":
                False,
            "external_authority_check_performed":
                False,
            "logical_reasoning_performed":
                False,
            "claim_integrity_adjudication_performed":
                False,
            "phrase_selected_for_linking":
                False,
            "target_selected":
                False,
            "url_selected":
                False,
            "link_type_selected":
                False,
            "highlight_color_selected":
                False,
            "semantic_memory_write_performed":
                False,
            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "final_article_local_section_evidence_result",
    }


__all__ = [
    "SECTION_EVIDENCE_INTELLIGENCE_VERSION",
    "SectionEvidenceIntelligenceError",
    "validate_section_evidence_intake_v1",
    "build_section_evidence_units_v1",
    "map_structural_evidence_v1",
    "attach_entity_concept_evidence_v1",
    "attach_phrase_neighborhood_evidence_v1",
    "attach_topic_intent_evidence_v1",
    "extract_statement_claim_evidence_v1",
    "score_evidence_strength_v1",
    "measure_evidence_coverage_v1",
    "flag_contradiction_insufficient_evidence_v1",
]
