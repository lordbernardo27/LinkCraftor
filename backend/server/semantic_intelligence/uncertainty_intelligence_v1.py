from __future__ import annotations

from typing import Any, Mapping
import re


class UncertaintyIntelligenceError(ValueError):
    """Raised when the Uncertainty Intelligence contract is violated."""


def validate_uncertainty_intelligence_intake_v1(
    certified_temporal_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate the canonical handoff from Phase 4.6.13
    Temporal Intelligence into Phase 4.6.14
    Uncertainty Intelligence.

    This stage performs intake validation only.

    It does NOT:
    - detect uncertainty expressions,
    - create uncertainty claim units,
    - classify possibility or likelihood,
    - classify approximation,
    - classify non-universal frequency,
    - classify epistemic uncertainty,
    - classify evidential hedging,
    - classify variability,
    - resolve uncertainty scope or target,
    - infer unstated uncertainty,
    - convert modal language into probability,
    - perform quantitative reasoning,
    - perform causal reasoning,
    - perform Analogical Intelligence,
    - perform Similarity Intelligence,
    - perform Temporal Intelligence,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        certified_temporal_result,
        Mapping,
    ):
        raise UncertaintyIntelligenceError(
            "certified_temporal_result must be a mapping."
        )

    if (
        certified_temporal_result.get(
            "schema_version"
        )
        != "temporal_intelligence_result_v1"
    ):
        raise UncertaintyIntelligenceError(
            "Uncertainty Intelligence requires "
            "temporal_intelligence_result_v1."
        )

    if (
        certified_temporal_result.get(
            "status"
        )
        != "TEMPORAL_INTELLIGENCE_CERTIFIED"
    ):
        raise UncertaintyIntelligenceError(
            "Temporal Intelligence must be certified "
            "before Uncertainty Intelligence intake."
        )

    if (
        certified_temporal_result.get(
            "phase"
        )
        != "4.6.13"
    ):
        raise UncertaintyIntelligenceError(
            "Uncertainty Intelligence intake requires "
            "Phase 4.6.13 input."
        )

    if (
        certified_temporal_result.get(
            "patch"
        )
        != "4.6.13Q"
    ):
        raise UncertaintyIntelligenceError(
            "Uncertainty Intelligence intake requires "
            "canonical 4.6.13Q input."
        )

    if (
        certified_temporal_result.get(
            "next_stage"
        )
        != "uncertainty_intelligence"
    ):
        raise UncertaintyIntelligenceError(
            "Certified Temporal Intelligence must hand off "
            "to uncertainty_intelligence."
        )

    if (
        certified_temporal_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise UncertaintyIntelligenceError(
            "Uncertainty Intelligence intake must remain transient."
        )

    certification = certified_temporal_result.get(
        "certification"
    )

    if not isinstance(
        certification,
        Mapping,
    ):
        raise UncertaintyIntelligenceError(
            "Certified Temporal certification metadata "
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
        != "4.6.13Q"
    ):
        raise UncertaintyIntelligenceError(
            "Certified Temporal certification state is invalid."
        )

    processing_boundaries = certified_temporal_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        processing_boundaries,
        Mapping,
    ):
        raise UncertaintyIntelligenceError(
            "Certified Temporal processing boundaries "
            "must be a mapping."
        )

    if (
        processing_boundaries.get(
            "temporal_intelligence_certification_performed"
        )
        is not True
    ):
        raise UncertaintyIntelligenceError(
            "Temporal hard-certification boundary "
            "must be complete."
        )

    forbidden_upstream_true = (
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

    for boundary_name in forbidden_upstream_true:
        if (
            processing_boundaries.get(
                boundary_name
            )
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Certified Temporal boundary must remain False: "
                + boundary_name
            )

    article_identity = certified_temporal_result.get(
        "article_identity"
    )

    if not isinstance(
        article_identity,
        Mapping,
    ):
        raise UncertaintyIntelligenceError(
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
            raise UncertaintyIntelligenceError(
                "Required article identity field missing: "
                + field_name
            )

    return {
        "schema_version":
            "uncertainty_intelligence_intake_v1",

        "uncertainty_intelligence_version":
            "uncertainty_intelligence_v1",

        "phase":
            "4.6.14",

        "patch":
            "4.6.14C",

        "status":
            "UNCERTAINTY_INTELLIGENCE_INTAKE_VALIDATED",

        "article_identity":
            dict(
                article_identity
            ),

        "upstream_temporal_result":
            certified_temporal_result,

        "upstream_certification": {
            "schema_version":
                certified_temporal_result.get(
                    "schema_version"
                ),

            "phase":
                certified_temporal_result.get(
                    "phase"
                ),

            "patch":
                certified_temporal_result.get(
                    "patch"
                ),

            "status":
                certified_temporal_result.get(
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
            "uncertainty_intelligence_intake_validated":
                True,

            "uncertainty_claim_units_prepared":
                False,

            "uncertainty_signal_interpretation_performed":
                False,

            "uncertainty_candidate_extraction_performed":
                False,

            "uncertainty_scope_grounding_performed":
                False,

            "uncertainty_type_classification_performed":
                False,

            "uncertainty_explicitness_strength_validation_performed":
                False,

            "same_sentence_uncertainty_validation_performed":
                False,

            "cross_sentence_uncertainty_anchoring_performed":
                False,

            "uncertainty_evidence_assessment_performed":
                False,

            "uncertainty_duplicate_resolution_performed":
                False,

            "article_uncertainty_consolidation_performed":
                False,

            "final_uncertainty_result_built":
                False,

            "uncertainty_certification_performed":
                False,

            "unstated_uncertainty_inference_performed":
                False,

            "numeric_probability_inference_performed":
                False,

            "new_quantitative_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "similarity_reasoning_performed":
                False,

            "new_temporal_reasoning_performed":
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

        "uncertainty_boundaries": {
            "article_local_only":
                True,

            "lexical_uncertainty_signal_is_validated_uncertainty":
                False,

            "lexical_modal_is_automatically_uncertainty":
                False,

            "unstated_uncertainty_inference_performed":
                False,

            "unstated_probability_inference_performed":
                False,

            "modal_to_numeric_probability_conversion_performed":
                False,

            "source_commitment_strength_preserved":
                True,

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
            "uncertainty_claim_unit_preparation",
    }


def build_uncertainty_claim_units_v1(
    certified_temporal_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Build canonical Phase 4.6.14 Uncertainty Claim Units from
    certified Phase 4.6.13 Temporal Intelligence.

    This is a one-to-one structural preparation stage.

    It does NOT:
    - reparse the article body,
    - detect uncertainty signals,
    - classify possibility or likelihood,
    - classify approximation,
    - classify frequency qualification,
    - classify epistemic uncertainty,
    - classify evidential hedging,
    - classify variability,
    - resolve uncertainty scope or target,
    - infer unstated uncertainty,
    - convert modal language into numeric probability,
    - perform quantitative reasoning,
    - perform causal reasoning,
    - perform Analogical Intelligence,
    - perform Similarity Intelligence,
    - perform new Temporal Intelligence,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    intake = validate_uncertainty_intelligence_intake_v1(
        certified_temporal_result
    )

    if (
        intake.get(
            "status"
        )
        != "UNCERTAINTY_INTELLIGENCE_INTAKE_VALIDATED"
    ):
        raise UncertaintyIntelligenceError(
            "Canonical Uncertainty Intelligence intake "
            "was not validated."
        )

    identity = dict(
        certified_temporal_result.get(
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

    if not article_id:
        raise UncertaintyIntelligenceError(
            "Certified Temporal article_id is required."
        )

    temporal_units = list(
        certified_temporal_result.get(
            "temporal_claim_units"
        )
        or []
    )

    uncertainty_units = []
    uncertainty_sections = []

    seen_uncertainty_ids = set()
    seen_temporal_ids = set()
    seen_statement_ids = set()
    seen_sentence_ids = set()

    previous_global_index = None

    units_by_section = {}
    section_metadata = {}

    for temporal_unit in temporal_units:

        if not isinstance(
            temporal_unit,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every certified Temporal Claim Unit "
                "must be a mapping."
            )

        temporal_claim_unit_id = str(
            temporal_unit.get(
                "temporal_claim_unit_id"
            )
            or ""
        )

        statement_id = str(
            temporal_unit.get(
                "statement_evidence_id"
            )
            or ""
        )

        sentence_id = str(
            temporal_unit.get(
                "sentence_id"
            )
            or ""
        )

        section_id = str(
            temporal_unit.get(
                "section_id"
            )
            or ""
        )

        if not temporal_claim_unit_id:
            raise UncertaintyIntelligenceError(
                "Temporal Claim Unit ID is required."
            )

        if not temporal_claim_unit_id.startswith(
            "temporal_claim_"
        ):
            raise UncertaintyIntelligenceError(
                "Unexpected Temporal Claim Unit ID format."
            )

        if not statement_id:
            raise UncertaintyIntelligenceError(
                "statement_evidence_id is required."
            )

        if not sentence_id:
            raise UncertaintyIntelligenceError(
                "sentence_id is required."
            )

        if not section_id:
            raise UncertaintyIntelligenceError(
                "section_id is required."
            )

        if temporal_claim_unit_id in seen_temporal_ids:
            raise UncertaintyIntelligenceError(
                "Duplicate Temporal Claim Unit ID."
            )

        if statement_id in seen_statement_ids:
            raise UncertaintyIntelligenceError(
                "Duplicate statement_evidence_id."
            )

        if sentence_id in seen_sentence_ids:
            raise UncertaintyIntelligenceError(
                "Duplicate sentence_id."
            )

        if (
            temporal_unit.get(
                "article_id"
            )
            != article_id
        ):
            raise UncertaintyIntelligenceError(
                "Temporal Claim Unit article identity mismatch."
            )

        global_index = temporal_unit.get(
            "sentence_global_index"
        )

        article_position = temporal_unit.get(
            "article_position"
        )

        if not isinstance(
            global_index,
            int,
        ):
            raise UncertaintyIntelligenceError(
                "sentence_global_index must be an integer."
            )

        if not isinstance(
            article_position,
            int,
        ):
            raise UncertaintyIntelligenceError(
                "article_position must be an integer."
            )

        if (
            previous_global_index is not None
            and global_index <= previous_global_index
        ):
            raise UncertaintyIntelligenceError(
                "Certified Temporal Claim Units are not "
                "in canonical sentence order."
            )

        temporal_state = dict(
            temporal_unit.get(
                "temporal_analysis_state"
            )
            or {}
        )

        required_complete_temporal_stages = (
            "temporal_signal_interpretation",
            "temporal_candidate_extraction",
            "temporal_anchor_participant_grounding",
            "temporal_relation_orientation",
            "point_duration_interval_validation",
            "sequence_boundary_recurrence_validation",
            "same_sentence_temporal_validation",
            "cross_sentence_temporal_anchoring",
            "temporal_evidence_assessment",
            "duplicate_temporal_resolution",
            "article_temporal_consolidation",
            "final_temporal_intelligence_result",
            "temporal_intelligence_certification",
        )

        for stage_name in required_complete_temporal_stages:
            if (
                temporal_state.get(
                    stage_name
                )
                != "COMPLETE"
            ):
                raise UncertaintyIntelligenceError(
                    "Temporal Claim Unit analysis is incomplete at "
                    + stage_name
                    + "."
                )

        upstream_boundaries = dict(
            temporal_unit.get(
                "processing_boundaries"
            )
            or {}
        )

        required_true_upstream_boundaries = (
            "final_temporal_result_built",
            "temporal_intelligence_certification_performed",
        )

        for boundary_name in required_true_upstream_boundaries:
            if (
                upstream_boundaries.get(
                    boundary_name
                )
                is not True
            ):
                raise UncertaintyIntelligenceError(
                    "Certified Temporal Claim Unit boundary "
                    "must be True: "
                    + boundary_name
                )

        required_false_upstream_boundaries = (
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
                raise UncertaintyIntelligenceError(
                    "Certified Temporal Claim Unit boundary "
                    "must remain False: "
                    + boundary_name
                )

        if (
            temporal_unit.get(
                "temporal_intelligence_certified"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Temporal Claim Unit must be certified before "
                "Uncertainty Claim Unit preparation."
            )

        uncertainty_claim_unit_id = (
            "uncertainty_claim_"
            + temporal_claim_unit_id[
                len("temporal_claim_"):
            ]
        )

        if uncertainty_claim_unit_id in seen_uncertainty_ids:
            raise UncertaintyIntelligenceError(
                "Duplicate Uncertainty Claim Unit ID."
            )

        uncertainty_unit = {
            "uncertainty_claim_unit_id":
                uncertainty_claim_unit_id,

            "upstream_temporal_claim_unit_id":
                temporal_claim_unit_id,

            "upstream_similarity_claim_unit_id":
                temporal_unit.get(
                    "upstream_similarity_claim_unit_id"
                ),

            "upstream_analogical_claim_unit_id":
                temporal_unit.get(
                    "upstream_analogical_claim_unit_id"
                ),

            "upstream_procedural_claim_unit_id":
                temporal_unit.get(
                    "upstream_procedural_claim_unit_id"
                ),

            "upstream_quantitative_claim_unit_id":
                temporal_unit.get(
                    "upstream_quantitative_claim_unit_id"
                ),

            "upstream_causal_claim_unit_id":
                temporal_unit.get(
                    "upstream_causal_claim_unit_id"
                ),

            "upstream_relational_claim_unit_id":
                temporal_unit.get(
                    "upstream_relational_claim_unit_id"
                ),

            "upstream_logical_claim_unit_id":
                temporal_unit.get(
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
                temporal_unit.get(
                    "section_evidence_unit_id"
                ),

            "section_index":
                temporal_unit.get(
                    "section_index"
                ),

            "section_title":
                temporal_unit.get(
                    "section_title"
                ),

            "heading_level":
                temporal_unit.get(
                    "heading_level"
                ),

            "block_id":
                temporal_unit.get(
                    "block_id"
                ),

            "paragraph_id":
                temporal_unit.get(
                    "paragraph_id"
                ),

            "block_type":
                temporal_unit.get(
                    "block_type"
                ),

            "block_index":
                temporal_unit.get(
                    "block_index"
                ),

            "sentence_index":
                temporal_unit.get(
                    "sentence_index"
                ),

            "sentence_global_index":
                global_index,

            "article_position":
                article_position,

            "claim_index_in_section":
                temporal_unit.get(
                    "claim_index_in_section"
                ),

            "text":
                temporal_unit.get(
                    "text"
                ),

            "word_count":
                temporal_unit.get(
                    "word_count"
                ),

            "character_count":
                temporal_unit.get(
                    "character_count"
                ),

            "statement_form":
                temporal_unit.get(
                    "statement_form"
                ),

            "canonical_claim_candidate":
                temporal_unit.get(
                    "canonical_claim_candidate"
                )
                is True,

            "evidence_context":
                dict(
                    temporal_unit.get(
                        "evidence_context"
                    )
                    or {}
                ),

            "upstream_temporal_analysis_state":
                temporal_state,

            "upstream_temporal_processing_boundaries":
                upstream_boundaries,

            "uncertainty_analysis_state": {
                "uncertainty_signal_interpretation":
                    "PENDING",

                "uncertainty_candidate_extraction":
                    "PENDING",

                "uncertainty_scope_target_grounding":
                    "PENDING",

                "uncertainty_type_classification":
                    "PENDING",

                "explicitness_strength_validation":
                    "PENDING",

                "same_sentence_uncertainty_validation":
                    "PENDING",

                "cross_sentence_uncertainty_anchoring":
                    "PENDING",

                "uncertainty_evidence_assessment":
                    "PENDING",

                "duplicate_uncertainty_resolution":
                    "PENDING",
            },

            "processing_boundaries": {
                "article_local_only":
                    True,

                "uncertainty_claim_unit_prepared":
                    True,

                "article_body_reparsed":
                    False,

                "uncertainty_signal_interpretation_performed":
                    False,

                "uncertainty_candidate_extraction_performed":
                    False,

                "uncertainty_scope_grounding_performed":
                    False,

                "uncertainty_type_classification_performed":
                    False,

                "uncertainty_explicitness_strength_validation_performed":
                    False,

                "same_sentence_uncertainty_validation_performed":
                    False,

                "cross_sentence_uncertainty_anchoring_performed":
                    False,

                "uncertainty_evidence_assessment_performed":
                    False,

                "uncertainty_duplicate_resolution_performed":
                    False,

                "lexical_uncertainty_signal_is_validated_uncertainty":
                    False,

                "lexical_modal_is_automatically_uncertainty":
                    False,

                "unstated_uncertainty_inference_performed":
                    False,

                "numeric_probability_inference_performed":
                    False,

                "new_quantitative_reasoning_performed":
                    False,

                "new_causal_reasoning_performed":
                    False,

                "analogical_reasoning_performed":
                    False,

                "similarity_reasoning_performed":
                    False,

                "new_temporal_reasoning_performed":
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

        uncertainty_units.append(
            uncertainty_unit
        )

        units_by_section.setdefault(
            section_id,
            [],
        ).append(
            uncertainty_unit
        )

        if section_id not in section_metadata:
            section_metadata[
                section_id
            ] = {
                "section_id":
                    section_id,

                "section_index":
                    temporal_unit.get(
                        "section_index"
                    ),

                "section_title":
                    temporal_unit.get(
                        "section_title"
                    ),

                "heading_level":
                    temporal_unit.get(
                        "heading_level"
                    ),
            }

        seen_uncertainty_ids.add(
            uncertainty_claim_unit_id
        )

        seen_temporal_ids.add(
            temporal_claim_unit_id
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

    for unit in uncertainty_units:
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

        uncertainty_sections.append({
            **metadata,

            "upstream_temporal_claim_count":
                len(
                    section_units
                ),

            "uncertainty_claim_unit_count":
                len(
                    section_units
                ),

            "uncertainty_claim_units":
                section_units,
        })

    if (
        len(
            uncertainty_units
        )
        != len(
            temporal_units
        )
    ):
        raise UncertaintyIntelligenceError(
            "Uncertainty Claim Unit construction must remain "
            "one-to-one with Temporal Claim Units."
        )

    return {
        "schema_version":
            "uncertainty_claim_units_v1",

        "uncertainty_intelligence_version":
            "uncertainty_intelligence_v1",

        "phase":
            "4.6.14",

        "patch":
            "4.6.14D",

        "status":
            "UNCERTAINTY_CLAIM_UNITS_PREPARED",

        "article_identity":
            identity,

        "temporal_claim_unit_count":
            len(
                temporal_units
            ),

        "uncertainty_claim_unit_count":
            len(
                uncertainty_units
            ),

        "section_count":
            len(
                uncertainty_sections
            ),

        "uncertainty_sections":
            uncertainty_sections,

        "uncertainty_claim_units":
            uncertainty_units,

        "construction_summary": {
            "source_temporal_claim_unit_count":
                len(
                    temporal_units
                ),

            "uncertainty_claim_unit_count":
                len(
                    uncertainty_units
                ),

            "one_to_one_temporal_mapping":
                (
                    len(
                        uncertainty_units
                    )
                    == len(
                        temporal_units
                    )
                ),

            "canonical_order_preserved":
                True,

            "canonical_text_preserved":
                True,

            "evidence_context_preserved":
                True,

            "temporal_context_preserved":
                True,

            "article_body_reparsed":
                False,

            "uncertainty_signals_interpreted":
                False,

            "uncertainty_types_classified":
                False,

            "uncertainty_scope_resolved":
                False,

            "numeric_probability_inferred":
                False,
        },

        "processing_boundaries": {
            "article_body_reparsed":
                False,

            "uncertainty_claim_units_prepared":
                True,

            "uncertainty_signal_interpretation_performed":
                False,

            "uncertainty_candidate_extraction_performed":
                False,

            "uncertainty_scope_grounding_performed":
                False,

            "uncertainty_type_classification_performed":
                False,

            "uncertainty_explicitness_strength_validation_performed":
                False,

            "same_sentence_uncertainty_validation_performed":
                False,

            "cross_sentence_uncertainty_anchoring_performed":
                False,

            "uncertainty_evidence_assessment_performed":
                False,

            "uncertainty_duplicate_resolution_performed":
                False,

            "lexical_uncertainty_signal_is_validated_uncertainty":
                False,

            "lexical_modal_is_automatically_uncertainty":
                False,

            "unstated_uncertainty_inference_performed":
                False,

            "numeric_probability_inference_performed":
                False,

            "new_quantitative_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "similarity_reasoning_performed":
                False,

            "new_temporal_reasoning_performed":
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
            "uncertainty_signal_interpretation",
    }


def interpret_uncertainty_signals_v1(
    uncertainty_claim_units_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Interpret explicit article-local Uncertainty lexical signals.

    Stage E identifies explicit lexical evidence only.

    It does NOT:
    - validate that a lexical signal expresses uncertainty,
    - extract canonical uncertainty candidates,
    - resolve uncertainty scope or target,
    - classify final uncertainty type,
    - determine final commitment strength,
    - perform cross-sentence uncertainty anchoring,
    - infer unstated uncertainty,
    - convert modal language into numeric probability,
    - perform quantitative reasoning,
    - perform causal reasoning,
    - perform Analogical Intelligence,
    - perform Similarity Intelligence,
    - perform new Temporal Intelligence,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        uncertainty_claim_units_result,
        Mapping,
    ):
        raise UncertaintyIntelligenceError(
            "uncertainty_claim_units_result must be a mapping."
        )

    if (
        uncertainty_claim_units_result.get(
            "schema_version"
        )
        != "uncertainty_claim_units_v1"
    ):
        raise UncertaintyIntelligenceError(
            "Stage E requires uncertainty_claim_units_v1."
        )

    if (
        uncertainty_claim_units_result.get(
            "status"
        )
        != "UNCERTAINTY_CLAIM_UNITS_PREPARED"
    ):
        raise UncertaintyIntelligenceError(
            "Uncertainty Claim Units must be prepared before Stage E."
        )

    if (
        uncertainty_claim_units_result.get(
            "phase"
        )
        != "4.6.14"
    ):
        raise UncertaintyIntelligenceError(
            "Stage E requires Phase 4.6.14 input."
        )

    if (
        uncertainty_claim_units_result.get(
            "patch"
        )
        != "4.6.14D"
    ):
        raise UncertaintyIntelligenceError(
            "Stage E requires canonical 4.6.14D input."
        )

    if (
        uncertainty_claim_units_result.get(
            "next_stage"
        )
        != "uncertainty_signal_interpretation"
    ):
        raise UncertaintyIntelligenceError(
            "Stage D must hand off to "
            "uncertainty_signal_interpretation."
        )

    if (
        uncertainty_claim_units_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise UncertaintyIntelligenceError(
            "Uncertainty Intelligence must remain transient."
        )

    top_boundaries = dict(
        uncertainty_claim_units_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        top_boundaries.get(
            "uncertainty_claim_units_prepared"
        )
        is not True
    ):
        raise UncertaintyIntelligenceError(
            "Uncertainty Claim Unit preparation boundary "
            "must be complete before Stage E."
        )

    if (
        top_boundaries.get(
            "uncertainty_signal_interpretation_performed"
        )
        is not False
    ):
        raise UncertaintyIntelligenceError(
            "Uncertainty signal interpretation must be "
            "pending before Stage E."
        )

    signal_specs = (
        (
            "POSSIBILITY_MODAL",
            "EXPLICIT_POSSIBILITY_SIGNAL",
            re.compile(
                r"\b(?:may|might|could)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "POSSIBILITY_LEXEME",
            "EXPLICIT_POSSIBILITY_SIGNAL",
            re.compile(
                r"\b(?:possible|possibly)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "CHANCE_CONSTRUCTION",
            "EXPLICIT_POSSIBILITY_SIGNAL",
            re.compile(
                r"\b(?:there(?:'s| is)\s+)?"
                r"(?:a\s+)?chance\s+that\b",
                re.IGNORECASE,
            ),
        ),
        (
            "LIKELIHOOD",
            "EXPLICIT_LIKELIHOOD_SIGNAL",
            re.compile(
                r"\b(?:likely|unlikely|probably|probable)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "NUMERIC_APPROXIMATION",
            "EXPLICIT_APPROXIMATION_SIGNAL",
            re.compile(
                r"\b(?:about|around|approximately|roughly|nearly|almost)"
                r"\s+(?=(?:age\s+)?\d)",
                re.IGNORECASE,
            ),
        ),
        (
            "NON_UNIVERSAL_FREQUENCY",
            "EXPLICIT_NON_UNIVERSAL_FREQUENCY_SIGNAL",
            re.compile(
                r"\b(?:usually|generally|typically|often|sometimes|"
                r"occasionally|rarely|seldom)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "UNKNOWN_OR_UNCLEAR",
            "EXPLICIT_EPISTEMIC_UNCERTAINTY_SIGNAL",
            re.compile(
                r"\b(?:unclear|unknown|uncertain|uncertainty|not\s+known)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "EVIDENCE_LIMITATION",
            "EXPLICIT_EVIDENCE_LIMITATION_SIGNAL",
            re.compile(
                r"\b(?:"
                r"(?:evidence|data|research|information)\s+"
                r"(?:is|are|remains?|remain)\s+"
                r"(?:limited|insufficient|inconclusive)"
                r"|"
                r"(?:limited|insufficient|inconclusive)\s+"
                r"(?:evidence|data|research|information)"
                r")\b",
                re.IGNORECASE,
            ),
        ),
        (
            "CONFLICTED_EVIDENCE",
            "EXPLICIT_CONFLICTED_EVIDENCE_SIGNAL",
            re.compile(
                r"\b(?:"
                r"(?:mixed|conflicting|inconsistent)\s+"
                r"(?:evidence|findings|results|data)"
                r"|"
                r"(?:evidence|findings|results|data)\s+"
                r"(?:is|are)\s+"
                r"(?:mixed|conflicting|inconsistent)"
                r")\b",
                re.IGNORECASE,
            ),
        ),
        (
            "NOT_ALWAYS",
            "EXPLICIT_NON_UNIVERSAL_FREQUENCY_SIGNAL",
            re.compile(
                r"\bnot\s+always\b",
                re.IGNORECASE,
            ),
        ),
    )

    ambiguous_specs = (
        (
            "AMBIGUOUS_CAN_MODAL",
            re.compile(
                r"\b(?:can|cannot|can't)\b",
                re.IGNORECASE,
            ),
            "CAN_MAY_EXPRESS_CAPABILITY_PERMISSION_OR_POSSIBILITY",
        ),
        (
            "AMBIGUOUS_SHOULD_MODAL",
            re.compile(
                r"\bshould\b",
                re.IGNORECASE,
            ),
            "SHOULD_MAY_EXPRESS_ADVICE_EXPECTATION_OR_NORMATIVE_FORCE",
        ),
        (
            "AMBIGUOUS_WOULD_MODAL",
            re.compile(
                r"\bwould\b",
                re.IGNORECASE,
            ),
            "WOULD_MAY_EXPRESS_CONDITIONALITY_HABIT_OR_HYPOTHETICAL_FORCE",
        ),
        (
            "AMBIGUOUS_BARE_ABOUT",
            re.compile(
                r"\babout\b",
                re.IGNORECASE,
            ),
            "ABOUT_MAY_BE_PREPOSITIONAL_TOPIC_LANGUAGE_OR_APPROXIMATION",
        ),
        (
            "AMBIGUOUS_BARE_AROUND",
            re.compile(
                r"\baround\b",
                re.IGNORECASE,
            ),
            "AROUND_MAY_BE_SPATIAL_LANGUAGE_OR_APPROXIMATION",
        ),
        (
            "AMBIGUOUS_APPEARS",
            re.compile(
                r"\bappears?\b",
                re.IGNORECASE,
            ),
            "APPEAR_MAY_EXPRESS_PERCEPTION_STATE_OR_EVIDENTIAL_HEDGING",
        ),
        (
            "AMBIGUOUS_SEEMS",
            re.compile(
                r"\bseems?\b",
                re.IGNORECASE,
            ),
            "SEEM_REQUIRES_SCOPE_AND_CLAIM_VALIDATION",
        ),
        (
            "AMBIGUOUS_INDICATES",
            re.compile(
                r"\bindicates?\b",
                re.IGNORECASE,
            ),
            "INDICATE_MAY_EXPRESS_EVIDENCE_SIGNAL_OR_ORDINARY_RELATION",
        ),
        (
            "AMBIGUOUS_VARIABILITY",
            re.compile(
                r"\b(?:vary|varies|varied|varying|depends?|depending)\b",
                re.IGNORECASE,
            ),
            "VARIABILITY_LANGUAGE_REQUIRES_TARGET_AND_SCOPE_VALIDATION",
        ),
        (
            "AMBIGUOUS_DIFFERENT",
            re.compile(
                r"\bdifferent\b",
                re.IGNORECASE,
            ),
            "DIFFERENT_IS_NOT_AUTOMATICALLY_UNCERTAINTY_OR_VARIABILITY",
        ),
    )

    source_units = list(
        uncertainty_claim_units_result.get(
            "uncertainty_claim_units"
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
            raise UncertaintyIntelligenceError(
                "Every Uncertainty Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "uncertainty_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "uncertainty_signal_interpretation"
            )
            != "PENDING"
        ):
            raise UncertaintyIntelligenceError(
                "Uncertainty signal interpretation must "
                "be PENDING before Stage E."
            )

        if (
            state.get(
                "uncertainty_candidate_extraction"
            )
            != "PENDING"
        ):
            raise UncertaintyIntelligenceError(
                "Uncertainty candidate extraction must "
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
                "uncertainty_claim_unit_prepared"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Uncertainty Claim Unit preparation boundary "
                "is incomplete."
            )

        required_false_boundaries = (
            "uncertainty_signal_interpretation_performed",
            "uncertainty_candidate_extraction_performed",
            "uncertainty_scope_grounding_performed",
            "uncertainty_type_classification_performed",
            "uncertainty_explicitness_strength_validation_performed",
            "same_sentence_uncertainty_validation_performed",
            "cross_sentence_uncertainty_anchoring_performed",
            "uncertainty_evidence_assessment_performed",
            "uncertainty_duplicate_resolution_performed",
            "unstated_uncertainty_inference_performed",
            "numeric_probability_inference_performed",
            "new_quantitative_reasoning_performed",
            "new_causal_reasoning_performed",
            "analogical_reasoning_performed",
            "similarity_reasoning_performed",
            "new_temporal_reasoning_performed",
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
                raise UncertaintyIntelligenceError(
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

                    "uncertainty_semantic_class":
                        semantic_class,

                    "matched_text":
                        match.group(0),

                    "character_start":
                        match.start(),

                    "character_end":
                        match.end(),

                    "article_asserted_signal":
                        True,

                    "uncertainty_validated":
                        False,

                    "uncertainty_candidate_extracted":
                        False,

                    "uncertainty_scope_grounded":
                        False,

                    "uncertainty_type_classified":
                        False,

                    "uncertainty_strength_validated":
                        False,

                    "same_sentence_uncertainty_validated":
                        False,

                    "cross_sentence_uncertainty_anchor_resolved":
                        False,

                    "numeric_probability_inference_performed":
                        False,

                    "unstated_uncertainty_inference_performed":
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
                        "AMBIGUOUS_UNCERTAINTY_LEXEME_DEFERRED",

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

                    "uncertainty_validation_performed":
                        False,

                    "uncertainty_scope_inference_performed":
                        False,

                    "numeric_probability_inference_performed":
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
            "uncertainty_signal_interpretation"
        ] = "COMPLETE"

        interpreted_boundaries = dict(
            boundaries
        )

        interpreted_boundaries[
            "uncertainty_signal_interpretation_performed"
        ] = True

        interpreted_boundaries[
            "uncertainty_candidate_extraction_performed"
        ] = False

        interpreted_boundaries[
            "uncertainty_scope_grounding_performed"
        ] = False

        interpreted_boundaries[
            "uncertainty_type_classification_performed"
        ] = False

        interpreted_boundaries[
            "uncertainty_explicitness_strength_validation_performed"
        ] = False

        interpreted_boundaries[
            "same_sentence_uncertainty_validation_performed"
        ] = False

        interpreted_boundaries[
            "cross_sentence_uncertainty_anchoring_performed"
        ] = False

        interpreted_boundaries[
            "uncertainty_evidence_assessment_performed"
        ] = False

        interpreted_boundaries[
            "uncertainty_duplicate_resolution_performed"
        ] = False

        interpreted_boundaries[
            "unstated_uncertainty_inference_performed"
        ] = False

        interpreted_boundaries[
            "numeric_probability_inference_performed"
        ] = False

        interpreted_boundaries[
            "truth_assessment_performed"
        ] = False

        interpreted_boundaries[
            "external_authority_check_performed"
        ] = False

        interpreted_boundaries[
            "semantic_memory_write_performed"
        ] = False

        interpreted_boundaries[
            "persistence_performed"
        ] = False

        interpreted_unit = dict(
            unit
        )

        interpreted_unit.update({
            "uncertainty_signals":
                signals,

            "uncertainty_signal_exclusions":
                exclusions,

            "uncertainty_signal_count":
                unit_total,

            "uncertainty_signal_exclusion_count":
                len(
                    exclusions
                ),

            "has_uncertainty_signal":
                unit_total > 0,

            "uncertainty_signal_interpretation_scope":
                (
                    "ARTICLE_LOCAL_EXPLICIT_"
                    "UNCERTAINTY_SIGNAL_ONLY"
                ),

            "uncertainty_analysis_state":
                interpreted_state,

            "processing_boundaries":
                interpreted_boundaries,
        })

        interpreted_units.append(
            interpreted_unit
        )

        unit_id = str(
            interpreted_unit.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise UncertaintyIntelligenceError(
                "Every interpreted Uncertainty Claim Unit "
                "requires an ID."
            )

        if unit_id in interpreted_by_id:
            raise UncertaintyIntelligenceError(
                "Duplicate interpreted Uncertainty Claim Unit ID."
            )

        interpreted_by_id[
            unit_id
        ] = interpreted_unit

    interpreted_sections = []

    for section in (
        uncertainty_claim_units_result.get(
            "uncertainty_sections"
        )
        or []
    ):

        if not isinstance(
            section,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "uncertainty_claim_units"
            )
            or []
        ):

            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise UncertaintyIntelligenceError(
                    "Every section Uncertainty Claim Unit "
                    "reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "uncertainty_claim_unit_id"
                )
                or ""
            )

            resolved_unit = interpreted_by_id.get(
                unit_id
            )

            if resolved_unit is None:
                raise UncertaintyIntelligenceError(
                    "Uncertainty section references "
                    "an unknown claim unit."
                )

            section_units.append(
                resolved_unit
            )

        interpreted_sections.append({
            **dict(
                section
            ),

            "uncertainty_claim_units":
                section_units,

            "uncertainty_signal_unit_count":
                sum(
                    1
                    for unit in section_units
                    if unit.get(
                        "has_uncertainty_signal"
                    )
                    is True
                ),

            "uncertainty_signal_count":
                sum(
                    int(
                        unit.get(
                            "uncertainty_signal_count"
                        )
                        or 0
                    )
                    for unit in section_units
                ),

            "uncertainty_signal_exclusion_count":
                sum(
                    int(
                        unit.get(
                            "uncertainty_signal_exclusion_count"
                        )
                        or 0
                    )
                    for unit in section_units
                ),
        })

    result = dict(
        uncertainty_claim_units_result
    )

    result_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    result_boundaries[
        "uncertainty_signal_interpretation_performed"
    ] = True

    result_boundaries[
        "uncertainty_candidate_extraction_performed"
    ] = False

    result_boundaries[
        "uncertainty_scope_grounding_performed"
    ] = False

    result_boundaries[
        "uncertainty_type_classification_performed"
    ] = False

    result_boundaries[
        "uncertainty_explicitness_strength_validation_performed"
    ] = False

    result_boundaries[
        "same_sentence_uncertainty_validation_performed"
    ] = False

    result_boundaries[
        "cross_sentence_uncertainty_anchoring_performed"
    ] = False

    result_boundaries[
        "uncertainty_evidence_assessment_performed"
    ] = False

    result_boundaries[
        "uncertainty_duplicate_resolution_performed"
    ] = False

    result_boundaries[
        "unstated_uncertainty_inference_performed"
    ] = False

    result_boundaries[
        "numeric_probability_inference_performed"
    ] = False

    result_boundaries[
        "truth_assessment_performed"
    ] = False

    result_boundaries[
        "external_authority_check_performed"
    ] = False

    result_boundaries[
        "semantic_memory_write_performed"
    ] = False

    result_boundaries[
        "persistence_performed"
    ] = False

    result.update({
        "schema_version":
            "uncertainty_signal_interpretation_v1",

        "patch":
            "4.6.14E",

        "status":
            "UNCERTAINTY_SIGNAL_INTERPRETATION_COMPLETE",

        "uncertainty_sections":
            interpreted_sections,

        "uncertainty_claim_units":
            interpreted_units,

        "uncertainty_signal_summary": {
            "claim_unit_count":
                len(
                    interpreted_units
                ),

            "units_with_uncertainty_signals":
                units_with_signals,

            "total_uncertainty_signal_count":
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

            "signal_presence_not_uncertainty_validity":
                True,

            "can_not_automatically_uncertainty":
                True,

            "should_not_automatically_uncertainty":
                True,

            "would_not_automatically_uncertainty":
                True,

            "bare_about_not_automatically_approximation":
                True,

            "bare_around_not_automatically_approximation":
                True,

            "appear_not_automatically_evidential_hedging":
                True,

            "different_not_automatically_variability":
                True,

            "uncertainty_candidates_extracted":
                False,

            "uncertainty_scope_grounded":
                False,

            "uncertainty_types_classified":
                False,

            "numeric_probability_inferred":
                False,

            "unstated_uncertainty_inferred":
                False,

            "truth_assessment_performed":
                False,
        },

        "processing_boundaries":
            result_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "uncertainty_candidate_extraction",
    })

    return result


def extract_uncertainty_candidates_v1(
    signal_interpretation_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Convert eligible explicit lexical Uncertainty signals into
    canonical article-local Uncertainty candidates.

    Stage F does NOT:
    - promote ambiguous exclusions,
    - resolve uncertainty scope or target,
    - perform final uncertainty type classification,
    - validate commitment strength,
    - perform same-sentence semantic validation,
    - perform cross-sentence anchoring,
    - infer unstated uncertainty,
    - convert modality into numeric probability,
    - assess factual truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        signal_interpretation_result,
        Mapping,
    ):
        raise UncertaintyIntelligenceError(
            "signal_interpretation_result must be a mapping."
        )

    if (
        signal_interpretation_result.get(
            "schema_version"
        )
        != "uncertainty_signal_interpretation_v1"
    ):
        raise UncertaintyIntelligenceError(
            "Stage F requires "
            "uncertainty_signal_interpretation_v1."
        )

    if (
        signal_interpretation_result.get(
            "status"
        )
        != "UNCERTAINTY_SIGNAL_INTERPRETATION_COMPLETE"
    ):
        raise UncertaintyIntelligenceError(
            "Stage E must be complete before Stage F."
        )

    if (
        signal_interpretation_result.get(
            "phase"
        )
        != "4.6.14"
    ):
        raise UncertaintyIntelligenceError(
            "Stage F requires Phase 4.6.14 input."
        )

    if (
        signal_interpretation_result.get(
            "patch"
        )
        != "4.6.14E"
    ):
        raise UncertaintyIntelligenceError(
            "Stage F requires canonical 4.6.14E input."
        )

    if (
        signal_interpretation_result.get(
            "next_stage"
        )
        != "uncertainty_candidate_extraction"
    ):
        raise UncertaintyIntelligenceError(
            "Stage E must hand off to "
            "uncertainty_candidate_extraction."
        )

    if (
        signal_interpretation_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise UncertaintyIntelligenceError(
            "Uncertainty Intelligence must remain transient."
        )

    top_boundaries = dict(
        signal_interpretation_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        top_boundaries.get(
            "uncertainty_signal_interpretation_performed"
        )
        is not True
    ):
        raise UncertaintyIntelligenceError(
            "Stage-E interpretation boundary must be complete."
        )

    if (
        top_boundaries.get(
            "uncertainty_candidate_extraction_performed"
        )
        is not False
    ):
        raise UncertaintyIntelligenceError(
            "Candidate extraction must be pending before Stage F."
        )

    source_units = list(
        signal_interpretation_result.get(
            "uncertainty_claim_units"
        )
        or []
    )

    extracted_units = []
    extracted_by_id = {}

    article_candidates = []

    seen_candidate_ids = set()

    units_with_candidates = 0
    total_candidate_count = 0

    signal_type_counts = {}
    semantic_class_counts = {}

    for unit in source_units:

        if not isinstance(
            unit,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise UncertaintyIntelligenceError(
                "Uncertainty Claim Unit ID is required."
            )

        if not unit_id.startswith(
            "uncertainty_claim_"
        ):
            raise UncertaintyIntelligenceError(
                "Unexpected Uncertainty Claim Unit ID format."
            )

        state = dict(
            unit.get(
                "uncertainty_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "uncertainty_signal_interpretation"
            )
            != "COMPLETE"
        ):
            raise UncertaintyIntelligenceError(
                "Signal interpretation must be COMPLETE "
                "before candidate extraction."
            )

        if (
            state.get(
                "uncertainty_candidate_extraction"
            )
            != "PENDING"
        ):
            raise UncertaintyIntelligenceError(
                "Candidate extraction must be PENDING "
                "before Stage F."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "uncertainty_signal_interpretation_performed"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Unit Stage-E boundary must be complete."
            )

        required_false_boundaries = (
            "uncertainty_candidate_extraction_performed",
            "uncertainty_scope_grounding_performed",
            "uncertainty_type_classification_performed",
            "uncertainty_explicitness_strength_validation_performed",
            "same_sentence_uncertainty_validation_performed",
            "cross_sentence_uncertainty_anchoring_performed",
            "uncertainty_evidence_assessment_performed",
            "uncertainty_duplicate_resolution_performed",
            "unstated_uncertainty_inference_performed",
            "numeric_probability_inference_performed",
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
                raise UncertaintyIntelligenceError(
                    boundary_name
                    + " must remain False before Stage F."
                )

        source_text = str(
            unit.get(
                "text"
            )
            or ""
        )

        signals = list(
            unit.get(
                "uncertainty_signals"
            )
            or []
        )

        exclusions = list(
            unit.get(
                "uncertainty_signal_exclusions"
            )
            or []
        )

        for exclusion in exclusions:
            if not isinstance(
                exclusion,
                Mapping,
            ):
                raise UncertaintyIntelligenceError(
                    "Uncertainty exclusion must be a mapping."
                )

            if (
                exclusion.get(
                    "candidate_eligible"
                )
                is not False
            ):
                raise UncertaintyIntelligenceError(
                    "Ambiguous Stage-E exclusions "
                    "must remain candidate-ineligible."
                )

        candidates = []
        updated_signals = []

        seen_signal_keys = set()

        candidate_ordinal = 0

        for signal in signals:

            if not isinstance(
                signal,
                Mapping,
            ):
                raise UncertaintyIntelligenceError(
                    "Every Uncertainty signal must be a mapping."
                )

            signal_type = str(
                signal.get(
                    "signal_type"
                )
                or ""
            )

            semantic_class = str(
                signal.get(
                    "uncertainty_semantic_class"
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

            if not signal_type:
                raise UncertaintyIntelligenceError(
                    "Signal type is required."
                )

            if not semantic_class:
                raise UncertaintyIntelligenceError(
                    "Uncertainty semantic class is required."
                )

            if not matched_text:
                raise UncertaintyIntelligenceError(
                    "Signal matched_text is required."
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
                    source_text
                )
            ):
                raise UncertaintyIntelligenceError(
                    "Uncertainty signal span is invalid."
                )

            if (
                source_text[
                    start:end
                ]
                != matched_text
            ):
                raise UncertaintyIntelligenceError(
                    "Uncertainty signal span does not "
                    "match source text."
                )

            signal_key = (
                signal_type,
                start,
                end,
                matched_text,
            )

            if signal_key in seen_signal_keys:
                raise UncertaintyIntelligenceError(
                    "Duplicate Uncertainty lexical signal."
                )

            seen_signal_keys.add(
                signal_key
            )

            if (
                signal.get(
                    "article_asserted_signal"
                )
                is not True
            ):
                raise UncertaintyIntelligenceError(
                    "Stage-F candidates require "
                    "article-asserted lexical signals."
                )

            if (
                signal.get(
                    "uncertainty_validated"
                )
                is not False
            ):
                raise UncertaintyIntelligenceError(
                    "Stage F must receive unvalidated signals."
                )

            if (
                signal.get(
                    "uncertainty_candidate_extracted"
                )
                is not False
            ):
                raise UncertaintyIntelligenceError(
                    "Signal candidate extraction must be pending."
                )

            candidate_ordinal += 1

            suffix = unit_id[
                len("uncertainty_claim_"):
            ]

            candidate_id = (
                "uncertainty_candidate_"
                + suffix
                + "_"
                + str(
                    candidate_ordinal
                ).zfill(3)
            )

            if candidate_id in seen_candidate_ids:
                raise UncertaintyIntelligenceError(
                    "Duplicate Uncertainty Candidate ID."
                )

            seen_candidate_ids.add(
                candidate_id
            )

            candidate = {
                "uncertainty_candidate_id":
                    candidate_id,

                "uncertainty_claim_unit_id":
                    unit_id,

                "upstream_temporal_claim_unit_id":
                    unit.get(
                        "upstream_temporal_claim_unit_id"
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
                    source_text,

                "signal_type":
                    signal_type,

                "lexical_uncertainty_semantic_class":
                    semantic_class,

                "matched_text":
                    matched_text,

                "character_start":
                    start,

                "character_end":
                    end,

                "candidate_basis":
                    "ARTICLE_LOCAL_EXPLICIT_LEXICAL_SIGNAL",

                "candidate_status":
                    "EXPLICIT_UNCERTAINTY_CANDIDATE",

                "article_asserted_signal":
                    True,

                "uncertainty_scope_grounded":
                    False,

                "uncertainty_target_grounded":
                    False,

                "uncertainty_type_classified":
                    False,

                "uncertainty_explicitness_validated":
                    False,

                "uncertainty_strength_validated":
                    False,

                "same_sentence_uncertainty_validated":
                    False,

                "cross_sentence_uncertainty_anchor_resolved":
                    False,

                "uncertainty_evidence_assessed":
                    False,

                "duplicate_resolution_performed":
                    False,

                "unstated_uncertainty_inference_performed":
                    False,

                "numeric_probability_inference_performed":
                    False,

                "truth_assessment_performed":
                    False,

                "external_authority_checked":
                    False,

                "semantic_memory_write_performed":
                    False,

                "linking_decisions_performed":
                    False,

                "persistence_performed":
                    False,
            }

            candidates.append(
                candidate
            )

            article_candidates.append(
                candidate
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

            updated_signal = dict(
                signal
            )

            updated_signal[
                "uncertainty_candidate_extracted"
            ] = True

            updated_signal[
                "uncertainty_candidate_id"
            ] = candidate_id

            updated_signals.append(
                updated_signal
            )

        if candidates:
            units_with_candidates += 1

        total_candidate_count += len(
            candidates
        )

        updated_state = dict(
            state
        )

        updated_state[
            "uncertainty_candidate_extraction"
        ] = "COMPLETE"

        updated_boundaries = dict(
            boundaries
        )

        updated_boundaries[
            "uncertainty_candidate_extraction_performed"
        ] = True

        updated_boundaries[
            "uncertainty_scope_grounding_performed"
        ] = False

        updated_boundaries[
            "uncertainty_type_classification_performed"
        ] = False

        updated_boundaries[
            "uncertainty_explicitness_strength_validation_performed"
        ] = False

        updated_boundaries[
            "same_sentence_uncertainty_validation_performed"
        ] = False

        updated_boundaries[
            "cross_sentence_uncertainty_anchoring_performed"
        ] = False

        updated_boundaries[
            "uncertainty_evidence_assessment_performed"
        ] = False

        updated_boundaries[
            "uncertainty_duplicate_resolution_performed"
        ] = False

        updated_boundaries[
            "unstated_uncertainty_inference_performed"
        ] = False

        updated_boundaries[
            "numeric_probability_inference_performed"
        ] = False

        updated_boundaries[
            "truth_assessment_performed"
        ] = False

        updated_boundaries[
            "external_authority_check_performed"
        ] = False

        updated_boundaries[
            "semantic_memory_write_performed"
        ] = False

        updated_boundaries[
            "persistence_performed"
        ] = False

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "uncertainty_signals":
                updated_signals,

            "uncertainty_candidates":
                candidates,

            "uncertainty_candidate_count":
                len(
                    candidates
                ),

            "has_uncertainty_candidate":
                bool(
                    candidates
                ),

            "uncertainty_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        extracted_units.append(
            updated_unit
        )

        if unit_id in extracted_by_id:
            raise UncertaintyIntelligenceError(
                "Duplicate extracted Uncertainty Claim Unit ID."
            )

        extracted_by_id[
            unit_id
        ] = updated_unit

    extracted_sections = []

    for section in (
        signal_interpretation_result.get(
            "uncertainty_sections"
        )
        or []
    ):

        if not isinstance(
            section,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "uncertainty_claim_units"
            )
            or []
        ):

            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise UncertaintyIntelligenceError(
                    "Section Uncertainty Claim Unit "
                    "reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "uncertainty_claim_unit_id"
                )
                or ""
            )

            resolved = extracted_by_id.get(
                unit_id
            )

            if resolved is None:
                raise UncertaintyIntelligenceError(
                    "Uncertainty section references "
                    "an unknown claim unit."
                )

            section_units.append(
                resolved
            )

        extracted_sections.append({
            **dict(
                section
            ),

            "uncertainty_claim_units":
                section_units,

            "uncertainty_candidate_unit_count":
                sum(
                    1
                    for unit in section_units
                    if unit.get(
                        "has_uncertainty_candidate"
                    )
                    is True
                ),

            "uncertainty_candidate_count":
                sum(
                    int(
                        unit.get(
                            "uncertainty_candidate_count"
                        )
                        or 0
                    )
                    for unit in section_units
                ),
        })

    result = dict(
        signal_interpretation_result
    )

    result_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    result_boundaries[
        "uncertainty_candidate_extraction_performed"
    ] = True

    result_boundaries[
        "uncertainty_scope_grounding_performed"
    ] = False

    result_boundaries[
        "uncertainty_type_classification_performed"
    ] = False

    result_boundaries[
        "uncertainty_explicitness_strength_validation_performed"
    ] = False

    result_boundaries[
        "same_sentence_uncertainty_validation_performed"
    ] = False

    result_boundaries[
        "cross_sentence_uncertainty_anchoring_performed"
    ] = False

    result_boundaries[
        "uncertainty_evidence_assessment_performed"
    ] = False

    result_boundaries[
        "uncertainty_duplicate_resolution_performed"
    ] = False

    result_boundaries[
        "unstated_uncertainty_inference_performed"
    ] = False

    result_boundaries[
        "numeric_probability_inference_performed"
    ] = False

    result_boundaries[
        "truth_assessment_performed"
    ] = False

    result_boundaries[
        "external_authority_check_performed"
    ] = False

    result_boundaries[
        "semantic_memory_write_performed"
    ] = False

    result_boundaries[
        "persistence_performed"
    ] = False

    result.update({
        "schema_version":
            "uncertainty_candidate_extraction_v1",

        "patch":
            "4.6.14F",

        "status":
            "UNCERTAINTY_CANDIDATE_EXTRACTION_COMPLETE",

        "uncertainty_sections":
            extracted_sections,

        "uncertainty_claim_units":
            extracted_units,

        "uncertainty_candidates":
            article_candidates,

        "uncertainty_candidate_summary": {
            "claim_unit_count":
                len(
                    extracted_units
                ),

            "units_with_uncertainty_candidates":
                units_with_candidates,

            "total_uncertainty_candidate_count":
                total_candidate_count,

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

            "explicit_signal_to_candidate_mapping":
                "ONE_TO_ONE",

            "ambiguous_exclusions_promoted":
                False,

            "zero_candidate_units_allowed":
                True,

            "scope_grounded":
                False,

            "types_classified":
                False,

            "strength_validated":
                False,

            "numeric_probability_inferred":
                False,

            "unstated_uncertainty_inferred":
                False,
        },

        "processing_boundaries":
            result_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "uncertainty_scope_target_grounding",
    })

    return result


def ground_uncertainty_scope_targets_v1(
    candidate_extraction_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Ground explicit Uncertainty candidates to article-local source scope.

    Stage G is deliberately conservative.

    It grounds each candidate to its exact source sentence and preserves
    the exact lexical signal span. It does not infer an unstated semantic
    object, proposition, probability, truth state, or cross-sentence scope.
    """

    if not isinstance(
        candidate_extraction_result,
        Mapping,
    ):
        raise UncertaintyIntelligenceError(
            "candidate_extraction_result must be a mapping."
        )

    if (
        candidate_extraction_result.get(
            "schema_version"
        )
        != "uncertainty_candidate_extraction_v1"
    ):
        raise UncertaintyIntelligenceError(
            "Stage G requires uncertainty_candidate_extraction_v1."
        )

    if (
        candidate_extraction_result.get(
            "status"
        )
        != "UNCERTAINTY_CANDIDATE_EXTRACTION_COMPLETE"
    ):
        raise UncertaintyIntelligenceError(
            "Uncertainty candidate extraction must be complete."
        )

    if (
        candidate_extraction_result.get(
            "phase"
        )
        != "4.6.14"
    ):
        raise UncertaintyIntelligenceError(
            "Stage G requires Phase 4.6.14 input."
        )

    if (
        candidate_extraction_result.get(
            "patch"
        )
        != "4.6.14F"
    ):
        raise UncertaintyIntelligenceError(
            "Stage G requires canonical 4.6.14F input."
        )

    if (
        candidate_extraction_result.get(
            "next_stage"
        )
        != "uncertainty_scope_target_grounding"
    ):
        raise UncertaintyIntelligenceError(
            "Stage F must hand off to uncertainty_scope_target_grounding."
        )

    if (
        candidate_extraction_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise UncertaintyIntelligenceError(
            "Uncertainty Intelligence must remain transient."
        )

    top_boundaries = dict(
        candidate_extraction_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        top_boundaries.get(
            "uncertainty_candidate_extraction_performed"
        )
        is not True
    ):
        raise UncertaintyIntelligenceError(
            "Candidate extraction boundary must be complete before Stage G."
        )

    if (
        top_boundaries.get(
            "uncertainty_scope_grounding_performed"
        )
        is not False
    ):
        raise UncertaintyIntelligenceError(
            "Scope grounding must be pending before Stage G."
        )

    source_units = list(
        candidate_extraction_result.get(
            "uncertainty_claim_units"
        )
        or []
    )

    unit_by_id = {}

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise UncertaintyIntelligenceError(
                "Uncertainty Claim Unit ID is required."
            )

        if unit_id in unit_by_id:
            raise UncertaintyIntelligenceError(
                "Duplicate Uncertainty Claim Unit ID."
            )

        state = dict(
            unit.get(
                "uncertainty_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "uncertainty_candidate_extraction"
            )
            != "COMPLETE"
        ):
            raise UncertaintyIntelligenceError(
                "Candidate extraction must be COMPLETE for every unit."
            )

        if (
            state.get(
                "uncertainty_scope_target_grounding"
            )
            != "PENDING"
        ):
            raise UncertaintyIntelligenceError(
                "Scope target grounding must be PENDING before Stage G."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "uncertainty_candidate_extraction_performed"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Unit candidate extraction boundary must be True."
            )

        if (
            boundaries.get(
                "uncertainty_scope_grounding_performed"
            )
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Unit scope grounding boundary must be False before Stage G."
            )

        unit_by_id[
            unit_id
        ] = unit

    candidates = list(
        candidate_extraction_result.get(
            "uncertainty_candidates"
        )
        or []
    )

    grounded_candidates = []
    grounded_by_id = {}
    seen_candidate_ids = set()

    for candidate in candidates:

        if not isinstance(
            candidate,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "uncertainty_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise UncertaintyIntelligenceError(
                "Uncertainty candidate ID is required."
            )

        if candidate_id in seen_candidate_ids:
            raise UncertaintyIntelligenceError(
                "Duplicate Uncertainty candidate ID."
            )

        seen_candidate_ids.add(
            candidate_id
        )

        unit_id = str(
            candidate.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        )

        source_unit = unit_by_id.get(
            unit_id
        )

        if source_unit is None:
            raise UncertaintyIntelligenceError(
                "Candidate references an unknown Uncertainty Claim Unit."
            )

        source_text = str(
            candidate.get(
                "source_text"
            )
            or ""
        )

        unit_text = str(
            source_unit.get(
                "text"
            )
            or ""
        )

        if source_text != unit_text:
            raise UncertaintyIntelligenceError(
                "Candidate source text does not match its Claim Unit."
            )

        start = candidate.get(
            "character_start"
        )

        end = candidate.get(
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
                source_text
            )
        ):
            raise UncertaintyIntelligenceError(
                "Candidate signal span is invalid."
            )

        matched_text = str(
            candidate.get(
                "matched_text"
            )
            or ""
        )

        if (
            source_text[
                start:end
            ]
            != matched_text
        ):
            raise UncertaintyIntelligenceError(
                "Candidate signal span does not match article evidence."
            )

        if (
            candidate.get(
                "uncertainty_candidate_extracted"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Candidate must already be extracted before Stage G."
            )

        if (
            candidate.get(
                "uncertainty_scope_grounded"
            )
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Candidate scope must not already be grounded."
            )

        if (
            candidate.get(
                "uncertainty_type_classified"
            )
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Uncertainty type classification must remain pending."
            )

        grounded = dict(
            candidate
        )

        grounded.update({
            "uncertainty_scope": {
                "scope_type":
                    "SAME_SENTENCE_EXPLICIT_CLAIM_SCOPE",

                "scope_text":
                    source_text,

                "character_start":
                    0,

                "character_end":
                    len(
                        source_text
                    ),

                "sentence_id":
                    source_unit.get(
                        "sentence_id"
                    ),

                "sentence_global_index":
                    source_unit.get(
                        "sentence_global_index"
                    ),

                "section_id":
                    source_unit.get(
                        "section_id"
                    ),

                "block_id":
                    source_unit.get(
                        "block_id"
                    ),

                "paragraph_id":
                    source_unit.get(
                        "paragraph_id"
                    ),

                "explicit_article_evidence":
                    True,

                "cross_sentence_scope":
                    False,

                "semantic_target_inferred":
                    False,
            },

            "uncertainty_target": {
                "target_type":
                    "SOURCE_SENTENCE_CLAIM",

                "target_text":
                    source_text,

                "target_sentence_id":
                    source_unit.get(
                        "sentence_id"
                    ),

                "target_section_id":
                    source_unit.get(
                        "section_id"
                    ),

                "explicit_article_evidence":
                    True,

                "semantic_object_inferred":
                    False,
            },

            "scope_grounding_status":
                "GROUNDED_TO_EXPLICIT_SOURCE_SENTENCE",

            "uncertainty_scope_grounded":
                True,

            "uncertainty_type_classified":
                False,

            "uncertainty_strength_validated":
                False,

            "same_sentence_uncertainty_validated":
                False,

            "cross_sentence_uncertainty_anchor_resolved":
                False,

            "cross_sentence_scope_inference_performed":
                False,

            "semantic_target_inference_performed":
                False,

            "numeric_probability_inference_performed":
                False,

            "unstated_uncertainty_inference_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
                False,

            "semantic_memory_write_performed":
                False,

            "persistence_performed":
                False,
        })

        grounded_candidates.append(
            grounded
        )

        grounded_by_id[
            candidate_id
        ] = grounded

    grounded_units = []
    grounded_unit_by_id = {}

    for source_unit in source_units:

        unit_id = str(
            source_unit.get(
                "uncertainty_claim_unit_id"
            )
        )

        unit_candidates = [
            candidate
            for candidate in grounded_candidates
            if candidate.get(
                "uncertainty_claim_unit_id"
            )
            == unit_id
        ]

        state = dict(
            source_unit.get(
                "uncertainty_analysis_state"
            )
            or {}
        )

        state[
            "uncertainty_scope_target_grounding"
        ] = "COMPLETE"

        boundaries = dict(
            source_unit.get(
                "processing_boundaries"
            )
            or {}
        )

        boundaries[
            "uncertainty_scope_grounding_performed"
        ] = True

        boundaries[
            "uncertainty_type_classification_performed"
        ] = False

        boundaries[
            "uncertainty_explicitness_strength_validation_performed"
        ] = False

        boundaries[
            "same_sentence_uncertainty_validation_performed"
        ] = False

        boundaries[
            "cross_sentence_uncertainty_anchoring_performed"
        ] = False

        boundaries[
            "uncertainty_evidence_assessment_performed"
        ] = False

        boundaries[
            "uncertainty_duplicate_resolution_performed"
        ] = False

        boundaries[
            "unstated_uncertainty_inference_performed"
        ] = False

        boundaries[
            "numeric_probability_inference_performed"
        ] = False

        boundaries[
            "truth_assessment_performed"
        ] = False

        boundaries[
            "external_authority_check_performed"
        ] = False

        boundaries[
            "semantic_memory_write_performed"
        ] = False

        boundaries[
            "persistence_performed"
        ] = False

        updated_unit = dict(
            source_unit
        )

        updated_unit.update({
            "uncertainty_candidates":
                unit_candidates,

            "uncertainty_grounded_candidate_count":
                len(
                    unit_candidates
                ),

            "uncertainty_analysis_state":
                state,

            "processing_boundaries":
                boundaries,
        })

        grounded_units.append(
            updated_unit
        )

        grounded_unit_by_id[
            unit_id
        ] = updated_unit

    grounded_sections = []

    for section in (
        candidate_extraction_result.get(
            "uncertainty_sections"
        )
        or []
    ):

        if not isinstance(
            section,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty section must be a mapping."
            )

        rebuilt_units = []

        for old_unit in (
            section.get(
                "uncertainty_claim_units"
            )
            or []
        ):

            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise UncertaintyIntelligenceError(
                    "Section Claim Unit reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "uncertainty_claim_unit_id"
                )
                or ""
            )

            resolved = grounded_unit_by_id.get(
                unit_id
            )

            if resolved is None:
                raise UncertaintyIntelligenceError(
                    "Uncertainty section references an unknown Claim Unit."
                )

            rebuilt_units.append(
                resolved
            )

        grounded_sections.append({
            **dict(
                section
            ),

            "uncertainty_claim_units":
                rebuilt_units,

            "uncertainty_grounded_candidate_count":
                sum(
                    int(
                        unit.get(
                            "uncertainty_grounded_candidate_count"
                        )
                        or 0
                    )
                    for unit in rebuilt_units
                ),
        })

    result = dict(
        candidate_extraction_result
    )

    result_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    result_boundaries[
        "uncertainty_scope_grounding_performed"
    ] = True

    result_boundaries[
        "uncertainty_type_classification_performed"
    ] = False

    result_boundaries[
        "uncertainty_explicitness_strength_validation_performed"
    ] = False

    result_boundaries[
        "same_sentence_uncertainty_validation_performed"
    ] = False

    result_boundaries[
        "cross_sentence_uncertainty_anchoring_performed"
    ] = False

    result_boundaries[
        "uncertainty_evidence_assessment_performed"
    ] = False

    result_boundaries[
        "uncertainty_duplicate_resolution_performed"
    ] = False

    result_boundaries[
        "unstated_uncertainty_inference_performed"
    ] = False

    result_boundaries[
        "numeric_probability_inference_performed"
    ] = False

    result_boundaries[
        "truth_assessment_performed"
    ] = False

    result_boundaries[
        "external_authority_check_performed"
    ] = False

    result_boundaries[
        "semantic_memory_write_performed"
    ] = False

    result_boundaries[
        "persistence_performed"
    ] = False

    result.update({
        "schema_version":
            "uncertainty_scope_target_grounding_v1",

        "patch":
            "4.6.14G",

        "status":
            "UNCERTAINTY_SCOPE_TARGET_GROUNDING_COMPLETE",

        "uncertainty_candidates":
            grounded_candidates,

        "uncertainty_claim_units":
            grounded_units,

        "uncertainty_sections":
            grounded_sections,

        "uncertainty_scope_grounding_summary": {
            "candidate_count":
                len(
                    grounded_candidates
                ),

            "grounded_candidate_count":
                sum(
                    1
                    for candidate in grounded_candidates
                    if candidate.get(
                        "uncertainty_scope_grounded"
                    )
                    is True
                ),

            "same_sentence_explicit_scope_count":
                len(
                    grounded_candidates
                ),

            "cross_sentence_scope_count":
                0,

            "semantic_target_inference_count":
                0,

            "unstated_uncertainty_inference_count":
                0,

            "numeric_probability_inference_count":
                0,

            "truth_assessment_performed":
                False,
        },

        "processing_boundaries":
            result_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "uncertainty_type_classification",
    })

    return result


def classify_uncertainty_types_v1(
    scope_grounding_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Classify canonical Uncertainty types from already-explicit
    and already-grounded article-local candidates.

    Stage H performs deterministic signal-family classification only.

    It does NOT:
    - infer uncertainty from unstated context,
    - classify ambiguous Stage-E exclusions,
    - resolve new scope,
    - perform cross-sentence anchoring,
    - convert uncertainty into numeric probability,
    - validate final commitment strength,
    - assess factual truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        scope_grounding_result,
        Mapping,
    ):
        raise UncertaintyIntelligenceError(
            "scope_grounding_result must be a mapping."
        )

    if (
        scope_grounding_result.get(
            "schema_version"
        )
        != "uncertainty_scope_target_grounding_v1"
    ):
        raise UncertaintyIntelligenceError(
            "Stage H requires "
            "uncertainty_scope_target_grounding_v1."
        )

    if (
        scope_grounding_result.get(
            "status"
        )
        != "UNCERTAINTY_SCOPE_TARGET_GROUNDING_COMPLETE"
    ):
        raise UncertaintyIntelligenceError(
            "Stage G must be complete before Stage H."
        )

    if (
        scope_grounding_result.get(
            "phase"
        )
        != "4.6.14"
    ):
        raise UncertaintyIntelligenceError(
            "Stage H requires Phase 4.6.14 input."
        )

    if (
        scope_grounding_result.get(
            "patch"
        )
        != "4.6.14G"
    ):
        raise UncertaintyIntelligenceError(
            "Stage H requires canonical 4.6.14G input."
        )

    if (
        scope_grounding_result.get(
            "next_stage"
        )
        != "uncertainty_type_classification"
    ):
        raise UncertaintyIntelligenceError(
            "Stage G must hand off to "
            "uncertainty_type_classification."
        )

    if (
        scope_grounding_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise UncertaintyIntelligenceError(
            "Uncertainty Intelligence must remain transient."
        )

    top_boundaries = dict(
        scope_grounding_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        top_boundaries.get(
            "uncertainty_scope_grounding_performed"
        )
        is not True
    ):
        raise UncertaintyIntelligenceError(
            "Stage-G grounding boundary must be complete."
        )

    if (
        top_boundaries.get(
            "uncertainty_type_classification_performed"
        )
        is not False
    ):
        raise UncertaintyIntelligenceError(
            "Type classification must be pending before Stage H."
        )

    signal_type_to_uncertainty_type = {
        "POSSIBILITY_MODAL":
            "POSSIBILITY",

        "POSSIBILITY_LEXEME":
            "POSSIBILITY",

        "CHANCE_CONSTRUCTION":
            "POSSIBILITY",

        "LIKELIHOOD":
            "LIKELIHOOD",

        "NUMERIC_APPROXIMATION":
            "APPROXIMATION",

        "NON_UNIVERSAL_FREQUENCY":
            "NON_UNIVERSAL_FREQUENCY",

        "NOT_ALWAYS":
            "NON_UNIVERSAL_FREQUENCY",

        "UNKNOWN_OR_UNCLEAR":
            "EPISTEMIC_UNCERTAINTY",

        "EVIDENCE_LIMITATION":
            "EVIDENCE_LIMITATION",

        "CONFLICTED_EVIDENCE":
            "CONFLICTED_EVIDENCE",
    }

    source_candidates = list(
        scope_grounding_result.get(
            "uncertainty_candidates"
        )
        or []
    )

    source_units = list(
        scope_grounding_result.get(
            "uncertainty_claim_units"
        )
        or []
    )

    unit_by_id = {}

    for unit in source_units:

        if not isinstance(
            unit,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise UncertaintyIntelligenceError(
                "Uncertainty Claim Unit ID is required."
            )

        if unit_id in unit_by_id:
            raise UncertaintyIntelligenceError(
                "Duplicate Uncertainty Claim Unit ID."
            )

        state = dict(
            unit.get(
                "uncertainty_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "uncertainty_scope_target_grounding"
            )
            != "COMPLETE"
        ):
            raise UncertaintyIntelligenceError(
                "Scope / target grounding must be COMPLETE "
                "before Stage H."
            )

        if (
            state.get(
                "uncertainty_type_classification"
            )
            != "PENDING"
        ):
            raise UncertaintyIntelligenceError(
                "Type classification must be PENDING "
                "before Stage H."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "uncertainty_scope_grounding_performed"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Unit Stage-G grounding boundary must be complete."
            )

        if (
            boundaries.get(
                "uncertainty_type_classification_performed"
            )
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Unit type classification must be pending."
            )

        unit_by_id[
            unit_id
        ] = unit

    classified_candidates = []
    classified_by_unit = {}

    type_counts = {}
    signal_type_counts = {}

    seen_candidate_ids = set()

    for candidate in source_candidates:

        if not isinstance(
            candidate,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "uncertainty_candidate_id"
            )
            or ""
        )

        unit_id = str(
            candidate.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        )

        signal_type = str(
            candidate.get(
                "signal_type"
            )
            or ""
        )

        if not candidate_id:
            raise UncertaintyIntelligenceError(
                "Uncertainty Candidate ID is required."
            )

        if candidate_id in seen_candidate_ids:
            raise UncertaintyIntelligenceError(
                "Duplicate Uncertainty Candidate ID."
            )

        seen_candidate_ids.add(
            candidate_id
        )

        if unit_id not in unit_by_id:
            raise UncertaintyIntelligenceError(
                "Uncertainty candidate references an unknown claim unit."
            )

        if (
            candidate.get(
                "uncertainty_scope_grounded"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Candidate scope must be grounded before Stage H."
            )

        if (
            candidate.get(
                "uncertainty_type_classified"
            )
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Candidate type must be unclassified before Stage H."
            )

        if (
            candidate.get(
                "numeric_probability_inference_performed"
            )
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Numeric probability inference is forbidden before Stage H."
            )

        if (
            candidate.get(
                "truth_assessment_performed"
            )
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Truth assessment is forbidden before Stage H."
            )

        uncertainty_type = (
            signal_type_to_uncertainty_type.get(
                signal_type
            )
        )

        if uncertainty_type is None:
            raise UncertaintyIntelligenceError(
                "Unsupported explicit Uncertainty signal type: "
                + signal_type
            )

        classified = dict(
            candidate
        )

        classified.update({
            "uncertainty_type":
                uncertainty_type,

            "uncertainty_type_classified":
                True,

            "uncertainty_type_classification_basis":
                "EXPLICIT_SIGNAL_TYPE_MAPPING",

            "uncertainty_type_classification_status":
                "CLASSIFIED",

            "numeric_probability":
                None,

            "numeric_probability_inference_performed":
                False,

            "uncertainty_strength_validated":
                False,

            "same_sentence_uncertainty_validated":
                False,

            "cross_sentence_uncertainty_anchor_resolved":
                False,

            "truth_assessment_performed":
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

        classified_candidates.append(
            classified
        )

        classified_by_unit.setdefault(
            unit_id,
            [],
        ).append(
            classified
        )

        type_counts[
            uncertainty_type
        ] = (
            type_counts.get(
                uncertainty_type,
                0,
            )
            + 1
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

    classified_units = []
    classified_unit_by_id = {}

    for unit in source_units:

        unit_id = str(
            unit.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        )

        state = dict(
            unit.get(
                "uncertainty_analysis_state"
            )
            or {}
        )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        state[
            "uncertainty_type_classification"
        ] = "COMPLETE"

        boundaries[
            "uncertainty_type_classification_performed"
        ] = True

        boundaries[
            "uncertainty_explicitness_strength_validation_performed"
        ] = False

        boundaries[
            "same_sentence_uncertainty_validation_performed"
        ] = False

        boundaries[
            "cross_sentence_uncertainty_anchoring_performed"
        ] = False

        boundaries[
            "uncertainty_evidence_assessment_performed"
        ] = False

        boundaries[
            "uncertainty_duplicate_resolution_performed"
        ] = False

        boundaries[
            "numeric_probability_inference_performed"
        ] = False

        boundaries[
            "unstated_uncertainty_inference_performed"
        ] = False

        boundaries[
            "truth_assessment_performed"
        ] = False

        boundaries[
            "external_authority_check_performed"
        ] = False

        boundaries[
            "semantic_memory_write_performed"
        ] = False

        boundaries[
            "persistence_performed"
        ] = False

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "uncertainty_candidates":
                list(
                    classified_by_unit.get(
                        unit_id,
                        []
                    )
                ),

            "uncertainty_classified_candidate_count":
                len(
                    classified_by_unit.get(
                        unit_id,
                        []
                    )
                ),

            "uncertainty_analysis_state":
                state,

            "processing_boundaries":
                boundaries,
        })

        classified_units.append(
            updated_unit
        )

        classified_unit_by_id[
            unit_id
        ] = updated_unit

    classified_sections = []

    for section in (
        scope_grounding_result.get(
            "uncertainty_sections"
        )
        or []
    ):

        if not isinstance(
            section,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "uncertainty_claim_units"
            )
            or []
        ):

            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise UncertaintyIntelligenceError(
                    "Section claim-unit reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "uncertainty_claim_unit_id"
                )
                or ""
            )

            resolved = classified_unit_by_id.get(
                unit_id
            )

            if resolved is None:
                raise UncertaintyIntelligenceError(
                    "Uncertainty section references "
                    "an unknown claim unit."
                )

            section_units.append(
                resolved
            )

        classified_sections.append({
            **dict(
                section
            ),

            "uncertainty_claim_units":
                section_units,

            "uncertainty_classified_candidate_count":
                sum(
                    int(
                        unit.get(
                            "uncertainty_classified_candidate_count"
                        )
                        or 0
                    )
                    for unit in section_units
                ),
        })

    result = dict(
        scope_grounding_result
    )

    result_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    result_boundaries[
        "uncertainty_type_classification_performed"
    ] = True

    result_boundaries[
        "uncertainty_explicitness_strength_validation_performed"
    ] = False

    result_boundaries[
        "same_sentence_uncertainty_validation_performed"
    ] = False

    result_boundaries[
        "cross_sentence_uncertainty_anchoring_performed"
    ] = False

    result_boundaries[
        "uncertainty_evidence_assessment_performed"
    ] = False

    result_boundaries[
        "uncertainty_duplicate_resolution_performed"
    ] = False

    result_boundaries[
        "numeric_probability_inference_performed"
    ] = False

    result_boundaries[
        "unstated_uncertainty_inference_performed"
    ] = False

    result_boundaries[
        "truth_assessment_performed"
    ] = False

    result_boundaries[
        "external_authority_check_performed"
    ] = False

    result_boundaries[
        "semantic_memory_write_performed"
    ] = False

    result_boundaries[
        "persistence_performed"
    ] = False

    result.update({
        "schema_version":
            "uncertainty_type_classification_v1",

        "patch":
            "4.6.14H",

        "status":
            "UNCERTAINTY_TYPE_CLASSIFICATION_COMPLETE",

        "uncertainty_sections":
            classified_sections,

        "uncertainty_claim_units":
            classified_units,

        "uncertainty_candidates":
            classified_candidates,

        "uncertainty_type_summary": {
            "candidate_count":
                len(
                    classified_candidates
                ),

            "classified_candidate_count":
                len(
                    classified_candidates
                ),

            "uncertainty_type_counts":
                dict(
                    sorted(
                        type_counts.items()
                    )
                ),

            "signal_type_counts":
                dict(
                    sorted(
                        signal_type_counts.items()
                    )
                ),

            "classification_basis":
                "EXPLICIT_SIGNAL_TYPE_MAPPING",

            "ambiguous_exclusions_classified":
                False,

            "scope_reinterpreted":
                False,

            "numeric_probability_inferred":
                False,

            "unstated_uncertainty_inferred":
                False,

            "strength_validated":
                False,

            "truth_assessment_performed":
                False,
        },

        "processing_boundaries":
            result_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "uncertainty_explicitness_strength_validation",
    })

    return result


def validate_uncertainty_explicitness_strength_v1(
    type_classification_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate explicit source commitment for classified
    Uncertainty candidates.

    Stage I validates only article-explicit uncertainty evidence
    and the qualitative commitment class expressed by that evidence.

    It does NOT:
    - infer numeric probability,
    - rank may/might/could numerically,
    - infer unstated uncertainty,
    - reinterpret scope,
    - perform same-sentence semantic validation,
    - perform cross-sentence anchoring,
    - assess factual truth,
    - use external authority,
    - write Semantic Memory,
    - make linking decisions,
    - persist intelligence.
    """

    if not isinstance(
        type_classification_result,
        Mapping,
    ):
        raise UncertaintyIntelligenceError(
            "type_classification_result must be a mapping."
        )

    if (
        type_classification_result.get(
            "schema_version"
        )
        != "uncertainty_type_classification_v1"
    ):
        raise UncertaintyIntelligenceError(
            "Stage I requires uncertainty_type_classification_v1."
        )

    if (
        type_classification_result.get(
            "status"
        )
        != "UNCERTAINTY_TYPE_CLASSIFICATION_COMPLETE"
    ):
        raise UncertaintyIntelligenceError(
            "Stage H must be complete before Stage I."
        )

    if (
        type_classification_result.get(
            "phase"
        )
        != "4.6.14"
    ):
        raise UncertaintyIntelligenceError(
            "Stage I requires Phase 4.6.14 input."
        )

    if (
        type_classification_result.get(
            "patch"
        )
        != "4.6.14H"
    ):
        raise UncertaintyIntelligenceError(
            "Stage I requires canonical 4.6.14H input."
        )

    if (
        type_classification_result.get(
            "next_stage"
        )
        != "uncertainty_explicitness_strength_validation"
    ):
        raise UncertaintyIntelligenceError(
            "Stage H must hand off to "
            "uncertainty_explicitness_strength_validation."
        )

    if (
        type_classification_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise UncertaintyIntelligenceError(
            "Uncertainty Intelligence must remain transient."
        )

    top_boundaries = dict(
        type_classification_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        top_boundaries.get(
            "uncertainty_type_classification_performed"
        )
        is not True
    ):
        raise UncertaintyIntelligenceError(
            "Stage-H classification boundary must be complete."
        )

    if (
        top_boundaries.get(
            "uncertainty_explicitness_strength_validation_performed"
        )
        is not False
    ):
        raise UncertaintyIntelligenceError(
            "Stage-I validation must be pending before execution."
        )

    commitment_map = {
        "POSSIBILITY":
            "EXPLICIT_POSSIBILITY_COMMITMENT",

        "LIKELIHOOD":
            "EXPLICIT_LIKELIHOOD_COMMITMENT",

        "APPROXIMATION":
            "EXPLICIT_APPROXIMATE_COMMITMENT",

        "NON_UNIVERSAL_FREQUENCY":
            "EXPLICIT_FREQUENCY_QUALIFIED_COMMITMENT",

        "EPISTEMIC_UNCERTAINTY":
            "EXPLICIT_UNCERTAIN_KNOWLEDGE_COMMITMENT",

        "EVIDENCE_LIMITATION":
            "EXPLICIT_LIMITED_EVIDENCE_COMMITMENT",

        "CONFLICTED_EVIDENCE":
            "EXPLICIT_CONFLICTED_EVIDENCE_COMMITMENT",
    }

    source_units = list(
        type_classification_result.get(
            "uncertainty_claim_units"
        )
        or []
    )

    unit_by_id = {}

    for unit in source_units:

        if not isinstance(
            unit,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise UncertaintyIntelligenceError(
                "Uncertainty Claim Unit ID is required."
            )

        if unit_id in unit_by_id:
            raise UncertaintyIntelligenceError(
                "Duplicate Uncertainty Claim Unit ID."
            )

        state = dict(
            unit.get(
                "uncertainty_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "uncertainty_type_classification"
            )
            != "COMPLETE"
        ):
            raise UncertaintyIntelligenceError(
                "Stage H must be COMPLETE for every Claim Unit."
            )

        if (
            state.get(
                "explicitness_strength_validation"
            )
            != "PENDING"
        ):
            raise UncertaintyIntelligenceError(
                "Explicitness/strength validation must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "uncertainty_type_classification_performed"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Unit Stage-H boundary must be True."
            )

        if (
            boundaries.get(
                "uncertainty_explicitness_strength_validation_performed"
            )
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Unit Stage-I boundary must be False before validation."
            )

        unit_by_id[
            unit_id
        ] = unit

    candidates = list(
        type_classification_result.get(
            "uncertainty_candidates"
        )
        or []
    )

    validated_candidates = []
    validated_by_id = {}
    seen_candidate_ids = set()

    for candidate in candidates:

        if not isinstance(
            candidate,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "uncertainty_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise UncertaintyIntelligenceError(
                "Uncertainty Candidate ID is required."
            )

        if candidate_id in seen_candidate_ids:
            raise UncertaintyIntelligenceError(
                "Duplicate Uncertainty Candidate ID."
            )

        seen_candidate_ids.add(
            candidate_id
        )

        unit_id = str(
            candidate.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        )

        if unit_id not in unit_by_id:
            raise UncertaintyIntelligenceError(
                "Candidate references unknown Uncertainty Claim Unit."
            )

        if (
            candidate.get(
                "uncertainty_scope_grounded"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Candidate scope must be grounded before Stage I."
            )

        if (
            candidate.get(
                "uncertainty_type_classified"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Candidate uncertainty type must be classified."
            )

        if (
            candidate.get(
                "uncertainty_strength_validated"
            )
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Candidate strength must not already be validated."
            )

        if (
            candidate.get(
                "numeric_probability_inference_performed"
            )
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Numeric probability inference is forbidden."
            )

        if (
            candidate.get(
                "truth_assessment_performed"
            )
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Truth assessment is forbidden before Stage I."
            )

        uncertainty_type = str(
            candidate.get(
                "uncertainty_type"
            )
            or ""
        )

        commitment_class = commitment_map.get(
            uncertainty_type
        )

        if commitment_class is None:
            raise UncertaintyIntelligenceError(
                "Unsupported classified uncertainty type: "
                + uncertainty_type
            )

        if (
            candidate.get(
                "uncertainty_type_classification_status"
            )
            != "CLASSIFIED"
        ):
            raise UncertaintyIntelligenceError(
                "Candidate classification status must be CLASSIFIED."
            )

        matched_text = str(
            candidate.get(
                "matched_text"
            )
            or ""
        ).strip()

        if not matched_text:
            raise UncertaintyIntelligenceError(
                "Explicit uncertainty evidence text is required."
            )

        scope = candidate.get(
            "uncertainty_scope"
        )

        if not isinstance(
            scope,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Grounded uncertainty scope must be a mapping."
            )

        if (
            scope.get(
                "explicit_article_evidence"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Stage I requires explicit article evidence."
            )

        validated = dict(
            candidate
        )

        validated.update({
            "uncertainty_explicitness":
                "EXPLICIT",

            "uncertainty_explicitness_validated":
                True,

            "uncertainty_commitment_class":
                commitment_class,

            "uncertainty_commitment_basis":
                "ARTICLE_EXPLICIT_LEXICAL_EVIDENCE",

            "uncertainty_strength_validation_status":
                "QUALITATIVE_COMMITMENT_VALIDATED",

            "uncertainty_strength_validated":
                True,

            "numeric_probability":
                None,

            "numeric_probability_inference_performed":
                False,

            "relative_probability_ranking_performed":
                False,

            "unstated_uncertainty_inference_performed":
                False,

            "scope_reinterpretation_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
                False,

            "semantic_memory_write_performed":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        })

        validated_candidates.append(
            validated
        )

        validated_by_id[
            candidate_id
        ] = validated

    validated_units = []
    validated_unit_by_id = {}

    for source_unit in source_units:

        unit_id = str(
            source_unit.get(
                "uncertainty_claim_unit_id"
            )
        )

        unit_candidates = [
            candidate
            for candidate in validated_candidates
            if candidate.get(
                "uncertainty_claim_unit_id"
            )
            == unit_id
        ]

        state = dict(
            source_unit.get(
                "uncertainty_analysis_state"
            )
            or {}
        )

        state[
            "explicitness_strength_validation"
        ] = "COMPLETE"

        boundaries = dict(
            source_unit.get(
                "processing_boundaries"
            )
            or {}
        )

        boundaries[
            "uncertainty_explicitness_strength_validation_performed"
        ] = True

        boundaries[
            "same_sentence_uncertainty_validation_performed"
        ] = False

        boundaries[
            "cross_sentence_uncertainty_anchoring_performed"
        ] = False

        boundaries[
            "uncertainty_evidence_assessment_performed"
        ] = False

        boundaries[
            "uncertainty_duplicate_resolution_performed"
        ] = False

        boundaries[
            "numeric_probability_inference_performed"
        ] = False

        boundaries[
            "unstated_uncertainty_inference_performed"
        ] = False

        boundaries[
            "truth_assessment_performed"
        ] = False

        boundaries[
            "external_authority_check_performed"
        ] = False

        boundaries[
            "semantic_memory_write_performed"
        ] = False

        boundaries[
            "persistence_performed"
        ] = False

        updated_unit = dict(
            source_unit
        )

        updated_unit.update({
            "uncertainty_candidates":
                unit_candidates,

            "uncertainty_strength_validated_candidate_count":
                len(
                    unit_candidates
                ),

            "uncertainty_analysis_state":
                state,

            "processing_boundaries":
                boundaries,
        })

        validated_units.append(
            updated_unit
        )

        validated_unit_by_id[
            unit_id
        ] = updated_unit

    validated_sections = []

    for section in (
        type_classification_result.get(
            "uncertainty_sections"
        )
        or []
    ):

        if not isinstance(
            section,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty section must be a mapping."
            )

        rebuilt_units = []

        for old_unit in (
            section.get(
                "uncertainty_claim_units"
            )
            or []
        ):

            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise UncertaintyIntelligenceError(
                    "Section Claim Unit reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "uncertainty_claim_unit_id"
                )
                or ""
            )

            resolved = validated_unit_by_id.get(
                unit_id
            )

            if resolved is None:
                raise UncertaintyIntelligenceError(
                    "Section references unknown Uncertainty Claim Unit."
                )

            rebuilt_units.append(
                resolved
            )

        validated_sections.append({
            **dict(
                section
            ),

            "uncertainty_claim_units":
                rebuilt_units,

            "uncertainty_strength_validated_candidate_count":
                sum(
                    int(
                        unit.get(
                            "uncertainty_strength_validated_candidate_count"
                        )
                        or 0
                    )
                    for unit in rebuilt_units
                ),
        })

    result = dict(
        type_classification_result
    )

    result_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    result_boundaries[
        "uncertainty_explicitness_strength_validation_performed"
    ] = True

    result_boundaries[
        "same_sentence_uncertainty_validation_performed"
    ] = False

    result_boundaries[
        "cross_sentence_uncertainty_anchoring_performed"
    ] = False

    result_boundaries[
        "uncertainty_evidence_assessment_performed"
    ] = False

    result_boundaries[
        "uncertainty_duplicate_resolution_performed"
    ] = False

    result_boundaries[
        "numeric_probability_inference_performed"
    ] = False

    result_boundaries[
        "unstated_uncertainty_inference_performed"
    ] = False

    result_boundaries[
        "truth_assessment_performed"
    ] = False

    result_boundaries[
        "external_authority_check_performed"
    ] = False

    result_boundaries[
        "semantic_memory_write_performed"
    ] = False

    result_boundaries[
        "persistence_performed"
    ] = False

    commitment_counts = {}

    for candidate in validated_candidates:
        commitment_class = candidate[
            "uncertainty_commitment_class"
        ]

        commitment_counts[
            commitment_class
        ] = (
            commitment_counts.get(
                commitment_class,
                0,
            )
            + 1
        )

    result.update({
        "schema_version":
            "uncertainty_explicitness_strength_validation_v1",

        "patch":
            "4.6.14I",

        "status":
            "UNCERTAINTY_EXPLICITNESS_STRENGTH_VALIDATION_COMPLETE",

        "uncertainty_candidates":
            validated_candidates,

        "uncertainty_claim_units":
            validated_units,

        "uncertainty_sections":
            validated_sections,

        "uncertainty_strength_summary": {
            "candidate_count":
                len(
                    validated_candidates
                ),

            "explicit_candidate_count":
                sum(
                    1
                    for candidate in validated_candidates
                    if candidate.get(
                        "uncertainty_explicitness"
                    )
                    == "EXPLICIT"
                ),

            "strength_validated_candidate_count":
                sum(
                    1
                    for candidate in validated_candidates
                    if candidate.get(
                        "uncertainty_strength_validated"
                    )
                    is True
                ),

            "commitment_class_counts":
                dict(
                    sorted(
                        commitment_counts.items()
                    )
                ),

            "numeric_probability_inferred":
                False,

            "relative_probability_ranking_performed":
                False,

            "unstated_uncertainty_inferred":
                False,

            "scope_reinterpreted":
                False,

            "truth_assessment_performed":
                False,
        },

        "processing_boundaries":
            result_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "same_sentence_uncertainty_validation",
    })

    return result


def validate_same_sentence_uncertainty_v1(
    explicitness_strength_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate same-sentence Uncertainty evidence.

    Stage J confirms that:
    - the uncertainty signal span is explicitly present,
    - the candidate source sentence matches its Claim Unit,
    - the grounded scope is the same explicit source sentence,
    - type / explicitness / qualitative commitment are already established.

    It does NOT:
    - infer cross-sentence uncertainty,
    - create new uncertainty candidates,
    - reinterpret scope,
    - infer numeric probability,
    - rank likelihood,
    - assess truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        explicitness_strength_result,
        Mapping,
    ):
        raise UncertaintyIntelligenceError(
            "explicitness_strength_result must be a mapping."
        )

    if (
        explicitness_strength_result.get("schema_version")
        != "uncertainty_explicitness_strength_validation_v1"
    ):
        raise UncertaintyIntelligenceError(
            "Stage J requires "
            "uncertainty_explicitness_strength_validation_v1."
        )

    if (
        explicitness_strength_result.get("status")
        != "UNCERTAINTY_EXPLICITNESS_STRENGTH_VALIDATION_COMPLETE"
    ):
        raise UncertaintyIntelligenceError(
            "Stage I must be complete before Stage J."
        )

    if explicitness_strength_result.get("phase") != "4.6.14":
        raise UncertaintyIntelligenceError(
            "Stage J requires Phase 4.6.14 input."
        )

    if explicitness_strength_result.get("patch") != "4.6.14I":
        raise UncertaintyIntelligenceError(
            "Stage J requires canonical 4.6.14I input."
        )

    if (
        explicitness_strength_result.get("next_stage")
        != "same_sentence_uncertainty_validation"
    ):
        raise UncertaintyIntelligenceError(
            "Stage I must hand off to "
            "same_sentence_uncertainty_validation."
        )

    if (
        explicitness_strength_result.get("persistence_policy")
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise UncertaintyIntelligenceError(
            "Uncertainty Intelligence must remain transient."
        )

    top_boundaries = dict(
        explicitness_strength_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        top_boundaries.get(
            "uncertainty_explicitness_strength_validation_performed"
        )
        is not True
    ):
        raise UncertaintyIntelligenceError(
            "Stage-I boundary must be complete."
        )

    if (
        top_boundaries.get(
            "same_sentence_uncertainty_validation_performed"
        )
        is not False
    ):
        raise UncertaintyIntelligenceError(
            "Same-sentence validation must be pending before Stage J."
        )

    source_units = list(
        explicitness_strength_result.get(
            "uncertainty_claim_units"
        )
        or []
    )

    source_candidates = list(
        explicitness_strength_result.get(
            "uncertainty_candidates"
        )
        or []
    )

    unit_by_id = {}

    for unit in source_units:

        if not isinstance(unit, Mapping):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get("uncertainty_claim_unit_id")
            or ""
        )

        if not unit_id:
            raise UncertaintyIntelligenceError(
                "Uncertainty Claim Unit ID is required."
            )

        if unit_id in unit_by_id:
            raise UncertaintyIntelligenceError(
                "Duplicate Uncertainty Claim Unit ID."
            )

        state = dict(
            unit.get("uncertainty_analysis_state")
            or {}
        )

        if (
            state.get("explicitness_strength_validation")
            != "COMPLETE"
        ):
            raise UncertaintyIntelligenceError(
                "Explicitness / strength validation must be COMPLETE."
            )

        if (
            state.get("same_sentence_uncertainty_validation")
            != "PENDING"
        ):
            raise UncertaintyIntelligenceError(
                "Same-sentence uncertainty validation must be PENDING."
            )

        boundaries = dict(
            unit.get("processing_boundaries")
            or {}
        )

        if (
            boundaries.get(
                "uncertainty_explicitness_strength_validation_performed"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Unit Stage-I boundary must be complete."
            )

        if (
            boundaries.get(
                "same_sentence_uncertainty_validation_performed"
            )
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Unit Stage-J boundary must be pending."
            )

        unit_by_id[unit_id] = unit

    validated_candidates = []
    validated_by_unit = {}

    seen_candidate_ids = set()

    for candidate in source_candidates:

        if not isinstance(candidate, Mapping):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get("uncertainty_candidate_id")
            or ""
        )

        unit_id = str(
            candidate.get("uncertainty_claim_unit_id")
            or ""
        )

        if not candidate_id:
            raise UncertaintyIntelligenceError(
                "Uncertainty Candidate ID is required."
            )

        if candidate_id in seen_candidate_ids:
            raise UncertaintyIntelligenceError(
                "Duplicate Uncertainty Candidate ID."
            )

        seen_candidate_ids.add(candidate_id)

        source_unit = unit_by_id.get(unit_id)

        if source_unit is None:
            raise UncertaintyIntelligenceError(
                "Candidate references an unknown Claim Unit."
            )

        if (
            candidate.get("uncertainty_scope_grounded")
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Candidate scope must be grounded before Stage J."
            )

        if (
            candidate.get("uncertainty_type_classified")
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Candidate type must be classified before Stage J."
            )

        if (
            candidate.get("uncertainty_explicitness_validated")
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Candidate explicitness must be validated before Stage J."
            )

        if (
            candidate.get("uncertainty_strength_validated")
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Candidate qualitative commitment must be validated."
            )

        if (
            candidate.get("same_sentence_uncertainty_validated")
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Candidate must not already be Stage-J validated."
            )

        source_text = str(
            candidate.get("source_text")
            or ""
        )

        unit_text = str(
            source_unit.get("text")
            or ""
        )

        if source_text != unit_text:
            raise UncertaintyIntelligenceError(
                "Candidate source text does not match Claim Unit text."
            )

        matched_text = str(
            candidate.get("matched_text")
            or ""
        )

        start = candidate.get("character_start")
        end = candidate.get("character_end")

        if (
            not isinstance(start, int)
            or not isinstance(end, int)
            or start < 0
            or end <= start
            or end > len(source_text)
        ):
            raise UncertaintyIntelligenceError(
                "Candidate uncertainty signal span is invalid."
            )

        if source_text[start:end] != matched_text:
            raise UncertaintyIntelligenceError(
                "Candidate uncertainty signal span does not "
                "match source sentence."
            )

        scope = candidate.get("uncertainty_scope")

        if not isinstance(scope, Mapping):
            raise UncertaintyIntelligenceError(
                "Candidate uncertainty_scope must be a mapping."
            )

        if (
            scope.get("scope_type")
            != "SAME_SENTENCE_EXPLICIT_CLAIM_SCOPE"
        ):
            raise UncertaintyIntelligenceError(
                "Stage J requires same-sentence explicit scope."
            )

        if (
            scope.get("explicit_article_evidence")
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Same-sentence scope must have explicit article evidence."
            )

        if (
            str(scope.get("scope_text") or "")
            != source_text
        ):
            raise UncertaintyIntelligenceError(
                "Grounded uncertainty scope does not match source sentence."
            )

        validated = dict(candidate)

        validated.update({
            "same_sentence_uncertainty_validated":
                True,

            "same_sentence_validation_status":
                "VALIDATED",

            "same_sentence_validation_basis":
                "EXPLICIT_SIGNAL_WITHIN_EXPLICIT_SOURCE_SENTENCE_SCOPE",

            "same_sentence_signal_present":
                True,

            "same_sentence_scope_matches_source":
                True,

            "same_sentence_explicit_article_evidence":
                True,

            "cross_sentence_uncertainty_anchor_resolved":
                False,

            "cross_sentence_uncertainty_inference_performed":
                False,

            "scope_reinterpretation_performed":
                False,

            "numeric_probability_inference_performed":
                False,

            "relative_probability_ranking_performed":
                False,

            "unstated_uncertainty_inference_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
                False,

            "semantic_memory_write_performed":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        })

        validated_candidates.append(validated)

        validated_by_unit.setdefault(
            unit_id,
            [],
        ).append(validated)

    validated_units = []
    validated_unit_by_id = {}

    for unit in source_units:

        unit_id = str(
            unit.get("uncertainty_claim_unit_id")
            or ""
        )

        state = dict(
            unit.get("uncertainty_analysis_state")
            or {}
        )

        boundaries = dict(
            unit.get("processing_boundaries")
            or {}
        )

        state[
            "same_sentence_uncertainty_validation"
        ] = "COMPLETE"

        boundaries[
            "same_sentence_uncertainty_validation_performed"
        ] = True

        boundaries[
            "cross_sentence_uncertainty_anchoring_performed"
        ] = False

        boundaries[
            "uncertainty_evidence_assessment_performed"
        ] = False

        boundaries[
            "uncertainty_duplicate_resolution_performed"
        ] = False

        boundaries[
            "numeric_probability_inference_performed"
        ] = False

        boundaries[
            "unstated_uncertainty_inference_performed"
        ] = False

        boundaries[
            "truth_assessment_performed"
        ] = False

        boundaries[
            "external_authority_check_performed"
        ] = False

        boundaries[
            "semantic_memory_write_performed"
        ] = False

        boundaries[
            "persistence_performed"
        ] = False

        updated_unit = dict(unit)

        unit_candidates = list(
            validated_by_unit.get(
                unit_id,
                []
            )
        )

        updated_unit.update({
            "uncertainty_candidates":
                unit_candidates,

            "same_sentence_validated_candidate_count":
                len(unit_candidates),

            "uncertainty_analysis_state":
                state,

            "processing_boundaries":
                boundaries,
        })

        validated_units.append(updated_unit)

        validated_unit_by_id[
            unit_id
        ] = updated_unit

    validated_sections = []

    for section in (
        explicitness_strength_result.get(
            "uncertainty_sections"
        )
        or []
    ):

        if not isinstance(section, Mapping):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get("uncertainty_claim_units")
            or []
        ):

            if not isinstance(old_unit, Mapping):
                raise UncertaintyIntelligenceError(
                    "Section Claim Unit reference must be a mapping."
                )

            unit_id = str(
                old_unit.get("uncertainty_claim_unit_id")
                or ""
            )

            resolved = validated_unit_by_id.get(
                unit_id
            )

            if resolved is None:
                raise UncertaintyIntelligenceError(
                    "Section references an unknown Claim Unit."
                )

            section_units.append(resolved)

        validated_sections.append({
            **dict(section),

            "uncertainty_claim_units":
                section_units,

            "same_sentence_validated_candidate_count":
                sum(
                    int(
                        unit.get(
                            "same_sentence_validated_candidate_count"
                        )
                        or 0
                    )
                    for unit in section_units
                ),
        })

    result = dict(
        explicitness_strength_result
    )

    result_boundaries = dict(
        result.get("processing_boundaries")
        or {}
    )

    result_boundaries[
        "same_sentence_uncertainty_validation_performed"
    ] = True

    result_boundaries[
        "cross_sentence_uncertainty_anchoring_performed"
    ] = False

    result_boundaries[
        "uncertainty_evidence_assessment_performed"
    ] = False

    result_boundaries[
        "uncertainty_duplicate_resolution_performed"
    ] = False

    result_boundaries[
        "numeric_probability_inference_performed"
    ] = False

    result_boundaries[
        "unstated_uncertainty_inference_performed"
    ] = False

    result_boundaries[
        "truth_assessment_performed"
    ] = False

    result_boundaries[
        "external_authority_check_performed"
    ] = False

    result_boundaries[
        "semantic_memory_write_performed"
    ] = False

    result_boundaries[
        "persistence_performed"
    ] = False

    result.update({
        "schema_version":
            "same_sentence_uncertainty_validation_v1",

        "patch":
            "4.6.14J",

        "status":
            "SAME_SENTENCE_UNCERTAINTY_VALIDATION_COMPLETE",

        "uncertainty_sections":
            validated_sections,

        "uncertainty_claim_units":
            validated_units,

        "uncertainty_candidates":
            validated_candidates,

        "same_sentence_uncertainty_summary": {
            "candidate_count":
                len(validated_candidates),

            "same_sentence_validated_candidate_count":
                sum(
                    1
                    for candidate in validated_candidates
                    if candidate.get(
                        "same_sentence_uncertainty_validated"
                    )
                    is True
                ),

            "cross_sentence_validation_performed":
                False,

            "scope_reinterpretation_performed":
                False,

            "numeric_probability_inferred":
                False,

            "relative_probability_ranking_performed":
                False,

            "unstated_uncertainty_inferred":
                False,

            "truth_assessment_performed":
                False,
        },

        "processing_boundaries":
            result_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "cross_sentence_uncertainty_anchoring",
    })

    return result


def anchor_cross_sentence_uncertainty_v1(
    same_sentence_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Close the cross-sentence anchoring stage conservatively.

    Candidates already fully validated within the same sentence do not
    require a cross-sentence anchor.

    This stage does NOT invent antecedents, infer unstated dependencies,
    reinterpret scope, infer probability, assess truth, access external
    authority, write Semantic Memory, make linking decisions, or persist.
    """

    if not isinstance(
        same_sentence_result,
        Mapping,
    ):
        raise UncertaintyIntelligenceError(
            "same_sentence_result must be a mapping."
        )

    if (
        same_sentence_result.get(
            "schema_version"
        )
        != "same_sentence_uncertainty_validation_v1"
    ):
        raise UncertaintyIntelligenceError(
            "Stage K requires "
            "same_sentence_uncertainty_validation_v1."
        )

    if (
        same_sentence_result.get(
            "status"
        )
        != "SAME_SENTENCE_UNCERTAINTY_VALIDATION_COMPLETE"
    ):
        raise UncertaintyIntelligenceError(
            "Stage J must be complete before Stage K."
        )

    if (
        same_sentence_result.get(
            "phase"
        )
        != "4.6.14"
    ):
        raise UncertaintyIntelligenceError(
            "Stage K requires Phase 4.6.14 input."
        )

    if (
        same_sentence_result.get(
            "patch"
        )
        != "4.6.14J"
    ):
        raise UncertaintyIntelligenceError(
            "Stage K requires canonical 4.6.14J input."
        )

    if (
        same_sentence_result.get(
            "next_stage"
        )
        != "cross_sentence_uncertainty_anchoring"
    ):
        raise UncertaintyIntelligenceError(
            "Stage J must hand off to "
            "cross_sentence_uncertainty_anchoring."
        )

    if (
        same_sentence_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise UncertaintyIntelligenceError(
            "Uncertainty Intelligence must remain transient."
        )

    top_boundaries = dict(
        same_sentence_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        top_boundaries.get(
            "same_sentence_uncertainty_validation_performed"
        )
        is not True
    ):
        raise UncertaintyIntelligenceError(
            "Stage-J boundary must be complete before Stage K."
        )

    if (
        top_boundaries.get(
            "cross_sentence_uncertainty_anchoring_performed"
        )
        is not False
    ):
        raise UncertaintyIntelligenceError(
            "Stage-K anchoring must be pending before execution."
        )

    source_units = list(
        same_sentence_result.get(
            "uncertainty_claim_units"
        )
        or []
    )

    unit_by_id = {}

    for unit in source_units:

        if not isinstance(
            unit,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise UncertaintyIntelligenceError(
                "Uncertainty Claim Unit ID is required."
            )

        if unit_id in unit_by_id:
            raise UncertaintyIntelligenceError(
                "Duplicate Uncertainty Claim Unit ID."
            )

        state = dict(
            unit.get(
                "uncertainty_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "same_sentence_uncertainty_validation"
            )
            != "COMPLETE"
        ):
            raise UncertaintyIntelligenceError(
                "Same-sentence validation must be COMPLETE."
            )

        if (
            state.get(
                "cross_sentence_uncertainty_anchoring"
            )
            != "PENDING"
        ):
            raise UncertaintyIntelligenceError(
                "Cross-sentence anchoring must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "same_sentence_uncertainty_validation_performed"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Unit Stage-J boundary must be True."
            )

        if (
            boundaries.get(
                "cross_sentence_uncertainty_anchoring_performed"
            )
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Unit Stage-K boundary must be False."
            )

        unit_by_id[
            unit_id
        ] = unit

    candidates = list(
        same_sentence_result.get(
            "uncertainty_candidates"
        )
        or []
    )

    anchored_candidates = []
    anchored_by_unit = {}

    seen_candidate_ids = set()

    for candidate in candidates:

        if not isinstance(
            candidate,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "uncertainty_candidate_id"
            )
            or ""
        )

        unit_id = str(
            candidate.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        )

        if not candidate_id:
            raise UncertaintyIntelligenceError(
                "Uncertainty Candidate ID is required."
            )

        if candidate_id in seen_candidate_ids:
            raise UncertaintyIntelligenceError(
                "Duplicate Uncertainty Candidate ID."
            )

        seen_candidate_ids.add(
            candidate_id
        )

        if unit_id not in unit_by_id:
            raise UncertaintyIntelligenceError(
                "Candidate references unknown Claim Unit."
            )

        if (
            candidate.get(
                "same_sentence_uncertainty_validated"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Stage K requires successful same-sentence validation."
            )

        if (
            candidate.get(
                "same_sentence_validation_status"
            )
            != "VALIDATED"
        ):
            raise UncertaintyIntelligenceError(
                "Same-sentence validation status must be VALIDATED."
            )

        if (
            candidate.get(
                "cross_sentence_uncertainty_anchor_resolved"
            )
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Cross-sentence anchor must not already be resolved."
            )

        if (
            candidate.get(
                "numeric_probability_inference_performed"
            )
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Numeric probability inference is forbidden."
            )

        if (
            candidate.get(
                "truth_assessment_performed"
            )
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Truth assessment is forbidden before Stage K."
            )

        anchored = dict(
            candidate
        )

        anchored.update({
            "cross_sentence_anchor_required":
                False,

            "cross_sentence_anchor_status":
                "NOT_REQUIRED_SAME_SENTENCE_RESOLVED",

            "cross_sentence_anchor":
                None,

            "cross_sentence_uncertainty_anchor_resolved":
                False,

            "cross_sentence_uncertainty_anchoring_completed":
                True,

            "cross_sentence_uncertainty_inference_performed":
                False,

            "unstated_antecedent_inference_performed":
                False,

            "scope_reinterpretation_performed":
                False,

            "numeric_probability_inference_performed":
                False,

            "relative_probability_ranking_performed":
                False,

            "unstated_uncertainty_inference_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
                False,

            "semantic_memory_write_performed":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        })

        anchored_candidates.append(
            anchored
        )

        anchored_by_unit.setdefault(
            unit_id,
            [],
        ).append(
            anchored
        )

    anchored_units = []
    anchored_unit_by_id = {}

    for unit in source_units:

        unit_id = str(
            unit.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        )

        state = dict(
            unit.get(
                "uncertainty_analysis_state"
            )
            or {}
        )

        state[
            "cross_sentence_uncertainty_anchoring"
        ] = "COMPLETE"

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        boundaries[
            "cross_sentence_uncertainty_anchoring_performed"
        ] = True

        boundaries[
            "uncertainty_evidence_assessment_performed"
        ] = False

        boundaries[
            "uncertainty_duplicate_resolution_performed"
        ] = False

        boundaries[
            "unstated_uncertainty_inference_performed"
        ] = False

        boundaries[
            "numeric_probability_inference_performed"
        ] = False

        boundaries[
            "truth_assessment_performed"
        ] = False

        boundaries[
            "external_authority_check_performed"
        ] = False

        boundaries[
            "semantic_memory_write_performed"
        ] = False

        boundaries[
            "persistence_performed"
        ] = False

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "uncertainty_candidates":
                list(
                    anchored_by_unit.get(
                        unit_id,
                        []
                    )
                ),

            "cross_sentence_anchor_required_count":
                0,

            "cross_sentence_anchor_not_required_count":
                len(
                    anchored_by_unit.get(
                        unit_id,
                        []
                    )
                ),

            "uncertainty_analysis_state":
                state,

            "processing_boundaries":
                boundaries,
        })

        anchored_units.append(
            updated_unit
        )

        anchored_unit_by_id[
            unit_id
        ] = updated_unit

    anchored_sections = []

    for section in (
        same_sentence_result.get(
            "uncertainty_sections"
        )
        or []
    ):

        if not isinstance(
            section,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty section must be a mapping."
            )

        rebuilt_units = []

        for old_unit in (
            section.get(
                "uncertainty_claim_units"
            )
            or []
        ):

            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise UncertaintyIntelligenceError(
                    "Section Claim Unit reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "uncertainty_claim_unit_id"
                )
                or ""
            )

            resolved = anchored_unit_by_id.get(
                unit_id
            )

            if resolved is None:
                raise UncertaintyIntelligenceError(
                    "Section references unknown Claim Unit."
                )

            rebuilt_units.append(
                resolved
            )

        anchored_sections.append({
            **dict(
                section
            ),

            "uncertainty_claim_units":
                rebuilt_units,

            "cross_sentence_anchor_required_count":
                0,

            "cross_sentence_anchor_not_required_count":
                sum(
                    int(
                        unit.get(
                            "cross_sentence_anchor_not_required_count"
                        )
                        or 0
                    )
                    for unit in rebuilt_units
                ),
        })

    result = dict(
        same_sentence_result
    )

    result_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    result_boundaries[
        "cross_sentence_uncertainty_anchoring_performed"
    ] = True

    result_boundaries[
        "uncertainty_evidence_assessment_performed"
    ] = False

    result_boundaries[
        "uncertainty_duplicate_resolution_performed"
    ] = False

    result_boundaries[
        "unstated_uncertainty_inference_performed"
    ] = False

    result_boundaries[
        "numeric_probability_inference_performed"
    ] = False

    result_boundaries[
        "truth_assessment_performed"
    ] = False

    result_boundaries[
        "external_authority_check_performed"
    ] = False

    result_boundaries[
        "semantic_memory_write_performed"
    ] = False

    result_boundaries[
        "persistence_performed"
    ] = False

    result.update({
        "schema_version":
            "cross_sentence_uncertainty_anchoring_v1",

        "patch":
            "4.6.14K",

        "status":
            "CROSS_SENTENCE_UNCERTAINTY_ANCHORING_COMPLETE",

        "uncertainty_candidates":
            anchored_candidates,

        "uncertainty_claim_units":
            anchored_units,

        "uncertainty_sections":
            anchored_sections,

        "cross_sentence_uncertainty_summary": {
            "candidate_count":
                len(
                    anchored_candidates
                ),

            "cross_sentence_anchor_required_count":
                0,

            "cross_sentence_anchor_resolved_count":
                0,

            "same_sentence_resolved_count":
                len(
                    anchored_candidates
                ),

            "cross_sentence_anchor_not_required_count":
                len(
                    anchored_candidates
                ),

            "unstated_antecedent_inference_count":
                0,

            "scope_reinterpretation_performed":
                False,

            "numeric_probability_inferred":
                False,

            "relative_probability_ranking_performed":
                False,

            "unstated_uncertainty_inferred":
                False,

            "truth_assessment_performed":
                False,
        },

        "processing_boundaries":
            result_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "uncertainty_evidence_assessment",
    })

    return result


def assess_uncertainty_evidence_confidence_v1(
    cross_sentence_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Assess article-local evidence quality for validated
    Uncertainty candidates.

    This confidence describes LinkCraftor's evidence support for
    the uncertainty interpretation. It does NOT describe:
    - the probability that the article claim is true,
    - scientific or factual truth,
    - numeric source probability,
    - unified Semantic Confidence,
    - external authority validation.

    Numeric unified confidence remains outside this layer.
    """

    if not isinstance(
        cross_sentence_result,
        Mapping,
    ):
        raise UncertaintyIntelligenceError(
            "cross_sentence_result must be a mapping."
        )

    if (
        cross_sentence_result.get(
            "schema_version"
        )
        != "cross_sentence_uncertainty_anchoring_v1"
    ):
        raise UncertaintyIntelligenceError(
            "Stage L requires "
            "cross_sentence_uncertainty_anchoring_v1."
        )

    if (
        cross_sentence_result.get(
            "status"
        )
        != "CROSS_SENTENCE_UNCERTAINTY_ANCHORING_COMPLETE"
    ):
        raise UncertaintyIntelligenceError(
            "Stage K must be complete before Stage L."
        )

    if (
        cross_sentence_result.get(
            "phase"
        )
        != "4.6.14"
    ):
        raise UncertaintyIntelligenceError(
            "Stage L requires Phase 4.6.14 input."
        )

    if (
        cross_sentence_result.get(
            "patch"
        )
        != "4.6.14K"
    ):
        raise UncertaintyIntelligenceError(
            "Stage L requires canonical 4.6.14K input."
        )

    if (
        cross_sentence_result.get(
            "next_stage"
        )
        != "uncertainty_evidence_assessment"
    ):
        raise UncertaintyIntelligenceError(
            "Stage K must hand off to "
            "uncertainty_evidence_assessment."
        )

    if (
        cross_sentence_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise UncertaintyIntelligenceError(
            "Uncertainty Intelligence must remain transient."
        )

    top_boundaries = dict(
        cross_sentence_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        top_boundaries.get(
            "cross_sentence_uncertainty_anchoring_performed"
        )
        is not True
    ):
        raise UncertaintyIntelligenceError(
            "Stage-K boundary must be complete."
        )

    if (
        top_boundaries.get(
            "uncertainty_evidence_assessment_performed"
        )
        is not False
    ):
        raise UncertaintyIntelligenceError(
            "Evidence assessment must be pending before Stage L."
        )

    source_units = list(
        cross_sentence_result.get(
            "uncertainty_claim_units"
        )
        or []
    )

    source_candidates = list(
        cross_sentence_result.get(
            "uncertainty_candidates"
        )
        or []
    )

    unit_by_id = {}

    for unit in source_units:

        if not isinstance(
            unit,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise UncertaintyIntelligenceError(
                "Uncertainty Claim Unit ID is required."
            )

        if unit_id in unit_by_id:
            raise UncertaintyIntelligenceError(
                "Duplicate Uncertainty Claim Unit ID."
            )

        state = dict(
            unit.get(
                "uncertainty_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "cross_sentence_uncertainty_anchoring"
            )
            != "COMPLETE"
        ):
            raise UncertaintyIntelligenceError(
                "Stage K must be COMPLETE for every Claim Unit."
            )

        if (
            state.get(
                "uncertainty_evidence_assessment"
            )
            != "PENDING"
        ):
            raise UncertaintyIntelligenceError(
                "Evidence assessment must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "cross_sentence_uncertainty_anchoring_performed"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Unit Stage-K boundary must be True."
            )

        if (
            boundaries.get(
                "uncertainty_evidence_assessment_performed"
            )
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Unit Stage-L boundary must be pending."
            )

        unit_by_id[
            unit_id
        ] = unit

    assessed_candidates = []
    assessed_by_unit = {}

    confidence_class_counts = {}
    evidence_status_counts = {}

    seen_candidate_ids = set()

    for candidate in source_candidates:

        if not isinstance(
            candidate,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "uncertainty_candidate_id"
            )
            or ""
        )

        unit_id = str(
            candidate.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        )

        if not candidate_id:
            raise UncertaintyIntelligenceError(
                "Uncertainty Candidate ID is required."
            )

        if candidate_id in seen_candidate_ids:
            raise UncertaintyIntelligenceError(
                "Duplicate Uncertainty Candidate ID."
            )

        seen_candidate_ids.add(
            candidate_id
        )

        if unit_id not in unit_by_id:
            raise UncertaintyIntelligenceError(
                "Candidate references an unknown Claim Unit."
            )

        if (
            candidate.get(
                "same_sentence_uncertainty_validated"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Same-sentence uncertainty must already be validated."
            )

        if (
            candidate.get(
                "same_sentence_validation_status"
            )
            != "VALIDATED"
        ):
            raise UncertaintyIntelligenceError(
                "Stage-J candidate status must be VALIDATED."
            )

        if (
            candidate.get(
                "cross_sentence_uncertainty_anchoring_completed"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Stage K must be completed for every candidate."
            )

        cross_status = str(
            candidate.get(
                "cross_sentence_anchor_status"
            )
            or ""
        )

        allowed_cross_statuses = {
            "NOT_REQUIRED_SAME_SENTENCE_RESOLVED",
            "RESOLVED_EXPLICIT_CROSS_SENTENCE_ANCHOR",
        }

        if cross_status not in allowed_cross_statuses:
            raise UncertaintyIntelligenceError(
                "Candidate has unsupported cross-sentence "
                "anchoring status."
            )

        if (
            candidate.get(
                "numeric_probability_inference_performed"
            )
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Numeric probability inference is forbidden."
            )

        if (
            candidate.get(
                "truth_assessment_performed"
            )
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Truth assessment is forbidden."
            )

        evidence_factors = {
            "explicit_uncertainty_signal":
                bool(
                    candidate.get(
                        "same_sentence_signal_present"
                    )
                    is True
                ),

            "explicit_article_scope":
                bool(
                    candidate.get(
                        "same_sentence_explicit_article_evidence"
                    )
                    is True
                ),

            "scope_matches_source_sentence":
                bool(
                    candidate.get(
                        "same_sentence_scope_matches_source"
                    )
                    is True
                ),

            "uncertainty_type_classified":
                bool(
                    candidate.get(
                        "uncertainty_type_classified"
                    )
                    is True
                ),

            "explicitness_validated":
                bool(
                    candidate.get(
                        "uncertainty_explicitness_validated"
                    )
                    is True
                ),

            "qualitative_commitment_validated":
                bool(
                    candidate.get(
                        "uncertainty_strength_validated"
                    )
                    is True
                ),

            "same_sentence_validation_complete":
                True,

            "cross_sentence_stage_complete":
                True,
        }

        if not all(
            evidence_factors.values()
        ):
            raise UncertaintyIntelligenceError(
                "Validated uncertainty candidate lacks "
                "required evidence factors."
            )

        if (
            cross_status
            == "NOT_REQUIRED_SAME_SENTENCE_RESOLVED"
        ):
            evidence_status = (
                "DIRECT_EXPLICIT_SAME_SENTENCE_EVIDENCE"
            )

            confidence_class = (
                "HIGH_STRUCTURAL_EVIDENCE_CONFIDENCE"
            )

            confidence_basis = (
                "EXPLICIT_SIGNAL_PLUS_VALIDATED_"
                "SAME_SENTENCE_SCOPE"
            )

        else:
            evidence_status = (
                "EXPLICIT_CROSS_SENTENCE_ANCHORED_EVIDENCE"
            )

            confidence_class = (
                "SUPPORTED_STRUCTURAL_EVIDENCE_CONFIDENCE"
            )

            confidence_basis = (
                "EXPLICIT_SIGNAL_PLUS_VALIDATED_"
                "CROSS_SENTENCE_ANCHOR"
            )

        assessed = dict(
            candidate
        )

        assessed.update({
            "uncertainty_evidence_status":
                evidence_status,

            "uncertainty_evidence_factors":
                evidence_factors,

            "uncertainty_evidence_assessed":
                True,

            "uncertainty_evidence_confidence_class":
                confidence_class,

            "uncertainty_evidence_confidence_basis":
                confidence_basis,

            "uncertainty_evidence_confidence_numeric":
                None,

            "unified_semantic_confidence_calculated":
                False,

            "source_claim_probability_estimated":
                False,

            "scientific_truth_assessed":
                False,

            "external_authority_checked":
                False,

            "numeric_probability_inference_performed":
                False,

            "relative_probability_ranking_performed":
                False,

            "unstated_uncertainty_inference_performed":
                False,

            "truth_assessment_performed":
                False,

            "semantic_memory_write_performed":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        })

        assessed_candidates.append(
            assessed
        )

        assessed_by_unit.setdefault(
            unit_id,
            [],
        ).append(
            assessed
        )

        confidence_class_counts[
            confidence_class
        ] = (
            confidence_class_counts.get(
                confidence_class,
                0,
            )
            + 1
        )

        evidence_status_counts[
            evidence_status
        ] = (
            evidence_status_counts.get(
                evidence_status,
                0,
            )
            + 1
        )

    assessed_units = []
    assessed_unit_by_id = {}

    for unit in source_units:

        unit_id = str(
            unit.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        )

        state = dict(
            unit.get(
                "uncertainty_analysis_state"
            )
            or {}
        )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        state[
            "uncertainty_evidence_assessment"
        ] = "COMPLETE"

        boundaries[
            "uncertainty_evidence_assessment_performed"
        ] = True

        boundaries[
            "uncertainty_duplicate_resolution_performed"
        ] = False

        boundaries[
            "numeric_probability_inference_performed"
        ] = False

        boundaries[
            "unstated_uncertainty_inference_performed"
        ] = False

        boundaries[
            "truth_assessment_performed"
        ] = False

        boundaries[
            "external_authority_check_performed"
        ] = False

        boundaries[
            "semantic_memory_write_performed"
        ] = False

        boundaries[
            "persistence_performed"
        ] = False

        unit_candidates = list(
            assessed_by_unit.get(
                unit_id,
                []
            )
        )

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "uncertainty_candidates":
                unit_candidates,

            "uncertainty_evidence_assessed_candidate_count":
                len(
                    unit_candidates
                ),

            "uncertainty_analysis_state":
                state,

            "processing_boundaries":
                boundaries,
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
            "uncertainty_sections"
        )
        or []
    ):

        if not isinstance(
            section,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "uncertainty_claim_units"
            )
            or []
        ):

            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise UncertaintyIntelligenceError(
                    "Section Claim Unit reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "uncertainty_claim_unit_id"
                )
                or ""
            )

            resolved = assessed_unit_by_id.get(
                unit_id
            )

            if resolved is None:
                raise UncertaintyIntelligenceError(
                    "Section references an unknown Claim Unit."
                )

            section_units.append(
                resolved
            )

        assessed_sections.append({
            **dict(
                section
            ),

            "uncertainty_claim_units":
                section_units,

            "uncertainty_evidence_assessed_candidate_count":
                sum(
                    int(
                        unit.get(
                            "uncertainty_evidence_assessed_candidate_count"
                        )
                        or 0
                    )
                    for unit in section_units
                ),
        })

    result = dict(
        cross_sentence_result
    )

    result_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    result_boundaries[
        "uncertainty_evidence_assessment_performed"
    ] = True

    result_boundaries[
        "uncertainty_duplicate_resolution_performed"
    ] = False

    result_boundaries[
        "numeric_probability_inference_performed"
    ] = False

    result_boundaries[
        "unstated_uncertainty_inference_performed"
    ] = False

    result_boundaries[
        "truth_assessment_performed"
    ] = False

    result_boundaries[
        "external_authority_check_performed"
    ] = False

    result_boundaries[
        "semantic_memory_write_performed"
    ] = False

    result_boundaries[
        "persistence_performed"
    ] = False

    result.update({
        "schema_version":
            "uncertainty_evidence_confidence_assessment_v1",

        "patch":
            "4.6.14L",

        "status":
            "UNCERTAINTY_EVIDENCE_CONFIDENCE_ASSESSMENT_COMPLETE",

        "uncertainty_candidates":
            assessed_candidates,

        "uncertainty_claim_units":
            assessed_units,

        "uncertainty_sections":
            assessed_sections,

        "uncertainty_evidence_summary": {
            "candidate_count":
                len(
                    assessed_candidates
                ),

            "evidence_assessed_candidate_count":
                sum(
                    1
                    for candidate in assessed_candidates
                    if candidate.get(
                        "uncertainty_evidence_assessed"
                    )
                    is True
                ),

            "confidence_class_counts":
                dict(
                    sorted(
                        confidence_class_counts.items()
                    )
                ),

            "evidence_status_counts":
                dict(
                    sorted(
                        evidence_status_counts.items()
                    )
                ),

            "numeric_evidence_confidence_calculated":
                False,

            "unified_semantic_confidence_calculated":
                False,

            "source_claim_probability_estimated":
                False,

            "scientific_truth_assessed":
                False,

            "external_authority_checked":
                False,

            "numeric_probability_inferred":
                False,

            "relative_probability_ranking_performed":
                False,
        },

        "processing_boundaries":
            result_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "uncertainty_duplicate_resolution",
    })

    return result


def resolve_uncertainty_duplicates_v1(
    evidence_assessment_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Resolve exact duplicate / redundant Uncertainty candidates.

    Duplicate identity is deliberately conservative:
    same Claim Unit + same explicit source span + same signal type
    + same canonical uncertainty type + same matched text.

    Distinct uncertainty signals in the same sentence are preserved.

    This stage does NOT:
    - merge different uncertainty types,
    - merge different lexical spans,
    - infer semantic equivalence,
    - infer probability,
    - reassess evidence confidence,
    - assess truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        evidence_assessment_result,
        Mapping,
    ):
        raise UncertaintyIntelligenceError(
            "evidence_assessment_result must be a mapping."
        )

    if (
        evidence_assessment_result.get(
            "schema_version"
        )
        != "uncertainty_evidence_confidence_assessment_v1"
    ):
        raise UncertaintyIntelligenceError(
            "Stage M requires "
            "uncertainty_evidence_confidence_assessment_v1."
        )

    if (
        evidence_assessment_result.get(
            "status"
        )
        != "UNCERTAINTY_EVIDENCE_CONFIDENCE_ASSESSMENT_COMPLETE"
    ):
        raise UncertaintyIntelligenceError(
            "Stage L must be complete before Stage M."
        )

    if (
        evidence_assessment_result.get(
            "phase"
        )
        != "4.6.14"
    ):
        raise UncertaintyIntelligenceError(
            "Stage M requires Phase 4.6.14 input."
        )

    if (
        evidence_assessment_result.get(
            "patch"
        )
        != "4.6.14L"
    ):
        raise UncertaintyIntelligenceError(
            "Stage M requires canonical 4.6.14L input."
        )

    if (
        evidence_assessment_result.get(
            "next_stage"
        )
        != "uncertainty_duplicate_resolution"
    ):
        raise UncertaintyIntelligenceError(
            "Stage L must hand off to "
            "uncertainty_duplicate_resolution."
        )

    if (
        evidence_assessment_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise UncertaintyIntelligenceError(
            "Uncertainty Intelligence must remain transient."
        )

    top_boundaries = dict(
        evidence_assessment_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        top_boundaries.get(
            "uncertainty_evidence_assessment_performed"
        )
        is not True
    ):
        raise UncertaintyIntelligenceError(
            "Stage-L evidence assessment boundary must be complete."
        )

    if (
        top_boundaries.get(
            "uncertainty_duplicate_resolution_performed"
        )
        is not False
    ):
        raise UncertaintyIntelligenceError(
            "Duplicate resolution must be pending before Stage M."
        )

    source_units = list(
        evidence_assessment_result.get(
            "uncertainty_claim_units"
        )
        or []
    )

    unit_by_id = {}

    for unit in source_units:

        if not isinstance(
            unit,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise UncertaintyIntelligenceError(
                "Uncertainty Claim Unit ID is required."
            )

        if unit_id in unit_by_id:
            raise UncertaintyIntelligenceError(
                "Duplicate Uncertainty Claim Unit ID."
            )

        state = dict(
            unit.get(
                "uncertainty_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "uncertainty_evidence_assessment"
            )
            != "COMPLETE"
        ):
            raise UncertaintyIntelligenceError(
                "Evidence assessment must be COMPLETE before Stage M."
            )

        if (
            state.get(
                "duplicate_uncertainty_resolution"
            )
            != "PENDING"
        ):
            raise UncertaintyIntelligenceError(
                "Duplicate resolution must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "uncertainty_evidence_assessment_performed"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Unit Stage-L boundary must be True."
            )

        if (
            boundaries.get(
                "uncertainty_duplicate_resolution_performed"
            )
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Unit Stage-M boundary must be False."
            )

        unit_by_id[
            unit_id
        ] = unit

    source_candidates = list(
        evidence_assessment_result.get(
            "uncertainty_candidates"
        )
        or []
    )

    resolved_candidates = []
    redundant_candidates = []

    canonical_by_key = {}
    seen_candidate_ids = set()

    for candidate in source_candidates:

        if not isinstance(
            candidate,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "uncertainty_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise UncertaintyIntelligenceError(
                "Uncertainty Candidate ID is required."
            )

        if candidate_id in seen_candidate_ids:
            raise UncertaintyIntelligenceError(
                "Duplicate candidate ID is not permitted."
            )

        seen_candidate_ids.add(
            candidate_id
        )

        unit_id = str(
            candidate.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        )

        if unit_id not in unit_by_id:
            raise UncertaintyIntelligenceError(
                "Candidate references unknown Claim Unit."
            )

        if (
            candidate.get(
                "uncertainty_evidence_assessed"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Candidate evidence must be assessed before Stage M."
            )

        if (
            candidate.get(
                "uncertainty_evidence_status"
            )
            != "DIRECT_EXPLICIT_SAME_SENTENCE_EVIDENCE"
        ):
            raise UncertaintyIntelligenceError(
                "Stage M currently requires direct explicit "
                "same-sentence evidence."
            )

        if (
            candidate.get(
                "duplicate_resolution_performed"
            )
            is True
        ):
            raise UncertaintyIntelligenceError(
                "Candidate duplicate resolution was already performed."
            )

        start = candidate.get(
            "character_start"
        )

        end = candidate.get(
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
        ):
            raise UncertaintyIntelligenceError(
                "Candidate requires a valid explicit source span."
            )

        signal_type = str(
            candidate.get(
                "signal_type"
            )
            or ""
        )

        uncertainty_type = str(
            candidate.get(
                "uncertainty_type"
            )
            or ""
        )

        matched_text = str(
            candidate.get(
                "matched_text"
            )
            or ""
        )

        if (
            not signal_type
            or not uncertainty_type
            or not matched_text
        ):
            raise UncertaintyIntelligenceError(
                "Candidate duplicate identity fields are incomplete."
            )

        duplicate_key = (
            unit_id,
            start,
            end,
            signal_type,
            uncertainty_type,
            matched_text,
        )

        canonical_candidate = (
            canonical_by_key.get(
                duplicate_key
            )
        )

        if canonical_candidate is None:

            resolved = dict(
                candidate
            )

            resolved.update({
                "duplicate_resolution_performed":
                    True,

                "duplicate_resolution_status":
                    "CANONICAL_UNIQUE_CANDIDATE",

                "is_redundant_candidate":
                    False,

                "canonical_uncertainty_candidate_id":
                    candidate_id,

                "redundant_with_candidate_id":
                    None,

                "semantic_equivalence_inference_performed":
                    False,

                "numeric_probability_inference_performed":
                    False,

                "truth_assessment_performed":
                    False,

                "external_authority_check_performed":
                    False,

                "semantic_memory_write_performed":
                    False,

                "linking_decisions_performed":
                    False,

                "persistence_performed":
                    False,
            })

            canonical_by_key[
                duplicate_key
            ] = resolved

            resolved_candidates.append(
                resolved
            )

        else:

            redundant = dict(
                candidate
            )

            redundant.update({
                "duplicate_resolution_performed":
                    True,

                "duplicate_resolution_status":
                    "REDUNDANT_EXACT_DUPLICATE",

                "is_redundant_candidate":
                    True,

                "canonical_uncertainty_candidate_id":
                    canonical_candidate[
                        "uncertainty_candidate_id"
                    ],

                "redundant_with_candidate_id":
                    canonical_candidate[
                        "uncertainty_candidate_id"
                    ],

                "semantic_equivalence_inference_performed":
                    False,

                "numeric_probability_inference_performed":
                    False,

                "truth_assessment_performed":
                    False,

                "external_authority_check_performed":
                    False,

                "semantic_memory_write_performed":
                    False,

                "linking_decisions_performed":
                    False,

                "persistence_performed":
                    False,
            })

            redundant_candidates.append(
                redundant
            )

    resolved_by_unit = {}

    for candidate in resolved_candidates:

        unit_id = str(
            candidate.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        )

        resolved_by_unit.setdefault(
            unit_id,
            [],
        ).append(
            candidate
        )

    redundant_by_unit = {}

    for candidate in redundant_candidates:

        unit_id = str(
            candidate.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        )

        redundant_by_unit.setdefault(
            unit_id,
            [],
        ).append(
            candidate
        )

    resolved_units = []
    resolved_unit_by_id = {}

    for unit in source_units:

        unit_id = str(
            unit.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        )

        state = dict(
            unit.get(
                "uncertainty_analysis_state"
            )
            or {}
        )

        state[
            "duplicate_uncertainty_resolution"
        ] = "COMPLETE"

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        boundaries[
            "uncertainty_duplicate_resolution_performed"
        ] = True

        boundaries[
            "numeric_probability_inference_performed"
        ] = False

        boundaries[
            "unstated_uncertainty_inference_performed"
        ] = False

        boundaries[
            "truth_assessment_performed"
        ] = False

        boundaries[
            "external_authority_check_performed"
        ] = False

        boundaries[
            "semantic_memory_write_performed"
        ] = False

        boundaries[
            "persistence_performed"
        ] = False

        canonical_candidates = list(
            resolved_by_unit.get(
                unit_id,
                []
            )
        )

        redundant_unit_candidates = list(
            redundant_by_unit.get(
                unit_id,
                []
            )
        )

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "uncertainty_candidates":
                canonical_candidates,

            "redundant_uncertainty_candidates":
                redundant_unit_candidates,

            "canonical_uncertainty_candidate_count":
                len(
                    canonical_candidates
                ),

            "redundant_uncertainty_candidate_count":
                len(
                    redundant_unit_candidates
                ),

            "uncertainty_analysis_state":
                state,

            "processing_boundaries":
                boundaries,
        })

        resolved_units.append(
            updated_unit
        )

        resolved_unit_by_id[
            unit_id
        ] = updated_unit

    resolved_sections = []

    for section in (
        evidence_assessment_result.get(
            "uncertainty_sections"
        )
        or []
    ):

        if not isinstance(
            section,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "uncertainty_claim_units"
            )
            or []
        ):

            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise UncertaintyIntelligenceError(
                    "Section Claim Unit reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "uncertainty_claim_unit_id"
                )
                or ""
            )

            resolved = (
                resolved_unit_by_id.get(
                    unit_id
                )
            )

            if resolved is None:
                raise UncertaintyIntelligenceError(
                    "Section references unknown Claim Unit."
                )

            section_units.append(
                resolved
            )

        resolved_sections.append({
            **dict(
                section
            ),

            "uncertainty_claim_units":
                section_units,

            "canonical_uncertainty_candidate_count":
                sum(
                    int(
                        unit.get(
                            "canonical_uncertainty_candidate_count"
                        )
                        or 0
                    )
                    for unit in section_units
                ),

            "redundant_uncertainty_candidate_count":
                sum(
                    int(
                        unit.get(
                            "redundant_uncertainty_candidate_count"
                        )
                        or 0
                    )
                    for unit in section_units
                ),
        })

    result = dict(
        evidence_assessment_result
    )

    result_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    result_boundaries[
        "uncertainty_duplicate_resolution_performed"
    ] = True

    result_boundaries[
        "numeric_probability_inference_performed"
    ] = False

    result_boundaries[
        "unstated_uncertainty_inference_performed"
    ] = False

    result_boundaries[
        "truth_assessment_performed"
    ] = False

    result_boundaries[
        "external_authority_check_performed"
    ] = False

    result_boundaries[
        "semantic_memory_write_performed"
    ] = False

    result_boundaries[
        "persistence_performed"
    ] = False

    result.update({
        "schema_version":
            "uncertainty_duplicate_resolution_v1",

        "patch":
            "4.6.14M",

        "status":
            "UNCERTAINTY_DUPLICATE_RESOLUTION_COMPLETE",

        "uncertainty_candidates":
            resolved_candidates,

        "redundant_uncertainty_candidates":
            redundant_candidates,

        "uncertainty_claim_units":
            resolved_units,

        "uncertainty_sections":
            resolved_sections,

        "uncertainty_duplicate_summary": {
            "input_candidate_count":
                len(
                    source_candidates
                ),

            "canonical_candidate_count":
                len(
                    resolved_candidates
                ),

            "redundant_candidate_count":
                len(
                    redundant_candidates
                ),

            "exact_duplicate_resolution_only":
                True,

            "different_signal_types_merged":
                False,

            "different_uncertainty_types_merged":
                False,

            "different_source_spans_merged":
                False,

            "semantic_equivalence_inference_performed":
                False,

            "numeric_probability_inferred":
                False,

            "truth_assessment_performed":
                False,
        },

        "processing_boundaries":
            result_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "article_uncertainty_consolidation",
    })

    return result


def consolidate_article_uncertainty_v1(
    duplicate_resolution_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Consolidate canonical article-local Uncertainty candidates
    into an article-level Uncertainty profile.

    Stage N aggregates only already-certified canonical candidates.

    It does NOT:
    - create new candidates,
    - infer unstated uncertainty,
    - merge semantic equivalents,
    - infer numeric probability,
    - calculate unified Semantic Confidence,
    - assess scientific or factual truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        duplicate_resolution_result,
        Mapping,
    ):
        raise UncertaintyIntelligenceError(
            "duplicate_resolution_result must be a mapping."
        )

    if (
        duplicate_resolution_result.get(
            "schema_version"
        )
        != "uncertainty_duplicate_resolution_v1"
    ):
        raise UncertaintyIntelligenceError(
            "Stage N requires uncertainty_duplicate_resolution_v1."
        )

    if (
        duplicate_resolution_result.get(
            "status"
        )
        != "UNCERTAINTY_DUPLICATE_RESOLUTION_COMPLETE"
    ):
        raise UncertaintyIntelligenceError(
            "Stage M must be complete before Stage N."
        )

    if (
        duplicate_resolution_result.get(
            "phase"
        )
        != "4.6.14"
    ):
        raise UncertaintyIntelligenceError(
            "Stage N requires Phase 4.6.14 input."
        )

    if (
        duplicate_resolution_result.get(
            "patch"
        )
        != "4.6.14M"
    ):
        raise UncertaintyIntelligenceError(
            "Stage N requires canonical 4.6.14M input."
        )

    if (
        duplicate_resolution_result.get(
            "next_stage"
        )
        != "article_uncertainty_consolidation"
    ):
        raise UncertaintyIntelligenceError(
            "Stage M must hand off to "
            "article_uncertainty_consolidation."
        )

    if (
        duplicate_resolution_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise UncertaintyIntelligenceError(
            "Uncertainty Intelligence must remain transient."
        )

    top_boundaries = dict(
        duplicate_resolution_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        top_boundaries.get(
            "uncertainty_duplicate_resolution_performed"
        )
        is not True
    ):
        raise UncertaintyIntelligenceError(
            "Stage-M duplicate resolution boundary must be complete."
        )

    if (
        top_boundaries.get(
            "article_uncertainty_consolidation_performed"
        )
        not in (
            None,
            False,
        )
    ):
        raise UncertaintyIntelligenceError(
            "Article consolidation must be pending before Stage N."
        )

    canonical_candidates = list(
        duplicate_resolution_result.get(
            "uncertainty_candidates"
        )
        or []
    )

    redundant_candidates = list(
        duplicate_resolution_result.get(
            "redundant_uncertainty_candidates"
        )
        or []
    )

    source_units = list(
        duplicate_resolution_result.get(
            "uncertainty_claim_units"
        )
        or []
    )

    unit_by_id = {}

    for unit in source_units:

        if not isinstance(
            unit,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise UncertaintyIntelligenceError(
                "Uncertainty Claim Unit ID is required."
            )

        if unit_id in unit_by_id:
            raise UncertaintyIntelligenceError(
                "Duplicate Uncertainty Claim Unit ID."
            )

        state = dict(
            unit.get(
                "uncertainty_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "duplicate_uncertainty_resolution"
            )
            != "COMPLETE"
        ):
            raise UncertaintyIntelligenceError(
                "Stage M must be COMPLETE for every Claim Unit."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "uncertainty_duplicate_resolution_performed"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Unit Stage-M boundary must be True."
            )

        unit_by_id[
            unit_id
        ] = unit

    type_counts = {}
    signal_type_counts = {}
    commitment_class_counts = {}
    confidence_class_counts = {}
    evidence_status_counts = {}
    section_candidate_counts = {}
    claim_unit_candidate_counts = {}

    seen_candidate_ids = set()

    consolidated_candidates = []

    for candidate in canonical_candidates:

        if not isinstance(
            candidate,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every canonical Uncertainty candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "uncertainty_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise UncertaintyIntelligenceError(
                "Canonical candidate ID is required."
            )

        if candidate_id in seen_candidate_ids:
            raise UncertaintyIntelligenceError(
                "Duplicate canonical candidate ID."
            )

        seen_candidate_ids.add(
            candidate_id
        )

        if (
            candidate.get(
                "duplicate_resolution_status"
            )
            != "CANONICAL_UNIQUE_CANDIDATE"
        ):
            raise UncertaintyIntelligenceError(
                "Stage N accepts only canonical unique candidates."
            )

        if (
            candidate.get(
                "duplicate_resolution_performed"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Canonical candidate duplicate resolution "
                "must already be performed."
            )

        if (
            candidate.get(
                "uncertainty_evidence_assessed"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Canonical candidate evidence must be assessed."
            )

        if (
            candidate.get(
                "numeric_probability_inference_performed"
            )
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Numeric probability inference is forbidden."
            )

        if (
            candidate.get(
                "truth_assessment_performed"
            )
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Truth assessment is forbidden."
            )

        unit_id = str(
            candidate.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        )

        if unit_id not in unit_by_id:
            raise UncertaintyIntelligenceError(
                "Canonical candidate references unknown Claim Unit."
            )

        uncertainty_type = str(
            candidate.get(
                "uncertainty_type"
            )
            or ""
        )

        signal_type = str(
            candidate.get(
                "signal_type"
            )
            or ""
        )

        commitment_class = str(
            candidate.get(
                "uncertainty_commitment_class"
            )
            or ""
        )

        confidence_class = str(
            candidate.get(
                "uncertainty_evidence_confidence_class"
            )
            or ""
        )

        evidence_status = str(
            candidate.get(
                "uncertainty_evidence_status"
            )
            or ""
        )

        section_id = str(
            candidate.get(
                "section_id"
            )
            or unit_by_id[
                unit_id
            ].get(
                "section_id"
            )
            or ""
        )

        if not uncertainty_type:
            raise UncertaintyIntelligenceError(
                "Canonical candidate uncertainty_type is required."
            )

        if not signal_type:
            raise UncertaintyIntelligenceError(
                "Canonical candidate signal_type is required."
            )

        if not confidence_class:
            raise UncertaintyIntelligenceError(
                "Canonical candidate evidence confidence class is required."
            )

        if not evidence_status:
            raise UncertaintyIntelligenceError(
                "Canonical candidate evidence status is required."
            )

        type_counts[
            uncertainty_type
        ] = (
            type_counts.get(
                uncertainty_type,
                0,
            )
            + 1
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

        if commitment_class:
            commitment_class_counts[
                commitment_class
            ] = (
                commitment_class_counts.get(
                    commitment_class,
                    0,
                )
                + 1
            )

        confidence_class_counts[
            confidence_class
        ] = (
            confidence_class_counts.get(
                confidence_class,
                0,
            )
            + 1
        )

        evidence_status_counts[
            evidence_status
        ] = (
            evidence_status_counts.get(
                evidence_status,
                0,
            )
            + 1
        )

        if section_id:
            section_candidate_counts[
                section_id
            ] = (
                section_candidate_counts.get(
                    section_id,
                    0,
                )
                + 1
            )

        claim_unit_candidate_counts[
            unit_id
        ] = (
            claim_unit_candidate_counts.get(
                unit_id,
                0,
            )
            + 1
        )

        consolidated = dict(
            candidate
        )

        consolidated.update({
            "article_uncertainty_consolidated":
                True,

            "article_uncertainty_consolidation_status":
                "INCLUDED_IN_CANONICAL_ARTICLE_UNCERTAINTY",

            "new_uncertainty_inference_performed":
                False,

            "semantic_equivalence_inference_performed":
                False,

            "numeric_probability_inference_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
                False,

            "semantic_memory_write_performed":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        })

        consolidated_candidates.append(
            consolidated
        )

    for redundant in redundant_candidates:

        if not isinstance(
            redundant,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every redundant candidate must be a mapping."
            )

        if (
            redundant.get(
                "duplicate_resolution_status"
            )
            != "REDUNDANT_EXACT_DUPLICATE"
        ):
            raise UncertaintyIntelligenceError(
                "Unexpected redundant candidate status."
            )

        canonical_id = str(
            redundant.get(
                "canonical_uncertainty_candidate_id"
            )
            or ""
        )

        if canonical_id not in seen_candidate_ids:
            raise UncertaintyIntelligenceError(
                "Redundant candidate references unknown canonical candidate."
            )

    consolidated_units = []
    consolidated_unit_by_id = {}

    for unit in source_units:

        unit_id = str(
            unit.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        )

        state = dict(
            unit.get(
                "uncertainty_analysis_state"
            )
            or {}
        )

        state[
            "article_uncertainty_consolidation"
        ] = "COMPLETE"

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        boundaries[
            "article_uncertainty_consolidation_performed"
        ] = True

        boundaries[
            "final_uncertainty_result_built"
        ] = False

        boundaries[
            "uncertainty_certification_performed"
        ] = False

        boundaries[
            "numeric_probability_inference_performed"
        ] = False

        boundaries[
            "unstated_uncertainty_inference_performed"
        ] = False

        boundaries[
            "truth_assessment_performed"
        ] = False

        boundaries[
            "external_authority_check_performed"
        ] = False

        boundaries[
            "semantic_memory_write_performed"
        ] = False

        boundaries[
            "persistence_performed"
        ] = False

        unit_candidates = [
            candidate
            for candidate in consolidated_candidates
            if candidate.get(
                "uncertainty_claim_unit_id"
            )
            == unit_id
        ]

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "uncertainty_candidates":
                unit_candidates,

            "canonical_uncertainty_candidate_count":
                len(
                    unit_candidates
                ),

            "article_uncertainty_consolidated":
                True,

            "uncertainty_analysis_state":
                state,

            "processing_boundaries":
                boundaries,
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
            "uncertainty_sections"
        )
        or []
    ):

        if not isinstance(
            section,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty section must be a mapping."
            )

        section_id = str(
            section.get(
                "section_id"
            )
            or ""
        )

        rebuilt_units = []

        for old_unit in (
            section.get(
                "uncertainty_claim_units"
            )
            or []
        ):

            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise UncertaintyIntelligenceError(
                    "Section Claim Unit reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "uncertainty_claim_unit_id"
                )
                or ""
            )

            resolved = consolidated_unit_by_id.get(
                unit_id
            )

            if resolved is None:
                raise UncertaintyIntelligenceError(
                    "Section references unknown Claim Unit."
                )

            rebuilt_units.append(
                resolved
            )

        section_candidates = [
            candidate
            for candidate in consolidated_candidates
            if (
                str(
                    candidate.get(
                        "section_id"
                    )
                    or ""
                )
                == section_id
            )
            or (
                str(
                    candidate.get(
                        "uncertainty_claim_unit_id"
                    )
                    or ""
                )
                in {
                    str(
                        unit.get(
                            "uncertainty_claim_unit_id"
                        )
                        or ""
                    )
                    for unit in rebuilt_units
                }
            )
        ]

        section_type_counts = {}

        for candidate in section_candidates:
            uncertainty_type = str(
                candidate.get(
                    "uncertainty_type"
                )
                or ""
            )

            if uncertainty_type:
                section_type_counts[
                    uncertainty_type
                ] = (
                    section_type_counts.get(
                        uncertainty_type,
                        0,
                    )
                    + 1
                )

        consolidated_sections.append({
            **dict(
                section
            ),

            "uncertainty_claim_units":
                rebuilt_units,

            "canonical_uncertainty_candidate_count":
                len(
                    section_candidates
                ),

            "uncertainty_type_counts":
                dict(
                    sorted(
                        section_type_counts.items()
                    )
                ),

            "article_uncertainty_consolidated":
                True,
        })

    result = dict(
        duplicate_resolution_result
    )

    result_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    result_boundaries[
        "article_uncertainty_consolidation_performed"
    ] = True

    result_boundaries[
        "final_uncertainty_result_built"
    ] = False

    result_boundaries[
        "uncertainty_certification_performed"
    ] = False

    result_boundaries[
        "numeric_probability_inference_performed"
    ] = False

    result_boundaries[
        "unstated_uncertainty_inference_performed"
    ] = False

    result_boundaries[
        "truth_assessment_performed"
    ] = False

    result_boundaries[
        "external_authority_check_performed"
    ] = False

    result_boundaries[
        "semantic_memory_write_performed"
    ] = False

    result_boundaries[
        "persistence_performed"
    ] = False

    article_identity = dict(
        duplicate_resolution_result.get(
            "article_identity"
        )
        or {}
    )

    result.update({
        "schema_version":
            "article_uncertainty_consolidation_v1",

        "patch":
            "4.6.14N",

        "status":
            "ARTICLE_UNCERTAINTY_CONSOLIDATION_COMPLETE",

        "article_identity":
            article_identity,

        "uncertainty_candidates":
            consolidated_candidates,

        "redundant_uncertainty_candidates":
            redundant_candidates,

        "uncertainty_claim_units":
            consolidated_units,

        "uncertainty_sections":
            consolidated_sections,

        "article_uncertainty_profile": {
            "article_id":
                article_identity.get(
                    "article_id"
                ),

            "canonical_uncertainty_candidate_count":
                len(
                    consolidated_candidates
                ),

            "redundant_candidate_count":
                len(
                    redundant_candidates
                ),

            "uncertainty_type_counts":
                dict(
                    sorted(
                        type_counts.items()
                    )
                ),

            "signal_type_counts":
                dict(
                    sorted(
                        signal_type_counts.items()
                    )
                ),

            "commitment_class_counts":
                dict(
                    sorted(
                        commitment_class_counts.items()
                    )
                ),

            "evidence_confidence_class_counts":
                dict(
                    sorted(
                        confidence_class_counts.items()
                    )
                ),

            "evidence_status_counts":
                dict(
                    sorted(
                        evidence_status_counts.items()
                    )
                ),

            "section_candidate_counts":
                dict(
                    sorted(
                        section_candidate_counts.items()
                    )
                ),

            "claim_unit_candidate_counts":
                dict(
                    sorted(
                        claim_unit_candidate_counts.items()
                    )
                ),

            "contains_explicit_uncertainty":
                bool(
                    consolidated_candidates
                ),

            "article_local_only":
                True,

            "exact_duplicates_excluded_from_profile":
                True,

            "semantic_equivalence_merging_performed":
                False,

            "new_uncertainty_inference_performed":
                False,

            "numeric_probability_inferred":
                False,

            "unified_semantic_confidence_calculated":
                False,

            "scientific_truth_assessed":
                False,

            "external_authority_checked":
                False,
        },

        "processing_boundaries":
            result_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "final_uncertainty_intelligence_result",
    })

    return result


def build_final_uncertainty_intelligence_result_v1(
    article_consolidation_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Build the canonical final Uncertainty Intelligence result.

    Stage O performs packaging/finalization only.

    It does NOT:
    - create new uncertainty candidates,
    - perform semantic-equivalence merging,
    - infer unstated uncertainty,
    - infer numeric probability,
    - calculate unified Semantic Confidence,
    - assess factual/scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence,
    - certify the layer.

    Layer certification belongs exclusively to Stage P.
    """

    if not isinstance(
        article_consolidation_result,
        Mapping,
    ):
        raise UncertaintyIntelligenceError(
            "article_consolidation_result must be a mapping."
        )

    if (
        article_consolidation_result.get("schema_version")
        != "article_uncertainty_consolidation_v1"
    ):
        raise UncertaintyIntelligenceError(
            "Stage O requires article_uncertainty_consolidation_v1."
        )

    if (
        article_consolidation_result.get("status")
        != "ARTICLE_UNCERTAINTY_CONSOLIDATION_COMPLETE"
    ):
        raise UncertaintyIntelligenceError(
            "Stage N must be complete before Stage O."
        )

    if article_consolidation_result.get("phase") != "4.6.14":
        raise UncertaintyIntelligenceError(
            "Stage O requires Phase 4.6.14 input."
        )

    if article_consolidation_result.get("patch") != "4.6.14N":
        raise UncertaintyIntelligenceError(
            "Stage O requires canonical 4.6.14N input."
        )

    if (
        article_consolidation_result.get("next_stage")
        != "final_uncertainty_intelligence_result"
    ):
        raise UncertaintyIntelligenceError(
            "Stage N must hand off to "
            "final_uncertainty_intelligence_result."
        )

    if (
        article_consolidation_result.get("persistence_policy")
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise UncertaintyIntelligenceError(
            "Uncertainty Intelligence must remain transient."
        )

    top_boundaries = dict(
        article_consolidation_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        top_boundaries.get(
            "article_uncertainty_consolidation_performed"
        )
        is not True
    ):
        raise UncertaintyIntelligenceError(
            "Stage-N consolidation boundary must be complete."
        )

    if (
        top_boundaries.get(
            "final_uncertainty_result_built"
        )
        is not False
    ):
        raise UncertaintyIntelligenceError(
            "Final Uncertainty result must be pending before Stage O."
        )

    article_identity = article_consolidation_result.get(
        "article_identity"
    )

    if not isinstance(article_identity, Mapping):
        raise UncertaintyIntelligenceError(
            "Canonical article_identity is required."
        )

    for key in (
        "article_id",
        "workspace_id",
        "source_type",
        "content_hash",
        "body_ref",
    ):
        if not str(article_identity.get(key) or ""):
            raise UncertaintyIntelligenceError(
                "Missing canonical article identity field: " + key
            )

    profile = article_consolidation_result.get(
        "article_uncertainty_profile"
    )

    if not isinstance(profile, Mapping):
        raise UncertaintyIntelligenceError(
            "Canonical article_uncertainty_profile is required."
        )

    canonical_candidates = list(
        article_consolidation_result.get(
            "uncertainty_candidates"
        )
        or []
    )

    redundant_candidates = list(
        article_consolidation_result.get(
            "redundant_uncertainty_candidates"
        )
        or []
    )

    claim_units = list(
        article_consolidation_result.get(
            "uncertainty_claim_units"
        )
        or []
    )

    sections = list(
        article_consolidation_result.get(
            "uncertainty_sections"
        )
        or []
    )

    expected_canonical_count = profile.get(
        "canonical_uncertainty_candidate_count"
    )

    expected_redundant_count = profile.get(
        "redundant_candidate_count"
    )

    if (
        not isinstance(expected_canonical_count, int)
        or expected_canonical_count < 0
        or expected_canonical_count != len(canonical_candidates)
    ):
        raise UncertaintyIntelligenceError(
            "Article profile canonical candidate count mismatch."
        )

    if (
        not isinstance(expected_redundant_count, int)
        or expected_redundant_count < 0
        or expected_redundant_count != len(redundant_candidates)
    ):
        raise UncertaintyIntelligenceError(
            "Article profile redundant candidate count mismatch."
        )

    canonical_ids = set()

    finalized_candidates = []

    for candidate in canonical_candidates:

        if not isinstance(candidate, Mapping):
            raise UncertaintyIntelligenceError(
                "Every canonical Uncertainty candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get("uncertainty_candidate_id")
            or ""
        )

        if not candidate_id:
            raise UncertaintyIntelligenceError(
                "Canonical Uncertainty Candidate ID is required."
            )

        if candidate_id in canonical_ids:
            raise UncertaintyIntelligenceError(
                "Duplicate canonical Uncertainty Candidate ID."
            )

        canonical_ids.add(candidate_id)

        if (
            candidate.get("duplicate_resolution_status")
            != "CANONICAL_UNIQUE_CANDIDATE"
        ):
            raise UncertaintyIntelligenceError(
                "Stage O accepts canonical candidates only."
            )

        if (
            candidate.get("article_uncertainty_consolidated")
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Candidate must be consolidated before Stage O."
            )

        if (
            candidate.get(
                "article_uncertainty_consolidation_status"
            )
            != "INCLUDED_IN_CANONICAL_ARTICLE_UNCERTAINTY"
        ):
            raise UncertaintyIntelligenceError(
                "Candidate consolidation status is invalid."
            )

        if (
            candidate.get("uncertainty_evidence_assessed")
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Candidate evidence must be assessed."
            )

        if (
            candidate.get("numeric_probability_inference_performed")
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Numeric probability inference is forbidden."
            )

        if (
            candidate.get("truth_assessment_performed")
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Truth assessment is forbidden."
            )

        finalized = dict(candidate)

        finalized.update({
            "final_uncertainty_result_included":
                True,

            "final_uncertainty_result_status":
                "INCLUDED",

            "uncertainty_intelligence_certified":
                False,

            "numeric_probability_inference_performed":
                False,

            "unified_semantic_confidence_calculated":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
                False,

            "semantic_memory_write_performed":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        })

        finalized_candidates.append(finalized)

    for redundant in redundant_candidates:

        if not isinstance(redundant, Mapping):
            raise UncertaintyIntelligenceError(
                "Every redundant candidate must be a mapping."
            )

        if (
            redundant.get("duplicate_resolution_status")
            != "REDUNDANT_EXACT_DUPLICATE"
        ):
            raise UncertaintyIntelligenceError(
                "Unexpected redundant candidate status."
            )

        canonical_id = str(
            redundant.get(
                "canonical_uncertainty_candidate_id"
            )
            or ""
        )

        if canonical_id not in canonical_ids:
            raise UncertaintyIntelligenceError(
                "Redundant candidate references unknown canonical candidate."
            )

    finalized_units = []
    finalized_unit_by_id = {}

    for unit in claim_units:

        if not isinstance(unit, Mapping):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get("uncertainty_claim_unit_id")
            or ""
        )

        if not unit_id:
            raise UncertaintyIntelligenceError(
                "Uncertainty Claim Unit ID is required."
            )

        if unit_id in finalized_unit_by_id:
            raise UncertaintyIntelligenceError(
                "Duplicate Uncertainty Claim Unit ID."
            )

        state = dict(
            unit.get("uncertainty_analysis_state")
            or {}
        )

        if (
            state.get("article_uncertainty_consolidation")
            != "COMPLETE"
        ):
            raise UncertaintyIntelligenceError(
                "Article uncertainty consolidation must be COMPLETE."
            )

        boundaries = dict(
            unit.get("processing_boundaries")
            or {}
        )

        if (
            boundaries.get(
                "article_uncertainty_consolidation_performed"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Unit Stage-N boundary must be True."
            )

        state[
            "final_uncertainty_intelligence_result"
        ] = "COMPLETE"

        state[
            "uncertainty_intelligence_certification"
        ] = "PENDING"

        boundaries[
            "final_uncertainty_result_built"
        ] = True

        boundaries[
            "uncertainty_intelligence_certification_performed"
        ] = False

        boundaries[
            "numeric_probability_inference_performed"
        ] = False

        boundaries[
            "truth_assessment_performed"
        ] = False

        boundaries[
            "external_authority_check_performed"
        ] = False

        boundaries[
            "semantic_memory_write_performed"
        ] = False

        boundaries[
            "persistence_performed"
        ] = False

        updated_unit = dict(unit)

        unit_candidates = [
            candidate
            for candidate in finalized_candidates
            if candidate.get(
                "uncertainty_claim_unit_id"
            )
            == unit_id
        ]

        updated_unit.update({
            "uncertainty_candidates":
                unit_candidates,

            "final_uncertainty_candidate_count":
                len(unit_candidates),

            "uncertainty_analysis_state":
                state,

            "processing_boundaries":
                boundaries,
        })

        finalized_units.append(updated_unit)

        finalized_unit_by_id[
            unit_id
        ] = updated_unit

    finalized_sections = []

    for section in sections:

        if not isinstance(section, Mapping):
            raise UncertaintyIntelligenceError(
                "Every Uncertainty section must be a mapping."
            )

        rebuilt_units = []

        for old_unit in (
            section.get("uncertainty_claim_units")
            or []
        ):

            if not isinstance(old_unit, Mapping):
                raise UncertaintyIntelligenceError(
                    "Section Claim Unit reference must be a mapping."
                )

            unit_id = str(
                old_unit.get("uncertainty_claim_unit_id")
                or ""
            )

            resolved = finalized_unit_by_id.get(unit_id)

            if resolved is None:
                raise UncertaintyIntelligenceError(
                    "Section references unknown Claim Unit."
                )

            rebuilt_units.append(resolved)

        finalized_sections.append({
            **dict(section),

            "uncertainty_claim_units":
                rebuilt_units,

            "final_uncertainty_candidate_count":
                sum(
                    int(
                        unit.get(
                            "final_uncertainty_candidate_count"
                        )
                        or 0
                    )
                    for unit in rebuilt_units
                ),
        })

    result = dict(
        article_consolidation_result
    )

    result_boundaries = dict(
        result.get("processing_boundaries")
        or {}
    )

    result_boundaries[
        "final_uncertainty_result_built"
    ] = True

    result_boundaries[
        "uncertainty_intelligence_certification_performed"
    ] = False

    result_boundaries[
        "numeric_probability_inference_performed"
    ] = False

    result_boundaries[
        "truth_assessment_performed"
    ] = False

    result_boundaries[
        "external_authority_check_performed"
    ] = False

    result_boundaries[
        "semantic_memory_write_performed"
    ] = False

    result_boundaries[
        "persistence_performed"
    ] = False

    result.update({
        "schema_version":
            "uncertainty_intelligence_result_v1",

        "uncertainty_intelligence_version":
            "uncertainty_intelligence_v1",

        "phase":
            "4.6.14",

        "patch":
            "4.6.14O",

        "status":
            "UNCERTAINTY_INTELLIGENCE_RESULT_BUILT",

        "article_identity":
            dict(article_identity),

        "article_uncertainty_profile":
            dict(profile),

        "uncertainty_candidates":
            finalized_candidates,

        "redundant_uncertainty_candidates":
            redundant_candidates,

        "uncertainty_claim_units":
            finalized_units,

        "uncertainty_sections":
            finalized_sections,

        "final_uncertainty_summary": {
            "canonical_candidate_count":
                len(finalized_candidates),

            "redundant_candidate_count":
                len(redundant_candidates),

            "contains_explicit_uncertainty":
                bool(
                    profile.get(
                        "contains_explicit_uncertainty"
                    )
                ),

            "uncertainty_type_counts":
                dict(
                    profile.get(
                        "uncertainty_type_counts"
                    )
                    or {}
                ),

            "section_candidate_counts":
                dict(
                    profile.get(
                        "section_candidate_counts"
                    )
                    or {}
                ),

            "exact_duplicates_excluded":
                True,

            "new_uncertainty_inference_performed":
                False,

            "semantic_equivalence_merging_performed":
                False,

            "numeric_probability_inferred":
                False,

            "unified_semantic_confidence_calculated":
                False,

            "scientific_truth_assessed":
                False,

            "external_authority_checked":
                False,

            "semantic_memory_written":
                False,

            "persistence_performed":
                False,

            "uncertainty_intelligence_certified":
                False,
        },

        "processing_boundaries":
            result_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "uncertainty_intelligence_certification",
    })

    return result


def certify_uncertainty_intelligence_v1(
    final_uncertainty_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Final certification gate for Phase 4.6.14 Uncertainty Intelligence.

    Certification validates the final article-local result and closes
    the layer for downstream Semantic Intelligence consumption.

    Certification does NOT:
    - create or reinterpret uncertainty,
    - infer numeric probability,
    - calculate unified Semantic Confidence,
    - assess truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        final_uncertainty_result,
        Mapping,
    ):
        raise UncertaintyIntelligenceError(
            "final_uncertainty_result must be a mapping."
        )

    if (
        final_uncertainty_result.get(
            "schema_version"
        )
        != "uncertainty_intelligence_result_v1"
    ):
        raise UncertaintyIntelligenceError(
            "Certification requires uncertainty_intelligence_result_v1."
        )

    if (
        final_uncertainty_result.get(
            "status"
        )
        != "UNCERTAINTY_INTELLIGENCE_RESULT_BUILT"
    ):
        raise UncertaintyIntelligenceError(
            "Final Uncertainty Intelligence result must be built."
        )

    if (
        final_uncertainty_result.get(
            "phase"
        )
        != "4.6.14"
    ):
        raise UncertaintyIntelligenceError(
            "Certification requires Phase 4.6.14."
        )

    if (
        final_uncertainty_result.get(
            "patch"
        )
        != "4.6.14O"
    ):
        raise UncertaintyIntelligenceError(
            "Certification requires canonical Stage 4.6.14O."
        )

    if (
        final_uncertainty_result.get(
            "next_stage"
        )
        != "uncertainty_intelligence_certification"
    ):
        raise UncertaintyIntelligenceError(
            "Stage O must hand off to "
            "uncertainty_intelligence_certification."
        )

    if (
        final_uncertainty_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise UncertaintyIntelligenceError(
            "Uncertainty Intelligence must remain transient."
        )

    article_identity = dict(
        final_uncertainty_result.get(
            "article_identity"
        )
        or {}
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
        ):
            raise UncertaintyIntelligenceError(
                "Final Uncertainty Intelligence article identity "
                "is missing "
                + field_name
                + "."
            )

    profile = final_uncertainty_result.get(
        "article_uncertainty_profile"
    )

    if not isinstance(
        profile,
        Mapping,
    ):
        raise UncertaintyIntelligenceError(
            "Article Uncertainty profile must be a mapping."
        )

    canonical_candidates = list(
        final_uncertainty_result.get(
            "uncertainty_candidates"
        )
        or []
    )

    redundant_candidates = list(
        final_uncertainty_result.get(
            "redundant_uncertainty_candidates"
        )
        or []
    )

    units = list(
        final_uncertainty_result.get(
            "uncertainty_claim_units"
        )
        or []
    )

    sections = list(
        final_uncertainty_result.get(
            "uncertainty_sections"
        )
        or []
    )

    expected_canonical_count = profile.get(
        "canonical_uncertainty_candidate_count"
    )

    expected_redundant_count = profile.get(
        "redundant_candidate_count"
    )

    if (
        not isinstance(
            expected_canonical_count,
            int,
        )
        or expected_canonical_count < 0
    ):
        raise UncertaintyIntelligenceError(
            "Profile canonical candidate count is invalid."
        )

    if (
        not isinstance(
            expected_redundant_count,
            int,
        )
        or expected_redundant_count < 0
    ):
        raise UncertaintyIntelligenceError(
            "Profile redundant candidate count is invalid."
        )

    if (
        expected_canonical_count
        != len(
            canonical_candidates
        )
    ):
        raise UncertaintyIntelligenceError(
            "Canonical candidate count does not match profile."
        )

    if (
        expected_redundant_count
        != len(
            redundant_candidates
        )
    ):
        raise UncertaintyIntelligenceError(
            "Redundant candidate count does not match profile."
        )

    top_boundaries = dict(
        final_uncertainty_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        top_boundaries.get(
            "article_uncertainty_consolidation_performed"
        )
        is not True
    ):
        raise UncertaintyIntelligenceError(
            "Article Uncertainty consolidation must be complete."
        )

    if (
        top_boundaries.get(
            "final_uncertainty_result_built"
        )
        is not True
    ):
        raise UncertaintyIntelligenceError(
            "Final Uncertainty result boundary must be complete."
        )

    if (
        top_boundaries.get(
            "uncertainty_intelligence_certification_performed"
        )
        is not False
    ):
        raise UncertaintyIntelligenceError(
            "Uncertainty certification must be pending."
        )

    forbidden_true_top_boundaries = (
        "numeric_probability_inference_performed",
        "unstated_uncertainty_inference_performed",
        "truth_assessment_performed",
        "external_authority_check_performed",
        "semantic_memory_write_performed",
        "linking_decisions_performed",
        "persistence_performed",
    )

    for boundary_name in forbidden_true_top_boundaries:
        if (
            top_boundaries.get(
                boundary_name
            )
            is True
        ):
            raise UncertaintyIntelligenceError(
                boundary_name
                + " must remain False."
            )

    required_unit_states = (
        "uncertainty_signal_interpretation",
        "uncertainty_candidate_extraction",
        "uncertainty_scope_target_grounding",
        "uncertainty_type_classification",
        "explicitness_strength_validation",
        "same_sentence_uncertainty_validation",
        "cross_sentence_uncertainty_anchoring",
        "uncertainty_evidence_assessment",
        "duplicate_uncertainty_resolution",
        "article_uncertainty_consolidation",
        "final_uncertainty_intelligence_result",
    )

    seen_unit_ids = set()

    certified_units = []

    for unit in units:

        if not isinstance(
            unit,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every final Uncertainty Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise UncertaintyIntelligenceError(
                "Final Uncertainty Claim Unit ID is required."
            )

        if unit_id in seen_unit_ids:
            raise UncertaintyIntelligenceError(
                "Duplicate final Uncertainty Claim Unit ID."
            )

        seen_unit_ids.add(
            unit_id
        )

        state = dict(
            unit.get(
                "uncertainty_analysis_state"
            )
            or {}
        )

        for state_name in required_unit_states:
            if (
                state.get(
                    state_name
                )
                != "COMPLETE"
            ):
                raise UncertaintyIntelligenceError(
                    "Final Claim Unit stage is not COMPLETE: "
                    + state_name
                )

        if (
            state.get(
                "uncertainty_intelligence_certification"
            )
            != "PENDING"
        ):
            raise UncertaintyIntelligenceError(
                "Unit certification state must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "final_uncertainty_result_built"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Unit final result boundary must be True."
            )

        if (
            boundaries.get(
                "uncertainty_intelligence_certification_performed"
            )
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Unit certification boundary must be False before P."
            )

        forbidden_unit_boundaries = (
            "numeric_probability_inference_performed",
            "unstated_uncertainty_inference_performed",
            "truth_assessment_performed",
            "external_authority_check_performed",
            "semantic_memory_write_performed",
            "linking_decisions_performed",
            "persistence_performed",
        )

        for boundary_name in forbidden_unit_boundaries:
            if (
                boundaries.get(
                    boundary_name
                )
                is True
            ):
                raise UncertaintyIntelligenceError(
                    "Forbidden Unit boundary became True: "
                    + boundary_name
                )

        certified_state = dict(
            state
        )

        certified_state[
            "uncertainty_intelligence_certification"
        ] = "COMPLETE"

        certified_boundaries = dict(
            boundaries
        )

        certified_boundaries[
            "uncertainty_intelligence_certification_performed"
        ] = True

        certified_boundaries[
            "numeric_probability_inference_performed"
        ] = False

        certified_boundaries[
            "unstated_uncertainty_inference_performed"
        ] = False

        certified_boundaries[
            "truth_assessment_performed"
        ] = False

        certified_boundaries[
            "external_authority_check_performed"
        ] = False

        certified_boundaries[
            "semantic_memory_write_performed"
        ] = False

        certified_boundaries[
            "linking_decisions_performed"
        ] = False

        certified_boundaries[
            "persistence_performed"
        ] = False

        certified_unit = dict(
            unit
        )

        certified_unit.update({
            "uncertainty_intelligence_certified":
                True,

            "uncertainty_intelligence_certification_status":
                "CERTIFIED",

            "uncertainty_analysis_state":
                certified_state,

            "processing_boundaries":
                certified_boundaries,
        })

        certified_units.append(
            certified_unit
        )

    seen_candidate_ids = set()

    certified_candidates = []

    for candidate in canonical_candidates:

        if not isinstance(
            candidate,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every final canonical candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "uncertainty_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise UncertaintyIntelligenceError(
                "Final canonical candidate ID is required."
            )

        if candidate_id in seen_candidate_ids:
            raise UncertaintyIntelligenceError(
                "Duplicate final canonical candidate ID."
            )

        seen_candidate_ids.add(
            candidate_id
        )

        if (
            candidate.get(
                "duplicate_resolution_status"
            )
            != "CANONICAL_UNIQUE_CANDIDATE"
        ):
            raise UncertaintyIntelligenceError(
                "Final candidate must be canonical unique."
            )

        if (
            candidate.get(
                "article_uncertainty_consolidated"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Final candidate must be article-consolidated."
            )

        if (
            candidate.get(
                "final_uncertainty_result_included"
            )
            is not True
        ):
            raise UncertaintyIntelligenceError(
                "Final candidate must be included in Stage O result."
            )

        if (
            candidate.get(
                "final_uncertainty_result_status"
            )
            != "INCLUDED"
        ):
            raise UncertaintyIntelligenceError(
                "Final candidate Stage-O status must be INCLUDED."
            )

        if (
            candidate.get(
                "uncertainty_intelligence_certified"
            )
            is not False
        ):
            raise UncertaintyIntelligenceError(
                "Candidate must not already be certified before Stage P."
            )

        candidate_unit_id = str(
            candidate.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        )

        if candidate_unit_id not in seen_unit_ids:
            raise UncertaintyIntelligenceError(
                "Canonical candidate references unknown final Claim Unit."
            )

        forbidden_candidate_flags = (
            "numeric_probability_inference_performed",
            "unstated_uncertainty_inference_performed",
            "truth_assessment_performed",
            "external_authority_check_performed",
            "semantic_memory_write_performed",
            "linking_decisions_performed",
            "persistence_performed",
        )

        for flag_name in forbidden_candidate_flags:
            if (
                candidate.get(
                    flag_name
                )
                is True
            ):
                raise UncertaintyIntelligenceError(
                    "Forbidden final candidate flag became True: "
                    + flag_name
                )

        certified_candidate = dict(
            candidate
        )

        certified_candidate.update({
            "uncertainty_intelligence_certified":
                True,

            "uncertainty_intelligence_certification_status":
                "CERTIFIED",

            "uncertainty_intelligence_certification_stage":
                "4.6.14P",

            "numeric_probability_inference_performed":
                False,

            "unstated_uncertainty_inference_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
                False,

            "semantic_memory_write_performed":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        })

        certified_candidates.append(
            certified_candidate
        )

    for redundant in redundant_candidates:

        if not isinstance(
            redundant,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every redundant candidate must be a mapping."
            )

        if (
            redundant.get(
                "duplicate_resolution_status"
            )
            != "REDUNDANT_EXACT_DUPLICATE"
        ):
            raise UncertaintyIntelligenceError(
                "Unexpected redundant candidate status."
            )

        canonical_id = str(
            redundant.get(
                "canonical_uncertainty_candidate_id"
            )
            or ""
        )

        if canonical_id not in seen_candidate_ids:
            raise UncertaintyIntelligenceError(
                "Redundant candidate references unknown canonical candidate."
            )

    certified_unit_by_id = {
        str(
            unit.get(
                "uncertainty_claim_unit_id"
            )
            or ""
        ):
            unit
        for unit in certified_units
    }

    certified_sections = []

    for section in sections:

        if not isinstance(
            section,
            Mapping,
        ):
            raise UncertaintyIntelligenceError(
                "Every final Uncertainty section must be a mapping."
            )

        rebuilt_units = []

        for old_unit in (
            section.get(
                "uncertainty_claim_units"
            )
            or []
        ):

            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise UncertaintyIntelligenceError(
                    "Section Claim Unit reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "uncertainty_claim_unit_id"
                )
                or ""
            )

            resolved = certified_unit_by_id.get(
                unit_id
            )

            if resolved is None:
                raise UncertaintyIntelligenceError(
                    "Section references unknown certified Claim Unit."
                )

            rebuilt_units.append(
                resolved
            )

        certified_sections.append({
            **dict(
                section
            ),

            "uncertainty_claim_units":
                rebuilt_units,

            "uncertainty_intelligence_certified":
                True,
        })

    certified_profile = dict(
        profile
    )

    certified_profile.update({
        "uncertainty_intelligence_certified":
            True,

        "uncertainty_intelligence_certification_stage":
            "4.6.14P",

        "numeric_probability_inferred":
            False,

        "unified_semantic_confidence_calculated":
            False,

        "scientific_truth_assessed":
            False,

        "external_authority_checked":
            False,

        "semantic_memory_written":
            False,

        "persistence_performed":
            False,
    })

    final_summary = dict(
        final_uncertainty_result.get(
            "final_uncertainty_summary"
        )
        or {}
    )

    final_summary.update({
        "uncertainty_intelligence_certified":
            True,

        "certification_stage":
            "4.6.14P",

        "certification_status":
            "CERTIFIED",

        "canonical_candidate_count":
            len(
                certified_candidates
            ),

        "redundant_candidate_count":
            len(
                redundant_candidates
            ),

        "numeric_probability_inferred":
            False,

        "unified_semantic_confidence_calculated":
            False,

        "scientific_truth_assessed":
            False,

        "external_authority_checked":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,

        "persistence_performed":
            False,
    })

    certified_boundaries = dict(
        top_boundaries
    )

    certified_boundaries[
        "uncertainty_intelligence_certification_performed"
    ] = True

    certified_boundaries[
        "numeric_probability_inference_performed"
    ] = False

    certified_boundaries[
        "unstated_uncertainty_inference_performed"
    ] = False

    certified_boundaries[
        "truth_assessment_performed"
    ] = False

    certified_boundaries[
        "external_authority_check_performed"
    ] = False

    certified_boundaries[
        "semantic_memory_write_performed"
    ] = False

    certified_boundaries[
        "linking_decisions_performed"
    ] = False

    certified_boundaries[
        "persistence_performed"
    ] = False

    result = dict(
        final_uncertainty_result
    )

    result.update({
        "schema_version":
            "uncertainty_intelligence_result_v1",

        "uncertainty_intelligence_version":
            "uncertainty_intelligence_v1",

        "phase":
            "4.6.14",

        "patch":
            "4.6.14P",

        "status":
            "UNCERTAINTY_INTELLIGENCE_CERTIFIED",

        "article_identity":
            article_identity,

        "article_uncertainty_profile":
            certified_profile,

        "uncertainty_candidates":
            certified_candidates,

        "redundant_uncertainty_candidates":
            redundant_candidates,

        "uncertainty_claim_units":
            certified_units,

        "uncertainty_sections":
            certified_sections,

        "final_uncertainty_summary":
            final_summary,

        "certification": {
            "performed":
                True,

            "certified":
                True,

            "stage":
                "4.6.14P",

            "status":
                "CERTIFIED",

            "certification_scope":
                "FULL_UNCERTAINTY_INTELLIGENCE_LAYER",

            "article_local_only":
                True,

            "canonical_candidates_only":
                True,

            "exact_duplicates_excluded":
                True,

            "numeric_probability_inferred":
                False,

            "unified_semantic_confidence_calculated":
                False,

            "scientific_truth_assessed":
                False,

            "external_authority_checked":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "processing_boundaries":
            certified_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "symbolic_neural_hybrid_intelligence",
    })

    return result
