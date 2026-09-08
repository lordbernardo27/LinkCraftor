from __future__ import annotations

import re

from typing import Any, Mapping


class QuantitativeIntelligenceError(ValueError):
    """Raised when Quantitative Intelligence receives invalid input."""


def validate_quantitative_intelligence_intake_v1(
    certified_causal_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate the certified Phase 4.6.8 Causal Intelligence result
    before Phase 4.6.9 Quantitative Intelligence begins.

    This stage performs intake validation only.

    It does NOT:
    - extract numbers,
    - interpret measurements,
    - normalize units,
    - perform calculations,
    - infer quantitative relationships,
    - perform temporal reasoning,
    - perform new causal reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        certified_causal_result,
        Mapping,
    ):
        raise QuantitativeIntelligenceError(
            "certified_causal_result must be a mapping."
        )

    if (
        certified_causal_result.get(
            "schema_version"
        )
        != "certified_causal_intelligence_result_v1"
    ):
        raise QuantitativeIntelligenceError(
            "Phase 4.6.9 requires certified_causal_intelligence_result_v1."
        )

    if (
        certified_causal_result.get(
            "status"
        )
        != "CAUSAL_INTELLIGENCE_CERTIFIED"
    ):
        raise QuantitativeIntelligenceError(
            "Causal Intelligence must be certified before Quantitative Intelligence."
        )

    if (
        certified_causal_result.get(
            "phase"
        )
        != "4.6.8"
    ):
        raise QuantitativeIntelligenceError(
            "Phase 4.6.9 requires certified Phase 4.6.8 input."
        )

    if (
        certified_causal_result.get(
            "patch"
        )
        != "4.6.8O"
    ):
        raise QuantitativeIntelligenceError(
            "Phase 4.6.9 requires canonical 4.6.8O input."
        )

    if (
        certified_causal_result.get(
            "next_stage"
        )
        != "quantitative_intelligence"
    ):
        raise QuantitativeIntelligenceError(
            "Certified Causal Intelligence must hand off to quantitative_intelligence."
        )

    if (
        certified_causal_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise QuantitativeIntelligenceError(
            "Quantitative Intelligence intake must remain article-local and transient."
        )

    certification = dict(
        certified_causal_result.get(
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
        != "4.6.8O"
        or certification.get(
            "certification_scope"
        )
        != "ARTICLE_LOCAL_CAUSAL_INTELLIGENCE"
    ):
        raise QuantitativeIntelligenceError(
            "Certified Causal Intelligence certification envelope is invalid."
        )

    required_true_certification_fields = (
        "structural_integrity_verified",
        "candidate_accounting_verified",
        "representative_causal_integrity_verified",
        "provenance_preserved",
        "causal_direction_integrity_verified",
        "causal_form_class_integrity_verified",
        "causal_sensitive_strength_cap_verified",
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
            raise QuantitativeIntelligenceError(
                "Required Causal Intelligence certification field is not verified: "
                + field_name
            )

    required_false_certification_fields = (
        "scientific_truth_verified",
        "truth_assessment_performed",
        "external_authority_check_performed",
        "causal_chain_inference_performed",
        "quantitative_reasoning_performed",
        "temporal_reasoning_performed",
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
            raise QuantitativeIntelligenceError(
                "Causal certification boundary must remain False: "
                + field_name
            )

    processing_boundaries = dict(
        certified_causal_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        processing_boundaries.get(
            "causal_certification_performed"
        )
        is not True
    ):
        raise QuantitativeIntelligenceError(
            "Causal certification processing boundary must be complete."
        )

    if (
        processing_boundaries.get(
            "causal_intelligence_certified"
        )
        is not True
    ):
        raise QuantitativeIntelligenceError(
            "Causal Intelligence must be marked certified."
        )

    causal_boundaries = dict(
        certified_causal_result.get(
            "causal_boundaries"
        )
        or {}
    )

    if (
        causal_boundaries.get(
            "article_local_only"
        )
        is not True
    ):
        raise QuantitativeIntelligenceError(
            "Certified Causal Intelligence must remain article-local."
        )

    required_false_causal_boundaries = (
        "scientific_truth_verified",
        "truth_assessment_performed",
        "external_authority_checked",
        "new_causal_relation_inference_performed",
        "causal_chain_inference_performed",
        "causal_form_strengthening_performed",
        "cause_effect_reversal_performed",
        "fuzzy_similarity_performed",
        "quantitative_reasoning_performed",
        "temporal_reasoning_performed",
        "linking_decisions_performed",
        "semantic_memory_write_performed",
        "persistence_performed",
    )

    for field_name in required_false_causal_boundaries:
        if (
            causal_boundaries.get(
                field_name
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Certified causal boundary must remain False: "
                + field_name
            )

    article_identity = dict(
        certified_causal_result.get(
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
            raise QuantitativeIntelligenceError(
                "Required article identity field missing: "
                + field_name
            )

    return {
        "schema_version":
            "quantitative_intelligence_intake_v1",

        "quantitative_intelligence_version":
            "quantitative_intelligence_v1",

        "phase":
            "4.6.9",

        "patch":
            "4.6.9B",

        "status":
            "QUANTITATIVE_INTELLIGENCE_INTAKE_VALIDATED",

        "article_identity":
            article_identity,

        "certified_causal_result":
            dict(
                certified_causal_result
            ),

        "intake_validation": {
            "certified_causal_schema_verified":
                True,

            "certified_causal_status_verified":
                True,

            "certified_causal_patch_verified":
                True,

            "causal_certification_verified":
                True,

            "causal_boundary_integrity_verified":
                True,

            "article_identity_verified":
                True,

            "quantitative_reasoning_not_preperformed":
                True,

            "article_local_only":
                True,
        },

        "processing_boundaries": {
            "quantitative_intake_validation_performed":
                True,

            "quantitative_claim_unit_preparation_performed":
                False,

            "numeric_signal_interpretation_performed":
                False,

            "quantitative_candidate_extraction_performed":
                False,

            "unit_normalization_performed":
                False,

            "derived_calculation_performed":
                False,

            "quantitative_inference_performed":
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
            "quantitative_claim_unit_preparation",
    }



def build_quantitative_claim_units_v1(
    certified_causal_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Build canonical Phase 4.6.9 Quantitative Claim Units from
    certified Phase 4.6.8 Causal Intelligence.

    This is a one-to-one structural preparation stage.

    It does NOT:
    - reparse the article body,
    - interpret numbers or measurements,
    - extract quantitative relations,
    - normalize units,
    - perform calculations,
    - infer quantitative relationships,
    - perform temporal reasoning,
    - perform new causal reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    intake = validate_quantitative_intelligence_intake_v1(
        certified_causal_result
    )

    if (
        intake.get(
            "status"
        )
        != "QUANTITATIVE_INTELLIGENCE_INTAKE_VALIDATED"
    ):
        raise QuantitativeIntelligenceError(
            "Canonical Quantitative Intelligence intake was not validated."
        )

    identity = dict(
        certified_causal_result.get(
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

    causal_units = list(
        certified_causal_result.get(
            "causal_claim_units"
        )
        or []
    )

    if not article_id:
        raise QuantitativeIntelligenceError(
            "Certified causal article_id is required."
        )

    quantitative_units = []
    quantitative_sections = []

    seen_quantitative_ids = set()
    seen_causal_ids = set()
    seen_statement_ids = set()
    seen_sentence_ids = set()

    previous_global_index = None

    units_by_section = {}
    section_metadata = {}

    for causal_unit in causal_units:
        if not isinstance(
            causal_unit,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every certified Causal Claim Unit must be a mapping."
            )

        causal_claim_unit_id = str(
            causal_unit.get(
                "causal_claim_unit_id"
            )
            or ""
        )

        statement_id = str(
            causal_unit.get(
                "statement_evidence_id"
            )
            or ""
        )

        sentence_id = str(
            causal_unit.get(
                "sentence_id"
            )
            or ""
        )

        section_id = str(
            causal_unit.get(
                "section_id"
            )
            or ""
        )

        if not causal_claim_unit_id:
            raise QuantitativeIntelligenceError(
                "Causal Claim Unit ID is required."
            )

        if not causal_claim_unit_id.startswith(
            "causal_claim_"
        ):
            raise QuantitativeIntelligenceError(
                "Unexpected Causal Claim Unit ID format."
            )

        if not statement_id:
            raise QuantitativeIntelligenceError(
                "statement_evidence_id is required."
            )

        if not sentence_id:
            raise QuantitativeIntelligenceError(
                "sentence_id is required."
            )

        if not section_id:
            raise QuantitativeIntelligenceError(
                "section_id is required."
            )

        if causal_claim_unit_id in seen_causal_ids:
            raise QuantitativeIntelligenceError(
                "Duplicate Causal Claim Unit ID."
            )

        if statement_id in seen_statement_ids:
            raise QuantitativeIntelligenceError(
                "Duplicate statement_evidence_id."
            )

        if sentence_id in seen_sentence_ids:
            raise QuantitativeIntelligenceError(
                "Duplicate sentence_id."
            )

        if (
            causal_unit.get(
                "article_id"
            )
            != article_id
        ):
            raise QuantitativeIntelligenceError(
                "Causal Claim Unit article identity mismatch."
            )

        global_index = causal_unit.get(
            "sentence_global_index"
        )

        article_position = causal_unit.get(
            "article_position"
        )

        if not isinstance(
            global_index,
            int,
        ):
            raise QuantitativeIntelligenceError(
                "sentence_global_index must be an integer."
            )

        if not isinstance(
            article_position,
            int,
        ):
            raise QuantitativeIntelligenceError(
                "article_position must be an integer."
            )

        if (
            previous_global_index is not None
            and global_index <= previous_global_index
        ):
            raise QuantitativeIntelligenceError(
                "Certified Causal Claim Units are not "
                "in canonical sentence order."
            )

        causal_state = dict(
            causal_unit.get(
                "causal_analysis_state"
            )
            or {}
        )

        required_complete_causal_stages = (
            "causal_signal_interpretation",
            "cause_effect_candidate_extraction",
            "entity_concept_grounding",
            "causal_relation_normalization",
            "cause_effect_orientation",
            "same_sentence_causal_validation",
            "cross_sentence_causal_validation",
            "causal_evidence_assessment",
            "duplicate_causal_resolution",
        )

        for stage_name in required_complete_causal_stages:
            if (
                causal_state.get(
                    stage_name
                )
                != "COMPLETE"
            ):
                raise QuantitativeIntelligenceError(
                    "Causal Claim Unit analysis is incomplete at "
                    + stage_name
                    + "."
                )

        upstream_boundaries = dict(
            causal_unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            upstream_boundaries.get(
                "quantitative_reasoning_performed"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Upstream Causal Claim Unit already contains quantitative reasoning."
            )

        if (
            upstream_boundaries.get(
                "truth_assessment_performed"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Upstream Causal Claim Unit already contains truth assessment."
            )

        if (
            upstream_boundaries.get(
                "external_authority_check_performed"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Upstream Causal Claim Unit already contains external-authority reasoning."
            )

        if (
            upstream_boundaries.get(
                "temporal_reasoning_performed"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Upstream Causal Claim Unit already contains temporal reasoning."
            )

        quantitative_claim_unit_id = (
            "quantitative_claim_"
            + causal_claim_unit_id[
                len("causal_claim_"):
            ]
        )

        if quantitative_claim_unit_id in seen_quantitative_ids:
            raise QuantitativeIntelligenceError(
                "Duplicate Quantitative Claim Unit ID."
            )

        quantitative_unit = {
            "quantitative_claim_unit_id":
                quantitative_claim_unit_id,

            "upstream_causal_claim_unit_id":
                causal_claim_unit_id,

            "upstream_relational_claim_unit_id":
                causal_unit.get(
                    "upstream_relational_claim_unit_id"
                ),

            "upstream_logical_claim_unit_id":
                causal_unit.get(
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
                causal_unit.get(
                    "section_evidence_unit_id"
                ),

            "section_index":
                causal_unit.get(
                    "section_index"
                ),

            "section_title":
                causal_unit.get(
                    "section_title"
                ),

            "heading_level":
                causal_unit.get(
                    "heading_level"
                ),

            "block_id":
                causal_unit.get(
                    "block_id"
                ),

            "paragraph_id":
                causal_unit.get(
                    "paragraph_id"
                ),

            "block_type":
                causal_unit.get(
                    "block_type"
                ),

            "block_index":
                causal_unit.get(
                    "block_index"
                ),

            "sentence_index":
                causal_unit.get(
                    "sentence_index"
                ),

            "sentence_global_index":
                global_index,

            "article_position":
                article_position,

            "claim_index_in_section":
                causal_unit.get(
                    "claim_index_in_section"
                ),

            "text":
                causal_unit.get(
                    "text"
                ),

            "word_count":
                causal_unit.get(
                    "word_count"
                ),

            "character_count":
                causal_unit.get(
                    "character_count"
                ),

            "statement_form":
                causal_unit.get(
                    "statement_form"
                ),

            "canonical_claim_candidate":
                causal_unit.get(
                    "canonical_claim_candidate"
                )
                is True,

            "evidence_context":
                dict(
                    causal_unit.get(
                        "evidence_context"
                    )
                    or {}
                ),

            "upstream_causal_analysis_state":
                causal_state,

            "upstream_causal_processing_boundaries":
                upstream_boundaries,

            "quantitative_analysis_state": {
                "numeric_measurement_signal_interpretation":
                    "PENDING",

                "quantitative_candidate_extraction":
                    "PENDING",

                "entity_concept_grounding":
                    "PENDING",

                "unit_measurement_normalization":
                    "PENDING",

                "quantity_role_comparison_orientation":
                    "PENDING",

                "same_sentence_quantitative_validation":
                    "PENDING",

                "cross_sentence_quantitative_validation":
                    "PENDING",

                "quantitative_evidence_assessment":
                    "PENDING",

                "duplicate_quantitative_resolution":
                    "PENDING",
            },

            "processing_boundaries": {
                "article_local_only":
                    True,

                "quantitative_claim_unit_prepared":
                    True,

                "article_body_reparsed":
                    False,

                "numeric_signal_interpretation_performed":
                    False,

                "quantitative_candidate_extraction_performed":
                    False,

                "unit_normalization_performed":
                    False,

                "derived_calculation_performed":
                    False,

                "quantitative_inference_performed":
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

        quantitative_units.append(
            quantitative_unit
        )

        units_by_section.setdefault(
            section_id,
            [],
        ).append(
            quantitative_unit
        )

        if section_id not in section_metadata:
            section_metadata[
                section_id
            ] = {
                "section_id":
                    section_id,

                "section_index":
                    causal_unit.get(
                        "section_index"
                    ),

                "section_title":
                    causal_unit.get(
                        "section_title"
                    ),

                "heading_level":
                    causal_unit.get(
                        "heading_level"
                    ),
            }

        seen_quantitative_ids.add(
            quantitative_claim_unit_id
        )

        seen_causal_ids.add(
            causal_claim_unit_id
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

    for unit in quantitative_units:
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

        quantitative_sections.append({
            **metadata,

            "upstream_causal_claim_count":
                len(
                    section_units
                ),

            "quantitative_claim_unit_count":
                len(
                    section_units
                ),

            "quantitative_claim_units":
                section_units,
        })

    if (
        len(
            quantitative_units
        )
        != len(
            causal_units
        )
    ):
        raise QuantitativeIntelligenceError(
            "Quantitative Claim Unit construction must remain "
            "one-to-one with Causal Claim Units."
        )

    return {
        "schema_version":
            "quantitative_claim_units_v1",

        "quantitative_intelligence_version":
            "quantitative_intelligence_v1",

        "phase":
            "4.6.9",

        "patch":
            "4.6.9C",

        "status":
            "QUANTITATIVE_CLAIM_UNITS_PREPARED",

        "article_identity":
            identity,

        "causal_claim_unit_count":
            len(
                causal_units
            ),

        "quantitative_claim_unit_count":
            len(
                quantitative_units
            ),

        "section_count":
            len(
                quantitative_sections
            ),

        "quantitative_sections":
            quantitative_sections,

        "quantitative_claim_units":
            quantitative_units,

        "construction_summary": {
            "source_causal_claim_unit_count":
                len(
                    causal_units
                ),

            "quantitative_claim_unit_count":
                len(
                    quantitative_units
                ),

            "one_to_one_causal_mapping":
                (
                    len(
                        quantitative_units
                    )
                    == len(
                        causal_units
                    )
                ),

            "canonical_order_preserved":
                True,

            "canonical_text_preserved":
                True,

            "evidence_context_preserved":
                True,

            "causal_context_preserved":
                True,

            "article_body_reparsed":
                False,

            "numeric_signals_interpreted":
                False,

            "quantitative_relations_inferred":
                False,

            "derived_calculation_performed":
                False,
        },

        "processing_boundaries": {
            "article_body_reparsed":
                False,

            "quantitative_claim_units_prepared":
                True,

            "numeric_signal_interpretation_performed":
                False,

            "quantitative_candidate_extraction_performed":
                False,

            "unit_normalization_performed":
                False,

            "derived_calculation_performed":
                False,

            "quantitative_inference_performed":
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
            "numeric_measurement_signal_interpretation",
    }



def interpret_numeric_measurement_signals_v1(
    quantitative_claim_units_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Interpret explicit article-local numeric and measurement signals.

    This stage identifies and classifies quantitative wording only.

    It does NOT:
    - extract final quantitative subject/value relationships,
    - normalize measurement units,
    - calculate derived values,
    - infer missing quantities,
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
        quantitative_claim_units_result,
        Mapping,
    ):
        raise QuantitativeIntelligenceError(
            "quantitative_claim_units_result must be a mapping."
        )

    if (
        quantitative_claim_units_result.get(
            "schema_version"
        )
        != "quantitative_claim_units_v1"
    ):
        raise QuantitativeIntelligenceError(
            "Stage D requires quantitative_claim_units_v1."
        )

    if (
        quantitative_claim_units_result.get(
            "status"
        )
        != "QUANTITATIVE_CLAIM_UNITS_PREPARED"
    ):
        raise QuantitativeIntelligenceError(
            "Quantitative Claim Units must be prepared before Stage D."
        )

    if (
        quantitative_claim_units_result.get(
            "phase"
        )
        != "4.6.9"
    ):
        raise QuantitativeIntelligenceError(
            "Stage D requires Phase 4.6.9 input."
        )

    if (
        quantitative_claim_units_result.get(
            "patch"
        )
        != "4.6.9C"
    ):
        raise QuantitativeIntelligenceError(
            "Stage D requires canonical 4.6.9C input."
        )

    if (
        quantitative_claim_units_result.get(
            "next_stage"
        )
        != "numeric_measurement_signal_interpretation"
    ):
        raise QuantitativeIntelligenceError(
            "Stage C must hand off to numeric_measurement_signal_interpretation."
        )

    if (
        quantitative_claim_units_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise QuantitativeIntelligenceError(
            "Quantitative Intelligence must remain transient."
        )

    number_token = (
        r"(?:"
        r"\d+\s+\d+/\d+"
        r"|"
        r"\d+/\d+"
        r"|"
        r"\d+(?:\.\d+)?"
        r")"
    )

    signal_specs = (
        (
            "PERCENTILE",
            "STATISTICAL_RANK",
            re.compile(
                r"\b\d+(?:st|nd|rd|th)\s+percentile\b",
                re.IGNORECASE,
            ),
        ),
        (
            "PERCENTAGE",
            "PROPORTION",
            re.compile(
                r"\b\d+(?:\.\d+)?\s*(?:%|percent)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "WEIGHT_MEASUREMENT",
            "MEASUREMENT",
            re.compile(
                r"\b"
                + number_token
                + r"\s*(?:pounds?|lbs?|ounces?|oz)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "LENGTH_HEIGHT_MEASUREMENT",
            "MEASUREMENT",
            re.compile(
                r"\b"
                + number_token
                + r"\s*(?:inches?|feet|ft|centimeters?|cm)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "AGE_DURATION",
            "TEMPORAL_QUANTITY",
            re.compile(
                r"\b"
                + number_token
                + r"\s*(?:days?|weeks?|months?|years?)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "NUMERIC_RANGE",
            "RANGE",
            re.compile(
                r"(?:"
                r"\bbetween\s+"
                + number_token
                + r"\s+and\s+"
                + number_token
                + r"\b"
                r"|"
                r"\b"
                + number_token
                + r"\s*(?:-|\u2013|to)\s*"
                + number_token
                + r"\b"
                r")",
                re.IGNORECASE,
            ),
        ),
        (
            "MEASUREMENT_RATE",
            "RATE",
            re.compile(
                r"\b"
                + number_token
                + r"\s*"
                + r"(?:pounds?|lbs?|ounces?|oz|inches?|feet|ft|centimeters?|cm)"
                + r"\s+per\s+"
                + r"(?:day|week|month|year)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "MULTIPLICATIVE_CHANGE",
            "MULTIPLICATIVE_RELATION",
            re.compile(
                r"\b(?:double|doubles|doubled|doubling|"
                r"triple|triples|tripled|tripling)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "INCREASE",
            "CHANGE_DIRECTION",
            re.compile(
                r"\b(?:increase|increases|increased|increasing|"
                r"gain|gains|gained|gaining|"
                r"rise|rises|rose|rising|higher)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "DECREASE",
            "CHANGE_DIRECTION",
            re.compile(
                r"\b(?:decrease|decreases|decreased|decreasing|"
                r"drop|drops|dropped|dropping|"
                r"lose|loses|lost|losing|lower)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "AVERAGE_REFERENCE",
            "STATISTICAL_REFERENCE",
            re.compile(
                r"\b(?:average|averages|mean|typically|usual|usually)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "COMPARISON",
            "COMPARATIVE_RELATION",
            re.compile(
                r"\b(?:more\s+than|less\s+than|greater\s+than|"
                r"fewer\s+than|at\s+least|at\s+most|"
                r"between|above|below)\b",
                re.IGNORECASE,
            ),
        ),
    )

    calendar_year_pattern = re.compile(
        r"\b(?:18|19|20)\d{2}\b"
    )

    generic_number_pattern = re.compile(
        r"\b\d+(?:\.\d+)?\b"
    )

    source_units = list(
        quantitative_claim_units_result.get(
            "quantitative_claim_units"
        )
        or []
    )

    interpreted_units = []
    interpreted_by_id = {}

    total_signal_count = 0
    units_with_signals = 0
    excluded_temporal_metadata_count = 0
    generic_numeric_signal_count = 0

    signal_type_counts = {}
    semantic_class_counts = {}

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every Quantitative Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "quantitative_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "numeric_measurement_signal_interpretation"
            )
            != "PENDING"
        ):
            raise QuantitativeIntelligenceError(
                "Numeric/measurement signal interpretation must be PENDING before Stage D."
            )

        if (
            state.get(
                "quantitative_candidate_extraction"
            )
            != "PENDING"
        ):
            raise QuantitativeIntelligenceError(
                "Quantitative candidate extraction must remain PENDING during Stage D."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "quantitative_claim_unit_prepared"
            )
            is not True
        ):
            raise QuantitativeIntelligenceError(
                "Quantitative Claim Unit preparation boundary is incomplete."
            )

        required_false_boundaries = (
            "numeric_signal_interpretation_performed",
            "quantitative_candidate_extraction_performed",
            "unit_normalization_performed",
            "derived_calculation_performed",
            "quantitative_inference_performed",
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
                raise QuantitativeIntelligenceError(
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

        calendar_year_spans = []

        for match in calendar_year_pattern.finditer(
            source_text
        ):
            calendar_year_spans.append(
                (
                    match.start(),
                    match.end(),
                )
            )

            exclusions.append({
                "signal_type":
                    "CALENDAR_YEAR",

                "classification":
                    "TEMPORAL_METADATA_DEFERRED",

                "matched_text":
                    match.group(0),

                "character_start":
                    match.start(),

                "character_end":
                    match.end(),

                "candidate_eligible":
                    False,

                "temporal_reasoning_performed":
                    False,
            })

            excluded_temporal_metadata_count += 1

        for (
            signal_type,
            semantic_class,
            pattern,
        ) in signal_specs:
            matches = list(
                pattern.finditer(
                    source_text
                )
            )

            for match in matches:
                signal = {
                    "signal_type":
                        signal_type,

                    "quantitative_semantic_class":
                        semantic_class,

                    "matched_text":
                        match.group(0),

                    "character_start":
                        match.start(),

                    "character_end":
                        match.end(),

                    "article_asserted_signal":
                        True,

                    "quantitative_candidate_extracted":
                        False,

                    "unit_normalized":
                        False,

                    "derived_calculation_performed":
                        False,

                    "quantitative_inference_performed":
                        False,

                    "temporal_reasoning_performed":
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

        for match in generic_number_pattern.finditer(
            source_text
        ):
            span = (
                match.start(),
                match.end(),
            )

            overlaps_specialized_signal = any(
                span[0] < occupied_end
                and span[1] > occupied_start
                for (
                    occupied_start,
                    occupied_end,
                ) in occupied_spans
            )

            overlaps_calendar_year = any(
                span[0] < year_end
                and span[1] > year_start
                for (
                    year_start,
                    year_end,
                ) in calendar_year_spans
            )

            if (
                overlaps_specialized_signal
                or overlaps_calendar_year
            ):
                continue

            signals.append({
                "signal_type":
                    "GENERIC_NUMBER",

                "quantitative_semantic_class":
                    "UNCLASSIFIED_NUMERIC_TOKEN",

                "matched_text":
                    match.group(0),

                "character_start":
                    match.start(),

                "character_end":
                    match.end(),

                "article_asserted_signal":
                    True,

                "quantitative_candidate_extracted":
                    False,

                "unit_normalized":
                    False,

                "derived_calculation_performed":
                    False,

                "quantitative_inference_performed":
                    False,

                "temporal_reasoning_performed":
                    False,

                "truth_verified":
                    False,
            })

            generic_numeric_signal_count += 1

            signal_type_counts[
                "GENERIC_NUMBER"
            ] = (
                signal_type_counts.get(
                    "GENERIC_NUMBER",
                    0,
                )
                + 1
            )

            semantic_class_counts[
                "UNCLASSIFIED_NUMERIC_TOKEN"
            ] = (
                semantic_class_counts.get(
                    "UNCLASSIFIED_NUMERIC_TOKEN",
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
            "numeric_measurement_signal_interpretation"
        ] = "COMPLETE"

        interpreted_boundaries = dict(
            boundaries
        )

        interpreted_boundaries[
            "numeric_signal_interpretation_performed"
        ] = True

        interpreted_boundaries[
            "quantitative_candidate_extraction_performed"
        ] = False

        interpreted_boundaries[
            "unit_normalization_performed"
        ] = False

        interpreted_boundaries[
            "derived_calculation_performed"
        ] = False

        interpreted_boundaries[
            "quantitative_inference_performed"
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
            "quantitative_signals":
                signals,

            "quantitative_signal_exclusions":
                exclusions,

            "quantitative_signal_count":
                unit_total,

            "has_quantitative_signal":
                unit_total > 0,

            "quantitative_signal_interpretation_scope":
                "ARTICLE_LOCAL_LEXICAL_AND_MEASUREMENT_SIGNAL_ONLY",

            "quantitative_analysis_state":
                interpreted_state,

            "processing_boundaries":
                interpreted_boundaries,
        })

        interpreted_units.append(
            interpreted_unit
        )

        interpreted_by_id[
            interpreted_unit.get(
                "quantitative_claim_unit_id"
            )
        ] = interpreted_unit

    interpreted_sections = []

    for section in (
        quantitative_claim_units_result.get(
            "quantitative_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every quantitative section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "quantitative_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "quantitative_claim_unit_id"
            )

            resolved_unit = interpreted_by_id.get(
                unit_id
            )

            if resolved_unit is None:
                raise QuantitativeIntelligenceError(
                    "Quantitative section references an unknown claim unit."
                )

            section_units.append(
                resolved_unit
            )

        interpreted_sections.append({
            **dict(
                section
            ),

            "quantitative_claim_units":
                section_units,

            "quantitative_signal_unit_count":
                sum(
                    1
                    for unit in section_units
                    if unit.get(
                        "has_quantitative_signal"
                    )
                    is True
                ),

            "quantitative_signal_count":
                sum(
                    int(
                        unit.get(
                            "quantitative_signal_count"
                        )
                        or 0
                    )
                    for unit in section_units
                ),
        })

    result = dict(
        quantitative_claim_units_result
    )

    result_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    result_boundaries[
        "numeric_signal_interpretation_performed"
    ] = True

    result_boundaries[
        "quantitative_candidate_extraction_performed"
    ] = False

    result_boundaries[
        "unit_normalization_performed"
    ] = False

    result_boundaries[
        "derived_calculation_performed"
    ] = False

    result_boundaries[
        "quantitative_inference_performed"
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
            "quantitative_signal_interpretation_v1",

        "patch":
            "4.6.9D",

        "status":
            "QUANTITATIVE_SIGNAL_INTERPRETATION_COMPLETE",

        "quantitative_sections":
            interpreted_sections,

        "quantitative_claim_units":
            interpreted_units,

        "quantitative_signal_summary": {
            "claim_unit_count":
                len(
                    interpreted_units
                ),

            "units_with_quantitative_signals":
                units_with_signals,

            "total_quantitative_signal_count":
                total_signal_count,

            "generic_numeric_signal_count":
                generic_numeric_signal_count,

            "excluded_temporal_metadata_count":
                excluded_temporal_metadata_count,

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

            "zero_signal_units_allowed":
                True,

            "quantitative_candidates_extracted":
                False,

            "units_normalized":
                False,

            "derived_calculation_performed":
                False,

            "quantitative_inference_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "truth_assessment_performed":
                False,
        },

        "processing_boundaries":
            result_boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "quantitative_candidate_extraction",
    })

    return result



def extract_quantitative_candidates_v1(
    quantitative_signal_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Extract conservative article-local quantitative candidates from
    interpreted numeric and measurement signals.

    This stage constructs quantitative candidate objects only.

    It does NOT:
    - ground candidate subjects to entities or concepts,
    - normalize units or measurements,
    - calculate derived values,
    - infer missing quantities,
    - resolve final quantitative roles or comparisons,
    - perform full temporal reasoning,
    - perform new causal reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    import hashlib

    if not isinstance(
        quantitative_signal_result,
        Mapping,
    ):
        raise QuantitativeIntelligenceError(
            "quantitative_signal_result must be a mapping."
        )

    if (
        quantitative_signal_result.get(
            "schema_version"
        )
        != "quantitative_signal_interpretation_v1"
    ):
        raise QuantitativeIntelligenceError(
            "Stage E requires quantitative_signal_interpretation_v1."
        )

    if (
        quantitative_signal_result.get(
            "status"
        )
        != "QUANTITATIVE_SIGNAL_INTERPRETATION_COMPLETE"
    ):
        raise QuantitativeIntelligenceError(
            "Quantitative signal interpretation must be complete."
        )

    if (
        quantitative_signal_result.get(
            "phase"
        )
        != "4.6.9"
    ):
        raise QuantitativeIntelligenceError(
            "Stage E requires Phase 4.6.9 input."
        )

    if (
        quantitative_signal_result.get(
            "patch"
        )
        != "4.6.9D"
    ):
        raise QuantitativeIntelligenceError(
            "Stage E requires canonical 4.6.9D input."
        )

    if (
        quantitative_signal_result.get(
            "next_stage"
        )
        != "quantitative_candidate_extraction"
    ):
        raise QuantitativeIntelligenceError(
            "Stage D must hand off to quantitative_candidate_extraction."
        )

    if (
        quantitative_signal_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise QuantitativeIntelligenceError(
            "Quantitative Intelligence must remain transient."
        )

    primary_signal_types = {
        "PERCENTILE",
        "PERCENTAGE",
        "WEIGHT_MEASUREMENT",
        "LENGTH_HEIGHT_MEASUREMENT",
        "AGE_DURATION",
        "NUMERIC_RANGE",
        "MEASUREMENT_RATE",
        "MULTIPLICATIVE_CHANGE",
        "GENERIC_NUMBER",
    }

    contextual_signal_types = {
        "INCREASE",
        "DECREASE",
        "AVERAGE_REFERENCE",
        "COMPARISON",
    }

    candidate_form_by_signal = {
        "PERCENTILE":
            "PERCENTILE_VALUE",

        "PERCENTAGE":
            "PERCENTAGE_VALUE",

        "WEIGHT_MEASUREMENT":
            "WEIGHT_MEASUREMENT",

        "LENGTH_HEIGHT_MEASUREMENT":
            "LENGTH_HEIGHT_MEASUREMENT",

        "AGE_DURATION":
            "TEMPORAL_QUANTITY",

        "NUMERIC_RANGE":
            "NUMERIC_RANGE",

        "MEASUREMENT_RATE":
            "MEASUREMENT_RATE",

        "MULTIPLICATIVE_CHANGE":
            "MULTIPLICATIVE_CHANGE",

        "GENERIC_NUMBER":
            "UNCLASSIFIED_NUMERIC_VALUE",
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
            "quantitative_candidate_"
            + hashlib.sha256(
                raw.encode(
                    "utf-8"
                )
            ).hexdigest()[:24]
        )

    source_units = list(
        quantitative_signal_result.get(
            "quantitative_claim_units"
        )
        or []
    )

    extracted_units = []
    extracted_by_id = {}
    all_candidates = []

    units_with_candidates = 0
    rejected_signal_count = 0
    contextual_signal_count = 0

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every Stage-D Quantitative Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "quantitative_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "numeric_measurement_signal_interpretation"
            )
            != "COMPLETE"
        ):
            raise QuantitativeIntelligenceError(
                "Numeric/measurement signal interpretation must be COMPLETE before Stage E."
            )

        if (
            state.get(
                "quantitative_candidate_extraction"
            )
            != "PENDING"
        ):
            raise QuantitativeIntelligenceError(
                "Quantitative candidate extraction must be PENDING before Stage E."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "numeric_signal_interpretation_performed"
            )
            is not True
        ):
            raise QuantitativeIntelligenceError(
                "Stage-D quantitative interpretation boundary is incomplete."
            )

        required_false_boundaries = (
            "quantitative_candidate_extraction_performed",
            "unit_normalization_performed",
            "derived_calculation_performed",
            "quantitative_inference_performed",
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
                raise QuantitativeIntelligenceError(
                    boundary_name
                    + " must be False before Stage E."
                )

        unit_id = str(
            unit.get(
                "quantitative_claim_unit_id"
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
            raise QuantitativeIntelligenceError(
                "Quantitative Claim Unit ID is required."
            )

        signals = list(
            unit.get(
                "quantitative_signals"
            )
            or []
        )

        contextual_signals = []

        for signal in signals:
            if not isinstance(
                signal,
                Mapping,
            ):
                raise QuantitativeIntelligenceError(
                    "Every quantitative signal must be a mapping."
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
                raise QuantitativeIntelligenceError(
                    "Every quantitative signal must be a mapping."
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
                raise QuantitativeIntelligenceError(
                    "Quantitative signal character span is invalid."
                )

            if (
                sentence_text[
                    start:end
                ]
                != matched_text
            ):
                raise QuantitativeIntelligenceError(
                    "Quantitative signal text does not match its source span."
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
                        "CONTEXTUAL_SIGNAL_REQUIRES_QUANTITATIVE_ANCHOR",

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
                        "UNSUPPORTED_QUANTITATIVE_PRIMARY_SIGNAL",

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
                        "EMPTY_QUANTITATIVE_SIGNAL_TEXT",

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

            candidate = {
                "quantitative_candidate_id":
                    candidate_id,

                "quantitative_claim_unit_id":
                    unit_id,

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

                "quantitative_semantic_class":
                    signal.get(
                        "quantitative_semantic_class"
                    ),

                "signal_matched_text":
                    matched_text,

                "signal_character_start":
                    start,

                "signal_character_end":
                    end,

                "candidate_quantitative_form":
                    candidate_form_by_signal[
                        signal_type
                    ],

                "contextual_quantitative_signals":
                    [
                        dict(
                            item
                        )
                        for item in contextual_signals
                    ],

                "contextual_quantitative_signal_count":
                    len(
                        contextual_signals
                    ),

                "article_asserted_candidate":
                    True,

                "same_sentence_candidate":
                    True,

                "entity_concept_grounded":
                    False,

                "unit_measurement_normalized":
                    False,

                "quantity_role_orientation_resolved":
                    False,

                "same_sentence_quantitative_validated":
                    False,

                "cross_sentence_quantitative_validated":
                    False,

                "quantitative_evidence_assessed":
                    False,

                "duplicate_resolution_performed":
                    False,

                "derived_calculation_performed":
                    False,

                "quantitative_inference_performed":
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

        if unit_candidates:
            units_with_candidates += 1

        extracted_state = dict(
            state
        )

        extracted_state[
            "quantitative_candidate_extraction"
        ] = "COMPLETE"

        extracted_boundaries = dict(
            boundaries
        )

        extracted_boundaries[
            "quantitative_candidate_extraction_performed"
        ] = True

        extracted_boundaries[
            "unit_normalization_performed"
        ] = False

        extracted_boundaries[
            "derived_calculation_performed"
        ] = False

        extracted_boundaries[
            "quantitative_inference_performed"
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
            "quantitative_candidates":
                unit_candidates,

            "quantitative_candidate_count":
                len(
                    unit_candidates
                ),

            "quantitative_extraction_rejections":
                unit_rejections,

            "quantitative_extraction_rejection_count":
                len(
                    unit_rejections
                ),

            "quantitative_analysis_state":
                extracted_state,

            "processing_boundaries":
                extracted_boundaries,
        })

        extracted_units.append(
            extracted_unit
        )

        extracted_by_id[
            unit_id
        ] = extracted_unit

    extracted_sections = []

    for section in (
        quantitative_signal_result.get(
            "quantitative_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every quantitative section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "quantitative_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "quantitative_claim_unit_id"
            )

            resolved_unit = extracted_by_id.get(
                unit_id
            )

            if resolved_unit is None:
                raise QuantitativeIntelligenceError(
                    "Quantitative section references an unknown claim unit."
                )

            section_units.append(
                resolved_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "quantitative_candidates"
                )
                or []
            )
        ]

        extracted_sections.append({
            **dict(
                section
            ),

            "quantitative_claim_units":
                section_units,

            "quantitative_candidate_count":
                len(
                    section_candidates
                ),

            "quantitative_candidates":
                section_candidates,
        })

    result = dict(
        quantitative_signal_result
    )

    result_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    result_boundaries[
        "quantitative_candidate_extraction_performed"
    ] = True

    result_boundaries[
        "unit_normalization_performed"
    ] = False

    result_boundaries[
        "derived_calculation_performed"
    ] = False

    result_boundaries[
        "quantitative_inference_performed"
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
            "quantitative_candidates_v1",

        "patch":
            "4.6.9E",

        "status":
            "QUANTITATIVE_CANDIDATE_EXTRACTION_COMPLETE",

        "quantitative_sections":
            extracted_sections,

        "quantitative_claim_units":
            extracted_units,

        "quantitative_candidates":
            all_candidates,

        "quantitative_extraction_summary": {
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

            "unit_measurement_normalization_performed":
                False,

            "quantity_role_orientation_performed":
                False,

            "derived_calculation_performed":
                False,

            "quantitative_inference_performed":
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



def ground_quantitative_candidates_v1(
    quantitative_candidates_result: Mapping[str, Any],
    entity_concept_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Ground quantitative candidates against canonical article-local
    Phase 4.6.2 Entity & Concept Intelligence objects.

    This stage identifies semantic objects present in each candidate's
    source sentence.

    It does NOT:
    - assign the final measured subject or quantitative role,
    - create new entities or concepts,
    - perform fuzzy semantic similarity,
    - normalize units or measurements,
    - perform derived calculations,
    - infer missing quantities,
    - resolve comparison orientation,
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
        quantitative_candidates_result,
        Mapping,
    ):
        raise QuantitativeIntelligenceError(
            "quantitative_candidates_result must be a mapping."
        )

    if not isinstance(
        entity_concept_result,
        Mapping,
    ):
        raise QuantitativeIntelligenceError(
            "entity_concept_result must be a mapping."
        )

    if (
        quantitative_candidates_result.get(
            "schema_version"
        )
        != "quantitative_candidates_v1"
    ):
        raise QuantitativeIntelligenceError(
            "Stage F requires quantitative_candidates_v1."
        )

    if (
        quantitative_candidates_result.get(
            "status"
        )
        != "QUANTITATIVE_CANDIDATE_EXTRACTION_COMPLETE"
    ):
        raise QuantitativeIntelligenceError(
            "Quantitative candidate extraction must be complete."
        )

    if (
        quantitative_candidates_result.get(
            "phase"
        )
        != "4.6.9"
    ):
        raise QuantitativeIntelligenceError(
            "Stage F requires Phase 4.6.9 input."
        )

    if (
        quantitative_candidates_result.get(
            "patch"
        )
        != "4.6.9E"
    ):
        raise QuantitativeIntelligenceError(
            "Stage F requires canonical 4.6.9E input."
        )

    if (
        quantitative_candidates_result.get(
            "next_stage"
        )
        != "entity_concept_grounding"
    ):
        raise QuantitativeIntelligenceError(
            "Stage E must hand off to entity_concept_grounding."
        )

    if (
        quantitative_candidates_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise QuantitativeIntelligenceError(
            "Quantitative Intelligence must remain transient."
        )

    if (
        entity_concept_result.get(
            "schema_version"
        )
        != "entity_concept_intelligence_result_v1"
    ):
        raise QuantitativeIntelligenceError(
            "Stage F requires canonical entity_concept_intelligence_result_v1."
        )

    if (
        entity_concept_result.get(
            "status"
        )
        != "ENTITY_CONCEPT_INTELLIGENCE_COMPLETE"
    ):
        raise QuantitativeIntelligenceError(
            "Entity & Concept Intelligence must be complete."
        )

    if (
        entity_concept_result.get(
            "phase"
        )
        != "4.6.2"
    ):
        raise QuantitativeIntelligenceError(
            "Stage F requires Phase 4.6.2 Entity & Concept Intelligence."
        )

    semantic_objects = list(
        entity_concept_result.get(
            "semantic_objects"
        )
        or []
    )

    if not semantic_objects:
        raise QuantitativeIntelligenceError(
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
        raise QuantitativeIntelligenceError(
            "Entity & Concept Intelligence must be article-local."
        )

    if (
        entity_boundaries.get(
            "semantic_memory_write_performed"
        )
        is not False
    ):
        raise QuantitativeIntelligenceError(
            "Unexpected Semantic Memory write detected upstream."
        )

    if (
        entity_boundaries.get(
            "reasoning_performed"
        )
        is not False
    ):
        raise QuantitativeIntelligenceError(
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
        quantitative_candidates_result.get(
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

    prepared_objects = []

    for semantic_object in semantic_objects:
        if not isinstance(
            semantic_object,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
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
            raise QuantitativeIntelligenceError(
                "Semantic object is missing canonical_text."
            )

        if semantic_kind not in {
            "entity",
            "concept",
        }:
            raise QuantitativeIntelligenceError(
                "Semantic object has invalid semantic_kind."
            )

        if (
            not isinstance(
                confidence,
                (int, float),
            )
            or confidence < 0.0
            or confidence > 1.0
        ):
            raise QuantitativeIntelligenceError(
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

                    "final_quantitative_role_assigned":
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
        quantitative_candidates_result.get(
            "quantitative_candidates"
        )
        or []
    )

    grounded_candidates = []

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every quantitative candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "quantitative_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise QuantitativeIntelligenceError(
                "Quantitative candidate ID is required."
            )

        if (
            candidate.get(
                "entity_concept_grounded"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
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

            "final_quantitative_referent_selected":
                False,

            "unit_measurement_normalized":
                False,

            "quantity_role_orientation_resolved":
                False,

            "same_sentence_quantitative_validated":
                False,

            "cross_sentence_quantitative_validated":
                False,

            "quantitative_evidence_assessed":
                False,

            "duplicate_resolution_performed":
                False,

            "derived_calculation_performed":
                False,

            "quantitative_inference_performed":
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
            "quantitative_candidate_id"
        ):
            candidate
        for candidate in grounded_candidates
    }

    grounded_units = []

    for unit in (
        quantitative_candidates_result.get(
            "quantitative_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every Quantitative Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "quantitative_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "quantitative_candidate_extraction"
            )
            != "COMPLETE"
        ):
            raise QuantitativeIntelligenceError(
                "Quantitative candidate extraction must be COMPLETE before grounding."
            )

        if (
            state.get(
                "entity_concept_grounding"
            )
            != "PENDING"
        ):
            raise QuantitativeIntelligenceError(
                "Entity/concept grounding must be PENDING."
            )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "quantitative_candidates"
            )
            or []
        ):
            candidate_id = old_candidate.get(
                "quantitative_candidate_id"
            )

            grounded = grounded_by_id.get(
                candidate_id
            )

            if grounded is None:
                raise QuantitativeIntelligenceError(
                    "Quantitative candidate/unit identity mismatch."
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
                "quantitative_candidate_extraction_performed"
            )
            is not True
        ):
            raise QuantitativeIntelligenceError(
                "Stage-E extraction boundary is incomplete."
            )

        required_false_boundaries = (
            "unit_normalization_performed",
            "derived_calculation_performed",
            "quantitative_inference_performed",
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
                raise QuantitativeIntelligenceError(
                    boundary_name
                    + " must be False before Stage F."
                )

        updated_boundaries[
            "entity_concept_grounding_performed"
        ] = True

        updated_boundaries[
            "unit_normalization_performed"
        ] = False

        updated_boundaries[
            "derived_calculation_performed"
        ] = False

        updated_boundaries[
            "quantitative_inference_performed"
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
            "quantitative_candidates":
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

            "quantitative_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        grounded_units.append(
            updated_unit
        )

    grounded_units_by_id = {
        unit.get(
            "quantitative_claim_unit_id"
        ):
            unit
        for unit in grounded_units
    }

    grounded_sections = []

    for section in (
        quantitative_candidates_result.get(
            "quantitative_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every quantitative section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "quantitative_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "quantitative_claim_unit_id"
            )

            grounded_unit = (
                grounded_units_by_id.get(
                    unit_id
                )
            )

            if grounded_unit is None:
                raise QuantitativeIntelligenceError(
                    "Quantitative section/unit grounding mismatch."
                )

            section_units.append(
                grounded_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "quantitative_candidates"
                )
                or []
            )
        ]

        grounded_sections.append({
            **dict(
                section
            ),

            "quantitative_claim_units":
                section_units,

            "quantitative_candidates":
                section_candidates,

            "quantitative_candidate_count":
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
        quantitative_candidates_result
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
        "unit_normalization_performed"
    ] = False

    boundaries[
        "derived_calculation_performed"
    ] = False

    boundaries[
        "quantitative_inference_performed"
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
            "quantitative_entity_concept_grounding_v1",

        "patch":
            "4.6.9F",

        "status":
            "QUANTITATIVE_ENTITY_CONCEPT_GROUNDING_COMPLETE",

        "quantitative_sections":
            grounded_sections,

        "quantitative_claim_units":
            grounded_units,

        "quantitative_candidates":
            grounded_candidates,

        "entity_concept_grounding_summary": {
            "semantic_object_count":
                len(
                    semantic_objects
                ),

            "quantitative_candidate_count":
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

            "final_quantitative_referent_selection_performed":
                False,

            "unit_measurement_normalization_performed":
                False,

            "quantity_role_orientation_performed":
                False,

            "derived_calculation_performed":
                False,

            "quantitative_inference_performed":
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
            "unit_measurement_normalization",
    })

    return result



def normalize_quantitative_units_v1(
    entity_concept_grounding_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Normalize article-expressed quantitative values, units, ranges,
    rates, percentages, percentiles, durations, and multiplicative
    forms into canonical quantitative representations.

    This stage normalizes only what is explicitly licensed by the
    candidate signal text.

    It does NOT:
    - derive new quantities,
    - calculate unstated rates,
    - convert measurements into another unit system,
    - select the final quantitative referent,
    - resolve quantity/comparison orientation,
    - perform same-sentence validation,
    - perform cross-sentence validation,
    - perform quantitative inference,
    - perform full temporal reasoning,
    - perform new causal reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    import re
    from fractions import Fraction

    if not isinstance(
        entity_concept_grounding_result,
        Mapping,
    ):
        raise QuantitativeIntelligenceError(
            "entity_concept_grounding_result must be a mapping."
        )

    if (
        entity_concept_grounding_result.get(
            "schema_version"
        )
        != "quantitative_entity_concept_grounding_v1"
    ):
        raise QuantitativeIntelligenceError(
            "Stage G requires quantitative_entity_concept_grounding_v1."
        )

    if (
        entity_concept_grounding_result.get(
            "status"
        )
        != "QUANTITATIVE_ENTITY_CONCEPT_GROUNDING_COMPLETE"
    ):
        raise QuantitativeIntelligenceError(
            "Entity/concept grounding must be complete before quantitative normalization."
        )

    if (
        entity_concept_grounding_result.get(
            "phase"
        )
        != "4.6.9"
    ):
        raise QuantitativeIntelligenceError(
            "Stage G requires Phase 4.6.9 input."
        )

    if (
        entity_concept_grounding_result.get(
            "patch"
        )
        != "4.6.9F"
    ):
        raise QuantitativeIntelligenceError(
            "Stage G requires canonical 4.6.9F input."
        )

    if (
        entity_concept_grounding_result.get(
            "next_stage"
        )
        != "unit_measurement_normalization"
    ):
        raise QuantitativeIntelligenceError(
            "Stage F must hand off to unit_measurement_normalization."
        )

    if (
        entity_concept_grounding_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise QuantitativeIntelligenceError(
            "Quantitative Intelligence must remain transient."
        )

    unit_registry = {
        "pound": {
            "family": "MASS_WEIGHT",
            "symbol": "lb",
            "aliases": {
                "pound",
                "pounds",
                "lb",
                "lbs",
            },
        },

        "ounce": {
            "family": "MASS_WEIGHT",
            "symbol": "oz",
            "aliases": {
                "ounce",
                "ounces",
                "oz",
            },
        },

        "inch": {
            "family": "LENGTH_DISTANCE",
            "symbol": "in",
            "aliases": {
                "inch",
                "inches",
                "in",
            },
        },

        "foot": {
            "family": "LENGTH_DISTANCE",
            "symbol": "ft",
            "aliases": {
                "foot",
                "feet",
                "ft",
            },
        },

        "centimeter": {
            "family": "LENGTH_DISTANCE",
            "symbol": "cm",
            "aliases": {
                "centimeter",
                "centimeters",
                "centimetre",
                "centimetres",
                "cm",
            },
        },

        "millimeter": {
            "family": "LENGTH_DISTANCE",
            "symbol": "mm",
            "aliases": {
                "millimeter",
                "millimeters",
                "millimetre",
                "millimetres",
                "mm",
            },
        },

        "meter": {
            "family": "LENGTH_DISTANCE",
            "symbol": "m",
            "aliases": {
                "meter",
                "meters",
                "metre",
                "metres",
            },
        },

        "day": {
            "family": "TIME_DURATION",
            "symbol": "day",
            "aliases": {
                "day",
                "days",
            },
        },

        "week": {
            "family": "TIME_DURATION",
            "symbol": "week",
            "aliases": {
                "week",
                "weeks",
            },
        },

        "month": {
            "family": "TIME_DURATION",
            "symbol": "month",
            "aliases": {
                "month",
                "months",
            },
        },

        "year": {
            "family": "TIME_DURATION",
            "symbol": "year",
            "aliases": {
                "year",
                "years",
            },
        },
    }

    alias_registry = {}

    for canonical_unit, spec in unit_registry.items():
        for alias in spec[
            "aliases"
        ]:
            normalized_alias = str(
                alias
            ).lower().strip()

            if normalized_alias in alias_registry:
                raise QuantitativeIntelligenceError(
                    "Duplicate unit alias detected: "
                    + normalized_alias
                )

            alias_registry[
                normalized_alias
            ] = canonical_unit

    multiplicative_registry = {
        "double": 2.0,
        "doubles": 2.0,
        "doubled": 2.0,
        "twice": 2.0,
        "triple": 3.0,
        "triples": 3.0,
        "tripled": 3.0,
    }

    def parse_number(
        value: str,
    ):
        raw = str(
            value
            or ""
        ).strip()

        if not raw:
            return None

        raw = raw.replace(
            ",",
            "",
        )

        mixed_match = re.fullmatch(
            r"(?P<whole>\d+)\s+"
            r"(?P<num>\d+)\s*/\s*"
            r"(?P<den>\d+)",
            raw,
        )

        if mixed_match:
            whole = int(
                mixed_match.group(
                    "whole"
                )
            )

            numerator = int(
                mixed_match.group(
                    "num"
                )
            )

            denominator = int(
                mixed_match.group(
                    "den"
                )
            )

            if denominator == 0:
                return None

            return float(
                whole
                + Fraction(
                    numerator,
                    denominator,
                )
            )

        fraction_match = re.fullmatch(
            r"(?P<num>\d+)\s*/\s*(?P<den>\d+)",
            raw,
        )

        if fraction_match:
            numerator = int(
                fraction_match.group(
                    "num"
                )
            )

            denominator = int(
                fraction_match.group(
                    "den"
                )
            )

            if denominator == 0:
                return None

            return float(
                Fraction(
                    numerator,
                    denominator,
                )
            )

        try:
            numeric = float(
                raw
            )
        except ValueError:
            return None

        if numeric.is_integer():
            return int(
                numeric
            )

        return numeric

    def extract_leading_number(
        text_value: str,
    ):
        match = re.search(
            r"\b("
            r"\d+\s+\d+\s*/\s*\d+"
            r"|"
            r"\d+\s*/\s*\d+"
            r"|"
            r"\d+(?:\.\d+)?"
            r")\b",
            str(
                text_value
                or ""
            ),
        )

        if match is None:
            return None

        return parse_number(
            match.group(
                1
            )
        )

    def resolve_unit(
        text_value: str,
    ):
        lowered = str(
            text_value
            or ""
        ).lower()

        tokens = re.findall(
            r"[a-z]+",
            lowered,
        )

        for token in tokens:
            canonical = alias_registry.get(
                token
            )

            if canonical is not None:
                spec = unit_registry[
                    canonical
                ]

                return {
                    "canonical_unit":
                        canonical,

                    "unit_symbol":
                        spec[
                            "symbol"
                        ],

                    "measurement_family":
                        spec[
                            "family"
                        ],

                    "matched_unit_alias":
                        token,
                }

        return {
            "canonical_unit":
                None,

            "unit_symbol":
                None,

            "measurement_family":
                None,

            "matched_unit_alias":
                None,
        }

    def normalize_candidate(
        candidate: Mapping[str, Any],
    ) -> dict[str, Any]:
        candidate_id = str(
            candidate.get(
                "quantitative_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise QuantitativeIntelligenceError(
                "Quantitative candidate ID is required."
            )

        if (
            candidate.get(
                "unit_measurement_normalized"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Candidate must not already be unit/measurement normalized."
            )

        signal_type = str(
            candidate.get(
                "signal_type"
            )
            or ""
        )

        matched_text = str(
            candidate.get(
                "signal_matched_text"
            )
            or ""
        ).strip()

        if not signal_type:
            raise QuantitativeIntelligenceError(
                "Quantitative candidate signal_type is required."
            )

        if not matched_text:
            raise QuantitativeIntelligenceError(
                "Quantitative candidate signal text is required."
            )

        normalized = dict(
            candidate
        )

        payload = {
            "normalization_status":
                "UNSUPPORTED",

            "raw_quantitative_text":
                matched_text,

            "normalized_value":
                None,

            "normalized_values":
                [],

            "canonical_unit":
                None,

            "unit_symbol":
                None,

            "measurement_family":
                None,

            "rate_denominator_unit":
                None,

            "rate_denominator_symbol":
                None,

            "quantitative_scale":
                None,

            "multiplicative_factor":
                None,

            "normalization_reason":
                None,
        }

        if signal_type == "PERCENTILE":
            percentile_match = re.search(
                r"\b(?P<value>\d+(?:\.\d+)?)"
                r"(?:st|nd|rd|th)\s+percentile\b",
                matched_text,
                re.IGNORECASE,
            )

            value = (
                parse_number(
                    percentile_match.group(
                        "value"
                    )
                )
                if percentile_match
                else None
            )

            if value is not None:
                payload.update({
                    "normalization_status":
                        "NORMALIZED",

                    "normalized_value":
                        value,

                    "quantitative_scale":
                        "PERCENTILE",

                    "normalization_reason":
                        "ARTICLE_EXPRESSED_PERCENTILE",
                })

        elif signal_type == "PERCENTAGE":
            value = extract_leading_number(
                matched_text
            )

            if value is not None:
                payload.update({
                    "normalization_status":
                        "NORMALIZED",

                    "normalized_value":
                        value,

                    "canonical_unit":
                        "percent",

                    "unit_symbol":
                        "%",

                    "measurement_family":
                        "PROPORTION_PERCENTAGE",

                    "quantitative_scale":
                        "PERCENTAGE",

                    "normalization_reason":
                        "ARTICLE_EXPRESSED_PERCENTAGE",
                })

        elif signal_type in {
            "WEIGHT_MEASUREMENT",
            "LENGTH_HEIGHT_MEASUREMENT",
            "AGE_DURATION",
        }:
            value = extract_leading_number(
                matched_text
            )

            unit_info = resolve_unit(
                matched_text
            )

            if (
                value is not None
                and unit_info[
                    "canonical_unit"
                ]
                is not None
            ):
                payload.update({
                    "normalization_status":
                        "NORMALIZED",

                    "normalized_value":
                        value,

                    "canonical_unit":
                        unit_info[
                            "canonical_unit"
                        ],

                    "unit_symbol":
                        unit_info[
                            "unit_symbol"
                        ],

                    "measurement_family":
                        unit_info[
                            "measurement_family"
                        ],

                    "normalization_reason":
                        "ARTICLE_EXPRESSED_MEASUREMENT",
                })

        elif signal_type == "NUMERIC_RANGE":
            values = [
                parse_number(
                    item
                )
                for item in re.findall(
                    r"\d+\s+\d+\s*/\s*\d+"
                    r"|"
                    r"\d+\s*/\s*\d+"
                    r"|"
                    r"\d+(?:\.\d+)?",
                    matched_text,
                )
            ]

            values = [
                value
                for value in values
                if value is not None
            ]

            if len(
                values
            ) == 2:
                payload.update({
                    "normalization_status":
                        "NORMALIZED",

                    "normalized_values":
                        values,

                    "quantitative_scale":
                        "RANGE",

                    "normalization_reason":
                        "ARTICLE_EXPRESSED_NUMERIC_RANGE",
                })

        elif signal_type == "MEASUREMENT_RATE":
            rate_match = re.search(
                r"(?P<number>"
                r"\d+\s+\d+\s*/\s*\d+"
                r"|"
                r"\d+\s*/\s*\d+"
                r"|"
                r"\d+(?:\.\d+)?"
                r")"
                r"\s+"
                r"(?P<numerator>[a-zA-Z]+)"
                r"\s+per\s+"
                r"(?P<denominator>[a-zA-Z]+)",
                matched_text,
                re.IGNORECASE,
            )

            if rate_match:
                value = parse_number(
                    rate_match.group(
                        "number"
                    )
                )

                numerator_alias = (
                    rate_match.group(
                        "numerator"
                    )
                    .lower()
                )

                denominator_alias = (
                    rate_match.group(
                        "denominator"
                    )
                    .lower()
                )

                numerator_unit = (
                    alias_registry.get(
                        numerator_alias
                    )
                )

                denominator_unit = (
                    alias_registry.get(
                        denominator_alias
                    )
                )

                if (
                    value is not None
                    and numerator_unit is not None
                    and denominator_unit is not None
                ):
                    numerator_spec = (
                        unit_registry[
                            numerator_unit
                        ]
                    )

                    denominator_spec = (
                        unit_registry[
                            denominator_unit
                        ]
                    )

                    payload.update({
                        "normalization_status":
                            "NORMALIZED",

                        "normalized_value":
                            value,

                        "canonical_unit":
                            numerator_unit,

                        "unit_symbol":
                            numerator_spec[
                                "symbol"
                            ],

                        "measurement_family":
                            "RATE",

                        "rate_denominator_unit":
                            denominator_unit,

                        "rate_denominator_symbol":
                            denominator_spec[
                                "symbol"
                            ],

                        "quantitative_scale":
                            "ARTICLE_EXPRESSED_RATE",

                        "normalization_reason":
                            "ARTICLE_EXPRESSED_MEASUREMENT_RATE",
                    })

        elif signal_type == "MULTIPLICATIVE_CHANGE":
            factor = multiplicative_registry.get(
                matched_text.lower()
            )

            if factor is not None:
                payload.update({
                    "normalization_status":
                        "NORMALIZED",

                    "normalized_value":
                        factor,

                    "multiplicative_factor":
                        factor,

                    "quantitative_scale":
                        "MULTIPLICATIVE_FACTOR",

                    "normalization_reason":
                        "ARTICLE_EXPRESSED_MULTIPLICATIVE_FORM",
                })

        elif signal_type == "GENERIC_NUMBER":
            value = parse_number(
                matched_text
            )

            if value is not None:
                payload.update({
                    "normalization_status":
                        "NORMALIZED",

                    "normalized_value":
                        value,

                    "quantitative_scale":
                        "UNCLASSIFIED_NUMERIC_VALUE",

                    "normalization_reason":
                        "ARTICLE_EXPRESSED_GENERIC_NUMBER",
                })

        if (
            payload[
                "normalization_status"
            ]
            != "NORMALIZED"
        ):
            payload[
                "normalization_reason"
            ] = (
                "QUANTITATIVE_FORM_NOT_NORMALIZABLE_WITH_CURRENT_CANONICAL_REGISTRY"
            )

        normalized.update({
            **payload,

            "unit_measurement_normalized":
                (
                    payload[
                        "normalization_status"
                    ]
                    == "NORMALIZED"
                ),

            "final_quantitative_referent_selected":
                False,

            "quantity_role_orientation_resolved":
                False,

            "same_sentence_quantitative_validated":
                False,

            "cross_sentence_quantitative_validated":
                False,

            "quantitative_evidence_assessed":
                False,

            "duplicate_resolution_performed":
                False,

            "derived_calculation_performed":
                False,

            "quantitative_inference_performed":
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
            "quantitative_candidates"
        )
        or []
    )

    normalized_candidates = [
        normalize_candidate(
            candidate
        )
        for candidate in source_candidates
    ]

    normalized_by_id = {
        candidate.get(
            "quantitative_candidate_id"
        ):
            candidate
        for candidate in normalized_candidates
    }

    normalized_units = []

    for unit in (
        entity_concept_grounding_result.get(
            "quantitative_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every Quantitative Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "quantitative_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "entity_concept_grounding"
            )
            != "COMPLETE"
        ):
            raise QuantitativeIntelligenceError(
                "Entity/concept grounding must be COMPLETE before normalization."
            )

        if (
            state.get(
                "unit_measurement_normalization"
            )
            != "PENDING"
        ):
            raise QuantitativeIntelligenceError(
                "Unit/measurement normalization must be PENDING."
            )

        updated_candidates = []

        for old_candidate in (
            unit.get(
                "quantitative_candidates"
            )
            or []
        ):
            candidate_id = old_candidate.get(
                "quantitative_candidate_id"
            )

            normalized_candidate = (
                normalized_by_id.get(
                    candidate_id
                )
            )

            if normalized_candidate is None:
                raise QuantitativeIntelligenceError(
                    "Quantitative candidate/unit normalization mismatch."
                )

            updated_candidates.append(
                normalized_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "unit_measurement_normalization"
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
            raise QuantitativeIntelligenceError(
                "Stage-F grounding boundary is incomplete."
            )

        required_false_boundaries = (
            "unit_normalization_performed",
            "derived_calculation_performed",
            "quantitative_inference_performed",
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
                raise QuantitativeIntelligenceError(
                    boundary_name
                    + " must be False before Stage G."
                )

        updated_boundaries[
            "unit_normalization_performed"
        ] = True

        updated_boundaries[
            "derived_calculation_performed"
        ] = False

        updated_boundaries[
            "quantitative_inference_performed"
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
            "quantitative_candidates":
                updated_candidates,

            "normalized_quantitative_candidate_count":
                sum(
                    1
                    for candidate in updated_candidates
                    if candidate.get(
                        "normalization_status"
                    )
                    == "NORMALIZED"
                ),

            "unsupported_quantitative_candidate_count":
                sum(
                    1
                    for candidate in updated_candidates
                    if candidate.get(
                        "normalization_status"
                    )
                    == "UNSUPPORTED"
                ),

            "quantitative_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        normalized_units.append(
            updated_unit
        )

    normalized_units_by_id = {
        unit.get(
            "quantitative_claim_unit_id"
        ):
            unit
        for unit in normalized_units
    }

    normalized_sections = []

    for section in (
        entity_concept_grounding_result.get(
            "quantitative_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every quantitative section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "quantitative_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "quantitative_claim_unit_id"
            )

            normalized_unit = (
                normalized_units_by_id.get(
                    unit_id
                )
            )

            if normalized_unit is None:
                raise QuantitativeIntelligenceError(
                    "Quantitative section/unit normalization mismatch."
                )

            section_units.append(
                normalized_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "quantitative_candidates"
                )
                or []
            )
        ]

        normalized_sections.append({
            **dict(
                section
            ),

            "quantitative_claim_units":
                section_units,

            "quantitative_candidates":
                section_candidates,

            "quantitative_candidate_count":
                len(
                    section_candidates
                ),

            "normalized_quantitative_candidate_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "normalization_status"
                    )
                    == "NORMALIZED"
                ),

            "unsupported_quantitative_candidate_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "normalization_status"
                    )
                    == "UNSUPPORTED"
                ),

            "unit_measurement_normalization_complete":
                True,
        })

    normalized_count = sum(
        1
        for candidate in normalized_candidates
        if candidate.get(
            "normalization_status"
        )
        == "NORMALIZED"
    )

    unsupported_count = sum(
        1
        for candidate in normalized_candidates
        if candidate.get(
            "normalization_status"
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

    boundaries[
        "unit_normalization_performed"
    ] = True

    boundaries[
        "derived_calculation_performed"
    ] = False

    boundaries[
        "quantitative_inference_performed"
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
            "quantitative_unit_measurement_normalization_v1",

        "patch":
            "4.6.9G",

        "status":
            "QUANTITATIVE_UNIT_MEASUREMENT_NORMALIZATION_COMPLETE",

        "quantitative_sections":
            normalized_sections,

        "quantitative_claim_units":
            normalized_units,

        "quantitative_candidates":
            normalized_candidates,

        "unsupported_quantitative_candidates":
            [
                candidate
                for candidate in normalized_candidates
                if candidate.get(
                    "normalization_status"
                )
                == "UNSUPPORTED"
            ],

        "unit_measurement_normalization_summary": {
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

            "canonical_unit_registry_applied":
                True,

            "unit_registry_entry_count":
                len(
                    unit_registry
                ),

            "article_expressed_values_only":
                True,

            "unit_conversion_performed":
                False,

            "derived_calculation_performed":
                False,

            "final_quantitative_referent_selection_performed":
                False,

            "quantity_role_orientation_performed":
                False,

            "same_sentence_quantitative_validation_performed":
                False,

            "cross_sentence_quantitative_validation_performed":
                False,

            "quantitative_inference_performed":
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
            "quantity_role_comparison_orientation",
    })

    return result



def resolve_quantitative_role_orientation_v1(
    unit_measurement_normalization_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Resolve article-local quantitative role, directional-change,
    comparison, and referent-selection metadata for normalized
    quantitative candidates.

    This stage may select a quantitative referent only when the
    previous grounding stage produced exactly one unambiguous
    article-local semantic-object match.

    It does NOT:
    - invent a referent when multiple grounding matches exist,
    - create new entities or concepts,
    - calculate derived values,
    - convert units,
    - infer unstated quantitative relationships,
    - validate the quantitative statement,
    - perform cross-sentence reasoning,
    - perform full temporal reasoning,
    - perform new causal reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        unit_measurement_normalization_result,
        Mapping,
    ):
        raise QuantitativeIntelligenceError(
            "unit_measurement_normalization_result must be a mapping."
        )

    if (
        unit_measurement_normalization_result.get(
            "schema_version"
        )
        != "quantitative_unit_measurement_normalization_v1"
    ):
        raise QuantitativeIntelligenceError(
            "Stage H requires quantitative_unit_measurement_normalization_v1."
        )

    if (
        unit_measurement_normalization_result.get(
            "status"
        )
        != "QUANTITATIVE_UNIT_MEASUREMENT_NORMALIZATION_COMPLETE"
    ):
        raise QuantitativeIntelligenceError(
            "Unit/measurement normalization must be complete before orientation."
        )

    if (
        unit_measurement_normalization_result.get(
            "phase"
        )
        != "4.6.9"
    ):
        raise QuantitativeIntelligenceError(
            "Stage H requires Phase 4.6.9 input."
        )

    if (
        unit_measurement_normalization_result.get(
            "patch"
        )
        != "4.6.9G"
    ):
        raise QuantitativeIntelligenceError(
            "Stage H requires canonical 4.6.9G input."
        )

    if (
        unit_measurement_normalization_result.get(
            "next_stage"
        )
        != "quantity_role_comparison_orientation"
    ):
        raise QuantitativeIntelligenceError(
            "Stage G must hand off to quantity_role_comparison_orientation."
        )

    if (
        unit_measurement_normalization_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise QuantitativeIntelligenceError(
            "Quantitative Intelligence must remain transient."
        )

    role_by_signal_type = {
        "PERCENTILE":
            "PERCENTILE_RANK",

        "PERCENTAGE":
            "PROPORTION_VALUE",

        "WEIGHT_MEASUREMENT":
            "MEASUREMENT_VALUE",

        "LENGTH_HEIGHT_MEASUREMENT":
            "MEASUREMENT_VALUE",

        "AGE_DURATION":
            "TEMPORAL_QUANTITY",

        "NUMERIC_RANGE":
            "RANGE_BOUNDARIES",

        "MEASUREMENT_RATE":
            "RATE_VALUE",

        "MULTIPLICATIVE_CHANGE":
            "MULTIPLICATIVE_CHANGE",

        "GENERIC_NUMBER":
            "UNCLASSIFIED_NUMERIC_VALUE",
    }

    measurement_role_by_family = {
        "MASS_WEIGHT":
            "WEIGHT_MEASUREMENT_VALUE",

        "LENGTH_DISTANCE":
            "LENGTH_DISTANCE_MEASUREMENT_VALUE",

        "TIME_DURATION":
            "TEMPORAL_QUANTITY",
    }

    source_candidates = list(
        unit_measurement_normalization_result.get(
            "quantitative_candidates"
        )
        or []
    )

    unit_candidate_counts = {}

    for source_unit in (
        unit_measurement_normalization_result.get(
            "quantitative_claim_units"
        )
        or []
    ):
        if not isinstance(
            source_unit,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every Quantitative Claim Unit must be a mapping."
            )

        source_unit_id = str(
            source_unit.get(
                "quantitative_claim_unit_id"
            )
            or ""
        )

        if not source_unit_id:
            raise QuantitativeIntelligenceError(
                "Quantitative Claim Unit ID is required."
            )

        if source_unit_id in unit_candidate_counts:
            raise QuantitativeIntelligenceError(
                "Duplicate Quantitative Claim Unit ID detected."
            )

        unit_candidate_counts[
            source_unit_id
        ] = len(
            source_unit.get(
                "quantitative_candidates"
            )
            or []
        )

    resolved_candidates = []

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every quantitative candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "quantitative_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise QuantitativeIntelligenceError(
                "Quantitative candidate ID is required."
            )

        if (
            candidate.get(
                "quantity_role_orientation_resolved"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Candidate must not already have quantitative role orientation."
            )

        if (
            candidate.get(
                "final_quantitative_referent_selected"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Candidate must not already have a final quantitative referent."
            )

        normalization_status = candidate.get(
            "normalization_status"
        )

        signal_type = str(
            candidate.get(
                "signal_type"
            )
            or ""
        ).strip()

        if not signal_type:
            raise QuantitativeIntelligenceError(
                "Quantitative candidate signal_type is required."
            )

        grounding_matches = list(
            candidate.get(
                "entity_concept_grounding_matches"
            )
            or []
        )

        grounding_match_count = int(
            candidate.get(
                "entity_concept_grounding_match_count"
            )
            or 0
        )

        if (
            grounding_match_count
            != len(
                grounding_matches
            )
        ):
            raise QuantitativeIntelligenceError(
                "Quantitative grounding match count is inconsistent."
            )

        contextual_signals = list(
            candidate.get(
                "contextual_quantitative_signals"
            )
            or []
        )

        for contextual_signal in contextual_signals:
            if not isinstance(
                contextual_signal,
                Mapping,
            ):
                raise QuantitativeIntelligenceError(
                    "Every contextual quantitative signal must be a mapping."
                )

        contextual_types = [
            str(
                item.get(
                    "signal_type"
                )
                or ""
            )
            for item in contextual_signals
        ]

        if normalization_status == "UNSUPPORTED":
            unresolved = dict(
                candidate
            )

            unresolved.update({
                "quantity_role_orientation_status":
                    "UNRESOLVED_UNSUPPORTED_QUANTITATIVE_FORM",

                "canonical_quantity_role":
                    None,

                "quantitative_direction":
                    None,

                "comparison_orientation":
                    None,

                "comparison_present":
                    (
                        "COMPARISON"
                        in contextual_types
                    ),

                "directional_change_present":
                    (
                        "INCREASE"
                        in contextual_types
                        or "DECREASE"
                        in contextual_types
                    ),

                "selected_quantitative_referent":
                    None,

                "quantitative_referent_selection_status":
                    "NOT_SELECTED",

                "quantitative_referent_selection_basis":
                    None,

                "final_quantitative_referent_selected":
                    False,

                "quantity_role_orientation_resolved":
                    False,

                "same_sentence_quantitative_validated":
                    False,

                "cross_sentence_quantitative_validated":
                    False,

                "quantitative_evidence_assessed":
                    False,

                "duplicate_resolution_performed":
                    False,

                "derived_calculation_performed":
                    False,

                "quantitative_inference_performed":
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
                unresolved
            )

            continue

        if normalization_status != "NORMALIZED":
            raise QuantitativeIntelligenceError(
                "Candidate has invalid quantitative normalization status."
            )

        if (
            candidate.get(
                "unit_measurement_normalized"
            )
            is not True
        ):
            raise QuantitativeIntelligenceError(
                "Normalized quantitative candidate must have unit_measurement_normalized=True."
            )

        canonical_role = role_by_signal_type.get(
            signal_type
        )

        if canonical_role is None:
            raise QuantitativeIntelligenceError(
                "Normalized quantitative signal type has no canonical role."
            )

        measurement_family = candidate.get(
            "measurement_family"
        )

        if (
            signal_type
            in {
                "WEIGHT_MEASUREMENT",
                "LENGTH_HEIGHT_MEASUREMENT",
                "AGE_DURATION",
            }
            and measurement_family
            in measurement_role_by_family
        ):
            canonical_role = (
                measurement_role_by_family[
                    measurement_family
                ]
            )

        candidate_unit_id = str(
            candidate.get(
                "quantitative_claim_unit_id"
            )
            or ""
        )

        if not candidate_unit_id:
            raise QuantitativeIntelligenceError(
                "Quantitative candidate claim-unit ID is required."
            )

        if (
            candidate_unit_id
            not in unit_candidate_counts
        ):
            raise QuantitativeIntelligenceError(
                "Quantitative candidate has no canonical claim unit."
            )

        unit_candidate_count = (
            unit_candidate_counts[
                candidate_unit_id
            ]
        )

        contextual_assignment_unambiguous = (
            unit_candidate_count == 1
        )

        raw_increase_context_present = (
            "INCREASE"
            in contextual_types
        )

        raw_decrease_context_present = (
            "DECREASE"
            in contextual_types
        )

        raw_comparison_context_present = (
            "COMPARISON"
            in contextual_types
        )

        raw_average_context_present = (
            "AVERAGE_REFERENCE"
            in contextual_types
        )

        increase_present = (
            raw_increase_context_present
            and contextual_assignment_unambiguous
        )

        decrease_present = (
            raw_decrease_context_present
            and contextual_assignment_unambiguous
        )

        comparison_present = (
            raw_comparison_context_present
            and contextual_assignment_unambiguous
        )

        average_present = (
            raw_average_context_present
            and contextual_assignment_unambiguous
        )

        contextual_assignment_ambiguous = (
            not contextual_assignment_unambiguous
            and bool(
                contextual_types
            )
        )

        if (
            increase_present
            and decrease_present
        ):
            quantitative_direction = (
                "DIRECTIONALLY_AMBIGUOUS"
            )

        elif increase_present:
            quantitative_direction = (
                "INCREASE"
            )

        elif decrease_present:
            quantitative_direction = (
                "DECREASE"
            )

        elif (
            signal_type
            == "MULTIPLICATIVE_CHANGE"
            and candidate.get(
                "multiplicative_factor"
            )
            is not None
        ):
            factor = candidate.get(
                "multiplicative_factor"
            )

            if factor > 1:
                quantitative_direction = (
                    "MULTIPLICATIVE_INCREASE"
                )

            elif factor < 1:
                quantitative_direction = (
                    "MULTIPLICATIVE_DECREASE"
                )

            else:
                quantitative_direction = (
                    "NO_MULTIPLICATIVE_CHANGE"
                )

        else:
            quantitative_direction = (
                "NO_EXPLICIT_DIRECTION"
            )

        if signal_type == "NUMERIC_RANGE":
            comparison_orientation = (
                "BOUNDED_RANGE"
            )

        elif comparison_present:
            comparison_orientation = (
                "ARTICLE_EXPRESSED_COMPARISON_CONTEXT"
            )

        else:
            comparison_orientation = (
                "NO_EXPLICIT_COMPARISON"
            )

        if increase_present:
            if canonical_role in {
                "WEIGHT_MEASUREMENT_VALUE",
                "LENGTH_DISTANCE_MEASUREMENT_VALUE",
                "MEASUREMENT_VALUE",
                "PROPORTION_VALUE",
                "UNCLASSIFIED_NUMERIC_VALUE",
            }:
                canonical_role = (
                    "CHANGE_AMOUNT"
                )

        elif decrease_present:
            if canonical_role in {
                "WEIGHT_MEASUREMENT_VALUE",
                "LENGTH_DISTANCE_MEASUREMENT_VALUE",
                "MEASUREMENT_VALUE",
                "PROPORTION_VALUE",
                "UNCLASSIFIED_NUMERIC_VALUE",
            }:
                canonical_role = (
                    "CHANGE_AMOUNT"
                )

        selected_referent = None
        referent_selected = False

        if grounding_match_count == 1:
            referent_selection_status = (
                "REFERENT_PENDING_SINGLE_GROUNDING_MATCH"
            )

            referent_selection_basis = (
                "SINGLE_ARTICLE_LOCAL_GROUNDING_REQUIRES_VALIDATION"
            )

        elif grounding_match_count > 1:
            referent_selection_status = (
                "REFERENT_PENDING_MULTIPLE_GROUNDING_MATCHES"
            )

            referent_selection_basis = (
                "MULTIPLE_ARTICLE_LOCAL_GROUNDING_MATCHES_REQUIRE_VALIDATION"
            )

        else:
            referent_selection_status = (
                "REFERENT_PENDING_NO_GROUNDING_MATCH"
            )

            referent_selection_basis = (
                "NO_ARTICLE_LOCAL_GROUNDING_MATCH"
            )

        role_status = (
            "ROLE_RESOLVED_REFERENT_PENDING_VALIDATION"
        )

        resolved = dict(
            candidate
        )

        resolved.update({
            "quantity_role_orientation_status":
                role_status,

            "canonical_quantity_role":
                canonical_role,

            "quantitative_direction":
                quantitative_direction,

            "comparison_orientation":
                comparison_orientation,

            "comparison_present":
                comparison_present,

            "average_reference_present":
                average_present,

            "raw_increase_context_present":
                raw_increase_context_present,

            "raw_decrease_context_present":
                raw_decrease_context_present,

            "raw_comparison_context_present":
                raw_comparison_context_present,

            "raw_average_context_present":
                raw_average_context_present,

            "contextual_assignment_unambiguous":
                contextual_assignment_unambiguous,

            "contextual_assignment_ambiguous":
                contextual_assignment_ambiguous,

            "claim_unit_quantitative_candidate_count":
                unit_candidate_count,

            "directional_change_present":
                (
                    increase_present
                    or decrease_present
                    or signal_type
                    == "MULTIPLICATIVE_CHANGE"
                ),

            "selected_quantitative_referent":
                selected_referent,

            "quantitative_referent_selection_status":
                referent_selection_status,

            "quantitative_referent_selection_basis":
                referent_selection_basis,

            "final_quantitative_referent_selected":
                referent_selected,

            "quantity_role_orientation_resolved":
                True,

            "same_sentence_quantitative_validated":
                False,

            "cross_sentence_quantitative_validated":
                False,

            "quantitative_evidence_assessed":
                False,

            "duplicate_resolution_performed":
                False,

            "derived_calculation_performed":
                False,

            "quantitative_inference_performed":
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

    resolved_by_id = {
        candidate.get(
            "quantitative_candidate_id"
        ):
            candidate
        for candidate in resolved_candidates
    }

    resolved_units = []

    for unit in (
        unit_measurement_normalization_result.get(
            "quantitative_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every Quantitative Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "quantitative_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "unit_measurement_normalization"
            )
            != "COMPLETE"
        ):
            raise QuantitativeIntelligenceError(
                "Unit/measurement normalization must be COMPLETE before orientation."
            )

        if (
            state.get(
                "quantity_role_comparison_orientation"
            )
            != "PENDING"
        ):
            raise QuantitativeIntelligenceError(
                "Quantity-role/comparison orientation must be PENDING."
            )

        updated_candidates = []

        for old_candidate in (
            unit.get(
                "quantitative_candidates"
            )
            or []
        ):
            candidate_id = old_candidate.get(
                "quantitative_candidate_id"
            )

            resolved_candidate = (
                resolved_by_id.get(
                    candidate_id
                )
            )

            if resolved_candidate is None:
                raise QuantitativeIntelligenceError(
                    "Quantitative candidate/unit orientation mismatch."
                )

            updated_candidates.append(
                resolved_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "quantity_role_comparison_orientation"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            updated_boundaries.get(
                "unit_normalization_performed"
            )
            is not True
        ):
            raise QuantitativeIntelligenceError(
                "Stage-G normalization boundary is incomplete."
            )

        required_false_boundaries = (
            "derived_calculation_performed",
            "quantitative_inference_performed",
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
                raise QuantitativeIntelligenceError(
                    boundary_name
                    + " must be False before Stage H."
                )

        updated_boundaries[
            "quantity_role_orientation_performed"
        ] = True

        updated_boundaries[
            "same_sentence_quantitative_validation_performed"
        ] = False

        updated_boundaries[
            "cross_sentence_quantitative_validation_performed"
        ] = False

        updated_boundaries[
            "derived_calculation_performed"
        ] = False

        updated_boundaries[
            "quantitative_inference_performed"
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
            "quantitative_candidates":
                updated_candidates,

            "resolved_quantity_role_count":
                sum(
                    1
                    for candidate in updated_candidates
                    if candidate.get(
                        "quantity_role_orientation_resolved"
                    )
                    is True
                ),

            "unresolved_quantity_role_count":
                sum(
                    1
                    for candidate in updated_candidates
                    if candidate.get(
                        "quantity_role_orientation_resolved"
                    )
                    is False
                ),

            "selected_referent_count":
                sum(
                    1
                    for candidate in updated_candidates
                    if candidate.get(
                        "final_quantitative_referent_selected"
                    )
                    is True
                ),

            "unresolved_referent_count":
                sum(
                    1
                    for candidate in updated_candidates
                    if candidate.get(
                        "final_quantitative_referent_selected"
                    )
                    is False
                ),

            "comparison_candidate_count":
                sum(
                    1
                    for candidate in updated_candidates
                    if candidate.get(
                        "comparison_present"
                    )
                    is True
                ),

            "directional_candidate_count":
                sum(
                    1
                    for candidate in updated_candidates
                    if candidate.get(
                        "directional_change_present"
                    )
                    is True
                ),

            "quantitative_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        resolved_units.append(
            updated_unit
        )

    resolved_units_by_id = {
        unit.get(
            "quantitative_claim_unit_id"
        ):
            unit
        for unit in resolved_units
    }

    resolved_sections = []

    for section in (
        unit_measurement_normalization_result.get(
            "quantitative_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every quantitative section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "quantitative_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "quantitative_claim_unit_id"
            )

            resolved_unit = (
                resolved_units_by_id.get(
                    unit_id
                )
            )

            if resolved_unit is None:
                raise QuantitativeIntelligenceError(
                    "Quantitative section/unit orientation mismatch."
                )

            section_units.append(
                resolved_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "quantitative_candidates"
                )
                or []
            )
        ]

        resolved_sections.append({
            **dict(
                section
            ),

            "quantitative_claim_units":
                section_units,

            "quantitative_candidates":
                section_candidates,

            "resolved_quantity_role_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "quantity_role_orientation_resolved"
                    )
                    is True
                ),

            "unresolved_quantity_role_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "quantity_role_orientation_resolved"
                    )
                    is False
                ),

            "selected_referent_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "final_quantitative_referent_selected"
                    )
                    is True
                ),

            "comparison_candidate_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "comparison_present"
                    )
                    is True
                ),

            "directional_candidate_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "directional_change_present"
                    )
                    is True
                ),

            "quantity_role_comparison_orientation_complete":
                True,
        })

    resolved_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "quantity_role_orientation_resolved"
        )
        is True
    )

    unresolved_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "quantity_role_orientation_resolved"
        )
        is False
    )

    selected_referent_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "final_quantitative_referent_selected"
        )
        is True
    )

    unresolved_referent_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "final_quantitative_referent_selected"
        )
        is False
    )

    comparison_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "comparison_present"
        )
        is True
    )

    directional_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "directional_change_present"
        )
        is True
    )

    increase_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "quantitative_direction"
        )
        in {
            "INCREASE",
            "MULTIPLICATIVE_INCREASE",
        }
    )

    decrease_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "quantitative_direction"
        )
        in {
            "DECREASE",
            "MULTIPLICATIVE_DECREASE",
        }
    )

    result = dict(
        unit_measurement_normalization_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    boundaries[
        "quantity_role_orientation_performed"
    ] = True

    boundaries[
        "same_sentence_quantitative_validation_performed"
    ] = False

    boundaries[
        "cross_sentence_quantitative_validation_performed"
    ] = False

    boundaries[
        "quantitative_evidence_assessment_performed"
    ] = False

    boundaries[
        "derived_calculation_performed"
    ] = False

    boundaries[
        "quantitative_inference_performed"
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
            "quantitative_role_comparison_orientation_v1",

        "patch":
            "4.6.9H",

        "status":
            "QUANTITATIVE_ROLE_COMPARISON_ORIENTATION_COMPLETE",

        "quantitative_sections":
            resolved_sections,

        "quantitative_claim_units":
            resolved_units,

        "quantitative_candidates":
            resolved_candidates,

        "quantity_role_comparison_orientation_summary": {
            "candidate_count":
                len(
                    resolved_candidates
                ),

            "resolved_quantity_role_count":
                resolved_count,

            "unresolved_quantity_role_count":
                unresolved_count,

            "candidate_count_accounted_for":
                (
                    resolved_count
                    + unresolved_count
                    == len(
                        resolved_candidates
                    )
                ),

            "selected_referent_count":
                selected_referent_count,

            "unresolved_referent_count":
                unresolved_referent_count,

            "referent_count_accounted_for":
                (
                    selected_referent_count
                    + unresolved_referent_count
                    == len(
                        resolved_candidates
                    )
                ),

            "comparison_candidate_count":
                comparison_count,

            "directional_candidate_count":
                directional_count,

            "increase_or_multiplicative_increase_count":
                increase_count,

            "decrease_or_multiplicative_decrease_count":
                decrease_count,

            "final_referent_selection_performed":
                False,

            "single_grounding_auto_selection_performed":
                False,

            "multiple_grounding_guessing_performed":
                False,

            "multi_candidate_context_auto_assignment_performed":
                False,

            "single_candidate_context_assignment_only":
                True,

            "new_entities_or_concepts_created":
                False,

            "unit_conversion_performed":
                False,

            "derived_calculation_performed":
                False,

            "same_sentence_quantitative_validation_performed":
                False,

            "cross_sentence_quantitative_validation_performed":
                False,

            "quantitative_inference_performed":
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
            "same_sentence_quantitative_validation",
    })

    return result



def validate_same_sentence_quantitative_v1(
    orientation_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate whether each quantitative candidate is supported by its
    canonical article-local Quantitative Claim Unit sentence.

    Validation is limited to the article expression itself.

    This stage verifies:
    - candidate-to-claim-unit identity,
    - sentence identity,
    - source-text continuity,
    - exact quantitative signal-span support,
    - completed normalization,
    - completed quantitative role orientation where supported,
    - preservation of contextual ambiguity.

    It does NOT:
    - choose a final quantitative referent,
    - resolve multi-candidate contextual ambiguity by guesswork,
    - calculate derived values,
    - convert units,
    - perform cross-sentence validation,
    - perform quantitative inference,
    - perform full temporal reasoning,
    - perform new causal reasoning,
    - establish factual/scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        orientation_result,
        Mapping,
    ):
        raise QuantitativeIntelligenceError(
            "orientation_result must be a mapping."
        )

    if (
        orientation_result.get(
            "schema_version"
        )
        != "quantitative_role_comparison_orientation_v1"
    ):
        raise QuantitativeIntelligenceError(
            "Stage I requires quantitative_role_comparison_orientation_v1."
        )

    if (
        orientation_result.get(
            "status"
        )
        != "QUANTITATIVE_ROLE_COMPARISON_ORIENTATION_COMPLETE"
    ):
        raise QuantitativeIntelligenceError(
            "Quantity-role/comparison orientation must be complete before Stage I."
        )

    if (
        orientation_result.get(
            "phase"
        )
        != "4.6.9"
    ):
        raise QuantitativeIntelligenceError(
            "Stage I requires Phase 4.6.9 input."
        )

    if (
        orientation_result.get(
            "patch"
        )
        != "4.6.9H"
    ):
        raise QuantitativeIntelligenceError(
            "Stage I requires canonical 4.6.9H input."
        )

    if (
        orientation_result.get(
            "next_stage"
        )
        != "same_sentence_quantitative_validation"
    ):
        raise QuantitativeIntelligenceError(
            "Stage H must hand off to same_sentence_quantitative_validation."
        )

    if (
        orientation_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise QuantitativeIntelligenceError(
            "Quantitative Intelligence must remain transient."
        )

    source_units = list(
        orientation_result.get(
            "quantitative_claim_units"
        )
        or []
    )

    if not source_units:
        raise QuantitativeIntelligenceError(
            "Quantitative Claim Units are required."
        )

    candidate_to_unit = {}
    unit_ids = set()

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every Quantitative Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "quantitative_claim_unit_id"
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
            raise QuantitativeIntelligenceError(
                "Quantitative Claim Unit ID is required."
            )

        if unit_id in unit_ids:
            raise QuantitativeIntelligenceError(
                "Duplicate Quantitative Claim Unit ID detected."
            )

        unit_ids.add(
            unit_id
        )

        if not sentence_id:
            raise QuantitativeIntelligenceError(
                "Quantitative Claim Unit sentence_id is required."
            )

        if not claim_text:
            raise QuantitativeIntelligenceError(
                "Quantitative Claim Unit text is required."
            )

        state = dict(
            unit.get(
                "quantitative_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "quantity_role_comparison_orientation"
            )
            != "COMPLETE"
        ):
            raise QuantitativeIntelligenceError(
                "Quantity-role/comparison orientation must be COMPLETE before Stage I."
            )

        if (
            state.get(
                "same_sentence_quantitative_validation"
            )
            != "PENDING"
        ):
            raise QuantitativeIntelligenceError(
                "Same-sentence quantitative validation must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "unit_normalization_performed"
            )
            is not True
        ):
            raise QuantitativeIntelligenceError(
                "Stage-G normalization boundary is incomplete."
            )

        if (
            boundaries.get(
                "quantity_role_orientation_performed"
            )
            is not True
        ):
            raise QuantitativeIntelligenceError(
                "Stage-H orientation boundary is incomplete."
            )

        required_false_boundaries = (
            "same_sentence_quantitative_validation_performed",
            "cross_sentence_quantitative_validation_performed",
            "quantitative_evidence_assessment_performed",
            "derived_calculation_performed",
            "quantitative_inference_performed",
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
                raise QuantitativeIntelligenceError(
                    boundary_name
                    + " must be False before Stage I."
                )

        for candidate in (
            unit.get(
                "quantitative_candidates"
            )
            or []
        ):
            if not isinstance(
                candidate,
                Mapping,
            ):
                raise QuantitativeIntelligenceError(
                    "Every quantitative candidate must be a mapping."
                )

            candidate_id = str(
                candidate.get(
                    "quantitative_candidate_id"
                )
                or ""
            )

            if not candidate_id:
                raise QuantitativeIntelligenceError(
                    "Quantitative candidate ID is required."
                )

            if candidate_id in candidate_to_unit:
                raise QuantitativeIntelligenceError(
                    "Duplicate quantitative candidate ID detected."
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
            and isinstance(
                end,
                int,
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
                    "EXACT_QUANTITATIVE_SIGNAL_SPAN_MATCH",
                )

        return (
            False,
            None,
        )

    source_candidates = list(
        orientation_result.get(
            "quantitative_candidates"
        )
        or []
    )

    validated_candidates = []

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every quantitative candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "quantitative_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise QuantitativeIntelligenceError(
                "Quantitative candidate ID is required."
            )

        unit_info = candidate_to_unit.get(
            candidate_id
        )

        if unit_info is None:
            raise QuantitativeIntelligenceError(
                "Quantitative candidate has no canonical claim-unit sentence."
            )

        if (
            candidate.get(
                "same_sentence_quantitative_validated"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Candidate must not already be same-sentence quantitative validated."
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
                "quantitative_claim_unit_id"
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

        normalization_status = (
            candidate.get(
                "normalization_status"
            )
        )

        normalization_supported = (
            normalization_status
            == "NORMALIZED"
            and candidate.get(
                "unit_measurement_normalized"
            )
            is True
        )

        orientation_supported = (
            candidate.get(
                "quantity_role_orientation_resolved"
            )
            is True
            and bool(
                candidate.get(
                    "canonical_quantity_role"
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

        final_referent_selected = (
            candidate.get(
                "final_quantitative_referent_selected"
            )
            is True
        )

        if final_referent_selected:
            raise QuantitativeIntelligenceError(
                "Stage I must not receive a preselected final quantitative referent."
            )

        if normalization_status == "UNSUPPORTED":
            validation_status = (
                "NOT_VALIDATED_UNSUPPORTED_QUANTITATIVE_FORM"
            )

            same_sentence_valid = False

            validation_reason = (
                "QUANTITATIVE_FORM_NOT_CANONICALLY_NORMALIZED"
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
                "NOT_VALIDATED_QUANTITATIVE_SIGNAL_SPAN_UNSUPPORTED"
            )

            same_sentence_valid = False

            validation_reason = (
                "QUANTITATIVE_SIGNAL_SPAN_NOT_SUPPORTED_BY_CANONICAL_SENTENCE"
            )

        elif not normalization_supported:
            validation_status = (
                "NOT_VALIDATED_QUANTITATIVE_NORMALIZATION_INCOMPLETE"
            )

            same_sentence_valid = False

            validation_reason = (
                "QUANTITATIVE_NORMALIZATION_NOT_COMPLETE"
            )

        elif not orientation_supported:
            validation_status = (
                "NOT_VALIDATED_QUANTITATIVE_ORIENTATION_UNRESOLVED"
            )

            same_sentence_valid = False

            validation_reason = (
                "QUANTITATIVE_ROLE_ORIENTATION_NOT_RESOLVED"
            )

        else:
            validation_status = (
                "VALIDATED_SAME_SENTENCE_QUANTITATIVE_EXPRESSION"
            )

            same_sentence_valid = True

            validation_reason = None

        validated = dict(
            candidate
        )

        validated.update({
            "same_sentence_quantitative_validation_status":
                validation_status,

            "same_sentence_quantitative_valid":
                same_sentence_valid,

            "same_sentence_quantitative_validation_reason":
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

            "same_sentence_quantitative_signal_supported":
                signal_supported,

            "quantitative_signal_support_method":
                signal_support_method,

            "same_sentence_normalization_supported":
                normalization_supported,

            "same_sentence_orientation_supported":
                orientation_supported,

            "same_sentence_contextual_assignment_ambiguous":
                contextual_assignment_ambiguous,

            "same_sentence_contextual_assignment_unambiguous":
                contextual_assignment_unambiguous,

            "same_sentence_quantitative_evidence": {
                "quantitative_claim_unit_id":
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
            },

            "final_quantitative_referent_selected":
                False,

            "selected_quantitative_referent":
                None,

            "same_sentence_quantitative_validated":
                same_sentence_valid,

            "cross_sentence_quantitative_validated":
                False,

            "quantitative_evidence_assessed":
                False,

            "duplicate_resolution_performed":
                False,

            "derived_calculation_performed":
                False,

            "quantitative_inference_performed":
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

    validated_by_id = {
        candidate.get(
            "quantitative_candidate_id"
        ):
            candidate
        for candidate in validated_candidates
    }

    validated_units = []

    for unit in source_units:
        state = dict(
            unit.get(
                "quantitative_analysis_state"
            )
            or {}
        )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "quantitative_candidates"
            )
            or []
        ):
            candidate_id = old_candidate.get(
                "quantitative_candidate_id"
            )

            validated_candidate = (
                validated_by_id.get(
                    candidate_id
                )
            )

            if validated_candidate is None:
                raise QuantitativeIntelligenceError(
                    "Quantitative candidate/unit validation mismatch."
                )

            unit_candidates.append(
                validated_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "same_sentence_quantitative_validation"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "same_sentence_quantitative_validation_performed"
        ] = True

        updated_boundaries[
            "cross_sentence_quantitative_validation_performed"
        ] = False

        updated_boundaries[
            "quantitative_evidence_assessment_performed"
        ] = False

        updated_boundaries[
            "derived_calculation_performed"
        ] = False

        updated_boundaries[
            "quantitative_inference_performed"
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
            "quantitative_candidates":
                unit_candidates,

            "same_sentence_quantitative_validated_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "same_sentence_quantitative_valid"
                    )
                    is True
                ),

            "same_sentence_quantitative_not_validated_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "same_sentence_quantitative_valid"
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

            "quantitative_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        validated_units.append(
            updated_unit
        )

    validated_units_by_id = {
        unit.get(
            "quantitative_claim_unit_id"
        ):
            unit
        for unit in validated_units
    }

    validated_sections = []

    for section in (
        orientation_result.get(
            "quantitative_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every quantitative section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "quantitative_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "quantitative_claim_unit_id"
            )

            validated_unit = (
                validated_units_by_id.get(
                    unit_id
                )
            )

            if validated_unit is None:
                raise QuantitativeIntelligenceError(
                    "Quantitative section/unit validation mismatch."
                )

            section_units.append(
                validated_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "quantitative_candidates"
                )
                or []
            )
        ]

        validated_sections.append({
            **dict(
                section
            ),

            "quantitative_claim_units":
                section_units,

            "quantitative_candidates":
                section_candidates,

            "same_sentence_quantitative_validated_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "same_sentence_quantitative_valid"
                    )
                    is True
                ),

            "same_sentence_quantitative_not_validated_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "same_sentence_quantitative_valid"
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

            "same_sentence_quantitative_validation_complete":
                True,
        })

    validated_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "same_sentence_quantitative_valid"
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

    boundaries[
        "same_sentence_quantitative_validation_performed"
    ] = True

    boundaries[
        "cross_sentence_quantitative_validation_performed"
    ] = False

    boundaries[
        "quantitative_evidence_assessment_performed"
    ] = False

    boundaries[
        "derived_calculation_performed"
    ] = False

    boundaries[
        "quantitative_inference_performed"
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
            "quantitative_same_sentence_validation_v1",

        "patch":
            "4.6.9I",

        "status":
            "QUANTITATIVE_SAME_SENTENCE_VALIDATION_COMPLETE",

        "quantitative_sections":
            validated_sections,

        "quantitative_claim_units":
            validated_units,

        "quantitative_candidates":
            validated_candidates,

        "same_sentence_quantitative_validation_summary": {
            "candidate_count":
                len(
                    validated_candidates
                ),

            "same_sentence_quantitative_validated_count":
                validated_count,

            "same_sentence_quantitative_not_validated_count":
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

            "normalization_support_required":
                True,

            "orientation_support_required":
                True,

            "contextual_ambiguity_preserved":
                True,

            "final_referent_selection_performed":
                False,

            "cross_sentence_quantitative_validation_performed":
                False,

            "quantitative_evidence_assessment_performed":
                False,

            "derived_calculation_performed":
                False,

            "quantitative_inference_performed":
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
            "cross_sentence_quantitative_validation",
    })

    return result



def validate_cross_sentence_quantitative_v1(
    same_sentence_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Assess immediate same-section adjacent-sentence support for
    already-established article-local quantitative expressions.

    Cross-sentence support is conservative:
    - only sentence distance 1 is eligible,
    - only within the same section,
    - Stage-I same-sentence quantitative validity remains the
      authoritative primary-expression validation,
    - adjacent sentences may provide corroborating semantic or
      quantitative context,
    - adjacency may NOT create a quantitative expression, attach
      a quantity to a referent, invent a comparison/direction, or
      rescue an unsupported primary signal.

    This stage does NOT:
    - select final quantitative referents,
    - calculate derived values,
    - convert units,
    - infer unstated numeric relationships,
    - perform full temporal reasoning,
    - perform new causal reasoning,
    - establish factual/scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        same_sentence_result,
        Mapping,
    ):
        raise QuantitativeIntelligenceError(
            "same_sentence_result must be a mapping."
        )

    if (
        same_sentence_result.get(
            "schema_version"
        )
        != "quantitative_same_sentence_validation_v1"
    ):
        raise QuantitativeIntelligenceError(
            "Stage J requires quantitative_same_sentence_validation_v1."
        )

    if (
        same_sentence_result.get(
            "status"
        )
        != "QUANTITATIVE_SAME_SENTENCE_VALIDATION_COMPLETE"
    ):
        raise QuantitativeIntelligenceError(
            "Same-sentence quantitative validation must be complete before Stage J."
        )

    if (
        same_sentence_result.get(
            "phase"
        )
        != "4.6.9"
    ):
        raise QuantitativeIntelligenceError(
            "Stage J requires Phase 4.6.9 input."
        )

    if (
        same_sentence_result.get(
            "patch"
        )
        != "4.6.9I"
    ):
        raise QuantitativeIntelligenceError(
            "Stage J requires canonical 4.6.9I input."
        )

    if (
        same_sentence_result.get(
            "next_stage"
        )
        != "cross_sentence_quantitative_validation"
    ):
        raise QuantitativeIntelligenceError(
            "Stage I must hand off to cross_sentence_quantitative_validation."
        )

    if (
        same_sentence_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise QuantitativeIntelligenceError(
            "Quantitative Intelligence must remain transient."
        )

    source_units = list(
        same_sentence_result.get(
            "quantitative_claim_units"
        )
        or []
    )

    if not source_units:
        raise QuantitativeIntelligenceError(
            "Quantitative Claim Units are required."
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
            raise QuantitativeIntelligenceError(
                "Every Quantitative Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "quantitative_claim_unit_id"
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
            raise QuantitativeIntelligenceError(
                "Quantitative Claim Unit ID is required."
            )

        if unit_id in seen_unit_ids:
            raise QuantitativeIntelligenceError(
                "Duplicate Quantitative Claim Unit ID detected."
            )

        seen_unit_ids.add(
            unit_id
        )

        if not sentence_id:
            raise QuantitativeIntelligenceError(
                "Quantitative Claim Unit sentence_id is required."
            )

        if sentence_id in seen_sentence_ids:
            raise QuantitativeIntelligenceError(
                "Duplicate quantitative sentence_id detected."
            )

        seen_sentence_ids.add(
            sentence_id
        )

        if not section_id:
            raise QuantitativeIntelligenceError(
                "Quantitative Claim Unit section_id is required."
            )

        if not claim_text:
            raise QuantitativeIntelligenceError(
                "Quantitative Claim Unit text is required."
            )

        if not isinstance(
            sentence_global_index,
            int,
        ):
            raise QuantitativeIntelligenceError(
                "sentence_global_index must be an integer."
            )

        if (
            previous_global_index is not None
            and sentence_global_index
            <= previous_global_index
        ):
            raise QuantitativeIntelligenceError(
                "Quantitative Claim Units are not in canonical sentence order."
            )

        previous_global_index = (
            sentence_global_index
        )

        state = dict(
            unit.get(
                "quantitative_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "same_sentence_quantitative_validation"
            )
            != "COMPLETE"
        ):
            raise QuantitativeIntelligenceError(
                "Same-sentence quantitative validation must be COMPLETE before Stage J."
            )

        if (
            state.get(
                "cross_sentence_quantitative_validation"
            )
            != "PENDING"
        ):
            raise QuantitativeIntelligenceError(
                "Cross-sentence quantitative validation must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "same_sentence_quantitative_validation_performed"
            )
            is not True
        ):
            raise QuantitativeIntelligenceError(
                "Stage-I same-sentence validation boundary is incomplete."
            )

        required_false_boundaries = (
            "cross_sentence_quantitative_validation_performed",
            "quantitative_evidence_assessment_performed",
            "derived_calculation_performed",
            "quantitative_inference_performed",
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
                raise QuantitativeIntelligenceError(
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
                "quantitative_candidates"
            )
            or []
        ):
            if not isinstance(
                candidate,
                Mapping,
            ):
                raise QuantitativeIntelligenceError(
                    "Every quantitative candidate must be a mapping."
                )

            candidate_id = str(
                candidate.get(
                    "quantitative_candidate_id"
                )
                or ""
            )

            if not candidate_id:
                raise QuantitativeIntelligenceError(
                    "Quantitative candidate ID is required."
                )

            if candidate_id in candidate_to_record:
                raise QuantitativeIntelligenceError(
                    "Duplicate quantitative candidate ID detected."
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

    def collect_adjacent_support(
        candidate: Mapping[str, Any],
        adjacent_records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        support = []

        grounding_matches = list(
            candidate.get(
                "entity_concept_grounding_matches"
            )
            or []
        )

        grounding_terms = set()

        for grounding in grounding_matches:
            if not isinstance(
                grounding,
                Mapping,
            ):
                continue

            canonical_text = normalize_text(
                grounding.get(
                    "canonical_text"
                )
            )

            matched_surface = normalize_text(
                grounding.get(
                    "matched_surface_form"
                )
            )

            if canonical_text:
                grounding_terms.add(
                    canonical_text
                )

            if matched_surface:
                grounding_terms.add(
                    matched_surface
                )

        signal_type = str(
            candidate.get(
                "signal_type"
            )
            or ""
        )

        canonical_role = str(
            candidate.get(
                "canonical_quantity_role"
            )
            or ""
        )

        for adjacent in adjacent_records:
            adjacent_text = normalize_text(
                adjacent[
                    "text"
                ]
            )

            matched_groundings = sorted(
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

            if not matched_groundings:
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

                "matched_grounding_terms":
                    matched_groundings,

                "support_type":
                    "ADJACENT_SEMANTIC_CONTEXT_CORROBORATION",

                "signal_type":
                    signal_type,

                "canonical_quantity_role":
                    canonical_role,

                "creates_quantitative_relation":
                    False,

                "selects_final_referent":
                    False,
            })

        return support

    source_candidates = list(
        same_sentence_result.get(
            "quantitative_candidates"
        )
        or []
    )

    validated_candidates = []

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every quantitative candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "quantitative_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise QuantitativeIntelligenceError(
                "Quantitative candidate ID is required."
            )

        record = candidate_to_record.get(
            candidate_id
        )

        if record is None:
            raise QuantitativeIntelligenceError(
                "Quantitative candidate has no canonical claim unit."
            )

        if (
            candidate.get(
                "cross_sentence_quantitative_validated"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Candidate must not already be cross-sentence quantitatively validated."
            )

        if (
            candidate.get(
                "final_quantitative_referent_selected"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Stage J must not receive a preselected final quantitative referent."
            )

        same_sentence_valid = (
            candidate.get(
                "same_sentence_quantitative_valid"
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
                "same_sentence_quantitative_signal_supported"
            )
            is True
        )

        normalization_supported = (
            candidate.get(
                "same_sentence_normalization_supported"
            )
            is True
        )

        orientation_supported = (
            candidate.get(
                "same_sentence_orientation_supported"
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

        if not article_asserted_confirmed:
            cross_sentence_status = (
                "NOT_VALIDATED_ARTICLE_ASSERTION_FAILED"
            )

            cross_sentence_valid = False

            final_quantitative_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_CREATE_ARTICLE_ASSERTION"
            )

        elif not same_sentence_candidate_confirmed:
            cross_sentence_status = (
                "NOT_VALIDATED_SAME_SENTENCE_CANDIDATE_ASSERTION_FAILED"
            )

            cross_sentence_valid = False

            final_quantitative_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_CREATE_SAME_SENTENCE_CANDIDATE"
            )

        elif not same_unit_match:
            cross_sentence_status = (
                "NOT_VALIDATED_CLAIM_UNIT_MISMATCH"
            )

            cross_sentence_valid = False

            final_quantitative_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_REPAIR_CLAIM_UNIT_IDENTITY"
            )

        elif not same_sentence_id_match:
            cross_sentence_status = (
                "NOT_VALIDATED_SENTENCE_ID_MISMATCH"
            )

            cross_sentence_valid = False

            final_quantitative_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_REPAIR_SENTENCE_IDENTITY"
            )

        elif not same_source_text_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_SOURCE_TEXT_MISMATCH"
            )

            cross_sentence_valid = False

            final_quantitative_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_REPAIR_SOURCE_TEXT_CONTINUITY"
            )

        elif (
            candidate.get(
                "normalization_status"
            )
            == "UNSUPPORTED"
        ):
            cross_sentence_status = (
                "NOT_VALIDATED_UNSUPPORTED_QUANTITATIVE_FORM"
            )

            cross_sentence_valid = False

            final_quantitative_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_RESCUE_UNSUPPORTED_QUANTITATIVE_FORM"
            )

        elif not same_signal_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_PRIMARY_QUANTITATIVE_SIGNAL_UNSUPPORTED"
            )

            cross_sentence_valid = False

            final_quantitative_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_CREATE_PRIMARY_QUANTITATIVE_SIGNAL"
            )

        elif not normalization_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_QUANTITATIVE_NORMALIZATION_INCOMPLETE"
            )

            cross_sentence_valid = False

            final_quantitative_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_REPAIR_QUANTITATIVE_NORMALIZATION"
            )

        elif not orientation_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_QUANTITATIVE_ORIENTATION_UNRESOLVED"
            )

            cross_sentence_valid = False

            final_quantitative_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_CREATE_QUANTITATIVE_ORIENTATION"
            )

        elif same_sentence_valid:
            cross_sentence_status = (
                "NOT_REQUIRED_SAME_SENTENCE_VALIDATION_SUFFICIENT"
            )

            cross_sentence_valid = False

            final_quantitative_expression_validated = True

            validation_reason = (
                "SAME_SENTENCE_QUANTITATIVE_VALIDATION_ALREADY_SUFFICIENT"
            )

        else:
            cross_sentence_status = (
                "NOT_VALIDATED_SAME_SENTENCE_EXPRESSION_INSUFFICIENT"
            )

            cross_sentence_valid = False

            final_quantitative_expression_validated = False

            validation_reason = (
                "CROSS_SENTENCE_PROXIMITY_CANNOT_CREATE_QUANTITATIVE_EXPRESSION"
            )


        validated = dict(
            candidate
        )

        validated.update({
            "cross_sentence_quantitative_validation_status":
                cross_sentence_status,

            "cross_sentence_quantitative_valid":
                cross_sentence_valid,

            "cross_sentence_quantitative_validation_reason":
                validation_reason,

            "adjacent_same_section_sentence_count":
                len(
                    adjacent_records
                ),

            "adjacent_quantitative_support_present":
                adjacent_support_present,

            "adjacent_quantitative_support_count":
                len(
                    adjacent_support_evidence
                ),

            "adjacent_quantitative_support_evidence":
                adjacent_support_evidence,

            "cross_sentence_adjacency_policy":
                "IMMEDIATE_SENTENCE_DISTANCE_1_SAME_SECTION_ONLY",

            "cross_sentence_support_policy":
                (
                    "CORROBORATION_ONLY_FOR_ALREADY_VALIDATED_"
                    "SAME_SENTENCE_QUANTITATIVE_EXPRESSION"
                ),

            "adjacent_sentence_may_create_quantitative_expression":
                False,

            "adjacent_sentence_may_create_quantitative_direction":
                False,

            "adjacent_sentence_may_create_quantitative_comparison":
                False,

            "adjacent_sentence_may_select_final_referent":
                False,

            "final_quantitative_expression_validated":
                final_quantitative_expression_validated,

            "final_quantitative_referent_selected":
                False,

            "selected_quantitative_referent":
                None,

            "cross_sentence_quantitative_validated":
                cross_sentence_valid,

            "quantitative_evidence_assessed":
                False,

            "duplicate_resolution_performed":
                False,

            "derived_calculation_performed":
                False,

            "quantitative_inference_performed":
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

    validated_by_id = {
        candidate.get(
            "quantitative_candidate_id"
        ):
            candidate
        for candidate in validated_candidates
    }

    validated_units = []

    for record in unit_records:
        unit = record[
            "unit"
        ]

        state = dict(
            unit.get(
                "quantitative_analysis_state"
            )
            or {}
        )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "quantitative_candidates"
            )
            or []
        ):
            candidate_id = old_candidate.get(
                "quantitative_candidate_id"
            )

            validated_candidate = (
                validated_by_id.get(
                    candidate_id
                )
            )

            if validated_candidate is None:
                raise QuantitativeIntelligenceError(
                    "Quantitative candidate/unit cross-sentence validation mismatch."
                )

            unit_candidates.append(
                validated_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "cross_sentence_quantitative_validation"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "cross_sentence_quantitative_validation_performed"
        ] = True

        updated_boundaries[
            "quantitative_evidence_assessment_performed"
        ] = False

        updated_boundaries[
            "derived_calculation_performed"
        ] = False

        updated_boundaries[
            "quantitative_inference_performed"
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
            "quantitative_candidates":
                unit_candidates,

            "adjacent_support_candidate_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "adjacent_quantitative_support_present"
                    )
                    is True
                ),

            "final_quantitative_expression_validated_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "final_quantitative_expression_validated"
                    )
                    is True
                ),

            "cross_sentence_quantitative_validated_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "cross_sentence_quantitative_valid"
                    )
                    is True
                ),

            "quantitative_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        validated_units.append(
            updated_unit
        )

    validated_units_by_id = {
        unit.get(
            "quantitative_claim_unit_id"
        ):
            unit
        for unit in validated_units
    }

    validated_sections = []

    for section in (
        same_sentence_result.get(
            "quantitative_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every quantitative section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "quantitative_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "quantitative_claim_unit_id"
            )

            validated_unit = (
                validated_units_by_id.get(
                    unit_id
                )
            )

            if validated_unit is None:
                raise QuantitativeIntelligenceError(
                    "Quantitative section/unit cross-sentence validation mismatch."
                )

            section_units.append(
                validated_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "quantitative_candidates"
                )
                or []
            )
        ]

        validated_sections.append({
            **dict(
                section
            ),

            "quantitative_claim_units":
                section_units,

            "quantitative_candidates":
                section_candidates,

            "adjacent_support_candidate_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "adjacent_quantitative_support_present"
                    )
                    is True
                ),

            "final_quantitative_expression_validated_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "final_quantitative_expression_validated"
                    )
                    is True
                ),

            "cross_sentence_quantitative_validation_complete":
                True,
        })

    same_sentence_validated_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "same_sentence_quantitative_valid"
        )
        is True
    )

    adjacent_support_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "adjacent_quantitative_support_present"
        )
        is True
    )

    cross_sentence_validated_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "cross_sentence_quantitative_valid"
        )
        is True
    )

    final_validated_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "final_quantitative_expression_validated"
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

    boundaries[
        "cross_sentence_quantitative_validation_performed"
    ] = True

    boundaries[
        "quantitative_evidence_assessment_performed"
    ] = False

    boundaries[
        "derived_calculation_performed"
    ] = False

    boundaries[
        "quantitative_inference_performed"
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
            "quantitative_cross_sentence_validation_v1",

        "patch":
            "4.6.9J",

        "status":
            "QUANTITATIVE_CROSS_SENTENCE_VALIDATION_COMPLETE",

        "quantitative_sections":
            validated_sections,

        "quantitative_claim_units":
            validated_units,

        "quantitative_candidates":
            validated_candidates,

        "cross_sentence_quantitative_validation_summary": {
            "candidate_count":
                len(
                    validated_candidates
                ),

            "already_same_sentence_validated_count":
                same_sentence_validated_count,

            "adjacent_support_candidate_count":
                adjacent_support_count,

            "cross_sentence_quantitative_validated_count":
                cross_sentence_validated_count,

            "final_quantitative_expression_validated_count":
                final_validated_count,

            "final_quantitative_expression_not_validated_count":
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

            "adjacent_sentence_may_create_quantitative_expression":
                False,

            "adjacent_sentence_may_create_quantitative_direction":
                False,

            "adjacent_sentence_may_create_quantitative_comparison":
                False,

            "adjacent_sentence_may_select_final_referent":
                False,

            "proximity_based_quantitative_inference_performed":
                False,

            "quantitative_evidence_assessment_performed":
                False,

            "derived_calculation_performed":
                False,

            "quantitative_inference_performed":
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
            "quantitative_evidence_confidence_assessment",
    })

    return result



