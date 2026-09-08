from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class AnalogicalIntelligenceError(ValueError):
    """Raised when Analogical Intelligence receives invalid input."""


def validate_analogical_intelligence_intake_v1(
    certified_procedural_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate the certified Phase 4.6.10 Procedural Intelligence result
    before Phase 4.6.11 Analogical Intelligence begins.

    This stage performs intake validation only.

    It does NOT:
    - identify analogies,
    - select an analogy source or target,
    - infer conceptual correspondences,
    - perform generic similarity reasoning,
    - invent analogy mappings,
    - extend an article-expressed analogy,
    - redo procedural reasoning,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - perform new causal reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        certified_procedural_result,
        Mapping,
    ):
        raise AnalogicalIntelligenceError(
            "certified_procedural_result must be a mapping."
        )

    if (
        certified_procedural_result.get(
            "schema_version"
        )
        != "certified_procedural_intelligence_result_v1"
    ):
        raise AnalogicalIntelligenceError(
            "Phase 4.6.11 requires certified_procedural_intelligence_result_v1."
        )

    if (
        certified_procedural_result.get(
            "status"
        )
        != "PROCEDURAL_INTELLIGENCE_CERTIFIED"
    ):
        raise AnalogicalIntelligenceError(
            "Procedural Intelligence must be certified before Analogical Intelligence."
        )

    if (
        certified_procedural_result.get(
            "phase"
        )
        != "4.6.10"
    ):
        raise AnalogicalIntelligenceError(
            "Phase 4.6.11 requires certified Phase 4.6.10 input."
        )

    if (
        certified_procedural_result.get(
            "patch"
        )
        != "4.6.10O"
    ):
        raise AnalogicalIntelligenceError(
            "Phase 4.6.11 requires canonical 4.6.10O input."
        )

    if (
        certified_procedural_result.get(
            "next_stage"
        )
        != "analogical_intelligence"
    ):
        raise AnalogicalIntelligenceError(
            "Certified Procedural Intelligence must hand off to analogical_intelligence."
        )

    if (
        certified_procedural_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise AnalogicalIntelligenceError(
            "Analogical Intelligence intake must remain article-local and transient."
        )

    certification = dict(
        certified_procedural_result.get(
            "certification"
        )
        or {}
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
        != "4.6.10O"
        or certification.get(
            "certification_scope"
        )
        != "ARTICLE_LOCAL_PROCEDURAL_INTELLIGENCE"
    ):
        raise AnalogicalIntelligenceError(
            "Certified Procedural Intelligence certification envelope is invalid."
        )

    required_true_certification_fields = (
        "structural_integrity_verified",
        "candidate_accounting_verified",
        "representative_procedural_integrity_verified",
        "provenance_preserved",
        "procedural_action_integrity_verified",
        "procedural_role_integrity_verified",
        "procedural_form_integrity_verified",
        "grounding_integrity_verified",
        "evidence_strength_integrity_verified",
        "contextual_ambiguity_strength_cap_verified",
        "multiple_grounding_strength_cap_verified",
        "cross_sentence_strength_cap_verified",
        "boundary_integrity_verified",
    )

    for field_name in required_true_certification_fields:
        if (
            certification.get(
                field_name
            )
            is not True
        ):
            raise AnalogicalIntelligenceError(
                "Required Procedural Intelligence certification field is not verified: "
                + field_name
            )

    required_false_certification_fields = (
        "scientific_truth_verified",
        "truth_assessment_performed",
        "external_authority_check_performed",
        "new_procedural_expression_inference_performed",
        "procedural_step_ordering_performed",
        "procedural_prerequisite_inference_performed",
        "missing_step_inference_performed",
        "procedural_evidence_strengthening_performed",
        "quantitative_reasoning_performed",
        "temporal_reasoning_performed",
        "new_causal_reasoning_performed",
        "semantic_memory_write_performed",
        "persistence_performed",
    )

    for field_name in required_false_certification_fields:
        if (
            certification.get(
                field_name
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Procedural certification boundary must remain False: "
                + field_name
            )

    processing_boundaries = dict(
        certified_procedural_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        processing_boundaries.get(
            "procedural_certification_performed"
        )
        is not True
    ):
        raise AnalogicalIntelligenceError(
            "Procedural certification processing boundary must be complete."
        )

    if (
        processing_boundaries.get(
            "procedural_intelligence_certified"
        )
        is not True
    ):
        raise AnalogicalIntelligenceError(
            "Procedural Intelligence must be marked certified."
        )

    procedural_boundaries = dict(
        certified_procedural_result.get(
            "procedural_boundaries"
        )
        or {}
    )

    if (
        procedural_boundaries.get(
            "article_local_only"
        )
        is not True
    ):
        raise AnalogicalIntelligenceError(
            "Certified Procedural Intelligence must remain article-local."
        )

    required_false_procedural_boundaries = (
        "scientific_truth_verified",
        "truth_assessment_performed",
        "external_authority_checked",
        "new_procedural_expression_inference_performed",
        "procedural_step_ordering_performed",
        "procedural_prerequisite_inference_performed",
        "missing_step_inference_performed",
        "final_procedural_participant_selection_performed",
        "procedural_evidence_strengthening_performed",
        "quantitative_reasoning_performed",
        "temporal_reasoning_performed",
        "new_causal_reasoning_performed",
        "fuzzy_similarity_performed",
        "linking_decisions_performed",
        "semantic_memory_write_performed",
        "persistence_performed",
    )

    for field_name in required_false_procedural_boundaries:
        if (
            procedural_boundaries.get(
                field_name
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Certified procedural boundary must remain False: "
                + field_name
            )

    article_identity = dict(
        certified_procedural_result.get(
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
        ).strip():
            raise AnalogicalIntelligenceError(
                "Required article identity field missing: "
                + field_name
            )

    return {
        "schema_version":
            "analogical_intelligence_intake_v1",

        "analogical_intelligence_version":
            "analogical_intelligence_v1",

        "phase":
            "4.6.11",

        "patch":
            "4.6.11B",

        "status":
            "ANALOGICAL_INTELLIGENCE_INTAKE_VALIDATED",

        "article_identity":
            article_identity,

        "certified_procedural_result":
            dict(
                certified_procedural_result
            ),

        "intake_validation": {
            "certified_procedural_schema_verified":
                True,

            "certified_procedural_status_verified":
                True,

            "certified_procedural_patch_verified":
                True,

            "procedural_certification_verified":
                True,

            "procedural_boundary_integrity_verified":
                True,

            "article_identity_verified":
                True,

            "analogical_reasoning_not_preperformed":
                True,

            "article_local_only":
                True,
        },

        "processing_boundaries": {
            "analogical_intake_validation_performed":
                True,

            "analogical_claim_unit_preparation_performed":
                False,

            "analogical_signal_interpretation_performed":
                False,

            "analogical_candidate_extraction_performed":
                False,

            "analogy_source_target_selection_performed":
                False,

            "analogical_correspondence_mapping_performed":
                False,

            "analogy_extension_performed":
                False,

            "generic_similarity_reasoning_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
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
            "analogical_claim_unit_preparation",
    }



def build_analogical_claim_units_v1(
    certified_procedural_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Build canonical Phase 4.6.11 Analogical Claim Units from
    certified Phase 4.6.10 Procedural Intelligence.

    This is a one-to-one structural preparation stage.

    It does NOT:
    - reparse the article body,
    - identify analogical signals,
    - determine whether a comparison is an analogy,
    - select an analogy source or target,
    - infer conceptual correspondences,
    - extend an article-expressed analogy,
    - perform generic similarity reasoning,
    - redo procedural reasoning,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - perform new causal reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    intake = validate_analogical_intelligence_intake_v1(
        certified_procedural_result
    )

    if (
        intake.get(
            "status"
        )
        != "ANALOGICAL_INTELLIGENCE_INTAKE_VALIDATED"
    ):
        raise AnalogicalIntelligenceError(
            "Canonical Analogical Intelligence intake was not validated."
        )

    identity = dict(
        certified_procedural_result.get(
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

    procedural_units = list(
        certified_procedural_result.get(
            "procedural_claim_units"
        )
        or []
    )

    if not article_id:
        raise AnalogicalIntelligenceError(
            "Certified procedural article_id is required."
        )

    analogical_units = []
    analogical_sections = []

    seen_analogical_ids = set()
    seen_procedural_ids = set()
    seen_statement_ids = set()
    seen_sentence_ids = set()

    previous_global_index = None

    units_by_section = {}
    section_metadata = {}

    for procedural_unit in procedural_units:
        if not isinstance(
            procedural_unit,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every certified Procedural Claim Unit must be a mapping."
            )

        procedural_claim_unit_id = str(
            procedural_unit.get(
                "procedural_claim_unit_id"
            )
            or ""
        )

        statement_id = str(
            procedural_unit.get(
                "statement_evidence_id"
            )
            or ""
        )

        sentence_id = str(
            procedural_unit.get(
                "sentence_id"
            )
            or ""
        )

        section_id = str(
            procedural_unit.get(
                "section_id"
            )
            or ""
        )

        if not procedural_claim_unit_id:
            raise AnalogicalIntelligenceError(
                "Procedural Claim Unit ID is required."
            )

        if not procedural_claim_unit_id.startswith(
            "procedural_claim_"
        ):
            raise AnalogicalIntelligenceError(
                "Unexpected Procedural Claim Unit ID format."
            )

        if not statement_id:
            raise AnalogicalIntelligenceError(
                "statement_evidence_id is required."
            )

        if not sentence_id:
            raise AnalogicalIntelligenceError(
                "sentence_id is required."
            )

        if not section_id:
            raise AnalogicalIntelligenceError(
                "section_id is required."
            )

        if procedural_claim_unit_id in seen_procedural_ids:
            raise AnalogicalIntelligenceError(
                "Duplicate Procedural Claim Unit ID."
            )

        if statement_id in seen_statement_ids:
            raise AnalogicalIntelligenceError(
                "Duplicate statement_evidence_id."
            )

        if sentence_id in seen_sentence_ids:
            raise AnalogicalIntelligenceError(
                "Duplicate sentence_id."
            )

        if (
            procedural_unit.get(
                "article_id"
            )
            != article_id
        ):
            raise AnalogicalIntelligenceError(
                "Procedural Claim Unit article identity mismatch."
            )

        global_index = procedural_unit.get(
            "sentence_global_index"
        )

        article_position = procedural_unit.get(
            "article_position"
        )

        if not isinstance(
            global_index,
            int,
        ):
            raise AnalogicalIntelligenceError(
                "sentence_global_index must be an integer."
            )

        if not isinstance(
            article_position,
            int,
        ):
            raise AnalogicalIntelligenceError(
                "article_position must be an integer."
            )

        if (
            previous_global_index is not None
            and global_index <= previous_global_index
        ):
            raise AnalogicalIntelligenceError(
                "Certified Procedural Claim Units are not "
                "in canonical sentence order."
            )

        procedural_state = dict(
            procedural_unit.get(
                "procedural_analysis_state"
            )
            or {}
        )

        required_complete_procedural_stages = (
            "procedural_signal_interpretation",
            "procedural_candidate_extraction",
            "entity_concept_grounding",
            "procedural_action_normalization",
            "procedure_role_orientation",
            "same_sentence_procedural_validation",
            "cross_sentence_procedural_validation",
            "procedural_evidence_assessment",
            "duplicate_procedural_resolution",
        )

        for stage_name in required_complete_procedural_stages:
            if (
                procedural_state.get(
                    stage_name
                )
                != "COMPLETE"
            ):
                raise AnalogicalIntelligenceError(
                    "Procedural Claim Unit analysis is incomplete at "
                    + stage_name
                    + "."
                )

        upstream_boundaries = dict(
            procedural_unit.get(
                "processing_boundaries"
            )
            or {}
        )

        required_false_upstream_boundaries = (
            "procedural_step_ordering_performed",
            "procedural_prerequisite_inference_performed",
            "missing_step_inference_performed",
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
                raise AnalogicalIntelligenceError(
                    "Upstream Procedural Claim Unit boundary must remain False: "
                    + boundary_name
                )

        analogical_claim_unit_id = (
            "analogical_claim_"
            + procedural_claim_unit_id[
                len("procedural_claim_"):
            ]
        )

        if analogical_claim_unit_id in seen_analogical_ids:
            raise AnalogicalIntelligenceError(
                "Duplicate Analogical Claim Unit ID."
            )

        analogical_unit = {
            "analogical_claim_unit_id":
                analogical_claim_unit_id,

            "upstream_procedural_claim_unit_id":
                procedural_claim_unit_id,

            "upstream_quantitative_claim_unit_id":
                procedural_unit.get(
                    "upstream_quantitative_claim_unit_id"
                ),

            "upstream_causal_claim_unit_id":
                procedural_unit.get(
                    "upstream_causal_claim_unit_id"
                ),

            "upstream_relational_claim_unit_id":
                procedural_unit.get(
                    "upstream_relational_claim_unit_id"
                ),

            "upstream_logical_claim_unit_id":
                procedural_unit.get(
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
                procedural_unit.get(
                    "section_evidence_unit_id"
                ),

            "section_index":
                procedural_unit.get(
                    "section_index"
                ),

            "section_title":
                procedural_unit.get(
                    "section_title"
                ),

            "heading_level":
                procedural_unit.get(
                    "heading_level"
                ),

            "block_id":
                procedural_unit.get(
                    "block_id"
                ),

            "paragraph_id":
                procedural_unit.get(
                    "paragraph_id"
                ),

            "block_type":
                procedural_unit.get(
                    "block_type"
                ),

            "block_index":
                procedural_unit.get(
                    "block_index"
                ),

            "sentence_index":
                procedural_unit.get(
                    "sentence_index"
                ),

            "sentence_global_index":
                global_index,

            "article_position":
                article_position,

            "claim_index_in_section":
                procedural_unit.get(
                    "claim_index_in_section"
                ),

            "text":
                procedural_unit.get(
                    "text"
                ),

            "word_count":
                procedural_unit.get(
                    "word_count"
                ),

            "character_count":
                procedural_unit.get(
                    "character_count"
                ),

            "statement_form":
                procedural_unit.get(
                    "statement_form"
                ),

            "canonical_claim_candidate":
                procedural_unit.get(
                    "canonical_claim_candidate"
                )
                is True,

            "evidence_context":
                dict(
                    procedural_unit.get(
                        "evidence_context"
                    )
                    or {}
                ),

            "upstream_procedural_analysis_state":
                procedural_state,

            "upstream_procedural_processing_boundaries":
                upstream_boundaries,

            "analogical_analysis_state": {
                "analogical_signal_interpretation":
                    "PENDING",

                "analogical_candidate_extraction":
                    "PENDING",

                "entity_concept_grounding":
                    "PENDING",

                "analogy_source_target_orientation":
                    "PENDING",

                "analogical_correspondence_validation":
                    "PENDING",

                "same_sentence_analogical_validation":
                    "PENDING",

                "cross_sentence_analogical_validation":
                    "PENDING",

                "analogical_evidence_assessment":
                    "PENDING",

                "duplicate_analogical_resolution":
                    "PENDING",
            },

            "processing_boundaries": {
                "article_local_only":
                    True,

                "analogical_claim_unit_prepared":
                    True,

                "article_body_reparsed":
                    False,

                "analogical_signal_interpretation_performed":
                    False,

                "analogical_candidate_extraction_performed":
                    False,

                "analogy_source_target_selection_performed":
                    False,

                "analogical_correspondence_mapping_performed":
                    False,

                "analogy_extension_performed":
                    False,

                "generic_similarity_reasoning_performed":
                    False,

                "procedural_reasoning_performed":
                    False,

                "quantitative_reasoning_performed":
                    False,

                "temporal_reasoning_performed":
                    False,

                "new_causal_reasoning_performed":
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

        analogical_units.append(
            analogical_unit
        )

        units_by_section.setdefault(
            section_id,
            [],
        ).append(
            analogical_unit
        )

        if section_id not in section_metadata:
            section_metadata[
                section_id
            ] = {
                "section_id":
                    section_id,

                "section_index":
                    procedural_unit.get(
                        "section_index"
                    ),

                "section_title":
                    procedural_unit.get(
                        "section_title"
                    ),

                "heading_level":
                    procedural_unit.get(
                        "heading_level"
                    ),
            }

        seen_analogical_ids.add(
            analogical_claim_unit_id
        )

        seen_procedural_ids.add(
            procedural_claim_unit_id
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

    for unit in analogical_units:
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

        analogical_sections.append({
            **metadata,

            "upstream_procedural_claim_count":
                len(
                    section_units
                ),

            "analogical_claim_unit_count":
                len(
                    section_units
                ),

            "analogical_claim_units":
                section_units,
        })

    if (
        len(
            analogical_units
        )
        != len(
            procedural_units
        )
    ):
        raise AnalogicalIntelligenceError(
            "Analogical Claim Unit construction must remain "
            "one-to-one with Procedural Claim Units."
        )

    return {
        "schema_version":
            "analogical_claim_units_v1",

        "analogical_intelligence_version":
            "analogical_intelligence_v1",

        "phase":
            "4.6.11",

        "patch":
            "4.6.11C",

        "status":
            "ANALOGICAL_CLAIM_UNITS_PREPARED",

        "article_identity":
            identity,

        "procedural_claim_unit_count":
            len(
                procedural_units
            ),

        "analogical_claim_unit_count":
            len(
                analogical_units
            ),

        "section_count":
            len(
                analogical_sections
            ),

        "analogical_sections":
            analogical_sections,

        "analogical_claim_units":
            analogical_units,

        "construction_summary": {
            "source_procedural_claim_unit_count":
                len(
                    procedural_units
                ),

            "analogical_claim_unit_count":
                len(
                    analogical_units
                ),

            "one_to_one_procedural_mapping":
                (
                    len(
                        analogical_units
                    )
                    == len(
                        procedural_units
                    )
                ),

            "canonical_order_preserved":
                True,

            "canonical_text_preserved":
                True,

            "evidence_context_preserved":
                True,

            "procedural_context_preserved":
                True,

            "article_body_reparsed":
                False,

            "analogical_signals_interpreted":
                False,

            "analogical_source_target_selected":
                False,

            "analogical_correspondences_inferred":
                False,

            "analogy_extension_performed":
                False,

            "generic_similarity_reasoning_performed":
                False,
        },

        "processing_boundaries": {
            "article_body_reparsed":
                False,

            "analogical_claim_units_prepared":
                True,

            "analogical_signal_interpretation_performed":
                False,

            "analogical_candidate_extraction_performed":
                False,

            "analogy_source_target_selection_performed":
                False,

            "analogical_correspondence_mapping_performed":
                False,

            "analogy_extension_performed":
                False,

            "generic_similarity_reasoning_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
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
            "analogical_signal_interpretation",
    }



def interpret_analogical_signals_v1(
    analogical_claim_units_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Interpret explicit article-local analogical wording.

    This stage identifies and classifies analogical framing signals only.

    It does NOT:
    - establish that every comparison is an analogy,
    - select the analogy source or target,
    - infer conceptual correspondences,
    - infer unstated analogy mappings,
    - extend an article-expressed analogy,
    - perform generic similarity reasoning,
    - determine final analogy validity,
    - redo procedural reasoning,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - perform new causal reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    import re

    if not isinstance(
        analogical_claim_units_result,
        Mapping,
    ):
        raise AnalogicalIntelligenceError(
            "analogical_claim_units_result must be a mapping."
        )

    if (
        analogical_claim_units_result.get(
            "schema_version"
        )
        != "analogical_claim_units_v1"
    ):
        raise AnalogicalIntelligenceError(
            "Stage D requires analogical_claim_units_v1."
        )

    if (
        analogical_claim_units_result.get(
            "status"
        )
        != "ANALOGICAL_CLAIM_UNITS_PREPARED"
    ):
        raise AnalogicalIntelligenceError(
            "Analogical Claim Units must be prepared before Stage D."
        )

    if (
        analogical_claim_units_result.get(
            "phase"
        )
        != "4.6.11"
    ):
        raise AnalogicalIntelligenceError(
            "Stage D requires Phase 4.6.11 input."
        )

    if (
        analogical_claim_units_result.get(
            "patch"
        )
        != "4.6.11C"
    ):
        raise AnalogicalIntelligenceError(
            "Stage D requires canonical 4.6.11C input."
        )

    if (
        analogical_claim_units_result.get(
            "next_stage"
        )
        != "analogical_signal_interpretation"
    ):
        raise AnalogicalIntelligenceError(
            "Stage C must hand off to analogical_signal_interpretation."
        )

    if (
        analogical_claim_units_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise AnalogicalIntelligenceError(
            "Analogical Intelligence must remain transient."
        )

    signal_specs = (
        (
            "EXPLICIT_ANALOGY_TERM",
            "EXPLICIT_ANALOGY_FRAMING",
            re.compile(
                r"\b(?:"
                r"analogy|"
                r"analogies|"
                r"analogous\s+to"
                r")\b",
                re.IGNORECASE,
            ),
        ),
        (
            "THINK_OF_AS",
            "EXPLANATORY_ANALOGY_FRAMING",
            re.compile(
                r"\bthink\s+of\b"
                r"[^.!?;]{1,120}?"
                r"\bas\b",
                re.IGNORECASE,
            ),
        ),
        (
            "THINK_OF_LIKE",
            "EXPLANATORY_ANALOGY_FRAMING",
            re.compile(
                r"\bthink\s+of\b"
                r"[^.!?;]{1,120}?"
                r"\blike\b",
                re.IGNORECASE,
            ),
        ),
        (
            "IS_LIKE",
            "COPULAR_ANALOGY_FRAMING",
            re.compile(
                r"\b(?:is|are|was|were)\s+like\b",
                re.IGNORECASE,
            ),
        ),
        (
            "WORKS_LIKE",
            "FUNCTIONAL_ANALOGY_FRAMING",
            re.compile(
                r"\bworks?\s+like\b",
                re.IGNORECASE,
            ),
        ),
        (
            "FUNCTIONS_LIKE",
            "FUNCTIONAL_ANALOGY_FRAMING",
            re.compile(
                r"\bfunctions?\s+like\b",
                re.IGNORECASE,
            ),
        ),
        (
            "OPERATES_LIKE",
            "FUNCTIONAL_ANALOGY_FRAMING",
            re.compile(
                r"\boperates?\s+like\b",
                re.IGNORECASE,
            ),
        ),
        (
            "SERVES_AS_ANALOGY",
            "EXPLANATORY_ANALOGY_FRAMING",
            re.compile(
                r"\bserves?\s+as\s+(?:an?\s+)?analogy\b",
                re.IGNORECASE,
            ),
        ),
        (
            "IN_THE_SAME_WAY",
            "CORRESPONDENCE_FRAMING",
            re.compile(
                r"\bin\s+the\s+same\s+way\b",
                re.IGNORECASE,
            ),
        ),
        (
            "JUST_AS_SO",
            "PARALLEL_CORRESPONDENCE_FRAMING",
            re.compile(
                r"\bjust\s+as\b"
                r"[^.!?;]{1,180}?"
                r"\bso\b",
                re.IGNORECASE,
            ),
        ),
        (
            "AS_IF_AS_THOUGH",
            "ANALOGICAL_FRAMING_CUE",
            re.compile(
                r"\bas\s+(?:if|though)\b",
                re.IGNORECASE,
            ),
        ),
    )

    ambiguous_specs = (
        (
            "GENERIC_LIKE",
            re.compile(
                r"\blike\b",
                re.IGNORECASE,
            ),
            "LIKE_ALONE_DOES_NOT_ESTABLISH_ANALOGY",
        ),
        (
            "GENERIC_SIMILAR_TO",
            re.compile(
                r"\bsimilar\s+to\b",
                re.IGNORECASE,
            ),
            "SIMILARITY_ALONE_BELONGS_TO_SIMILARITY_INTELLIGENCE",
        ),
        (
            "GENERIC_COMPARED_TO",
            re.compile(
                r"\bcompar(?:ed|ing)\s+to\b",
                re.IGNORECASE,
            ),
            "COMPARISON_ALONE_DOES_NOT_ESTABLISH_ANALOGY",
        ),
        (
            "GENERIC_JUST_AS",
            re.compile(
                r"\bjust\s+as\b",
                re.IGNORECASE,
            ),
            "JUST_AS_WITHOUT_PAIRED_CORRESPONDENCE_IS_AMBIGUOUS",
        ),
        (
            "SOUNDS_LIKE",
            re.compile(
                r"\bsounds?\s+like\b",
                re.IGNORECASE,
            ),
            "SOUNDS_LIKE_MAY_BE_IDIOMATIC_OR_PERCEPTUAL",
        ),
        (
            "LOOKS_LIKE",
            re.compile(
                r"\blooks?\s+like\b",
                re.IGNORECASE,
            ),
            "LOOKS_LIKE_MAY_EXPRESS_APPEARANCE_NOT_ANALOGY",
        ),
        (
            "FEELS_LIKE",
            re.compile(
                r"\bfeels?\s+like\b",
                re.IGNORECASE,
            ),
            "FEELS_LIKE_MAY_EXPRESS_SUBJECTIVE_STATE_NOT_ANALOGY",
        ),
        (
            "SAME_AS",
            re.compile(
                r"\b(?:the\s+)?same\s+as\b",
                re.IGNORECASE,
            ),
            "EQUIVALENCE_WORDING_DOES_NOT_AUTOMATICALLY_ESTABLISH_ANALOGY",
        ),
    )

    source_units = list(
        analogical_claim_units_result.get(
            "analogical_claim_units"
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
            raise AnalogicalIntelligenceError(
                "Every Analogical Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "analogical_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "analogical_signal_interpretation"
            )
            != "PENDING"
        ):
            raise AnalogicalIntelligenceError(
                "Analogical signal interpretation must be PENDING before Stage D."
            )

        if (
            state.get(
                "analogical_candidate_extraction"
            )
            != "PENDING"
        ):
            raise AnalogicalIntelligenceError(
                "Analogical candidate extraction must remain PENDING during Stage D."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "analogical_claim_unit_prepared"
            )
            is not True
        ):
            raise AnalogicalIntelligenceError(
                "Analogical Claim Unit preparation boundary is incomplete."
            )

        required_false_boundaries = (
            "analogical_signal_interpretation_performed",
            "analogical_candidate_extraction_performed",
            "analogy_source_target_selection_performed",
            "analogical_correspondence_mapping_performed",
            "analogy_extension_performed",
            "generic_similarity_reasoning_performed",
            "procedural_reasoning_performed",
            "quantitative_reasoning_performed",
            "temporal_reasoning_performed",
            "new_causal_reasoning_performed",
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
                raise AnalogicalIntelligenceError(
                    boundary_name
                    + " must be False before Stage D."
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

                duplicate_span = any(
                    span[0] == existing_start
                    and span[1] == existing_end
                    and signal_type == existing_type
                    for (
                        existing_start,
                        existing_end,
                        existing_type,
                    ) in occupied_spans
                )

                if duplicate_span:
                    continue

                signal = {
                    "signal_type":
                        signal_type,

                    "analogical_semantic_class":
                        semantic_class,

                    "matched_text":
                        match.group(0),

                    "character_start":
                        match.start(),

                    "character_end":
                        match.end(),

                    "article_asserted_signal":
                        True,

                    "analogical_candidate_extracted":
                        False,

                    "analogy_source_selected":
                        False,

                    "analogy_target_selected":
                        False,

                    "analogical_correspondence_mapped":
                        False,

                    "analogy_extended":
                        False,

                    "generic_similarity_reasoning_performed":
                        False,

                    "procedural_reasoning_performed":
                        False,

                    "quantitative_reasoning_performed":
                        False,

                    "temporal_reasoning_performed":
                        False,

                    "new_causal_reasoning_performed":
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
                        "AMBIGUOUS_ANALOGICAL_LEXEME_DEFERRED",

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

                    "analogy_inference_performed":
                        False,

                    "generic_similarity_reasoning_performed":
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
            "analogical_signal_interpretation"
        ] = "COMPLETE"

        interpreted_boundaries = dict(
            boundaries
        )

        interpreted_boundaries[
            "analogical_signal_interpretation_performed"
        ] = True

        interpreted_boundaries[
            "analogical_candidate_extraction_performed"
        ] = False

        interpreted_boundaries[
            "analogy_source_target_selection_performed"
        ] = False

        interpreted_boundaries[
            "analogical_correspondence_mapping_performed"
        ] = False

        interpreted_boundaries[
            "analogy_extension_performed"
        ] = False

        interpreted_boundaries[
            "generic_similarity_reasoning_performed"
        ] = False

        interpreted_boundaries[
            "procedural_reasoning_performed"
        ] = False

        interpreted_boundaries[
            "quantitative_reasoning_performed"
        ] = False

        interpreted_boundaries[
            "temporal_reasoning_performed"
        ] = False

        interpreted_boundaries[
            "new_causal_reasoning_performed"
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
            "analogical_signals":
                signals,

            "analogical_signal_exclusions":
                exclusions,

            "analogical_signal_count":
                unit_total,

            "analogical_signal_exclusion_count":
                len(
                    exclusions
                ),

            "has_analogical_signal":
                unit_total > 0,

            "analogical_signal_interpretation_scope":
                "ARTICLE_LOCAL_EXPLICIT_ANALOGICAL_FRAMING_SIGNAL_ONLY",

            "analogical_analysis_state":
                interpreted_state,

            "processing_boundaries":
                interpreted_boundaries,
        })

        interpreted_units.append(
            interpreted_unit
        )

        unit_id = str(
            interpreted_unit.get(
                "analogical_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise AnalogicalIntelligenceError(
                "Every interpreted Analogical Claim Unit requires an ID."
            )

        if unit_id in interpreted_by_id:
            raise AnalogicalIntelligenceError(
                "Duplicate interpreted Analogical Claim Unit ID."
            )

        interpreted_by_id[
            unit_id
        ] = interpreted_unit

    interpreted_sections = []

    for section in (
        analogical_claim_units_result.get(
            "analogical_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every analogical section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "analogical_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise AnalogicalIntelligenceError(
                    "Every section Analogical Claim Unit reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "analogical_claim_unit_id"
                )
                or ""
            )

            resolved_unit = interpreted_by_id.get(
                unit_id
            )

            if resolved_unit is None:
                raise AnalogicalIntelligenceError(
                    "Analogical section references an unknown claim unit."
                )

            section_units.append(
                resolved_unit
            )

        interpreted_sections.append({
            **dict(
                section
            ),

            "analogical_claim_units":
                section_units,

            "analogical_signal_unit_count":
                sum(
                    1
                    for unit in section_units
                    if unit.get(
                        "has_analogical_signal"
                    )
                    is True
                ),

            "analogical_signal_count":
                sum(
                    int(
                        unit.get(
                            "analogical_signal_count"
                        )
                        or 0
                    )
                    for unit in section_units
                ),

            "analogical_signal_exclusion_count":
                sum(
                    int(
                        unit.get(
                            "analogical_signal_exclusion_count"
                        )
                        or 0
                    )
                    for unit in section_units
                ),
        })

    result = dict(
        analogical_claim_units_result
    )

    result_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    result_boundaries[
        "analogical_signal_interpretation_performed"
    ] = True

    result_boundaries[
        "analogical_candidate_extraction_performed"
    ] = False

    result_boundaries[
        "analogy_source_target_selection_performed"
    ] = False

    result_boundaries[
        "analogical_correspondence_mapping_performed"
    ] = False

    result_boundaries[
        "analogy_extension_performed"
    ] = False

    result_boundaries[
        "generic_similarity_reasoning_performed"
    ] = False

    result_boundaries[
        "procedural_reasoning_performed"
    ] = False

    result_boundaries[
        "quantitative_reasoning_performed"
    ] = False

    result_boundaries[
        "temporal_reasoning_performed"
    ] = False

    result_boundaries[
        "new_causal_reasoning_performed"
    ] = False

    result_boundaries[
        "truth_assessment_performed"
    ] = False

    result_boundaries[
        "external_authority_check_performed"
    ] = False

    result.update({
        "schema_version":
            "analogical_signal_interpretation_v1",

        "patch":
            "4.6.11D",

        "status":
            "ANALOGICAL_SIGNAL_INTERPRETATION_COMPLETE",

        "analogical_sections":
            interpreted_sections,

        "analogical_claim_units":
            interpreted_units,

        "analogical_signal_summary": {
            "claim_unit_count":
                len(
                    interpreted_units
                ),

            "units_with_analogical_signals":
                units_with_signals,

            "total_analogical_signal_count":
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

            "ordinary_comparison_not_automatically_analogical":
                True,

            "generic_similarity_not_automatically_analogical":
                True,

            "analogical_candidates_extracted":
                False,

            "analogy_source_target_selected":
                False,

            "analogical_correspondence_mapping_performed":
                False,

            "analogy_extension_performed":
                False,

            "generic_similarity_reasoning_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "truth_assessment_performed":
                False,
        },

        "processing_boundaries":
            result_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "analogical_candidate_extraction",
    })

    return result



def extract_analogical_candidates_v1(
    analogical_signal_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Extract conservative article-local analogical candidates from
    interpreted Analogical Intelligence signals.

    This stage constructs analogical candidate objects only.

    It does NOT:
    - select the final analogy source,
    - select the final analogy target,
    - ground source or target concepts,
    - infer conceptual correspondences,
    - infer unstated analogy mappings,
    - extend an article-expressed analogy,
    - convert contextual-only signals into standalone analogies,
    - perform generic similarity reasoning,
    - determine final analogy validity,
    - redo procedural reasoning,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - perform new causal reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    import hashlib

    if not isinstance(
        analogical_signal_result,
        Mapping,
    ):
        raise AnalogicalIntelligenceError(
            "analogical_signal_result must be a mapping."
        )

    if (
        analogical_signal_result.get(
            "schema_version"
        )
        != "analogical_signal_interpretation_v1"
    ):
        raise AnalogicalIntelligenceError(
            "Stage E requires analogical_signal_interpretation_v1."
        )

    if (
        analogical_signal_result.get(
            "status"
        )
        != "ANALOGICAL_SIGNAL_INTERPRETATION_COMPLETE"
    ):
        raise AnalogicalIntelligenceError(
            "Analogical signal interpretation must be complete."
        )

    if (
        analogical_signal_result.get(
            "phase"
        )
        != "4.6.11"
    ):
        raise AnalogicalIntelligenceError(
            "Stage E requires Phase 4.6.11 input."
        )

    if (
        analogical_signal_result.get(
            "patch"
        )
        != "4.6.11D"
    ):
        raise AnalogicalIntelligenceError(
            "Stage E requires canonical 4.6.11D input."
        )

    if (
        analogical_signal_result.get(
            "next_stage"
        )
        != "analogical_candidate_extraction"
    ):
        raise AnalogicalIntelligenceError(
            "Stage D must hand off to analogical_candidate_extraction."
        )

    if (
        analogical_signal_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise AnalogicalIntelligenceError(
            "Analogical Intelligence must remain transient."
        )

    primary_signal_types = {
        "THINK_OF_AS",
        "THINK_OF_LIKE",
        "IS_LIKE",
        "WORKS_LIKE",
        "FUNCTIONS_LIKE",
        "OPERATES_LIKE",
        "JUST_AS_SO",
        "AS_IF_AS_THOUGH",
    }

    contextual_signal_types = {
        "EXPLICIT_ANALOGY_TERM",
        "SERVES_AS_ANALOGY",
        "IN_THE_SAME_WAY",
    }

    candidate_form_by_signal = {
        "THINK_OF_AS":
            "EXPLANATORY_ANALOGY",

        "THINK_OF_LIKE":
            "EXPLANATORY_ANALOGY",

        "IS_LIKE":
            "EXPLANATORY_ANALOGY",

        "WORKS_LIKE":
            "FUNCTIONAL_ANALOGY",

        "FUNCTIONS_LIKE":
            "FUNCTIONAL_ANALOGY",

        "OPERATES_LIKE":
            "FUNCTIONAL_ANALOGY",

        "JUST_AS_SO":
            "PARALLEL_CORRESPONDENCE_ANALOGY",

        "AS_IF_AS_THOUGH":
            "FRAMED_ANALOGICAL_CONSTRUCTION",
    }

    def build_candidate_id(
        unit_id: str,
        signal_type: str,
        matched_text: str,
        start: int,
        end: int,
        ordinal: int,
    ) -> str:
        raw = "|".join([
            unit_id,
            signal_type,
            matched_text,
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
            "analogical_candidate_"
            + hashlib.sha256(
                raw.encode(
                    "utf-8"
                )
            ).hexdigest()[:24]
        )

    source_units = list(
        analogical_signal_result.get(
            "analogical_claim_units"
        )
        or []
    )

    extracted_units = []
    extracted_by_id = {}
    all_candidates = []

    seen_candidate_ids = set()

    units_with_candidates = 0
    rejected_signal_count = 0
    contextual_signal_count = 0

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every Stage-D Analogical Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "analogical_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "analogical_signal_interpretation"
            )
            != "COMPLETE"
        ):
            raise AnalogicalIntelligenceError(
                "Analogical signal interpretation must be COMPLETE before Stage E."
            )

        if (
            state.get(
                "analogical_candidate_extraction"
            )
            != "PENDING"
        ):
            raise AnalogicalIntelligenceError(
                "Analogical candidate extraction must be PENDING before Stage E."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "analogical_signal_interpretation_performed"
            )
            is not True
        ):
            raise AnalogicalIntelligenceError(
                "Stage-D Analogical interpretation boundary is incomplete."
            )

        required_false_boundaries = (
            "analogical_candidate_extraction_performed",
            "analogy_source_target_selection_performed",
            "analogical_correspondence_mapping_performed",
            "analogy_extension_performed",
            "generic_similarity_reasoning_performed",
            "procedural_reasoning_performed",
            "quantitative_reasoning_performed",
            "temporal_reasoning_performed",
            "new_causal_reasoning_performed",
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
                raise AnalogicalIntelligenceError(
                    boundary_name
                    + " must be False before Stage E."
                )

        unit_id = str(
            unit.get(
                "analogical_claim_unit_id"
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
            raise AnalogicalIntelligenceError(
                "Analogical Claim Unit ID is required."
            )

        signals = list(
            unit.get(
                "analogical_signals"
            )
            or []
        )

        contextual_signals = []

        for signal in signals:
            if not isinstance(
                signal,
                Mapping,
            ):
                raise AnalogicalIntelligenceError(
                    "Every analogical signal must be a mapping."
                )

            signal_type = str(
                signal.get(
                    "signal_type"
                )
                or ""
            )

            if signal_type in contextual_signal_types:
                contextual_signals.append(
                    dict(
                        signal
                    )
                )

        contextual_signal_count += len(
            contextual_signals
        )

        unit_candidates = []
        unit_rejections = []

        for signal_index, signal in enumerate(
            signals,
            start=1,
        ):
            if not isinstance(
                signal,
                Mapping,
            ):
                raise AnalogicalIntelligenceError(
                    "Every analogical signal must be a mapping."
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
                raise AnalogicalIntelligenceError(
                    "Analogical signal character span is invalid."
                )

            if (
                sentence_text[
                    start:end
                ]
                != matched_text
            ):
                raise AnalogicalIntelligenceError(
                    "Analogical signal text does not match its source span."
                )

            if signal_type in contextual_signal_types:
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
                        "CONTEXTUAL_SIGNAL_REQUIRES_EXPLICIT_ANALOGICAL_ANCHOR",

                    "candidate_created":
                        False,
                })

                rejected_signal_count += 1
                continue

            if signal_type not in primary_signal_types:
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
                        "UNSUPPORTED_ANALOGICAL_PRIMARY_SIGNAL",

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
                        "EMPTY_ANALOGICAL_SIGNAL_TEXT",

                    "candidate_created":
                        False,
                })

                rejected_signal_count += 1
                continue

            candidate_id = build_candidate_id(
                unit_id,
                signal_type,
                matched_text,
                start,
                end,
                signal_index,
            )

            if candidate_id in seen_candidate_ids:
                raise AnalogicalIntelligenceError(
                    "Duplicate Analogical Candidate ID."
                )

            candidate = {
                "analogical_candidate_id":
                    candidate_id,

                "analogical_claim_unit_id":
                    unit_id,

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

                "signal_type":
                    signal_type,

                "analogical_semantic_class":
                    signal.get(
                        "analogical_semantic_class"
                    ),

                "signal_matched_text":
                    matched_text,

                "signal_character_start":
                    start,

                "signal_character_end":
                    end,

                "candidate_analogical_form":
                    candidate_form_by_signal[
                        signal_type
                    ],

                "contextual_analogical_signals": [
                    dict(
                        item
                    )
                    for item in contextual_signals
                ],

                "contextual_analogical_signal_count":
                    len(
                        contextual_signals
                    ),

                "article_asserted_candidate":
                    True,

                "same_sentence_candidate":
                    True,

                "entity_concept_grounded":
                    False,

                "analogy_source_selected":
                    False,

                "selected_analogy_source":
                    None,

                "analogy_target_selected":
                    False,

                "selected_analogy_target":
                    None,

                "analogy_source_target_orientation_resolved":
                    False,

                "analogical_correspondence_validated":
                    False,

                "analogical_correspondence_mapped":
                    False,

                "same_sentence_analogical_validated":
                    False,

                "cross_sentence_analogical_validated":
                    False,

                "analogical_evidence_assessed":
                    False,

                "duplicate_resolution_performed":
                    False,

                "analogy_extended":
                    False,

                "generic_similarity_reasoning_performed":
                    False,

                "procedural_reasoning_performed":
                    False,

                "quantitative_reasoning_performed":
                    False,

                "temporal_reasoning_performed":
                    False,

                "new_causal_reasoning_performed":
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

        if unit_candidates:
            units_with_candidates += 1

        extracted_state = dict(
            state
        )

        extracted_state[
            "analogical_candidate_extraction"
        ] = "COMPLETE"

        extracted_boundaries = dict(
            boundaries
        )

        extracted_boundaries[
            "analogical_candidate_extraction_performed"
        ] = True

        extracted_boundaries[
            "analogy_source_target_selection_performed"
        ] = False

        extracted_boundaries[
            "analogical_correspondence_mapping_performed"
        ] = False

        extracted_boundaries[
            "analogy_extension_performed"
        ] = False

        extracted_boundaries[
            "generic_similarity_reasoning_performed"
        ] = False

        extracted_boundaries[
            "procedural_reasoning_performed"
        ] = False

        extracted_boundaries[
            "quantitative_reasoning_performed"
        ] = False

        extracted_boundaries[
            "temporal_reasoning_performed"
        ] = False

        extracted_boundaries[
            "new_causal_reasoning_performed"
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
            "analogical_candidates":
                unit_candidates,

            "analogical_candidate_count":
                len(
                    unit_candidates
                ),

            "analogical_extraction_rejections":
                unit_rejections,

            "analogical_extraction_rejection_count":
                len(
                    unit_rejections
                ),

            "analogical_analysis_state":
                extracted_state,

            "processing_boundaries":
                extracted_boundaries,
        })

        extracted_units.append(
            extracted_unit
        )

        if unit_id in extracted_by_id:
            raise AnalogicalIntelligenceError(
                "Duplicate extracted Analogical Claim Unit ID."
            )

        extracted_by_id[
            unit_id
        ] = extracted_unit

    extracted_sections = []

    for section in (
        analogical_signal_result.get(
            "analogical_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every analogical section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "analogical_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise AnalogicalIntelligenceError(
                    "Every section Analogical Claim Unit reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "analogical_claim_unit_id"
                )
                or ""
            )

            resolved_unit = extracted_by_id.get(
                unit_id
            )

            if resolved_unit is None:
                raise AnalogicalIntelligenceError(
                    "Analogical section references an unknown claim unit."
                )

            section_units.append(
                resolved_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "analogical_candidates"
                )
                or []
            )
        ]

        extracted_sections.append({
            **dict(
                section
            ),

            "analogical_claim_units":
                section_units,

            "analogical_candidate_count":
                len(
                    section_candidates
                ),

            "analogical_candidates":
                section_candidates,
        })

    result = dict(
        analogical_signal_result
    )

    result_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    result_boundaries[
        "analogical_candidate_extraction_performed"
    ] = True

    result_boundaries[
        "analogy_source_target_selection_performed"
    ] = False

    result_boundaries[
        "analogical_correspondence_mapping_performed"
    ] = False

    result_boundaries[
        "analogy_extension_performed"
    ] = False

    result_boundaries[
        "generic_similarity_reasoning_performed"
    ] = False

    result_boundaries[
        "procedural_reasoning_performed"
    ] = False

    result_boundaries[
        "quantitative_reasoning_performed"
    ] = False

    result_boundaries[
        "temporal_reasoning_performed"
    ] = False

    result_boundaries[
        "new_causal_reasoning_performed"
    ] = False

    result_boundaries[
        "truth_assessment_performed"
    ] = False

    result_boundaries[
        "external_authority_check_performed"
    ] = False

    result.update({
        "schema_version":
            "analogical_candidates_v1",

        "patch":
            "4.6.11E",

        "status":
            "ANALOGICAL_CANDIDATE_EXTRACTION_COMPLETE",

        "analogical_sections":
            extracted_sections,

        "analogical_claim_units":
            extracted_units,

        "analogical_candidates":
            all_candidates,

        "analogical_extraction_summary": {
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

            "contextual_signal_count":
                contextual_signal_count,

            "primary_signal_types":
                sorted(
                    primary_signal_types
                ),

            "contextual_signal_types":
                sorted(
                    contextual_signal_types
                ),

            "zero_candidates_allowed":
                True,

            "same_sentence_extraction_only":
                True,

            "ambiguous_stage_d_exclusions_not_promoted":
                True,

            "entity_concept_grounding_performed":
                False,

            "analogy_source_target_selection_performed":
                False,

            "analogical_correspondence_mapping_performed":
                False,

            "analogy_extension_performed":
                False,

            "generic_similarity_reasoning_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "truth_assessment_performed":
                False,
        },

        "processing_boundaries":
            result_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "entity_concept_grounding",
    })

    return result



def ground_analogical_candidates_v1(
    analogical_candidates_result: Mapping[str, Any],
    entity_concept_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Ground Analogical Intelligence candidates against canonical
    article-local Phase 4.6.2 Entity & Concept Intelligence objects.

    This stage identifies semantic objects present in each
    analogical candidate's source sentence.

    It does NOT:
    - select the final analogy source,
    - select the final analogy target,
    - assign source/target orientation,
    - create new entities or concepts,
    - perform fuzzy semantic similarity,
    - infer conceptual correspondences,
    - infer unstated analogy mappings,
    - extend an article-expressed analogy,
    - determine final analogy validity,
    - redo procedural reasoning,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - perform new causal reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    import hashlib
    import re

    if not isinstance(
        analogical_candidates_result,
        Mapping,
    ):
        raise AnalogicalIntelligenceError(
            "analogical_candidates_result must be a mapping."
        )

    if not isinstance(
        entity_concept_result,
        Mapping,
    ):
        raise AnalogicalIntelligenceError(
            "entity_concept_result must be a mapping."
        )

    if (
        analogical_candidates_result.get(
            "schema_version"
        )
        != "analogical_candidates_v1"
    ):
        raise AnalogicalIntelligenceError(
            "Stage F requires analogical_candidates_v1."
        )

    if (
        analogical_candidates_result.get(
            "status"
        )
        != "ANALOGICAL_CANDIDATE_EXTRACTION_COMPLETE"
    ):
        raise AnalogicalIntelligenceError(
            "Analogical candidate extraction must be complete."
        )

    if (
        analogical_candidates_result.get(
            "phase"
        )
        != "4.6.11"
    ):
        raise AnalogicalIntelligenceError(
            "Stage F requires Phase 4.6.11 input."
        )

    if (
        analogical_candidates_result.get(
            "patch"
        )
        != "4.6.11E"
    ):
        raise AnalogicalIntelligenceError(
            "Stage F requires canonical 4.6.11E input."
        )

    if (
        analogical_candidates_result.get(
            "next_stage"
        )
        != "entity_concept_grounding"
    ):
        raise AnalogicalIntelligenceError(
            "Stage E must hand off to entity_concept_grounding."
        )

    if (
        analogical_candidates_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise AnalogicalIntelligenceError(
            "Analogical Intelligence must remain transient."
        )

    if (
        entity_concept_result.get(
            "schema_version"
        )
        != "entity_concept_intelligence_result_v1"
    ):
        raise AnalogicalIntelligenceError(
            "Stage F requires canonical entity_concept_intelligence_result_v1."
        )

    if (
        entity_concept_result.get(
            "status"
        )
        != "ENTITY_CONCEPT_INTELLIGENCE_COMPLETE"
    ):
        raise AnalogicalIntelligenceError(
            "Entity & Concept Intelligence must be complete."
        )

    if (
        entity_concept_result.get(
            "phase"
        )
        != "4.6.2"
    ):
        raise AnalogicalIntelligenceError(
            "Stage F requires Phase 4.6.2 Entity & Concept Intelligence."
        )

    semantic_objects = list(
        entity_concept_result.get(
            "semantic_objects"
        )
        or []
    )

    if not semantic_objects:
        raise AnalogicalIntelligenceError(
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
        raise AnalogicalIntelligenceError(
            "Entity & Concept Intelligence must be article-local."
        )

    if (
        entity_boundaries.get(
            "semantic_memory_write_performed"
        )
        is not False
    ):
        raise AnalogicalIntelligenceError(
            "Unexpected Semantic Memory write detected upstream."
        )

    if (
        entity_boundaries.get(
            "reasoning_performed"
        )
        is not False
    ):
        raise AnalogicalIntelligenceError(
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
        analogical_candidates_result.get(
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
        raise AnalogicalIntelligenceError(
            "Analogical article_id is required."
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
        raise AnalogicalIntelligenceError(
            "Entity/Concept Intelligence article identity mismatch."
        )

    prepared_objects = []

    for semantic_object in semantic_objects:
        if not isinstance(
            semantic_object,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
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
            raise AnalogicalIntelligenceError(
                "Semantic object is missing canonical_text."
            )

        if semantic_kind not in {
            "entity",
            "concept",
        }:
            raise AnalogicalIntelligenceError(
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
            raise AnalogicalIntelligenceError(
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
            "article_semantic_object_"
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

                    "analogy_source_selected":
                        False,

                    "analogy_target_selected":
                        False,

                    "analogy_participant_selected":
                        False,

                    "analogy_source_target_orientation_resolved":
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

    source_candidates = list(
        analogical_candidates_result.get(
            "analogical_candidates"
        )
        or []
    )

    grounded_candidates = []
    seen_candidate_ids = set()

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every analogical candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "analogical_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise AnalogicalIntelligenceError(
                "Analogical candidate ID is required."
            )

        if candidate_id in seen_candidate_ids:
            raise AnalogicalIntelligenceError(
                "Duplicate Analogical Candidate ID."
            )

        seen_candidate_ids.add(
            candidate_id
        )

        if (
            candidate.get(
                "entity_concept_grounded"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Candidate must not already be entity/concept grounded."
            )

        source_text = str(
            candidate.get(
                "source_text"
            )
            or ""
        )

        grounding_matches = (
            collect_context_groundings(
                source_text
            )
        )

        grounding_match_count = len(
            grounding_matches
        )

        if grounding_match_count == 0:
            grounding_status = (
                "UNGROUNDED"
            )

        elif grounding_match_count == 1:
            grounding_status = (
                "GROUNDED_SINGLE_MATCH"
            )

        else:
            grounding_status = (
                "GROUNDED_MULTIPLE_MATCHES"
            )

        grounded_candidate = dict(
            candidate
        )

        grounded_candidate.update({
            "entity_concept_grounding_matches":
                grounding_matches,

            "entity_concept_grounding_match_count":
                grounding_match_count,

            "grounding_status":
                grounding_status,

            "entity_concept_grounded":
                grounding_match_count > 0,

            "analogy_participant_selection_performed":
                False,

            "analogy_source_selected":
                False,

            "selected_analogy_source":
                None,

            "analogy_target_selected":
                False,

            "selected_analogy_target":
                None,

            "analogy_source_target_orientation_resolved":
                False,

            "analogical_correspondence_validated":
                False,

            "analogical_correspondence_mapped":
                False,

            "same_sentence_analogical_validated":
                False,

            "cross_sentence_analogical_validated":
                False,

            "analogical_evidence_assessed":
                False,

            "duplicate_resolution_performed":
                False,

            "analogy_extended":
                False,

            "generic_similarity_reasoning_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,
        })

        grounded_candidates.append(
            grounded_candidate
        )

    grounded_by_id = {
        candidate.get(
            "analogical_candidate_id"
        ):
            candidate
        for candidate in grounded_candidates
    }

    grounded_units = []
    seen_unit_ids = set()

    for unit in (
        analogical_candidates_result.get(
            "analogical_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every Analogical Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "analogical_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise AnalogicalIntelligenceError(
                "Analogical Claim Unit ID is required."
            )

        if unit_id in seen_unit_ids:
            raise AnalogicalIntelligenceError(
                "Duplicate Analogical Claim Unit ID."
            )

        seen_unit_ids.add(
            unit_id
        )

        state = dict(
            unit.get(
                "analogical_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "analogical_candidate_extraction"
            )
            != "COMPLETE"
        ):
            raise AnalogicalIntelligenceError(
                "Analogical candidate extraction must be COMPLETE before grounding."
            )

        if (
            state.get(
                "entity_concept_grounding"
            )
            != "PENDING"
        ):
            raise AnalogicalIntelligenceError(
                "Entity/concept grounding must be PENDING."
            )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "analogical_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise AnalogicalIntelligenceError(
                    "Every unit Analogical Candidate reference must be a mapping."
                )

            candidate_id = str(
                old_candidate.get(
                    "analogical_candidate_id"
                )
                or ""
            )

            grounded = grounded_by_id.get(
                candidate_id
            )

            if grounded is None:
                raise AnalogicalIntelligenceError(
                    "Analogical candidate/unit identity mismatch."
                )

            unit_candidates.append(
                grounded
            )

        updated_state = dict(
            state
        )

        updated_state[
            "entity_concept_grounding"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            updated_boundaries.get(
                "analogical_candidate_extraction_performed"
            )
            is not True
        ):
            raise AnalogicalIntelligenceError(
                "Stage-E extraction boundary is incomplete."
            )

        required_false_boundaries = (
            "analogy_source_target_selection_performed",
            "analogical_correspondence_mapping_performed",
            "analogy_extension_performed",
            "generic_similarity_reasoning_performed",
            "procedural_reasoning_performed",
            "quantitative_reasoning_performed",
            "temporal_reasoning_performed",
            "new_causal_reasoning_performed",
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
                raise AnalogicalIntelligenceError(
                    boundary_name
                    + " must be False before Stage F."
                )

        updated_boundaries[
            "entity_concept_grounding_performed"
        ] = True

        updated_boundaries[
            "analogy_source_target_selection_performed"
        ] = False

        updated_boundaries[
            "analogical_correspondence_mapping_performed"
        ] = False

        updated_boundaries[
            "analogy_extension_performed"
        ] = False

        updated_boundaries[
            "generic_similarity_reasoning_performed"
        ] = False

        updated_boundaries[
            "procedural_reasoning_performed"
        ] = False

        updated_boundaries[
            "quantitative_reasoning_performed"
        ] = False

        updated_boundaries[
            "temporal_reasoning_performed"
        ] = False

        updated_boundaries[
            "new_causal_reasoning_performed"
        ] = False

        updated_boundaries[
            "truth_assessment_performed"
        ] = False

        updated_boundaries[
            "external_authority_check_performed"
        ] = False

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "analogical_candidates":
                unit_candidates,

            "grounded_candidate_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "entity_concept_grounded"
                    )
                    is True
                ),

            "single_match_grounded_candidate_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "grounding_status"
                    )
                    == "GROUNDED_SINGLE_MATCH"
                ),

            "multiple_match_grounded_candidate_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "grounding_status"
                    )
                    == "GROUNDED_MULTIPLE_MATCHES"
                ),

            "ungrounded_candidate_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "grounding_status"
                    )
                    == "UNGROUNDED"
                ),

            "analogical_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        grounded_units.append(
            updated_unit
        )

    grounded_units_by_id = {
        unit.get(
            "analogical_claim_unit_id"
        ):
            unit
        for unit in grounded_units
    }

    grounded_sections = []

    for section in (
        analogical_candidates_result.get(
            "analogical_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every analogical section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "analogical_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise AnalogicalIntelligenceError(
                    "Every section Analogical Claim Unit reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "analogical_claim_unit_id"
                )
                or ""
            )

            grounded_unit = (
                grounded_units_by_id.get(
                    unit_id
                )
            )

            if grounded_unit is None:
                raise AnalogicalIntelligenceError(
                    "Analogical section/unit grounding mismatch."
                )

            section_units.append(
                grounded_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "analogical_candidates"
                )
                or []
            )
        ]

        grounded_sections.append({
            **dict(
                section
            ),

            "analogical_claim_units":
                section_units,

            "analogical_candidates":
                section_candidates,

            "analogical_candidate_count":
                len(
                    section_candidates
                ),

            "grounded_candidate_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "entity_concept_grounded"
                    )
                    is True
                ),

            "ungrounded_candidate_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "entity_concept_grounded"
                    )
                    is False
                ),

            "entity_concept_grounding_complete":
                True,
        })

    grounded_count = sum(
        1
        for candidate in grounded_candidates
        if candidate.get(
            "entity_concept_grounded"
        )
        is True
    )

    single_match_count = sum(
        1
        for candidate in grounded_candidates
        if candidate.get(
            "grounding_status"
        )
        == "GROUNDED_SINGLE_MATCH"
    )

    multiple_match_count = sum(
        1
        for candidate in grounded_candidates
        if candidate.get(
            "grounding_status"
        )
        == "GROUNDED_MULTIPLE_MATCHES"
    )

    ungrounded_count = sum(
        1
        for candidate in grounded_candidates
        if candidate.get(
            "grounding_status"
        )
        == "UNGROUNDED"
    )

    total_grounding_matches = sum(
        int(
            candidate.get(
                "entity_concept_grounding_match_count"
            )
            or 0
        )
        for candidate in grounded_candidates
    )

    result = dict(
        analogical_candidates_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    boundaries[
        "entity_concept_grounding_performed"
    ] = True

    boundaries[
        "analogy_source_target_selection_performed"
    ] = False

    boundaries[
        "analogical_correspondence_mapping_performed"
    ] = False

    boundaries[
        "analogy_extension_performed"
    ] = False

    boundaries[
        "generic_similarity_reasoning_performed"
    ] = False

    boundaries[
        "procedural_reasoning_performed"
    ] = False

    boundaries[
        "quantitative_reasoning_performed"
    ] = False

    boundaries[
        "temporal_reasoning_performed"
    ] = False

    boundaries[
        "new_causal_reasoning_performed"
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

    result.update({
        "schema_version":
            "analogical_entity_concept_grounding_v1",

        "patch":
            "4.6.11F",

        "status":
            "ANALOGICAL_ENTITY_CONCEPT_GROUNDING_COMPLETE",

        "analogical_sections":
            grounded_sections,

        "analogical_claim_units":
            grounded_units,

        "analogical_candidates":
            grounded_candidates,

        "entity_concept_grounding_summary": {
            "semantic_object_count":
                len(
                    semantic_objects
                ),

            "analogical_candidate_count":
                len(
                    grounded_candidates
                ),

            "grounded_candidate_count":
                grounded_count,

            "single_match_grounded_candidate_count":
                single_match_count,

            "multiple_match_grounded_candidate_count":
                multiple_match_count,

            "ungrounded_candidate_count":
                ungrounded_count,

            "total_grounding_match_count":
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

            "fuzzy_similarity_performed":
                False,

            "analogy_participant_selection_performed":
                False,

            "analogy_source_target_selection_performed":
                False,

            "analogy_source_target_orientation_performed":
                False,

            "analogical_correspondence_mapping_performed":
                False,

            "analogy_extension_performed":
                False,

            "generic_similarity_reasoning_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
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
            "analogy_source_target_orientation",
    })

    return result



def resolve_analogy_source_target_orientation_v1(
    analogical_grounding_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Resolve article-local analogy source/target orientation from
    explicit analogical structure plus canonical grounding evidence.

    TARGET:
        the article concept being explained.

    SOURCE:
        the article concept being used as the explanatory model.

    Resolution is deliberately conservative. A candidate resolves only
    when its explicit construction supplies directional structure and
    exactly one grounded semantic object can be located on each side.

    It does NOT:
    - infer missing analogy participants,
    - orient candidates from grounding count alone,
    - select among multiple competing groundings by similarity,
    - infer conceptual correspondences,
    - map source properties to target properties,
    - extend an analogy,
    - perform generic similarity reasoning,
    - validate the final analogy,
    - perform cross-sentence analogy resolution,
    - redo procedural reasoning,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - perform new causal reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    import re

    if not isinstance(
        analogical_grounding_result,
        Mapping,
    ):
        raise AnalogicalIntelligenceError(
            "analogical_grounding_result must be a mapping."
        )

    if (
        analogical_grounding_result.get(
            "schema_version"
        )
        != "analogical_entity_concept_grounding_v1"
    ):
        raise AnalogicalIntelligenceError(
            "Stage G requires analogical_entity_concept_grounding_v1."
        )

    if (
        analogical_grounding_result.get(
            "status"
        )
        != "ANALOGICAL_ENTITY_CONCEPT_GROUNDING_COMPLETE"
    ):
        raise AnalogicalIntelligenceError(
            "Analogical entity/concept grounding must be complete."
        )

    if (
        analogical_grounding_result.get(
            "phase"
        )
        != "4.6.11"
    ):
        raise AnalogicalIntelligenceError(
            "Stage G requires Phase 4.6.11 input."
        )

    if (
        analogical_grounding_result.get(
            "patch"
        )
        != "4.6.11F"
    ):
        raise AnalogicalIntelligenceError(
            "Stage G requires canonical 4.6.11F input."
        )

    if (
        analogical_grounding_result.get(
            "next_stage"
        )
        != "analogy_source_target_orientation"
    ):
        raise AnalogicalIntelligenceError(
            "Stage F must hand off to analogy_source_target_orientation."
        )

    if (
        analogical_grounding_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise AnalogicalIntelligenceError(
            "Analogical Intelligence must remain transient."
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

    def unique_groundings_in_segment(
        segment_text: str,
        grounding_matches: list[Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        normalized_segment = normalize(
            segment_text
        )

        if not normalized_segment:
            return []

        resolved_by_ref = {}

        for grounding in grounding_matches:
            if not isinstance(
                grounding,
                Mapping,
            ):
                raise AnalogicalIntelligenceError(
                    "Every grounding match must be a mapping."
                )

            grounding_ref = str(
                grounding.get(
                    "grounding_ref"
                )
                or ""
            )

            canonical_text = str(
                grounding.get(
                    "canonical_text"
                )
                or ""
            ).strip()

            matched_surface = str(
                grounding.get(
                    "matched_surface_form"
                )
                or ""
            ).strip()

            if not grounding_ref:
                raise AnalogicalIntelligenceError(
                    "Grounding match requires grounding_ref."
                )

            variants = {
                canonical_text,
                matched_surface,
            }

            segment_match = False

            for variant in variants:
                normalized_variant = normalize(
                    variant
                )

                if not normalized_variant:
                    continue

                bounded_pattern = (
                    r"(?<![a-z0-9'])"
                    + re.escape(
                        normalized_variant
                    )
                    + r"(?![a-z0-9'])"
                )

                if re.search(
                    bounded_pattern,
                    normalized_segment,
                ):
                    segment_match = True
                    break

            if segment_match:
                resolved_by_ref[
                    grounding_ref
                ] = dict(
                    grounding
                )

        matches = list(
            resolved_by_ref.values()
        )

        matches.sort(
            key=lambda item: (
                str(
                    item.get(
                        "canonical_text"
                    )
                    or ""
                ),
                str(
                    item.get(
                        "grounding_ref"
                    )
                    or ""
                ),
            )
        )

        return matches

    def split_directional_segments(
        candidate: Mapping[str, Any],
    ) -> dict[str, Any]:
        source_text = str(
            candidate.get(
                "source_text"
            )
            or ""
        )

        signal_type = str(
            candidate.get(
                "signal_type"
            )
            or ""
        )

        candidate_form = str(
            candidate.get(
                "candidate_analogical_form"
            )
            or ""
        )

        if not source_text:
            return {
                "supported":
                    False,

                "reason":
                    "EMPTY_SOURCE_TEXT",

                "target_segment":
                    None,

                "source_segment":
                    None,

                "orientation_pattern":
                    None,
            }

        if signal_type in {
            "THINK_OF_AS",
            "THINK_OF_LIKE",
        }:
            if signal_type == "THINK_OF_AS":
                pattern = re.compile(
                    r"\bthink\s+of\s+(.+?)\s+as\s+(.+?)(?:[.!?]|$)",
                    re.IGNORECASE,
                )

                orientation_pattern = (
                    "THINK_OF_TARGET_AS_SOURCE"
                )

            else:
                pattern = re.compile(
                    r"\bthink\s+of\s+(.+?)\s+like\s+(.+?)(?:[.!?]|$)",
                    re.IGNORECASE,
                )

                orientation_pattern = (
                    "THINK_OF_TARGET_LIKE_SOURCE"
                )

            match = pattern.search(
                source_text
            )

            if match is None:
                return {
                    "supported":
                        False,

                    "reason":
                        "EXPLICIT_THINK_OF_STRUCTURE_NOT_RESOLVED",

                    "target_segment":
                        None,

                    "source_segment":
                        None,

                    "orientation_pattern":
                        orientation_pattern,
                }

            return {
                "supported":
                    True,

                "reason":
                    "EXPLICIT_DIRECTIONAL_STRUCTURE",

                "target_segment":
                    match.group(1).strip(),

                "source_segment":
                    match.group(2).strip(),

                "orientation_pattern":
                    orientation_pattern,
            }

        if signal_type == "IS_LIKE":
            pattern = re.compile(
                r"^(.+?)\s+(?:is|are|was|were)\s+like\s+(.+?)(?:[.!?]|$)",
                re.IGNORECASE,
            )

            match = pattern.search(
                source_text.strip()
            )

            if match is None:
                return {
                    "supported":
                        False,

                    "reason":
                        "COPULAR_ANALOGY_STRUCTURE_NOT_RESOLVED",

                    "target_segment":
                        None,

                    "source_segment":
                        None,

                    "orientation_pattern":
                        "COPULAR_TARGET_IS_LIKE_SOURCE",
                }

            return {
                "supported":
                    True,

                "reason":
                    "EXPLICIT_DIRECTIONAL_STRUCTURE",

                "target_segment":
                    match.group(1).strip(),

                "source_segment":
                    match.group(2).strip(),

                "orientation_pattern":
                    "COPULAR_TARGET_IS_LIKE_SOURCE",
            }

        if signal_type in {
            "WORKS_LIKE",
            "FUNCTIONS_LIKE",
            "OPERATES_LIKE",
        }:
            verb_by_signal = {
                "WORKS_LIKE":
                    r"works?",

                "FUNCTIONS_LIKE":
                    r"functions?",

                "OPERATES_LIKE":
                    r"operates?",
            }

            pattern = re.compile(
                r"^(.+?)\s+"
                + verb_by_signal[
                    signal_type
                ]
                + r"\s+like\s+(.+?)(?:[.!?]|$)",
                re.IGNORECASE,
            )

            match = pattern.search(
                source_text.strip()
            )

            if match is None:
                return {
                    "supported":
                        False,

                    "reason":
                        "FUNCTIONAL_ANALOGY_STRUCTURE_NOT_RESOLVED",

                    "target_segment":
                        None,

                    "source_segment":
                        None,

                    "orientation_pattern":
                        "TARGET_FUNCTIONS_LIKE_SOURCE",
                }

            return {
                "supported":
                    True,

                "reason":
                    "EXPLICIT_DIRECTIONAL_STRUCTURE",

                "target_segment":
                    match.group(1).strip(),

                "source_segment":
                    match.group(2).strip(),

                "orientation_pattern":
                    "TARGET_FUNCTIONS_LIKE_SOURCE",
            }

        if signal_type == "JUST_AS_SO":
            pattern = re.compile(
                r"\bjust\s+as\s+(.+?),\s*so\s+(.+?)(?:[.!?]|$)",
                re.IGNORECASE,
            )

            match = pattern.search(
                source_text
            )

            if match is None:
                return {
                    "supported":
                        False,

                    "reason":
                        "JUST_AS_SO_STRUCTURE_NOT_RESOLVED",

                    "target_segment":
                        None,

                    "source_segment":
                        None,

                    "orientation_pattern":
                        "JUST_AS_SOURCE_SO_TARGET",
                }

            return {
                "supported":
                    True,

                "reason":
                    "EXPLICIT_DIRECTIONAL_STRUCTURE",

                "target_segment":
                    match.group(2).strip(),

                "source_segment":
                    match.group(1).strip(),

                "orientation_pattern":
                    "JUST_AS_SOURCE_SO_TARGET",
            }

        if signal_type == "AS_IF_AS_THOUGH":
            pattern = re.compile(
                r"^(.+?)\s+as\s+(?:if|though)\s+(.+?)(?:[.!?]|$)",
                re.IGNORECASE,
            )

            match = pattern.search(
                source_text.strip()
            )

            if match is None:
                return {
                    "supported":
                        False,

                    "reason":
                        "AS_IF_AS_THOUGH_STRUCTURE_NOT_RESOLVED",

                    "target_segment":
                        None,

                    "source_segment":
                        None,

                    "orientation_pattern":
                        "TARGET_AS_IF_SOURCE",
                }

            return {
                "supported":
                    True,

                "reason":
                    "EXPLICIT_DIRECTIONAL_STRUCTURE",

                "target_segment":
                    match.group(1).strip(),

                "source_segment":
                    match.group(2).strip(),

                "orientation_pattern":
                    "TARGET_AS_IF_SOURCE",
            }

        return {
            "supported":
                False,

            "reason":
                "UNSUPPORTED_ANALOGICAL_ORIENTATION_SIGNAL",

            "target_segment":
                None,

            "source_segment":
                None,

            "orientation_pattern":
                (
                    candidate_form
                    or signal_type
                    or None
                ),
        }

    source_candidates = list(
        analogical_grounding_result.get(
            "analogical_candidates"
        )
        or []
    )

    unit_candidate_counts = {}

    for source_unit in (
        analogical_grounding_result.get(
            "analogical_claim_units"
        )
        or []
    ):
        if not isinstance(
            source_unit,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every Analogical Claim Unit must be a mapping."
            )

        source_unit_id = str(
            source_unit.get(
                "analogical_claim_unit_id"
            )
            or ""
        )

        if not source_unit_id:
            raise AnalogicalIntelligenceError(
                "Analogical Claim Unit ID is required."
            )

        if source_unit_id in unit_candidate_counts:
            raise AnalogicalIntelligenceError(
                "Duplicate Analogical Claim Unit ID detected."
            )

        unit_candidate_counts[
            source_unit_id
        ] = len(
            source_unit.get(
                "analogical_candidates"
            )
            or []
        )

    oriented_candidates = []
    oriented_by_id = {}

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every analogical candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "analogical_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise AnalogicalIntelligenceError(
                "Analogical candidate ID is required."
            )

        if candidate_id in oriented_by_id:
            raise AnalogicalIntelligenceError(
                "Duplicate Analogical Candidate ID during orientation."
            )

        if (
            candidate.get(
                "analogy_source_target_orientation_resolved"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Candidate must not already have source/target orientation."
            )

        if (
            candidate.get(
                "analogy_source_selected"
            )
            is not False
            or candidate.get(
                "selected_analogy_source"
            )
            is not None
            or candidate.get(
                "analogy_target_selected"
            )
            is not False
            or candidate.get(
                "selected_analogy_target"
            )
            is not None
        ):
            raise AnalogicalIntelligenceError(
                "Candidate must not already have source/target selection."
            )

        candidate_unit_id = str(
            candidate.get(
                "analogical_claim_unit_id"
            )
            or ""
        )

        if not candidate_unit_id:
            raise AnalogicalIntelligenceError(
                "Analogical candidate claim-unit ID is required."
            )

        if candidate_unit_id not in unit_candidate_counts:
            raise AnalogicalIntelligenceError(
                "Analogical candidate has no canonical claim unit."
            )

        grounding_matches = list(
            candidate.get(
                "entity_concept_grounding_matches"
            )
            or []
        )

        grounding_match_count = candidate.get(
            "entity_concept_grounding_match_count"
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
            raise AnalogicalIntelligenceError(
                "Candidate has invalid grounding-match count."
            )

        if grounding_match_count != len(
            grounding_matches
        ):
            raise AnalogicalIntelligenceError(
                "Candidate grounding-match count does not match grounding evidence."
            )

        if (
            candidate.get(
                "entity_concept_grounded"
            )
            is not (
                grounding_match_count > 0
            )
        ):
            raise AnalogicalIntelligenceError(
                "Candidate grounding flag is inconsistent with grounding evidence."
            )

        structure = split_directional_segments(
            candidate
        )

        target_segment = structure.get(
            "target_segment"
        )

        source_segment = structure.get(
            "source_segment"
        )

        if (
            structure.get(
                "supported"
            )
            is True
        ):
            target_matches = unique_groundings_in_segment(
                str(
                    target_segment
                    or ""
                ),
                grounding_matches,
            )

            source_matches = unique_groundings_in_segment(
                str(
                    source_segment
                    or ""
                ),
                grounding_matches,
            )

        else:
            target_matches = []
            source_matches = []

        target_refs = {
            item.get(
                "grounding_ref"
            )
            for item in target_matches
        }

        source_refs = {
            item.get(
                "grounding_ref"
            )
            for item in source_matches
        }

        overlap_refs = (
            target_refs
            & source_refs
        )

        if (
            structure.get(
                "supported"
            )
            is not True
        ):
            orientation_status = (
                "ANALOGY_ORIENTATION_UNRESOLVED"
            )

            orientation_basis = str(
                structure.get(
                    "reason"
                )
                or "UNSUPPORTED_ANALOGICAL_STRUCTURE"
            )

            orientation_resolved = False
            selected_target = None
            selected_source = None

        elif grounding_match_count < 2:
            orientation_status = (
                "ANALOGY_ORIENTATION_UNRESOLVED"
            )

            orientation_basis = (
                "INSUFFICIENT_ARTICLE_LOCAL_GROUNDING_FOR_TWO_SIDES"
            )

            orientation_resolved = False
            selected_target = None
            selected_source = None

        elif overlap_refs:
            orientation_status = (
                "ANALOGY_ORIENTATION_UNRESOLVED"
            )

            orientation_basis = (
                "GROUNDING_OBJECT_OCCURS_ON_BOTH_ANALOGY_SIDES"
            )

            orientation_resolved = False
            selected_target = None
            selected_source = None

        elif (
            len(
                target_matches
            )
            == 1
            and len(
                source_matches
            )
            == 1
        ):
            orientation_status = (
                "ANALOGY_SOURCE_TARGET_ORIENTATION_RESOLVED"
            )

            orientation_basis = (
                "EXPLICIT_DIRECTIONAL_STRUCTURE_PLUS_UNIQUE_ARTICLE_LOCAL_GROUNDING"
            )

            orientation_resolved = True

            selected_target = dict(
                target_matches[0]
            )

            selected_source = dict(
                source_matches[0]
            )

        elif len(
            target_matches
        ) == 0:
            orientation_status = (
                "ANALOGY_ORIENTATION_UNRESOLVED"
            )

            orientation_basis = (
                "NO_UNIQUE_TARGET_SIDE_GROUNDING"
            )

            orientation_resolved = False
            selected_target = None
            selected_source = None

        elif len(
            source_matches
        ) == 0:
            orientation_status = (
                "ANALOGY_ORIENTATION_UNRESOLVED"
            )

            orientation_basis = (
                "NO_UNIQUE_SOURCE_SIDE_GROUNDING"
            )

            orientation_resolved = False
            selected_target = None
            selected_source = None

        else:
            orientation_status = (
                "ANALOGY_ORIENTATION_UNRESOLVED"
            )

            orientation_basis = (
                "AMBIGUOUS_MULTIPLE_GROUNDINGS_ON_ANALOGY_SIDE"
            )

            orientation_resolved = False
            selected_target = None
            selected_source = None

        oriented = dict(
            candidate
        )

        oriented.update({
            "analogy_orientation_status":
                orientation_status,

            "analogy_orientation_basis":
                orientation_basis,

            "analogy_orientation_pattern":
                structure.get(
                    "orientation_pattern"
                ),

            "candidate_analogical_structure_supported":
                structure.get(
                    "supported"
                )
                is True,

            "orientation_target_segment":
                target_segment,

            "orientation_source_segment":
                source_segment,

            "target_side_grounding_matches":
                target_matches,

            "target_side_grounding_match_count":
                len(
                    target_matches
                ),

            "source_side_grounding_matches":
                source_matches,

            "source_side_grounding_match_count":
                len(
                    source_matches
                ),

            "cross_side_grounding_overlap_count":
                len(
                    overlap_refs
                ),

            "selected_analogy_target":
                selected_target,

            "analogy_target_selected":
                selected_target
                is not None,

            "selected_analogy_source":
                selected_source,

            "analogy_source_selected":
                selected_source
                is not None,

            "analogy_participant_selection_performed":
                orientation_resolved,

            "analogy_source_target_orientation_resolved":
                orientation_resolved,

            "analogical_correspondence_validated":
                False,

            "analogical_correspondence_mapped":
                False,

            "same_sentence_analogical_validated":
                False,

            "cross_sentence_analogical_validated":
                False,

            "analogical_evidence_assessed":
                False,

            "duplicate_resolution_performed":
                False,

            "analogy_extended":
                False,

            "generic_similarity_reasoning_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,
        })

        oriented_candidates.append(
            oriented
        )

        oriented_by_id[
            candidate_id
        ] = oriented

    oriented_units = []
    oriented_units_by_id = {}

    for unit in (
        analogical_grounding_result.get(
            "analogical_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every Analogical Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "analogical_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise AnalogicalIntelligenceError(
                "Analogical Claim Unit ID is required."
            )

        if unit_id in oriented_units_by_id:
            raise AnalogicalIntelligenceError(
                "Duplicate Analogical Claim Unit ID during orientation."
            )

        state = dict(
            unit.get(
                "analogical_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "entity_concept_grounding"
            )
            != "COMPLETE"
        ):
            raise AnalogicalIntelligenceError(
                "Entity/concept grounding must be COMPLETE before orientation."
            )

        if (
            state.get(
                "analogy_source_target_orientation"
            )
            != "PENDING"
        ):
            raise AnalogicalIntelligenceError(
                "Analogy source/target orientation must be PENDING."
            )

        updated_candidates = []

        for old_candidate in (
            unit.get(
                "analogical_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise AnalogicalIntelligenceError(
                    "Every unit Analogical Candidate reference must be a mapping."
                )

            candidate_id = str(
                old_candidate.get(
                    "analogical_candidate_id"
                )
                or ""
            )

            oriented_candidate = (
                oriented_by_id.get(
                    candidate_id
                )
            )

            if oriented_candidate is None:
                raise AnalogicalIntelligenceError(
                    "Analogical candidate/unit orientation mismatch."
                )

            updated_candidates.append(
                oriented_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "analogy_source_target_orientation"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            updated_boundaries.get(
                "entity_concept_grounding_performed"
            )
            is not True
        ):
            raise AnalogicalIntelligenceError(
                "Stage-F entity/concept grounding boundary is incomplete."
            )

        if (
            updated_boundaries.get(
                "analogy_source_target_selection_performed"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Analogy source/target selection must not already be performed."
            )

        required_false_boundaries = (
            "analogical_correspondence_mapping_performed",
            "analogy_extension_performed",
            "generic_similarity_reasoning_performed",
            "procedural_reasoning_performed",
            "quantitative_reasoning_performed",
            "temporal_reasoning_performed",
            "new_causal_reasoning_performed",
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
                raise AnalogicalIntelligenceError(
                    boundary_name
                    + " must be False before Stage G."
                )

        updated_boundaries[
            "analogy_source_target_selection_performed"
        ] = True

        updated_boundaries[
            "analogy_source_target_orientation_performed"
        ] = True

        updated_boundaries[
            "analogical_correspondence_mapping_performed"
        ] = False

        updated_boundaries[
            "analogy_extension_performed"
        ] = False

        updated_boundaries[
            "generic_similarity_reasoning_performed"
        ] = False

        updated_boundaries[
            "procedural_reasoning_performed"
        ] = False

        updated_boundaries[
            "quantitative_reasoning_performed"
        ] = False

        updated_boundaries[
            "temporal_reasoning_performed"
        ] = False

        updated_boundaries[
            "new_causal_reasoning_performed"
        ] = False

        updated_boundaries[
            "truth_assessment_performed"
        ] = False

        updated_boundaries[
            "external_authority_check_performed"
        ] = False

        updated_unit = dict(
            unit
        )

        updated_unit.update({
            "analogical_candidates":
                updated_candidates,

            "resolved_analogy_orientation_count":
                sum(
                    1
                    for candidate in updated_candidates
                    if candidate.get(
                        "analogy_source_target_orientation_resolved"
                    )
                    is True
                ),

            "unresolved_analogy_orientation_count":
                sum(
                    1
                    for candidate in updated_candidates
                    if candidate.get(
                        "analogy_source_target_orientation_resolved"
                    )
                    is False
                ),

            "selected_analogy_source_count":
                sum(
                    1
                    for candidate in updated_candidates
                    if candidate.get(
                        "analogy_source_selected"
                    )
                    is True
                ),

            "selected_analogy_target_count":
                sum(
                    1
                    for candidate in updated_candidates
                    if candidate.get(
                        "analogy_target_selected"
                    )
                    is True
                ),

            "analogical_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        oriented_units.append(
            updated_unit
        )

        oriented_units_by_id[
            unit_id
        ] = updated_unit

    oriented_sections = []

    for section in (
        analogical_grounding_result.get(
            "analogical_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every analogical section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "analogical_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise AnalogicalIntelligenceError(
                    "Every section Analogical Claim Unit reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "analogical_claim_unit_id"
                )
                or ""
            )

            oriented_unit = (
                oriented_units_by_id.get(
                    unit_id
                )
            )

            if oriented_unit is None:
                raise AnalogicalIntelligenceError(
                    "Analogical section/unit orientation mismatch."
                )

            section_units.append(
                oriented_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "analogical_candidates"
                )
                or []
            )
        ]

        oriented_sections.append({
            **dict(
                section
            ),

            "analogical_claim_units":
                section_units,

            "analogical_candidates":
                section_candidates,

            "analogical_candidate_count":
                len(
                    section_candidates
                ),

            "resolved_analogy_orientation_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "analogy_source_target_orientation_resolved"
                    )
                    is True
                ),

            "unresolved_analogy_orientation_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "analogy_source_target_orientation_resolved"
                    )
                    is False
                ),

            "analogy_source_target_orientation_complete":
                True,
        })

    resolved_count = sum(
        1
        for candidate in oriented_candidates
        if candidate.get(
            "analogy_source_target_orientation_resolved"
        )
        is True
    )

    unresolved_count = sum(
        1
        for candidate in oriented_candidates
        if candidate.get(
            "analogy_source_target_orientation_resolved"
        )
        is False
    )

    selected_source_count = sum(
        1
        for candidate in oriented_candidates
        if candidate.get(
            "analogy_source_selected"
        )
        is True
    )

    selected_target_count = sum(
        1
        for candidate in oriented_candidates
        if candidate.get(
            "analogy_target_selected"
        )
        is True
    )

    result = dict(
        analogical_grounding_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        boundaries.get(
            "analogy_source_target_selection_performed"
        )
        is not False
    ):
        raise AnalogicalIntelligenceError(
            "Top-level analogy source/target selection must not already be performed."
        )

    boundaries[
        "analogy_source_target_selection_performed"
    ] = True

    boundaries[
        "analogy_source_target_orientation_performed"
    ] = True

    boundaries[
        "analogical_correspondence_mapping_performed"
    ] = False

    boundaries[
        "analogy_extension_performed"
    ] = False

    boundaries[
        "generic_similarity_reasoning_performed"
    ] = False

    boundaries[
        "procedural_reasoning_performed"
    ] = False

    boundaries[
        "quantitative_reasoning_performed"
    ] = False

    boundaries[
        "temporal_reasoning_performed"
    ] = False

    boundaries[
        "new_causal_reasoning_performed"
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

    result.update({
        "schema_version":
            "analogical_source_target_orientation_v1",

        "patch":
            "4.6.11G",

        "status":
            "ANALOGICAL_SOURCE_TARGET_ORIENTATION_COMPLETE",

        "analogical_sections":
            oriented_sections,

        "analogical_claim_units":
            oriented_units,

        "analogical_candidates":
            oriented_candidates,

        "analogy_source_target_orientation_summary": {
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

            "selected_analogy_source_count":
                selected_source_count,

            "selected_analogy_target_count":
                selected_target_count,

            "orientation_requires_explicit_directional_structure":
                True,

            "orientation_requires_unique_grounding_per_side":
                True,

            "single_grounding_auto_orientation_performed":
                False,

            "multiple_grounding_guessing_performed":
                False,

            "cross_sentence_orientation_performed":
                False,

            "analogical_correspondence_validation_performed":
                False,

            "analogical_correspondence_mapping_performed":
                False,

            "analogy_extension_performed":
                False,

            "generic_similarity_reasoning_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
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
            "analogical_correspondence_validation",
    })

    return result



def validate_analogical_correspondence_v1(
    orientation_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate whether an oriented Analogical Candidate has an
    article-supported source/target correspondence.

    Validation is strictly article-local and same-sentence at this stage.

    This stage verifies:
    - candidate-to-claim-unit identity,
    - sentence identity,
    - source-text continuity,
    - exact analogical signal-span support,
    - article-asserted candidate provenance,
    - same-sentence candidate provenance,
    - completed source/target orientation,
    - selected source and target consistency,
    - source/target grounding evidence,
    - preservation of source/target directional structure.

    It does NOT:
    - invent a source or target,
    - rescue unresolved orientation,
    - infer property-level correspondence mappings,
    - map source properties to target properties,
    - extend an analogy,
    - use neighboring sentences,
    - perform generic similarity reasoning,
    - perform procedural reasoning,
    - perform quantitative reasoning,
    - perform full temporal reasoning,
    - perform new causal reasoning,
    - establish factual/scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    import re

    if not isinstance(
        orientation_result,
        Mapping,
    ):
        raise AnalogicalIntelligenceError(
            "orientation_result must be a mapping."
        )

    if (
        orientation_result.get(
            "schema_version"
        )
        != "analogical_source_target_orientation_v1"
    ):
        raise AnalogicalIntelligenceError(
            "Stage H requires analogical_source_target_orientation_v1."
        )

    if (
        orientation_result.get(
            "status"
        )
        != "ANALOGICAL_SOURCE_TARGET_ORIENTATION_COMPLETE"
    ):
        raise AnalogicalIntelligenceError(
            "Analogy source/target orientation must be complete before Stage H."
        )

    if (
        orientation_result.get(
            "phase"
        )
        != "4.6.11"
    ):
        raise AnalogicalIntelligenceError(
            "Stage H requires Phase 4.6.11 input."
        )

    if (
        orientation_result.get(
            "patch"
        )
        != "4.6.11G"
    ):
        raise AnalogicalIntelligenceError(
            "Stage H requires canonical 4.6.11G input."
        )

    if (
        orientation_result.get(
            "next_stage"
        )
        != "analogical_correspondence_validation"
    ):
        raise AnalogicalIntelligenceError(
            "Stage G must hand off to analogical_correspondence_validation."
        )

    if (
        orientation_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise AnalogicalIntelligenceError(
            "Analogical Intelligence must remain transient."
        )

    source_units = list(
        orientation_result.get(
            "analogical_claim_units"
        )
        or []
    )

    if not source_units:
        raise AnalogicalIntelligenceError(
            "Analogical Claim Units are required."
        )

    candidate_to_unit = {}
    unit_ids = set()

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every Analogical Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "analogical_claim_unit_id"
            )
            or ""
        )

        sentence_id = str(
            unit.get(
                "sentence_id"
            )
            or ""
        )

        claim_text = str(
            unit.get(
                "text"
            )
            or ""
        )

        if not unit_id:
            raise AnalogicalIntelligenceError(
                "Analogical Claim Unit ID is required."
            )

        if unit_id in unit_ids:
            raise AnalogicalIntelligenceError(
                "Duplicate Analogical Claim Unit ID detected."
            )

        unit_ids.add(
            unit_id
        )

        if not sentence_id:
            raise AnalogicalIntelligenceError(
                "Analogical Claim Unit sentence_id is required."
            )

        if not claim_text:
            raise AnalogicalIntelligenceError(
                "Analogical Claim Unit text is required."
            )

        state = dict(
            unit.get(
                "analogical_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "analogy_source_target_orientation"
            )
            != "COMPLETE"
        ):
            raise AnalogicalIntelligenceError(
                "Analogy source/target orientation must be COMPLETE before Stage H."
            )

        if (
            state.get(
                "analogical_correspondence_validation"
            )
            != "PENDING"
        ):
            raise AnalogicalIntelligenceError(
                "Analogical correspondence validation must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "entity_concept_grounding_performed"
            )
            is not True
        ):
            raise AnalogicalIntelligenceError(
                "Stage-F entity/concept grounding boundary is incomplete."
            )

        if (
            boundaries.get(
                "analogy_source_target_orientation_performed"
            )
            is not True
        ):
            raise AnalogicalIntelligenceError(
                "Stage-G analogy orientation boundary is incomplete."
            )

        required_false_boundaries = (
            "analogical_correspondence_mapping_performed",
            "analogy_extension_performed",
            "generic_similarity_reasoning_performed",
            "procedural_reasoning_performed",
            "quantitative_reasoning_performed",
            "temporal_reasoning_performed",
            "new_causal_reasoning_performed",
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
                raise AnalogicalIntelligenceError(
                    boundary_name
                    + " must be False before Stage H."
                )

        for candidate in (
            unit.get(
                "analogical_candidates"
            )
            or []
        ):
            if not isinstance(
                candidate,
                Mapping,
            ):
                raise AnalogicalIntelligenceError(
                    "Every Analogical Candidate must be a mapping."
                )

            candidate_id = str(
                candidate.get(
                    "analogical_candidate_id"
                )
                or ""
            )

            if not candidate_id:
                raise AnalogicalIntelligenceError(
                    "Analogical Candidate ID is required."
                )

            if candidate_id in candidate_to_unit:
                raise AnalogicalIntelligenceError(
                    "Duplicate Analogical Candidate ID detected."
                )

            candidate_to_unit[
                candidate_id
            ] = {
                "unit_id":
                    unit_id,

                "sentence_id":
                    sentence_id,

                "claim_text":
                    claim_text,
            }

    def normalize_text(
        value: Any,
    ) -> str:
        value = str(
            value
            or ""
        )

        value = value.replace(
            "\u2019",
            "'",
        )

        value = value.replace(
            "\u2018",
            "'",
        )

        value = value.replace(
            "\u2013",
            "-",
        )

        value = value.replace(
            "\u2014",
            "-",
        )

        value = value.lower()

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()

    def signal_span_supported(
        candidate: Mapping[str, Any],
        claim_text: str,
    ) -> tuple[bool, str | None]:
        matched_text = str(
            candidate.get(
                "signal_matched_text"
            )
            or ""
        )

        start = candidate.get(
            "signal_character_start"
        )

        end = candidate.get(
            "signal_character_end"
        )

        if not matched_text.strip():
            return (
                False,
                None,
            )

        if (
            isinstance(
                start,
                int,
            )
            and not isinstance(
                start,
                bool,
            )
            and isinstance(
                end,
                int,
            )
            and not isinstance(
                end,
                bool,
            )
            and start >= 0
            and end > start
            and end <= len(
                claim_text
            )
        ):
            source_slice = claim_text[
                start:end
            ]

            if (
                normalize_text(
                    source_slice
                )
                == normalize_text(
                    matched_text
                )
            ):
                return (
                    True,
                    "EXACT_ANALOGICAL_SIGNAL_SPAN_MATCH",
                )

        return (
            False,
            None,
        )

    source_candidates = list(
        orientation_result.get(
            "analogical_candidates"
        )
        or []
    )

    validated_candidates = []
    validated_by_id = {}

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every analogical candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "analogical_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise AnalogicalIntelligenceError(
                "Analogical Candidate ID is required."
            )

        if candidate_id in validated_by_id:
            raise AnalogicalIntelligenceError(
                "Duplicate top-level Analogical Candidate ID detected."
            )

        unit_info = candidate_to_unit.get(
            candidate_id
        )

        if unit_info is None:
            raise AnalogicalIntelligenceError(
                "Analogical candidate has no canonical claim-unit sentence."
            )

        if (
            candidate.get(
                "analogical_correspondence_validated"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Candidate must not already be correspondence validated."
            )

        if (
            candidate.get(
                "analogical_correspondence_mapped"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Stage H must not receive a mapped correspondence."
            )

        canonical_sentence_id = (
            unit_info[
                "sentence_id"
            ]
        )

        claim_text = (
            unit_info[
                "claim_text"
            ]
        )

        canonical_unit_id = (
            unit_info[
                "unit_id"
            ]
        )

        candidate_sentence_id = str(
            candidate.get(
                "sentence_id"
            )
            or ""
        )

        candidate_unit_id = str(
            candidate.get(
                "analogical_claim_unit_id"
            )
            or ""
        )

        source_text = str(
            candidate.get(
                "source_text"
            )
            or ""
        )

        same_sentence_identity = (
            candidate_sentence_id
            == canonical_sentence_id
        )

        same_unit_identity = (
            candidate_unit_id
            == canonical_unit_id
        )

        source_text_supported = (
            normalize_text(
                source_text
            )
            == normalize_text(
                claim_text
            )
            and bool(
                normalize_text(
                    claim_text
                )
            )
        )

        signal_supported, signal_support_method = (
            signal_span_supported(
                candidate,
                claim_text,
            )
        )

        article_asserted_candidate = (
            candidate.get(
                "article_asserted_candidate"
            )
            is True
        )

        same_sentence_candidate = (
            candidate.get(
                "same_sentence_candidate"
            )
            is True
        )

        orientation_resolved = (
            candidate.get(
                "analogy_source_target_orientation_resolved"
            )
            is True
        )

        source_selected = (
            candidate.get(
                "analogy_source_selected"
            )
            is True
            and isinstance(
                candidate.get(
                    "selected_analogy_source"
                ),
                Mapping,
            )
        )

        target_selected = (
            candidate.get(
                "analogy_target_selected"
            )
            is True
            and isinstance(
                candidate.get(
                    "selected_analogy_target"
                ),
                Mapping,
            )
        )

        structure_supported = (
            candidate.get(
                "candidate_analogical_structure_supported"
            )
            is True
        )

        target_side_count = candidate.get(
            "target_side_grounding_match_count"
        )

        source_side_count = candidate.get(
            "source_side_grounding_match_count"
        )

        overlap_count = candidate.get(
            "cross_side_grounding_overlap_count"
        )

        grounding_counts_valid = (
            isinstance(
                target_side_count,
                int,
            )
            and not isinstance(
                target_side_count,
                bool,
            )
            and target_side_count >= 0
            and isinstance(
                source_side_count,
                int,
            )
            and not isinstance(
                source_side_count,
                bool,
            )
            and source_side_count >= 0
            and isinstance(
                overlap_count,
                int,
            )
            and not isinstance(
                overlap_count,
                bool,
            )
            and overlap_count >= 0
        )

        unique_directional_grounding_supported = (
            grounding_counts_valid
            and target_side_count == 1
            and source_side_count == 1
            and overlap_count == 0
        )

        if not article_asserted_candidate:
            validation_status = (
                "NOT_VALIDATED_NOT_ARTICLE_ASSERTED_CANDIDATE"
            )

            correspondence_valid = False

            validation_reason = (
                "STAGE_E_ARTICLE_ASSERTED_CANDIDATE_IS_NOT_TRUE"
            )

        elif not same_sentence_candidate:
            validation_status = (
                "NOT_VALIDATED_NOT_SAME_SENTENCE_CANDIDATE"
            )

            correspondence_valid = False

            validation_reason = (
                "STAGE_E_SAME_SENTENCE_CANDIDATE_IS_NOT_TRUE"
            )

        elif not same_unit_identity:
            validation_status = (
                "NOT_VALIDATED_CLAIM_UNIT_ID_MISMATCH"
            )

            correspondence_valid = False

            validation_reason = (
                "CANDIDATE_CLAIM_UNIT_ID_DOES_NOT_MATCH_CANONICAL_UNIT"
            )

        elif not same_sentence_identity:
            validation_status = (
                "NOT_VALIDATED_SENTENCE_ID_MISMATCH"
            )

            correspondence_valid = False

            validation_reason = (
                "CANDIDATE_SENTENCE_ID_DOES_NOT_MATCH_CLAIM_UNIT"
            )

        elif not source_text_supported:
            validation_status = (
                "NOT_VALIDATED_SOURCE_TEXT_MISMATCH"
            )

            correspondence_valid = False

            validation_reason = (
                "CANDIDATE_SOURCE_TEXT_DOES_NOT_MATCH_CANONICAL_SENTENCE"
            )

        elif not signal_supported:
            validation_status = (
                "NOT_VALIDATED_ANALOGICAL_SIGNAL_SPAN_UNSUPPORTED"
            )

            correspondence_valid = False

            validation_reason = (
                "ANALOGICAL_SIGNAL_SPAN_NOT_SUPPORTED_BY_CANONICAL_SENTENCE"
            )

        elif not structure_supported:
            validation_status = (
                "NOT_VALIDATED_ANALOGICAL_STRUCTURE_UNSUPPORTED"
            )

            correspondence_valid = False

            validation_reason = (
                "EXPLICIT_ANALOGICAL_STRUCTURE_NOT_SUPPORTED"
            )

        elif not orientation_resolved:
            validation_status = (
                "NOT_VALIDATED_SOURCE_TARGET_ORIENTATION_UNRESOLVED"
            )

            correspondence_valid = False

            validation_reason = (
                "ANALOGY_SOURCE_TARGET_ORIENTATION_NOT_RESOLVED"
            )

        elif not source_selected:
            validation_status = (
                "NOT_VALIDATED_ANALOGY_SOURCE_NOT_SELECTED"
            )

            correspondence_valid = False

            validation_reason = (
                "ORIENTED_ANALOGY_SOURCE_SELECTION_MISSING"
            )

        elif not target_selected:
            validation_status = (
                "NOT_VALIDATED_ANALOGY_TARGET_NOT_SELECTED"
            )

            correspondence_valid = False

            validation_reason = (
                "ORIENTED_ANALOGY_TARGET_SELECTION_MISSING"
            )

        elif not grounding_counts_valid:
            validation_status = (
                "NOT_VALIDATED_INVALID_DIRECTIONAL_GROUNDING_COUNTS"
            )

            correspondence_valid = False

            validation_reason = (
                "SOURCE_TARGET_GROUNDING_COUNT_EVIDENCE_INVALID"
            )

        elif not unique_directional_grounding_supported:
            validation_status = (
                "NOT_VALIDATED_DIRECTIONAL_GROUNDING_AMBIGUOUS"
            )

            correspondence_valid = False

            validation_reason = (
                "SOURCE_TARGET_GROUNDING_NOT_UNIQUELY_SUPPORTED"
            )

        else:
            validation_status = (
                "VALIDATED_ARTICLE_EXPRESSED_ANALOGICAL_CORRESPONDENCE"
            )

            correspondence_valid = True

            validation_reason = None

        validated = dict(
            candidate
        )

        validated.update({
            "analogical_correspondence_validation_status":
                validation_status,

            "analogical_correspondence_valid":
                correspondence_valid,

            "analogical_correspondence_validation_reason":
                validation_reason,

            "article_asserted_candidate_confirmed":
                article_asserted_candidate,

            "same_sentence_candidate_confirmed":
                same_sentence_candidate,

            "same_claim_unit_id_match":
                same_unit_identity,

            "same_sentence_id_match":
                same_sentence_identity,

            "same_sentence_source_text_supported":
                source_text_supported,

            "same_sentence_analogical_signal_supported":
                signal_supported,

            "analogical_signal_support_method":
                signal_support_method,

            "analogical_structure_supported":
                structure_supported,

            "source_target_orientation_supported":
                orientation_resolved,

            "selected_analogy_source_supported":
                source_selected,

            "selected_analogy_target_supported":
                target_selected,

            "directional_grounding_counts_valid":
                grounding_counts_valid,

            "unique_directional_grounding_supported":
                unique_directional_grounding_supported,

            "analogical_correspondence_evidence": {
                "analogical_claim_unit_id":
                    canonical_unit_id,

                "sentence_id":
                    canonical_sentence_id,

                "sentence_text":
                    claim_text,

                "signal_type":
                    candidate.get(
                        "signal_type"
                    ),

                "signal_matched_text":
                    candidate.get(
                        "signal_matched_text"
                    ),

                "signal_character_start":
                    candidate.get(
                        "signal_character_start"
                    ),

                "signal_character_end":
                    candidate.get(
                        "signal_character_end"
                    ),

                "candidate_analogical_form":
                    candidate.get(
                        "candidate_analogical_form"
                    ),

                "analogy_orientation_pattern":
                    candidate.get(
                        "analogy_orientation_pattern"
                    ),

                "orientation_target_segment":
                    candidate.get(
                        "orientation_target_segment"
                    ),

                "orientation_source_segment":
                    candidate.get(
                        "orientation_source_segment"
                    ),

                "selected_analogy_target":
                    candidate.get(
                        "selected_analogy_target"
                    ),

                "selected_analogy_source":
                    candidate.get(
                        "selected_analogy_source"
                    ),
            },

            "analogical_correspondence_validated":
                correspondence_valid,

            "analogical_correspondence_mapped":
                False,

            "same_sentence_analogical_validated":
                False,

            "cross_sentence_analogical_validated":
                False,

            "analogical_evidence_assessed":
                False,

            "duplicate_resolution_performed":
                False,

            "analogy_extended":
                False,

            "generic_similarity_reasoning_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,
        })

        validated_candidates.append(
            validated
        )

        validated_by_id[
            candidate_id
        ] = validated

    validated_units = []
    validated_units_by_id = {}

    for unit in source_units:
        unit_id = str(
            unit.get(
                "analogical_claim_unit_id"
            )
            or ""
        )

        state = dict(
            unit.get(
                "analogical_analysis_state"
            )
            or {}
        )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "analogical_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise AnalogicalIntelligenceError(
                    "Every unit Analogical Candidate reference must be a mapping."
                )

            candidate_id = str(
                old_candidate.get(
                    "analogical_candidate_id"
                )
                or ""
            )

            validated_candidate = (
                validated_by_id.get(
                    candidate_id
                )
            )

            if validated_candidate is None:
                raise AnalogicalIntelligenceError(
                    "Analogical candidate/unit correspondence-validation mismatch."
                )

            unit_candidates.append(
                validated_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "analogical_correspondence_validation"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "analogical_correspondence_validation_performed"
        ] = True

        updated_boundaries[
            "analogical_correspondence_mapping_performed"
        ] = False

        updated_boundaries[
            "same_sentence_analogical_validation_performed"
        ] = False

        updated_boundaries[
            "cross_sentence_analogical_validation_performed"
        ] = False

        updated_boundaries[
            "analogy_extension_performed"
        ] = False

        updated_boundaries[
            "generic_similarity_reasoning_performed"
        ] = False

        updated_boundaries[
            "procedural_reasoning_performed"
        ] = False

        updated_boundaries[
            "quantitative_reasoning_performed"
        ] = False

        updated_boundaries[
            "temporal_reasoning_performed"
        ] = False

        updated_boundaries[
            "new_causal_reasoning_performed"
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
            "analogical_candidates":
                unit_candidates,

            "validated_analogical_correspondence_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "analogical_correspondence_valid"
                    )
                    is True
                ),

            "not_validated_analogical_correspondence_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "analogical_correspondence_valid"
                    )
                    is False
                ),

            "analogical_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        if unit_id in validated_units_by_id:
            raise AnalogicalIntelligenceError(
                "Duplicate Analogical Claim Unit ID during Stage-H reconstruction."
            )

        validated_units.append(
            updated_unit
        )

        validated_units_by_id[
            unit_id
        ] = updated_unit

    validated_sections = []

    for section in (
        orientation_result.get(
            "analogical_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every analogical section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "analogical_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise AnalogicalIntelligenceError(
                    "Every section Analogical Claim Unit reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "analogical_claim_unit_id"
                )
                or ""
            )

            validated_unit = (
                validated_units_by_id.get(
                    unit_id
                )
            )

            if validated_unit is None:
                raise AnalogicalIntelligenceError(
                    "Analogical section/unit correspondence-validation mismatch."
                )

            section_units.append(
                validated_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "analogical_candidates"
                )
                or []
            )
        ]

        validated_sections.append({
            **dict(
                section
            ),

            "analogical_claim_units":
                section_units,

            "analogical_candidates":
                section_candidates,

            "validated_analogical_correspondence_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "analogical_correspondence_valid"
                    )
                    is True
                ),

            "not_validated_analogical_correspondence_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "analogical_correspondence_valid"
                    )
                    is False
                ),

            "analogical_correspondence_validation_complete":
                True,
        })

    validated_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "analogical_correspondence_valid"
        )
        is True
    )

    not_validated_count = (
        len(
            validated_candidates
        )
        - validated_count
    )

    result = dict(
        orientation_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        boundaries.get(
            "analogy_source_target_orientation_performed"
        )
        is not True
    ):
        raise AnalogicalIntelligenceError(
            "Top-level Stage-G analogy-orientation boundary is incomplete."
        )

    if (
        boundaries.get(
            "analogical_correspondence_validation_performed",
            False,
        )
        is not False
    ):
        raise AnalogicalIntelligenceError(
            "Top-level analogical correspondence validation must not already be performed."
        )

    boundaries[
        "analogical_correspondence_validation_performed"
    ] = True

    boundaries[
        "analogical_correspondence_mapping_performed"
    ] = False

    boundaries[
        "same_sentence_analogical_validation_performed"
    ] = False

    boundaries[
        "cross_sentence_analogical_validation_performed"
    ] = False

    boundaries[
        "analogy_extension_performed"
    ] = False

    boundaries[
        "generic_similarity_reasoning_performed"
    ] = False

    boundaries[
        "procedural_reasoning_performed"
    ] = False

    boundaries[
        "quantitative_reasoning_performed"
    ] = False

    boundaries[
        "temporal_reasoning_performed"
    ] = False

    boundaries[
        "new_causal_reasoning_performed"
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

    result.update({
        "schema_version":
            "analogical_correspondence_validation_v1",

        "patch":
            "4.6.11H",

        "status":
            "ANALOGICAL_CORRESPONDENCE_VALIDATION_COMPLETE",

        "analogical_sections":
            validated_sections,

        "analogical_claim_units":
            validated_units,

        "analogical_candidates":
            validated_candidates,

        "analogical_correspondence_validation_summary": {
            "candidate_count":
                len(
                    validated_candidates
                ),

            "validated_correspondence_count":
                validated_count,

            "not_validated_correspondence_count":
                not_validated_count,

            "candidate_count_accounted_for":
                (
                    validated_count
                    + not_validated_count
                    == len(
                        validated_candidates
                    )
                ),

            "article_asserted_candidate_required":
                True,

            "same_sentence_candidate_required":
                True,

            "claim_unit_identity_required":
                True,

            "sentence_identity_required":
                True,

            "source_text_continuity_required":
                True,

            "exact_signal_span_support_required":
                True,

            "resolved_source_target_orientation_required":
                True,

            "unique_directional_grounding_required":
                True,

            "correspondence_mapping_performed":
                False,

            "property_level_mapping_performed":
                False,

            "neighbor_sentence_rescue_performed":
                False,

            "cross_sentence_validation_performed":
                False,

            "analogy_extension_performed":
                False,

            "generic_similarity_reasoning_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
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
            "same_sentence_analogical_validation",
    })

    return result


def validate_same_sentence_analogical_v1(
    correspondence_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate whether each Analogical Candidate is fully supported by its
    canonical article-local Analogical Claim Unit sentence.

    This stage verifies:
    - a valid Stage-H article-expressed analogical correspondence,
    - candidate-to-claim-unit identity,
    - sentence identity,
    - source-text continuity,
    - exact analogical signal-span support,
    - article-asserted candidate provenance,
    - same-sentence candidate provenance,
    - supported analogical structure,
    - resolved source/target orientation,
    - selected analogy source and target,
    - unique directional grounding.

    It does NOT:
    - rescue a candidate with neighboring sentences,
    - perform cross-sentence validation,
    - map analogy properties,
    - extend an analogy,
    - perform generic similarity reasoning,
    - redo entity/concept grounding,
    - redo source/target orientation,
    - perform procedural reasoning,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - perform new causal reasoning,
    - establish factual/scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    import re

    if not isinstance(
        correspondence_result,
        Mapping,
    ):
        raise AnalogicalIntelligenceError(
            "correspondence_result must be a mapping."
        )

    if (
        correspondence_result.get(
            "schema_version"
        )
        != "analogical_correspondence_validation_v1"
    ):
        raise AnalogicalIntelligenceError(
            "Stage I requires analogical_correspondence_validation_v1."
        )

    if (
        correspondence_result.get(
            "status"
        )
        != "ANALOGICAL_CORRESPONDENCE_VALIDATION_COMPLETE"
    ):
        raise AnalogicalIntelligenceError(
            "Analogical correspondence validation must be complete before Stage I."
        )

    if (
        correspondence_result.get(
            "phase"
        )
        != "4.6.11"
    ):
        raise AnalogicalIntelligenceError(
            "Stage I requires Phase 4.6.11 input."
        )

    if (
        correspondence_result.get(
            "patch"
        )
        != "4.6.11H"
    ):
        raise AnalogicalIntelligenceError(
            "Stage I requires canonical 4.6.11H input."
        )

    if (
        correspondence_result.get(
            "next_stage"
        )
        != "same_sentence_analogical_validation"
    ):
        raise AnalogicalIntelligenceError(
            "Stage H must hand off to same_sentence_analogical_validation."
        )

    if (
        correspondence_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise AnalogicalIntelligenceError(
            "Analogical Intelligence must remain transient."
        )

    source_units = list(
        correspondence_result.get(
            "analogical_claim_units"
        )
        or []
    )

    if not source_units:
        raise AnalogicalIntelligenceError(
            "Analogical Claim Units are required."
        )

    candidate_to_unit = {}
    unit_ids = set()

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every Analogical Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "analogical_claim_unit_id"
            )
            or ""
        )

        sentence_id = str(
            unit.get(
                "sentence_id"
            )
            or ""
        )

        claim_text = str(
            unit.get(
                "text"
            )
            or ""
        )

        if not unit_id:
            raise AnalogicalIntelligenceError(
                "Analogical Claim Unit ID is required."
            )

        if unit_id in unit_ids:
            raise AnalogicalIntelligenceError(
                "Duplicate Analogical Claim Unit ID detected."
            )

        unit_ids.add(
            unit_id
        )

        if not sentence_id:
            raise AnalogicalIntelligenceError(
                "Analogical Claim Unit sentence_id is required."
            )

        if not claim_text:
            raise AnalogicalIntelligenceError(
                "Analogical Claim Unit text is required."
            )

        state = dict(
            unit.get(
                "analogical_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "analogical_correspondence_validation"
            )
            != "COMPLETE"
        ):
            raise AnalogicalIntelligenceError(
                "Analogical correspondence validation must be COMPLETE before Stage I."
            )

        if (
            state.get(
                "same_sentence_analogical_validation"
            )
            != "PENDING"
        ):
            raise AnalogicalIntelligenceError(
                "Same-sentence analogical validation must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "entity_concept_grounding_performed"
            )
            is not True
        ):
            raise AnalogicalIntelligenceError(
                "Stage-F entity/concept grounding boundary is incomplete."
            )

        if (
            boundaries.get(
                "analogy_source_target_orientation_performed"
            )
            is not True
        ):
            raise AnalogicalIntelligenceError(
                "Stage-G analogy-orientation boundary is incomplete."
            )

        if (
            boundaries.get(
                "analogical_correspondence_validation_performed"
            )
            is not True
        ):
            raise AnalogicalIntelligenceError(
                "Stage-H correspondence-validation boundary is incomplete."
            )

        required_false_boundaries = (
            "analogical_correspondence_mapping_performed",
            "same_sentence_analogical_validation_performed",
            "cross_sentence_analogical_validation_performed",
            "analogy_extension_performed",
            "generic_similarity_reasoning_performed",
            "procedural_reasoning_performed",
            "quantitative_reasoning_performed",
            "temporal_reasoning_performed",
            "new_causal_reasoning_performed",
            "truth_assessment_performed",
            "external_authority_check_performed",
            "semantic_memory_write_performed",
            "persistence_performed",
        )

        for boundary_name in required_false_boundaries:
            if (
                boundaries.get(
                    boundary_name,
                    False,
                )
                is not False
            ):
                raise AnalogicalIntelligenceError(
                    boundary_name
                    + " must be False before Stage I."
                )

        for candidate in (
            unit.get(
                "analogical_candidates"
            )
            or []
        ):
            if not isinstance(
                candidate,
                Mapping,
            ):
                raise AnalogicalIntelligenceError(
                    "Every Analogical Candidate must be a mapping."
                )

            candidate_id = str(
                candidate.get(
                    "analogical_candidate_id"
                )
                or ""
            )

            if not candidate_id:
                raise AnalogicalIntelligenceError(
                    "Analogical Candidate ID is required."
                )

            if candidate_id in candidate_to_unit:
                raise AnalogicalIntelligenceError(
                    "Duplicate Analogical Candidate ID detected."
                )

            candidate_to_unit[
                candidate_id
            ] = {
                "unit_id":
                    unit_id,

                "sentence_id":
                    sentence_id,

                "claim_text":
                    claim_text,
            }

    def normalize_text(
        value: Any,
    ) -> str:
        value = str(
            value
            or ""
        )

        value = value.replace(
            "\u2019",
            "'",
        )

        value = value.replace(
            "\u2018",
            "'",
        )

        value = value.replace(
            "\u2013",
            "-",
        )

        value = value.replace(
            "\u2014",
            "-",
        )

        value = value.lower()

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()

    def signal_span_supported(
        candidate: Mapping[str, Any],
        claim_text: str,
    ) -> tuple[bool, str | None]:
        matched_text = str(
            candidate.get(
                "signal_matched_text"
            )
            or ""
        )

        start = candidate.get(
            "signal_character_start"
        )

        end = candidate.get(
            "signal_character_end"
        )

        if not matched_text.strip():
            return (
                False,
                None,
            )

        if (
            isinstance(
                start,
                int,
            )
            and not isinstance(
                start,
                bool,
            )
            and isinstance(
                end,
                int,
            )
            and not isinstance(
                end,
                bool,
            )
            and start >= 0
            and end > start
            and end <= len(
                claim_text
            )
        ):
            source_slice = claim_text[
                start:end
            ]

            if (
                normalize_text(
                    source_slice
                )
                == normalize_text(
                    matched_text
                )
            ):
                return (
                    True,
                    "EXACT_ANALOGICAL_SIGNAL_SPAN_MATCH",
                )

        return (
            False,
            None,
        )

    source_candidates = list(
        correspondence_result.get(
            "analogical_candidates"
        )
        or []
    )

    validated_candidates = []
    validated_by_id = {}

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every analogical candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "analogical_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise AnalogicalIntelligenceError(
                "Analogical Candidate ID is required."
            )

        if candidate_id in validated_by_id:
            raise AnalogicalIntelligenceError(
                "Duplicate top-level Analogical Candidate ID detected."
            )

        unit_info = candidate_to_unit.get(
            candidate_id
        )

        if unit_info is None:
            raise AnalogicalIntelligenceError(
                "Analogical candidate has no canonical claim-unit sentence."
            )

        if (
            candidate.get(
                "same_sentence_analogical_validated"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Candidate must not already be same-sentence validated."
            )

        if (
            candidate.get(
                "cross_sentence_analogical_validated"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Stage I must not receive a cross-sentence validated candidate."
            )

        if (
            candidate.get(
                "analogical_correspondence_mapped"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Stage I must not receive a mapped correspondence."
            )

        canonical_sentence_id = (
            unit_info[
                "sentence_id"
            ]
        )

        canonical_unit_id = (
            unit_info[
                "unit_id"
            ]
        )

        claim_text = (
            unit_info[
                "claim_text"
            ]
        )

        candidate_sentence_id = str(
            candidate.get(
                "sentence_id"
            )
            or ""
        )

        candidate_unit_id = str(
            candidate.get(
                "analogical_claim_unit_id"
            )
            or ""
        )

        source_text = str(
            candidate.get(
                "source_text"
            )
            or ""
        )

        same_sentence_identity = (
            candidate_sentence_id
            == canonical_sentence_id
        )

        same_unit_identity = (
            candidate_unit_id
            == canonical_unit_id
        )

        source_text_supported = (
            normalize_text(
                source_text
            )
            == normalize_text(
                claim_text
            )
            and bool(
                normalize_text(
                    claim_text
                )
            )
        )

        signal_supported, signal_support_method = (
            signal_span_supported(
                candidate,
                claim_text,
            )
        )

        article_asserted_candidate = (
            candidate.get(
                "article_asserted_candidate"
            )
            is True
        )

        same_sentence_candidate = (
            candidate.get(
                "same_sentence_candidate"
            )
            is True
        )

        correspondence_supported = (
            candidate.get(
                "analogical_correspondence_valid"
            )
            is True
            and candidate.get(
                "analogical_correspondence_validated"
            )
            is True
        )

        structure_supported = (
            candidate.get(
                "candidate_analogical_structure_supported"
            )
            is True
        )

        orientation_supported = (
            candidate.get(
                "analogy_source_target_orientation_resolved"
            )
            is True
        )

        source_supported = (
            candidate.get(
                "analogy_source_selected"
            )
            is True
            and isinstance(
                candidate.get(
                    "selected_analogy_source"
                ),
                Mapping,
            )
        )

        target_supported = (
            candidate.get(
                "analogy_target_selected"
            )
            is True
            and isinstance(
                candidate.get(
                    "selected_analogy_target"
                ),
                Mapping,
            )
        )

        unique_directional_grounding_supported = (
            candidate.get(
                "unique_directional_grounding_supported"
            )
            is True
        )

        if not correspondence_supported:
            validation_status = (
                "NOT_VALIDATED_CORRESPONDENCE_NOT_VALIDATED"
            )

            same_sentence_valid = False

            validation_reason = (
                "STAGE_H_ANALOGICAL_CORRESPONDENCE_IS_NOT_VALID"
            )

        elif not article_asserted_candidate:
            validation_status = (
                "NOT_VALIDATED_NOT_ARTICLE_ASSERTED_CANDIDATE"
            )

            same_sentence_valid = False

            validation_reason = (
                "STAGE_E_ARTICLE_ASSERTED_CANDIDATE_IS_NOT_TRUE"
            )

        elif not same_sentence_candidate:
            validation_status = (
                "NOT_VALIDATED_NOT_SAME_SENTENCE_CANDIDATE"
            )

            same_sentence_valid = False

            validation_reason = (
                "STAGE_E_SAME_SENTENCE_CANDIDATE_IS_NOT_TRUE"
            )

        elif not same_unit_identity:
            validation_status = (
                "NOT_VALIDATED_CLAIM_UNIT_ID_MISMATCH"
            )

            same_sentence_valid = False

            validation_reason = (
                "CANDIDATE_CLAIM_UNIT_ID_DOES_NOT_MATCH_CANONICAL_UNIT"
            )

        elif not same_sentence_identity:
            validation_status = (
                "NOT_VALIDATED_SENTENCE_ID_MISMATCH"
            )

            same_sentence_valid = False

            validation_reason = (
                "CANDIDATE_SENTENCE_ID_DOES_NOT_MATCH_CLAIM_UNIT"
            )

        elif not source_text_supported:
            validation_status = (
                "NOT_VALIDATED_SOURCE_TEXT_MISMATCH"
            )

            same_sentence_valid = False

            validation_reason = (
                "CANDIDATE_SOURCE_TEXT_DOES_NOT_MATCH_CANONICAL_SENTENCE"
            )

        elif not signal_supported:
            validation_status = (
                "NOT_VALIDATED_ANALOGICAL_SIGNAL_SPAN_UNSUPPORTED"
            )

            same_sentence_valid = False

            validation_reason = (
                "ANALOGICAL_SIGNAL_SPAN_NOT_SUPPORTED_BY_CANONICAL_SENTENCE"
            )

        elif not structure_supported:
            validation_status = (
                "NOT_VALIDATED_ANALOGICAL_STRUCTURE_UNSUPPORTED"
            )

            same_sentence_valid = False

            validation_reason = (
                "EXPLICIT_ANALOGICAL_STRUCTURE_NOT_SUPPORTED"
            )

        elif not orientation_supported:
            validation_status = (
                "NOT_VALIDATED_SOURCE_TARGET_ORIENTATION_UNRESOLVED"
            )

            same_sentence_valid = False

            validation_reason = (
                "ANALOGY_SOURCE_TARGET_ORIENTATION_NOT_RESOLVED"
            )

        elif not source_supported:
            validation_status = (
                "NOT_VALIDATED_ANALOGY_SOURCE_NOT_SELECTED"
            )

            same_sentence_valid = False

            validation_reason = (
                "ORIENTED_ANALOGY_SOURCE_SELECTION_MISSING"
            )

        elif not target_supported:
            validation_status = (
                "NOT_VALIDATED_ANALOGY_TARGET_NOT_SELECTED"
            )

            same_sentence_valid = False

            validation_reason = (
                "ORIENTED_ANALOGY_TARGET_SELECTION_MISSING"
            )

        elif not unique_directional_grounding_supported:
            validation_status = (
                "NOT_VALIDATED_DIRECTIONAL_GROUNDING_NOT_UNIQUE"
            )

            same_sentence_valid = False

            validation_reason = (
                "SOURCE_TARGET_GROUNDING_NOT_UNIQUELY_SUPPORTED"
            )

        else:
            validation_status = (
                "VALIDATED_SAME_SENTENCE_ANALOGICAL_EXPRESSION"
            )

            same_sentence_valid = True

            validation_reason = None

        validated = dict(
            candidate
        )

        validated.update({
            "same_sentence_analogical_validation_status":
                validation_status,

            "same_sentence_analogical_valid":
                same_sentence_valid,

            "same_sentence_analogical_validation_reason":
                validation_reason,

            "article_asserted_candidate_confirmed":
                article_asserted_candidate,

            "same_sentence_candidate_confirmed":
                same_sentence_candidate,

            "same_claim_unit_id_match":
                same_unit_identity,

            "same_sentence_id_match":
                same_sentence_identity,

            "same_sentence_source_text_supported":
                source_text_supported,

            "same_sentence_analogical_signal_supported":
                signal_supported,

            "analogical_signal_support_method":
                signal_support_method,

            "same_sentence_correspondence_supported":
                correspondence_supported,

            "same_sentence_analogical_structure_supported":
                structure_supported,

            "same_sentence_source_target_orientation_supported":
                orientation_supported,

            "same_sentence_analogy_source_supported":
                source_supported,

            "same_sentence_analogy_target_supported":
                target_supported,

            "same_sentence_unique_directional_grounding_supported":
                unique_directional_grounding_supported,

            "same_sentence_analogical_evidence": {
                "analogical_claim_unit_id":
                    canonical_unit_id,

                "sentence_id":
                    canonical_sentence_id,

                "sentence_text":
                    claim_text,

                "signal_type":
                    candidate.get(
                        "signal_type"
                    ),

                "signal_matched_text":
                    candidate.get(
                        "signal_matched_text"
                    ),

                "signal_character_start":
                    candidate.get(
                        "signal_character_start"
                    ),

                "signal_character_end":
                    candidate.get(
                        "signal_character_end"
                    ),

                "candidate_analogical_form":
                    candidate.get(
                        "candidate_analogical_form"
                    ),

                "analogy_orientation_pattern":
                    candidate.get(
                        "analogy_orientation_pattern"
                    ),

                "orientation_target_segment":
                    candidate.get(
                        "orientation_target_segment"
                    ),

                "orientation_source_segment":
                    candidate.get(
                        "orientation_source_segment"
                    ),

                "selected_analogy_target":
                    candidate.get(
                        "selected_analogy_target"
                    ),

                "selected_analogy_source":
                    candidate.get(
                        "selected_analogy_source"
                    ),

                "analogical_correspondence_validation_status":
                    candidate.get(
                        "analogical_correspondence_validation_status"
                    ),
            },

            "same_sentence_analogical_validated":
                same_sentence_valid,

            "cross_sentence_analogical_validated":
                False,

            "analogical_evidence_assessed":
                False,

            "duplicate_resolution_performed":
                False,

            "analogical_correspondence_mapped":
                False,

            "analogy_extended":
                False,

            "generic_similarity_reasoning_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,
        })

        validated_candidates.append(
            validated
        )

        validated_by_id[
            candidate_id
        ] = validated

    validated_units = []
    validated_units_by_id = {}

    for unit in source_units:
        unit_id = str(
            unit.get(
                "analogical_claim_unit_id"
            )
            or ""
        )

        state = dict(
            unit.get(
                "analogical_analysis_state"
            )
            or {}
        )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "analogical_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise AnalogicalIntelligenceError(
                    "Every unit Analogical Candidate reference must be a mapping."
                )

            candidate_id = str(
                old_candidate.get(
                    "analogical_candidate_id"
                )
                or ""
            )

            validated_candidate = (
                validated_by_id.get(
                    candidate_id
                )
            )

            if validated_candidate is None:
                raise AnalogicalIntelligenceError(
                    "Analogical candidate/unit same-sentence-validation mismatch."
                )

            unit_candidates.append(
                validated_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "same_sentence_analogical_validation"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "same_sentence_analogical_validation_performed"
        ] = True

        updated_boundaries[
            "cross_sentence_analogical_validation_performed"
        ] = False

        updated_boundaries[
            "analogical_correspondence_mapping_performed"
        ] = False

        updated_boundaries[
            "analogy_extension_performed"
        ] = False

        updated_boundaries[
            "generic_similarity_reasoning_performed"
        ] = False

        updated_boundaries[
            "procedural_reasoning_performed"
        ] = False

        updated_boundaries[
            "quantitative_reasoning_performed"
        ] = False

        updated_boundaries[
            "temporal_reasoning_performed"
        ] = False

        updated_boundaries[
            "new_causal_reasoning_performed"
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
            "analogical_candidates":
                unit_candidates,

            "same_sentence_analogical_validated_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "same_sentence_analogical_valid"
                    )
                    is True
                ),

            "same_sentence_analogical_not_validated_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "same_sentence_analogical_valid"
                    )
                    is False
                ),

            "analogical_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        if unit_id in validated_units_by_id:
            raise AnalogicalIntelligenceError(
                "Duplicate Analogical Claim Unit ID during Stage-I reconstruction."
            )

        validated_units.append(
            updated_unit
        )

        validated_units_by_id[
            unit_id
        ] = updated_unit

    validated_sections = []

    for section in (
        correspondence_result.get(
            "analogical_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every analogical section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "analogical_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise AnalogicalIntelligenceError(
                    "Every section Analogical Claim Unit reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "analogical_claim_unit_id"
                )
                or ""
            )

            validated_unit = (
                validated_units_by_id.get(
                    unit_id
                )
            )

            if validated_unit is None:
                raise AnalogicalIntelligenceError(
                    "Analogical section/unit same-sentence-validation mismatch."
                )

            section_units.append(
                validated_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "analogical_candidates"
                )
                or []
            )
        ]

        validated_sections.append({
            **dict(
                section
            ),

            "analogical_claim_units":
                section_units,

            "analogical_candidates":
                section_candidates,

            "same_sentence_analogical_validated_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "same_sentence_analogical_valid"
                    )
                    is True
                ),

            "same_sentence_analogical_not_validated_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "same_sentence_analogical_valid"
                    )
                    is False
                ),

            "same_sentence_analogical_validation_complete":
                True,
        })

    validated_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "same_sentence_analogical_valid"
        )
        is True
    )

    not_validated_count = (
        len(
            validated_candidates
        )
        - validated_count
    )

    result = dict(
        correspondence_result
    )

    result_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        result_boundaries.get(
            "analogical_correspondence_validation_performed"
        )
        is not True
    ):
        raise AnalogicalIntelligenceError(
            "Top-level Stage-H correspondence-validation boundary is incomplete."
        )

    if (
        result_boundaries.get(
            "same_sentence_analogical_validation_performed",
            False,
        )
        is not False
    ):
        raise AnalogicalIntelligenceError(
            "Top-level same-sentence analogical validation must not already be performed."
        )

    result_boundaries[
        "same_sentence_analogical_validation_performed"
    ] = True

    result_boundaries[
        "cross_sentence_analogical_validation_performed"
    ] = False

    result_boundaries[
        "analogical_correspondence_mapping_performed"
    ] = False

    result_boundaries[
        "analogy_extension_performed"
    ] = False

    result_boundaries[
        "generic_similarity_reasoning_performed"
    ] = False

    result_boundaries[
        "procedural_reasoning_performed"
    ] = False

    result_boundaries[
        "quantitative_reasoning_performed"
    ] = False

    result_boundaries[
        "temporal_reasoning_performed"
    ] = False

    result_boundaries[
        "new_causal_reasoning_performed"
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
            "analogical_same_sentence_validation_v1",

        "patch":
            "4.6.11I",

        "status":
            "ANALOGICAL_SAME_SENTENCE_VALIDATION_COMPLETE",

        "analogical_sections":
            validated_sections,

        "analogical_claim_units":
            validated_units,

        "analogical_candidates":
            validated_candidates,

        "same_sentence_analogical_validation_summary": {
            "candidate_count":
                len(
                    validated_candidates
                ),

            "same_sentence_analogical_validated_count":
                validated_count,

            "same_sentence_analogical_not_validated_count":
                not_validated_count,

            "candidate_count_accounted_for":
                (
                    validated_count
                    + not_validated_count
                    == len(
                        validated_candidates
                    )
                ),

            "stage_h_valid_correspondence_required":
                True,

            "article_asserted_candidate_required":
                True,

            "same_sentence_candidate_required":
                True,

            "claim_unit_identity_required":
                True,

            "sentence_identity_required":
                True,

            "source_text_continuity_required":
                True,

            "exact_signal_span_support_required":
                True,

            "analogical_structure_support_required":
                True,

            "resolved_source_target_orientation_required":
                True,

            "selected_source_target_required":
                True,

            "unique_directional_grounding_required":
                True,

            "correspondence_mapping_performed":
                False,

            "property_level_mapping_performed":
                False,

            "neighbor_sentence_rescue_performed":
                False,

            "cross_sentence_analogical_validation_performed":
                False,

            "analogy_extension_performed":
                False,

            "generic_similarity_reasoning_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            result_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "cross_sentence_analogical_validation",
    })

    return result


def validate_cross_sentence_analogical_v1(
    same_sentence_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Assess immediate same-section adjacent-sentence corroboration for
    already-established article-local analogical expressions.

    Cross-sentence support is conservative:
    - only sentence distance 1 is eligible,
    - only within the same section,
    - Stage-I same-sentence analogical validity remains authoritative,
    - adjacent sentences may provide corroborating article-local
      source/target context,
    - adjacency may NOT create an analogy,
    - adjacency may NOT rescue an invalid analogy,
    - adjacency may NOT create source/target orientation,
    - adjacency may NOT create analogical correspondence,
    - adjacency may NOT map analogy properties,
    - adjacency may NOT extend an analogy.

    It does NOT:
    - create new analogical candidates,
    - create new entity/concept groundings,
    - create or repair source/target orientation,
    - create or repair correspondence validity,
    - perform correspondence/property mapping,
    - extend an analogy,
    - perform generic similarity reasoning,
    - perform procedural reasoning,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - perform new causal reasoning,
    - establish factual/scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    import re

    if not isinstance(
        same_sentence_result,
        Mapping,
    ):
        raise AnalogicalIntelligenceError(
            "same_sentence_result must be a mapping."
        )

    if (
        same_sentence_result.get(
            "schema_version"
        )
        != "analogical_same_sentence_validation_v1"
    ):
        raise AnalogicalIntelligenceError(
            "Stage J requires analogical_same_sentence_validation_v1."
        )

    if (
        same_sentence_result.get(
            "status"
        )
        != "ANALOGICAL_SAME_SENTENCE_VALIDATION_COMPLETE"
    ):
        raise AnalogicalIntelligenceError(
            "Same-sentence analogical validation must be complete before Stage J."
        )

    if (
        same_sentence_result.get(
            "phase"
        )
        != "4.6.11"
    ):
        raise AnalogicalIntelligenceError(
            "Stage J requires Phase 4.6.11 input."
        )

    if (
        same_sentence_result.get(
            "patch"
        )
        != "4.6.11I"
    ):
        raise AnalogicalIntelligenceError(
            "Stage J requires canonical 4.6.11I input."
        )

    if (
        same_sentence_result.get(
            "next_stage"
        )
        != "cross_sentence_analogical_validation"
    ):
        raise AnalogicalIntelligenceError(
            "Stage I must hand off to cross_sentence_analogical_validation."
        )

    if (
        same_sentence_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise AnalogicalIntelligenceError(
            "Analogical Intelligence must remain transient."
        )

    source_units = list(
        same_sentence_result.get(
            "analogical_claim_units"
        )
        or []
    )

    if not source_units:
        raise AnalogicalIntelligenceError(
            "Analogical Claim Units are required."
        )

    unit_records = []
    seen_unit_ids = set()
    seen_sentence_ids = set()
    previous_global_index = None

    for position, unit in enumerate(
        source_units
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every Analogical Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "analogical_claim_unit_id"
            )
            or ""
        )

        sentence_id = str(
            unit.get(
                "sentence_id"
            )
            or ""
        )

        section_id = str(
            unit.get(
                "section_id"
            )
            or ""
        )

        claim_text = str(
            unit.get(
                "text"
            )
            or ""
        ).strip()

        sentence_global_index = unit.get(
            "sentence_global_index"
        )

        if not unit_id:
            raise AnalogicalIntelligenceError(
                "Analogical Claim Unit ID is required."
            )

        if unit_id in seen_unit_ids:
            raise AnalogicalIntelligenceError(
                "Duplicate Analogical Claim Unit ID detected."
            )

        seen_unit_ids.add(
            unit_id
        )

        if not sentence_id:
            raise AnalogicalIntelligenceError(
                "Analogical Claim Unit sentence_id is required."
            )

        if sentence_id in seen_sentence_ids:
            raise AnalogicalIntelligenceError(
                "Duplicate analogical sentence_id detected."
            )

        seen_sentence_ids.add(
            sentence_id
        )

        if not section_id:
            raise AnalogicalIntelligenceError(
                "Analogical Claim Unit section_id is required."
            )

        if not claim_text:
            raise AnalogicalIntelligenceError(
                "Analogical Claim Unit text is required."
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
            raise AnalogicalIntelligenceError(
                "sentence_global_index must be an integer."
            )

        if (
            previous_global_index is not None
            and sentence_global_index
            <= previous_global_index
        ):
            raise AnalogicalIntelligenceError(
                "Analogical Claim Units are not in canonical sentence order."
            )

        previous_global_index = (
            sentence_global_index
        )

        state = dict(
            unit.get(
                "analogical_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "same_sentence_analogical_validation"
            )
            != "COMPLETE"
        ):
            raise AnalogicalIntelligenceError(
                "Same-sentence analogical validation must be COMPLETE before Stage J."
            )

        if (
            state.get(
                "cross_sentence_analogical_validation"
            )
            != "PENDING"
        ):
            raise AnalogicalIntelligenceError(
                "Cross-sentence analogical validation must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "same_sentence_analogical_validation_performed"
            )
            is not True
        ):
            raise AnalogicalIntelligenceError(
                "Stage-I same-sentence analogical validation boundary is incomplete."
            )

        required_false_boundaries = (
            "cross_sentence_analogical_validation_performed",
            "analogical_correspondence_mapping_performed",
            "analogy_extension_performed",
            "generic_similarity_reasoning_performed",
            "procedural_reasoning_performed",
            "quantitative_reasoning_performed",
            "temporal_reasoning_performed",
            "new_causal_reasoning_performed",
            "truth_assessment_performed",
            "external_authority_check_performed",
            "semantic_memory_write_performed",
            "persistence_performed",
        )

        for boundary_name in required_false_boundaries:
            if (
                boundaries.get(
                    boundary_name,
                    False,
                )
                is not False
            ):
                raise AnalogicalIntelligenceError(
                    boundary_name
                    + " must be False before Stage J."
                )

        unit_records.append({
            "position":
                position,

            "unit":
                unit,

            "unit_id":
                unit_id,

            "sentence_id":
                sentence_id,

            "section_id":
                section_id,

            "sentence_global_index":
                sentence_global_index,

            "text":
                claim_text,
        })

    candidate_to_record = {}

    for record in unit_records:
        for candidate in (
            record[
                "unit"
            ].get(
                "analogical_candidates"
            )
            or []
        ):
            if not isinstance(
                candidate,
                Mapping,
            ):
                raise AnalogicalIntelligenceError(
                    "Every analogical candidate must be a mapping."
                )

            candidate_id = str(
                candidate.get(
                    "analogical_candidate_id"
                )
                or ""
            )

            if not candidate_id:
                raise AnalogicalIntelligenceError(
                    "Analogical Candidate ID is required."
                )

            if candidate_id in candidate_to_record:
                raise AnalogicalIntelligenceError(
                    "Duplicate Analogical Candidate ID detected."
                )

            candidate_to_record[
                candidate_id
            ] = record

    def normalize_text(
        value: Any,
    ) -> str:
        value = str(
            value
            or ""
        ).lower()

        value = value.replace(
            "\u2019",
            "'",
        )

        value = value.replace(
            "\u2018",
            "'",
        )

        value = value.replace(
            "\u2013",
            "-",
        )

        value = value.replace(
            "\u2014",
            "-",
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()

    def collect_candidate_terms(
        candidate: Mapping[str, Any],
    ) -> list[str]:
        terms = []

        for selected_key in (
            "selected_analogy_target",
            "selected_analogy_source",
        ):
            selected = candidate.get(
                selected_key
            )

            if not isinstance(
                selected,
                Mapping,
            ):
                continue

            for key in (
                "canonical_text",
                "matched_surface_form",
            ):
                term = normalize_text(
                    selected.get(
                        key
                    )
                )

                if (
                    term
                    and term not in terms
                ):
                    terms.append(
                        term
                    )

        for grounding in (
            candidate.get(
                "entity_concept_grounding_matches"
            )
            or []
        ):
            if not isinstance(
                grounding,
                Mapping,
            ):
                continue

            for key in (
                "canonical_text",
                "matched_surface_form",
            ):
                term = normalize_text(
                    grounding.get(
                        key
                    )
                )

                if (
                    term
                    and term not in terms
                ):
                    terms.append(
                        term
                    )

        return terms

    def collect_adjacent_support(
        candidate: Mapping[str, Any],
        adjacent_records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        support = []

        candidate_terms = collect_candidate_terms(
            candidate
        )

        if not candidate_terms:
            return support

        for adjacent in adjacent_records:
            adjacent_text = normalize_text(
                adjacent[
                    "text"
                ]
            )

            matched_terms = sorted(
                term
                for term in candidate_terms
                if (
                    term
                    and re.search(
                        r"(?<!\w)"
                        + re.escape(
                            term
                        )
                        + r"(?!\w)",
                        adjacent_text,
                    )
                )
            )

            if not matched_terms:
                continue

            support.append({
                "sentence_id":
                    adjacent[
                        "sentence_id"
                    ],

                "section_id":
                    adjacent[
                        "section_id"
                    ],

                "sentence_global_index":
                    adjacent[
                        "sentence_global_index"
                    ],

                "sentence_text":
                    adjacent[
                        "text"
                    ],

                "sentence_distance":
                    1,

                "matched_article_local_terms":
                    matched_terms,

                "support_type":
                    "ADJACENT_ANALOGICAL_CONTEXT_CORROBORATION",

                "selected_analogy_target":
                    candidate.get(
                        "selected_analogy_target"
                    ),

                "selected_analogy_source":
                    candidate.get(
                        "selected_analogy_source"
                    ),

                "creates_analogical_expression":
                    False,

                "creates_source_target_orientation":
                    False,

                "creates_analogical_correspondence":
                    False,

                "maps_analogical_properties":
                    False,

                "extends_analogy":
                    False,
            })

        return support

    source_candidates = list(
        same_sentence_result.get(
            "analogical_candidates"
        )
        or []
    )

    validated_candidates = []
    validated_by_id = {}

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every analogical candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "analogical_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise AnalogicalIntelligenceError(
                "Analogical Candidate ID is required."
            )

        if candidate_id in validated_by_id:
            raise AnalogicalIntelligenceError(
                "Duplicate top-level Analogical Candidate ID detected."
            )

        record = candidate_to_record.get(
            candidate_id
        )

        if record is None:
            raise AnalogicalIntelligenceError(
                "Analogical candidate has no canonical claim unit."
            )

        if (
            candidate.get(
                "cross_sentence_analogical_validated"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Candidate must not already be cross-sentence analogically validated."
            )

        if (
            candidate.get(
                "analogical_correspondence_mapped"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Stage J must not receive a mapped analogical correspondence."
            )

        if (
            candidate.get(
                "analogy_extended"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Stage J must not receive an extended analogy."
            )

        same_sentence_valid = (
            candidate.get(
                "same_sentence_analogical_valid"
            )
            is True
        )

        article_asserted_confirmed = (
            candidate.get(
                "article_asserted_candidate_confirmed"
            )
            is True
        )

        same_sentence_candidate_confirmed = (
            candidate.get(
                "same_sentence_candidate_confirmed"
            )
            is True
        )

        same_unit_match = (
            candidate.get(
                "same_claim_unit_id_match"
            )
            is True
        )

        same_sentence_id_match = (
            candidate.get(
                "same_sentence_id_match"
            )
            is True
        )

        same_source_text_supported = (
            candidate.get(
                "same_sentence_source_text_supported"
            )
            is True
        )

        same_signal_supported = (
            candidate.get(
                "same_sentence_analogical_signal_supported"
            )
            is True
        )

        correspondence_supported = (
            candidate.get(
                "same_sentence_correspondence_supported"
            )
            is True
        )

        structure_supported = (
            candidate.get(
                "same_sentence_analogical_structure_supported"
            )
            is True
        )

        orientation_supported = (
            candidate.get(
                "same_sentence_source_target_orientation_supported"
            )
            is True
        )

        source_supported = (
            candidate.get(
                "same_sentence_analogy_source_supported"
            )
            is True
        )

        target_supported = (
            candidate.get(
                "same_sentence_analogy_target_supported"
            )
            is True
        )

        unique_grounding_supported = (
            candidate.get(
                "same_sentence_unique_directional_grounding_supported"
            )
            is True
        )

        adjacent_records = []

        for other in unit_records:
            if (
                other[
                    "unit_id"
                ]
                == record[
                    "unit_id"
                ]
            ):
                continue

            if (
                other[
                    "section_id"
                ]
                != record[
                    "section_id"
                ]
            ):
                continue

            distance = abs(
                other[
                    "sentence_global_index"
                ]
                - record[
                    "sentence_global_index"
                ]
            )

            if distance == 1:
                adjacent_records.append(
                    other
                )

        adjacent_records.sort(
            key=lambda item: (
                item[
                    "sentence_global_index"
                ],
            )
        )

        eligible_for_adjacent_support = (
            same_sentence_valid
            and article_asserted_confirmed
            and same_sentence_candidate_confirmed
            and same_unit_match
            and same_sentence_id_match
            and same_source_text_supported
            and same_signal_supported
            and correspondence_supported
            and structure_supported
            and orientation_supported
            and source_supported
            and target_supported
            and unique_grounding_supported
        )

        adjacent_support_evidence = []

        if eligible_for_adjacent_support:
            adjacent_support_evidence = (
                collect_adjacent_support(
                    candidate,
                    adjacent_records,
                )
            )

        adjacent_support_present = bool(
            adjacent_support_evidence
        )

        if not article_asserted_confirmed:
            cross_sentence_status = (
                "NOT_VALIDATED_ARTICLE_ASSERTION_FAILED"
            )

            cross_sentence_valid = False
            final_analogical_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_CREATE_ARTICLE_ASSERTION"
            )

        elif not same_sentence_candidate_confirmed:
            cross_sentence_status = (
                "NOT_VALIDATED_SAME_SENTENCE_CANDIDATE_ASSERTION_FAILED"
            )

            cross_sentence_valid = False
            final_analogical_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_CREATE_SAME_SENTENCE_CANDIDATE"
            )

        elif not same_unit_match:
            cross_sentence_status = (
                "NOT_VALIDATED_CLAIM_UNIT_MISMATCH"
            )

            cross_sentence_valid = False
            final_analogical_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_REPAIR_CLAIM_UNIT_IDENTITY"
            )

        elif not same_sentence_id_match:
            cross_sentence_status = (
                "NOT_VALIDATED_SENTENCE_ID_MISMATCH"
            )

            cross_sentence_valid = False
            final_analogical_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_REPAIR_SENTENCE_IDENTITY"
            )

        elif not same_source_text_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_SOURCE_TEXT_MISMATCH"
            )

            cross_sentence_valid = False
            final_analogical_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_REPAIR_SOURCE_TEXT_CONTINUITY"
            )

        elif not same_signal_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_PRIMARY_ANALOGICAL_SIGNAL_UNSUPPORTED"
            )

            cross_sentence_valid = False
            final_analogical_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_CREATE_PRIMARY_ANALOGICAL_SIGNAL"
            )

        elif not correspondence_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_ANALOGICAL_CORRESPONDENCE_UNSUPPORTED"
            )

            cross_sentence_valid = False
            final_analogical_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_CREATE_ANALOGICAL_CORRESPONDENCE"
            )

        elif not structure_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_ANALOGICAL_STRUCTURE_UNSUPPORTED"
            )

            cross_sentence_valid = False
            final_analogical_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_CREATE_ANALOGICAL_STRUCTURE"
            )

        elif not orientation_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_SOURCE_TARGET_ORIENTATION_UNRESOLVED"
            )

            cross_sentence_valid = False
            final_analogical_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_CREATE_SOURCE_TARGET_ORIENTATION"
            )

        elif not source_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_ANALOGY_SOURCE_UNSUPPORTED"
            )

            cross_sentence_valid = False
            final_analogical_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_CREATE_ANALOGY_SOURCE_SELECTION"
            )

        elif not target_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_ANALOGY_TARGET_UNSUPPORTED"
            )

            cross_sentence_valid = False
            final_analogical_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_CREATE_ANALOGY_TARGET_SELECTION"
            )

        elif not unique_grounding_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_DIRECTIONAL_GROUNDING_NOT_UNIQUE"
            )

            cross_sentence_valid = False
            final_analogical_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_REPAIR_DIRECTIONAL_GROUNDING"
            )

        elif same_sentence_valid:
            cross_sentence_status = (
                "NOT_REQUIRED_SAME_SENTENCE_VALIDATION_SUFFICIENT"
            )

            cross_sentence_valid = False
            final_analogical_expression_validated = True

            validation_reason = (
                "SAME_SENTENCE_ANALOGICAL_VALIDATION_ALREADY_SUFFICIENT"
            )

        else:
            cross_sentence_status = (
                "NOT_VALIDATED_SAME_SENTENCE_EXPRESSION_INSUFFICIENT"
            )

            cross_sentence_valid = False
            final_analogical_expression_validated = False

            validation_reason = (
                "CROSS_SENTENCE_PROXIMITY_CANNOT_CREATE_ANALOGICAL_EXPRESSION"
            )

        validated = dict(
            candidate
        )

        validated.update({
            "cross_sentence_analogical_validation_status":
                cross_sentence_status,

            "cross_sentence_analogical_valid":
                cross_sentence_valid,

            "cross_sentence_analogical_validation_reason":
                validation_reason,

            "adjacent_same_section_sentence_count":
                len(
                    adjacent_records
                ),

            "adjacent_analogical_support_present":
                adjacent_support_present,

            "adjacent_analogical_support_count":
                len(
                    adjacent_support_evidence
                ),

            "adjacent_analogical_support_evidence":
                adjacent_support_evidence,

            "cross_sentence_adjacency_policy":
                "IMMEDIATE_SENTENCE_DISTANCE_1_SAME_SECTION_ONLY",

            "cross_sentence_support_policy":
                (
                    "CORROBORATION_ONLY_FOR_ALREADY_VALIDATED_"
                    "SAME_SENTENCE_ANALOGICAL_EXPRESSION"
                ),

            "adjacent_sentence_may_create_analogical_expression":
                False,

            "adjacent_sentence_may_create_source_target_orientation":
                False,

            "adjacent_sentence_may_create_analogical_correspondence":
                False,

            "adjacent_sentence_may_map_analogical_properties":
                False,

            "adjacent_sentence_may_extend_analogy":
                False,

            "final_analogical_expression_validated":
                final_analogical_expression_validated,

            "cross_sentence_analogical_validated":
                cross_sentence_valid,

            "analogical_evidence_assessed":
                False,

            "duplicate_resolution_performed":
                False,

            "analogical_correspondence_mapped":
                False,

            "analogy_extended":
                False,

            "generic_similarity_reasoning_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,
        })

        validated_candidates.append(
            validated
        )

        validated_by_id[
            candidate_id
        ] = validated

    validated_units = []
    validated_units_by_id = {}

    for record in unit_records:
        unit = record[
            "unit"
        ]

        unit_id = record[
            "unit_id"
        ]

        state = dict(
            unit.get(
                "analogical_analysis_state"
            )
            or {}
        )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "analogical_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise AnalogicalIntelligenceError(
                    "Every unit Analogical Candidate reference must be a mapping."
                )

            candidate_id = str(
                old_candidate.get(
                    "analogical_candidate_id"
                )
                or ""
            )

            validated_candidate = (
                validated_by_id.get(
                    candidate_id
                )
            )

            if validated_candidate is None:
                raise AnalogicalIntelligenceError(
                    "Analogical candidate/unit cross-sentence validation mismatch."
                )

            unit_candidates.append(
                validated_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "cross_sentence_analogical_validation"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "cross_sentence_analogical_validation_performed"
        ] = True

        updated_boundaries[
            "analogical_correspondence_mapping_performed"
        ] = False

        updated_boundaries[
            "analogy_extension_performed"
        ] = False

        updated_boundaries[
            "generic_similarity_reasoning_performed"
        ] = False

        updated_boundaries[
            "procedural_reasoning_performed"
        ] = False

        updated_boundaries[
            "quantitative_reasoning_performed"
        ] = False

        updated_boundaries[
            "temporal_reasoning_performed"
        ] = False

        updated_boundaries[
            "new_causal_reasoning_performed"
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
            "analogical_candidates":
                unit_candidates,

            "adjacent_support_candidate_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "adjacent_analogical_support_present"
                    )
                    is True
                ),

            "final_analogical_expression_validated_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "final_analogical_expression_validated"
                    )
                    is True
                ),

            "cross_sentence_analogical_validated_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "cross_sentence_analogical_valid"
                    )
                    is True
                ),

            "analogical_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        if unit_id in validated_units_by_id:
            raise AnalogicalIntelligenceError(
                "Duplicate Analogical Claim Unit ID during Stage-J reconstruction."
            )

        validated_units.append(
            updated_unit
        )

        validated_units_by_id[
            unit_id
        ] = updated_unit

    validated_sections = []

    for section in (
        same_sentence_result.get(
            "analogical_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every analogical section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "analogical_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise AnalogicalIntelligenceError(
                    "Every section Analogical Claim Unit reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "analogical_claim_unit_id"
                )
                or ""
            )

            validated_unit = (
                validated_units_by_id.get(
                    unit_id
                )
            )

            if validated_unit is None:
                raise AnalogicalIntelligenceError(
                    "Analogical section/unit cross-sentence validation mismatch."
                )

            section_units.append(
                validated_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "analogical_candidates"
                )
                or []
            )
        ]

        validated_sections.append({
            **dict(
                section
            ),

            "analogical_claim_units":
                section_units,

            "analogical_candidates":
                section_candidates,

            "adjacent_support_candidate_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "adjacent_analogical_support_present"
                    )
                    is True
                ),

            "final_analogical_expression_validated_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "final_analogical_expression_validated"
                    )
                    is True
                ),

            "cross_sentence_analogical_validation_complete":
                True,
        })

    same_sentence_validated_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "same_sentence_analogical_valid"
        )
        is True
    )

    adjacent_support_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "adjacent_analogical_support_present"
        )
        is True
    )

    cross_sentence_validated_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "cross_sentence_analogical_valid"
        )
        is True
    )

    final_validated_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "final_analogical_expression_validated"
        )
        is True
    )

    final_not_validated_count = (
        len(
            validated_candidates
        )
        - final_validated_count
    )

    result = dict(
        same_sentence_result
    )

    result_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        result_boundaries.get(
            "same_sentence_analogical_validation_performed"
        )
        is not True
    ):
        raise AnalogicalIntelligenceError(
            "Top-level Stage-I same-sentence analogical validation boundary is incomplete."
        )

    if (
        result_boundaries.get(
            "cross_sentence_analogical_validation_performed"
        )
        is not False
    ):
        raise AnalogicalIntelligenceError(
            "Top-level cross-sentence analogical validation must not already be performed."
        )

    result_boundaries[
        "cross_sentence_analogical_validation_performed"
    ] = True

    result_boundaries[
        "analogical_correspondence_mapping_performed"
    ] = False

    result_boundaries[
        "analogy_extension_performed"
    ] = False

    result_boundaries[
        "generic_similarity_reasoning_performed"
    ] = False

    result_boundaries[
        "procedural_reasoning_performed"
    ] = False

    result_boundaries[
        "quantitative_reasoning_performed"
    ] = False

    result_boundaries[
        "temporal_reasoning_performed"
    ] = False

    result_boundaries[
        "new_causal_reasoning_performed"
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
            "analogical_cross_sentence_validation_v1",

        "patch":
            "4.6.11J",

        "status":
            "ANALOGICAL_CROSS_SENTENCE_VALIDATION_COMPLETE",

        "analogical_sections":
            validated_sections,

        "analogical_claim_units":
            validated_units,

        "analogical_candidates":
            validated_candidates,

        "cross_sentence_analogical_validation_summary": {
            "candidate_count":
                len(
                    validated_candidates
                ),

            "already_same_sentence_validated_count":
                same_sentence_validated_count,

            "adjacent_support_candidate_count":
                adjacent_support_count,

            "cross_sentence_analogical_validated_count":
                cross_sentence_validated_count,

            "final_analogical_expression_validated_count":
                final_validated_count,

            "final_analogical_expression_not_validated_count":
                final_not_validated_count,

            "candidate_count_accounted_for":
                (
                    final_validated_count
                    + final_not_validated_count
                    == len(
                        validated_candidates
                    )
                ),

            "adjacency_policy":
                "IMMEDIATE_SENTENCE_DISTANCE_1_SAME_SECTION_ONLY",

            "adjacent_sentence_support_role":
                "CORROBORATION_ONLY",

            "same_sentence_primary_expression_required":
                True,

            "adjacent_sentence_may_create_analogical_expression":
                False,

            "adjacent_sentence_may_create_source_target_orientation":
                False,

            "adjacent_sentence_may_create_analogical_correspondence":
                False,

            "adjacent_sentence_may_map_analogical_properties":
                False,

            "adjacent_sentence_may_extend_analogy":
                False,

            "proximity_based_analogical_inference_performed":
                False,

            "correspondence_mapping_performed":
                False,

            "property_level_mapping_performed":
                False,

            "analogical_evidence_assessment_performed":
                False,

            "generic_similarity_reasoning_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            result_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "analogical_evidence_confidence_assessment",
    })

    return result


