from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class ProceduralIntelligenceError(ValueError):
    """Raised when Procedural Intelligence receives invalid input."""




def validate_procedural_intelligence_intake_v1(
    certified_quantitative_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate the certified Phase 4.6.9 Quantitative Intelligence result
    before Phase 4.6.10 Procedural Intelligence begins.

    This stage performs intake validation only.

    It does NOT:
    - identify procedural steps,
    - interpret procedural ordering,
    - classify instructions,
    - infer missing actions,
    - infer prerequisites,
    - perform quantitative reasoning,
    - perform temporal reasoning beyond validating boundaries,
    - perform new causal reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        certified_quantitative_result,
        Mapping,
    ):
        raise ProceduralIntelligenceError(
            "certified_quantitative_result must be a mapping."
        )

    if (
        certified_quantitative_result.get(
            "schema_version"
        )
        != "certified_quantitative_intelligence_result_v1"
    ):
        raise ProceduralIntelligenceError(
            "Phase 4.6.10 requires certified_quantitative_intelligence_result_v1."
        )

    if (
        certified_quantitative_result.get(
            "status"
        )
        != "QUANTITATIVE_INTELLIGENCE_CERTIFIED"
    ):
        raise ProceduralIntelligenceError(
            "Quantitative Intelligence must be certified before Procedural Intelligence."
        )

    if (
        certified_quantitative_result.get(
            "phase"
        )
        != "4.6.9"
    ):
        raise ProceduralIntelligenceError(
            "Phase 4.6.10 requires certified Phase 4.6.9 input."
        )

    if (
        certified_quantitative_result.get(
            "patch"
        )
        != "4.6.9O"
    ):
        raise ProceduralIntelligenceError(
            "Phase 4.6.10 requires canonical 4.6.9O input."
        )

    if (
        certified_quantitative_result.get(
            "next_stage"
        )
        != "procedural_intelligence"
    ):
        raise ProceduralIntelligenceError(
            "Certified Quantitative Intelligence must hand off to procedural_intelligence."
        )

    if (
        certified_quantitative_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise ProceduralIntelligenceError(
            "Procedural Intelligence intake must remain article-local and transient."
        )

    certification = dict(
        certified_quantitative_result.get(
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
        != "4.6.9O"
        or certification.get(
            "certification_scope"
        )
        != "ARTICLE_LOCAL_QUANTITATIVE_INTELLIGENCE"
    ):
        raise ProceduralIntelligenceError(
            "Certified Quantitative Intelligence certification envelope is invalid."
        )

    required_true_certification_fields = (
        "structural_integrity_verified",
        "candidate_accounting_verified",
        "representative_quantitative_integrity_verified",
        "provenance_preserved",
        "quantitative_value_integrity_verified",
        "quantitative_unit_integrity_verified",
        "quantity_role_integrity_verified",
        "quantitative_orientation_integrity_verified",
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
            raise ProceduralIntelligenceError(
                "Required Quantitative Intelligence certification field is not verified: "
                + field_name
            )

    required_false_certification_fields = (
        "scientific_truth_verified",
        "truth_assessment_performed",
        "external_authority_check_performed",
        "derived_calculation_performed",
        "unit_conversion_performed",
        "trend_inference_performed",
        "aggregate_calculation_performed",
        "quantitative_inference_performed",
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
            raise ProceduralIntelligenceError(
                "Quantitative certification boundary must remain False: "
                + field_name
            )

    processing_boundaries = dict(
        certified_quantitative_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        processing_boundaries.get(
            "quantitative_certification_performed"
        )
        is not True
    ):
        raise ProceduralIntelligenceError(
            "Quantitative certification processing boundary must be complete."
        )

    if (
        processing_boundaries.get(
            "quantitative_intelligence_certified"
        )
        is not True
    ):
        raise ProceduralIntelligenceError(
            "Quantitative Intelligence must be marked certified."
        )

    quantitative_boundaries = dict(
        certified_quantitative_result.get(
            "quantitative_boundaries"
        )
        or {}
    )

    if (
        quantitative_boundaries.get(
            "article_local_only"
        )
        is not True
    ):
        raise ProceduralIntelligenceError(
            "Certified Quantitative Intelligence must remain article-local."
        )

    required_false_quantitative_boundaries = (
        "scientific_truth_verified",
        "truth_assessment_performed",
        "external_authority_checked",
        "new_quantitative_expression_inference_performed",
        "derived_calculation_performed",
        "unit_conversion_performed",
        "trend_inference_performed",
        "aggregate_calculation_performed",
        "final_quantitative_referent_selection_performed",
        "quantitative_evidence_strengthening_performed",
        "quantitative_inference_performed",
        "temporal_reasoning_performed",
        "new_causal_reasoning_performed",
        "fuzzy_similarity_performed",
        "linking_decisions_performed",
        "semantic_memory_write_performed",
        "persistence_performed",
    )

    for field_name in required_false_quantitative_boundaries:
        if (
            quantitative_boundaries.get(
                field_name
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Certified quantitative boundary must remain False: "
                + field_name
            )

    article_identity = dict(
        certified_quantitative_result.get(
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
            raise ProceduralIntelligenceError(
                "Required article identity field missing: "
                + field_name
            )

    return {
        "schema_version":
            "procedural_intelligence_intake_v1",

        "procedural_intelligence_version":
            "procedural_intelligence_v1",

        "phase":
            "4.6.10",

        "patch":
            "4.6.10B",

        "status":
            "PROCEDURAL_INTELLIGENCE_INTAKE_VALIDATED",

        "article_identity":
            article_identity,

        "certified_quantitative_result":
            dict(
                certified_quantitative_result
            ),

        "intake_validation": {
            "certified_quantitative_schema_verified":
                True,

            "certified_quantitative_status_verified":
                True,

            "certified_quantitative_patch_verified":
                True,

            "quantitative_certification_verified":
                True,

            "quantitative_boundary_integrity_verified":
                True,

            "article_identity_verified":
                True,

            "procedural_reasoning_not_preperformed":
                True,

            "article_local_only":
                True,
        },

        "processing_boundaries": {
            "procedural_intake_validation_performed":
                True,

            "procedural_claim_unit_preparation_performed":
                False,

            "procedural_signal_interpretation_performed":
                False,

            "procedural_candidate_extraction_performed":
                False,

            "procedural_step_ordering_performed":
                False,

            "procedural_prerequisite_inference_performed":
                False,

            "missing_step_inference_performed":
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
            "procedural_claim_unit_preparation",
    }



def build_procedural_claim_units_v1(
    certified_quantitative_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Build canonical Phase 4.6.10 Procedural Claim Units from
    certified Phase 4.6.9 Quantitative Intelligence.

    This is a one-to-one structural preparation stage.

    It does NOT:
    - reparse the article body,
    - identify procedural signals,
    - classify instructions,
    - extract procedural steps,
    - infer step ordering,
    - infer prerequisites,
    - infer missing steps,
    - perform quantitative reasoning,
    - perform temporal reasoning,
    - perform new causal reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    intake = validate_procedural_intelligence_intake_v1(
        certified_quantitative_result
    )

    if (
        intake.get(
            "status"
        )
        != "PROCEDURAL_INTELLIGENCE_INTAKE_VALIDATED"
    ):
        raise ProceduralIntelligenceError(
            "Canonical Procedural Intelligence intake was not validated."
        )

    identity = dict(
        certified_quantitative_result.get(
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

    quantitative_units = list(
        certified_quantitative_result.get(
            "quantitative_claim_units"
        )
        or []
    )

    if not article_id:
        raise ProceduralIntelligenceError(
            "Certified quantitative article_id is required."
        )

    procedural_units = []
    procedural_sections = []

    seen_procedural_ids = set()
    seen_quantitative_ids = set()
    seen_statement_ids = set()
    seen_sentence_ids = set()

    previous_global_index = None

    units_by_section = {}
    section_metadata = {}

    for quantitative_unit in quantitative_units:
        if not isinstance(
            quantitative_unit,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
                "Every certified Quantitative Claim Unit must be a mapping."
            )

        quantitative_claim_unit_id = str(
            quantitative_unit.get(
                "quantitative_claim_unit_id"
            )
            or ""
        )

        statement_id = str(
            quantitative_unit.get(
                "statement_evidence_id"
            )
            or ""
        )

        sentence_id = str(
            quantitative_unit.get(
                "sentence_id"
            )
            or ""
        )

        section_id = str(
            quantitative_unit.get(
                "section_id"
            )
            or ""
        )

        if not quantitative_claim_unit_id:
            raise ProceduralIntelligenceError(
                "Quantitative Claim Unit ID is required."
            )

        if not quantitative_claim_unit_id.startswith(
            "quantitative_claim_"
        ):
            raise ProceduralIntelligenceError(
                "Unexpected Quantitative Claim Unit ID format."
            )

        if not statement_id:
            raise ProceduralIntelligenceError(
                "statement_evidence_id is required."
            )

        if not sentence_id:
            raise ProceduralIntelligenceError(
                "sentence_id is required."
            )

        if not section_id:
            raise ProceduralIntelligenceError(
                "section_id is required."
            )

        if quantitative_claim_unit_id in seen_quantitative_ids:
            raise ProceduralIntelligenceError(
                "Duplicate Quantitative Claim Unit ID."
            )

        if statement_id in seen_statement_ids:
            raise ProceduralIntelligenceError(
                "Duplicate statement_evidence_id."
            )

        if sentence_id in seen_sentence_ids:
            raise ProceduralIntelligenceError(
                "Duplicate sentence_id."
            )

        if (
            quantitative_unit.get(
                "article_id"
            )
            != article_id
        ):
            raise ProceduralIntelligenceError(
                "Quantitative Claim Unit article identity mismatch."
            )

        global_index = quantitative_unit.get(
            "sentence_global_index"
        )

        article_position = quantitative_unit.get(
            "article_position"
        )

        if not isinstance(
            global_index,
            int,
        ):
            raise ProceduralIntelligenceError(
                "sentence_global_index must be an integer."
            )

        if not isinstance(
            article_position,
            int,
        ):
            raise ProceduralIntelligenceError(
                "article_position must be an integer."
            )

        if (
            previous_global_index is not None
            and global_index <= previous_global_index
        ):
            raise ProceduralIntelligenceError(
                "Certified Quantitative Claim Units are not "
                "in canonical sentence order."
            )

        quantitative_state = dict(
            quantitative_unit.get(
                "quantitative_analysis_state"
            )
            or {}
        )

        required_complete_quantitative_stages = (
            "numeric_measurement_signal_interpretation",
            "quantitative_candidate_extraction",
            "entity_concept_grounding",
            "unit_measurement_normalization",
            "quantity_role_comparison_orientation",
            "same_sentence_quantitative_validation",
            "cross_sentence_quantitative_validation",
            "quantitative_evidence_assessment",
            "duplicate_quantitative_resolution",
        )

        for stage_name in required_complete_quantitative_stages:
            if (
                quantitative_state.get(
                    stage_name
                )
                != "COMPLETE"
            ):
                raise ProceduralIntelligenceError(
                    "Quantitative Claim Unit analysis is incomplete at "
                    + stage_name
                    + "."
                )

        upstream_boundaries = dict(
            quantitative_unit.get(
                "processing_boundaries"
            )
            or {}
        )

        required_false_upstream_boundaries = (
            "derived_calculation_performed",
            "quantitative_inference_performed",
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
                raise ProceduralIntelligenceError(
                    "Upstream Quantitative Claim Unit boundary must remain False: "
                    + boundary_name
                )

        procedural_claim_unit_id = (
            "procedural_claim_"
            + quantitative_claim_unit_id[
                len("quantitative_claim_"):
            ]
        )

        if procedural_claim_unit_id in seen_procedural_ids:
            raise ProceduralIntelligenceError(
                "Duplicate Procedural Claim Unit ID."
            )

        procedural_unit = {
            "procedural_claim_unit_id":
                procedural_claim_unit_id,

            "upstream_quantitative_claim_unit_id":
                quantitative_claim_unit_id,

            "upstream_causal_claim_unit_id":
                quantitative_unit.get(
                    "upstream_causal_claim_unit_id"
                ),

            "upstream_relational_claim_unit_id":
                quantitative_unit.get(
                    "upstream_relational_claim_unit_id"
                ),

            "upstream_logical_claim_unit_id":
                quantitative_unit.get(
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
                quantitative_unit.get(
                    "section_evidence_unit_id"
                ),

            "section_index":
                quantitative_unit.get(
                    "section_index"
                ),

            "section_title":
                quantitative_unit.get(
                    "section_title"
                ),

            "heading_level":
                quantitative_unit.get(
                    "heading_level"
                ),

            "block_id":
                quantitative_unit.get(
                    "block_id"
                ),

            "paragraph_id":
                quantitative_unit.get(
                    "paragraph_id"
                ),

            "block_type":
                quantitative_unit.get(
                    "block_type"
                ),

            "block_index":
                quantitative_unit.get(
                    "block_index"
                ),

            "sentence_index":
                quantitative_unit.get(
                    "sentence_index"
                ),

            "sentence_global_index":
                global_index,

            "article_position":
                article_position,

            "claim_index_in_section":
                quantitative_unit.get(
                    "claim_index_in_section"
                ),

            "text":
                quantitative_unit.get(
                    "text"
                ),

            "word_count":
                quantitative_unit.get(
                    "word_count"
                ),

            "character_count":
                quantitative_unit.get(
                    "character_count"
                ),

            "statement_form":
                quantitative_unit.get(
                    "statement_form"
                ),

            "canonical_claim_candidate":
                quantitative_unit.get(
                    "canonical_claim_candidate"
                )
                is True,

            "evidence_context":
                dict(
                    quantitative_unit.get(
                        "evidence_context"
                    )
                    or {}
                ),

            "upstream_quantitative_analysis_state":
                quantitative_state,

            "upstream_quantitative_processing_boundaries":
                upstream_boundaries,

            "procedural_analysis_state": {
                "procedural_signal_interpretation":
                    "PENDING",

                "procedural_candidate_extraction":
                    "PENDING",

                "entity_concept_grounding":
                    "PENDING",

                "procedural_action_normalization":
                    "PENDING",

                "procedure_role_orientation":
                    "PENDING",

                "same_sentence_procedural_validation":
                    "PENDING",

                "cross_sentence_procedural_validation":
                    "PENDING",

                "procedural_evidence_assessment":
                    "PENDING",

                "duplicate_procedural_resolution":
                    "PENDING",
            },

            "processing_boundaries": {
                "article_local_only":
                    True,

                "procedural_claim_unit_prepared":
                    True,

                "article_body_reparsed":
                    False,

                "procedural_signal_interpretation_performed":
                    False,

                "procedural_candidate_extraction_performed":
                    False,

                "procedural_step_ordering_performed":
                    False,

                "procedural_prerequisite_inference_performed":
                    False,

                "missing_step_inference_performed":
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

        procedural_units.append(
            procedural_unit
        )

        units_by_section.setdefault(
            section_id,
            [],
        ).append(
            procedural_unit
        )

        if section_id not in section_metadata:
            section_metadata[
                section_id
            ] = {
                "section_id":
                    section_id,

                "section_index":
                    quantitative_unit.get(
                        "section_index"
                    ),

                "section_title":
                    quantitative_unit.get(
                        "section_title"
                    ),

                "heading_level":
                    quantitative_unit.get(
                        "heading_level"
                    ),
            }

        seen_procedural_ids.add(
            procedural_claim_unit_id
        )

        seen_quantitative_ids.add(
            quantitative_claim_unit_id
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

    for unit in procedural_units:
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

        procedural_sections.append({
            **metadata,

            "upstream_quantitative_claim_count":
                len(
                    section_units
                ),

            "procedural_claim_unit_count":
                len(
                    section_units
                ),

            "procedural_claim_units":
                section_units,
        })

    if (
        len(
            procedural_units
        )
        != len(
            quantitative_units
        )
    ):
        raise ProceduralIntelligenceError(
            "Procedural Claim Unit construction must remain "
            "one-to-one with Quantitative Claim Units."
        )

    return {
        "schema_version":
            "procedural_claim_units_v1",

        "procedural_intelligence_version":
            "procedural_intelligence_v1",

        "phase":
            "4.6.10",

        "patch":
            "4.6.10C",

        "status":
            "PROCEDURAL_CLAIM_UNITS_PREPARED",

        "article_identity":
            identity,

        "quantitative_claim_unit_count":
            len(
                quantitative_units
            ),

        "procedural_claim_unit_count":
            len(
                procedural_units
            ),

        "section_count":
            len(
                procedural_sections
            ),

        "procedural_sections":
            procedural_sections,

        "procedural_claim_units":
            procedural_units,

        "construction_summary": {
            "source_quantitative_claim_unit_count":
                len(
                    quantitative_units
                ),

            "procedural_claim_unit_count":
                len(
                    procedural_units
                ),

            "one_to_one_quantitative_mapping":
                (
                    len(
                        procedural_units
                    )
                    == len(
                        quantitative_units
                    )
                ),

            "canonical_order_preserved":
                True,

            "canonical_text_preserved":
                True,

            "evidence_context_preserved":
                True,

            "quantitative_context_preserved":
                True,

            "article_body_reparsed":
                False,

            "procedural_signals_interpreted":
                False,

            "procedural_steps_inferred":
                False,

            "procedural_ordering_inferred":
                False,

            "missing_steps_inferred":
                False,
        },

        "processing_boundaries": {
            "article_body_reparsed":
                False,

            "procedural_claim_units_prepared":
                True,

            "procedural_signal_interpretation_performed":
                False,

            "procedural_candidate_extraction_performed":
                False,

            "procedural_step_ordering_performed":
                False,

            "procedural_prerequisite_inference_performed":
                False,

            "missing_step_inference_performed":
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
            "procedural_signal_interpretation",
    }



def interpret_procedural_signals_v1(
    procedural_claim_units_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Interpret explicit article-local procedural wording.

    This stage identifies and classifies procedural signals only.

    It does NOT:
    - extract final procedural action/step relationships,
    - infer missing steps,
    - infer prerequisites,
    - infer a procedure merely from generic modal wording,
    - infer a procedure merely from generic chronology,
    - perform full step ordering,
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
        procedural_claim_units_result,
        Mapping,
    ):
        raise ProceduralIntelligenceError(
            "procedural_claim_units_result must be a mapping."
        )

    if (
        procedural_claim_units_result.get(
            "schema_version"
        )
        != "procedural_claim_units_v1"
    ):
        raise ProceduralIntelligenceError(
            "Stage D requires procedural_claim_units_v1."
        )

    if (
        procedural_claim_units_result.get(
            "status"
        )
        != "PROCEDURAL_CLAIM_UNITS_PREPARED"
    ):
        raise ProceduralIntelligenceError(
            "Procedural Claim Units must be prepared before Stage D."
        )

    if (
        procedural_claim_units_result.get(
            "phase"
        )
        != "4.6.10"
    ):
        raise ProceduralIntelligenceError(
            "Stage D requires Phase 4.6.10 input."
        )

    if (
        procedural_claim_units_result.get(
            "patch"
        )
        != "4.6.10C"
    ):
        raise ProceduralIntelligenceError(
            "Stage D requires canonical 4.6.10C input."
        )

    if (
        procedural_claim_units_result.get(
            "next_stage"
        )
        != "procedural_signal_interpretation"
    ):
        raise ProceduralIntelligenceError(
            "Stage C must hand off to procedural_signal_interpretation."
        )

    if (
        procedural_claim_units_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise ProceduralIntelligenceError(
            "Procedural Intelligence must remain transient."
        )

    action_verb = (
        r"(?:"
        r"measure|record|plot|check|compare|find|follow|"
        r"place|position|wrap|stretch|remove|enter|select|choose|"
        r"read|track|monitor|ask|call|talk|consult|determine|"
        r"repeat|continue|wait|apply|insert|attach|open|close|"
        r"turn|press|click|mix|add|remove|wash|rinse|"
        r"take|use"
        r")"
    )

    signal_specs = (
        (
            "EXPLICIT_METHOD_HEADING_OR_PHRASE",
            "PROCEDURAL_METHOD",
            re.compile(
                r"\b(?:"
                r"how\s+to|"
                r"how\s+do\s+you|"
                r"step[- ]by[- ]step|"
                r"steps?\s+to|"
                r"instructions?\s+for"
                r")\b",
                re.IGNORECASE,
            ),
        ),
        (
            "EXPLICIT_NEXT_STEP",
            "PROCEDURAL_SEQUENCE",
            re.compile(
                r"\b(?:"
                r"the\s+next\s+step\s+is\s+to|"
                r"next\s+step\s*:?"
                r")\b",
                re.IGNORECASE,
            ),
        ),
        (
            "ORDERED_STEP_MARKER",
            "PROCEDURAL_SEQUENCE",
            re.compile(
                r"(?:^|(?<=[.!?])\s+)"
                r"(?:first|second|third|fourth|fifth|finally)"
                r"\s*(?:,|:)\s*",
                re.IGNORECASE,
            ),
        ),
        (
            "THEN_ACTION",
            "PROCEDURAL_SEQUENCE_ACTION",
            re.compile(
                r"\bthen\s+"
                + action_verb
                + r"\b",
                re.IGNORECASE,
            ),
        ),
        (
            "SENTENCE_INITIAL_IMPERATIVE",
            "PROCEDURAL_ACTION",
            re.compile(
                r"^\s*(?:"
                r"please\s+|"
                r"then\s+|"
                r"next\s+|"
                r"first\s+|"
                r"finally\s+"
                r")?"
                + action_verb
                + r"\b",
                re.IGNORECASE,
            ),
        ),
        (
            "PURPOSE_METHOD_USING",
            "PROCEDURAL_METHOD",
            re.compile(
                r"\b"
                + action_verb
                + r"\b"
                r"[^.!?;]{0,90}?"
                r"\busing\s+(?:a|an|the|your|his|her|their)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "BY_ACTION_METHOD",
            "PROCEDURAL_METHOD",
            re.compile(
                r"\bby\s+"
                r"(?:measuring|recording|plotting|checking|comparing|"
                r"finding|following|placing|positioning|wrapping|"
                r"stretching|removing|entering|selecting|choosing|"
                r"reading|tracking|monitoring|asking|calling|"
                r"consulting|determining|repeating|applying|"
                r"inserting|attaching|mixing|adding|washing|rinsing)"
                r"\b",
                re.IGNORECASE,
            ),
        ),
        (
            "ACTION_UNTIL_BOUNDARY",
            "PROCEDURAL_TERMINATION_CONDITION",
            re.compile(
                r"\b"
                + action_verb
                + r"\b"
                r"[^.!?;]{0,100}?"
                r"\buntil\b",
                re.IGNORECASE,
            ),
        ),
        (
            "CONDITIONAL_NEXT_STEP",
            "PROCEDURAL_CONDITION",
            re.compile(
                r"\bif\b"
                r"[^.!?;]{1,140}?"
                r"\b(?:next\s+step|then\s+"
                + action_verb
                + r")\b",
                re.IGNORECASE,
            ),
        ),
    )

    ambiguous_specs = (
        (
            "GENERIC_MODAL",
            re.compile(
                r"\b(?:can|could|may|might|should)\b",
                re.IGNORECASE,
            ),
            "MODAL_ALONE_NOT_PROCEDURAL",
        ),
        (
            "GENERIC_AFTER",
            re.compile(
                r"\bafter\b",
                re.IGNORECASE,
            ),
            "CHRONOLOGY_ALONE_NOT_PROCEDURAL",
        ),
        (
            "GENERIC_BEFORE",
            re.compile(
                r"\bbefore\b",
                re.IGNORECASE,
            ),
            "CHRONOLOGY_ALONE_NOT_PROCEDURAL",
        ),
        (
            "GENERIC_FIRST",
            re.compile(
                r"\bfirst\b",
                re.IGNORECASE,
            ),
            "ORDINAL_ALONE_NOT_PROCEDURAL",
        ),
        (
            "GENERIC_SECOND",
            re.compile(
                r"\bsecond\b",
                re.IGNORECASE,
            ),
            "ORDINAL_ALONE_NOT_PROCEDURAL",
        ),
        (
            "GENERIC_USE",
            re.compile(
                r"\b(?:use|uses|used|using)\b",
                re.IGNORECASE,
            ),
            "ACTION_WORD_ALONE_NOT_PROCEDURAL",
        ),
        (
            "GENERIC_TAKE",
            re.compile(
                r"\b(?:take|takes|took|taken|taking)\b",
                re.IGNORECASE,
            ),
            "ACTION_WORD_ALONE_NOT_PROCEDURAL",
        ),
    )

    source_units = list(
        procedural_claim_units_result.get(
            "procedural_claim_units"
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
            raise ProceduralIntelligenceError(
                "Every Procedural Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "procedural_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "procedural_signal_interpretation"
            )
            != "PENDING"
        ):
            raise ProceduralIntelligenceError(
                "Procedural signal interpretation must be PENDING before Stage D."
            )

        if (
            state.get(
                "procedural_candidate_extraction"
            )
            != "PENDING"
        ):
            raise ProceduralIntelligenceError(
                "Procedural candidate extraction must remain PENDING during Stage D."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "procedural_claim_unit_prepared"
            )
            is not True
        ):
            raise ProceduralIntelligenceError(
                "Procedural Claim Unit preparation boundary is incomplete."
            )

        required_false_boundaries = (
            "procedural_signal_interpretation_performed",
            "procedural_candidate_extraction_performed",
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

        for boundary_name in required_false_boundaries:
            if (
                boundaries.get(
                    boundary_name
                )
                is not False
            ):
                raise ProceduralIntelligenceError(
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

                    "procedural_semantic_class":
                        semantic_class,

                    "matched_text":
                        match.group(0),

                    "character_start":
                        match.start(),

                    "character_end":
                        match.end(),

                    "article_asserted_signal":
                        True,

                    "procedural_candidate_extracted":
                        False,

                    "procedural_action_normalized":
                        False,

                    "procedural_step_order_assigned":
                        False,

                    "procedural_prerequisite_inferred":
                        False,

                    "missing_step_inferred":
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
                        "AMBIGUOUS_PROCEDURAL_LEXEME_DEFERRED",

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

                    "procedural_inference_performed":
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
            "procedural_signal_interpretation"
        ] = "COMPLETE"

        interpreted_boundaries = dict(
            boundaries
        )

        interpreted_boundaries[
            "procedural_signal_interpretation_performed"
        ] = True

        interpreted_boundaries[
            "procedural_candidate_extraction_performed"
        ] = False

        interpreted_boundaries[
            "procedural_step_ordering_performed"
        ] = False

        interpreted_boundaries[
            "procedural_prerequisite_inference_performed"
        ] = False

        interpreted_boundaries[
            "missing_step_inference_performed"
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
            "procedural_signals":
                signals,

            "procedural_signal_exclusions":
                exclusions,

            "procedural_signal_count":
                unit_total,

            "procedural_signal_exclusion_count":
                len(
                    exclusions
                ),

            "has_procedural_signal":
                unit_total > 0,

            "procedural_signal_interpretation_scope":
                "ARTICLE_LOCAL_EXPLICIT_PROCEDURAL_LEXICAL_SIGNAL_ONLY",

            "procedural_analysis_state":
                interpreted_state,

            "processing_boundaries":
                interpreted_boundaries,
        })

        interpreted_units.append(
            interpreted_unit
        )

        unit_id = str(
            interpreted_unit.get(
                "procedural_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise ProceduralIntelligenceError(
                "Every interpreted Procedural Claim Unit requires an ID."
            )

        if unit_id in interpreted_by_id:
            raise ProceduralIntelligenceError(
                "Duplicate interpreted Procedural Claim Unit ID."
            )

        interpreted_by_id[
            unit_id
        ] = interpreted_unit

    interpreted_sections = []

    for section in (
        procedural_claim_units_result.get(
            "procedural_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
                "Every procedural section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "procedural_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise ProceduralIntelligenceError(
                    "Every section Procedural Claim Unit reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "procedural_claim_unit_id"
                )
                or ""
            )

            resolved_unit = interpreted_by_id.get(
                unit_id
            )

            if resolved_unit is None:
                raise ProceduralIntelligenceError(
                    "Procedural section references an unknown claim unit."
                )

            section_units.append(
                resolved_unit
            )

        interpreted_sections.append({
            **dict(
                section
            ),

            "procedural_claim_units":
                section_units,

            "procedural_signal_unit_count":
                sum(
                    1
                    for unit in section_units
                    if unit.get(
                        "has_procedural_signal"
                    )
                    is True
                ),

            "procedural_signal_count":
                sum(
                    int(
                        unit.get(
                            "procedural_signal_count"
                        )
                        or 0
                    )
                    for unit in section_units
                ),

            "procedural_signal_exclusion_count":
                sum(
                    int(
                        unit.get(
                            "procedural_signal_exclusion_count"
                        )
                        or 0
                    )
                    for unit in section_units
                ),
        })

    result = dict(
        procedural_claim_units_result
    )

    result_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    result_boundaries[
        "procedural_signal_interpretation_performed"
    ] = True

    result_boundaries[
        "procedural_candidate_extraction_performed"
    ] = False

    result_boundaries[
        "procedural_step_ordering_performed"
    ] = False

    result_boundaries[
        "procedural_prerequisite_inference_performed"
    ] = False

    result_boundaries[
        "missing_step_inference_performed"
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
            "procedural_signal_interpretation_v1",

        "patch":
            "4.6.10D",

        "status":
            "PROCEDURAL_SIGNAL_INTERPRETATION_COMPLETE",

        "procedural_sections":
            interpreted_sections,

        "procedural_claim_units":
            interpreted_units,

        "procedural_signal_summary": {
            "claim_unit_count":
                len(
                    interpreted_units
                ),

            "units_with_procedural_signals":
                units_with_signals,

            "total_procedural_signal_count":
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

            "procedural_candidates_extracted":
                False,

            "procedural_step_ordering_performed":
                False,

            "procedural_prerequisite_inference_performed":
                False,

            "missing_step_inference_performed":
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
            "procedural_candidate_extraction",
    })

    return result



def extract_procedural_candidates_v1(
    procedural_signal_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Extract conservative article-local procedural candidates from
    interpreted procedural signals.

    This stage constructs procedural candidate objects only.

    It does NOT:
    - ground actions or objects to entities/concepts,
    - normalize procedural actions,
    - assign final procedure roles,
    - infer missing actions,
    - infer missing steps,
    - infer prerequisites,
    - establish cross-sentence step ordering,
    - perform full temporal reasoning,
    - perform quantitative reasoning,
    - perform new causal reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    import hashlib

    if not isinstance(
        procedural_signal_result,
        Mapping,
    ):
        raise ProceduralIntelligenceError(
            "procedural_signal_result must be a mapping."
        )

    if (
        procedural_signal_result.get(
            "schema_version"
        )
        != "procedural_signal_interpretation_v1"
    ):
        raise ProceduralIntelligenceError(
            "Stage E requires procedural_signal_interpretation_v1."
        )

    if (
        procedural_signal_result.get(
            "status"
        )
        != "PROCEDURAL_SIGNAL_INTERPRETATION_COMPLETE"
    ):
        raise ProceduralIntelligenceError(
            "Procedural signal interpretation must be complete."
        )

    if (
        procedural_signal_result.get(
            "phase"
        )
        != "4.6.10"
    ):
        raise ProceduralIntelligenceError(
            "Stage E requires Phase 4.6.10 input."
        )

    if (
        procedural_signal_result.get(
            "patch"
        )
        != "4.6.10D"
    ):
        raise ProceduralIntelligenceError(
            "Stage E requires canonical 4.6.10D input."
        )

    if (
        procedural_signal_result.get(
            "next_stage"
        )
        != "procedural_candidate_extraction"
    ):
        raise ProceduralIntelligenceError(
            "Stage D must hand off to procedural_candidate_extraction."
        )

    if (
        procedural_signal_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise ProceduralIntelligenceError(
            "Procedural Intelligence must remain transient."
        )

    primary_signal_types = {
        "THEN_ACTION",
        "SENTENCE_INITIAL_IMPERATIVE",
        "PURPOSE_METHOD_USING",
        "BY_ACTION_METHOD",
        "ACTION_UNTIL_BOUNDARY",
        "EXPLICIT_NEXT_STEP",
        "CONDITIONAL_NEXT_STEP",
    }

    contextual_signal_types = {
        "EXPLICIT_METHOD_HEADING_OR_PHRASE",
        "ORDERED_STEP_MARKER",
    }

    candidate_form_by_signal = {
        "THEN_ACTION":
            "SEQUENCED_ACTION",

        "SENTENCE_INITIAL_IMPERATIVE":
            "DIRECT_ACTION_STEP",

        "PURPOSE_METHOD_USING":
            "METHOD_ACTION",

        "BY_ACTION_METHOD":
            "METHOD_ACTION",

        "ACTION_UNTIL_BOUNDARY":
            "ACTION_WITH_TERMINATION_CONDITION",

        "EXPLICIT_NEXT_STEP":
            "EXPLICIT_STEP_FRAME",

        "CONDITIONAL_NEXT_STEP":
            "CONDITIONAL_STEP_FRAME",
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
            "procedural_candidate_"
            + hashlib.sha256(
                raw.encode(
                    "utf-8"
                )
            ).hexdigest()[:24]
        )

    source_units = list(
        procedural_signal_result.get(
            "procedural_claim_units"
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
            raise ProceduralIntelligenceError(
                "Every Stage-D Procedural Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "procedural_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "procedural_signal_interpretation"
            )
            != "COMPLETE"
        ):
            raise ProceduralIntelligenceError(
                "Procedural signal interpretation must be COMPLETE before Stage E."
            )

        if (
            state.get(
                "procedural_candidate_extraction"
            )
            != "PENDING"
        ):
            raise ProceduralIntelligenceError(
                "Procedural candidate extraction must be PENDING before Stage E."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "procedural_signal_interpretation_performed"
            )
            is not True
        ):
            raise ProceduralIntelligenceError(
                "Stage-D procedural interpretation boundary is incomplete."
            )

        required_false_boundaries = (
            "procedural_candidate_extraction_performed",
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

        for boundary_name in required_false_boundaries:
            if (
                boundaries.get(
                    boundary_name
                )
                is not False
            ):
                raise ProceduralIntelligenceError(
                    boundary_name
                    + " must be False before Stage E."
                )

        unit_id = str(
            unit.get(
                "procedural_claim_unit_id"
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
            raise ProceduralIntelligenceError(
                "Procedural Claim Unit ID is required."
            )

        signals = list(
            unit.get(
                "procedural_signals"
            )
            or []
        )

        contextual_signals = []

        for signal in signals:
            if not isinstance(
                signal,
                Mapping,
            ):
                raise ProceduralIntelligenceError(
                    "Every procedural signal must be a mapping."
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
                raise ProceduralIntelligenceError(
                    "Every procedural signal must be a mapping."
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
                raise ProceduralIntelligenceError(
                    "Procedural signal character span is invalid."
                )

            if (
                sentence_text[
                    start:end
                ]
                != matched_text
            ):
                raise ProceduralIntelligenceError(
                    "Procedural signal text does not match its source span."
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
                        "CONTEXTUAL_SIGNAL_REQUIRES_PROCEDURAL_ACTION_ANCHOR",

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
                        "UNSUPPORTED_PROCEDURAL_PRIMARY_SIGNAL",

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
                        "EMPTY_PROCEDURAL_SIGNAL_TEXT",

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
                raise ProceduralIntelligenceError(
                    "Duplicate Procedural Candidate ID."
                )

            candidate = {
                "procedural_candidate_id":
                    candidate_id,

                "procedural_claim_unit_id":
                    unit_id,

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

                "procedural_semantic_class":
                    signal.get(
                        "procedural_semantic_class"
                    ),

                "signal_matched_text":
                    matched_text,

                "signal_character_start":
                    start,

                "signal_character_end":
                    end,

                "candidate_procedural_form":
                    candidate_form_by_signal[
                        signal_type
                    ],

                "contextual_procedural_signals": [
                    dict(
                        item
                    )
                    for item in contextual_signals
                ],

                "contextual_procedural_signal_count":
                    len(
                        contextual_signals
                    ),

                "article_asserted_candidate":
                    True,

                "same_sentence_candidate":
                    True,

                "entity_concept_grounded":
                    False,

                "procedural_action_normalized":
                    False,

                "procedure_role_orientation_resolved":
                    False,

                "same_sentence_procedural_validated":
                    False,

                "cross_sentence_procedural_validated":
                    False,

                "procedural_evidence_assessed":
                    False,

                "duplicate_resolution_performed":
                    False,

                "procedural_step_order_assigned":
                    False,

                "procedural_prerequisite_inferred":
                    False,

                "missing_step_inferred":
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
            "procedural_candidate_extraction"
        ] = "COMPLETE"

        extracted_boundaries = dict(
            boundaries
        )

        extracted_boundaries[
            "procedural_candidate_extraction_performed"
        ] = True

        extracted_boundaries[
            "procedural_step_ordering_performed"
        ] = False

        extracted_boundaries[
            "procedural_prerequisite_inference_performed"
        ] = False

        extracted_boundaries[
            "missing_step_inference_performed"
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
            "procedural_candidates":
                unit_candidates,

            "procedural_candidate_count":
                len(
                    unit_candidates
                ),

            "procedural_extraction_rejections":
                unit_rejections,

            "procedural_extraction_rejection_count":
                len(
                    unit_rejections
                ),

            "procedural_analysis_state":
                extracted_state,

            "processing_boundaries":
                extracted_boundaries,
        })

        extracted_units.append(
            extracted_unit
        )

        if unit_id in extracted_by_id:
            raise ProceduralIntelligenceError(
                "Duplicate extracted Procedural Claim Unit ID."
            )

        extracted_by_id[
            unit_id
        ] = extracted_unit

    extracted_sections = []

    for section in (
        procedural_signal_result.get(
            "procedural_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
                "Every procedural section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "procedural_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise ProceduralIntelligenceError(
                    "Every section Procedural Claim Unit reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "procedural_claim_unit_id"
                )
                or ""
            )

            resolved_unit = extracted_by_id.get(
                unit_id
            )

            if resolved_unit is None:
                raise ProceduralIntelligenceError(
                    "Procedural section references an unknown claim unit."
                )

            section_units.append(
                resolved_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "procedural_candidates"
                )
                or []
            )
        ]

        extracted_sections.append({
            **dict(
                section
            ),

            "procedural_claim_units":
                section_units,

            "procedural_candidate_count":
                len(
                    section_candidates
                ),

            "procedural_candidates":
                section_candidates,
        })

    result = dict(
        procedural_signal_result
    )

    result_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    result_boundaries[
        "procedural_candidate_extraction_performed"
    ] = True

    result_boundaries[
        "procedural_step_ordering_performed"
    ] = False

    result_boundaries[
        "procedural_prerequisite_inference_performed"
    ] = False

    result_boundaries[
        "missing_step_inference_performed"
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
            "procedural_candidates_v1",

        "patch":
            "4.6.10E",

        "status":
            "PROCEDURAL_CANDIDATE_EXTRACTION_COMPLETE",

        "procedural_sections":
            extracted_sections,

        "procedural_claim_units":
            extracted_units,

        "procedural_candidates":
            all_candidates,

        "procedural_extraction_summary": {
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

            "entity_concept_grounding_performed":
                False,

            "procedural_action_normalization_performed":
                False,

            "procedure_role_orientation_performed":
                False,

            "procedural_step_ordering_performed":
                False,

            "procedural_prerequisite_inference_performed":
                False,

            "missing_step_inference_performed":
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



def ground_procedural_candidates_v1(
    procedural_candidates_result: Mapping[str, Any],
    entity_concept_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Ground procedural candidates against canonical article-local
    Phase 4.6.2 Entity & Concept Intelligence objects.

    This stage identifies semantic objects present in each procedural
    candidate's source sentence.

    It does NOT:
    - select a final procedural actor, object, instrument, or target,
    - create new entities or concepts,
    - perform fuzzy semantic similarity,
    - normalize procedural actions,
    - assign final procedural roles,
    - assign step order,
    - infer prerequisites,
    - infer missing steps,
    - perform quantitative reasoning,
    - perform full temporal reasoning,
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
        procedural_candidates_result,
        Mapping,
    ):
        raise ProceduralIntelligenceError(
            "procedural_candidates_result must be a mapping."
        )

    if not isinstance(
        entity_concept_result,
        Mapping,
    ):
        raise ProceduralIntelligenceError(
            "entity_concept_result must be a mapping."
        )

    if (
        procedural_candidates_result.get(
            "schema_version"
        )
        != "procedural_candidates_v1"
    ):
        raise ProceduralIntelligenceError(
            "Stage F requires procedural_candidates_v1."
        )

    if (
        procedural_candidates_result.get(
            "status"
        )
        != "PROCEDURAL_CANDIDATE_EXTRACTION_COMPLETE"
    ):
        raise ProceduralIntelligenceError(
            "Procedural candidate extraction must be complete."
        )

    if (
        procedural_candidates_result.get(
            "phase"
        )
        != "4.6.10"
    ):
        raise ProceduralIntelligenceError(
            "Stage F requires Phase 4.6.10 input."
        )

    if (
        procedural_candidates_result.get(
            "patch"
        )
        != "4.6.10E"
    ):
        raise ProceduralIntelligenceError(
            "Stage F requires canonical 4.6.10E input."
        )

    if (
        procedural_candidates_result.get(
            "next_stage"
        )
        != "entity_concept_grounding"
    ):
        raise ProceduralIntelligenceError(
            "Stage E must hand off to entity_concept_grounding."
        )

    if (
        procedural_candidates_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise ProceduralIntelligenceError(
            "Procedural Intelligence must remain transient."
        )

    if (
        entity_concept_result.get(
            "schema_version"
        )
        != "entity_concept_intelligence_result_v1"
    ):
        raise ProceduralIntelligenceError(
            "Stage F requires canonical entity_concept_intelligence_result_v1."
        )

    if (
        entity_concept_result.get(
            "status"
        )
        != "ENTITY_CONCEPT_INTELLIGENCE_COMPLETE"
    ):
        raise ProceduralIntelligenceError(
            "Entity & Concept Intelligence must be complete."
        )

    if (
        entity_concept_result.get(
            "phase"
        )
        != "4.6.2"
    ):
        raise ProceduralIntelligenceError(
            "Stage F requires Phase 4.6.2 Entity & Concept Intelligence."
        )

    semantic_objects = list(
        entity_concept_result.get(
            "semantic_objects"
        )
        or []
    )

    if not semantic_objects:
        raise ProceduralIntelligenceError(
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
        raise ProceduralIntelligenceError(
            "Entity & Concept Intelligence must be article-local."
        )

    if (
        entity_boundaries.get(
            "semantic_memory_write_performed"
        )
        is not False
    ):
        raise ProceduralIntelligenceError(
            "Unexpected Semantic Memory write detected upstream."
        )

    if (
        entity_boundaries.get(
            "reasoning_performed"
        )
        is not False
    ):
        raise ProceduralIntelligenceError(
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
        procedural_candidates_result.get(
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
        raise ProceduralIntelligenceError(
            "Procedural article_id is required."
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
        raise ProceduralIntelligenceError(
            "Entity/Concept Intelligence article identity mismatch."
        )

    prepared_objects = []

    for semantic_object in semantic_objects:
        if not isinstance(
            semantic_object,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
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
            raise ProceduralIntelligenceError(
                "Semantic object is missing canonical_text."
            )

        if semantic_kind not in {
            "entity",
            "concept",
        }:
            raise ProceduralIntelligenceError(
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
            raise ProceduralIntelligenceError(
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

                    "final_procedural_role_assigned":
                        False,

                    "procedural_participant_selected":
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
        procedural_candidates_result.get(
            "procedural_candidates"
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
            raise ProceduralIntelligenceError(
                "Every procedural candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "procedural_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise ProceduralIntelligenceError(
                "Procedural candidate ID is required."
            )

        if candidate_id in seen_candidate_ids:
            raise ProceduralIntelligenceError(
                "Duplicate Procedural Candidate ID."
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
            raise ProceduralIntelligenceError(
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

            "final_procedural_participant_selected":
                False,

            "procedural_action_normalized":
                False,

            "procedure_role_orientation_resolved":
                False,

            "same_sentence_procedural_validated":
                False,

            "cross_sentence_procedural_validated":
                False,

            "procedural_evidence_assessed":
                False,

            "duplicate_resolution_performed":
                False,

            "procedural_step_order_assigned":
                False,

            "procedural_prerequisite_inferred":
                False,

            "missing_step_inferred":
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
            "procedural_candidate_id"
        ):
            candidate
        for candidate in grounded_candidates
    }

    grounded_units = []
    seen_unit_ids = set()

    for unit in (
        procedural_candidates_result.get(
            "procedural_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
                "Every Procedural Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "procedural_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise ProceduralIntelligenceError(
                "Procedural Claim Unit ID is required."
            )

        if unit_id in seen_unit_ids:
            raise ProceduralIntelligenceError(
                "Duplicate Procedural Claim Unit ID."
            )

        seen_unit_ids.add(
            unit_id
        )

        state = dict(
            unit.get(
                "procedural_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "procedural_candidate_extraction"
            )
            != "COMPLETE"
        ):
            raise ProceduralIntelligenceError(
                "Procedural candidate extraction must be COMPLETE before grounding."
            )

        if (
            state.get(
                "entity_concept_grounding"
            )
            != "PENDING"
        ):
            raise ProceduralIntelligenceError(
                "Entity/concept grounding must be PENDING."
            )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "procedural_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise ProceduralIntelligenceError(
                    "Every unit Procedural Candidate reference must be a mapping."
                )

            candidate_id = str(
                old_candidate.get(
                    "procedural_candidate_id"
                )
                or ""
            )

            grounded = grounded_by_id.get(
                candidate_id
            )

            if grounded is None:
                raise ProceduralIntelligenceError(
                    "Procedural candidate/unit identity mismatch."
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
                "procedural_candidate_extraction_performed"
            )
            is not True
        ):
            raise ProceduralIntelligenceError(
                "Stage-E extraction boundary is incomplete."
            )

        required_false_boundaries = (
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

        for boundary_name in required_false_boundaries:
            if (
                updated_boundaries.get(
                    boundary_name
                )
                is not False
            ):
                raise ProceduralIntelligenceError(
                    boundary_name
                    + " must be False before Stage F."
                )

        updated_boundaries[
            "entity_concept_grounding_performed"
        ] = True

        updated_boundaries[
            "procedural_step_ordering_performed"
        ] = False

        updated_boundaries[
            "procedural_prerequisite_inference_performed"
        ] = False

        updated_boundaries[
            "missing_step_inference_performed"
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
            "procedural_candidates":
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

            "procedural_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        grounded_units.append(
            updated_unit
        )

    grounded_units_by_id = {
        unit.get(
            "procedural_claim_unit_id"
        ):
            unit
        for unit in grounded_units
    }

    grounded_sections = []

    for section in (
        procedural_candidates_result.get(
            "procedural_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
                "Every procedural section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "procedural_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise ProceduralIntelligenceError(
                    "Every section Procedural Claim Unit reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "procedural_claim_unit_id"
                )
                or ""
            )

            grounded_unit = (
                grounded_units_by_id.get(
                    unit_id
                )
            )

            if grounded_unit is None:
                raise ProceduralIntelligenceError(
                    "Procedural section/unit grounding mismatch."
                )

            section_units.append(
                grounded_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "procedural_candidates"
                )
                or []
            )
        ]

        grounded_sections.append({
            **dict(
                section
            ),

            "procedural_claim_units":
                section_units,

            "procedural_candidates":
                section_candidates,

            "procedural_candidate_count":
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
        procedural_candidates_result
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
        "procedural_step_ordering_performed"
    ] = False

    boundaries[
        "procedural_prerequisite_inference_performed"
    ] = False

    boundaries[
        "missing_step_inference_performed"
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
            "procedural_entity_concept_grounding_v1",

        "patch":
            "4.6.10F",

        "status":
            "PROCEDURAL_ENTITY_CONCEPT_GROUNDING_COMPLETE",

        "procedural_sections":
            grounded_sections,

        "procedural_claim_units":
            grounded_units,

        "procedural_candidates":
            grounded_candidates,

        "entity_concept_grounding_summary": {
            "semantic_object_count":
                len(
                    semantic_objects
                ),

            "procedural_candidate_count":
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

            "final_procedural_participant_selection_performed":
                False,

            "procedural_action_normalization_performed":
                False,

            "procedure_role_orientation_performed":
                False,

            "procedural_step_ordering_performed":
                False,

            "procedural_prerequisite_inference_performed":
                False,

            "missing_step_inference_performed":
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
            "procedural_action_normalization",
    })

    return result



def normalize_procedural_actions_v1(
    entity_concept_grounding_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Normalize explicitly expressed procedural action forms into
    conservative canonical lexical action representations.

    This stage normalizes only actions directly licensed by the
    article-local candidate source text.

    It does NOT:
    - infer unstated actions,
    - merge semantically related but lexically different actions,
    - select a final procedural actor, object, instrument, or target,
    - assign final procedural roles,
    - establish step order,
    - infer prerequisites,
    - infer missing steps,
    - perform same-sentence procedural validation,
    - perform cross-sentence procedural validation,
    - perform quantitative reasoning,
    - perform full temporal reasoning,
    - perform new causal reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    import re

    if not isinstance(
        entity_concept_grounding_result,
        Mapping,
    ):
        raise ProceduralIntelligenceError(
            "entity_concept_grounding_result must be a mapping."
        )

    if (
        entity_concept_grounding_result.get(
            "schema_version"
        )
        != "procedural_entity_concept_grounding_v1"
    ):
        raise ProceduralIntelligenceError(
            "Stage G requires procedural_entity_concept_grounding_v1."
        )

    if (
        entity_concept_grounding_result.get(
            "status"
        )
        != "PROCEDURAL_ENTITY_CONCEPT_GROUNDING_COMPLETE"
    ):
        raise ProceduralIntelligenceError(
            "Entity/concept grounding must be complete before procedural action normalization."
        )

    if (
        entity_concept_grounding_result.get(
            "phase"
        )
        != "4.6.10"
    ):
        raise ProceduralIntelligenceError(
            "Stage G requires Phase 4.6.10 input."
        )

    if (
        entity_concept_grounding_result.get(
            "patch"
        )
        != "4.6.10F"
    ):
        raise ProceduralIntelligenceError(
            "Stage G requires canonical 4.6.10F input."
        )

    if (
        entity_concept_grounding_result.get(
            "next_stage"
        )
        != "procedural_action_normalization"
    ):
        raise ProceduralIntelligenceError(
            "Stage F must hand off to procedural_action_normalization."
        )

    if (
        entity_concept_grounding_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise ProceduralIntelligenceError(
            "Procedural Intelligence must remain transient."
        )

    action_registry = {
        "measure": {
            "measure",
            "measures",
            "measured",
            "measuring",
        },

        "record": {
            "record",
            "records",
            "recorded",
            "recording",
        },

        "plot": {
            "plot",
            "plots",
            "plotted",
            "plotting",
        },

        "check": {
            "check",
            "checks",
            "checked",
            "checking",
        },

        "compare": {
            "compare",
            "compares",
            "compared",
            "comparing",
        },

        "find": {
            "find",
            "finds",
            "found",
            "finding",
        },

        "follow": {
            "follow",
            "follows",
            "followed",
            "following",
        },

        "place": {
            "place",
            "places",
            "placed",
            "placing",
        },

        "position": {
            "position",
            "positions",
            "positioned",
            "positioning",
        },

        "wrap": {
            "wrap",
            "wraps",
            "wrapped",
            "wrapping",
        },

        "stretch": {
            "stretch",
            "stretches",
            "stretched",
            "stretching",
        },

        "remove": {
            "remove",
            "removes",
            "removed",
            "removing",
        },

        "enter": {
            "enter",
            "enters",
            "entered",
            "entering",
        },

        "select": {
            "select",
            "selects",
            "selected",
            "selecting",
        },

        "choose": {
            "choose",
            "chooses",
            "chose",
            "chosen",
            "choosing",
        },

        "read": {
            "read",
            "reads",
            "reading",
        },

        "track": {
            "track",
            "tracks",
            "tracked",
            "tracking",
        },

        "monitor": {
            "monitor",
            "monitors",
            "monitored",
            "monitoring",
        },

        "ask": {
            "ask",
            "asks",
            "asked",
            "asking",
        },

        "call": {
            "call",
            "calls",
            "called",
            "calling",
        },

        "talk": {
            "talk",
            "talks",
            "talked",
            "talking",
        },

        "consult": {
            "consult",
            "consults",
            "consulted",
            "consulting",
        },

        "determine": {
            "determine",
            "determines",
            "determined",
            "determining",
        },

        "repeat": {
            "repeat",
            "repeats",
            "repeated",
            "repeating",
        },

        "continue": {
            "continue",
            "continues",
            "continued",
            "continuing",
        },

        "wait": {
            "wait",
            "waits",
            "waited",
            "waiting",
        },

        "apply": {
            "apply",
            "applies",
            "applied",
            "applying",
        },

        "insert": {
            "insert",
            "inserts",
            "inserted",
            "inserting",
        },

        "attach": {
            "attach",
            "attaches",
            "attached",
            "attaching",
        },

        "open": {
            "open",
            "opens",
            "opened",
            "opening",
        },

        "close": {
            "close",
            "closes",
            "closed",
            "closing",
        },

        "turn": {
            "turn",
            "turns",
            "turned",
            "turning",
        },

        "press": {
            "press",
            "presses",
            "pressed",
            "pressing",
        },

        "click": {
            "click",
            "clicks",
            "clicked",
            "clicking",
        },

        "mix": {
            "mix",
            "mixes",
            "mixed",
            "mixing",
        },

        "add": {
            "add",
            "adds",
            "added",
            "adding",
        },

        "wash": {
            "wash",
            "washes",
            "washed",
            "washing",
        },

        "rinse": {
            "rinse",
            "rinses",
            "rinsed",
            "rinsing",
        },

        "take": {
            "take",
            "takes",
            "took",
            "taken",
            "taking",
        },

        "use": {
            "use",
            "uses",
            "used",
            "using",
        },

        "treat": {
            "treat",
            "treats",
            "treated",
            "treating",
        },
    }

    alias_registry = {}

    for canonical_action, aliases in action_registry.items():
        for alias in aliases:
            normalized_alias = str(
                alias
            ).lower().strip()

            if normalized_alias in alias_registry:
                raise ProceduralIntelligenceError(
                    "Duplicate procedural action alias detected: "
                    + normalized_alias
                )

            alias_registry[
                normalized_alias
            ] = canonical_action

    def collect_action_matches(
        source_text: str,
    ) -> list[dict[str, Any]]:
        matches = []

        for match in re.finditer(
            r"\b[a-zA-Z]+\b",
            str(
                source_text
                or ""
            ),
        ):
            surface = match.group(
                0
            )

            canonical = alias_registry.get(
                surface.lower()
            )

            if canonical is None:
                continue

            matches.append({
                "canonical_action":
                    canonical,

                "matched_action_surface":
                    surface,

                "action_character_start":
                    match.start(),

                "action_character_end":
                    match.end(),

                "normalization_strategy":
                    "EXACT_LEXICAL_ALIAS",

                "semantic_synonym_resolution_performed":
                    False,
            })

        return matches

    def choose_licensed_action(
        candidate: Mapping[str, Any],
    ) -> dict[str, Any]:
        candidate_id = str(
            candidate.get(
                "procedural_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise ProceduralIntelligenceError(
                "Procedural candidate ID is required."
            )

        if (
            candidate.get(
                "procedural_action_normalized"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Candidate must not already be procedurally action-normalized."
            )

        signal_type = str(
            candidate.get(
                "signal_type"
            )
            or ""
        )

        source_text = str(
            candidate.get(
                "source_text"
            )
            or ""
        )

        signal_text = str(
            candidate.get(
                "signal_matched_text"
            )
            or ""
        )

        if not signal_type:
            raise ProceduralIntelligenceError(
                "Procedural candidate signal_type is required."
            )

        if not source_text:
            raise ProceduralIntelligenceError(
                "Procedural candidate source_text is required."
            )

        if not signal_text:
            raise ProceduralIntelligenceError(
                "Procedural candidate signal text is required."
            )

        action_matches = collect_action_matches(
            source_text
        )

        payload = {
            "action_normalization_status":
                "UNSUPPORTED",

            "raw_procedural_signal_text":
                signal_text,

            "canonical_action":
                None,

            "matched_action_surface":
                None,

            "action_character_start":
                None,

            "action_character_end":
                None,

            "action_normalization_strategy":
                None,

            "action_normalization_reason":
                "NO_EXPLICIT_CANONICAL_ACTION_MATCH",

            "action_candidate_match_count":
                len(
                    action_matches
                ),

            "article_expressed_action_only":
                True,

            "semantic_synonym_resolution_performed":
                False,
        }

        selected = None

        if signal_type == "THEN_ACTION":
            pattern = re.compile(
                r"\bthen\s+([a-zA-Z]+)\b",
                re.IGNORECASE,
            )

            match = pattern.search(
                source_text
            )

            if match is not None:
                canonical = alias_registry.get(
                    match.group(
                        1
                    ).lower()
                )

                if canonical is not None:
                    selected = {
                        "canonical_action":
                            canonical,

                        "matched_action_surface":
                            match.group(
                                1
                            ),

                        "action_character_start":
                            match.start(
                                1
                            ),

                        "action_character_end":
                            match.end(
                                1
                            ),

                        "normalization_strategy":
                            "SIGNAL_LICENSED_THEN_ACTION",
                    }

        elif signal_type == "SENTENCE_INITIAL_IMPERATIVE":
            pattern = re.compile(
                r"^\s*"
                r"(?:please\s+)?"
                r"(?:(?:then|next|first|finally)\s+)?"
                r"([a-zA-Z]+)\b",
                re.IGNORECASE,
            )

            match = pattern.search(
                source_text
            )

            if match is not None:
                canonical = alias_registry.get(
                    match.group(
                        1
                    ).lower()
                )

                if canonical is not None:
                    selected = {
                        "canonical_action":
                            canonical,

                        "matched_action_surface":
                            match.group(
                                1
                            ),

                        "action_character_start":
                            match.start(
                                1
                            ),

                        "action_character_end":
                            match.end(
                                1
                            ),

                        "normalization_strategy":
                            "SIGNAL_LICENSED_INITIAL_ACTION",
                    }

        elif signal_type == "BY_ACTION_METHOD":
            pattern = re.compile(
                r"\bby\s+([a-zA-Z]+)\b",
                re.IGNORECASE,
            )

            match = pattern.search(
                source_text
            )

            if match is not None:
                canonical = alias_registry.get(
                    match.group(
                        1
                    ).lower()
                )

                if canonical is not None:
                    selected = {
                        "canonical_action":
                            canonical,

                        "matched_action_surface":
                            match.group(
                                1
                            ),

                        "action_character_start":
                            match.start(
                                1
                            ),

                        "action_character_end":
                            match.end(
                                1
                            ),

                        "normalization_strategy":
                            "SIGNAL_LICENSED_BY_ACTION",
                    }

        elif signal_type in {
            "EXPLICIT_NEXT_STEP",
            "CONDITIONAL_NEXT_STEP",
        }:
            pattern = re.compile(
                r"\bnext\s+step\s+is\s+to\s+"
                r"([a-zA-Z]+)\b",
                re.IGNORECASE,
            )

            match = pattern.search(
                source_text
            )

            if match is not None:
                canonical = alias_registry.get(
                    match.group(
                        1
                    ).lower()
                )

                if canonical is not None:
                    selected = {
                        "canonical_action":
                            canonical,

                        "matched_action_surface":
                            match.group(
                                1
                            ),

                        "action_character_start":
                            match.start(
                                1
                            ),

                        "action_character_end":
                            match.end(
                                1
                            ),

                        "normalization_strategy":
                            "SIGNAL_LICENSED_NEXT_STEP_ACTION",
                    }

        elif signal_type in {
            "ACTION_UNTIL_BOUNDARY",
            "PURPOSE_METHOD_USING",
        }:
            if action_matches:
                selected = dict(
                    action_matches[
                        0
                    ]
                )

                selected[
                    "normalization_strategy"
                ] = (
                    "SIGNAL_LICENSED_EXPLICIT_ACTION"
                )

        if selected is not None:
            payload.update({
                "action_normalization_status":
                    "NORMALIZED",

                "canonical_action":
                    selected[
                        "canonical_action"
                    ],

                "matched_action_surface":
                    selected[
                        "matched_action_surface"
                    ],

                "action_character_start":
                    selected[
                        "action_character_start"
                    ],

                "action_character_end":
                    selected[
                        "action_character_end"
                    ],

                "action_normalization_strategy":
                    selected[
                        "normalization_strategy"
                    ],

                "action_normalization_reason":
                    "ARTICLE_EXPRESSED_PROCEDURAL_ACTION",
            })

        normalized = dict(
            candidate
        )

        normalized.update({
            **payload,

            "procedural_action_normalized":
                (
                    payload[
                        "action_normalization_status"
                    ]
                    == "NORMALIZED"
                ),

            "final_procedural_participant_selected":
                False,

            "procedure_role_orientation_resolved":
                False,

            "same_sentence_procedural_validated":
                False,

            "cross_sentence_procedural_validated":
                False,

            "procedural_evidence_assessed":
                False,

            "duplicate_resolution_performed":
                False,

            "procedural_step_order_assigned":
                False,

            "procedural_prerequisite_inferred":
                False,

            "missing_step_inferred":
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

        return normalized

    source_candidates = list(
        entity_concept_grounding_result.get(
            "procedural_candidates"
        )
        or []
    )

    normalized_candidates = []
    normalized_by_id = {}

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
                "Every procedural candidate must be a mapping."
            )

        normalized_candidate = choose_licensed_action(
            candidate
        )

        candidate_id = str(
            normalized_candidate.get(
                "procedural_candidate_id"
            )
            or ""
        )

        if candidate_id in normalized_by_id:
            raise ProceduralIntelligenceError(
                "Duplicate Procedural Candidate ID during normalization."
            )

        normalized_candidates.append(
            normalized_candidate
        )

        normalized_by_id[
            candidate_id
        ] = normalized_candidate

    normalized_units = []
    normalized_units_by_id = {}

    for unit in (
        entity_concept_grounding_result.get(
            "procedural_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
                "Every Procedural Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "procedural_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise ProceduralIntelligenceError(
                "Procedural Claim Unit ID is required."
            )

        if unit_id in normalized_units_by_id:
            raise ProceduralIntelligenceError(
                "Duplicate Procedural Claim Unit ID during normalization."
            )

        state = dict(
            unit.get(
                "procedural_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "entity_concept_grounding"
            )
            != "COMPLETE"
        ):
            raise ProceduralIntelligenceError(
                "Entity/concept grounding must be COMPLETE before procedural action normalization."
            )

        if (
            state.get(
                "procedural_action_normalization"
            )
            != "PENDING"
        ):
            raise ProceduralIntelligenceError(
                "Procedural action normalization must be PENDING."
            )

        updated_candidates = []

        for old_candidate in (
            unit.get(
                "procedural_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise ProceduralIntelligenceError(
                    "Every unit Procedural Candidate reference must be a mapping."
                )

            candidate_id = str(
                old_candidate.get(
                    "procedural_candidate_id"
                )
                or ""
            )

            normalized_candidate = (
                normalized_by_id.get(
                    candidate_id
                )
            )

            if normalized_candidate is None:
                raise ProceduralIntelligenceError(
                    "Procedural candidate/unit normalization mismatch."
                )

            updated_candidates.append(
                normalized_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "procedural_action_normalization"
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
            raise ProceduralIntelligenceError(
                "Stage-F grounding boundary is incomplete."
            )

        if (
            updated_boundaries.get(
                "procedural_action_normalization_performed",
                False,
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Procedural action normalization must not already be performed."
            )

        required_false_boundaries = (
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

        for boundary_name in required_false_boundaries:
            if (
                updated_boundaries.get(
                    boundary_name
                )
                is not False
            ):
                raise ProceduralIntelligenceError(
                    boundary_name
                    + " must be False before Stage G."
                )

        updated_boundaries[
            "procedural_action_normalization_performed"
        ] = True

        updated_boundaries[
            "procedural_step_ordering_performed"
        ] = False

        updated_boundaries[
            "procedural_prerequisite_inference_performed"
        ] = False

        updated_boundaries[
            "missing_step_inference_performed"
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
            "procedural_candidates":
                updated_candidates,

            "normalized_procedural_candidate_count":
                sum(
                    1
                    for candidate in updated_candidates
                    if candidate.get(
                        "action_normalization_status"
                    )
                    == "NORMALIZED"
                ),

            "unsupported_procedural_candidate_count":
                sum(
                    1
                    for candidate in updated_candidates
                    if candidate.get(
                        "action_normalization_status"
                    )
                    == "UNSUPPORTED"
                ),

            "procedural_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        normalized_units.append(
            updated_unit
        )

        normalized_units_by_id[
            unit_id
        ] = updated_unit

    normalized_sections = []

    for section in (
        entity_concept_grounding_result.get(
            "procedural_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
                "Every procedural section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "procedural_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise ProceduralIntelligenceError(
                    "Every section Procedural Claim Unit reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "procedural_claim_unit_id"
                )
                or ""
            )

            normalized_unit = (
                normalized_units_by_id.get(
                    unit_id
                )
            )

            if normalized_unit is None:
                raise ProceduralIntelligenceError(
                    "Procedural section/unit normalization mismatch."
                )

            section_units.append(
                normalized_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "procedural_candidates"
                )
                or []
            )
        ]

        normalized_sections.append({
            **dict(
                section
            ),

            "procedural_claim_units":
                section_units,

            "procedural_candidates":
                section_candidates,

            "procedural_candidate_count":
                len(
                    section_candidates
                ),

            "normalized_procedural_candidate_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "action_normalization_status"
                    )
                    == "NORMALIZED"
                ),

            "unsupported_procedural_candidate_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "action_normalization_status"
                    )
                    == "UNSUPPORTED"
                ),

            "procedural_action_normalization_complete":
                True,
        })

    normalized_count = sum(
        1
        for candidate in normalized_candidates
        if candidate.get(
            "action_normalization_status"
        )
        == "NORMALIZED"
    )

    unsupported_count = sum(
        1
        for candidate in normalized_candidates
        if candidate.get(
            "action_normalization_status"
        )
        == "UNSUPPORTED"
    )

    result = dict(
        entity_concept_grounding_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        boundaries.get(
            "procedural_action_normalization_performed",
            False,
        )
        is not False
    ):
        raise ProceduralIntelligenceError(
            "Top-level procedural action normalization must not already be performed."
        )

    boundaries[
        "procedural_action_normalization_performed"
    ] = True

    boundaries[
        "procedural_step_ordering_performed"
    ] = False

    boundaries[
        "procedural_prerequisite_inference_performed"
    ] = False

    boundaries[
        "missing_step_inference_performed"
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
            "procedural_action_normalization_v1",

        "patch":
            "4.6.10G",

        "status":
            "PROCEDURAL_ACTION_NORMALIZATION_COMPLETE",

        "procedural_sections":
            normalized_sections,

        "procedural_claim_units":
            normalized_units,

        "procedural_candidates":
            normalized_candidates,

        "unsupported_procedural_candidates": [
            candidate
            for candidate in normalized_candidates
            if candidate.get(
                "action_normalization_status"
            )
            == "UNSUPPORTED"
        ],

        "procedural_action_normalization_summary": {
            "candidate_count":
                len(
                    normalized_candidates
                ),

            "normalized_candidate_count":
                normalized_count,

            "unsupported_candidate_count":
                unsupported_count,

            "candidate_count_accounted_for":
                (
                    normalized_count
                    + unsupported_count
                    == len(
                        normalized_candidates
                    )
                ),

            "canonical_action_registry_applied":
                True,

            "canonical_action_count":
                len(
                    action_registry
                ),

            "article_expressed_actions_only":
                True,

            "lexical_alias_normalization_only":
                True,

            "semantic_synonym_resolution_performed":
                False,

            "new_action_inference_performed":
                False,

            "final_procedural_participant_selection_performed":
                False,

            "procedure_role_orientation_performed":
                False,

            "procedural_step_ordering_performed":
                False,

            "procedural_prerequisite_inference_performed":
                False,

            "missing_step_inference_performed":
                False,

            "same_sentence_procedural_validation_performed":
                False,

            "cross_sentence_procedural_validation_performed":
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
            "procedure_role_orientation",
    })

    return result



def resolve_procedural_role_orientation_v1(
    procedural_action_normalization_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Resolve the article-local structural procedural role of each
    Procedural Candidate after action normalization.

    This stage identifies whether the candidate is functioning as a
    direct action, sequence-marked action, method action, explicit
    step, conditional step, or termination-condition action.

    It does NOT:
    - establish cross-sentence procedural order,
    - assign absolute step numbers,
    - infer prerequisites,
    - convert a condition into a prerequisite relation,
    - infer missing steps,
    - select a final actor, object, instrument, target, or participant,
    - invent an action,
    - semantically merge different actions,
    - perform same-sentence procedural validation,
    - perform cross-sentence procedural validation,
    - perform quantitative reasoning,
    - perform full temporal reasoning,
    - perform new causal reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        procedural_action_normalization_result,
        Mapping,
    ):
        raise ProceduralIntelligenceError(
            "procedural_action_normalization_result must be a mapping."
        )

    if (
        procedural_action_normalization_result.get(
            "schema_version"
        )
        != "procedural_action_normalization_v1"
    ):
        raise ProceduralIntelligenceError(
            "Stage H requires procedural_action_normalization_v1."
        )

    if (
        procedural_action_normalization_result.get(
            "status"
        )
        != "PROCEDURAL_ACTION_NORMALIZATION_COMPLETE"
    ):
        raise ProceduralIntelligenceError(
            "Procedural action normalization must be complete before role orientation."
        )

    if (
        procedural_action_normalization_result.get(
            "phase"
        )
        != "4.6.10"
    ):
        raise ProceduralIntelligenceError(
            "Stage H requires Phase 4.6.10 input."
        )

    if (
        procedural_action_normalization_result.get(
            "patch"
        )
        != "4.6.10G"
    ):
        raise ProceduralIntelligenceError(
            "Stage H requires canonical 4.6.10G input."
        )

    if (
        procedural_action_normalization_result.get(
            "next_stage"
        )
        != "procedure_role_orientation"
    ):
        raise ProceduralIntelligenceError(
            "Stage G must hand off to procedure_role_orientation."
        )

    if (
        procedural_action_normalization_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise ProceduralIntelligenceError(
            "Procedural Intelligence must remain transient."
        )

    role_by_candidate_form = {
        "DIRECT_ACTION_STEP":
            "DIRECT_ACTION",

        "SEQUENCED_ACTION":
            "SEQUENCE_MARKED_ACTION",

        "METHOD_ACTION":
            "METHOD_ACTION",

        "EXPLICIT_STEP_FRAME":
            "EXPLICIT_STEP",

        "CONDITIONAL_STEP_FRAME":
            "CONDITIONAL_STEP",

        "ACTION_WITH_TERMINATION_CONDITION":
            "TERMINATION_CONDITION_ACTION",
    }

    source_candidates = list(
        procedural_action_normalization_result.get(
            "procedural_candidates"
        )
        or []
    )

    unit_candidate_counts = {}

    for source_unit in (
        procedural_action_normalization_result.get(
            "procedural_claim_units"
        )
        or []
    ):
        if not isinstance(
            source_unit,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
                "Every Procedural Claim Unit must be a mapping."
            )

        source_unit_id = str(
            source_unit.get(
                "procedural_claim_unit_id"
            )
            or ""
        )

        if not source_unit_id:
            raise ProceduralIntelligenceError(
                "Procedural Claim Unit ID is required."
            )

        if source_unit_id in unit_candidate_counts:
            raise ProceduralIntelligenceError(
                "Duplicate Procedural Claim Unit ID detected."
            )

        unit_candidate_counts[
            source_unit_id
        ] = len(
            source_unit.get(
                "procedural_candidates"
            )
            or []
        )

    resolved_candidates = []
    resolved_by_id = {}

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
                "Every procedural candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "procedural_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise ProceduralIntelligenceError(
                "Procedural candidate ID is required."
            )

        if candidate_id in resolved_by_id:
            raise ProceduralIntelligenceError(
                "Duplicate Procedural Candidate ID during role orientation."
            )

        if (
            candidate.get(
                "procedure_role_orientation_resolved"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Candidate must not already have procedural role orientation."
            )

        candidate_form = str(
            candidate.get(
                "candidate_procedural_form"
            )
            or ""
        )

        if not candidate_form:
            raise ProceduralIntelligenceError(
                "Procedural candidate form is required."
            )

        normalization_status = str(
            candidate.get(
                "action_normalization_status"
            )
            or ""
        )

        if normalization_status not in {
            "NORMALIZED",
            "UNSUPPORTED",
        }:
            raise ProceduralIntelligenceError(
                "Candidate has invalid procedural action normalization status."
            )

        candidate_unit_id = str(
            candidate.get(
                "procedural_claim_unit_id"
            )
            or ""
        )

        if not candidate_unit_id:
            raise ProceduralIntelligenceError(
                "Procedural candidate claim-unit ID is required."
            )

        if (
            candidate_unit_id
            not in unit_candidate_counts
        ):
            raise ProceduralIntelligenceError(
                "Procedural candidate has no canonical claim unit."
            )

        unit_candidate_count = (
            unit_candidate_counts[
                candidate_unit_id
            ]
        )

        candidate_form_known = (
            candidate_form
            in role_by_candidate_form
        )

        if (
            normalization_status
            == "NORMALIZED"
            and candidate_form_known
        ):
            canonical_role = (
                role_by_candidate_form[
                    candidate_form
                ]
            )

            role_status = (
                "PROCEDURAL_ROLE_RESOLVED"
            )

            role_resolved = True

            role_resolution_basis = (
                "CANONICAL_CANDIDATE_FORM"
            )

        elif (
            normalization_status
            == "UNSUPPORTED"
        ):
            canonical_role = None

            role_status = (
                "PROCEDURAL_ROLE_PENDING_ACTION_NORMALIZATION"
            )

            role_resolved = False

            role_resolution_basis = (
                "ACTION_NORMALIZATION_UNSUPPORTED"
            )

        else:
            canonical_role = None

            role_status = (
                "PROCEDURAL_ROLE_UNRESOLVED"
            )

            role_resolved = False

            role_resolution_basis = (
                "UNSUPPORTED_CANDIDATE_FORM"
            )

        sequence_marker_present = (
            candidate_form
            == "SEQUENCED_ACTION"
        )

        explicit_step_frame_present = (
            candidate_form
            == "EXPLICIT_STEP_FRAME"
        )

        conditional_frame_present = (
            candidate_form
            == "CONDITIONAL_STEP_FRAME"
        )

        method_frame_present = (
            candidate_form
            == "METHOD_ACTION"
        )

        termination_condition_present = (
            candidate_form
            == "ACTION_WITH_TERMINATION_CONDITION"
        )

        direct_action_present = (
            candidate_form
            == "DIRECT_ACTION_STEP"
        )

        grounding_match_count = int(
            candidate.get(
                "entity_concept_grounding_match_count"
            )
            or 0
        )

        if grounding_match_count == 0:
            participant_selection_status = (
                "PARTICIPANT_PENDING_NO_GROUNDING_MATCH"
            )

            participant_selection_basis = (
                "NO_ARTICLE_LOCAL_GROUNDING_MATCH"
            )

        elif grounding_match_count == 1:
            participant_selection_status = (
                "PARTICIPANT_PENDING_SINGLE_GROUNDING_MATCH"
            )

            participant_selection_basis = (
                "GROUNDING_MATCH_REQUIRES_PROCEDURAL_VALIDATION"
            )

        else:
            participant_selection_status = (
                "PARTICIPANT_PENDING_MULTIPLE_GROUNDING_MATCHES"
            )

            participant_selection_basis = (
                "MULTIPLE_GROUNDING_MATCHES_REQUIRE_VALIDATION"
            )

        contextual_assignment_unambiguous = (
            unit_candidate_count == 1
        )

        contextual_assignment_ambiguous = (
            unit_candidate_count > 1
        )

        resolved = dict(
            candidate
        )

        resolved.update({
            "procedure_role_orientation_status":
                role_status,

            "canonical_procedure_role":
                canonical_role,

            "procedure_role_resolution_basis":
                role_resolution_basis,

            "candidate_procedural_form_known":
                candidate_form_known,

            "direct_action_present":
                direct_action_present,

            "sequence_marker_present":
                sequence_marker_present,

            "explicit_step_frame_present":
                explicit_step_frame_present,

            "conditional_frame_present":
                conditional_frame_present,

            "method_frame_present":
                method_frame_present,

            "termination_condition_present":
                termination_condition_present,

            "claim_unit_procedural_candidate_count":
                unit_candidate_count,

            "contextual_assignment_unambiguous":
                contextual_assignment_unambiguous,

            "contextual_assignment_ambiguous":
                contextual_assignment_ambiguous,

            "selected_procedural_participant":
                None,

            "procedural_participant_selection_status":
                participant_selection_status,

            "procedural_participant_selection_basis":
                participant_selection_basis,

            "final_procedural_participant_selected":
                False,

            "procedure_role_orientation_resolved":
                role_resolved,

            "procedural_step_order_assigned":
                False,

            "procedural_prerequisite_inferred":
                False,

            "missing_step_inferred":
                False,

            "same_sentence_procedural_validated":
                False,

            "cross_sentence_procedural_validated":
                False,

            "procedural_evidence_assessed":
                False,

            "duplicate_resolution_performed":
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

        resolved_candidates.append(
            resolved
        )

        resolved_by_id[
            candidate_id
        ] = resolved

    resolved_units = []
    resolved_units_by_id = {}

    for unit in (
        procedural_action_normalization_result.get(
            "procedural_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
                "Every Procedural Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "procedural_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise ProceduralIntelligenceError(
                "Procedural Claim Unit ID is required."
            )

        if unit_id in resolved_units_by_id:
            raise ProceduralIntelligenceError(
                "Duplicate Procedural Claim Unit ID during role orientation."
            )

        state = dict(
            unit.get(
                "procedural_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "procedural_action_normalization"
            )
            != "COMPLETE"
        ):
            raise ProceduralIntelligenceError(
                "Procedural action normalization must be COMPLETE before role orientation."
            )

        if (
            state.get(
                "procedure_role_orientation"
            )
            != "PENDING"
        ):
            raise ProceduralIntelligenceError(
                "Procedure role orientation must be PENDING."
            )

        updated_candidates = []

        for old_candidate in (
            unit.get(
                "procedural_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise ProceduralIntelligenceError(
                    "Every unit Procedural Candidate reference must be a mapping."
                )

            candidate_id = str(
                old_candidate.get(
                    "procedural_candidate_id"
                )
                or ""
            )

            resolved_candidate = (
                resolved_by_id.get(
                    candidate_id
                )
            )

            if resolved_candidate is None:
                raise ProceduralIntelligenceError(
                    "Procedural candidate/unit role-orientation mismatch."
                )

            updated_candidates.append(
                resolved_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "procedure_role_orientation"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            updated_boundaries.get(
                "procedural_action_normalization_performed"
            )
            is not True
        ):
            raise ProceduralIntelligenceError(
                "Stage-G action-normalization boundary is incomplete."
            )

        if (
            updated_boundaries.get(
                "procedure_role_orientation_performed",
                False,
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Procedure role orientation must not already be performed."
            )

        required_false_boundaries = (
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

        for boundary_name in required_false_boundaries:
            if (
                updated_boundaries.get(
                    boundary_name
                )
                is not False
            ):
                raise ProceduralIntelligenceError(
                    boundary_name
                    + " must be False before Stage H."
                )

        updated_boundaries[
            "procedure_role_orientation_performed"
        ] = True

        updated_boundaries[
            "same_sentence_procedural_validation_performed"
        ] = False

        updated_boundaries[
            "cross_sentence_procedural_validation_performed"
        ] = False

        updated_boundaries[
            "procedural_step_ordering_performed"
        ] = False

        updated_boundaries[
            "procedural_prerequisite_inference_performed"
        ] = False

        updated_boundaries[
            "missing_step_inference_performed"
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
            "procedural_candidates":
                updated_candidates,

            "resolved_procedure_role_count":
                sum(
                    1
                    for candidate in updated_candidates
                    if candidate.get(
                        "procedure_role_orientation_resolved"
                    )
                    is True
                ),

            "unresolved_procedure_role_count":
                sum(
                    1
                    for candidate in updated_candidates
                    if candidate.get(
                        "procedure_role_orientation_resolved"
                    )
                    is False
                ),

            "selected_procedural_participant_count":
                sum(
                    1
                    for candidate in updated_candidates
                    if candidate.get(
                        "final_procedural_participant_selected"
                    )
                    is True
                ),

            "sequence_marked_candidate_count":
                sum(
                    1
                    for candidate in updated_candidates
                    if candidate.get(
                        "sequence_marker_present"
                    )
                    is True
                ),

            "conditional_candidate_count":
                sum(
                    1
                    for candidate in updated_candidates
                    if candidate.get(
                        "conditional_frame_present"
                    )
                    is True
                ),

            "method_candidate_count":
                sum(
                    1
                    for candidate in updated_candidates
                    if candidate.get(
                        "method_frame_present"
                    )
                    is True
                ),

            "termination_condition_candidate_count":
                sum(
                    1
                    for candidate in updated_candidates
                    if candidate.get(
                        "termination_condition_present"
                    )
                    is True
                ),

            "procedural_analysis_state":
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
        procedural_action_normalization_result.get(
            "procedural_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
                "Every procedural section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "procedural_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise ProceduralIntelligenceError(
                    "Every section Procedural Claim Unit reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "procedural_claim_unit_id"
                )
                or ""
            )

            resolved_unit = (
                resolved_units_by_id.get(
                    unit_id
                )
            )

            if resolved_unit is None:
                raise ProceduralIntelligenceError(
                    "Procedural section/unit role-orientation mismatch."
                )

            section_units.append(
                resolved_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "procedural_candidates"
                )
                or []
            )
        ]

        resolved_sections.append({
            **dict(
                section
            ),

            "procedural_claim_units":
                section_units,

            "procedural_candidates":
                section_candidates,

            "resolved_procedure_role_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "procedure_role_orientation_resolved"
                    )
                    is True
                ),

            "unresolved_procedure_role_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "procedure_role_orientation_resolved"
                    )
                    is False
                ),

            "sequence_marked_candidate_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "sequence_marker_present"
                    )
                    is True
                ),

            "conditional_candidate_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "conditional_frame_present"
                    )
                    is True
                ),

            "method_candidate_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "method_frame_present"
                    )
                    is True
                ),

            "termination_condition_candidate_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "termination_condition_present"
                    )
                    is True
                ),

            "procedure_role_orientation_complete":
                True,
        })

    resolved_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "procedure_role_orientation_resolved"
        )
        is True
    )

    unresolved_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "procedure_role_orientation_resolved"
        )
        is False
    )

    sequence_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "sequence_marker_present"
        )
        is True
    )

    conditional_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "conditional_frame_present"
        )
        is True
    )

    method_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "method_frame_present"
        )
        is True
    )

    termination_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "termination_condition_present"
        )
        is True
    )

    selected_participant_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "final_procedural_participant_selected"
        )
        is True
    )

    result = dict(
        procedural_action_normalization_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        boundaries.get(
            "procedure_role_orientation_performed",
            False,
        )
        is not False
    ):
        raise ProceduralIntelligenceError(
            "Top-level procedure role orientation must not already be performed."
        )

    boundaries[
        "procedure_role_orientation_performed"
    ] = True

    boundaries[
        "same_sentence_procedural_validation_performed"
    ] = False

    boundaries[
        "cross_sentence_procedural_validation_performed"
    ] = False

    boundaries[
        "procedural_step_ordering_performed"
    ] = False

    boundaries[
        "procedural_prerequisite_inference_performed"
    ] = False

    boundaries[
        "missing_step_inference_performed"
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
            "procedural_role_orientation_v1",

        "patch":
            "4.6.10H",

        "status":
            "PROCEDURAL_ROLE_ORIENTATION_COMPLETE",

        "procedural_sections":
            resolved_sections,

        "procedural_claim_units":
            resolved_units,

        "procedural_candidates":
            resolved_candidates,

        "procedure_role_orientation_summary": {
            "candidate_count":
                len(
                    resolved_candidates
                ),

            "resolved_procedure_role_count":
                resolved_count,

            "unresolved_procedure_role_count":
                unresolved_count,

            "candidate_count_accounted_for":
                (
                    resolved_count
                    + unresolved_count
                    == len(
                        resolved_candidates
                    )
                ),

            "sequence_marked_candidate_count":
                sequence_count,

            "conditional_candidate_count":
                conditional_count,

            "method_candidate_count":
                method_count,

            "termination_condition_candidate_count":
                termination_count,

            "selected_procedural_participant_count":
                selected_participant_count,

            "final_participant_selection_performed":
                False,

            "single_grounding_auto_selection_performed":
                False,

            "multiple_grounding_guessing_performed":
                False,

            "absolute_step_number_assignment_performed":
                False,

            "cross_sentence_ordering_performed":
                False,

            "procedural_prerequisite_inference_performed":
                False,

            "missing_step_inference_performed":
                False,

            "new_action_inference_performed":
                False,

            "semantic_synonym_resolution_performed":
                False,

            "same_sentence_procedural_validation_performed":
                False,

            "cross_sentence_procedural_validation_performed":
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
            "same_sentence_procedural_validation",
    })

    return result



def validate_same_sentence_procedural_v1(
    orientation_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate whether each Procedural Candidate is supported by its
    canonical article-local Procedural Claim Unit sentence.

    Validation is limited strictly to same-sentence article evidence.

    This stage verifies:
    - candidate-to-claim-unit identity,
    - sentence identity,
    - source-text continuity,
    - exact procedural signal-span support,
    - article-asserted candidate provenance,
    - same-sentence candidate provenance,
    - completed action normalization where supported,
    - completed procedural role orientation where supported,
    - preservation of contextual ambiguity.

    It does NOT:
    - select a procedural participant,
    - use neighboring sentences to rescue a candidate,
    - perform cross-sentence validation,
    - assign procedural step order,
    - infer prerequisites,
    - infer missing steps,
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
        raise ProceduralIntelligenceError(
            "orientation_result must be a mapping."
        )

    if (
        orientation_result.get(
            "schema_version"
        )
        != "procedural_role_orientation_v1"
    ):
        raise ProceduralIntelligenceError(
            "Stage I requires procedural_role_orientation_v1."
        )

    if (
        orientation_result.get(
            "status"
        )
        != "PROCEDURAL_ROLE_ORIENTATION_COMPLETE"
    ):
        raise ProceduralIntelligenceError(
            "Procedure role orientation must be complete before Stage I."
        )

    if (
        orientation_result.get(
            "phase"
        )
        != "4.6.10"
    ):
        raise ProceduralIntelligenceError(
            "Stage I requires Phase 4.6.10 input."
        )

    if (
        orientation_result.get(
            "patch"
        )
        != "4.6.10H"
    ):
        raise ProceduralIntelligenceError(
            "Stage I requires canonical 4.6.10H input."
        )

    if (
        orientation_result.get(
            "next_stage"
        )
        != "same_sentence_procedural_validation"
    ):
        raise ProceduralIntelligenceError(
            "Stage H must hand off to same_sentence_procedural_validation."
        )

    if (
        orientation_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise ProceduralIntelligenceError(
            "Procedural Intelligence must remain transient."
        )

    source_units = list(
        orientation_result.get(
            "procedural_claim_units"
        )
        or []
    )

    if not source_units:
        raise ProceduralIntelligenceError(
            "Procedural Claim Units are required."
        )

    candidate_to_unit = {}
    unit_ids = set()

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
                "Every Procedural Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "procedural_claim_unit_id"
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
            raise ProceduralIntelligenceError(
                "Procedural Claim Unit ID is required."
            )

        if unit_id in unit_ids:
            raise ProceduralIntelligenceError(
                "Duplicate Procedural Claim Unit ID detected."
            )

        unit_ids.add(
            unit_id
        )

        if not sentence_id:
            raise ProceduralIntelligenceError(
                "Procedural Claim Unit sentence_id is required."
            )

        if not claim_text:
            raise ProceduralIntelligenceError(
                "Procedural Claim Unit text is required."
            )

        state = dict(
            unit.get(
                "procedural_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "procedure_role_orientation"
            )
            != "COMPLETE"
        ):
            raise ProceduralIntelligenceError(
                "Procedure role orientation must be COMPLETE before Stage I."
            )

        if (
            state.get(
                "same_sentence_procedural_validation"
            )
            != "PENDING"
        ):
            raise ProceduralIntelligenceError(
                "Same-sentence procedural validation must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "procedural_action_normalization_performed"
            )
            is not True
        ):
            raise ProceduralIntelligenceError(
                "Stage-G action-normalization boundary is incomplete."
            )

        if (
            boundaries.get(
                "procedure_role_orientation_performed"
            )
            is not True
        ):
            raise ProceduralIntelligenceError(
                "Stage-H role-orientation boundary is incomplete."
            )

        required_false_boundaries = (
            "same_sentence_procedural_validation_performed",
            "cross_sentence_procedural_validation_performed",
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

        for boundary_name in required_false_boundaries:
            if (
                boundaries.get(
                    boundary_name
                )
                is not False
            ):
                raise ProceduralIntelligenceError(
                    boundary_name
                    + " must be False before Stage I."
                )

        for candidate in (
            unit.get(
                "procedural_candidates"
            )
            or []
        ):
            if not isinstance(
                candidate,
                Mapping,
            ):
                raise ProceduralIntelligenceError(
                    "Every procedural candidate must be a mapping."
                )

            candidate_id = str(
                candidate.get(
                    "procedural_candidate_id"
                )
                or ""
            )

            if not candidate_id:
                raise ProceduralIntelligenceError(
                    "Procedural candidate ID is required."
                )

            if candidate_id in candidate_to_unit:
                raise ProceduralIntelligenceError(
                    "Duplicate procedural candidate ID detected."
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
                    "EXACT_PROCEDURAL_SIGNAL_SPAN_MATCH",
                )

        return (
            False,
            None,
        )

    source_candidates = list(
        orientation_result.get(
            "procedural_candidates"
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
            raise ProceduralIntelligenceError(
                "Every procedural candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "procedural_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise ProceduralIntelligenceError(
                "Procedural candidate ID is required."
            )

        if candidate_id in validated_by_id:
            raise ProceduralIntelligenceError(
                "Duplicate top-level Procedural Candidate ID detected."
            )

        unit_info = candidate_to_unit.get(
            candidate_id
        )

        if unit_info is None:
            raise ProceduralIntelligenceError(
                "Procedural candidate has no canonical claim-unit sentence."
            )

        if (
            candidate.get(
                "same_sentence_procedural_validated"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Candidate must not already be same-sentence procedural validated."
            )

        if (
            candidate.get(
                "final_procedural_participant_selected"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Stage I must not receive a preselected procedural participant."
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
                "procedural_claim_unit_id"
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

        normalization_status = str(
            candidate.get(
                "action_normalization_status"
            )
            or ""
        )

        normalization_supported = (
            normalization_status
            == "NORMALIZED"
            and candidate.get(
                "procedural_action_normalized"
            )
            is True
            and bool(
                candidate.get(
                    "canonical_action"
                )
            )
        )

        orientation_supported = (
            candidate.get(
                "procedure_role_orientation_resolved"
            )
            is True
            and bool(
                candidate.get(
                    "canonical_procedure_role"
                )
            )
        )

        contextual_assignment_ambiguous = (
            candidate.get(
                "contextual_assignment_ambiguous"
            )
            is True
        )

        contextual_assignment_unambiguous = (
            candidate.get(
                "contextual_assignment_unambiguous"
            )
            is True
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

        if normalization_status == "UNSUPPORTED":
            validation_status = (
                "NOT_VALIDATED_UNSUPPORTED_PROCEDURAL_ACTION"
            )

            same_sentence_valid = False

            validation_reason = (
                "PROCEDURAL_ACTION_NOT_CANONICALLY_NORMALIZED"
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
                "NOT_VALIDATED_PROCEDURAL_SIGNAL_SPAN_UNSUPPORTED"
            )

            same_sentence_valid = False

            validation_reason = (
                "PROCEDURAL_SIGNAL_SPAN_NOT_SUPPORTED_BY_CANONICAL_SENTENCE"
            )

        elif not normalization_supported:
            validation_status = (
                "NOT_VALIDATED_PROCEDURAL_ACTION_NORMALIZATION_INCOMPLETE"
            )

            same_sentence_valid = False

            validation_reason = (
                "PROCEDURAL_ACTION_NORMALIZATION_NOT_COMPLETE"
            )

        elif not orientation_supported:
            validation_status = (
                "NOT_VALIDATED_PROCEDURAL_ROLE_ORIENTATION_UNRESOLVED"
            )

            same_sentence_valid = False

            validation_reason = (
                "PROCEDURAL_ROLE_ORIENTATION_NOT_RESOLVED"
            )

        else:
            validation_status = (
                "VALIDATED_SAME_SENTENCE_PROCEDURAL_EXPRESSION"
            )

            same_sentence_valid = True

            validation_reason = None

        validated = dict(
            candidate
        )

        validated.update({
            "same_sentence_procedural_validation_status":
                validation_status,

            "same_sentence_procedural_valid":
                same_sentence_valid,

            "same_sentence_procedural_validation_reason":
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

            "same_sentence_procedural_signal_supported":
                signal_supported,

            "procedural_signal_support_method":
                signal_support_method,

            "same_sentence_action_normalization_supported":
                normalization_supported,

            "same_sentence_role_orientation_supported":
                orientation_supported,

            "same_sentence_contextual_assignment_ambiguous":
                contextual_assignment_ambiguous,

            "same_sentence_contextual_assignment_unambiguous":
                contextual_assignment_unambiguous,

            "same_sentence_procedural_evidence": {
                "procedural_claim_unit_id":
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

                "candidate_procedural_form":
                    candidate.get(
                        "candidate_procedural_form"
                    ),

                "canonical_action":
                    candidate.get(
                        "canonical_action"
                    ),

                "canonical_procedure_role":
                    candidate.get(
                        "canonical_procedure_role"
                    ),
            },

            "selected_procedural_participant":
                None,

            "final_procedural_participant_selected":
                False,

            "same_sentence_procedural_validated":
                same_sentence_valid,

            "cross_sentence_procedural_validated":
                False,

            "procedural_evidence_assessed":
                False,

            "duplicate_resolution_performed":
                False,

            "procedural_step_order_assigned":
                False,

            "procedural_prerequisite_inferred":
                False,

            "missing_step_inferred":
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
                "procedural_claim_unit_id"
            )
            or ""
        )

        state = dict(
            unit.get(
                "procedural_analysis_state"
            )
            or {}
        )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "procedural_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise ProceduralIntelligenceError(
                    "Every unit Procedural Candidate reference must be a mapping."
                )

            candidate_id = str(
                old_candidate.get(
                    "procedural_candidate_id"
                )
                or ""
            )

            validated_candidate = (
                validated_by_id.get(
                    candidate_id
                )
            )

            if validated_candidate is None:
                raise ProceduralIntelligenceError(
                    "Procedural candidate/unit validation mismatch."
                )

            unit_candidates.append(
                validated_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "same_sentence_procedural_validation"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "same_sentence_procedural_validation_performed"
        ] = True

        updated_boundaries[
            "cross_sentence_procedural_validation_performed"
        ] = False

        updated_boundaries[
            "procedural_step_ordering_performed"
        ] = False

        updated_boundaries[
            "procedural_prerequisite_inference_performed"
        ] = False

        updated_boundaries[
            "missing_step_inference_performed"
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
            "procedural_candidates":
                unit_candidates,

            "same_sentence_procedural_validated_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "same_sentence_procedural_valid"
                    )
                    is True
                ),

            "same_sentence_procedural_not_validated_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "same_sentence_procedural_valid"
                    )
                    is False
                ),

            "contextually_ambiguous_candidate_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "same_sentence_contextual_assignment_ambiguous"
                    )
                    is True
                ),

            "procedural_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        validated_units.append(
            updated_unit
        )

        if unit_id in validated_units_by_id:
            raise ProceduralIntelligenceError(
                "Duplicate Procedural Claim Unit ID during Stage-I reconstruction."
            )

        validated_units_by_id[
            unit_id
        ] = updated_unit

    validated_sections = []

    for section in (
        orientation_result.get(
            "procedural_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
                "Every procedural section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "procedural_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise ProceduralIntelligenceError(
                    "Every section Procedural Claim Unit reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "procedural_claim_unit_id"
                )
                or ""
            )

            validated_unit = (
                validated_units_by_id.get(
                    unit_id
                )
            )

            if validated_unit is None:
                raise ProceduralIntelligenceError(
                    "Procedural section/unit validation mismatch."
                )

            section_units.append(
                validated_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "procedural_candidates"
                )
                or []
            )
        ]

        validated_sections.append({
            **dict(
                section
            ),

            "procedural_claim_units":
                section_units,

            "procedural_candidates":
                section_candidates,

            "same_sentence_procedural_validated_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "same_sentence_procedural_valid"
                    )
                    is True
                ),

            "same_sentence_procedural_not_validated_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "same_sentence_procedural_valid"
                    )
                    is False
                ),

            "contextually_ambiguous_candidate_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "same_sentence_contextual_assignment_ambiguous"
                    )
                    is True
                ),

            "same_sentence_procedural_validation_complete":
                True,
        })

    validated_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "same_sentence_procedural_valid"
        )
        is True
    )

    not_validated_count = (
        len(
            validated_candidates
        )
        - validated_count
    )

    ambiguous_context_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "same_sentence_contextual_assignment_ambiguous"
        )
        is True
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
            "procedure_role_orientation_performed"
        )
        is not True
    ):
        raise ProceduralIntelligenceError(
            "Top-level Stage-H role-orientation boundary is incomplete."
        )

    if (
        boundaries.get(
            "same_sentence_procedural_validation_performed"
        )
        is not False
    ):
        raise ProceduralIntelligenceError(
            "Top-level same-sentence procedural validation must not already be performed."
        )

    boundaries[
        "same_sentence_procedural_validation_performed"
    ] = True

    boundaries[
        "cross_sentence_procedural_validation_performed"
    ] = False

    boundaries[
        "procedural_step_ordering_performed"
    ] = False

    boundaries[
        "procedural_prerequisite_inference_performed"
    ] = False

    boundaries[
        "missing_step_inference_performed"
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
            "procedural_same_sentence_validation_v1",

        "patch":
            "4.6.10I",

        "status":
            "PROCEDURAL_SAME_SENTENCE_VALIDATION_COMPLETE",

        "procedural_sections":
            validated_sections,

        "procedural_claim_units":
            validated_units,

        "procedural_candidates":
            validated_candidates,

        "same_sentence_procedural_validation_summary": {
            "candidate_count":
                len(
                    validated_candidates
                ),

            "same_sentence_procedural_validated_count":
                validated_count,

            "same_sentence_procedural_not_validated_count":
                not_validated_count,

            "candidate_count_accounted_for":
                (
                    validated_count
                    + not_validated_count
                    == len(
                        validated_candidates
                    )
                ),

            "contextually_ambiguous_candidate_count":
                ambiguous_context_count,

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

            "action_normalization_support_required":
                True,

            "role_orientation_support_required":
                True,

            "contextual_ambiguity_preserved":
                True,

            "final_participant_selection_performed":
                False,

            "neighbor_sentence_rescue_performed":
                False,

            "cross_sentence_procedural_validation_performed":
                False,

            "procedural_step_ordering_performed":
                False,

            "procedural_prerequisite_inference_performed":
                False,

            "missing_step_inference_performed":
                False,

            "procedural_evidence_assessment_performed":
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
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "cross_sentence_procedural_validation",
    })

    return result



def validate_cross_sentence_procedural_v1(
    same_sentence_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Assess immediate same-section adjacent-sentence corroboration for
    already-established article-local procedural expressions.

    Cross-sentence support is conservative:
    - only sentence distance 1 is eligible,
    - only within the same section,
    - Stage-I same-sentence procedural validity remains authoritative,
    - adjacent sentences may provide corroborating article-local
      semantic/action context,
    - adjacency may NOT create a procedural expression,
    - adjacency may NOT create procedural order,
    - adjacency may NOT create prerequisites,
    - adjacency may NOT infer missing steps,
    - adjacency may NOT rescue an unsupported primary procedural signal.

    It does NOT:
    - select final procedural participants,
    - create new actions,
    - assign step numbers,
    - infer workflow sequence,
    - infer prerequisites,
    - infer missing steps,
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
        same_sentence_result,
        Mapping,
    ):
        raise ProceduralIntelligenceError(
            "same_sentence_result must be a mapping."
        )

    if (
        same_sentence_result.get(
            "schema_version"
        )
        != "procedural_same_sentence_validation_v1"
    ):
        raise ProceduralIntelligenceError(
            "Stage J requires procedural_same_sentence_validation_v1."
        )

    if (
        same_sentence_result.get(
            "status"
        )
        != "PROCEDURAL_SAME_SENTENCE_VALIDATION_COMPLETE"
    ):
        raise ProceduralIntelligenceError(
            "Same-sentence procedural validation must be complete before Stage J."
        )

    if (
        same_sentence_result.get(
            "phase"
        )
        != "4.6.10"
    ):
        raise ProceduralIntelligenceError(
            "Stage J requires Phase 4.6.10 input."
        )

    if (
        same_sentence_result.get(
            "patch"
        )
        != "4.6.10I"
    ):
        raise ProceduralIntelligenceError(
            "Stage J requires canonical 4.6.10I input."
        )

    if (
        same_sentence_result.get(
            "next_stage"
        )
        != "cross_sentence_procedural_validation"
    ):
        raise ProceduralIntelligenceError(
            "Stage I must hand off to cross_sentence_procedural_validation."
        )

    if (
        same_sentence_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise ProceduralIntelligenceError(
            "Procedural Intelligence must remain transient."
        )

    source_units = list(
        same_sentence_result.get(
            "procedural_claim_units"
        )
        or []
    )

    if not source_units:
        raise ProceduralIntelligenceError(
            "Procedural Claim Units are required."
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
            raise ProceduralIntelligenceError(
                "Every Procedural Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "procedural_claim_unit_id"
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
            raise ProceduralIntelligenceError(
                "Procedural Claim Unit ID is required."
            )

        if unit_id in seen_unit_ids:
            raise ProceduralIntelligenceError(
                "Duplicate Procedural Claim Unit ID detected."
            )

        seen_unit_ids.add(
            unit_id
        )

        if not sentence_id:
            raise ProceduralIntelligenceError(
                "Procedural Claim Unit sentence_id is required."
            )

        if sentence_id in seen_sentence_ids:
            raise ProceduralIntelligenceError(
                "Duplicate procedural sentence_id detected."
            )

        seen_sentence_ids.add(
            sentence_id
        )

        if not section_id:
            raise ProceduralIntelligenceError(
                "Procedural Claim Unit section_id is required."
            )

        if not claim_text:
            raise ProceduralIntelligenceError(
                "Procedural Claim Unit text is required."
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
            raise ProceduralIntelligenceError(
                "sentence_global_index must be an integer."
            )

        if (
            previous_global_index is not None
            and sentence_global_index
            <= previous_global_index
        ):
            raise ProceduralIntelligenceError(
                "Procedural Claim Units are not in canonical sentence order."
            )

        previous_global_index = (
            sentence_global_index
        )

        state = dict(
            unit.get(
                "procedural_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "same_sentence_procedural_validation"
            )
            != "COMPLETE"
        ):
            raise ProceduralIntelligenceError(
                "Same-sentence procedural validation must be COMPLETE before Stage J."
            )

        if (
            state.get(
                "cross_sentence_procedural_validation"
            )
            != "PENDING"
        ):
            raise ProceduralIntelligenceError(
                "Cross-sentence procedural validation must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "same_sentence_procedural_validation_performed"
            )
            is not True
        ):
            raise ProceduralIntelligenceError(
                "Stage-I same-sentence validation boundary is incomplete."
            )

        required_false_boundaries = (
            "cross_sentence_procedural_validation_performed",
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

        for boundary_name in required_false_boundaries:
            if (
                boundaries.get(
                    boundary_name
                )
                is not False
            ):
                raise ProceduralIntelligenceError(
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
                "procedural_candidates"
            )
            or []
        ):
            if not isinstance(
                candidate,
                Mapping,
            ):
                raise ProceduralIntelligenceError(
                    "Every procedural candidate must be a mapping."
                )

            candidate_id = str(
                candidate.get(
                    "procedural_candidate_id"
                )
                or ""
            )

            if not candidate_id:
                raise ProceduralIntelligenceError(
                    "Procedural candidate ID is required."
                )

            if candidate_id in candidate_to_record:
                raise ProceduralIntelligenceError(
                    "Duplicate procedural candidate ID detected."
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

        canonical_action = normalize_text(
            candidate.get(
                "canonical_action"
            )
        )

        if canonical_action:
            terms.append(
                canonical_action
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

        grounding_terms = collect_candidate_terms(
            candidate
        )

        if not grounding_terms:
            return support

        for adjacent in adjacent_records:
            adjacent_text = normalize_text(
                adjacent[
                    "text"
                ]
            )

            matched_terms = sorted(
                term
                for term in grounding_terms
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
                    "ADJACENT_PROCEDURAL_CONTEXT_CORROBORATION",

                "canonical_action":
                    candidate.get(
                        "canonical_action"
                    ),

                "canonical_procedure_role":
                    candidate.get(
                        "canonical_procedure_role"
                    ),

                "creates_procedural_expression":
                    False,

                "creates_procedural_order":
                    False,

                "creates_prerequisite_relation":
                    False,

                "infers_missing_step":
                    False,

                "selects_final_participant":
                    False,
            })

        return support

    source_candidates = list(
        same_sentence_result.get(
            "procedural_candidates"
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
            raise ProceduralIntelligenceError(
                "Every procedural candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "procedural_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise ProceduralIntelligenceError(
                "Procedural candidate ID is required."
            )

        if candidate_id in validated_by_id:
            raise ProceduralIntelligenceError(
                "Duplicate top-level Procedural Candidate ID detected."
            )

        record = candidate_to_record.get(
            candidate_id
        )

        if record is None:
            raise ProceduralIntelligenceError(
                "Procedural candidate has no canonical claim unit."
            )

        if (
            candidate.get(
                "cross_sentence_procedural_validated"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Candidate must not already be cross-sentence procedurally validated."
            )

        if (
            candidate.get(
                "final_procedural_participant_selected"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Stage J must not receive a preselected procedural participant."
            )

        same_sentence_valid = (
            candidate.get(
                "same_sentence_procedural_valid"
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
                "same_sentence_procedural_signal_supported"
            )
            is True
        )

        normalization_supported = (
            candidate.get(
                "same_sentence_action_normalization_supported"
            )
            is True
        )

        orientation_supported = (
            candidate.get(
                "same_sentence_role_orientation_supported"
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
            and normalization_supported
            and orientation_supported
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

        normalization_status = str(
            candidate.get(
                "action_normalization_status"
            )
            or ""
        )

        if not article_asserted_confirmed:
            cross_sentence_status = (
                "NOT_VALIDATED_ARTICLE_ASSERTION_FAILED"
            )

            cross_sentence_valid = False
            final_procedural_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_CREATE_ARTICLE_ASSERTION"
            )

        elif not same_sentence_candidate_confirmed:
            cross_sentence_status = (
                "NOT_VALIDATED_SAME_SENTENCE_CANDIDATE_ASSERTION_FAILED"
            )

            cross_sentence_valid = False
            final_procedural_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_CREATE_SAME_SENTENCE_CANDIDATE"
            )

        elif not same_unit_match:
            cross_sentence_status = (
                "NOT_VALIDATED_CLAIM_UNIT_MISMATCH"
            )

            cross_sentence_valid = False
            final_procedural_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_REPAIR_CLAIM_UNIT_IDENTITY"
            )

        elif not same_sentence_id_match:
            cross_sentence_status = (
                "NOT_VALIDATED_SENTENCE_ID_MISMATCH"
            )

            cross_sentence_valid = False
            final_procedural_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_REPAIR_SENTENCE_IDENTITY"
            )

        elif not same_source_text_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_SOURCE_TEXT_MISMATCH"
            )

            cross_sentence_valid = False
            final_procedural_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_REPAIR_SOURCE_TEXT_CONTINUITY"
            )

        elif normalization_status == "UNSUPPORTED":
            cross_sentence_status = (
                "NOT_VALIDATED_UNSUPPORTED_PROCEDURAL_ACTION"
            )

            cross_sentence_valid = False
            final_procedural_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_RESCUE_UNSUPPORTED_PROCEDURAL_ACTION"
            )

        elif not same_signal_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_PRIMARY_PROCEDURAL_SIGNAL_UNSUPPORTED"
            )

            cross_sentence_valid = False
            final_procedural_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_CREATE_PRIMARY_PROCEDURAL_SIGNAL"
            )

        elif not normalization_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_PROCEDURAL_ACTION_NORMALIZATION_INCOMPLETE"
            )

            cross_sentence_valid = False
            final_procedural_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_REPAIR_PROCEDURAL_ACTION_NORMALIZATION"
            )

        elif not orientation_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_PROCEDURAL_ROLE_ORIENTATION_UNRESOLVED"
            )

            cross_sentence_valid = False
            final_procedural_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_CREATE_PROCEDURAL_ROLE_ORIENTATION"
            )

        elif same_sentence_valid:
            cross_sentence_status = (
                "NOT_REQUIRED_SAME_SENTENCE_VALIDATION_SUFFICIENT"
            )

            cross_sentence_valid = False
            final_procedural_expression_validated = True

            validation_reason = (
                "SAME_SENTENCE_PROCEDURAL_VALIDATION_ALREADY_SUFFICIENT"
            )

        else:
            cross_sentence_status = (
                "NOT_VALIDATED_SAME_SENTENCE_EXPRESSION_INSUFFICIENT"
            )

            cross_sentence_valid = False
            final_procedural_expression_validated = False

            validation_reason = (
                "CROSS_SENTENCE_PROXIMITY_CANNOT_CREATE_PROCEDURAL_EXPRESSION"
            )

        validated = dict(
            candidate
        )

        validated.update({
            "cross_sentence_procedural_validation_status":
                cross_sentence_status,

            "cross_sentence_procedural_valid":
                cross_sentence_valid,

            "cross_sentence_procedural_validation_reason":
                validation_reason,

            "adjacent_same_section_sentence_count":
                len(
                    adjacent_records
                ),

            "adjacent_procedural_support_present":
                adjacent_support_present,

            "adjacent_procedural_support_count":
                len(
                    adjacent_support_evidence
                ),

            "adjacent_procedural_support_evidence":
                adjacent_support_evidence,

            "cross_sentence_adjacency_policy":
                "IMMEDIATE_SENTENCE_DISTANCE_1_SAME_SECTION_ONLY",

            "cross_sentence_support_policy":
                (
                    "CORROBORATION_ONLY_FOR_ALREADY_VALIDATED_"
                    "SAME_SENTENCE_PROCEDURAL_EXPRESSION"
                ),

            "adjacent_sentence_may_create_procedural_expression":
                False,

            "adjacent_sentence_may_create_procedural_order":
                False,

            "adjacent_sentence_may_create_prerequisite_relation":
                False,

            "adjacent_sentence_may_infer_missing_step":
                False,

            "adjacent_sentence_may_select_final_participant":
                False,

            "final_procedural_expression_validated":
                final_procedural_expression_validated,

            "selected_procedural_participant":
                None,

            "final_procedural_participant_selected":
                False,

            "cross_sentence_procedural_validated":
                cross_sentence_valid,

            "procedural_evidence_assessed":
                False,

            "duplicate_resolution_performed":
                False,

            "procedural_step_order_assigned":
                False,

            "procedural_prerequisite_inferred":
                False,

            "missing_step_inferred":
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
                "procedural_analysis_state"
            )
            or {}
        )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "procedural_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise ProceduralIntelligenceError(
                    "Every unit Procedural Candidate reference must be a mapping."
                )

            candidate_id = str(
                old_candidate.get(
                    "procedural_candidate_id"
                )
                or ""
            )

            validated_candidate = (
                validated_by_id.get(
                    candidate_id
                )
            )

            if validated_candidate is None:
                raise ProceduralIntelligenceError(
                    "Procedural candidate/unit cross-sentence validation mismatch."
                )

            unit_candidates.append(
                validated_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "cross_sentence_procedural_validation"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "cross_sentence_procedural_validation_performed"
        ] = True

        updated_boundaries[
            "procedural_step_ordering_performed"
        ] = False

        updated_boundaries[
            "procedural_prerequisite_inference_performed"
        ] = False

        updated_boundaries[
            "missing_step_inference_performed"
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
            "procedural_candidates":
                unit_candidates,

            "adjacent_support_candidate_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "adjacent_procedural_support_present"
                    )
                    is True
                ),

            "final_procedural_expression_validated_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "final_procedural_expression_validated"
                    )
                    is True
                ),

            "cross_sentence_procedural_validated_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "cross_sentence_procedural_valid"
                    )
                    is True
                ),

            "procedural_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        validated_units.append(
            updated_unit
        )

        if unit_id in validated_units_by_id:
            raise ProceduralIntelligenceError(
                "Duplicate Procedural Claim Unit ID during Stage-J reconstruction."
            )

        validated_units_by_id[
            unit_id
        ] = updated_unit

    validated_sections = []

    for section in (
        same_sentence_result.get(
            "procedural_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
                "Every procedural section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "procedural_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise ProceduralIntelligenceError(
                    "Every section Procedural Claim Unit reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "procedural_claim_unit_id"
                )
                or ""
            )

            validated_unit = (
                validated_units_by_id.get(
                    unit_id
                )
            )

            if validated_unit is None:
                raise ProceduralIntelligenceError(
                    "Procedural section/unit cross-sentence validation mismatch."
                )

            section_units.append(
                validated_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "procedural_candidates"
                )
                or []
            )
        ]

        validated_sections.append({
            **dict(
                section
            ),

            "procedural_claim_units":
                section_units,

            "procedural_candidates":
                section_candidates,

            "adjacent_support_candidate_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "adjacent_procedural_support_present"
                    )
                    is True
                ),

            "final_procedural_expression_validated_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "final_procedural_expression_validated"
                    )
                    is True
                ),

            "cross_sentence_procedural_validation_complete":
                True,
        })

    same_sentence_validated_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "same_sentence_procedural_valid"
        )
        is True
    )

    adjacent_support_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "adjacent_procedural_support_present"
        )
        is True
    )

    cross_sentence_validated_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "cross_sentence_procedural_valid"
        )
        is True
    )

    final_validated_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "final_procedural_expression_validated"
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

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        boundaries.get(
            "same_sentence_procedural_validation_performed"
        )
        is not True
    ):
        raise ProceduralIntelligenceError(
            "Top-level Stage-I same-sentence validation boundary is incomplete."
        )

    if (
        boundaries.get(
            "cross_sentence_procedural_validation_performed"
        )
        is not False
    ):
        raise ProceduralIntelligenceError(
            "Top-level cross-sentence procedural validation must not already be performed."
        )

    boundaries[
        "cross_sentence_procedural_validation_performed"
    ] = True

    boundaries[
        "procedural_step_ordering_performed"
    ] = False

    boundaries[
        "procedural_prerequisite_inference_performed"
    ] = False

    boundaries[
        "missing_step_inference_performed"
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
            "procedural_cross_sentence_validation_v1",

        "patch":
            "4.6.10J",

        "status":
            "PROCEDURAL_CROSS_SENTENCE_VALIDATION_COMPLETE",

        "procedural_sections":
            validated_sections,

        "procedural_claim_units":
            validated_units,

        "procedural_candidates":
            validated_candidates,

        "cross_sentence_procedural_validation_summary": {
            "candidate_count":
                len(
                    validated_candidates
                ),

            "already_same_sentence_validated_count":
                same_sentence_validated_count,

            "adjacent_support_candidate_count":
                adjacent_support_count,

            "cross_sentence_procedural_validated_count":
                cross_sentence_validated_count,

            "final_procedural_expression_validated_count":
                final_validated_count,

            "final_procedural_expression_not_validated_count":
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

            "adjacent_sentence_may_create_procedural_expression":
                False,

            "adjacent_sentence_may_create_procedural_order":
                False,

            "adjacent_sentence_may_create_prerequisite_relation":
                False,

            "adjacent_sentence_may_infer_missing_step":
                False,

            "adjacent_sentence_may_select_final_participant":
                False,

            "proximity_based_procedural_inference_performed":
                False,

            "procedural_step_ordering_performed":
                False,

            "procedural_prerequisite_inference_performed":
                False,

            "missing_step_inference_performed":
                False,

            "procedural_evidence_assessment_performed":
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
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "procedural_evidence_confidence_assessment",
    })

    return result