def assess_quantitative_confidence_evidence_v1(
    cross_sentence_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Assess article-local evidence strength for quantitative expressions
    already processed through same- and cross-sentence validation.

    Confidence measures how strongly the article itself supports the
    extracted quantitative expression. It does NOT measure factual,
    scientific, medical, statistical, or real-world truth.

    Safeguards:
    - unvalidated quantitative expressions receive zero confidence,
    - exact same-sentence quantitative support is authoritative,
    - adjacent-sentence evidence is corroborative only,
    - multiple grounding matches do not establish a final referent,
    - contextual ambiguity prevents promotion to STRONG,
    - multiple grounding ambiguity prevents promotion to STRONG,
    - no derived calculations or unstated quantitative relationships
      are created.

    This stage does NOT:
    - select a final quantitative referent,
    - establish factual/scientific truth,
    - perform external verification,
    - calculate derived values,
    - convert units,
    - infer unstated quantitative relationships,
    - perform full temporal reasoning,
    - perform new causal reasoning,
    - resolve duplicate quantitative expressions,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        cross_sentence_result,
        Mapping,
    ):
        raise QuantitativeIntelligenceError(
            "cross_sentence_result must be a mapping."
        )

    if (
        cross_sentence_result.get(
            "schema_version"
        )
        != "quantitative_cross_sentence_validation_v1"
    ):
        raise QuantitativeIntelligenceError(
            "Stage K requires quantitative_cross_sentence_validation_v1."
        )

    if (
        cross_sentence_result.get(
            "status"
        )
        != "QUANTITATIVE_CROSS_SENTENCE_VALIDATION_COMPLETE"
    ):
        raise QuantitativeIntelligenceError(
            "Cross-sentence quantitative validation must be complete."
        )

    if (
        cross_sentence_result.get(
            "phase"
        )
        != "4.6.9"
    ):
        raise QuantitativeIntelligenceError(
            "Stage K requires Phase 4.6.9 input."
        )

    if (
        cross_sentence_result.get(
            "patch"
        )
        != "4.6.9J"
    ):
        raise QuantitativeIntelligenceError(
            "Stage K requires canonical 4.6.9J input."
        )

    if (
        cross_sentence_result.get(
            "next_stage"
        )
        != "quantitative_evidence_confidence_assessment"
    ):
        raise QuantitativeIntelligenceError(
            "Stage J must hand off to quantitative_evidence_confidence_assessment."
        )

    if (
        cross_sentence_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise QuantitativeIntelligenceError(
            "Quantitative Intelligence must remain transient."
        )

    source_candidates = list(
        cross_sentence_result.get(
            "quantitative_candidates"
        )
        or []
    )

    assessed_candidates = []

    valid_grounding_statuses = {
        "UNGROUNDED",
        "GROUNDED_SINGLE_MATCH",
        "GROUNDED_MULTIPLE_MATCHES",
    }

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every quantitative candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "quantitative_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise QuantitativeIntelligenceError(
                "Quantitative candidate ID is required."
            )

        if (
            candidate.get(
                "quantitative_evidence_assessed"
            )
            is True
            or candidate.get(
                "quantitative_evidence_assessed"
            )
            is not False
            and candidate.get(
                "quantitative_evidence_assessed"
            )
            is not None
        ):
            raise QuantitativeIntelligenceError(
                "Candidate must not already have quantitative evidence assessment."
            )

        if (
            candidate.get(
                "final_quantitative_referent_selected"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Stage K must not receive a selected final quantitative referent."
            )

        final_validated = (
            candidate.get(
                "final_quantitative_expression_validated"
            )
            is True
        )

        same_sentence_valid = (
            candidate.get(
                "same_sentence_quantitative_valid"
            )
            is True
        )

        cross_sentence_valid = (
            candidate.get(
                "cross_sentence_quantitative_valid"
            )
            is True
        )

        exact_signal_supported = (
            candidate.get(
                "same_sentence_quantitative_signal_supported"
            )
            is True
        )

        normalization_supported = (
            candidate.get(
                "same_sentence_normalization_supported"
            )
            is True
        )

        orientation_supported = (
            candidate.get(
                "same_sentence_orientation_supported"
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
                "adjacent_quantitative_support_present"
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
            raise QuantitativeIntelligenceError(
                "Candidate has invalid quantitative grounding_status."
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
            raise QuantitativeIntelligenceError(
                "Quantitative grounding match count must be an integer."
            )

        if grounding_match_count != len(
            grounding_matches
        ):
            raise QuantitativeIntelligenceError(
                "Quantitative grounding match count mismatch."
            )

        if (
            grounding_status == "UNGROUNDED"
            and grounding_match_count != 0
        ):
            raise QuantitativeIntelligenceError(
                "UNGROUNDED candidate cannot contain grounding matches."
            )

        if (
            grounding_status == "GROUNDED_SINGLE_MATCH"
            and grounding_match_count != 1
        ):
            raise QuantitativeIntelligenceError(
                "GROUNDED_SINGLE_MATCH requires exactly one grounding match."
            )

        if (
            grounding_status == "GROUNDED_MULTIPLE_MATCHES"
            and grounding_match_count < 2
        ):
            raise QuantitativeIntelligenceError(
                "GROUNDED_MULTIPLE_MATCHES requires at least two matches."
            )

        grounding_confidences = []

        for grounding in grounding_matches:
            if not isinstance(
                grounding,
                Mapping,
            ):
                raise QuantitativeIntelligenceError(
                    "Every quantitative grounding match must be a mapping."
                )

            confidence = grounding.get(
                "extraction_confidence"
            )

            if (
                not isinstance(
                    confidence,
                    (int, float),
                )
                or confidence < 0.0
                or confidence > 1.0
            ):
                raise QuantitativeIntelligenceError(
                    "Quantitative grounding match has invalid extraction_confidence."
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
                "QUANTITATIVE_EXPRESSION_NOT_VALIDATED"
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
                raise QuantitativeIntelligenceError(
                    "Final validated quantitative candidate has inconsistent Stage-I support."
                )

            evidence_score = 0.48

            if same_sentence_valid:
                evidence_score += 0.24

                primary_basis = (
                    "SAME_SENTENCE_QUANTITATIVE_EXPRESSION_VALIDATED"
                )

            elif cross_sentence_valid:
                evidence_score += 0.10

                primary_basis = (
                    "CROSS_SENTENCE_QUANTITATIVE_EXPRESSION_VALIDATED"
                )

            else:
                raise QuantitativeIntelligenceError(
                    "Final validated quantitative candidate has no recognized validation mode."
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
            "quantitative_evidence_assessed":
                True,

            "quantitative_evidence_score":
                evidence_score,

            "quantitative_evidence_strength":
                evidence_strength,

            "quantitative_evidence_basis":
                primary_basis,

            "quantitative_confidence_cap_applied":
                confidence_cap_applied,

            "quantitative_evidence_factors": {
                "final_quantitative_expression_validated":
                    final_validated,

                "same_sentence_quantitative_valid":
                    same_sentence_valid,

                "cross_sentence_quantitative_valid":
                    cross_sentence_valid,

                "article_asserted_candidate_confirmed":
                    article_asserted_confirmed,

                "same_sentence_candidate_confirmed":
                    same_sentence_candidate_confirmed,

                "exact_quantitative_signal_supported":
                    exact_signal_supported,

                "normalization_supported":
                    normalization_supported,

                "orientation_supported":
                    orientation_supported,

                "grounding_status":
                    grounding_status,

                "grounding_match_count":
                    grounding_match_count,

                "grounding_confidence":
                    grounding_confidence,

                "contextual_assignment_ambiguous":
                    contextual_ambiguity,

                "adjacent_quantitative_support_present":
                    adjacent_support_present,
            },

            "quantitative_role_preserved":
                True,

            "quantitative_normalization_preserved":
                True,

            "contextual_ambiguity_promoted_to_strong":
                False,

            "multiple_grounding_matches_promoted_to_strong":
                False,

            "cross_sentence_expression_promoted_to_strong":
                False,

            "final_quantitative_referent_selected":
                False,

            "selected_quantitative_referent":
                None,

            "confidence_scope":
                "ARTICLE_LOCAL_QUANTITATIVE_EXPRESSION_EVIDENCE_ONLY",

            "duplicate_resolution_performed":
                False,

            "derived_calculation_performed":
                False,

            "quantitative_inference_performed":
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
            "quantitative_candidate_id"
        ):
            candidate
        for candidate in assessed_candidates
    }

    assessed_units = []

    for unit in (
        cross_sentence_result.get(
            "quantitative_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every Quantitative Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "quantitative_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "cross_sentence_quantitative_validation"
            )
            != "COMPLETE"
        ):
            raise QuantitativeIntelligenceError(
                "Cross-sentence quantitative validation must be COMPLETE before Stage K."
            )

        if (
            state.get(
                "quantitative_evidence_assessment"
            )
            != "PENDING"
        ):
            raise QuantitativeIntelligenceError(
                "Quantitative evidence assessment must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "cross_sentence_quantitative_validation_performed"
            )
            is not True
        ):
            raise QuantitativeIntelligenceError(
                "Stage-J cross-sentence quantitative validation boundary is incomplete."
            )

        if (
            boundaries.get(
                "quantitative_evidence_assessment_performed"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Quantitative evidence assessment boundary must be False before Stage K."
            )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "quantitative_candidates"
            )
            or []
        ):
            candidate_id = old_candidate.get(
                "quantitative_candidate_id"
            )

            assessed_candidate = (
                assessed_by_id.get(
                    candidate_id
                )
            )

            if assessed_candidate is None:
                raise QuantitativeIntelligenceError(
                    "Quantitative candidate/unit evidence mismatch."
                )

            unit_candidates.append(
                assessed_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "quantitative_evidence_assessment"
        ] = "COMPLETE"

        updated_boundaries = dict(
            boundaries
        )

        updated_boundaries[
            "quantitative_evidence_assessment_performed"
        ] = True

        updated_boundaries[
            "duplicate_quantitative_resolution_performed"
        ] = False

        updated_boundaries[
            "derived_calculation_performed"
        ] = False

        updated_boundaries[
            "quantitative_inference_performed"
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
            "quantitative_candidates":
                unit_candidates,

            "strong_quantitative_evidence_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "quantitative_evidence_strength"
                    )
                    == "STRONG"
                ),

            "moderate_quantitative_evidence_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "quantitative_evidence_strength"
                    )
                    == "MODERATE"
                ),

            "limited_quantitative_evidence_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "quantitative_evidence_strength"
                    )
                    == "LIMITED"
                ),

            "insufficient_quantitative_evidence_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "quantitative_evidence_strength"
                    )
                    == "INSUFFICIENT"
                ),

            "quantitative_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        assessed_units.append(
            updated_unit
        )

    assessed_units_by_id = {
        unit.get(
            "quantitative_claim_unit_id"
        ):
            unit
        for unit in assessed_units
    }

    assessed_sections = []

    for section in (
        cross_sentence_result.get(
            "quantitative_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every quantitative section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "quantitative_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "quantitative_claim_unit_id"
            )

            assessed_unit = (
                assessed_units_by_id.get(
                    unit_id
                )
            )

            if assessed_unit is None:
                raise QuantitativeIntelligenceError(
                    "Quantitative section/unit evidence mismatch."
                )

            section_units.append(
                assessed_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "quantitative_candidates"
                )
                or []
            )
        ]

        assessed_sections.append({
            **dict(
                section
            ),

            "quantitative_claim_units":
                section_units,

            "quantitative_candidates":
                section_candidates,

            "strong_quantitative_evidence_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "quantitative_evidence_strength"
                    )
                    == "STRONG"
                ),

            "moderate_quantitative_evidence_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "quantitative_evidence_strength"
                    )
                    == "MODERATE"
                ),

            "limited_quantitative_evidence_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "quantitative_evidence_strength"
                    )
                    == "LIMITED"
                ),

            "insufficient_quantitative_evidence_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "quantitative_evidence_strength"
                    )
                    == "INSUFFICIENT"
                ),

            "quantitative_evidence_assessment_complete":
                True,
        })

    strong_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "quantitative_evidence_strength"
        )
        == "STRONG"
    )

    moderate_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "quantitative_evidence_strength"
        )
        == "MODERATE"
    )

    limited_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "quantitative_evidence_strength"
        )
        == "LIMITED"
    )

    insufficient_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "quantitative_evidence_strength"
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
            "quantitative_evidence_strength"
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
            "quantitative_evidence_strength"
        )
        == "STRONG"
    )

    cross_sentence_strong_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "cross_sentence_quantitative_valid"
        )
        is True
        and candidate.get(
            "quantitative_evidence_strength"
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

    boundaries[
        "quantitative_evidence_assessment_performed"
    ] = True

    boundaries[
        "duplicate_quantitative_resolution_performed"
    ] = False

    boundaries[
        "derived_calculation_performed"
    ] = False

    boundaries[
        "quantitative_inference_performed"
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
            "quantitative_evidence_assessment_v1",

        "patch":
            "4.6.9K",

        "status":
            "QUANTITATIVE_EVIDENCE_ASSESSMENT_COMPLETE",

        "quantitative_sections":
            assessed_sections,

        "quantitative_claim_units":
            assessed_units,

        "quantitative_candidates":
            assessed_candidates,

        "quantitative_evidence_summary": {
            "candidate_count":
                len(
                    assessed_candidates
                ),

            "strong_quantitative_evidence_count":
                strong_count,

            "moderate_quantitative_evidence_count":
                moderate_count,

            "limited_quantitative_evidence_count":
                limited_count,

            "insufficient_quantitative_evidence_count":
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
                "ARTICLE_LOCAL_QUANTITATIVE_EXPRESSION_EVIDENCE_ONLY",

            "scientific_truth_confidence_computed":
                False,

            "real_world_numeric_validity_verified":
                False,

            "final_referent_selected":
                False,

            "duplicate_resolution_performed":
                False,

            "derived_calculation_performed":
                False,

            "quantitative_inference_performed":
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
            "duplicate_redundant_quantitative_resolution",
    })

    return result



def resolve_duplicate_redundant_quantitative_relations_v1(
    evidence_assessment_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Resolve exact article-local duplicate quantitative candidates.

    Duplicate identity is deliberately conservative. It requires the
    same normalized quantitative form, role, unit structure,
    orientation, and referent-grounding identity.

    This stage does NOT:
    - use fuzzy semantic similarity,
    - merge different values,
    - merge different units,
    - merge percentage with percentile,
    - merge different ranges,
    - merge different rate denominators,
    - merge different quantitative roles,
    - merge different directional/comparison orientations,
    - guess among multiple grounding matches,
    - select a final quantitative referent,
    - perform unit conversion,
    - perform derived calculations,
    - infer unstated quantitative relations,
    - assess factual/scientific truth,
    - use external authority,
    - perform temporal reasoning,
    - perform new causal reasoning,
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
        raise QuantitativeIntelligenceError(
            "evidence_assessment_result must be a mapping."
        )

    if (
        evidence_assessment_result.get(
            "schema_version"
        )
        != "quantitative_evidence_assessment_v1"
    ):
        raise QuantitativeIntelligenceError(
            "Stage L requires quantitative_evidence_assessment_v1."
        )

    if (
        evidence_assessment_result.get(
            "status"
        )
        != "QUANTITATIVE_EVIDENCE_ASSESSMENT_COMPLETE"
    ):
        raise QuantitativeIntelligenceError(
            "Quantitative evidence assessment must be complete."
        )

    if (
        evidence_assessment_result.get(
            "phase"
        )
        != "4.6.9"
    ):
        raise QuantitativeIntelligenceError(
            "Stage L requires Phase 4.6.9 input."
        )

    if (
        evidence_assessment_result.get(
            "patch"
        )
        != "4.6.9K"
    ):
        raise QuantitativeIntelligenceError(
            "Stage L requires canonical 4.6.9K input."
        )

    if (
        evidence_assessment_result.get(
            "next_stage"
        )
        != "duplicate_redundant_quantitative_resolution"
    ):
        raise QuantitativeIntelligenceError(
            "Stage K must hand off to duplicate_redundant_quantitative_resolution."
        )

    if (
        evidence_assessment_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise QuantitativeIntelligenceError(
            "Quantitative Intelligence must remain transient."
        )

    def normalize_text(
        value: Any,
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
            r"[^a-z0-9.%'+/-]+",
            " ",
            value,
        )

        return re.sub(
            r"\s+",
            " ",
            value,
        ).strip()

    def stable_value(
        value: Any,
    ) -> str:
        if isinstance(
            value,
            float,
        ):
            return format(
                value,
                ".12g",
            )

        if isinstance(
            value,
            (int, str),
        ):
            return str(
                value
            )

        if value is None:
            return ""

        return json.dumps(
            value,
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
            ensure_ascii=False,
        )

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

        if not isinstance(
            match_count,
            int,
        ):
            raise QuantitativeIntelligenceError(
                "Quantitative grounding match count must be an integer."
            )

        if match_count != len(
            matches
        ):
            raise QuantitativeIntelligenceError(
                "Quantitative grounding match count mismatch."
            )

        if status == "GROUNDED_SINGLE_MATCH":
            if match_count != 1:
                raise QuantitativeIntelligenceError(
                    "Single-grounded quantitative candidate must have exactly one grounding match."
                )

            grounding = matches[
                0
            ]

            if not isinstance(
                grounding,
                Mapping,
            ):
                raise QuantitativeIntelligenceError(
                    "Quantitative grounding match must be a mapping."
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
                raise QuantitativeIntelligenceError(
                    "Single-grounded candidate is missing canonical grounding text."
                )

            if semantic_kind not in {
                "entity",
                "concept",
            }:
                raise QuantitativeIntelligenceError(
                    "Single-grounded candidate has invalid semantic kind."
                )

            return (
                semantic_kind,
                canonical_text,
            )

        if status == "UNGROUNDED":
            if match_count != 0:
                raise QuantitativeIntelligenceError(
                    "UNGROUNDED quantitative candidate cannot contain grounding matches."
                )

            return None

        if status == "GROUNDED_MULTIPLE_MATCHES":
            if match_count < 2:
                raise QuantitativeIntelligenceError(
                    "Multiple-grounded candidate requires at least two grounding matches."
                )

            return None

        raise QuantitativeIntelligenceError(
            "Candidate has invalid quantitative grounding status."
        )

    def duplicate_key(
        candidate: Mapping[str, Any],
    ) -> tuple[str, ...] | None:
        if (
            candidate.get(
                "final_quantitative_expression_validated"
            )
            is not True
        ):
            return None

        if (
            candidate.get(
                "normalization_status"
            )
            != "NORMALIZED"
        ):
            return None

        if (
            candidate.get(
                "quantity_role_orientation_resolved"
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

        # Multiple grounding matches remain referentially ambiguous.
        # Do not merge them automatically.
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

        quantity_role = normalize_text(
            candidate.get(
                "canonical_quantity_role"
            )
        )

        quantitative_scale = normalize_text(
            candidate.get(
                "quantitative_scale"
            )
        )

        normalized_value = stable_value(
            candidate.get(
                "normalized_value"
            )
        )

        normalized_values = stable_value(
            candidate.get(
                "normalized_values"
            )
        )

        canonical_unit = normalize_text(
            candidate.get(
                "canonical_unit"
            )
        )

        measurement_family = normalize_text(
            candidate.get(
                "measurement_family"
            )
        )

        rate_denominator_unit = normalize_text(
            candidate.get(
                "rate_denominator_unit"
            )
        )

        multiplicative_factor = stable_value(
            candidate.get(
                "multiplicative_factor"
            )
        )

        direction = normalize_text(
            candidate.get(
                "quantitative_direction"
            )
        )

        comparison_orientation = normalize_text(
            candidate.get(
                "comparison_orientation"
            )
        )

        contextual_ambiguity = (
            candidate.get(
                "contextual_assignment_ambiguous"
            )
            is True
        )

        if (
            not signal_type
            or not quantity_role
            or not quantitative_scale
        ):
            return None

        if (
            not normalized_value
            and not normalized_values
        ):
            return None

        if grounding is None:
            # Without an identified semantic referent, only exact
            # source-sentence identity may be safely deduplicated.
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
            quantity_role,
            quantitative_scale,
            normalized_value,
            normalized_values,
            canonical_unit,
            measurement_family,
            rate_denominator_unit,
            multiplicative_factor,
            direction,
            comparison_orientation,
            "ambiguous"
            if contextual_ambiguity
            else "unambiguous",
            grounding_kind,
            grounding_text,
        )

    source_candidates = list(
        evidence_assessment_result.get(
            "quantitative_candidates"
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
            raise QuantitativeIntelligenceError(
                "Every quantitative candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "quantitative_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise QuantitativeIntelligenceError(
                "Quantitative candidate ID is required."
            )

        if candidate_id in seen_candidate_ids:
            raise QuantitativeIntelligenceError(
                "Duplicate quantitative candidate ID encountered."
            )

        seen_candidate_ids.add(
            candidate_id
        )

        if (
            candidate.get(
                "quantitative_evidence_assessed"
            )
            is not True
        ):
            raise QuantitativeIntelligenceError(
                "Every quantitative candidate must have completed evidence assessment."
            )

        if (
            candidate.get(
                "duplicate_resolution_performed"
            )
            is True
        ):
            raise QuantitativeIntelligenceError(
                "Candidate must not already have duplicate resolution."
            )

        if (
            candidate.get(
                "final_quantitative_referent_selected"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Stage L must not receive a selected final quantitative referent."
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
                            "quantitative_evidence_strength"
                        )
                        or ""
                    ),
                    0,
                ),
                -float(
                    candidate.get(
                        "quantitative_evidence_score"
                    )
                    or 0.0
                ),
                0
                if candidate.get(
                    "same_sentence_quantitative_valid"
                )
                is True
                else 1,
                0
                if candidate.get(
                    "adjacent_quantitative_support_present"
                )
                is True
                else 1,
                str(
                    candidate.get(
                        "quantitative_candidate_id"
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
                    "quantitative_candidate_id"
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
            "quantitative_duplicate_group_"
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
                "quantitative_candidate_id"
            )
        )

        for index, member in enumerate(
            ordered
        ):
            member_id = str(
                member.get(
                    "quantitative_candidate_id"
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

                "quantitative_duplicate_group_id":
                    group_id,

                "quantitative_duplicate_group_size":
                    len(
                        ordered
                    ),

                "quantitative_duplicate_member_ids":
                    member_ids,

                "is_quantitative_duplicate_group":
                    is_duplicate_group,

                "is_representative_quantitative_expression":
                    is_representative,

                "representative_quantitative_candidate_id":
                    representative_id,

                "duplicate_of_quantitative_candidate_id":
                    (
                        None
                        if is_representative
                        else representative_id
                    ),

                "quantitative_duplicate_resolution_status":
                    (
                        "REPRESENTATIVE"
                        if is_representative
                        else "DUPLICATE_REDUNDANT"
                    ),

                "quantitative_duplicate_key": {
                    "signal_type":
                        key[
                            0
                        ],

                    "canonical_quantity_role":
                        key[
                            1
                        ],

                    "quantitative_scale":
                        key[
                            2
                        ],

                    "normalized_value":
                        key[
                            3
                        ],

                    "normalized_values":
                        key[
                            4
                        ],

                    "canonical_unit":
                        key[
                            5
                        ],

                    "measurement_family":
                        key[
                            6
                        ],

                    "rate_denominator_unit":
                        key[
                            7
                        ],

                    "multiplicative_factor":
                        key[
                            8
                        ],

                    "quantitative_direction":
                        key[
                            9
                        ],

                    "comparison_orientation":
                        key[
                            10
                        ],

                    "contextual_assignment":
                        key[
                            11
                        ],

                    "grounding_identity_kind":
                        key[
                            12
                        ],

                    "grounding_identity":
                        key[
                            13
                        ],
                },

                "exact_canonical_quantitative_identity_used":
                    True,

                "different_values_merged":
                    False,

                "different_units_merged":
                    False,

                "different_quantitative_roles_merged":
                    False,

                "different_ranges_merged":
                    False,

                "different_rate_denominators_merged":
                    False,

                "different_directions_merged":
                    False,

                "different_comparison_orientations_merged":
                    False,

                "multiple_grounding_guessing_performed":
                    False,

                "fuzzy_similarity_performed":
                    False,

                "final_quantitative_referent_selected":
                    False,

                "selected_quantitative_referent":
                    None,

                "derived_calculation_performed":
                    False,

                "quantitative_inference_performed":
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
                "quantitative_candidate_id"
            )
        )

        resolved = dict(
            member
        )

        resolved.update({
            "duplicate_resolution_performed":
                True,

            "quantitative_duplicate_group_id":
                None,

            "quantitative_duplicate_group_size":
                1,

            "quantitative_duplicate_member_ids": [
                member_id,
            ],

            "is_quantitative_duplicate_group":
                False,

            "is_representative_quantitative_expression":
                True,

            "representative_quantitative_candidate_id":
                member_id,

            "duplicate_of_quantitative_candidate_id":
                None,

            "quantitative_duplicate_resolution_status":
                "UNIQUE_NON_GROUPABLE",

            "quantitative_duplicate_key":
                None,

            "exact_canonical_quantitative_identity_used":
                False,

            "different_values_merged":
                False,

            "different_units_merged":
                False,

            "different_quantitative_roles_merged":
                False,

            "different_ranges_merged":
                False,

            "different_rate_denominators_merged":
                False,

            "different_directions_merged":
                False,

            "different_comparison_orientations_merged":
                False,

            "multiple_grounding_guessing_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "final_quantitative_referent_selected":
                False,

            "selected_quantitative_referent":
                None,

            "derived_calculation_performed":
                False,

            "quantitative_inference_performed":
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
                "quantitative_candidate_id"
            )
        )

        resolved = resolved_by_id.get(
            candidate_id
        )

        if resolved is None:
            raise QuantitativeIntelligenceError(
                "Duplicate quantitative resolution lost a candidate."
            )

        resolved_candidates.append(
            resolved
        )

    representative_candidates.sort(
        key=lambda candidate: str(
            candidate.get(
                "quantitative_candidate_id"
            )
            or ""
        )
    )

    resolved_units = []

    for unit in (
        evidence_assessment_result.get(
            "quantitative_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every Quantitative Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "quantitative_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "quantitative_evidence_assessment"
            )
            != "COMPLETE"
        ):
            raise QuantitativeIntelligenceError(
                "Quantitative evidence assessment must be COMPLETE before Stage L."
            )

        if (
            state.get(
                "duplicate_quantitative_resolution"
            )
            != "PENDING"
        ):
            raise QuantitativeIntelligenceError(
                "Duplicate quantitative resolution must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "quantitative_evidence_assessment_performed"
            )
            is not True
        ):
            raise QuantitativeIntelligenceError(
                "Stage-K quantitative evidence boundary must be complete."
            )

        if (
            boundaries.get(
                "duplicate_quantitative_resolution_performed"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Duplicate quantitative resolution boundary must be False before Stage L."
            )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "quantitative_candidates"
            )
            or []
        ):
            candidate_id = old_candidate.get(
                "quantitative_candidate_id"
            )

            resolved_candidate = (
                resolved_by_id.get(
                    candidate_id
                )
            )

            if resolved_candidate is None:
                raise QuantitativeIntelligenceError(
                    "Quantitative candidate/unit duplicate mismatch."
                )

            unit_candidates.append(
                resolved_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "duplicate_quantitative_resolution"
        ] = "COMPLETE"

        updated_boundaries = dict(
            boundaries
        )

        updated_boundaries[
            "duplicate_quantitative_resolution_performed"
        ] = True

        updated_boundaries[
            "fuzzy_similarity_performed"
        ] = False

        updated_boundaries[
            "derived_calculation_performed"
        ] = False

        updated_boundaries[
            "quantitative_inference_performed"
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
            "quantitative_candidates":
                unit_candidates,

            "representative_quantitative_expression_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "is_representative_quantitative_expression"
                    )
                    is True
                ),

            "duplicate_redundant_quantitative_expression_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "quantitative_duplicate_resolution_status"
                    )
                    == "DUPLICATE_REDUNDANT"
                ),

            "quantitative_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        resolved_units.append(
            updated_unit
        )

    resolved_units_by_id = {
        unit.get(
            "quantitative_claim_unit_id"
        ):
            unit
        for unit in resolved_units
    }

    resolved_sections = []

    for section in (
        evidence_assessment_result.get(
            "quantitative_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every quantitative section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "quantitative_claim_units"
            )
            or []
        ):
            unit_id = old_unit.get(
                "quantitative_claim_unit_id"
            )

            resolved_unit = (
                resolved_units_by_id.get(
                    unit_id
                )
            )

            if resolved_unit is None:
                raise QuantitativeIntelligenceError(
                    "Quantitative section/unit duplicate mismatch."
                )

            section_units.append(
                resolved_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "quantitative_candidates"
                )
                or []
            )
        ]

        resolved_sections.append({
            **dict(
                section
            ),

            "quantitative_claim_units":
                section_units,

            "quantitative_candidates":
                section_candidates,

            "representative_quantitative_expression_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "is_representative_quantitative_expression"
                    )
                    is True
                ),

            "duplicate_redundant_quantitative_expression_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "quantitative_duplicate_resolution_status"
                    )
                    == "DUPLICATE_REDUNDANT"
                ),

            "duplicate_quantitative_resolution_complete":
                True,
        })

    representative_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "is_representative_quantitative_expression"
        )
        is True
    )

    redundant_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "quantitative_duplicate_resolution_status"
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
            "quantitative_duplicate_resolution_status"
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

    boundaries[
        "duplicate_quantitative_resolution_performed"
    ] = True

    boundaries[
        "fuzzy_similarity_performed"
    ] = False

    boundaries[
        "derived_calculation_performed"
    ] = False

    boundaries[
        "quantitative_inference_performed"
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
            "quantitative_duplicate_resolution_v1",

        "patch":
            "4.6.9L",

        "status":
            "QUANTITATIVE_DUPLICATE_RESOLUTION_COMPLETE",

        "quantitative_sections":
            resolved_sections,

        "quantitative_claim_units":
            resolved_units,

        "quantitative_candidates":
            resolved_candidates,

        "representative_quantitative_candidates":
            representative_candidates,

        "quantitative_duplicate_resolution_summary": {
            "candidate_count":
                len(
                    resolved_candidates
                ),

            "representative_quantitative_expression_count":
                representative_count,

            "duplicate_redundant_quantitative_expression_count":
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
                "canonical_quantity_role",
                "quantitative_scale",
                "normalized_value",
                "normalized_values",
                "canonical_unit",
                "measurement_family",
                "rate_denominator_unit",
                "multiplicative_factor",
                "quantitative_direction",
                "comparison_orientation",
                "contextual_assignment",
                "grounding_identity",
            ],

            "different_values_merged":
                False,

            "different_units_merged":
                False,

            "percentage_percentile_merged":
                False,

            "different_ranges_merged":
                False,

            "different_rate_denominators_merged":
                False,

            "different_quantitative_roles_merged":
                False,

            "different_directions_merged":
                False,

            "different_comparison_orientations_merged":
                False,

            "multiple_grounding_auto_merge_performed":
                False,

            "ungrounded_cross_sentence_merge_performed":
                False,

            "strongest_evidence_representative_selected":
                True,

            "duplicate_provenance_preserved":
                True,

            "final_referent_selection_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "unit_conversion_performed":
                False,

            "derived_calculation_performed":
                False,

            "quantitative_inference_performed":
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
            "article_quantitative_consolidation",
    })

    return result