def assess_analogical_confidence_evidence_v1(
    cross_sentence_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Assess article-local evidence strength for analogical expressions
    already processed through correspondence, same-sentence, and
    cross-sentence validation.

    Confidence measures how strongly the article itself supports the
    extracted analogy. It does NOT measure factual, scientific,
    explanatory, medical, operational, or real-world truth.

    Safeguards:
    - unvalidated analogical expressions receive zero confidence,
    - exact same-sentence analogical support is authoritative,
    - adjacent-sentence evidence is corroborative only,
    - source and target must remain uniquely directionally grounded,
    - two directional grounding records are expected and are not treated
      as ambiguity,
    - source/target extraction confidence comes only from Stage-F
      article-local semantic-object extraction,
    - no new analogy, mapping, extension, or similarity reasoning occurs.

    This stage does NOT:
    - create an analogical candidate,
    - rescue an invalid analogy,
    - create source/target orientation,
    - select new source or target concepts,
    - create analogical correspondence,
    - map correspondence properties,
    - extend an analogy,
    - perform generic similarity reasoning,
    - perform procedural reasoning,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - perform new causal reasoning,
    - establish factual/scientific truth,
    - perform external verification,
    - resolve duplicate analogical expressions,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        cross_sentence_result,
        Mapping,
    ):
        raise AnalogicalIntelligenceError(
            "cross_sentence_result must be a mapping."
        )

    if (
        cross_sentence_result.get(
            "schema_version"
        )
        != "analogical_cross_sentence_validation_v1"
    ):
        raise AnalogicalIntelligenceError(
            "Stage K requires analogical_cross_sentence_validation_v1."
        )

    if (
        cross_sentence_result.get(
            "status"
        )
        != "ANALOGICAL_CROSS_SENTENCE_VALIDATION_COMPLETE"
    ):
        raise AnalogicalIntelligenceError(
            "Cross-sentence analogical validation must be complete."
        )

    if (
        cross_sentence_result.get(
            "phase"
        )
        != "4.6.11"
    ):
        raise AnalogicalIntelligenceError(
            "Stage K requires Phase 4.6.11 input."
        )

    if (
        cross_sentence_result.get(
            "patch"
        )
        != "4.6.11J"
    ):
        raise AnalogicalIntelligenceError(
            "Stage K requires canonical 4.6.11J input."
        )

    if (
        cross_sentence_result.get(
            "next_stage"
        )
        != "analogical_evidence_confidence_assessment"
    ):
        raise AnalogicalIntelligenceError(
            "Stage J must hand off to analogical_evidence_confidence_assessment."
        )

    if (
        cross_sentence_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise AnalogicalIntelligenceError(
            "Analogical Intelligence must remain transient."
        )

    source_candidates = list(
        cross_sentence_result.get(
            "analogical_candidates"
        )
        or []
    )

    assessed_candidates = []
    seen_candidate_ids = set()

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every analogical candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "analogical_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise AnalogicalIntelligenceError(
                "Analogical Candidate ID is required."
            )

        if candidate_id in seen_candidate_ids:
            raise AnalogicalIntelligenceError(
                "Duplicate Analogical Candidate ID detected."
            )

        seen_candidate_ids.add(
            candidate_id
        )

        evidence_state = candidate.get(
            "analogical_evidence_assessed"
        )

        if (
            evidence_state is True
            or (
                evidence_state is not False
                and evidence_state is not None
            )
        ):
            raise AnalogicalIntelligenceError(
                "Candidate must not already have analogical evidence assessment."
            )

        if (
            candidate.get(
                "analogical_correspondence_mapped"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Stage K must not receive a mapped analogical correspondence."
            )

        if (
            candidate.get(
                "analogy_extended"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Stage K must not receive an extended analogy."
            )

        final_validated = (
            candidate.get(
                "final_analogical_expression_validated"
            )
            is True
        )

        same_sentence_valid = (
            candidate.get(
                "same_sentence_analogical_valid"
            )
            is True
        )

        cross_sentence_valid = (
            candidate.get(
                "cross_sentence_analogical_valid"
            )
            is True
        )

        article_asserted_confirmed = (
            candidate.get(
                "article_asserted_candidate_confirmed"
            )
            is True
        )

        same_sentence_candidate_confirmed = (
            candidate.get(
                "same_sentence_candidate_confirmed"
            )
            is True
        )

        exact_signal_supported = (
            candidate.get(
                "same_sentence_analogical_signal_supported"
            )
            is True
        )

        correspondence_supported = (
            candidate.get(
                "same_sentence_correspondence_supported"
            )
            is True
        )

        structure_supported = (
            candidate.get(
                "same_sentence_analogical_structure_supported"
            )
            is True
        )

        orientation_supported = (
            candidate.get(
                "same_sentence_source_target_orientation_supported"
            )
            is True
        )

        source_supported = (
            candidate.get(
                "same_sentence_analogy_source_supported"
            )
            is True
        )

        target_supported = (
            candidate.get(
                "same_sentence_analogy_target_supported"
            )
            is True
        )

        unique_directional_grounding = (
            candidate.get(
                "same_sentence_unique_directional_grounding_supported"
            )
            is True
        )

        adjacent_support_present = (
            candidate.get(
                "adjacent_analogical_support_present"
            )
            is True
        )

        target_matches = list(
            candidate.get(
                "target_side_grounding_matches"
            )
            or []
        )

        source_matches = list(
            candidate.get(
                "source_side_grounding_matches"
            )
            or []
        )

        target_count = candidate.get(
            "target_side_grounding_match_count"
        )

        source_count = candidate.get(
            "source_side_grounding_match_count"
        )

        overlap_count = candidate.get(
            "cross_side_grounding_overlap_count"
        )

        for name, value in (
            (
                "target_side_grounding_match_count",
                target_count,
            ),
            (
                "source_side_grounding_match_count",
                source_count,
            ),
            (
                "cross_side_grounding_overlap_count",
                overlap_count,
            ),
        ):
            if (
                not isinstance(
                    value,
                    int,
                )
                or isinstance(
                    value,
                    bool,
                )
                or value < 0
            ):
                raise AnalogicalIntelligenceError(
                    name
                    + " must be a non-negative integer."
                )

        if target_count != len(
            target_matches
        ):
            raise AnalogicalIntelligenceError(
                "Target-side grounding count mismatch."
            )

        if source_count != len(
            source_matches
        ):
            raise AnalogicalIntelligenceError(
                "Source-side grounding count mismatch."
            )

        selected_target = candidate.get(
            "selected_analogy_target"
        )

        selected_source = candidate.get(
            "selected_analogy_source"
        )

        directional_confidences = []

        if final_validated:
            if not (
                article_asserted_confirmed
                and same_sentence_candidate_confirmed
                and exact_signal_supported
                and correspondence_supported
                and structure_supported
                and orientation_supported
                and source_supported
                and target_supported
                and unique_directional_grounding
            ):
                raise AnalogicalIntelligenceError(
                    "Final validated analogical candidate has inconsistent Stage-I support."
                )

            if (
                not same_sentence_valid
                and not cross_sentence_valid
            ):
                raise AnalogicalIntelligenceError(
                    "Final validated analogical candidate has no recognized validation mode."
                )

            if (
                target_count != 1
                or source_count != 1
                or overlap_count != 0
            ):
                raise AnalogicalIntelligenceError(
                    "Final validated analogy must have exactly one unique grounding per directional side and zero overlap."
                )

            if not isinstance(
                selected_target,
                Mapping,
            ):
                raise AnalogicalIntelligenceError(
                    "Final validated analogy requires selected_analogy_target."
                )

            if not isinstance(
                selected_source,
                Mapping,
            ):
                raise AnalogicalIntelligenceError(
                    "Final validated analogy requires selected_analogy_source."
                )

            for role, grounding in (
                (
                    "target",
                    selected_target,
                ),
                (
                    "source",
                    selected_source,
                ),
            ):
                confidence = grounding.get(
                    "extraction_confidence"
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
                    raise AnalogicalIntelligenceError(
                        "Selected analogy "
                        + role
                        + " has invalid extraction_confidence."
                    )

                directional_confidences.append(
                    float(
                        confidence
                    )
                )

            target_ref = str(
                selected_target.get(
                    "grounding_ref"
                )
                or ""
            )

            source_ref = str(
                selected_source.get(
                    "grounding_ref"
                )
                or ""
            )

            if not target_ref:
                raise AnalogicalIntelligenceError(
                    "Selected analogy target requires grounding_ref."
                )

            if not source_ref:
                raise AnalogicalIntelligenceError(
                    "Selected analogy source requires grounding_ref."
                )

            target_match_refs = {
                str(
                    grounding.get(
                        "grounding_ref"
                    )
                    or ""
                )
                for grounding in target_matches
                if isinstance(
                    grounding,
                    Mapping,
                )
            }

            source_match_refs = {
                str(
                    grounding.get(
                        "grounding_ref"
                    )
                    or ""
                )
                for grounding in source_matches
                if isinstance(
                    grounding,
                    Mapping,
                )
            }

            if target_ref not in target_match_refs:
                raise AnalogicalIntelligenceError(
                    "Selected analogy target does not match target-side grounding evidence."
                )

            if source_ref not in source_match_refs:
                raise AnalogicalIntelligenceError(
                    "Selected analogy source does not match source-side grounding evidence."
                )

        if directional_confidences:
            directional_grounding_confidence = round(
                sum(
                    directional_confidences
                )
                / len(
                    directional_confidences
                ),
                3,
            )

        else:
            directional_grounding_confidence = None

        if not final_validated:
            evidence_score = 0.0

            evidence_strength = (
                "INSUFFICIENT"
            )

            primary_basis = (
                "ANALOGICAL_EXPRESSION_NOT_VALIDATED"
            )

            confidence_cap_applied = None

        else:
            evidence_score = 0.48

            if same_sentence_valid:
                evidence_score += 0.24

                primary_basis = (
                    "SAME_SENTENCE_ANALOGICAL_EXPRESSION_VALIDATED"
                )

            elif cross_sentence_valid:
                evidence_score += 0.10

                primary_basis = (
                    "CROSS_SENTENCE_ANALOGICAL_EXPRESSION_VALIDATED"
                )

            else:
                raise AnalogicalIntelligenceError(
                    "Final validated analogical candidate has no recognized validation mode."
                )

            if unique_directional_grounding:
                evidence_score += 0.08

            if directional_grounding_confidence is not None:
                evidence_score += (
                    directional_grounding_confidence
                    * 0.08
                )

            if (
                correspondence_supported
                and structure_supported
                and orientation_supported
                and source_supported
                and target_supported
            ):
                evidence_score += 0.04

            if adjacent_support_present:
                evidence_score += 0.03

            evidence_score = min(
                evidence_score,
                0.95,
            )

            confidence_cap_applied = None

            if cross_sentence_valid:
                if evidence_score > 0.79:
                    evidence_score = 0.79

                    confidence_cap_applied = (
                        "CROSS_SENTENCE_MAX_MODERATE"
                    )

            evidence_score = round(
                evidence_score,
                3,
            )

            if evidence_score >= 0.85:
                evidence_strength = (
                    "STRONG"
                )

            elif evidence_score >= 0.70:
                evidence_strength = (
                    "MODERATE"
                )

            else:
                evidence_strength = (
                    "LIMITED"
                )

        assessed = dict(
            candidate
        )

        assessed.update({
            "analogical_evidence_assessed":
                True,

            "analogical_evidence_score":
                evidence_score,

            "analogical_evidence_strength":
                evidence_strength,

            "analogical_evidence_basis":
                primary_basis,

            "analogical_confidence_cap_applied":
                confidence_cap_applied,

            "analogical_evidence_factors": {
                "final_analogical_expression_validated":
                    final_validated,

                "same_sentence_analogical_valid":
                    same_sentence_valid,

                "cross_sentence_analogical_valid":
                    cross_sentence_valid,

                "article_asserted_candidate_confirmed":
                    article_asserted_confirmed,

                "same_sentence_candidate_confirmed":
                    same_sentence_candidate_confirmed,

                "exact_analogical_signal_supported":
                    exact_signal_supported,

                "analogical_correspondence_supported":
                    correspondence_supported,

                "analogical_structure_supported":
                    structure_supported,

                "source_target_orientation_supported":
                    orientation_supported,

                "analogy_source_supported":
                    source_supported,

                "analogy_target_supported":
                    target_supported,

                "unique_directional_grounding_supported":
                    unique_directional_grounding,

                "target_side_grounding_match_count":
                    target_count,

                "source_side_grounding_match_count":
                    source_count,

                "cross_side_grounding_overlap_count":
                    overlap_count,

                "directional_grounding_confidence":
                    directional_grounding_confidence,

                "adjacent_analogical_support_present":
                    adjacent_support_present,
            },

            "directional_grounding_integrity_preserved":
                True,

            "analogical_correspondence_preserved":
                True,

            "source_target_orientation_preserved":
                True,

            "multiple_total_groundings_treated_as_ambiguity":
                False,

            "cross_sentence_expression_promoted_to_strong":
                False,

            "confidence_scope":
                "ARTICLE_LOCAL_ANALOGICAL_EXPRESSION_EVIDENCE_ONLY",

            "duplicate_resolution_performed":
                False,

            "analogical_correspondence_mapped":
                False,

            "analogy_extended":
                False,

            "generic_similarity_reasoning_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,
        })

        assessed_candidates.append(
            assessed
        )

    assessed_by_id = {
        candidate.get(
            "analogical_candidate_id"
        ):
            candidate
        for candidate in assessed_candidates
    }

    assessed_units = []
    assessed_units_by_id = {}

    for unit in (
        cross_sentence_result.get(
            "analogical_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every Analogical Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "analogical_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise AnalogicalIntelligenceError(
                "Analogical Claim Unit ID is required."
            )

        if unit_id in assessed_units_by_id:
            raise AnalogicalIntelligenceError(
                "Duplicate Analogical Claim Unit ID detected."
            )

        state = dict(
            unit.get(
                "analogical_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "cross_sentence_analogical_validation"
            )
            != "COMPLETE"
        ):
            raise AnalogicalIntelligenceError(
                "Cross-sentence analogical validation must be COMPLETE before Stage K."
            )

        if (
            state.get(
                "analogical_evidence_assessment"
            )
            != "PENDING"
        ):
            raise AnalogicalIntelligenceError(
                "Analogical evidence assessment must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "cross_sentence_analogical_validation_performed"
            )
            is not True
        ):
            raise AnalogicalIntelligenceError(
                "Stage-J cross-sentence analogical validation boundary is incomplete."
            )

        if (
            boundaries.get(
                "analogical_evidence_assessment_performed",
                False,
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Analogical evidence assessment boundary must be False before Stage K."
            )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "analogical_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise AnalogicalIntelligenceError(
                    "Every unit Analogical Candidate must be a mapping."
                )

            candidate_id = old_candidate.get(
                "analogical_candidate_id"
            )

            assessed_candidate = (
                assessed_by_id.get(
                    candidate_id
                )
            )

            if assessed_candidate is None:
                raise AnalogicalIntelligenceError(
                    "Analogical candidate/unit evidence mismatch."
                )

            unit_candidates.append(
                assessed_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "analogical_evidence_assessment"
        ] = "COMPLETE"

        updated_boundaries = dict(
            boundaries
        )

        updated_boundaries[
            "analogical_evidence_assessment_performed"
        ] = True

        updated_boundaries[
            "duplicate_resolution_performed"
        ] = False

        updated_boundaries[
            "analogical_correspondence_mapping_performed"
        ] = False

        updated_boundaries[
            "analogy_extension_performed"
        ] = False

        updated_boundaries[
            "generic_similarity_reasoning_performed"
        ] = False

        updated_boundaries[
            "procedural_reasoning_performed"
        ] = False

        updated_boundaries[
            "quantitative_reasoning_performed"
        ] = False

        updated_boundaries[
            "temporal_reasoning_performed"
        ] = False

        updated_boundaries[
            "new_causal_reasoning_performed"
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
            "analogical_candidates":
                unit_candidates,

            "strong_analogical_evidence_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "analogical_evidence_strength"
                    )
                    == "STRONG"
                ),

            "moderate_analogical_evidence_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "analogical_evidence_strength"
                    )
                    == "MODERATE"
                ),

            "limited_analogical_evidence_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "analogical_evidence_strength"
                    )
                    == "LIMITED"
                ),

            "insufficient_analogical_evidence_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "analogical_evidence_strength"
                    )
                    == "INSUFFICIENT"
                ),

            "analogical_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        assessed_units.append(
            updated_unit
        )

        assessed_units_by_id[
            unit_id
        ] = updated_unit

    assessed_sections = []

    for section in (
        cross_sentence_result.get(
            "analogical_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every analogical section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "analogical_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise AnalogicalIntelligenceError(
                    "Every section Analogical Claim Unit must be a mapping."
                )

            unit_id = old_unit.get(
                "analogical_claim_unit_id"
            )

            assessed_unit = (
                assessed_units_by_id.get(
                    unit_id
                )
            )

            if assessed_unit is None:
                raise AnalogicalIntelligenceError(
                    "Analogical section/unit evidence mismatch."
                )

            section_units.append(
                assessed_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "analogical_candidates"
                )
                or []
            )
        ]

        assessed_sections.append({
            **dict(
                section
            ),

            "analogical_claim_units":
                section_units,

            "analogical_candidates":
                section_candidates,

            "strong_analogical_evidence_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "analogical_evidence_strength"
                    )
                    == "STRONG"
                ),

            "moderate_analogical_evidence_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "analogical_evidence_strength"
                    )
                    == "MODERATE"
                ),

            "limited_analogical_evidence_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "analogical_evidence_strength"
                    )
                    == "LIMITED"
                ),

            "insufficient_analogical_evidence_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "analogical_evidence_strength"
                    )
                    == "INSUFFICIENT"
                ),

            "analogical_evidence_assessment_complete":
                True,
        })

    strong_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "analogical_evidence_strength"
        )
        == "STRONG"
    )

    moderate_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "analogical_evidence_strength"
        )
        == "MODERATE"
    )

    limited_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "analogical_evidence_strength"
        )
        == "LIMITED"
    )

    insufficient_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "analogical_evidence_strength"
        )
        == "INSUFFICIENT"
    )

    invalid_strong_count = sum(
        1
        for candidate in assessed_candidates
        if (
            candidate.get(
                "final_analogical_expression_validated"
            )
            is not True
            and candidate.get(
                "analogical_evidence_strength"
            )
            == "STRONG"
        )
    )

    cross_sentence_strong_count = sum(
        1
        for candidate in assessed_candidates
        if (
            candidate.get(
                "cross_sentence_analogical_valid"
            )
            is True
            and candidate.get(
                "analogical_evidence_strength"
            )
            == "STRONG"
        )
    )

    result = dict(
        cross_sentence_result
    )

    result_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        result_boundaries.get(
            "cross_sentence_analogical_validation_performed"
        )
        is not True
    ):
        raise AnalogicalIntelligenceError(
            "Top-level Stage-J cross-sentence validation boundary is incomplete."
        )

    if (
        result_boundaries.get(
            "analogical_evidence_assessment_performed",
            False,
        )
        is not False
    ):
        raise AnalogicalIntelligenceError(
            "Top-level analogical evidence assessment must not already be performed."
        )

    result_boundaries[
        "analogical_evidence_assessment_performed"
    ] = True

    result_boundaries[
        "duplicate_resolution_performed"
    ] = False

    result_boundaries[
        "analogical_correspondence_mapping_performed"
    ] = False

    result_boundaries[
        "analogy_extension_performed"
    ] = False

    result_boundaries[
        "generic_similarity_reasoning_performed"
    ] = False

    result_boundaries[
        "procedural_reasoning_performed"
    ] = False

    result_boundaries[
        "quantitative_reasoning_performed"
    ] = False

    result_boundaries[
        "temporal_reasoning_performed"
    ] = False

    result_boundaries[
        "new_causal_reasoning_performed"
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
            "analogical_evidence_assessment_v1",

        "patch":
            "4.6.11K",

        "status":
            "ANALOGICAL_EVIDENCE_ASSESSMENT_COMPLETE",

        "analogical_sections":
            assessed_sections,

        "analogical_claim_units":
            assessed_units,

        "analogical_candidates":
            assessed_candidates,

        "analogical_evidence_summary": {
            "candidate_count":
                len(
                    assessed_candidates
                ),

            "strong_analogical_evidence_count":
                strong_count,

            "moderate_analogical_evidence_count":
                moderate_count,

            "limited_analogical_evidence_count":
                limited_count,

            "insufficient_analogical_evidence_count":
                insufficient_count,

            "candidate_count_accounted_for":
                (
                    strong_count
                    + moderate_count
                    + limited_count
                    + insufficient_count
                    == len(
                        assessed_candidates
                    )
                ),

            "invalid_expression_strong_count":
                invalid_strong_count,

            "cross_sentence_strong_count":
                cross_sentence_strong_count,

            "invalid_expression_strong_promotion_prohibited":
                True,

            "cross_sentence_strong_promotion_prohibited":
                True,

            "directional_grounding_model":
                "ONE_UNIQUE_TARGET_PLUS_ONE_UNIQUE_SOURCE_ZERO_OVERLAP",

            "two_total_directional_groundings_treated_as_ambiguity":
                False,

            "grounding_confidence_source":
                "STAGE_F_DIRECTIONAL_EXTRACTION_CONFIDENCE",

            "confidence_scope":
                "ARTICLE_LOCAL_ANALOGICAL_EXPRESSION_EVIDENCE_ONLY",

            "scientific_truth_confidence_computed":
                False,

            "real_world_analogy_validity_verified":
                False,

            "correspondence_mapping_performed":
                False,

            "property_level_mapping_performed":
                False,

            "analogy_extension_performed":
                False,

            "duplicate_resolution_performed":
                False,

            "generic_similarity_reasoning_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            result_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "duplicate_redundant_analogical_resolution",
    })

    return result


