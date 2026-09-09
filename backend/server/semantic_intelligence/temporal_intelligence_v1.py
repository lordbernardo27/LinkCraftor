from __future__ import annotations

from typing import Any, Mapping
import re
import hashlib


class TemporalIntelligenceError(ValueError):
    """Raised when canonical Temporal Intelligence contracts are violated."""


def validate_temporal_intelligence_intake_v1(
    certified_similarity_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate the canonical handoff from Phase 4.6.12
    Semantic Similarity Intelligence into Phase 4.6.13
    Temporal Intelligence.

    This stage performs intake validation only.

    It does NOT:
    - detect temporal expressions,
    - create temporal claim units,
    - infer dates or ages,
    - normalize temporal values,
    - infer before/after relations,
    - infer duration or intervals,
    - infer recurrence,
    - resolve temporal anchors,
    - infer chronology,
    - perform procedural reasoning,
    - perform quantitative reasoning,
    - perform new causal reasoning,
    - perform Analogical Intelligence,
    - perform Similarity Intelligence,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        certified_similarity_result,
        Mapping,
    ):
        raise TemporalIntelligenceError(
            "certified_similarity_result must be a mapping."
        )

    if (
        certified_similarity_result.get(
            "schema_version"
        )
        != "certified_similarity_intelligence_result_v1"
    ):
        raise TemporalIntelligenceError(
            "Temporal Intelligence requires "
            "certified_similarity_intelligence_result_v1."
        )

    if (
        certified_similarity_result.get(
            "status"
        )
        != "SIMILARITY_INTELLIGENCE_CERTIFIED"
    ):
        raise TemporalIntelligenceError(
            "Similarity Intelligence must be certified "
            "before Temporal Intelligence intake."
        )

    if (
        certified_similarity_result.get(
            "phase"
        )
        != "4.6.12"
    ):
        raise TemporalIntelligenceError(
            "Temporal Intelligence intake requires "
            "Phase 4.6.12 input."
        )

    if (
        certified_similarity_result.get(
            "patch"
        )
        != "4.6.12Q"
    ):
        raise TemporalIntelligenceError(
            "Temporal Intelligence intake requires "
            "canonical 4.6.12Q input."
        )

    if (
        certified_similarity_result.get(
            "next_stage"
        )
        != "temporal_intelligence"
    ):
        raise TemporalIntelligenceError(
            "Certified Similarity Intelligence must hand off "
            "to temporal_intelligence."
        )

    if (
        certified_similarity_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise TemporalIntelligenceError(
            "Temporal Intelligence intake must remain transient."
        )

    certification = certified_similarity_result.get(
        "certification"
    )

    if not isinstance(
        certification,
        Mapping,
    ):
        raise TemporalIntelligenceError(
            "Certified Similarity certification metadata "
            "must be a mapping."
        )

    if (
        certification.get(
            "performed"
        )
        is not True
        or certification.get(
            "certified"
        )
        is not True
        or certification.get(
            "certification_stage"
        )
        != "4.6.12Q"
    ):
        raise TemporalIntelligenceError(
            "Certified Similarity certification state is invalid."
        )

    processing_boundaries = certified_similarity_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        processing_boundaries,
        Mapping,
    ):
        raise TemporalIntelligenceError(
            "Certified Similarity processing boundaries "
            "must be a mapping."
        )

    if (
        processing_boundaries.get(
            "similarity_certification_performed"
        )
        is not True
        or processing_boundaries.get(
            "similarity_intelligence_certified"
        )
        is not True
    ):
        raise TemporalIntelligenceError(
            "Similarity hard-certification boundaries "
            "must be complete."
        )

    article_identity = certified_similarity_result.get(
        "article_identity"
    )

    if not isinstance(
        article_identity,
        Mapping,
    ):
        raise TemporalIntelligenceError(
            "Article identity must be a mapping."
        )

    required_identity_fields = (
        "article_id",
        "workspace_id",
        "source_type",
        "content_hash",
        "body_ref",
    )

    for field_name in required_identity_fields:
        if not str(
            article_identity.get(
                field_name
            )
            or ""
        ).strip():
            raise TemporalIntelligenceError(
                "Required article identity field missing: "
                + field_name
            )

    return {
        "schema_version":
            "temporal_intelligence_intake_v1",

        "temporal_intelligence_version":
            "temporal_intelligence_v1",

        "phase":
            "4.6.13",

        "patch":
            "4.6.13C",

        "status":
            "TEMPORAL_INTELLIGENCE_INTAKE_VALIDATED",

        "article_identity":
            dict(
                article_identity
            ),

        "upstream_similarity_result":
            certified_similarity_result,

        "upstream_certification": {
            "schema_version":
                certified_similarity_result.get(
                    "schema_version"
                ),

            "phase":
                certified_similarity_result.get(
                    "phase"
                ),

            "patch":
                certified_similarity_result.get(
                    "patch"
                ),

            "status":
                certified_similarity_result.get(
                    "status"
                ),

            "certification_stage":
                certification.get(
                    "certification_stage"
                ),

            "certified":
                True,
        },

        "processing_boundaries": {
            "temporal_intelligence_intake_validated":
                True,

            "temporal_claim_units_prepared":
                False,

            "temporal_signal_interpretation_performed":
                False,

            "temporal_candidate_extraction_performed":
                False,

            "temporal_grounding_performed":
                False,

            "temporal_orientation_performed":
                False,

            "temporal_value_validation_performed":
                False,

            "temporal_relation_validation_performed":
                False,

            "same_sentence_temporal_validation_performed":
                False,

            "cross_sentence_temporal_anchoring_performed":
                False,

            "temporal_evidence_assessment_performed":
                False,

            "temporal_duplicate_resolution_performed":
                False,

            "article_temporal_consolidation_performed":
                False,

            "final_temporal_result_built":
                False,

            "temporal_certification_performed":
                False,

            "new_temporal_relation_inference_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "similarity_reasoning_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
                False,

            "linking_decisions_performed":
                False,

            "semantic_memory_write_performed":
                False,

            "persistence_performed":
                False,
        },

        "temporal_boundaries": {
            "article_local_only":
                True,

            "lexical_temporal_signal_is_relation":
                False,

            "unstated_temporal_relation_inference_performed":
                False,

            "unstated_temporal_anchor_inference_performed":
                False,

            "unstated_duration_inference_performed":
                False,

            "unstated_recurrence_inference_performed":
                False,

            "scientific_truth_verified":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_checked":
                False,

            "linking_decisions_performed":
                False,

            "semantic_memory_write_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "temporal_claim_unit_preparation",
    }


def build_temporal_claim_units_v1(
    certified_similarity_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Build canonical Phase 4.6.13 Temporal Claim Units from
    certified Phase 4.6.12 Similarity Intelligence.

    This is a one-to-one structural preparation stage.

    It does NOT:
    - reparse the article body,
    - identify temporal signals,
    - determine whether a temporal expression establishes a relation,
    - normalize dates, ages, durations, or intervals,
    - select temporal anchors,
    - infer temporal anchors,
    - determine before/after orientation,
    - determine point/duration/interval type,
    - determine sequence, boundary, or recurrence relations,
    - perform cross-sentence temporal anchoring,
    - infer unstated chronology,
    - perform procedural reasoning,
    - perform quantitative reasoning,
    - perform new causal reasoning,
    - perform Analogical Intelligence,
    - perform new Similarity reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    intake = validate_temporal_intelligence_intake_v1(
        certified_similarity_result
    )

    if (
        intake.get(
            "status"
        )
        != "TEMPORAL_INTELLIGENCE_INTAKE_VALIDATED"
    ):
        raise TemporalIntelligenceError(
            "Canonical Temporal Intelligence intake was not validated."
        )

    identity = dict(
        certified_similarity_result.get(
            "article_identity"
        )
        or {}
    )

    article_id = str(
        identity.get(
            "article_id"
        )
        or ""
    )

    similarity_units = list(
        certified_similarity_result.get(
            "similarity_claim_units"
        )
        or []
    )

    if not article_id:
        raise TemporalIntelligenceError(
            "Certified Similarity article_id is required."
        )

    temporal_units = []
    temporal_sections = []

    seen_temporal_ids = set()
    seen_similarity_ids = set()
    seen_statement_ids = set()
    seen_sentence_ids = set()

    previous_global_index = None

    units_by_section = {}
    section_metadata = {}

    for similarity_unit in similarity_units:
        if not isinstance(
            similarity_unit,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every certified Similarity Claim Unit must be a mapping."
            )

        similarity_claim_unit_id = str(
            similarity_unit.get(
                "similarity_claim_unit_id"
            )
            or ""
        )

        statement_id = str(
            similarity_unit.get(
                "statement_evidence_id"
            )
            or ""
        )

        sentence_id = str(
            similarity_unit.get(
                "sentence_id"
            )
            or ""
        )

        section_id = str(
            similarity_unit.get(
                "section_id"
            )
            or ""
        )

        if not similarity_claim_unit_id:
            raise TemporalIntelligenceError(
                "Similarity Claim Unit ID is required."
            )

        if not similarity_claim_unit_id.startswith(
            "similarity_claim_"
        ):
            raise TemporalIntelligenceError(
                "Unexpected Similarity Claim Unit ID format."
            )

        if not statement_id:
            raise TemporalIntelligenceError(
                "statement_evidence_id is required."
            )

        if not sentence_id:
            raise TemporalIntelligenceError(
                "sentence_id is required."
            )

        if not section_id:
            raise TemporalIntelligenceError(
                "section_id is required."
            )

        if similarity_claim_unit_id in seen_similarity_ids:
            raise TemporalIntelligenceError(
                "Duplicate Similarity Claim Unit ID."
            )

        if statement_id in seen_statement_ids:
            raise TemporalIntelligenceError(
                "Duplicate statement_evidence_id."
            )

        if sentence_id in seen_sentence_ids:
            raise TemporalIntelligenceError(
                "Duplicate sentence_id."
            )

        if (
            similarity_unit.get(
                "article_id"
            )
            != article_id
        ):
            raise TemporalIntelligenceError(
                "Similarity Claim Unit article identity mismatch."
            )

        global_index = similarity_unit.get(
            "sentence_global_index"
        )

        article_position = similarity_unit.get(
            "article_position"
        )

        if not isinstance(
            global_index,
            int,
        ):
            raise TemporalIntelligenceError(
                "sentence_global_index must be an integer."
            )

        if not isinstance(
            article_position,
            int,
        ):
            raise TemporalIntelligenceError(
                "article_position must be an integer."
            )

        if (
            previous_global_index is not None
            and global_index <= previous_global_index
        ):
            raise TemporalIntelligenceError(
                "Certified Similarity Claim Units are not "
                "in canonical sentence order."
            )

        similarity_state = dict(
            similarity_unit.get(
                "similarity_analysis_state"
            )
            or {}
        )

        required_complete_similarity_stages = (
            "similarity_signal_interpretation",
            "similarity_candidate_extraction",
            "similarity_participant_grounding",
            "similarity_difference_orientation",
            "shared_characteristic_validation",
            "difference_contrast_validation",
            "same_sentence_similarity_validation",
            "cross_sentence_similarity_validation",
            "similarity_evidence_assessment",
            "duplicate_similarity_resolution",
        )

        for stage_name in required_complete_similarity_stages:
            if (
                similarity_state.get(
                    stage_name
                )
                != "COMPLETE"
            ):
                raise TemporalIntelligenceError(
                    "Similarity Claim Unit analysis is incomplete at "
                    + stage_name
                    + "."
                )

        upstream_boundaries = dict(
            similarity_unit.get(
                "processing_boundaries"
            )
            or {}
        )

        required_false_upstream_boundaries = (
            "embedding_similarity_performed",
            "fuzzy_similarity_performed",
            "unstated_shared_property_inference_performed",
            "unstated_difference_inference_performed",
            "analogical_reasoning_performed",
            "procedural_reasoning_performed",
            "quantitative_reasoning_performed",
            "temporal_reasoning_performed",
            "new_causal_reasoning_performed",
            "truth_assessment_performed",
            "external_authority_check_performed",
            "semantic_memory_write_performed",
            "persistence_performed",
        )

        for boundary_name in required_false_upstream_boundaries:
            if (
                upstream_boundaries.get(
                    boundary_name
                )
                is not False
            ):
                raise TemporalIntelligenceError(
                    "Upstream Similarity Claim Unit boundary "
                    "must remain False: "
                    + boundary_name
                )

        temporal_claim_unit_id = (
            "temporal_claim_"
            + similarity_claim_unit_id[
                len("similarity_claim_"):
            ]
        )

        if temporal_claim_unit_id in seen_temporal_ids:
            raise TemporalIntelligenceError(
                "Duplicate Temporal Claim Unit ID."
            )

        temporal_unit = {
            "temporal_claim_unit_id":
                temporal_claim_unit_id,

            "upstream_similarity_claim_unit_id":
                similarity_claim_unit_id,

            "upstream_analogical_claim_unit_id":
                similarity_unit.get(
                    "upstream_analogical_claim_unit_id"
                ),

            "upstream_procedural_claim_unit_id":
                similarity_unit.get(
                    "upstream_procedural_claim_unit_id"
                ),

            "upstream_quantitative_claim_unit_id":
                similarity_unit.get(
                    "upstream_quantitative_claim_unit_id"
                ),

            "upstream_causal_claim_unit_id":
                similarity_unit.get(
                    "upstream_causal_claim_unit_id"
                ),

            "upstream_relational_claim_unit_id":
                similarity_unit.get(
                    "upstream_relational_claim_unit_id"
                ),

            "upstream_logical_claim_unit_id":
                similarity_unit.get(
                    "upstream_logical_claim_unit_id"
                ),

            "statement_evidence_id":
                statement_id,

            "sentence_id":
                sentence_id,

            "article_id":
                article_id,

            "section_id":
                section_id,

            "section_evidence_unit_id":
                similarity_unit.get(
                    "section_evidence_unit_id"
                ),

            "section_index":
                similarity_unit.get(
                    "section_index"
                ),

            "section_title":
                similarity_unit.get(
                    "section_title"
                ),

            "heading_level":
                similarity_unit.get(
                    "heading_level"
                ),

            "block_id":
                similarity_unit.get(
                    "block_id"
                ),

            "paragraph_id":
                similarity_unit.get(
                    "paragraph_id"
                ),

            "block_type":
                similarity_unit.get(
                    "block_type"
                ),

            "block_index":
                similarity_unit.get(
                    "block_index"
                ),

            "sentence_index":
                similarity_unit.get(
                    "sentence_index"
                ),

            "sentence_global_index":
                global_index,

            "article_position":
                article_position,

            "claim_index_in_section":
                similarity_unit.get(
                    "claim_index_in_section"
                ),

            "text":
                similarity_unit.get(
                    "text"
                ),

            "word_count":
                similarity_unit.get(
                    "word_count"
                ),

            "character_count":
                similarity_unit.get(
                    "character_count"
                ),

            "statement_form":
                similarity_unit.get(
                    "statement_form"
                ),

            "canonical_claim_candidate":
                similarity_unit.get(
                    "canonical_claim_candidate"
                )
                is True,

            "evidence_context":
                dict(
                    similarity_unit.get(
                        "evidence_context"
                    )
                    or {}
                ),

            "upstream_similarity_analysis_state":
                similarity_state,

            "upstream_similarity_processing_boundaries":
                upstream_boundaries,

            "temporal_analysis_state": {
                "temporal_signal_interpretation":
                    "PENDING",

                "temporal_candidate_extraction":
                    "PENDING",

                "temporal_anchor_participant_grounding":
                    "PENDING",

                "temporal_relation_orientation":
                    "PENDING",

                "point_duration_interval_validation":
                    "PENDING",

                "sequence_boundary_recurrence_validation":
                    "PENDING",

                "same_sentence_temporal_validation":
                    "PENDING",

                "cross_sentence_temporal_anchoring":
                    "PENDING",

                "temporal_evidence_assessment":
                    "PENDING",

                "duplicate_temporal_resolution":
                    "PENDING",
            },

            "processing_boundaries": {
                "article_local_only":
                    True,

                "temporal_claim_unit_prepared":
                    True,

                "article_body_reparsed":
                    False,

                "temporal_signal_interpretation_performed":
                    False,

                "temporal_candidate_extraction_performed":
                    False,

                "temporal_grounding_performed":
                    False,

                "temporal_orientation_performed":
                    False,

                "temporal_value_validation_performed":
                    False,

                "temporal_relation_validation_performed":
                    False,

                "same_sentence_temporal_validation_performed":
                    False,

                "cross_sentence_temporal_anchoring_performed":
                    False,

                "temporal_evidence_assessment_performed":
                    False,

                "temporal_duplicate_resolution_performed":
                    False,

                "lexical_temporal_signal_is_relation":
                    False,

                "unstated_temporal_relation_inference_performed":
                    False,

                "unstated_temporal_anchor_inference_performed":
                    False,

                "unstated_duration_inference_performed":
                    False,

                "unstated_recurrence_inference_performed":
                    False,

                "procedural_reasoning_performed":
                    False,

                "quantitative_reasoning_performed":
                    False,

                "new_causal_reasoning_performed":
                    False,

                "analogical_reasoning_performed":
                    False,

                "similarity_reasoning_performed":
                    False,

                "truth_assessment_performed":
                    False,

                "external_authority_check_performed":
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
        }

        temporal_units.append(
            temporal_unit
        )

        units_by_section.setdefault(
            section_id,
            [],
        ).append(
            temporal_unit
        )

        if section_id not in section_metadata:
            section_metadata[
                section_id
            ] = {
                "section_id":
                    section_id,

                "section_index":
                    similarity_unit.get(
                        "section_index"
                    ),

                "section_title":
                    similarity_unit.get(
                        "section_title"
                    ),

                "heading_level":
                    similarity_unit.get(
                        "heading_level"
                    ),
            }

        seen_temporal_ids.add(
            temporal_claim_unit_id
        )

        seen_similarity_ids.add(
            similarity_claim_unit_id
        )

        seen_statement_ids.add(
            statement_id
        )

        seen_sentence_ids.add(
            sentence_id
        )

        previous_global_index = (
            global_index
        )

    ordered_section_ids = []

    for unit in temporal_units:
        section_id = str(
            unit.get(
                "section_id"
            )
            or ""
        )

        if section_id not in ordered_section_ids:
            ordered_section_ids.append(
                section_id
            )

    for section_id in ordered_section_ids:
        metadata = dict(
            section_metadata.get(
                section_id
            )
            or {}
        )

        section_units = list(
            units_by_section.get(
                section_id,
                []
            )
        )

        temporal_sections.append({
            **metadata,

            "upstream_similarity_claim_count":
                len(
                    section_units
                ),

            "temporal_claim_unit_count":
                len(
                    section_units
                ),

            "temporal_claim_units":
                section_units,
        })

    if (
        len(
            temporal_units
        )
        != len(
            similarity_units
        )
    ):
        raise TemporalIntelligenceError(
            "Temporal Claim Unit construction must remain "
            "one-to-one with Similarity Claim Units."
        )

    return {
        "schema_version":
            "temporal_claim_units_v1",

        "temporal_intelligence_version":
            "temporal_intelligence_v1",

        "phase":
            "4.6.13",

        "patch":
            "4.6.13D",

        "status":
            "TEMPORAL_CLAIM_UNITS_PREPARED",

        "article_identity":
            identity,

        "similarity_claim_unit_count":
            len(
                similarity_units
            ),

        "temporal_claim_unit_count":
            len(
                temporal_units
            ),

        "section_count":
            len(
                temporal_sections
            ),

        "temporal_sections":
            temporal_sections,

        "temporal_claim_units":
            temporal_units,

        "construction_summary": {
            "source_similarity_claim_unit_count":
                len(
                    similarity_units
                ),

            "temporal_claim_unit_count":
                len(
                    temporal_units
                ),

            "one_to_one_similarity_mapping":
                (
                    len(
                        temporal_units
                    )
                    == len(
                        similarity_units
                    )
                ),

            "canonical_order_preserved":
                True,

            "canonical_text_preserved":
                True,

            "evidence_context_preserved":
                True,

            "similarity_context_preserved":
                True,

            "article_body_reparsed":
                False,

            "temporal_signals_interpreted":
                False,

            "temporal_anchors_selected":
                False,

            "temporal_values_normalized":
                False,

            "temporal_relations_inferred":
                False,

            "unstated_chronology_inferred":
                False,
        },

        "processing_boundaries": {
            "article_body_reparsed":
                False,

            "temporal_claim_units_prepared":
                True,

            "temporal_signal_interpretation_performed":
                False,

            "temporal_candidate_extraction_performed":
                False,

            "temporal_grounding_performed":
                False,

            "temporal_orientation_performed":
                False,

            "temporal_value_validation_performed":
                False,

            "temporal_relation_validation_performed":
                False,

            "same_sentence_temporal_validation_performed":
                False,

            "cross_sentence_temporal_anchoring_performed":
                False,

            "temporal_evidence_assessment_performed":
                False,

            "temporal_duplicate_resolution_performed":
                False,

            "unstated_temporal_relation_inference_performed":
                False,

            "unstated_temporal_anchor_inference_performed":
                False,

            "unstated_duration_inference_performed":
                False,

            "unstated_recurrence_inference_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "similarity_reasoning_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
                False,

            "linking_decisions_performed":
                False,

            "semantic_memory_write_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "temporal_signal_interpretation",
    }


def interpret_temporal_signals_v1(
    temporal_claim_units_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Interpret explicit article-local Temporal signals in canonical
    Phase 4.6.13 Temporal Claim Units.

    Stage E identifies lexical/structural Temporal evidence only.

    Signal presence does NOT establish a valid Temporal relation.

    This stage does NOT:
    - extract Temporal candidates,
    - select or ground Temporal anchors,
    - determine Temporal relation orientation,
    - normalize dates, ages, durations, or intervals,
    - validate point/duration/interval semantics,
    - validate sequence/boundary/recurrence semantics,
    - perform same-sentence Temporal validation,
    - perform cross-sentence Temporal anchoring,
    - infer unstated chronology,
    - infer unstated Temporal anchors,
    - infer unstated durations,
    - infer unstated recurrence,
    - perform procedural reasoning,
    - perform quantitative reasoning,
    - perform new causal reasoning,
    - perform Analogical Intelligence,
    - perform new Similarity reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        temporal_claim_units_result,
        Mapping,
    ):
        raise TemporalIntelligenceError(
            "temporal_claim_units_result must be a mapping."
        )

    if (
        temporal_claim_units_result.get(
            "schema_version"
        )
        != "temporal_claim_units_v1"
    ):
        raise TemporalIntelligenceError(
            "Stage E requires temporal_claim_units_v1."
        )

    if (
        temporal_claim_units_result.get(
            "status"
        )
        != "TEMPORAL_CLAIM_UNITS_PREPARED"
    ):
        raise TemporalIntelligenceError(
            "Temporal Claim Units must be prepared before Stage E."
        )

    if (
        temporal_claim_units_result.get(
            "phase"
        )
        != "4.6.13"
    ):
        raise TemporalIntelligenceError(
            "Stage E requires Phase 4.6.13 input."
        )

    if (
        temporal_claim_units_result.get(
            "patch"
        )
        != "4.6.13D"
    ):
        raise TemporalIntelligenceError(
            "Stage E requires canonical 4.6.13D input."
        )

    if (
        temporal_claim_units_result.get(
            "next_stage"
        )
        != "temporal_signal_interpretation"
    ):
        raise TemporalIntelligenceError(
            "Stage D must hand off to temporal_signal_interpretation."
        )

    if (
        temporal_claim_units_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise TemporalIntelligenceError(
            "Temporal Intelligence must remain transient."
        )

    signal_specs = (
        (
            "BETWEEN_RANGE",
            "EXPLICIT_TEMPORAL_INTERVAL_SIGNAL",
            re.compile(
                r"\bbetween\s+"
                r"(?:about\s+|around\s+)?"
                r"\d+(?:\.\d+)?\s*"
                r"(?:days?|weeks?|months?|years?)?"
                r"\s+and\s+"
                r"(?:about\s+|around\s+)?"
                r"\d+(?:\.\d+)?\s*"
                r"(?:days?|weeks?|months?|years?)"
                r"(?:\s+old)?\b",
                re.IGNORECASE,
            ),
        ),
        (
            "FROM_TO_RANGE",
            "EXPLICIT_TEMPORAL_INTERVAL_SIGNAL",
            re.compile(
                r"\bfrom\s+"
                r"(?:age\s+)?"
                r"\d+(?:\.\d+)?\s*"
                r"(?:days?|weeks?|months?|years?)?"
                r"\s+(?:to|until|through)\s+"
                r"(?:age\s+)?"
                r"(?:\d+(?:\.\d+)?\s*"
                r"(?:days?|weeks?|months?|years?)"
                r"|adolescence|adulthood)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "AFTER",
            "EXPLICIT_TEMPORAL_SEQUENCE_SIGNAL",
            re.compile(
                r"\bafter\b",
                re.IGNORECASE,
            ),
        ),
        (
            "BEFORE",
            "EXPLICIT_TEMPORAL_SEQUENCE_SIGNAL",
            re.compile(
                r"\bbefore\b",
                re.IGNORECASE,
            ),
        ),
        (
            "DURING",
            "EXPLICIT_TEMPORAL_CONTAINMENT_SIGNAL",
            re.compile(
                r"\bduring\b",
                re.IGNORECASE,
            ),
        ),
        (
            "SINCE",
            "EXPLICIT_TEMPORAL_START_BOUNDARY_SIGNAL",
            re.compile(
                r"\bsince\b",
                re.IGNORECASE,
            ),
        ),
        (
            "UNTIL",
            "EXPLICIT_TEMPORAL_END_BOUNDARY_SIGNAL",
            re.compile(
                r"\buntil\b",
                re.IGNORECASE,
            ),
        ),
        (
            "WITHIN",
            "EXPLICIT_TEMPORAL_BOUNDARY_SIGNAL",
            re.compile(
                r"\bwithin\b",
                re.IGNORECASE,
            ),
        ),
        (
            "BY_TIME",
            "EXPLICIT_TEMPORAL_UPPER_BOUND_SIGNAL",
            re.compile(
                r"\bby\s+"
                r"(?:about\s+|around\s+)?"
                r"(?:age\s+)?"
                r"\d+(?:\.\d+)?\s*"
                r"(?:days?|weeks?|months?|years?)"
                r"(?:\s+old)?\b",
                re.IGNORECASE,
            ),
        ),
        (
            "AT_AGE_TIME",
            "EXPLICIT_TEMPORAL_POINT_SIGNAL",
            re.compile(
                r"\bat\s+"
                r"(?:about\s+|around\s+)?"
                r"(?:age\s+)?"
                r"\d+(?:\.\d+)?\s*"
                r"(?:days?|weeks?|months?|years?)"
                r"(?:\s+old)?\b",
                re.IGNORECASE,
            ),
        ),
        (
            "AGE_UNDER",
            "EXPLICIT_TEMPORAL_AGE_BOUND_SIGNAL",
            re.compile(
                r"\bunder\s+"
                r"(?:age\s+)?"
                r"\d+(?:\.\d+)?\s*"
                r"(?:days?|weeks?|months?|years?)"
                r"(?:\s+old)?\b",
                re.IGNORECASE,
            ),
        ),
        (
            "UP_TO_AGE",
            "EXPLICIT_TEMPORAL_UPPER_BOUND_SIGNAL",
            re.compile(
                r"\bup\s+to\s+"
                r"(?:age\s+)?"
                r"\d+(?:\.\d+)?\s*"
                r"(?:days?|weeks?|months?|years?)?"
                r"(?:\s+old)?\b",
                re.IGNORECASE,
            ),
        ),
        (
            "AGE_RANGE",
            "EXPLICIT_TEMPORAL_INTERVAL_SIGNAL",
            re.compile(
                r"\b(?:ages?\s+)?"
                r"\d+(?:\.\d+)?\s*"
                r"(?:days?|weeks?|months?|years?)?"
                r"\s+to\s+"
                r"\d+(?:\.\d+)?\s*"
                r"(?:days?|weeks?|months?|years?)"
                r"(?:\s+old)?\b",
                re.IGNORECASE,
            ),
        ),
        (
            "AGE_POINT",
            "EXPLICIT_TEMPORAL_AGE_SIGNAL",
            re.compile(
                r"\b(?:"
                r"age\s+\d+(?:\.\d+)?"
                r"(?:\s*(?:days?|weeks?|months?|years?)"
                r"(?:\s+old)?)?"
                r"|"
                r"\d+(?:\.\d+)?\s*"
                r"(?:days?|weeks?|months?|years?)"
                r"(?:\s+old)?"
                r")\b",
                re.IGNORECASE,
            ),
        ),
        (
            "BIRTH_ANCHOR",
            "EXPLICIT_TEMPORAL_ANCHOR_SIGNAL",
            re.compile(
                r"\b(?:"
                r"at\s+birth"
                r"|since\s+birth"
                r"|from\s+birth"
                r"|after\s+birth"
                r"|before\s+birth"
                r")\b",
                re.IGNORECASE,
            ),
        ),
        (
            "OVER_TIME",
            "EXPLICIT_TEMPORAL_PROGRESS_SIGNAL",
            re.compile(
                r"\bover\s+time\b",
                re.IGNORECASE,
            ),
        ),
        (
            "OVER_PERIOD",
            "EXPLICIT_TEMPORAL_DURATION_SIGNAL",
            re.compile(
                r"\bover\s+(?:"
                r"(?:a|an|the)?\s*"
                r"(?:short|long|extended|brief)?\s*"
                r"period\s+of\s+time"
                r"|"
                r"\d+(?:\.\d+)?\s*"
                r"(?:days?|weeks?|months?|years?)"
                r")\b",
                re.IGNORECASE,
            ),
        ),
        (
            "PER_TIME_UNIT",
            "EXPLICIT_TEMPORAL_RECURRENCE_SIGNAL",
            re.compile(
                r"\bper\s+"
                r"(?:day|week|month|year|visit)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "EACH_TIME_UNIT",
            "EXPLICIT_TEMPORAL_RECURRENCE_SIGNAL",
            re.compile(
                r"\b(?:each|every)\s+"
                r"(?:day|week|month|year|visit|appointment|checkup)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "LAST_EVENT_REFERENCE",
            "EXPLICIT_RELATIVE_TEMPORAL_REFERENCE_SIGNAL",
            re.compile(
                r"\b(?:last|previous)\s+"
                r"(?:visit|appointment|checkup|measurement)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "FIRST_PERIOD",
            "EXPLICIT_TEMPORAL_PERIOD_SIGNAL",
            re.compile(
                r"\bfirst\s+"
                r"(?:few\s+)?"
                r"(?:days?|weeks?|months?|years?)"
                r"(?:\s+of\s+(?:life|infancy|childhood))?\b",
                re.IGNORECASE,
            ),
        ),
    )

    ambiguous_specs = (
        (
            "GENERIC_THEN",
            re.compile(
                r"\bthen\b",
                re.IGNORECASE,
            ),
            "THEN_MAY_BE_PROCEDURAL_OR_DISCOURSE_SEQUENCE",
        ),
        (
            "GENERIC_FIRST",
            re.compile(
                r"\bfirst\b",
                re.IGNORECASE,
            ),
            "FIRST_MAY_BE_PROCEDURAL_PRIORITY_OR_TEMPORAL_ORDER",
        ),
        (
            "GENERIC_NEXT",
            re.compile(
                r"\bnext\b",
                re.IGNORECASE,
            ),
            "NEXT_MAY_BE_PROCEDURAL_OR_RELATIVE_TEMPORAL_REFERENCE",
        ),
        (
            "GENERIC_WHILE",
            re.compile(
                r"\bwhile\b",
                re.IGNORECASE,
            ),
            "WHILE_MAY_EXPRESS_SIMULTANEITY_OR_PROCEDURAL_CONTEXT",
        ),
        (
            "GENERIC_LATER",
            re.compile(
                r"\blater\b",
                re.IGNORECASE,
            ),
            "LATER_REQUIRES_A_RESOLVABLE_TEMPORAL_ANCHOR",
        ),
        (
            "GENERIC_EARLIER",
            re.compile(
                r"\bearlier\b",
                re.IGNORECASE,
            ),
            "EARLIER_REQUIRES_A_RESOLVABLE_TEMPORAL_ANCHOR",
        ),
        (
            "GENERIC_CURRENT",
            re.compile(
                r"\bcurrent\b",
                re.IGNORECASE,
            ),
            "CURRENT_MAY_BE_CONTEXTUAL_WITHOUT_A_RESOLVED_TEMPORAL_ANCHOR",
        ),
    )

    source_units = list(
        temporal_claim_units_result.get(
            "temporal_claim_units"
        )
        or []
    )

    interpreted_units = []
    interpreted_by_id = {}

    total_signal_count = 0
    units_with_signals = 0
    deferred_ambiguous_signal_count = 0

    signal_type_counts = {}
    semantic_class_counts = {}
    exclusion_type_counts = {}

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "temporal_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "temporal_signal_interpretation"
            )
            != "PENDING"
        ):
            raise TemporalIntelligenceError(
                "Temporal signal interpretation must "
                "be PENDING before Stage E."
            )

        if (
            state.get(
                "temporal_candidate_extraction"
            )
            != "PENDING"
        ):
            raise TemporalIntelligenceError(
                "Temporal candidate extraction must "
                "remain PENDING during Stage E."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "temporal_claim_unit_prepared"
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                "Temporal Claim Unit preparation "
                "boundary is incomplete."
            )

        required_false_boundaries = (
            "temporal_signal_interpretation_performed",
            "temporal_candidate_extraction_performed",
            "temporal_grounding_performed",
            "temporal_orientation_performed",
            "temporal_value_validation_performed",
            "temporal_relation_validation_performed",
            "same_sentence_temporal_validation_performed",
            "cross_sentence_temporal_anchoring_performed",
            "temporal_evidence_assessment_performed",
            "temporal_duplicate_resolution_performed",
            "unstated_temporal_relation_inference_performed",
            "unstated_temporal_anchor_inference_performed",
            "unstated_duration_inference_performed",
            "unstated_recurrence_inference_performed",
            "procedural_reasoning_performed",
            "quantitative_reasoning_performed",
            "new_causal_reasoning_performed",
            "analogical_reasoning_performed",
            "similarity_reasoning_performed",
            "truth_assessment_performed",
            "external_authority_check_performed",
            "semantic_memory_write_performed",
            "persistence_performed",
        )

        for boundary_name in required_false_boundaries:
            if (
                boundaries.get(
                    boundary_name
                )
                is not False
            ):
                raise TemporalIntelligenceError(
                    boundary_name
                    + " must be False before Stage E."
                )

        source_text = str(
            unit.get(
                "text"
            )
            or ""
        )

        signals = []
        exclusions = []
        occupied_spans = []

        for (
            signal_type,
            semantic_class,
            pattern,
        ) in signal_specs:
            for match in pattern.finditer(
                source_text
            ):
                span = (
                    match.start(),
                    match.end(),
                )

                duplicate_signal_span = any(
                    span[0] == existing_start
                    and span[1] == existing_end
                    and signal_type == existing_type
                    for (
                        existing_start,
                        existing_end,
                        existing_type,
                    ) in occupied_spans
                )

                if duplicate_signal_span:
                    continue

                signal = {
                    "signal_type":
                        signal_type,

                    "temporal_semantic_class":
                        semantic_class,

                    "matched_text":
                        match.group(0),

                    "character_start":
                        match.start(),

                    "character_end":
                        match.end(),

                    "article_asserted_signal":
                        True,

                    "temporal_relation_validated":
                        False,

                    "temporal_candidate_extracted":
                        False,

                    "temporal_anchor_grounded":
                        False,

                    "temporal_orientation_determined":
                        False,

                    "temporal_value_validated":
                        False,

                    "same_sentence_temporal_validated":
                        False,

                    "cross_sentence_temporal_anchor_resolved":
                        False,

                    "unstated_temporal_relation_inference_performed":
                        False,

                    "unstated_temporal_anchor_inference_performed":
                        False,

                    "unstated_duration_inference_performed":
                        False,

                    "unstated_recurrence_inference_performed":
                        False,

                    "procedural_reasoning_performed":
                        False,

                    "quantitative_reasoning_performed":
                        False,

                    "new_causal_reasoning_performed":
                        False,

                    "analogical_reasoning_performed":
                        False,

                    "similarity_reasoning_performed":
                        False,

                    "truth_verified":
                        False,
                }

                signals.append(
                    signal
                )

                occupied_spans.append(
                    (
                        match.start(),
                        match.end(),
                        signal_type,
                    )
                )

                signal_type_counts[
                    signal_type
                ] = (
                    signal_type_counts.get(
                        signal_type,
                        0,
                    )
                    + 1
                )

                semantic_class_counts[
                    semantic_class
                ] = (
                    semantic_class_counts.get(
                        semantic_class,
                        0,
                    )
                    + 1
                )

        for (
            exclusion_type,
            pattern,
            reason,
        ) in ambiguous_specs:
            for match in pattern.finditer(
                source_text
            ):
                span = (
                    match.start(),
                    match.end(),
                )

                overlaps_explicit_signal = any(
                    span[0] < signal_end
                    and span[1] > signal_start
                    for (
                        signal_start,
                        signal_end,
                        _,
                    ) in occupied_spans
                )

                if overlaps_explicit_signal:
                    continue

                exclusions.append({
                    "signal_type":
                        exclusion_type,

                    "classification":
                        "AMBIGUOUS_TEMPORAL_LEXEME_DEFERRED",

                    "exclusion_reason":
                        reason,

                    "matched_text":
                        match.group(0),

                    "character_start":
                        match.start(),

                    "character_end":
                        match.end(),

                    "candidate_eligible":
                        False,

                    "temporal_relation_inference_performed":
                        False,

                    "temporal_anchor_inference_performed":
                        False,

                    "procedural_reasoning_performed":
                        False,

                    "truth_verified":
                        False,
                })

                deferred_ambiguous_signal_count += 1

                exclusion_type_counts[
                    exclusion_type
                ] = (
                    exclusion_type_counts.get(
                        exclusion_type,
                        0,
                    )
                    + 1
                )

        signals.sort(
            key=lambda item: (
                int(
                    item.get(
                        "character_start"
                    )
                    or 0
                ),
                int(
                    item.get(
                        "character_end"
                    )
                    or 0
                ),
                str(
                    item.get(
                        "signal_type"
                    )
                    or ""
                ),
            )
        )

        exclusions.sort(
            key=lambda item: (
                int(
                    item.get(
                        "character_start"
                    )
                    or 0
                ),
                int(
                    item.get(
                        "character_end"
                    )
                    or 0
                ),
                str(
                    item.get(
                        "signal_type"
                    )
                    or ""
                ),
            )
        )

        unit_total = len(
            signals
        )

        total_signal_count += (
            unit_total
        )

        if unit_total:
            units_with_signals += 1

        interpreted_state = dict(
            state
        )

        interpreted_state[
            "temporal_signal_interpretation"
        ] = "COMPLETE"

        interpreted_boundaries = dict(
            boundaries
        )

        interpreted_boundaries[
            "temporal_signal_interpretation_performed"
        ] = True

        interpreted_boundaries[
            "temporal_candidate_extraction_performed"
        ] = False

        interpreted_boundaries[
            "temporal_grounding_performed"
        ] = False

        interpreted_boundaries[
            "temporal_orientation_performed"
        ] = False

        interpreted_boundaries[
            "temporal_value_validation_performed"
        ] = False

        interpreted_boundaries[
            "temporal_relation_validation_performed"
        ] = False

        interpreted_boundaries[
            "same_sentence_temporal_validation_performed"
        ] = False

        interpreted_boundaries[
            "cross_sentence_temporal_anchoring_performed"
        ] = False

        interpreted_boundaries[
            "temporal_evidence_assessment_performed"
        ] = False

        interpreted_boundaries[
            "temporal_duplicate_resolution_performed"
        ] = False

        interpreted_boundaries[
            "unstated_temporal_relation_inference_performed"
        ] = False

        interpreted_boundaries[
            "unstated_temporal_anchor_inference_performed"
        ] = False

        interpreted_boundaries[
            "unstated_duration_inference_performed"
        ] = False

        interpreted_boundaries[
            "unstated_recurrence_inference_performed"
        ] = False

        interpreted_boundaries[
            "procedural_reasoning_performed"
        ] = False

        interpreted_boundaries[
            "quantitative_reasoning_performed"
        ] = False

        interpreted_boundaries[
            "new_causal_reasoning_performed"
        ] = False

        interpreted_boundaries[
            "analogical_reasoning_performed"
        ] = False

        interpreted_boundaries[
            "similarity_reasoning_performed"
        ] = False

        interpreted_boundaries[
            "truth_assessment_performed"
        ] = False

        interpreted_boundaries[
            "external_authority_check_performed"
        ] = False

        interpreted_unit = dict(
            unit
        )

        interpreted_unit.update({
            "temporal_signals":
                signals,

            "temporal_signal_exclusions":
                exclusions,

            "temporal_signal_count":
                unit_total,

            "temporal_signal_exclusion_count":
                len(
                    exclusions
                ),

            "has_temporal_signal":
                unit_total > 0,

            "temporal_signal_interpretation_scope":
                (
                    "ARTICLE_LOCAL_EXPLICIT_"
                    "TEMPORAL_SIGNAL_ONLY"
                ),

            "temporal_analysis_state":
                interpreted_state,

            "processing_boundaries":
                interpreted_boundaries,
        })

        interpreted_units.append(
            interpreted_unit
        )

        unit_id = str(
            interpreted_unit.get(
                "temporal_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise TemporalIntelligenceError(
                "Every interpreted Temporal Claim Unit requires an ID."
            )

        if unit_id in interpreted_by_id:
            raise TemporalIntelligenceError(
                "Duplicate interpreted Temporal Claim Unit ID."
            )

        interpreted_by_id[
            unit_id
        ] = interpreted_unit

    interpreted_sections = []

    for section in (
        temporal_claim_units_result.get(
            "temporal_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "temporal_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Every section Temporal Claim Unit "
                    "reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "temporal_claim_unit_id"
                )
                or ""
            )

            resolved_unit = interpreted_by_id.get(
                unit_id
            )

            if resolved_unit is None:
                raise TemporalIntelligenceError(
                    "Temporal section references "
                    "an unknown claim unit."
                )

            section_units.append(
                resolved_unit
            )

        interpreted_sections.append({
            **dict(
                section
            ),

            "temporal_claim_units":
                section_units,

            "temporal_signal_unit_count":
                sum(
                    1
                    for unit in section_units
                    if unit.get(
                        "has_temporal_signal"
                    )
                    is True
                ),

            "temporal_signal_count":
                sum(
                    int(
                        unit.get(
                            "temporal_signal_count"
                        )
                        or 0
                    )
                    for unit in section_units
                ),

            "temporal_signal_exclusion_count":
                sum(
                    int(
                        unit.get(
                            "temporal_signal_exclusion_count"
                        )
                        or 0
                    )
                    for unit in section_units
                ),
        })

    result = dict(
        temporal_claim_units_result
    )

    result_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    result_boundaries[
        "temporal_signal_interpretation_performed"
    ] = True

    result_boundaries[
        "temporal_candidate_extraction_performed"
    ] = False

    result_boundaries[
        "temporal_grounding_performed"
    ] = False

    result_boundaries[
        "temporal_orientation_performed"
    ] = False

    result_boundaries[
        "temporal_value_validation_performed"
    ] = False

    result_boundaries[
        "temporal_relation_validation_performed"
    ] = False

    result_boundaries[
        "same_sentence_temporal_validation_performed"
    ] = False

    result_boundaries[
        "cross_sentence_temporal_anchoring_performed"
    ] = False

    result_boundaries[
        "temporal_evidence_assessment_performed"
    ] = False

    result_boundaries[
        "temporal_duplicate_resolution_performed"
    ] = False

    result_boundaries[
        "unstated_temporal_relation_inference_performed"
    ] = False

    result_boundaries[
        "unstated_temporal_anchor_inference_performed"
    ] = False

    result_boundaries[
        "unstated_duration_inference_performed"
    ] = False

    result_boundaries[
        "unstated_recurrence_inference_performed"
    ] = False

    result_boundaries[
        "procedural_reasoning_performed"
    ] = False

    result_boundaries[
        "quantitative_reasoning_performed"
    ] = False

    result_boundaries[
        "new_causal_reasoning_performed"
    ] = False

    result_boundaries[
        "analogical_reasoning_performed"
    ] = False

    result_boundaries[
        "similarity_reasoning_performed"
    ] = False

    result_boundaries[
        "truth_assessment_performed"
    ] = False

    result_boundaries[
        "external_authority_check_performed"
    ] = False

    result.update({
        "schema_version":
            "temporal_signal_interpretation_v1",

        "patch":
            "4.6.13E",

        "status":
            "TEMPORAL_SIGNAL_INTERPRETATION_COMPLETE",

        "temporal_sections":
            interpreted_sections,

        "temporal_claim_units":
            interpreted_units,

        "temporal_signal_summary": {
            "claim_unit_count":
                len(
                    interpreted_units
                ),

            "units_with_temporal_signals":
                units_with_signals,

            "total_temporal_signal_count":
                total_signal_count,

            "deferred_ambiguous_signal_count":
                deferred_ambiguous_signal_count,

            "signal_type_counts":
                dict(
                    sorted(
                        signal_type_counts.items()
                    )
                ),

            "semantic_class_counts":
                dict(
                    sorted(
                        semantic_class_counts.items()
                    )
                ),

            "exclusion_type_counts":
                dict(
                    sorted(
                        exclusion_type_counts.items()
                    )
                ),

            "zero_signal_units_allowed":
                True,

            "ambiguous_lexemes_deferred":
                True,

            "signal_presence_not_relation_validity":
                True,

            "generic_then_not_automatically_temporal_relation":
                True,

            "generic_first_not_automatically_temporal_relation":
                True,

            "generic_next_not_automatically_temporal_relation":
                True,

            "generic_while_not_automatically_simultaneity":
                True,

            "relative_later_requires_anchor":
                True,

            "relative_earlier_requires_anchor":
                True,

            "temporal_candidates_extracted":
                False,

            "temporal_anchors_grounded":
                False,

            "temporal_orientation_determined":
                False,

            "temporal_values_normalized":
                False,

            "unstated_chronology_inferred":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "similarity_reasoning_performed":
                False,

            "truth_assessment_performed":
                False,
        },

        "processing_boundaries":
            result_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "temporal_candidate_extraction",
    })

    return result


def extract_temporal_candidates_v1(
    temporal_signal_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Extract article-local Temporal candidates from certified Stage-E
    explicit Temporal signals.

    Stage F converts explicit signal evidence into provisional Temporal
    candidate objects.

    Overlapping/nested explicit signals are consolidated into one
    candidate-evidence bundle so lexical nesting does not manufacture
    duplicate Temporal candidates.

    This stage does NOT:
    - promote Stage-E ambiguous exclusions,
    - ground Temporal anchors or participants,
    - infer missing Temporal anchors,
    - determine before/after or other Temporal orientation,
    - normalize dates, ages, durations, or intervals,
    - validate point/duration/interval semantics,
    - validate sequence/boundary/recurrence semantics,
    - validate a Temporal relation,
    - perform same-sentence Temporal validation,
    - perform cross-sentence Temporal anchoring,
    - perform semantic duplicate resolution,
    - infer unstated chronology,
    - perform procedural reasoning,
    - perform quantitative reasoning,
    - perform new causal reasoning,
    - perform Analogical Intelligence,
    - perform new Similarity reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        temporal_signal_result,
        Mapping,
    ):
        raise TemporalIntelligenceError(
            "temporal_signal_result must be a mapping."
        )

    if (
        temporal_signal_result.get(
            "schema_version"
        )
        != "temporal_signal_interpretation_v1"
    ):
        raise TemporalIntelligenceError(
            "Stage F requires temporal_signal_interpretation_v1."
        )

    if (
        temporal_signal_result.get(
            "status"
        )
        != "TEMPORAL_SIGNAL_INTERPRETATION_COMPLETE"
    ):
        raise TemporalIntelligenceError(
            "Temporal signal interpretation must be complete before Stage F."
        )

    if (
        temporal_signal_result.get(
            "phase"
        )
        != "4.6.13"
    ):
        raise TemporalIntelligenceError(
            "Stage F requires Phase 4.6.13 input."
        )

    if (
        temporal_signal_result.get(
            "patch"
        )
        != "4.6.13E"
    ):
        raise TemporalIntelligenceError(
            "Stage F requires canonical 4.6.13E input."
        )

    if (
        temporal_signal_result.get(
            "next_stage"
        )
        != "temporal_candidate_extraction"
    ):
        raise TemporalIntelligenceError(
            "Stage E must hand off to temporal_candidate_extraction."
        )

    if (
        temporal_signal_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise TemporalIntelligenceError(
            "Temporal Intelligence must remain transient."
        )

    candidate_form_by_signal = {
        "BETWEEN_RANGE":
            "INTERVAL_CANDIDATE",

        "FROM_TO_RANGE":
            "INTERVAL_CANDIDATE",

        "AFTER":
            "SEQUENCE_CANDIDATE",

        "BEFORE":
            "SEQUENCE_CANDIDATE",

        "DURING":
            "CONTAINMENT_CANDIDATE",

        "SINCE":
            "START_BOUNDARY_CANDIDATE",

        "UNTIL":
            "END_BOUNDARY_CANDIDATE",

        "WITHIN":
            "BOUNDED_WINDOW_CANDIDATE",

        "BY_TIME":
            "UPPER_BOUND_CANDIDATE",

        "AT_AGE_TIME":
            "POINT_CANDIDATE",

        "AGE_UNDER":
            "AGE_BOUND_CANDIDATE",

        "UP_TO_AGE":
            "UPPER_BOUND_CANDIDATE",

        "AGE_RANGE":
            "INTERVAL_CANDIDATE",

        "AGE_POINT":
            "AGE_POINT_CANDIDATE",

        "BIRTH_ANCHOR":
            "ANCHOR_REFERENCE_CANDIDATE",

        "OVER_TIME":
            "TEMPORAL_PROGRESS_CANDIDATE",

        "OVER_PERIOD":
            "DURATION_CANDIDATE",

        "PER_TIME_UNIT":
            "RECURRENCE_CANDIDATE",

        "EACH_TIME_UNIT":
            "RECURRENCE_CANDIDATE",

        "LAST_EVENT_REFERENCE":
            "RELATIVE_REFERENCE_CANDIDATE",

        "FIRST_PERIOD":
            "TEMPORAL_PERIOD_CANDIDATE",
    }

    supported_signal_types = set(
        candidate_form_by_signal
    )

    def build_candidate_id(
        unit_id: str,
        primary_signal_type: str,
        candidate_text: str,
        start: int,
        end: int,
        ordinal: int,
    ) -> str:
        raw = "|".join([
            unit_id,
            primary_signal_type,
            candidate_text,
            str(
                start
            ),
            str(
                end
            ),
            str(
                ordinal
            ),
        ])

        return (
            "temporal_candidate_"
            + hashlib.sha256(
                raw.encode(
                    "utf-8"
                )
            ).hexdigest()[:24]
        )

    source_units = list(
        temporal_signal_result.get(
            "temporal_claim_units"
        )
        or []
    )

    extracted_units = []
    extracted_by_id = {}
    all_candidates = []

    seen_candidate_ids = set()

    units_with_candidates = 0
    rejected_signal_count = 0
    consolidated_nested_signal_count = 0

    candidate_form_counts = {}
    primary_signal_type_counts = {}
    contributing_signal_type_counts = {}

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Stage-E Temporal Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "temporal_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "temporal_signal_interpretation"
            )
            != "COMPLETE"
        ):
            raise TemporalIntelligenceError(
                "Temporal signal interpretation must "
                "be COMPLETE before Stage F."
            )

        if (
            state.get(
                "temporal_candidate_extraction"
            )
            != "PENDING"
        ):
            raise TemporalIntelligenceError(
                "Temporal candidate extraction must "
                "be PENDING before Stage F."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "temporal_signal_interpretation_performed"
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                "Stage-E Temporal interpretation boundary is incomplete."
            )

        required_false_boundaries = (
            "temporal_candidate_extraction_performed",
            "temporal_grounding_performed",
            "temporal_orientation_performed",
            "temporal_value_validation_performed",
            "temporal_relation_validation_performed",
            "same_sentence_temporal_validation_performed",
            "cross_sentence_temporal_anchoring_performed",
            "temporal_evidence_assessment_performed",
            "temporal_duplicate_resolution_performed",
            "unstated_temporal_relation_inference_performed",
            "unstated_temporal_anchor_inference_performed",
            "unstated_duration_inference_performed",
            "unstated_recurrence_inference_performed",
            "procedural_reasoning_performed",
            "quantitative_reasoning_performed",
            "new_causal_reasoning_performed",
            "analogical_reasoning_performed",
            "similarity_reasoning_performed",
            "truth_assessment_performed",
            "external_authority_check_performed",
            "semantic_memory_write_performed",
            "persistence_performed",
        )

        for boundary_name in required_false_boundaries:
            if (
                boundaries.get(
                    boundary_name
                )
                is not False
            ):
                raise TemporalIntelligenceError(
                    boundary_name
                    + " must be False before Stage F."
                )

        unit_id = str(
            unit.get(
                "temporal_claim_unit_id"
            )
            or ""
        )

        sentence_text = str(
            unit.get(
                "text"
            )
            or ""
        )

        if not unit_id:
            raise TemporalIntelligenceError(
                "Temporal Claim Unit ID is required."
            )

        signals = list(
            unit.get(
                "temporal_signals"
            )
            or []
        )

        exclusions = list(
            unit.get(
                "temporal_signal_exclusions"
            )
            or []
        )

        valid_signals = []
        unit_rejections = []

        for signal in signals:
            if not isinstance(
                signal,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Every Temporal signal must be a mapping."
                )

            signal_type = str(
                signal.get(
                    "signal_type"
                )
                or ""
            )

            matched_text = str(
                signal.get(
                    "matched_text"
                )
                or ""
            )

            start = signal.get(
                "character_start"
            )

            end = signal.get(
                "character_end"
            )

            if (
                not isinstance(
                    start,
                    int,
                )
                or not isinstance(
                    end,
                    int,
                )
                or start < 0
                or end <= start
                or end > len(
                    sentence_text
                )
            ):
                raise TemporalIntelligenceError(
                    "Temporal signal character span is invalid."
                )

            if (
                sentence_text[
                    start:end
                ]
                != matched_text
            ):
                raise TemporalIntelligenceError(
                    "Temporal signal text does not match its source span."
                )

            if signal_type not in supported_signal_types:
                unit_rejections.append({
                    "signal_type":
                        signal_type,

                    "matched_text":
                        matched_text,

                    "character_start":
                        start,

                    "character_end":
                        end,

                    "rejection_reason":
                        "UNSUPPORTED_TEMPORAL_SIGNAL_TYPE",

                    "candidate_created":
                        False,
                })

                rejected_signal_count += 1
                continue

            if not matched_text.strip():
                unit_rejections.append({
                    "signal_type":
                        signal_type,

                    "matched_text":
                        matched_text,

                    "character_start":
                        start,

                    "character_end":
                        end,

                    "rejection_reason":
                        "EMPTY_TEMPORAL_SIGNAL_TEXT",

                    "candidate_created":
                        False,
                })

                rejected_signal_count += 1
                continue

            if (
                signal.get(
                    "article_asserted_signal"
                )
                is not True
            ):
                raise TemporalIntelligenceError(
                    "Stage-F Temporal candidates require "
                    "article-asserted Stage-E signals."
                )

            if (
                signal.get(
                    "temporal_relation_validated"
                )
                is not False
            ):
                raise TemporalIntelligenceError(
                    "Temporal relation validation must not occur before Stage F."
                )

            if (
                signal.get(
                    "temporal_candidate_extracted"
                )
                is not False
            ):
                raise TemporalIntelligenceError(
                    "Temporal candidate must not already be extracted."
                )

            if (
                signal.get(
                    "temporal_anchor_grounded"
                )
                is not False
            ):
                raise TemporalIntelligenceError(
                    "Temporal anchor grounding must not occur before Stage F."
                )

            if (
                signal.get(
                    "temporal_orientation_determined"
                )
                is not False
            ):
                raise TemporalIntelligenceError(
                    "Temporal orientation must not occur before Stage F."
                )

            valid_signals.append(
                dict(
                    signal
                )
            )

        valid_signals.sort(
            key=lambda item: (
                int(
                    item.get(
                        "character_start"
                    )
                    or 0
                ),
                int(
                    item.get(
                        "character_end"
                    )
                    or 0
                ),
                str(
                    item.get(
                        "signal_type"
                    )
                    or ""
                ),
            )
        )

        temporal_operator_signal_types = {
            "AFTER",
            "BEFORE",
            "DURING",
            "SINCE",
            "UNTIL",
            "WITHIN",
        }

        temporal_anchor_value_signal_types = {
            "BETWEEN_RANGE",
            "FROM_TO_RANGE",
            "BY_TIME",
            "AT_AGE_TIME",
            "AGE_UNDER",
            "UP_TO_AGE",
            "AGE_RANGE",
            "AGE_POINT",
            "BIRTH_ANCHOR",
            "OVER_TIME",
            "OVER_PERIOD",
            "PER_TIME_UNIT",
            "EACH_TIME_UNIT",
            "LAST_EVENT_REFERENCE",
            "FIRST_PERIOD",
        }

        signal_groups = []

        for signal in valid_signals:
            signal_start = int(
                signal[
                    "character_start"
                ]
            )

            signal_end = int(
                signal[
                    "character_end"
                ]
            )

            overlapping_group = None

            for group in signal_groups:
                group_start = min(
                    int(
                        item[
                            "character_start"
                        ]
                    )
                    for item in group
                )

                group_end = max(
                    int(
                        item[
                            "character_end"
                        ]
                    )
                    for item in group
                )

                overlaps_group = (
                    signal_start < group_end
                    and signal_end > group_start
                )

                current_signal_type = str(
                    signal.get(
                        "signal_type"
                    )
                    or ""
                )

                group_signal_types = {
                    str(
                        item.get(
                            "signal_type"
                        )
                        or ""
                    )
                    for item in group
                }

                adjacent_whitespace_only = (
                    group_end <= signal_start
                    and sentence_text[
                        group_end:
                        signal_start
                    ].strip()
                    == ""
                )

                operator_anchor_adjacency = (
                    adjacent_whitespace_only
                    and (
                        (
                            current_signal_type
                            in temporal_anchor_value_signal_types
                            and any(
                                existing_type
                                in temporal_operator_signal_types
                                for existing_type
                                in group_signal_types
                            )
                        )
                        or
                        (
                            current_signal_type
                            in temporal_operator_signal_types
                            and any(
                                existing_type
                                in temporal_anchor_value_signal_types
                                for existing_type
                                in group_signal_types
                            )
                        )
                    )
                )

                if (
                    overlaps_group
                    or operator_anchor_adjacency
                ):
                    overlapping_group = group
                    break

            if overlapping_group is None:
                signal_groups.append([
                    signal
                ])
            else:
                overlapping_group.append(
                    signal
                )

        unit_candidates = []

        for candidate_ordinal, group in enumerate(
            signal_groups,
            start=1,
        ):
            group = sorted(
                group,
                key=lambda item: (
                    -(
                        int(
                            item[
                                "character_end"
                            ]
                        )
                        - int(
                            item[
                                "character_start"
                            ]
                        )
                    ),
                    int(
                        item[
                            "character_start"
                        ]
                    ),
                    str(
                        item[
                            "signal_type"
                        ]
                    ),
                ),
            )

            primary_signal = group[0]

            group_operator_signals = [
                item
                for item in group
                if str(
                    item.get(
                        "signal_type"
                    )
                    or ""
                )
                in temporal_operator_signal_types
            ]

            group_anchor_value_signals = [
                item
                for item in group
                if str(
                    item.get(
                        "signal_type"
                    )
                    or ""
                )
                in temporal_anchor_value_signal_types
            ]

            if (
                len(
                    group_operator_signals
                )
                == 1
                and group_anchor_value_signals
            ):
                primary_signal = (
                    group_operator_signals[0]
                )

            primary_signal_type = str(
                primary_signal[
                    "signal_type"
                ]
            )

            group_start = min(
                int(
                    item[
                        "character_start"
                    ]
                )
                for item in group
            )

            group_end = max(
                int(
                    item[
                        "character_end"
                    ]
                )
                for item in group
            )

            candidate_text = sentence_text[
                group_start:
                group_end
            ]

            candidate_form = (
                candidate_form_by_signal[
                    primary_signal_type
                ]
            )

            candidate_id = build_candidate_id(
                unit_id,
                primary_signal_type,
                candidate_text,
                group_start,
                group_end,
                candidate_ordinal,
            )

            if candidate_id in seen_candidate_ids:
                raise TemporalIntelligenceError(
                    "Duplicate Temporal Candidate ID."
                )

            contributing_signals = [
                {
                    "signal_type":
                        str(
                            item.get(
                                "signal_type"
                            )
                            or ""
                        ),

                    "temporal_semantic_class":
                        item.get(
                            "temporal_semantic_class"
                        ),

                    "matched_text":
                        item.get(
                            "matched_text"
                        ),

                    "character_start":
                        item.get(
                            "character_start"
                        ),

                    "character_end":
                        item.get(
                            "character_end"
                        ),
                }
                for item in sorted(
                    group,
                    key=lambda item: (
                        int(
                            item.get(
                                "character_start"
                            )
                            or 0
                        ),
                        int(
                            item.get(
                                "character_end"
                            )
                            or 0
                        ),
                        str(
                            item.get(
                                "signal_type"
                            )
                            or ""
                        ),
                    ),
                )
            ]

            if len(
                contributing_signals
            ) > 1:
                consolidated_nested_signal_count += (
                    len(
                        contributing_signals
                    )
                    - 1
                )

            candidate = {
                "temporal_candidate_id":
                    candidate_id,

                "temporal_claim_unit_id":
                    unit_id,

                "upstream_similarity_claim_unit_id":
                    unit.get(
                        "upstream_similarity_claim_unit_id"
                    ),

                "upstream_analogical_claim_unit_id":
                    unit.get(
                        "upstream_analogical_claim_unit_id"
                    ),

                "upstream_procedural_claim_unit_id":
                    unit.get(
                        "upstream_procedural_claim_unit_id"
                    ),

                "upstream_quantitative_claim_unit_id":
                    unit.get(
                        "upstream_quantitative_claim_unit_id"
                    ),

                "upstream_causal_claim_unit_id":
                    unit.get(
                        "upstream_causal_claim_unit_id"
                    ),

                "upstream_relational_claim_unit_id":
                    unit.get(
                        "upstream_relational_claim_unit_id"
                    ),

                "upstream_logical_claim_unit_id":
                    unit.get(
                        "upstream_logical_claim_unit_id"
                    ),

                "statement_evidence_id":
                    unit.get(
                        "statement_evidence_id"
                    ),

                "sentence_id":
                    unit.get(
                        "sentence_id"
                    ),

                "article_id":
                    unit.get(
                        "article_id"
                    ),

                "section_id":
                    unit.get(
                        "section_id"
                    ),

                "section_index":
                    unit.get(
                        "section_index"
                    ),

                "section_evidence_unit_id":
                    unit.get(
                        "section_evidence_unit_id"
                    ),

                "block_id":
                    unit.get(
                        "block_id"
                    ),

                "paragraph_id":
                    unit.get(
                        "paragraph_id"
                    ),

                "sentence_global_index":
                    unit.get(
                        "sentence_global_index"
                    ),

                "article_position":
                    unit.get(
                        "article_position"
                    ),

                "source_text":
                    sentence_text,

                "candidate_text":
                    candidate_text,

                "candidate_character_start":
                    group_start,

                "candidate_character_end":
                    group_end,

                "primary_signal_type":
                    primary_signal_type,

                "primary_temporal_semantic_class":
                    primary_signal.get(
                        "temporal_semantic_class"
                    ),

                "primary_signal_matched_text":
                    primary_signal.get(
                        "matched_text"
                    ),

                "primary_signal_character_start":
                    primary_signal.get(
                        "character_start"
                    ),

                "primary_signal_character_end":
                    primary_signal.get(
                        "character_end"
                    ),

                "candidate_temporal_form":
                    candidate_form,

                "contributing_signal_count":
                    len(
                        contributing_signals
                    ),

                "contributing_signals":
                    contributing_signals,

                "nested_signal_evidence_consolidated":
                    (
                        len(
                            contributing_signals
                        )
                        > 1
                    ),

                "article_asserted_candidate":
                    True,

                "same_sentence_candidate":
                    True,

                "temporal_anchor_grounding_performed":
                    False,

                "temporal_anchor_selected":
                    False,

                "selected_temporal_anchor":
                    None,

                "temporal_participant_grounding_performed":
                    False,

                "temporal_participant_selected":
                    False,

                "selected_temporal_participant":
                    None,

                "temporal_orientation_determined":
                    False,

                "temporal_orientation":
                    None,

                "temporal_value_validation_performed":
                    False,

                "temporal_value_type":
                    None,

                "normalized_temporal_value":
                    None,

                "temporal_relation_validated":
                    False,

                "same_sentence_temporal_validated":
                    False,

                "cross_sentence_temporal_anchor_resolved":
                    False,

                "temporal_evidence_assessed":
                    False,

                "semantic_duplicate_resolution_performed":
                    False,

                "unstated_temporal_relation_inference_performed":
                    False,

                "unstated_temporal_anchor_inference_performed":
                    False,

                "unstated_duration_inference_performed":
                    False,

                "unstated_recurrence_inference_performed":
                    False,

                "procedural_reasoning_performed":
                    False,

                "quantitative_reasoning_performed":
                    False,

                "new_causal_reasoning_performed":
                    False,

                "analogical_reasoning_performed":
                    False,

                "similarity_reasoning_performed":
                    False,

                "truth_assessed":
                    False,

                "external_authority_checked":
                    False,
            }

            unit_candidates.append(
                candidate
            )

            all_candidates.append(
                candidate
            )

            seen_candidate_ids.add(
                candidate_id
            )

            candidate_form_counts[
                candidate_form
            ] = (
                candidate_form_counts.get(
                    candidate_form,
                    0,
                )
                + 1
            )

            primary_signal_type_counts[
                primary_signal_type
            ] = (
                primary_signal_type_counts.get(
                    primary_signal_type,
                    0,
                )
                + 1
            )

            for contributing_signal in contributing_signals:
                contributing_type = str(
                    contributing_signal.get(
                        "signal_type"
                    )
                    or ""
                )

                contributing_signal_type_counts[
                    contributing_type
                ] = (
                    contributing_signal_type_counts.get(
                        contributing_type,
                        0,
                    )
                    + 1
                )

        if unit_candidates:
            units_with_candidates += 1

        extracted_state = dict(
            state
        )

        extracted_state[
            "temporal_candidate_extraction"
        ] = "COMPLETE"

        extracted_boundaries = dict(
            boundaries
        )

        extracted_boundaries[
            "temporal_candidate_extraction_performed"
        ] = True

        extracted_boundaries[
            "temporal_grounding_performed"
        ] = False

        extracted_boundaries[
            "temporal_orientation_performed"
        ] = False

        extracted_boundaries[
            "temporal_value_validation_performed"
        ] = False

        extracted_boundaries[
            "temporal_relation_validation_performed"
        ] = False

        extracted_boundaries[
            "same_sentence_temporal_validation_performed"
        ] = False

        extracted_boundaries[
            "cross_sentence_temporal_anchoring_performed"
        ] = False

        extracted_boundaries[
            "temporal_evidence_assessment_performed"
        ] = False

        extracted_boundaries[
            "temporal_duplicate_resolution_performed"
        ] = False

        extracted_boundaries[
            "unstated_temporal_relation_inference_performed"
        ] = False

        extracted_boundaries[
            "unstated_temporal_anchor_inference_performed"
        ] = False

        extracted_boundaries[
            "unstated_duration_inference_performed"
        ] = False

        extracted_boundaries[
            "unstated_recurrence_inference_performed"
        ] = False

        extracted_boundaries[
            "procedural_reasoning_performed"
        ] = False

        extracted_boundaries[
            "quantitative_reasoning_performed"
        ] = False

        extracted_boundaries[
            "new_causal_reasoning_performed"
        ] = False

        extracted_boundaries[
            "analogical_reasoning_performed"
        ] = False

        extracted_boundaries[
            "similarity_reasoning_performed"
        ] = False

        extracted_boundaries[
            "truth_assessment_performed"
        ] = False

        extracted_boundaries[
            "external_authority_check_performed"
        ] = False

        extracted_unit = dict(
            unit
        )

        extracted_unit.update({
            "temporal_candidates":
                unit_candidates,

            "temporal_candidate_count":
                len(
                    unit_candidates
                ),

            "temporal_extraction_rejections":
                unit_rejections,

            "temporal_extraction_rejection_count":
                len(
                    unit_rejections
                ),

            "temporal_signal_exclusions":
                exclusions,

            "temporal_analysis_state":
                extracted_state,

            "processing_boundaries":
                extracted_boundaries,
        })

        extracted_units.append(
            extracted_unit
        )

        if unit_id in extracted_by_id:
            raise TemporalIntelligenceError(
                "Duplicate extracted Temporal Claim Unit ID."
            )

        extracted_by_id[
            unit_id
        ] = extracted_unit

    extracted_sections = []

    for section in (
        temporal_signal_result.get(
            "temporal_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "temporal_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Every section Temporal Claim Unit "
                    "reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "temporal_claim_unit_id"
                )
                or ""
            )

            resolved_unit = extracted_by_id.get(
                unit_id
            )

            if resolved_unit is None:
                raise TemporalIntelligenceError(
                    "Temporal section references "
                    "an unknown claim unit."
                )

            section_units.append(
                resolved_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "temporal_candidates"
                )
                or []
            )
        ]

        extracted_sections.append({
            **dict(
                section
            ),

            "temporal_claim_units":
                section_units,

            "temporal_candidate_count":
                len(
                    section_candidates
                ),

            "temporal_candidates":
                section_candidates,
        })

    result = dict(
        temporal_signal_result
    )

    result_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    result_boundaries[
        "temporal_candidate_extraction_performed"
    ] = True

    result_boundaries[
        "temporal_grounding_performed"
    ] = False

    result_boundaries[
        "temporal_orientation_performed"
    ] = False

    result_boundaries[
        "temporal_value_validation_performed"
    ] = False

    result_boundaries[
        "temporal_relation_validation_performed"
    ] = False

    result_boundaries[
        "same_sentence_temporal_validation_performed"
    ] = False

    result_boundaries[
        "cross_sentence_temporal_anchoring_performed"
    ] = False

    result_boundaries[
        "temporal_evidence_assessment_performed"
    ] = False

    result_boundaries[
        "temporal_duplicate_resolution_performed"
    ] = False

    result_boundaries[
        "unstated_temporal_relation_inference_performed"
    ] = False

    result_boundaries[
        "unstated_temporal_anchor_inference_performed"
    ] = False

    result_boundaries[
        "unstated_duration_inference_performed"
    ] = False

    result_boundaries[
        "unstated_recurrence_inference_performed"
    ] = False

    result_boundaries[
        "procedural_reasoning_performed"
    ] = False

    result_boundaries[
        "quantitative_reasoning_performed"
    ] = False

    result_boundaries[
        "new_causal_reasoning_performed"
    ] = False

    result_boundaries[
        "analogical_reasoning_performed"
    ] = False

    result_boundaries[
        "similarity_reasoning_performed"
    ] = False

    result_boundaries[
        "truth_assessment_performed"
    ] = False

    result_boundaries[
        "external_authority_check_performed"
    ] = False

    result.update({
        "schema_version":
            "temporal_candidates_v1",

        "patch":
            "4.6.13F",

        "status":
            "TEMPORAL_CANDIDATE_EXTRACTION_COMPLETE",

        "temporal_sections":
            extracted_sections,

        "temporal_claim_units":
            extracted_units,

        "temporal_candidates":
            all_candidates,

        "temporal_extraction_summary": {
            "claim_unit_count":
                len(
                    extracted_units
                ),

            "units_with_candidates":
                units_with_candidates,

            "candidate_count":
                len(
                    all_candidates
                ),

            "rejected_signal_count":
                rejected_signal_count,

            "consolidated_nested_signal_count":
                consolidated_nested_signal_count,

            "supported_signal_types":
                sorted(
                    supported_signal_types
                ),

            "candidate_form_counts":
                dict(
                    sorted(
                        candidate_form_counts.items()
                    )
                ),

            "primary_signal_type_counts":
                dict(
                    sorted(
                        primary_signal_type_counts.items()
                    )
                ),

            "contributing_signal_type_counts":
                dict(
                    sorted(
                        contributing_signal_type_counts.items()
                    )
                ),

            "zero_candidates_allowed":
                True,

            "same_sentence_extraction_only":
                True,

            "ambiguous_stage_e_exclusions_not_promoted":
                True,

            "nested_signal_evidence_consolidated":
                True,

            "semantic_duplicate_resolution_performed":
                False,

            "temporal_anchor_grounding_performed":
                False,

            "temporal_orientation_performed":
                False,

            "temporal_value_validation_performed":
                False,

            "temporal_relation_validation_performed":
                False,

            "cross_sentence_temporal_anchoring_performed":
                False,

            "unstated_temporal_relation_inference_performed":
                False,

            "unstated_temporal_anchor_inference_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "similarity_reasoning_performed":
                False,

            "truth_assessment_performed":
                False,
        },

        "processing_boundaries":
            result_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "temporal_anchor_participant_grounding",
    })

    return result


def ground_temporal_candidates_v1(
    temporal_candidates_result: Mapping[str, Any],
    entity_concept_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Ground Phase 4.6.13 Temporal candidates against explicit
    article-local Temporal anchor evidence and canonical Phase 4.6.2
    Entity & Concept Intelligence objects.

    Stage G:
    - preserves explicit Temporal anchor evidence already carried by
      each Stage-F candidate,
    - grounds candidate source sentences against canonical article-local
      entities/concepts,
    - records zero/single/multiple participant grounding matches.

    It does NOT:
    - invent a Temporal anchor,
    - infer an unstated participant,
    - select a final Temporal participant,
    - determine Temporal relation orientation,
    - normalize Temporal values,
    - validate point/duration/interval semantics,
    - validate sequence/boundary/recurrence semantics,
    - validate a Temporal relation,
    - perform cross-sentence Temporal anchoring,
    - create new entities or concepts,
    - perform fuzzy matching,
    - perform embedding similarity,
    - perform procedural reasoning,
    - perform quantitative reasoning,
    - perform new causal reasoning,
    - perform Analogical Intelligence,
    - perform new Similarity reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    import hashlib
    import re

    if not isinstance(
        temporal_candidates_result,
        Mapping,
    ):
        raise TemporalIntelligenceError(
            "temporal_candidates_result must be a mapping."
        )

    if not isinstance(
        entity_concept_result,
        Mapping,
    ):
        raise TemporalIntelligenceError(
            "entity_concept_result must be a mapping."
        )

    if (
        temporal_candidates_result.get(
            "schema_version"
        )
        != "temporal_candidates_v1"
    ):
        raise TemporalIntelligenceError(
            "Stage G requires temporal_candidates_v1."
        )

    if (
        temporal_candidates_result.get(
            "status"
        )
        != "TEMPORAL_CANDIDATE_EXTRACTION_COMPLETE"
    ):
        raise TemporalIntelligenceError(
            "Temporal candidate extraction must be complete."
        )

    if (
        temporal_candidates_result.get(
            "phase"
        )
        != "4.6.13"
    ):
        raise TemporalIntelligenceError(
            "Stage G requires Phase 4.6.13 input."
        )

    if (
        temporal_candidates_result.get(
            "patch"
        )
        != "4.6.13F"
    ):
        raise TemporalIntelligenceError(
            "Stage G requires canonical 4.6.13F input."
        )

    if (
        temporal_candidates_result.get(
            "next_stage"
        )
        != "temporal_anchor_participant_grounding"
    ):
        raise TemporalIntelligenceError(
            "Stage F must hand off to "
            "temporal_anchor_participant_grounding."
        )

    if (
        temporal_candidates_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise TemporalIntelligenceError(
            "Temporal Intelligence must remain transient."
        )

    if (
        entity_concept_result.get(
            "schema_version"
        )
        != "entity_concept_intelligence_result_v1"
    ):
        raise TemporalIntelligenceError(
            "Stage G requires canonical "
            "entity_concept_intelligence_result_v1."
        )

    if (
        entity_concept_result.get(
            "status"
        )
        != "ENTITY_CONCEPT_INTELLIGENCE_COMPLETE"
    ):
        raise TemporalIntelligenceError(
            "Entity & Concept Intelligence must be complete."
        )

    if (
        entity_concept_result.get(
            "phase"
        )
        != "4.6.2"
    ):
        raise TemporalIntelligenceError(
            "Stage G requires Phase 4.6.2 "
            "Entity & Concept Intelligence."
        )

    semantic_objects = list(
        entity_concept_result.get(
            "semantic_objects"
        )
        or []
    )

    if not semantic_objects:
        raise TemporalIntelligenceError(
            "Canonical semantic_objects are required for grounding."
        )

    entity_boundaries = dict(
        entity_concept_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        entity_boundaries.get(
            "article_local_only"
        )
        is not True
    ):
        raise TemporalIntelligenceError(
            "Entity & Concept Intelligence must be article-local."
        )

    if (
        entity_boundaries.get(
            "semantic_memory_write_performed"
        )
        is not False
    ):
        raise TemporalIntelligenceError(
            "Unexpected Semantic Memory write detected upstream."
        )

    if (
        entity_boundaries.get(
            "reasoning_performed"
        )
        is not False
    ):
        raise TemporalIntelligenceError(
            "Unexpected reasoning detected in Phase 4.6.2."
        )

    def normalize(
        value: str,
    ) -> str:
        value = str(
            value
            or ""
        ).lower()

        value = value.replace(
            "?",
            "'",
        )

        value = re.sub(
            r"[^a-z0-9']+",
            " ",
            value,
        )

        return re.sub(
            r"\s+",
            " ",
            value,
        ).strip()

    article_identity = dict(
        temporal_candidates_result.get(
            "article_identity"
        )
        or {}
    )

    article_id = str(
        article_identity.get(
            "article_id"
        )
        or ""
    )

    if not article_id:
        raise TemporalIntelligenceError(
            "Temporal article_id is required."
        )

    entity_identity = dict(
        entity_concept_result.get(
            "article_identity"
        )
        or {}
    )

    entity_article_id = str(
        entity_identity.get(
            "article_id"
        )
        or ""
    )

    if (
        entity_article_id
        and entity_article_id != article_id
    ):
        raise TemporalIntelligenceError(
            "Entity/Concept Intelligence article identity mismatch."
        )

    prepared_objects = []

    for semantic_object in semantic_objects:
        if not isinstance(
            semantic_object,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every semantic object must be a mapping."
            )

        canonical_text = str(
            semantic_object.get(
                "canonical_text"
            )
            or ""
        ).strip()

        semantic_kind = semantic_object.get(
            "semantic_kind"
        )

        confidence = semantic_object.get(
            "extraction_confidence"
        )

        if not canonical_text:
            raise TemporalIntelligenceError(
                "Semantic object is missing canonical_text."
            )

        if semantic_kind not in {
            "entity",
            "concept",
        }:
            raise TemporalIntelligenceError(
                "Semantic object has invalid semantic_kind."
            )

        if (
            not isinstance(
                confidence,
                (int, float),
            )
            or isinstance(
                confidence,
                bool,
            )
            or confidence < 0.0
            or confidence > 1.0
        ):
            raise TemporalIntelligenceError(
                "Semantic object has invalid extraction_confidence."
            )

        variants = {
            canonical_text,
        }

        for surface in (
            semantic_object.get(
                "surface_forms"
            )
            or []
        ):
            if (
                isinstance(
                    surface,
                    str,
                )
                and surface.strip()
            ):
                variants.add(
                    surface.strip()
                )

        normalized_variants = {
            normalize(
                variant
            ):
                variant
            for variant in variants
            if normalize(
                variant
            )
        }

        stable_material = (
            article_id
            + "|"
            + str(
                semantic_kind
            )
            + "|"
            + normalize(
                canonical_text
            )
        )

        grounding_ref = (
            "article_temporal_semantic_object_"
            + hashlib.sha256(
                stable_material.encode(
                    "utf-8"
                )
            ).hexdigest()[:16]
        )

        prepared_objects.append({
            "grounding_ref":
                grounding_ref,

            "semantic_object":
                semantic_object,

            "canonical_text":
                canonical_text,

            "semantic_kind":
                semantic_kind,

            "extraction_confidence":
                confidence,

            "normalized_variants":
                normalized_variants,
        })

    def collect_context_groundings(
        source_text: str,
    ) -> list[dict[str, Any]]:
        normalized_source = normalize(
            source_text
        )

        if not normalized_source:
            return []

        matches_by_ref = {}

        for prepared in prepared_objects:
            for (
                normalized_variant,
                original_variant,
            ) in prepared[
                "normalized_variants"
            ].items():

                if not normalized_variant:
                    continue

                bounded_pattern = (
                    r"(?<![a-z0-9'])"
                    + re.escape(
                        normalized_variant
                    )
                    + r"(?![a-z0-9'])"
                )

                match = re.search(
                    bounded_pattern,
                    normalized_source,
                )

                if match is None:
                    continue

                if (
                    normalized_source
                    == normalized_variant
                ):
                    strategy = (
                        "EXACT_CANONICAL_OR_SURFACE_MATCH"
                    )
                else:
                    strategy = (
                        "BOUNDED_CANONICAL_OR_SURFACE_MATCH"
                    )

                candidate_match = {
                    "grounding_ref":
                        prepared[
                            "grounding_ref"
                        ],

                    "canonical_text":
                        prepared[
                            "canonical_text"
                        ],

                    "semantic_kind":
                        prepared[
                            "semantic_kind"
                        ],

                    "extraction_confidence":
                        prepared[
                            "extraction_confidence"
                        ],

                    "matched_surface_form":
                        original_variant,

                    "normalized_match":
                        normalized_variant,

                    "match_strategy":
                        strategy,

                    "match_token_count":
                        len(
                            normalized_variant.split()
                        ),

                    "temporal_participant_selected":
                        False,

                    "temporal_anchor_selected":
                        False,

                    "temporal_relation_orientation_resolved":
                        False,
                }

                existing = matches_by_ref.get(
                    prepared[
                        "grounding_ref"
                    ]
                )

                if existing is None:
                    matches_by_ref[
                        prepared[
                            "grounding_ref"
                        ]
                    ] = candidate_match
                    continue

                existing_rank = (
                    0
                    if existing[
                        "match_strategy"
                    ]
                    == "EXACT_CANONICAL_OR_SURFACE_MATCH"
                    else 1,

                    -existing[
                        "match_token_count"
                    ],

                    -existing[
                        "extraction_confidence"
                    ],
                )

                candidate_rank = (
                    0
                    if strategy
                    == "EXACT_CANONICAL_OR_SURFACE_MATCH"
                    else 1,

                    -candidate_match[
                        "match_token_count"
                    ],

                    -candidate_match[
                        "extraction_confidence"
                    ],
                )

                if candidate_rank < existing_rank:
                    matches_by_ref[
                        prepared[
                            "grounding_ref"
                        ]
                    ] = candidate_match

        matches = list(
            matches_by_ref.values()
        )

        matches.sort(
            key=lambda item: (
                0
                if item[
                    "match_strategy"
                ]
                == "EXACT_CANONICAL_OR_SURFACE_MATCH"
                else 1,

                -item[
                    "match_token_count"
                ],

                -item[
                    "extraction_confidence"
                ],

                item[
                    "canonical_text"
                ],
            )
        )

        return matches

    temporal_anchor_value_signal_types = {
        "BETWEEN_RANGE",
        "FROM_TO_RANGE",
        "BY_TIME",
        "AT_AGE_TIME",
        "AGE_UNDER",
        "UP_TO_AGE",
        "AGE_RANGE",
        "AGE_POINT",
        "BIRTH_ANCHOR",
        "OVER_TIME",
        "OVER_PERIOD",
        "PER_TIME_UNIT",
        "EACH_TIME_UNIT",
        "LAST_EVENT_REFERENCE",
        "FIRST_PERIOD",
    }

    source_candidates = list(
        temporal_candidates_result.get(
            "temporal_candidates"
        )
        or []
    )

    grounded_candidates = []
    grounded_by_id = {}
    seen_candidate_ids = set()

    grounded_count = 0
    single_match_count = 0
    multiple_match_count = 0
    ungrounded_count = 0
    total_grounding_matches = 0
    explicit_anchor_count = 0

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "temporal_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise TemporalIntelligenceError(
                "Temporal candidate ID is required."
            )

        if candidate_id in seen_candidate_ids:
            raise TemporalIntelligenceError(
                "Duplicate Temporal Candidate ID."
            )

        seen_candidate_ids.add(
            candidate_id
        )

        if (
            candidate.get(
                "temporal_anchor_grounding_performed"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Candidate must not already be Temporal-anchor grounded."
            )

        if (
            candidate.get(
                "temporal_participant_grounding_performed"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Candidate must not already be participant grounded."
            )

        if (
            candidate.get(
                "temporal_orientation_determined"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Temporal orientation must not occur before Stage G."
            )

        source_text = str(
            candidate.get(
                "source_text"
            )
            or ""
        )

        candidate_text = str(
            candidate.get(
                "candidate_text"
            )
            or ""
        )

        candidate_start = candidate.get(
            "candidate_character_start"
        )

        candidate_end = candidate.get(
            "candidate_character_end"
        )

        if (
            not isinstance(
                candidate_start,
                int,
            )
            or not isinstance(
                candidate_end,
                int,
            )
            or candidate_start < 0
            or candidate_end <= candidate_start
            or candidate_end > len(
                source_text
            )
        ):
            raise TemporalIntelligenceError(
                "Temporal candidate span is invalid."
            )

        if (
            source_text[
                candidate_start:
                candidate_end
            ]
            != candidate_text
        ):
            raise TemporalIntelligenceError(
                "Temporal candidate text does not match source span."
            )

        contributing_signals = list(
            candidate.get(
                "contributing_signals"
            )
            or []
        )

        if not contributing_signals:
            raise TemporalIntelligenceError(
                "Temporal candidate requires explicit contributing signals."
            )

        anchor_evidence = []

        seen_anchor_keys = set()

        for signal in contributing_signals:
            if not isinstance(
                signal,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Every contributing Temporal signal must be a mapping."
                )

            signal_type = str(
                signal.get(
                    "signal_type"
                )
                or ""
            )

            matched_text = str(
                signal.get(
                    "matched_text"
                )
                or ""
            )

            start = signal.get(
                "character_start"
            )

            end = signal.get(
                "character_end"
            )

            if (
                not signal_type
                or not matched_text
                or not isinstance(
                    start,
                    int,
                )
                or not isinstance(
                    end,
                    int,
                )
                or start < 0
                or end <= start
                or end > len(
                    source_text
                )
            ):
                raise TemporalIntelligenceError(
                    "Contributing Temporal signal is malformed."
                )

            if (
                source_text[
                    start:end
                ]
                != matched_text
            ):
                raise TemporalIntelligenceError(
                    "Contributing Temporal signal does not match source span."
                )

            if (
                signal_type
                not in temporal_anchor_value_signal_types
            ):
                continue

            key = (
                signal_type,
                start,
                end,
                matched_text,
            )

            if key in seen_anchor_keys:
                continue

            seen_anchor_keys.add(
                key
            )

            anchor_evidence.append({
                "signal_type":
                    signal_type,

                "temporal_semantic_class":
                    signal.get(
                        "temporal_semantic_class"
                    ),

                "anchor_text":
                    matched_text,

                "character_start":
                    start,

                "character_end":
                    end,

                "explicit_article_evidence":
                    True,

                "anchor_inference_performed":
                    False,

                "temporal_value_normalized":
                    False,

                "temporal_relation_validated":
                    False,
            })

        anchor_evidence.sort(
            key=lambda item: (
                item[
                    "character_start"
                ],
                item[
                    "character_end"
                ],
                item[
                    "signal_type"
                ],
            )
        )

        anchor_evidence_count = len(
            anchor_evidence
        )

        if anchor_evidence_count == 0:
            anchor_status = (
                "NO_EXPLICIT_TEMPORAL_ANCHOR_EVIDENCE"
            )
        elif anchor_evidence_count == 1:
            anchor_status = (
                "EXPLICIT_TEMPORAL_ANCHOR_SINGLE_EVIDENCE"
            )
        else:
            anchor_status = (
                "EXPLICIT_TEMPORAL_ANCHOR_MULTIPLE_EVIDENCE"
            )

        participant_matches = (
            collect_context_groundings(
                source_text
            )
        )

        participant_match_count = len(
            participant_matches
        )

        if participant_match_count == 0:
            participant_status = (
                "UNGROUNDED"
            )
            ungrounded_count += 1

        elif participant_match_count == 1:
            participant_status = (
                "GROUNDED_SINGLE_MATCH"
            )
            grounded_count += 1
            single_match_count += 1

        else:
            participant_status = (
                "GROUNDED_MULTIPLE_MATCHES"
            )
            grounded_count += 1
            multiple_match_count += 1

        total_grounding_matches += (
            participant_match_count
        )

        if anchor_evidence_count > 0:
            explicit_anchor_count += 1

        grounded_candidate = dict(
            candidate
        )

        grounded_candidate.update({
            "temporal_anchor_grounding_evidence":
                anchor_evidence,

            "temporal_anchor_grounding_evidence_count":
                anchor_evidence_count,

            "temporal_anchor_grounding_status":
                anchor_status,

            "temporal_anchor_explicitly_grounded":
                anchor_evidence_count > 0,

            "temporal_anchor_grounding_performed":
                True,

            "temporal_anchor_selected":
                False,

            "selected_temporal_anchor":
                None,

            "temporal_participant_grounding_matches":
                participant_matches,

            "temporal_participant_grounding_match_count":
                participant_match_count,

            "temporal_participant_grounding_status":
                participant_status,

            "temporal_participant_grounded":
                participant_match_count > 0,

            "temporal_participant_grounding_performed":
                True,

            "temporal_participant_selection_performed":
                False,

            "temporal_participant_selected":
                False,

            "selected_temporal_participant":
                None,

            "temporal_orientation_determined":
                False,

            "temporal_orientation":
                None,

            "temporal_value_validation_performed":
                False,

            "temporal_relation_validated":
                False,

            "same_sentence_temporal_validated":
                False,

            "cross_sentence_temporal_anchor_resolved":
                False,

            "temporal_evidence_assessed":
                False,

            "semantic_duplicate_resolution_performed":
                False,

            "unstated_temporal_relation_inference_performed":
                False,

            "unstated_temporal_anchor_inference_performed":
                False,

            "unstated_duration_inference_performed":
                False,

            "unstated_recurrence_inference_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "similarity_reasoning_performed":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,
        })

        grounded_candidates.append(
            grounded_candidate
        )

        grounded_by_id[
            candidate_id
        ] = grounded_candidate

    grounded_units = []
    grounded_unit_by_id = {}

    for unit in (
        temporal_candidates_result.get(
            "temporal_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "temporal_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise TemporalIntelligenceError(
                "Temporal Claim Unit ID is required."
            )

        if unit_id in grounded_unit_by_id:
            raise TemporalIntelligenceError(
                "Duplicate Temporal Claim Unit ID."
            )

        state = dict(
            unit.get(
                "temporal_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "temporal_candidate_extraction"
            )
            != "COMPLETE"
        ):
            raise TemporalIntelligenceError(
                "Temporal candidate extraction must "
                "be COMPLETE before grounding."
            )

        if (
            state.get(
                "temporal_anchor_participant_grounding"
            )
            != "PENDING"
        ):
            raise TemporalIntelligenceError(
                "Temporal anchor/participant grounding must be PENDING."
            )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "temporal_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Every unit Temporal Candidate reference "
                    "must be a mapping."
                )

            candidate_id = str(
                old_candidate.get(
                    "temporal_candidate_id"
                )
                or ""
            )

            grounded = grounded_by_id.get(
                candidate_id
            )

            if grounded is None:
                raise TemporalIntelligenceError(
                    "Temporal candidate/unit identity mismatch."
                )

            unit_candidates.append(
                grounded
            )

        updated_state = dict(
            state
        )

        updated_state[
            "temporal_anchor_participant_grounding"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            updated_boundaries.get(
                "temporal_candidate_extraction_performed"
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                "Stage-F extraction boundary is incomplete."
            )

        required_false_boundaries = (
            "temporal_grounding_performed",
            "temporal_orientation_performed",
            "temporal_value_validation_performed",
            "temporal_relation_validation_performed",
            "same_sentence_temporal_validation_performed",
            "cross_sentence_temporal_anchoring_performed",
            "temporal_evidence_assessment_performed",
            "temporal_duplicate_resolution_performed",
            "unstated_temporal_relation_inference_performed",
            "unstated_temporal_anchor_inference_performed",
            "unstated_duration_inference_performed",
            "unstated_recurrence_inference_performed",
            "procedural_reasoning_performed",
            "quantitative_reasoning_performed",
            "new_causal_reasoning_performed",
            "analogical_reasoning_performed",
            "similarity_reasoning_performed",
            "truth_assessment_performed",
            "external_authority_check_performed",
            "semantic_memory_write_performed",
            "persistence_performed",
        )

        for boundary_name in required_false_boundaries:
            if (
                updated_boundaries.get(
                    boundary_name
                )
                is not False
            ):
                raise TemporalIntelligenceError(
                    boundary_name
                    + " must be False before Stage G."
                )

        updated_boundaries[
            "temporal_grounding_performed"
        ] = True

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "temporal_candidates":
                unit_candidates,

            "temporal_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        grounded_units.append(
            updated_unit
        )

        grounded_unit_by_id[
            unit_id
        ] = updated_unit

    grounded_sections = []

    for section in (
        temporal_candidates_result.get(
            "temporal_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "temporal_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Every section Temporal Claim Unit "
                    "reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "temporal_claim_unit_id"
                )
                or ""
            )

            grounded_unit = (
                grounded_unit_by_id.get(
                    unit_id
                )
            )

            if grounded_unit is None:
                raise TemporalIntelligenceError(
                    "Temporal section references "
                    "an unknown grounded claim unit."
                )

            section_units.append(
                grounded_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "temporal_candidates"
                )
                or []
            )
        ]

        grounded_sections.append({
            **dict(
                section
            ),

            "temporal_claim_units":
                section_units,

            "temporal_candidates":
                section_candidates,

            "temporal_candidate_count":
                len(
                    section_candidates
                ),

            "explicit_anchor_grounded_candidate_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "temporal_anchor_explicitly_grounded"
                    )
                    is True
                ),

            "participant_grounded_candidate_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "temporal_participant_grounded"
                    )
                    is True
                ),
        })

    result = dict(
        temporal_candidates_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        boundaries.get(
            "temporal_candidate_extraction_performed"
        )
        is not True
    ):
        raise TemporalIntelligenceError(
            "Top-level Stage-F extraction boundary is incomplete."
        )

    required_false_boundaries = (
        "temporal_grounding_performed",
        "temporal_orientation_performed",
        "temporal_value_validation_performed",
        "temporal_relation_validation_performed",
        "same_sentence_temporal_validation_performed",
        "cross_sentence_temporal_anchoring_performed",
        "temporal_evidence_assessment_performed",
        "temporal_duplicate_resolution_performed",
        "unstated_temporal_relation_inference_performed",
        "unstated_temporal_anchor_inference_performed",
        "unstated_duration_inference_performed",
        "unstated_recurrence_inference_performed",
        "procedural_reasoning_performed",
        "quantitative_reasoning_performed",
        "new_causal_reasoning_performed",
        "analogical_reasoning_performed",
        "similarity_reasoning_performed",
        "truth_assessment_performed",
        "external_authority_check_performed",
        "semantic_memory_write_performed",
        "persistence_performed",
    )

    for boundary_name in required_false_boundaries:
        if (
            boundaries.get(
                boundary_name
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                boundary_name
                + " must be False before Stage G."
            )

    boundaries[
        "temporal_grounding_performed"
    ] = True

    result.update({
        "schema_version":
            "temporal_anchor_participant_grounding_v1",

        "patch":
            "4.6.13G",

        "status":
            "TEMPORAL_ANCHOR_PARTICIPANT_GROUNDING_COMPLETE",

        "temporal_sections":
            grounded_sections,

        "temporal_claim_units":
            grounded_units,

        "temporal_candidates":
            grounded_candidates,

        "temporal_grounding_summary": {
            "semantic_object_count":
                len(
                    semantic_objects
                ),

            "temporal_candidate_count":
                len(
                    grounded_candidates
                ),

            "explicit_anchor_grounded_candidate_count":
                explicit_anchor_count,

            "participant_grounded_candidate_count":
                grounded_count,

            "single_match_participant_candidate_count":
                single_match_count,

            "multiple_match_participant_candidate_count":
                multiple_match_count,

            "ungrounded_participant_candidate_count":
                ungrounded_count,

            "total_participant_grounding_match_count":
                total_grounding_matches,

            "candidate_count_accounted_for":
                (
                    grounded_count
                    + ungrounded_count
                    == len(
                        grounded_candidates
                    )
                ),

            "canonical_entity_concept_objects_reused":
                True,

            "new_entity_concept_objects_created":
                False,

            "exact_or_bounded_surface_matching_only":
                True,

            "explicit_temporal_anchor_evidence_only":
                True,

            "unstated_temporal_anchor_inference_performed":
                False,

            "temporal_participant_selection_performed":
                False,

            "temporal_anchor_selection_performed":
                False,

            "temporal_orientation_performed":
                False,

            "temporal_value_validation_performed":
                False,

            "temporal_relation_validation_performed":
                False,

            "cross_sentence_temporal_anchoring_performed":
                False,

            "fuzzy_matching_performed":
                False,

            "embedding_similarity_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "similarity_reasoning_performed":
                False,

            "truth_assessment_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "temporal_relation_orientation",
    })

    return result


def resolve_temporal_relation_orientation_v1(
    temporal_grounding_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Resolve the explicit article-local structural orientation of
    Phase 4.6.13 Temporal candidates.

    Stage H may:
    - interpret supported explicit Temporal operator/structure signals,
    - select one explicit Temporal anchor/reference when deterministically
      available from Stage-G anchor evidence,
    - select one article-local participant when exactly one canonical
      grounding exists,
    - resolve the structural Temporal orientation only when operator,
      anchor/reference, and participant evidence are sufficiently
      unambiguous.

    Stage H does NOT:
    - validate point/duration/interval values,
    - validate sequence/boundary/recurrence semantics,
    - validate the final Temporal relation,
    - perform same-sentence Temporal validation,
    - perform cross-sentence Temporal anchoring,
    - infer unstated anchors, dates, ages, durations, or recurrence,
    - guess between multiple participant groundings,
    - perform arithmetic,
    - perform procedural reasoning,
    - perform quantitative reasoning,
    - perform new causal reasoning,
    - perform Analogical or Similarity reasoning,
    - assess factual/scientific truth,
    - use external authority,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        temporal_grounding_result,
        Mapping,
    ):
        raise TemporalIntelligenceError(
            "temporal_grounding_result must be a mapping."
        )

    if (
        temporal_grounding_result.get(
            "schema_version"
        )
        != "temporal_anchor_participant_grounding_v1"
    ):
        raise TemporalIntelligenceError(
            "Stage H requires "
            "temporal_anchor_participant_grounding_v1."
        )

    if (
        temporal_grounding_result.get(
            "status"
        )
        != "TEMPORAL_ANCHOR_PARTICIPANT_GROUNDING_COMPLETE"
    ):
        raise TemporalIntelligenceError(
            "Temporal anchor/participant grounding must be complete."
        )

    if (
        temporal_grounding_result.get(
            "phase"
        )
        != "4.6.13"
    ):
        raise TemporalIntelligenceError(
            "Stage H requires Phase 4.6.13 input."
        )

    if (
        temporal_grounding_result.get(
            "patch"
        )
        != "4.6.13G"
    ):
        raise TemporalIntelligenceError(
            "Stage H requires canonical 4.6.13G input."
        )

    if (
        temporal_grounding_result.get(
            "next_stage"
        )
        != "temporal_relation_orientation"
    ):
        raise TemporalIntelligenceError(
            "Stage G must hand off to temporal_relation_orientation."
        )

    if (
        temporal_grounding_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise TemporalIntelligenceError(
            "Temporal Intelligence must remain transient."
        )

    orientation_class_by_signal = {
        "AFTER":
            "AFTER_ANCHOR",

        "BEFORE":
            "BEFORE_ANCHOR",

        "DURING":
            "DURING_ANCHOR",

        "SINCE":
            "SINCE_START_ANCHOR",

        "UNTIL":
            "UNTIL_END_ANCHOR",

        "WITHIN":
            "WITHIN_BOUNDED_WINDOW",

        "BY_TIME":
            "BY_UPPER_BOUND",

        "AT_AGE_TIME":
            "AT_TEMPORAL_POINT",

        "AGE_UNDER":
            "UNDER_AGE_BOUND",

        "UP_TO_AGE":
            "UP_TO_AGE_BOUND",

        "BETWEEN_RANGE":
            "NON_DIRECTIONAL_BETWEEN_INTERVAL",

        "FROM_TO_RANGE":
            "NON_DIRECTIONAL_FROM_TO_INTERVAL",

        "AGE_RANGE":
            "NON_DIRECTIONAL_AGE_INTERVAL",

        "AGE_POINT":
            "AT_AGE_POINT",

        "BIRTH_ANCHOR":
            "AT_BIRTH_REFERENCE",

        "OVER_TIME":
            "OVER_TIME_PROGRESSION",

        "OVER_PERIOD":
            "OVER_PERIOD_DURATION",

        "PER_TIME_UNIT":
            "RECURRENCE_PER_TIME_UNIT",

        "EACH_TIME_UNIT":
            "RECURRENCE_EACH_TIME_UNIT",

        "LAST_EVENT_REFERENCE":
            "RELATIVE_LAST_EVENT_REFERENCE",

        "FIRST_PERIOD":
            "FIRST_PERIOD_REFERENCE",
    }

    operator_priority = (
        "AFTER",
        "BEFORE",
        "SINCE",
        "UNTIL",
        "DURING",
        "WITHIN",
        "BY_TIME",
        "AT_AGE_TIME",
        "AGE_UNDER",
        "UP_TO_AGE",
        "BETWEEN_RANGE",
        "FROM_TO_RANGE",
        "AGE_RANGE",
        "AGE_POINT",
        "BIRTH_ANCHOR",
        "OVER_TIME",
        "OVER_PERIOD",
        "PER_TIME_UNIT",
        "EACH_TIME_UNIT",
        "LAST_EVENT_REFERENCE",
        "FIRST_PERIOD",
    )

    preferred_anchor_signal_types = (
        "BETWEEN_RANGE",
        "FROM_TO_RANGE",
        "AGE_RANGE",
        "AT_AGE_TIME",
        "BY_TIME",
        "AGE_UNDER",
        "UP_TO_AGE",
        "AGE_POINT",
        "BIRTH_ANCHOR",
        "OVER_PERIOD",
        "OVER_TIME",
        "PER_TIME_UNIT",
        "EACH_TIME_UNIT",
        "LAST_EVENT_REFERENCE",
        "FIRST_PERIOD",
    )

    source_candidates = list(
        temporal_grounding_result.get(
            "temporal_candidates"
        )
        or []
    )

    oriented_candidates = []
    oriented_by_id = {}
    seen_candidate_ids = set()

    resolved_count = 0
    unresolved_count = 0
    selected_participant_count = 0
    selected_anchor_count = 0
    orientation_class_counts = {}
    orientation_basis_counts = {}

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "temporal_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise TemporalIntelligenceError(
                "Temporal candidate ID is required."
            )

        if candidate_id in seen_candidate_ids:
            raise TemporalIntelligenceError(
                "Duplicate Temporal Candidate ID."
            )

        seen_candidate_ids.add(
            candidate_id
        )

        if (
            candidate.get(
                "temporal_anchor_grounding_performed"
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                "Candidate Temporal-anchor grounding must be complete."
            )

        if (
            candidate.get(
                "temporal_participant_grounding_performed"
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                "Candidate participant grounding must be complete."
            )

        if (
            candidate.get(
                "temporal_orientation_determined"
            )
            is not False
            or candidate.get(
                "temporal_orientation"
            )
            is not None
        ):
            raise TemporalIntelligenceError(
                "Candidate must not already have Temporal orientation."
            )

        if (
            candidate.get(
                "temporal_anchor_selected"
            )
            is not False
            or candidate.get(
                "selected_temporal_anchor"
            )
            is not None
        ):
            raise TemporalIntelligenceError(
                "Candidate must not already have Temporal-anchor selection."
            )

        if (
            candidate.get(
                "temporal_participant_selected"
            )
            is not False
            or candidate.get(
                "selected_temporal_participant"
            )
            is not None
        ):
            raise TemporalIntelligenceError(
                "Candidate must not already have participant selection."
            )

        contributing_signals = list(
            candidate.get(
                "contributing_signals"
            )
            or []
        )

        if not contributing_signals:
            raise TemporalIntelligenceError(
                "Temporal candidate requires contributing signals."
            )

        signal_types = []

        signal_by_type = {}

        for signal in contributing_signals:
            if not isinstance(
                signal,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Every contributing Temporal signal must be a mapping."
                )

            signal_type = str(
                signal.get(
                    "signal_type"
                )
                or ""
            )

            if not signal_type:
                raise TemporalIntelligenceError(
                    "Contributing Temporal signal type is required."
                )

            signal_types.append(
                signal_type
            )

            signal_by_type.setdefault(
                signal_type,
                signal,
            )

        orientation_signal_type = None

        primary_signal_type = str(
            candidate.get(
                "primary_signal_type"
            )
            or ""
        )

        if (
            primary_signal_type
            in orientation_class_by_signal
            and primary_signal_type
            in signal_types
        ):
            orientation_signal_type = (
                primary_signal_type
            )

        else:
            for signal_type in operator_priority:
                if signal_type in signal_types:
                    orientation_signal_type = (
                        signal_type
                    )
                    break

        orientation_class = (
            orientation_class_by_signal.get(
                orientation_signal_type
            )
            if orientation_signal_type
            else None
        )

        orientation_signal = (
            signal_by_type.get(
                orientation_signal_type
            )
            if orientation_signal_type
            else None
        )

        orientation_operator_text = (
            str(
                orientation_signal.get(
                    "matched_text"
                )
                or ""
            )
            if orientation_signal
            else None
        )

        anchor_evidence = list(
            candidate.get(
                "temporal_anchor_grounding_evidence"
            )
            or []
        )

        anchor_count = candidate.get(
            "temporal_anchor_grounding_evidence_count"
        )

        if (
            not isinstance(
                anchor_count,
                int,
            )
            or isinstance(
                anchor_count,
                bool,
            )
            or anchor_count < 0
        ):
            raise TemporalIntelligenceError(
                "Candidate has invalid Temporal anchor-evidence count."
            )

        if anchor_count != len(
            anchor_evidence
        ):
            raise TemporalIntelligenceError(
                "Temporal anchor-evidence count does not match evidence."
            )

        if (
            candidate.get(
                "temporal_anchor_explicitly_grounded"
            )
            is not (
                anchor_count > 0
            )
        ):
            raise TemporalIntelligenceError(
                "Temporal anchor-grounding flag is inconsistent."
            )

        for anchor in anchor_evidence:
            if not isinstance(
                anchor,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Every Temporal anchor evidence item must be a mapping."
                )

            if (
                anchor.get(
                    "explicit_article_evidence"
                )
                is not True
            ):
                raise TemporalIntelligenceError(
                    "Stage H accepts explicit article anchor evidence only."
                )

            if (
                anchor.get(
                    "anchor_inference_performed"
                )
                is not False
            ):
                raise TemporalIntelligenceError(
                    "Stage H refuses inferred Temporal anchors."
                )

            if (
                anchor.get(
                    "temporal_value_normalized"
                )
                is not False
            ):
                raise TemporalIntelligenceError(
                    "Temporal values must not be normalized before Stage H."
                )

            if (
                anchor.get(
                    "temporal_relation_validated"
                )
                is not False
            ):
                raise TemporalIntelligenceError(
                    "Temporal relation must not be validated before Stage H."
                )

        grounding_matches = list(
            candidate.get(
                "temporal_participant_grounding_matches"
            )
            or []
        )

        grounding_match_count = candidate.get(
            "temporal_participant_grounding_match_count"
        )

        if (
            not isinstance(
                grounding_match_count,
                int,
            )
            or isinstance(
                grounding_match_count,
                bool,
            )
            or grounding_match_count < 0
        ):
            raise TemporalIntelligenceError(
                "Candidate has invalid participant-grounding count."
            )

        if grounding_match_count != len(
            grounding_matches
        ):
            raise TemporalIntelligenceError(
                "Participant-grounding count does not match evidence."
            )

        if (
            candidate.get(
                "temporal_participant_grounded"
            )
            is not (
                grounding_match_count > 0
            )
        ):
            raise TemporalIntelligenceError(
                "Participant-grounding flag is inconsistent."
            )

        selected_anchor_candidate = None
        anchor_selection_basis = None

        if anchor_count == 1:
            selected_anchor_candidate = dict(
                anchor_evidence[0]
            )

            anchor_selection_basis = (
                "UNIQUE_EXPLICIT_TEMPORAL_ANCHOR_EVIDENCE"
            )

        elif anchor_count > 1:
            primary_signal_type = str(
                candidate.get(
                    "primary_signal_type"
                )
                or ""
            )

            primary_matches = [
                item
                for item in anchor_evidence
                if str(
                    item.get(
                        "signal_type"
                    )
                    or ""
                )
                == primary_signal_type
            ]

            if len(
                primary_matches
            ) == 1:
                selected_anchor_candidate = dict(
                    primary_matches[0]
                )

                anchor_selection_basis = (
                    "PRIMARY_SIGNAL_MATCHES_EXPLICIT_ANCHOR_EVIDENCE"
                )

            else:
                ranked = []

                for anchor in anchor_evidence:
                    anchor_signal_type = str(
                        anchor.get(
                            "signal_type"
                        )
                        or ""
                    )

                    try:
                        type_rank = (
                            preferred_anchor_signal_types.index(
                                anchor_signal_type
                            )
                        )
                    except ValueError:
                        type_rank = len(
                            preferred_anchor_signal_types
                        )

                    start = anchor.get(
                        "character_start"
                    )

                    end = anchor.get(
                        "character_end"
                    )

                    span_length = (
                        end - start
                        if (
                            isinstance(
                                start,
                                int,
                            )
                            and isinstance(
                                end,
                                int,
                            )
                            and end >= start
                        )
                        else -1
                    )

                    ranked.append(
                        (
                            type_rank,
                            -span_length,
                            start
                            if isinstance(
                                start,
                                int,
                            )
                            else 10**12,
                            dict(
                                anchor
                            ),
                        )
                    )

                ranked.sort(
                    key=lambda item: (
                        item[0],
                        item[1],
                        item[2],
                    )
                )

                if ranked:
                    best = ranked[0]

                    tied = [
                        item
                        for item in ranked
                        if (
                            item[0],
                            item[1],
                        )
                        == (
                            best[0],
                            best[1],
                        )
                    ]

                    if len(
                        tied
                    ) == 1:
                        selected_anchor_candidate = best[3]

                        anchor_selection_basis = (
                            "UNIQUE_HIGHEST_PRIORITY_EXPLICIT_ANCHOR_EVIDENCE"
                        )

        if orientation_class is None:
            orientation_status = (
                "TEMPORAL_RELATION_ORIENTATION_UNRESOLVED"
            )

            orientation_basis = (
                "UNSUPPORTED_TEMPORAL_ORIENTATION_SIGNAL"
            )

            orientation_resolved = False

        elif anchor_count == 0:
            orientation_status = (
                "TEMPORAL_RELATION_ORIENTATION_UNRESOLVED"
            )

            orientation_basis = (
                "NO_EXPLICIT_TEMPORAL_ANCHOR_EVIDENCE"
            )

            orientation_resolved = False

        elif selected_anchor_candidate is None:
            orientation_status = (
                "TEMPORAL_RELATION_ORIENTATION_UNRESOLVED"
            )

            orientation_basis = (
                "AMBIGUOUS_MULTIPLE_TEMPORAL_ANCHOR_EVIDENCE"
            )

            orientation_resolved = False

        elif grounding_match_count == 0:
            orientation_status = (
                "TEMPORAL_RELATION_ORIENTATION_UNRESOLVED"
            )

            orientation_basis = (
                "NO_ARTICLE_LOCAL_TEMPORAL_PARTICIPANT_GROUNDING"
            )

            orientation_resolved = False

        elif grounding_match_count > 1:
            orientation_status = (
                "TEMPORAL_RELATION_ORIENTATION_UNRESOLVED"
            )

            orientation_basis = (
                "AMBIGUOUS_MULTIPLE_TEMPORAL_PARTICIPANT_GROUNDINGS"
            )

            orientation_resolved = False

        else:
            orientation_status = (
                "TEMPORAL_RELATION_ORIENTATION_RESOLVED"
            )

            orientation_basis = (
                "EXPLICIT_TEMPORAL_STRUCTURE_PLUS_UNIQUE_ANCHOR_AND_PARTICIPANT_GROUNDING"
            )

            orientation_resolved = True

        selected_participant = (
            dict(
                grounding_matches[0]
            )
            if orientation_resolved
            else None
        )

        selected_anchor = (
            dict(
                selected_anchor_candidate
            )
            if orientation_resolved
            else None
        )

        oriented = dict(
            candidate
        )

        oriented.update({
            "temporal_orientation_status":
                orientation_status,

            "temporal_orientation_basis":
                orientation_basis,

            "temporal_orientation_class":
                orientation_class,

            "temporal_orientation_operator_signal_type":
                orientation_signal_type,

            "temporal_orientation_operator_text":
                orientation_operator_text,

            "temporal_anchor_selection_basis":
                (
                    anchor_selection_basis
                    if orientation_resolved
                    else None
                ),

            "selected_temporal_anchor":
                selected_anchor,

            "temporal_anchor_selected":
                selected_anchor
                is not None,

            "temporal_anchor_selection_performed":
                orientation_resolved,

            "selected_temporal_participant":
                selected_participant,

            "temporal_participant_selected":
                selected_participant
                is not None,

            "temporal_participant_selection_performed":
                orientation_resolved,

            "temporal_orientation_determined":
                orientation_resolved,

            "temporal_orientation":
                (
                    orientation_class
                    if orientation_resolved
                    else None
                ),

            "temporal_value_validation_performed":
                False,

            "temporal_relation_validated":
                False,

            "same_sentence_temporal_validated":
                False,

            "cross_sentence_temporal_anchor_resolved":
                False,

            "temporal_evidence_assessed":
                False,

            "semantic_duplicate_resolution_performed":
                False,

            "unstated_temporal_relation_inference_performed":
                False,

            "unstated_temporal_anchor_inference_performed":
                False,

            "unstated_duration_inference_performed":
                False,

            "unstated_recurrence_inference_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "similarity_reasoning_performed":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,
        })

        if orientation_resolved:
            resolved_count += 1
            selected_participant_count += 1
            selected_anchor_count += 1
        else:
            unresolved_count += 1

        class_key = (
            orientation_class
            or "UNSUPPORTED"
        )

        orientation_class_counts[
            class_key
        ] = (
            orientation_class_counts.get(
                class_key,
                0,
            )
            + 1
        )

        orientation_basis_counts[
            orientation_basis
        ] = (
            orientation_basis_counts.get(
                orientation_basis,
                0,
            )
            + 1
        )

        oriented_candidates.append(
            oriented
        )

        oriented_by_id[
            candidate_id
        ] = oriented

    oriented_units = []
    oriented_unit_by_id = {}

    for unit in (
        temporal_grounding_result.get(
            "temporal_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "temporal_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise TemporalIntelligenceError(
                "Temporal Claim Unit ID is required."
            )

        if unit_id in oriented_unit_by_id:
            raise TemporalIntelligenceError(
                "Duplicate Temporal Claim Unit ID."
            )

        state = dict(
            unit.get(
                "temporal_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "temporal_anchor_participant_grounding"
            )
            != "COMPLETE"
        ):
            raise TemporalIntelligenceError(
                "Temporal anchor/participant grounding must "
                "be COMPLETE before orientation."
            )

        if (
            state.get(
                "temporal_relation_orientation"
            )
            != "PENDING"
        ):
            raise TemporalIntelligenceError(
                "Temporal relation orientation must be PENDING."
            )

        updated_candidates = []

        for old_candidate in (
            unit.get(
                "temporal_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Every unit Temporal Candidate reference "
                    "must be a mapping."
                )

            candidate_id = str(
                old_candidate.get(
                    "temporal_candidate_id"
                )
                or ""
            )

            oriented_candidate = (
                oriented_by_id.get(
                    candidate_id
                )
            )

            if oriented_candidate is None:
                raise TemporalIntelligenceError(
                    "Temporal candidate/unit orientation mismatch."
                )

            updated_candidates.append(
                oriented_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "temporal_relation_orientation"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            updated_boundaries.get(
                "temporal_grounding_performed"
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                "Stage-G Temporal grounding boundary is incomplete."
            )

        if (
            updated_boundaries.get(
                "temporal_orientation_performed"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Temporal orientation must not already be performed."
            )

        required_false_boundaries = (
            "temporal_value_validation_performed",
            "temporal_relation_validation_performed",
            "same_sentence_temporal_validation_performed",
            "cross_sentence_temporal_anchoring_performed",
            "temporal_evidence_assessment_performed",
            "temporal_duplicate_resolution_performed",
            "unstated_temporal_relation_inference_performed",
            "unstated_temporal_anchor_inference_performed",
            "unstated_duration_inference_performed",
            "unstated_recurrence_inference_performed",
            "procedural_reasoning_performed",
            "quantitative_reasoning_performed",
            "new_causal_reasoning_performed",
            "analogical_reasoning_performed",
            "similarity_reasoning_performed",
            "truth_assessment_performed",
            "external_authority_check_performed",
            "semantic_memory_write_performed",
            "persistence_performed",
        )

        for boundary_name in required_false_boundaries:
            if (
                updated_boundaries.get(
                    boundary_name
                )
                is not False
            ):
                raise TemporalIntelligenceError(
                    boundary_name
                    + " must be False before Stage H."
                )

        updated_boundaries[
            "temporal_orientation_performed"
        ] = True

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "temporal_candidates":
                updated_candidates,

            "temporal_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        oriented_units.append(
            updated_unit
        )

        oriented_unit_by_id[
            unit_id
        ] = updated_unit

    oriented_sections = []

    for section in (
        temporal_grounding_result.get(
            "temporal_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "temporal_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Every section Temporal Claim Unit "
                    "reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "temporal_claim_unit_id"
                )
                or ""
            )

            oriented_unit = (
                oriented_unit_by_id.get(
                    unit_id
                )
            )

            if oriented_unit is None:
                raise TemporalIntelligenceError(
                    "Temporal section references an unknown oriented unit."
                )

            section_units.append(
                oriented_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "temporal_candidates"
                )
                or []
            )
        ]

        oriented_sections.append({
            **dict(
                section
            ),

            "temporal_claim_units":
                section_units,

            "temporal_candidates":
                section_candidates,

            "temporal_candidate_count":
                len(
                    section_candidates
                ),

            "resolved_temporal_orientation_count":
                sum(
                    1
                    for candidate
                    in section_candidates
                    if candidate.get(
                        "temporal_orientation_determined"
                    )
                    is True
                ),

            "unresolved_temporal_orientation_count":
                sum(
                    1
                    for candidate
                    in section_candidates
                    if candidate.get(
                        "temporal_orientation_determined"
                    )
                    is False
                ),
        })

    result = dict(
        temporal_grounding_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        boundaries.get(
            "temporal_grounding_performed"
        )
        is not True
    ):
        raise TemporalIntelligenceError(
            "Top-level Stage-G grounding boundary is incomplete."
        )

    if (
        boundaries.get(
            "temporal_orientation_performed"
        )
        is not False
    ):
        raise TemporalIntelligenceError(
            "Top-level Temporal orientation must not already be performed."
        )

    required_false_boundaries = (
        "temporal_value_validation_performed",
        "temporal_relation_validation_performed",
        "same_sentence_temporal_validation_performed",
        "cross_sentence_temporal_anchoring_performed",
        "temporal_evidence_assessment_performed",
        "temporal_duplicate_resolution_performed",
        "unstated_temporal_relation_inference_performed",
        "unstated_temporal_anchor_inference_performed",
        "unstated_duration_inference_performed",
        "unstated_recurrence_inference_performed",
        "procedural_reasoning_performed",
        "quantitative_reasoning_performed",
        "new_causal_reasoning_performed",
        "analogical_reasoning_performed",
        "similarity_reasoning_performed",
        "truth_assessment_performed",
        "external_authority_check_performed",
        "semantic_memory_write_performed",
        "persistence_performed",
    )

    for boundary_name in required_false_boundaries:
        if (
            boundaries.get(
                boundary_name
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                boundary_name
                + " must be False before Stage H."
            )

    boundaries[
        "temporal_orientation_performed"
    ] = True

    result.update({
        "schema_version":
            "temporal_relation_orientation_v1",

        "patch":
            "4.6.13H",

        "status":
            "TEMPORAL_RELATION_ORIENTATION_COMPLETE",

        "temporal_sections":
            oriented_sections,

        "temporal_claim_units":
            oriented_units,

        "temporal_candidates":
            oriented_candidates,

        "temporal_orientation_summary": {
            "candidate_count":
                len(
                    oriented_candidates
                ),

            "resolved_orientation_count":
                resolved_count,

            "unresolved_orientation_count":
                unresolved_count,

            "candidate_count_accounted_for":
                (
                    resolved_count
                    + unresolved_count
                    == len(
                        oriented_candidates
                    )
                ),

            "selected_temporal_participant_count":
                selected_participant_count,

            "selected_temporal_anchor_count":
                selected_anchor_count,

            "orientation_class_counts":
                dict(
                    sorted(
                        orientation_class_counts.items()
                    )
                ),

            "orientation_basis_counts":
                dict(
                    sorted(
                        orientation_basis_counts.items()
                    )
                ),

            "orientation_requires_explicit_temporal_structure":
                True,

            "orientation_requires_explicit_anchor_evidence":
                True,

            "orientation_requires_unique_participant_grounding":
                True,

            "multiple_participant_grounding_guessing_performed":
                False,

            "ambiguous_anchor_guessing_performed":
                False,

            "cross_sentence_orientation_performed":
                False,

            "temporal_value_validation_performed":
                False,

            "temporal_relation_validation_performed":
                False,

            "same_sentence_temporal_validation_performed":
                False,

            "cross_sentence_temporal_anchoring_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "similarity_reasoning_performed":
                False,

            "truth_assessment_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "point_duration_interval_validation",
    })

    return result


def validate_temporal_point_duration_interval_v1(
    temporal_orientation_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate explicit article-local Temporal point, duration, and interval
    structures after Stage-H orientation.

    Stage I may:
    - classify supported explicit Temporal values as POINT, DURATION,
      or INTERVAL,
    - preserve article-expressed numeric values,
    - canonicalize explicitly written time units,
    - validate explicit two-bound numeric interval ordering,
    - preserve non-numeric Temporal references such as birth.

    Stage I does NOT:
    - calculate an interval's duration,
    - infer an omitted time unit,
    - convert age N into N years when "years" is not written,
    - infer missing interval endpoints,
    - perform sequence/boundary/recurrence validation,
    - validate the final Temporal relation,
    - perform same-sentence Temporal validation,
    - perform cross-sentence Temporal anchoring,
    - perform procedural reasoning,
    - perform quantitative derived calculations,
    - perform new causal reasoning,
    - perform Analogical or Similarity reasoning,
    - assess factual/scientific truth,
    - use external authority,
    - write Semantic Memory,
    - persist intelligence.
    """

    import re

    if not isinstance(
        temporal_orientation_result,
        Mapping,
    ):
        raise TemporalIntelligenceError(
            "temporal_orientation_result must be a mapping."
        )

    if (
        temporal_orientation_result.get(
            "schema_version"
        )
        != "temporal_relation_orientation_v1"
    ):
        raise TemporalIntelligenceError(
            "Stage I requires temporal_relation_orientation_v1."
        )

    if (
        temporal_orientation_result.get(
            "status"
        )
        != "TEMPORAL_RELATION_ORIENTATION_COMPLETE"
    ):
        raise TemporalIntelligenceError(
            "Temporal relation orientation must be complete."
        )

    if (
        temporal_orientation_result.get(
            "phase"
        )
        != "4.6.13"
    ):
        raise TemporalIntelligenceError(
            "Stage I requires Phase 4.6.13 input."
        )

    if (
        temporal_orientation_result.get(
            "patch"
        )
        != "4.6.13H"
    ):
        raise TemporalIntelligenceError(
            "Stage I requires canonical 4.6.13H input."
        )

    if (
        temporal_orientation_result.get(
            "next_stage"
        )
        != "point_duration_interval_validation"
    ):
        raise TemporalIntelligenceError(
            "Stage H must hand off to "
            "point_duration_interval_validation."
        )

    if (
        temporal_orientation_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise TemporalIntelligenceError(
            "Temporal Intelligence must remain transient."
        )

    value_kind_by_signal = {
        "AGE_POINT":
            "POINT",

        "AT_AGE_TIME":
            "POINT",

        "BIRTH_ANCHOR":
            "POINT",

        "BETWEEN_RANGE":
            "INTERVAL",

        "FROM_TO_RANGE":
            "INTERVAL",

        "AGE_RANGE":
            "INTERVAL",

        "OVER_PERIOD":
            "DURATION",

        "FIRST_PERIOD":
            "DURATION",
    }

    unit_registry = {
        "day":
            {
                "day",
                "days",
            },

        "week":
            {
                "week",
                "weeks",
            },

        "month":
            {
                "month",
                "months",
            },

        "year":
            {
                "year",
                "years",
            },
    }

    def parse_number(
        value_text,
    ):
        try:
            value = float(
                value_text
            )
        except (
            TypeError,
            ValueError,
        ):
            return None

        if value.is_integer():
            return int(
                value
            )

        return value

    def explicit_numbers(
        raw_text,
    ):
        values = []

        for item in re.findall(
            r"\d+(?:\.\d+)?",
            raw_text,
        ):
            parsed = parse_number(
                item
            )

            if parsed is not None:
                values.append(
                    parsed
                )

        return values

    def explicit_unit(
        raw_text,
    ):
        lowered = raw_text.lower()

        matches = []

        for canonical_unit, aliases in (
            unit_registry.items()
        ):
            for alias in aliases:
                match = re.search(
                    r"\b"
                    + re.escape(
                        alias
                    )
                    + r"\b",
                    lowered,
                )

                if match:
                    matches.append(
                        (
                            match.start(),
                            canonical_unit,
                            alias,
                        )
                    )

        if not matches:
            return (
                None,
                None,
            )

        matches.sort(
            key=lambda item: (
                item[0],
                item[1],
                item[2],
            )
        )

        return (
            matches[0][1],
            matches[0][2],
        )

    def validate_candidate_value(
        candidate,
    ):
        validated = dict(
            candidate
        )

        if (
            candidate.get(
                "temporal_value_validation_performed"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Temporal value validation must not already be performed."
            )

        if (
            candidate.get(
                "temporal_relation_validated"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Temporal relation must not already be validated."
            )

        if (
            candidate.get(
                "same_sentence_temporal_validated"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Same-sentence Temporal validation must not "
                "already be performed."
            )

        if (
            candidate.get(
                "cross_sentence_temporal_anchor_resolved"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Cross-sentence Temporal anchoring must not "
                "already be performed."
            )

        if (
            candidate.get(
                "temporal_orientation_status"
            )
            not in {
                "TEMPORAL_RELATION_ORIENTATION_RESOLVED",
                "TEMPORAL_RELATION_ORIENTATION_UNRESOLVED",
            }
        ):
            raise TemporalIntelligenceError(
                "Candidate has invalid Temporal orientation status."
            )

        selected_anchor = candidate.get(
            "selected_temporal_anchor"
        )

        orientation_resolved = (
            candidate.get(
                "temporal_orientation_determined"
            )
            is True
        )

        if orientation_resolved:
            if (
                candidate.get(
                    "temporal_anchor_selected"
                )
                is not True
                or not isinstance(
                    selected_anchor,
                    Mapping,
                )
            ):
                raise TemporalIntelligenceError(
                    "Resolved Temporal orientation requires "
                    "one selected Temporal anchor."
                )

        else:
            if (
                candidate.get(
                    "temporal_anchor_selected"
                )
                is not False
                or selected_anchor
                is not None
            ):
                raise TemporalIntelligenceError(
                    "Unresolved Temporal orientation must not "
                    "contain a selected Temporal anchor."
                )

        payload = {
            "validation_status":
                "NOT_APPLICABLE",

            "temporal_value_kind":
                None,

            "raw_temporal_text":
                None,

            "source_signal_type":
                None,

            "normalized_value":
                None,

            "normalized_values":
                [],

            "canonical_unit":
                None,

            "article_explicit_unit":
                None,

            "unit_explicit":
                False,

            "temporal_reference_kind":
                None,

            "interval_order_valid":
                None,

            "interval_lower_value":
                None,

            "interval_upper_value":
                None,

            "interval_duration_calculated":
                False,

            "derived_duration":
                None,

            "normalization_reason":
                "NO_STAGE_I_SUPPORTED_SELECTED_TEMPORAL_VALUE",

            "article_explicit_value_only":
                True,

            "omitted_unit_inference_performed":
                False,

            "missing_endpoint_inference_performed":
                False,

            "derived_calculation_performed":
                False,
        }

        if not orientation_resolved:
            payload.update({
                "validation_status":
                    "UNRESOLVED",

                "normalization_reason":
                    "TEMPORAL_ORIENTATION_UNRESOLVED",
            })

            validated.update({
                "temporal_value_validation_performed":
                    True,

                "temporal_value_validated":
                    False,

                "temporal_value_validation":
                    payload,

                "derived_temporal_calculation_performed":
                    False,

                "temporal_value_inference_performed":
                    False,
            })

            return validated

        anchor_signal_type = str(
            selected_anchor.get(
                "signal_type"
            )
            or ""
        )

        raw_text = str(
            selected_anchor.get(
                "anchor_text"
            )
            or ""
        ).strip()

        if not anchor_signal_type:
            raise TemporalIntelligenceError(
                "Selected Temporal anchor signal_type is required."
            )

        if not raw_text:
            raise TemporalIntelligenceError(
                "Selected Temporal anchor text is required."
            )

        value_kind = value_kind_by_signal.get(
            anchor_signal_type
        )

        payload.update({
            "raw_temporal_text":
                raw_text,

            "source_signal_type":
                anchor_signal_type,

            "temporal_value_kind":
                value_kind,
        })

        if value_kind is None:
            validated.update({
                "temporal_value_validation_performed":
                    True,

                "temporal_value_validated":
                    False,

                "temporal_value_validation":
                    payload,

                "derived_temporal_calculation_performed":
                    False,

                "temporal_value_inference_performed":
                    False,
            })

            return validated

        numbers = explicit_numbers(
            raw_text
        )

        canonical_unit, written_unit = (
            explicit_unit(
                raw_text
            )
        )

        payload[
            "canonical_unit"
        ] = canonical_unit

        payload[
            "article_explicit_unit"
        ] = written_unit

        payload[
            "unit_explicit"
        ] = canonical_unit is not None

        if value_kind == "POINT":
            if anchor_signal_type == "BIRTH_ANCHOR":
                payload.update({
                    "validation_status":
                        "VALIDATED",

                    "temporal_reference_kind":
                        "BIRTH_REFERENCE",

                    "normalization_reason":
                        "ARTICLE_EXPRESSED_BIRTH_TEMPORAL_POINT",
                })

            elif len(
                numbers
            ) >= 1:
                payload.update({
                    "validation_status":
                        "VALIDATED",

                    "normalized_value":
                        numbers[0],

                    "normalized_values":
                        [
                            numbers[0]
                        ],

                    "temporal_reference_kind":
                        "AGE_POINT",

                    "normalization_reason":
                        (
                            "ARTICLE_EXPRESSED_AGE_POINT_WITH_EXPLICIT_UNIT"
                            if canonical_unit
                            else
                            "ARTICLE_EXPRESSED_AGE_POINT_WITHOUT_UNIT_INFERENCE"
                        ),
                })

            else:
                payload.update({
                    "validation_status":
                        "UNRESOLVED",

                    "normalization_reason":
                        "POINT_VALUE_NOT_EXPLICITLY_PARSEABLE",
                })

        elif value_kind == "DURATION":
            if (
                anchor_signal_type
                == "FIRST_PERIOD"
                and canonical_unit
                and re.search(
                    r"\bfirst\b",
                    raw_text,
                    re.IGNORECASE,
                )
            ):
                payload.update({
                    "validation_status":
                        "VALIDATED",

                    "temporal_reference_kind":
                        "EXPLICIT_FIRST_PERIOD",

                    "normalization_reason":
                        "ARTICLE_EXPRESSED_FIRST_TEMPORAL_PERIOD",
                })

            elif (
                len(
                    numbers
                )
                >= 1
                and canonical_unit
            ):
                payload.update({
                    "validation_status":
                        "VALIDATED",

                    "normalized_value":
                        numbers[0],

                    "normalized_values":
                        [
                            numbers[0]
                        ],

                    "temporal_reference_kind":
                        "EXPLICIT_DURATION",

                    "normalization_reason":
                        "ARTICLE_EXPRESSED_TEMPORAL_DURATION",
                })

            else:
                payload.update({
                    "validation_status":
                        "UNRESOLVED",

                    "normalization_reason":
                        "DURATION_REQUIRES_EXPLICIT_VALUE_AND_UNIT",
                })

        elif value_kind == "INTERVAL":
            if len(
                numbers
            ) == 2:
                lower = numbers[0]
                upper = numbers[1]

                order_valid = (
                    lower <= upper
                )

                payload.update({
                    "validation_status":
                        (
                            "VALIDATED"
                            if order_valid
                            else "INVALID"
                        ),

                    "normalized_values":
                        [
                            lower,
                            upper,
                        ],

                    "interval_lower_value":
                        lower,

                    "interval_upper_value":
                        upper,

                    "interval_order_valid":
                        order_valid,

                    "temporal_reference_kind":
                        "EXPLICIT_NUMERIC_INTERVAL",

                    "normalization_reason":
                        (
                            "ARTICLE_EXPRESSED_ORDERED_TEMPORAL_INTERVAL"
                            if order_valid
                            else
                            "ARTICLE_EXPRESSED_REVERSED_TEMPORAL_INTERVAL"
                        ),
                })

            else:
                payload.update({
                    "validation_status":
                        "UNRESOLVED",

                    "temporal_reference_kind":
                        "EXPLICIT_INTERVAL_REFERENCE",

                    "normalization_reason":
                        "INTERVAL_ENDPOINTS_NOT_BOTH_NUMERICALLY_EXPLICIT",
                })

        validated.update({
            "temporal_value_validation_performed":
                True,

            "temporal_value_validated":
                payload[
                    "validation_status"
                ]
                == "VALIDATED",

            "temporal_value_validation":
                payload,

            "derived_temporal_calculation_performed":
                False,

            "temporal_value_inference_performed":
                False,

            "temporal_relation_validated":
                False,

            "same_sentence_temporal_validated":
                False,

            "cross_sentence_temporal_anchor_resolved":
                False,

            "temporal_evidence_assessed":
                False,

            "semantic_duplicate_resolution_performed":
                False,

            "unstated_temporal_relation_inference_performed":
                False,

            "unstated_temporal_anchor_inference_performed":
                False,

            "unstated_duration_inference_performed":
                False,

            "unstated_recurrence_inference_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "similarity_reasoning_performed":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,
        })

        return validated

    source_candidates = list(
        temporal_orientation_result.get(
            "temporal_candidates"
        )
        or []
    )

    validated_candidates = []
    validated_by_id = {}
    seen_candidate_ids = set()

    validated_count = 0
    unresolved_count = 0
    invalid_count = 0
    not_applicable_count = 0
    point_count = 0
    duration_count = 0
    interval_count = 0

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "temporal_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise TemporalIntelligenceError(
                "Temporal Candidate ID is required."
            )

        if candidate_id in seen_candidate_ids:
            raise TemporalIntelligenceError(
                "Duplicate Temporal Candidate ID."
            )

        seen_candidate_ids.add(
            candidate_id
        )

        validated = validate_candidate_value(
            candidate
        )

        validation = validated[
            "temporal_value_validation"
        ]

        status = validation[
            "validation_status"
        ]

        kind = validation[
            "temporal_value_kind"
        ]

        if status == "VALIDATED":
            validated_count += 1

        elif status == "UNRESOLVED":
            unresolved_count += 1

        elif status == "INVALID":
            invalid_count += 1

        elif status == "NOT_APPLICABLE":
            not_applicable_count += 1

        else:
            raise TemporalIntelligenceError(
                "Unknown Temporal value validation status."
            )

        if kind == "POINT":
            point_count += 1

        elif kind == "DURATION":
            duration_count += 1

        elif kind == "INTERVAL":
            interval_count += 1

        elif kind is not None:
            raise TemporalIntelligenceError(
                "Unknown Temporal value kind."
            )

        validated_candidates.append(
            validated
        )

        validated_by_id[
            candidate_id
        ] = validated

    validated_units = []
    validated_unit_by_id = {}

    for unit in (
        temporal_orientation_result.get(
            "temporal_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "temporal_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise TemporalIntelligenceError(
                "Temporal Claim Unit ID is required."
            )

        if unit_id in validated_unit_by_id:
            raise TemporalIntelligenceError(
                "Duplicate Temporal Claim Unit ID."
            )

        state = dict(
            unit.get(
                "temporal_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "temporal_relation_orientation"
            )
            != "COMPLETE"
        ):
            raise TemporalIntelligenceError(
                "Temporal relation orientation must be COMPLETE "
                "before Stage I."
            )

        if (
            state.get(
                "point_duration_interval_validation"
            )
            != "PENDING"
        ):
            raise TemporalIntelligenceError(
                "Point/duration/interval validation must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "temporal_orientation_performed"
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                "Stage-H orientation boundary is incomplete."
            )

        required_false_boundaries = (
            "temporal_value_validation_performed",
            "temporal_relation_validation_performed",
            "same_sentence_temporal_validation_performed",
            "cross_sentence_temporal_anchoring_performed",
            "temporal_evidence_assessment_performed",
            "temporal_duplicate_resolution_performed",
            "unstated_temporal_relation_inference_performed",
            "unstated_temporal_anchor_inference_performed",
            "unstated_duration_inference_performed",
            "unstated_recurrence_inference_performed",
            "procedural_reasoning_performed",
            "quantitative_reasoning_performed",
            "new_causal_reasoning_performed",
            "analogical_reasoning_performed",
            "similarity_reasoning_performed",
            "truth_assessment_performed",
            "external_authority_check_performed",
            "semantic_memory_write_performed",
            "persistence_performed",
        )

        for boundary_name in required_false_boundaries:
            if (
                boundaries.get(
                    boundary_name
                )
                is not False
            ):
                raise TemporalIntelligenceError(
                    boundary_name
                    + " must be False before Stage I."
                )

        updated_candidates = []

        for old_candidate in (
            unit.get(
                "temporal_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Every unit Temporal candidate reference "
                    "must be a mapping."
                )

            candidate_id = str(
                old_candidate.get(
                    "temporal_candidate_id"
                )
                or ""
            )

            validated_candidate = (
                validated_by_id.get(
                    candidate_id
                )
            )

            if validated_candidate is None:
                raise TemporalIntelligenceError(
                    "Temporal candidate/unit validation mismatch."
                )

            updated_candidates.append(
                validated_candidate
            )

        state[
            "point_duration_interval_validation"
        ] = "COMPLETE"

        boundaries[
            "temporal_value_validation_performed"
        ] = True

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "temporal_candidates":
                updated_candidates,

            "temporal_analysis_state":
                state,

            "processing_boundaries":
                boundaries,

            "validated_temporal_value_candidate_count":
                sum(
                    1
                    for candidate
                    in updated_candidates
                    if candidate.get(
                        "temporal_value_validated"
                    )
                    is True
                ),
        })

        validated_units.append(
            updated_unit
        )

        validated_unit_by_id[
            unit_id
        ] = updated_unit

    validated_sections = []

    for section in (
        temporal_orientation_result.get(
            "temporal_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "temporal_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Every section Temporal Claim Unit "
                    "reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "temporal_claim_unit_id"
                )
                or ""
            )

            validated_unit = (
                validated_unit_by_id.get(
                    unit_id
                )
            )

            if validated_unit is None:
                raise TemporalIntelligenceError(
                    "Temporal section references an unknown "
                    "validated claim unit."
                )

            section_units.append(
                validated_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "temporal_candidates"
                )
                or []
            )
        ]

        validated_sections.append({
            **dict(
                section
            ),

            "temporal_claim_units":
                section_units,

            "temporal_candidates":
                section_candidates,

            "temporal_candidate_count":
                len(
                    section_candidates
                ),

            "validated_temporal_value_candidate_count":
                sum(
                    1
                    for candidate
                    in section_candidates
                    if candidate.get(
                        "temporal_value_validated"
                    )
                    is True
                ),
        })

    result = dict(
        temporal_orientation_result
    )

    top_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        top_boundaries.get(
            "temporal_orientation_performed"
        )
        is not True
    ):
        raise TemporalIntelligenceError(
            "Top-level Stage-H orientation boundary is incomplete."
        )

    if (
        top_boundaries.get(
            "temporal_value_validation_performed"
        )
        is not False
    ):
        raise TemporalIntelligenceError(
            "Top-level Temporal value validation must not "
            "already be performed."
        )

    required_false_top_boundaries = (
        "temporal_relation_validation_performed",
        "same_sentence_temporal_validation_performed",
        "cross_sentence_temporal_anchoring_performed",
        "temporal_evidence_assessment_performed",
        "temporal_duplicate_resolution_performed",
        "unstated_temporal_relation_inference_performed",
        "unstated_temporal_anchor_inference_performed",
        "unstated_duration_inference_performed",
        "unstated_recurrence_inference_performed",
        "procedural_reasoning_performed",
        "quantitative_reasoning_performed",
        "new_causal_reasoning_performed",
        "analogical_reasoning_performed",
        "similarity_reasoning_performed",
        "truth_assessment_performed",
        "external_authority_check_performed",
        "semantic_memory_write_performed",
        "persistence_performed",
    )

    for boundary_name in required_false_top_boundaries:
        if (
            top_boundaries.get(
                boundary_name
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                boundary_name
                + " must be False before Stage I."
            )

    top_boundaries[
        "temporal_value_validation_performed"
    ] = True

    result.update({
        "schema_version":
            "temporal_point_duration_interval_validation_v1",

        "patch":
            "4.6.13I",

        "status":
            "TEMPORAL_POINT_DURATION_INTERVAL_VALIDATION_COMPLETE",

        "temporal_sections":
            validated_sections,

        "temporal_claim_units":
            validated_units,

        "temporal_candidates":
            validated_candidates,

        "temporal_value_validation_summary": {
            "candidate_count":
                len(
                    validated_candidates
                ),

            "validated_candidate_count":
                validated_count,

            "unresolved_candidate_count":
                unresolved_count,

            "invalid_candidate_count":
                invalid_count,

            "not_applicable_candidate_count":
                not_applicable_count,

            "candidate_count_accounted_for":
                (
                    validated_count
                    + unresolved_count
                    + invalid_count
                    + not_applicable_count
                    == len(
                        validated_candidates
                    )
                ),

            "point_candidate_count":
                point_count,

            "duration_candidate_count":
                duration_count,

            "interval_candidate_count":
                interval_count,

            "article_explicit_values_only":
                True,

            "omitted_unit_inference_performed":
                False,

            "missing_interval_endpoint_inference_performed":
                False,

            "interval_duration_calculation_performed":
                False,

            "derived_calculation_performed":
                False,

            "sequence_boundary_recurrence_validation_performed":
                False,

            "temporal_relation_validation_performed":
                False,

            "same_sentence_temporal_validation_performed":
                False,

            "cross_sentence_temporal_anchoring_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "similarity_reasoning_performed":
                False,

            "truth_assessment_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            top_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "sequence_boundary_recurrence_validation",
    })

    return result


def validate_temporal_sequence_boundary_recurrence_v1(
    temporal_value_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate explicit article-local Temporal relation structure after
    Stage-I point/duration/interval validation.

    Stage J owns structural validation of:
    - SEQUENCE:
        AFTER, BEFORE
    - BOUNDARY / WINDOW:
        SINCE, UNTIL, WITHIN, BY_TIME, AGE_UNDER, UP_TO_AGE
    - RECURRENCE:
        PER_TIME_UNIT, EACH_TIME_UNIT

    Stage J does NOT perform final same-sentence semantic validation.
    Therefore structurally recognized relations remain provisional until K.

    Stage J does not:
    - infer unstated Temporal relations,
    - infer missing anchors or values,
    - calculate durations,
    - perform procedural reasoning,
    - perform quantitative derived calculations,
    - perform cross-sentence anchoring,
    - assess evidence confidence,
    - resolve duplicates,
    - assess factual truth,
    - use external authority,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        temporal_value_result,
        Mapping,
    ):
        raise TemporalIntelligenceError(
            "temporal_value_result must be a mapping."
        )

    if (
        temporal_value_result.get(
            "schema_version"
        )
        != "temporal_point_duration_interval_validation_v1"
    ):
        raise TemporalIntelligenceError(
            "Stage J requires "
            "temporal_point_duration_interval_validation_v1."
        )

    if (
        temporal_value_result.get(
            "status"
        )
        != "TEMPORAL_POINT_DURATION_INTERVAL_VALIDATION_COMPLETE"
    ):
        raise TemporalIntelligenceError(
            "Point/duration/interval validation must be complete."
        )

    if (
        temporal_value_result.get(
            "phase"
        )
        != "4.6.13"
    ):
        raise TemporalIntelligenceError(
            "Stage J requires Phase 4.6.13 input."
        )

    if (
        temporal_value_result.get(
            "patch"
        )
        != "4.6.13I"
    ):
        raise TemporalIntelligenceError(
            "Stage J requires canonical 4.6.13I input."
        )

    if (
        temporal_value_result.get(
            "next_stage"
        )
        != "sequence_boundary_recurrence_validation"
    ):
        raise TemporalIntelligenceError(
            "Stage I must hand off to "
            "sequence_boundary_recurrence_validation."
        )

    if (
        temporal_value_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise TemporalIntelligenceError(
            "Temporal Intelligence must remain transient."
        )

    structural_relation_by_signal = {
        "AFTER": {
            "relation_family":
                "SEQUENCE",

            "relation_type":
                "AFTER",

            "direction":
                "EVENT_AFTER_ANCHOR",

            "boundary_role":
                None,

            "recurrence_role":
                None,
        },

        "BEFORE": {
            "relation_family":
                "SEQUENCE",

            "relation_type":
                "BEFORE",

            "direction":
                "EVENT_BEFORE_ANCHOR",

            "boundary_role":
                None,

            "recurrence_role":
                None,
        },

        "SINCE": {
            "relation_family":
                "BOUNDARY",

            "relation_type":
                "SINCE",

            "direction":
                None,

            "boundary_role":
                "START_BOUNDARY",

            "recurrence_role":
                None,
        },

        "UNTIL": {
            "relation_family":
                "BOUNDARY",

            "relation_type":
                "UNTIL",

            "direction":
                None,

            "boundary_role":
                "END_BOUNDARY",

            "recurrence_role":
                None,
        },

        "WITHIN": {
            "relation_family":
                "BOUNDARY",

            "relation_type":
                "WITHIN",

            "direction":
                None,

            "boundary_role":
                "BOUNDED_WINDOW",

            "recurrence_role":
                None,
        },

        "BY_TIME": {
            "relation_family":
                "BOUNDARY",

            "relation_type":
                "BY_TIME",

            "direction":
                None,

            "boundary_role":
                "UPPER_BOUNDARY",

            "recurrence_role":
                None,
        },

        "AGE_UNDER": {
            "relation_family":
                "BOUNDARY",

            "relation_type":
                "AGE_UNDER",

            "direction":
                None,

            "boundary_role":
                "UPPER_AGE_BOUNDARY_EXCLUSIVE",

            "recurrence_role":
                None,
        },

        "UP_TO_AGE": {
            "relation_family":
                "BOUNDARY",

            "relation_type":
                "UP_TO_AGE",

            "direction":
                None,

            "boundary_role":
                "UPPER_AGE_BOUNDARY",

            "recurrence_role":
                None,
        },

        "PER_TIME_UNIT": {
            "relation_family":
                "RECURRENCE",

            "relation_type":
                "PER_TIME_UNIT",

            "direction":
                None,

            "boundary_role":
                None,

            "recurrence_role":
                "RATE_RECURRENCE",
        },

        "EACH_TIME_UNIT": {
            "relation_family":
                "RECURRENCE",

            "relation_type":
                "EACH_TIME_UNIT",

            "direction":
                None,

            "boundary_role":
                None,

            "recurrence_role":
                "EACH_PERIOD_RECURRENCE",
        },
    }

    def validate_candidate_relation(
        candidate,
    ):
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal candidate must be a mapping."
            )

        if (
            candidate.get(
                "temporal_value_validation_performed"
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                "Stage-I Temporal value validation must be complete."
            )

        if (
            candidate.get(
                "temporal_relation_validated"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Temporal relation must not already be validated."
            )

        if (
            candidate.get(
                "same_sentence_temporal_validated"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Same-sentence Temporal validation must remain pending."
            )

        if (
            candidate.get(
                "cross_sentence_temporal_anchor_resolved"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Cross-sentence Temporal anchoring must remain pending."
            )

        orientation_status = str(
            candidate.get(
                "temporal_orientation_status"
            )
            or ""
        )

        orientation_signal = str(
            candidate.get(
                "temporal_orientation_operator_signal_type"
            )
            or ""
        )

        selected_anchor = candidate.get(
            "selected_temporal_anchor"
        )

        selected_participant = candidate.get(
            "selected_temporal_participant"
        )

        payload = {
            "validation_status":
                "NOT_APPLICABLE",

            "relation_family":
                None,

            "relation_type":
                None,

            "direction":
                None,

            "boundary_role":
                None,

            "recurrence_role":
                None,

            "orientation_signal_type":
                orientation_signal
                or None,

            "orientation_class":
                candidate.get(
                    "temporal_orientation"
                ),

            "selected_temporal_anchor":
                (
                    dict(
                        selected_anchor
                    )
                    if isinstance(
                        selected_anchor,
                        Mapping,
                    )
                    else None
                ),

            "selected_temporal_participant":
                (
                    dict(
                        selected_participant
                    )
                    if isinstance(
                        selected_participant,
                        Mapping,
                    )
                    else None
                ),

            "explicit_structure_only":
                True,

            "same_sentence_semantic_validation_performed":
                False,

            "cross_sentence_resolution_performed":
                False,

            "relation_inference_performed":
                False,

            "anchor_inference_performed":
                False,

            "recurrence_inference_performed":
                False,

            "derived_calculation_performed":
                False,

            "validation_reason":
                "NO_STAGE_J_SUPPORTED_RELATION_STRUCTURE",
        }

        if (
            orientation_status
            != "TEMPORAL_RELATION_ORIENTATION_RESOLVED"
        ):
            payload.update({
                "validation_status":
                    "UNRESOLVED",

                "validation_reason":
                    "TEMPORAL_ORIENTATION_UNRESOLVED",
            })

            validated = dict(
                candidate
            )

            validated.update({
                "temporal_relation_validation_performed":
                    True,

                "temporal_relation_validated":
                    False,

                "temporal_relation_structure":
                    payload,

                "sequence_boundary_recurrence_validation_performed":
                    True,

                "same_sentence_temporal_validated":
                    False,

                "cross_sentence_temporal_anchor_resolved":
                    False,
            })

            return validated

        relation_spec = (
            structural_relation_by_signal.get(
                orientation_signal
            )
        )

        if relation_spec is None:
            validated = dict(
                candidate
            )

            validated.update({
                "temporal_relation_validation_performed":
                    True,

                "temporal_relation_validated":
                    False,

                "temporal_relation_structure":
                    payload,

                "sequence_boundary_recurrence_validation_performed":
                    True,

                "same_sentence_temporal_validated":
                    False,

                "cross_sentence_temporal_anchor_resolved":
                    False,
            })

            return validated

        if not isinstance(
            selected_anchor,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Supported Stage-J relation requires selected anchor."
            )

        if not isinstance(
            selected_participant,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Supported Stage-J relation requires selected participant."
            )

        payload.update(
            relation_spec
        )

        payload.update({
            "validation_status":
                "STRUCTURALLY_VALIDATED",

            "validation_reason":
                "EXPLICIT_ORIENTED_RELATION_WITH_SELECTED_ANCHOR_AND_PARTICIPANT",
        })

        validated = dict(
            candidate
        )

        validated.update({
            "temporal_relation_validation_performed":
                True,

            # This means Stage-J structural relation validation only.
            # K still owns final same-sentence semantic validation.
            "temporal_relation_validated":
                True,

            "temporal_relation_structure":
                payload,

            "sequence_boundary_recurrence_validation_performed":
                True,

            "same_sentence_temporal_validated":
                False,

            "cross_sentence_temporal_anchor_resolved":
                False,

            "temporal_evidence_assessed":
                False,

            "semantic_duplicate_resolution_performed":
                False,

            "unstated_temporal_relation_inference_performed":
                False,

            "unstated_temporal_anchor_inference_performed":
                False,

            "unstated_duration_inference_performed":
                False,

            "unstated_recurrence_inference_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "similarity_reasoning_performed":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,
        })

        return validated

    source_candidates = list(
        temporal_value_result.get(
            "temporal_candidates"
        )
        or []
    )

    validated_candidates = []
    validated_by_id = {}
    seen_candidate_ids = set()

    structurally_validated_count = 0
    unresolved_count = 0
    not_applicable_count = 0

    sequence_count = 0
    boundary_count = 0
    recurrence_count = 0

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "temporal_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise TemporalIntelligenceError(
                "Temporal Candidate ID is required."
            )

        if candidate_id in seen_candidate_ids:
            raise TemporalIntelligenceError(
                "Duplicate Temporal Candidate ID."
            )

        seen_candidate_ids.add(
            candidate_id
        )

        validated = validate_candidate_relation(
            candidate
        )

        relation = validated[
            "temporal_relation_structure"
        ]

        validation_status = relation[
            "validation_status"
        ]

        family = relation[
            "relation_family"
        ]

        if (
            validation_status
            == "STRUCTURALLY_VALIDATED"
        ):
            structurally_validated_count += 1

        elif validation_status == "UNRESOLVED":
            unresolved_count += 1

        elif validation_status == "NOT_APPLICABLE":
            not_applicable_count += 1

        else:
            raise TemporalIntelligenceError(
                "Unknown Stage-J validation status."
            )

        if family == "SEQUENCE":
            sequence_count += 1

        elif family == "BOUNDARY":
            boundary_count += 1

        elif family == "RECURRENCE":
            recurrence_count += 1

        elif family is not None:
            raise TemporalIntelligenceError(
                "Unknown Stage-J Temporal relation family."
            )

        validated_candidates.append(
            validated
        )

        validated_by_id[
            candidate_id
        ] = validated

    validated_units = []
    validated_unit_by_id = {}

    for unit in (
        temporal_value_result.get(
            "temporal_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "temporal_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise TemporalIntelligenceError(
                "Temporal Claim Unit ID is required."
            )

        if unit_id in validated_unit_by_id:
            raise TemporalIntelligenceError(
                "Duplicate Temporal Claim Unit ID."
            )

        state = dict(
            unit.get(
                "temporal_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "point_duration_interval_validation"
            )
            != "COMPLETE"
        ):
            raise TemporalIntelligenceError(
                "Stage-I validation must be COMPLETE before J."
            )

        if (
            state.get(
                "sequence_boundary_recurrence_validation"
            )
            != "PENDING"
        ):
            raise TemporalIntelligenceError(
                "Stage-J state must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "temporal_value_validation_performed"
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                "Stage-I boundary is incomplete."
            )

        if (
            boundaries.get(
                "temporal_relation_validation_performed"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Temporal relation validation must be False before J."
            )

        later_false = (
            "same_sentence_temporal_validation_performed",
            "cross_sentence_temporal_anchoring_performed",
            "temporal_evidence_assessment_performed",
            "temporal_duplicate_resolution_performed",
            "unstated_temporal_relation_inference_performed",
            "unstated_temporal_anchor_inference_performed",
            "unstated_duration_inference_performed",
            "unstated_recurrence_inference_performed",
            "procedural_reasoning_performed",
            "quantitative_reasoning_performed",
            "new_causal_reasoning_performed",
            "analogical_reasoning_performed",
            "similarity_reasoning_performed",
            "truth_assessment_performed",
            "external_authority_check_performed",
            "semantic_memory_write_performed",
            "persistence_performed",
        )

        for boundary_name in later_false:
            if (
                boundaries.get(
                    boundary_name
                )
                is not False
            ):
                raise TemporalIntelligenceError(
                    boundary_name
                    + " must remain False before Stage J."
                )

        updated_candidates = []

        for old_candidate in (
            unit.get(
                "temporal_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Unit Temporal candidate must be a mapping."
                )

            candidate_id = str(
                old_candidate.get(
                    "temporal_candidate_id"
                )
                or ""
            )

            replacement = (
                validated_by_id.get(
                    candidate_id
                )
            )

            if replacement is None:
                raise TemporalIntelligenceError(
                    "Stage-J candidate/unit mismatch."
                )

            updated_candidates.append(
                replacement
            )

        state[
            "sequence_boundary_recurrence_validation"
        ] = "COMPLETE"

        boundaries[
            "temporal_relation_validation_performed"
        ] = True

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "temporal_candidates":
                updated_candidates,

            "temporal_analysis_state":
                state,

            "processing_boundaries":
                boundaries,

            "structurally_validated_temporal_relation_count":
                sum(
                    1
                    for candidate
                    in updated_candidates
                    if candidate.get(
                        "temporal_relation_structure",
                        {},
                    ).get(
                        "validation_status"
                    )
                    == "STRUCTURALLY_VALIDATED"
                ),
        })

        validated_units.append(
            updated_unit
        )

        validated_unit_by_id[
            unit_id
        ] = updated_unit

    validated_sections = []

    for section in (
        temporal_value_result.get(
            "temporal_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "temporal_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Section Temporal Claim Unit must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "temporal_claim_unit_id"
                )
                or ""
            )

            replacement = (
                validated_unit_by_id.get(
                    unit_id
                )
            )

            if replacement is None:
                raise TemporalIntelligenceError(
                    "Temporal section references unknown Stage-J unit."
                )

            section_units.append(
                replacement
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "temporal_candidates"
                )
                or []
            )
        ]

        validated_sections.append({
            **dict(
                section
            ),

            "temporal_claim_units":
                section_units,

            "temporal_candidates":
                section_candidates,

            "temporal_candidate_count":
                len(
                    section_candidates
                ),

            "structurally_validated_temporal_relation_count":
                sum(
                    1
                    for candidate
                    in section_candidates
                    if candidate.get(
                        "temporal_relation_structure",
                        {},
                    ).get(
                        "validation_status"
                    )
                    == "STRUCTURALLY_VALIDATED"
                ),
        })

    result = dict(
        temporal_value_result
    )

    top_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        top_boundaries.get(
            "temporal_value_validation_performed"
        )
        is not True
    ):
        raise TemporalIntelligenceError(
            "Top-level Stage-I boundary is incomplete."
        )

    if (
        top_boundaries.get(
            "temporal_relation_validation_performed"
        )
        is not False
    ):
        raise TemporalIntelligenceError(
            "Top-level Temporal relation validation must "
            "not already be performed."
        )

    top_boundaries[
        "temporal_relation_validation_performed"
    ] = True

    result.update({
        "schema_version":
            "temporal_sequence_boundary_recurrence_validation_v1",

        "patch":
            "4.6.13J",

        "status":
            "TEMPORAL_SEQUENCE_BOUNDARY_RECURRENCE_VALIDATION_COMPLETE",

        "temporal_sections":
            validated_sections,

        "temporal_claim_units":
            validated_units,

        "temporal_candidates":
            validated_candidates,

        "temporal_relation_validation_summary": {
            "candidate_count":
                len(
                    validated_candidates
                ),

            "structurally_validated_candidate_count":
                structurally_validated_count,

            "unresolved_candidate_count":
                unresolved_count,

            "not_applicable_candidate_count":
                not_applicable_count,

            "candidate_count_accounted_for":
                (
                    structurally_validated_count
                    + unresolved_count
                    + not_applicable_count
                    == len(
                        validated_candidates
                    )
                ),

            "sequence_relation_count":
                sequence_count,

            "boundary_relation_count":
                boundary_count,

            "recurrence_relation_count":
                recurrence_count,

            "same_sentence_semantic_validation_performed":
                False,

            "cross_sentence_resolution_performed":
                False,

            "unstated_temporal_relation_inference_performed":
                False,

            "unstated_temporal_anchor_inference_performed":
                False,

            "unstated_recurrence_inference_performed":
                False,

            "derived_calculation_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "similarity_reasoning_performed":
                False,

            "truth_assessment_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            top_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "same_sentence_temporal_validation",
    })

    return result


def validate_same_sentence_temporal_relation_v1(
    temporal_relation_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate whether a Stage-J structurally recognized Temporal relation
    is supported within the candidate's own sentence.

    Stage K may confirm:
    - one sentence provenance,
    - explicit selected Temporal anchor evidence inside that sentence,
    - previously selected article-local participant grounding,
    - Stage-J structurally validated sequence/boundary/recurrence relation.

    Stage K does NOT:
    - search neighboring sentences,
    - repair missing anchors from another sentence,
    - infer missing participants,
    - infer unstated Temporal relations,
    - perform quantitative calculation,
    - perform new procedural reasoning,
    - assess external truth,
    - use external authority,
    - write Semantic Memory,
    - persist intelligence.

    Cross-sentence repair belongs exclusively to Stage L.
    """

    if not isinstance(
        temporal_relation_result,
        Mapping,
    ):
        raise TemporalIntelligenceError(
            "temporal_relation_result must be a mapping."
        )

    if (
        temporal_relation_result.get(
            "schema_version"
        )
        != "temporal_sequence_boundary_recurrence_validation_v1"
    ):
        raise TemporalIntelligenceError(
            "Stage K requires "
            "temporal_sequence_boundary_recurrence_validation_v1."
        )

    if (
        temporal_relation_result.get(
            "status"
        )
        != "TEMPORAL_SEQUENCE_BOUNDARY_RECURRENCE_VALIDATION_COMPLETE"
    ):
        raise TemporalIntelligenceError(
            "Stage-J Temporal relation validation must be complete."
        )

    if (
        temporal_relation_result.get(
            "phase"
        )
        != "4.6.13"
    ):
        raise TemporalIntelligenceError(
            "Stage K requires Phase 4.6.13 input."
        )

    if (
        temporal_relation_result.get(
            "patch"
        )
        != "4.6.13J"
    ):
        raise TemporalIntelligenceError(
            "Stage K requires canonical 4.6.13J input."
        )

    if (
        temporal_relation_result.get(
            "next_stage"
        )
        != "same_sentence_temporal_validation"
    ):
        raise TemporalIntelligenceError(
            "Stage J must hand off to same_sentence_temporal_validation."
        )

    if (
        temporal_relation_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise TemporalIntelligenceError(
            "Temporal Intelligence must remain transient."
        )

    procedural_statement_forms = {
        "imperative",
        "instruction",
        "instructional",
        "procedural",
        "directive",
    }

    def validate_candidate_same_sentence(
        candidate,
        unit,
    ):
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal candidate must be a mapping."
            )

        if not isinstance(
            unit,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Temporal Claim Unit must be a mapping."
            )

        if (
            candidate.get(
                "sequence_boundary_recurrence_validation_performed"
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                "Stage-J candidate validation must be complete."
            )

        if (
            candidate.get(
                "same_sentence_temporal_validated"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Same-sentence Temporal validation must not already be complete."
            )

        if (
            candidate.get(
                "cross_sentence_temporal_anchor_resolved"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Cross-sentence Temporal anchoring must remain pending."
            )

        relation = candidate.get(
            "temporal_relation_structure"
        )

        if not isinstance(
            relation,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Stage-K candidate requires Temporal relation structure."
            )

        relation_status = str(
            relation.get(
                "validation_status"
            )
            or ""
        )

        sentence_id = str(
            candidate.get(
                "sentence_id"
            )
            or unit.get(
                "sentence_id"
            )
            or ""
        )

        source_text = str(
            candidate.get(
                "source_text"
            )
            or unit.get(
                "text"
            )
            or ""
        )

        statement_form = str(
            unit.get(
                "statement_form"
            )
            or ""
        ).strip().lower()

        selected_anchor = candidate.get(
            "selected_temporal_anchor"
        )

        selected_participant = candidate.get(
            "selected_temporal_participant"
        )

        payload = {
            "validation_status":
                "NOT_APPLICABLE",

            "sentence_id":
                sentence_id
                or None,

            "source_text":
                source_text,

            "relation_family":
                relation.get(
                    "relation_family"
                ),

            "relation_type":
                relation.get(
                    "relation_type"
                ),

            "selected_temporal_anchor":
                (
                    dict(
                        selected_anchor
                    )
                    if isinstance(
                        selected_anchor,
                        Mapping,
                    )
                    else None
                ),

            "selected_temporal_participant":
                (
                    dict(
                        selected_participant
                    )
                    if isinstance(
                        selected_participant,
                        Mapping,
                    )
                    else None
                ),

            "anchor_within_same_sentence":
                False,

            "participant_grounding_already_article_local":
                isinstance(
                    selected_participant,
                    Mapping,
                ),

            "statement_form":
                statement_form
                or None,

            "procedural_or_instructional_form_detected":
                statement_form
                in procedural_statement_forms,

            "cross_sentence_search_performed":
                False,

            "cross_sentence_repair_performed":
                False,

            "new_anchor_inference_performed":
                False,

            "new_participant_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "derived_calculation_performed":
                False,

            "truth_assessment_performed":
                False,

            "validation_reason":
                "NO_STAGE_K_APPLICABLE_STRUCTURAL_RELATION",
        }

        if relation_status == "UNRESOLVED":
            payload.update({
                "validation_status":
                    "UNRESOLVED",

                "validation_reason":
                    "STAGE_J_RELATION_UNRESOLVED",
            })

            validated = dict(
                candidate
            )

            validated.update({
                "same_sentence_temporal_validation_performed":
                    True,

                "same_sentence_temporal_validated":
                    False,

                "same_sentence_temporal_validation":
                    payload,

                "cross_sentence_temporal_anchor_resolved":
                    False,
            })

            return validated

        if relation_status == "NOT_APPLICABLE":
            validated = dict(
                candidate
            )

            validated.update({
                "same_sentence_temporal_validation_performed":
                    True,

                "same_sentence_temporal_validated":
                    False,

                "same_sentence_temporal_validation":
                    payload,

                "cross_sentence_temporal_anchor_resolved":
                    False,
            })

            return validated

        if (
            relation_status
            != "STRUCTURALLY_VALIDATED"
        ):
            raise TemporalIntelligenceError(
                "Unknown Stage-J Temporal relation validation status."
            )

        if not sentence_id:
            payload.update({
                "validation_status":
                    "UNRESOLVED",

                "validation_reason":
                    "MISSING_SENTENCE_PROVENANCE",
            })

            validated = dict(
                candidate
            )

            validated.update({
                "same_sentence_temporal_validation_performed":
                    True,

                "same_sentence_temporal_validated":
                    False,

                "same_sentence_temporal_validation":
                    payload,

                "cross_sentence_temporal_anchor_resolved":
                    False,
            })

            return validated

        if not source_text:
            payload.update({
                "validation_status":
                    "UNRESOLVED",

                "validation_reason":
                    "MISSING_SENTENCE_TEXT",
            })

            validated = dict(
                candidate
            )

            validated.update({
                "same_sentence_temporal_validation_performed":
                    True,

                "same_sentence_temporal_validated":
                    False,

                "same_sentence_temporal_validation":
                    payload,

                "cross_sentence_temporal_anchor_resolved":
                    False,
            })

            return validated

        if not isinstance(
            selected_anchor,
            Mapping,
        ):
            payload.update({
                "validation_status":
                    "UNRESOLVED",

                "validation_reason":
                    "NO_SELECTED_TEMPORAL_ANCHOR",
            })

            validated = dict(
                candidate
            )

            validated.update({
                "same_sentence_temporal_validation_performed":
                    True,

                "same_sentence_temporal_validated":
                    False,

                "same_sentence_temporal_validation":
                    payload,

                "cross_sentence_temporal_anchor_resolved":
                    False,
            })

            return validated

        if not isinstance(
            selected_participant,
            Mapping,
        ):
            payload.update({
                "validation_status":
                    "UNRESOLVED",

                "validation_reason":
                    "NO_SELECTED_TEMPORAL_PARTICIPANT",
            })

            validated = dict(
                candidate
            )

            validated.update({
                "same_sentence_temporal_validation_performed":
                    True,

                "same_sentence_temporal_validated":
                    False,

                "same_sentence_temporal_validation":
                    payload,

                "cross_sentence_temporal_anchor_resolved":
                    False,
            })

            return validated

        anchor_text = str(
            selected_anchor.get(
                "anchor_text"
            )
            or ""
        )

        anchor_start = selected_anchor.get(
            "character_start"
        )

        anchor_end = selected_anchor.get(
            "character_end"
        )

        anchor_span_valid = (
            bool(
                anchor_text
            )
            and isinstance(
                anchor_start,
                int,
            )
            and not isinstance(
                anchor_start,
                bool,
            )
            and isinstance(
                anchor_end,
                int,
            )
            and not isinstance(
                anchor_end,
                bool,
            )
            and anchor_start >= 0
            and anchor_end > anchor_start
            and anchor_end <= len(
                source_text
            )
            and source_text[
                anchor_start:
                anchor_end
            ]
            == anchor_text
        )

        payload[
            "anchor_within_same_sentence"
        ] = anchor_span_valid

        if not anchor_span_valid:
            payload.update({
                "validation_status":
                    "UNRESOLVED",

                "validation_reason":
                    "SELECTED_ANCHOR_NOT_PROVEN_INSIDE_CANDIDATE_SENTENCE",
            })

            validated = dict(
                candidate
            )

            validated.update({
                "same_sentence_temporal_validation_performed":
                    True,

                "same_sentence_temporal_validated":
                    False,

                "same_sentence_temporal_validation":
                    payload,

                "cross_sentence_temporal_anchor_resolved":
                    False,
            })

            return validated

        if (
            statement_form
            in procedural_statement_forms
        ):
            payload.update({
                "validation_status":
                    "REJECTED_PROCEDURAL_FORM",

                "validation_reason":
                    "INSTRUCTIONAL_OR_PROCEDURAL_SENTENCE_NOT_PROMOTED_AS_TEMPORAL_FACT",
            })

            validated = dict(
                candidate
            )

            validated.update({
                "same_sentence_temporal_validation_performed":
                    True,

                "same_sentence_temporal_validated":
                    False,

                "same_sentence_temporal_validation":
                    payload,

                "cross_sentence_temporal_anchor_resolved":
                    False,
            })

            return validated

        payload.update({
            "validation_status":
                "SAME_SENTENCE_VALIDATED",

            "validation_reason":
                "STRUCTURAL_RELATION_PLUS_EXPLICIT_SAME_SENTENCE_ANCHOR_AND_ARTICLE_LOCAL_PARTICIPANT",
        })

        validated = dict(
            candidate
        )

        validated.update({
            "same_sentence_temporal_validation_performed":
                True,

            "same_sentence_temporal_validated":
                True,

            "same_sentence_temporal_validation":
                payload,

            "cross_sentence_temporal_anchor_resolved":
                False,

            "temporal_evidence_assessed":
                False,

            "semantic_duplicate_resolution_performed":
                False,

            "unstated_temporal_relation_inference_performed":
                False,

            "unstated_temporal_anchor_inference_performed":
                False,

            "unstated_duration_inference_performed":
                False,

            "unstated_recurrence_inference_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "similarity_reasoning_performed":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,
        })

        return validated

    source_candidates = list(
        temporal_relation_result.get(
            "temporal_candidates"
        )
        or []
    )

    source_units = list(
        temporal_relation_result.get(
            "temporal_claim_units"
        )
        or []
    )

    unit_by_id = {}

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "temporal_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise TemporalIntelligenceError(
                "Temporal Claim Unit ID is required."
            )

        if unit_id in unit_by_id:
            raise TemporalIntelligenceError(
                "Duplicate Temporal Claim Unit ID."
            )

        unit_by_id[
            unit_id
        ] = unit

    validated_candidates = []
    validated_by_id = {}

    same_sentence_validated_count = 0
    unresolved_count = 0
    rejected_procedural_count = 0
    not_applicable_count = 0

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "temporal_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise TemporalIntelligenceError(
                "Temporal Candidate ID is required."
            )

        if candidate_id in validated_by_id:
            raise TemporalIntelligenceError(
                "Duplicate Temporal Candidate ID."
            )

        unit_id = str(
            candidate.get(
                "temporal_claim_unit_id"
            )
            or ""
        )

        unit = unit_by_id.get(
            unit_id
        )

        if unit is None:
            raise TemporalIntelligenceError(
                "Temporal candidate references unknown claim unit."
            )

        validated = validate_candidate_same_sentence(
            candidate,
            unit,
        )

        status = validated[
            "same_sentence_temporal_validation"
        ][
            "validation_status"
        ]

        if status == "SAME_SENTENCE_VALIDATED":
            same_sentence_validated_count += 1

        elif status == "UNRESOLVED":
            unresolved_count += 1

        elif status == "REJECTED_PROCEDURAL_FORM":
            rejected_procedural_count += 1

        elif status == "NOT_APPLICABLE":
            not_applicable_count += 1

        else:
            raise TemporalIntelligenceError(
                "Unknown Stage-K validation status."
            )

        validated_candidates.append(
            validated
        )

        validated_by_id[
            candidate_id
        ] = validated

    validated_units = []
    validated_unit_by_id = {}

    for unit in source_units:
        unit_id = str(
            unit.get(
                "temporal_claim_unit_id"
            )
            or ""
        )

        state = dict(
            unit.get(
                "temporal_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "sequence_boundary_recurrence_validation"
            )
            != "COMPLETE"
        ):
            raise TemporalIntelligenceError(
                "Stage-J validation must be COMPLETE before K."
            )

        if (
            state.get(
                "same_sentence_temporal_validation"
            )
            != "PENDING"
        ):
            raise TemporalIntelligenceError(
                "Stage-K state must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "temporal_relation_validation_performed"
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                "Stage-J relation boundary is incomplete."
            )

        if (
            boundaries.get(
                "same_sentence_temporal_validation_performed"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Same-sentence boundary must be False before K."
            )

        if (
            boundaries.get(
                "cross_sentence_temporal_anchoring_performed"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Cross-sentence anchoring must remain False before K."
            )

        updated_candidates = []

        for old_candidate in (
            unit.get(
                "temporal_candidates"
            )
            or []
        ):
            candidate_id = str(
                old_candidate.get(
                    "temporal_candidate_id"
                )
                or ""
            )

            replacement = validated_by_id.get(
                candidate_id
            )

            if replacement is None:
                raise TemporalIntelligenceError(
                    "Stage-K candidate/unit mismatch."
                )

            updated_candidates.append(
                replacement
            )

        state[
            "same_sentence_temporal_validation"
        ] = "COMPLETE"

        boundaries[
            "same_sentence_temporal_validation_performed"
        ] = True

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "temporal_candidates":
                updated_candidates,

            "temporal_analysis_state":
                state,

            "processing_boundaries":
                boundaries,

            "same_sentence_validated_temporal_relation_count":
                sum(
                    1
                    for candidate
                    in updated_candidates
                    if candidate.get(
                        "same_sentence_temporal_validated"
                    )
                    is True
                ),
        })

        validated_units.append(
            updated_unit
        )

        validated_unit_by_id[
            unit_id
        ] = updated_unit

    validated_sections = []

    for section in (
        temporal_relation_result.get(
            "temporal_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "temporal_claim_units"
            )
            or []
        ):
            unit_id = str(
                old_unit.get(
                    "temporal_claim_unit_id"
                )
                or ""
            )

            replacement = validated_unit_by_id.get(
                unit_id
            )

            if replacement is None:
                raise TemporalIntelligenceError(
                    "Temporal section references unknown Stage-K unit."
                )

            section_units.append(
                replacement
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "temporal_candidates"
                )
                or []
            )
        ]

        validated_sections.append({
            **dict(
                section
            ),

            "temporal_claim_units":
                section_units,

            "temporal_candidates":
                section_candidates,

            "temporal_candidate_count":
                len(
                    section_candidates
                ),

            "same_sentence_validated_temporal_relation_count":
                sum(
                    1
                    for candidate
                    in section_candidates
                    if candidate.get(
                        "same_sentence_temporal_validated"
                    )
                    is True
                ),
        })

    top_boundaries = dict(
        temporal_relation_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        top_boundaries.get(
            "temporal_relation_validation_performed"
        )
        is not True
    ):
        raise TemporalIntelligenceError(
            "Top-level Stage-J relation boundary is incomplete."
        )

    if (
        top_boundaries.get(
            "same_sentence_temporal_validation_performed"
        )
        is not False
    ):
        raise TemporalIntelligenceError(
            "Top-level same-sentence validation must not already be performed."
        )

    if (
        top_boundaries.get(
            "cross_sentence_temporal_anchoring_performed"
        )
        is not False
    ):
        raise TemporalIntelligenceError(
            "Cross-sentence anchoring must remain pending."
        )

    top_boundaries[
        "same_sentence_temporal_validation_performed"
    ] = True

    result = dict(
        temporal_relation_result
    )

    result.update({
        "schema_version":
            "temporal_same_sentence_validation_v1",

        "patch":
            "4.6.13K",

        "status":
            "TEMPORAL_SAME_SENTENCE_VALIDATION_COMPLETE",

        "temporal_sections":
            validated_sections,

        "temporal_claim_units":
            validated_units,

        "temporal_candidates":
            validated_candidates,

        "same_sentence_temporal_validation_summary": {
            "candidate_count":
                len(
                    validated_candidates
                ),

            "same_sentence_validated_candidate_count":
                same_sentence_validated_count,

            "unresolved_candidate_count":
                unresolved_count,

            "rejected_procedural_candidate_count":
                rejected_procedural_count,

            "not_applicable_candidate_count":
                not_applicable_count,

            "candidate_count_accounted_for":
                (
                    same_sentence_validated_count
                    + unresolved_count
                    + rejected_procedural_count
                    + not_applicable_count
                    == len(
                        validated_candidates
                    )
                ),

            "cross_sentence_search_performed":
                False,

            "cross_sentence_repair_performed":
                False,

            "new_anchor_inference_performed":
                False,

            "new_participant_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "derived_calculation_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "similarity_reasoning_performed":
                False,

            "truth_assessment_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            top_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "cross_sentence_temporal_anchoring",
    })

    return result


def resolve_cross_sentence_temporal_anchoring_v1(
    same_sentence_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Resolve only conservative article-local cross-sentence Temporal
    anchoring after Stage-K same-sentence validation.

    Resolution is allowed only when:
    - Stage K left the candidate unresolved,
    - the unresolved candidate already carries one selected participant,
    - one immediately adjacent sentence in the same section contains
      a Stage-K same-sentence-validated Temporal candidate,
    - that adjacent candidate has the exact same semantic_object_ref,
    - relation family and relation type are identical,
    - that adjacent candidate has one explicit selected Temporal anchor.

    Stage L does NOT:
    - perform pronoun/coreference resolution,
    - perform fuzzy or embedding participant matching,
    - search beyond immediately adjacent sentences,
    - cross section boundaries,
    - infer a missing participant,
    - infer a new Temporal relation,
    - calculate durations,
    - perform evidence/confidence scoring,
    - resolve duplicates,
    - assess truth,
    - use external authority,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        same_sentence_result,
        Mapping,
    ):
        raise TemporalIntelligenceError(
            "same_sentence_result must be a mapping."
        )

    if (
        same_sentence_result.get(
            "schema_version"
        )
        != "temporal_same_sentence_validation_v1"
    ):
        raise TemporalIntelligenceError(
            "Stage L requires temporal_same_sentence_validation_v1."
        )

    if (
        same_sentence_result.get(
            "status"
        )
        != "TEMPORAL_SAME_SENTENCE_VALIDATION_COMPLETE"
    ):
        raise TemporalIntelligenceError(
            "Stage-K same-sentence validation must be complete."
        )

    if (
        same_sentence_result.get(
            "phase"
        )
        != "4.6.13"
    ):
        raise TemporalIntelligenceError(
            "Stage L requires Phase 4.6.13 input."
        )

    if (
        same_sentence_result.get(
            "patch"
        )
        != "4.6.13K"
    ):
        raise TemporalIntelligenceError(
            "Stage L requires canonical 4.6.13K input."
        )

    if (
        same_sentence_result.get(
            "next_stage"
        )
        != "cross_sentence_temporal_anchoring"
    ):
        raise TemporalIntelligenceError(
            "Stage K must hand off to "
            "cross_sentence_temporal_anchoring."
        )

    if (
        same_sentence_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise TemporalIntelligenceError(
            "Temporal Intelligence must remain transient."
        )

    source_units = list(
        same_sentence_result.get(
            "temporal_claim_units"
        )
        or []
    )

    unit_by_id = {}
    ordered_units = []

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "temporal_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise TemporalIntelligenceError(
                "Temporal Claim Unit ID is required."
            )

        if unit_id in unit_by_id:
            raise TemporalIntelligenceError(
                "Duplicate Temporal Claim Unit ID."
            )

        sentence_global_index = unit.get(
            "sentence_global_index"
        )

        if (
            not isinstance(
                sentence_global_index,
                int,
            )
            or isinstance(
                sentence_global_index,
                bool,
            )
        ):
            raise TemporalIntelligenceError(
                "Stage L requires integer sentence_global_index "
                "on every Temporal Claim Unit."
            )

        section_id = str(
            unit.get(
                "section_id"
            )
            or ""
        )

        if not section_id:
            raise TemporalIntelligenceError(
                "Stage L requires section_id "
                "on every Temporal Claim Unit."
            )

        unit_by_id[
            unit_id
        ] = unit

        ordered_units.append(
            unit
        )

    ordered_units.sort(
        key=lambda unit: (
            unit[
                "sentence_global_index"
            ],
            str(
                unit.get(
                    "temporal_claim_unit_id"
                )
                or ""
            ),
        )
    )

    seen_global_indexes = set()

    for unit in ordered_units:
        index = unit[
            "sentence_global_index"
        ]

        if index in seen_global_indexes:
            raise TemporalIntelligenceError(
                "Duplicate sentence_global_index is ambiguous "
                "for Stage-L adjacency."
            )

        seen_global_indexes.add(
            index
        )

    unit_by_global_index = {
        unit[
            "sentence_global_index"
        ]:
            unit
        for unit in ordered_units
    }

    def participant_ref(
        candidate,
    ):
        selected = candidate.get(
            "selected_temporal_participant"
        )

        if not isinstance(
            selected,
            Mapping,
        ):
            return None

        value = str(
            selected.get(
                "semantic_object_ref"
            )
            or ""
        )

        return value or None

    def relation_identity(
        candidate,
    ):
        relation = candidate.get(
            "temporal_relation_structure"
        )

        if not isinstance(
            relation,
            Mapping,
        ):
            return (
                None,
                None,
            )

        family = str(
            relation.get(
                "relation_family"
            )
            or ""
        )

        relation_type = str(
            relation.get(
                "relation_type"
            )
            or ""
        )

        return (
            family or None,
            relation_type or None,
        )

    def explicit_anchor(
        candidate,
    ):
        anchor = candidate.get(
            "selected_temporal_anchor"
        )

        if not isinstance(
            anchor,
            Mapping,
        ):
            return None

        if (
            anchor.get(
                "explicit_article_evidence"
            )
            is not True
        ):
            return None

        anchor_text = str(
            anchor.get(
                "anchor_text"
            )
            or ""
        )

        if not anchor_text:
            return None

        return dict(
            anchor
        )

    def eligible_adjacent_matches(
        candidate,
        source_unit,
    ):
        current_index = source_unit[
            "sentence_global_index"
        ]

        current_section = str(
            source_unit.get(
                "section_id"
            )
            or ""
        )

        current_participant = participant_ref(
            candidate
        )

        current_family, current_type = (
            relation_identity(
                candidate
            )
        )

        if (
            current_participant is None
            or current_family is None
            or current_type is None
        ):
            return []

        matches = []

        for adjacent_index in (
            current_index - 1,
            current_index + 1,
        ):
            adjacent_unit = (
                unit_by_global_index.get(
                    adjacent_index
                )
            )

            if adjacent_unit is None:
                continue

            if (
                str(
                    adjacent_unit.get(
                        "section_id"
                    )
                    or ""
                )
                != current_section
            ):
                continue

            for adjacent_candidate in (
                adjacent_unit.get(
                    "temporal_candidates"
                )
                or []
            ):
                if not isinstance(
                    adjacent_candidate,
                    Mapping,
                ):
                    raise TemporalIntelligenceError(
                        "Adjacent Temporal candidate must be a mapping."
                    )

                if (
                    adjacent_candidate.get(
                        "same_sentence_temporal_validated"
                    )
                    is not True
                ):
                    continue

                if (
                    participant_ref(
                        adjacent_candidate
                    )
                    != current_participant
                ):
                    continue

                adjacent_family, adjacent_type = (
                    relation_identity(
                        adjacent_candidate
                    )
                )

                if (
                    adjacent_family
                    != current_family
                    or adjacent_type
                    != current_type
                ):
                    continue

                anchor = explicit_anchor(
                    adjacent_candidate
                )

                if anchor is None:
                    continue

                matches.append({
                    "source_temporal_candidate_id":
                        adjacent_candidate.get(
                            "temporal_candidate_id"
                        ),

                    "source_temporal_claim_unit_id":
                        adjacent_unit.get(
                            "temporal_claim_unit_id"
                        ),

                    "source_sentence_id":
                        adjacent_candidate.get(
                            "sentence_id"
                        )
                        or adjacent_unit.get(
                            "sentence_id"
                        ),

                    "source_sentence_global_index":
                        adjacent_index,

                    "sentence_distance":
                        abs(
                            adjacent_index
                            - current_index
                        ),

                    "section_id":
                        current_section,

                    "semantic_object_ref":
                        current_participant,

                    "relation_family":
                        current_family,

                    "relation_type":
                        current_type,

                    "selected_temporal_anchor":
                        anchor,

                    "explicit_article_evidence":
                        True,

                    "coreference_resolution_performed":
                        False,

                    "fuzzy_matching_performed":
                        False,

                    "embedding_matching_performed":
                        False,
                })

        matches.sort(
            key=lambda item: (
                item[
                    "sentence_distance"
                ],
                item[
                    "source_sentence_global_index"
                ],
                str(
                    item[
                        "source_temporal_candidate_id"
                    ]
                    or ""
                ),
            )
        )

        return matches

    source_candidates = list(
        same_sentence_result.get(
            "temporal_candidates"
        )
        or []
    )

    resolved_candidates = []
    resolved_by_id = {}

    cross_sentence_resolved_count = 0
    no_resolution_needed_count = 0
    unresolved_count = 0
    ineligible_count = 0
    ambiguous_count = 0

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "temporal_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise TemporalIntelligenceError(
                "Temporal Candidate ID is required."
            )

        if candidate_id in resolved_by_id:
            raise TemporalIntelligenceError(
                "Duplicate Temporal Candidate ID."
            )

        if (
            candidate.get(
                "same_sentence_temporal_validation_performed"
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                "Stage-K candidate validation must be complete."
            )

        if (
            candidate.get(
                "cross_sentence_temporal_anchor_resolved"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Cross-sentence anchoring must not already be resolved."
            )

        unit_id = str(
            candidate.get(
                "temporal_claim_unit_id"
            )
            or ""
        )

        source_unit = unit_by_id.get(
            unit_id
        )

        if source_unit is None:
            raise TemporalIntelligenceError(
                "Temporal candidate references unknown claim unit."
            )

        k_payload = candidate.get(
            "same_sentence_temporal_validation"
        )

        if not isinstance(
            k_payload,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Stage-L candidate requires Stage-K validation payload."
            )

        k_status = str(
            k_payload.get(
                "validation_status"
            )
            or ""
        )

        payload = {
            "resolution_status":
                "UNRESOLVED",

            "resolution_reason":
                "NO_ELIGIBLE_ADJACENT_TEMPORAL_ANCHOR",

            "source_sentence_global_index":
                source_unit.get(
                    "sentence_global_index"
                ),

            "section_id":
                source_unit.get(
                    "section_id"
                ),

            "adjacent_sentence_only":
                True,

            "same_section_only":
                True,

            "exact_semantic_object_ref_required":
                True,

            "same_relation_identity_required":
                True,

            "eligible_adjacent_match_count":
                0,

            "eligible_adjacent_matches":
                [],

            "selected_cross_sentence_anchor":
                None,

            "selected_cross_sentence_source_candidate_id":
                None,

            "selected_cross_sentence_source_unit_id":
                None,

            "selected_cross_sentence_source_sentence_id":
                None,

            "sentence_distance":
                None,

            "cross_sentence_search_performed":
                False,

            "cross_sentence_anchor_borrowing_performed":
                False,

            "coreference_resolution_performed":
                False,

            "fuzzy_matching_performed":
                False,

            "embedding_matching_performed":
                False,

            "new_participant_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "cross_section_search_performed":
                False,

            "multi_sentence_range_search_performed":
                False,

            "truth_assessment_performed":
                False,
        }

        if k_status == "SAME_SENTENCE_VALIDATED":
            payload.update({
                "resolution_status":
                    "NO_CROSS_SENTENCE_NEEDED",

                "resolution_reason":
                    "SAME_SENTENCE_TEMPORAL_RELATION_ALREADY_VALIDATED",
            })

            no_resolution_needed_count += 1

        elif k_status in {
            "REJECTED_PROCEDURAL_FORM",
            "NOT_APPLICABLE",
        }:
            payload.update({
                "resolution_status":
                    "INELIGIBLE",

                "resolution_reason":
                    (
                        "PROCEDURAL_SENTENCE_INELIGIBLE"
                        if k_status
                        == "REJECTED_PROCEDURAL_FORM"
                        else
                        "STAGE_K_NOT_APPLICABLE"
                    ),
            })

            ineligible_count += 1

        elif k_status == "UNRESOLVED":
            payload[
                "cross_sentence_search_performed"
            ] = True

            matches = eligible_adjacent_matches(
                candidate,
                source_unit,
            )

            payload[
                "eligible_adjacent_matches"
            ] = matches

            payload[
                "eligible_adjacent_match_count"
            ] = len(
                matches
            )

            if len(matches) == 1:
                selected = matches[0]

                payload.update({
                    "resolution_status":
                        "CROSS_SENTENCE_ANCHOR_RESOLVED",

                    "resolution_reason":
                        "UNIQUE_ADJACENT_SAME_PARTICIPANT_SAME_RELATION_ANCHOR",

                    "selected_cross_sentence_anchor":
                        dict(
                            selected[
                                "selected_temporal_anchor"
                            ]
                        ),

                    "selected_cross_sentence_source_candidate_id":
                        selected[
                            "source_temporal_candidate_id"
                        ],

                    "selected_cross_sentence_source_unit_id":
                        selected[
                            "source_temporal_claim_unit_id"
                        ],

                    "selected_cross_sentence_source_sentence_id":
                        selected[
                            "source_sentence_id"
                        ],

                    "sentence_distance":
                        selected[
                            "sentence_distance"
                        ],

                    "cross_sentence_anchor_borrowing_performed":
                        True,
                })

                cross_sentence_resolved_count += 1

            elif len(matches) > 1:
                payload.update({
                    "resolution_status":
                        "AMBIGUOUS",

                    "resolution_reason":
                        "MULTIPLE_ELIGIBLE_ADJACENT_TEMPORAL_ANCHORS",
                })

                ambiguous_count += 1

            else:
                unresolved_count += 1

        else:
            raise TemporalIntelligenceError(
                "Unknown Stage-K validation status."
            )

        resolved = dict(
            candidate
        )

        resolved.update({
            "cross_sentence_temporal_anchoring_performed":
                True,

            "cross_sentence_temporal_anchor_resolved":
                payload[
                    "resolution_status"
                ]
                == "CROSS_SENTENCE_ANCHOR_RESOLVED",

            "cross_sentence_temporal_anchoring":
                payload,

            "temporal_evidence_assessed":
                False,

            "semantic_duplicate_resolution_performed":
                False,

            "unstated_temporal_relation_inference_performed":
                False,

            "unstated_temporal_anchor_inference_performed":
                False,

            "unstated_duration_inference_performed":
                False,

            "unstated_recurrence_inference_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "similarity_reasoning_performed":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,
        })

        resolved_candidates.append(
            resolved
        )

        resolved_by_id[
            candidate_id
        ] = resolved

    resolved_units = []
    resolved_unit_by_id = {}

    for unit in source_units:
        unit_id = str(
            unit.get(
                "temporal_claim_unit_id"
            )
            or ""
        )

        state = dict(
            unit.get(
                "temporal_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "same_sentence_temporal_validation"
            )
            != "COMPLETE"
        ):
            raise TemporalIntelligenceError(
                "Stage-K validation must be COMPLETE before L."
            )

        if (
            state.get(
                "cross_sentence_temporal_anchoring"
            )
            != "PENDING"
        ):
            raise TemporalIntelligenceError(
                "Stage-L state must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "same_sentence_temporal_validation_performed"
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                "Stage-K boundary is incomplete."
            )

        if (
            boundaries.get(
                "cross_sentence_temporal_anchoring_performed"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Cross-sentence anchoring must be False before L."
            )

        if (
            boundaries.get(
                "temporal_evidence_assessment_performed"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Temporal evidence assessment must remain pending."
            )

        updated_candidates = []

        for old_candidate in (
            unit.get(
                "temporal_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Unit Temporal candidate must be a mapping."
                )

            candidate_id = str(
                old_candidate.get(
                    "temporal_candidate_id"
                )
                or ""
            )

            replacement = resolved_by_id.get(
                candidate_id
            )

            if replacement is None:
                raise TemporalIntelligenceError(
                    "Stage-L candidate/unit mismatch."
                )

            updated_candidates.append(
                replacement
            )

        state[
            "cross_sentence_temporal_anchoring"
        ] = "COMPLETE"

        boundaries[
            "cross_sentence_temporal_anchoring_performed"
        ] = True

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "temporal_candidates":
                updated_candidates,

            "temporal_analysis_state":
                state,

            "processing_boundaries":
                boundaries,

            "cross_sentence_resolved_temporal_anchor_count":
                sum(
                    1
                    for candidate
                    in updated_candidates
                    if candidate.get(
                        "cross_sentence_temporal_anchor_resolved"
                    )
                    is True
                ),
        })

        resolved_units.append(
            updated_unit
        )

        resolved_unit_by_id[
            unit_id
        ] = updated_unit

    resolved_sections = []

    for section in (
        same_sentence_result.get(
            "temporal_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "temporal_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Section Temporal Claim Unit must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "temporal_claim_unit_id"
                )
                or ""
            )

            replacement = resolved_unit_by_id.get(
                unit_id
            )

            if replacement is None:
                raise TemporalIntelligenceError(
                    "Temporal section references unknown Stage-L unit."
                )

            section_units.append(
                replacement
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "temporal_candidates"
                )
                or []
            )
        ]

        resolved_sections.append({
            **dict(
                section
            ),

            "temporal_claim_units":
                section_units,

            "temporal_candidates":
                section_candidates,

            "temporal_candidate_count":
                len(
                    section_candidates
                ),

            "cross_sentence_resolved_temporal_anchor_count":
                sum(
                    1
                    for candidate
                    in section_candidates
                    if candidate.get(
                        "cross_sentence_temporal_anchor_resolved"
                    )
                    is True
                ),
        })

    top_boundaries = dict(
        same_sentence_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        top_boundaries.get(
            "same_sentence_temporal_validation_performed"
        )
        is not True
    ):
        raise TemporalIntelligenceError(
            "Top-level Stage-K boundary is incomplete."
        )

    if (
        top_boundaries.get(
            "cross_sentence_temporal_anchoring_performed"
        )
        is not False
    ):
        raise TemporalIntelligenceError(
            "Top-level cross-sentence anchoring must "
            "not already be performed."
        )

    if (
        top_boundaries.get(
            "temporal_evidence_assessment_performed"
        )
        is not False
    ):
        raise TemporalIntelligenceError(
            "Evidence assessment must remain pending before L."
        )

    top_boundaries[
        "cross_sentence_temporal_anchoring_performed"
    ] = True

    result = dict(
        same_sentence_result
    )

    result.update({
        "schema_version":
            "temporal_cross_sentence_anchoring_v1",

        "patch":
            "4.6.13L",

        "status":
            "TEMPORAL_CROSS_SENTENCE_ANCHORING_COMPLETE",

        "temporal_sections":
            resolved_sections,

        "temporal_claim_units":
            resolved_units,

        "temporal_candidates":
            resolved_candidates,

        "cross_sentence_temporal_anchoring_summary": {
            "candidate_count":
                len(
                    resolved_candidates
                ),

            "cross_sentence_resolved_candidate_count":
                cross_sentence_resolved_count,

            "no_cross_sentence_needed_candidate_count":
                no_resolution_needed_count,

            "unresolved_candidate_count":
                unresolved_count,

            "ineligible_candidate_count":
                ineligible_count,

            "ambiguous_candidate_count":
                ambiguous_count,

            "candidate_count_accounted_for":
                (
                    cross_sentence_resolved_count
                    + no_resolution_needed_count
                    + unresolved_count
                    + ineligible_count
                    + ambiguous_count
                    == len(
                        resolved_candidates
                    )
                ),

            "adjacent_sentence_only":
                True,

            "same_section_only":
                True,

            "exact_semantic_object_ref_required":
                True,

            "same_relation_identity_required":
                True,

            "maximum_sentence_distance":
                1,

            "coreference_resolution_performed":
                False,

            "fuzzy_matching_performed":
                False,

            "embedding_matching_performed":
                False,

            "new_participant_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "cross_section_search_performed":
                False,

            "multi_sentence_range_search_performed":
                False,

            "evidence_assessment_performed":
                False,

            "duplicate_resolution_performed":
                False,

            "truth_assessment_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            top_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "temporal_evidence_confidence_assessment",
    })

    return result


def assess_temporal_evidence_confidence_v1(
    cross_sentence_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Assess deterministic article-local evidence strength for Temporal
    candidates after Stage-L cross-sentence anchoring.

    This is evidence confidence, not factual truth probability.

    Evidence hierarchy:
    - HIGH:
        explicit same-sentence Temporal relation validated by K.
    - MODERATE:
        uniquely resolved immediately adjacent cross-sentence anchor by L.
    - LOW:
        ambiguous competing adjacent evidence.
    - INSUFFICIENT:
        unresolved article-local Temporal evidence.
    - NOT_APPLICABLE:
        procedural/ineligible or non-applicable Temporal structures.

    Stage M does NOT:
    - assess factual/scientific truth,
    - call external authority,
    - use Semantic Memory,
    - perform new relation or participant inference,
    - perform coreference, fuzzy, or embedding matching,
    - calculate derived Temporal values,
    - resolve duplicates,
    - consolidate article Temporal intelligence,
    - persist intelligence.
    """

    if not isinstance(
        cross_sentence_result,
        Mapping,
    ):
        raise TemporalIntelligenceError(
            "cross_sentence_result must be a mapping."
        )

    if (
        cross_sentence_result.get(
            "schema_version"
        )
        != "temporal_cross_sentence_anchoring_v1"
    ):
        raise TemporalIntelligenceError(
            "Stage M requires temporal_cross_sentence_anchoring_v1."
        )

    if (
        cross_sentence_result.get(
            "status"
        )
        != "TEMPORAL_CROSS_SENTENCE_ANCHORING_COMPLETE"
    ):
        raise TemporalIntelligenceError(
            "Stage-L cross-sentence anchoring must be complete."
        )

    if (
        cross_sentence_result.get(
            "phase"
        )
        != "4.6.13"
    ):
        raise TemporalIntelligenceError(
            "Stage M requires Phase 4.6.13 input."
        )

    if (
        cross_sentence_result.get(
            "patch"
        )
        != "4.6.13L"
    ):
        raise TemporalIntelligenceError(
            "Stage M requires canonical 4.6.13L input."
        )

    if (
        cross_sentence_result.get(
            "next_stage"
        )
        != "temporal_evidence_confidence_assessment"
    ):
        raise TemporalIntelligenceError(
            "Stage L must hand off to "
            "temporal_evidence_confidence_assessment."
        )

    if (
        cross_sentence_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise TemporalIntelligenceError(
            "Temporal Intelligence must remain transient."
        )

    def selected_participant_present(
        candidate,
    ):
        participant = candidate.get(
            "selected_temporal_participant"
        )

        if not isinstance(
            participant,
            Mapping,
        ):
            return False

        return bool(
            str(
                participant.get(
                    "semantic_object_ref"
                )
                or ""
            )
        )

    def explicit_anchor_present(
        anchor,
    ):
        if not isinstance(
            anchor,
            Mapping,
        ):
            return False

        return (
            anchor.get(
                "explicit_article_evidence"
            )
            is True
            and bool(
                str(
                    anchor.get(
                        "anchor_text"
                    )
                    or ""
                )
            )
        )

    def assess_candidate(
        candidate,
    ):
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal candidate must be a mapping."
            )

        if (
            candidate.get(
                "cross_sentence_temporal_anchoring_performed"
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                "Stage-L candidate anchoring must be complete."
            )

        if (
            candidate.get(
                "temporal_evidence_assessed"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Temporal evidence must not already be assessed."
            )

        if (
            candidate.get(
                "semantic_duplicate_resolution_performed"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Duplicate resolution must remain pending before M."
            )

        k_payload = candidate.get(
            "same_sentence_temporal_validation"
        )

        l_payload = candidate.get(
            "cross_sentence_temporal_anchoring"
        )

        relation = candidate.get(
            "temporal_relation_structure"
        )

        if not isinstance(
            k_payload,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Stage M requires Stage-K validation payload."
            )

        if not isinstance(
            l_payload,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Stage M requires Stage-L anchoring payload."
            )

        if not isinstance(
            relation,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Stage M requires Temporal relation structure."
            )

        k_status = str(
            k_payload.get(
                "validation_status"
            )
            or ""
        )

        l_status = str(
            l_payload.get(
                "resolution_status"
            )
            or ""
        )

        relation_status = str(
            relation.get(
                "validation_status"
            )
            or ""
        )

        participant_present = (
            selected_participant_present(
                candidate
            )
        )

        same_sentence_anchor_explicit = (
            explicit_anchor_present(
                candidate.get(
                    "selected_temporal_anchor"
                )
            )
        )

        cross_sentence_anchor = (
            l_payload.get(
                "selected_cross_sentence_anchor"
            )
        )

        cross_sentence_anchor_explicit = (
            explicit_anchor_present(
                cross_sentence_anchor
            )
        )

        eligible_match_count = (
            l_payload.get(
                "eligible_adjacent_match_count"
            )
        )

        if not isinstance(
            eligible_match_count,
            int,
        ) or isinstance(
            eligible_match_count,
            bool,
        ) or eligible_match_count < 0:
            raise TemporalIntelligenceError(
                "Stage-L eligible adjacent match count is invalid."
            )

        sentence_distance = (
            l_payload.get(
                "sentence_distance"
            )
        )

        if (
            sentence_distance is not None
            and (
                not isinstance(
                    sentence_distance,
                    int,
                )
                or isinstance(
                    sentence_distance,
                    bool,
                )
                or sentence_distance < 0
            )
        ):
            raise TemporalIntelligenceError(
                "Stage-L sentence distance is invalid."
            )

        payload = {
            "assessment_status":
                "ASSESSED",

            "evidence_class":
                None,

            "evidence_score":
                None,

            "evidence_basis":
                None,

            "stage_k_validation_status":
                k_status,

            "stage_l_resolution_status":
                l_status,

            "relation_validation_status":
                relation_status,

            "participant_grounding_present":
                participant_present,

            "same_sentence_explicit_anchor_present":
                same_sentence_anchor_explicit,

            "cross_sentence_explicit_anchor_present":
                cross_sentence_anchor_explicit,

            "eligible_adjacent_match_count":
                eligible_match_count,

            "sentence_distance":
                sentence_distance,

            "ambiguity_present":
                l_status
                == "AMBIGUOUS",

            "same_sentence_support":
                k_status
                == "SAME_SENTENCE_VALIDATED",

            "cross_sentence_support":
                l_status
                == "CROSS_SENTENCE_ANCHOR_RESOLVED",

            "article_local_only":
                True,

            "deterministic_evidence_scoring":
                True,

            "factual_truth_probability":
                None,

            "model_probability_used":
                False,

            "external_authority_checked":
                False,

            "semantic_memory_used":
                False,

            "coreference_resolution_performed":
                False,

            "fuzzy_matching_performed":
                False,

            "embedding_matching_performed":
                False,

            "new_participant_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "derived_calculation_performed":
                False,

            "duplicate_resolution_performed":
                False,

            "truth_assessment_performed":
                False,
        }

        if (
            k_status
            == "SAME_SENTENCE_VALIDATED"
            and l_status
            == "NO_CROSS_SENTENCE_NEEDED"
        ):
            if (
                not participant_present
                or not same_sentence_anchor_explicit
                or relation_status
                != "STRUCTURALLY_VALIDATED"
            ):
                raise TemporalIntelligenceError(
                    "High-confidence same-sentence Temporal evidence "
                    "requires explicit anchor, participant, and "
                    "structurally validated relation."
                )

            payload.update({
                "evidence_class":
                    "HIGH",

                "evidence_score":
                    0.95,

                "evidence_basis":
                    "EXPLICIT_SAME_SENTENCE_RELATION_ANCHOR_AND_PARTICIPANT",
            })

        elif (
            k_status
            == "UNRESOLVED"
            and l_status
            == "CROSS_SENTENCE_ANCHOR_RESOLVED"
        ):
            if (
                not participant_present
                or not cross_sentence_anchor_explicit
                or eligible_match_count
                != 1
                or sentence_distance
                != 1
                or relation_status
                != "STRUCTURALLY_VALIDATED"
            ):
                raise TemporalIntelligenceError(
                    "Moderate cross-sentence Temporal evidence "
                    "requires one explicit adjacent anchor, exact "
                    "participant, and structurally validated relation."
                )

            payload.update({
                "evidence_class":
                    "MODERATE",

                "evidence_score":
                    0.80,

                "evidence_basis":
                    "UNIQUE_ADJACENT_EXPLICIT_ANCHOR_WITH_EXACT_PARTICIPANT_AND_RELATION",
            })

        elif (
            k_status
            == "UNRESOLVED"
            and l_status
            == "AMBIGUOUS"
        ):
            if eligible_match_count < 2:
                raise TemporalIntelligenceError(
                    "Ambiguous Temporal evidence requires "
                    "multiple eligible adjacent matches."
                )

            payload.update({
                "evidence_class":
                    "LOW",

                "evidence_score":
                    0.35,

                "evidence_basis":
                    "MULTIPLE_COMPETING_ADJACENT_TEMPORAL_ANCHORS",
            })

        elif (
            k_status
            == "UNRESOLVED"
            and l_status
            == "UNRESOLVED"
        ):
            payload.update({
                "evidence_class":
                    "INSUFFICIENT",

                "evidence_score":
                    0.15,

                "evidence_basis":
                    "NO_SUFFICIENT_ARTICLE_LOCAL_TEMPORAL_ANCHOR_SUPPORT",
            })

        elif (
            k_status
            in {
                "REJECTED_PROCEDURAL_FORM",
                "NOT_APPLICABLE",
            }
            and l_status
            == "INELIGIBLE"
        ):
            payload.update({
                "assessment_status":
                    "NOT_APPLICABLE",

                "evidence_class":
                    "NOT_APPLICABLE",

                "evidence_score":
                    None,

                "evidence_basis":
                    (
                        "PROCEDURAL_TEMPORAL_STRUCTURE_NOT_PROMOTED"
                        if k_status
                        == "REJECTED_PROCEDURAL_FORM"
                        else
                        "TEMPORAL_RELATION_NOT_APPLICABLE"
                    ),
            })

        else:
            raise TemporalIntelligenceError(
                "Unsupported Stage-K/Stage-L evidence-state combination."
            )

        assessed = dict(
            candidate
        )

        assessed.update({
            "temporal_evidence_assessed":
                True,

            "temporal_evidence_confidence":
                payload,

            "semantic_duplicate_resolution_performed":
                False,

            "unstated_temporal_relation_inference_performed":
                False,

            "unstated_temporal_anchor_inference_performed":
                False,

            "unstated_duration_inference_performed":
                False,

            "unstated_recurrence_inference_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "similarity_reasoning_performed":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,
        })

        return assessed

    source_candidates = list(
        cross_sentence_result.get(
            "temporal_candidates"
        )
        or []
    )

    assessed_candidates = []
    assessed_by_id = {}

    class_counts = {
        "HIGH":
            0,

        "MODERATE":
            0,

        "LOW":
            0,

        "INSUFFICIENT":
            0,

        "NOT_APPLICABLE":
            0,
    }

    score_total = 0.0
    scored_candidate_count = 0

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "temporal_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise TemporalIntelligenceError(
                "Temporal Candidate ID is required."
            )

        if candidate_id in assessed_by_id:
            raise TemporalIntelligenceError(
                "Duplicate Temporal Candidate ID."
            )

        assessed = assess_candidate(
            candidate
        )

        evidence = assessed[
            "temporal_evidence_confidence"
        ]

        evidence_class = evidence[
            "evidence_class"
        ]

        if evidence_class not in class_counts:
            raise TemporalIntelligenceError(
                "Unknown Temporal evidence class."
            )

        class_counts[
            evidence_class
        ] += 1

        score = evidence[
            "evidence_score"
        ]

        if score is not None:
            if (
                not isinstance(
                    score,
                    (
                        int,
                        float,
                    ),
                )
                or isinstance(
                    score,
                    bool,
                )
                or score < 0.0
                or score > 1.0
            ):
                raise TemporalIntelligenceError(
                    "Temporal evidence score must be within [0, 1]."
                )

            score_total += float(
                score
            )

            scored_candidate_count += 1

        assessed_candidates.append(
            assessed
        )

        assessed_by_id[
            candidate_id
        ] = assessed

    source_units = list(
        cross_sentence_result.get(
            "temporal_claim_units"
        )
        or []
    )

    assessed_units = []
    assessed_unit_by_id = {}

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "temporal_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise TemporalIntelligenceError(
                "Temporal Claim Unit ID is required."
            )

        if unit_id in assessed_unit_by_id:
            raise TemporalIntelligenceError(
                "Duplicate Temporal Claim Unit ID."
            )

        state = dict(
            unit.get(
                "temporal_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "cross_sentence_temporal_anchoring"
            )
            != "COMPLETE"
        ):
            raise TemporalIntelligenceError(
                "Stage-L anchoring must be COMPLETE before M."
            )

        if (
            state.get(
                "temporal_evidence_assessment"
            )
            != "PENDING"
        ):
            raise TemporalIntelligenceError(
                "Stage-M state must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "cross_sentence_temporal_anchoring_performed"
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                "Stage-L boundary is incomplete."
            )

        if (
            boundaries.get(
                "temporal_evidence_assessment_performed"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Temporal evidence assessment must be False before M."
            )

        if (
            boundaries.get(
                "temporal_duplicate_resolution_performed"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Duplicate resolution must remain pending before M."
            )

        updated_candidates = []

        for old_candidate in (
            unit.get(
                "temporal_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Unit Temporal candidate must be a mapping."
                )

            candidate_id = str(
                old_candidate.get(
                    "temporal_candidate_id"
                )
                or ""
            )

            replacement = assessed_by_id.get(
                candidate_id
            )

            if replacement is None:
                raise TemporalIntelligenceError(
                    "Stage-M candidate/unit mismatch."
                )

            updated_candidates.append(
                replacement
            )

        state[
            "temporal_evidence_assessment"
        ] = "COMPLETE"

        boundaries[
            "temporal_evidence_assessment_performed"
        ] = True

        unit_scores = [
            candidate[
                "temporal_evidence_confidence"
            ][
                "evidence_score"
            ]
            for candidate
            in updated_candidates
            if candidate[
                "temporal_evidence_confidence"
            ][
                "evidence_score"
            ]
            is not None
        ]

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "temporal_candidates":
                updated_candidates,

            "temporal_analysis_state":
                state,

            "processing_boundaries":
                boundaries,

            "temporal_evidence_assessed_candidate_count":
                len(
                    updated_candidates
                ),

            "mean_temporal_evidence_score":
                (
                    round(
                        sum(
                            unit_scores
                        )
                        / len(
                            unit_scores
                        ),
                        6,
                    )
                    if unit_scores
                    else None
                ),
        })

        assessed_units.append(
            updated_unit
        )

        assessed_unit_by_id[
            unit_id
        ] = updated_unit

    assessed_sections = []

    for section in (
        cross_sentence_result.get(
            "temporal_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "temporal_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Section Temporal Claim Unit must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "temporal_claim_unit_id"
                )
                or ""
            )

            replacement = assessed_unit_by_id.get(
                unit_id
            )

            if replacement is None:
                raise TemporalIntelligenceError(
                    "Temporal section references unknown Stage-M unit."
                )

            section_units.append(
                replacement
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "temporal_candidates"
                )
                or []
            )
        ]

        section_scores = [
            candidate[
                "temporal_evidence_confidence"
            ][
                "evidence_score"
            ]
            for candidate
            in section_candidates
            if candidate[
                "temporal_evidence_confidence"
            ][
                "evidence_score"
            ]
            is not None
        ]

        assessed_sections.append({
            **dict(
                section
            ),

            "temporal_claim_units":
                section_units,

            "temporal_candidates":
                section_candidates,

            "temporal_candidate_count":
                len(
                    section_candidates
                ),

            "mean_temporal_evidence_score":
                (
                    round(
                        sum(
                            section_scores
                        )
                        / len(
                            section_scores
                        ),
                        6,
                    )
                    if section_scores
                    else None
                ),
        })

    top_boundaries = dict(
        cross_sentence_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        top_boundaries.get(
            "cross_sentence_temporal_anchoring_performed"
        )
        is not True
    ):
        raise TemporalIntelligenceError(
            "Top-level Stage-L boundary is incomplete."
        )

    if (
        top_boundaries.get(
            "temporal_evidence_assessment_performed"
        )
        is not False
    ):
        raise TemporalIntelligenceError(
            "Top-level evidence assessment must not "
            "already be performed."
        )

    if (
        top_boundaries.get(
            "temporal_duplicate_resolution_performed"
        )
        is not False
    ):
        raise TemporalIntelligenceError(
            "Top-level duplicate resolution must remain pending."
        )

    top_boundaries[
        "temporal_evidence_assessment_performed"
    ] = True

    result = dict(
        cross_sentence_result
    )

    result.update({
        "schema_version":
            "temporal_evidence_confidence_assessment_v1",

        "patch":
            "4.6.13M",

        "status":
            "TEMPORAL_EVIDENCE_CONFIDENCE_ASSESSMENT_COMPLETE",

        "temporal_sections":
            assessed_sections,

        "temporal_claim_units":
            assessed_units,

        "temporal_candidates":
            assessed_candidates,

        "temporal_evidence_confidence_summary": {
            "candidate_count":
                len(
                    assessed_candidates
                ),

            "high_evidence_candidate_count":
                class_counts[
                    "HIGH"
                ],

            "moderate_evidence_candidate_count":
                class_counts[
                    "MODERATE"
                ],

            "low_evidence_candidate_count":
                class_counts[
                    "LOW"
                ],

            "insufficient_evidence_candidate_count":
                class_counts[
                    "INSUFFICIENT"
                ],

            "not_applicable_candidate_count":
                class_counts[
                    "NOT_APPLICABLE"
                ],

            "candidate_count_accounted_for":
                sum(
                    class_counts.values()
                )
                == len(
                    assessed_candidates
                ),

            "scored_candidate_count":
                scored_candidate_count,

            "mean_temporal_evidence_score":
                (
                    round(
                        score_total
                        / scored_candidate_count,
                        6,
                    )
                    if scored_candidate_count
                    else None
                ),

            "same_sentence_score":
                0.95,

            "unique_adjacent_cross_sentence_score":
                0.80,

            "ambiguous_score":
                0.35,

            "unresolved_score":
                0.15,

            "deterministic_evidence_scoring":
                True,

            "model_probability_used":
                False,

            "factual_truth_probability_assessed":
                False,

            "external_authority_checked":
                False,

            "semantic_memory_used":
                False,

            "coreference_resolution_performed":
                False,

            "fuzzy_matching_performed":
                False,

            "embedding_matching_performed":
                False,

            "new_participant_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "derived_calculation_performed":
                False,

            "duplicate_resolution_performed":
                False,

            "article_consolidation_performed":
                False,

            "persistence_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            top_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "temporal_duplicate_redundant_resolution",
    })

    return result


def resolve_temporal_duplicate_redundancy_v1(
    evidence_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Conservatively resolve exact duplicate and repeated-redundant
    Temporal candidates after Stage-M evidence assessment.

    Exact duplicate:
    - same claim unit,
    - same selected participant semantic_object_ref,
    - same relation family/type,
    - same effective explicit Temporal anchor,
    - same normalized source sentence.

    Repeated redundant evidence:
    - different claim units,
    - same section,
    - same selected participant semantic_object_ref,
    - same relation family/type,
    - same effective explicit Temporal anchor,
    - identical normalized full source sentence.

    Distinct wording is never collapsed merely because participant,
    relation, or anchor are similar.

    Stage N does NOT:
    - perform fuzzy/paraphrase duplicate detection,
    - use embeddings,
    - infer semantic equivalence,
    - merge different participants,
    - merge different relation identities,
    - merge different anchor identities,
    - resolve factual conflicts,
    - consolidate article Temporal intelligence,
    - assess truth,
    - use external authority,
    - use Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        evidence_result,
        Mapping,
    ):
        raise TemporalIntelligenceError(
            "evidence_result must be a mapping."
        )

    if (
        evidence_result.get(
            "schema_version"
        )
        != "temporal_evidence_confidence_assessment_v1"
    ):
        raise TemporalIntelligenceError(
            "Stage N requires "
            "temporal_evidence_confidence_assessment_v1."
        )

    if (
        evidence_result.get(
            "status"
        )
        != "TEMPORAL_EVIDENCE_CONFIDENCE_ASSESSMENT_COMPLETE"
    ):
        raise TemporalIntelligenceError(
            "Stage-M evidence assessment must be complete."
        )

    if (
        evidence_result.get(
            "phase"
        )
        != "4.6.13"
    ):
        raise TemporalIntelligenceError(
            "Stage N requires Phase 4.6.13 input."
        )

    if (
        evidence_result.get(
            "patch"
        )
        != "4.6.13M"
    ):
        raise TemporalIntelligenceError(
            "Stage N requires canonical 4.6.13M input."
        )

    if (
        evidence_result.get(
            "next_stage"
        )
        != "temporal_duplicate_redundant_resolution"
    ):
        raise TemporalIntelligenceError(
            "Stage M must hand off to "
            "temporal_duplicate_redundant_resolution."
        )

    if (
        evidence_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise TemporalIntelligenceError(
            "Temporal Intelligence must remain transient."
        )

    evidence_rank = {
        "HIGH":
            4,

        "MODERATE":
            3,

        "LOW":
            2,

        "INSUFFICIENT":
            1,

        "NOT_APPLICABLE":
            0,
    }

    def normalize_text(
        value,
    ):
        return " ".join(
            str(
                value
                or ""
            )
            .casefold()
            .split()
        )

    def participant_ref(
        candidate,
    ):
        participant = candidate.get(
            "selected_temporal_participant"
        )

        if not isinstance(
            participant,
            Mapping,
        ):
            return None

        ref = str(
            participant.get(
                "semantic_object_ref"
            )
            or ""
        )

        return ref or None

    def relation_identity(
        candidate,
    ):
        relation = candidate.get(
            "temporal_relation_structure"
        )

        if not isinstance(
            relation,
            Mapping,
        ):
            return (
                None,
                None,
            )

        family = str(
            relation.get(
                "relation_family"
            )
            or ""
        )

        relation_type = str(
            relation.get(
                "relation_type"
            )
            or ""
        )

        return (
            family or None,
            relation_type or None,
        )

    def effective_anchor(
        candidate,
    ):
        cross_sentence = candidate.get(
            "cross_sentence_temporal_anchoring"
        )

        if isinstance(
            cross_sentence,
            Mapping,
        ):
            if (
                cross_sentence.get(
                    "resolution_status"
                )
                == "CROSS_SENTENCE_ANCHOR_RESOLVED"
            ):
                anchor = cross_sentence.get(
                    "selected_cross_sentence_anchor"
                )

                if isinstance(
                    anchor,
                    Mapping,
                ):
                    return anchor

        anchor = candidate.get(
            "selected_temporal_anchor"
        )

        if isinstance(
            anchor,
            Mapping,
        ):
            return anchor

        return None

    def anchor_identity(
        candidate,
    ):
        anchor = effective_anchor(
            candidate
        )

        if not isinstance(
            anchor,
            Mapping,
        ):
            return (
                None,
                None,
            )

        signal_type = str(
            anchor.get(
                "signal_type"
            )
            or ""
        )

        anchor_text = normalize_text(
            anchor.get(
                "anchor_text"
            )
        )

        return (
            signal_type or None,
            anchor_text or None,
        )

    def evidence_payload(
        candidate,
    ):
        payload = candidate.get(
            "temporal_evidence_confidence"
        )

        if not isinstance(
            payload,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Stage N requires Temporal evidence confidence payload."
            )

        evidence_class = str(
            payload.get(
                "evidence_class"
            )
            or ""
        )

        if evidence_class not in evidence_rank:
            raise TemporalIntelligenceError(
                "Unknown Temporal evidence class."
            )

        score = payload.get(
            "evidence_score"
        )

        if score is not None:
            if (
                not isinstance(
                    score,
                    (
                        int,
                        float,
                    ),
                )
                or isinstance(
                    score,
                    bool,
                )
                or score < 0.0
                or score > 1.0
            ):
                raise TemporalIntelligenceError(
                    "Temporal evidence score must be within [0, 1]."
                )

        return (
            payload,
            evidence_class,
            score,
        )

    def candidate_identity(
        candidate,
    ):
        participant = participant_ref(
            candidate
        )

        family, relation_type = (
            relation_identity(
                candidate
            )
        )

        anchor_type, anchor_text = (
            anchor_identity(
                candidate
            )
        )

        source_text = normalize_text(
            candidate.get(
                "source_text"
            )
        )

        return (
            participant,
            family,
            relation_type,
            anchor_type,
            anchor_text,
            source_text,
        )

    def canonical_sort_key(
        candidate,
    ):
        (
            _payload,
            evidence_class,
            score,
        ) = evidence_payload(
            candidate
        )

        article_position = candidate.get(
            "article_position"
        )

        if not isinstance(
            article_position,
            int,
        ) or isinstance(
            article_position,
            bool,
        ):
            article_position = 10**12

        sentence_index = candidate.get(
            "sentence_global_index"
        )

        if not isinstance(
            sentence_index,
            int,
        ) or isinstance(
            sentence_index,
            bool,
        ):
            sentence_index = 10**12

        return (
            -float(
                score
                if score is not None
                else -1.0
            ),
            -evidence_rank[
                evidence_class
            ],
            article_position,
            sentence_index,
            str(
                candidate.get(
                    "temporal_candidate_id"
                )
                or ""
            ),
        )

    source_candidates = list(
        evidence_result.get(
            "temporal_candidates"
        )
        or []
    )

    candidate_by_id = {}
    working_candidates = []

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "temporal_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise TemporalIntelligenceError(
                "Temporal Candidate ID is required."
            )

        if candidate_id in candidate_by_id:
            raise TemporalIntelligenceError(
                "Duplicate Temporal Candidate ID."
            )

        if (
            candidate.get(
                "temporal_evidence_assessed"
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                "Stage-M evidence assessment must be complete."
            )

        if (
            candidate.get(
                "semantic_duplicate_resolution_performed"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Stage-N duplicate resolution must not "
                "already be performed."
            )

        evidence_payload(
            candidate
        )

        working_candidates.append(
            dict(
                candidate
            )
        )

        candidate_by_id[
            candidate_id
        ] = candidate

    # ---------------------------------------------------------
    # Build conservative identity groups.
    #
    # NOT_APPLICABLE candidates are intentionally preserved
    # individually because they are not promoted Temporal claims.
    # ---------------------------------------------------------

    exact_groups = {}
    redundant_groups = {}

    for candidate in working_candidates:
        candidate_id = str(
            candidate[
                "temporal_candidate_id"
            ]
        )

        evidence = candidate[
            "temporal_evidence_confidence"
        ]

        if (
            evidence.get(
                "evidence_class"
            )
            == "NOT_APPLICABLE"
        ):
            continue

        identity = candidate_identity(
            candidate
        )

        if (
            identity[0] is None
            or identity[1] is None
            or identity[2] is None
            or identity[3] is None
            or identity[4] is None
            or not identity[5]
        ):
            continue

        unit_id = str(
            candidate.get(
                "temporal_claim_unit_id"
            )
            or ""
        )

        section_id = str(
            candidate.get(
                "section_id"
            )
            or ""
        )

        if unit_id:
            exact_key = (
                unit_id,
                identity,
            )

            exact_groups.setdefault(
                exact_key,
                []
            ).append(
                candidate_id
            )

        if section_id:
            redundant_key = (
                section_id,
                identity,
            )

            redundant_groups.setdefault(
                redundant_key,
                []
            ).append(
                candidate_id
            )

    duplicate_of = {}
    redundant_of = {}
    canonical_group_members = {}

    # Exact duplicates first.
    for group_ids in exact_groups.values():
        if len(
            group_ids
        ) < 2:
            continue

        members = [
            next(
                candidate
                for candidate
                in working_candidates
                if candidate[
                    "temporal_candidate_id"
                ]
                == candidate_id
            )
            for candidate_id
            in group_ids
        ]

        members.sort(
            key=canonical_sort_key
        )

        canonical_id = members[0][
            "temporal_candidate_id"
        ]

        canonical_group_members.setdefault(
            canonical_id,
            set(),
        ).update(
            group_ids
        )

        for member in members[1:]:
            duplicate_of[
                member[
                    "temporal_candidate_id"
                ]
            ] = canonical_id

    # Repeated redundancy only across different claim units,
    # excluding candidates already exact-duplicate suppressed.
    for group_ids in redundant_groups.values():
        surviving_ids = [
            candidate_id
            for candidate_id
            in group_ids
            if candidate_id
            not in duplicate_of
        ]

        if len(
            surviving_ids
        ) < 2:
            continue

        member_units = {
            str(
                next(
                    candidate
                    for candidate
                    in working_candidates
                    if candidate[
                        "temporal_candidate_id"
                    ]
                    == candidate_id
                ).get(
                    "temporal_claim_unit_id"
                )
                or ""
            )
            for candidate_id
            in surviving_ids
        }

        if len(
            member_units
        ) < 2:
            continue

        members = [
            next(
                candidate
                for candidate
                in working_candidates
                if candidate[
                    "temporal_candidate_id"
                ]
                == candidate_id
            )
            for candidate_id
            in surviving_ids
        ]

        members.sort(
            key=canonical_sort_key
        )

        canonical_id = members[0][
            "temporal_candidate_id"
        ]

        canonical_group_members.setdefault(
            canonical_id,
            set(),
        ).update(
            surviving_ids
        )

        for member in members[1:]:
            redundant_of[
                member[
                    "temporal_candidate_id"
                ]
            ] = canonical_id

    resolved_candidates = []
    resolved_by_id = {}

    canonical_count = 0
    exact_duplicate_count = 0
    redundant_count = 0
    independent_count = 0
    not_applicable_count = 0

    for candidate in working_candidates:
        candidate_id = str(
            candidate[
                "temporal_candidate_id"
            ]
        )

        evidence_class = candidate[
            "temporal_evidence_confidence"
        ][
            "evidence_class"
        ]

        payload = {
            "resolution_status":
                None,

            "canonical_temporal_candidate_id":
                None,

            "suppressed":
                False,

            "exact_duplicate":
                False,

            "redundant_repeated_evidence":
                False,

            "group_member_candidate_ids":
                [],

            "identity_basis":
                (
                    "EXACT_PARTICIPANT_RELATION_ANCHOR_AND_NORMALIZED_SOURCE_TEXT"
                ),

            "fuzzy_duplicate_detection_performed":
                False,

            "paraphrase_matching_performed":
                False,

            "embedding_matching_performed":
                False,

            "semantic_equivalence_inference_performed":
                False,

            "conflict_resolution_performed":
                False,

            "truth_assessment_performed":
                False,

            "article_consolidation_performed":
                False,
        }

        if evidence_class == "NOT_APPLICABLE":
            payload.update({
                "resolution_status":
                    "NOT_APPLICABLE_PRESERVED",

                "canonical_temporal_candidate_id":
                    candidate_id,
            })

            not_applicable_count += 1

        elif candidate_id in duplicate_of:
            canonical_id = duplicate_of[
                candidate_id
            ]

            payload.update({
                "resolution_status":
                    "EXACT_DUPLICATE_SUPPRESSED",

                "canonical_temporal_candidate_id":
                    canonical_id,

                "suppressed":
                    True,

                "exact_duplicate":
                    True,
            })

            exact_duplicate_count += 1

        elif candidate_id in redundant_of:
            canonical_id = redundant_of[
                candidate_id
            ]

            payload.update({
                "resolution_status":
                    "REDUNDANT_REPEATED_EVIDENCE_SUPPRESSED",

                "canonical_temporal_candidate_id":
                    canonical_id,

                "suppressed":
                    True,

                "redundant_repeated_evidence":
                    True,
            })

            redundant_count += 1

        elif candidate_id in canonical_group_members:
            group_members = sorted(
                canonical_group_members[
                    candidate_id
                ]
            )

            payload.update({
                "resolution_status":
                    "CANONICAL_REPRESENTATIVE",

                "canonical_temporal_candidate_id":
                    candidate_id,

                "group_member_candidate_ids":
                    group_members,
            })

            canonical_count += 1

        else:
            payload.update({
                "resolution_status":
                    "INDEPENDENT_UNIQUE",

                "canonical_temporal_candidate_id":
                    candidate_id,
            })

            independent_count += 1

        resolved = dict(
            candidate
        )

        resolved.update({
            "semantic_duplicate_resolution_performed":
                True,

            "temporal_duplicate_redundancy_resolution":
                payload,

            "temporal_candidate_suppressed":
                payload[
                    "suppressed"
                ],

            "temporal_canonical_candidate_id":
                payload[
                    "canonical_temporal_candidate_id"
                ],

            "article_temporal_consolidation_performed":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,

            "semantic_memory_write_performed":
                False,

            "persistence_performed":
                False,
        })

        resolved_candidates.append(
            resolved
        )

        resolved_by_id[
            candidate_id
        ] = resolved

    source_units = list(
        evidence_result.get(
            "temporal_claim_units"
        )
        or []
    )

    resolved_units = []
    resolved_unit_by_id = {}

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "temporal_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise TemporalIntelligenceError(
                "Temporal Claim Unit ID is required."
            )

        if unit_id in resolved_unit_by_id:
            raise TemporalIntelligenceError(
                "Duplicate Temporal Claim Unit ID."
            )

        state = dict(
            unit.get(
                "temporal_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "temporal_evidence_assessment"
            )
            != "COMPLETE"
        ):
            raise TemporalIntelligenceError(
                "Stage-M evidence assessment must be COMPLETE before N."
            )

        if (
            state.get(
                "duplicate_temporal_resolution"
            )
            != "PENDING"
        ):
            raise TemporalIntelligenceError(
                "Stage-N state must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "temporal_evidence_assessment_performed"
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                "Stage-M boundary is incomplete."
            )

        if (
            boundaries.get(
                "temporal_duplicate_resolution_performed"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Stage-N duplicate boundary must be False before N."
            )

        updated_candidates = []

        for old_candidate in (
            unit.get(
                "temporal_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Unit Temporal candidate must be a mapping."
                )

            candidate_id = str(
                old_candidate.get(
                    "temporal_candidate_id"
                )
                or ""
            )

            replacement = resolved_by_id.get(
                candidate_id
            )

            if replacement is None:
                raise TemporalIntelligenceError(
                    "Stage-N candidate/unit mismatch."
                )

            updated_candidates.append(
                replacement
            )

        state[
            "duplicate_temporal_resolution"
        ] = "COMPLETE"

        boundaries[
            "temporal_duplicate_resolution_performed"
        ] = True

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "temporal_candidates":
                updated_candidates,

            "temporal_analysis_state":
                state,

            "processing_boundaries":
                boundaries,

            "active_temporal_candidate_count":
                sum(
                    1
                    for candidate
                    in updated_candidates
                    if candidate.get(
                        "temporal_candidate_suppressed"
                    )
                    is False
                ),

            "suppressed_temporal_candidate_count":
                sum(
                    1
                    for candidate
                    in updated_candidates
                    if candidate.get(
                        "temporal_candidate_suppressed"
                    )
                    is True
                ),
        })

        resolved_units.append(
            updated_unit
        )

        resolved_unit_by_id[
            unit_id
        ] = updated_unit

    resolved_sections = []

    for section in (
        evidence_result.get(
            "temporal_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "temporal_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Section Temporal Claim Unit must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "temporal_claim_unit_id"
                )
                or ""
            )

            replacement = resolved_unit_by_id.get(
                unit_id
            )

            if replacement is None:
                raise TemporalIntelligenceError(
                    "Temporal section references unknown Stage-N unit."
                )

            section_units.append(
                replacement
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "temporal_candidates"
                )
                or []
            )
        ]

        resolved_sections.append({
            **dict(
                section
            ),

            "temporal_claim_units":
                section_units,

            "temporal_candidates":
                section_candidates,

            "temporal_candidate_count":
                len(
                    section_candidates
                ),

            "active_temporal_candidate_count":
                sum(
                    1
                    for candidate
                    in section_candidates
                    if candidate.get(
                        "temporal_candidate_suppressed"
                    )
                    is False
                ),

            "suppressed_temporal_candidate_count":
                sum(
                    1
                    for candidate
                    in section_candidates
                    if candidate.get(
                        "temporal_candidate_suppressed"
                    )
                    is True
                ),
        })

    top_boundaries = dict(
        evidence_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        top_boundaries.get(
            "temporal_evidence_assessment_performed"
        )
        is not True
    ):
        raise TemporalIntelligenceError(
            "Top-level Stage-M boundary is incomplete."
        )

    if (
        top_boundaries.get(
            "temporal_duplicate_resolution_performed"
        )
        is not False
    ):
        raise TemporalIntelligenceError(
            "Top-level duplicate resolution must not already be performed."
        )

    top_boundaries[
        "temporal_duplicate_resolution_performed"
    ] = True

    active_candidates = [
        candidate
        for candidate
        in resolved_candidates
        if candidate.get(
            "temporal_candidate_suppressed"
        )
        is False
    ]

    suppressed_candidates = [
        candidate
        for candidate
        in resolved_candidates
        if candidate.get(
            "temporal_candidate_suppressed"
        )
        is True
    ]

    result = dict(
        evidence_result
    )

    result.update({
        "schema_version":
            "temporal_duplicate_redundant_resolution_v1",

        "patch":
            "4.6.13N",

        "status":
            "TEMPORAL_DUPLICATE_REDUNDANT_RESOLUTION_COMPLETE",

        "temporal_sections":
            resolved_sections,

        "temporal_claim_units":
            resolved_units,

        "temporal_candidates":
            resolved_candidates,

        "active_temporal_candidates":
            active_candidates,

        "suppressed_temporal_candidates":
            suppressed_candidates,

        "temporal_duplicate_redundancy_summary": {
            "candidate_count":
                len(
                    resolved_candidates
                ),

            "active_candidate_count":
                len(
                    active_candidates
                ),

            "suppressed_candidate_count":
                len(
                    suppressed_candidates
                ),

            "canonical_representative_count":
                canonical_count,

            "exact_duplicate_suppressed_count":
                exact_duplicate_count,

            "redundant_repeated_evidence_suppressed_count":
                redundant_count,

            "independent_unique_count":
                independent_count,

            "not_applicable_preserved_count":
                not_applicable_count,

            "candidate_count_accounted_for":
                (
                    canonical_count
                    + exact_duplicate_count
                    + redundant_count
                    + independent_count
                    + not_applicable_count
                    == len(
                        resolved_candidates
                    )
                ),

            "exact_identity_required":
                True,

            "normalized_full_source_text_required_for_redundancy":
                True,

            "same_section_required_for_redundancy":
                True,

            "fuzzy_duplicate_detection_performed":
                False,

            "paraphrase_matching_performed":
                False,

            "embedding_matching_performed":
                False,

            "semantic_equivalence_inference_performed":
                False,

            "conflict_resolution_performed":
                False,

            "truth_assessment_performed":
                False,

            "article_consolidation_performed":
                False,

            "semantic_memory_used":
                False,

            "external_authority_checked":
                False,

            "persistence_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            top_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "article_temporal_consolidation",
    })

    return result


def consolidate_article_temporal_intelligence_v1(
    duplicate_resolution_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Consolidate certified article-local Temporal candidates into an
    article-level Temporal intelligence view after Stage-N duplicate /
    redundancy resolution.

    Stage O consolidates already-established evidence only.

    It may organize:
    - sequence relations,
    - boundary relations,
    - recurrence relations,
    - explicit Temporal points,
    - durations,
    - intervals,
    - explicit Temporal references,
    - evidence-strength distributions,
    - section-level Temporal summaries.

    Stage O does NOT:
    - infer new relations between separate candidates,
    - infer chronology between unrelated participants,
    - perform new arithmetic,
    - reconstruct an unstated timeline,
    - resolve semantic conflicts,
    - perform fuzzy/paraphrase equivalence,
    - re-enable suppressed duplicates,
    - assess factual truth,
    - use external authority,
    - use Semantic Memory,
    - persist intelligence.

    Final output certification belongs to Stage P.
    """

    if not isinstance(
        duplicate_resolution_result,
        Mapping,
    ):
        raise TemporalIntelligenceError(
            "duplicate_resolution_result must be a mapping."
        )

    if (
        duplicate_resolution_result.get(
            "schema_version"
        )
        != "temporal_duplicate_redundant_resolution_v1"
    ):
        raise TemporalIntelligenceError(
            "Stage O requires "
            "temporal_duplicate_redundant_resolution_v1."
        )

    if (
        duplicate_resolution_result.get(
            "status"
        )
        != "TEMPORAL_DUPLICATE_REDUNDANT_RESOLUTION_COMPLETE"
    ):
        raise TemporalIntelligenceError(
            "Stage-N duplicate/redundancy resolution must be complete."
        )

    if (
        duplicate_resolution_result.get(
            "phase"
        )
        != "4.6.13"
    ):
        raise TemporalIntelligenceError(
            "Stage O requires Phase 4.6.13 input."
        )

    if (
        duplicate_resolution_result.get(
            "patch"
        )
        != "4.6.13N"
    ):
        raise TemporalIntelligenceError(
            "Stage O requires canonical 4.6.13N input."
        )

    if (
        duplicate_resolution_result.get(
            "next_stage"
        )
        != "article_temporal_consolidation"
    ):
        raise TemporalIntelligenceError(
            "Stage N must hand off to article_temporal_consolidation."
        )

    if (
        duplicate_resolution_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise TemporalIntelligenceError(
            "Temporal Intelligence must remain transient."
        )

    all_candidates = list(
        duplicate_resolution_result.get(
            "temporal_candidates"
        )
        or []
    )

    active_candidates = list(
        duplicate_resolution_result.get(
            "active_temporal_candidates"
        )
        or []
    )

    suppressed_candidates = list(
        duplicate_resolution_result.get(
            "suppressed_temporal_candidates"
        )
        or []
    )

    all_ids = set()
    active_ids = set()
    suppressed_ids = set()

    for candidate in all_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "temporal_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise TemporalIntelligenceError(
                "Temporal Candidate ID is required."
            )

        if candidate_id in all_ids:
            raise TemporalIntelligenceError(
                "Duplicate Temporal Candidate ID."
            )

        if (
            candidate.get(
                "semantic_duplicate_resolution_performed"
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                "Stage-N duplicate resolution must be complete."
            )

        if (
            candidate.get(
                "article_temporal_consolidation_performed"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Article Temporal consolidation must not "
                "already be performed."
            )

        all_ids.add(
            candidate_id
        )

    for candidate in active_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every active Temporal candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "temporal_candidate_id"
            )
            or ""
        )

        if (
            not candidate_id
            or candidate_id not in all_ids
        ):
            raise TemporalIntelligenceError(
                "Active Temporal candidate must reference "
                "the canonical Stage-N candidate set."
            )

        if (
            candidate.get(
                "temporal_candidate_suppressed"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Active Temporal candidate cannot be suppressed."
            )

        if candidate_id in active_ids:
            raise TemporalIntelligenceError(
                "Duplicate active Temporal Candidate ID."
            )

        active_ids.add(
            candidate_id
        )

    for candidate in suppressed_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every suppressed Temporal candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "temporal_candidate_id"
            )
            or ""
        )

        if (
            not candidate_id
            or candidate_id not in all_ids
        ):
            raise TemporalIntelligenceError(
                "Suppressed Temporal candidate must reference "
                "the canonical Stage-N candidate set."
            )

        if (
            candidate.get(
                "temporal_candidate_suppressed"
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                "Suppressed Temporal candidate must be marked suppressed."
            )

        if candidate_id in suppressed_ids:
            raise TemporalIntelligenceError(
                "Duplicate suppressed Temporal Candidate ID."
            )

        suppressed_ids.add(
            candidate_id
        )

    if active_ids & suppressed_ids:
        raise TemporalIntelligenceError(
            "Temporal candidate cannot be both active and suppressed."
        )

    if (
        active_ids
        | suppressed_ids
        != all_ids
    ):
        raise TemporalIntelligenceError(
            "Active and suppressed Temporal candidate sets "
            "must account for every Stage-N candidate."
        )

    def participant_payload(
        candidate,
    ):
        participant = candidate.get(
            "selected_temporal_participant"
        )

        if not isinstance(
            participant,
            Mapping,
        ):
            return None

        return {
            "semantic_object_ref":
                participant.get(
                    "semantic_object_ref"
                ),

            "canonical_text":
                participant.get(
                    "canonical_text"
                ),

            "matched_text":
                participant.get(
                    "matched_text"
                ),
        }

    def effective_anchor(
        candidate,
    ):
        cross_sentence = candidate.get(
            "cross_sentence_temporal_anchoring"
        )

        if isinstance(
            cross_sentence,
            Mapping,
        ):
            if (
                cross_sentence.get(
                    "resolution_status"
                )
                == "CROSS_SENTENCE_ANCHOR_RESOLVED"
            ):
                anchor = cross_sentence.get(
                    "selected_cross_sentence_anchor"
                )

                if isinstance(
                    anchor,
                    Mapping,
                ):
                    return dict(
                        anchor
                    )

        anchor = candidate.get(
            "selected_temporal_anchor"
        )

        if isinstance(
            anchor,
            Mapping,
        ):
            return dict(
                anchor
            )

        return None

    def relation_payload(
        candidate,
    ):
        relation = candidate.get(
            "temporal_relation_structure"
        )

        if not isinstance(
            relation,
            Mapping,
        ):
            return None

        return {
            "validation_status":
                relation.get(
                    "validation_status"
                ),

            "relation_family":
                relation.get(
                    "relation_family"
                ),

            "relation_type":
                relation.get(
                    "relation_type"
                ),

            "direction":
                relation.get(
                    "direction"
                ),

            "boundary_role":
                relation.get(
                    "boundary_role"
                ),

            "recurrence_role":
                relation.get(
                    "recurrence_role"
                ),
        }

    def value_payload(
        candidate,
    ):
        value = candidate.get(
            "temporal_value_validation"
        )

        if not isinstance(
            value,
            Mapping,
        ):
            return None

        return {
            "validation_status":
                value.get(
                    "validation_status"
                ),

            "temporal_value_kind":
                value.get(
                    "temporal_value_kind"
                ),

            "normalized_value":
                value.get(
                    "normalized_value"
                ),

            "normalized_values":
                value.get(
                    "normalized_values"
                ),

            "canonical_unit":
                value.get(
                    "canonical_unit"
                ),

            "temporal_reference_kind":
                value.get(
                    "temporal_reference_kind"
                ),
        }

    def evidence_payload(
        candidate,
    ):
        evidence = candidate.get(
            "temporal_evidence_confidence"
        )

        if not isinstance(
            evidence,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Stage-O active candidate requires "
                "Temporal evidence confidence."
            )

        return {
            "evidence_class":
                evidence.get(
                    "evidence_class"
                ),

            "evidence_score":
                evidence.get(
                    "evidence_score"
                ),

            "evidence_basis":
                evidence.get(
                    "evidence_basis"
                ),
        }

    def ordering_key(
        candidate,
    ):
        article_position = candidate.get(
            "article_position"
        )

        if (
            not isinstance(
                article_position,
                int,
            )
            or isinstance(
                article_position,
                bool,
            )
        ):
            article_position = 10**12

        sentence_index = candidate.get(
            "sentence_global_index"
        )

        if (
            not isinstance(
                sentence_index,
                int,
            )
            or isinstance(
                sentence_index,
                bool,
            )
        ):
            sentence_index = 10**12

        return (
            article_position,
            sentence_index,
            str(
                candidate.get(
                    "temporal_candidate_id"
                )
                or ""
            ),
        )

    ordered_active_candidates = sorted(
        active_candidates,
        key=ordering_key,
    )

    consolidated_items = []

    relation_family_counts = {
        "SEQUENCE":
            0,

        "BOUNDARY":
            0,

        "RECURRENCE":
            0,
    }

    value_kind_counts = {
        "POINT":
            0,

        "DURATION":
            0,

        "INTERVAL":
            0,
    }

    explicit_reference_count = 0

    evidence_class_counts = {
        "HIGH":
            0,

        "MODERATE":
            0,

        "LOW":
            0,

        "INSUFFICIENT":
            0,

        "NOT_APPLICABLE":
            0,
    }

    relation_items = {
        "SEQUENCE":
            [],

        "BOUNDARY":
            [],

        "RECURRENCE":
            [],
    }

    temporal_value_items = {
        "POINT":
            [],

        "DURATION":
            [],

        "INTERVAL":
            [],
    }

    temporal_reference_items = []

    unresolved_or_low_support_items = []
    non_promoted_items = []

    for candidate in ordered_active_candidates:
        candidate_id = str(
            candidate[
                "temporal_candidate_id"
            ]
        )

        participant = participant_payload(
            candidate
        )

        anchor = effective_anchor(
            candidate
        )

        relation = relation_payload(
            candidate
        )

        value = value_payload(
            candidate
        )

        evidence = evidence_payload(
            candidate
        )

        evidence_class = str(
            evidence.get(
                "evidence_class"
            )
            or ""
        )

        if evidence_class not in evidence_class_counts:
            raise TemporalIntelligenceError(
                "Unknown Stage-O Temporal evidence class."
            )

        evidence_class_counts[
            evidence_class
        ] += 1

        item = {
            "temporal_candidate_id":
                candidate_id,

            "temporal_canonical_candidate_id":
                candidate.get(
                    "temporal_canonical_candidate_id"
                ),

            "temporal_claim_unit_id":
                candidate.get(
                    "temporal_claim_unit_id"
                ),

            "sentence_id":
                candidate.get(
                    "sentence_id"
                ),

            "sentence_global_index":
                candidate.get(
                    "sentence_global_index"
                ),

            "article_position":
                candidate.get(
                    "article_position"
                ),

            "section_id":
                candidate.get(
                    "section_id"
                ),

            "section_index":
                candidate.get(
                    "section_index"
                ),

            "block_id":
                candidate.get(
                    "block_id"
                ),

            "paragraph_id":
                candidate.get(
                    "paragraph_id"
                ),

            "source_text":
                candidate.get(
                    "source_text"
                ),

            "primary_signal_type":
                candidate.get(
                    "primary_signal_type"
                ),

            "participant":
                participant,

            "effective_temporal_anchor":
                anchor,

            "temporal_relation":
                relation,

            "temporal_value":
                value,

            "temporal_evidence":
                evidence,

            "source_candidate_suppressed":
                False,

            "new_temporal_relation_inferred":
                False,

            "new_temporal_order_inferred":
                False,

            "cross_candidate_timeline_inference_performed":
                False,

            "derived_temporal_calculation_performed":
                False,

            "truth_assessment_performed":
                False,
        }

        promoted = False

        if isinstance(
            relation,
            Mapping,
        ):
            if (
                relation.get(
                    "validation_status"
                )
                == "STRUCTURALLY_VALIDATED"
            ):
                family = relation.get(
                    "relation_family"
                )

                if family in relation_items:
                    relation_items[
                        family
                    ].append(
                        item
                    )

                    relation_family_counts[
                        family
                    ] += 1

                    promoted = True

        if isinstance(
            value,
            Mapping,
        ):
            if (
                value.get(
                    "validation_status"
                )
                == "VALIDATED"
            ):
                value_kind = value.get(
                    "temporal_value_kind"
                )

                if value_kind in temporal_value_items:
                    temporal_value_items[
                        value_kind
                    ].append(
                        item
                    )

                    value_kind_counts[
                        value_kind
                    ] += 1

                    promoted = True

                reference_kind = value.get(
                    "temporal_reference_kind"
                )

                if reference_kind:
                    temporal_reference_items.append(
                        item
                    )

                    explicit_reference_count += 1

                    promoted = True

        if evidence_class in {
            "LOW",
            "INSUFFICIENT",
        }:
            unresolved_or_low_support_items.append(
                item
            )

        if not promoted:
            non_promoted_items.append(
                item
            )

        consolidated_items.append(
            item
        )

    # ---------------------------------------------------------
    # Mark all canonical candidate records as having passed O.
    # Suppressed candidates remain suppressed and are never
    # inserted into the article-level active Temporal views.
    # ---------------------------------------------------------

    consolidated_candidates = []
    consolidated_by_id = {}

    for candidate in all_candidates:
        candidate_id = str(
            candidate[
                "temporal_candidate_id"
            ]
        )

        updated = dict(
            candidate
        )

        updated.update({
            "article_temporal_consolidation_performed":
                True,

            "article_temporal_consolidation_member":
                candidate_id
                in active_ids,

            "article_temporal_consolidation_suppressed":
                candidate_id
                in suppressed_ids,

            "final_temporal_result_built":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,

            "semantic_memory_write_performed":
                False,

            "persistence_performed":
                False,
        })

        consolidated_candidates.append(
            updated
        )

        consolidated_by_id[
            candidate_id
        ] = updated

    source_units = list(
        duplicate_resolution_result.get(
            "temporal_claim_units"
        )
        or []
    )

    consolidated_units = []
    consolidated_unit_by_id = {}

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "temporal_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise TemporalIntelligenceError(
                "Temporal Claim Unit ID is required."
            )

        if unit_id in consolidated_unit_by_id:
            raise TemporalIntelligenceError(
                "Duplicate Temporal Claim Unit ID."
            )

        state = dict(
            unit.get(
                "temporal_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "duplicate_temporal_resolution"
            )
            != "COMPLETE"
        ):
            raise TemporalIntelligenceError(
                "Stage-N duplicate resolution must be COMPLETE before O."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "temporal_duplicate_resolution_performed"
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                "Stage-N boundary is incomplete."
            )

        updated_candidates = []

        for old_candidate in (
            unit.get(
                "temporal_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Unit Temporal candidate must be a mapping."
                )

            candidate_id = str(
                old_candidate.get(
                    "temporal_candidate_id"
                )
                or ""
            )

            replacement = consolidated_by_id.get(
                candidate_id
            )

            if replacement is None:
                raise TemporalIntelligenceError(
                    "Stage-O candidate/unit mismatch."
                )

            updated_candidates.append(
                replacement
            )

        state[
            "article_temporal_consolidation"
        ] = "COMPLETE"

        boundaries[
            "article_temporal_consolidation_performed"
        ] = True

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "temporal_candidates":
                updated_candidates,

            "temporal_analysis_state":
                state,

            "processing_boundaries":
                boundaries,

            "active_temporal_candidate_count":
                sum(
                    1
                    for candidate
                    in updated_candidates
                    if candidate.get(
                        "article_temporal_consolidation_member"
                    )
                    is True
                ),

            "suppressed_temporal_candidate_count":
                sum(
                    1
                    for candidate
                    in updated_candidates
                    if candidate.get(
                        "article_temporal_consolidation_suppressed"
                    )
                    is True
                ),
        })

        consolidated_units.append(
            updated_unit
        )

        consolidated_unit_by_id[
            unit_id
        ] = updated_unit

    consolidated_sections = []

    for section in (
        duplicate_resolution_result.get(
            "temporal_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal section must be a mapping."
            )

        section_id = str(
            section.get(
                "section_id"
            )
            or ""
        )

        section_units = []

        for old_unit in (
            section.get(
                "temporal_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Section Temporal Claim Unit must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "temporal_claim_unit_id"
                )
                or ""
            )

            replacement = consolidated_unit_by_id.get(
                unit_id
            )

            if replacement is None:
                raise TemporalIntelligenceError(
                    "Temporal section references unknown Stage-O unit."
                )

            section_units.append(
                replacement
            )

        section_active_items = [
            item
            for item in consolidated_items
            if str(
                item.get(
                    "section_id"
                )
                or ""
            )
            == section_id
        ]

        consolidated_sections.append({
            **dict(
                section
            ),

            "temporal_claim_units":
                section_units,

            "article_temporal_items":
                section_active_items,

            "article_temporal_item_count":
                len(
                    section_active_items
                ),

            "sequence_relation_count":
                sum(
                    1
                    for item
                    in section_active_items
                    if (
                        item.get(
                            "temporal_relation"
                        )
                        or {}
                    ).get(
                        "relation_family"
                    )
                    == "SEQUENCE"
                ),

            "boundary_relation_count":
                sum(
                    1
                    for item
                    in section_active_items
                    if (
                        item.get(
                            "temporal_relation"
                        )
                        or {}
                    ).get(
                        "relation_family"
                    )
                    == "BOUNDARY"
                ),

            "recurrence_relation_count":
                sum(
                    1
                    for item
                    in section_active_items
                    if (
                        item.get(
                            "temporal_relation"
                        )
                        or {}
                    ).get(
                        "relation_family"
                    )
                    == "RECURRENCE"
                ),
        })

    top_boundaries = dict(
        duplicate_resolution_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        top_boundaries.get(
            "temporal_duplicate_resolution_performed"
        )
        is not True
    ):
        raise TemporalIntelligenceError(
            "Top-level Stage-N duplicate boundary is incomplete."
        )

    if (
        top_boundaries.get(
            "article_temporal_consolidation_performed"
        )
        is True
    ):
        raise TemporalIntelligenceError(
            "Top-level article Temporal consolidation "
            "must not already be performed."
        )

    top_boundaries[
        "article_temporal_consolidation_performed"
    ] = True

    result = dict(
        duplicate_resolution_result
    )

    result.update({
        "schema_version":
            "article_temporal_consolidation_v1",

        "patch":
            "4.6.13O",

        "status":
            "ARTICLE_TEMPORAL_CONSOLIDATION_COMPLETE",

        "temporal_sections":
            consolidated_sections,

        "temporal_claim_units":
            consolidated_units,

        "temporal_candidates":
            consolidated_candidates,

        "article_temporal_items":
            consolidated_items,

        "article_temporal_relations": {
            "sequence":
                relation_items[
                    "SEQUENCE"
                ],

            "boundary":
                relation_items[
                    "BOUNDARY"
                ],

            "recurrence":
                relation_items[
                    "RECURRENCE"
                ],
        },

        "article_temporal_values": {
            "points":
                temporal_value_items[
                    "POINT"
                ],

            "durations":
                temporal_value_items[
                    "DURATION"
                ],

            "intervals":
                temporal_value_items[
                    "INTERVAL"
                ],

            "references":
                temporal_reference_items,
        },

        "article_temporal_low_or_unresolved_support":
            unresolved_or_low_support_items,

        "article_temporal_non_promoted_items":
            non_promoted_items,

        "article_temporal_consolidation_summary": {
            "all_candidate_count":
                len(
                    all_candidates
                ),

            "active_candidate_count":
                len(
                    active_candidates
                ),

            "suppressed_candidate_count":
                len(
                    suppressed_candidates
                ),

            "article_temporal_item_count":
                len(
                    consolidated_items
                ),

            "sequence_relation_count":
                relation_family_counts[
                    "SEQUENCE"
                ],

            "boundary_relation_count":
                relation_family_counts[
                    "BOUNDARY"
                ],

            "recurrence_relation_count":
                relation_family_counts[
                    "RECURRENCE"
                ],

            "point_value_count":
                value_kind_counts[
                    "POINT"
                ],

            "duration_value_count":
                value_kind_counts[
                    "DURATION"
                ],

            "interval_value_count":
                value_kind_counts[
                    "INTERVAL"
                ],

            "explicit_temporal_reference_count":
                explicit_reference_count,

            "high_evidence_count":
                evidence_class_counts[
                    "HIGH"
                ],

            "moderate_evidence_count":
                evidence_class_counts[
                    "MODERATE"
                ],

            "low_evidence_count":
                evidence_class_counts[
                    "LOW"
                ],

            "insufficient_evidence_count":
                evidence_class_counts[
                    "INSUFFICIENT"
                ],

            "not_applicable_evidence_count":
                evidence_class_counts[
                    "NOT_APPLICABLE"
                ],

            "low_or_unresolved_support_item_count":
                len(
                    unresolved_or_low_support_items
                ),

            "non_promoted_item_count":
                len(
                    non_promoted_items
                ),

            "suppressed_candidates_reintroduced":
                False,

            "new_temporal_relation_inference_performed":
                False,

            "new_temporal_order_inference_performed":
                False,

            "cross_candidate_timeline_inference_performed":
                False,

            "derived_temporal_calculation_performed":
                False,

            "conflict_resolution_performed":
                False,

            "fuzzy_or_paraphrase_consolidation_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_checked":
                False,

            "semantic_memory_used":
                False,

            "persistence_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            top_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "final_temporal_intelligence_result",
    })

    return result


def build_final_temporal_intelligence_result_v1(
    article_consolidation_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Build the canonical final article-local Temporal Intelligence result
    after Stage-O article consolidation.

    Stage P is packaging/canonicalization only.

    It does NOT:
    - infer new Temporal relations,
    - infer new Temporal ordering,
    - infer an unstated timeline,
    - perform new point/duration/interval validation,
    - perform cross-sentence repair,
    - perform new evidence scoring,
    - perform duplicate resolution,
    - perform arithmetic,
    - assess factual truth,
    - use external authority,
    - use Semantic Memory,
    - make linking decisions,
    - persist intelligence.

    Full layer certification belongs exclusively to Stage Q.
    """

    if not isinstance(
        article_consolidation_result,
        Mapping,
    ):
        raise TemporalIntelligenceError(
            "article_consolidation_result must be a mapping."
        )

    if (
        article_consolidation_result.get(
            "schema_version"
        )
        != "article_temporal_consolidation_v1"
    ):
        raise TemporalIntelligenceError(
            "Stage P requires article_temporal_consolidation_v1."
        )

    if (
        article_consolidation_result.get(
            "status"
        )
        != "ARTICLE_TEMPORAL_CONSOLIDATION_COMPLETE"
    ):
        raise TemporalIntelligenceError(
            "Article Temporal consolidation must be complete."
        )

    if (
        article_consolidation_result.get(
            "phase"
        )
        != "4.6.13"
    ):
        raise TemporalIntelligenceError(
            "Stage P requires Phase 4.6.13 input."
        )

    if (
        article_consolidation_result.get(
            "patch"
        )
        != "4.6.13O"
    ):
        raise TemporalIntelligenceError(
            "Stage P requires canonical 4.6.13O input."
        )

    if (
        article_consolidation_result.get(
            "next_stage"
        )
        != "final_temporal_intelligence_result"
    ):
        raise TemporalIntelligenceError(
            "Stage O must hand off to "
            "final_temporal_intelligence_result."
        )

    if (
        article_consolidation_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise TemporalIntelligenceError(
            "Temporal Intelligence must remain transient."
        )

    boundaries = dict(
        article_consolidation_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        boundaries.get(
            "article_temporal_consolidation_performed"
        )
        is not True
    ):
        raise TemporalIntelligenceError(
            "Article Temporal consolidation boundary must be complete."
        )

    required_false_boundaries = (
        "new_temporal_relation_inference_performed",
        "new_temporal_order_inference_performed",
        "cross_candidate_timeline_inference_performed",
        "derived_temporal_calculation_performed",
        "conflict_resolution_performed",
        "truth_assessment_performed",
        "external_authority_check_performed",
        "semantic_memory_write_performed",
        "linking_decisions_performed",
        "persistence_performed",
    )

    for boundary_name in required_false_boundaries:
        if (
            boundary_name in boundaries
            and boundaries.get(
                boundary_name
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                boundary_name
                + " must remain False in final Temporal Intelligence."
            )

    temporal_candidates = list(
        article_consolidation_result.get(
            "temporal_candidates"
        )
        or []
    )

    temporal_sections = list(
        article_consolidation_result.get(
            "temporal_sections"
        )
        or []
    )

    temporal_claim_units = list(
        article_consolidation_result.get(
            "temporal_claim_units"
        )
        or []
    )

    article_temporal_items = list(
        article_consolidation_result.get(
            "article_temporal_items"
        )
        or []
    )

    article_temporal_relations = dict(
        article_consolidation_result.get(
            "article_temporal_relations"
        )
        or {}
    )

    article_temporal_values = dict(
        article_consolidation_result.get(
            "article_temporal_values"
        )
        or {}
    )

    low_or_unresolved = list(
        article_consolidation_result.get(
            "article_temporal_low_or_unresolved_support"
        )
        or []
    )

    non_promoted = list(
        article_consolidation_result.get(
            "article_temporal_non_promoted_items"
        )
        or []
    )

    consolidation_summary = dict(
        article_consolidation_result.get(
            "article_temporal_consolidation_summary"
        )
        or {}
    )

    if not isinstance(
        article_temporal_relations.get(
            "sequence",
            [],
        ),
        list,
    ):
        raise TemporalIntelligenceError(
            "Final Temporal sequence view must be a list."
        )

    if not isinstance(
        article_temporal_relations.get(
            "boundary",
            [],
        ),
        list,
    ):
        raise TemporalIntelligenceError(
            "Final Temporal boundary view must be a list."
        )

    if not isinstance(
        article_temporal_relations.get(
            "recurrence",
            [],
        ),
        list,
    ):
        raise TemporalIntelligenceError(
            "Final Temporal recurrence view must be a list."
        )

    for value_key in (
        "points",
        "durations",
        "intervals",
        "references",
    ):
        if not isinstance(
            article_temporal_values.get(
                value_key,
                [],
            ),
            list,
        ):
            raise TemporalIntelligenceError(
                "Final Temporal value view "
                + value_key
                + " must be a list."
            )

    candidate_ids = set()

    final_candidates = []

    for candidate in temporal_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every final Temporal candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "temporal_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise TemporalIntelligenceError(
                "Final Temporal Candidate ID is required."
            )

        if candidate_id in candidate_ids:
            raise TemporalIntelligenceError(
                "Duplicate final Temporal Candidate ID."
            )

        if (
            candidate.get(
                "article_temporal_consolidation_performed"
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                "Stage-O consolidation must be complete "
                "for every final Temporal candidate."
            )

        if (
            candidate.get(
                "final_temporal_result_built"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Final Temporal result must not already be built."
            )

        candidate_ids.add(
            candidate_id
        )

        updated = dict(
            candidate
        )

        updated.update({
            "final_temporal_result_built":
                True,

            "temporal_intelligence_certification_performed":
                False,

            "temporal_intelligence_certified":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,

            "semantic_memory_write_performed":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        })

        final_candidates.append(
            updated
        )

    final_candidate_by_id = {
        candidate[
            "temporal_candidate_id"
        ]:
            candidate
        for candidate in final_candidates
    }

    final_units = []

    seen_unit_ids = set()

    for unit in temporal_claim_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every final Temporal Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "temporal_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise TemporalIntelligenceError(
                "Final Temporal Claim Unit ID is required."
            )

        if unit_id in seen_unit_ids:
            raise TemporalIntelligenceError(
                "Duplicate final Temporal Claim Unit ID."
            )

        seen_unit_ids.add(
            unit_id
        )

        updated_candidates = []

        for old_candidate in (
            unit.get(
                "temporal_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Final unit Temporal candidate must be a mapping."
                )

            candidate_id = str(
                old_candidate.get(
                    "temporal_candidate_id"
                )
                or ""
            )

            replacement = final_candidate_by_id.get(
                candidate_id
            )

            if replacement is None:
                raise TemporalIntelligenceError(
                    "Final Temporal candidate/unit mismatch."
                )

            updated_candidates.append(
                replacement
            )

        state = dict(
            unit.get(
                "temporal_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "article_temporal_consolidation"
            )
            != "COMPLETE"
        ):
            raise TemporalIntelligenceError(
                "Stage-O unit consolidation must be COMPLETE before P."
            )

        state[
            "final_temporal_intelligence_result"
        ] = "COMPLETE"

        unit_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            unit_boundaries.get(
                "article_temporal_consolidation_performed"
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                "Stage-O unit boundary must be complete before P."
            )

        unit_boundaries[
            "final_temporal_result_built"
        ] = True

        unit_boundaries[
            "temporal_intelligence_certification_performed"
        ] = False

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "temporal_candidates":
                updated_candidates,

            "temporal_analysis_state":
                state,

            "processing_boundaries":
                unit_boundaries,
        })

        final_units.append(
            updated_unit
        )

    final_unit_by_id = {
        unit[
            "temporal_claim_unit_id"
        ]:
            unit
        for unit in final_units
    }

    final_sections = []

    for section in temporal_sections:
        if not isinstance(
            section,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every final Temporal section must be a mapping."
            )

        updated_units = []

        for old_unit in (
            section.get(
                "temporal_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Final section Temporal Claim Unit must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "temporal_claim_unit_id"
                )
                or ""
            )

            replacement = final_unit_by_id.get(
                unit_id
            )

            if replacement is None:
                raise TemporalIntelligenceError(
                    "Final Temporal section references unknown unit."
                )

            updated_units.append(
                replacement
            )

        updated_section = dict(
            section
        )

        updated_section[
            "temporal_claim_units"
        ] = updated_units

        final_sections.append(
            updated_section
        )

    final_boundaries = dict(
        boundaries
    )

    final_boundaries[
        "final_temporal_result_built"
    ] = True

    final_boundaries[
        "temporal_intelligence_certification_performed"
    ] = False

    final_boundaries[
        "new_temporal_relation_inference_performed"
    ] = False

    final_boundaries[
        "new_temporal_order_inference_performed"
    ] = False

    final_boundaries[
        "cross_candidate_timeline_inference_performed"
    ] = False

    final_boundaries[
        "derived_temporal_calculation_performed"
    ] = False

    final_boundaries[
        "truth_assessment_performed"
    ] = False

    final_boundaries[
        "external_authority_check_performed"
    ] = False

    final_boundaries[
        "semantic_memory_write_performed"
    ] = False

    final_boundaries[
        "linking_decisions_performed"
    ] = False

    final_boundaries[
        "persistence_performed"
    ] = False

    article_identity = dict(
        article_consolidation_result.get(
            "article_identity"
        )
        or {}
    )

    result = {
        "schema_version":
            "temporal_intelligence_result_v1",

        "temporal_intelligence_version":
            article_consolidation_result.get(
                "temporal_intelligence_version"
            )
            or "temporal_intelligence_v1",

        "phase":
            "4.6.13",

        "patch":
            "4.6.13P",

        "status":
            "TEMPORAL_INTELLIGENCE_RESULT_COMPLETE",

        "article_identity": {
            "article_id":
                article_identity.get(
                    "article_id"
                )
                or article_consolidation_result.get(
                    "article_id"
                ),

            "workspace_id":
                article_identity.get(
                    "workspace_id"
                )
                or article_consolidation_result.get(
                    "workspace_id"
                ),

            "source_type":
                article_identity.get(
                    "source_type"
                )
                or article_consolidation_result.get(
                    "source_type"
                ),

            "content_hash":
                article_identity.get(
                    "content_hash"
                )
                or article_consolidation_result.get(
                    "content_hash"
                ),

            "body_ref":
                article_identity.get(
                    "body_ref"
                )
                or article_consolidation_result.get(
                    "body_ref"
                ),
        },

        "temporal_sections":
            final_sections,

        "temporal_claim_units":
            final_units,

        "temporal_candidates":
            final_candidates,

        "article_temporal_items":
            article_temporal_items,

        "article_temporal_relations":
            article_temporal_relations,

        "article_temporal_values":
            article_temporal_values,

        "article_temporal_low_or_unresolved_support":
            low_or_unresolved,

        "article_temporal_non_promoted_items":
            non_promoted,

        "article_temporal_summary":
            consolidation_summary,

        "result_contract": {
            "article_local_only":
                True,

            "transient_only":
                True,

            "article_temporal_consolidation_complete":
                True,

            "new_temporal_relation_inference_performed":
                False,

            "new_temporal_order_inference_performed":
                False,

            "cross_candidate_timeline_inference_performed":
                False,

            "derived_temporal_calculation_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_checked":
                False,

            "semantic_memory_used":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "processing_boundaries":
            final_boundaries,

        "certification": {
            "performed":
                False,

            "certified":
                False,

            "certification_stage":
                "4.6.13Q",
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "temporal_intelligence_certification",
    }

    return result


def certify_temporal_intelligence_v1(
    final_temporal_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Certify the canonical final Temporal Intelligence result.

    Stage Q performs certification only.

    It does NOT:
    - add or change Temporal relations,
    - add or change Temporal values,
    - perform new Temporal ordering,
    - perform cross-candidate timeline inference,
    - perform arithmetic,
    - strengthen evidence,
    - resolve duplicates,
    - assess factual truth,
    - use external authority,
    - use Semantic Memory,
    - make linking decisions,
    - persist intelligence.

    Successful certification closes Phase 4.6.13 and hands the
    article-local transient result to Uncertainty Intelligence.
    """

    if not isinstance(
        final_temporal_result,
        Mapping,
    ):
        raise TemporalIntelligenceError(
            "final_temporal_result must be a mapping."
        )

    if (
        final_temporal_result.get(
            "schema_version"
        )
        != "temporal_intelligence_result_v1"
    ):
        raise TemporalIntelligenceError(
            "Stage Q requires temporal_intelligence_result_v1."
        )

    if (
        final_temporal_result.get(
            "status"
        )
        != "TEMPORAL_INTELLIGENCE_RESULT_COMPLETE"
    ):
        raise TemporalIntelligenceError(
            "Final Temporal Intelligence result must be complete."
        )

    if (
        final_temporal_result.get(
            "phase"
        )
        != "4.6.13"
    ):
        raise TemporalIntelligenceError(
            "Stage Q requires Phase 4.6.13 input."
        )

    if (
        final_temporal_result.get(
            "patch"
        )
        != "4.6.13P"
    ):
        raise TemporalIntelligenceError(
            "Stage Q requires canonical 4.6.13P input."
        )

    if (
        final_temporal_result.get(
            "next_stage"
        )
        != "temporal_intelligence_certification"
    ):
        raise TemporalIntelligenceError(
            "Stage P must hand off to "
            "temporal_intelligence_certification."
        )

    if (
        final_temporal_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise TemporalIntelligenceError(
            "Temporal Intelligence must remain transient."
        )

    certification = final_temporal_result.get(
        "certification"
    )

    if not isinstance(
        certification,
        Mapping,
    ):
        raise TemporalIntelligenceError(
            "Final Temporal result requires certification contract."
        )

    if (
        certification.get(
            "performed"
        )
        is not False
    ):
        raise TemporalIntelligenceError(
            "Temporal certification must not already be performed."
        )

    if (
        certification.get(
            "certified"
        )
        is not False
    ):
        raise TemporalIntelligenceError(
            "Temporal result must not already be certified."
        )

    if (
        certification.get(
            "certification_stage"
        )
        != "4.6.13Q"
    ):
        raise TemporalIntelligenceError(
            "Temporal certification stage must be 4.6.13Q."
        )

    result_contract = final_temporal_result.get(
        "result_contract"
    )

    if not isinstance(
        result_contract,
        Mapping,
    ):
        raise TemporalIntelligenceError(
            "Final Temporal result requires result_contract."
        )

    required_true_contracts = (
        "article_local_only",
        "transient_only",
        "article_temporal_consolidation_complete",
    )

    for name in required_true_contracts:
        if (
            result_contract.get(
                name
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                name
                + " must be True before Temporal certification."
            )

    required_false_contracts = (
        "new_temporal_relation_inference_performed",
        "new_temporal_order_inference_performed",
        "cross_candidate_timeline_inference_performed",
        "derived_temporal_calculation_performed",
        "truth_assessment_performed",
        "external_authority_checked",
        "semantic_memory_used",
        "linking_decisions_performed",
        "persistence_performed",
    )

    for name in required_false_contracts:
        if (
            result_contract.get(
                name
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                name
                + " must remain False before Temporal certification."
            )

    boundaries = dict(
        final_temporal_result.get(
            "processing_boundaries"
        )
        or {}
    )

    required_true_boundaries = (
        "article_temporal_consolidation_performed",
        "final_temporal_result_built",
    )

    for name in required_true_boundaries:
        if (
            boundaries.get(
                name
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                name
                + " must be True before Temporal certification."
            )

    if (
        boundaries.get(
            "temporal_intelligence_certification_performed"
        )
        is not False
    ):
        raise TemporalIntelligenceError(
            "Temporal certification boundary must be False before Q."
        )

    required_false_boundaries = (
        "new_temporal_relation_inference_performed",
        "new_temporal_order_inference_performed",
        "cross_candidate_timeline_inference_performed",
        "derived_temporal_calculation_performed",
        "truth_assessment_performed",
        "external_authority_check_performed",
        "semantic_memory_write_performed",
        "linking_decisions_performed",
        "persistence_performed",
    )

    for name in required_false_boundaries:
        if (
            boundaries.get(
                name
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                name
                + " must remain False during Temporal certification."
            )

    candidates = list(
        final_temporal_result.get(
            "temporal_candidates"
        )
        or []
    )

    certified_candidates = []
    seen_candidate_ids = set()

    for candidate in candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "temporal_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise TemporalIntelligenceError(
                "Temporal Candidate ID is required."
            )

        if candidate_id in seen_candidate_ids:
            raise TemporalIntelligenceError(
                "Duplicate Temporal Candidate ID."
            )

        seen_candidate_ids.add(
            candidate_id
        )

        if (
            candidate.get(
                "final_temporal_result_built"
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                "Final Temporal result must be built "
                "for every candidate before Q."
            )

        if (
            candidate.get(
                "temporal_intelligence_certification_performed"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Candidate certification must be pending before Q."
            )

        if (
            candidate.get(
                "temporal_intelligence_certified"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Candidate must not already be certified."
            )

        candidate_forbidden_false = (
            "truth_assessed",
            "external_authority_checked",
            "semantic_memory_write_performed",
            "linking_decisions_performed",
            "persistence_performed",
        )

        for name in candidate_forbidden_false:
            if (
                candidate.get(
                    name
                )
                is not False
            ):
                raise TemporalIntelligenceError(
                    name
                    + " must remain False on certified Temporal candidates."
                )

        updated = dict(
            candidate
        )

        updated.update({
            "temporal_intelligence_certification_performed":
                True,

            "temporal_intelligence_certified":
                True,
        })

        certified_candidates.append(
            updated
        )

    candidate_by_id = {
        candidate[
            "temporal_candidate_id"
        ]:
            candidate
        for candidate in certified_candidates
    }

    units = list(
        final_temporal_result.get(
            "temporal_claim_units"
        )
        or []
    )

    certified_units = []
    certified_unit_by_id = {}
    seen_unit_ids = set()

    for unit in units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "temporal_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise TemporalIntelligenceError(
                "Temporal Claim Unit ID is required."
            )

        if unit_id in seen_unit_ids:
            raise TemporalIntelligenceError(
                "Duplicate Temporal Claim Unit ID."
            )

        seen_unit_ids.add(
            unit_id
        )

        state = dict(
            unit.get(
                "temporal_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "final_temporal_intelligence_result"
            )
            != "COMPLETE"
        ):
            raise TemporalIntelligenceError(
                "Stage-P unit result must be COMPLETE before Q."
            )

        unit_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            unit_boundaries.get(
                "final_temporal_result_built"
            )
            is not True
        ):
            raise TemporalIntelligenceError(
                "Unit final Temporal result boundary must be True."
            )

        if (
            unit_boundaries.get(
                "temporal_intelligence_certification_performed"
            )
            is not False
        ):
            raise TemporalIntelligenceError(
                "Unit certification boundary must be False before Q."
            )

        updated_candidates = []

        for old_candidate in (
            unit.get(
                "temporal_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Unit Temporal candidate must be a mapping."
                )

            candidate_id = str(
                old_candidate.get(
                    "temporal_candidate_id"
                )
                or ""
            )

            replacement = candidate_by_id.get(
                candidate_id
            )

            if replacement is None:
                raise TemporalIntelligenceError(
                    "Certified Temporal candidate/unit mismatch."
                )

            updated_candidates.append(
                replacement
            )

        state[
            "temporal_intelligence_certification"
        ] = "COMPLETE"

        unit_boundaries[
            "temporal_intelligence_certification_performed"
        ] = True

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "temporal_candidates":
                updated_candidates,

            "temporal_analysis_state":
                state,

            "processing_boundaries":
                unit_boundaries,

            "temporal_intelligence_certified":
                True,
        })

        certified_units.append(
            updated_unit
        )

        certified_unit_by_id[
            unit_id
        ] = updated_unit

    sections = list(
        final_temporal_result.get(
            "temporal_sections"
        )
        or []
    )

    certified_sections = []

    for section in sections:
        if not isinstance(
            section,
            Mapping,
        ):
            raise TemporalIntelligenceError(
                "Every Temporal section must be a mapping."
            )

        updated_units = []

        for old_unit in (
            section.get(
                "temporal_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise TemporalIntelligenceError(
                    "Section Temporal Claim Unit must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "temporal_claim_unit_id"
                )
                or ""
            )

            replacement = certified_unit_by_id.get(
                unit_id
            )

            if replacement is None:
                raise TemporalIntelligenceError(
                    "Certified Temporal section references unknown unit."
                )

            updated_units.append(
                replacement
            )

        updated_section = dict(
            section
        )

        updated_section.update({
            "temporal_claim_units":
                updated_units,

            "temporal_intelligence_certified":
                True,
        })

        certified_sections.append(
            updated_section
        )

    certified_boundaries = dict(
        boundaries
    )

    certified_boundaries[
        "temporal_intelligence_certification_performed"
    ] = True

    certified_result = dict(
        final_temporal_result
    )

    certified_result.update({
        "schema_version":
            "temporal_intelligence_result_v1",

        "temporal_intelligence_version":
            final_temporal_result.get(
                "temporal_intelligence_version"
            )
            or "temporal_intelligence_v1",

        "phase":
            "4.6.13",

        "patch":
            "4.6.13Q",

        "status":
            "TEMPORAL_INTELLIGENCE_CERTIFIED",

        "temporal_candidates":
            certified_candidates,

        "temporal_claim_units":
            certified_units,

        "temporal_sections":
            certified_sections,

        "processing_boundaries":
            certified_boundaries,

        "certification": {
            "performed":
                True,

            "certified":
                True,

            "certification_stage":
                "4.6.13Q",

            "certification_scope":
                "FULL_TEMPORAL_INTELLIGENCE_LAYER",

            "article_local_only":
                True,

            "transient_only":
                True,

            "new_temporal_reasoning_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_checked":
                False,

            "semantic_memory_used":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "uncertainty_intelligence",
    })

    return certified_result