def consolidate_article_quantitative_intelligence_v1(
    duplicate_resolution_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Consolidate completed article-local Quantitative Intelligence into
    article-level and section-level summaries.

    Only representative quantitative expressions are included in the
    canonical consolidated quantitative set. Full candidate provenance
    remains preserved in the complete source candidate collection.

    This stage does NOT:
    - create new quantitative expressions,
    - infer missing quantities,
    - calculate totals, averages, rates, or trends,
    - perform unit conversion,
    - merge different quantitative identities,
    - select a final quantitative referent,
    - strengthen evidence classifications,
    - infer temporal relationships,
    - perform new causal reasoning,
    - establish factual, scientific, medical, or statistical truth,
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
        raise QuantitativeIntelligenceError(
            "duplicate_resolution_result must be a mapping."
        )

    if (
        duplicate_resolution_result.get(
            "schema_version"
        )
        != "quantitative_duplicate_resolution_v1"
    ):
        raise QuantitativeIntelligenceError(
            "Stage M requires quantitative_duplicate_resolution_v1."
        )

    if (
        duplicate_resolution_result.get(
            "status"
        )
        != "QUANTITATIVE_DUPLICATE_RESOLUTION_COMPLETE"
    ):
        raise QuantitativeIntelligenceError(
            "Duplicate quantitative resolution must be complete."
        )

    if (
        duplicate_resolution_result.get(
            "phase"
        )
        != "4.6.9"
    ):
        raise QuantitativeIntelligenceError(
            "Stage M requires Phase 4.6.9 input."
        )

    if (
        duplicate_resolution_result.get(
            "patch"
        )
        != "4.6.9L"
    ):
        raise QuantitativeIntelligenceError(
            "Stage M requires canonical 4.6.9L input."
        )

    if (
        duplicate_resolution_result.get(
            "next_stage"
        )
        != "article_quantitative_consolidation"
    ):
        raise QuantitativeIntelligenceError(
            "Stage L must hand off to article_quantitative_consolidation."
        )

    if (
        duplicate_resolution_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise QuantitativeIntelligenceError(
            "Quantitative Intelligence must remain transient."
        )

    source_candidates = list(
        duplicate_resolution_result.get(
            "quantitative_candidates"
        )
        or []
    )

    representative_candidates = list(
        duplicate_resolution_result.get(
            "representative_quantitative_candidates"
        )
        or []
    )

    seen_source_ids = set()

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every quantitative candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "quantitative_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise QuantitativeIntelligenceError(
                "Quantitative candidate ID is required."
            )

        if candidate_id in seen_source_ids:
            raise QuantitativeIntelligenceError(
                "Duplicate quantitative candidate ID encountered."
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
            raise QuantitativeIntelligenceError(
                "All quantitative candidates must complete duplicate resolution before Stage M."
            )

    representative_ids = []

    seen_representative_ids = set()

    for candidate in representative_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every representative quantitative expression must be a mapping."
            )

        if (
            candidate.get(
                "is_representative_quantitative_expression"
            )
            is not True
        ):
            raise QuantitativeIntelligenceError(
                "Representative quantitative list contains a non-representative candidate."
            )

        candidate_id = str(
            candidate.get(
                "quantitative_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise QuantitativeIntelligenceError(
                "Representative quantitative candidate ID is required."
            )

        if candidate_id in seen_representative_ids:
            raise QuantitativeIntelligenceError(
                "Duplicate representative quantitative candidate ID encountered."
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
                "quantitative_candidate_id"
            )
            or ""
        )
        for candidate in source_candidates
        if candidate.get(
            "is_representative_quantitative_expression"
        )
        is True
    }

    if set(
        representative_ids
    ) != expected_representative_ids:
        raise QuantitativeIntelligenceError(
            "Representative quantitative list does not match resolved candidates."
        )

    signal_type_counts = {}
    quantity_role_counts = {}
    quantitative_scale_counts = {}
    measurement_family_counts = {}
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

    comparison_count = 0
    directional_count = 0

    consolidated_quantitative_expressions = []

    for candidate in representative_candidates:
        signal_type = str(
            candidate.get(
                "signal_type"
            )
            or "UNSPECIFIED"
        )

        quantity_role = str(
            candidate.get(
                "canonical_quantity_role"
            )
            or "UNSPECIFIED"
        )

        quantitative_scale = str(
            candidate.get(
                "quantitative_scale"
            )
            or "UNSPECIFIED"
        )

        measurement_family = str(
            candidate.get(
                "measurement_family"
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
                "quantitative_evidence_strength"
            )
            or "INSUFFICIENT"
        )

        if evidence_strength not in evidence_strength_counts:
            raise QuantitativeIntelligenceError(
                "Representative candidate has invalid quantitative evidence strength."
            )

        final_validated = (
            candidate.get(
                "final_quantitative_expression_validated"
            )
            is True
        )

        same_sentence_valid = (
            candidate.get(
                "same_sentence_quantitative_valid"
            )
            is True
        )

        cross_sentence_valid = (
            candidate.get(
                "cross_sentence_quantitative_valid"
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
        )

        comparison_present = (
            candidate.get(
                "comparison_present"
            )
            is True
        )

        directional_present = (
            candidate.get(
                "directional_change_present"
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

        quantity_role_counts[
            quantity_role
        ] = (
            quantity_role_counts.get(
                quantity_role,
                0,
            )
            + 1
        )

        quantitative_scale_counts[
            quantitative_scale
        ] = (
            quantitative_scale_counts.get(
                quantitative_scale,
                0,
            )
            + 1
        )

        measurement_family_counts[
            measurement_family
        ] = (
            measurement_family_counts.get(
                measurement_family,
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

        if comparison_present:
            comparison_count += 1

        if directional_present:
            directional_count += 1

        consolidated_quantitative_expressions.append({
            "quantitative_candidate_id":
                candidate.get(
                    "quantitative_candidate_id"
                ),

            "signal_type":
                candidate.get(
                    "signal_type"
                ),

            "canonical_quantity_role":
                candidate.get(
                    "canonical_quantity_role"
                ),

            "quantitative_scale":
                candidate.get(
                    "quantitative_scale"
                ),

            "normalized_value":
                candidate.get(
                    "normalized_value"
                ),

            "normalized_values":
                candidate.get(
                    "normalized_values"
                ),

            "canonical_unit":
                candidate.get(
                    "canonical_unit"
                ),

            "unit_symbol":
                candidate.get(
                    "unit_symbol"
                ),

            "measurement_family":
                candidate.get(
                    "measurement_family"
                ),

            "rate_denominator_unit":
                candidate.get(
                    "rate_denominator_unit"
                ),

            "rate_denominator_symbol":
                candidate.get(
                    "rate_denominator_symbol"
                ),

            "multiplicative_factor":
                candidate.get(
                    "multiplicative_factor"
                ),

            "quantitative_direction":
                candidate.get(
                    "quantitative_direction"
                ),

            "comparison_orientation":
                candidate.get(
                    "comparison_orientation"
                ),

            "comparison_present":
                comparison_present,

            "directional_change_present":
                directional_present,

            "contextual_assignment_ambiguous":
                contextual_ambiguity,

            "grounding_status":
                grounding_status,

            "entity_concept_grounded":
                grounded,

            "entity_concept_grounding_match_count":
                candidate.get(
                    "entity_concept_grounding_match_count"
                ),

            "final_quantitative_expression_validated":
                final_validated,

            "same_sentence_quantitative_valid":
                same_sentence_valid,

            "cross_sentence_quantitative_valid":
                cross_sentence_valid,

            "quantitative_evidence_score":
                candidate.get(
                    "quantitative_evidence_score"
                ),

            "quantitative_evidence_strength":
                evidence_strength,

            "quantitative_evidence_basis":
                candidate.get(
                    "quantitative_evidence_basis"
                ),

            "quantitative_confidence_cap_applied":
                candidate.get(
                    "quantitative_confidence_cap_applied"
                ),

            "section_id":
                candidate.get(
                    "section_id"
                ),

            "sentence_id":
                candidate.get(
                    "sentence_id"
                ),

            "quantitative_duplicate_group_id":
                candidate.get(
                    "quantitative_duplicate_group_id"
                ),

            "quantitative_duplicate_group_size":
                candidate.get(
                    "quantitative_duplicate_group_size"
                ),

            "final_quantitative_referent_selected":
                False,

            "selected_quantitative_referent":
                None,

            "quantitative_role_preserved":
                candidate.get(
                    "quantitative_role_preserved"
                )
                is True,

            "quantitative_normalization_preserved":
                candidate.get(
                    "quantitative_normalization_preserved"
                )
                is True,

            "contextual_ambiguity_promoted_to_strong":
                False,

            "multiple_grounding_matches_promoted_to_strong":
                False,

            "cross_sentence_expression_promoted_to_strong":
                False,

            "derived_calculation_performed":
                False,

            "quantitative_inference_performed":
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

    consolidated_quantitative_expressions.sort(
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
                    "canonical_quantity_role"
                )
                or ""
            ),
            str(
                expression.get(
                    "normalized_value"
                )
                or expression.get(
                    "normalized_values"
                )
                or ""
            ),
            str(
                expression.get(
                    "canonical_unit"
                )
                or ""
            ),
            str(
                expression.get(
                    "quantitative_candidate_id"
                )
                or ""
            ),
        )
    )

    consolidated_sections = []

    seen_section_ids = set()

    for section in (
        duplicate_resolution_result.get(
            "quantitative_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every quantitative section must be a mapping."
            )

        section_id = str(
            section.get(
                "section_id"
            )
            or ""
        )

        if not section_id:
            raise QuantitativeIntelligenceError(
                "Quantitative section ID is required."
            )

        if section_id in seen_section_ids:
            raise QuantitativeIntelligenceError(
                "Duplicate quantitative section ID encountered."
            )

        seen_section_ids.add(
            section_id
        )

        section_expressions = [
            expression
            for expression in consolidated_quantitative_expressions
            if str(
                expression.get(
                    "section_id"
                )
                or ""
            )
            == section_id
        ]

        section_signal_counts = {}
        section_role_counts = {}
        section_scale_counts = {}
        section_measurement_family_counts = {}
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

            quantity_role = str(
                expression.get(
                    "canonical_quantity_role"
                )
                or "UNSPECIFIED"
            )

            quantitative_scale = str(
                expression.get(
                    "quantitative_scale"
                )
                or "UNSPECIFIED"
            )

            measurement_family = str(
                expression.get(
                    "measurement_family"
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
                    "quantitative_evidence_strength"
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

            section_role_counts[
                quantity_role
            ] = (
                section_role_counts.get(
                    quantity_role,
                    0,
                )
                + 1
            )

            section_scale_counts[
                quantitative_scale
            ] = (
                section_scale_counts.get(
                    quantitative_scale,
                    0,
                )
                + 1
            )

            section_measurement_family_counts[
                measurement_family
            ] = (
                section_measurement_family_counts.get(
                    measurement_family,
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

            "representative_quantitative_expressions":
                section_expressions,

            "representative_quantitative_expression_count":
                len(
                    section_expressions
                ),

            "validated_quantitative_expression_count":
                sum(
                    1
                    for expression in section_expressions
                    if expression.get(
                        "final_quantitative_expression_validated"
                    )
                    is True
                ),

            "unvalidated_quantitative_expression_count":
                sum(
                    1
                    for expression in section_expressions
                    if expression.get(
                        "final_quantitative_expression_validated"
                    )
                    is False
                ),

            "same_sentence_validated_quantitative_count":
                sum(
                    1
                    for expression in section_expressions
                    if expression.get(
                        "same_sentence_quantitative_valid"
                    )
                    is True
                ),

            "cross_sentence_validated_quantitative_count":
                sum(
                    1
                    for expression in section_expressions
                    if expression.get(
                        "cross_sentence_quantitative_valid"
                    )
                    is True
                ),

            "grounded_quantitative_expression_count":
                sum(
                    1
                    for expression in section_expressions
                    if expression.get(
                        "entity_concept_grounded"
                    )
                    is True
                ),

            "ungrounded_quantitative_expression_count":
                sum(
                    1
                    for expression in section_expressions
                    if expression.get(
                        "entity_concept_grounded"
                    )
                    is False
                ),

            "contextually_ambiguous_quantitative_count":
                sum(
                    1
                    for expression in section_expressions
                    if expression.get(
                        "contextual_assignment_ambiguous"
                    )
                    is True
                ),

            "comparison_quantitative_expression_count":
                sum(
                    1
                    for expression in section_expressions
                    if expression.get(
                        "comparison_present"
                    )
                    is True
                ),

            "directional_quantitative_expression_count":
                sum(
                    1
                    for expression in section_expressions
                    if expression.get(
                        "directional_change_present"
                    )
                    is True
                ),

            "quantitative_signal_type_counts":
                section_signal_counts,

            "canonical_quantity_role_counts":
                section_role_counts,

            "quantitative_scale_counts":
                section_scale_counts,

            "measurement_family_counts":
                section_measurement_family_counts,

            "grounding_status_counts":
                section_grounding_status_counts,

            "quantitative_evidence_strength_counts":
                section_strength_counts,

            "quantitative_consolidation_complete":
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
            "quantitative_duplicate_resolution_status"
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

    boundaries[
        "article_quantitative_consolidation_performed"
    ] = True

    boundaries[
        "new_quantitative_expression_inference_performed"
    ] = False

    boundaries[
        "derived_calculation_performed"
    ] = False

    boundaries[
        "unit_conversion_performed"
    ] = False

    boundaries[
        "trend_inference_performed"
    ] = False

    boundaries[
        "aggregate_calculation_performed"
    ] = False

    boundaries[
        "final_quantitative_referent_selection_performed"
    ] = False

    boundaries[
        "quantitative_evidence_strengthening_performed"
    ] = False

    boundaries[
        "quantitative_inference_performed"
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
            "quantitative_article_consolidation_v1",

        "patch":
            "4.6.9M",

        "status":
            "QUANTITATIVE_ARTICLE_CONSOLIDATION_COMPLETE",

        "consolidated_quantitative_sections":
            consolidated_sections,

        "consolidated_quantitative_expressions":
            consolidated_quantitative_expressions,

        "article_quantitative_summary": {
            "total_candidate_count":
                total_candidate_count,

            "representative_quantitative_expression_count":
                representative_count,

            "duplicate_redundant_quantitative_expression_count":
                redundant_count,

            "validated_quantitative_expression_count":
                validated_count,

            "unvalidated_quantitative_expression_count":
                unvalidated_count,

            "same_sentence_validated_quantitative_count":
                same_sentence_validated_count,

            "cross_sentence_validated_quantitative_count":
                cross_sentence_validated_count,

            "grounded_quantitative_expression_count":
                grounded_count,

            "ungrounded_quantitative_expression_count":
                ungrounded_count,

            "contextually_ambiguous_quantitative_count":
                contextual_ambiguous_count,

            "contextually_unambiguous_quantitative_count":
                contextual_unambiguous_count,

            "comparison_quantitative_expression_count":
                comparison_count,

            "directional_quantitative_expression_count":
                directional_count,

            "quantitative_signal_type_counts":
                signal_type_counts,

            "canonical_quantity_role_counts":
                quantity_role_counts,

            "quantitative_scale_counts":
                quantitative_scale_counts,

            "measurement_family_counts":
                measurement_family_counts,

            "grounding_status_counts":
                grounding_status_counts,

            "quantitative_evidence_strength_counts":
                evidence_strength_counts,

            "representative_count_matches_consolidated":
                (
                    representative_count
                    == len(
                        consolidated_quantitative_expressions
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

            "quantitative_values_preserved":
                True,

            "quantitative_units_preserved":
                True,

            "quantitative_roles_preserved":
                True,

            "quantitative_orientation_preserved":
                True,

            "evidence_strengths_preserved":
                True,

            "final_referent_selection_performed":
                False,

            "new_quantitative_expression_inference_performed":
                False,

            "derived_calculation_performed":
                False,

            "unit_conversion_performed":
                False,

            "trend_inference_performed":
                False,

            "aggregate_calculation_performed":
                False,

            "quantitative_evidence_strengthening_performed":
                False,

            "quantitative_inference_performed":
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
            "final_quantitative_intelligence_result",
    })

    return result



def build_final_quantitative_intelligence_result_v1(
    article_consolidation_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Build the final canonical Phase 4.6.9 Quantitative Intelligence result.

    This stage packages the completed article-local quantitative analysis
    without adding new interpretation.

    It does NOT:
    - certify the result,
    - create or infer quantitative expressions,
    - calculate derived values,
    - calculate totals or averages,
    - infer trends,
    - convert units,
    - select a final quantitative referent,
    - strengthen quantitative evidence,
    - infer temporal relationships,
    - perform new causal reasoning,
    - establish factual, scientific, medical, or statistical truth,
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
        raise QuantitativeIntelligenceError(
            "article_consolidation_result must be a mapping."
        )

    if (
        article_consolidation_result.get(
            "schema_version"
        )
        != "quantitative_article_consolidation_v1"
    ):
        raise QuantitativeIntelligenceError(
            "Stage N requires quantitative_article_consolidation_v1."
        )

    if (
        article_consolidation_result.get(
            "status"
        )
        != "QUANTITATIVE_ARTICLE_CONSOLIDATION_COMPLETE"
    ):
        raise QuantitativeIntelligenceError(
            "Article quantitative consolidation must be complete."
        )

    if (
        article_consolidation_result.get(
            "phase"
        )
        != "4.6.9"
    ):
        raise QuantitativeIntelligenceError(
            "Stage N requires Phase 4.6.9 input."
        )

    if (
        article_consolidation_result.get(
            "patch"
        )
        != "4.6.9M"
    ):
        raise QuantitativeIntelligenceError(
            "Stage N requires canonical 4.6.9M input."
        )

    if (
        article_consolidation_result.get(
            "next_stage"
        )
        != "final_quantitative_intelligence_result"
    ):
        raise QuantitativeIntelligenceError(
            "Stage M must hand off to final_quantitative_intelligence_result."
        )

    if (
        article_consolidation_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise QuantitativeIntelligenceError(
            "Quantitative Intelligence must remain transient."
        )

    consolidated_expressions = list(
        article_consolidation_result.get(
            "consolidated_quantitative_expressions"
        )
        or []
    )

    consolidated_sections = list(
        article_consolidation_result.get(
            "consolidated_quantitative_sections"
        )
        or []
    )

    full_candidates = list(
        article_consolidation_result.get(
            "quantitative_candidates"
        )
        or []
    )

    representative_candidates = list(
        article_consolidation_result.get(
            "representative_quantitative_candidates"
        )
        or []
    )

    summary = dict(
        article_consolidation_result.get(
            "article_quantitative_summary"
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
        "quantitative_values_preserved",
        "quantitative_units_preserved",
        "quantitative_roles_preserved",
        "quantitative_orientation_preserved",
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
            raise QuantitativeIntelligenceError(
                field_name
                + " must be True before final Quantitative Intelligence packaging."
            )

    required_false_summary_fields = (
        "final_referent_selection_performed",
        "new_quantitative_expression_inference_performed",
        "derived_calculation_performed",
        "unit_conversion_performed",
        "trend_inference_performed",
        "aggregate_calculation_performed",
        "quantitative_evidence_strengthening_performed",
        "quantitative_inference_performed",
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
            raise QuantitativeIntelligenceError(
                field_name
                + " must remain False before final Quantitative Intelligence packaging."
            )

    consolidated_ids = set()

    for expression in consolidated_expressions:
        if not isinstance(
            expression,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every consolidated quantitative expression must be a mapping."
            )

        candidate_id = str(
            expression.get(
                "quantitative_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise QuantitativeIntelligenceError(
                "Consolidated quantitative candidate ID is required."
            )

        if candidate_id in consolidated_ids:
            raise QuantitativeIntelligenceError(
                "Duplicate consolidated quantitative candidate ID encountered."
            )

        consolidated_ids.add(
            candidate_id
        )

        if (
            expression.get(
                "final_quantitative_referent_selected"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Final Quantitative Intelligence must not select a quantitative referent."
            )

        if (
            expression.get(
                "selected_quantitative_referent"
            )
            is not None
        ):
            raise QuantitativeIntelligenceError(
                "Selected quantitative referent must remain None."
            )

        if (
            expression.get(
                "contextual_ambiguity_promoted_to_strong"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Contextual ambiguity must not be promoted to STRONG."
            )

        if (
            expression.get(
                "multiple_grounding_matches_promoted_to_strong"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Multiple-grounding expressions must not be promoted to STRONG."
            )

        if (
            expression.get(
                "cross_sentence_expression_promoted_to_strong"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Cross-sentence quantitative expressions must not be promoted to STRONG."
            )

        if (
            expression.get(
                "derived_calculation_performed"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Final Quantitative Intelligence must not perform derived calculations."
            )

        if (
            expression.get(
                "quantitative_inference_performed"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Final Quantitative Intelligence must not add quantitative inference."
            )

        if (
            expression.get(
                "temporal_reasoning_performed"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Final Quantitative Intelligence must not perform temporal reasoning."
            )

        if (
            expression.get(
                "new_causal_reasoning_performed"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Final Quantitative Intelligence must not perform new causal reasoning."
            )

        if (
            expression.get(
                "truth_assessed"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Quantitative Intelligence must not assess factual truth."
            )

        if (
            expression.get(
                "external_authority_checked"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Quantitative Intelligence must not use external authority."
            )

    representative_ids = {
        str(
            candidate.get(
                "quantitative_candidate_id"
            )
            or ""
        )
        for candidate in representative_candidates
    }

    if "" in representative_ids:
        raise QuantitativeIntelligenceError(
            "Representative quantitative candidate ID is required."
        )

    if representative_ids != consolidated_ids:
        raise QuantitativeIntelligenceError(
            "Final consolidated quantitative set must match representative candidates exactly."
        )

    boundaries = dict(
        article_consolidation_result.get(
            "processing_boundaries"
        )
        or {}
    )

    required_false_boundaries = (
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
            raise QuantitativeIntelligenceError(
                boundary_name
                + " must remain False in final Quantitative Intelligence."
            )

    if (
        boundaries.get(
            "article_quantitative_consolidation_performed"
        )
        is not True
    ):
        raise QuantitativeIntelligenceError(
            "Article quantitative consolidation boundary must be complete."
        )

    final_boundaries = dict(
        boundaries
    )

    final_boundaries[
        "final_quantitative_result_built"
    ] = True

    final_boundaries[
        "quantitative_certification_performed"
    ] = False

    result = {
        "schema_version":
            "quantitative_intelligence_result_v1",

        "quantitative_intelligence_version":
            article_consolidation_result.get(
                "quantitative_intelligence_version"
            )
            or "quantitative_intelligence_v1",

        "phase":
            "4.6.9",

        "patch":
            "4.6.9N",

        "status":
            "QUANTITATIVE_INTELLIGENCE_RESULT_COMPLETE",

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

        "consolidated_quantitative_expressions":
            consolidated_expressions,

        "consolidated_quantitative_sections":
            consolidated_sections,

        "representative_quantitative_candidates":
            representative_candidates,

        "quantitative_candidates":
            full_candidates,

        "quantitative_claim_units":
            list(
                article_consolidation_result.get(
                    "quantitative_claim_units"
                )
                or []
            ),

        "article_quantitative_summary":
            summary,

        "quantitative_boundaries": {
            "article_local_only":
                True,

            "scientific_truth_verified":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_checked":
                False,

            "new_quantitative_expression_inference_performed":
                False,

            "derived_calculation_performed":
                False,

            "unit_conversion_performed":
                False,

            "trend_inference_performed":
                False,

            "aggregate_calculation_performed":
                False,

            "final_quantitative_referent_selection_performed":
                False,

            "quantitative_evidence_strengthening_performed":
                False,

            "quantitative_inference_performed":
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
                "4.6.9O",
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "quantitative_intelligence_certification",
    }

    return result



def certify_quantitative_intelligence_v1(
    final_quantitative_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Certify the final Phase 4.6.9 Quantitative Intelligence result.

    Certification validates structure, accounting, provenance,
    quantitative-value integrity, unit integrity, quantity-role integrity,
    orientation integrity, evidence-strength caps, boundaries, and
    handoff readiness.

    Certification does NOT:
    - create or infer quantitative expressions,
    - calculate derived values,
    - calculate totals, averages, rates, or trends,
    - perform unit conversion,
    - select a final quantitative referent,
    - strengthen evidence classifications,
    - establish factual, scientific, medical, or statistical truth,
    - use external authority,
    - perform temporal reasoning,
    - perform new causal reasoning,
    - perform fuzzy similarity,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        final_quantitative_result,
        Mapping,
    ):
        raise QuantitativeIntelligenceError(
            "final_quantitative_result must be a mapping."
        )

    if (
        final_quantitative_result.get(
            "schema_version"
        )
        != "quantitative_intelligence_result_v1"
    ):
        raise QuantitativeIntelligenceError(
            "Stage O requires quantitative_intelligence_result_v1."
        )

    if (
        final_quantitative_result.get(
            "status"
        )
        != "QUANTITATIVE_INTELLIGENCE_RESULT_COMPLETE"
    ):
        raise QuantitativeIntelligenceError(
            "Final Quantitative Intelligence result must be complete."
        )

    if (
        final_quantitative_result.get(
            "phase"
        )
        != "4.6.9"
    ):
        raise QuantitativeIntelligenceError(
            "Stage O requires Phase 4.6.9 input."
        )

    if (
        final_quantitative_result.get(
            "patch"
        )
        != "4.6.9N"
    ):
        raise QuantitativeIntelligenceError(
            "Stage O requires canonical 4.6.9N input."
        )

    if (
        final_quantitative_result.get(
            "next_stage"
        )
        != "quantitative_intelligence_certification"
    ):
        raise QuantitativeIntelligenceError(
            "Stage N must hand off to quantitative_intelligence_certification."
        )

    if (
        final_quantitative_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise QuantitativeIntelligenceError(
            "Quantitative Intelligence must remain transient."
        )

    identity = dict(
        final_quantitative_result.get(
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
            raise QuantitativeIntelligenceError(
                "Required article identity field missing: "
                + field
            )

    consolidated_expressions = list(
        final_quantitative_result.get(
            "consolidated_quantitative_expressions"
        )
        or []
    )

    representative_candidates = list(
        final_quantitative_result.get(
            "representative_quantitative_candidates"
        )
        or []
    )

    full_candidates = list(
        final_quantitative_result.get(
            "quantitative_candidates"
        )
        or []
    )

    claim_units = list(
        final_quantitative_result.get(
            "quantitative_claim_units"
        )
        or []
    )

    consolidated_sections = list(
        final_quantitative_result.get(
            "consolidated_quantitative_sections"
        )
        or []
    )

    summary = dict(
        final_quantitative_result.get(
            "article_quantitative_summary"
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
        "quantitative_values_preserved",
        "quantitative_units_preserved",
        "quantitative_roles_preserved",
        "quantitative_orientation_preserved",
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
            raise QuantitativeIntelligenceError(
                field_name
                + " must be verified before Quantitative Intelligence certification."
            )

    if (
        summary.get(
            "representative_quantitative_expression_count"
        )
        != len(
            consolidated_expressions
        )
    ):
        raise QuantitativeIntelligenceError(
            "Consolidated quantitative expression count does not match summary."
        )

    if (
        len(
            representative_candidates
        )
        != len(
            consolidated_expressions
        )
    ):
        raise QuantitativeIntelligenceError(
            "Representative candidate count does not match consolidated quantitative expressions."
        )

    if (
        summary.get(
            "total_candidate_count"
        )
        != len(
            full_candidates
        )
    ):
        raise QuantitativeIntelligenceError(
            "Full quantitative candidate count does not match summary."
        )

    redundant_count = sum(
        1
        for candidate in full_candidates
        if candidate.get(
            "quantitative_duplicate_resolution_status"
        )
        == "DUPLICATE_REDUNDANT"
    )

    if (
        summary.get(
            "duplicate_redundant_quantitative_expression_count"
        )
        != redundant_count
    ):
        raise QuantitativeIntelligenceError(
            "Redundant quantitative candidate count does not match summary."
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
        raise QuantitativeIntelligenceError(
            "Quantitative representative/redundant accounting is invalid."
        )

    consolidated_ids = [
        str(
            expression.get(
                "quantitative_candidate_id"
            )
            or ""
        )
        for expression in consolidated_expressions
    ]

    representative_ids = [
        str(
            candidate.get(
                "quantitative_candidate_id"
            )
            or ""
        )
        for candidate in representative_candidates
    ]

    full_candidate_ids = [
        str(
            candidate.get(
                "quantitative_candidate_id"
            )
            or ""
        )
        for candidate in full_candidates
    ]

    if any(
        not candidate_id
        for candidate_id in consolidated_ids
    ):
        raise QuantitativeIntelligenceError(
            "Every consolidated quantitative expression requires a candidate ID."
        )

    if any(
        not candidate_id
        for candidate_id in representative_ids
    ):
        raise QuantitativeIntelligenceError(
            "Every representative quantitative candidate requires a candidate ID."
        )

    if any(
        not candidate_id
        for candidate_id in full_candidate_ids
    ):
        raise QuantitativeIntelligenceError(
            "Every quantitative candidate requires a candidate ID."
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
        raise QuantitativeIntelligenceError(
            "Duplicate consolidated quantitative candidate IDs are not allowed."
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
        raise QuantitativeIntelligenceError(
            "Duplicate representative quantitative candidate IDs are not allowed."
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
        raise QuantitativeIntelligenceError(
            "Duplicate full quantitative candidate IDs are not allowed."
        )

    if (
        set(
            consolidated_ids
        )
        != set(
            representative_ids
        )
    ):
        raise QuantitativeIntelligenceError(
            "Consolidated expressions and representative quantitative candidates disagree."
        )

    if not set(
        representative_ids
    ).issubset(
        set(
            full_candidate_ids
        )
    ):
        raise QuantitativeIntelligenceError(
            "Representative quantitative candidates must exist in the full candidate collection."
        )

    contextual_ambiguous_strong_count = 0
    multiple_grounding_strong_count = 0
    cross_sentence_strong_count = 0

    for expression in consolidated_expressions:
        if not isinstance(
            expression,
            Mapping,
        ):
            raise QuantitativeIntelligenceError(
                "Every consolidated quantitative expression must be a mapping."
            )

        if (
            expression.get(
                "final_quantitative_referent_selected"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Certified Quantitative Intelligence must not select a final referent."
            )

        if (
            expression.get(
                "selected_quantitative_referent"
            )
            is not None
        ):
            raise QuantitativeIntelligenceError(
                "Selected quantitative referent must remain None."
            )

        if (
            expression.get(
                "quantitative_role_preserved"
            )
            is not True
        ):
            raise QuantitativeIntelligenceError(
                "Every consolidated quantitative expression must preserve its quantity role."
            )

        if (
            expression.get(
                "quantitative_normalization_preserved"
            )
            is not True
        ):
            raise QuantitativeIntelligenceError(
                "Every consolidated quantitative expression must preserve normalization."
            )

        if (
            expression.get(
                "contextual_ambiguity_promoted_to_strong"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Contextual ambiguity promotion must remain prohibited."
            )

        if (
            expression.get(
                "multiple_grounding_matches_promoted_to_strong"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Multiple-grounding STRONG promotion must remain prohibited."
            )

        if (
            expression.get(
                "cross_sentence_expression_promoted_to_strong"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Cross-sentence STRONG promotion must remain prohibited."
            )

        if (
            expression.get(
                "derived_calculation_performed"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Certified Quantitative Intelligence must not perform derived calculations."
            )

        if (
            expression.get(
                "quantitative_inference_performed"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Certified Quantitative Intelligence must not add quantitative inference."
            )

        if (
            expression.get(
                "temporal_reasoning_performed"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Certified Quantitative Intelligence must not perform temporal reasoning."
            )

        if (
            expression.get(
                "new_causal_reasoning_performed"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Certified Quantitative Intelligence must not perform new causal reasoning."
            )

        if (
            expression.get(
                "truth_assessed"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Quantitative Intelligence must not assess factual truth."
            )

        if (
            expression.get(
                "external_authority_checked"
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                "Quantitative Intelligence must not use external authority."
            )

        evidence_strength = str(
            expression.get(
                "quantitative_evidence_strength"
            )
            or ""
        )

        if evidence_strength not in {
            "STRONG",
            "MODERATE",
            "LIMITED",
            "INSUFFICIENT",
        }:
            raise QuantitativeIntelligenceError(
                "Consolidated quantitative expression has invalid evidence strength."
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
                "cross_sentence_quantitative_valid"
            )
            is True
            and evidence_strength
            == "STRONG"
        ):
            cross_sentence_strong_count += 1

    if contextual_ambiguous_strong_count != 0:
        raise QuantitativeIntelligenceError(
            "Contextually ambiguous quantitative expressions must never certify with STRONG evidence."
        )

    if multiple_grounding_strong_count != 0:
        raise QuantitativeIntelligenceError(
            "Multiple-grounding quantitative expressions must never certify with STRONG evidence."
        )

    if cross_sentence_strong_count != 0:
        raise QuantitativeIntelligenceError(
            "Cross-sentence quantitative expressions must never certify with STRONG evidence."
        )

    quantitative_boundaries = dict(
        final_quantitative_result.get(
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
        raise QuantitativeIntelligenceError(
            "Final Quantitative Intelligence must remain article-local."
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

    for boundary_name in required_false_quantitative_boundaries:
        if (
            quantitative_boundaries.get(
                boundary_name
            )
            is not False
        ):
            raise QuantitativeIntelligenceError(
                boundary_name
                + " must remain False."
            )

    processing_boundaries = dict(
        final_quantitative_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        processing_boundaries.get(
            "article_quantitative_consolidation_performed"
        )
        is not True
    ):
        raise QuantitativeIntelligenceError(
            "Article quantitative consolidation must be complete."
        )

    if (
        processing_boundaries.get(
            "final_quantitative_result_built"
        )
        is not True
    ):
        raise QuantitativeIntelligenceError(
            "Final Quantitative Intelligence result must already be built."
        )

    if (
        processing_boundaries.get(
            "quantitative_certification_performed"
        )
        is not False
    ):
        raise QuantitativeIntelligenceError(
            "Input must not already be certified."
        )

    certification = dict(
        final_quantitative_result.get(
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
        != "4.6.9O"
    ):
        raise QuantitativeIntelligenceError(
            "Stage N certification state is invalid."
        )

    required_false_summary_fields = (
        "final_referent_selection_performed",
        "new_quantitative_expression_inference_performed",
        "derived_calculation_performed",
        "unit_conversion_performed",
        "trend_inference_performed",
        "aggregate_calculation_performed",
        "quantitative_evidence_strengthening_performed",
        "quantitative_inference_performed",
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
            raise QuantitativeIntelligenceError(
                field_name
                + " must remain False at certification."
            )

    certified_processing_boundaries = dict(
        processing_boundaries
    )

    certified_processing_boundaries[
        "quantitative_certification_performed"
    ] = True

    certified_processing_boundaries[
        "quantitative_intelligence_certified"
    ] = True

    result = dict(
        final_quantitative_result
    )

    result.update({
        "schema_version":
            "certified_quantitative_intelligence_result_v1",

        "patch":
            "4.6.9O",

        "status":
            "QUANTITATIVE_INTELLIGENCE_CERTIFIED",

        "processing_boundaries":
            certified_processing_boundaries,

        "certification": {
            "performed":
                True,

            "certified":
                True,

            "certification_stage":
                "4.6.9O",

            "certification_scope":
                "ARTICLE_LOCAL_QUANTITATIVE_INTELLIGENCE",

            "structural_integrity_verified":
                True,

            "candidate_accounting_verified":
                True,

            "representative_quantitative_integrity_verified":
                True,

            "provenance_preserved":
                True,

            "quantitative_value_integrity_verified":
                True,

            "quantitative_unit_integrity_verified":
                True,

            "quantity_role_integrity_verified":
                True,

            "quantitative_orientation_integrity_verified":
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

            "derived_calculation_performed":
                False,

            "unit_conversion_performed":
                False,

            "trend_inference_performed":
                False,

            "aggregate_calculation_performed":
                False,

            "quantitative_inference_performed":
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

        "quantitative_certification_summary": {
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

            "representative_quantitative_expression_count":
                len(
                    representative_candidates
                ),

            "consolidated_quantitative_expression_count":
                len(
                    consolidated_expressions
                ),

            "duplicate_redundant_quantitative_expression_count":
                redundant_count,

            "validated_quantitative_expression_count":
                summary.get(
                    "validated_quantitative_expression_count"
                ),

            "unvalidated_quantitative_expression_count":
                summary.get(
                    "unvalidated_quantitative_expression_count"
                ),

            "same_sentence_validated_quantitative_count":
                summary.get(
                    "same_sentence_validated_quantitative_count"
                ),

            "cross_sentence_validated_quantitative_count":
                summary.get(
                    "cross_sentence_validated_quantitative_count"
                ),

            "contextually_ambiguous_quantitative_count":
                summary.get(
                    "contextually_ambiguous_quantitative_count"
                ),

            "contextual_ambiguous_strong_count":
                contextual_ambiguous_strong_count,

            "multiple_grounding_strong_count":
                multiple_grounding_strong_count,

            "cross_sentence_strong_count":
                cross_sentence_strong_count,

            "quantitative_values_preserved":
                True,

            "quantitative_units_preserved":
                True,

            "quantity_roles_preserved":
                True,

            "quantitative_orientation_preserved":
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
            "procedural_intelligence",
    })

    return result
