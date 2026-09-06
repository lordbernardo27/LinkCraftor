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
