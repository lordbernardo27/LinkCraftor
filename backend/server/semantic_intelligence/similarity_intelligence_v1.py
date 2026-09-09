from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class SimilarityIntelligenceError(ValueError):
    """Raised when canonical Similarity Intelligence contracts are violated."""


def validate_similarity_intelligence_intake_v1(
    certified_analogical_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate certified Phase 4.6.11 Analogical Intelligence before
    Phase 4.6.12 Semantic Similarity Intelligence begins.

    This stage performs intake validation only.

    It does NOT:
    - detect similarity relations,
    - detect difference or contrast relations,
    - extract compared entities or concepts,
    - select comparison participants,
    - infer shared characteristics,
    - infer unstated differences,
    - determine comparison orientation,
    - calculate semantic similarity scores,
    - perform embedding similarity,
    - perform fuzzy similarity,
    - reinterpret analogies as similarities,
    - redo analogical reasoning,
    - perform quantitative reasoning,
    - perform procedural reasoning,
    - perform temporal reasoning,
    - perform new causal reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        certified_analogical_result,
        Mapping,
    ):
        raise SimilarityIntelligenceError(
            "certified_analogical_result must be a mapping."
        )

    if (
        certified_analogical_result.get(
            "schema_version"
        )
        != "certified_analogical_intelligence_result_v1"
    ):
        raise SimilarityIntelligenceError(
            "Phase 4.6.12 requires "
            "certified_analogical_intelligence_result_v1."
        )

    if (
        certified_analogical_result.get(
            "status"
        )
        != "ANALOGICAL_INTELLIGENCE_CERTIFIED"
    ):
        raise SimilarityIntelligenceError(
            "Analogical Intelligence must be certified "
            "before Similarity Intelligence."
        )

    if (
        certified_analogical_result.get(
            "phase"
        )
        != "4.6.11"
    ):
        raise SimilarityIntelligenceError(
            "Phase 4.6.12 requires certified Phase 4.6.11 input."
        )

    if (
        certified_analogical_result.get(
            "patch"
        )
        != "4.6.11O"
    ):
        raise SimilarityIntelligenceError(
            "Phase 4.6.12 requires canonical 4.6.11O input."
        )

    if (
        certified_analogical_result.get(
            "next_stage"
        )
        != "similarity_intelligence"
    ):
        raise SimilarityIntelligenceError(
            "Certified Analogical Intelligence must hand off "
            "to similarity_intelligence."
        )

    if (
        certified_analogical_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise SimilarityIntelligenceError(
            "Similarity Intelligence intake must remain "
            "article-local and transient."
        )

    certification = dict(
        certified_analogical_result.get(
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
        != "4.6.11O"
        or certification.get(
            "certification_scope"
        )
        != "ARTICLE_LOCAL_ANALOGICAL_INTELLIGENCE"
    ):
        raise SimilarityIntelligenceError(
            "Certified Analogical Intelligence "
            "certification envelope is invalid."
        )

    required_true_certification_fields = (
        "structural_integrity_verified",
        "candidate_accounting_verified",
        "representative_analogical_integrity_verified",
        "provenance_preserved",
        "analogy_direction_integrity_verified",
        "source_target_grounding_integrity_verified",
        "analogical_form_integrity_verified",
        "orientation_pattern_integrity_verified",
        "evidence_strength_integrity_verified",
        "unvalidated_strength_cap_verified",
        "non_directional_strength_cap_verified",
        "cross_sentence_strength_cap_verified",
        "duplicate_provenance_integrity_verified",
        "boundary_integrity_verified",
    )

    for field_name in required_true_certification_fields:
        if (
            certification.get(
                field_name
            )
            is not True
        ):
            raise SimilarityIntelligenceError(
                "Required Analogical Intelligence certification "
                "field is not verified: "
                + field_name
            )

    required_false_certification_fields = (
        "scientific_truth_verified",
        "truth_assessment_performed",
        "external_authority_check_performed",
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
            raise SimilarityIntelligenceError(
                "Analogical certification boundary "
                "must remain False: "
                + field_name
            )

    processing_boundaries = dict(
        certified_analogical_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        processing_boundaries.get(
            "analogical_certification_performed"
        )
        is not True
    ):
        raise SimilarityIntelligenceError(
            "Analogical certification processing "
            "boundary must be complete."
        )

    if (
        processing_boundaries.get(
            "analogical_intelligence_certified"
        )
        is not True
    ):
        raise SimilarityIntelligenceError(
            "Analogical Intelligence must be marked certified."
        )

    analogical_boundaries = dict(
        certified_analogical_result.get(
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
        raise SimilarityIntelligenceError(
            "Certified Analogical Intelligence "
            "must remain article-local."
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

    for field_name in required_false_analogical_boundaries:
        if (
            analogical_boundaries.get(
                field_name
            )
            is not False
        ):
            raise SimilarityIntelligenceError(
                "Certified analogical boundary "
                "must remain False: "
                + field_name
            )

    article_identity = dict(
        certified_analogical_result.get(
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
            raise SimilarityIntelligenceError(
                "Required article identity field missing: "
                + field_name
            )

    return {
        "schema_version":
            "similarity_intelligence_intake_v1",

        "similarity_intelligence_version":
            "similarity_intelligence_v1",

        "phase":
            "4.6.12",

        "patch":
            "4.6.12C",

        "status":
            "SIMILARITY_INTELLIGENCE_INTAKE_VALIDATED",

        "article_identity":
            article_identity,

        "certified_analogical_result":
            dict(
                certified_analogical_result
            ),

        "intake_validation": {
            "certified_analogical_schema_verified":
                True,

            "certified_analogical_status_verified":
                True,

            "certified_analogical_patch_verified":
                True,

            "analogical_certification_verified":
                True,

            "analogical_boundary_integrity_verified":
                True,

            "article_identity_verified":
                True,

            "similarity_reasoning_not_preperformed":
                True,

            "article_local_only":
                True,
        },

        "processing_boundaries": {
            "similarity_intake_validation_performed":
                True,

            "similarity_claim_unit_preparation_performed":
                False,

            "similarity_signal_interpretation_performed":
                False,

            "similarity_candidate_extraction_performed":
                False,

            "similarity_participant_grounding_performed":
                False,

            "similarity_orientation_performed":
                False,

            "shared_characteristic_validation_performed":
                False,

            "difference_contrast_validation_performed":
                False,

            "same_sentence_similarity_validation_performed":
                False,

            "cross_sentence_similarity_validation_performed":
                False,

            "similarity_evidence_assessment_performed":
                False,

            "similarity_duplicate_resolution_performed":
                False,

            "article_similarity_consolidation_performed":
                False,

            "similarity_certification_performed":
                False,

            "embedding_similarity_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "unstated_shared_property_inference_performed":
                False,

            "unstated_difference_inference_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "procedural_reasoning_performed":
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
            "similarity_claim_unit_preparation",
    }


def build_similarity_claim_units_v1(
    certified_analogical_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Build canonical Phase 4.6.12 Similarity Claim Units from
    certified Phase 4.6.11 Analogical Intelligence.

    This is a one-to-one structural preparation stage.

    It does NOT:
    - reparse the article body,
    - identify similarity signals,
    - determine whether a comparison expresses similarity,
    - determine whether a comparison expresses difference,
    - select comparison participants,
    - ground comparison participants,
    - infer shared characteristics,
    - infer unstated differences,
    - determine similarity/difference orientation,
    - calculate semantic similarity scores,
    - perform embedding similarity,
    - perform fuzzy similarity,
    - reinterpret analogies as similarities,
    - redo analogical reasoning,
    - perform quantitative reasoning,
    - perform procedural reasoning,
    - perform temporal reasoning,
    - perform new causal reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    intake = validate_similarity_intelligence_intake_v1(
        certified_analogical_result
    )

    if (
        intake.get(
            "status"
        )
        != "SIMILARITY_INTELLIGENCE_INTAKE_VALIDATED"
    ):
        raise SimilarityIntelligenceError(
            "Canonical Similarity Intelligence intake was not validated."
        )

    identity = dict(
        certified_analogical_result.get(
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

    analogical_units = list(
        certified_analogical_result.get(
            "analogical_claim_units"
        )
        or []
    )

    if not article_id:
        raise SimilarityIntelligenceError(
            "Certified analogical article_id is required."
        )

    similarity_units = []
    similarity_sections = []

    seen_similarity_ids = set()
    seen_analogical_ids = set()
    seen_statement_ids = set()
    seen_sentence_ids = set()

    previous_global_index = None

    units_by_section = {}
    section_metadata = {}

    for analogical_unit in analogical_units:
        if not isinstance(
            analogical_unit,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every certified Analogical Claim Unit must be a mapping."
            )

        analogical_claim_unit_id = str(
            analogical_unit.get(
                "analogical_claim_unit_id"
            )
            or ""
        )

        statement_id = str(
            analogical_unit.get(
                "statement_evidence_id"
            )
            or ""
        )

        sentence_id = str(
            analogical_unit.get(
                "sentence_id"
            )
            or ""
        )

        section_id = str(
            analogical_unit.get(
                "section_id"
            )
            or ""
        )

        if not analogical_claim_unit_id:
            raise SimilarityIntelligenceError(
                "Analogical Claim Unit ID is required."
            )

        if not analogical_claim_unit_id.startswith(
            "analogical_claim_"
        ):
            raise SimilarityIntelligenceError(
                "Unexpected Analogical Claim Unit ID format."
            )

        if not statement_id:
            raise SimilarityIntelligenceError(
                "statement_evidence_id is required."
            )

        if not sentence_id:
            raise SimilarityIntelligenceError(
                "sentence_id is required."
            )

        if not section_id:
            raise SimilarityIntelligenceError(
                "section_id is required."
            )

        if analogical_claim_unit_id in seen_analogical_ids:
            raise SimilarityIntelligenceError(
                "Duplicate Analogical Claim Unit ID."
            )

        if statement_id in seen_statement_ids:
            raise SimilarityIntelligenceError(
                "Duplicate statement_evidence_id."
            )

        if sentence_id in seen_sentence_ids:
            raise SimilarityIntelligenceError(
                "Duplicate sentence_id."
            )

        if (
            analogical_unit.get(
                "article_id"
            )
            != article_id
        ):
            raise SimilarityIntelligenceError(
                "Analogical Claim Unit article identity mismatch."
            )

        global_index = analogical_unit.get(
            "sentence_global_index"
        )

        article_position = analogical_unit.get(
            "article_position"
        )

        if not isinstance(
            global_index,
            int,
        ):
            raise SimilarityIntelligenceError(
                "sentence_global_index must be an integer."
            )

        if not isinstance(
            article_position,
            int,
        ):
            raise SimilarityIntelligenceError(
                "article_position must be an integer."
            )

        if (
            previous_global_index is not None
            and global_index <= previous_global_index
        ):
            raise SimilarityIntelligenceError(
                "Certified Analogical Claim Units are not "
                "in canonical sentence order."
            )

        analogical_state = dict(
            analogical_unit.get(
                "analogical_analysis_state"
            )
            or {}
        )

        required_complete_analogical_stages = (
            "analogical_signal_interpretation",
            "analogical_candidate_extraction",
            "entity_concept_grounding",
            "analogy_source_target_orientation",
            "analogical_correspondence_validation",
            "same_sentence_analogical_validation",
            "cross_sentence_analogical_validation",
            "analogical_evidence_assessment",
            "duplicate_analogical_resolution",
        )

        for stage_name in required_complete_analogical_stages:
            if (
                analogical_state.get(
                    stage_name
                )
                != "COMPLETE"
            ):
                raise SimilarityIntelligenceError(
                    "Analogical Claim Unit analysis is incomplete at "
                    + stage_name
                    + "."
                )

        upstream_boundaries = dict(
            analogical_unit.get(
                "processing_boundaries"
            )
            or {}
        )

        required_false_upstream_boundaries = (
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

        for boundary_name in required_false_upstream_boundaries:
            if (
                upstream_boundaries.get(
                    boundary_name
                )
                is not False
            ):
                raise SimilarityIntelligenceError(
                    "Upstream Analogical Claim Unit boundary "
                    "must remain False: "
                    + boundary_name
                )

        similarity_claim_unit_id = (
            "similarity_claim_"
            + analogical_claim_unit_id[
                len("analogical_claim_"):
            ]
        )

        if similarity_claim_unit_id in seen_similarity_ids:
            raise SimilarityIntelligenceError(
                "Duplicate Similarity Claim Unit ID."
            )

        similarity_unit = {
            "similarity_claim_unit_id":
                similarity_claim_unit_id,

            "upstream_analogical_claim_unit_id":
                analogical_claim_unit_id,

            "upstream_procedural_claim_unit_id":
                analogical_unit.get(
                    "upstream_procedural_claim_unit_id"
                ),

            "upstream_quantitative_claim_unit_id":
                analogical_unit.get(
                    "upstream_quantitative_claim_unit_id"
                ),

            "upstream_causal_claim_unit_id":
                analogical_unit.get(
                    "upstream_causal_claim_unit_id"
                ),

            "upstream_relational_claim_unit_id":
                analogical_unit.get(
                    "upstream_relational_claim_unit_id"
                ),

            "upstream_logical_claim_unit_id":
                analogical_unit.get(
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
                analogical_unit.get(
                    "section_evidence_unit_id"
                ),

            "section_index":
                analogical_unit.get(
                    "section_index"
                ),

            "section_title":
                analogical_unit.get(
                    "section_title"
                ),

            "heading_level":
                analogical_unit.get(
                    "heading_level"
                ),

            "block_id":
                analogical_unit.get(
                    "block_id"
                ),

            "paragraph_id":
                analogical_unit.get(
                    "paragraph_id"
                ),

            "block_type":
                analogical_unit.get(
                    "block_type"
                ),

            "block_index":
                analogical_unit.get(
                    "block_index"
                ),

            "sentence_index":
                analogical_unit.get(
                    "sentence_index"
                ),

            "sentence_global_index":
                global_index,

            "article_position":
                article_position,

            "claim_index_in_section":
                analogical_unit.get(
                    "claim_index_in_section"
                ),

            "text":
                analogical_unit.get(
                    "text"
                ),

            "word_count":
                analogical_unit.get(
                    "word_count"
                ),

            "character_count":
                analogical_unit.get(
                    "character_count"
                ),

            "statement_form":
                analogical_unit.get(
                    "statement_form"
                ),

            "canonical_claim_candidate":
                analogical_unit.get(
                    "canonical_claim_candidate"
                )
                is True,

            "evidence_context":
                dict(
                    analogical_unit.get(
                        "evidence_context"
                    )
                    or {}
                ),

            "upstream_analogical_analysis_state":
                analogical_state,

            "upstream_analogical_processing_boundaries":
                upstream_boundaries,

            "similarity_analysis_state": {
                "similarity_signal_interpretation":
                    "PENDING",

                "similarity_candidate_extraction":
                    "PENDING",

                "similarity_participant_grounding":
                    "PENDING",

                "similarity_difference_orientation":
                    "PENDING",

                "shared_characteristic_validation":
                    "PENDING",

                "difference_contrast_validation":
                    "PENDING",

                "same_sentence_similarity_validation":
                    "PENDING",

                "cross_sentence_similarity_validation":
                    "PENDING",

                "similarity_evidence_assessment":
                    "PENDING",

                "duplicate_similarity_resolution":
                    "PENDING",
            },

            "processing_boundaries": {
                "article_local_only":
                    True,

                "similarity_claim_unit_prepared":
                    True,

                "article_body_reparsed":
                    False,

                "similarity_signal_interpretation_performed":
                    False,

                "similarity_candidate_extraction_performed":
                    False,

                "similarity_participant_grounding_performed":
                    False,

                "similarity_orientation_performed":
                    False,

                "shared_characteristic_validation_performed":
                    False,

                "difference_contrast_validation_performed":
                    False,

                "same_sentence_similarity_validation_performed":
                    False,

                "cross_sentence_similarity_validation_performed":
                    False,

                "similarity_evidence_assessment_performed":
                    False,

                "similarity_duplicate_resolution_performed":
                    False,

                "embedding_similarity_performed":
                    False,

                "fuzzy_similarity_performed":
                    False,

                "unstated_shared_property_inference_performed":
                    False,

                "unstated_difference_inference_performed":
                    False,

                "analogical_reasoning_performed":
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

        similarity_units.append(
            similarity_unit
        )

        units_by_section.setdefault(
            section_id,
            [],
        ).append(
            similarity_unit
        )

        if section_id not in section_metadata:
            section_metadata[
                section_id
            ] = {
                "section_id":
                    section_id,

                "section_index":
                    analogical_unit.get(
                        "section_index"
                    ),

                "section_title":
                    analogical_unit.get(
                        "section_title"
                    ),

                "heading_level":
                    analogical_unit.get(
                        "heading_level"
                    ),
            }

        seen_similarity_ids.add(
            similarity_claim_unit_id
        )

        seen_analogical_ids.add(
            analogical_claim_unit_id
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

    for unit in similarity_units:
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

        similarity_sections.append({
            **metadata,

            "upstream_analogical_claim_count":
                len(
                    section_units
                ),

            "similarity_claim_unit_count":
                len(
                    section_units
                ),

            "similarity_claim_units":
                section_units,
        })

    if (
        len(
            similarity_units
        )
        != len(
            analogical_units
        )
    ):
        raise SimilarityIntelligenceError(
            "Similarity Claim Unit construction must remain "
            "one-to-one with Analogical Claim Units."
        )

    return {
        "schema_version":
            "similarity_claim_units_v1",

        "similarity_intelligence_version":
            "similarity_intelligence_v1",

        "phase":
            "4.6.12",

        "patch":
            "4.6.12D",

        "status":
            "SIMILARITY_CLAIM_UNITS_PREPARED",

        "article_identity":
            identity,

        "analogical_claim_unit_count":
            len(
                analogical_units
            ),

        "similarity_claim_unit_count":
            len(
                similarity_units
            ),

        "section_count":
            len(
                similarity_sections
            ),

        "similarity_sections":
            similarity_sections,

        "similarity_claim_units":
            similarity_units,

        "construction_summary": {
            "source_analogical_claim_unit_count":
                len(
                    analogical_units
                ),

            "similarity_claim_unit_count":
                len(
                    similarity_units
                ),

            "one_to_one_analogical_mapping":
                (
                    len(
                        similarity_units
                    )
                    == len(
                        analogical_units
                    )
                ),

            "canonical_order_preserved":
                True,

            "canonical_text_preserved":
                True,

            "evidence_context_preserved":
                True,

            "analogical_context_preserved":
                True,

            "article_body_reparsed":
                False,

            "similarity_signals_interpreted":
                False,

            "similarity_participants_selected":
                False,

            "shared_characteristics_inferred":
                False,

            "unstated_differences_inferred":
                False,

            "embedding_similarity_performed":
                False,

            "fuzzy_similarity_performed":
                False,
        },

        "processing_boundaries": {
            "article_body_reparsed":
                False,

            "similarity_claim_units_prepared":
                True,

            "similarity_signal_interpretation_performed":
                False,

            "similarity_candidate_extraction_performed":
                False,

            "similarity_participant_grounding_performed":
                False,

            "similarity_orientation_performed":
                False,

            "shared_characteristic_validation_performed":
                False,

            "difference_contrast_validation_performed":
                False,

            "same_sentence_similarity_validation_performed":
                False,

            "cross_sentence_similarity_validation_performed":
                False,

            "similarity_evidence_assessment_performed":
                False,

            "similarity_duplicate_resolution_performed":
                False,

            "embedding_similarity_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "unstated_shared_property_inference_performed":
                False,

            "unstated_difference_inference_performed":
                False,

            "analogical_reasoning_performed":
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
            "similarity_signal_interpretation",
    }


def interpret_similarity_signals_v1(
    similarity_claim_units_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Interpret explicit Phase 4.6.12 Similarity-family signals.

    This stage detects article-expressed lexical framing only.

    It does NOT:
    - extract final similarity candidates,
    - select or ground comparison participants,
    - infer shared characteristics,
    - infer unstated differences,
    - determine final similarity validity,
    - determine final difference validity,
    - determine final comparison orientation,
    - calculate semantic similarity scores,
    - perform embedding similarity,
    - perform fuzzy similarity,
    - reinterpret analogical expressions,
    - redo analogical reasoning,
    - redo quantitative reasoning,
    - redo procedural reasoning,
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
        similarity_claim_units_result,
        Mapping,
    ):
        raise SimilarityIntelligenceError(
            "similarity_claim_units_result must be a mapping."
        )

    if (
        similarity_claim_units_result.get(
            "schema_version"
        )
        != "similarity_claim_units_v1"
    ):
        raise SimilarityIntelligenceError(
            "Stage E requires similarity_claim_units_v1."
        )

    if (
        similarity_claim_units_result.get(
            "status"
        )
        != "SIMILARITY_CLAIM_UNITS_PREPARED"
    ):
        raise SimilarityIntelligenceError(
            "Similarity Claim Units must be prepared before Stage E."
        )

    if (
        similarity_claim_units_result.get(
            "phase"
        )
        != "4.6.12"
    ):
        raise SimilarityIntelligenceError(
            "Stage E requires Phase 4.6.12 input."
        )

    if (
        similarity_claim_units_result.get(
            "patch"
        )
        != "4.6.12D"
    ):
        raise SimilarityIntelligenceError(
            "Stage E requires canonical 4.6.12D input."
        )

    if (
        similarity_claim_units_result.get(
            "next_stage"
        )
        != "similarity_signal_interpretation"
    ):
        raise SimilarityIntelligenceError(
            "Stage D must hand off to "
            "similarity_signal_interpretation."
        )

    if (
        similarity_claim_units_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise SimilarityIntelligenceError(
            "Similarity Intelligence must remain transient."
        )

    signal_specs = (
        (
            "SIMILAR_TO",
            "EXPLICIT_SIMILARITY_FRAMING",
            re.compile(
                r"\bsimilar\s+to\b",
                re.IGNORECASE,
            ),
        ),
        (
            "RESEMBLES",
            "EXPLICIT_RESEMBLANCE_FRAMING",
            re.compile(
                r"\bresembl(?:e|es|ed|ing)\b",
                re.IGNORECASE,
            ),
        ),
        (
            "ALIKE",
            "EXPLICIT_RESEMBLANCE_FRAMING",
            re.compile(
                r"\balike\b",
                re.IGNORECASE,
            ),
        ),
        (
            "COMPARABLE_TO",
            "EXPLICIT_COMPARABILITY_FRAMING",
            re.compile(
                r"\bcomparable\s+to\b",
                re.IGNORECASE,
            ),
        ),
        (
            "SAME_AS",
            "EXPLICIT_EQUIVALENCE_COMPARISON_FRAMING",
            re.compile(
                r"\b(?:the\s+)?same\s+as\b",
                re.IGNORECASE,
            ),
        ),
        (
            "DIFFERENT_FROM",
            "EXPLICIT_DIFFERENCE_FRAMING",
            re.compile(
                r"\bdifferent\s+from\b",
                re.IGNORECASE,
            ),
        ),
        (
            "DIFFERS_FROM",
            "EXPLICIT_DIFFERENCE_FRAMING",
            re.compile(
                r"\bdiffers?\s+from\b",
                re.IGNORECASE,
            ),
        ),
        (
            "UNLIKE",
            "EXPLICIT_CONTRAST_FRAMING",
            re.compile(
                r"\bunlike\b",
                re.IGNORECASE,
            ),
        ),
        (
            "COMPARED_TO",
            "EXPLICIT_COMPARISON_FRAMING",
            re.compile(
                r"\bcompared\s+to\b",
                re.IGNORECASE,
            ),
        ),
        (
            "COMPARED_WITH",
            "EXPLICIT_COMPARISON_FRAMING",
            re.compile(
                r"\bcompared\s+with\b",
                re.IGNORECASE,
            ),
        ),
        (
            "IN_CONTRAST_TO",
            "EXPLICIT_CONTRAST_FRAMING",
            re.compile(
                r"\bin\s+contrast\s+to\b",
                re.IGNORECASE,
            ),
        ),
        (
            "IN_CONTRAST_WITH",
            "EXPLICIT_CONTRAST_FRAMING",
            re.compile(
                r"\bin\s+contrast\s+with\b",
                re.IGNORECASE,
            ),
        ),
    )

    ambiguous_specs = (
        (
            "GENERIC_BOTH",
            re.compile(
                r"\bboth\b",
                re.IGNORECASE,
            ),
            "BOTH_ALONE_MAY_EXPRESS_PLURALITY_NOT_SIMILARITY",
        ),
        (
            "GENERIC_DIFFERENT",
            re.compile(
                r"\bdifferent\b",
                re.IGNORECASE,
            ),
            "DIFFERENT_ALONE_DOES_NOT_ESTABLISH_A_COMPARISON_PAIR",
        ),
        (
            "GENERIC_COMPARE",
            re.compile(
                r"\bcompar(?:e|es|ed|ing)\b",
                re.IGNORECASE,
            ),
            "COMPARE_WORDING_ALONE_DOES_NOT_ESTABLISH_SIMILARITY",
        ),
        (
            "GENERIC_LIKE",
            re.compile(
                r"\blike\b",
                re.IGNORECASE,
            ),
            "LIKE_MAY_BE_ANALOGICAL_IDIOMATIC_OR_NON_SIMILARITY",
        ),
        (
            "GENERIC_JUST_AS",
            re.compile(
                r"\bjust\s+as\b",
                re.IGNORECASE,
            ),
            "JUST_AS_MAY_BELONG_TO_ANALOGICAL_CORRESPONDENCE",
        ),
        (
            "SIMILARLY_DISCOURSE",
            re.compile(
                r"\bsimilarly\b",
                re.IGNORECASE,
            ),
            "SIMILARLY_MAY_BE_A_DISCOURSE_CONNECTOR_WITHOUT_A_COMPARISON_PAIR",
        ),
        (
            "WHEREAS",
            re.compile(
                r"\bwhereas\b",
                re.IGNORECASE,
            ),
            "WHEREAS_SIGNALS_CONTRAST_BUT_DOES_NOT_BY_ITSELF_ESTABLISH_SIMILARITY",
        ),
        (
            "RATHER_THAN",
            re.compile(
                r"\brather\s+than\b",
                re.IGNORECASE,
            ),
            "RATHER_THAN_MAY_EXPRESS_SELECTION_OR_CORRECTION_NOT_SIMILARITY",
        ),
    )

    source_units = list(
        similarity_claim_units_result.get(
            "similarity_claim_units"
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
            raise SimilarityIntelligenceError(
                "Every Similarity Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "similarity_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "similarity_signal_interpretation"
            )
            != "PENDING"
        ):
            raise SimilarityIntelligenceError(
                "Similarity signal interpretation must "
                "be PENDING before Stage E."
            )

        if (
            state.get(
                "similarity_candidate_extraction"
            )
            != "PENDING"
        ):
            raise SimilarityIntelligenceError(
                "Similarity candidate extraction must "
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
                "similarity_claim_unit_prepared"
            )
            is not True
        ):
            raise SimilarityIntelligenceError(
                "Similarity Claim Unit preparation "
                "boundary is incomplete."
            )

        required_false_boundaries = (
            "similarity_signal_interpretation_performed",
            "similarity_candidate_extraction_performed",
            "similarity_participant_grounding_performed",
            "similarity_orientation_performed",
            "shared_characteristic_validation_performed",
            "difference_contrast_validation_performed",
            "same_sentence_similarity_validation_performed",
            "cross_sentence_similarity_validation_performed",
            "similarity_evidence_assessment_performed",
            "similarity_duplicate_resolution_performed",
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

        for boundary_name in required_false_boundaries:
            if (
                boundaries.get(
                    boundary_name
                )
                is not False
            ):
                raise SimilarityIntelligenceError(
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

                    "similarity_semantic_class":
                        semantic_class,

                    "matched_text":
                        match.group(0),

                    "character_start":
                        match.start(),

                    "character_end":
                        match.end(),

                    "article_asserted_signal":
                        True,

                    "similarity_candidate_extracted":
                        False,

                    "participants_grounded":
                        False,

                    "similarity_orientation_determined":
                        False,

                    "shared_characteristic_validated":
                        False,

                    "difference_contrast_validated":
                        False,

                    "embedding_similarity_performed":
                        False,

                    "fuzzy_similarity_performed":
                        False,

                    "unstated_shared_property_inference_performed":
                        False,

                    "unstated_difference_inference_performed":
                        False,

                    "analogical_reasoning_performed":
                        False,

                    "quantitative_reasoning_performed":
                        False,

                    "procedural_reasoning_performed":
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
                        "AMBIGUOUS_SIMILARITY_LEXEME_DEFERRED",

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

                    "similarity_inference_performed":
                        False,

                    "difference_inference_performed":
                        False,

                    "embedding_similarity_performed":
                        False,

                    "fuzzy_similarity_performed":
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
            "similarity_signal_interpretation"
        ] = "COMPLETE"

        interpreted_boundaries = dict(
            boundaries
        )

        interpreted_boundaries[
            "similarity_signal_interpretation_performed"
        ] = True

        interpreted_boundaries[
            "similarity_candidate_extraction_performed"
        ] = False

        interpreted_boundaries[
            "similarity_participant_grounding_performed"
        ] = False

        interpreted_boundaries[
            "similarity_orientation_performed"
        ] = False

        interpreted_boundaries[
            "shared_characteristic_validation_performed"
        ] = False

        interpreted_boundaries[
            "difference_contrast_validation_performed"
        ] = False

        interpreted_boundaries[
            "embedding_similarity_performed"
        ] = False

        interpreted_boundaries[
            "fuzzy_similarity_performed"
        ] = False

        interpreted_boundaries[
            "unstated_shared_property_inference_performed"
        ] = False

        interpreted_boundaries[
            "unstated_difference_inference_performed"
        ] = False

        interpreted_boundaries[
            "analogical_reasoning_performed"
        ] = False

        interpreted_boundaries[
            "quantitative_reasoning_performed"
        ] = False

        interpreted_boundaries[
            "procedural_reasoning_performed"
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
            "similarity_signals":
                signals,

            "similarity_signal_exclusions":
                exclusions,

            "similarity_signal_count":
                unit_total,

            "similarity_signal_exclusion_count":
                len(
                    exclusions
                ),

            "has_similarity_signal":
                unit_total > 0,

            "similarity_signal_interpretation_scope":
                (
                    "ARTICLE_LOCAL_EXPLICIT_"
                    "SIMILARITY_COMPARISON_SIGNAL_ONLY"
                ),

            "similarity_analysis_state":
                interpreted_state,

            "processing_boundaries":
                interpreted_boundaries,
        })

        interpreted_units.append(
            interpreted_unit
        )

        unit_id = str(
            interpreted_unit.get(
                "similarity_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise SimilarityIntelligenceError(
                "Every interpreted Similarity "
                "Claim Unit requires an ID."
            )

        if unit_id in interpreted_by_id:
            raise SimilarityIntelligenceError(
                "Duplicate interpreted Similarity Claim Unit ID."
            )

        interpreted_by_id[
            unit_id
        ] = interpreted_unit

    interpreted_sections = []

    for section in (
        similarity_claim_units_result.get(
            "similarity_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every similarity section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "similarity_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise SimilarityIntelligenceError(
                    "Every section Similarity Claim Unit "
                    "reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "similarity_claim_unit_id"
                )
                or ""
            )

            resolved_unit = interpreted_by_id.get(
                unit_id
            )

            if resolved_unit is None:
                raise SimilarityIntelligenceError(
                    "Similarity section references "
                    "an unknown claim unit."
                )

            section_units.append(
                resolved_unit
            )

        interpreted_sections.append({
            **dict(
                section
            ),

            "similarity_claim_units":
                section_units,

            "similarity_signal_unit_count":
                sum(
                    1
                    for unit in section_units
                    if unit.get(
                        "has_similarity_signal"
                    )
                    is True
                ),

            "similarity_signal_count":
                sum(
                    int(
                        unit.get(
                            "similarity_signal_count"
                        )
                        or 0
                    )
                    for unit in section_units
                ),

            "similarity_signal_exclusion_count":
                sum(
                    int(
                        unit.get(
                            "similarity_signal_exclusion_count"
                        )
                        or 0
                    )
                    for unit in section_units
                ),
        })

    result = dict(
        similarity_claim_units_result
    )

    result_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    result_boundaries[
        "similarity_signal_interpretation_performed"
    ] = True

    result_boundaries[
        "similarity_candidate_extraction_performed"
    ] = False

    result_boundaries[
        "similarity_participant_grounding_performed"
    ] = False

    result_boundaries[
        "similarity_orientation_performed"
    ] = False

    result_boundaries[
        "shared_characteristic_validation_performed"
    ] = False

    result_boundaries[
        "difference_contrast_validation_performed"
    ] = False

    result_boundaries[
        "embedding_similarity_performed"
    ] = False

    result_boundaries[
        "fuzzy_similarity_performed"
    ] = False

    result_boundaries[
        "unstated_shared_property_inference_performed"
    ] = False

    result_boundaries[
        "unstated_difference_inference_performed"
    ] = False

    result_boundaries[
        "analogical_reasoning_performed"
    ] = False

    result_boundaries[
        "quantitative_reasoning_performed"
    ] = False

    result_boundaries[
        "procedural_reasoning_performed"
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
            "similarity_signal_interpretation_v1",

        "patch":
            "4.6.12E",

        "status":
            "SIMILARITY_SIGNAL_INTERPRETATION_COMPLETE",

        "similarity_sections":
            interpreted_sections,

        "similarity_claim_units":
            interpreted_units,

        "similarity_signal_summary": {
            "claim_unit_count":
                len(
                    interpreted_units
                ),

            "units_with_similarity_signals":
                units_with_signals,

            "total_similarity_signal_count":
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

            "generic_both_not_automatically_similarity":
                True,

            "generic_different_not_automatically_comparison":
                True,

            "generic_compare_not_automatically_similarity":
                True,

            "like_not_reinterpreted_from_analogical_intelligence":
                True,

            "similarity_candidates_extracted":
                False,

            "participants_grounded":
                False,

            "shared_characteristics_inferred":
                False,

            "unstated_differences_inferred":
                False,

            "embedding_similarity_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "procedural_reasoning_performed":
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
            "similarity_candidate_extraction",
    })

    return result


def extract_similarity_candidates_v1(
    similarity_signal_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Extract canonical Phase 4.6.12 Similarity candidates from
    explicit Stage-E similarity-family signals.

    This stage performs structural candidate extraction only.

    It does NOT:
    - ground comparison participants,
    - determine final comparison orientation,
    - infer shared characteristics,
    - infer unstated differences,
    - validate final similarity,
    - validate final difference or contrast,
    - perform cross-sentence reasoning,
    - calculate semantic similarity scores,
    - perform embedding similarity,
    - perform fuzzy similarity,
    - reinterpret analogies,
    - redo analogical reasoning,
    - redo quantitative reasoning,
    - redo procedural reasoning,
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
        similarity_signal_result,
        Mapping,
    ):
        raise SimilarityIntelligenceError(
            "similarity_signal_result must be a mapping."
        )

    if (
        similarity_signal_result.get(
            "schema_version"
        )
        != "similarity_signal_interpretation_v1"
    ):
        raise SimilarityIntelligenceError(
            "Stage F requires similarity_signal_interpretation_v1."
        )

    if (
        similarity_signal_result.get(
            "status"
        )
        != "SIMILARITY_SIGNAL_INTERPRETATION_COMPLETE"
    ):
        raise SimilarityIntelligenceError(
            "Similarity signal interpretation must be complete."
        )

    if (
        similarity_signal_result.get(
            "phase"
        )
        != "4.6.12"
    ):
        raise SimilarityIntelligenceError(
            "Stage F requires Phase 4.6.12 input."
        )

    if (
        similarity_signal_result.get(
            "patch"
        )
        != "4.6.12E"
    ):
        raise SimilarityIntelligenceError(
            "Stage F requires canonical 4.6.12E input."
        )

    if (
        similarity_signal_result.get(
            "next_stage"
        )
        != "similarity_candidate_extraction"
    ):
        raise SimilarityIntelligenceError(
            "Stage E must hand off to "
            "similarity_candidate_extraction."
        )

    if (
        similarity_signal_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise SimilarityIntelligenceError(
            "Similarity Intelligence must remain transient."
        )

    supported_signal_types = {
        "SIMILAR_TO",
        "RESEMBLES",
        "ALIKE",
        "COMPARABLE_TO",
        "SAME_AS",
        "DIFFERENT_FROM",
        "DIFFERS_FROM",
        "UNLIKE",
        "COMPARED_TO",
        "COMPARED_WITH",
        "IN_CONTRAST_TO",
        "IN_CONTRAST_WITH",
    }

    candidate_form_by_signal = {
        "SIMILAR_TO":
            "SIMILARITY",

        "RESEMBLES":
            "RESEMBLANCE",

        "ALIKE":
            "RESEMBLANCE",

        "COMPARABLE_TO":
            "COMPARABILITY",

        "SAME_AS":
            "EQUIVALENCE_COMPARISON",

        "DIFFERENT_FROM":
            "DIFFERENCE",

        "DIFFERS_FROM":
            "DIFFERENCE",

        "UNLIKE":
            "CONTRAST",

        "COMPARED_TO":
            "GENERAL_COMPARISON",

        "COMPARED_WITH":
            "GENERAL_COMPARISON",

        "IN_CONTRAST_TO":
            "CONTRAST",

        "IN_CONTRAST_WITH":
            "CONTRAST",
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
            "similarity_candidate_"
            + hashlib.sha256(
                raw.encode(
                    "utf-8"
                )
            ).hexdigest()[:24]
        )

    source_units = list(
        similarity_signal_result.get(
            "similarity_claim_units"
        )
        or []
    )

    extracted_units = []
    extracted_by_id = {}
    all_candidates = []

    seen_candidate_ids = set()

    units_with_candidates = 0
    rejected_signal_count = 0

    candidate_form_counts = {}
    signal_type_counts = {}

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every Stage-E Similarity Claim Unit must be a mapping."
            )

        state = dict(
            unit.get(
                "similarity_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "similarity_signal_interpretation"
            )
            != "COMPLETE"
        ):
            raise SimilarityIntelligenceError(
                "Similarity signal interpretation must "
                "be COMPLETE before Stage F."
            )

        if (
            state.get(
                "similarity_candidate_extraction"
            )
            != "PENDING"
        ):
            raise SimilarityIntelligenceError(
                "Similarity candidate extraction must "
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
                "similarity_signal_interpretation_performed"
            )
            is not True
        ):
            raise SimilarityIntelligenceError(
                "Stage-E Similarity interpretation "
                "boundary is incomplete."
            )

        required_false_boundaries = (
            "similarity_candidate_extraction_performed",
            "similarity_participant_grounding_performed",
            "similarity_orientation_performed",
            "shared_characteristic_validation_performed",
            "difference_contrast_validation_performed",
            "same_sentence_similarity_validation_performed",
            "cross_sentence_similarity_validation_performed",
            "similarity_evidence_assessment_performed",
            "similarity_duplicate_resolution_performed",
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

        for boundary_name in required_false_boundaries:
            if (
                boundaries.get(
                    boundary_name
                )
                is not False
            ):
                raise SimilarityIntelligenceError(
                    boundary_name
                    + " must be False before Stage F."
                )

        unit_id = str(
            unit.get(
                "similarity_claim_unit_id"
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
            raise SimilarityIntelligenceError(
                "Similarity Claim Unit ID is required."
            )

        signals = list(
            unit.get(
                "similarity_signals"
            )
            or []
        )

        exclusions = list(
            unit.get(
                "similarity_signal_exclusions"
            )
            or []
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
                raise SimilarityIntelligenceError(
                    "Every similarity signal must be a mapping."
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
                raise SimilarityIntelligenceError(
                    "Similarity signal character span is invalid."
                )

            if (
                sentence_text[
                    start:end
                ]
                != matched_text
            ):
                raise SimilarityIntelligenceError(
                    "Similarity signal text does not "
                    "match its source span."
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
                        "UNSUPPORTED_SIMILARITY_SIGNAL_TYPE",

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
                        "EMPTY_SIMILARITY_SIGNAL_TEXT",

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
                raise SimilarityIntelligenceError(
                    "Duplicate Similarity Candidate ID."
                )

            candidate_form = (
                candidate_form_by_signal[
                    signal_type
                ]
            )

            candidate = {
                "similarity_candidate_id":
                    candidate_id,

                "similarity_claim_unit_id":
                    unit_id,

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

                "signal_type":
                    signal_type,

                "similarity_semantic_class":
                    signal.get(
                        "similarity_semantic_class"
                    ),

                "signal_matched_text":
                    matched_text,

                "signal_character_start":
                    start,

                "signal_character_end":
                    end,

                "candidate_similarity_form":
                    candidate_form,

                "article_asserted_candidate":
                    True,

                "same_sentence_candidate":
                    True,

                "participant_grounding_performed":
                    False,

                "participant_a_selected":
                    False,

                "selected_participant_a":
                    None,

                "participant_b_selected":
                    False,

                "selected_participant_b":
                    None,

                "similarity_difference_orientation_resolved":
                    False,

                "shared_characteristic_validated":
                    False,

                "difference_contrast_validated":
                    False,

                "same_sentence_similarity_validated":
                    False,

                "cross_sentence_similarity_validated":
                    False,

                "similarity_evidence_assessed":
                    False,

                "duplicate_resolution_performed":
                    False,

                "embedding_similarity_performed":
                    False,

                "fuzzy_similarity_performed":
                    False,

                "unstated_shared_property_inference_performed":
                    False,

                "unstated_difference_inference_performed":
                    False,

                "analogical_reasoning_performed":
                    False,

                "quantitative_reasoning_performed":
                    False,

                "procedural_reasoning_performed":
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

            candidate_form_counts[
                candidate_form
            ] = (
                candidate_form_counts.get(
                    candidate_form,
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

        if unit_candidates:
            units_with_candidates += 1

        extracted_state = dict(
            state
        )

        extracted_state[
            "similarity_candidate_extraction"
        ] = "COMPLETE"

        extracted_boundaries = dict(
            boundaries
        )

        extracted_boundaries[
            "similarity_candidate_extraction_performed"
        ] = True

        extracted_boundaries[
            "similarity_participant_grounding_performed"
        ] = False

        extracted_boundaries[
            "similarity_orientation_performed"
        ] = False

        extracted_boundaries[
            "shared_characteristic_validation_performed"
        ] = False

        extracted_boundaries[
            "difference_contrast_validation_performed"
        ] = False

        extracted_boundaries[
            "same_sentence_similarity_validation_performed"
        ] = False

        extracted_boundaries[
            "cross_sentence_similarity_validation_performed"
        ] = False

        extracted_boundaries[
            "embedding_similarity_performed"
        ] = False

        extracted_boundaries[
            "fuzzy_similarity_performed"
        ] = False

        extracted_boundaries[
            "unstated_shared_property_inference_performed"
        ] = False

        extracted_boundaries[
            "unstated_difference_inference_performed"
        ] = False

        extracted_boundaries[
            "analogical_reasoning_performed"
        ] = False

        extracted_boundaries[
            "quantitative_reasoning_performed"
        ] = False

        extracted_boundaries[
            "procedural_reasoning_performed"
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
            "similarity_candidates":
                unit_candidates,

            "similarity_candidate_count":
                len(
                    unit_candidates
                ),

            "similarity_extraction_rejections":
                unit_rejections,

            "similarity_extraction_rejection_count":
                len(
                    unit_rejections
                ),

            "similarity_signal_exclusions":
                exclusions,

            "similarity_analysis_state":
                extracted_state,

            "processing_boundaries":
                extracted_boundaries,
        })

        extracted_units.append(
            extracted_unit
        )

        if unit_id in extracted_by_id:
            raise SimilarityIntelligenceError(
                "Duplicate extracted Similarity Claim Unit ID."
            )

        extracted_by_id[
            unit_id
        ] = extracted_unit

    extracted_sections = []

    for section in (
        similarity_signal_result.get(
            "similarity_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every similarity section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "similarity_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise SimilarityIntelligenceError(
                    "Every section Similarity Claim Unit "
                    "reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "similarity_claim_unit_id"
                )
                or ""
            )

            resolved_unit = extracted_by_id.get(
                unit_id
            )

            if resolved_unit is None:
                raise SimilarityIntelligenceError(
                    "Similarity section references "
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
                    "similarity_candidates"
                )
                or []
            )
        ]

        extracted_sections.append({
            **dict(
                section
            ),

            "similarity_claim_units":
                section_units,

            "similarity_candidate_count":
                len(
                    section_candidates
                ),

            "similarity_candidates":
                section_candidates,
        })

    result = dict(
        similarity_signal_result
    )

    result_boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    result_boundaries[
        "similarity_candidate_extraction_performed"
    ] = True

    result_boundaries[
        "similarity_participant_grounding_performed"
    ] = False

    result_boundaries[
        "similarity_orientation_performed"
    ] = False

    result_boundaries[
        "shared_characteristic_validation_performed"
    ] = False

    result_boundaries[
        "difference_contrast_validation_performed"
    ] = False

    result_boundaries[
        "same_sentence_similarity_validation_performed"
    ] = False

    result_boundaries[
        "cross_sentence_similarity_validation_performed"
    ] = False

    result_boundaries[
        "embedding_similarity_performed"
    ] = False

    result_boundaries[
        "fuzzy_similarity_performed"
    ] = False

    result_boundaries[
        "unstated_shared_property_inference_performed"
    ] = False

    result_boundaries[
        "unstated_difference_inference_performed"
    ] = False

    result_boundaries[
        "analogical_reasoning_performed"
    ] = False

    result_boundaries[
        "quantitative_reasoning_performed"
    ] = False

    result_boundaries[
        "procedural_reasoning_performed"
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
            "similarity_candidates_v1",

        "patch":
            "4.6.12F",

        "status":
            "SIMILARITY_CANDIDATE_EXTRACTION_COMPLETE",

        "similarity_sections":
            extracted_sections,

        "similarity_claim_units":
            extracted_units,

        "similarity_candidates":
            all_candidates,

        "similarity_extraction_summary": {
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

            "signal_type_counts":
                dict(
                    sorted(
                        signal_type_counts.items()
                    )
                ),

            "zero_candidates_allowed":
                True,

            "same_sentence_extraction_only":
                True,

            "ambiguous_stage_e_exclusions_not_promoted":
                True,

            "participant_grounding_performed":
                False,

            "similarity_orientation_performed":
                False,

            "shared_characteristic_validation_performed":
                False,

            "difference_contrast_validation_performed":
                False,

            "embedding_similarity_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "unstated_shared_property_inference_performed":
                False,

            "unstated_difference_inference_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "procedural_reasoning_performed":
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
            "similarity_participant_grounding",
    })

    return result


def ground_similarity_candidates_v1(
    similarity_candidates_result: Mapping[str, Any],
    entity_concept_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Ground Phase 4.6.12 Similarity candidates against canonical
    article-local Phase 4.6.2 Entity & Concept Intelligence objects.

    This stage identifies canonical semantic objects present in
    each Similarity candidate's source sentence.

    It does NOT:
    - select Participant A,
    - select Participant B,
    - assign similarity/difference orientation,
    - infer shared characteristics,
    - infer unstated differences,
    - create new entities or concepts,
    - perform fuzzy semantic similarity,
    - perform embedding similarity,
    - determine final similarity validity,
    - determine final difference validity,
    - reinterpret analogical expressions,
    - redo analogical reasoning,
    - redo quantitative reasoning,
    - redo procedural reasoning,
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
        similarity_candidates_result,
        Mapping,
    ):
        raise SimilarityIntelligenceError(
            "similarity_candidates_result must be a mapping."
        )

    if not isinstance(
        entity_concept_result,
        Mapping,
    ):
        raise SimilarityIntelligenceError(
            "entity_concept_result must be a mapping."
        )

    if (
        similarity_candidates_result.get(
            "schema_version"
        )
        != "similarity_candidates_v1"
    ):
        raise SimilarityIntelligenceError(
            "Stage G requires similarity_candidates_v1."
        )

    if (
        similarity_candidates_result.get(
            "status"
        )
        != "SIMILARITY_CANDIDATE_EXTRACTION_COMPLETE"
    ):
        raise SimilarityIntelligenceError(
            "Similarity candidate extraction must be complete."
        )

    if (
        similarity_candidates_result.get(
            "phase"
        )
        != "4.6.12"
    ):
        raise SimilarityIntelligenceError(
            "Stage G requires Phase 4.6.12 input."
        )

    if (
        similarity_candidates_result.get(
            "patch"
        )
        != "4.6.12F"
    ):
        raise SimilarityIntelligenceError(
            "Stage G requires canonical 4.6.12F input."
        )

    if (
        similarity_candidates_result.get(
            "next_stage"
        )
        != "similarity_participant_grounding"
    ):
        raise SimilarityIntelligenceError(
            "Stage F must hand off to "
            "similarity_participant_grounding."
        )

    if (
        similarity_candidates_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise SimilarityIntelligenceError(
            "Similarity Intelligence must remain transient."
        )

    if (
        entity_concept_result.get(
            "schema_version"
        )
        != "entity_concept_intelligence_result_v1"
    ):
        raise SimilarityIntelligenceError(
            "Stage G requires canonical "
            "entity_concept_intelligence_result_v1."
        )

    if (
        entity_concept_result.get(
            "status"
        )
        != "ENTITY_CONCEPT_INTELLIGENCE_COMPLETE"
    ):
        raise SimilarityIntelligenceError(
            "Entity & Concept Intelligence must be complete."
        )

    if (
        entity_concept_result.get(
            "phase"
        )
        != "4.6.2"
    ):
        raise SimilarityIntelligenceError(
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
        raise SimilarityIntelligenceError(
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
        raise SimilarityIntelligenceError(
            "Entity & Concept Intelligence must be article-local."
        )

    if (
        entity_boundaries.get(
            "semantic_memory_write_performed"
        )
        is not False
    ):
        raise SimilarityIntelligenceError(
            "Unexpected Semantic Memory write detected upstream."
        )

    if (
        entity_boundaries.get(
            "reasoning_performed"
        )
        is not False
    ):
        raise SimilarityIntelligenceError(
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
        similarity_candidates_result.get(
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
        raise SimilarityIntelligenceError(
            "Similarity article_id is required."
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
        raise SimilarityIntelligenceError(
            "Entity/Concept Intelligence article identity mismatch."
        )

    prepared_objects = []

    for semantic_object in semantic_objects:
        if not isinstance(
            semantic_object,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
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
            raise SimilarityIntelligenceError(
                "Semantic object is missing canonical_text."
            )

        if semantic_kind not in {
            "entity",
            "concept",
        }:
            raise SimilarityIntelligenceError(
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
            raise SimilarityIntelligenceError(
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

                    "participant_a_selected":
                        False,

                    "participant_b_selected":
                        False,

                    "similarity_participant_selected":
                        False,

                    "similarity_difference_orientation_resolved":
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
        similarity_candidates_result.get(
            "similarity_candidates"
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
            raise SimilarityIntelligenceError(
                "Every similarity candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "similarity_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise SimilarityIntelligenceError(
                "Similarity candidate ID is required."
            )

        if candidate_id in seen_candidate_ids:
            raise SimilarityIntelligenceError(
                "Duplicate Similarity Candidate ID."
            )

        seen_candidate_ids.add(
            candidate_id
        )

        if (
            candidate.get(
                "participant_grounding_performed"
            )
            is not False
        ):
            raise SimilarityIntelligenceError(
                "Candidate must not already be participant grounded."
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
            "similarity_participant_grounding_matches":
                grounding_matches,

            "similarity_participant_grounding_match_count":
                grounding_match_count,

            "grounding_status":
                grounding_status,

            "similarity_participant_grounded":
                grounding_match_count > 0,

            "participant_grounding_performed":
                True,

            "participant_selection_performed":
                False,

            "participant_a_selected":
                False,

            "selected_participant_a":
                None,

            "participant_b_selected":
                False,

            "selected_participant_b":
                None,

            "similarity_difference_orientation_resolved":
                False,

            "shared_characteristic_validated":
                False,

            "difference_contrast_validated":
                False,

            "same_sentence_similarity_validated":
                False,

            "cross_sentence_similarity_validated":
                False,

            "similarity_evidence_assessed":
                False,

            "duplicate_resolution_performed":
                False,

            "embedding_similarity_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "unstated_shared_property_inference_performed":
                False,

            "unstated_difference_inference_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "procedural_reasoning_performed":
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
            "similarity_candidate_id"
        ):
            candidate
        for candidate in grounded_candidates
    }

    grounded_units = []
    seen_unit_ids = set()

    for unit in (
        similarity_candidates_result.get(
            "similarity_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every Similarity Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "similarity_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise SimilarityIntelligenceError(
                "Similarity Claim Unit ID is required."
            )

        if unit_id in seen_unit_ids:
            raise SimilarityIntelligenceError(
                "Duplicate Similarity Claim Unit ID."
            )

        seen_unit_ids.add(
            unit_id
        )

        state = dict(
            unit.get(
                "similarity_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "similarity_candidate_extraction"
            )
            != "COMPLETE"
        ):
            raise SimilarityIntelligenceError(
                "Similarity candidate extraction must "
                "be COMPLETE before grounding."
            )

        if (
            state.get(
                "similarity_participant_grounding"
            )
            != "PENDING"
        ):
            raise SimilarityIntelligenceError(
                "Similarity participant grounding must be PENDING."
            )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "similarity_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise SimilarityIntelligenceError(
                    "Every unit Similarity Candidate "
                    "reference must be a mapping."
                )

            candidate_id = str(
                old_candidate.get(
                    "similarity_candidate_id"
                )
                or ""
            )

            grounded = grounded_by_id.get(
                candidate_id
            )

            if grounded is None:
                raise SimilarityIntelligenceError(
                    "Similarity candidate/unit identity mismatch."
                )

            unit_candidates.append(
                grounded
            )

        updated_state = dict(
            state
        )

        updated_state[
            "similarity_participant_grounding"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            updated_boundaries.get(
                "similarity_candidate_extraction_performed"
            )
            is not True
        ):
            raise SimilarityIntelligenceError(
                "Stage-F extraction boundary is incomplete."
            )

        required_false_boundaries = (
            "similarity_participant_grounding_performed",
            "similarity_orientation_performed",
            "shared_characteristic_validation_performed",
            "difference_contrast_validation_performed",
            "same_sentence_similarity_validation_performed",
            "cross_sentence_similarity_validation_performed",
            "similarity_evidence_assessment_performed",
            "similarity_duplicate_resolution_performed",
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

        for boundary_name in required_false_boundaries:
            if (
                updated_boundaries.get(
                    boundary_name
                )
                is not False
            ):
                raise SimilarityIntelligenceError(
                    boundary_name
                    + " must be False before Stage G."
                )

        updated_boundaries[
            "similarity_participant_grounding_performed"
        ] = True

        updated_boundaries[
            "similarity_orientation_performed"
        ] = False

        updated_boundaries[
            "shared_characteristic_validation_performed"
        ] = False

        updated_boundaries[
            "difference_contrast_validation_performed"
        ] = False

        updated_boundaries[
            "same_sentence_similarity_validation_performed"
        ] = False

        updated_boundaries[
            "cross_sentence_similarity_validation_performed"
        ] = False

        updated_boundaries[
            "embedding_similarity_performed"
        ] = False

        updated_boundaries[
            "fuzzy_similarity_performed"
        ] = False

        updated_boundaries[
            "unstated_shared_property_inference_performed"
        ] = False

        updated_boundaries[
            "unstated_difference_inference_performed"
        ] = False

        updated_boundaries[
            "analogical_reasoning_performed"
        ] = False

        updated_boundaries[
            "quantitative_reasoning_performed"
        ] = False

        updated_boundaries[
            "procedural_reasoning_performed"
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
            "similarity_candidates":
                unit_candidates,

            "grounded_candidate_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "similarity_participant_grounded"
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

            "similarity_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        grounded_units.append(
            updated_unit
        )

    grounded_units_by_id = {
        unit.get(
            "similarity_claim_unit_id"
        ):
            unit
        for unit in grounded_units
    }

    grounded_sections = []

    for section in (
        similarity_candidates_result.get(
            "similarity_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every similarity section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "similarity_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise SimilarityIntelligenceError(
                    "Every section Similarity Claim Unit "
                    "reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "similarity_claim_unit_id"
                )
                or ""
            )

            grounded_unit = (
                grounded_units_by_id.get(
                    unit_id
                )
            )

            if grounded_unit is None:
                raise SimilarityIntelligenceError(
                    "Similarity section/unit grounding mismatch."
                )

            section_units.append(
                grounded_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "similarity_candidates"
                )
                or []
            )
        ]

        grounded_sections.append({
            **dict(
                section
            ),

            "similarity_claim_units":
                section_units,

            "similarity_candidates":
                section_candidates,

            "similarity_candidate_count":
                len(
                    section_candidates
                ),

            "grounded_candidate_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "similarity_participant_grounded"
                    )
                    is True
                ),

            "ungrounded_candidate_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "similarity_participant_grounded"
                    )
                    is False
                ),

            "similarity_participant_grounding_complete":
                True,
        })

    grounded_count = sum(
        1
        for candidate in grounded_candidates
        if candidate.get(
            "similarity_participant_grounded"
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
                "similarity_participant_grounding_match_count"
            )
            or 0
        )
        for candidate in grounded_candidates
    )

    result = dict(
        similarity_candidates_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    boundaries[
        "similarity_participant_grounding_performed"
    ] = True

    boundaries[
        "similarity_orientation_performed"
    ] = False

    boundaries[
        "shared_characteristic_validation_performed"
    ] = False

    boundaries[
        "difference_contrast_validation_performed"
    ] = False

    boundaries[
        "same_sentence_similarity_validation_performed"
    ] = False

    boundaries[
        "cross_sentence_similarity_validation_performed"
    ] = False

    boundaries[
        "similarity_evidence_assessment_performed"
    ] = False

    boundaries[
        "similarity_duplicate_resolution_performed"
    ] = False

    boundaries[
        "embedding_similarity_performed"
    ] = False

    boundaries[
        "fuzzy_similarity_performed"
    ] = False

    boundaries[
        "unstated_shared_property_inference_performed"
    ] = False

    boundaries[
        "unstated_difference_inference_performed"
    ] = False

    boundaries[
        "analogical_reasoning_performed"
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
            "similarity_participant_grounding_v1",

        "patch":
            "4.6.12G",

        "status":
            "SIMILARITY_PARTICIPANT_GROUNDING_COMPLETE",

        "similarity_sections":
            grounded_sections,

        "similarity_claim_units":
            grounded_units,

        "similarity_candidates":
            grounded_candidates,

        "similarity_participant_grounding_summary": {
            "semantic_object_count":
                len(
                    semantic_objects
                ),

            "similarity_candidate_count":
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

            "exact_or_bounded_surface_matching_only":
                True,

            "fuzzy_similarity_performed":
                False,

            "embedding_similarity_performed":
                False,

            "participant_selection_performed":
                False,

            "participant_a_selected":
                False,

            "participant_b_selected":
                False,

            "similarity_orientation_performed":
                False,

            "shared_characteristic_validation_performed":
                False,

            "difference_contrast_validation_performed":
                False,

            "unstated_shared_property_inference_performed":
                False,

            "unstated_difference_inference_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "procedural_reasoning_performed":
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
            "similarity_difference_orientation",
    })

    return result


def resolve_similarity_difference_orientation_v1(
    similarity_grounding_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Resolve article-local Similarity / Difference orientation from
    explicit comparison structure plus canonical grounding evidence.

    PARTICIPANT A:
        the first article-expressed comparison side.

    PARTICIPANT B:
        the second article-expressed comparison side.

    The ordering preserves textual evidence structure. It does not
    make symmetric similarity relations semantically directional.

    Resolution is deliberately conservative. A candidate resolves only
    when its explicit construction supplies a supported two-side
    structure and exactly one grounded semantic object is located on
    each side.

    It does NOT:
    - infer missing participants,
    - orient candidates from grounding count alone,
    - select among competing groundings by similarity,
    - infer shared characteristics,
    - validate shared characteristics,
    - infer unstated differences,
    - validate difference or contrast,
    - infer equivalence,
    - perform fuzzy semantic similarity,
    - perform embedding similarity,
    - redo Analogical Intelligence,
    - redo Quantitative Intelligence,
    - redo Procedural Intelligence,
    - perform temporal reasoning,
    - perform new causal reasoning,
    - perform cross-sentence orientation,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    import re

    if not isinstance(
        similarity_grounding_result,
        Mapping,
    ):
        raise SimilarityIntelligenceError(
            "similarity_grounding_result must be a mapping."
        )

    if (
        similarity_grounding_result.get(
            "schema_version"
        )
        != "similarity_participant_grounding_v1"
    ):
        raise SimilarityIntelligenceError(
            "Stage H requires similarity_participant_grounding_v1."
        )

    if (
        similarity_grounding_result.get(
            "status"
        )
        != "SIMILARITY_PARTICIPANT_GROUNDING_COMPLETE"
    ):
        raise SimilarityIntelligenceError(
            "Similarity participant grounding must be complete."
        )

    if (
        similarity_grounding_result.get(
            "phase"
        )
        != "4.6.12"
    ):
        raise SimilarityIntelligenceError(
            "Stage H requires Phase 4.6.12 input."
        )

    if (
        similarity_grounding_result.get(
            "patch"
        )
        != "4.6.12G"
    ):
        raise SimilarityIntelligenceError(
            "Stage H requires canonical 4.6.12G input."
        )

    if (
        similarity_grounding_result.get(
            "next_stage"
        )
        != "similarity_difference_orientation"
    ):
        raise SimilarityIntelligenceError(
            "Stage G must hand off to "
            "similarity_difference_orientation."
        )

    if (
        similarity_grounding_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise SimilarityIntelligenceError(
            "Similarity Intelligence must remain transient."
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
                raise SimilarityIntelligenceError(
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
                raise SimilarityIntelligenceError(
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

    orientation_class_by_signal = {
        "SIMILAR_TO":
            "SIMILARITY",

        "RESEMBLES":
            "RESEMBLANCE",

        "ALIKE":
            "RESEMBLANCE",

        "COMPARABLE_TO":
            "COMPARABILITY",

        "SAME_AS":
            "EQUIVALENCE_COMPARISON",

        "DIFFERENT_FROM":
            "DIFFERENCE",

        "DIFFERS_FROM":
            "DIFFERENCE",

        "UNLIKE":
            "CONTRAST",

        "COMPARED_TO":
            "GENERAL_COMPARISON",

        "COMPARED_WITH":
            "GENERAL_COMPARISON",

        "IN_CONTRAST_TO":
            "CONTRAST",

        "IN_CONTRAST_WITH":
            "CONTRAST",
    }

    def unsupported_structure(
        reason: str,
        pattern: str | None,
    ) -> dict[str, Any]:
        return {
            "supported":
                False,

            "reason":
                reason,

            "participant_a_segment":
                None,

            "participant_b_segment":
                None,

            "orientation_pattern":
                pattern,
        }

    def supported_structure(
        participant_a_segment: str,
        participant_b_segment: str,
        pattern: str,
    ) -> dict[str, Any]:
        return {
            "supported":
                True,

            "reason":
                "EXPLICIT_TWO_SIDE_COMPARISON_STRUCTURE",

            "participant_a_segment":
                participant_a_segment.strip(),

            "participant_b_segment":
                participant_b_segment.strip(),

            "orientation_pattern":
                pattern,
        }

    def split_comparison_segments(
        candidate: Mapping[str, Any],
    ) -> dict[str, Any]:
        source_text = str(
            candidate.get(
                "source_text"
            )
            or ""
        ).strip()

        signal_type = str(
            candidate.get(
                "signal_type"
            )
            or ""
        )

        candidate_form = str(
            candidate.get(
                "candidate_similarity_form"
            )
            or ""
        )

        if not source_text:
            return unsupported_structure(
                "EMPTY_SOURCE_TEXT",
                None,
            )

        if signal_type == "SIMILAR_TO":
            pattern = re.compile(
                r"^(.+?)\s+(?:is|are|was|were)\s+similar\s+to\s+(.+?)(?:[.!?]|$)",
                re.IGNORECASE,
            )

            match = pattern.search(
                source_text
            )

            if match is None:
                return unsupported_structure(
                    "SIMILAR_TO_STRUCTURE_NOT_RESOLVED",
                    "PARTICIPANT_A_SIMILAR_TO_PARTICIPANT_B",
                )

            return supported_structure(
                match.group(1),
                match.group(2),
                "PARTICIPANT_A_SIMILAR_TO_PARTICIPANT_B",
            )

        if signal_type == "RESEMBLES":
            pattern = re.compile(
                r"^(.+?)\s+(?:resembles|resemble|resembled)\s+(.+?)(?:[.!?]|$)",
                re.IGNORECASE,
            )

            match = pattern.search(
                source_text
            )

            if match is None:
                return unsupported_structure(
                    "RESEMBLES_STRUCTURE_NOT_RESOLVED",
                    "PARTICIPANT_A_RESEMBLES_PARTICIPANT_B",
                )

            return supported_structure(
                match.group(1),
                match.group(2),
                "PARTICIPANT_A_RESEMBLES_PARTICIPANT_B",
            )

        if signal_type == "ALIKE":
            pattern = re.compile(
                r"^(.+?)\s+and\s+(.+?)\s+(?:are|were|seem|seemed)\s+alike(?:[.!?]|$)",
                re.IGNORECASE,
            )

            match = pattern.search(
                source_text
            )

            if match is None:
                return unsupported_structure(
                    "ALIKE_TWO_PARTICIPANT_STRUCTURE_NOT_RESOLVED",
                    "PARTICIPANT_A_AND_PARTICIPANT_B_ARE_ALIKE",
                )

            return supported_structure(
                match.group(1),
                match.group(2),
                "PARTICIPANT_A_AND_PARTICIPANT_B_ARE_ALIKE",
            )

        if signal_type == "COMPARABLE_TO":
            pattern = re.compile(
                r"^(.+?)\s+(?:is|are|was|were)\s+comparable\s+to\s+(.+?)(?:[.!?]|$)",
                re.IGNORECASE,
            )

            match = pattern.search(
                source_text
            )

            if match is None:
                return unsupported_structure(
                    "COMPARABLE_TO_STRUCTURE_NOT_RESOLVED",
                    "PARTICIPANT_A_COMPARABLE_TO_PARTICIPANT_B",
                )

            return supported_structure(
                match.group(1),
                match.group(2),
                "PARTICIPANT_A_COMPARABLE_TO_PARTICIPANT_B",
            )

        if signal_type == "SAME_AS":
            pattern = re.compile(
                r"^(.+?)\s+(?:is|are|was|were)\s+(?:the\s+)?same\s+as\s+(.+?)(?:[.!?]|$)",
                re.IGNORECASE,
            )

            match = pattern.search(
                source_text
            )

            if match is None:
                return unsupported_structure(
                    "SAME_AS_STRUCTURE_NOT_RESOLVED",
                    "PARTICIPANT_A_SAME_AS_PARTICIPANT_B",
                )

            return supported_structure(
                match.group(1),
                match.group(2),
                "PARTICIPANT_A_SAME_AS_PARTICIPANT_B",
            )

        if signal_type == "DIFFERENT_FROM":
            pattern = re.compile(
                r"^(.+?)\s+(?:is|are|was|were)\s+different\s+from\s+(.+?)(?:[.!?]|$)",
                re.IGNORECASE,
            )

            match = pattern.search(
                source_text
            )

            if match is None:
                return unsupported_structure(
                    "DIFFERENT_FROM_STRUCTURE_NOT_RESOLVED",
                    "PARTICIPANT_A_DIFFERENT_FROM_PARTICIPANT_B",
                )

            return supported_structure(
                match.group(1),
                match.group(2),
                "PARTICIPANT_A_DIFFERENT_FROM_PARTICIPANT_B",
            )

        if signal_type == "DIFFERS_FROM":
            pattern = re.compile(
                r"^(.+?)\s+(?:differs|differ|differed)\s+from\s+(.+?)(?:[.!?]|$)",
                re.IGNORECASE,
            )

            match = pattern.search(
                source_text
            )

            if match is None:
                return unsupported_structure(
                    "DIFFERS_FROM_STRUCTURE_NOT_RESOLVED",
                    "PARTICIPANT_A_DIFFERS_FROM_PARTICIPANT_B",
                )

            return supported_structure(
                match.group(1),
                match.group(2),
                "PARTICIPANT_A_DIFFERS_FROM_PARTICIPANT_B",
            )

        if signal_type == "UNLIKE":
            pattern = re.compile(
                r"^\s*unlike\s+(.+?),\s*(.+?)(?:[.!?]|$)",
                re.IGNORECASE,
            )

            match = pattern.search(
                source_text
            )

            if match is None:
                return unsupported_structure(
                    "UNLIKE_STRUCTURE_NOT_RESOLVED",
                    "UNLIKE_PARTICIPANT_A_PARTICIPANT_B",
                )

            return supported_structure(
                match.group(1),
                match.group(2),
                "UNLIKE_PARTICIPANT_A_PARTICIPANT_B",
            )

        if signal_type == "COMPARED_TO":
            pattern = re.compile(
                r"^(.+?)\s+(?:is|are|was|were|be|been|being)\s+compared\s+to\s+(.+?)(?:[.!?]|$)",
                re.IGNORECASE,
            )

            match = pattern.search(
                source_text
            )

            if match is None:
                return unsupported_structure(
                    "COMPARED_TO_STRUCTURE_NOT_RESOLVED",
                    "PARTICIPANT_A_COMPARED_TO_PARTICIPANT_B",
                )

            return supported_structure(
                match.group(1),
                match.group(2),
                "PARTICIPANT_A_COMPARED_TO_PARTICIPANT_B",
            )

        if signal_type == "COMPARED_WITH":
            pattern = re.compile(
                r"^(.+?)\s+(?:is|are|was|were|be|been|being)\s+compared\s+with\s+(.+?)(?:[.!?]|$)",
                re.IGNORECASE,
            )

            match = pattern.search(
                source_text
            )

            if match is None:
                return unsupported_structure(
                    "COMPARED_WITH_STRUCTURE_NOT_RESOLVED",
                    "PARTICIPANT_A_COMPARED_WITH_PARTICIPANT_B",
                )

            return supported_structure(
                match.group(1),
                match.group(2),
                "PARTICIPANT_A_COMPARED_WITH_PARTICIPANT_B",
            )

        if signal_type == "IN_CONTRAST_TO":
            prefix_pattern = re.compile(
                r"^\s*in\s+contrast\s+to\s+(.+?),\s*(.+?)(?:[.!?]|$)",
                re.IGNORECASE,
            )

            prefix_match = prefix_pattern.search(
                source_text
            )

            if prefix_match is not None:
                return supported_structure(
                    prefix_match.group(1),
                    prefix_match.group(2),
                    "IN_CONTRAST_TO_PARTICIPANT_A_PARTICIPANT_B",
                )

            inline_pattern = re.compile(
                r"^(.+?)\s+in\s+contrast\s+to\s+(.+?)(?:[.!?]|$)",
                re.IGNORECASE,
            )

            inline_match = inline_pattern.search(
                source_text
            )

            if inline_match is not None:
                return supported_structure(
                    inline_match.group(1),
                    inline_match.group(2),
                    "PARTICIPANT_A_IN_CONTRAST_TO_PARTICIPANT_B",
                )

            return unsupported_structure(
                "IN_CONTRAST_TO_STRUCTURE_NOT_RESOLVED",
                "IN_CONTRAST_TO_TWO_SIDE_STRUCTURE",
            )

        if signal_type == "IN_CONTRAST_WITH":
            prefix_pattern = re.compile(
                r"^\s*in\s+contrast\s+with\s+(.+?),\s*(.+?)(?:[.!?]|$)",
                re.IGNORECASE,
            )

            prefix_match = prefix_pattern.search(
                source_text
            )

            if prefix_match is not None:
                return supported_structure(
                    prefix_match.group(1),
                    prefix_match.group(2),
                    "IN_CONTRAST_WITH_PARTICIPANT_A_PARTICIPANT_B",
                )

            inline_pattern = re.compile(
                r"^(.+?)\s+in\s+contrast\s+with\s+(.+?)(?:[.!?]|$)",
                re.IGNORECASE,
            )

            inline_match = inline_pattern.search(
                source_text
            )

            if inline_match is not None:
                return supported_structure(
                    inline_match.group(1),
                    inline_match.group(2),
                    "PARTICIPANT_A_IN_CONTRAST_WITH_PARTICIPANT_B",
                )

            return unsupported_structure(
                "IN_CONTRAST_WITH_STRUCTURE_NOT_RESOLVED",
                "IN_CONTRAST_WITH_TWO_SIDE_STRUCTURE",
            )

        return unsupported_structure(
            "UNSUPPORTED_SIMILARITY_ORIENTATION_SIGNAL",
            (
                candidate_form
                or signal_type
                or None
            ),
        )

    source_candidates = list(
        similarity_grounding_result.get(
            "similarity_candidates"
        )
        or []
    )

    unit_candidate_counts = {}

    for source_unit in (
        similarity_grounding_result.get(
            "similarity_claim_units"
        )
        or []
    ):
        if not isinstance(
            source_unit,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every Similarity Claim Unit must be a mapping."
            )

        source_unit_id = str(
            source_unit.get(
                "similarity_claim_unit_id"
            )
            or ""
        )

        if not source_unit_id:
            raise SimilarityIntelligenceError(
                "Similarity Claim Unit ID is required."
            )

        if source_unit_id in unit_candidate_counts:
            raise SimilarityIntelligenceError(
                "Duplicate Similarity Claim Unit ID detected."
            )

        unit_candidate_counts[
            source_unit_id
        ] = len(
            source_unit.get(
                "similarity_candidates"
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
            raise SimilarityIntelligenceError(
                "Every similarity candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "similarity_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise SimilarityIntelligenceError(
                "Similarity candidate ID is required."
            )

        if candidate_id in oriented_by_id:
            raise SimilarityIntelligenceError(
                "Duplicate Similarity Candidate ID during orientation."
            )

        if (
            candidate.get(
                "participant_grounding_performed"
            )
            is not True
        ):
            raise SimilarityIntelligenceError(
                "Candidate participant grounding must be complete."
            )

        if (
            candidate.get(
                "similarity_difference_orientation_resolved"
            )
            is not False
        ):
            raise SimilarityIntelligenceError(
                "Candidate must not already have orientation."
            )

        if (
            candidate.get(
                "participant_a_selected"
            )
            is not False
            or candidate.get(
                "selected_participant_a"
            )
            is not None
            or candidate.get(
                "participant_b_selected"
            )
            is not False
            or candidate.get(
                "selected_participant_b"
            )
            is not None
        ):
            raise SimilarityIntelligenceError(
                "Candidate must not already have participant selection."
            )

        candidate_unit_id = str(
            candidate.get(
                "similarity_claim_unit_id"
            )
            or ""
        )

        if not candidate_unit_id:
            raise SimilarityIntelligenceError(
                "Similarity candidate claim-unit ID is required."
            )

        if candidate_unit_id not in unit_candidate_counts:
            raise SimilarityIntelligenceError(
                "Similarity candidate has no canonical claim unit."
            )

        grounding_matches = list(
            candidate.get(
                "similarity_participant_grounding_matches"
            )
            or []
        )

        grounding_match_count = candidate.get(
            "similarity_participant_grounding_match_count"
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
            raise SimilarityIntelligenceError(
                "Candidate has invalid grounding-match count."
            )

        if grounding_match_count != len(
            grounding_matches
        ):
            raise SimilarityIntelligenceError(
                "Candidate grounding-match count does not match grounding evidence."
            )

        if (
            candidate.get(
                "similarity_participant_grounded"
            )
            is not (
                grounding_match_count > 0
            )
        ):
            raise SimilarityIntelligenceError(
                "Candidate grounding flag is inconsistent with grounding evidence."
            )

        signal_type = str(
            candidate.get(
                "signal_type"
            )
            or ""
        )

        orientation_class = (
            orientation_class_by_signal.get(
                signal_type
            )
        )

        structure = split_comparison_segments(
            candidate
        )

        participant_a_segment = structure.get(
            "participant_a_segment"
        )

        participant_b_segment = structure.get(
            "participant_b_segment"
        )

        if (
            structure.get(
                "supported"
            )
            is True
        ):
            participant_a_matches = (
                unique_groundings_in_segment(
                    str(
                        participant_a_segment
                        or ""
                    ),
                    grounding_matches,
                )
            )

            participant_b_matches = (
                unique_groundings_in_segment(
                    str(
                        participant_b_segment
                        or ""
                    ),
                    grounding_matches,
                )
            )

        else:
            participant_a_matches = []
            participant_b_matches = []

        participant_a_refs = {
            item.get(
                "grounding_ref"
            )
            for item in participant_a_matches
        }

        participant_b_refs = {
            item.get(
                "grounding_ref"
            )
            for item in participant_b_matches
        }

        overlap_refs = (
            participant_a_refs
            & participant_b_refs
        )

        if orientation_class is None:
            orientation_status = (
                "SIMILARITY_DIFFERENCE_ORIENTATION_UNRESOLVED"
            )

            orientation_basis = (
                "UNSUPPORTED_SIMILARITY_ORIENTATION_SIGNAL"
            )

            orientation_resolved = False
            selected_a = None
            selected_b = None

        elif (
            structure.get(
                "supported"
            )
            is not True
        ):
            orientation_status = (
                "SIMILARITY_DIFFERENCE_ORIENTATION_UNRESOLVED"
            )

            orientation_basis = str(
                structure.get(
                    "reason"
                )
                or "UNSUPPORTED_COMPARISON_STRUCTURE"
            )

            orientation_resolved = False
            selected_a = None
            selected_b = None

        elif grounding_match_count < 2:
            orientation_status = (
                "SIMILARITY_DIFFERENCE_ORIENTATION_UNRESOLVED"
            )

            orientation_basis = (
                "INSUFFICIENT_ARTICLE_LOCAL_GROUNDING_FOR_TWO_PARTICIPANTS"
            )

            orientation_resolved = False
            selected_a = None
            selected_b = None

        elif overlap_refs:
            orientation_status = (
                "SIMILARITY_DIFFERENCE_ORIENTATION_UNRESOLVED"
            )

            orientation_basis = (
                "GROUNDING_OBJECT_OCCURS_ON_BOTH_COMPARISON_SIDES"
            )

            orientation_resolved = False
            selected_a = None
            selected_b = None

        elif (
            len(
                participant_a_matches
            )
            == 1
            and len(
                participant_b_matches
            )
            == 1
        ):
            orientation_status = (
                "SIMILARITY_DIFFERENCE_ORIENTATION_RESOLVED"
            )

            orientation_basis = (
                "EXPLICIT_TWO_SIDE_STRUCTURE_PLUS_UNIQUE_ARTICLE_LOCAL_GROUNDING"
            )

            orientation_resolved = True

            selected_a = dict(
                participant_a_matches[0]
            )

            selected_b = dict(
                participant_b_matches[0]
            )

        elif len(
            participant_a_matches
        ) == 0:
            orientation_status = (
                "SIMILARITY_DIFFERENCE_ORIENTATION_UNRESOLVED"
            )

            orientation_basis = (
                "NO_UNIQUE_PARTICIPANT_A_SIDE_GROUNDING"
            )

            orientation_resolved = False
            selected_a = None
            selected_b = None

        elif len(
            participant_b_matches
        ) == 0:
            orientation_status = (
                "SIMILARITY_DIFFERENCE_ORIENTATION_UNRESOLVED"
            )

            orientation_basis = (
                "NO_UNIQUE_PARTICIPANT_B_SIDE_GROUNDING"
            )

            orientation_resolved = False
            selected_a = None
            selected_b = None

        else:
            orientation_status = (
                "SIMILARITY_DIFFERENCE_ORIENTATION_UNRESOLVED"
            )

            orientation_basis = (
                "AMBIGUOUS_MULTIPLE_GROUNDINGS_ON_COMPARISON_SIDE"
            )

            orientation_resolved = False
            selected_a = None
            selected_b = None

        oriented = dict(
            candidate
        )

        oriented.update({
            "similarity_difference_orientation_status":
                orientation_status,

            "similarity_difference_orientation_basis":
                orientation_basis,

            "similarity_difference_orientation_class":
                orientation_class,

            "similarity_difference_orientation_pattern":
                structure.get(
                    "orientation_pattern"
                ),

            "candidate_comparison_structure_supported":
                structure.get(
                    "supported"
                )
                is True,

            "participant_a_segment":
                participant_a_segment,

            "participant_b_segment":
                participant_b_segment,

            "participant_a_side_grounding_matches":
                participant_a_matches,

            "participant_a_side_grounding_match_count":
                len(
                    participant_a_matches
                ),

            "participant_b_side_grounding_matches":
                participant_b_matches,

            "participant_b_side_grounding_match_count":
                len(
                    participant_b_matches
                ),

            "cross_side_grounding_overlap_count":
                len(
                    overlap_refs
                ),

            "selected_participant_a":
                selected_a,

            "participant_a_selected":
                selected_a
                is not None,

            "selected_participant_b":
                selected_b,

            "participant_b_selected":
                selected_b
                is not None,

            "participant_selection_performed":
                orientation_resolved,

            "similarity_difference_orientation_resolved":
                orientation_resolved,

            "shared_characteristic_validated":
                False,

            "difference_contrast_validated":
                False,

            "same_sentence_similarity_validated":
                False,

            "cross_sentence_similarity_validated":
                False,

            "similarity_evidence_assessed":
                False,

            "duplicate_resolution_performed":
                False,

            "embedding_similarity_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "unstated_shared_property_inference_performed":
                False,

            "unstated_difference_inference_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "procedural_reasoning_performed":
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
        similarity_grounding_result.get(
            "similarity_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every Similarity Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "similarity_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise SimilarityIntelligenceError(
                "Similarity Claim Unit ID is required."
            )

        if unit_id in oriented_units_by_id:
            raise SimilarityIntelligenceError(
                "Duplicate Similarity Claim Unit ID during orientation."
            )

        state = dict(
            unit.get(
                "similarity_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "similarity_participant_grounding"
            )
            != "COMPLETE"
        ):
            raise SimilarityIntelligenceError(
                "Similarity participant grounding must "
                "be COMPLETE before orientation."
            )

        if (
            state.get(
                "similarity_difference_orientation"
            )
            != "PENDING"
        ):
            raise SimilarityIntelligenceError(
                "Similarity/difference orientation must be PENDING."
            )

        updated_candidates = []

        for old_candidate in (
            unit.get(
                "similarity_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise SimilarityIntelligenceError(
                    "Every unit Similarity Candidate "
                    "reference must be a mapping."
                )

            candidate_id = str(
                old_candidate.get(
                    "similarity_candidate_id"
                )
                or ""
            )

            oriented_candidate = (
                oriented_by_id.get(
                    candidate_id
                )
            )

            if oriented_candidate is None:
                raise SimilarityIntelligenceError(
                    "Similarity candidate/unit orientation mismatch."
                )

            updated_candidates.append(
                oriented_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "similarity_difference_orientation"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            updated_boundaries.get(
                "similarity_participant_grounding_performed"
            )
            is not True
        ):
            raise SimilarityIntelligenceError(
                "Stage-G participant grounding boundary is incomplete."
            )

        if (
            updated_boundaries.get(
                "similarity_orientation_performed"
            )
            is not False
        ):
            raise SimilarityIntelligenceError(
                "Similarity orientation must not already be performed."
            )

        required_false_boundaries = (
            "shared_characteristic_validation_performed",
            "difference_contrast_validation_performed",
            "same_sentence_similarity_validation_performed",
            "cross_sentence_similarity_validation_performed",
            "similarity_evidence_assessment_performed",
            "similarity_duplicate_resolution_performed",
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

        for boundary_name in required_false_boundaries:
            if (
                updated_boundaries.get(
                    boundary_name
                )
                is not False
            ):
                raise SimilarityIntelligenceError(
                    boundary_name
                    + " must be False before Stage H."
                )

        updated_boundaries[
            "similarity_orientation_performed"
        ] = True

        updated_boundaries[
            "shared_characteristic_validation_performed"
        ] = False

        updated_boundaries[
            "difference_contrast_validation_performed"
        ] = False

        updated_boundaries[
            "same_sentence_similarity_validation_performed"
        ] = False

        updated_boundaries[
            "cross_sentence_similarity_validation_performed"
        ] = False

        updated_boundaries[
            "similarity_evidence_assessment_performed"
        ] = False

        updated_boundaries[
            "similarity_duplicate_resolution_performed"
        ] = False

        updated_boundaries[
            "embedding_similarity_performed"
        ] = False

        updated_boundaries[
            "fuzzy_similarity_performed"
        ] = False

        updated_boundaries[
            "unstated_shared_property_inference_performed"
        ] = False

        updated_boundaries[
            "unstated_difference_inference_performed"
        ] = False

        updated_boundaries[
            "analogical_reasoning_performed"
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
            "similarity_candidates":
                updated_candidates,

            "resolved_orientation_count":
                sum(
                    1
                    for candidate in updated_candidates
                    if candidate.get(
                        "similarity_difference_orientation_resolved"
                    )
                    is True
                ),

            "unresolved_orientation_count":
                sum(
                    1
                    for candidate in updated_candidates
                    if candidate.get(
                        "similarity_difference_orientation_resolved"
                    )
                    is False
                ),

            "selected_participant_a_count":
                sum(
                    1
                    for candidate in updated_candidates
                    if candidate.get(
                        "participant_a_selected"
                    )
                    is True
                ),

            "selected_participant_b_count":
                sum(
                    1
                    for candidate in updated_candidates
                    if candidate.get(
                        "participant_b_selected"
                    )
                    is True
                ),

            "similarity_analysis_state":
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
        similarity_grounding_result.get(
            "similarity_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every similarity section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "similarity_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise SimilarityIntelligenceError(
                    "Every section Similarity Claim Unit "
                    "reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "similarity_claim_unit_id"
                )
                or ""
            )

            oriented_unit = (
                oriented_units_by_id.get(
                    unit_id
                )
            )

            if oriented_unit is None:
                raise SimilarityIntelligenceError(
                    "Similarity section/unit orientation mismatch."
                )

            section_units.append(
                oriented_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "similarity_candidates"
                )
                or []
            )
        ]

        oriented_sections.append({
            **dict(
                section
            ),

            "similarity_claim_units":
                section_units,

            "similarity_candidates":
                section_candidates,

            "similarity_candidate_count":
                len(
                    section_candidates
                ),

            "resolved_orientation_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "similarity_difference_orientation_resolved"
                    )
                    is True
                ),

            "unresolved_orientation_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "similarity_difference_orientation_resolved"
                    )
                    is False
                ),

            "similarity_difference_orientation_complete":
                True,
        })

    resolved_count = sum(
        1
        for candidate in oriented_candidates
        if candidate.get(
            "similarity_difference_orientation_resolved"
        )
        is True
    )

    unresolved_count = sum(
        1
        for candidate in oriented_candidates
        if candidate.get(
            "similarity_difference_orientation_resolved"
        )
        is False
    )

    selected_a_count = sum(
        1
        for candidate in oriented_candidates
        if candidate.get(
            "participant_a_selected"
        )
        is True
    )

    selected_b_count = sum(
        1
        for candidate in oriented_candidates
        if candidate.get(
            "participant_b_selected"
        )
        is True
    )

    orientation_class_counts = {}

    for candidate in oriented_candidates:
        orientation_class = candidate.get(
            "similarity_difference_orientation_class"
        )

        if orientation_class:
            orientation_class_counts[
                orientation_class
            ] = (
                orientation_class_counts.get(
                    orientation_class,
                    0,
                )
                + 1
            )

    result = dict(
        similarity_grounding_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        boundaries.get(
            "similarity_orientation_performed"
        )
        is not False
    ):
        raise SimilarityIntelligenceError(
            "Top-level Similarity orientation must not already be performed."
        )

    boundaries[
        "similarity_orientation_performed"
    ] = True

    boundaries[
        "shared_characteristic_validation_performed"
    ] = False

    boundaries[
        "difference_contrast_validation_performed"
    ] = False

    boundaries[
        "same_sentence_similarity_validation_performed"
    ] = False

    boundaries[
        "cross_sentence_similarity_validation_performed"
    ] = False

    boundaries[
        "similarity_evidence_assessment_performed"
    ] = False

    boundaries[
        "similarity_duplicate_resolution_performed"
    ] = False

    boundaries[
        "embedding_similarity_performed"
    ] = False

    boundaries[
        "fuzzy_similarity_performed"
    ] = False

    boundaries[
        "unstated_shared_property_inference_performed"
    ] = False

    boundaries[
        "unstated_difference_inference_performed"
    ] = False

    boundaries[
        "analogical_reasoning_performed"
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
            "similarity_difference_orientation_v1",

        "patch":
            "4.6.12H",

        "status":
            "SIMILARITY_DIFFERENCE_ORIENTATION_COMPLETE",

        "similarity_sections":
            oriented_sections,

        "similarity_claim_units":
            oriented_units,

        "similarity_candidates":
            oriented_candidates,

        "similarity_difference_orientation_summary": {
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

            "selected_participant_a_count":
                selected_a_count,

            "selected_participant_b_count":
                selected_b_count,

            "orientation_class_counts":
                dict(
                    sorted(
                        orientation_class_counts.items()
                    )
                ),

            "orientation_requires_explicit_two_side_structure":
                True,

            "orientation_requires_unique_grounding_per_side":
                True,

            "grounding_count_only_orientation_performed":
                False,

            "multiple_grounding_guessing_performed":
                False,

            "cross_sentence_orientation_performed":
                False,

            "shared_characteristic_validation_performed":
                False,

            "difference_contrast_validation_performed":
                False,

            "embedding_similarity_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "unstated_shared_property_inference_performed":
                False,

            "unstated_difference_inference_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "procedural_reasoning_performed":
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
            "shared_characteristic_validation",
    })

    return result


def validate_shared_characteristics_v1(
    orientation_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate explicitly article-expressed shared characteristics for
    oriented Phase 4.6.12 Similarity candidates.

    This stage is same-sentence and article-local.

    A valid Similarity / Difference orientation does not by itself
    establish a shared characteristic. Shared-characteristic evidence
    must be explicitly expressed in the candidate's canonical sentence.

    It does NOT:
    - infer a characteristic from world knowledge,
    - infer a characteristic from embedding similarity,
    - infer a characteristic from lexical similarity,
    - infer a characteristic merely because two participants are compared,
    - infer equivalence from SAME_AS beyond the article wording,
    - validate difference or contrast,
    - use neighboring sentences,
    - redo participant orientation,
    - redo Analogical Intelligence,
    - redo Quantitative Intelligence,
    - redo Procedural Intelligence,
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
        orientation_result,
        Mapping,
    ):
        raise SimilarityIntelligenceError(
            "orientation_result must be a mapping."
        )

    if (
        orientation_result.get(
            "schema_version"
        )
        != "similarity_difference_orientation_v1"
    ):
        raise SimilarityIntelligenceError(
            "Stage I requires similarity_difference_orientation_v1."
        )

    if (
        orientation_result.get(
            "status"
        )
        != "SIMILARITY_DIFFERENCE_ORIENTATION_COMPLETE"
    ):
        raise SimilarityIntelligenceError(
            "Similarity/difference orientation must be complete before Stage I."
        )

    if (
        orientation_result.get(
            "phase"
        )
        != "4.6.12"
    ):
        raise SimilarityIntelligenceError(
            "Stage I requires Phase 4.6.12 input."
        )

    if (
        orientation_result.get(
            "patch"
        )
        != "4.6.12H"
    ):
        raise SimilarityIntelligenceError(
            "Stage I requires canonical 4.6.12H input."
        )

    if (
        orientation_result.get(
            "next_stage"
        )
        != "shared_characteristic_validation"
    ):
        raise SimilarityIntelligenceError(
            "Stage H must hand off to shared_characteristic_validation."
        )

    if (
        orientation_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise SimilarityIntelligenceError(
            "Similarity Intelligence must remain transient."
        )

    source_units = list(
        orientation_result.get(
            "similarity_claim_units"
        )
        or []
    )

    if not source_units:
        raise SimilarityIntelligenceError(
            "Similarity Claim Units are required."
        )

    candidate_to_unit = {}
    unit_ids = set()

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every Similarity Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "similarity_claim_unit_id"
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
            raise SimilarityIntelligenceError(
                "Similarity Claim Unit ID is required."
            )

        if unit_id in unit_ids:
            raise SimilarityIntelligenceError(
                "Duplicate Similarity Claim Unit ID detected."
            )

        unit_ids.add(
            unit_id
        )

        if not sentence_id:
            raise SimilarityIntelligenceError(
                "Similarity Claim Unit sentence_id is required."
            )

        if not claim_text:
            raise SimilarityIntelligenceError(
                "Similarity Claim Unit text is required."
            )

        state = dict(
            unit.get(
                "similarity_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "similarity_difference_orientation"
            )
            != "COMPLETE"
        ):
            raise SimilarityIntelligenceError(
                "Similarity/difference orientation must be COMPLETE before Stage I."
            )

        if (
            state.get(
                "shared_characteristic_validation"
            )
            != "PENDING"
        ):
            raise SimilarityIntelligenceError(
                "Shared-characteristic validation must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "similarity_participant_grounding_performed"
            )
            is not True
        ):
            raise SimilarityIntelligenceError(
                "Stage-G participant grounding boundary is incomplete."
            )

        if (
            boundaries.get(
                "similarity_orientation_performed"
            )
            is not True
        ):
            raise SimilarityIntelligenceError(
                "Stage-H Similarity orientation boundary is incomplete."
            )

        required_false_boundaries = (
            "shared_characteristic_validation_performed",
            "difference_contrast_validation_performed",
            "same_sentence_similarity_validation_performed",
            "cross_sentence_similarity_validation_performed",
            "similarity_evidence_assessment_performed",
            "similarity_duplicate_resolution_performed",
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

        for boundary_name in required_false_boundaries:
            if (
                boundaries.get(
                    boundary_name
                )
                is not False
            ):
                raise SimilarityIntelligenceError(
                    boundary_name
                    + " must be False before Stage I."
                )

        for candidate in (
            unit.get(
                "similarity_candidates"
            )
            or []
        ):
            if not isinstance(
                candidate,
                Mapping,
            ):
                raise SimilarityIntelligenceError(
                    "Every Similarity Candidate must be a mapping."
                )

            candidate_id = str(
                candidate.get(
                    "similarity_candidate_id"
                )
                or ""
            )

            if not candidate_id:
                raise SimilarityIntelligenceError(
                    "Similarity Candidate ID is required."
                )

            if candidate_id in candidate_to_unit:
                raise SimilarityIntelligenceError(
                    "Duplicate Similarity Candidate ID detected."
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
                    "EXACT_SIMILARITY_SIGNAL_SPAN_MATCH",
                )

        return (
            False,
            None,
        )

    eligible_shared_orientation_classes = {
        "SIMILARITY",
        "RESEMBLANCE",
        "COMPARABILITY",
        "EQUIVALENCE_COMPARISON",
    }

    def clean_characteristic(
        value: str,
    ) -> str | None:
        cleaned = str(
            value
            or ""
        ).strip()

        cleaned = re.sub(
            r"[.!?]+$",
            "",
            cleaned,
        ).strip()

        if not cleaned:
            return None

        return cleaned

    def extract_explicit_shared_characteristic(
        candidate: Mapping[str, Any],
        claim_text: str,
    ) -> dict[str, Any]:
        signal_type = str(
            candidate.get(
                "signal_type"
            )
            or ""
        )

        orientation_class = str(
            candidate.get(
                "similarity_difference_orientation_class"
            )
            or ""
        )

        if (
            orientation_class
            not in eligible_shared_orientation_classes
        ):
            return {
                "explicit_shared_characteristic_found":
                    False,

                "shared_characteristic_text":
                    None,

                "shared_characteristic_extraction_pattern":
                    None,

                "reason":
                    "ORIENTATION_CLASS_DOES_NOT_ASSERT_SHARED_CHARACTERISTIC",
            }

        patterns = []

        if signal_type == "SIMILAR_TO":
            patterns = [
                (
                    re.compile(
                        r"\bsimilar\s+to\s+.+?\s+in\s+(.+?)(?:[.!?]|$)",
                        re.IGNORECASE,
                    ),
                    "SIMILAR_TO_IN_CHARACTERISTIC",
                ),
                (
                    re.compile(
                        r"\bsimilar\s+to\s+.+?\s+because\s+both\s+(.+?)(?:[.!?]|$)",
                        re.IGNORECASE,
                    ),
                    "SIMILAR_TO_BECAUSE_BOTH_CHARACTERISTIC",
                ),
                (
                    re.compile(
                        r"\bsimilar\s+to\s+.+?\s+because\s+they\s+both\s+(.+?)(?:[.!?]|$)",
                        re.IGNORECASE,
                    ),
                    "SIMILAR_TO_BECAUSE_THEY_BOTH_CHARACTERISTIC",
                ),
            ]

        elif signal_type == "RESEMBLES":
            patterns = [
                (
                    re.compile(
                        r"\bresembl(?:e|es|ed)\s+.+?\s+in\s+(.+?)(?:[.!?]|$)",
                        re.IGNORECASE,
                    ),
                    "RESEMBLES_IN_CHARACTERISTIC",
                ),
            ]

        elif signal_type == "ALIKE":
            patterns = [
                (
                    re.compile(
                        r"\balike\s+in\s+(.+?)(?:[.!?]|$)",
                        re.IGNORECASE,
                    ),
                    "ALIKE_IN_CHARACTERISTIC",
                ),
            ]

        elif signal_type == "COMPARABLE_TO":
            patterns = [
                (
                    re.compile(
                        r"\bcomparable\s+to\s+.+?\s+in\s+(.+?)(?:[.!?]|$)",
                        re.IGNORECASE,
                    ),
                    "COMPARABLE_TO_IN_CHARACTERISTIC",
                ),
            ]

        elif signal_type == "SAME_AS":
            patterns = [
                (
                    re.compile(
                        r"\b(?:the\s+)?same\s+as\s+.+?\s+in\s+(.+?)(?:[.!?]|$)",
                        re.IGNORECASE,
                    ),
                    "SAME_AS_IN_CHARACTERISTIC",
                ),
            ]

        for pattern, pattern_name in patterns:
            match = pattern.search(
                claim_text
            )

            if match is None:
                continue

            characteristic = clean_characteristic(
                match.group(1)
            )

            if characteristic:
                return {
                    "explicit_shared_characteristic_found":
                        True,

                    "shared_characteristic_text":
                        characteristic,

                    "shared_characteristic_extraction_pattern":
                        pattern_name,

                    "reason":
                        None,
                }

        return {
            "explicit_shared_characteristic_found":
                False,

            "shared_characteristic_text":
                None,

            "shared_characteristic_extraction_pattern":
                None,

            "reason":
                "NO_EXPLICIT_SAME_SENTENCE_SHARED_CHARACTERISTIC",
        }

    source_candidates = list(
        orientation_result.get(
            "similarity_candidates"
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
            raise SimilarityIntelligenceError(
                "Every similarity candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "similarity_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise SimilarityIntelligenceError(
                "Similarity Candidate ID is required."
            )

        if candidate_id in validated_by_id:
            raise SimilarityIntelligenceError(
                "Duplicate top-level Similarity Candidate ID detected."
            )

        unit_info = candidate_to_unit.get(
            candidate_id
        )

        if unit_info is None:
            raise SimilarityIntelligenceError(
                "Similarity candidate has no canonical claim-unit sentence."
            )

        if (
            candidate.get(
                "shared_characteristic_validated"
            )
            is not False
        ):
            raise SimilarityIntelligenceError(
                "Candidate must not already be shared-characteristic validated."
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
                "similarity_claim_unit_id"
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
        )

        (
            signal_supported,
            signal_support_method,
        ) = signal_span_supported(
            candidate,
            claim_text,
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

        structure_supported = (
            candidate.get(
                "candidate_comparison_structure_supported"
            )
            is True
        )

        orientation_resolved = (
            candidate.get(
                "similarity_difference_orientation_resolved"
            )
            is True
        )

        participant_a_selected = (
            candidate.get(
                "participant_a_selected"
            )
            is True
            and isinstance(
                candidate.get(
                    "selected_participant_a"
                ),
                Mapping,
            )
        )

        participant_b_selected = (
            candidate.get(
                "participant_b_selected"
            )
            is True
            and isinstance(
                candidate.get(
                    "selected_participant_b"
                ),
                Mapping,
            )
        )

        participant_a_side_count = candidate.get(
            "participant_a_side_grounding_match_count"
        )

        participant_b_side_count = candidate.get(
            "participant_b_side_grounding_match_count"
        )

        overlap_count = candidate.get(
            "cross_side_grounding_overlap_count"
        )

        grounding_counts_valid = (
            isinstance(
                participant_a_side_count,
                int,
            )
            and not isinstance(
                participant_a_side_count,
                bool,
            )
            and participant_a_side_count >= 0
            and isinstance(
                participant_b_side_count,
                int,
            )
            and not isinstance(
                participant_b_side_count,
                bool,
            )
            and participant_b_side_count >= 0
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

        unique_two_side_grounding_supported = (
            grounding_counts_valid
            and participant_a_side_count == 1
            and participant_b_side_count == 1
            and overlap_count == 0
        )

        characteristic_result = (
            extract_explicit_shared_characteristic(
                candidate,
                claim_text,
            )
        )

        explicit_characteristic_found = (
            characteristic_result[
                "explicit_shared_characteristic_found"
            ]
            is True
        )

        if not article_asserted_candidate:
            validation_status = (
                "NOT_VALIDATED_NOT_ARTICLE_ASSERTED_CANDIDATE"
            )

            shared_characteristic_valid = False

            validation_reason = (
                "ARTICLE_ASSERTED_CANDIDATE_IS_NOT_TRUE"
            )

        elif not same_sentence_candidate:
            validation_status = (
                "NOT_VALIDATED_NOT_SAME_SENTENCE_CANDIDATE"
            )

            shared_characteristic_valid = False

            validation_reason = (
                "SAME_SENTENCE_CANDIDATE_IS_NOT_TRUE"
            )

        elif not same_unit_identity:
            validation_status = (
                "NOT_VALIDATED_CLAIM_UNIT_ID_MISMATCH"
            )

            shared_characteristic_valid = False

            validation_reason = (
                "CANDIDATE_CLAIM_UNIT_ID_DOES_NOT_MATCH_CANONICAL_UNIT"
            )

        elif not same_sentence_identity:
            validation_status = (
                "NOT_VALIDATED_SENTENCE_ID_MISMATCH"
            )

            shared_characteristic_valid = False

            validation_reason = (
                "CANDIDATE_SENTENCE_ID_DOES_NOT_MATCH_CLAIM_UNIT"
            )

        elif not source_text_supported:
            validation_status = (
                "NOT_VALIDATED_SOURCE_TEXT_MISMATCH"
            )

            shared_characteristic_valid = False

            validation_reason = (
                "CANDIDATE_SOURCE_TEXT_DOES_NOT_MATCH_CANONICAL_SENTENCE"
            )

        elif not signal_supported:
            validation_status = (
                "NOT_VALIDATED_SIMILARITY_SIGNAL_SPAN_UNSUPPORTED"
            )

            shared_characteristic_valid = False

            validation_reason = (
                "SIMILARITY_SIGNAL_SPAN_NOT_SUPPORTED_BY_CANONICAL_SENTENCE"
            )

        elif not structure_supported:
            validation_status = (
                "NOT_VALIDATED_COMPARISON_STRUCTURE_UNSUPPORTED"
            )

            shared_characteristic_valid = False

            validation_reason = (
                "EXPLICIT_COMPARISON_STRUCTURE_NOT_SUPPORTED"
            )

        elif not orientation_resolved:
            validation_status = (
                "NOT_VALIDATED_SIMILARITY_DIFFERENCE_ORIENTATION_UNRESOLVED"
            )

            shared_characteristic_valid = False

            validation_reason = (
                "SIMILARITY_DIFFERENCE_ORIENTATION_NOT_RESOLVED"
            )

        elif not participant_a_selected:
            validation_status = (
                "NOT_VALIDATED_PARTICIPANT_A_NOT_SELECTED"
            )

            shared_characteristic_valid = False

            validation_reason = (
                "ORIENTED_PARTICIPANT_A_SELECTION_MISSING"
            )

        elif not participant_b_selected:
            validation_status = (
                "NOT_VALIDATED_PARTICIPANT_B_NOT_SELECTED"
            )

            shared_characteristic_valid = False

            validation_reason = (
                "ORIENTED_PARTICIPANT_B_SELECTION_MISSING"
            )

        elif not grounding_counts_valid:
            validation_status = (
                "NOT_VALIDATED_INVALID_TWO_SIDE_GROUNDING_COUNTS"
            )

            shared_characteristic_valid = False

            validation_reason = (
                "PARTICIPANT_GROUNDING_COUNT_EVIDENCE_INVALID"
            )

        elif not unique_two_side_grounding_supported:
            validation_status = (
                "NOT_VALIDATED_TWO_SIDE_GROUNDING_AMBIGUOUS"
            )

            shared_characteristic_valid = False

            validation_reason = (
                "PARTICIPANT_GROUNDING_NOT_UNIQUELY_SUPPORTED"
            )

        elif not explicit_characteristic_found:
            validation_status = (
                "NOT_VALIDATED_NO_EXPLICIT_SHARED_CHARACTERISTIC"
            )

            shared_characteristic_valid = False

            validation_reason = (
                characteristic_result[
                    "reason"
                ]
                or "NO_EXPLICIT_SAME_SENTENCE_SHARED_CHARACTERISTIC"
            )

        else:
            validation_status = (
                "VALIDATED_ARTICLE_EXPRESSED_SHARED_CHARACTERISTIC"
            )

            shared_characteristic_valid = True
            validation_reason = None

        validated = dict(
            candidate
        )

        validated.update({
            "shared_characteristic_validation_status":
                validation_status,

            "shared_characteristic_valid":
                shared_characteristic_valid,

            "shared_characteristic_validation_reason":
                validation_reason,

            "explicit_shared_characteristic_found":
                explicit_characteristic_found,

            "shared_characteristic_text":
                (
                    characteristic_result[
                        "shared_characteristic_text"
                    ]
                    if shared_characteristic_valid
                    else None
                ),

            "shared_characteristic_extraction_pattern":
                (
                    characteristic_result[
                        "shared_characteristic_extraction_pattern"
                    ]
                    if shared_characteristic_valid
                    else None
                ),

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

            "same_sentence_similarity_signal_supported":
                signal_supported,

            "similarity_signal_support_method":
                signal_support_method,

            "comparison_structure_supported":
                structure_supported,

            "similarity_difference_orientation_supported":
                orientation_resolved,

            "selected_participant_a_supported":
                participant_a_selected,

            "selected_participant_b_supported":
                participant_b_selected,

            "two_side_grounding_counts_valid":
                grounding_counts_valid,

            "unique_two_side_grounding_supported":
                unique_two_side_grounding_supported,

            "shared_characteristic_evidence": {
                "similarity_claim_unit_id":
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

                "orientation_class":
                    candidate.get(
                        "similarity_difference_orientation_class"
                    ),

                "orientation_pattern":
                    candidate.get(
                        "similarity_difference_orientation_pattern"
                    ),

                "participant_a_segment":
                    candidate.get(
                        "participant_a_segment"
                    ),

                "participant_b_segment":
                    candidate.get(
                        "participant_b_segment"
                    ),

                "selected_participant_a":
                    candidate.get(
                        "selected_participant_a"
                    ),

                "selected_participant_b":
                    candidate.get(
                        "selected_participant_b"
                    ),

                "shared_characteristic_text":
                    (
                        characteristic_result[
                            "shared_characteristic_text"
                        ]
                        if shared_characteristic_valid
                        else None
                    ),

                "shared_characteristic_extraction_pattern":
                    (
                        characteristic_result[
                            "shared_characteristic_extraction_pattern"
                        ]
                        if shared_characteristic_valid
                        else None
                    ),
            },

            "shared_characteristic_validated":
                shared_characteristic_valid,

            "difference_contrast_validated":
                False,

            "same_sentence_similarity_validated":
                False,

            "cross_sentence_similarity_validated":
                False,

            "similarity_evidence_assessed":
                False,

            "duplicate_resolution_performed":
                False,

            "embedding_similarity_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "unstated_shared_property_inference_performed":
                False,

            "unstated_difference_inference_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "procedural_reasoning_performed":
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
                "similarity_claim_unit_id"
            )
            or ""
        )

        state = dict(
            unit.get(
                "similarity_analysis_state"
            )
            or {}
        )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "similarity_candidates"
            )
            or []
        ):
            candidate_id = str(
                old_candidate.get(
                    "similarity_candidate_id"
                )
                or ""
            )

            validated_candidate = (
                validated_by_id.get(
                    candidate_id
                )
            )

            if validated_candidate is None:
                raise SimilarityIntelligenceError(
                    "Similarity candidate/unit shared-characteristic mismatch."
                )

            unit_candidates.append(
                validated_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "shared_characteristic_validation"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "shared_characteristic_validation_performed"
        ] = True

        updated_boundaries[
            "difference_contrast_validation_performed"
        ] = False

        updated_boundaries[
            "same_sentence_similarity_validation_performed"
        ] = False

        updated_boundaries[
            "cross_sentence_similarity_validation_performed"
        ] = False

        updated_boundaries[
            "similarity_evidence_assessment_performed"
        ] = False

        updated_boundaries[
            "similarity_duplicate_resolution_performed"
        ] = False

        updated_boundaries[
            "embedding_similarity_performed"
        ] = False

        updated_boundaries[
            "fuzzy_similarity_performed"
        ] = False

        updated_boundaries[
            "unstated_shared_property_inference_performed"
        ] = False

        updated_boundaries[
            "unstated_difference_inference_performed"
        ] = False

        updated_boundaries[
            "analogical_reasoning_performed"
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
            "similarity_candidates":
                unit_candidates,

            "validated_shared_characteristic_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "shared_characteristic_valid"
                    )
                    is True
                ),

            "nonvalidated_shared_characteristic_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "shared_characteristic_valid"
                    )
                    is False
                ),

            "similarity_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        validated_units.append(
            updated_unit
        )

        validated_units_by_id[
            unit_id
        ] = updated_unit

    validated_sections = []

    for section in (
        orientation_result.get(
            "similarity_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every similarity section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "similarity_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise SimilarityIntelligenceError(
                    "Every section Similarity Claim Unit reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "similarity_claim_unit_id"
                )
                or ""
            )

            validated_unit = (
                validated_units_by_id.get(
                    unit_id
                )
            )

            if validated_unit is None:
                raise SimilarityIntelligenceError(
                    "Similarity section/unit shared-characteristic mismatch."
                )

            section_units.append(
                validated_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "similarity_candidates"
                )
                or []
            )
        ]

        validated_sections.append({
            **dict(
                section
            ),

            "similarity_claim_units":
                section_units,

            "similarity_candidates":
                section_candidates,

            "validated_shared_characteristic_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "shared_characteristic_valid"
                    )
                    is True
                ),

            "nonvalidated_shared_characteristic_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "shared_characteristic_valid"
                    )
                    is False
                ),

            "shared_characteristic_validation_complete":
                True,
        })

    validated_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "shared_characteristic_valid"
        )
        is True
    )

    nonvalidated_count = (
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
            "shared_characteristic_validation_performed"
        )
        is not False
    ):
        raise SimilarityIntelligenceError(
            "Top-level shared-characteristic validation must not already be performed."
        )

    boundaries[
        "shared_characteristic_validation_performed"
    ] = True

    boundaries[
        "difference_contrast_validation_performed"
    ] = False

    boundaries[
        "same_sentence_similarity_validation_performed"
    ] = False

    boundaries[
        "cross_sentence_similarity_validation_performed"
    ] = False

    boundaries[
        "similarity_evidence_assessment_performed"
    ] = False

    boundaries[
        "similarity_duplicate_resolution_performed"
    ] = False

    boundaries[
        "embedding_similarity_performed"
    ] = False

    boundaries[
        "fuzzy_similarity_performed"
    ] = False

    boundaries[
        "unstated_shared_property_inference_performed"
    ] = False

    boundaries[
        "unstated_difference_inference_performed"
    ] = False

    boundaries[
        "analogical_reasoning_performed"
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
            "similarity_shared_characteristic_validation_v1",

        "patch":
            "4.6.12I",

        "status":
            "SIMILARITY_SHARED_CHARACTERISTIC_VALIDATION_COMPLETE",

        "similarity_sections":
            validated_sections,

        "similarity_claim_units":
            validated_units,

        "similarity_candidates":
            validated_candidates,

        "shared_characteristic_validation_summary": {
            "candidate_count":
                len(
                    validated_candidates
                ),

            "validated_shared_characteristic_count":
                validated_count,

            "nonvalidated_shared_characteristic_count":
                nonvalidated_count,

            "candidate_count_accounted_for":
                (
                    validated_count
                    + nonvalidated_count
                    == len(
                        validated_candidates
                    )
                ),

            "explicit_same_sentence_characteristic_required":
                True,

            "orientation_alone_treated_as_shared_characteristic":
                False,

            "general_comparison_treated_as_shared_characteristic":
                False,

            "difference_treated_as_shared_characteristic":
                False,

            "contrast_treated_as_shared_characteristic":
                False,

            "embedding_similarity_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "unstated_shared_property_inference_performed":
                False,

            "difference_contrast_validation_performed":
                False,

            "cross_sentence_validation_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "procedural_reasoning_performed":
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
            "difference_contrast_validation",
    })

    return result


def validate_difference_contrast_v1(
    shared_characteristic_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate article-expressed Difference / Contrast relations for
    Phase 4.6.12 Similarity Intelligence.

    This stage is strictly article-local and same-sentence.

    A DIFFERENCE or CONTRAST relation may be valid even when the
    article does not explicitly name the dimension of difference.
    When a difference dimension is explicitly expressed, it is
    preserved as additional evidence.

    It does NOT:
    - infer an unstated difference,
    - infer a difference dimension from world knowledge,
    - infer difference from embedding distance,
    - infer difference from lexical dissimilarity,
    - convert general comparison into difference,
    - convert similarity/resemblance/comparability into difference,
    - redo participant orientation,
    - redo shared-characteristic validation,
    - use neighboring sentences,
    - redo Analogical Intelligence,
    - redo Quantitative Intelligence,
    - redo Procedural Intelligence,
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
        shared_characteristic_result,
        Mapping,
    ):
        raise SimilarityIntelligenceError(
            "shared_characteristic_result must be a mapping."
        )

    if (
        shared_characteristic_result.get(
            "schema_version"
        )
        != "similarity_shared_characteristic_validation_v1"
    ):
        raise SimilarityIntelligenceError(
            "Stage J requires "
            "similarity_shared_characteristic_validation_v1."
        )

    if (
        shared_characteristic_result.get(
            "status"
        )
        != "SIMILARITY_SHARED_CHARACTERISTIC_VALIDATION_COMPLETE"
    ):
        raise SimilarityIntelligenceError(
            "Shared-characteristic validation must be complete "
            "before Stage J."
        )

    if (
        shared_characteristic_result.get(
            "phase"
        )
        != "4.6.12"
    ):
        raise SimilarityIntelligenceError(
            "Stage J requires Phase 4.6.12 input."
        )

    if (
        shared_characteristic_result.get(
            "patch"
        )
        != "4.6.12I"
    ):
        raise SimilarityIntelligenceError(
            "Stage J requires canonical 4.6.12I input."
        )

    if (
        shared_characteristic_result.get(
            "next_stage"
        )
        != "difference_contrast_validation"
    ):
        raise SimilarityIntelligenceError(
            "Stage I must hand off to "
            "difference_contrast_validation."
        )

    if (
        shared_characteristic_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise SimilarityIntelligenceError(
            "Similarity Intelligence must remain transient."
        )

    source_units = list(
        shared_characteristic_result.get(
            "similarity_claim_units"
        )
        or []
    )

    if not source_units:
        raise SimilarityIntelligenceError(
            "Similarity Claim Units are required."
        )

    candidate_to_unit = {}
    unit_ids = set()

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every Similarity Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "similarity_claim_unit_id"
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
            raise SimilarityIntelligenceError(
                "Similarity Claim Unit ID is required."
            )

        if unit_id in unit_ids:
            raise SimilarityIntelligenceError(
                "Duplicate Similarity Claim Unit ID detected."
            )

        unit_ids.add(
            unit_id
        )

        if not sentence_id:
            raise SimilarityIntelligenceError(
                "Similarity Claim Unit sentence_id is required."
            )

        if not claim_text:
            raise SimilarityIntelligenceError(
                "Similarity Claim Unit text is required."
            )

        state = dict(
            unit.get(
                "similarity_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "shared_characteristic_validation"
            )
            != "COMPLETE"
        ):
            raise SimilarityIntelligenceError(
                "Shared-characteristic validation must "
                "be COMPLETE before Stage J."
            )

        if (
            state.get(
                "difference_contrast_validation"
            )
            != "PENDING"
        ):
            raise SimilarityIntelligenceError(
                "Difference/contrast validation must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "similarity_participant_grounding_performed"
            )
            is not True
        ):
            raise SimilarityIntelligenceError(
                "Stage-G participant grounding boundary is incomplete."
            )

        if (
            boundaries.get(
                "similarity_orientation_performed"
            )
            is not True
        ):
            raise SimilarityIntelligenceError(
                "Stage-H orientation boundary is incomplete."
            )

        if (
            boundaries.get(
                "shared_characteristic_validation_performed"
            )
            is not True
        ):
            raise SimilarityIntelligenceError(
                "Stage-I shared-characteristic boundary is incomplete."
            )

        required_false_boundaries = (
            "difference_contrast_validation_performed",
            "same_sentence_similarity_validation_performed",
            "cross_sentence_similarity_validation_performed",
            "similarity_evidence_assessment_performed",
            "similarity_duplicate_resolution_performed",
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

        for boundary_name in required_false_boundaries:
            if (
                boundaries.get(
                    boundary_name
                )
                is not False
            ):
                raise SimilarityIntelligenceError(
                    boundary_name
                    + " must be False before Stage J."
                )

        for candidate in (
            unit.get(
                "similarity_candidates"
            )
            or []
        ):
            if not isinstance(
                candidate,
                Mapping,
            ):
                raise SimilarityIntelligenceError(
                    "Every Similarity Candidate must be a mapping."
                )

            candidate_id = str(
                candidate.get(
                    "similarity_candidate_id"
                )
                or ""
            )

            if not candidate_id:
                raise SimilarityIntelligenceError(
                    "Similarity Candidate ID is required."
                )

            if candidate_id in candidate_to_unit:
                raise SimilarityIntelligenceError(
                    "Duplicate Similarity Candidate ID detected."
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
                    "EXACT_DIFFERENCE_CONTRAST_SIGNAL_SPAN_MATCH",
                )

        return (
            False,
            None,
        )

    eligible_orientation_classes = {
        "DIFFERENCE",
        "CONTRAST",
    }

    eligible_signal_types = {
        "DIFFERENT_FROM",
        "DIFFERS_FROM",
        "UNLIKE",
        "IN_CONTRAST_TO",
        "IN_CONTRAST_WITH",
    }

    def clean_dimension(
        value: str,
    ) -> str | None:
        cleaned = str(
            value
            or ""
        ).strip()

        cleaned = re.sub(
            r"[.!?]+$",
            "",
            cleaned,
        ).strip()

        if not cleaned:
            return None

        return cleaned

    def extract_explicit_difference_dimension(
        candidate: Mapping[str, Any],
        claim_text: str,
    ) -> dict[str, Any]:
        signal_type = str(
            candidate.get(
                "signal_type"
            )
            or ""
        )

        patterns = []

        if signal_type == "DIFFERENT_FROM":
            patterns = [
                (
                    re.compile(
                        r"\bdifferent\s+from\s+.+?\s+in\s+(.+?)(?:[.!?]|$)",
                        re.IGNORECASE,
                    ),
                    "DIFFERENT_FROM_IN_DIMENSION",
                ),
            ]

        elif signal_type == "DIFFERS_FROM":
            patterns = [
                (
                    re.compile(
                        r"\bdiffers?\s+from\s+.+?\s+in\s+(.+?)(?:[.!?]|$)",
                        re.IGNORECASE,
                    ),
                    "DIFFERS_FROM_IN_DIMENSION",
                ),
            ]

        elif signal_type == "UNLIKE":
            patterns = [
                (
                    re.compile(
                        r"^\s*unlike\s+.+?,\s*.+?\s+in\s+(.+?)(?:[.!?]|$)",
                        re.IGNORECASE,
                    ),
                    "UNLIKE_SECOND_PARTICIPANT_IN_DIMENSION",
                ),
            ]

        elif signal_type == "IN_CONTRAST_TO":
            patterns = [
                (
                    re.compile(
                        r"\bin\s+contrast\s+to\s+.+?,\s*.+?\s+in\s+(.+?)(?:[.!?]|$)",
                        re.IGNORECASE,
                    ),
                    "IN_CONTRAST_TO_EXPLICIT_DIMENSION",
                ),
            ]

        elif signal_type == "IN_CONTRAST_WITH":
            patterns = [
                (
                    re.compile(
                        r"\bin\s+contrast\s+with\s+.+?,\s*.+?\s+in\s+(.+?)(?:[.!?]|$)",
                        re.IGNORECASE,
                    ),
                    "IN_CONTRAST_WITH_EXPLICIT_DIMENSION",
                ),
            ]

        for pattern, pattern_name in patterns:
            match = pattern.search(
                claim_text
            )

            if match is None:
                continue

            dimension = clean_dimension(
                match.group(1)
            )

            if dimension:
                return {
                    "explicit_difference_dimension_found":
                        True,

                    "difference_dimension_text":
                        dimension,

                    "difference_dimension_extraction_pattern":
                        pattern_name,
                }

        return {
            "explicit_difference_dimension_found":
                False,

            "difference_dimension_text":
                None,

            "difference_dimension_extraction_pattern":
                None,
        }

    source_candidates = list(
        shared_characteristic_result.get(
            "similarity_candidates"
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
            raise SimilarityIntelligenceError(
                "Every similarity candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "similarity_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise SimilarityIntelligenceError(
                "Similarity Candidate ID is required."
            )

        if candidate_id in validated_by_id:
            raise SimilarityIntelligenceError(
                "Duplicate top-level Similarity Candidate ID detected."
            )

        unit_info = candidate_to_unit.get(
            candidate_id
        )

        if unit_info is None:
            raise SimilarityIntelligenceError(
                "Similarity candidate has no canonical claim-unit sentence."
            )

        if (
            candidate.get(
                "difference_contrast_validated"
            )
            is not False
        ):
            raise SimilarityIntelligenceError(
                "Candidate must not already be difference/contrast validated."
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
                "similarity_claim_unit_id"
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
        )

        (
            signal_supported,
            signal_support_method,
        ) = signal_span_supported(
            candidate,
            claim_text,
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

        structure_supported = (
            candidate.get(
                "candidate_comparison_structure_supported"
            )
            is True
        )

        orientation_resolved = (
            candidate.get(
                "similarity_difference_orientation_resolved"
            )
            is True
        )

        orientation_class = str(
            candidate.get(
                "similarity_difference_orientation_class"
            )
            or ""
        )

        signal_type = str(
            candidate.get(
                "signal_type"
            )
            or ""
        )

        orientation_eligible = (
            orientation_class
            in eligible_orientation_classes
            and signal_type
            in eligible_signal_types
        )

        participant_a_selected = (
            candidate.get(
                "participant_a_selected"
            )
            is True
            and isinstance(
                candidate.get(
                    "selected_participant_a"
                ),
                Mapping,
            )
        )

        participant_b_selected = (
            candidate.get(
                "participant_b_selected"
            )
            is True
            and isinstance(
                candidate.get(
                    "selected_participant_b"
                ),
                Mapping,
            )
        )

        participant_a_side_count = candidate.get(
            "participant_a_side_grounding_match_count"
        )

        participant_b_side_count = candidate.get(
            "participant_b_side_grounding_match_count"
        )

        overlap_count = candidate.get(
            "cross_side_grounding_overlap_count"
        )

        grounding_counts_valid = (
            isinstance(
                participant_a_side_count,
                int,
            )
            and not isinstance(
                participant_a_side_count,
                bool,
            )
            and participant_a_side_count >= 0
            and isinstance(
                participant_b_side_count,
                int,
            )
            and not isinstance(
                participant_b_side_count,
                bool,
            )
            and participant_b_side_count >= 0
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

        unique_two_side_grounding_supported = (
            grounding_counts_valid
            and participant_a_side_count == 1
            and participant_b_side_count == 1
            and overlap_count == 0
        )

        difference_dimension = (
            extract_explicit_difference_dimension(
                candidate,
                claim_text,
            )
        )

        if not orientation_eligible:
            validation_status = (
                "NOT_VALIDATED_NOT_DIFFERENCE_OR_CONTRAST_ORIENTATION"
            )

            relation_valid = False

            validation_reason = (
                "ORIENTATION_CLASS_DOES_NOT_ASSERT_DIFFERENCE_OR_CONTRAST"
            )

        elif not article_asserted_candidate:
            validation_status = (
                "NOT_VALIDATED_NOT_ARTICLE_ASSERTED_CANDIDATE"
            )

            relation_valid = False

            validation_reason = (
                "ARTICLE_ASSERTED_CANDIDATE_IS_NOT_TRUE"
            )

        elif not same_sentence_candidate:
            validation_status = (
                "NOT_VALIDATED_NOT_SAME_SENTENCE_CANDIDATE"
            )

            relation_valid = False

            validation_reason = (
                "SAME_SENTENCE_CANDIDATE_IS_NOT_TRUE"
            )

        elif not same_unit_identity:
            validation_status = (
                "NOT_VALIDATED_CLAIM_UNIT_ID_MISMATCH"
            )

            relation_valid = False

            validation_reason = (
                "CANDIDATE_CLAIM_UNIT_ID_DOES_NOT_MATCH_CANONICAL_UNIT"
            )

        elif not same_sentence_identity:
            validation_status = (
                "NOT_VALIDATED_SENTENCE_ID_MISMATCH"
            )

            relation_valid = False

            validation_reason = (
                "CANDIDATE_SENTENCE_ID_DOES_NOT_MATCH_CLAIM_UNIT"
            )

        elif not source_text_supported:
            validation_status = (
                "NOT_VALIDATED_SOURCE_TEXT_MISMATCH"
            )

            relation_valid = False

            validation_reason = (
                "CANDIDATE_SOURCE_TEXT_DOES_NOT_MATCH_CANONICAL_SENTENCE"
            )

        elif not signal_supported:
            validation_status = (
                "NOT_VALIDATED_DIFFERENCE_CONTRAST_SIGNAL_SPAN_UNSUPPORTED"
            )

            relation_valid = False

            validation_reason = (
                "DIFFERENCE_CONTRAST_SIGNAL_SPAN_NOT_SUPPORTED_BY_CANONICAL_SENTENCE"
            )

        elif not structure_supported:
            validation_status = (
                "NOT_VALIDATED_COMPARISON_STRUCTURE_UNSUPPORTED"
            )

            relation_valid = False

            validation_reason = (
                "EXPLICIT_COMPARISON_STRUCTURE_NOT_SUPPORTED"
            )

        elif not orientation_resolved:
            validation_status = (
                "NOT_VALIDATED_SIMILARITY_DIFFERENCE_ORIENTATION_UNRESOLVED"
            )

            relation_valid = False

            validation_reason = (
                "SIMILARITY_DIFFERENCE_ORIENTATION_NOT_RESOLVED"
            )

        elif not participant_a_selected:
            validation_status = (
                "NOT_VALIDATED_PARTICIPANT_A_NOT_SELECTED"
            )

            relation_valid = False

            validation_reason = (
                "ORIENTED_PARTICIPANT_A_SELECTION_MISSING"
            )

        elif not participant_b_selected:
            validation_status = (
                "NOT_VALIDATED_PARTICIPANT_B_NOT_SELECTED"
            )

            relation_valid = False

            validation_reason = (
                "ORIENTED_PARTICIPANT_B_SELECTION_MISSING"
            )

        elif not grounding_counts_valid:
            validation_status = (
                "NOT_VALIDATED_INVALID_TWO_SIDE_GROUNDING_COUNTS"
            )

            relation_valid = False

            validation_reason = (
                "PARTICIPANT_GROUNDING_COUNT_EVIDENCE_INVALID"
            )

        elif not unique_two_side_grounding_supported:
            validation_status = (
                "NOT_VALIDATED_TWO_SIDE_GROUNDING_AMBIGUOUS"
            )

            relation_valid = False

            validation_reason = (
                "PARTICIPANT_GROUNDING_NOT_UNIQUELY_SUPPORTED"
            )

        else:
            validation_status = (
                "VALIDATED_ARTICLE_EXPRESSED_DIFFERENCE_CONTRAST"
            )

            relation_valid = True
            validation_reason = None

        validated = dict(
            candidate
        )

        validated.update({
            "difference_contrast_validation_status":
                validation_status,

            "difference_contrast_valid":
                relation_valid,

            "difference_contrast_validation_reason":
                validation_reason,

            "difference_contrast_orientation_eligible":
                orientation_eligible,

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

            "same_sentence_difference_contrast_signal_supported":
                signal_supported,

            "difference_contrast_signal_support_method":
                signal_support_method,

            "comparison_structure_supported":
                structure_supported,

            "similarity_difference_orientation_supported":
                orientation_resolved,

            "selected_participant_a_supported":
                participant_a_selected,

            "selected_participant_b_supported":
                participant_b_selected,

            "two_side_grounding_counts_valid":
                grounding_counts_valid,

            "unique_two_side_grounding_supported":
                unique_two_side_grounding_supported,

            "explicit_difference_dimension_found":
                (
                    difference_dimension[
                        "explicit_difference_dimension_found"
                    ]
                    is True
                    and relation_valid
                ),

            "difference_dimension_text":
                (
                    difference_dimension[
                        "difference_dimension_text"
                    ]
                    if relation_valid
                    else None
                ),

            "difference_dimension_extraction_pattern":
                (
                    difference_dimension[
                        "difference_dimension_extraction_pattern"
                    ]
                    if relation_valid
                    else None
                ),

            "difference_contrast_evidence": {
                "similarity_claim_unit_id":
                    canonical_unit_id,

                "sentence_id":
                    canonical_sentence_id,

                "sentence_text":
                    claim_text,

                "signal_type":
                    signal_type,

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

                "orientation_class":
                    orientation_class,

                "orientation_pattern":
                    candidate.get(
                        "similarity_difference_orientation_pattern"
                    ),

                "participant_a_segment":
                    candidate.get(
                        "participant_a_segment"
                    ),

                "participant_b_segment":
                    candidate.get(
                        "participant_b_segment"
                    ),

                "selected_participant_a":
                    candidate.get(
                        "selected_participant_a"
                    ),

                "selected_participant_b":
                    candidate.get(
                        "selected_participant_b"
                    ),

                "explicit_difference_dimension_found":
                    (
                        difference_dimension[
                            "explicit_difference_dimension_found"
                        ]
                        is True
                        and relation_valid
                    ),

                "difference_dimension_text":
                    (
                        difference_dimension[
                            "difference_dimension_text"
                        ]
                        if relation_valid
                        else None
                    ),

                "difference_dimension_extraction_pattern":
                    (
                        difference_dimension[
                            "difference_dimension_extraction_pattern"
                        ]
                        if relation_valid
                        else None
                    ),
            },

            "difference_contrast_validated":
                relation_valid,

            "same_sentence_similarity_validated":
                False,

            "cross_sentence_similarity_validated":
                False,

            "similarity_evidence_assessed":
                False,

            "duplicate_resolution_performed":
                False,

            "embedding_similarity_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "unstated_difference_inference_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "procedural_reasoning_performed":
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
                "similarity_claim_unit_id"
            )
            or ""
        )

        state = dict(
            unit.get(
                "similarity_analysis_state"
            )
            or {}
        )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "similarity_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise SimilarityIntelligenceError(
                    "Every unit Similarity Candidate "
                    "reference must be a mapping."
                )

            candidate_id = str(
                old_candidate.get(
                    "similarity_candidate_id"
                )
                or ""
            )

            validated_candidate = (
                validated_by_id.get(
                    candidate_id
                )
            )

            if validated_candidate is None:
                raise SimilarityIntelligenceError(
                    "Similarity candidate/unit difference-contrast mismatch."
                )

            unit_candidates.append(
                validated_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "difference_contrast_validation"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "difference_contrast_validation_performed"
        ] = True

        updated_boundaries[
            "same_sentence_similarity_validation_performed"
        ] = False

        updated_boundaries[
            "cross_sentence_similarity_validation_performed"
        ] = False

        updated_boundaries[
            "similarity_evidence_assessment_performed"
        ] = False

        updated_boundaries[
            "similarity_duplicate_resolution_performed"
        ] = False

        updated_boundaries[
            "embedding_similarity_performed"
        ] = False

        updated_boundaries[
            "fuzzy_similarity_performed"
        ] = False

        updated_boundaries[
            "unstated_shared_property_inference_performed"
        ] = False

        updated_boundaries[
            "unstated_difference_inference_performed"
        ] = False

        updated_boundaries[
            "analogical_reasoning_performed"
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
            "similarity_candidates":
                unit_candidates,

            "validated_difference_contrast_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "difference_contrast_valid"
                    )
                    is True
                ),

            "nonvalidated_difference_contrast_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "difference_contrast_valid"
                    )
                    is False
                ),

            "similarity_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        validated_units.append(
            updated_unit
        )

        validated_units_by_id[
            unit_id
        ] = updated_unit

    validated_sections = []

    for section in (
        shared_characteristic_result.get(
            "similarity_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every similarity section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "similarity_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise SimilarityIntelligenceError(
                    "Every section Similarity Claim Unit "
                    "reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "similarity_claim_unit_id"
                )
                or ""
            )

            validated_unit = (
                validated_units_by_id.get(
                    unit_id
                )
            )

            if validated_unit is None:
                raise SimilarityIntelligenceError(
                    "Similarity section/unit difference-contrast mismatch."
                )

            section_units.append(
                validated_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "similarity_candidates"
                )
                or []
            )
        ]

        validated_sections.append({
            **dict(
                section
            ),

            "similarity_claim_units":
                section_units,

            "similarity_candidates":
                section_candidates,

            "validated_difference_contrast_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "difference_contrast_valid"
                    )
                    is True
                ),

            "nonvalidated_difference_contrast_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "difference_contrast_valid"
                    )
                    is False
                ),

            "difference_contrast_validation_complete":
                True,
        })

    validated_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "difference_contrast_valid"
        )
        is True
    )

    nonvalidated_count = (
        len(
            validated_candidates
        )
        - validated_count
    )

    explicit_dimension_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "explicit_difference_dimension_found"
        )
        is True
    )

    result = dict(
        shared_characteristic_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        boundaries.get(
            "difference_contrast_validation_performed"
        )
        is not False
    ):
        raise SimilarityIntelligenceError(
            "Top-level difference/contrast validation "
            "must not already be performed."
        )

    boundaries[
        "difference_contrast_validation_performed"
    ] = True

    boundaries[
        "same_sentence_similarity_validation_performed"
    ] = False

    boundaries[
        "cross_sentence_similarity_validation_performed"
    ] = False

    boundaries[
        "similarity_evidence_assessment_performed"
    ] = False

    boundaries[
        "similarity_duplicate_resolution_performed"
    ] = False

    boundaries[
        "embedding_similarity_performed"
    ] = False

    boundaries[
        "fuzzy_similarity_performed"
    ] = False

    boundaries[
        "unstated_shared_property_inference_performed"
    ] = False

    boundaries[
        "unstated_difference_inference_performed"
    ] = False

    boundaries[
        "analogical_reasoning_performed"
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
            "similarity_difference_contrast_validation_v1",

        "patch":
            "4.6.12J",

        "status":
            "SIMILARITY_DIFFERENCE_CONTRAST_VALIDATION_COMPLETE",

        "similarity_sections":
            validated_sections,

        "similarity_claim_units":
            validated_units,

        "similarity_candidates":
            validated_candidates,

        "difference_contrast_validation_summary": {
            "candidate_count":
                len(
                    validated_candidates
                ),

            "validated_difference_contrast_count":
                validated_count,

            "nonvalidated_difference_contrast_count":
                nonvalidated_count,

            "explicit_difference_dimension_count":
                explicit_dimension_count,

            "candidate_count_accounted_for":
                (
                    validated_count
                    + nonvalidated_count
                    == len(
                        validated_candidates
                    )
                ),

            "difference_dimension_required_for_relation_validation":
                False,

            "difference_orientation_required":
                True,

            "contrast_orientation_required":
                True,

            "general_comparison_treated_as_difference":
                False,

            "similarity_treated_as_difference":
                False,

            "resemblance_treated_as_difference":
                False,

            "comparability_treated_as_difference":
                False,

            "embedding_difference_performed":
                False,

            "fuzzy_difference_performed":
                False,

            "unstated_difference_inference_performed":
                False,

            "cross_sentence_validation_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "procedural_reasoning_performed":
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
            "same_sentence_similarity_validation",
    })

    return result


def validate_same_sentence_similarity_v1(
    difference_contrast_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate whether each Phase 4.6.12 Similarity candidate is fully
    supported as an article-local same-sentence comparison relation.

    Supported relation families:
    - positive similarity:
        SIMILARITY,
        RESEMBLANCE,
        COMPARABILITY,
        EQUIVALENCE_COMPARISON;
    - difference:
        DIFFERENCE,
        CONTRAST;
    - general comparison:
        GENERAL_COMPARISON.

    A positive similarity relation does not require an explicitly named
    shared characteristic at this stage. Stage I preserves one when the
    article states it.

    A DIFFERENCE / CONTRAST relation must agree with the validated
    Stage-J difference/contrast result.

    GENERAL_COMPARISON may validate as an explicit comparison relation
    without being promoted to similarity or difference.

    It does NOT:
    - infer a shared characteristic,
    - infer a difference,
    - infer comparison from semantic proximity,
    - rescue a candidate with neighboring sentences,
    - perform cross-sentence validation,
    - redo participant grounding,
    - redo orientation,
    - redo shared-characteristic extraction,
    - redo difference/contrast validation,
    - perform embedding similarity,
    - perform fuzzy similarity,
    - redo Analogical Intelligence,
    - redo Quantitative Intelligence,
    - redo Procedural Intelligence,
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
        difference_contrast_result,
        Mapping,
    ):
        raise SimilarityIntelligenceError(
            "difference_contrast_result must be a mapping."
        )

    if (
        difference_contrast_result.get(
            "schema_version"
        )
        != "similarity_difference_contrast_validation_v1"
    ):
        raise SimilarityIntelligenceError(
            "Stage K requires "
            "similarity_difference_contrast_validation_v1."
        )

    if (
        difference_contrast_result.get(
            "status"
        )
        != "SIMILARITY_DIFFERENCE_CONTRAST_VALIDATION_COMPLETE"
    ):
        raise SimilarityIntelligenceError(
            "Difference/contrast validation must be complete "
            "before Stage K."
        )

    if (
        difference_contrast_result.get(
            "phase"
        )
        != "4.6.12"
    ):
        raise SimilarityIntelligenceError(
            "Stage K requires Phase 4.6.12 input."
        )

    if (
        difference_contrast_result.get(
            "patch"
        )
        != "4.6.12J"
    ):
        raise SimilarityIntelligenceError(
            "Stage K requires canonical 4.6.12J input."
        )

    if (
        difference_contrast_result.get(
            "next_stage"
        )
        != "same_sentence_similarity_validation"
    ):
        raise SimilarityIntelligenceError(
            "Stage J must hand off to "
            "same_sentence_similarity_validation."
        )

    if (
        difference_contrast_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise SimilarityIntelligenceError(
            "Similarity Intelligence must remain transient."
        )

    source_units = list(
        difference_contrast_result.get(
            "similarity_claim_units"
        )
        or []
    )

    if not source_units:
        raise SimilarityIntelligenceError(
            "Similarity Claim Units are required."
        )

    candidate_to_unit = {}
    unit_ids = set()

    for unit in source_units:
        if not isinstance(
            unit,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every Similarity Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "similarity_claim_unit_id"
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
            raise SimilarityIntelligenceError(
                "Similarity Claim Unit ID is required."
            )

        if unit_id in unit_ids:
            raise SimilarityIntelligenceError(
                "Duplicate Similarity Claim Unit ID detected."
            )

        unit_ids.add(
            unit_id
        )

        if not sentence_id:
            raise SimilarityIntelligenceError(
                "Similarity Claim Unit sentence_id is required."
            )

        if not claim_text:
            raise SimilarityIntelligenceError(
                "Similarity Claim Unit text is required."
            )

        state = dict(
            unit.get(
                "similarity_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "difference_contrast_validation"
            )
            != "COMPLETE"
        ):
            raise SimilarityIntelligenceError(
                "Difference/contrast validation must "
                "be COMPLETE before Stage K."
            )

        if (
            state.get(
                "same_sentence_similarity_validation"
            )
            != "PENDING"
        ):
            raise SimilarityIntelligenceError(
                "Same-sentence Similarity validation must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        required_true_boundaries = (
            "similarity_participant_grounding_performed",
            "similarity_orientation_performed",
            "shared_characteristic_validation_performed",
            "difference_contrast_validation_performed",
        )

        for boundary_name in required_true_boundaries:
            if (
                boundaries.get(
                    boundary_name
                )
                is not True
            ):
                raise SimilarityIntelligenceError(
                    boundary_name
                    + " must be True before Stage K."
                )

        required_false_boundaries = (
            "same_sentence_similarity_validation_performed",
            "cross_sentence_similarity_validation_performed",
            "similarity_evidence_assessment_performed",
            "similarity_duplicate_resolution_performed",
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

        for boundary_name in required_false_boundaries:
            if (
                boundaries.get(
                    boundary_name
                )
                is not False
            ):
                raise SimilarityIntelligenceError(
                    boundary_name
                    + " must be False before Stage K."
                )

        for candidate in (
            unit.get(
                "similarity_candidates"
            )
            or []
        ):
            if not isinstance(
                candidate,
                Mapping,
            ):
                raise SimilarityIntelligenceError(
                    "Every Similarity Candidate must be a mapping."
                )

            candidate_id = str(
                candidate.get(
                    "similarity_candidate_id"
                )
                or ""
            )

            if not candidate_id:
                raise SimilarityIntelligenceError(
                    "Similarity Candidate ID is required."
                )

            if candidate_id in candidate_to_unit:
                raise SimilarityIntelligenceError(
                    "Duplicate Similarity Candidate ID detected."
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
                    "EXACT_SIMILARITY_SIGNAL_SPAN_MATCH",
                )

        return (
            False,
            None,
        )

    positive_similarity_classes = {
        "SIMILARITY",
        "RESEMBLANCE",
        "COMPARABILITY",
        "EQUIVALENCE_COMPARISON",
    }

    difference_classes = {
        "DIFFERENCE",
        "CONTRAST",
    }

    general_comparison_classes = {
        "GENERAL_COMPARISON",
    }

    supported_relation_classes = (
        positive_similarity_classes
        | difference_classes
        | general_comparison_classes
    )

    source_candidates = list(
        difference_contrast_result.get(
            "similarity_candidates"
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
            raise SimilarityIntelligenceError(
                "Every similarity candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "similarity_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise SimilarityIntelligenceError(
                "Similarity Candidate ID is required."
            )

        if candidate_id in validated_by_id:
            raise SimilarityIntelligenceError(
                "Duplicate top-level Similarity Candidate ID detected."
            )

        unit_info = candidate_to_unit.get(
            candidate_id
        )

        if unit_info is None:
            raise SimilarityIntelligenceError(
                "Similarity candidate has no canonical claim-unit sentence."
            )

        if (
            candidate.get(
                "same_sentence_similarity_validated"
            )
            is not False
        ):
            raise SimilarityIntelligenceError(
                "Candidate must not already be same-sentence validated."
            )

        if (
            candidate.get(
                "cross_sentence_similarity_validated"
            )
            is not False
        ):
            raise SimilarityIntelligenceError(
                "Stage K must not receive a cross-sentence "
                "validated candidate."
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
                "similarity_claim_unit_id"
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

        (
            signal_supported,
            signal_support_method,
        ) = signal_span_supported(
            candidate,
            claim_text,
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

        structure_supported = (
            candidate.get(
                "candidate_comparison_structure_supported"
            )
            is True
        )

        orientation_supported = (
            candidate.get(
                "similarity_difference_orientation_resolved"
            )
            is True
        )

        participant_a_supported = (
            candidate.get(
                "participant_a_selected"
            )
            is True
            and isinstance(
                candidate.get(
                    "selected_participant_a"
                ),
                Mapping,
            )
        )

        participant_b_supported = (
            candidate.get(
                "participant_b_selected"
            )
            is True
            and isinstance(
                candidate.get(
                    "selected_participant_b"
                ),
                Mapping,
            )
        )

        participant_a_side_count = candidate.get(
            "participant_a_side_grounding_match_count"
        )

        participant_b_side_count = candidate.get(
            "participant_b_side_grounding_match_count"
        )

        overlap_count = candidate.get(
            "cross_side_grounding_overlap_count"
        )

        grounding_counts_valid = (
            isinstance(
                participant_a_side_count,
                int,
            )
            and not isinstance(
                participant_a_side_count,
                bool,
            )
            and participant_a_side_count >= 0
            and isinstance(
                participant_b_side_count,
                int,
            )
            and not isinstance(
                participant_b_side_count,
                bool,
            )
            and participant_b_side_count >= 0
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

        unique_two_side_grounding_supported = (
            grounding_counts_valid
            and participant_a_side_count == 1
            and participant_b_side_count == 1
            and overlap_count == 0
        )

        orientation_class = str(
            candidate.get(
                "similarity_difference_orientation_class"
            )
            or ""
        )

        relation_class_supported = (
            orientation_class
            in supported_relation_classes
        )

        shared_validation_status = str(
            candidate.get(
                "shared_characteristic_validation_status"
            )
            or ""
        )

        difference_validation_status = str(
            candidate.get(
                "difference_contrast_validation_status"
            )
            or ""
        )

        if not shared_validation_status:
            raise SimilarityIntelligenceError(
                "Candidate is missing Stage-I "
                "shared-characteristic validation status."
            )

        if not difference_validation_status:
            raise SimilarityIntelligenceError(
                "Candidate is missing Stage-J "
                "difference/contrast validation status."
            )

        if orientation_class in positive_similarity_classes:
            upstream_relation_supported = True

            upstream_relation_basis = (
                "EXPLICIT_POSITIVE_SIMILARITY_ORIENTATION"
            )

        elif orientation_class in difference_classes:
            upstream_relation_supported = (
                candidate.get(
                    "difference_contrast_valid"
                )
                is True
                and candidate.get(
                    "difference_contrast_validated"
                )
                is True
            )

            upstream_relation_basis = (
                "VALIDATED_STAGE_J_DIFFERENCE_CONTRAST"
            )

        elif orientation_class in general_comparison_classes:
            upstream_relation_supported = True

            upstream_relation_basis = (
                "EXPLICIT_GENERAL_COMPARISON_ORIENTATION"
            )

        else:
            upstream_relation_supported = False

            upstream_relation_basis = (
                "UNSUPPORTED_RELATION_CLASS"
            )

        if not relation_class_supported:
            validation_status = (
                "NOT_VALIDATED_UNSUPPORTED_SIMILARITY_RELATION_CLASS"
            )

            same_sentence_valid = False

            validation_reason = (
                "ORIENTATION_CLASS_IS_NOT_A_SUPPORTED_SIMILARITY_RELATION"
            )

        elif not article_asserted_candidate:
            validation_status = (
                "NOT_VALIDATED_NOT_ARTICLE_ASSERTED_CANDIDATE"
            )

            same_sentence_valid = False

            validation_reason = (
                "ARTICLE_ASSERTED_CANDIDATE_IS_NOT_TRUE"
            )

        elif not same_sentence_candidate:
            validation_status = (
                "NOT_VALIDATED_NOT_SAME_SENTENCE_CANDIDATE"
            )

            same_sentence_valid = False

            validation_reason = (
                "SAME_SENTENCE_CANDIDATE_IS_NOT_TRUE"
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
                "NOT_VALIDATED_SIMILARITY_SIGNAL_SPAN_UNSUPPORTED"
            )

            same_sentence_valid = False

            validation_reason = (
                "SIMILARITY_SIGNAL_SPAN_NOT_SUPPORTED_BY_CANONICAL_SENTENCE"
            )

        elif not structure_supported:
            validation_status = (
                "NOT_VALIDATED_COMPARISON_STRUCTURE_UNSUPPORTED"
            )

            same_sentence_valid = False

            validation_reason = (
                "EXPLICIT_COMPARISON_STRUCTURE_NOT_SUPPORTED"
            )

        elif not orientation_supported:
            validation_status = (
                "NOT_VALIDATED_SIMILARITY_DIFFERENCE_ORIENTATION_UNRESOLVED"
            )

            same_sentence_valid = False

            validation_reason = (
                "SIMILARITY_DIFFERENCE_ORIENTATION_NOT_RESOLVED"
            )

        elif not participant_a_supported:
            validation_status = (
                "NOT_VALIDATED_PARTICIPANT_A_NOT_SELECTED"
            )

            same_sentence_valid = False

            validation_reason = (
                "ORIENTED_PARTICIPANT_A_SELECTION_MISSING"
            )

        elif not participant_b_supported:
            validation_status = (
                "NOT_VALIDATED_PARTICIPANT_B_NOT_SELECTED"
            )

            same_sentence_valid = False

            validation_reason = (
                "ORIENTED_PARTICIPANT_B_SELECTION_MISSING"
            )

        elif not grounding_counts_valid:
            validation_status = (
                "NOT_VALIDATED_INVALID_TWO_SIDE_GROUNDING_COUNTS"
            )

            same_sentence_valid = False

            validation_reason = (
                "PARTICIPANT_GROUNDING_COUNT_EVIDENCE_INVALID"
            )

        elif not unique_two_side_grounding_supported:
            validation_status = (
                "NOT_VALIDATED_TWO_SIDE_GROUNDING_NOT_UNIQUE"
            )

            same_sentence_valid = False

            validation_reason = (
                "PARTICIPANT_GROUNDING_NOT_UNIQUELY_SUPPORTED"
            )

        elif not upstream_relation_supported:
            validation_status = (
                "NOT_VALIDATED_UPSTREAM_RELATION_NOT_SUPPORTED"
            )

            same_sentence_valid = False

            validation_reason = (
                upstream_relation_basis
            )

        else:
            validation_status = (
                "VALIDATED_SAME_SENTENCE_SIMILARITY_EXPRESSION"
            )

            same_sentence_valid = True
            validation_reason = None

        validated = dict(
            candidate
        )

        validated.update({
            "same_sentence_similarity_validation_status":
                validation_status,

            "same_sentence_similarity_valid":
                same_sentence_valid,

            "same_sentence_similarity_validation_reason":
                validation_reason,

            "same_sentence_relation_class":
                orientation_class,

            "same_sentence_relation_class_supported":
                relation_class_supported,

            "same_sentence_upstream_relation_supported":
                upstream_relation_supported,

            "same_sentence_upstream_relation_basis":
                upstream_relation_basis,

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

            "same_sentence_similarity_signal_supported":
                signal_supported,

            "similarity_signal_support_method":
                signal_support_method,

            "same_sentence_comparison_structure_supported":
                structure_supported,

            "same_sentence_orientation_supported":
                orientation_supported,

            "same_sentence_participant_a_supported":
                participant_a_supported,

            "same_sentence_participant_b_supported":
                participant_b_supported,

            "same_sentence_grounding_counts_valid":
                grounding_counts_valid,

            "same_sentence_unique_two_side_grounding_supported":
                unique_two_side_grounding_supported,

            "same_sentence_similarity_evidence": {
                "similarity_claim_unit_id":
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

                "orientation_class":
                    orientation_class,

                "orientation_pattern":
                    candidate.get(
                        "similarity_difference_orientation_pattern"
                    ),

                "participant_a_segment":
                    candidate.get(
                        "participant_a_segment"
                    ),

                "participant_b_segment":
                    candidate.get(
                        "participant_b_segment"
                    ),

                "selected_participant_a":
                    candidate.get(
                        "selected_participant_a"
                    ),

                "selected_participant_b":
                    candidate.get(
                        "selected_participant_b"
                    ),

                "shared_characteristic_validation_status":
                    shared_validation_status,

                "shared_characteristic_valid":
                    candidate.get(
                        "shared_characteristic_valid"
                    ),

                "shared_characteristic_text":
                    candidate.get(
                        "shared_characteristic_text"
                    ),

                "difference_contrast_validation_status":
                    difference_validation_status,

                "difference_contrast_valid":
                    candidate.get(
                        "difference_contrast_valid"
                    ),

                "difference_dimension_text":
                    candidate.get(
                        "difference_dimension_text"
                    ),
            },

            "same_sentence_similarity_validated":
                same_sentence_valid,

            "cross_sentence_similarity_validated":
                False,

            "similarity_evidence_assessed":
                False,

            "duplicate_resolution_performed":
                False,

            "embedding_similarity_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "unstated_shared_property_inference_performed":
                False,

            "unstated_difference_inference_performed":
                False,

            "analogical_reasoning_performed":
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
                "similarity_claim_unit_id"
            )
            or ""
        )

        state = dict(
            unit.get(
                "similarity_analysis_state"
            )
            or {}
        )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "similarity_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise SimilarityIntelligenceError(
                    "Every unit Similarity Candidate "
                    "reference must be a mapping."
                )

            candidate_id = str(
                old_candidate.get(
                    "similarity_candidate_id"
                )
                or ""
            )

            validated_candidate = (
                validated_by_id.get(
                    candidate_id
                )
            )

            if validated_candidate is None:
                raise SimilarityIntelligenceError(
                    "Similarity candidate/unit "
                    "same-sentence-validation mismatch."
                )

            unit_candidates.append(
                validated_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "same_sentence_similarity_validation"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "same_sentence_similarity_validation_performed"
        ] = True

        updated_boundaries[
            "cross_sentence_similarity_validation_performed"
        ] = False

        updated_boundaries[
            "similarity_evidence_assessment_performed"
        ] = False

        updated_boundaries[
            "similarity_duplicate_resolution_performed"
        ] = False

        updated_boundaries[
            "embedding_similarity_performed"
        ] = False

        updated_boundaries[
            "fuzzy_similarity_performed"
        ] = False

        updated_boundaries[
            "unstated_shared_property_inference_performed"
        ] = False

        updated_boundaries[
            "unstated_difference_inference_performed"
        ] = False

        updated_boundaries[
            "analogical_reasoning_performed"
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
            "similarity_candidates":
                unit_candidates,

            "same_sentence_similarity_validated_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "same_sentence_similarity_valid"
                    )
                    is True
                ),

            "same_sentence_similarity_nonvalidated_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "same_sentence_similarity_valid"
                    )
                    is False
                ),

            "similarity_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        validated_units.append(
            updated_unit
        )

        validated_units_by_id[
            unit_id
        ] = updated_unit

    validated_sections = []

    for section in (
        difference_contrast_result.get(
            "similarity_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every similarity section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "similarity_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise SimilarityIntelligenceError(
                    "Every section Similarity Claim Unit "
                    "reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "similarity_claim_unit_id"
                )
                or ""
            )

            validated_unit = (
                validated_units_by_id.get(
                    unit_id
                )
            )

            if validated_unit is None:
                raise SimilarityIntelligenceError(
                    "Similarity section/unit same-sentence mismatch."
                )

            section_units.append(
                validated_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "similarity_candidates"
                )
                or []
            )
        ]

        validated_sections.append({
            **dict(
                section
            ),

            "similarity_claim_units":
                section_units,

            "similarity_candidates":
                section_candidates,

            "same_sentence_similarity_validated_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "same_sentence_similarity_valid"
                    )
                    is True
                ),

            "same_sentence_similarity_nonvalidated_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "same_sentence_similarity_valid"
                    )
                    is False
                ),

            "same_sentence_similarity_validation_complete":
                True,
        })

    validated_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "same_sentence_similarity_valid"
        )
        is True
    )

    nonvalidated_count = (
        len(
            validated_candidates
        )
        - validated_count
    )

    class_counts = {}

    for candidate in validated_candidates:
        relation_class = str(
            candidate.get(
                "same_sentence_relation_class"
            )
            or ""
        )

        if relation_class:
            class_counts[
                relation_class
            ] = (
                class_counts.get(
                    relation_class,
                    0,
                )
                + 1
            )

    result = dict(
        difference_contrast_result
    )

    boundaries = dict(
        result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        boundaries.get(
            "same_sentence_similarity_validation_performed"
        )
        is not False
    ):
        raise SimilarityIntelligenceError(
            "Top-level same-sentence Similarity validation "
            "must not already be performed."
        )

    boundaries[
        "same_sentence_similarity_validation_performed"
    ] = True

    boundaries[
        "cross_sentence_similarity_validation_performed"
    ] = False

    boundaries[
        "similarity_evidence_assessment_performed"
    ] = False

    boundaries[
        "similarity_duplicate_resolution_performed"
    ] = False

    boundaries[
        "embedding_similarity_performed"
    ] = False

    boundaries[
        "fuzzy_similarity_performed"
    ] = False

    boundaries[
        "unstated_shared_property_inference_performed"
    ] = False

    boundaries[
        "unstated_difference_inference_performed"
    ] = False

    boundaries[
        "analogical_reasoning_performed"
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
            "similarity_same_sentence_validation_v1",

        "patch":
            "4.6.12K",

        "status":
            "SIMILARITY_SAME_SENTENCE_VALIDATION_COMPLETE",

        "similarity_sections":
            validated_sections,

        "similarity_claim_units":
            validated_units,

        "similarity_candidates":
            validated_candidates,

        "same_sentence_similarity_validation_summary": {
            "candidate_count":
                len(
                    validated_candidates
                ),

            "validated_candidate_count":
                validated_count,

            "nonvalidated_candidate_count":
                nonvalidated_count,

            "candidate_count_accounted_for":
                (
                    validated_count
                    + nonvalidated_count
                    == len(
                        validated_candidates
                    )
                ),

            "relation_class_counts":
                dict(
                    sorted(
                        class_counts.items()
                    )
                ),

            "positive_similarity_requires_named_shared_characteristic":
                False,

            "difference_contrast_requires_stage_j_validation":
                True,

            "general_comparison_may_validate_as_comparison_only":
                True,

            "general_comparison_promoted_to_similarity":
                False,

            "general_comparison_promoted_to_difference":
                False,

            "neighboring_sentence_rescue_performed":
                False,

            "cross_sentence_validation_performed":
                False,

            "embedding_similarity_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "unstated_shared_property_inference_performed":
                False,

            "unstated_difference_inference_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "procedural_reasoning_performed":
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
            "cross_sentence_similarity_validation",
    })

    return result


def validate_cross_sentence_similarity_v1(
    same_sentence_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Assess immediate same-section adjacent-sentence corroboration for
    already-established Phase 4.6.12 Similarity relations.

    Cross-sentence support is strictly corroborative:
    - only sentence distance 1 is eligible,
    - only within the same section,
    - Stage K same-sentence validity remains authoritative,
    - adjacent sentences may mention already-grounded participants,
    - adjacency may NOT create a Similarity relation,
    - adjacency may NOT rescue an invalid Similarity relation,
    - adjacency may NOT create participant grounding,
    - adjacency may NOT create participant orientation,
    - adjacency may NOT create a shared characteristic,
    - adjacency may NOT create a difference or contrast,
    - adjacency may NOT promote a general comparison.

    It does NOT:
    - create new candidates,
    - create new entity/concept groundings,
    - create or repair participant selection,
    - create or repair orientation,
    - infer shared properties,
    - infer differences,
    - perform embedding similarity,
    - perform fuzzy similarity,
    - redo Analogical Intelligence,
    - redo Quantitative Intelligence,
    - redo Procedural Intelligence,
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
        same_sentence_result,
        Mapping,
    ):
        raise SimilarityIntelligenceError(
            "same_sentence_result must be a mapping."
        )

    if (
        same_sentence_result.get(
            "schema_version"
        )
        != "similarity_same_sentence_validation_v1"
    ):
        raise SimilarityIntelligenceError(
            "Stage L requires "
            "similarity_same_sentence_validation_v1."
        )

    if (
        same_sentence_result.get(
            "status"
        )
        != "SIMILARITY_SAME_SENTENCE_VALIDATION_COMPLETE"
    ):
        raise SimilarityIntelligenceError(
            "Same-sentence Similarity validation must "
            "be complete before Stage L."
        )

    if (
        same_sentence_result.get(
            "phase"
        )
        != "4.6.12"
    ):
        raise SimilarityIntelligenceError(
            "Stage L requires Phase 4.6.12 input."
        )

    if (
        same_sentence_result.get(
            "patch"
        )
        != "4.6.12K"
    ):
        raise SimilarityIntelligenceError(
            "Stage L requires canonical 4.6.12K input."
        )

    if (
        same_sentence_result.get(
            "next_stage"
        )
        != "cross_sentence_similarity_validation"
    ):
        raise SimilarityIntelligenceError(
            "Stage K must hand off to "
            "cross_sentence_similarity_validation."
        )

    if (
        same_sentence_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise SimilarityIntelligenceError(
            "Similarity Intelligence must remain transient."
        )

    source_units = list(
        same_sentence_result.get(
            "similarity_claim_units"
        )
        or []
    )

    if not source_units:
        raise SimilarityIntelligenceError(
            "Similarity Claim Units are required."
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
            raise SimilarityIntelligenceError(
                "Every Similarity Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "similarity_claim_unit_id"
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
            raise SimilarityIntelligenceError(
                "Similarity Claim Unit ID is required."
            )

        if unit_id in seen_unit_ids:
            raise SimilarityIntelligenceError(
                "Duplicate Similarity Claim Unit ID detected."
            )

        seen_unit_ids.add(
            unit_id
        )

        if not sentence_id:
            raise SimilarityIntelligenceError(
                "Similarity Claim Unit sentence_id is required."
            )

        if sentence_id in seen_sentence_ids:
            raise SimilarityIntelligenceError(
                "Duplicate Similarity sentence_id detected."
            )

        seen_sentence_ids.add(
            sentence_id
        )

        if not section_id:
            raise SimilarityIntelligenceError(
                "Similarity Claim Unit section_id is required."
            )

        if not claim_text:
            raise SimilarityIntelligenceError(
                "Similarity Claim Unit text is required."
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
            raise SimilarityIntelligenceError(
                "sentence_global_index must be an integer."
            )

        if (
            previous_global_index is not None
            and sentence_global_index
            <= previous_global_index
        ):
            raise SimilarityIntelligenceError(
                "Similarity Claim Units are not in "
                "canonical sentence order."
            )

        previous_global_index = (
            sentence_global_index
        )

        state = dict(
            unit.get(
                "similarity_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "same_sentence_similarity_validation"
            )
            != "COMPLETE"
        ):
            raise SimilarityIntelligenceError(
                "Same-sentence Similarity validation must "
                "be COMPLETE before Stage L."
            )

        if (
            state.get(
                "cross_sentence_similarity_validation"
            )
            != "PENDING"
        ):
            raise SimilarityIntelligenceError(
                "Cross-sentence Similarity validation must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "same_sentence_similarity_validation_performed"
            )
            is not True
        ):
            raise SimilarityIntelligenceError(
                "Stage-K same-sentence Similarity validation "
                "boundary is incomplete."
            )

        required_false_boundaries = (
            "cross_sentence_similarity_validation_performed",
            "similarity_evidence_assessment_performed",
            "similarity_duplicate_resolution_performed",
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

        for boundary_name in required_false_boundaries:
            if (
                boundaries.get(
                    boundary_name
                )
                is not False
            ):
                raise SimilarityIntelligenceError(
                    boundary_name
                    + " must be False before Stage L."
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
                "similarity_candidates"
            )
            or []
        ):
            if not isinstance(
                candidate,
                Mapping,
            ):
                raise SimilarityIntelligenceError(
                    "Every Similarity Candidate must be a mapping."
                )

            candidate_id = str(
                candidate.get(
                    "similarity_candidate_id"
                )
                or ""
            )

            if not candidate_id:
                raise SimilarityIntelligenceError(
                    "Similarity Candidate ID is required."
                )

            if candidate_id in candidate_to_record:
                raise SimilarityIntelligenceError(
                    "Duplicate Similarity Candidate ID detected."
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
            "selected_participant_a",
            "selected_participant_b",
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
                "similarity_participant_grounding_matches"
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
                    "ADJACENT_SIMILARITY_CONTEXT_CORROBORATION",

                "selected_participant_a":
                    candidate.get(
                        "selected_participant_a"
                    ),

                "selected_participant_b":
                    candidate.get(
                        "selected_participant_b"
                    ),

                "creates_similarity_expression":
                    False,

                "creates_participant_grounding":
                    False,

                "creates_participant_orientation":
                    False,

                "creates_shared_characteristic":
                    False,

                "creates_difference_contrast":
                    False,

                "promotes_general_comparison":
                    False,
            })

        return support

    source_candidates = list(
        same_sentence_result.get(
            "similarity_candidates"
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
            raise SimilarityIntelligenceError(
                "Every Similarity Candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "similarity_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise SimilarityIntelligenceError(
                "Similarity Candidate ID is required."
            )

        if candidate_id in validated_by_id:
            raise SimilarityIntelligenceError(
                "Duplicate top-level Similarity Candidate ID detected."
            )

        record = candidate_to_record.get(
            candidate_id
        )

        if record is None:
            raise SimilarityIntelligenceError(
                "Similarity candidate has no canonical claim unit."
            )

        if (
            candidate.get(
                "cross_sentence_similarity_validated"
            )
            is not False
        ):
            raise SimilarityIntelligenceError(
                "Candidate must not already be "
                "cross-sentence Similarity validated."
            )

        same_sentence_valid = (
            candidate.get(
                "same_sentence_similarity_valid"
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
                "same_sentence_similarity_signal_supported"
            )
            is True
        )

        structure_supported = (
            candidate.get(
                "same_sentence_comparison_structure_supported"
            )
            is True
        )

        orientation_supported = (
            candidate.get(
                "same_sentence_orientation_supported"
            )
            is True
        )

        participant_a_supported = (
            candidate.get(
                "same_sentence_participant_a_supported"
            )
            is True
        )

        participant_b_supported = (
            candidate.get(
                "same_sentence_participant_b_supported"
            )
            is True
        )

        unique_grounding_supported = (
            candidate.get(
                "same_sentence_unique_two_side_grounding_supported"
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
            and structure_supported
            and orientation_supported
            and participant_a_supported
            and participant_b_supported
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
            final_similarity_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_CREATE_ARTICLE_ASSERTION"
            )

        elif not same_sentence_candidate_confirmed:
            cross_sentence_status = (
                "NOT_VALIDATED_SAME_SENTENCE_CANDIDATE_ASSERTION_FAILED"
            )

            cross_sentence_valid = False
            final_similarity_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_CREATE_SAME_SENTENCE_CANDIDATE"
            )

        elif not same_unit_match:
            cross_sentence_status = (
                "NOT_VALIDATED_CLAIM_UNIT_MISMATCH"
            )

            cross_sentence_valid = False
            final_similarity_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_REPAIR_CLAIM_UNIT_IDENTITY"
            )

        elif not same_sentence_id_match:
            cross_sentence_status = (
                "NOT_VALIDATED_SENTENCE_ID_MISMATCH"
            )

            cross_sentence_valid = False
            final_similarity_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_REPAIR_SENTENCE_IDENTITY"
            )

        elif not same_source_text_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_SOURCE_TEXT_MISMATCH"
            )

            cross_sentence_valid = False
            final_similarity_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_REPAIR_SOURCE_TEXT_CONTINUITY"
            )

        elif not same_signal_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_PRIMARY_SIMILARITY_SIGNAL_UNSUPPORTED"
            )

            cross_sentence_valid = False
            final_similarity_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_CREATE_PRIMARY_SIMILARITY_SIGNAL"
            )

        elif not structure_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_COMPARISON_STRUCTURE_UNSUPPORTED"
            )

            cross_sentence_valid = False
            final_similarity_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_CREATE_COMPARISON_STRUCTURE"
            )

        elif not orientation_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_SIMILARITY_DIFFERENCE_ORIENTATION_UNRESOLVED"
            )

            cross_sentence_valid = False
            final_similarity_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_CREATE_ORIENTATION"
            )

        elif not participant_a_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_PARTICIPANT_A_UNSUPPORTED"
            )

            cross_sentence_valid = False
            final_similarity_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_CREATE_PARTICIPANT_A_SELECTION"
            )

        elif not participant_b_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_PARTICIPANT_B_UNSUPPORTED"
            )

            cross_sentence_valid = False
            final_similarity_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_CREATE_PARTICIPANT_B_SELECTION"
            )

        elif not unique_grounding_supported:
            cross_sentence_status = (
                "NOT_VALIDATED_TWO_SIDE_GROUNDING_NOT_UNIQUE"
            )

            cross_sentence_valid = False
            final_similarity_expression_validated = False

            validation_reason = (
                "ADJACENT_SENTENCE_CANNOT_REPAIR_TWO_SIDE_GROUNDING"
            )

        elif same_sentence_valid:
            cross_sentence_status = (
                "NOT_REQUIRED_SAME_SENTENCE_VALIDATION_SUFFICIENT"
            )

            cross_sentence_valid = False
            final_similarity_expression_validated = True

            validation_reason = (
                "SAME_SENTENCE_SIMILARITY_VALIDATION_ALREADY_SUFFICIENT"
            )

        else:
            cross_sentence_status = (
                "NOT_VALIDATED_SAME_SENTENCE_EXPRESSION_INSUFFICIENT"
            )

            cross_sentence_valid = False
            final_similarity_expression_validated = False

            validation_reason = (
                "CROSS_SENTENCE_PROXIMITY_CANNOT_CREATE_SIMILARITY_EXPRESSION"
            )

        validated = dict(
            candidate
        )

        validated.update({
            "cross_sentence_similarity_validation_status":
                cross_sentence_status,

            "cross_sentence_similarity_valid":
                cross_sentence_valid,

            "cross_sentence_similarity_validation_reason":
                validation_reason,

            "adjacent_same_section_sentence_count":
                len(
                    adjacent_records
                ),

            "adjacent_similarity_support_present":
                adjacent_support_present,

            "adjacent_similarity_support_count":
                len(
                    adjacent_support_evidence
                ),

            "adjacent_similarity_support_evidence":
                adjacent_support_evidence,

            "cross_sentence_adjacency_policy":
                "IMMEDIATE_SENTENCE_DISTANCE_1_SAME_SECTION_ONLY",

            "cross_sentence_support_policy":
                (
                    "CORROBORATION_ONLY_FOR_ALREADY_VALIDATED_"
                    "SAME_SENTENCE_SIMILARITY_EXPRESSION"
                ),

            "adjacent_sentence_may_create_similarity_expression":
                False,

            "adjacent_sentence_may_create_participant_grounding":
                False,

            "adjacent_sentence_may_create_participant_orientation":
                False,

            "adjacent_sentence_may_create_shared_characteristic":
                False,

            "adjacent_sentence_may_create_difference_contrast":
                False,

            "adjacent_sentence_may_promote_general_comparison":
                False,

            "final_similarity_expression_validated":
                final_similarity_expression_validated,

            "cross_sentence_similarity_validated":
                cross_sentence_valid,

            "similarity_evidence_assessed":
                False,

            "duplicate_resolution_performed":
                False,

            "embedding_similarity_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "unstated_shared_property_inference_performed":
                False,

            "unstated_difference_inference_performed":
                False,

            "analogical_reasoning_performed":
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
                "similarity_analysis_state"
            )
            or {}
        )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "similarity_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise SimilarityIntelligenceError(
                    "Every unit Similarity Candidate "
                    "reference must be a mapping."
                )

            candidate_id = str(
                old_candidate.get(
                    "similarity_candidate_id"
                )
                or ""
            )

            validated_candidate = (
                validated_by_id.get(
                    candidate_id
                )
            )

            if validated_candidate is None:
                raise SimilarityIntelligenceError(
                    "Similarity candidate/unit "
                    "cross-sentence validation mismatch."
                )

            unit_candidates.append(
                validated_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "cross_sentence_similarity_validation"
        ] = "COMPLETE"

        updated_boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        updated_boundaries[
            "cross_sentence_similarity_validation_performed"
        ] = True

        updated_boundaries[
            "similarity_evidence_assessment_performed"
        ] = False

        updated_boundaries[
            "similarity_duplicate_resolution_performed"
        ] = False

        updated_boundaries[
            "embedding_similarity_performed"
        ] = False

        updated_boundaries[
            "fuzzy_similarity_performed"
        ] = False

        updated_boundaries[
            "unstated_shared_property_inference_performed"
        ] = False

        updated_boundaries[
            "unstated_difference_inference_performed"
        ] = False

        updated_boundaries[
            "analogical_reasoning_performed"
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
            "similarity_candidates":
                unit_candidates,

            "adjacent_similarity_support_candidate_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "adjacent_similarity_support_present"
                    )
                    is True
                ),

            "final_similarity_expression_validated_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "final_similarity_expression_validated"
                    )
                    is True
                ),

            "cross_sentence_similarity_validated_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "cross_sentence_similarity_valid"
                    )
                    is True
                ),

            "similarity_analysis_state":
                updated_state,

            "processing_boundaries":
                updated_boundaries,
        })

        validated_units.append(
            updated_unit
        )

        validated_units_by_id[
            unit_id
        ] = updated_unit

    validated_sections = []

    for section in (
        same_sentence_result.get(
            "similarity_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every similarity section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "similarity_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise SimilarityIntelligenceError(
                    "Every section Similarity Claim Unit "
                    "reference must be a mapping."
                )

            unit_id = str(
                old_unit.get(
                    "similarity_claim_unit_id"
                )
                or ""
            )

            validated_unit = (
                validated_units_by_id.get(
                    unit_id
                )
            )

            if validated_unit is None:
                raise SimilarityIntelligenceError(
                    "Similarity section/unit cross-sentence mismatch."
                )

            section_units.append(
                validated_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "similarity_candidates"
                )
                or []
            )
        ]

        validated_sections.append({
            **dict(
                section
            ),

            "similarity_claim_units":
                section_units,

            "similarity_candidates":
                section_candidates,

            "adjacent_similarity_support_candidate_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "adjacent_similarity_support_present"
                    )
                    is True
                ),

            "final_similarity_expression_validated_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "final_similarity_expression_validated"
                    )
                    is True
                ),

            "cross_sentence_similarity_validation_complete":
                True,
        })

    adjacent_support_candidate_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "adjacent_similarity_support_present"
        )
        is True
    )

    adjacent_support_evidence_count = sum(
        int(
            candidate.get(
                "adjacent_similarity_support_count"
            )
            or 0
        )
        for candidate in validated_candidates
    )

    final_validated_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "final_similarity_expression_validated"
        )
        is True
    )

    cross_sentence_validated_count = sum(
        1
        for candidate in validated_candidates
        if candidate.get(
            "cross_sentence_similarity_valid"
        )
        is True
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
            "cross_sentence_similarity_validation_performed"
        )
        is not False
    ):
        raise SimilarityIntelligenceError(
            "Top-level cross-sentence Similarity validation "
            "must not already be performed."
        )

    boundaries[
        "cross_sentence_similarity_validation_performed"
    ] = True

    boundaries[
        "similarity_evidence_assessment_performed"
    ] = False

    boundaries[
        "similarity_duplicate_resolution_performed"
    ] = False

    boundaries[
        "embedding_similarity_performed"
    ] = False

    boundaries[
        "fuzzy_similarity_performed"
    ] = False

    boundaries[
        "unstated_shared_property_inference_performed"
    ] = False

    boundaries[
        "unstated_difference_inference_performed"
    ] = False

    boundaries[
        "analogical_reasoning_performed"
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
            "similarity_cross_sentence_validation_v1",

        "patch":
            "4.6.12L",

        "status":
            "SIMILARITY_CROSS_SENTENCE_VALIDATION_COMPLETE",

        "similarity_sections":
            validated_sections,

        "similarity_claim_units":
            validated_units,

        "similarity_candidates":
            validated_candidates,

        "cross_sentence_similarity_validation_summary": {
            "candidate_count":
                len(
                    validated_candidates
                ),

            "adjacent_support_candidate_count":
                adjacent_support_candidate_count,

            "adjacent_support_evidence_count":
                adjacent_support_evidence_count,

            "final_similarity_expression_validated_count":
                final_validated_count,

            "cross_sentence_similarity_validated_count":
                cross_sentence_validated_count,

            "sentence_distance_limit":
                1,

            "same_section_only":
                True,

            "same_sentence_validation_authoritative":
                True,

            "cross_sentence_support_is_corroboration_only":
                True,

            "cross_sentence_may_create_relation":
                False,

            "cross_sentence_may_rescue_invalid_relation":
                False,

            "cross_sentence_may_create_grounding":
                False,

            "cross_sentence_may_create_orientation":
                False,

            "cross_sentence_may_create_shared_characteristic":
                False,

            "cross_sentence_may_create_difference_contrast":
                False,

            "cross_sentence_may_promote_general_comparison":
                False,

            "embedding_similarity_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "unstated_shared_property_inference_performed":
                False,

            "unstated_difference_inference_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "procedural_reasoning_performed":
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
            "similarity_evidence_confidence_assessment",
    })

    return result