def assess_procedural_confidence_evidence_v1(
    cross_sentence_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Assess article-local evidence strength for procedural expressions
    already processed through same- and cross-sentence validation.

    Confidence measures how strongly the article itself supports the
    extracted procedural expression. It does NOT measure factual,
    scientific, medical, operational, or real-world truth.

    Safeguards:
    - unvalidated procedural expressions receive zero confidence,
    - exact same-sentence procedural support is authoritative,
    - adjacent-sentence evidence is corroborative only,
    - multiple grounding matches do not establish a participant,
    - contextual ambiguity prevents promotion to STRONG,
    - multiple grounding ambiguity prevents promotion to STRONG,
    - no order, prerequisite, or missing-step inference is created.

    This stage does NOT:
    - select a final procedural participant,
    - establish factual/scientific truth,
    - perform external verification,
    - assign procedural sequence,
    - infer prerequisites,
    - infer missing steps,
    - perform quantitative reasoning,
    - perform full temporal reasoning,
    - perform new causal reasoning,
    - resolve duplicate procedural expressions,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        cross_sentence_result,
        Mapping,
    ):
        raise ProceduralIntelligenceError(
            "cross_sentence_result must be a mapping."
        )

    if (
        cross_sentence_result.get(
            "schema_version"
        )
        != "procedural_cross_sentence_validation_v1"
    ):
        raise ProceduralIntelligenceError(
            "Stage K requires procedural_cross_sentence_validation_v1."
        )

    if (
        cross_sentence_result.get(
            "status"
        )
        != "PROCEDURAL_CROSS_SENTENCE_VALIDATION_COMPLETE"
    ):
        raise ProceduralIntelligenceError(
            "Cross-sentence procedural validation must be complete."
        )

    if (
        cross_sentence_result.get(
            "phase"
        )
        != "4.6.10"
    ):
        raise ProceduralIntelligenceError(
            "Stage K requires Phase 4.6.10 input."
        )

    if (
        cross_sentence_result.get(
            "patch"
        )
        != "4.6.10J"
    ):
        raise ProceduralIntelligenceError(
            "Stage K requires canonical 4.6.10J input."
        )

    if (
        cross_sentence_result.get(
            "next_stage"
        )
        != "procedural_evidence_confidence_assessment"
    ):
        raise ProceduralIntelligenceError(
            "Stage J must hand off to procedural_evidence_confidence_assessment."
        )

    if (
        cross_sentence_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise ProceduralIntelligenceError(
            "Procedural Intelligence must remain transient."
        )

    source_candidates = list(
        cross_sentence_result.get(
            "procedural_candidates"
        )
        or []
    )

    assessed_candidates = []

    valid_grounding_statuses = {
        "UNGROUNDED",
        "GROUNDED_SINGLE_MATCH",
        "GROUNDED_MULTIPLE_MATCHES",
    }

    seen_candidate_ids = set()

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
                "Every procedural candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "procedural_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise ProceduralIntelligenceError(
                "Procedural candidate ID is required."
            )

        if candidate_id in seen_candidate_ids:
            raise ProceduralIntelligenceError(
                "Duplicate procedural candidate ID detected."
            )

        seen_candidate_ids.add(
            candidate_id
        )

        if (
            candidate.get(
                "procedural_evidence_assessed"
            )
            is True
            or (
                candidate.get(
                    "procedural_evidence_assessed"
                )
                is not False
                and candidate.get(
                    "procedural_evidence_assessed"
                )
                is not None
            )
        ):
            raise ProceduralIntelligenceError(
                "Candidate must not already have procedural evidence assessment."
            )

        if (
            candidate.get(
                "final_procedural_participant_selected"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Stage K must not receive a selected procedural participant."
            )

        final_validated = (
            candidate.get(
                "final_procedural_expression_validated"
            )
            is True
        )

        same_sentence_valid = (
            candidate.get(
                "same_sentence_procedural_valid"
            )
            is True
        )

        cross_sentence_valid = (
            candidate.get(
                "cross_sentence_procedural_valid"
            )
            is True
        )

        exact_signal_supported = (
            candidate.get(
                "same_sentence_procedural_signal_supported"
            )
            is True
        )

        normalization_supported = (
            candidate.get(
                "same_sentence_action_normalization_supported"
            )
            is True
        )

        orientation_supported = (
            candidate.get(
                "same_sentence_role_orientation_supported"
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

        contextual_ambiguity = (
            candidate.get(
                "same_sentence_contextual_assignment_ambiguous"
            )
            is True
            or candidate.get(
                "contextual_assignment_ambiguous"
            )
            is True
        )

        adjacent_support_present = (
            candidate.get(
                "adjacent_procedural_support_present"
            )
            is True
        )

        grounding_status = str(
            candidate.get(
                "grounding_status"
            )
            or "UNGROUNDED"
        )

        if grounding_status not in valid_grounding_statuses:
            raise ProceduralIntelligenceError(
                "Candidate has invalid procedural grounding_status."
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

        if not isinstance(
            grounding_match_count,
            int,
        ):
            raise ProceduralIntelligenceError(
                "Procedural grounding match count must be an integer."
            )

        if isinstance(
            grounding_match_count,
            bool,
        ):
            raise ProceduralIntelligenceError(
                "Procedural grounding match count must not be boolean."
            )

        if grounding_match_count != len(
            grounding_matches
        ):
            raise ProceduralIntelligenceError(
                "Procedural grounding match count mismatch."
            )

        if (
            grounding_status == "UNGROUNDED"
            and grounding_match_count != 0
        ):
            raise ProceduralIntelligenceError(
                "UNGROUNDED candidate cannot contain grounding matches."
            )

        if (
            grounding_status == "GROUNDED_SINGLE_MATCH"
            and grounding_match_count != 1
        ):
            raise ProceduralIntelligenceError(
                "GROUNDED_SINGLE_MATCH requires exactly one grounding match."
            )

        if (
            grounding_status == "GROUNDED_MULTIPLE_MATCHES"
            and grounding_match_count < 2
        ):
            raise ProceduralIntelligenceError(
                "GROUNDED_MULTIPLE_MATCHES requires at least two matches."
            )

        grounding_confidences = []

        for grounding in grounding_matches:
            if not isinstance(
                grounding,
                Mapping,
            ):
                raise ProceduralIntelligenceError(
                    "Every procedural grounding match must be a mapping."
                )

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
                raise ProceduralIntelligenceError(
                    "Procedural grounding match has invalid extraction_confidence."
                )

            grounding_confidences.append(
                float(
                    confidence
                )
            )

        if grounding_confidences:
            grounding_confidence = round(
                sum(
                    grounding_confidences
                )
                / len(
                    grounding_confidences
                ),
                3,
            )

        else:
            grounding_confidence = None

        if not final_validated:
            evidence_score = 0.0

            evidence_strength = (
                "INSUFFICIENT"
            )

            primary_basis = (
                "PROCEDURAL_EXPRESSION_NOT_VALIDATED"
            )

            confidence_cap_applied = None

        else:
            if not (
                article_asserted_confirmed
                and same_sentence_candidate_confirmed
                and exact_signal_supported
                and normalization_supported
                and orientation_supported
            ):
                raise ProceduralIntelligenceError(
                    "Final validated procedural candidate has inconsistent Stage-I support."
                )

            evidence_score = 0.48

            if same_sentence_valid:
                evidence_score += 0.24

                primary_basis = (
                    "SAME_SENTENCE_PROCEDURAL_EXPRESSION_VALIDATED"
                )

            elif cross_sentence_valid:
                evidence_score += 0.10

                primary_basis = (
                    "CROSS_SENTENCE_PROCEDURAL_EXPRESSION_VALIDATED"
                )

            else:
                raise ProceduralIntelligenceError(
                    "Final validated procedural candidate has no recognized validation mode."
                )

            if grounding_status == "GROUNDED_SINGLE_MATCH":
                evidence_score += 0.08

            elif grounding_status == "GROUNDED_MULTIPLE_MATCHES":
                evidence_score += 0.04

            if grounding_confidence is not None:
                evidence_score += (
                    grounding_confidence
                    * 0.08
                )

            if adjacent_support_present:
                evidence_score += 0.03

            if not contextual_ambiguity:
                evidence_score += 0.04

            evidence_score = min(
                evidence_score,
                0.99,
            )

            confidence_cap_applied = None

            if contextual_ambiguity:
                if evidence_score > 0.79:
                    evidence_score = 0.79

                    confidence_cap_applied = (
                        "CONTEXTUAL_AMBIGUITY_MAX_MODERATE"
                    )

            if (
                grounding_status
                == "GROUNDED_MULTIPLE_MATCHES"
                and evidence_score > 0.79
            ):
                evidence_score = 0.79

                if confidence_cap_applied is None:
                    confidence_cap_applied = (
                        "MULTIPLE_GROUNDING_MATCHES_MAX_MODERATE"
                    )

                else:
                    confidence_cap_applied = (
                        confidence_cap_applied
                        + "+"
                        + "MULTIPLE_GROUNDING_MATCHES_MAX_MODERATE"
                    )

            if cross_sentence_valid:
                if evidence_score > 0.79:
                    evidence_score = 0.79

                    if confidence_cap_applied is None:
                        confidence_cap_applied = (
                            "CROSS_SENTENCE_MAX_MODERATE"
                        )

                    else:
                        confidence_cap_applied = (
                            confidence_cap_applied
                            + "+"
                            + "CROSS_SENTENCE_MAX_MODERATE"
                        )

            evidence_score = round(
                evidence_score,
                3,
            )

            if evidence_score >= 0.85:
                evidence_strength = "STRONG"

            elif evidence_score >= 0.70:
                evidence_strength = "MODERATE"

            else:
                evidence_strength = "LIMITED"

        assessed = dict(
            candidate
        )

        assessed.update({
            "procedural_evidence_assessed":
                True,

            "procedural_evidence_score":
                evidence_score,

            "procedural_evidence_strength":
                evidence_strength,

            "procedural_evidence_basis":
                primary_basis,

            "procedural_confidence_cap_applied":
                confidence_cap_applied,

            "procedural_evidence_factors": {
                "final_procedural_expression_validated":
                    final_validated,

                "same_sentence_procedural_valid":
                    same_sentence_valid,

                "cross_sentence_procedural_valid":
                    cross_sentence_valid,

                "article_asserted_candidate_confirmed":
                    article_asserted_confirmed,

                "same_sentence_candidate_confirmed":
                    same_sentence_candidate_confirmed,

                "exact_procedural_signal_supported":
                    exact_signal_supported,

                "action_normalization_supported":
                    normalization_supported,

                "role_orientation_supported":
                    orientation_supported,

                "grounding_status":
                    grounding_status,

                "grounding_match_count":
                    grounding_match_count,

                "grounding_confidence":
                    grounding_confidence,

                "contextual_assignment_ambiguous":
                    contextual_ambiguity,

                "adjacent_procedural_support_present":
                    adjacent_support_present,
            },

            "procedural_role_preserved":
                True,

            "procedural_action_normalization_preserved":
                True,

            "contextual_ambiguity_promoted_to_strong":
                False,

            "multiple_grounding_matches_promoted_to_strong":
                False,

            "cross_sentence_expression_promoted_to_strong":
                False,

            "final_procedural_participant_selected":
                False,

            "selected_procedural_participant":
                None,

            "confidence_scope":
                "ARTICLE_LOCAL_PROCEDURAL_EXPRESSION_EVIDENCE_ONLY",

            "duplicate_resolution_performed":
                False,

            "procedural_step_order_assigned":
                False,

            "procedural_prerequisite_inferred":
                False,

            "missing_step_inferred":
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
            "procedural_candidate_id"
        ):
            candidate
        for candidate in assessed_candidates
    }

    assessed_units = []

    for unit in (
        cross_sentence_result.get(
            "procedural_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
                "Every Procedural Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "procedural_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "cross_sentence_procedural_validation"
            )
            != "COMPLETE"
        ):
            raise ProceduralIntelligenceError(
                "Cross-sentence procedural validation must be COMPLETE before Stage K."
            )

        if (
            state.get(
                "procedural_evidence_assessment"
            )
            != "PENDING"
        ):
            raise ProceduralIntelligenceError(
                "Procedural evidence assessment must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "cross_sentence_procedural_validation_performed"
            )
            is not True
        ):
            raise ProceduralIntelligenceError(
                "Stage-J cross-sentence procedural validation boundary is incomplete."
            )

        if (
            boundaries.get(
                "procedural_evidence_assessment_performed"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Procedural evidence assessment boundary must be False before Stage K."
            )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "procedural_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise ProceduralIntelligenceError(
                    "Every unit procedural candidate must be a mapping."
                )

            candidate_id = old_candidate.get(
                "procedural_candidate_id"
            )

            assessed_candidate = (
                assessed_by_id.get(
                    candidate_id
                )
            )

            if assessed_candidate is None:
                raise ProceduralIntelligenceError(
                    "Procedural candidate/unit evidence mismatch."
                )

            unit_candidates.append(
                assessed_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "procedural_evidence_assessment"
        ] = "COMPLETE"

        updated_boundaries = dict(
            boundaries
        )

        updated_boundaries[
            "procedural_evidence_assessment_performed"
        ] = True

        updated_boundaries[
            "duplicate_resolution_performed"
        ] = False

        updated_boundaries[
            "procedural_step_ordering_performed"
        ] = False

        updated_boundaries[
            "procedural_prerequisite_inference_performed"
        ] = False

        updated_boundaries[
            "missing_step_inference_performed"
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
            "procedural_candidates":
                unit_candidates,

            "strong_procedural_evidence_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "procedural_evidence_strength"
                    )
                    == "STRONG"
                ),

            "moderate_procedural_evidence_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "procedural_evidence_strength"
                    )
                    == "MODERATE"
                ),

            "limited_procedural_evidence_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "procedural_evidence_strength"
                    )
                    == "LIMITED"
                ),

            "insufficient_procedural_evidence_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "procedural_evidence_strength"
                    )
                    == "INSUFFICIENT"
                ),

            "procedural_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        assessed_units.append(
            updated_unit
        )

    assessed_units_by_id = {
        unit.get(
            "procedural_claim_unit_id"
        ):
            unit
        for unit in assessed_units
    }

    assessed_sections = []

    for section in (
        cross_sentence_result.get(
            "procedural_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
                "Every procedural section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "procedural_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise ProceduralIntelligenceError(
                    "Every section Procedural Claim Unit reference must be a mapping."
                )

            unit_id = old_unit.get(
                "procedural_claim_unit_id"
            )

            assessed_unit = (
                assessed_units_by_id.get(
                    unit_id
                )
            )

            if assessed_unit is None:
                raise ProceduralIntelligenceError(
                    "Procedural section/unit evidence mismatch."
                )

            section_units.append(
                assessed_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "procedural_candidates"
                )
                or []
            )
        ]

        assessed_sections.append({
            **dict(
                section
            ),

            "procedural_claim_units":
                section_units,

            "procedural_candidates":
                section_candidates,

            "strong_procedural_evidence_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "procedural_evidence_strength"
                    )
                    == "STRONG"
                ),

            "moderate_procedural_evidence_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "procedural_evidence_strength"
                    )
                    == "MODERATE"
                ),

            "limited_procedural_evidence_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "procedural_evidence_strength"
                    )
                    == "LIMITED"
                ),

            "insufficient_procedural_evidence_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "procedural_evidence_strength"
                    )
                    == "INSUFFICIENT"
                ),

            "procedural_evidence_assessment_complete":
                True,
        })

    strong_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "procedural_evidence_strength"
        )
        == "STRONG"
    )

    moderate_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "procedural_evidence_strength"
        )
        == "MODERATE"
    )

    limited_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "procedural_evidence_strength"
        )
        == "LIMITED"
    )

    insufficient_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "procedural_evidence_strength"
        )
        == "INSUFFICIENT"
    )

    contextual_ambiguity_strong_count = sum(
        1
        for candidate in assessed_candidates
        if (
            candidate.get(
                "same_sentence_contextual_assignment_ambiguous"
            )
            is True
            or candidate.get(
                "contextual_assignment_ambiguous"
            )
            is True
        )
        and candidate.get(
            "procedural_evidence_strength"
        )
        == "STRONG"
    )

    multiple_grounding_strong_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "grounding_status"
        )
        == "GROUNDED_MULTIPLE_MATCHES"
        and candidate.get(
            "procedural_evidence_strength"
        )
        == "STRONG"
    )

    cross_sentence_strong_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "cross_sentence_procedural_valid"
        )
        is True
        and candidate.get(
            "procedural_evidence_strength"
        )
        == "STRONG"
    )

    result = dict(
        cross_sentence_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        boundaries.get(
            "cross_sentence_procedural_validation_performed"
        )
        is not True
    ):
        raise ProceduralIntelligenceError(
            "Top-level Stage-J cross-sentence validation boundary is incomplete."
        )

    if (
        boundaries.get(
            "procedural_evidence_assessment_performed"
        )
        is not False
    ):
        raise ProceduralIntelligenceError(
            "Top-level procedural evidence assessment must not already be performed."
        )

    boundaries[
        "procedural_evidence_assessment_performed"
    ] = True

    boundaries[
        "duplicate_resolution_performed"
    ] = False

    boundaries[
        "procedural_step_ordering_performed"
    ] = False

    boundaries[
        "procedural_prerequisite_inference_performed"
    ] = False

    boundaries[
        "missing_step_inference_performed"
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
            "procedural_evidence_assessment_v1",

        "patch":
            "4.6.10K",

        "status":
            "PROCEDURAL_EVIDENCE_ASSESSMENT_COMPLETE",

        "procedural_sections":
            assessed_sections,

        "procedural_claim_units":
            assessed_units,

        "procedural_candidates":
            assessed_candidates,

        "procedural_evidence_summary": {
            "candidate_count":
                len(
                    assessed_candidates
                ),

            "strong_procedural_evidence_count":
                strong_count,

            "moderate_procedural_evidence_count":
                moderate_count,

            "limited_procedural_evidence_count":
                limited_count,

            "insufficient_procedural_evidence_count":
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

            "contextual_ambiguity_strong_count":
                contextual_ambiguity_strong_count,

            "multiple_grounding_strong_count":
                multiple_grounding_strong_count,

            "cross_sentence_strong_count":
                cross_sentence_strong_count,

            "contextual_ambiguity_strong_promotion_prohibited":
                True,

            "multiple_grounding_strong_promotion_prohibited":
                True,

            "cross_sentence_strong_promotion_prohibited":
                True,

            "grounding_confidence_source":
                "STAGE_F_EXTRACTION_CONFIDENCE",

            "confidence_scope":
                "ARTICLE_LOCAL_PROCEDURAL_EXPRESSION_EVIDENCE_ONLY",

            "scientific_truth_confidence_computed":
                False,

            "real_world_procedural_validity_verified":
                False,

            "final_participant_selected":
                False,

            "duplicate_resolution_performed":
                False,

            "procedural_step_ordering_performed":
                False,

            "procedural_prerequisite_inference_performed":
                False,

            "missing_step_inference_performed":
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
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "duplicate_redundant_procedural_resolution",
    })

    return result



