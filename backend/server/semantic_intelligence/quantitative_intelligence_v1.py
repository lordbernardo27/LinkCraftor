from __future__ import annotations

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