def assess_similarity_confidence_evidence_v1(
    cross_sentence_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Assess article-local evidence strength for Phase 4.6.12 Similarity
    expressions already processed through same-sentence and
    cross-sentence validation.

    Confidence measures how strongly the article itself supports the
    extracted comparison relation. It does NOT measure factual,
    scientific, medical, operational, or real-world truth.

    Safeguards:
    - unvalidated Similarity expressions receive zero confidence,
    - Stage-K same-sentence validation is authoritative,
    - Stage-L adjacent evidence is corroborative only,
    - Participant A and Participant B must remain uniquely grounded,
    - exactly one grounding per side and zero overlap are required,
    - grounding confidence comes only from existing article-local
      semantic-object extraction confidence,
    - DIFFERENCE / CONTRAST must remain supported by Stage J,
    - positive similarity does not require a named shared property,
    - GENERAL_COMPARISON is assessed only as comparison,
    - no new relation, property, difference, orientation, or grounding
      is created.

    It does NOT:
    - create or rescue a Similarity candidate,
    - infer a shared characteristic,
    - infer a difference,
    - create participant orientation,
    - select new participants,
    - perform embedding similarity,
    - perform fuzzy similarity,
    - perform Analogical Intelligence,
    - perform Quantitative Intelligence,
    - perform Procedural Intelligence,
    - perform temporal reasoning,
    - perform new causal reasoning,
    - establish factual/scientific truth,
    - perform external verification,
    - resolve duplicate Similarity expressions,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        cross_sentence_result,
        Mapping,
    ):
        raise SimilarityIntelligenceError(
            "cross_sentence_result must be a mapping."
        )

    if (
        cross_sentence_result.get(
            "schema_version"
        )
        != "similarity_cross_sentence_validation_v1"
    ):
        raise SimilarityIntelligenceError(
            "Stage M requires "
            "similarity_cross_sentence_validation_v1."
        )

    if (
        cross_sentence_result.get(
            "status"
        )
        != "SIMILARITY_CROSS_SENTENCE_VALIDATION_COMPLETE"
    ):
        raise SimilarityIntelligenceError(
            "Cross-sentence Similarity validation "
            "must be complete before Stage M."
        )

    if (
        cross_sentence_result.get(
            "phase"
        )
        != "4.6.12"
    ):
        raise SimilarityIntelligenceError(
            "Stage M requires Phase 4.6.12 input."
        )

    if (
        cross_sentence_result.get(
            "patch"
        )
        != "4.6.12L"
    ):
        raise SimilarityIntelligenceError(
            "Stage M requires canonical 4.6.12L input."
        )

    if (
        cross_sentence_result.get(
            "next_stage"
        )
        != "similarity_evidence_confidence_assessment"
    ):
        raise SimilarityIntelligenceError(
            "Stage L must hand off to "
            "similarity_evidence_confidence_assessment."
        )

    if (
        cross_sentence_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise SimilarityIntelligenceError(
            "Similarity Intelligence must remain transient."
        )

    source_candidates = list(
        cross_sentence_result.get(
            "similarity_candidates"
        )
        or []
    )

    assessed_candidates = []
    seen_candidate_ids = set()

    positive_similarity_classes = {
        "SIMILARITY",
        "RESEMBLANCE",
        "COMPARABILITY",
        "EQUIVALENCE_COMPARISON",
    }

    difference_classes = {
        "DIFFERENCE",
        "CONTRAST",
    }

    general_comparison_classes = {
        "GENERAL_COMPARISON",
    }

    supported_classes = (
        positive_similarity_classes
        | difference_classes
        | general_comparison_classes
    )

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every Similarity Candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "similarity_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise SimilarityIntelligenceError(
                "Similarity Candidate ID is required."
            )

        if candidate_id in seen_candidate_ids:
            raise SimilarityIntelligenceError(
                "Duplicate Similarity Candidate ID detected."
            )

        seen_candidate_ids.add(
            candidate_id
        )

        evidence_state = candidate.get(
            "similarity_evidence_assessed"
        )

        if (
            evidence_state is True
            or (
                evidence_state is not False
                and evidence_state is not None
            )
        ):
            raise SimilarityIntelligenceError(
                "Candidate must not already have "
                "Similarity evidence assessment."
            )

        if (
            candidate.get(
                "duplicate_resolution_performed"
            )
            is not False
        ):
            raise SimilarityIntelligenceError(
                "Stage M must not receive a duplicate-resolved candidate."
            )

        final_validated = (
            candidate.get(
                "final_similarity_expression_validated"
            )
            is True
        )

        same_sentence_valid = (
            candidate.get(
                "same_sentence_similarity_valid"
            )
            is True
        )

        cross_sentence_valid = (
            candidate.get(
                "cross_sentence_similarity_valid"
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
                "same_sentence_similarity_signal_supported"
            )
            is True
        )

        structure_supported = (
            candidate.get(
                "same_sentence_comparison_structure_supported"
            )
            is True
        )

        orientation_supported = (
            candidate.get(
                "same_sentence_orientation_supported"
            )
            is True
        )

        participant_a_supported = (
            candidate.get(
                "same_sentence_participant_a_supported"
            )
            is True
        )

        participant_b_supported = (
            candidate.get(
                "same_sentence_participant_b_supported"
            )
            is True
        )

        unique_two_side_grounding = (
            candidate.get(
                "same_sentence_unique_two_side_grounding_supported"
            )
            is True
        )

        adjacent_support_present = (
            candidate.get(
                "adjacent_similarity_support_present"
            )
            is True
        )

        orientation_class = str(
            candidate.get(
                "same_sentence_relation_class"
            )
            or candidate.get(
                "similarity_difference_orientation_class"
            )
            or ""
        )

        if (
            final_validated
            and orientation_class not in supported_classes
        ):
            raise SimilarityIntelligenceError(
                "Final validated Similarity candidate has "
                "unsupported relation class."
            )

        participant_a_matches = list(
            candidate.get(
                "participant_a_side_grounding_matches"
            )
            or []
        )

        participant_b_matches = list(
            candidate.get(
                "participant_b_side_grounding_matches"
            )
            or []
        )

        participant_a_count = candidate.get(
            "participant_a_side_grounding_match_count"
        )

        participant_b_count = candidate.get(
            "participant_b_side_grounding_match_count"
        )

        overlap_count = candidate.get(
            "cross_side_grounding_overlap_count"
        )

        for name, value in (
            (
                "participant_a_side_grounding_match_count",
                participant_a_count,
            ),
            (
                "participant_b_side_grounding_match_count",
                participant_b_count,
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
                raise SimilarityIntelligenceError(
                    name
                    + " must be a non-negative integer."
                )

        if participant_a_count != len(
            participant_a_matches
        ):
            raise SimilarityIntelligenceError(
                "Participant-A grounding count mismatch."
            )

        if participant_b_count != len(
            participant_b_matches
        ):
            raise SimilarityIntelligenceError(
                "Participant-B grounding count mismatch."
            )

        selected_a = candidate.get(
            "selected_participant_a"
        )

        selected_b = candidate.get(
            "selected_participant_b"
        )

        grounding_confidences = []

        if final_validated:
            if not (
                same_sentence_valid
                and article_asserted_confirmed
                and same_sentence_candidate_confirmed
                and exact_signal_supported
                and structure_supported
                and orientation_supported
                and participant_a_supported
                and participant_b_supported
                and unique_two_side_grounding
            ):
                raise SimilarityIntelligenceError(
                    "Final validated Similarity candidate has "
                    "inconsistent Stage-K support."
                )

            if cross_sentence_valid:
                raise SimilarityIntelligenceError(
                    "Stage-L corroboration must not independently "
                    "validate a Similarity relation."
                )

            if (
                participant_a_count != 1
                or participant_b_count != 1
                or overlap_count != 0
            ):
                raise SimilarityIntelligenceError(
                    "Final validated Similarity relation must have "
                    "exactly one unique grounding per participant side "
                    "and zero overlap."
                )

            if not isinstance(
                selected_a,
                Mapping,
            ):
                raise SimilarityIntelligenceError(
                    "Final validated Similarity relation requires "
                    "selected_participant_a."
                )

            if not isinstance(
                selected_b,
                Mapping,
            ):
                raise SimilarityIntelligenceError(
                    "Final validated Similarity relation requires "
                    "selected_participant_b."
                )

            for role, grounding in (
                (
                    "participant_a",
                    selected_a,
                ),
                (
                    "participant_b",
                    selected_b,
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
                    raise SimilarityIntelligenceError(
                        "Selected "
                        + role
                        + " has invalid extraction_confidence."
                    )

                grounding_confidences.append(
                    float(
                        confidence
                    )
                )

            participant_a_ref = str(
                selected_a.get(
                    "grounding_ref"
                )
                or ""
            )

            participant_b_ref = str(
                selected_b.get(
                    "grounding_ref"
                )
                or ""
            )

            if not participant_a_ref:
                raise SimilarityIntelligenceError(
                    "Selected Participant A requires grounding_ref."
                )

            if not participant_b_ref:
                raise SimilarityIntelligenceError(
                    "Selected Participant B requires grounding_ref."
                )

            participant_a_match_refs = {
                str(
                    grounding.get(
                        "grounding_ref"
                    )
                    or ""
                )
                for grounding in participant_a_matches
                if isinstance(
                    grounding,
                    Mapping,
                )
            }

            participant_b_match_refs = {
                str(
                    grounding.get(
                        "grounding_ref"
                    )
                    or ""
                )
                for grounding in participant_b_matches
                if isinstance(
                    grounding,
                    Mapping,
                )
            }

            if participant_a_ref not in participant_a_match_refs:
                raise SimilarityIntelligenceError(
                    "Selected Participant A does not match "
                    "Participant-A grounding evidence."
                )

            if participant_b_ref not in participant_b_match_refs:
                raise SimilarityIntelligenceError(
                    "Selected Participant B does not match "
                    "Participant-B grounding evidence."
                )

            if orientation_class in difference_classes:
                if not (
                    candidate.get(
                        "difference_contrast_valid"
                    )
                    is True
                    and candidate.get(
                        "difference_contrast_validated"
                    )
                    is True
                ):
                    raise SimilarityIntelligenceError(
                        "Final validated DIFFERENCE / CONTRAST relation "
                        "must retain Stage-J validation."
                    )

            if orientation_class in general_comparison_classes:
                if (
                    candidate.get(
                        "difference_contrast_valid"
                    )
                    is True
                ):
                    raise SimilarityIntelligenceError(
                        "GENERAL_COMPARISON must not be promoted "
                        "to difference/contrast."
                    )

        if grounding_confidences:
            two_side_grounding_confidence = round(
                sum(
                    grounding_confidences
                )
                / len(
                    grounding_confidences
                ),
                3,
            )

        else:
            two_side_grounding_confidence = None

        if not final_validated:
            evidence_score = 0.0

            evidence_strength = (
                "INSUFFICIENT"
            )

            primary_basis = (
                "SIMILARITY_EXPRESSION_NOT_VALIDATED"
            )

        else:
            evidence_score = 0.48

            evidence_score += 0.24

            primary_basis = (
                "SAME_SENTENCE_SIMILARITY_EXPRESSION_VALIDATED"
            )

            if unique_two_side_grounding:
                evidence_score += 0.08

            if two_side_grounding_confidence is not None:
                evidence_score += (
                    two_side_grounding_confidence
                    * 0.08
                )

            if (
                structure_supported
                and orientation_supported
                and participant_a_supported
                and participant_b_supported
            ):
                evidence_score += 0.04

            if adjacent_support_present:
                evidence_score += 0.03

            evidence_score = min(
                evidence_score,
                0.95,
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
            "similarity_evidence_assessed":
                True,

            "similarity_evidence_score":
                evidence_score,

            "similarity_evidence_strength":
                evidence_strength,

            "similarity_evidence_basis":
                primary_basis,

            "similarity_evidence_factors": {
                "final_similarity_expression_validated":
                    final_validated,

                "same_sentence_similarity_valid":
                    same_sentence_valid,

                "cross_sentence_similarity_valid":
                    cross_sentence_valid,

                "article_asserted_candidate_confirmed":
                    article_asserted_confirmed,

                "same_sentence_candidate_confirmed":
                    same_sentence_candidate_confirmed,

                "exact_similarity_signal_supported":
                    exact_signal_supported,

                "comparison_structure_supported":
                    structure_supported,

                "similarity_difference_orientation_supported":
                    orientation_supported,

                "participant_a_supported":
                    participant_a_supported,

                "participant_b_supported":
                    participant_b_supported,

                "unique_two_side_grounding_supported":
                    unique_two_side_grounding,

                "participant_a_side_grounding_match_count":
                    participant_a_count,

                "participant_b_side_grounding_match_count":
                    participant_b_count,

                "cross_side_grounding_overlap_count":
                    overlap_count,

                "two_side_grounding_confidence":
                    two_side_grounding_confidence,

                "adjacent_similarity_support_present":
                    adjacent_support_present,

                "shared_characteristic_valid":
                    (
                        candidate.get(
                            "shared_characteristic_valid"
                        )
                        is True
                    ),

                "difference_contrast_valid":
                    (
                        candidate.get(
                            "difference_contrast_valid"
                        )
                        is True
                    ),

                "relation_class":
                    orientation_class,
            },

            "two_side_grounding_integrity_preserved":
                True,

            "similarity_orientation_preserved":
                True,

            "stage_j_difference_validation_preserved":
                (
                    orientation_class not in difference_classes
                    or (
                        candidate.get(
                            "difference_contrast_valid"
                        )
                        is True
                    )
                ),

            "general_comparison_not_promoted":
                (
                    orientation_class
                    not in general_comparison_classes
                    or (
                        candidate.get(
                            "difference_contrast_valid"
                        )
                        is not True
                    )
                ),

            "multiple_total_groundings_treated_as_ambiguity":
                False,

            "adjacent_corroboration_used_only_as_bonus":
                True,

            "confidence_scope":
                "ARTICLE_LOCAL_SIMILARITY_EXPRESSION_EVIDENCE_ONLY",

            "duplicate_resolution_performed":
                False,

            "embedding_similarity_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "unstated_shared_property_inference_performed":
                False,

            "unstated_difference_inference_performed":
                False,

            "analogical_reasoning_performed":
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
            "similarity_candidate_id"
        ):
            candidate
        for candidate in assessed_candidates
    }

    assessed_units = []
    assessed_units_by_id = {}

    for unit in (
        cross_sentence_result.get(
            "similarity_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every Similarity Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "similarity_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise SimilarityIntelligenceError(
                "Similarity Claim Unit ID is required."
            )

        if unit_id in assessed_units_by_id:
            raise SimilarityIntelligenceError(
                "Duplicate Similarity Claim Unit ID detected."
            )

        state = dict(
            unit.get(
                "similarity_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "cross_sentence_similarity_validation"
            )
            != "COMPLETE"
        ):
            raise SimilarityIntelligenceError(
                "Cross-sentence Similarity validation must "
                "be COMPLETE before Stage M."
            )

        if (
            state.get(
                "similarity_evidence_assessment"
            )
            != "PENDING"
        ):
            raise SimilarityIntelligenceError(
                "Similarity evidence assessment must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "cross_sentence_similarity_validation_performed"
            )
            is not True
        ):
            raise SimilarityIntelligenceError(
                "Stage-L cross-sentence Similarity validation "
                "boundary is incomplete."
            )

        if (
            boundaries.get(
                "similarity_evidence_assessment_performed"
            )
            is not False
        ):
            raise SimilarityIntelligenceError(
                "Similarity evidence assessment boundary "
                "must be False before Stage M."
            )

        required_false_boundaries = (
            "similarity_duplicate_resolution_performed",
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

        for boundary_name in required_false_boundaries:
            if (
                boundaries.get(
                    boundary_name
                )
                is not False
            ):
                raise SimilarityIntelligenceError(
                    boundary_name
                    + " must be False before Stage M."
                )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "similarity_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise SimilarityIntelligenceError(
                    "Every unit Similarity Candidate must be a mapping."
                )

            candidate_id = old_candidate.get(
                "similarity_candidate_id"
            )

            assessed_candidate = (
                assessed_by_id.get(
                    candidate_id
                )
            )

            if assessed_candidate is None:
                raise SimilarityIntelligenceError(
                    "Similarity candidate/unit evidence mismatch."
                )

            unit_candidates.append(
                assessed_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "similarity_evidence_assessment"
        ] = "COMPLETE"

        updated_boundaries = dict(
            boundaries
        )

        updated_boundaries[
            "similarity_evidence_assessment_performed"
        ] = True

        updated_boundaries[
            "similarity_duplicate_resolution_performed"
        ] = False

        updated_boundaries[
            "embedding_similarity_performed"
        ] = False

        updated_boundaries[
            "fuzzy_similarity_performed"
        ] = False

        updated_boundaries[
            "unstated_shared_property_inference_performed"
        ] = False

        updated_boundaries[
            "unstated_difference_inference_performed"
        ] = False

        updated_boundaries[
            "analogical_reasoning_performed"
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
            "similarity_candidates":
                unit_candidates,

            "strong_similarity_evidence_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "similarity_evidence_strength"
                    )
                    == "STRONG"
                ),

            "moderate_similarity_evidence_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "similarity_evidence_strength"
                    )
                    == "MODERATE"
                ),

            "limited_similarity_evidence_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "similarity_evidence_strength"
                    )
                    == "LIMITED"
                ),

            "insufficient_similarity_evidence_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "similarity_evidence_strength"
                    )
                    == "INSUFFICIENT"
                ),

            "similarity_analysis_state":
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
            "similarity_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every Similarity section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "similarity_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise SimilarityIntelligenceError(
                    "Every section Similarity Claim Unit "
                    "must be a mapping."
                )

            unit_id = old_unit.get(
                "similarity_claim_unit_id"
            )

            assessed_unit = (
                assessed_units_by_id.get(
                    unit_id
                )
            )

            if assessed_unit is None:
                raise SimilarityIntelligenceError(
                    "Similarity section/unit evidence mismatch."
                )

            section_units.append(
                assessed_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "similarity_candidates"
                )
                or []
            )
        ]

        assessed_sections.append({
            **dict(
                section
            ),

            "similarity_claim_units":
                section_units,

            "similarity_candidates":
                section_candidates,

            "strong_similarity_evidence_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "similarity_evidence_strength"
                    )
                    == "STRONG"
                ),

            "moderate_similarity_evidence_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "similarity_evidence_strength"
                    )
                    == "MODERATE"
                ),

            "limited_similarity_evidence_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "similarity_evidence_strength"
                    )
                    == "LIMITED"
                ),

            "insufficient_similarity_evidence_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "similarity_evidence_strength"
                    )
                    == "INSUFFICIENT"
                ),

            "similarity_evidence_assessment_complete":
                True,
        })

    strong_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "similarity_evidence_strength"
        )
        == "STRONG"
    )

    moderate_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "similarity_evidence_strength"
        )
        == "MODERATE"
    )

    limited_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "similarity_evidence_strength"
        )
        == "LIMITED"
    )

    insufficient_count = sum(
        1
        for candidate in assessed_candidates
        if candidate.get(
            "similarity_evidence_strength"
        )
        == "INSUFFICIENT"
    )

    invalid_strong_count = sum(
        1
        for candidate in assessed_candidates
        if (
            candidate.get(
                "final_similarity_expression_validated"
            )
            is not True
            and candidate.get(
                "similarity_evidence_strength"
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
            "cross_sentence_similarity_validation_performed"
        )
        is not True
    ):
        raise SimilarityIntelligenceError(
            "Top-level Stage-L cross-sentence Similarity "
            "validation boundary is incomplete."
        )

    if (
        result_boundaries.get(
            "similarity_evidence_assessment_performed"
        )
        is not False
    ):
        raise SimilarityIntelligenceError(
            "Top-level Similarity evidence assessment "
            "must not already be performed."
        )

    result_boundaries[
        "similarity_evidence_assessment_performed"
    ] = True

    result_boundaries[
        "similarity_duplicate_resolution_performed"
    ] = False

    result_boundaries[
        "embedding_similarity_performed"
    ] = False

    result_boundaries[
        "fuzzy_similarity_performed"
    ] = False

    result_boundaries[
        "unstated_shared_property_inference_performed"
    ] = False

    result_boundaries[
        "unstated_difference_inference_performed"
    ] = False

    result_boundaries[
        "analogical_reasoning_performed"
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
            "similarity_evidence_assessment_v1",

        "patch":
            "4.6.12M",

        "status":
            "SIMILARITY_EVIDENCE_ASSESSMENT_COMPLETE",

        "similarity_sections":
            assessed_sections,

        "similarity_claim_units":
            assessed_units,

        "similarity_candidates":
            assessed_candidates,

        "similarity_evidence_summary": {
            "candidate_count":
                len(
                    assessed_candidates
                ),

            "strong_similarity_evidence_count":
                strong_count,

            "moderate_similarity_evidence_count":
                moderate_count,

            "limited_similarity_evidence_count":
                limited_count,

            "insufficient_similarity_evidence_count":
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

            "invalid_expression_strong_promotion_prohibited":
                True,

            "two_side_grounding_model":
                "ONE_UNIQUE_PARTICIPANT_A_PLUS_ONE_UNIQUE_PARTICIPANT_B_ZERO_OVERLAP",

            "two_total_groundings_treated_as_ambiguity":
                False,

            "grounding_confidence_source":
                "STAGE_G_ARTICLE_LOCAL_EXTRACTION_CONFIDENCE",

            "same_sentence_validation_authoritative":
                True,

            "adjacent_support_is_corroboration_only":
                True,

            "confidence_scope":
                "ARTICLE_LOCAL_SIMILARITY_EXPRESSION_EVIDENCE_ONLY",

            "scientific_truth_confidence_computed":
                False,

            "real_world_similarity_validity_verified":
                False,

            "shared_property_inference_performed":
                False,

            "difference_inference_performed":
                False,

            "duplicate_resolution_performed":
                False,

            "embedding_similarity_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "analogical_reasoning_performed":
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
            "duplicate_redundant_similarity_resolution",
    })

    return result


def resolve_duplicate_redundant_similarity_relations_v1(
    evidence_assessment_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Resolve exact article-local duplicate/redundant Similarity relations.

    Duplicate identity is deliberately conservative. Two candidates are
    groupable only when they have:
    - the same certified Similarity relation class,
    - the same exact Participant-A grounding identity,
    - the same exact Participant-B grounding identity,
    - the same validated shared-characteristic text, when present,
    - the same validated difference-dimension text, when present.

    Participant ordering is preserved as article-local evidence identity.
    Reversed A/B expressions are not automatically treated as duplicates.

    This stage does NOT:
    - use fuzzy or embedding similarity,
    - merge different relation classes,
    - merge different Participant-A identities,
    - merge different Participant-B identities,
    - merge different shared characteristics,
    - merge different difference dimensions,
    - infer symmetry,
    - infer unstated shared properties,
    - infer unstated differences,
    - rescue invalid relations,
    - create grounding or orientation,
    - perform Analogical Intelligence,
    - perform Procedural Intelligence,
    - perform Quantitative Intelligence,
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
        raise SimilarityIntelligenceError(
            "evidence_assessment_result must be a mapping."
        )

    if (
        evidence_assessment_result.get(
            "schema_version"
        )
        != "similarity_evidence_assessment_v1"
    ):
        raise SimilarityIntelligenceError(
            "Stage N requires similarity_evidence_assessment_v1."
        )

    if (
        evidence_assessment_result.get(
            "status"
        )
        != "SIMILARITY_EVIDENCE_ASSESSMENT_COMPLETE"
    ):
        raise SimilarityIntelligenceError(
            "Similarity evidence assessment must be complete."
        )

    if (
        evidence_assessment_result.get(
            "phase"
        )
        != "4.6.12"
    ):
        raise SimilarityIntelligenceError(
            "Stage N requires Phase 4.6.12 input."
        )

    if (
        evidence_assessment_result.get(
            "patch"
        )
        != "4.6.12M"
    ):
        raise SimilarityIntelligenceError(
            "Stage N requires canonical 4.6.12M input."
        )

    if (
        evidence_assessment_result.get(
            "next_stage"
        )
        != "duplicate_redundant_similarity_resolution"
    ):
        raise SimilarityIntelligenceError(
            "Stage M must hand off to "
            "duplicate_redundant_similarity_resolution."
        )

    if (
        evidence_assessment_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise SimilarityIntelligenceError(
            "Similarity Intelligence must remain transient."
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

    def participant_grounding_identity(
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
            raise SimilarityIntelligenceError(
                "Selected "
                + role
                + " requires grounding_ref."
            )

        if not canonical_text:
            raise SimilarityIntelligenceError(
                "Selected "
                + role
                + " requires canonical_text."
            )

        if semantic_kind not in {
            "entity",
            "concept",
        }:
            raise SimilarityIntelligenceError(
                "Selected "
                + role
                + " has invalid semantic_kind."
            )

        return (
            semantic_kind,
            canonical_text,
            grounding_ref,
        )

    def relation_detail_identity(
        candidate: Mapping[str, Any],
        relation_class: str,
    ) -> tuple[str, str]:
        shared_text = ""
        difference_text = ""

        if (
            candidate.get(
                "shared_characteristic_valid"
            )
            is True
        ):
            shared_text = normalize_text(
                candidate.get(
                    "shared_characteristic_text"
                )
            )

            if not shared_text:
                raise SimilarityIntelligenceError(
                    "Validated shared characteristic requires "
                    "shared_characteristic_text."
                )

        if (
            candidate.get(
                "difference_contrast_valid"
            )
            is True
            and candidate.get(
                "explicit_difference_dimension_found"
            )
            is True
        ):
            difference_text = normalize_text(
                candidate.get(
                    "difference_dimension_text"
                )
            )

            if not difference_text:
                raise SimilarityIntelligenceError(
                    "Explicit difference dimension requires "
                    "difference_dimension_text."
                )

        if relation_class in {
            "DIFFERENCE",
            "CONTRAST",
        }:
            if (
                candidate.get(
                    "difference_contrast_valid"
                )
                is not True
            ):
                raise SimilarityIntelligenceError(
                    "Validated DIFFERENCE / CONTRAST relation "
                    "must retain Stage-J validation."
                )

            shared_text = ""

        elif relation_class == "GENERAL_COMPARISON":
            if (
                candidate.get(
                    "difference_contrast_valid"
                )
                is True
            ):
                raise SimilarityIntelligenceError(
                    "GENERAL_COMPARISON must not be promoted "
                    "to difference/contrast."
                )

            shared_text = ""
            difference_text = ""

        elif relation_class in {
            "SIMILARITY",
            "RESEMBLANCE",
            "COMPARABILITY",
            "EQUIVALENCE_COMPARISON",
        }:
            difference_text = ""

        else:
            raise SimilarityIntelligenceError(
                "Unsupported Similarity relation class."
            )

        return (
            shared_text,
            difference_text,
        )

    def duplicate_key(
        candidate: Mapping[str, Any],
    ) -> tuple[str, ...] | None:
        if (
            candidate.get(
                "final_similarity_expression_validated"
            )
            is not True
        ):
            return None

        if (
            candidate.get(
                "similarity_evidence_assessed"
            )
            is not True
        ):
            return None

        if (
            candidate.get(
                "same_sentence_similarity_valid"
            )
            is not True
        ):
            return None

        if (
            candidate.get(
                "same_sentence_orientation_supported"
            )
            is not True
        ):
            return None

        if (
            candidate.get(
                "same_sentence_participant_a_supported"
            )
            is not True
            or candidate.get(
                "same_sentence_participant_b_supported"
            )
            is not True
        ):
            return None

        if (
            candidate.get(
                "same_sentence_unique_two_side_grounding_supported"
            )
            is not True
        ):
            return None

        participant_a_count = candidate.get(
            "participant_a_side_grounding_match_count"
        )

        participant_b_count = candidate.get(
            "participant_b_side_grounding_match_count"
        )

        overlap_count = candidate.get(
            "cross_side_grounding_overlap_count"
        )

        for name, value in (
            (
                "participant_a_side_grounding_match_count",
                participant_a_count,
            ),
            (
                "participant_b_side_grounding_match_count",
                participant_b_count,
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
                raise SimilarityIntelligenceError(
                    name
                    + " must be a non-negative integer."
                )

        if (
            participant_a_count != 1
            or participant_b_count != 1
            or overlap_count != 0
        ):
            return None

        participant_a_identity = (
            participant_grounding_identity(
                candidate.get(
                    "selected_participant_a"
                ),
                "Participant A",
            )
        )

        participant_b_identity = (
            participant_grounding_identity(
                candidate.get(
                    "selected_participant_b"
                ),
                "Participant B",
            )
        )

        if (
            participant_a_identity is None
            or participant_b_identity is None
        ):
            return None

        relation_class = str(
            candidate.get(
                "same_sentence_relation_class"
            )
            or candidate.get(
                "similarity_difference_orientation_class"
            )
            or ""
        ).strip().upper()

        if not relation_class:
            return None

        shared_text, difference_text = (
            relation_detail_identity(
                candidate,
                relation_class,
            )
        )

        return (
            relation_class,

            "participant_a",
            participant_a_identity[0],
            participant_a_identity[1],
            participant_a_identity[2],

            "participant_b",
            participant_b_identity[0],
            participant_b_identity[1],
            participant_b_identity[2],

            "shared_characteristic",
            shared_text,

            "difference_dimension",
            difference_text,
        )

    source_candidates = list(
        evidence_assessment_result.get(
            "similarity_candidates"
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
            raise SimilarityIntelligenceError(
                "Every Similarity Candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "similarity_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise SimilarityIntelligenceError(
                "Similarity Candidate ID is required."
            )

        if candidate_id in seen_candidate_ids:
            raise SimilarityIntelligenceError(
                "Duplicate Similarity Candidate ID encountered."
            )

        seen_candidate_ids.add(
            candidate_id
        )

        if (
            candidate.get(
                "similarity_evidence_assessed"
            )
            is not True
        ):
            raise SimilarityIntelligenceError(
                "Every Similarity Candidate must have "
                "completed evidence assessment."
            )

        if (
            candidate.get(
                "duplicate_resolution_performed"
            )
            is not False
        ):
            raise SimilarityIntelligenceError(
                "Candidate must not already have duplicate resolution."
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
                            "similarity_evidence_strength"
                        )
                        or ""
                    ),
                    0,
                ),

                -float(
                    candidate.get(
                        "similarity_evidence_score"
                    )
                    or 0.0
                ),

                0
                if candidate.get(
                    "same_sentence_similarity_valid"
                )
                is True
                else 1,

                0
                if candidate.get(
                    "adjacent_similarity_support_present"
                )
                is True
                else 1,

                str(
                    candidate.get(
                        "similarity_candidate_id"
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
                    "similarity_candidate_id"
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
            "similarity_duplicate_group_"
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
                "similarity_candidate_id"
            )
        )

        for index, member in enumerate(
            ordered
        ):
            member_id = str(
                member.get(
                    "similarity_candidate_id"
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

                "similarity_duplicate_group_id":
                    group_id,

                "similarity_duplicate_group_size":
                    len(
                        ordered
                    ),

                "similarity_duplicate_member_ids":
                    member_ids,

                "is_similarity_duplicate_group":
                    is_duplicate_group,

                "is_representative_similarity_expression":
                    is_representative,

                "representative_similarity_candidate_id":
                    representative_id,

                "duplicate_of_similarity_candidate_id":
                    (
                        None
                        if is_representative
                        else representative_id
                    ),

                "similarity_duplicate_resolution_status":
                    (
                        "REPRESENTATIVE"
                        if is_representative
                        else "DUPLICATE_REDUNDANT"
                    ),

                "similarity_duplicate_key": {
                    "relation_class":
                        key[0],

                    "participant_a_semantic_kind":
                        key[2],

                    "participant_a_canonical_text":
                        key[3],

                    "participant_a_grounding_ref":
                        key[4],

                    "participant_b_semantic_kind":
                        key[6],

                    "participant_b_canonical_text":
                        key[7],

                    "participant_b_grounding_ref":
                        key[8],

                    "shared_characteristic_text":
                        key[10],

                    "difference_dimension_text":
                        key[12],
                },

                "exact_similarity_relation_identity_used":
                    True,

                "participant_order_preserved":
                    True,

                "different_relation_classes_merged":
                    False,

                "different_participant_a_merged":
                    False,

                "different_participant_b_merged":
                    False,

                "different_shared_characteristics_merged":
                    False,

                "different_difference_dimensions_merged":
                    False,

                "symmetry_inference_performed":
                    False,

                "embedding_similarity_performed":
                    False,

                "fuzzy_similarity_performed":
                    False,

                "unstated_shared_property_inference_performed":
                    False,

                "unstated_difference_inference_performed":
                    False,

                "analogical_reasoning_performed":
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
                "similarity_candidate_id"
            )
        )

        resolved = dict(
            member
        )

        resolved.update({
            "duplicate_resolution_performed":
                True,

            "similarity_duplicate_group_id":
                None,

            "similarity_duplicate_group_size":
                1,

            "similarity_duplicate_member_ids": [
                member_id,
            ],

            "is_similarity_duplicate_group":
                False,

            "is_representative_similarity_expression":
                True,

            "representative_similarity_candidate_id":
                member_id,

            "duplicate_of_similarity_candidate_id":
                None,

            "similarity_duplicate_resolution_status":
                "UNIQUE_NON_GROUPABLE",

            "similarity_duplicate_key":
                None,

            "exact_similarity_relation_identity_used":
                False,

            "participant_order_preserved":
                True,

            "different_relation_classes_merged":
                False,

            "different_participant_a_merged":
                False,

            "different_participant_b_merged":
                False,

            "different_shared_characteristics_merged":
                False,

            "different_difference_dimensions_merged":
                False,

            "symmetry_inference_performed":
                False,

            "embedding_similarity_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "unstated_shared_property_inference_performed":
                False,

            "unstated_difference_inference_performed":
                False,

            "analogical_reasoning_performed":
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
                "similarity_candidate_id"
            )
        )

        resolved = resolved_by_id.get(
            candidate_id
        )

        if resolved is None:
            raise SimilarityIntelligenceError(
                "Duplicate Similarity resolution lost a candidate."
            )

        resolved_candidates.append(
            resolved
        )

    representative_candidates.sort(
        key=lambda candidate: str(
            candidate.get(
                "similarity_candidate_id"
            )
            or ""
        )
    )

    resolved_units = []
    resolved_units_by_id = {}

    for unit in (
        evidence_assessment_result.get(
            "similarity_claim_units"
        )
        or []
    ):
        if not isinstance(
            unit,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every Similarity Claim Unit must be a mapping."
            )

        unit_id = str(
            unit.get(
                "similarity_claim_unit_id"
            )
            or ""
        )

        if not unit_id:
            raise SimilarityIntelligenceError(
                "Similarity Claim Unit ID is required."
            )

        if unit_id in resolved_units_by_id:
            raise SimilarityIntelligenceError(
                "Duplicate Similarity Claim Unit ID detected."
            )

        state = dict(
            unit.get(
                "similarity_analysis_state"
            )
            or {}
        )

        if (
            state.get(
                "similarity_evidence_assessment"
            )
            != "COMPLETE"
        ):
            raise SimilarityIntelligenceError(
                "Similarity evidence assessment must be "
                "COMPLETE before Stage N."
            )

        if (
            state.get(
                "duplicate_similarity_resolution"
            )
            != "PENDING"
        ):
            raise SimilarityIntelligenceError(
                "Duplicate Similarity resolution must be PENDING."
            )

        boundaries = dict(
            unit.get(
                "processing_boundaries"
            )
            or {}
        )

        if (
            boundaries.get(
                "similarity_evidence_assessment_performed"
            )
            is not True
        ):
            raise SimilarityIntelligenceError(
                "Stage-M Similarity evidence boundary must be complete."
            )

        if (
            boundaries.get(
                "similarity_duplicate_resolution_performed"
            )
            is not False
        ):
            raise SimilarityIntelligenceError(
                "Duplicate Similarity resolution boundary "
                "must be False before Stage N."
            )

        unit_candidates = []

        for old_candidate in (
            unit.get(
                "similarity_candidates"
            )
            or []
        ):
            if not isinstance(
                old_candidate,
                Mapping,
            ):
                raise SimilarityIntelligenceError(
                    "Every unit Similarity Candidate must be a mapping."
                )

            candidate_id = old_candidate.get(
                "similarity_candidate_id"
            )

            resolved_candidate = (
                resolved_by_id.get(
                    candidate_id
                )
            )

            if resolved_candidate is None:
                raise SimilarityIntelligenceError(
                    "Similarity candidate/unit duplicate mismatch."
                )

            unit_candidates.append(
                resolved_candidate
            )

        updated_state = dict(
            state
        )

        updated_state[
            "duplicate_similarity_resolution"
        ] = "COMPLETE"

        updated_boundaries = dict(
            boundaries
        )

        updated_boundaries[
            "similarity_duplicate_resolution_performed"
        ] = True

        updated_boundaries[
            "embedding_similarity_performed"
        ] = False

        updated_boundaries[
            "fuzzy_similarity_performed"
        ] = False

        updated_boundaries[
            "unstated_shared_property_inference_performed"
        ] = False

        updated_boundaries[
            "unstated_difference_inference_performed"
        ] = False

        updated_boundaries[
            "analogical_reasoning_performed"
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
            "similarity_candidates":
                unit_candidates,

            "representative_similarity_expression_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "is_representative_similarity_expression"
                    )
                    is True
                ),

            "duplicate_redundant_similarity_expression_count":
                sum(
                    1
                    for candidate in unit_candidates
                    if candidate.get(
                        "similarity_duplicate_resolution_status"
                    )
                    == "DUPLICATE_REDUNDANT"
                ),

            "similarity_analysis_state":
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
            "similarity_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every Similarity section must be a mapping."
            )

        section_units = []

        for old_unit in (
            section.get(
                "similarity_claim_units"
            )
            or []
        ):
            if not isinstance(
                old_unit,
                Mapping,
            ):
                raise SimilarityIntelligenceError(
                    "Every section Similarity Claim Unit "
                    "must be a mapping."
                )

            unit_id = old_unit.get(
                "similarity_claim_unit_id"
            )

            resolved_unit = (
                resolved_units_by_id.get(
                    unit_id
                )
            )

            if resolved_unit is None:
                raise SimilarityIntelligenceError(
                    "Similarity section/unit duplicate mismatch."
                )

            section_units.append(
                resolved_unit
            )

        section_candidates = [
            candidate
            for unit in section_units
            for candidate in (
                unit.get(
                    "similarity_candidates"
                )
                or []
            )
        ]

        resolved_sections.append({
            **dict(
                section
            ),

            "similarity_claim_units":
                section_units,

            "similarity_candidates":
                section_candidates,

            "representative_similarity_expression_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "is_representative_similarity_expression"
                    )
                    is True
                ),

            "duplicate_redundant_similarity_expression_count":
                sum(
                    1
                    for candidate in section_candidates
                    if candidate.get(
                        "similarity_duplicate_resolution_status"
                    )
                    == "DUPLICATE_REDUNDANT"
                ),

            "duplicate_similarity_resolution_complete":
                True,
        })

    representative_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "is_representative_similarity_expression"
        )
        is True
    )

    redundant_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "similarity_duplicate_resolution_status"
        )
        == "DUPLICATE_REDUNDANT"
    )

    non_groupable_count = sum(
        1
        for candidate in resolved_candidates
        if candidate.get(
            "similarity_duplicate_resolution_status"
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
            "similarity_evidence_assessment_performed"
        )
        is not True
    ):
        raise SimilarityIntelligenceError(
            "Top-level Stage-M Similarity evidence "
            "boundary must be complete."
        )

    if (
        result_boundaries.get(
            "similarity_duplicate_resolution_performed"
        )
        is not False
    ):
        raise SimilarityIntelligenceError(
            "Top-level duplicate Similarity resolution "
            "must not already be performed."
        )

    result_boundaries[
        "similarity_duplicate_resolution_performed"
    ] = True

    result_boundaries[
        "embedding_similarity_performed"
    ] = False

    result_boundaries[
        "fuzzy_similarity_performed"
    ] = False

    result_boundaries[
        "unstated_shared_property_inference_performed"
    ] = False

    result_boundaries[
        "unstated_difference_inference_performed"
    ] = False

    result_boundaries[
        "analogical_reasoning_performed"
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
            "similarity_duplicate_resolution_v1",

        "patch":
            "4.6.12N",

        "status":
            "SIMILARITY_DUPLICATE_RESOLUTION_COMPLETE",

        "similarity_sections":
            resolved_sections,

        "similarity_claim_units":
            resolved_units,

        "similarity_candidates":
            resolved_candidates,

        "representative_similarity_candidates":
            representative_candidates,

        "similarity_duplicate_resolution_summary": {
            "candidate_count":
                len(
                    resolved_candidates
                ),

            "representative_similarity_expression_count":
                representative_count,

            "duplicate_redundant_similarity_expression_count":
                redundant_count,

            "duplicate_group_count":
                duplicate_group_count,

            "duplicate_candidate_count":
                duplicate_candidate_count,

            "non_groupable_similarity_candidate_count":
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
                "relation_class",
                "participant_a_semantic_kind",
                "participant_a_canonical_text",
                "participant_a_grounding_ref",
                "participant_b_semantic_kind",
                "participant_b_canonical_text",
                "participant_b_grounding_ref",
                "shared_characteristic_text",
                "difference_dimension_text",
            ],

            "participant_order_is_identity":
                True,

            "relation_class_is_identity":
                True,

            "shared_characteristic_is_identity_when_present":
                True,

            "difference_dimension_is_identity_when_present":
                True,

            "different_relation_classes_merged":
                False,

            "different_participant_a_merged":
                False,

            "different_participant_b_merged":
                False,

            "different_shared_characteristics_merged":
                False,

            "different_difference_dimensions_merged":
                False,

            "symmetry_inference_performed":
                False,

            "strongest_evidence_representative_selected":
                True,

            "duplicate_provenance_preserved":
                True,

            "embedding_similarity_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "unstated_shared_property_inference_performed":
                False,

            "unstated_difference_inference_performed":
                False,

            "analogical_reasoning_performed":
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
            "article_similarity_consolidation",
    })

    return result