def resolve_duplicate_redundant_procedural_relations_v1(
    evidence_assessment_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Resolve exact article-local duplicate procedural candidates.

    Duplicate identity is deliberately conservative. It requires the
    same canonical procedural signal, normalized action, role,
    procedural form, contextual assignment, and grounding identity.

    This stage does NOT:
    - use fuzzy semantic similarity,
    - merge different procedural actions,
    - merge different procedural roles,
    - merge different procedural forms,
    - merge different contextual assignments,
    - guess among multiple grounding matches,
    - select a final procedural participant,
    - create procedural order,
    - infer prerequisites,
    - infer missing steps,
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
        raise ProceduralIntelligenceError(
            "evidence_assessment_result must be a mapping."
        )

    if (
        evidence_assessment_result.get(
            "schema_version"
        )
        != "procedural_evidence_assessment_v1"
    ):
        raise ProceduralIntelligenceError(
            "Stage L requires procedural_evidence_assessment_v1."
        )

    if (
        evidence_assessment_result.get(
            "status"
        )
        != "PROCEDURAL_EVIDENCE_ASSESSMENT_COMPLETE"
    ):
        raise ProceduralIntelligenceError(
            "Procedural evidence assessment must be complete."
        )

    if (
        evidence_assessment_result.get(
            "phase"
        )
        != "4.6.10"
    ):
        raise ProceduralIntelligenceError(
            "Stage L requires Phase 4.6.10 input."
        )

    if (
        evidence_assessment_result.get(
            "patch"
        )
        != "4.6.10K"
    ):
        raise ProceduralIntelligenceError(
            "Stage L requires canonical 4.6.10K input."
        )

    if (
        evidence_assessment_result.get(
            "next_stage"
        )
        != "duplicate_redundant_procedural_resolution"
    ):
        raise ProceduralIntelligenceError(
            "Stage K must hand off to duplicate_redundant_procedural_resolution."
        )

    if (
        evidence_assessment_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise ProceduralIntelligenceError(
            "Procedural Intelligence must remain transient."
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

    def grounding_identity(
        candidate: Mapping[str, Any],
    ) -> tuple[str, str] | None:
        status = candidate.get(
            "grounding_status"
        )

        matches = list(
            candidate.get(
                "entity_concept_grounding_matches"
            )
            or []
        )

        match_count = candidate.get(
            "entity_concept_grounding_match_count"
        )

        if (
            not isinstance(
                match_count,
                int,
            )
            or isinstance(
                match_count,
                bool,
            )
        ):
            raise ProceduralIntelligenceError(
                "Procedural grounding match count must be an integer."
            )

        if match_count != len(
            matches
        ):
            raise ProceduralIntelligenceError(
                "Procedural grounding match count mismatch."
            )

        if status == "GROUNDED_SINGLE_MATCH":
            if match_count != 1:
                raise ProceduralIntelligenceError(
                    "Single-grounded procedural candidate must have exactly one grounding match."
                )

            grounding = matches[
                0
            ]

            if not isinstance(
                grounding,
                Mapping,
            ):
                raise ProceduralIntelligenceError(
                    "Procedural grounding match must be a mapping."
                )

            canonical_text = normalize_text(
                grounding.get(
                    "canonical_text"
                )
            )

            semantic_kind = normalize_text(
                grounding.get(
                    "semantic_kind"
                )
            )

            if not canonical_text:
                raise ProceduralIntelligenceError(
                    "Single-grounded candidate is missing canonical grounding text."
                )

            if semantic_kind not in {
                "entity",
                "concept",
            }:
                raise ProceduralIntelligenceError(
                    "Single-grounded candidate has invalid semantic kind."
                )

            return (
                semantic_kind,
                canonical_text,
            )

        if status == "UNGROUNDED":
            if match_count != 0:
                raise ProceduralIntelligenceError(
                    "UNGROUNDED procedural candidate cannot contain grounding matches."
                )

            return None

        if status == "GROUNDED_MULTIPLE_MATCHES":
            if match_count < 2:
                raise ProceduralIntelligenceError(
                    "Multiple-grounded procedural candidate requires at least two grounding matches."
                )

            return None

        raise ProceduralIntelligenceError(
            "Candidate has invalid procedural grounding status."
        )

    def duplicate_key(
        candidate: Mapping[str, Any],
    ) -> tuple[str, ...] | None:
        if (
            candidate.get(
                "final_procedural_expression_validated"
            )
            is not True
        ):
            return None

        if (
            candidate.get(
                "action_normalization_status"
            )
            != "NORMALIZED"
        ):
            return None

        if (
            candidate.get(
                "procedure_role_orientation_resolved"
            )
            is not True
        ):
            return None

        grounding = grounding_identity(
            candidate
        )

        grounding_status = candidate.get(
            "grounding_status"
        )

        if (
            grounding_status
            == "GROUNDED_MULTIPLE_MATCHES"
        ):
            return None

        signal_type = normalize_text(
            candidate.get(
                "signal_type"
            )
        )

        canonical_action = normalize_text(
            candidate.get(
                "canonical_action"
            )
        )

        canonical_role = normalize_text(
            candidate.get(
                "canonical_procedure_role"
            )
        )

        procedural_form = normalize_text(
            candidate.get(
                "candidate_procedural_form"
            )
        )

        contextual_ambiguity = (
            candidate.get(
                "contextual_assignment_ambiguous"
            )
            is True
            or candidate.get(
                "same_sentence_contextual_assignment_ambiguous"
            )
            is True
        )

        if (
            not signal_type
            or not canonical_action
            or not canonical_role
            or not procedural_form
        ):
            return None

        if grounding is None:
            source_identity = normalize_text(
                candidate.get(
                    "source_text"
                )
            )

            if not source_identity:
                return None

            grounding_kind = (
                "ungrounded_exact_source"
            )

            grounding_text = (
                source_identity
            )

        else:
            grounding_kind = grounding[
                0
            ]

            grounding_text = grounding[
                1
            ]

        return (
            signal_type,
            canonical_action,
            canonical_role,
            procedural_form,
            "ambiguous"
            if contextual_ambiguity
            else "unambiguous",
            grounding_kind,
            grounding_text,
        )

    source_candidates = list(
        evidence_assessment_result.get(
            "procedural_candidates"
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
            raise ProceduralIntelligenceError(
                "Every procedural candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "procedural_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise ProceduralIntelligenceError(
                "Procedural candidate ID is required."
            )

        if candidate_id in seen_candidate_ids:
            raise ProceduralIntelligenceError(
                "Duplicate procedural candidate ID encountered."
            )

        seen_candidate_ids.add(
            candidate_id
        )

        if (
            candidate.get(
                "procedural_evidence_assessed"
            )
            is not True
        ):
            raise ProceduralIntelligenceError(
                "Every procedural candidate must have completed evidence assessment."
            )

        if (
            candidate.get(
                "duplicate_resolution_performed"
            )
            is True
        ):
            raise ProceduralIntelligenceError(
                "Candidate must not already have duplicate resolution."
            )

        if (
            candidate.get(
                "final_procedural_participant_selected"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Stage L must not receive a selected final procedural participant."
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
                            "procedural_evidence_strength"
                        )
                        or ""
                    ),
                    0,
                ),
                -float(
                    candidate.get(
                        "procedural_evidence_score"
                    )
                    or 0.0
                ),
                0
                if candidate.get(
                    "same_sentence_procedural_valid"
                )
                is True
                else 1,
                0
                if candidate.get(
                    "adjacent_procedural_support_present"
                )
                is True
                else 1,
                str(
                    candidate.get(
                        "procedural_candidate_id"
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
                    "procedural_candidate_id"
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
            "procedural_duplicate_group_"
            + hashlib.sha256(
                raw_key.encode(
                    "utf-8"
                )
            ).hexdigest()[
                :16
            ]
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
                "procedural_candidate_id"
            )
        )

        for index, member in enumerate(
            ordered
        ):
            member_id = str(
                member.get(
                    "procedural_candidate_id"
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

                "procedural_duplicate_group_id":
                    group_id,

                "procedural_duplicate_group_size":
                    len(
                        ordered
                    ),

                "procedural_duplicate_member_ids":
                    member_ids,

                "is_procedural_duplicate_group":
                    is_duplicate_group,

                "is_representative_procedural_expression":
                    is_representative,

                "representative_procedural_candidate_id":
                    representative_id,

                "duplicate_of_procedural_candidate_id":
                    (
                        None
                        if is_representative
                        else representative_id
                    ),

                "procedural_duplicate_resolution_status":
                    (
                        "REPRESENTATIVE"
                        if is_representative
                        else "DUPLICATE_REDUNDANT"
                    ),

                "procedural_duplicate_key": {
                    "signal_type":
                        key[
                            0
                        ],

                    "canonical_action":
                        key[
                            1
                        ],

                    "canonical_procedure_role":
                        key[
                            2
                        ],

                    "candidate_procedural_form":
                        key[
                            3
                        ],

                    "contextual_assignment":
                        key[
                            4
                        ],

                    "grounding_identity_kind":
                        key[
                            5
                        ],

                    "grounding_identity":
                        key[
                            6
                        ],
                },

                "exact_canonical_procedural_identity_used":
                    True,

                "different_actions_merged":
                    False,

                "different_procedural_roles_merged":
                    False,

                "different_procedural_forms_merged":
                    False,

                "different_contextual_assignments_merged":
                    False,

                "multiple_grounding_guessing_performed":
                    False,

                "fuzzy_similarity_performed":
                    False,

                "final_procedural_participant_selected":
                    False,

                "selected_procedural_participant":
                    None,

                "procedural_step_order_assigned":
                    False,

                "procedural_prerequisite_inferred":
                    False,

                "missing_step_inferred":
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
                "procedural_candidate_id"
            )
        )

        resolved = dict(
            member
        )

        resolved.update({
            "duplicate_resolution_performed":
                True,

            "procedural_duplicate_group_id":
                None,

            "procedural_duplicate_group_size":
                1,

            "procedural_duplicate_member_ids": [
                member_id,
            ],

            "is_procedural_duplicate_group":
                False,

            "is_representative_procedural_expression":
                True,

            "representative_procedural_candidate_id":
                member_id,

            "duplicate_of_procedural_candidate_id":
                None,

            "procedural_duplicate_resolution_status":
                "UNIQUE_NON_GROUPABLE",

            "procedural_duplicate_key":
                None,

            "exact_canonical_procedural_identity_used":
                False,

            "different_actions_merged":
                False,

            "different_procedural_roles_merged":
                False,

            "different_procedural_forms_merged":
                False,

            "different_contextual_assignments_merged":
                False,

            "multiple_grounding_guessing_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "final_procedural_participant_selected":
                False,

            "selected_procedural_participant":
                None,

            "procedural_step_order_assigned":
                False,

            "procedural_prerequisite_inferred":
                False,

            "missing_step_inferred":
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
                "procedural_candidate_id"
            )
        )

        resolved = resolved_by_id.get(
            candidate_id
        )

        if resolved is None:
            raise ProceduralIntelligenceError(
                "Duplicate procedural resolution lost a candidate."
            )

        resolved_candidates.append(
            resolved
        )

    representative_candidates.sort(
        key=lambda candidate: str(
            candidate.get(
                "procedural_candidate_id"
            )
            or ""
        )
    )

    resolved_units = []

    for unit in (
        evidence_assessment_result.get(
            "procedural_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
                "Every Procedural Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "procedural_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "procedural_evidence_assessment"
            )
            != "COMPLETE"
        ):
            raise ProceduralIntelligenceError(
                "Procedural evidence assessment must be COMPLETE before Stage L."
            )

        if (
            state.get(
                "duplicate_procedural_resolution"
            )
            != "PENDING"
        ):
            raise ProceduralIntelligenceError(
                "Duplicate procedural resolution must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "procedural_evidence_assessment_performed"
            )
            is not True
        ):
            raise ProceduralIntelligenceError(
                "Stage-K procedural evidence boundary must be complete."
            )

        if (
            boundaries.get(
                "duplicate_resolution_performed"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Duplicate procedural resolution boundary must be False before Stage L."
            )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "procedural_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise ProceduralIntelligenceError(
                    "Every unit procedural candidate must be a mapping."
                )

            candidate_id = old_candidate.get(
                "procedural_candidate_id"
            )

            resolved_candidate = (
                resolved_by_id.get(
                    candidate_id
                )
            )

            if resolved_candidate is None:
                raise ProceduralIntelligenceError(
                    "Procedural candidate/unit duplicate mismatch."
                )

            unit_candidates.append(
                resolved_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "duplicate_procedural_resolution"
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
            "procedural_step_ordering_performed"
        ] = False

        updated_boundaries[
            "procedural_prerequisite_inference_performed"
        ] = False

        updated_boundaries[
            "missing_step_inference_performed"
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
            "procedural_candidates":
                unit_candidates,

            "representative_procedural_expression_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "is_representative_procedural_expression"
                    )
                    is True
                ),

            "duplicate_redundant_procedural_expression_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "procedural_duplicate_resolution_status"
                    )
                    == "DUPLICATE_REDUNDANT"
                ),

            "procedural_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        resolved_units.append(
            updated_unit
        )

    resolved_units_by_id = {
        unit.get(
            "procedural_claim_unit_id"
        ):
            unit
        for unit in resolved_units
    }

    resolved_sections = []

    for section in (
        evidence_assessment_result.get(
            "procedural_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
                "Every procedural section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "procedural_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise ProceduralIntelligenceError(
                    "Every section Procedural Claim Unit reference must be a mapping."
                )

            unit_id = old_unit.get(
                "procedural_claim_unit_id"
            )

            resolved_unit = (
                resolved_units_by_id.get(
                    unit_id
                )
            )

            if resolved_unit is None:
                raise ProceduralIntelligenceError(
                    "Procedural section/unit duplicate mismatch."
                )

            section_units.append(
                resolved_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "procedural_candidates"
                )
                or []
            )
        ]

        resolved_sections.append({
            **dict(
                section
            ),

            "procedural_claim_units":
                section_units,

            "procedural_candidates":
                section_candidates,

            "representative_procedural_expression_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "is_representative_procedural_expression"
                    )
                    is True
                ),

            "duplicate_redundant_procedural_expression_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "procedural_duplicate_resolution_status"
                    )
                    == "DUPLICATE_REDUNDANT"
                ),

            "duplicate_procedural_resolution_complete":
                True,
        })

    representative_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "is_representative_procedural_expression"
        )
        is True
    )

    redundant_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "procedural_duplicate_resolution_status"
        )
        == "DUPLICATE_REDUNDANT"
    )

    multiple_grounding_non_groupable_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "grounding_status"
        )
        == "GROUNDED_MULTIPLE_MATCHES"
        and candidate.get(
            "procedural_duplicate_resolution_status"
        )
        == "UNIQUE_NON_GROUPABLE"
    )

    result = dict(
        evidence_assessment_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        boundaries.get(
            "procedural_evidence_assessment_performed"
        )
        is not True
    ):
        raise ProceduralIntelligenceError(
            "Top-level Stage-K procedural evidence boundary must be complete."
        )

    if (
        boundaries.get(
            "duplicate_resolution_performed"
        )
        is not False
    ):
        raise ProceduralIntelligenceError(
            "Top-level duplicate procedural resolution must not already be performed."
        )

    boundaries[
        "duplicate_resolution_performed"
    ] = True

    boundaries[
        "fuzzy_similarity_performed"
    ] = False

    boundaries[
        "procedural_step_ordering_performed"
    ] = False

    boundaries[
        "procedural_prerequisite_inference_performed"
    ] = False

    boundaries[
        "missing_step_inference_performed"
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
            "procedural_duplicate_resolution_v1",

        "patch":
            "4.6.10L",

        "status":
            "PROCEDURAL_DUPLICATE_RESOLUTION_COMPLETE",

        "procedural_sections":
            resolved_sections,

        "procedural_claim_units":
            resolved_units,

        "procedural_candidates":
            resolved_candidates,

        "representative_procedural_candidates":
            representative_candidates,

        "procedural_duplicate_resolution_summary": {
            "candidate_count":
                len(
                    resolved_candidates
                ),

            "representative_procedural_expression_count":
                representative_count,

            "duplicate_redundant_procedural_expression_count":
                redundant_count,

            "duplicate_group_count":
                duplicate_group_count,

            "duplicate_candidate_count":
                duplicate_candidate_count,

            "multiple_grounding_non_groupable_count":
                multiple_grounding_non_groupable_count,

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
                "canonical_action",
                "canonical_procedure_role",
                "candidate_procedural_form",
                "contextual_assignment",
                "grounding_identity",
            ],

            "different_actions_merged":
                False,

            "different_procedural_roles_merged":
                False,

            "different_procedural_forms_merged":
                False,

            "different_contextual_assignments_merged":
                False,

            "multiple_grounding_auto_merge_performed":
                False,

            "ungrounded_cross_sentence_merge_performed":
                False,

            "strongest_evidence_representative_selected":
                True,

            "duplicate_provenance_preserved":
                True,

            "final_participant_selection_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "procedural_step_ordering_performed":
                False,

            "procedural_prerequisite_inference_performed":
                False,

            "missing_step_inference_performed":
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
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "article_procedural_consolidation",
    })

    return result