def resolve_duplicate_redundant_analogical_relations_v1(
    evidence_assessment_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Resolve exact article-local duplicate analogical candidates.

    Duplicate identity is deliberately conservative. It requires the
    same canonical analogical signal, analogical form, orientation
    pattern, exact target grounding identity, and exact source grounding
    identity.

    Direction is part of identity. TARGET->SOURCE is not interchangeable
    with SOURCE->TARGET.

    This stage does NOT:
    - use fuzzy semantic similarity,
    - merge different analogy directions,
    - merge different targets,
    - merge different sources,
    - merge different analogical forms,
    - guess unresolved grounding,
    - rescue invalid analogies,
    - create source/target orientation,
    - create correspondence mappings,
    - map analogy properties,
    - extend an analogy,
    - perform generic similarity reasoning,
    - perform procedural reasoning,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - perform new causal reasoning,
    - assess factual/scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    import hashlib
    import json
    import re

    if not isinstance(
        evidence_assessment_result,
        Mapping,
    ):
        raise AnalogicalIntelligenceError(
            "evidence_assessment_result must be a mapping."
        )

    if (
        evidence_assessment_result.get(
            "schema_version"
        )
        != "analogical_evidence_assessment_v1"
    ):
        raise AnalogicalIntelligenceError(
            "Stage L requires analogical_evidence_assessment_v1."
        )

    if (
        evidence_assessment_result.get(
            "status"
        )
        != "ANALOGICAL_EVIDENCE_ASSESSMENT_COMPLETE"
    ):
        raise AnalogicalIntelligenceError(
            "Analogical evidence assessment must be complete."
        )

    if (
        evidence_assessment_result.get(
            "phase"
        )
        != "4.6.11"
    ):
        raise AnalogicalIntelligenceError(
            "Stage L requires Phase 4.6.11 input."
        )

    if (
        evidence_assessment_result.get(
            "patch"
        )
        != "4.6.11K"
    ):
        raise AnalogicalIntelligenceError(
            "Stage L requires canonical 4.6.11K input."
        )

    if (
        evidence_assessment_result.get(
            "next_stage"
        )
        != "duplicate_redundant_analogical_resolution"
    ):
        raise AnalogicalIntelligenceError(
            "Stage K must hand off to duplicate_redundant_analogical_resolution."
        )

    if (
        evidence_assessment_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise AnalogicalIntelligenceError(
            "Analogical Intelligence must remain transient."
        )

    def normalize_text(
        value: Any,
    ) -> str:
        value = str(
            value
            or ""
        ).lower()

        value = value.replace(
            "\u2019",
            "'",
        )

        value = value.replace(
            "\u2018",
            "'",
        )

        value = value.replace(
            "\u2013",
            "-",
        )

        value = value.replace(
            "\u2014",
            "-",
        )

        value = re.sub(
            r"[^a-z0-9.%'+/-]+",
            " ",
            value,
        )

        return re.sub(
            r"\s+",
            " ",
            value,
        ).strip()

    def directional_grounding_identity(
        selected: Any,
        role: str,
    ) -> tuple[str, str, str] | None:
        if not isinstance(
            selected,
            Mapping,
        ):
            return None

        grounding_ref = normalize_text(
            selected.get(
                "grounding_ref"
            )
        )

        canonical_text = normalize_text(
            selected.get(
                "canonical_text"
            )
        )

        semantic_kind = normalize_text(
            selected.get(
                "semantic_kind"
            )
        )

        if not grounding_ref:
            raise AnalogicalIntelligenceError(
                "Selected analogy "
                + role
                + " requires grounding_ref."
            )

        if not canonical_text:
            raise AnalogicalIntelligenceError(
                "Selected analogy "
                + role
                + " requires canonical_text."
            )

        if semantic_kind not in {
            "entity",
            "concept",
        }:
            raise AnalogicalIntelligenceError(
                "Selected analogy "
                + role
                + " has invalid semantic_kind."
            )

        return (
            semantic_kind,
            canonical_text,
            grounding_ref,
        )

    def duplicate_key(
        candidate: Mapping[str, Any],
    ) -> tuple[str, ...] | None:
        if (
            candidate.get(
                "final_analogical_expression_validated"
            )
            is not True
        ):
            return None

        if (
            candidate.get(
                "analogical_evidence_assessed"
            )
            is not True
        ):
            return None

        if (
            candidate.get(
                "analogy_source_target_orientation_resolved"
            )
            is not True
        ):
            return None

        if (
            candidate.get(
                "analogy_target_selected"
            )
            is not True
            or candidate.get(
                "analogy_source_selected"
            )
            is not True
        ):
            return None

        if (
            candidate.get(
                "same_sentence_unique_directional_grounding_supported"
            )
            is not True
        ):
            return None

        target_count = candidate.get(
            "target_side_grounding_match_count"
        )

        source_count = candidate.get(
            "source_side_grounding_match_count"
        )

        overlap_count = candidate.get(
            "cross_side_grounding_overlap_count"
        )

        for name, value in (
            (
                "target_side_grounding_match_count",
                target_count,
            ),
            (
                "source_side_grounding_match_count",
                source_count,
            ),
            (
                "cross_side_grounding_overlap_count",
                overlap_count,
            ),
        ):
            if (
                not isinstance(
                    value,
                    int,
                )
                or isinstance(
                    value,
                    bool,
                )
                or value < 0
            ):
                raise AnalogicalIntelligenceError(
                    name
                    + " must be a non-negative integer."
                )

        if (
            target_count != 1
            or source_count != 1
            or overlap_count != 0
        ):
            return None

        target_identity = (
            directional_grounding_identity(
                candidate.get(
                    "selected_analogy_target"
                ),
                "target",
            )
        )

        source_identity = (
            directional_grounding_identity(
                candidate.get(
                    "selected_analogy_source"
                ),
                "source",
            )
        )

        if (
            target_identity is None
            or source_identity is None
        ):
            return None

        signal_type = normalize_text(
            candidate.get(
                "signal_type"
            )
        )

        analogical_form = normalize_text(
            candidate.get(
                "candidate_analogical_form"
            )
        )

        orientation_pattern = normalize_text(
            candidate.get(
                "analogy_orientation_pattern"
            )
        )

        if (
            not signal_type
            or not analogical_form
            or not orientation_pattern
        ):
            return None

        return (
            signal_type,
            analogical_form,
            orientation_pattern,

            "target",
            target_identity[0],
            target_identity[1],
            target_identity[2],

            "source",
            source_identity[0],
            source_identity[1],
            source_identity[2],
        )

    source_candidates = list(
        evidence_assessment_result.get(
            "analogical_candidates"
        )
        or []
    )

    groups: dict[
        tuple[str, ...],
        list[dict[str, Any]],
    ] = {}

    non_groupable = []

    seen_candidate_ids = set()

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every analogical candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "analogical_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise AnalogicalIntelligenceError(
                "Analogical Candidate ID is required."
            )

        if candidate_id in seen_candidate_ids:
            raise AnalogicalIntelligenceError(
                "Duplicate Analogical Candidate ID encountered."
            )

        seen_candidate_ids.add(
            candidate_id
        )

        if (
            candidate.get(
                "analogical_evidence_assessed"
            )
            is not True
        ):
            raise AnalogicalIntelligenceError(
                "Every analogical candidate must have completed evidence assessment."
            )

        if (
            candidate.get(
                "duplicate_resolution_performed"
            )
            is True
        ):
            raise AnalogicalIntelligenceError(
                "Candidate must not already have duplicate resolution."
            )

        if (
            candidate.get(
                "analogical_correspondence_mapped"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Stage L must not receive mapped analogical correspondence."
            )

        if (
            candidate.get(
                "analogy_extended"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Stage L must not receive extended analogy."
            )

        copied = dict(
            candidate
        )

        key = duplicate_key(
            copied
        )

        if key is None:
            non_groupable.append(
                copied
            )

            continue

        groups.setdefault(
            key,
            [],
        ).append(
            copied
        )

    strength_rank = {
        "STRONG":
            4,

        "MODERATE":
            3,

        "LIMITED":
            2,

        "INSUFFICIENT":
            1,
    }

    resolved_by_id = {}

    representative_candidates = []

    duplicate_group_count = 0
    duplicate_candidate_count = 0

    for key, members in groups.items():
        ordered = sorted(
            members,
            key=lambda candidate: (
                -strength_rank.get(
                    str(
                        candidate.get(
                            "analogical_evidence_strength"
                        )
                        or ""
                    ),
                    0,
                ),
                -float(
                    candidate.get(
                        "analogical_evidence_score"
                    )
                    or 0.0
                ),
                0
                if candidate.get(
                    "same_sentence_analogical_valid"
                )
                is True
                else 1,
                0
                if candidate.get(
                    "adjacent_analogical_support_present"
                )
                is True
                else 1,
                str(
                    candidate.get(
                        "analogical_candidate_id"
                    )
                    or ""
                ),
            ),
        )

        representative = ordered[
            0
        ]

        member_ids = [
            str(
                member.get(
                    "analogical_candidate_id"
                )
            )
            for member in ordered
        ]

        raw_key = json.dumps(
            key,
            ensure_ascii=False,
            separators=(
                ",",
                ":",
            ),
        )

        group_id = (
            "analogical_duplicate_group_"
            + hashlib.sha256(
                raw_key.encode(
                    "utf-8"
                )
            ).hexdigest()[:16]
        )

        is_duplicate_group = (
            len(
                ordered
            )
            > 1
        )

        if is_duplicate_group:
            duplicate_group_count += 1

            duplicate_candidate_count += (
                len(
                    ordered
                )
                - 1
            )

        representative_id = str(
            representative.get(
                "analogical_candidate_id"
            )
        )

        for index, member in enumerate(
            ordered
        ):
            member_id = str(
                member.get(
                    "analogical_candidate_id"
                )
            )

            is_representative = (
                index == 0
            )

            resolved = dict(
                member
            )

            resolved.update({
                "duplicate_resolution_performed":
                    True,

                "analogical_duplicate_group_id":
                    group_id,

                "analogical_duplicate_group_size":
                    len(
                        ordered
                    ),

                "analogical_duplicate_member_ids":
                    member_ids,

                "is_analogical_duplicate_group":
                    is_duplicate_group,

                "is_representative_analogical_expression":
                    is_representative,

                "representative_analogical_candidate_id":
                    representative_id,

                "duplicate_of_analogical_candidate_id":
                    (
                        None
                        if is_representative
                        else representative_id
                    ),

                "analogical_duplicate_resolution_status":
                    (
                        "REPRESENTATIVE"
                        if is_representative
                        else "DUPLICATE_REDUNDANT"
                    ),

                "analogical_duplicate_key": {
                    "signal_type":
                        key[0],

                    "candidate_analogical_form":
                        key[1],

                    "analogy_orientation_pattern":
                        key[2],

                    "target_semantic_kind":
                        key[4],

                    "target_canonical_text":
                        key[5],

                    "target_grounding_ref":
                        key[6],

                    "source_semantic_kind":
                        key[8],

                    "source_canonical_text":
                        key[9],

                    "source_grounding_ref":
                        key[10],
                },

                "exact_directional_analogical_identity_used":
                    True,

                "analogy_direction_preserved":
                    True,

                "different_targets_merged":
                    False,

                "different_sources_merged":
                    False,

                "different_analogical_forms_merged":
                    False,

                "different_orientation_patterns_merged":
                    False,

                "fuzzy_similarity_performed":
                    False,

                "analogical_correspondence_mapped":
                    False,

                "analogy_extended":
                    False,

                "generic_similarity_reasoning_performed":
                    False,

                "procedural_reasoning_performed":
                    False,

                "quantitative_reasoning_performed":
                    False,

                "temporal_reasoning_performed":
                    False,

                "new_causal_reasoning_performed":
                    False,

                "truth_assessed":
                    False,

                "external_authority_checked":
                    False,
            })

            resolved_by_id[
                member_id
            ] = resolved

            if is_representative:
                representative_candidates.append(
                    resolved
                )

    for member in non_groupable:
        member_id = str(
            member.get(
                "analogical_candidate_id"
            )
        )

        resolved = dict(
            member
        )

        resolved.update({
            "duplicate_resolution_performed":
                True,

            "analogical_duplicate_group_id":
                None,

            "analogical_duplicate_group_size":
                1,

            "analogical_duplicate_member_ids": [
                member_id,
            ],

            "is_analogical_duplicate_group":
                False,

            "is_representative_analogical_expression":
                True,

            "representative_analogical_candidate_id":
                member_id,

            "duplicate_of_analogical_candidate_id":
                None,

            "analogical_duplicate_resolution_status":
                "UNIQUE_NON_GROUPABLE",

            "analogical_duplicate_key":
                None,

            "exact_directional_analogical_identity_used":
                False,

            "analogy_direction_preserved":
                True,

            "different_targets_merged":
                False,

            "different_sources_merged":
                False,

            "different_analogical_forms_merged":
                False,

            "different_orientation_patterns_merged":
                False,

            "fuzzy_similarity_performed":
                False,

            "analogical_correspondence_mapped":
                False,

            "analogy_extended":
                False,

            "generic_similarity_reasoning_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,
        })

        resolved_by_id[
            member_id
        ] = resolved

        representative_candidates.append(
            resolved
        )

    resolved_candidates = []

    for candidate in source_candidates:
        candidate_id = str(
            candidate.get(
                "analogical_candidate_id"
            )
        )

        resolved = resolved_by_id.get(
            candidate_id
        )

        if resolved is None:
            raise AnalogicalIntelligenceError(
                "Duplicate analogical resolution lost a candidate."
            )

        resolved_candidates.append(
            resolved
        )

    representative_candidates.sort(
        key=lambda candidate: str(
            candidate.get(
                "analogical_candidate_id"
            )
            or ""
        )
    )

    resolved_units = []
    resolved_units_by_id = {}

    for unit in (
        evidence_assessment_result.get(
            "analogical_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every Analogical Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "analogical_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise AnalogicalIntelligenceError(
                "Analogical Claim Unit ID is required."
            )

        if unit_id in resolved_units_by_id:
            raise AnalogicalIntelligenceError(
                "Duplicate Analogical Claim Unit ID detected."
            )

        state = dict(
            unit.get(
                "analogical_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "analogical_evidence_assessment"
            )
            != "COMPLETE"
        ):
            raise AnalogicalIntelligenceError(
                "Analogical evidence assessment must be COMPLETE before Stage L."
            )

        if (
            state.get(
                "duplicate_analogical_resolution"
            )
            != "PENDING"
        ):
            raise AnalogicalIntelligenceError(
                "Duplicate analogical resolution must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "analogical_evidence_assessment_performed"
            )
            is not True
        ):
            raise AnalogicalIntelligenceError(
                "Stage-K analogical evidence boundary must be complete."
            )

        if (
            boundaries.get(
                "duplicate_resolution_performed"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Duplicate analogical resolution boundary must be False before Stage L."
            )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "analogical_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise AnalogicalIntelligenceError(
                    "Every unit Analogical Candidate must be a mapping."
                )

            candidate_id = old_candidate.get(
                "analogical_candidate_id"
            )

            resolved_candidate = (
                resolved_by_id.get(
                    candidate_id
                )
            )

            if resolved_candidate is None:
                raise AnalogicalIntelligenceError(
                    "Analogical candidate/unit duplicate mismatch."
                )

            unit_candidates.append(
                resolved_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "duplicate_analogical_resolution"
        ] = "COMPLETE"

        updated_boundaries = dict(
            boundaries
        )

        updated_boundaries[
            "duplicate_resolution_performed"
        ] = True

        updated_boundaries[
            "fuzzy_similarity_performed"
        ] = False

        updated_boundaries[
            "analogical_correspondence_mapping_performed"
        ] = False

        updated_boundaries[
            "analogy_extension_performed"
        ] = False

        updated_boundaries[
            "generic_similarity_reasoning_performed"
        ] = False

        updated_boundaries[
            "procedural_reasoning_performed"
        ] = False

        updated_boundaries[
            "quantitative_reasoning_performed"
        ] = False

        updated_boundaries[
            "temporal_reasoning_performed"
        ] = False

        updated_boundaries[
            "new_causal_reasoning_performed"
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
            "analogical_candidates":
                unit_candidates,

            "representative_analogical_expression_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "is_representative_analogical_expression"
                    )
                    is True
                ),

            "duplicate_redundant_analogical_expression_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "analogical_duplicate_resolution_status"
                    )
                    == "DUPLICATE_REDUNDANT"
                ),

            "analogical_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        resolved_units.append(
            updated_unit
        )

        resolved_units_by_id[
            unit_id
        ] = updated_unit

    resolved_sections = []

    for section in (
        evidence_assessment_result.get(
            "analogical_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every analogical section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "analogical_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise AnalogicalIntelligenceError(
                    "Every section Analogical Claim Unit must be a mapping."
                )

            unit_id = old_unit.get(
                "analogical_claim_unit_id"
            )

            resolved_unit = (
                resolved_units_by_id.get(
                    unit_id
                )
            )

            if resolved_unit is None:
                raise AnalogicalIntelligenceError(
                    "Analogical section/unit duplicate mismatch."
                )

            section_units.append(
                resolved_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "analogical_candidates"
                )
                or []
            )
        ]

        resolved_sections.append({
            **dict(
                section
            ),

            "analogical_claim_units":
                section_units,

            "analogical_candidates":
                section_candidates,

            "representative_analogical_expression_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "is_representative_analogical_expression"
                    )
                    is True
                ),

            "duplicate_redundant_analogical_expression_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "analogical_duplicate_resolution_status"
                    )
                    == "DUPLICATE_REDUNDANT"
                ),

            "duplicate_analogical_resolution_complete":
                True,
        })

    representative_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "is_representative_analogical_expression"
        )
        is True
    )

    redundant_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "analogical_duplicate_resolution_status"
        )
        == "DUPLICATE_REDUNDANT"
    )

    non_groupable_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "analogical_duplicate_resolution_status"
        )
        == "UNIQUE_NON_GROUPABLE"
    )

    result = dict(
        evidence_assessment_result
    )

    result_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        result_boundaries.get(
            "analogical_evidence_assessment_performed"
        )
        is not True
    ):
        raise AnalogicalIntelligenceError(
            "Top-level Stage-K analogical evidence boundary must be complete."
        )

    if (
        result_boundaries.get(
            "duplicate_resolution_performed"
        )
        is not False
    ):
        raise AnalogicalIntelligenceError(
            "Top-level duplicate analogical resolution must not already be performed."
        )

    result_boundaries[
        "duplicate_resolution_performed"
    ] = True

    result_boundaries[
        "fuzzy_similarity_performed"
    ] = False

    result_boundaries[
        "analogical_correspondence_mapping_performed"
    ] = False

    result_boundaries[
        "analogy_extension_performed"
    ] = False

    result_boundaries[
        "generic_similarity_reasoning_performed"
    ] = False

    result_boundaries[
        "procedural_reasoning_performed"
    ] = False

    result_boundaries[
        "quantitative_reasoning_performed"
    ] = False

    result_boundaries[
        "temporal_reasoning_performed"
    ] = False

    result_boundaries[
        "new_causal_reasoning_performed"
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
            "analogical_duplicate_resolution_v1",

        "patch":
            "4.6.11L",

        "status":
            "ANALOGICAL_DUPLICATE_RESOLUTION_COMPLETE",

        "analogical_sections":
            resolved_sections,

        "analogical_claim_units":
            resolved_units,

        "analogical_candidates":
            resolved_candidates,

        "representative_analogical_candidates":
            representative_candidates,

        "analogical_duplicate_resolution_summary": {
            "candidate_count":
                len(
                    resolved_candidates
                ),

            "representative_analogical_expression_count":
                representative_count,

            "duplicate_redundant_analogical_expression_count":
                redundant_count,

            "duplicate_group_count":
                duplicate_group_count,

            "duplicate_candidate_count":
                duplicate_candidate_count,

            "non_groupable_analogical_candidate_count":
                non_groupable_count,

            "candidate_count_accounted_for":
                (
                    representative_count
                    + redundant_count
                    == len(
                        resolved_candidates
                    )
                ),

            "exact_canonical_key_only":
                True,

            "duplicate_key_fields": [
                "signal_type",
                "candidate_analogical_form",
                "analogy_orientation_pattern",
                "target_semantic_kind",
                "target_canonical_text",
                "target_grounding_ref",
                "source_semantic_kind",
                "source_canonical_text",
                "source_grounding_ref",
            ],

            "analogy_direction_is_identity":
                True,

            "different_targets_merged":
                False,

            "different_sources_merged":
                False,

            "different_analogical_forms_merged":
                False,

            "different_orientation_patterns_merged":
                False,

            "strongest_evidence_representative_selected":
                True,

            "duplicate_provenance_preserved":
                True,

            "fuzzy_similarity_performed":
                False,

            "correspondence_mapping_performed":
                False,

            "property_level_mapping_performed":
                False,

            "analogy_extension_performed":
                False,

            "generic_similarity_reasoning_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            result_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "article_analogical_consolidation",
    })

    return result