def consolidate_article_similarity_intelligence_v1(
    duplicate_resolution_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Consolidate completed article-local Similarity Intelligence into
    article-level and section-level summaries.

    Only representative Similarity expressions are included in the
    canonical consolidated relation set. Full candidate and duplicate
    provenance remains preserved in the complete source collection.

    This stage does NOT:
    - create new Similarity relations,
    - rescue invalid relations,
    - merge different relation identities,
    - infer participant symmetry,
    - create or repair grounding,
    - create or repair orientation,
    - infer shared characteristics,
    - infer difference dimensions,
    - strengthen evidence classifications,
    - perform embedding similarity,
    - perform fuzzy similarity,
    - perform Analogical Intelligence,
    - perform Procedural Intelligence,
    - perform Quantitative Intelligence,
    - perform temporal reasoning,
    - perform new causal reasoning,
    - establish factual/scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        duplicate_resolution_result,
        Mapping,
    ):
        raise SimilarityIntelligenceError(
            "duplicate_resolution_result must be a mapping."
        )

    if (
        duplicate_resolution_result.get(
            "schema_version"
        )
        != "similarity_duplicate_resolution_v1"
    ):
        raise SimilarityIntelligenceError(
            "Stage O requires similarity_duplicate_resolution_v1."
        )

    if (
        duplicate_resolution_result.get(
            "status"
        )
        != "SIMILARITY_DUPLICATE_RESOLUTION_COMPLETE"
    ):
        raise SimilarityIntelligenceError(
            "Duplicate Similarity resolution must be complete."
        )

    if (
        duplicate_resolution_result.get(
            "phase"
        )
        != "4.6.12"
    ):
        raise SimilarityIntelligenceError(
            "Stage O requires Phase 4.6.12 input."
        )

    if (
        duplicate_resolution_result.get(
            "patch"
        )
        != "4.6.12N"
    ):
        raise SimilarityIntelligenceError(
            "Stage O requires canonical 4.6.12N input."
        )

    if (
        duplicate_resolution_result.get(
            "next_stage"
        )
        != "article_similarity_consolidation"
    ):
        raise SimilarityIntelligenceError(
            "Stage N must hand off to article_similarity_consolidation."
        )

    if (
        duplicate_resolution_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise SimilarityIntelligenceError(
            "Similarity Intelligence must remain transient."
        )

    source_candidates = list(
        duplicate_resolution_result.get(
            "similarity_candidates"
        )
        or []
    )

    representative_candidates = list(
        duplicate_resolution_result.get(
            "representative_similarity_candidates"
        )
        or []
    )

    seen_source_ids = set()

    for candidate in source_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every Similarity Candidate must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "similarity_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise SimilarityIntelligenceError(
                "Similarity Candidate ID is required."
            )

        if candidate_id in seen_source_ids:
            raise SimilarityIntelligenceError(
                "Duplicate Similarity Candidate ID encountered."
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
            raise SimilarityIntelligenceError(
                "All Similarity candidates must complete "
                "duplicate resolution before Stage O."
            )

    representative_ids = []
    seen_representative_ids = set()

    for candidate in representative_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every representative Similarity expression "
                "must be a mapping."
            )

        if (
            candidate.get(
                "is_representative_similarity_expression"
            )
            is not True
        ):
            raise SimilarityIntelligenceError(
                "Representative Similarity list contains "
                "a non-representative candidate."
            )

        candidate_id = str(
            candidate.get(
                "similarity_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise SimilarityIntelligenceError(
                "Representative Similarity Candidate ID is required."
            )

        if candidate_id in seen_representative_ids:
            raise SimilarityIntelligenceError(
                "Duplicate representative Similarity Candidate ID encountered."
            )

        seen_representative_ids.add(
            candidate_id
        )

        representative_ids.append(
            candidate_id
        )

    source_candidate_by_id = {
        str(
            candidate.get(
                "similarity_candidate_id"
            )
            or ""
        ):
            candidate
        for candidate in source_candidates
    }

    expected_representative_ids = {
        candidate_id
        for candidate_id, candidate
        in source_candidate_by_id.items()
        if candidate.get(
            "is_representative_similarity_expression"
        )
        is True
    }

    if set(
        representative_ids
    ) != expected_representative_ids:
        raise SimilarityIntelligenceError(
            "Representative Similarity list does not match resolved candidates."
        )

    for representative in representative_candidates:
        candidate_id = str(
            representative.get(
                "similarity_candidate_id"
            )
            or ""
        )

        source_candidate = source_candidate_by_id.get(
            candidate_id
        )

        if source_candidate is None:
            raise SimilarityIntelligenceError(
                "Representative Similarity candidate has no canonical "
                "Stage-N source candidate."
            )

        if dict(
            representative
        ) != dict(
            source_candidate
        ):
            raise SimilarityIntelligenceError(
                "Representative Similarity candidate content diverges "
                "from canonical Stage-N source candidate."
            )

    relation_class_counts = {}

    evidence_strength_counts = {
        "STRONG": 0,
        "MODERATE": 0,
        "LIMITED": 0,
        "INSUFFICIENT": 0,
    }

    validated_count = 0
    unvalidated_count = 0
    same_sentence_validated_count = 0
    adjacent_support_count = 0
    uniquely_grounded_count = 0
    non_uniquely_grounded_count = 0
    shared_characteristic_count = 0
    difference_contrast_count = 0
    explicit_difference_dimension_count = 0
    general_comparison_count = 0

    consolidated_similarity_relations = []

    for candidate in representative_candidates:
        relation_class = str(
            candidate.get(
                "same_sentence_relation_class"
            )
            or candidate.get(
                "similarity_difference_orientation_class"
            )
            or "UNSPECIFIED"
        ).strip().upper()

        evidence_strength = str(
            candidate.get(
                "similarity_evidence_strength"
            )
            or "INSUFFICIENT"
        )

        if evidence_strength not in evidence_strength_counts:
            raise SimilarityIntelligenceError(
                "Representative candidate has invalid "
                "Similarity evidence strength."
            )

        final_validated = (
            candidate.get(
                "final_similarity_expression_validated"
            )
            is True
        )

        same_sentence_valid = (
            candidate.get(
                "same_sentence_similarity_valid"
            )
            is True
        )

        adjacent_support = (
            candidate.get(
                "adjacent_similarity_support_present"
            )
            is True
        )

        uniquely_grounded = (
            candidate.get(
                "same_sentence_unique_two_side_grounding_supported"
            )
            is True
            and candidate.get(
                "participant_a_side_grounding_match_count"
            )
            == 1
            and candidate.get(
                "participant_b_side_grounding_match_count"
            )
            == 1
            and candidate.get(
                "cross_side_grounding_overlap_count"
            )
            == 0
        )

        shared_characteristic_valid = (
            candidate.get(
                "shared_characteristic_valid"
            )
            is True
        )

        difference_contrast_valid = (
            candidate.get(
                "difference_contrast_valid"
            )
            is True
        )

        explicit_difference_dimension = (
            candidate.get(
                "explicit_difference_dimension_found"
            )
            is True
        )

        relation_class_counts[
            relation_class
        ] = (
            relation_class_counts.get(
                relation_class,
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

        if adjacent_support:
            adjacent_support_count += 1

        if uniquely_grounded:
            uniquely_grounded_count += 1
        else:
            non_uniquely_grounded_count += 1

        if shared_characteristic_valid:
            shared_characteristic_count += 1

        if difference_contrast_valid:
            difference_contrast_count += 1

        if explicit_difference_dimension:
            explicit_difference_dimension_count += 1

        if relation_class == "GENERAL_COMPARISON":
            general_comparison_count += 1

        consolidated_similarity_relations.append({
            "similarity_candidate_id":
                candidate.get(
                    "similarity_candidate_id"
                ),

            "relation_class":
                relation_class,

            "signal_type":
                candidate.get(
                    "signal_type"
                ),

            "selected_participant_a":
                candidate.get(
                    "selected_participant_a"
                ),

            "selected_participant_b":
                candidate.get(
                    "selected_participant_b"
                ),

            "participant_a_side_grounding_match_count":
                candidate.get(
                    "participant_a_side_grounding_match_count"
                ),

            "participant_b_side_grounding_match_count":
                candidate.get(
                    "participant_b_side_grounding_match_count"
                ),

            "cross_side_grounding_overlap_count":
                candidate.get(
                    "cross_side_grounding_overlap_count"
                ),

            "unique_two_side_grounding_supported":
                uniquely_grounded,

            "shared_characteristic_valid":
                shared_characteristic_valid,

            "shared_characteristic_text":
                (
                    candidate.get(
                        "shared_characteristic_text"
                    )
                    if shared_characteristic_valid
                    else None
                ),

            "shared_characteristic_extraction_pattern":
                (
                    candidate.get(
                        "shared_characteristic_extraction_pattern"
                    )
                    if shared_characteristic_valid
                    else None
                ),

            "difference_contrast_valid":
                difference_contrast_valid,

            "explicit_difference_dimension_found":
                explicit_difference_dimension,

            "difference_dimension_text":
                (
                    candidate.get(
                        "difference_dimension_text"
                    )
                    if explicit_difference_dimension
                    else None
                ),

            "difference_dimension_extraction_pattern":
                (
                    candidate.get(
                        "difference_dimension_extraction_pattern"
                    )
                    if explicit_difference_dimension
                    else None
                ),

            "final_similarity_expression_validated":
                final_validated,

            "same_sentence_similarity_valid":
                same_sentence_valid,

            "cross_sentence_similarity_valid":
                (
                    candidate.get(
                        "cross_sentence_similarity_valid"
                    )
                    is True
                ),

            "adjacent_similarity_support_present":
                adjacent_support,

            "similarity_evidence_score":
                candidate.get(
                    "similarity_evidence_score"
                ),

            "similarity_evidence_strength":
                evidence_strength,

            "similarity_evidence_basis":
                candidate.get(
                    "similarity_evidence_basis"
                ),

            "section_id":
                candidate.get(
                    "section_id"
                ),

            "sentence_id":
                candidate.get(
                    "sentence_id"
                ),

            "similarity_claim_unit_id":
                candidate.get(
                    "similarity_claim_unit_id"
                ),

            "source_text":
                candidate.get(
                    "source_text"
                ),

            "signal_span":
                candidate.get(
                    "signal_span"
                ),

            "similarity_duplicate_group_id":
                candidate.get(
                    "similarity_duplicate_group_id"
                ),

            "similarity_duplicate_group_size":
                candidate.get(
                    "similarity_duplicate_group_size"
                ),

            "similarity_duplicate_member_ids":
                candidate.get(
                    "similarity_duplicate_member_ids"
                ),

            "similarity_duplicate_resolution_status":
                candidate.get(
                    "similarity_duplicate_resolution_status"
                ),

            "similarity_duplicate_key":
                candidate.get(
                    "similarity_duplicate_key"
                ),

            "participant_order_preserved":
                (
                    candidate.get(
                        "participant_order_preserved"
                    )
                    is True
                ),

            "duplicate_provenance_preserved":
                True,

            "new_similarity_relation_inference_performed":
                False,

            "similarity_evidence_strengthening_performed":
                False,

            "symmetry_inference_performed":
                False,

            "embedding_similarity_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "unstated_shared_property_inference_performed":
                False,

            "unstated_difference_inference_performed":
                False,

            "analogical_reasoning_performed":
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

    consolidated_similarity_relations.sort(
        key=lambda relation: (
            str(
                relation.get(
                    "section_id"
                )
                or ""
            ),
            str(
                relation.get(
                    "relation_class"
                )
                or ""
            ),
            str(
                relation.get(
                    "signal_type"
                )
                or ""
            ),
            str(
                relation.get(
                    "similarity_candidate_id"
                )
                or ""
            ),
        )
    )

    consolidated_sections = []
    seen_section_ids = set()

    for section in (
        duplicate_resolution_result.get(
            "similarity_sections"
        )
        or []
    ):
        if not isinstance(
            section,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every Similarity section must be a mapping."
            )

        section_id = str(
            section.get(
                "section_id"
            )
            or ""
        )

        if not section_id:
            raise SimilarityIntelligenceError(
                "Similarity section ID is required."
            )

        if section_id in seen_section_ids:
            raise SimilarityIntelligenceError(
                "Duplicate Similarity section ID encountered."
            )

        seen_section_ids.add(
            section_id
        )

        section_relations = [
            relation
            for relation in consolidated_similarity_relations
            if str(
                relation.get(
                    "section_id"
                )
                or ""
            )
            == section_id
        ]

        section_relation_class_counts = {}

        section_strength_counts = {
            "STRONG": 0,
            "MODERATE": 0,
            "LIMITED": 0,
            "INSUFFICIENT": 0,
        }

        for relation in section_relations:
            relation_class = str(
                relation.get(
                    "relation_class"
                )
                or "UNSPECIFIED"
            )

            evidence_strength = str(
                relation.get(
                    "similarity_evidence_strength"
                )
                or "INSUFFICIENT"
            )

            if evidence_strength not in section_strength_counts:
                raise SimilarityIntelligenceError(
                    "Section representative has invalid "
                    "Similarity evidence strength."
                )

            section_relation_class_counts[
                relation_class
            ] = (
                section_relation_class_counts.get(
                    relation_class,
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

            "representative_similarity_relations":
                section_relations,

            "representative_similarity_relation_count":
                len(
                    section_relations
                ),

            "validated_similarity_relation_count":
                sum(
                    1
                    for relation in section_relations
                    if relation.get(
                        "final_similarity_expression_validated"
                    )
                    is True
                ),

            "unvalidated_similarity_relation_count":
                sum(
                    1
                    for relation in section_relations
                    if relation.get(
                        "final_similarity_expression_validated"
                    )
                    is False
                ),

            "same_sentence_validated_similarity_count":
                sum(
                    1
                    for relation in section_relations
                    if relation.get(
                        "same_sentence_similarity_valid"
                    )
                    is True
                ),

            "uniquely_grounded_similarity_count":
                sum(
                    1
                    for relation in section_relations
                    if relation.get(
                        "unique_two_side_grounding_supported"
                    )
                    is True
                ),

            "non_uniquely_grounded_similarity_count":
                sum(
                    1
                    for relation in section_relations
                    if relation.get(
                        "unique_two_side_grounding_supported"
                    )
                    is False
                ),

            "shared_characteristic_relation_count":
                sum(
                    1
                    for relation in section_relations
                    if relation.get(
                        "shared_characteristic_valid"
                    )
                    is True
                ),

            "difference_contrast_relation_count":
                sum(
                    1
                    for relation in section_relations
                    if relation.get(
                        "difference_contrast_valid"
                    )
                    is True
                ),

            "explicit_difference_dimension_count":
                sum(
                    1
                    for relation in section_relations
                    if relation.get(
                        "explicit_difference_dimension_found"
                    )
                    is True
                ),

            "adjacent_support_similarity_count":
                sum(
                    1
                    for relation in section_relations
                    if relation.get(
                        "adjacent_similarity_support_present"
                    )
                    is True
                ),

            "similarity_relation_class_counts":
                section_relation_class_counts,

            "similarity_evidence_strength_counts":
                section_strength_counts,

            "similarity_consolidation_complete":
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
            "similarity_duplicate_resolution_status"
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
            "similarity_duplicate_resolution_performed"
        )
        is not True
    ):
        raise SimilarityIntelligenceError(
            "Top-level Stage-N duplicate Similarity "
            "resolution boundary must be complete."
        )

    if (
        boundaries.get(
            "article_similarity_consolidation_performed"
        )
        is True
    ):
        raise SimilarityIntelligenceError(
            "Article Similarity consolidation "
            "must not already be performed."
        )

    boundaries[
        "article_similarity_consolidation_performed"
    ] = True

    boundaries[
        "new_similarity_relation_inference_performed"
    ] = False

    boundaries[
        "similarity_evidence_strengthening_performed"
    ] = False

    boundaries[
        "symmetry_inference_performed"
    ] = False

    boundaries[
        "embedding_similarity_performed"
    ] = False

    boundaries[
        "fuzzy_similarity_performed"
    ] = False

    boundaries[
        "unstated_shared_property_inference_performed"
    ] = False

    boundaries[
        "unstated_difference_inference_performed"
    ] = False

    boundaries[
        "analogical_reasoning_performed"
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
            "similarity_article_consolidation_v1",

        "patch":
            "4.6.12O",

        "status":
            "SIMILARITY_ARTICLE_CONSOLIDATION_COMPLETE",

        "consolidated_similarity_sections":
            consolidated_sections,

        "consolidated_similarity_relations":
            consolidated_similarity_relations,

        "article_similarity_summary": {
            "total_candidate_count":
                total_candidate_count,

            "representative_similarity_relation_count":
                representative_count,

            "duplicate_redundant_similarity_expression_count":
                redundant_count,

            "validated_similarity_relation_count":
                validated_count,

            "unvalidated_similarity_relation_count":
                unvalidated_count,

            "same_sentence_validated_similarity_count":
                same_sentence_validated_count,

            "uniquely_grounded_similarity_count":
                uniquely_grounded_count,

            "non_uniquely_grounded_similarity_count":
                non_uniquely_grounded_count,

            "shared_characteristic_relation_count":
                shared_characteristic_count,

            "difference_contrast_relation_count":
                difference_contrast_count,

            "explicit_difference_dimension_count":
                explicit_difference_dimension_count,

            "general_comparison_relation_count":
                general_comparison_count,

            "adjacent_support_similarity_count":
                adjacent_support_count,

            "similarity_relation_class_counts":
                relation_class_counts,

            "similarity_evidence_strength_counts":
                evidence_strength_counts,

            "representative_count_matches_consolidated":
                (
                    representative_count
                    == len(
                        consolidated_similarity_relations
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
                    uniquely_grounded_count
                    + non_uniquely_grounded_count
                    == representative_count
                ),

            "representatives_only_in_consolidated_set":
                True,

            "participant_order_preserved":
                True,

            "relation_classes_preserved":
                True,

            "shared_characteristics_preserved":
                True,

            "difference_dimensions_preserved":
                True,

            "evidence_strengths_preserved":
                True,

            "duplicate_provenance_preserved":
                True,

            "new_similarity_relation_inference_performed":
                False,

            "similarity_evidence_strengthening_performed":
                False,

            "symmetry_inference_performed":
                False,

            "embedding_similarity_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "unstated_shared_property_inference_performed":
                False,

            "unstated_difference_inference_performed":
                False,

            "analogical_reasoning_performed":
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

            "article_local_only":
                True,
        },

        "processing_boundaries":
            boundaries,

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "final_similarity_intelligence_result",
    })

    return result


def build_final_similarity_intelligence_result_v1(
    article_consolidation_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Build the final canonical Phase 4.6.12 Similarity Intelligence result.

    This stage packages completed article-local Similarity Intelligence
    without adding new interpretation.

    It does NOT:
    - certify the result,
    - create or infer Similarity relations,
    - rescue invalid relations,
    - create or repair participant grounding,
    - create or repair participant orientation,
    - infer shared characteristics,
    - infer difference dimensions,
    - infer participant symmetry,
    - strengthen Similarity evidence,
    - perform embedding similarity,
    - perform fuzzy similarity,
    - perform Analogical Intelligence,
    - perform Procedural Intelligence,
    - perform Quantitative Intelligence,
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
        raise SimilarityIntelligenceError(
            "article_consolidation_result must be a mapping."
        )

    if (
        article_consolidation_result.get(
            "schema_version"
        )
        != "similarity_article_consolidation_v1"
    ):
        raise SimilarityIntelligenceError(
            "Stage P requires similarity_article_consolidation_v1."
        )

    if (
        article_consolidation_result.get(
            "status"
        )
        != "SIMILARITY_ARTICLE_CONSOLIDATION_COMPLETE"
    ):
        raise SimilarityIntelligenceError(
            "Article Similarity consolidation must be complete."
        )

    if (
        article_consolidation_result.get(
            "phase"
        )
        != "4.6.12"
    ):
        raise SimilarityIntelligenceError(
            "Stage P requires Phase 4.6.12 input."
        )

    if (
        article_consolidation_result.get(
            "patch"
        )
        != "4.6.12O"
    ):
        raise SimilarityIntelligenceError(
            "Stage P requires canonical 4.6.12O input."
        )

    if (
        article_consolidation_result.get(
            "next_stage"
        )
        != "final_similarity_intelligence_result"
    ):
        raise SimilarityIntelligenceError(
            "Stage O must hand off to "
            "final_similarity_intelligence_result."
        )

    if (
        article_consolidation_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise SimilarityIntelligenceError(
            "Similarity Intelligence must remain transient."
        )

    consolidated_relations = list(
        article_consolidation_result.get(
            "consolidated_similarity_relations"
        )
        or []
    )

    consolidated_sections = list(
        article_consolidation_result.get(
            "consolidated_similarity_sections"
        )
        or []
    )

    full_candidates = list(
        article_consolidation_result.get(
            "similarity_candidates"
        )
        or []
    )

    representative_candidates = list(
        article_consolidation_result.get(
            "representative_similarity_candidates"
        )
        or []
    )

    summary = dict(
        article_consolidation_result.get(
            "article_similarity_summary"
        )
        or {}
    )

    required_true_summary_fields = (
        "representative_count_matches_consolidated",
        "candidate_accounting_valid",
        "validation_count_accounting_valid",
        "grounding_count_accounting_valid",
        "representatives_only_in_consolidated_set",
        "participant_order_preserved",
        "relation_classes_preserved",
        "shared_characteristics_preserved",
        "difference_dimensions_preserved",
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
            raise SimilarityIntelligenceError(
                field_name
                + " must be True before final "
                "Similarity Intelligence packaging."
            )

    required_false_summary_fields = (
        "new_similarity_relation_inference_performed",
        "similarity_evidence_strengthening_performed",
        "symmetry_inference_performed",
        "embedding_similarity_performed",
        "fuzzy_similarity_performed",
        "unstated_shared_property_inference_performed",
        "unstated_difference_inference_performed",
        "analogical_reasoning_performed",
        "procedural_reasoning_performed",
        "quantitative_reasoning_performed",
        "temporal_reasoning_performed",
        "new_causal_reasoning_performed",
        "scientific_truth_verified",
        "truth_assessment_performed",
        "external_authority_check_performed",
    )

    for field_name in required_false_summary_fields:
        if (
            summary.get(
                field_name
            )
            is not False
        ):
            raise SimilarityIntelligenceError(
                field_name
                + " must remain False before final "
                "Similarity Intelligence packaging."
            )

    consolidated_ids = set()

    for relation in consolidated_relations:
        if not isinstance(
            relation,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every consolidated Similarity relation "
                "must be a mapping."
            )

        candidate_id = str(
            relation.get(
                "similarity_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise SimilarityIntelligenceError(
                "Consolidated Similarity Candidate ID is required."
            )

        if candidate_id in consolidated_ids:
            raise SimilarityIntelligenceError(
                "Duplicate consolidated Similarity Candidate ID encountered."
            )

        consolidated_ids.add(
            candidate_id
        )

        required_false_relation_fields = (
            "new_similarity_relation_inference_performed",
            "similarity_evidence_strengthening_performed",
            "symmetry_inference_performed",
            "embedding_similarity_performed",
            "fuzzy_similarity_performed",
            "unstated_shared_property_inference_performed",
            "unstated_difference_inference_performed",
            "analogical_reasoning_performed",
            "procedural_reasoning_performed",
            "quantitative_reasoning_performed",
            "temporal_reasoning_performed",
            "new_causal_reasoning_performed",
            "truth_assessed",
            "external_authority_checked",
        )

        for field_name in required_false_relation_fields:
            if (
                relation.get(
                    field_name
                )
                is not False
            ):
                raise SimilarityIntelligenceError(
                    field_name
                    + " must remain False in final "
                    "Similarity Intelligence."
                )

        if (
            relation.get(
                "duplicate_provenance_preserved"
            )
            is not True
        ):
            raise SimilarityIntelligenceError(
                "Final Similarity Intelligence must preserve "
                "duplicate provenance."
            )

        if (
            relation.get(
                "participant_order_preserved"
            )
            is not True
        ):
            raise SimilarityIntelligenceError(
                "Final Similarity Intelligence must preserve "
                "Participant A/B ordering."
            )

    representative_ids = set()

    representative_by_id = {}

    for candidate in representative_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every representative Similarity candidate "
                "must be a mapping."
            )

        candidate_id = str(
            candidate.get(
                "similarity_candidate_id"
            )
            or ""
        )

        if not candidate_id:
            raise SimilarityIntelligenceError(
                "Representative Similarity Candidate ID is required."
            )

        if candidate_id in representative_ids:
            raise SimilarityIntelligenceError(
                "Duplicate representative Similarity Candidate ID encountered."
            )

        representative_ids.add(
            candidate_id
        )

        representative_by_id[
            candidate_id
        ] = candidate

    if representative_ids != consolidated_ids:
        raise SimilarityIntelligenceError(
            "Final consolidated Similarity set must match "
            "representative candidates exactly."
        )

    for relation in consolidated_relations:
        candidate_id = str(
            relation.get(
                "similarity_candidate_id"
            )
            or ""
        )

        representative = representative_by_id.get(
            candidate_id
        )

        if representative is None:
            raise SimilarityIntelligenceError(
                "Consolidated Similarity relation has no "
                "representative candidate."
            )

        relation_class = str(
            relation.get(
                "relation_class"
            )
            or ""
        ).strip().upper()

        representative_relation_class = str(
            representative.get(
                "same_sentence_relation_class"
            )
            or representative.get(
                "similarity_difference_orientation_class"
            )
            or ""
        ).strip().upper()

        if (
            relation_class
            != representative_relation_class
        ):
            raise SimilarityIntelligenceError(
                "Consolidated Similarity relation class diverges "
                "from representative candidate."
            )

        if (
            relation.get(
                "selected_participant_a"
            )
            != representative.get(
                "selected_participant_a"
            )
        ):
            raise SimilarityIntelligenceError(
                "Consolidated Participant A diverges from "
                "representative candidate."
            )

        if (
            relation.get(
                "selected_participant_b"
            )
            != representative.get(
                "selected_participant_b"
            )
        ):
            raise SimilarityIntelligenceError(
                "Consolidated Participant B diverges from "
                "representative candidate."
            )

        expected_shared_text = (
            representative.get(
                "shared_characteristic_text"
            )
            if representative.get(
                "shared_characteristic_valid"
            )
            is True
            else None
        )

        if (
            relation.get(
                "shared_characteristic_text"
            )
            != expected_shared_text
        ):
            raise SimilarityIntelligenceError(
                "Consolidated shared characteristic diverges "
                "from representative candidate."
            )

        expected_difference_text = (
            representative.get(
                "difference_dimension_text"
            )
            if representative.get(
                "explicit_difference_dimension_found"
            )
            is True
            else None
        )

        if (
            relation.get(
                "difference_dimension_text"
            )
            != expected_difference_text
        ):
            raise SimilarityIntelligenceError(
                "Consolidated difference dimension diverges "
                "from representative candidate."
            )

        if (
            relation.get(
                "similarity_evidence_score"
            )
            != representative.get(
                "similarity_evidence_score"
            )
        ):
            raise SimilarityIntelligenceError(
                "Consolidated Similarity evidence score diverges "
                "from representative candidate."
            )

        if (
            relation.get(
                "similarity_evidence_strength"
            )
            != representative.get(
                "similarity_evidence_strength"
            )
        ):
            raise SimilarityIntelligenceError(
                "Consolidated Similarity evidence strength diverges "
                "from representative candidate."
            )

        if (
            relation.get(
                "similarity_duplicate_group_id"
            )
            != representative.get(
                "similarity_duplicate_group_id"
            )
        ):
            raise SimilarityIntelligenceError(
                "Consolidated duplicate provenance diverges "
                "from representative candidate."
            )

    boundaries = dict(
        article_consolidation_result.get(
            "processing_boundaries"
        )
        or {}
    )

    required_false_boundaries = (
        "new_similarity_relation_inference_performed",
        "similarity_evidence_strengthening_performed",
        "symmetry_inference_performed",
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

    for boundary_name in required_false_boundaries:
        if (
            boundaries.get(
                boundary_name
            )
            is not False
        ):
            raise SimilarityIntelligenceError(
                boundary_name
                + " must remain False in final "
                "Similarity Intelligence."
            )

    if (
        boundaries.get(
            "article_similarity_consolidation_performed"
        )
        is not True
    ):
        raise SimilarityIntelligenceError(
            "Article Similarity consolidation boundary "
            "must be complete."
        )

    if (
        boundaries.get(
            "final_similarity_result_built"
        )
        is True
    ):
        raise SimilarityIntelligenceError(
            "Final Similarity result must not already be built."
        )

    final_boundaries = dict(
        boundaries
    )

    final_boundaries[
        "final_similarity_result_built"
    ] = True

    final_boundaries[
        "similarity_certification_performed"
    ] = False

    article_identity = dict(
        article_consolidation_result.get(
            "article_identity"
        )
        or {}
    )

    result = {
        "schema_version":
            "similarity_intelligence_result_v1",

        "similarity_intelligence_version":
            article_consolidation_result.get(
                "similarity_intelligence_version"
            )
            or "similarity_intelligence_v1",

        "phase":
            "4.6.12",

        "patch":
            "4.6.12P",

        "status":
            "SIMILARITY_INTELLIGENCE_RESULT_COMPLETE",

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

        "consolidated_similarity_relations":
            consolidated_relations,

        "consolidated_similarity_sections":
            consolidated_sections,

        "representative_similarity_candidates":
            representative_candidates,

        "similarity_candidates":
            full_candidates,

        "similarity_claim_units":
            list(
                article_consolidation_result.get(
                    "similarity_claim_units"
                )
                or []
            ),

        "article_similarity_summary":
            summary,

        "similarity_boundaries": {
            "article_local_only":
                True,

            "scientific_truth_verified":
                False,

            "truth_assessment_performed":
                False,

            "external_authority_checked":
                False,

            "new_similarity_relation_inference_performed":
                False,

            "similarity_evidence_strengthening_performed":
                False,

            "symmetry_inference_performed":
                False,

            "embedding_similarity_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "unstated_shared_property_inference_performed":
                False,

            "unstated_difference_inference_performed":
                False,

            "analogical_reasoning_performed":
                False,

            "procedural_reasoning_performed":
                False,

            "quantitative_reasoning_performed":
                False,

            "temporal_reasoning_performed":
                False,

            "new_causal_reasoning_performed":
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
                "4.6.12Q",
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "similarity_intelligence_certification",
    }

    return result


def certify_similarity_intelligence_v1(
    final_similarity_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Hard-certify the canonical Phase 4.6.12 Similarity Intelligence result.

    Certification verifies structural integrity, candidate accounting,
    representative integrity, participant grounding/order integrity,
    relation-class integrity, shared-characteristic integrity,
    difference-dimension integrity, evidence integrity, duplicate
    provenance, and reasoning boundaries.

    It does NOT:
    - create new Similarity relations,
    - rescue invalid relations,
    - repair Participant A/B grounding,
    - repair Participant A/B orientation,
    - infer participant symmetry,
    - infer shared characteristics,
    - infer difference dimensions,
    - strengthen evidence,
    - perform embedding similarity,
    - perform fuzzy similarity,
    - perform Analogical Intelligence,
    - perform Procedural Intelligence,
    - perform Quantitative Intelligence,
    - perform temporal reasoning,
    - perform new causal reasoning,
    - establish factual or scientific truth,
    - use external authority,
    - make linking decisions,
    - write Semantic Memory,
    - persist intelligence.
    """

    if not isinstance(
        final_similarity_result,
        Mapping,
    ):
        raise SimilarityIntelligenceError(
            "final_similarity_result must be a mapping."
        )

    if (
        final_similarity_result.get(
            "schema_version"
        )
        != "similarity_intelligence_result_v1"
    ):
        raise SimilarityIntelligenceError(
            "Stage Q requires similarity_intelligence_result_v1."
        )

    if (
        final_similarity_result.get(
            "status"
        )
        != "SIMILARITY_INTELLIGENCE_RESULT_COMPLETE"
    ):
        raise SimilarityIntelligenceError(
            "Final Similarity Intelligence result must be complete."
        )

    if (
        final_similarity_result.get(
            "phase"
        )
        != "4.6.12"
    ):
        raise SimilarityIntelligenceError(
            "Stage Q requires Phase 4.6.12 input."
        )

    if (
        final_similarity_result.get(
            "patch"
        )
        != "4.6.12P"
    ):
        raise SimilarityIntelligenceError(
            "Stage Q requires canonical 4.6.12P input."
        )

    if (
        final_similarity_result.get(
            "next_stage"
        )
        != "similarity_intelligence_certification"
    ):
        raise SimilarityIntelligenceError(
            "Stage P must hand off to "
            "similarity_intelligence_certification."
        )

    if (
        final_similarity_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise SimilarityIntelligenceError(
            "Similarity Intelligence must remain transient."
        )

    identity = dict(
        final_similarity_result.get(
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
            raise SimilarityIntelligenceError(
                "Required article identity field missing: "
                + field
            )

    consolidated_relations = list(
        final_similarity_result.get(
            "consolidated_similarity_relations"
        )
        or []
    )

    representative_candidates = list(
        final_similarity_result.get(
            "representative_similarity_candidates"
        )
        or []
    )

    full_candidates = list(
        final_similarity_result.get(
            "similarity_candidates"
        )
        or []
    )

    claim_units = list(
        final_similarity_result.get(
            "similarity_claim_units"
        )
        or []
    )

    consolidated_sections = list(
        final_similarity_result.get(
            "consolidated_similarity_sections"
        )
        or []
    )

    summary = dict(
        final_similarity_result.get(
            "article_similarity_summary"
        )
        or {}
    )

    required_true_summary_fields = (
        "representative_count_matches_consolidated",
        "candidate_accounting_valid",
        "validation_count_accounting_valid",
        "grounding_count_accounting_valid",
        "representatives_only_in_consolidated_set",
        "participant_order_preserved",
        "relation_classes_preserved",
        "shared_characteristics_preserved",
        "difference_dimensions_preserved",
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
            raise SimilarityIntelligenceError(
                field_name
                + " must be verified before "
                "Similarity Intelligence certification."
            )

    if (
        summary.get(
            "representative_similarity_relation_count"
        )
        != len(
            consolidated_relations
        )
    ):
        raise SimilarityIntelligenceError(
            "Consolidated Similarity relation count "
            "does not match summary."
        )

    if (
        len(
            representative_candidates
        )
        != len(
            consolidated_relations
        )
    ):
        raise SimilarityIntelligenceError(
            "Representative candidate count does not match "
            "consolidated Similarity relations."
        )

    if (
        summary.get(
            "total_candidate_count"
        )
        != len(
            full_candidates
        )
    ):
        raise SimilarityIntelligenceError(
            "Full Similarity candidate count does not match summary."
        )

    redundant_count = sum(
        1
        for candidate in full_candidates
        if isinstance(
            candidate,
            Mapping,
        )
        and candidate.get(
            "similarity_duplicate_resolution_status"
        )
        == "DUPLICATE_REDUNDANT"
    )

    if (
        summary.get(
            "duplicate_redundant_similarity_expression_count"
        )
        != redundant_count
    ):
        raise SimilarityIntelligenceError(
            "Redundant Similarity candidate count does not match summary."
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
        raise SimilarityIntelligenceError(
            "Similarity representative/redundant accounting is invalid."
        )

    consolidated_ids = []
    representative_ids = []
    full_candidate_ids = []

    for relation in consolidated_relations:
        if not isinstance(
            relation,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every consolidated Similarity relation "
                "must be a mapping."
            )

        consolidated_ids.append(
            str(
                relation.get(
                    "similarity_candidate_id"
                )
                or ""
            )
        )

    for candidate in representative_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every representative Similarity candidate "
                "must be a mapping."
            )

        representative_ids.append(
            str(
                candidate.get(
                    "similarity_candidate_id"
                )
                or ""
            )
        )

    for candidate in full_candidates:
        if not isinstance(
            candidate,
            Mapping,
        ):
            raise SimilarityIntelligenceError(
                "Every Similarity candidate must be a mapping."
            )

        full_candidate_ids.append(
            str(
                candidate.get(
                    "similarity_candidate_id"
                )
                or ""
            )
        )

    if any(
        not candidate_id
        for candidate_id in consolidated_ids
    ):
        raise SimilarityIntelligenceError(
            "Every consolidated Similarity relation "
            "requires a candidate ID."
        )

    if any(
        not candidate_id
        for candidate_id in representative_ids
    ):
        raise SimilarityIntelligenceError(
            "Every representative Similarity candidate "
            "requires a candidate ID."
        )

    if any(
        not candidate_id
        for candidate_id in full_candidate_ids
    ):
        raise SimilarityIntelligenceError(
            "Every Similarity candidate requires a candidate ID."
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
        raise SimilarityIntelligenceError(
            "Duplicate consolidated Similarity candidate IDs "
            "are not allowed."
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
        raise SimilarityIntelligenceError(
            "Duplicate representative Similarity candidate IDs "
            "are not allowed."
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
        raise SimilarityIntelligenceError(
            "Duplicate full Similarity candidate IDs "
            "are not allowed."
        )

    if (
        set(
            consolidated_ids
        )
        != set(
            representative_ids
        )
    ):
        raise SimilarityIntelligenceError(
            "Consolidated relations and representative "
            "Similarity candidates disagree."
        )

    if not set(
        representative_ids
    ).issubset(
        set(
            full_candidate_ids
        )
    ):
        raise SimilarityIntelligenceError(
            "Representative Similarity candidates must exist "
            "in the full candidate collection."
        )

    representative_by_id = {
        str(
            candidate.get(
                "similarity_candidate_id"
            )
            or ""
        ):
            candidate
        for candidate in representative_candidates
    }

    invalid_strong_count = 0
    non_unique_grounding_strong_count = 0
    general_comparison_strong_count = 0
    cross_sentence_strong_count = 0

    valid_evidence_strengths = {
        "STRONG",
        "MODERATE",
        "LIMITED",
        "INSUFFICIENT",
    }

    for relation in consolidated_relations:
        candidate_id = str(
            relation.get(
                "similarity_candidate_id"
            )
            or ""
        )

        representative = representative_by_id.get(
            candidate_id
        )

        if representative is None:
            raise SimilarityIntelligenceError(
                "Consolidated Similarity relation has no "
                "representative candidate."
            )

        if (
            relation.get(
                "participant_order_preserved"
            )
            is not True
        ):
            raise SimilarityIntelligenceError(
                "Every consolidated Similarity relation must preserve "
                "Participant A/B ordering."
            )

        if (
            relation.get(
                "duplicate_provenance_preserved"
            )
            is not True
        ):
            raise SimilarityIntelligenceError(
                "Every consolidated Similarity relation must preserve "
                "duplicate provenance."
            )

        required_false_relation_fields = (
            "new_similarity_relation_inference_performed",
            "similarity_evidence_strengthening_performed",
            "symmetry_inference_performed",
            "embedding_similarity_performed",
            "fuzzy_similarity_performed",
            "unstated_shared_property_inference_performed",
            "unstated_difference_inference_performed",
            "analogical_reasoning_performed",
            "procedural_reasoning_performed",
            "quantitative_reasoning_performed",
            "temporal_reasoning_performed",
            "new_causal_reasoning_performed",
            "truth_assessed",
            "external_authority_checked",
        )

        for field_name in required_false_relation_fields:
            if (
                relation.get(
                    field_name
                )
                is not False
            ):
                raise SimilarityIntelligenceError(
                    field_name
                    + " must remain False in certified "
                    "Similarity Intelligence."
                )

        relation_class = str(
            relation.get(
                "relation_class"
            )
            or ""
        ).strip().upper()

        representative_relation_class = str(
            representative.get(
                "same_sentence_relation_class"
            )
            or representative.get(
                "similarity_difference_orientation_class"
            )
            or ""
        ).strip().upper()

        if (
            relation_class
            != representative_relation_class
        ):
            raise SimilarityIntelligenceError(
                "Certified Similarity relation class diverges "
                "from representative candidate."
            )

        if (
            relation.get(
                "selected_participant_a"
            )
            != representative.get(
                "selected_participant_a"
            )
        ):
            raise SimilarityIntelligenceError(
                "Certified Participant A diverges "
                "from representative candidate."
            )

        if (
            relation.get(
                "selected_participant_b"
            )
            != representative.get(
                "selected_participant_b"
            )
        ):
            raise SimilarityIntelligenceError(
                "Certified Participant B diverges "
                "from representative candidate."
            )

        expected_shared_text = (
            representative.get(
                "shared_characteristic_text"
            )
            if representative.get(
                "shared_characteristic_valid"
            )
            is True
            else None
        )

        if (
            relation.get(
                "shared_characteristic_text"
            )
            != expected_shared_text
        ):
            raise SimilarityIntelligenceError(
                "Certified shared characteristic diverges "
                "from representative candidate."
            )

        expected_difference_text = (
            representative.get(
                "difference_dimension_text"
            )
            if representative.get(
                "explicit_difference_dimension_found"
            )
            is True
            else None
        )

        if (
            relation.get(
                "difference_dimension_text"
            )
            != expected_difference_text
        ):
            raise SimilarityIntelligenceError(
                "Certified difference dimension diverges "
                "from representative candidate."
            )

        if (
            relation.get(
                "similarity_evidence_score"
            )
            != representative.get(
                "similarity_evidence_score"
            )
        ):
            raise SimilarityIntelligenceError(
                "Certified Similarity evidence score diverges "
                "from representative candidate."
            )

        if (
            relation.get(
                "similarity_evidence_strength"
            )
            != representative.get(
                "similarity_evidence_strength"
            )
        ):
            raise SimilarityIntelligenceError(
                "Certified Similarity evidence strength diverges "
                "from representative candidate."
            )

        if (
            relation.get(
                "similarity_duplicate_group_id"
            )
            != representative.get(
                "similarity_duplicate_group_id"
            )
        ):
            raise SimilarityIntelligenceError(
                "Certified duplicate provenance diverges "
                "from representative candidate."
            )

        evidence_strength = str(
            relation.get(
                "similarity_evidence_strength"
            )
            or ""
        )

        if evidence_strength not in valid_evidence_strengths:
            raise SimilarityIntelligenceError(
                "Consolidated Similarity relation has invalid "
                "evidence strength."
            )

        final_validated = (
            relation.get(
                "final_similarity_expression_validated"
            )
            is True
        )

        uniquely_grounded = (
            relation.get(
                "unique_two_side_grounding_supported"
            )
            is True
        )

        cross_sentence_valid = (
            relation.get(
                "cross_sentence_similarity_valid"
            )
            is True
        )

        if (
            not final_validated
            and evidence_strength
            == "STRONG"
        ):
            invalid_strong_count += 1

        if (
            not uniquely_grounded
            and evidence_strength
            == "STRONG"
        ):
            non_unique_grounding_strong_count += 1

        if (
            relation_class
            == "GENERAL_COMPARISON"
            and evidence_strength
            == "STRONG"
        ):
            general_comparison_strong_count += 1

        if (
            cross_sentence_valid
            and evidence_strength
            == "STRONG"
        ):
            cross_sentence_strong_count += 1

    if invalid_strong_count != 0:
        raise SimilarityIntelligenceError(
            "Unvalidated Similarity relations must never certify "
            "with STRONG evidence."
        )

    if non_unique_grounding_strong_count != 0:
        raise SimilarityIntelligenceError(
            "Non-uniquely-grounded Similarity relations must never "
            "certify with STRONG evidence."
        )

    if general_comparison_strong_count != 0:
        raise SimilarityIntelligenceError(
            "GENERAL_COMPARISON relations must never certify "
            "with STRONG evidence."
        )

    if cross_sentence_strong_count != 0:
        raise SimilarityIntelligenceError(
            "Cross-sentence Similarity relations must never certify "
            "with STRONG evidence."
        )

    similarity_boundaries = dict(
        final_similarity_result.get(
            "similarity_boundaries"
        )
        or {}
    )

    if (
        similarity_boundaries.get(
            "article_local_only"
        )
        is not True
    ):
        raise SimilarityIntelligenceError(
            "Final Similarity Intelligence must remain article-local."
        )

    required_false_similarity_boundaries = (
        "scientific_truth_verified",
        "truth_assessment_performed",
        "external_authority_checked",
        "new_similarity_relation_inference_performed",
        "similarity_evidence_strengthening_performed",
        "symmetry_inference_performed",
        "embedding_similarity_performed",
        "fuzzy_similarity_performed",
        "unstated_shared_property_inference_performed",
        "unstated_difference_inference_performed",
        "analogical_reasoning_performed",
        "procedural_reasoning_performed",
        "quantitative_reasoning_performed",
        "temporal_reasoning_performed",
        "new_causal_reasoning_performed",
        "linking_decisions_performed",
        "semantic_memory_write_performed",
        "persistence_performed",
    )

    for boundary_name in required_false_similarity_boundaries:
        if (
            similarity_boundaries.get(
                boundary_name
            )
            is not False
        ):
            raise SimilarityIntelligenceError(
                boundary_name
                + " must remain False."
            )

    processing_boundaries = dict(
        final_similarity_result.get(
            "processing_boundaries"
        )
        or {}
    )

    if (
        processing_boundaries.get(
            "article_similarity_consolidation_performed"
        )
        is not True
    ):
        raise SimilarityIntelligenceError(
            "Article Similarity consolidation must be complete."
        )

    if (
        processing_boundaries.get(
            "final_similarity_result_built"
        )
        is not True
    ):
        raise SimilarityIntelligenceError(
            "Final Similarity Intelligence result "
            "must already be built."
        )

    if (
        processing_boundaries.get(
            "similarity_certification_performed"
        )
        is not False
    ):
        raise SimilarityIntelligenceError(
            "Input must not already be certified."
        )

    certification = dict(
        final_similarity_result.get(
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
        != "4.6.12Q"
    ):
        raise SimilarityIntelligenceError(
            "Stage-P certification state is invalid."
        )

    required_false_summary_fields = (
        "new_similarity_relation_inference_performed",
        "similarity_evidence_strengthening_performed",
        "symmetry_inference_performed",
        "embedding_similarity_performed",
        "fuzzy_similarity_performed",
        "unstated_shared_property_inference_performed",
        "unstated_difference_inference_performed",
        "analogical_reasoning_performed",
        "procedural_reasoning_performed",
        "quantitative_reasoning_performed",
        "temporal_reasoning_performed",
        "new_causal_reasoning_performed",
        "scientific_truth_verified",
        "truth_assessment_performed",
        "external_authority_check_performed",
    )

    for field_name in required_false_summary_fields:
        if (
            summary.get(
                field_name
            )
            is not False
        ):
            raise SimilarityIntelligenceError(
                field_name
                + " must remain False at certification."
            )

    certified_processing_boundaries = dict(
        processing_boundaries
    )

    certified_processing_boundaries[
        "similarity_certification_performed"
    ] = True

    certified_processing_boundaries[
        "similarity_intelligence_certified"
    ] = True

    result = dict(
        final_similarity_result
    )

    result.update({
        "schema_version":
            "certified_similarity_intelligence_result_v1",

        "patch":
            "4.6.12Q",

        "status":
            "SIMILARITY_INTELLIGENCE_CERTIFIED",

        "processing_boundaries":
            certified_processing_boundaries,

        "certification": {
            "performed":
                True,

            "certified":
                True,

            "certification_stage":
                "4.6.12Q",

            "certification_scope":
                "ARTICLE_LOCAL_SIMILARITY_INTELLIGENCE",

            "structural_integrity_verified":
                True,

            "candidate_accounting_verified":
                True,

            "representative_similarity_integrity_verified":
                True,

            "provenance_preserved":
                True,

            "participant_order_integrity_verified":
                True,

            "participant_grounding_integrity_verified":
                True,

            "relation_class_integrity_verified":
                True,

            "shared_characteristic_integrity_verified":
                True,

            "difference_dimension_integrity_verified":
                True,

            "evidence_strength_integrity_verified":
                True,

            "unvalidated_strength_cap_verified":
                True,

            "non_unique_grounding_strength_cap_verified":
                True,

            "general_comparison_strength_cap_verified":
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

            "new_similarity_relation_inference_performed":
                False,

            "similarity_evidence_strengthening_performed":
                False,

            "symmetry_inference_performed":
                False,

            "embedding_similarity_performed":
                False,

            "fuzzy_similarity_performed":
                False,

            "unstated_shared_property_inference_performed":
                False,

            "unstated_difference_inference_performed":
                False,

            "analogical_reasoning_performed":
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

        "similarity_certification_summary": {
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

            "representative_similarity_relation_count":
                len(
                    representative_candidates
                ),

            "consolidated_similarity_relation_count":
                len(
                    consolidated_relations
                ),

            "duplicate_redundant_similarity_expression_count":
                redundant_count,

            "validated_similarity_relation_count":
                summary.get(
                    "validated_similarity_relation_count"
                ),

            "unvalidated_similarity_relation_count":
                summary.get(
                    "unvalidated_similarity_relation_count"
                ),

            "same_sentence_validated_similarity_count":
                summary.get(
                    "same_sentence_validated_similarity_count"
                ),

            "uniquely_grounded_similarity_count":
                summary.get(
                    "uniquely_grounded_similarity_count"
                ),

            "non_uniquely_grounded_similarity_count":
                summary.get(
                    "non_uniquely_grounded_similarity_count"
                ),

            "shared_characteristic_relation_count":
                summary.get(
                    "shared_characteristic_relation_count"
                ),

            "difference_contrast_relation_count":
                summary.get(
                    "difference_contrast_relation_count"
                ),

            "explicit_difference_dimension_count":
                summary.get(
                    "explicit_difference_dimension_count"
                ),

            "general_comparison_relation_count":
                summary.get(
                    "general_comparison_relation_count"
                ),

            "invalid_strong_count":
                invalid_strong_count,

            "non_unique_grounding_strong_count":
                non_unique_grounding_strong_count,

            "general_comparison_strong_count":
                general_comparison_strong_count,

            "cross_sentence_strong_count":
                cross_sentence_strong_count,

            "participant_order_preserved":
                True,

            "participant_grounding_preserved":
                True,

            "relation_classes_preserved":
                True,

            "shared_characteristics_preserved":
                True,

            "difference_dimensions_preserved":
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
            "temporal_intelligence",
    })

    return result