def consolidate_article_procedural_intelligence_v1(
    duplicate_resolution_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Consolidate completed article-local Procedural Intelligence into
    article-level and section-level summaries.

    Only representative procedural expressions are included in the
    canonical consolidated procedural set. Full candidate provenance
    remains preserved in the complete source candidate collection.

    This stage does NOT:
    - create new procedural expressions,
    - infer missing steps,
    - assign procedural sequence or step order,
    - infer prerequisites or dependencies,
    - merge different procedural identities,
    - select a final procedural participant,
    - strengthen evidence classifications,
    - perform quantitative reasoning,
    - perform full temporal reasoning,
    - perform new causal reasoning,
    - establish factual, scientific, medical, or operational truth,
    - use external authority,
    - perform fuzzy semantic similarity,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        duplicate_resolution_result,
        Mapping,
    ):
        raise ProceduralIntelligenceError(
            "duplicate_resolution_result must be a mapping."
        )

    if (
        duplicate_resolution_result.get(
            "schema_version"
        )
        != "procedural_duplicate_resolution_v1"
    ):
        raise ProceduralIntelligenceError(
            "Stage M requires procedural_duplicate_resolution_v1."
        )

    if (
        duplicate_resolution_result.get(
            "status"
        )
        != "PROCEDURAL_DUPLICATE_RESOLUTION_COMPLETE"
    ):
        raise ProceduralIntelligenceError(
            "Duplicate procedural resolution must be complete."
        )

    if (
        duplicate_resolution_result.get(
            "phase"
        )
        != "4.6.10"
    ):
        raise ProceduralIntelligenceError(
            "Stage M requires Phase 4.6.10 input."
        )

    if (
        duplicate_resolution_result.get(
            "patch"
        )
        != "4.6.10L"
    ):
        raise ProceduralIntelligenceError(
            "Stage M requires canonical 4.6.10L input."
        )

    if (
        duplicate_resolution_result.get(
            "next_stage"
        )
        != "article_procedural_consolidation"
    ):
        raise ProceduralIntelligenceError(
            "Stage L must hand off to article_procedural_consolidation."
        )

    if (
        duplicate_resolution_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise ProceduralIntelligenceError(
            "Procedural Intelligence must remain transient."
        )

    source_candidates = list(
        duplicate_resolution_result.get(
            "procedural_candidates"
        )
        or []
    )

    representative_candidates = list(
        duplicate_resolution_result.get(
            "representative_procedural_candidates"
        )
        or []
    )

    seen_source_ids = set()

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
                "Every procedural candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "procedural_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise ProceduralIntelligenceError(
                "Procedural candidate ID is required."
            )

        if candidate_id in seen_source_ids:
            raise ProceduralIntelligenceError(
                "Duplicate procedural candidate ID encountered."
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
            raise ProceduralIntelligenceError(
                "All procedural candidates must complete duplicate resolution before Stage M."
            )

    representative_ids = []

    seen_representative_ids = set()

    for candidate in representative_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
                "Every representative procedural expression must be a mapping."
            )

        if (
            candidate.get(
                "is_representative_procedural_expression"
            )
            is not True
        ):
            raise ProceduralIntelligenceError(
                "Representative procedural list contains a non-representative candidate."
            )

        candidate_id = str(
            candidate.get(
                "procedural_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise ProceduralIntelligenceError(
                "Representative procedural candidate ID is required."
            )

        if candidate_id in seen_representative_ids:
            raise ProceduralIntelligenceError(
                "Duplicate representative procedural candidate ID encountered."
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
                "procedural_candidate_id"
            )
            or ""
        )
        for candidate in source_candidates
        if candidate.get(
            "is_representative_procedural_expression"
        )
        is True
    }

    if set(
        representative_ids
    ) != expected_representative_ids:
        raise ProceduralIntelligenceError(
            "Representative procedural list does not match resolved candidates."
        )

    signal_type_counts = {}
    canonical_action_counts = {}
    procedure_role_counts = {}
    procedural_form_counts = {}
    grounding_status_counts = {}

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

    grounded_count = 0
    ungrounded_count = 0

    contextual_ambiguous_count = 0
    contextual_unambiguous_count = 0

    consolidated_procedural_expressions = []

    for candidate in representative_candidates:
        signal_type = str(
            candidate.get(
                "signal_type"
            )
            or "UNSPECIFIED"
        )

        canonical_action = str(
            candidate.get(
                "canonical_action"
            )
            or "UNSPECIFIED"
        )

        procedure_role = str(
            candidate.get(
                "canonical_procedure_role"
            )
            or "UNSPECIFIED"
        )

        procedural_form = str(
            candidate.get(
                "candidate_procedural_form"
            )
            or "UNSPECIFIED"
        )

        grounding_status = str(
            candidate.get(
                "grounding_status"
            )
            or "UNSPECIFIED"
        )

        evidence_strength = str(
            candidate.get(
                "procedural_evidence_strength"
            )
            or "INSUFFICIENT"
        )

        if evidence_strength not in evidence_strength_counts:
            raise ProceduralIntelligenceError(
                "Representative candidate has invalid procedural evidence strength."
            )

        final_validated = (
            candidate.get(
                "final_procedural_expression_validated"
            )
            is True
        )

        same_sentence_valid = (
            candidate.get(
                "same_sentence_procedural_valid"
            )
            is True
        )

        cross_sentence_valid = (
            candidate.get(
                "cross_sentence_procedural_valid"
            )
            is True
        )

        grounded = (
            candidate.get(
                "entity_concept_grounded"
            )
            is True
        )

        contextual_ambiguity = (
            candidate.get(
                "contextual_assignment_ambiguous"
            )
            is True
            or candidate.get(
                "same_sentence_contextual_assignment_ambiguous"
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

        canonical_action_counts[
            canonical_action
        ] = (
            canonical_action_counts.get(
                canonical_action,
                0,
            )
            + 1
        )

        procedure_role_counts[
            procedure_role
        ] = (
            procedure_role_counts.get(
                procedure_role,
                0,
            )
            + 1
        )

        procedural_form_counts[
            procedural_form
        ] = (
            procedural_form_counts.get(
                procedural_form,
                0,
            )
            + 1
        )

        grounding_status_counts[
            grounding_status
        ] = (
            grounding_status_counts.get(
                grounding_status,
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

        if grounded:
            grounded_count += 1

        else:
            ungrounded_count += 1

        if contextual_ambiguity:
            contextual_ambiguous_count += 1

        else:
            contextual_unambiguous_count += 1

        consolidated_procedural_expressions.append({
            "procedural_candidate_id":
                candidate.get(
                    "procedural_candidate_id"
                ),

            "signal_type":
                candidate.get(
                    "signal_type"
                ),

            "canonical_action":
                candidate.get(
                    "canonical_action"
                ),

            "candidate_procedural_form":
                candidate.get(
                    "candidate_procedural_form"
                ),

            "canonical_procedure_role":
                candidate.get(
                    "canonical_procedure_role"
                ),

            "action_normalization_status":
                candidate.get(
                    "action_normalization_status"
                ),

            "procedure_role_orientation_resolved":
                candidate.get(
                    "procedure_role_orientation_resolved"
                )
                is True,

            "grounding_status":
                grounding_status,

            "entity_concept_grounded":
                grounded,

            "entity_concept_grounding_match_count":
                candidate.get(
                    "entity_concept_grounding_match_count"
                ),

            "entity_concept_grounding_matches":
                candidate.get(
                    "entity_concept_grounding_matches"
                ),

            "final_procedural_expression_validated":
                final_validated,

            "same_sentence_procedural_valid":
                same_sentence_valid,

            "cross_sentence_procedural_valid":
                cross_sentence_valid,

            "contextual_assignment_ambiguous":
                contextual_ambiguity,

            "adjacent_procedural_support_present":
                candidate.get(
                    "adjacent_procedural_support_present"
                )
                is True,

            "procedural_evidence_score":
                candidate.get(
                    "procedural_evidence_score"
                ),

            "procedural_evidence_strength":
                evidence_strength,

            "procedural_evidence_basis":
                candidate.get(
                    "procedural_evidence_basis"
                ),

            "procedural_confidence_cap_applied":
                candidate.get(
                    "procedural_confidence_cap_applied"
                ),

            "section_id":
                candidate.get(
                    "section_id"
                ),

            "sentence_id":
                candidate.get(
                    "sentence_id"
                ),

            "source_text":
                candidate.get(
                    "source_text"
                ),

            "procedural_duplicate_group_id":
                candidate.get(
                    "procedural_duplicate_group_id"
                ),

            "procedural_duplicate_group_size":
                candidate.get(
                    "procedural_duplicate_group_size"
                ),

            "procedural_duplicate_member_ids":
                candidate.get(
                    "procedural_duplicate_member_ids"
                ),

            "final_procedural_participant_selected":
                False,

            "selected_procedural_participant":
                None,

            "procedural_role_preserved":
                candidate.get(
                    "procedural_role_preserved"
                )
                is True,

            "procedural_action_normalization_preserved":
                candidate.get(
                    "procedural_action_normalization_preserved"
                )
                is True,

            "contextual_ambiguity_promoted_to_strong":
                False,

            "multiple_grounding_matches_promoted_to_strong":
                False,

            "cross_sentence_expression_promoted_to_strong":
                False,

            "new_procedural_expression_inference_performed":
                False,

            "procedural_step_order_assigned":
                False,

            "procedural_prerequisite_inferred":
                False,

            "missing_step_inferred":
                False,

            "procedural_evidence_strengthening_performed":
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

    consolidated_procedural_expressions.sort(
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
                    "canonical_procedure_role"
                )
                or ""
            ),
            str(
                expression.get(
                    "canonical_action"
                )
                or ""
            ),
            str(
                expression.get(
                    "candidate_procedural_form"
                )
                or ""
            ),
            str(
                expression.get(
                    "procedural_candidate_id"
                )
                or ""
            ),
        )
    )

    consolidated_sections = []

    seen_section_ids = set()

    for section in (
        duplicate_resolution_result.get(
            "procedural_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
                "Every procedural section must be a mapping."
            )

        section_id = str(
            section.get(
                "section_id"
            )
            or ""
        )

        if not section_id:
            raise ProceduralIntelligenceError(
                "Procedural section ID is required."
            )

        if section_id in seen_section_ids:
            raise ProceduralIntelligenceError(
                "Duplicate procedural section ID encountered."
            )

        seen_section_ids.add(
            section_id
        )

        section_expressions = [
            expression
            for expression in consolidated_procedural_expressions
            if str(
                expression.get(
                    "section_id"
                )
                or ""
            )
            == section_id
        ]

        section_signal_counts = {}
        section_action_counts = {}
        section_role_counts = {}
        section_form_counts = {}
        section_grounding_status_counts = {}

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

            canonical_action = str(
                expression.get(
                    "canonical_action"
                )
                or "UNSPECIFIED"
            )

            procedure_role = str(
                expression.get(
                    "canonical_procedure_role"
                )
                or "UNSPECIFIED"
            )

            procedural_form = str(
                expression.get(
                    "candidate_procedural_form"
                )
                or "UNSPECIFIED"
            )

            grounding_status = str(
                expression.get(
                    "grounding_status"
                )
                or "UNSPECIFIED"
            )

            evidence_strength = str(
                expression.get(
                    "procedural_evidence_strength"
                )
                or "INSUFFICIENT"
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

            section_action_counts[
                canonical_action
            ] = (
                section_action_counts.get(
                    canonical_action,
                    0,
                )
                + 1
            )

            section_role_counts[
                procedure_role
            ] = (
                section_role_counts.get(
                    procedure_role,
                    0,
                )
                + 1
            )

            section_form_counts[
                procedural_form
            ] = (
                section_form_counts.get(
                    procedural_form,
                    0,
                )
                + 1
            )

            section_grounding_status_counts[
                grounding_status
            ] = (
                section_grounding_status_counts.get(
                    grounding_status,
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

            "representative_procedural_expressions":
                section_expressions,

            "representative_procedural_expression_count":
                len(
                    section_expressions
                ),

            "validated_procedural_expression_count":
                sum(
                    1
                    for expression in section_expressions
                    if expression.get(
                        "final_procedural_expression_validated"
                    )
                    is True
                ),

            "unvalidated_procedural_expression_count":
                sum(
                    1
                    for expression in section_expressions
                    if expression.get(
                        "final_procedural_expression_validated"
                    )
                    is False
                ),

            "same_sentence_validated_procedural_count":
                sum(
                    1
                    for expression in section_expressions
                    if expression.get(
                        "same_sentence_procedural_valid"
                    )
                    is True
                ),

            "cross_sentence_validated_procedural_count":
                sum(
                    1
                    for expression in section_expressions
                    if expression.get(
                        "cross_sentence_procedural_valid"
                    )
                    is True
                ),

            "grounded_procedural_expression_count":
                sum(
                    1
                    for expression in section_expressions
                    if expression.get(
                        "entity_concept_grounded"
                    )
                    is True
                ),

            "ungrounded_procedural_expression_count":
                sum(
                    1
                    for expression in section_expressions
                    if expression.get(
                        "entity_concept_grounded"
                    )
                    is False
                ),

            "contextually_ambiguous_procedural_count":
                sum(
                    1
                    for expression in section_expressions
                    if expression.get(
                        "contextual_assignment_ambiguous"
                    )
                    is True
                ),

            "procedural_signal_type_counts":
                section_signal_counts,

            "canonical_action_counts":
                section_action_counts,

            "canonical_procedure_role_counts":
                section_role_counts,

            "procedural_form_counts":
                section_form_counts,

            "grounding_status_counts":
                section_grounding_status_counts,

            "procedural_evidence_strength_counts":
                section_strength_counts,

            "procedural_consolidation_complete":
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
            "procedural_duplicate_resolution_status"
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
        raise ProceduralIntelligenceError(
            "Top-level Stage-L duplicate resolution boundary must be complete."
        )

    if (
        boundaries.get(
            "article_procedural_consolidation_performed"
        )
        is True
    ):
        raise ProceduralIntelligenceError(
            "Article procedural consolidation must not already be performed."
        )

    boundaries[
        "article_procedural_consolidation_performed"
    ] = True

    boundaries[
        "new_procedural_expression_inference_performed"
    ] = False

    boundaries[
        "procedural_step_ordering_performed"
    ] = False

    boundaries[
        "procedural_prerequisite_inference_performed"
    ] = False

    boundaries[
        "missing_step_inference_performed"
    ] = False

    boundaries[
        "final_procedural_participant_selection_performed"
    ] = False

    boundaries[
        "procedural_evidence_strengthening_performed"
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
            "procedural_article_consolidation_v1",

        "patch":
            "4.6.10M",

        "status":
            "PROCEDURAL_ARTICLE_CONSOLIDATION_COMPLETE",

        "consolidated_procedural_sections":
            consolidated_sections,

        "consolidated_procedural_expressions":
            consolidated_procedural_expressions,

        "article_procedural_summary": {
            "total_candidate_count":
                total_candidate_count,

            "representative_procedural_expression_count":
                representative_count,

            "duplicate_redundant_procedural_expression_count":
                redundant_count,

            "validated_procedural_expression_count":
                validated_count,

            "unvalidated_procedural_expression_count":
                unvalidated_count,

            "same_sentence_validated_procedural_count":
                same_sentence_validated_count,

            "cross_sentence_validated_procedural_count":
                cross_sentence_validated_count,

            "grounded_procedural_expression_count":
                grounded_count,

            "ungrounded_procedural_expression_count":
                ungrounded_count,

            "contextually_ambiguous_procedural_count":
                contextual_ambiguous_count,

            "contextually_unambiguous_procedural_count":
                contextual_unambiguous_count,

            "procedural_signal_type_counts":
                signal_type_counts,

            "canonical_action_counts":
                canonical_action_counts,

            "canonical_procedure_role_counts":
                procedure_role_counts,

            "procedural_form_counts":
                procedural_form_counts,

            "grounding_status_counts":
                grounding_status_counts,

            "procedural_evidence_strength_counts":
                evidence_strength_counts,

            "representative_count_matches_consolidated":
                (
                    representative_count
                    == len(
                        consolidated_procedural_expressions
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

            "grounding_count_accounting_valid":
                (
                    grounded_count
                    + ungrounded_count
                    == representative_count
                ),

            "contextual_ambiguity_count_accounting_valid":
                (
                    contextual_ambiguous_count
                    + contextual_unambiguous_count
                    == representative_count
                ),

            "representatives_only_in_consolidated_set":
                True,

            "procedural_actions_preserved":
                True,

            "procedural_roles_preserved":
                True,

            "procedural_forms_preserved":
                True,

            "grounding_identity_preserved":
                True,

            "evidence_strengths_preserved":
                True,

            "final_participant_selection_performed":
                False,

            "new_procedural_expression_inference_performed":
                False,

            "procedural_step_ordering_performed":
                False,

            "procedural_prerequisite_inference_performed":
                False,

            "missing_step_inference_performed":
                False,

            "procedural_evidence_strengthening_performed":
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
            "final_procedural_intelligence_result",
    })

    return result



def build_final_procedural_intelligence_result_v1(
    article_consolidation_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Build the final canonical Phase 4.6.10 Procedural Intelligence result.

    This stage packages the completed article-local procedural analysis
    without adding new interpretation.

    It does NOT:
    - certify the result,
    - create or infer procedural expressions,
    - assign procedural sequence or step order,
    - infer prerequisites or dependencies,
    - infer missing steps,
    - select a final procedural participant,
    - strengthen procedural evidence,
    - perform quantitative reasoning,
    - perform full temporal reasoning,
    - perform new causal reasoning,
    - establish factual, scientific, medical, or operational truth,
    - use external authority,
    - perform fuzzy similarity,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        article_consolidation_result,
        Mapping,
    ):
        raise ProceduralIntelligenceError(
            "article_consolidation_result must be a mapping."
        )

    if (
        article_consolidation_result.get(
            "schema_version"
        )
        != "procedural_article_consolidation_v1"
    ):
        raise ProceduralIntelligenceError(
            "Stage N requires procedural_article_consolidation_v1."
        )

    if (
        article_consolidation_result.get(
            "status"
        )
        != "PROCEDURAL_ARTICLE_CONSOLIDATION_COMPLETE"
    ):
        raise ProceduralIntelligenceError(
            "Article procedural consolidation must be complete."
        )

    if (
        article_consolidation_result.get(
            "phase"
        )
        != "4.6.10"
    ):
        raise ProceduralIntelligenceError(
            "Stage N requires Phase 4.6.10 input."
        )

    if (
        article_consolidation_result.get(
            "patch"
        )
        != "4.6.10M"
    ):
        raise ProceduralIntelligenceError(
            "Stage N requires canonical 4.6.10M input."
        )

    if (
        article_consolidation_result.get(
            "next_stage"
        )
        != "final_procedural_intelligence_result"
    ):
        raise ProceduralIntelligenceError(
            "Stage M must hand off to final_procedural_intelligence_result."
        )

    if (
        article_consolidation_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise ProceduralIntelligenceError(
            "Procedural Intelligence must remain transient."
        )

    consolidated_expressions = list(
        article_consolidation_result.get(
            "consolidated_procedural_expressions"
        )
        or []
    )

    consolidated_sections = list(
        article_consolidation_result.get(
            "consolidated_procedural_sections"
        )
        or []
    )

    full_candidates = list(
        article_consolidation_result.get(
            "procedural_candidates"
        )
        or []
    )

    representative_candidates = list(
        article_consolidation_result.get(
            "representative_procedural_candidates"
        )
        or []
    )

    summary = dict(
        article_consolidation_result.get(
            "article_procedural_summary"
        )
        or {}
    )

    required_true_summary_fields = (
        "representative_count_matches_consolidated",
        "candidate_accounting_valid",
        "validation_count_accounting_valid",
        "grounding_count_accounting_valid",
        "contextual_ambiguity_count_accounting_valid",
        "representatives_only_in_consolidated_set",
        "procedural_actions_preserved",
        "procedural_roles_preserved",
        "procedural_forms_preserved",
        "grounding_identity_preserved",
        "evidence_strengths_preserved",
        "article_local_only",
    )

    for field_name in required_true_summary_fields:
        if (
            summary.get(
                field_name
            )
            is not True
        ):
            raise ProceduralIntelligenceError(
                field_name
                + " must be True before final Procedural Intelligence packaging."
            )

    required_false_summary_fields = (
        "final_participant_selection_performed",
        "new_procedural_expression_inference_performed",
        "procedural_step_ordering_performed",
        "procedural_prerequisite_inference_performed",
        "missing_step_inference_performed",
        "procedural_evidence_strengthening_performed",
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
            raise ProceduralIntelligenceError(
                field_name
                + " must remain False before final Procedural Intelligence packaging."
            )

    consolidated_ids = set()

    for expression in consolidated_expressions:
        if not isinstance(
            expression,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
                "Every consolidated procedural expression must be a mapping."
            )

        candidate_id = str(
            expression.get(
                "procedural_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise ProceduralIntelligenceError(
                "Consolidated procedural candidate ID is required."
            )

        if candidate_id in consolidated_ids:
            raise ProceduralIntelligenceError(
                "Duplicate consolidated procedural candidate ID encountered."
            )

        consolidated_ids.add(
            candidate_id
        )

        if (
            expression.get(
                "final_procedural_participant_selected"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Final Procedural Intelligence must not select a procedural participant."
            )

        if (
            expression.get(
                "selected_procedural_participant"
            )
            is not None
        ):
            raise ProceduralIntelligenceError(
                "Selected procedural participant must remain None."
            )

        if (
            expression.get(
                "contextual_ambiguity_promoted_to_strong"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Contextual ambiguity must not be promoted to STRONG."
            )

        if (
            expression.get(
                "multiple_grounding_matches_promoted_to_strong"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Multiple-grounding procedural expressions must not be promoted to STRONG."
            )

        if (
            expression.get(
                "cross_sentence_expression_promoted_to_strong"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Cross-sentence procedural expressions must not be promoted to STRONG."
            )

        if (
            expression.get(
                "new_procedural_expression_inference_performed"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Final Procedural Intelligence must not add new procedural expressions."
            )

        if (
            expression.get(
                "procedural_step_order_assigned"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Final Procedural Intelligence must not assign procedural step order."
            )

        if (
            expression.get(
                "procedural_prerequisite_inferred"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Final Procedural Intelligence must not infer procedural prerequisites."
            )

        if (
            expression.get(
                "missing_step_inferred"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Final Procedural Intelligence must not infer missing steps."
            )

        if (
            expression.get(
                "procedural_evidence_strengthening_performed"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Final Procedural Intelligence must not strengthen procedural evidence."
            )

        if (
            expression.get(
                "quantitative_reasoning_performed"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Final Procedural Intelligence must not perform quantitative reasoning."
            )

        if (
            expression.get(
                "temporal_reasoning_performed"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Final Procedural Intelligence must not perform temporal reasoning."
            )

        if (
            expression.get(
                "new_causal_reasoning_performed"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Final Procedural Intelligence must not perform new causal reasoning."
            )

        if (
            expression.get(
                "truth_assessed"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Procedural Intelligence must not assess factual truth."
            )

        if (
            expression.get(
                "external_authority_checked"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Procedural Intelligence must not use external authority."
            )

    representative_ids = {
        str(
            candidate.get(
                "procedural_candidate_id"
            )
            or ""
        )
        for candidate in representative_candidates
    }

    if "" in representative_ids:
        raise ProceduralIntelligenceError(
            "Representative procedural candidate ID is required."
        )

    if representative_ids != consolidated_ids:
        raise ProceduralIntelligenceError(
            "Final consolidated procedural set must match representative candidates exactly."
        )

    boundaries = dict(
        article_consolidation_result.get(
            "processing_boundaries"
        )
        or {}
    )

    required_false_boundaries = (
        "new_procedural_expression_inference_performed",
        "procedural_step_ordering_performed",
        "procedural_prerequisite_inference_performed",
        "missing_step_inference_performed",
        "final_procedural_participant_selection_performed",
        "procedural_evidence_strengthening_performed",
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
            raise ProceduralIntelligenceError(
                boundary_name
                + " must remain False in final Procedural Intelligence."
            )

    if (
        boundaries.get(
            "article_procedural_consolidation_performed"
        )
        is not True
    ):
        raise ProceduralIntelligenceError(
            "Article procedural consolidation boundary must be complete."
        )

    final_boundaries = dict(
        boundaries
    )

    final_boundaries[
        "final_procedural_result_built"
    ] = True

    final_boundaries[
        "procedural_certification_performed"
    ] = False

    result = {
        "schema_version":
            "procedural_intelligence_result_v1",

        "procedural_intelligence_version":
            article_consolidation_result.get(
                "procedural_intelligence_version"
            )
            or "procedural_intelligence_v1",

        "phase":
            "4.6.10",

        "patch":
            "4.6.10N",

        "status":
            "PROCEDURAL_INTELLIGENCE_RESULT_COMPLETE",

        "article_identity": {
            "article_id":
                article_consolidation_result.get(
                    "article_id"
                ),

            "workspace_id":
                article_consolidation_result.get(
                    "workspace_id"
                ),

            "source_type":
                article_consolidation_result.get(
                    "source_type"
                ),

            "source_id":
                article_consolidation_result.get(
                    "source_id"
                ),

            "document_id":
                article_consolidation_result.get(
                    "document_id"
                ),

            "content_hash":
                article_consolidation_result.get(
                    "content_hash"
                ),

            "body_ref":
                article_consolidation_result.get(
                    "body_ref"
                ),

            "title":
                article_consolidation_result.get(
                    "title"
                ),
        },

        "consolidated_procedural_expressions":
            consolidated_expressions,

        "consolidated_procedural_sections":
            consolidated_sections,

        "representative_procedural_candidates":
            representative_candidates,

        "procedural_candidates":
            full_candidates,

        "procedural_claim_units":
            list(
                article_consolidation_result.get(
                    "procedural_claim_units"
                )
                or []
            ),

        "article_procedural_summary":
            summary,

        "procedural_boundaries": {
            "article_local_only":
                True,

            "scientific_truth_verified":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_checked":
                False,

            "new_procedural_expression_inference_performed":
                False,

            "procedural_step_ordering_performed":
                False,

            "procedural_prerequisite_inference_performed":
                False,

            "missing_step_inference_performed":
                False,

            "final_procedural_participant_selection_performed":
                False,

            "procedural_evidence_strengthening_performed":
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
                "4.6.10O",
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "procedural_intelligence_certification",
    }

    return result



def certify_procedural_intelligence_v1(
    final_procedural_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Certify the final Phase 4.6.10 Procedural Intelligence result.

    Certification validates structure, accounting, provenance,
    procedural-action integrity, procedural-role integrity,
    procedural-form integrity, grounding integrity, evidence-strength
    caps, boundaries, and handoff readiness.

    Certification does NOT:
    - create or infer procedural expressions,
    - assign procedural sequence or step order,
    - infer prerequisites or dependencies,
    - infer missing steps,
    - select a final procedural participant,
    - strengthen evidence classifications,
    - perform quantitative reasoning,
    - perform full temporal reasoning,
    - perform new causal reasoning,
    - establish factual, scientific, medical, or operational truth,
    - use external authority,
    - perform fuzzy similarity,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        final_procedural_result,
        Mapping,
    ):
        raise ProceduralIntelligenceError(
            "final_procedural_result must be a mapping."
        )

    if (
        final_procedural_result.get(
            "schema_version"
        )
        != "procedural_intelligence_result_v1"
    ):
        raise ProceduralIntelligenceError(
            "Stage O requires procedural_intelligence_result_v1."
        )

    if (
        final_procedural_result.get(
            "status"
        )
        != "PROCEDURAL_INTELLIGENCE_RESULT_COMPLETE"
    ):
        raise ProceduralIntelligenceError(
            "Final Procedural Intelligence result must be complete."
        )

    if (
        final_procedural_result.get(
            "phase"
        )
        != "4.6.10"
    ):
        raise ProceduralIntelligenceError(
            "Stage O requires Phase 4.6.10 input."
        )

    if (
        final_procedural_result.get(
            "patch"
        )
        != "4.6.10N"
    ):
        raise ProceduralIntelligenceError(
            "Stage O requires canonical 4.6.10N input."
        )

    if (
        final_procedural_result.get(
            "next_stage"
        )
        != "procedural_intelligence_certification"
    ):
        raise ProceduralIntelligenceError(
            "Stage N must hand off to procedural_intelligence_certification."
        )

    if (
        final_procedural_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise ProceduralIntelligenceError(
            "Procedural Intelligence must remain transient."
        )

    identity = dict(
        final_procedural_result.get(
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
            raise ProceduralIntelligenceError(
                "Required article identity field missing: "
                + field
            )

    consolidated_expressions = list(
        final_procedural_result.get(
            "consolidated_procedural_expressions"
        )
        or []
    )

    representative_candidates = list(
        final_procedural_result.get(
            "representative_procedural_candidates"
        )
        or []
    )

    full_candidates = list(
        final_procedural_result.get(
            "procedural_candidates"
        )
        or []
    )

    claim_units = list(
        final_procedural_result.get(
            "procedural_claim_units"
        )
        or []
    )

    consolidated_sections = list(
        final_procedural_result.get(
            "consolidated_procedural_sections"
        )
        or []
    )

    summary = dict(
        final_procedural_result.get(
            "article_procedural_summary"
        )
        or {}
    )

    required_true_summary_fields = (
        "representative_count_matches_consolidated",
        "candidate_accounting_valid",
        "validation_count_accounting_valid",
        "grounding_count_accounting_valid",
        "contextual_ambiguity_count_accounting_valid",
        "representatives_only_in_consolidated_set",
        "procedural_actions_preserved",
        "procedural_roles_preserved",
        "procedural_forms_preserved",
        "grounding_identity_preserved",
        "evidence_strengths_preserved",
        "article_local_only",
    )

    for field_name in required_true_summary_fields:
        if (
            summary.get(
                field_name
            )
            is not True
        ):
            raise ProceduralIntelligenceError(
                field_name
                + " must be verified before Procedural Intelligence certification."
            )

    if (
        summary.get(
            "representative_procedural_expression_count"
        )
        != len(
            consolidated_expressions
        )
    ):
        raise ProceduralIntelligenceError(
            "Consolidated procedural expression count does not match summary."
        )

    if (
        len(
            representative_candidates
        )
        != len(
            consolidated_expressions
        )
    ):
        raise ProceduralIntelligenceError(
            "Representative candidate count does not match consolidated procedural expressions."
        )

    if (
        summary.get(
            "total_candidate_count"
        )
        != len(
            full_candidates
        )
    ):
        raise ProceduralIntelligenceError(
            "Full procedural candidate count does not match summary."
        )

    redundant_count = sum(
        1
        for candidate in full_candidates
        if candidate.get(
            "procedural_duplicate_resolution_status"
        )
        == "DUPLICATE_REDUNDANT"
    )

    if (
        summary.get(
            "duplicate_redundant_procedural_expression_count"
        )
        != redundant_count
    ):
        raise ProceduralIntelligenceError(
            "Redundant procedural candidate count does not match summary."
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
        raise ProceduralIntelligenceError(
            "Procedural representative/redundant accounting is invalid."
        )

    consolidated_ids = [
        str(
            expression.get(
                "procedural_candidate_id"
            )
            or ""
        )
        for expression in consolidated_expressions
    ]

    representative_ids = [
        str(
            candidate.get(
                "procedural_candidate_id"
            )
            or ""
        )
        for candidate in representative_candidates
    ]

    full_candidate_ids = [
        str(
            candidate.get(
                "procedural_candidate_id"
            )
            or ""
        )
        for candidate in full_candidates
    ]

    if any(
        not candidate_id
        for candidate_id in consolidated_ids
    ):
        raise ProceduralIntelligenceError(
            "Every consolidated procedural expression requires a candidate ID."
        )

    if any(
        not candidate_id
        for candidate_id in representative_ids
    ):
        raise ProceduralIntelligenceError(
            "Every representative procedural candidate requires a candidate ID."
        )

    if any(
        not candidate_id
        for candidate_id in full_candidate_ids
    ):
        raise ProceduralIntelligenceError(
            "Every procedural candidate requires a candidate ID."
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
        raise ProceduralIntelligenceError(
            "Duplicate consolidated procedural candidate IDs are not allowed."
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
        raise ProceduralIntelligenceError(
            "Duplicate representative procedural candidate IDs are not allowed."
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
        raise ProceduralIntelligenceError(
            "Duplicate full procedural candidate IDs are not allowed."
        )

    if (
        set(
            consolidated_ids
        )
        != set(
            representative_ids
        )
    ):
        raise ProceduralIntelligenceError(
            "Consolidated expressions and representative procedural candidates disagree."
        )

    if not set(
        representative_ids
    ).issubset(
        set(
            full_candidate_ids
        )
    ):
        raise ProceduralIntelligenceError(
            "Representative procedural candidates must exist in the full candidate collection."
        )

    contextual_ambiguous_strong_count = 0
    multiple_grounding_strong_count = 0
    cross_sentence_strong_count = 0

    for expression in consolidated_expressions:
        if not isinstance(
            expression,
            Mapping,
        ):
            raise ProceduralIntelligenceError(
                "Every consolidated procedural expression must be a mapping."
            )

        if (
            expression.get(
                "final_procedural_participant_selected"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Certified Procedural Intelligence must not select a final participant."
            )

        if (
            expression.get(
                "selected_procedural_participant"
            )
            is not None
        ):
            raise ProceduralIntelligenceError(
                "Selected procedural participant must remain None."
            )

        if (
            expression.get(
                "procedural_role_preserved"
            )
            is not True
        ):
            raise ProceduralIntelligenceError(
                "Every consolidated procedural expression must preserve its procedure role."
            )

        if (
            expression.get(
                "procedural_action_normalization_preserved"
            )
            is not True
        ):
            raise ProceduralIntelligenceError(
                "Every consolidated procedural expression must preserve action normalization."
            )

        if (
            expression.get(
                "contextual_ambiguity_promoted_to_strong"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Contextual ambiguity promotion must remain prohibited."
            )

        if (
            expression.get(
                "multiple_grounding_matches_promoted_to_strong"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Multiple-grounding STRONG promotion must remain prohibited."
            )

        if (
            expression.get(
                "cross_sentence_expression_promoted_to_strong"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Cross-sentence STRONG promotion must remain prohibited."
            )

        if (
            expression.get(
                "new_procedural_expression_inference_performed"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Certified Procedural Intelligence must not add new procedural expressions."
            )

        if (
            expression.get(
                "procedural_step_order_assigned"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Certified Procedural Intelligence must not assign procedural step order."
            )

        if (
            expression.get(
                "procedural_prerequisite_inferred"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Certified Procedural Intelligence must not infer prerequisites."
            )

        if (
            expression.get(
                "missing_step_inferred"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Certified Procedural Intelligence must not infer missing steps."
            )

        if (
            expression.get(
                "procedural_evidence_strengthening_performed"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Certified Procedural Intelligence must not strengthen evidence."
            )

        if (
            expression.get(
                "quantitative_reasoning_performed"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Certified Procedural Intelligence must not perform quantitative reasoning."
            )

        if (
            expression.get(
                "temporal_reasoning_performed"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Certified Procedural Intelligence must not perform temporal reasoning."
            )

        if (
            expression.get(
                "new_causal_reasoning_performed"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Certified Procedural Intelligence must not perform new causal reasoning."
            )

        if (
            expression.get(
                "truth_assessed"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Procedural Intelligence must not assess factual truth."
            )

        if (
            expression.get(
                "external_authority_checked"
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                "Procedural Intelligence must not use external authority."
            )

        evidence_strength = str(
            expression.get(
                "procedural_evidence_strength"
            )
            or ""
        )

        if evidence_strength not in {
            "STRONG",
            "MODERATE",
            "LIMITED",
            "INSUFFICIENT",
        }:
            raise ProceduralIntelligenceError(
                "Consolidated procedural expression has invalid evidence strength."
            )

        if (
            expression.get(
                "contextual_assignment_ambiguous"
            )
            is True
            and evidence_strength
            == "STRONG"
        ):
            contextual_ambiguous_strong_count += 1

        if (
            expression.get(
                "grounding_status"
            )
            == "GROUNDED_MULTIPLE_MATCHES"
            and evidence_strength
            == "STRONG"
        ):
            multiple_grounding_strong_count += 1

        if (
            expression.get(
                "cross_sentence_procedural_valid"
            )
            is True
            and evidence_strength
            == "STRONG"
        ):
            cross_sentence_strong_count += 1

    if contextual_ambiguous_strong_count != 0:
        raise ProceduralIntelligenceError(
            "Contextually ambiguous procedural expressions must never certify with STRONG evidence."
        )

    if multiple_grounding_strong_count != 0:
        raise ProceduralIntelligenceError(
            "Multiple-grounding procedural expressions must never certify with STRONG evidence."
        )

    if cross_sentence_strong_count != 0:
        raise ProceduralIntelligenceError(
            "Cross-sentence procedural expressions must never certify with STRONG evidence."
        )

    procedural_boundaries = dict(
        final_procedural_result.get(
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
        raise ProceduralIntelligenceError(
            "Final Procedural Intelligence must remain article-local."
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

    for boundary_name in required_false_procedural_boundaries:
        if (
            procedural_boundaries.get(
                boundary_name
            )
            is not False
        ):
            raise ProceduralIntelligenceError(
                boundary_name
                + " must remain False."
            )

    processing_boundaries = dict(
        final_procedural_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        processing_boundaries.get(
            "article_procedural_consolidation_performed"
        )
        is not True
    ):
        raise ProceduralIntelligenceError(
            "Article procedural consolidation must be complete."
        )

    if (
        processing_boundaries.get(
            "final_procedural_result_built"
        )
        is not True
    ):
        raise ProceduralIntelligenceError(
            "Final Procedural Intelligence result must already be built."
        )

    if (
        processing_boundaries.get(
            "procedural_certification_performed"
        )
        is not False
    ):
        raise ProceduralIntelligenceError(
            "Input must not already be certified."
        )

    certification = dict(
        final_procedural_result.get(
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
        != "4.6.10O"
    ):
        raise ProceduralIntelligenceError(
            "Stage N certification state is invalid."
        )

    required_false_summary_fields = (
        "final_participant_selection_performed",
        "new_procedural_expression_inference_performed",
        "procedural_step_ordering_performed",
        "procedural_prerequisite_inference_performed",
        "missing_step_inference_performed",
        "procedural_evidence_strengthening_performed",
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
            raise ProceduralIntelligenceError(
                field_name
                + " must remain False at certification."
            )

    certified_processing_boundaries = dict(
        processing_boundaries
    )

    certified_processing_boundaries[
        "procedural_certification_performed"
    ] = True

    certified_processing_boundaries[
        "procedural_intelligence_certified"
    ] = True

    result = dict(
        final_procedural_result
    )

    result.update({
        "schema_version":
            "certified_procedural_intelligence_result_v1",

        "patch":
            "4.6.10O",

        "status":
            "PROCEDURAL_INTELLIGENCE_CERTIFIED",

        "processing_boundaries":
            certified_processing_boundaries,

        "certification": {
            "performed":
                True,

            "certified":
                True,

            "certification_stage":
                "4.6.10O",

            "certification_scope":
                "ARTICLE_LOCAL_PROCEDURAL_INTELLIGENCE",

            "structural_integrity_verified":
                True,

            "candidate_accounting_verified":
                True,

            "representative_procedural_integrity_verified":
                True,

            "provenance_preserved":
                True,

            "procedural_action_integrity_verified":
                True,

            "procedural_role_integrity_verified":
                True,

            "procedural_form_integrity_verified":
                True,

            "grounding_integrity_verified":
                True,

            "evidence_strength_integrity_verified":
                True,

            "contextual_ambiguity_strength_cap_verified":
                True,

            "multiple_grounding_strength_cap_verified":
                True,

            "cross_sentence_strength_cap_verified":
                True,

            "boundary_integrity_verified":
                True,

            "scientific_truth_verified":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_check_performed":
                False,

            "new_procedural_expression_inference_performed":
                False,

            "procedural_step_ordering_performed":
                False,

            "procedural_prerequisite_inference_performed":
                False,

            "missing_step_inference_performed":
                False,

            "procedural_evidence_strengthening_performed":
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

        "procedural_certification_summary": {
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

            "representative_procedural_expression_count":
                len(
                    representative_candidates
                ),

            "consolidated_procedural_expression_count":
                len(
                    consolidated_expressions
                ),

            "duplicate_redundant_procedural_expression_count":
                redundant_count,

            "validated_procedural_expression_count":
                summary.get(
                    "validated_procedural_expression_count"
                ),

            "unvalidated_procedural_expression_count":
                summary.get(
                    "unvalidated_procedural_expression_count"
                ),

            "same_sentence_validated_procedural_count":
                summary.get(
                    "same_sentence_validated_procedural_count"
                ),

            "cross_sentence_validated_procedural_count":
                summary.get(
                    "cross_sentence_validated_procedural_count"
                ),

            "contextually_ambiguous_procedural_count":
                summary.get(
                    "contextually_ambiguous_procedural_count"
                ),

            "contextual_ambiguous_strong_count":
                contextual_ambiguous_strong_count,

            "multiple_grounding_strong_count":
                multiple_grounding_strong_count,

            "cross_sentence_strong_count":
                cross_sentence_strong_count,

            "procedural_actions_preserved":
                True,

            "procedural_roles_preserved":
                True,

            "procedural_forms_preserved":
                True,

            "grounding_integrity_preserved":
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
            "analogical_intelligence",
    })

    return result