def consolidate_article_analogical_intelligence_v1(
    duplicate_resolution_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Consolidate completed article-local Analogical Intelligence into
    article-level and section-level summaries.

    Only representative analogical expressions are included in the
    canonical consolidated analogical set. Full candidate provenance
    remains preserved in the complete source candidate collection.

    This stage does NOT:
    - create new analogical expressions,
    - rescue invalid analogies,
    - merge different analogical identities,
    - create or repair source/target orientation,
    - create correspondence mappings,
    - map source properties to target properties,
    - extend an analogy,
    - strengthen evidence classifications,
    - perform generic similarity reasoning,
    - perform procedural reasoning,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - perform new causal reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        duplicate_resolution_result,
        Mapping,
    ):
        raise AnalogicalIntelligenceError(
            "duplicate_resolution_result must be a mapping."
        )

    if (
        duplicate_resolution_result.get(
            "schema_version"
        )
        != "analogical_duplicate_resolution_v1"
    ):
        raise AnalogicalIntelligenceError(
            "Stage M requires analogical_duplicate_resolution_v1."
        )

    if (
        duplicate_resolution_result.get(
            "status"
        )
        != "ANALOGICAL_DUPLICATE_RESOLUTION_COMPLETE"
    ):
        raise AnalogicalIntelligenceError(
            "Duplicate analogical resolution must be complete."
        )

    if (
        duplicate_resolution_result.get(
            "phase"
        )
        != "4.6.11"
    ):
        raise AnalogicalIntelligenceError(
            "Stage M requires Phase 4.6.11 input."
        )

    if (
        duplicate_resolution_result.get(
            "patch"
        )
        != "4.6.11L"
    ):
        raise AnalogicalIntelligenceError(
            "Stage M requires canonical 4.6.11L input."
        )

    if (
        duplicate_resolution_result.get(
            "next_stage"
        )
        != "article_analogical_consolidation"
    ):
        raise AnalogicalIntelligenceError(
            "Stage L must hand off to article_analogical_consolidation."
        )

    if (
        duplicate_resolution_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise AnalogicalIntelligenceError(
            "Analogical Intelligence must remain transient."
        )

    source_candidates = list(
        duplicate_resolution_result.get(
            "analogical_candidates"
        )
        or []
    )

    representative_candidates = list(
        duplicate_resolution_result.get(
            "representative_analogical_candidates"
        )
        or []
    )

    seen_source_ids = set()

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every analogical candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "analogical_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise AnalogicalIntelligenceError(
                "Analogical Candidate ID is required."
            )

        if candidate_id in seen_source_ids:
            raise AnalogicalIntelligenceError(
                "Duplicate Analogical Candidate ID encountered."
            )

        seen_source_ids.add(
            candidate_id
        )

        if (
            candidate.get(
                "duplicate_resolution_performed"
            )
            is not True
        ):
            raise AnalogicalIntelligenceError(
                "All analogical candidates must complete duplicate resolution before Stage M."
            )

    representative_ids = []
    seen_representative_ids = set()

    for candidate in representative_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every representative analogical expression must be a mapping."
            )

        if (
            candidate.get(
                "is_representative_analogical_expression"
            )
            is not True
        ):
            raise AnalogicalIntelligenceError(
                "Representative analogical list contains a non-representative candidate."
            )

        candidate_id = str(
            candidate.get(
                "analogical_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise AnalogicalIntelligenceError(
                "Representative Analogical Candidate ID is required."
            )

        if candidate_id in seen_representative_ids:
            raise AnalogicalIntelligenceError(
                "Duplicate representative Analogical Candidate ID encountered."
            )

        seen_representative_ids.add(
            candidate_id
        )

        representative_ids.append(
            candidate_id
        )

    expected_representative_ids = {
        str(
            candidate.get(
                "analogical_candidate_id"
            )
            or ""
        )
        for candidate in source_candidates
        if candidate.get(
            "is_representative_analogical_expression"
        )
        is True
    }

    if set(
        representative_ids
    ) != expected_representative_ids:
        raise AnalogicalIntelligenceError(
            "Representative analogical list does not match resolved candidates."
        )

    signal_type_counts = {}
    analogical_form_counts = {}
    orientation_pattern_counts = {}

    evidence_strength_counts = {
        "STRONG":
            0,

        "MODERATE":
            0,

        "LIMITED":
            0,

        "INSUFFICIENT":
            0,
    }

    validated_count = 0
    unvalidated_count = 0

    same_sentence_validated_count = 0
    cross_sentence_validated_count = 0

    directionally_grounded_count = 0
    non_directionally_grounded_count = 0

    adjacent_support_count = 0

    consolidated_analogical_expressions = []

    for candidate in representative_candidates:
        signal_type = str(
            candidate.get(
                "signal_type"
            )
            or "UNSPECIFIED"
        )

        analogical_form = str(
            candidate.get(
                "candidate_analogical_form"
            )
            or "UNSPECIFIED"
        )

        orientation_pattern = str(
            candidate.get(
                "analogy_orientation_pattern"
            )
            or "UNSPECIFIED"
        )

        evidence_strength = str(
            candidate.get(
                "analogical_evidence_strength"
            )
            or "INSUFFICIENT"
        )

        if evidence_strength not in evidence_strength_counts:
            raise AnalogicalIntelligenceError(
                "Representative candidate has invalid analogical evidence strength."
            )

        final_validated = (
            candidate.get(
                "final_analogical_expression_validated"
            )
            is True
        )

        same_sentence_valid = (
            candidate.get(
                "same_sentence_analogical_valid"
            )
            is True
        )

        cross_sentence_valid = (
            candidate.get(
                "cross_sentence_analogical_valid"
            )
            is True
        )

        directionally_grounded = (
            candidate.get(
                "analogy_source_target_orientation_resolved"
            )
            is True
            and candidate.get(
                "analogy_target_selected"
            )
            is True
            and candidate.get(
                "analogy_source_selected"
            )
            is True
            and candidate.get(
                "target_side_grounding_match_count"
            )
            == 1
            and candidate.get(
                "source_side_grounding_match_count"
            )
            == 1
            and candidate.get(
                "cross_side_grounding_overlap_count"
            )
            == 0
        )

        adjacent_support = (
            candidate.get(
                "adjacent_analogical_support_present"
            )
            is True
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

        analogical_form_counts[
            analogical_form
        ] = (
            analogical_form_counts.get(
                analogical_form,
                0,
            )
            + 1
        )

        orientation_pattern_counts[
            orientation_pattern
        ] = (
            orientation_pattern_counts.get(
                orientation_pattern,
                0,
            )
            + 1
        )

        evidence_strength_counts[
            evidence_strength
        ] += 1

        if final_validated:
            validated_count += 1
        else:
            unvalidated_count += 1

        if same_sentence_valid:
            same_sentence_validated_count += 1

        if cross_sentence_valid:
            cross_sentence_validated_count += 1

        if directionally_grounded:
            directionally_grounded_count += 1
        else:
            non_directionally_grounded_count += 1

        if adjacent_support:
            adjacent_support_count += 1

        consolidated_analogical_expressions.append({
            "analogical_candidate_id":
                candidate.get(
                    "analogical_candidate_id"
                ),

            "signal_type":
                candidate.get(
                    "signal_type"
                ),

            "candidate_analogical_form":
                candidate.get(
                    "candidate_analogical_form"
                ),

            "analogy_orientation_pattern":
                candidate.get(
                    "analogy_orientation_pattern"
                ),

            "analogy_orientation_status":
                candidate.get(
                    "analogy_orientation_status"
                ),

            "analogy_orientation_basis":
                candidate.get(
                    "analogy_orientation_basis"
                ),

            "analogy_source_target_orientation_resolved":
                candidate.get(
                    "analogy_source_target_orientation_resolved"
                )
                is True,

            "selected_analogy_target":
                candidate.get(
                    "selected_analogy_target"
                ),

            "selected_analogy_source":
                candidate.get(
                    "selected_analogy_source"
                ),

            "analogy_target_selected":
                candidate.get(
                    "analogy_target_selected"
                )
                is True,

            "analogy_source_selected":
                candidate.get(
                    "analogy_source_selected"
                )
                is True,

            "target_side_grounding_match_count":
                candidate.get(
                    "target_side_grounding_match_count"
                ),

            "source_side_grounding_match_count":
                candidate.get(
                    "source_side_grounding_match_count"
                ),

            "cross_side_grounding_overlap_count":
                candidate.get(
                    "cross_side_grounding_overlap_count"
                ),

            "directional_grounding_supported":
                directionally_grounded,

            "analogical_correspondence_valid":
                candidate.get(
                    "analogical_correspondence_valid"
                )
                is True,

            "final_analogical_expression_validated":
                final_validated,

            "same_sentence_analogical_valid":
                same_sentence_valid,

            "cross_sentence_analogical_valid":
                cross_sentence_valid,

            "adjacent_analogical_support_present":
                adjacent_support,

            "analogical_evidence_score":
                candidate.get(
                    "analogical_evidence_score"
                ),

            "analogical_evidence_strength":
                evidence_strength,

            "analogical_evidence_basis":
                candidate.get(
                    "analogical_evidence_basis"
                ),

            "analogical_confidence_cap_applied":
                candidate.get(
                    "analogical_confidence_cap_applied"
                ),

            "section_id":
                candidate.get(
                    "section_id"
                ),

            "sentence_id":
                candidate.get(
                    "sentence_id"
                ),

            "analogical_claim_unit_id":
                candidate.get(
                    "analogical_claim_unit_id"
                ),

            "source_text":
                candidate.get(
                    "source_text"
                ),

            "signal_span":
                candidate.get(
                    "signal_span"
                ),

            "analogical_duplicate_group_id":
                candidate.get(
                    "analogical_duplicate_group_id"
                ),

            "analogical_duplicate_group_size":
                candidate.get(
                    "analogical_duplicate_group_size"
                ),

            "analogical_duplicate_member_ids":
                candidate.get(
                    "analogical_duplicate_member_ids"
                ),

            "analogical_duplicate_resolution_status":
                candidate.get(
                    "analogical_duplicate_resolution_status"
                ),

            "analogical_duplicate_key":
                candidate.get(
                    "analogical_duplicate_key"
                ),

            "analogy_direction_preserved":
                candidate.get(
                    "analogy_direction_preserved"
                )
                is True,

            "source_target_orientation_preserved":
                candidate.get(
                    "source_target_orientation_preserved"
                )
                is True,

            "analogical_correspondence_preserved":
                candidate.get(
                    "analogical_correspondence_preserved"
                )
                is True,

            "directional_grounding_integrity_preserved":
                candidate.get(
                    "directional_grounding_integrity_preserved"
                )
                is True,

            "new_analogical_expression_inference_performed":
                False,

            "analogical_evidence_strengthening_performed":
                False,

            "analogical_correspondence_mapped":
                False,

            "property_level_mapping_performed":
                False,

            "analogy_extended":
                False,

            "generic_similarity_reasoning_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "truth_assessed":
                False,

            "external_authority_checked":
                False,
        })

    consolidated_analogical_expressions.sort(
        key=lambda expression: (
            str(
                expression.get(
                    "section_id"
                )
                or ""
            ),
            str(
                expression.get(
                    "signal_type"
                )
                or ""
            ),
            str(
                expression.get(
                    "candidate_analogical_form"
                )
                or ""
            ),
            str(
                expression.get(
                    "analogy_orientation_pattern"
                )
                or ""
            ),
            str(
                expression.get(
                    "analogical_candidate_id"
                )
                or ""
            ),
        )
    )

    consolidated_sections = []

    seen_section_ids = set()

    for section in (
        duplicate_resolution_result.get(
            "analogical_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every analogical section must be a mapping."
            )

        section_id = str(
            section.get(
                "section_id"
            )
            or ""
        )

        if not section_id:
            raise AnalogicalIntelligenceError(
                "Analogical section ID is required."
            )

        if section_id in seen_section_ids:
            raise AnalogicalIntelligenceError(
                "Duplicate analogical section ID encountered."
            )

        seen_section_ids.add(
            section_id
        )

        section_expressions = [
            expression
            for expression in consolidated_analogical_expressions
            if str(
                expression.get(
                    "section_id"
                )
                or ""
            )
            == section_id
        ]

        section_signal_counts = {}
        section_form_counts = {}
        section_orientation_counts = {}

        section_strength_counts = {
            "STRONG":
                0,

            "MODERATE":
                0,

            "LIMITED":
                0,

            "INSUFFICIENT":
                0,
        }

        for expression in section_expressions:
            signal_type = str(
                expression.get(
                    "signal_type"
                )
                or "UNSPECIFIED"
            )

            analogical_form = str(
                expression.get(
                    "candidate_analogical_form"
                )
                or "UNSPECIFIED"
            )

            orientation_pattern = str(
                expression.get(
                    "analogy_orientation_pattern"
                )
                or "UNSPECIFIED"
            )

            evidence_strength = str(
                expression.get(
                    "analogical_evidence_strength"
                )
                or "INSUFFICIENT"
            )

            if evidence_strength not in section_strength_counts:
                raise AnalogicalIntelligenceError(
                    "Section representative has invalid analogical evidence strength."
                )

            section_signal_counts[
                signal_type
            ] = (
                section_signal_counts.get(
                    signal_type,
                    0,
                )
                + 1
            )

            section_form_counts[
                analogical_form
            ] = (
                section_form_counts.get(
                    analogical_form,
                    0,
                )
                + 1
            )

            section_orientation_counts[
                orientation_pattern
            ] = (
                section_orientation_counts.get(
                    orientation_pattern,
                    0,
                )
                + 1
            )

            section_strength_counts[
                evidence_strength
            ] += 1

        consolidated_sections.append({
            "section_id":
                section_id,

            "representative_analogical_expressions":
                section_expressions,

            "representative_analogical_expression_count":
                len(
                    section_expressions
                ),

            "validated_analogical_expression_count":
                sum(
                    1
                    for expression in section_expressions
                    if expression.get(
                        "final_analogical_expression_validated"
                    )
                    is True
                ),

            "unvalidated_analogical_expression_count":
                sum(
                    1
                    for expression in section_expressions
                    if expression.get(
                        "final_analogical_expression_validated"
                    )
                    is False
                ),

            "same_sentence_validated_analogical_count":
                sum(
                    1
                    for expression in section_expressions
                    if expression.get(
                        "same_sentence_analogical_valid"
                    )
                    is True
                ),

            "cross_sentence_validated_analogical_count":
                sum(
                    1
                    for expression in section_expressions
                    if expression.get(
                        "cross_sentence_analogical_valid"
                    )
                    is True
                ),

            "directionally_grounded_analogical_count":
                sum(
                    1
                    for expression in section_expressions
                    if expression.get(
                        "directional_grounding_supported"
                    )
                    is True
                ),

            "non_directionally_grounded_analogical_count":
                sum(
                    1
                    for expression in section_expressions
                    if expression.get(
                        "directional_grounding_supported"
                    )
                    is False
                ),

            "adjacent_support_analogical_count":
                sum(
                    1
                    for expression in section_expressions
                    if expression.get(
                        "adjacent_analogical_support_present"
                    )
                    is True
                ),

            "analogical_signal_type_counts":
                section_signal_counts,

            "analogical_form_counts":
                section_form_counts,

            "orientation_pattern_counts":
                section_orientation_counts,

            "analogical_evidence_strength_counts":
                section_strength_counts,

            "analogical_consolidation_complete":
                True,
        })

    total_candidate_count = len(
        source_candidates
    )

    representative_count = len(
        representative_candidates
    )

    redundant_count = sum(
        1
        for candidate in source_candidates
        if candidate.get(
            "analogical_duplicate_resolution_status"
        )
        == "DUPLICATE_REDUNDANT"
    )

    result = dict(
        duplicate_resolution_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        boundaries.get(
            "duplicate_resolution_performed"
        )
        is not True
    ):
        raise AnalogicalIntelligenceError(
            "Top-level Stage-L duplicate resolution boundary must be complete."
        )

    if (
        boundaries.get(
            "article_analogical_consolidation_performed"
        )
        is True
    ):
        raise AnalogicalIntelligenceError(
            "Article analogical consolidation must not already be performed."
        )

    boundaries[
        "article_analogical_consolidation_performed"
    ] = True

    boundaries[
        "new_analogical_expression_inference_performed"
    ] = False

    boundaries[
        "analogical_evidence_strengthening_performed"
    ] = False

    boundaries[
        "analogical_correspondence_mapping_performed"
    ] = False

    boundaries[
        "property_level_mapping_performed"
    ] = False

    boundaries[
        "analogy_extension_performed"
    ] = False

    boundaries[
        "generic_similarity_reasoning_performed"
    ] = False

    boundaries[
        "procedural_reasoning_performed"
    ] = False

    boundaries[
        "quantitative_reasoning_performed"
    ] = False

    boundaries[
        "temporal_reasoning_performed"
    ] = False

    boundaries[
        "new_causal_reasoning_performed"
    ] = False

    boundaries[
        "truth_assessment_performed"
    ] = False

    boundaries[
        "external_authority_check_performed"
    ] = False

    boundaries[
        "fuzzy_similarity_performed"
    ] = False

    boundaries[
        "semantic_memory_write_performed"
    ] = False

    boundaries[
        "persistence_performed"
    ] = False

    result.update({
        "schema_version":
            "analogical_article_consolidation_v1",

        "patch":
            "4.6.11M",

        "status":
            "ANALOGICAL_ARTICLE_CONSOLIDATION_COMPLETE",

        "consolidated_analogical_sections":
            consolidated_sections,

        "consolidated_analogical_expressions":
            consolidated_analogical_expressions,

        "article_analogical_summary": {
            "total_candidate_count":
                total_candidate_count,

            "representative_analogical_expression_count":
                representative_count,

            "duplicate_redundant_analogical_expression_count":
                redundant_count,

            "validated_analogical_expression_count":
                validated_count,

            "unvalidated_analogical_expression_count":
                unvalidated_count,

            "same_sentence_validated_analogical_count":
                same_sentence_validated_count,

            "cross_sentence_validated_analogical_count":
                cross_sentence_validated_count,

            "directionally_grounded_analogical_count":
                directionally_grounded_count,

            "non_directionally_grounded_analogical_count":
                non_directionally_grounded_count,

            "adjacent_support_analogical_count":
                adjacent_support_count,

            "analogical_signal_type_counts":
                signal_type_counts,

            "analogical_form_counts":
                analogical_form_counts,

            "orientation_pattern_counts":
                orientation_pattern_counts,

            "analogical_evidence_strength_counts":
                evidence_strength_counts,

            "representative_count_matches_consolidated":
                (
                    representative_count
                    == len(
                        consolidated_analogical_expressions
                    )
                ),

            "candidate_accounting_valid":
                (
                    representative_count
                    + redundant_count
                    == total_candidate_count
                ),

            "validation_count_accounting_valid":
                (
                    validated_count
                    + unvalidated_count
                    == representative_count
                ),

            "directional_grounding_count_accounting_valid":
                (
                    directionally_grounded_count
                    + non_directionally_grounded_count
                    == representative_count
                ),

            "representatives_only_in_consolidated_set":
                True,

            "analogy_direction_preserved":
                True,

            "source_target_grounding_preserved":
                True,

            "analogical_forms_preserved":
                True,

            "orientation_patterns_preserved":
                True,

            "evidence_strengths_preserved":
                True,

            "duplicate_provenance_preserved":
                True,

            "new_analogical_expression_inference_performed":
                False,

            "analogical_evidence_strengthening_performed":
                False,

            "correspondence_mapping_performed":
                False,

            "property_level_mapping_performed":
                False,

            "analogy_extension_performed":
                False,

            "generic_similarity_reasoning_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "scientific_truth_verified":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "article_local_only":
                True,
        },

        "processing_boundaries":
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "final_analogical_intelligence_result",
    })

    return result


def build_final_analogical_intelligence_result_v1(
    article_consolidation_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Build the final canonical Phase 4.6.11 Analogical Intelligence result.

    This stage packages the completed article-local analogical analysis
    without adding new interpretation.

    It does NOT:
    - certify the result,
    - create or infer analogical expressions,
    - rescue invalid analogies,
    - create or repair source/target orientation,
    - create correspondence mappings,
    - map source properties to target properties,
    - extend analogies,
    - strengthen analogical evidence,
    - perform generic similarity reasoning,
    - perform procedural reasoning,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - perform new causal reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        article_consolidation_result,
        Mapping,
    ):
        raise AnalogicalIntelligenceError(
            "article_consolidation_result must be a mapping."
        )

    if (
        article_consolidation_result.get(
            "schema_version"
        )
        != "analogical_article_consolidation_v1"
    ):
        raise AnalogicalIntelligenceError(
            "Stage N requires analogical_article_consolidation_v1."
        )

    if (
        article_consolidation_result.get(
            "status"
        )
        != "ANALOGICAL_ARTICLE_CONSOLIDATION_COMPLETE"
    ):
        raise AnalogicalIntelligenceError(
            "Article analogical consolidation must be complete."
        )

    if (
        article_consolidation_result.get(
            "phase"
        )
        != "4.6.11"
    ):
        raise AnalogicalIntelligenceError(
            "Stage N requires Phase 4.6.11 input."
        )

    if (
        article_consolidation_result.get(
            "patch"
        )
        != "4.6.11M"
    ):
        raise AnalogicalIntelligenceError(
            "Stage N requires canonical 4.6.11M input."
        )

    if (
        article_consolidation_result.get(
            "next_stage"
        )
        != "final_analogical_intelligence_result"
    ):
        raise AnalogicalIntelligenceError(
            "Stage M must hand off to final_analogical_intelligence_result."
        )

    if (
        article_consolidation_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise AnalogicalIntelligenceError(
            "Analogical Intelligence must remain transient."
        )

    consolidated_expressions = list(
        article_consolidation_result.get(
            "consolidated_analogical_expressions"
        )
        or []
    )

    consolidated_sections = list(
        article_consolidation_result.get(
            "consolidated_analogical_sections"
        )
        or []
    )

    full_candidates = list(
        article_consolidation_result.get(
            "analogical_candidates"
        )
        or []
    )

    representative_candidates = list(
        article_consolidation_result.get(
            "representative_analogical_candidates"
        )
        or []
    )

    summary = dict(
        article_consolidation_result.get(
            "article_analogical_summary"
        )
        or {}
    )

    required_true_summary_fields = (
        "representative_count_matches_consolidated",
        "candidate_accounting_valid",
        "validation_count_accounting_valid",
        "directional_grounding_count_accounting_valid",
        "representatives_only_in_consolidated_set",
        "analogy_direction_preserved",
        "source_target_grounding_preserved",
        "analogical_forms_preserved",
        "orientation_patterns_preserved",
        "evidence_strengths_preserved",
        "duplicate_provenance_preserved",
        "article_local_only",
    )

    for field_name in required_true_summary_fields:
        if (
            summary.get(
                field_name
            )
            is not True
        ):
            raise AnalogicalIntelligenceError(
                field_name
                + " must be True before final Analogical Intelligence packaging."
            )

    required_false_summary_fields = (
        "new_analogical_expression_inference_performed",
        "analogical_evidence_strengthening_performed",
        "correspondence_mapping_performed",
        "property_level_mapping_performed",
        "analogy_extension_performed",
        "generic_similarity_reasoning_performed",
        "procedural_reasoning_performed",
        "quantitative_reasoning_performed",
        "temporal_reasoning_performed",
        "new_causal_reasoning_performed",
        "scientific_truth_verified",
        "truth_assessment_performed",
        "external_authority_check_performed",
        "fuzzy_similarity_performed",
    )

    for field_name in required_false_summary_fields:
        if (
            summary.get(
                field_name
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                field_name
                + " must remain False before final Analogical Intelligence packaging."
            )

    consolidated_ids = set()

    for expression in consolidated_expressions:
        if not isinstance(
            expression,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every consolidated analogical expression must be a mapping."
            )

        candidate_id = str(
            expression.get(
                "analogical_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise AnalogicalIntelligenceError(
                "Consolidated Analogical Candidate ID is required."
            )

        if candidate_id in consolidated_ids:
            raise AnalogicalIntelligenceError(
                "Duplicate consolidated Analogical Candidate ID encountered."
            )

        consolidated_ids.add(
            candidate_id
        )

        if (
            expression.get(
                "new_analogical_expression_inference_performed"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Final Analogical Intelligence must not add new analogical expressions."
            )

        if (
            expression.get(
                "analogical_evidence_strengthening_performed"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Final Analogical Intelligence must not strengthen analogical evidence."
            )

        if (
            expression.get(
                "analogical_correspondence_mapped"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Final Analogical Intelligence must not map analogical correspondences."
            )

        if (
            expression.get(
                "property_level_mapping_performed"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Final Analogical Intelligence must not create property-level mappings."
            )

        if (
            expression.get(
                "analogy_extended"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Final Analogical Intelligence must not extend analogies."
            )

        if (
            expression.get(
                "generic_similarity_reasoning_performed"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Final Analogical Intelligence must not perform generic similarity reasoning."
            )

        if (
            expression.get(
                "procedural_reasoning_performed"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Final Analogical Intelligence must not perform procedural reasoning."
            )

        if (
            expression.get(
                "quantitative_reasoning_performed"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Final Analogical Intelligence must not perform quantitative reasoning."
            )

        if (
            expression.get(
                "temporal_reasoning_performed"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Final Analogical Intelligence must not perform temporal reasoning."
            )

        if (
            expression.get(
                "new_causal_reasoning_performed"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Final Analogical Intelligence must not perform new causal reasoning."
            )

        if (
            expression.get(
                "truth_assessed"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Analogical Intelligence must not assess factual truth."
            )

        if (
            expression.get(
                "external_authority_checked"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Analogical Intelligence must not use external authority."
            )

        if (
            expression.get(
                "analogy_direction_preserved"
            )
            is not True
        ):
            raise AnalogicalIntelligenceError(
                "Final Analogical Intelligence must preserve analogy direction."
            )

    representative_ids = {
        str(
            candidate.get(
                "analogical_candidate_id"
            )
            or ""
        )
        for candidate in representative_candidates
    }

    if "" in representative_ids:
        raise AnalogicalIntelligenceError(
            "Representative Analogical Candidate ID is required."
        )

    if representative_ids != consolidated_ids:
        raise AnalogicalIntelligenceError(
            "Final consolidated analogical set must match representative candidates exactly."
        )

    boundaries = dict(
        article_consolidation_result.get(
            "processing_boundaries"
        )
        or {}
    )

    required_false_boundaries = (
        "new_analogical_expression_inference_performed",
        "analogical_evidence_strengthening_performed",
        "analogical_correspondence_mapping_performed",
        "property_level_mapping_performed",
        "analogy_extension_performed",
        "generic_similarity_reasoning_performed",
        "procedural_reasoning_performed",
        "quantitative_reasoning_performed",
        "temporal_reasoning_performed",
        "new_causal_reasoning_performed",
        "truth_assessment_performed",
        "external_authority_check_performed",
        "fuzzy_similarity_performed",
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
            raise AnalogicalIntelligenceError(
                boundary_name
                + " must remain False in final Analogical Intelligence."
            )

    if (
        boundaries.get(
            "article_analogical_consolidation_performed"
        )
        is not True
    ):
        raise AnalogicalIntelligenceError(
            "Article analogical consolidation boundary must be complete."
        )

    final_boundaries = dict(
        boundaries
    )

    final_boundaries[
        "final_analogical_result_built"
    ] = True

    final_boundaries[
        "analogical_certification_performed"
    ] = False

    article_identity = dict(
        article_consolidation_result.get(
            "article_identity"
        )
        or {}
    )

    result = {
        "schema_version":
            "analogical_intelligence_result_v1",

        "analogical_intelligence_version":
            article_consolidation_result.get(
                "analogical_intelligence_version"
            )
            or "analogical_intelligence_v1",

        "phase":
            "4.6.11",

        "patch":
            "4.6.11N",

        "status":
            "ANALOGICAL_INTELLIGENCE_RESULT_COMPLETE",

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

            "source_id":
                article_identity.get(
                    "source_id"
                )
                or article_consolidation_result.get(
                    "source_id"
                ),

            "document_id":
                article_identity.get(
                    "document_id"
                )
                or article_consolidation_result.get(
                    "document_id"
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

            "title":
                article_identity.get(
                    "title"
                )
                or article_consolidation_result.get(
                    "title"
                ),
        },

        "consolidated_analogical_expressions":
            consolidated_expressions,

        "consolidated_analogical_sections":
            consolidated_sections,

        "representative_analogical_candidates":
            representative_candidates,

        "analogical_candidates":
            full_candidates,

        "analogical_claim_units":
            list(
                article_consolidation_result.get(
                    "analogical_claim_units"
                )
                or []
            ),

        "article_analogical_summary":
            summary,

        "analogical_boundaries": {
            "article_local_only":
                True,

            "scientific_truth_verified":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_checked":
                False,

            "new_analogical_expression_inference_performed":
                False,

            "analogical_evidence_strengthening_performed":
                False,

            "correspondence_mapping_performed":
                False,

            "property_level_mapping_performed":
                False,

            "analogy_extension_performed":
                False,

            "generic_similarity_reasoning_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "linking_decisions_performed":
                False,

            "semantic_memory_write_performed":
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
                "4.6.11O",
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "analogical_intelligence_certification",
    }

    return result


def certify_analogical_intelligence_v1(
    final_analogical_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Hard-certify the canonical Phase 4.6.11 Analogical Intelligence result.

    Certification verifies structural integrity, directional analogy
    integrity, candidate accounting, representative integrity,
    provenance preservation, evidence integrity, and reasoning
    boundaries.

    It does NOT:
    - create new analogies,
    - rescue invalid analogies,
    - repair source/target orientation,
    - create correspondence mappings,
    - map source properties to target properties,
    - extend analogies,
    - strengthen evidence,
    - perform generic similarity reasoning,
    - perform procedural reasoning,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - perform new causal reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        final_analogical_result,
        Mapping,
    ):
        raise AnalogicalIntelligenceError(
            "final_analogical_result must be a mapping."
        )

    if (
        final_analogical_result.get(
            "schema_version"
        )
        != "analogical_intelligence_result_v1"
    ):
        raise AnalogicalIntelligenceError(
            "Stage O requires analogical_intelligence_result_v1."
        )

    if (
        final_analogical_result.get(
            "status"
        )
        != "ANALOGICAL_INTELLIGENCE_RESULT_COMPLETE"
    ):
        raise AnalogicalIntelligenceError(
            "Final Analogical Intelligence result must be complete."
        )

    if (
        final_analogical_result.get(
            "phase"
        )
        != "4.6.11"
    ):
        raise AnalogicalIntelligenceError(
            "Stage O requires Phase 4.6.11 input."
        )

    if (
        final_analogical_result.get(
            "patch"
        )
        != "4.6.11N"
    ):
        raise AnalogicalIntelligenceError(
            "Stage O requires canonical 4.6.11N input."
        )

    if (
        final_analogical_result.get(
            "next_stage"
        )
        != "analogical_intelligence_certification"
    ):
        raise AnalogicalIntelligenceError(
            "Stage N must hand off to analogical_intelligence_certification."
        )

    if (
        final_analogical_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise AnalogicalIntelligenceError(
            "Analogical Intelligence must remain transient."
        )

    identity = dict(
        final_analogical_result.get(
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

    for field in required_identity_fields:
        if not str(
            identity.get(
                field
            )
            or ""
        ).strip():
            raise AnalogicalIntelligenceError(
                "Required article identity field missing: "
                + field
            )

    consolidated_expressions = list(
        final_analogical_result.get(
            "consolidated_analogical_expressions"
        )
        or []
    )

    representative_candidates = list(
        final_analogical_result.get(
            "representative_analogical_candidates"
        )
        or []
    )

    full_candidates = list(
        final_analogical_result.get(
            "analogical_candidates"
        )
        or []
    )

    claim_units = list(
        final_analogical_result.get(
            "analogical_claim_units"
        )
        or []
    )

    consolidated_sections = list(
        final_analogical_result.get(
            "consolidated_analogical_sections"
        )
        or []
    )

    summary = dict(
        final_analogical_result.get(
            "article_analogical_summary"
        )
        or {}
    )

    required_true_summary_fields = (
        "representative_count_matches_consolidated",
        "candidate_accounting_valid",
        "validation_count_accounting_valid",
        "directional_grounding_count_accounting_valid",
        "representatives_only_in_consolidated_set",
        "analogy_direction_preserved",
        "source_target_grounding_preserved",
        "analogical_forms_preserved",
        "orientation_patterns_preserved",
        "evidence_strengths_preserved",
        "duplicate_provenance_preserved",
        "article_local_only",
    )

    for field_name in required_true_summary_fields:
        if (
            summary.get(
                field_name
            )
            is not True
        ):
            raise AnalogicalIntelligenceError(
                field_name
                + " must be verified before Analogical Intelligence certification."
            )

    if (
        summary.get(
            "representative_analogical_expression_count"
        )
        != len(
            consolidated_expressions
        )
    ):
        raise AnalogicalIntelligenceError(
            "Consolidated analogical expression count does not match summary."
        )

    if (
        len(
            representative_candidates
        )
        != len(
            consolidated_expressions
        )
    ):
        raise AnalogicalIntelligenceError(
            "Representative candidate count does not match consolidated analogical expressions."
        )

    if (
        summary.get(
            "total_candidate_count"
        )
        != len(
            full_candidates
        )
    ):
        raise AnalogicalIntelligenceError(
            "Full analogical candidate count does not match summary."
        )

    redundant_count = sum(
        1
        for candidate in full_candidates
        if candidate.get(
            "analogical_duplicate_resolution_status"
        )
        == "DUPLICATE_REDUNDANT"
    )

    if (
        summary.get(
            "duplicate_redundant_analogical_expression_count"
        )
        != redundant_count
    ):
        raise AnalogicalIntelligenceError(
            "Redundant analogical candidate count does not match summary."
        )

    if (
        len(
            representative_candidates
        )
        + redundant_count
        != len(
            full_candidates
        )
    ):
        raise AnalogicalIntelligenceError(
            "Analogical representative/redundant accounting is invalid."
        )

    consolidated_ids = [
        str(
            expression.get(
                "analogical_candidate_id"
            )
            or ""
        )
        for expression in consolidated_expressions
    ]

    representative_ids = [
        str(
            candidate.get(
                "analogical_candidate_id"
            )
            or ""
        )
        for candidate in representative_candidates
    ]

    full_candidate_ids = [
        str(
            candidate.get(
                "analogical_candidate_id"
            )
            or ""
        )
        for candidate in full_candidates
    ]

    if any(
        not candidate_id
        for candidate_id in consolidated_ids
    ):
        raise AnalogicalIntelligenceError(
            "Every consolidated analogical expression requires a candidate ID."
        )

    if any(
        not candidate_id
        for candidate_id in representative_ids
    ):
        raise AnalogicalIntelligenceError(
            "Every representative analogical candidate requires a candidate ID."
        )

    if any(
        not candidate_id
        for candidate_id in full_candidate_ids
    ):
        raise AnalogicalIntelligenceError(
            "Every analogical candidate requires a candidate ID."
        )

    if (
        len(
            consolidated_ids
        )
        != len(
            set(
                consolidated_ids
            )
        )
    ):
        raise AnalogicalIntelligenceError(
            "Duplicate consolidated analogical candidate IDs are not allowed."
        )

    if (
        len(
            representative_ids
        )
        != len(
            set(
                representative_ids
            )
        )
    ):
        raise AnalogicalIntelligenceError(
            "Duplicate representative analogical candidate IDs are not allowed."
        )

    if (
        len(
            full_candidate_ids
        )
        != len(
            set(
                full_candidate_ids
            )
        )
    ):
        raise AnalogicalIntelligenceError(
            "Duplicate full analogical candidate IDs are not allowed."
        )

    if (
        set(
            consolidated_ids
        )
        != set(
            representative_ids
        )
    ):
        raise AnalogicalIntelligenceError(
            "Consolidated expressions and representative analogical candidates disagree."
        )

    if not set(
        representative_ids
    ).issubset(
        set(
            full_candidate_ids
        )
    ):
        raise AnalogicalIntelligenceError(
            "Representative analogical candidates must exist in the full candidate collection."
        )

    invalid_strong_count = 0
    non_directional_strong_count = 0
    cross_sentence_strong_count = 0

    valid_evidence_strengths = {
        "STRONG",
        "MODERATE",
        "LIMITED",
        "INSUFFICIENT",
    }

    for expression in consolidated_expressions:
        if not isinstance(
            expression,
            Mapping,
        ):
            raise AnalogicalIntelligenceError(
                "Every consolidated analogical expression must be a mapping."
            )

        if (
            expression.get(
                "analogy_direction_preserved"
            )
            is not True
        ):
            raise AnalogicalIntelligenceError(
                "Every consolidated analogical expression must preserve analogy direction."
            )

        if (
            expression.get(
                "new_analogical_expression_inference_performed"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Certified Analogical Intelligence must not add new analogical expressions."
            )

        if (
            expression.get(
                "analogical_evidence_strengthening_performed"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Certified Analogical Intelligence must not strengthen evidence."
            )

        if (
            expression.get(
                "analogical_correspondence_mapped"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Certified Analogical Intelligence must not map analogical correspondences."
            )

        if (
            expression.get(
                "property_level_mapping_performed"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Certified Analogical Intelligence must not create property-level mappings."
            )

        if (
            expression.get(
                "analogy_extended"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Certified Analogical Intelligence must not extend analogies."
            )

        if (
            expression.get(
                "generic_similarity_reasoning_performed"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Certified Analogical Intelligence must not perform generic similarity reasoning."
            )

        if (
            expression.get(
                "procedural_reasoning_performed"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Certified Analogical Intelligence must not perform procedural reasoning."
            )

        if (
            expression.get(
                "quantitative_reasoning_performed"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Certified Analogical Intelligence must not perform quantitative reasoning."
            )

        if (
            expression.get(
                "temporal_reasoning_performed"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Certified Analogical Intelligence must not perform temporal reasoning."
            )

        if (
            expression.get(
                "new_causal_reasoning_performed"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Certified Analogical Intelligence must not perform new causal reasoning."
            )

        if (
            expression.get(
                "truth_assessed"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Analogical Intelligence must not assess factual truth."
            )

        if (
            expression.get(
                "external_authority_checked"
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                "Analogical Intelligence must not use external authority."
            )

        evidence_strength = str(
            expression.get(
                "analogical_evidence_strength"
            )
            or ""
        )

        if evidence_strength not in valid_evidence_strengths:
            raise AnalogicalIntelligenceError(
                "Consolidated analogical expression has invalid evidence strength."
            )

        if (
            expression.get(
                "final_analogical_expression_validated"
            )
            is not True
            and evidence_strength
            == "STRONG"
        ):
            invalid_strong_count += 1

        directionally_grounded = (
            expression.get(
                "directional_grounding_supported"
            )
            is True
        )

        if (
            not directionally_grounded
            and evidence_strength
            == "STRONG"
        ):
            non_directional_strong_count += 1

        if (
            expression.get(
                "cross_sentence_analogical_valid"
            )
            is True
            and evidence_strength
            == "STRONG"
        ):
            cross_sentence_strong_count += 1

    if invalid_strong_count != 0:
        raise AnalogicalIntelligenceError(
            "Unvalidated analogical expressions must never certify with STRONG evidence."
        )

    if non_directional_strong_count != 0:
        raise AnalogicalIntelligenceError(
            "Non-directionally-grounded analogical expressions must never certify with STRONG evidence."
        )

    if cross_sentence_strong_count != 0:
        raise AnalogicalIntelligenceError(
            "Cross-sentence analogical expressions must never certify with STRONG evidence."
        )

    analogical_boundaries = dict(
        final_analogical_result.get(
            "analogical_boundaries"
        )
        or {}
    )

    if (
        analogical_boundaries.get(
            "article_local_only"
        )
        is not True
    ):
        raise AnalogicalIntelligenceError(
            "Final Analogical Intelligence must remain article-local."
        )

    required_false_analogical_boundaries = (
        "scientific_truth_verified",
        "truth_assessment_performed",
        "external_authority_checked",
        "new_analogical_expression_inference_performed",
        "analogical_evidence_strengthening_performed",
        "correspondence_mapping_performed",
        "property_level_mapping_performed",
        "analogy_extension_performed",
        "generic_similarity_reasoning_performed",
        "procedural_reasoning_performed",
        "quantitative_reasoning_performed",
        "temporal_reasoning_performed",
        "new_causal_reasoning_performed",
        "fuzzy_similarity_performed",
        "linking_decisions_performed",
        "semantic_memory_write_performed",
        "persistence_performed",
    )

    for boundary_name in required_false_analogical_boundaries:
        if (
            analogical_boundaries.get(
                boundary_name
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                boundary_name
                + " must remain False."
            )

    processing_boundaries = dict(
        final_analogical_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        processing_boundaries.get(
            "article_analogical_consolidation_performed"
        )
        is not True
    ):
        raise AnalogicalIntelligenceError(
            "Article analogical consolidation must be complete."
        )

    if (
        processing_boundaries.get(
            "final_analogical_result_built"
        )
        is not True
    ):
        raise AnalogicalIntelligenceError(
            "Final Analogical Intelligence result must already be built."
        )

    if (
        processing_boundaries.get(
            "analogical_certification_performed"
        )
        is not False
    ):
        raise AnalogicalIntelligenceError(
            "Input must not already be certified."
        )

    certification = dict(
        final_analogical_result.get(
            "certification"
        )
        or {}
    )

    if (
        certification.get(
            "performed"
        )
        is not False
        or certification.get(
            "certified"
        )
        is not False
        or certification.get(
            "certification_stage"
        )
        != "4.6.11O"
    ):
        raise AnalogicalIntelligenceError(
            "Stage N certification state is invalid."
        )

    required_false_summary_fields = (
        "new_analogical_expression_inference_performed",
        "analogical_evidence_strengthening_performed",
        "correspondence_mapping_performed",
        "property_level_mapping_performed",
        "analogy_extension_performed",
        "generic_similarity_reasoning_performed",
        "procedural_reasoning_performed",
        "quantitative_reasoning_performed",
        "temporal_reasoning_performed",
        "new_causal_reasoning_performed",
        "scientific_truth_verified",
        "truth_assessment_performed",
        "external_authority_check_performed",
        "fuzzy_similarity_performed",
    )

    for field_name in required_false_summary_fields:
        if (
            summary.get(
                field_name
            )
            is not False
        ):
            raise AnalogicalIntelligenceError(
                field_name
                + " must remain False at certification."
            )

    certified_processing_boundaries = dict(
        processing_boundaries
    )

    certified_processing_boundaries[
        "analogical_certification_performed"
    ] = True

    certified_processing_boundaries[
        "analogical_intelligence_certified"
    ] = True

    result = dict(
        final_analogical_result
    )

    result.update({
        "schema_version":
            "certified_analogical_intelligence_result_v1",

        "patch":
            "4.6.11O",

        "status":
            "ANALOGICAL_INTELLIGENCE_CERTIFIED",

        "processing_boundaries":
            certified_processing_boundaries,

        "certification": {
            "performed":
                True,

            "certified":
                True,

            "certification_stage":
                "4.6.11O",

            "certification_scope":
                "ARTICLE_LOCAL_ANALOGICAL_INTELLIGENCE",

            "structural_integrity_verified":
                True,

            "candidate_accounting_verified":
                True,

            "representative_analogical_integrity_verified":
                True,

            "provenance_preserved":
                True,

            "analogy_direction_integrity_verified":
                True,

            "source_target_grounding_integrity_verified":
                True,

            "analogical_form_integrity_verified":
                True,

            "orientation_pattern_integrity_verified":
                True,

            "evidence_strength_integrity_verified":
                True,

            "unvalidated_strength_cap_verified":
                True,

            "non_directional_strength_cap_verified":
                True,

            "cross_sentence_strength_cap_verified":
                True,

            "duplicate_provenance_integrity_verified":
                True,

            "boundary_integrity_verified":
                True,

            "scientific_truth_verified":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
                False,

            "new_analogical_expression_inference_performed":
                False,

            "analogical_evidence_strengthening_performed":
                False,

            "correspondence_mapping_performed":
                False,

            "property_level_mapping_performed":
                False,

            "analogy_extension_performed":
                False,

            "generic_similarity_reasoning_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
                False,

            "semantic_memory_write_performed":
                False,

            "persistence_performed":
                False,
        },

        "analogical_certification_summary": {
            "article_id":
                identity.get(
                    "article_id"
                ),

            "candidate_count":
                len(
                    full_candidates
                ),

            "claim_unit_count":
                len(
                    claim_units
                ),

            "section_count":
                len(
                    consolidated_sections
                ),

            "representative_analogical_expression_count":
                len(
                    representative_candidates
                ),

            "consolidated_analogical_expression_count":
                len(
                    consolidated_expressions
                ),

            "duplicate_redundant_analogical_expression_count":
                redundant_count,

            "validated_analogical_expression_count":
                summary.get(
                    "validated_analogical_expression_count"
                ),

            "unvalidated_analogical_expression_count":
                summary.get(
                    "unvalidated_analogical_expression_count"
                ),

            "same_sentence_validated_analogical_count":
                summary.get(
                    "same_sentence_validated_analogical_count"
                ),

            "cross_sentence_validated_analogical_count":
                summary.get(
                    "cross_sentence_validated_analogical_count"
                ),

            "directionally_grounded_analogical_count":
                summary.get(
                    "directionally_grounded_analogical_count"
                ),

            "non_directionally_grounded_analogical_count":
                summary.get(
                    "non_directionally_grounded_analogical_count"
                ),

            "invalid_strong_count":
                invalid_strong_count,

            "non_directional_strong_count":
                non_directional_strong_count,

            "cross_sentence_strong_count":
                cross_sentence_strong_count,

            "analogy_direction_preserved":
                True,

            "source_target_grounding_preserved":
                True,

            "analogical_forms_preserved":
                True,

            "orientation_patterns_preserved":
                True,

            "duplicate_provenance_preserved":
                True,

            "article_local_only":
                True,

            "scientific_truth_verified":
                False,

            "certification_passed":
                True,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "similarity_intelligence",
    })

    return result
