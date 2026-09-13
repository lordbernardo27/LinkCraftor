from __future__ import annotations

from typing import Any


ARTICLE_SEMANTIC_CONSOLIDATION_VERSION = (
    "article_semantic_consolidation_v1"
)

ARTICLE_SEMANTIC_CONSOLIDATION_PHASE = "4.6.16"


class ArticleSemanticConsolidationError(ValueError):
    """Raised when Article Semantic Consolidation contracts are violated."""


_UPSTREAM_SEMANTIC_PHASE_ORDER = (
    "4.6.1",
    "4.6.2",
    "4.6.3",
    "4.6.4",
    "4.6.5",
    "4.6.6",
    "4.6.7",
    "4.6.8",
    "4.6.9",
    "4.6.10",
    "4.6.11",
    "4.6.12",
    "4.6.13",
    "4.6.14",
    "4.6.15",
)


_FOUNDATIONAL_SEMANTIC_LAYERS = (
    "semantic_runtime_reader",
    "entity_concept_intelligence",
    "phrase_neighborhood_intelligence",
    "topic_intent_intelligence",
    "section_evidence_intelligence",
)


_STRUCTURED_REASONING_LAYERS = (
    "logical_intelligence",
    "relational_intelligence",
    "causal_intelligence",
    "quantitative_intelligence",
    "procedural_intelligence",
)


_CONTEXTUAL_COMPARATIVE_LAYERS = (
    "analogical_intelligence",
    "similarity_intelligence",
    "temporal_intelligence",
    "uncertainty_intelligence",
)


_HYBRID_INTELLIGENCE_LAYERS = (
    "symbolic_neural_hybrid_intelligence",
)


_ARTICLE_SEMANTIC_LAYER_PHASES = {
    "semantic_runtime_reader":
        "4.6.1",

    "entity_concept_intelligence":
        "4.6.2",

    "phrase_neighborhood_intelligence":
        "4.6.3",

    "topic_intent_intelligence":
        "4.6.4",

    "section_evidence_intelligence":
        "4.6.5",

    "logical_intelligence":
        "4.6.6",

    "relational_intelligence":
        "4.6.7",

    "causal_intelligence":
        "4.6.8",

    "quantitative_intelligence":
        "4.6.9",

    "procedural_intelligence":
        "4.6.10",

    "analogical_intelligence":
        "4.6.11",

    "similarity_intelligence":
        "4.6.12",

    "temporal_intelligence":
        "4.6.13",

    "uncertainty_intelligence":
        "4.6.14",

    "symbolic_neural_hybrid_intelligence":
        "4.6.15",
}


_ARTICLE_SEMANTIC_INPUT_AUTHORITY = {
    "semantic_runtime_reader":
        "CANONICAL_COMPLETE_RESULT",

    "entity_concept_intelligence":
        "CANONICAL_COMPLETE_RESULT",

    "phrase_neighborhood_intelligence":
        "CANONICAL_COMPLETE_RESULT",

    "topic_intent_intelligence":
        "CANONICAL_COMPLETE_RESULT",

    "section_evidence_intelligence":
        "CANONICAL_COMPLETE_RESULT",

    "logical_intelligence":
        "CERTIFIED_RESULT",

    "relational_intelligence":
        "CERTIFIED_RESULT",

    "causal_intelligence":
        "CERTIFIED_RESULT",

    "quantitative_intelligence":
        "CERTIFIED_RESULT",

    "procedural_intelligence":
        "CERTIFIED_RESULT",

    "analogical_intelligence":
        "CERTIFIED_RESULT",

    "similarity_intelligence":
        "CERTIFIED_RESULT",

    "temporal_intelligence":
        "CERTIFIED_RESULT",

    "uncertainty_intelligence":
        "CERTIFIED_RESULT",

    "symbolic_neural_hybrid_intelligence":
        "FINAL_FROZEN_RESULT_FROM_CERTIFIED_IMPLEMENTATION",
}


_ARTICLE_SEMANTIC_PRESERVATION_RULES = (
    "PRESERVE_ARTICLE_IDENTITY",
    "PRESERVE_CANONICAL_SOURCE_ORDER",
    "PRESERVE_UPSTREAM_MEANING",
    "PRESERVE_UPSTREAM_EVIDENCE",
    "PRESERVE_UPSTREAM_PROVENANCE",
    "PRESERVE_UPSTREAM_CONFIDENCE",
    "PRESERVE_UPSTREAM_UNCERTAINTY",
    "PRESERVE_UPSTREAM_CONFLICT_STATE",
    "PRESERVE_UPSTREAM_ABSTENTION_STATE",
    "PRESERVE_SYMBOLIC_CONSTRAINT_AUTHORITY",
    "PRESERVE_NEURAL_SEMANTIC_INTERPRETIVE_BOUNDARY",
    "PRESERVE_DUPLICATE_REDUNDANCY_LINEAGE",
    "PRESERVE_ARTICLE_LOCAL_BOUNDARY",
)


_ARTICLE_SEMANTIC_FORBIDDEN_OPERATIONS = (
    "NEW_REASONING",
    "NEW_FACT_INFERENCE",
    "NEW_RELATION_INFERENCE",
    "NEW_CAUSAL_INFERENCE",
    "NEW_QUANTITATIVE_CALCULATION",
    "NEW_PROCEDURAL_INFERENCE",
    "NEW_ANALOGICAL_INFERENCE",
    "NEW_SIMILARITY_INFERENCE",
    "NEW_TEMPORAL_INFERENCE",
    "NEW_UNCERTAINTY_INFERENCE",
    "UNCERTAINTY_STRENGTHENING",
    "CONFLICT_RE_RESOLUTION",
    "CONFIDENCE_RECALCULATION",
    "SEMANTIC_OVERRIDE_OF_SYMBOLIC_CONSTRAINTS",
    "CROSS_LAYER_FACT_SYNTHESIS",
    "FUZZY_SEMANTIC_DEDUPLICATION",
    "TRUTH_ASSESSMENT",
    "EXTERNAL_VALIDATION",
    "EXTERNAL_MODEL_CALL",
    "SEMANTIC_MEMORY_WRITE",
    "PERSISTENCE",
    "LINKING_DECISION",
)


def get_article_semantic_consolidation_architecture_v1(
) -> dict[str, Any]:
    """
    Return the canonical Phase 4.6.16 architecture definition.

    Phase 4.6.16 consolidates already-produced article-local
    Semantic Intelligence only.

    It does not perform new reasoning or alter the meaning,
    confidence, conflict, uncertainty, provenance, authority,
    or abstention state of any upstream result.
    """

    return {
        "schema_version":
            "article_semantic_consolidation_architecture_v1",

        "article_semantic_consolidation_version":
            ARTICLE_SEMANTIC_CONSOLIDATION_VERSION,

        "phase":
            ARTICLE_SEMANTIC_CONSOLIDATION_PHASE,

        "patch":
            "4.6.16C",

        "status":
            "ARTICLE_SEMANTIC_CONSOLIDATION_ARCHITECTURE_DEFINED",

        "purpose": (
            "Assemble and organize the already-produced "
            "article-local Semantic Intelligence from Phases "
            "4.6.1 through 4.6.15 into one canonical article "
            "semantic representation without performing new reasoning."
        ),

        "governing_rule": (
            "Article Semantic Consolidation assembles and organizes "
            "the already-produced article-local semantic intelligence "
            "from Phases 4.6.1-4.6.15 into one canonical article "
            "semantic representation, while preserving every upstream "
            "meaning, state, uncertainty, conflict, confidence, "
            "provenance, authority boundary, and abstention decision "
            "exactly as received."
        ),

        "upstream_phase_order":
            list(
                _UPSTREAM_SEMANTIC_PHASE_ORDER
            ),

        "layer_phase_registry":
            dict(
                _ARTICLE_SEMANTIC_LAYER_PHASES
            ),

        "input_authority_registry":
            dict(
                _ARTICLE_SEMANTIC_INPUT_AUTHORITY
            ),

        "input_groups": {
            "foundational_semantic_intelligence":
                list(
                    _FOUNDATIONAL_SEMANTIC_LAYERS
                ),

            "structured_reasoning_intelligence":
                list(
                    _STRUCTURED_REASONING_LAYERS
                ),

            "contextual_comparative_intelligence":
                list(
                    _CONTEXTUAL_COMPARATIVE_LAYERS
                ),

            "symbolic_neural_hybrid_intelligence":
                list(
                    _HYBRID_INTELLIGENCE_LAYERS
                ),
        },

        "input_group_counts": {
            "foundational_semantic_intelligence":
                len(
                    _FOUNDATIONAL_SEMANTIC_LAYERS
                ),

            "structured_reasoning_intelligence":
                len(
                    _STRUCTURED_REASONING_LAYERS
                ),

            "contextual_comparative_intelligence":
                len(
                    _CONTEXTUAL_COMPARATIVE_LAYERS
                ),

            "symbolic_neural_hybrid_intelligence":
                len(
                    _HYBRID_INTELLIGENCE_LAYERS
                ),

            "total_upstream_layers":
                len(
                    _ARTICLE_SEMANTIC_LAYER_PHASES
                ),
        },

        "preservation_rules":
            list(
                _ARTICLE_SEMANTIC_PRESERVATION_RULES
            ),

        "forbidden_operations":
            list(
                _ARTICLE_SEMANTIC_FORBIDDEN_OPERATIONS
            ),

        "consolidation_model": {
            "mode":
                "STRUCTURAL_PRESERVATION_AND_INDEXING",

            "cross_layer_reasoning":
                False,

            "cross_layer_fact_synthesis":
                False,

            "upstream_meaning_rewrite":
                False,

            "upstream_conflict_resolution":
                False,

            "upstream_confidence_recalculation":
                False,

            "semantic_deduplication":
                "EXACT_STRUCTURAL_ONLY_WHERE_EXPLICITLY_AUTHORIZED",

            "article_local_only":
                True,
        },

        "output_contract": {
            "output_type":
                "CANONICAL_ARTICLE_SEMANTIC_CONSOLIDATION",

            "contains":
                [
                    "article_identity",
                    "foundational_semantic_intelligence",
                    "structured_reasoning_intelligence",
                    "contextual_comparative_intelligence",
                    "symbolic_neural_hybrid_intelligence",
                    "cross_layer_provenance",
                    "cross_layer_state_indexes",
                    "conflict_uncertainty_abstention_state",
                    "processing_boundaries",
                ],

            "new_reasoning_allowed":
                False,

            "new_fact_inference_allowed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "article_semantic_consolidation_intake",
    }


# =====================================================================
# PATCH 4.6.16D ? Consolidation Intake
# =====================================================================

_ARTICLE_SEMANTIC_UPSTREAM_RESULT_CONTRACTS = {
    "semantic_runtime_reader": {
        "schema_version":
            "semantic_intelligence_runtime_reader_result_v1",
        "phase":
            "4.6.1",
        "patch":
            None,
        "status":
            "SEMANTIC_RUNTIME_READING_COMPLETE",
        "persistence_policy":
            None,
        "next_stage":
            "entity_and_concept_intelligence",
    },

    "entity_concept_intelligence": {
        "schema_version":
            "entity_concept_intelligence_result_v1",
        "phase":
            "4.6.2",
        "patch":
            None,
        "status":
            "ENTITY_CONCEPT_INTELLIGENCE_COMPLETE",
        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        "next_stage":
            "phrase_neighborhood_intelligence",
    },

    "phrase_neighborhood_intelligence": {
        "schema_version":
            "phrase_neighborhood_intelligence_result_v1",
        "phase":
            "4.6.3",
        "patch":
            None,
        "status":
            "PHRASE_NEIGHBORHOOD_INTELLIGENCE_COMPLETE",
        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        "next_stage":
            "topic_intent_intelligence",
    },

    "topic_intent_intelligence": {
        "schema_version":
            "topic_intent_intelligence_result_v1",
        "phase":
            "4.6.4",
        "patch":
            None,
        "status":
            "TOPIC_INTENT_INTELLIGENCE_COMPLETE",
        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        "next_stage":
            "section_evidence_intelligence",
    },

    "section_evidence_intelligence": {
        "schema_version":
            "section_evidence_intelligence_result_v1",
        "phase":
            "4.6.5",
        "patch":
            "4.6.5M",
        "status":
            "SECTION_EVIDENCE_RESULT_COMPLETE",
        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        "next_stage":
            "section_evidence_certification",
    },

    "logical_intelligence": {
        "schema_version":
            "certified_logical_intelligence_result_v1",
        "phase":
            "4.6.6",
        "patch":
            "4.6.6O",
        "status":
            "LOGICAL_INTELLIGENCE_CERTIFIED",
        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        "next_stage":
            "relational_intelligence",
    },

    "relational_intelligence": {
        "schema_version":
            "certified_relational_intelligence_result_v1",
        "phase":
            "4.6.7",
        "patch":
            "4.6.7O",
        "status":
            "RELATIONAL_INTELLIGENCE_CERTIFIED",
        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        "next_stage":
            "causal_intelligence",
    },

    "causal_intelligence": {
        "schema_version":
            "certified_causal_intelligence_result_v1",
        "phase":
            "4.6.8",
        "patch":
            "4.6.8O",
        "status":
            "CAUSAL_INTELLIGENCE_CERTIFIED",
        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        "next_stage":
            "quantitative_intelligence",
    },

    "quantitative_intelligence": {
        "schema_version":
            "certified_quantitative_intelligence_result_v1",
        "phase":
            "4.6.9",
        "patch":
            "4.6.9O",
        "status":
            "QUANTITATIVE_INTELLIGENCE_CERTIFIED",
        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        "next_stage":
            "procedural_intelligence",
    },

    "procedural_intelligence": {
        "schema_version":
            "certified_procedural_intelligence_result_v1",
        "phase":
            "4.6.10",
        "patch":
            "4.6.10O",
        "status":
            "PROCEDURAL_INTELLIGENCE_CERTIFIED",
        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        "next_stage":
            "analogical_intelligence",
    },

    "analogical_intelligence": {
        "schema_version":
            "certified_analogical_intelligence_result_v1",
        "phase":
            "4.6.11",
        "patch":
            "4.6.11O",
        "status":
            "ANALOGICAL_INTELLIGENCE_CERTIFIED",
        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        "next_stage":
            "similarity_intelligence",
    },

    "similarity_intelligence": {
        "schema_version":
            "certified_similarity_intelligence_result_v1",
        "phase":
            "4.6.12",
        "patch":
            "4.6.12Q",
        "status":
            "SIMILARITY_INTELLIGENCE_CERTIFIED",
        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        "next_stage":
            "temporal_intelligence",
    },

    "temporal_intelligence": {
        "schema_version":
            "temporal_intelligence_result_v1",
        "phase":
            "4.6.13",
        "patch":
            "4.6.13Q",
        "status":
            "TEMPORAL_INTELLIGENCE_CERTIFIED",
        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        "next_stage":
            "uncertainty_intelligence",
    },

    "uncertainty_intelligence": {
        "schema_version":
            "uncertainty_intelligence_result_v1",
        "phase":
            "4.6.14",
        "patch":
            "4.6.14P",
        "status":
            "UNCERTAINTY_INTELLIGENCE_CERTIFIED",
        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        "next_stage":
            "symbolic_neural_hybrid_intelligence",
    },

    "symbolic_neural_hybrid_intelligence": {
        "schema_version":
            "symbolic_neural_hybrid_intelligence_result_v1",
        "phase":
            "4.6.15",
        "patch":
            "4.6.15S",
        "status":
            "SYMBOLIC_NEURAL_HYBRID_INTELLIGENCE_RESULT_READY",
        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        "next_stage":
            "symbolic_neural_hybrid_certification",
    },
}


def validate_article_semantic_consolidation_intake_v1(
    upstream_semantic_results: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate the exact canonical upstream result bundle admitted into
    Phase 4.6.16 Article Semantic Consolidation.

    This stage validates contracts only.

    It does NOT:
    - normalize upstream intelligence,
    - align article identities,
    - merge evidence,
    - perform reasoning,
    - infer facts or relations,
    - resolve conflicts,
    - recalculate confidence,
    - strengthen uncertainty,
    - deduplicate semantic meaning,
    - call external models,
    - write Semantic Memory,
    - persist intelligence,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        upstream_semantic_results,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "upstream_semantic_results must be a mapping."
        )

    expected_layers = tuple(
        _ARTICLE_SEMANTIC_LAYER_PHASES.keys()
    )

    actual_layers = tuple(
        upstream_semantic_results.keys()
    )

    missing_layers = [
        layer_name
        for layer_name in expected_layers
        if layer_name not in upstream_semantic_results
    ]

    unexpected_layers = [
        layer_name
        for layer_name in actual_layers
        if layer_name not in _ARTICLE_SEMANTIC_LAYER_PHASES
    ]

    if missing_layers:
        raise ArticleSemanticConsolidationError(
            "Required upstream Semantic Intelligence layers are missing: "
            + ", ".join(
                missing_layers
            )
        )

    if unexpected_layers:
        raise ArticleSemanticConsolidationError(
            "Unexpected upstream Semantic Intelligence layers were supplied: "
            + ", ".join(
                unexpected_layers
            )
        )

    if len(
        actual_layers
    ) != len(
        expected_layers
    ):
        raise ArticleSemanticConsolidationError(
            "Article Semantic Consolidation requires exactly 15 "
            "upstream Semantic Intelligence results."
        )

    admitted_results = {}
    admission_records = []

    for layer_name in expected_layers:

        source_result = upstream_semantic_results[
            layer_name
        ]

        if not isinstance(
            source_result,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " result must be a mapping."
            )

        expected_contract = (
            _ARTICLE_SEMANTIC_UPSTREAM_RESULT_CONTRACTS[
                layer_name
            ]
        )

        for field_name in (
            "schema_version",
            "phase",
            "status",
            "next_stage",
        ):
            expected_value = expected_contract[
                field_name
            ]

            actual_value = source_result.get(
                field_name
            )

            if actual_value != expected_value:
                raise ArticleSemanticConsolidationError(
                    layer_name
                    + " has invalid "
                    + field_name
                    + ": expected "
                    + repr(
                        expected_value
                    )
                    + ", received "
                    + repr(
                        actual_value
                    )
                    + "."
                )

        expected_patch = expected_contract[
            "patch"
        ]

        if expected_patch is not None:

            if (
                source_result.get(
                    "patch"
                )
                != expected_patch
            ):
                raise ArticleSemanticConsolidationError(
                    layer_name
                    + " has invalid canonical patch."
                )

        expected_persistence = expected_contract[
            "persistence_policy"
        ]

        if expected_persistence is not None:

            if (
                source_result.get(
                    "persistence_policy"
                )
                != expected_persistence
            ):
                raise ArticleSemanticConsolidationError(
                    layer_name
                    + " violates the required article-local "
                    "transient persistence boundary."
                )

        admitted_results[
            layer_name
        ] = deepcopy(
            dict(
                source_result
            )
        )

        admission_records.append({
            "layer_name":
                layer_name,

            "phase":
                expected_contract[
                    "phase"
                ],

            "schema_version":
                expected_contract[
                    "schema_version"
                ],

            "patch":
                expected_patch,

            "status":
                expected_contract[
                    "status"
                ],

            "input_authority":
                _ARTICLE_SEMANTIC_INPUT_AUTHORITY[
                    layer_name
                ],

            "contract_validated":
                True,

            "article_identity_alignment_performed":
                False,

            "normalization_performed":
                False,

            "new_reasoning_performed":
                False,
        })

    hybrid_result = admitted_results[
        "symbolic_neural_hybrid_intelligence"
    ]

    final_hybrid = hybrid_result.get(
        "final_symbolic_neural_hybrid_intelligence"
    )

    if not isinstance(
        final_hybrid,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 final symbolic-neural hybrid article result "
            "is missing."
        )

    if (
        final_hybrid.get(
            "final_status"
        )
        != "SYMBOLIC_NEURAL_HYBRID_INTELLIGENCE_READY"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 final hybrid article state is not ready."
        )

    hybrid_boundaries = hybrid_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        hybrid_boundaries,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 processing boundaries are missing."
        )

    if (
        hybrid_boundaries.get(
            "final_symbolic_neural_hybrid_result_prepared"
        )
        is not True
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 final hybrid-result preparation boundary "
            "is incomplete."
        )

    required_false_hybrid_boundaries = (
        "semantic_override_allowed",
        "new_reasoning_performed",
        "cross_candidate_synthesis_performed",
        "evidence_rewrite_performed",
        "candidate_meaning_change_performed",
        "conflict_resolution_reperformed",
        "confidence_recalculation_performed",
        "duplicate_resolution_reperformed",
        "article_consolidation_reperformed",
        "new_hybrid_fact_inference_performed",
        "new_article_fact_inference_performed",
        "truth_assessment_performed",
        "external_validation_performed",
        "external_model_called",
        "semantic_memory_written",
        "linking_decisions_performed",
        "persistence_performed",
    )

    for boundary_name in required_false_hybrid_boundaries:

        if (
            hybrid_boundaries.get(
                boundary_name
            )
            is not False
        ):
            raise ArticleSemanticConsolidationError(
                "4.6.15 certified boundary violation: "
                + boundary_name
                + " must remain False."
            )

    return {
        "schema_version":
            "article_semantic_consolidation_intake_v1",

        "article_semantic_consolidation_version":
            ARTICLE_SEMANTIC_CONSOLIDATION_VERSION,

        "phase":
            ARTICLE_SEMANTIC_CONSOLIDATION_PHASE,

        "patch":
            "4.6.16D",

        "status":
            "ARTICLE_SEMANTIC_CONSOLIDATION_INTAKE_VALIDATED",

        "admitted_layer_order":
            list(
                expected_layers
            ),

        "admitted_layer_count":
            len(
                expected_layers
            ),

        "upstream_semantic_results":
            admitted_results,

        "upstream_admission_records":
            admission_records,

        "input_groups": {
            "foundational_semantic_intelligence":
                list(
                    _FOUNDATIONAL_SEMANTIC_LAYERS
                ),

            "structured_reasoning_intelligence":
                list(
                    _STRUCTURED_REASONING_LAYERS
                ),

            "contextual_comparative_intelligence":
                list(
                    _CONTEXTUAL_COMPARATIVE_LAYERS
                ),

            "symbolic_neural_hybrid_intelligence":
                list(
                    _HYBRID_INTELLIGENCE_LAYERS
                ),
        },

        "processing_boundaries": {
            "intake_validation_performed":
                True,

            "all_15_upstream_contracts_admitted":
                True,

            "exact_layer_set_enforced":
                True,

            "hybrid_final_boundary_validated":
                True,

            "upstream_normalization_performed":
                False,

            "foundational_assembly_performed":
                False,

            "structured_reasoning_assembly_performed":
                False,

            "contextual_comparative_assembly_performed":
                False,

            "hybrid_integration_performed":
                False,

            "article_identity_alignment_performed":
                False,

            "cross_layer_provenance_alignment_performed":
                False,

            "cross_layer_state_index_construction_performed":
                False,

            "conflict_uncertainty_abstention_preservation_performed":
                False,

            "article_semantic_consolidation_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "cross_layer_fact_synthesis_performed":
                False,

            "conflict_resolution_performed":
                False,

            "confidence_recalculation_performed":
                False,

            "uncertainty_strengthening_performed":
                False,

            "fuzzy_semantic_deduplication_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_validation_performed":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "upstream_intelligence_normalization",
    }


# =====================================================================
# PATCH 4.6.16E ? Upstream Intelligence Normalization
# =====================================================================

def normalize_article_semantic_upstream_intelligence_v1(
    intake_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Normalize the validated 4.6.16D upstream Semantic Intelligence
    bundle into deterministic per-layer envelopes.

    Normalization standardizes contract metadata and grouping only.

    It does NOT:
    - alter or rewrite source payloads,
    - align article identities,
    - infer a canonical identity,
    - assemble semantic evidence,
    - merge cross-layer facts,
    - perform reasoning,
    - resolve conflicts,
    - recalculate confidence,
    - strengthen uncertainty,
    - perform fuzzy semantic deduplication,
    - call external models,
    - write Semantic Memory,
    - persist intelligence,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        intake_result,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "intake_result must be a mapping."
        )

    if (
        intake_result.get(
            "schema_version"
        )
        != "article_semantic_consolidation_intake_v1"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16E requires "
            "article_semantic_consolidation_intake_v1."
        )

    if (
        intake_result.get(
            "phase"
        )
        != "4.6.16"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16E requires Phase 4.6.16 input."
        )

    if (
        intake_result.get(
            "patch"
        )
        != "4.6.16D"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16E requires canonical 4.6.16D input."
        )

    if (
        intake_result.get(
            "status"
        )
        != "ARTICLE_SEMANTIC_CONSOLIDATION_INTAKE_VALIDATED"
    ):
        raise ArticleSemanticConsolidationError(
            "Article Semantic Consolidation intake is not validated."
        )

    if (
        intake_result.get(
            "next_stage"
        )
        != "upstream_intelligence_normalization"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16D does not hand off to upstream normalization."
        )

    if (
        intake_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16 intake must remain article-local and transient."
        )

    boundaries = intake_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16D processing boundaries are missing."
        )

    if (
        boundaries.get(
            "intake_validation_performed"
        )
        is not True
        or boundaries.get(
            "all_15_upstream_contracts_admitted"
        )
        is not True
        or boundaries.get(
            "exact_layer_set_enforced"
        )
        is not True
        or boundaries.get(
            "hybrid_final_boundary_validated"
        )
        is not True
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16D admission boundaries are incomplete."
        )

    if (
        boundaries.get(
            "upstream_normalization_performed"
        )
        is not False
    ):
        raise ArticleSemanticConsolidationError(
            "Upstream normalization was already performed."
        )

    admitted_order = intake_result.get(
        "admitted_layer_order"
    )

    admitted_results = intake_result.get(
        "upstream_semantic_results"
    )

    admission_records = intake_result.get(
        "upstream_admission_records"
    )

    if not isinstance(
        admitted_order,
        list,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16D admitted layer order is invalid."
        )

    if not isinstance(
        admitted_results,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16D admitted upstream result map is invalid."
        )

    if not isinstance(
        admission_records,
        list,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16D upstream admission records are invalid."
        )

    expected_order = list(
        _ARTICLE_SEMANTIC_LAYER_PHASES.keys()
    )

    if admitted_order != expected_order:
        raise ArticleSemanticConsolidationError(
            "4.6.16D admitted layer order is not canonical."
        )

    if (
        intake_result.get(
            "admitted_layer_count"
        )
        != len(
            expected_order
        )
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16D admitted layer count is invalid."
        )

    if len(
        admitted_results
    ) != len(
        expected_order
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16D admitted result count is invalid."
        )

    if len(
        admission_records
    ) != len(
        expected_order
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16D admission record count is invalid."
        )

    admission_record_by_layer = {}

    for record in admission_records:

        if not isinstance(
            record,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                "Every upstream admission record must be a mapping."
            )

        layer_name = record.get(
            "layer_name"
        )

        if (
            layer_name
            not in _ARTICLE_SEMANTIC_LAYER_PHASES
        ):
            raise ArticleSemanticConsolidationError(
                "Admission record contains an unknown layer."
            )

        if layer_name in admission_record_by_layer:
            raise ArticleSemanticConsolidationError(
                "Duplicate upstream admission record detected."
            )

        if (
            record.get(
                "contract_validated"
            )
            is not True
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " was not contract-validated at intake."
            )

        if (
            record.get(
                "normalization_performed"
            )
            is not False
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " was already normalized before 4.6.16E."
            )

        if (
            record.get(
                "new_reasoning_performed"
            )
            is not False
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " intake record violates the no-reasoning boundary."
            )

        admission_record_by_layer[
            layer_name
        ] = record

    normalized_layers = {}
    normalization_records = []

    for ordinal, layer_name in enumerate(
        expected_order,
        1,
    ):

        source_payload = admitted_results.get(
            layer_name
        )

        if not isinstance(
            source_payload,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " admitted source payload is invalid."
            )

        contract = (
            _ARTICLE_SEMANTIC_UPSTREAM_RESULT_CONTRACTS[
                layer_name
            ]
        )

        admission_record = admission_record_by_layer.get(
            layer_name
        )

        if admission_record is None:
            raise ArticleSemanticConsolidationError(
                layer_name
                + " admission record is missing."
            )

        expected_authority = (
            _ARTICLE_SEMANTIC_INPUT_AUTHORITY[
                layer_name
            ]
        )

        if (
            admission_record.get(
                "phase"
            )
            != contract[
                "phase"
            ]
            or admission_record.get(
                "schema_version"
            )
            != contract[
                "schema_version"
            ]
            or admission_record.get(
                "patch"
            )
            != contract[
                "patch"
            ]
            or admission_record.get(
                "status"
            )
            != contract[
                "status"
            ]
            or admission_record.get(
                "input_authority"
            )
            != expected_authority
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " admission metadata does not match the canonical "
                "upstream contract."
            )

        if (
            source_payload.get(
                "schema_version"
            )
            != contract[
                "schema_version"
            ]
            or source_payload.get(
                "phase"
            )
            != contract[
                "phase"
            ]
            or source_payload.get(
                "status"
            )
            != contract[
                "status"
            ]
            or source_payload.get(
                "next_stage"
            )
            != contract[
                "next_stage"
            ]
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " source contract changed after 4.6.16D intake."
            )

        if (
            contract[
                "patch"
            ]
            is not None
            and source_payload.get(
                "patch"
            )
            != contract[
                "patch"
            ]
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " canonical patch changed after intake."
            )

        if (
            contract[
                "persistence_policy"
            ]
            is not None
            and source_payload.get(
                "persistence_policy"
            )
            != contract[
                "persistence_policy"
            ]
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " persistence boundary changed after intake."
            )

        if layer_name in _FOUNDATIONAL_SEMANTIC_LAYERS:
            group_name = (
                "foundational_semantic_intelligence"
            )

        elif layer_name in _STRUCTURED_REASONING_LAYERS:
            group_name = (
                "structured_reasoning_intelligence"
            )

        elif layer_name in _CONTEXTUAL_COMPARATIVE_LAYERS:
            group_name = (
                "contextual_comparative_intelligence"
            )

        elif layer_name in _HYBRID_INTELLIGENCE_LAYERS:
            group_name = (
                "symbolic_neural_hybrid_intelligence"
            )

        else:
            raise ArticleSemanticConsolidationError(
                layer_name
                + " has no canonical semantic consolidation group."
            )

        normalized_layers[
            layer_name
        ] = {
            "normalization_status":
                "UPSTREAM_SEMANTIC_LAYER_NORMALIZED",

            "ordinal":
                ordinal,

            "layer_name":
                layer_name,

            "group_name":
                group_name,

            "phase":
                contract[
                    "phase"
                ],

            "schema_version":
                contract[
                    "schema_version"
                ],

            "patch":
                contract[
                    "patch"
                ],

            "status":
                contract[
                    "status"
                ],

            "source_next_stage":
                contract[
                    "next_stage"
                ],

            "input_authority":
                expected_authority,

            "source_persistence_policy":
                contract[
                    "persistence_policy"
                ],

            "source_payload":
                deepcopy(
                    dict(
                        source_payload
                    )
                ),

            "source_payload_preserved":
                True,

            "article_identity_alignment_performed":
                False,

            "semantic_assembly_performed":
                False,

            "cross_layer_reasoning_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,
        }

        normalization_records.append({
            "normalization_record_id":
                "ASC_NORMALIZATION:"
                + str(
                    ordinal
                ),

            "ordinal":
                ordinal,

            "layer_name":
                layer_name,

            "group_name":
                group_name,

            "phase":
                contract[
                    "phase"
                ],

            "input_authority":
                expected_authority,

            "contract_revalidated":
                True,

            "payload_deep_copied":
                True,

            "payload_meaning_changed":
                False,

            "article_identity_alignment_performed":
                False,

            "new_reasoning_performed":
                False,
        })

    normalized_group_index = {
        "foundational_semantic_intelligence":
            list(
                _FOUNDATIONAL_SEMANTIC_LAYERS
            ),

        "structured_reasoning_intelligence":
            list(
                _STRUCTURED_REASONING_LAYERS
            ),

        "contextual_comparative_intelligence":
            list(
                _CONTEXTUAL_COMPARATIVE_LAYERS
            ),

        "symbolic_neural_hybrid_intelligence":
            list(
                _HYBRID_INTELLIGENCE_LAYERS
            ),
    }

    return {
        "schema_version":
            "article_semantic_upstream_normalization_v1",

        "article_semantic_consolidation_version":
            ARTICLE_SEMANTIC_CONSOLIDATION_VERSION,

        "phase":
            ARTICLE_SEMANTIC_CONSOLIDATION_PHASE,

        "patch":
            "4.6.16E",

        "status":
            "ARTICLE_SEMANTIC_UPSTREAM_INTELLIGENCE_NORMALIZED",

        "normalized_layer_order":
            deepcopy(
                expected_order
            ),

        "normalized_layer_count":
            len(
                expected_order
            ),

        "normalized_layers":
            normalized_layers,

        "normalization_records":
            normalization_records,

        "normalized_group_index":
            normalized_group_index,

        "source_intake_result":
            deepcopy(
                dict(
                    intake_result
                )
            ),

        "processing_boundaries": {
            "intake_validation_preserved":
                True,

            "upstream_normalization_performed":
                True,

            "all_15_upstream_layers_normalized":
                True,

            "source_payloads_deep_copied":
                True,

            "source_payload_meaning_preserved":
                True,

            "canonical_layer_order_preserved":
                True,

            "foundational_assembly_performed":
                False,

            "structured_reasoning_assembly_performed":
                False,

            "contextual_comparative_assembly_performed":
                False,

            "hybrid_integration_performed":
                False,

            "article_identity_alignment_performed":
                False,

            "cross_layer_provenance_alignment_performed":
                False,

            "cross_layer_state_index_construction_performed":
                False,

            "conflict_uncertainty_abstention_preservation_performed":
                False,

            "article_semantic_consolidation_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "cross_layer_fact_synthesis_performed":
                False,

            "conflict_resolution_performed":
                False,

            "confidence_recalculation_performed":
                False,

            "uncertainty_strengthening_performed":
                False,

            "fuzzy_semantic_deduplication_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_validation_performed":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "foundational_semantic_intelligence_assembly",
    }


# =====================================================================
# PATCH 4.6.16F ? Foundational Semantic Intelligence Assembly
# =====================================================================

def assemble_foundational_semantic_intelligence_v1(
    normalized_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Assemble the five normalized foundational Semantic Intelligence
    layers into one governed article-local foundational collection.

    The five layers are:
    - Semantic Runtime Reader
    - Entity & Concept Intelligence
    - Phrase Neighborhood Intelligence
    - Topic Intent Intelligence
    - Section Evidence Intelligence

    This stage performs structural assembly only.

    It does NOT:
    - rewrite source payloads,
    - merge semantic meaning,
    - align article identities,
    - infer canonical article identity,
    - perform cross-layer reasoning,
    - create new facts or relations,
    - resolve conflicts,
    - recalculate confidence,
    - strengthen uncertainty,
    - perform fuzzy semantic deduplication,
    - call external models,
    - write Semantic Memory,
    - persist intelligence,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        normalized_result,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "normalized_result must be a mapping."
        )

    if (
        normalized_result.get(
            "schema_version"
        )
        != "article_semantic_upstream_normalization_v1"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16F requires "
            "article_semantic_upstream_normalization_v1."
        )

    if (
        normalized_result.get(
            "phase"
        )
        != "4.6.16"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16F requires Phase 4.6.16 input."
        )

    if (
        normalized_result.get(
            "patch"
        )
        != "4.6.16E"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16F requires canonical 4.6.16E input."
        )

    if (
        normalized_result.get(
            "status"
        )
        != "ARTICLE_SEMANTIC_UPSTREAM_INTELLIGENCE_NORMALIZED"
    ):
        raise ArticleSemanticConsolidationError(
            "Upstream Semantic Intelligence is not normalized."
        )

    if (
        normalized_result.get(
            "next_stage"
        )
        != "foundational_semantic_intelligence_assembly"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16E does not hand off to foundational assembly."
        )

    if (
        normalized_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16F requires article-local transient intelligence."
        )

    boundaries = normalized_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16E processing boundaries are missing."
        )

    required_true_boundaries = (
        "intake_validation_preserved",
        "upstream_normalization_performed",
        "all_15_upstream_layers_normalized",
        "source_payloads_deep_copied",
        "source_payload_meaning_preserved",
        "canonical_layer_order_preserved",
    )

    for boundary_name in required_true_boundaries:

        if (
            boundaries.get(
                boundary_name
            )
            is not True
        ):
            raise ArticleSemanticConsolidationError(
                "Required 4.6.16E boundary is not preserved: "
                + boundary_name
            )

    if (
        boundaries.get(
            "foundational_assembly_performed"
        )
        is not False
    ):
        raise ArticleSemanticConsolidationError(
            "Foundational assembly was already performed."
        )

    normalized_layers = normalized_result.get(
        "normalized_layers"
    )

    normalized_group_index = normalized_result.get(
        "normalized_group_index"
    )

    normalized_order = normalized_result.get(
        "normalized_layer_order"
    )

    if not isinstance(
        normalized_layers,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Normalized layer map is invalid."
        )

    if not isinstance(
        normalized_group_index,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Normalized group index is invalid."
        )

    if not isinstance(
        normalized_order,
        list,
    ):
        raise ArticleSemanticConsolidationError(
            "Normalized layer order is invalid."
        )

    expected_full_order = list(
        _ARTICLE_SEMANTIC_LAYER_PHASES.keys()
    )

    if normalized_order != expected_full_order:
        raise ArticleSemanticConsolidationError(
            "Normalized layer order is no longer canonical."
        )

    expected_foundational_layers = list(
        _FOUNDATIONAL_SEMANTIC_LAYERS
    )

    actual_foundational_index = (
        normalized_group_index.get(
            "foundational_semantic_intelligence"
        )
    )

    if (
        actual_foundational_index
        != expected_foundational_layers
    ):
        raise ArticleSemanticConsolidationError(
            "Foundational Semantic Intelligence group index "
            "does not match the canonical five-layer definition."
        )

    foundational_layers = {}
    assembly_records = []

    for group_ordinal, layer_name in enumerate(
        expected_foundational_layers,
        1,
    ):

        envelope = normalized_layers.get(
            layer_name
        )

        if not isinstance(
            envelope,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " normalized envelope is missing."
            )

        if (
            envelope.get(
                "normalization_status"
            )
            != "UPSTREAM_SEMANTIC_LAYER_NORMALIZED"
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " is not normalized."
            )

        if (
            envelope.get(
                "layer_name"
            )
            != layer_name
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " normalized envelope has the wrong layer identity."
            )

        if (
            envelope.get(
                "group_name"
            )
            != "foundational_semantic_intelligence"
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " is assigned to the wrong normalized group."
            )

        expected_contract = (
            _ARTICLE_SEMANTIC_UPSTREAM_RESULT_CONTRACTS[
                layer_name
            ]
        )

        if (
            envelope.get(
                "phase"
            )
            != expected_contract[
                "phase"
            ]
            or envelope.get(
                "schema_version"
            )
            != expected_contract[
                "schema_version"
            ]
            or envelope.get(
                "patch"
            )
            != expected_contract[
                "patch"
            ]
            or envelope.get(
                "status"
            )
            != expected_contract[
                "status"
            ]
            or envelope.get(
                "source_next_stage"
            )
            != expected_contract[
                "next_stage"
            ]
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " normalized metadata does not match its "
                "canonical source contract."
            )

        if (
            envelope.get(
                "source_payload_preserved"
            )
            is not True
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " source payload preservation is not guaranteed."
            )

        for forbidden_true_field in (
            "article_identity_alignment_performed",
            "semantic_assembly_performed",
            "cross_layer_reasoning_performed",
            "new_reasoning_performed",
            "new_fact_inference_performed",
        ):

            if (
                envelope.get(
                    forbidden_true_field
                )
                is not False
            ):
                raise ArticleSemanticConsolidationError(
                    layer_name
                    + " violates pre-foundational-assembly boundary: "
                    + forbidden_true_field
                )

        assembled_envelope = deepcopy(
            dict(
                envelope
            )
        )

        assembled_envelope[
            "foundational_group_ordinal"
        ] = group_ordinal

        assembled_envelope[
            "foundational_assembly_status"
        ] = (
            "FOUNDATIONAL_SEMANTIC_LAYER_ASSEMBLED"
        )

        assembled_envelope[
            "source_payload_preserved"
        ] = True

        assembled_envelope[
            "article_identity_alignment_performed"
        ] = False

        assembled_envelope[
            "cross_layer_reasoning_performed"
        ] = False

        assembled_envelope[
            "new_reasoning_performed"
        ] = False

        assembled_envelope[
            "new_fact_inference_performed"
        ] = False

        foundational_layers[
            layer_name
        ] = assembled_envelope

        assembly_records.append({
            "assembly_record_id":
                "ASC_FOUNDATIONAL:"
                + str(
                    group_ordinal
                ),

            "group_ordinal":
                group_ordinal,

            "layer_name":
                layer_name,

            "phase":
                expected_contract[
                    "phase"
                ],

            "source_schema_version":
                expected_contract[
                    "schema_version"
                ],

            "source_status":
                expected_contract[
                    "status"
                ],

            "source_payload_preserved":
                True,

            "source_meaning_changed":
                False,

            "article_identity_alignment_performed":
                False,

            "cross_layer_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "assembled":
                True,
        })

    foundational_assembly = {
        "assembly_status":
            "FOUNDATIONAL_SEMANTIC_INTELLIGENCE_ASSEMBLED",

        "group_name":
            "foundational_semantic_intelligence",

        "layer_order":
            deepcopy(
                expected_foundational_layers
            ),

        "layer_count":
            len(
                expected_foundational_layers
            ),

        "layers":
            foundational_layers,

        "assembly_records":
            assembly_records,

        "source_payloads_preserved":
            True,

        "source_meaning_preserved":
            True,

        "article_identity_alignment_performed":
            False,

        "cross_layer_reasoning_performed":
            False,

        "cross_layer_fact_synthesis_performed":
            False,

        "new_reasoning_performed":
            False,

        "new_fact_inference_performed":
            False,
    }

    return {
        "schema_version":
            "article_foundational_semantic_assembly_v1",

        "article_semantic_consolidation_version":
            ARTICLE_SEMANTIC_CONSOLIDATION_VERSION,

        "phase":
            ARTICLE_SEMANTIC_CONSOLIDATION_PHASE,

        "patch":
            "4.6.16F",

        "status":
            "FOUNDATIONAL_SEMANTIC_INTELLIGENCE_ASSEMBLED",

        "foundational_semantic_intelligence":
            foundational_assembly,

        "normalized_layers":
            deepcopy(
                dict(
                    normalized_layers
                )
            ),

        "normalized_group_index":
            deepcopy(
                dict(
                    normalized_group_index
                )
            ),

        "source_normalization_result":
            deepcopy(
                dict(
                    normalized_result
                )
            ),

        "processing_boundaries": {
            "intake_validation_preserved":
                True,

            "upstream_normalization_preserved":
                True,

            "foundational_assembly_performed":
                True,

            "exact_five_foundational_layers_assembled":
                True,

            "foundational_source_payloads_preserved":
                True,

            "foundational_source_meaning_preserved":
                True,

            "structured_reasoning_assembly_performed":
                False,

            "contextual_comparative_assembly_performed":
                False,

            "hybrid_integration_performed":
                False,

            "article_identity_alignment_performed":
                False,

            "cross_layer_provenance_alignment_performed":
                False,

            "cross_layer_state_index_construction_performed":
                False,

            "conflict_uncertainty_abstention_preservation_performed":
                False,

            "article_semantic_consolidation_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "cross_layer_fact_synthesis_performed":
                False,

            "conflict_resolution_performed":
                False,

            "confidence_recalculation_performed":
                False,

            "uncertainty_strengthening_performed":
                False,

            "fuzzy_semantic_deduplication_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_validation_performed":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "structured_reasoning_intelligence_assembly",
    }


# =====================================================================
# PATCH 4.6.16G ? Structured Reasoning Intelligence Assembly
# =====================================================================

def assemble_structured_reasoning_intelligence_v1(
    foundational_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Assemble the five normalized certified structured-reasoning layers:

    - Logical Intelligence
    - Relational Intelligence
    - Causal Intelligence
    - Quantitative Intelligence
    - Procedural Intelligence

    Structural assembly only.

    This stage does NOT:
    - rerun reasoning,
    - merge conclusions,
    - infer new facts,
    - infer new relations,
    - resolve conflicts,
    - recalculate confidence,
    - strengthen uncertainty,
    - align article identities,
    - rewrite evidence,
    - perform fuzzy semantic deduplication,
    - call external models,
    - persist intelligence,
    - write Semantic Memory,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        foundational_result,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "foundational_result must be a mapping."
        )

    if (
        foundational_result.get(
            "schema_version"
        )
        != "article_foundational_semantic_assembly_v1"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16G requires "
            "article_foundational_semantic_assembly_v1."
        )

    if foundational_result.get(
        "phase"
    ) != "4.6.16":
        raise ArticleSemanticConsolidationError(
            "4.6.16G requires Phase 4.6.16 input."
        )

    if foundational_result.get(
        "patch"
    ) != "4.6.16F":
        raise ArticleSemanticConsolidationError(
            "4.6.16G requires canonical 4.6.16F input."
        )

    if (
        foundational_result.get(
            "status"
        )
        != "FOUNDATIONAL_SEMANTIC_INTELLIGENCE_ASSEMBLED"
    ):
        raise ArticleSemanticConsolidationError(
            "Foundational Semantic Intelligence is not assembled."
        )

    if (
        foundational_result.get(
            "next_stage"
        )
        != "structured_reasoning_intelligence_assembly"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16F does not hand off to structured reasoning assembly."
        )

    if (
        foundational_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16G requires article-local transient intelligence."
        )

    boundaries = foundational_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16F processing boundaries are missing."
        )

    for boundary_name in (
        "intake_validation_preserved",
        "upstream_normalization_preserved",
        "foundational_assembly_performed",
        "exact_five_foundational_layers_assembled",
        "foundational_source_payloads_preserved",
        "foundational_source_meaning_preserved",
    ):
        if boundaries.get(
            boundary_name
        ) is not True:
            raise ArticleSemanticConsolidationError(
                "Required 4.6.16F boundary is not preserved: "
                + boundary_name
            )

    if boundaries.get(
        "structured_reasoning_assembly_performed"
    ) is not False:
        raise ArticleSemanticConsolidationError(
            "Structured reasoning assembly was already performed."
        )

    foundational = foundational_result.get(
        "foundational_semantic_intelligence"
    )

    if not isinstance(
        foundational,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Foundational Semantic Intelligence collection is missing."
        )

    if (
        foundational.get(
            "assembly_status"
        )
        != "FOUNDATIONAL_SEMANTIC_INTELLIGENCE_ASSEMBLED"
    ):
        raise ArticleSemanticConsolidationError(
            "Foundational assembly state is invalid."
        )

    normalized_layers = foundational_result.get(
        "normalized_layers"
    )

    normalized_group_index = foundational_result.get(
        "normalized_group_index"
    )

    if not isinstance(
        normalized_layers,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Normalized layer map is missing."
        )

    if not isinstance(
        normalized_group_index,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Normalized group index is missing."
        )

    expected_layers = list(
        _STRUCTURED_REASONING_LAYERS
    )

    if (
        normalized_group_index.get(
            "structured_reasoning_intelligence"
        )
        != expected_layers
    ):
        raise ArticleSemanticConsolidationError(
            "Structured reasoning group index does not match "
            "the canonical five-layer definition."
        )

    structured_layers = {}
    assembly_records = []

    for group_ordinal, layer_name in enumerate(
        expected_layers,
        1,
    ):

        envelope = normalized_layers.get(
            layer_name
        )

        if not isinstance(
            envelope,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " normalized envelope is missing."
            )

        if (
            envelope.get(
                "normalization_status"
            )
            != "UPSTREAM_SEMANTIC_LAYER_NORMALIZED"
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " is not normalized."
            )

        if envelope.get(
            "layer_name"
        ) != layer_name:
            raise ArticleSemanticConsolidationError(
                layer_name
                + " normalized layer identity is invalid."
            )

        if (
            envelope.get(
                "group_name"
            )
            != "structured_reasoning_intelligence"
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " is assigned to the wrong reasoning group."
            )

        contract = (
            _ARTICLE_SEMANTIC_UPSTREAM_RESULT_CONTRACTS[
                layer_name
            ]
        )

        expected_authority = (
            _ARTICLE_SEMANTIC_INPUT_AUTHORITY[
                layer_name
            ]
        )

        if (
            envelope.get(
                "phase"
            )
            != contract[
                "phase"
            ]
            or envelope.get(
                "schema_version"
            )
            != contract[
                "schema_version"
            ]
            or envelope.get(
                "patch"
            )
            != contract[
                "patch"
            ]
            or envelope.get(
                "status"
            )
            != contract[
                "status"
            ]
            or envelope.get(
                "source_next_stage"
            )
            != contract[
                "next_stage"
            ]
            or envelope.get(
                "input_authority"
            )
            != expected_authority
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " normalized certified contract is invalid."
            )

        if expected_authority != "CERTIFIED_RESULT":
            raise ArticleSemanticConsolidationError(
                layer_name
                + " does not carry certified reasoning authority."
            )

        if (
            envelope.get(
                "source_payload_preserved"
            )
            is not True
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " source payload preservation was lost."
            )

        for field_name in (
            "article_identity_alignment_performed",
            "semantic_assembly_performed",
            "cross_layer_reasoning_performed",
            "new_reasoning_performed",
            "new_fact_inference_performed",
        ):
            if envelope.get(
                field_name
            ) is not False:
                raise ArticleSemanticConsolidationError(
                    layer_name
                    + " violates pre-assembly boundary: "
                    + field_name
                )

        assembled = deepcopy(
            dict(
                envelope
            )
        )

        assembled[
            "structured_reasoning_group_ordinal"
        ] = group_ordinal

        assembled[
            "structured_reasoning_assembly_status"
        ] = (
            "STRUCTURED_REASONING_LAYER_ASSEMBLED"
        )

        assembled[
            "certified_source_preserved"
        ] = True

        assembled[
            "source_payload_preserved"
        ] = True

        assembled[
            "article_identity_alignment_performed"
        ] = False

        assembled[
            "cross_layer_reasoning_performed"
        ] = False

        assembled[
            "new_reasoning_performed"
        ] = False

        assembled[
            "new_fact_inference_performed"
        ] = False

        assembled[
            "new_relation_inference_performed"
        ] = False

        structured_layers[
            layer_name
        ] = assembled

        assembly_records.append({
            "assembly_record_id":
                "ASC_STRUCTURED_REASONING:"
                + str(
                    group_ordinal
                ),

            "group_ordinal":
                group_ordinal,

            "layer_name":
                layer_name,

            "phase":
                contract[
                    "phase"
                ],

            "source_schema_version":
                contract[
                    "schema_version"
                ],

            "source_patch":
                contract[
                    "patch"
                ],

            "source_status":
                contract[
                    "status"
                ],

            "source_authority":
                expected_authority,

            "certified_source_preserved":
                True,

            "source_payload_preserved":
                True,

            "source_meaning_changed":
                False,

            "cross_layer_reasoning_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "assembled":
                True,
        })

    structured_assembly = {
        "assembly_status":
            "STRUCTURED_REASONING_INTELLIGENCE_ASSEMBLED",

        "group_name":
            "structured_reasoning_intelligence",

        "layer_order":
            deepcopy(
                expected_layers
            ),

        "layer_count":
            len(
                expected_layers
            ),

        "layers":
            structured_layers,

        "assembly_records":
            assembly_records,

        "certified_sources_preserved":
            True,

        "source_payloads_preserved":
            True,

        "source_meaning_preserved":
            True,

        "article_identity_alignment_performed":
            False,

        "cross_layer_reasoning_performed":
            False,

        "cross_layer_fact_synthesis_performed":
            False,

        "conflict_resolution_performed":
            False,

        "confidence_recalculation_performed":
            False,

        "new_reasoning_performed":
            False,

        "new_fact_inference_performed":
            False,

        "new_relation_inference_performed":
            False,
    }

    return {
        "schema_version":
            "article_structured_reasoning_assembly_v1",

        "article_semantic_consolidation_version":
            ARTICLE_SEMANTIC_CONSOLIDATION_VERSION,

        "phase":
            ARTICLE_SEMANTIC_CONSOLIDATION_PHASE,

        "patch":
            "4.6.16G",

        "status":
            "STRUCTURED_REASONING_INTELLIGENCE_ASSEMBLED",

        "foundational_semantic_intelligence":
            deepcopy(
                dict(
                    foundational
                )
            ),

        "structured_reasoning_intelligence":
            structured_assembly,

        "normalized_layers":
            deepcopy(
                dict(
                    normalized_layers
                )
            ),

        "normalized_group_index":
            deepcopy(
                dict(
                    normalized_group_index
                )
            ),

        "source_foundational_result":
            deepcopy(
                dict(
                    foundational_result
                )
            ),

        "processing_boundaries": {
            "intake_validation_preserved":
                True,

            "upstream_normalization_preserved":
                True,

            "foundational_assembly_preserved":
                True,

            "structured_reasoning_assembly_performed":
                True,

            "exact_five_structured_reasoning_layers_assembled":
                True,

            "structured_certified_sources_preserved":
                True,

            "structured_source_payloads_preserved":
                True,

            "structured_source_meaning_preserved":
                True,

            "contextual_comparative_assembly_performed":
                False,

            "hybrid_integration_performed":
                False,

            "article_identity_alignment_performed":
                False,

            "cross_layer_provenance_alignment_performed":
                False,

            "cross_layer_state_index_construction_performed":
                False,

            "conflict_uncertainty_abstention_preservation_performed":
                False,

            "article_semantic_consolidation_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "cross_layer_fact_synthesis_performed":
                False,

            "conflict_resolution_performed":
                False,

            "confidence_recalculation_performed":
                False,

            "uncertainty_strengthening_performed":
                False,

            "fuzzy_semantic_deduplication_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_validation_performed":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "contextual_comparative_intelligence_assembly",
    }


# =====================================================================
# PATCH 4.6.16H ? Contextual / Comparative Intelligence Assembly
# =====================================================================

def assemble_contextual_comparative_intelligence_v1(
    structured_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Assemble the four normalized certified contextual/comparative
    Semantic Intelligence layers:

    - Analogical Intelligence
    - Semantic Similarity Intelligence
    - Temporal Intelligence
    - Uncertainty Intelligence

    Structural assembly only.

    This stage does NOT:
    - rerun analogical reasoning,
    - rerun similarity reasoning,
    - infer temporal relationships,
    - strengthen or weaken uncertainty,
    - merge conclusions,
    - infer new facts or relations,
    - align article identities,
    - resolve conflicts,
    - recalculate confidence,
    - rewrite evidence,
    - perform fuzzy semantic deduplication,
    - call external models,
    - write Semantic Memory,
    - persist intelligence,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        structured_result,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "structured_result must be a mapping."
        )

    if (
        structured_result.get(
            "schema_version"
        )
        != "article_structured_reasoning_assembly_v1"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16H requires "
            "article_structured_reasoning_assembly_v1."
        )

    if (
        structured_result.get(
            "phase"
        )
        != "4.6.16"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16H requires Phase 4.6.16 input."
        )

    if (
        structured_result.get(
            "patch"
        )
        != "4.6.16G"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16H requires canonical 4.6.16G input."
        )

    if (
        structured_result.get(
            "status"
        )
        != "STRUCTURED_REASONING_INTELLIGENCE_ASSEMBLED"
    ):
        raise ArticleSemanticConsolidationError(
            "Structured Reasoning Intelligence is not assembled."
        )

    if (
        structured_result.get(
            "next_stage"
        )
        != "contextual_comparative_intelligence_assembly"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16G does not hand off to contextual/comparative assembly."
        )

    if (
        structured_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16H requires article-local transient intelligence."
        )

    boundaries = structured_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16G processing boundaries are missing."
        )

    for boundary_name in (
        "intake_validation_preserved",
        "upstream_normalization_preserved",
        "foundational_assembly_preserved",
        "structured_reasoning_assembly_performed",
        "exact_five_structured_reasoning_layers_assembled",
        "structured_certified_sources_preserved",
        "structured_source_payloads_preserved",
        "structured_source_meaning_preserved",
    ):
        if (
            boundaries.get(
                boundary_name
            )
            is not True
        ):
            raise ArticleSemanticConsolidationError(
                "Required 4.6.16G boundary is not preserved: "
                + boundary_name
            )

    if (
        boundaries.get(
            "contextual_comparative_assembly_performed"
        )
        is not False
    ):
        raise ArticleSemanticConsolidationError(
            "Contextual/comparative assembly was already performed."
        )

    foundational = structured_result.get(
        "foundational_semantic_intelligence"
    )

    structured = structured_result.get(
        "structured_reasoning_intelligence"
    )

    normalized_layers = structured_result.get(
        "normalized_layers"
    )

    normalized_group_index = structured_result.get(
        "normalized_group_index"
    )

    if not isinstance(
        foundational,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Foundational Semantic Intelligence is missing."
        )

    if not isinstance(
        structured,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Structured Reasoning Intelligence is missing."
        )

    if (
        structured.get(
            "assembly_status"
        )
        != "STRUCTURED_REASONING_INTELLIGENCE_ASSEMBLED"
    ):
        raise ArticleSemanticConsolidationError(
            "Structured reasoning assembly state is invalid."
        )

    if not isinstance(
        normalized_layers,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Normalized layer map is missing."
        )

    if not isinstance(
        normalized_group_index,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Normalized group index is missing."
        )

    expected_layers = list(
        _CONTEXTUAL_COMPARATIVE_LAYERS
    )

    if (
        normalized_group_index.get(
            "contextual_comparative_intelligence"
        )
        != expected_layers
    ):
        raise ArticleSemanticConsolidationError(
            "Contextual/comparative group index does not match "
            "the canonical four-layer definition."
        )

    contextual_layers = {}
    assembly_records = []

    for group_ordinal, layer_name in enumerate(
        expected_layers,
        1,
    ):

        envelope = normalized_layers.get(
            layer_name
        )

        if not isinstance(
            envelope,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " normalized envelope is missing."
            )

        if (
            envelope.get(
                "normalization_status"
            )
            != "UPSTREAM_SEMANTIC_LAYER_NORMALIZED"
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " is not normalized."
            )

        if (
            envelope.get(
                "layer_name"
            )
            != layer_name
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " normalized layer identity is invalid."
            )

        if (
            envelope.get(
                "group_name"
            )
            != "contextual_comparative_intelligence"
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " is assigned to the wrong contextual group."
            )

        contract = (
            _ARTICLE_SEMANTIC_UPSTREAM_RESULT_CONTRACTS[
                layer_name
            ]
        )

        expected_authority = (
            _ARTICLE_SEMANTIC_INPUT_AUTHORITY[
                layer_name
            ]
        )

        if expected_authority != "CERTIFIED_RESULT":
            raise ArticleSemanticConsolidationError(
                layer_name
                + " does not carry certified contextual authority."
            )

        if (
            envelope.get(
                "phase"
            )
            != contract[
                "phase"
            ]
            or envelope.get(
                "schema_version"
            )
            != contract[
                "schema_version"
            ]
            or envelope.get(
                "patch"
            )
            != contract[
                "patch"
            ]
            or envelope.get(
                "status"
            )
            != contract[
                "status"
            ]
            or envelope.get(
                "source_next_stage"
            )
            != contract[
                "next_stage"
            ]
            or envelope.get(
                "input_authority"
            )
            != expected_authority
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " normalized certified contract is invalid."
            )

        if (
            envelope.get(
                "source_payload_preserved"
            )
            is not True
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " source payload preservation was lost."
            )

        for field_name in (
            "article_identity_alignment_performed",
            "semantic_assembly_performed",
            "cross_layer_reasoning_performed",
            "new_reasoning_performed",
            "new_fact_inference_performed",
        ):
            if (
                envelope.get(
                    field_name
                )
                is not False
            ):
                raise ArticleSemanticConsolidationError(
                    layer_name
                    + " violates pre-assembly boundary: "
                    + field_name
                )

        assembled = deepcopy(
            dict(
                envelope
            )
        )

        assembled[
            "contextual_comparative_group_ordinal"
        ] = group_ordinal

        assembled[
            "contextual_comparative_assembly_status"
        ] = (
            "CONTEXTUAL_COMPARATIVE_LAYER_ASSEMBLED"
        )

        assembled[
            "certified_source_preserved"
        ] = True

        assembled[
            "source_payload_preserved"
        ] = True

        assembled[
            "article_identity_alignment_performed"
        ] = False

        assembled[
            "cross_layer_reasoning_performed"
        ] = False

        assembled[
            "new_reasoning_performed"
        ] = False

        assembled[
            "new_fact_inference_performed"
        ] = False

        assembled[
            "new_relation_inference_performed"
        ] = False

        assembled[
            "uncertainty_strengthening_performed"
        ] = False

        contextual_layers[
            layer_name
        ] = assembled

        assembly_records.append({
            "assembly_record_id":
                "ASC_CONTEXTUAL_COMPARATIVE:"
                + str(
                    group_ordinal
                ),

            "group_ordinal":
                group_ordinal,

            "layer_name":
                layer_name,

            "phase":
                contract[
                    "phase"
                ],

            "source_schema_version":
                contract[
                    "schema_version"
                ],

            "source_patch":
                contract[
                    "patch"
                ],

            "source_status":
                contract[
                    "status"
                ],

            "source_authority":
                expected_authority,

            "certified_source_preserved":
                True,

            "source_payload_preserved":
                True,

            "source_meaning_changed":
                False,

            "article_identity_alignment_performed":
                False,

            "cross_layer_reasoning_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "uncertainty_strengthening_performed":
                False,

            "assembled":
                True,
        })

    contextual_assembly = {
        "assembly_status":
            "CONTEXTUAL_COMPARATIVE_INTELLIGENCE_ASSEMBLED",

        "group_name":
            "contextual_comparative_intelligence",

        "layer_order":
            deepcopy(
                expected_layers
            ),

        "layer_count":
            len(
                expected_layers
            ),

        "layers":
            contextual_layers,

        "assembly_records":
            assembly_records,

        "certified_sources_preserved":
            True,

        "source_payloads_preserved":
            True,

        "source_meaning_preserved":
            True,

        "article_identity_alignment_performed":
            False,

        "cross_layer_reasoning_performed":
            False,

        "cross_layer_fact_synthesis_performed":
            False,

        "conflict_resolution_performed":
            False,

        "confidence_recalculation_performed":
            False,

        "uncertainty_strengthening_performed":
            False,

        "new_reasoning_performed":
            False,

        "new_fact_inference_performed":
            False,

        "new_relation_inference_performed":
            False,
    }

    return {
        "schema_version":
            "article_contextual_comparative_assembly_v1",

        "article_semantic_consolidation_version":
            ARTICLE_SEMANTIC_CONSOLIDATION_VERSION,

        "phase":
            ARTICLE_SEMANTIC_CONSOLIDATION_PHASE,

        "patch":
            "4.6.16H",

        "status":
            "CONTEXTUAL_COMPARATIVE_INTELLIGENCE_ASSEMBLED",

        "foundational_semantic_intelligence":
            deepcopy(
                dict(
                    foundational
                )
            ),

        "structured_reasoning_intelligence":
            deepcopy(
                dict(
                    structured
                )
            ),

        "contextual_comparative_intelligence":
            contextual_assembly,

        "normalized_layers":
            deepcopy(
                dict(
                    normalized_layers
                )
            ),

        "normalized_group_index":
            deepcopy(
                dict(
                    normalized_group_index
                )
            ),

        "source_structured_result":
            deepcopy(
                dict(
                    structured_result
                )
            ),

        "processing_boundaries": {
            "intake_validation_preserved":
                True,

            "upstream_normalization_preserved":
                True,

            "foundational_assembly_preserved":
                True,

            "structured_reasoning_assembly_preserved":
                True,

            "contextual_comparative_assembly_performed":
                True,

            "exact_four_contextual_comparative_layers_assembled":
                True,

            "contextual_certified_sources_preserved":
                True,

            "contextual_source_payloads_preserved":
                True,

            "contextual_source_meaning_preserved":
                True,

            "hybrid_integration_performed":
                False,

            "article_identity_alignment_performed":
                False,

            "cross_layer_provenance_alignment_performed":
                False,

            "cross_layer_state_index_construction_performed":
                False,

            "conflict_uncertainty_abstention_preservation_performed":
                False,

            "article_semantic_consolidation_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "cross_layer_fact_synthesis_performed":
                False,

            "conflict_resolution_performed":
                False,

            "confidence_recalculation_performed":
                False,

            "uncertainty_strengthening_performed":
                False,

            "fuzzy_semantic_deduplication_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_validation_performed":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "symbolic_neural_hybrid_result_integration",
    }


# =====================================================================
# PATCH 4.6.16I ? Symbolic?Neural Hybrid Result Integration
# =====================================================================

def integrate_symbolic_neural_hybrid_result_v1(
    contextual_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Integrate the frozen 4.6.15S Symbolic?Neural Hybrid result into
    Article Semantic Consolidation.

    Integration is preservation-only.

    This stage does NOT:
    - rerun symbolic reasoning,
    - rerun semantic interpretation,
    - rebuild alignment pairs,
    - redetect agreement or conflict,
    - reconstruct hybrid candidates,
    - resolve conflicts again,
    - recalculate confidence,
    - strengthen uncertainty,
    - alter abstention decisions,
    - override symbolic constraints,
    - align article identities,
    - infer new facts or relations,
    - perform cross-layer synthesis,
    - call external models,
    - write Semantic Memory,
    - persist intelligence,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        contextual_result,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "contextual_result must be a mapping."
        )

    if (
        contextual_result.get(
            "schema_version"
        )
        != "article_contextual_comparative_assembly_v1"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16I requires "
            "article_contextual_comparative_assembly_v1."
        )

    if (
        contextual_result.get(
            "phase"
        )
        != "4.6.16"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16I requires Phase 4.6.16 input."
        )

    if (
        contextual_result.get(
            "patch"
        )
        != "4.6.16H"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16I requires canonical 4.6.16H input."
        )

    if (
        contextual_result.get(
            "status"
        )
        != "CONTEXTUAL_COMPARATIVE_INTELLIGENCE_ASSEMBLED"
    ):
        raise ArticleSemanticConsolidationError(
            "Contextual/comparative intelligence is not assembled."
        )

    if (
        contextual_result.get(
            "next_stage"
        )
        != "symbolic_neural_hybrid_result_integration"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16H does not hand off to hybrid-result integration."
        )

    if (
        contextual_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16I requires article-local transient intelligence."
        )

    boundaries = contextual_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16H processing boundaries are missing."
        )

    for boundary_name in (
        "intake_validation_preserved",
        "upstream_normalization_preserved",
        "foundational_assembly_preserved",
        "structured_reasoning_assembly_preserved",
        "contextual_comparative_assembly_performed",
        "exact_four_contextual_comparative_layers_assembled",
        "contextual_certified_sources_preserved",
        "contextual_source_payloads_preserved",
        "contextual_source_meaning_preserved",
    ):
        if (
            boundaries.get(
                boundary_name
            )
            is not True
        ):
            raise ArticleSemanticConsolidationError(
                "Required 4.6.16H boundary is not preserved: "
                + boundary_name
            )

    if (
        boundaries.get(
            "hybrid_integration_performed"
        )
        is not False
    ):
        raise ArticleSemanticConsolidationError(
            "Hybrid integration was already performed."
        )

    foundational = contextual_result.get(
        "foundational_semantic_intelligence"
    )

    structured = contextual_result.get(
        "structured_reasoning_intelligence"
    )

    contextual = contextual_result.get(
        "contextual_comparative_intelligence"
    )

    normalized_layers = contextual_result.get(
        "normalized_layers"
    )

    normalized_group_index = contextual_result.get(
        "normalized_group_index"
    )

    for name, value in (
        (
            "foundational_semantic_intelligence",
            foundational,
        ),
        (
            "structured_reasoning_intelligence",
            structured,
        ),
        (
            "contextual_comparative_intelligence",
            contextual,
        ),
        (
            "normalized_layers",
            normalized_layers,
        ),
        (
            "normalized_group_index",
            normalized_group_index,
        ),
    ):
        if not isinstance(
            value,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                name
                + " is missing or invalid."
            )

    if (
        foundational.get(
            "assembly_status"
        )
        != "FOUNDATIONAL_SEMANTIC_INTELLIGENCE_ASSEMBLED"
    ):
        raise ArticleSemanticConsolidationError(
            "Foundational assembly state was not preserved."
        )

    if (
        structured.get(
            "assembly_status"
        )
        != "STRUCTURED_REASONING_INTELLIGENCE_ASSEMBLED"
    ):
        raise ArticleSemanticConsolidationError(
            "Structured assembly state was not preserved."
        )

    if (
        contextual.get(
            "assembly_status"
        )
        != "CONTEXTUAL_COMPARATIVE_INTELLIGENCE_ASSEMBLED"
    ):
        raise ArticleSemanticConsolidationError(
            "Contextual assembly state was not preserved."
        )

    expected_hybrid_group = list(
        _HYBRID_INTELLIGENCE_LAYERS
    )

    if (
        normalized_group_index.get(
            "symbolic_neural_hybrid_intelligence"
        )
        != expected_hybrid_group
    ):
        raise ArticleSemanticConsolidationError(
            "Hybrid group index does not match the canonical definition."
        )

    if expected_hybrid_group != [
        "symbolic_neural_hybrid_intelligence"
    ]:
        raise ArticleSemanticConsolidationError(
            "Canonical hybrid group must contain exactly one layer."
        )

    layer_name = (
        "symbolic_neural_hybrid_intelligence"
    )

    envelope = normalized_layers.get(
        layer_name
    )

    if not isinstance(
        envelope,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Normalized 4.6.15 hybrid envelope is missing."
        )

    contract = (
        _ARTICLE_SEMANTIC_UPSTREAM_RESULT_CONTRACTS[
            layer_name
        ]
    )

    expected_authority = (
        _ARTICLE_SEMANTIC_INPUT_AUTHORITY[
            layer_name
        ]
    )

    if (
        expected_authority
        != "FINAL_FROZEN_RESULT_FROM_CERTIFIED_IMPLEMENTATION"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 hybrid authority contract is invalid."
        )

    if (
        envelope.get(
            "normalization_status"
        )
        != "UPSTREAM_SEMANTIC_LAYER_NORMALIZED"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 hybrid result is not normalized."
        )

    if (
        envelope.get(
            "layer_name"
        )
        != layer_name
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 hybrid envelope has the wrong layer identity."
        )

    if (
        envelope.get(
            "group_name"
        )
        != "symbolic_neural_hybrid_intelligence"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 hybrid envelope is assigned to the wrong group."
        )

    if (
        envelope.get(
            "phase"
        )
        != contract[
            "phase"
        ]
        or envelope.get(
            "schema_version"
        )
        != contract[
            "schema_version"
        ]
        or envelope.get(
            "patch"
        )
        != contract[
            "patch"
        ]
        or envelope.get(
            "status"
        )
        != contract[
            "status"
        ]
        or envelope.get(
            "source_next_stage"
        )
        != contract[
            "next_stage"
        ]
        or envelope.get(
            "input_authority"
        )
        != expected_authority
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 frozen hybrid contract is invalid."
        )

    if (
        envelope.get(
            "source_payload_preserved"
        )
        is not True
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 hybrid source payload preservation was lost."
        )

    for field_name in (
        "article_identity_alignment_performed",
        "semantic_assembly_performed",
        "cross_layer_reasoning_performed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
    ):
        if (
            envelope.get(
                field_name
            )
            is not False
        ):
            raise ArticleSemanticConsolidationError(
                "4.6.15 normalized hybrid envelope violates boundary: "
                + field_name
            )

    source_payload = envelope.get(
        "source_payload"
    )

    if not isinstance(
        source_payload,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 source payload is invalid."
        )

    if (
        source_payload.get(
            "schema_version"
        )
        != "symbolic_neural_hybrid_intelligence_result_v1"
        or source_payload.get(
            "phase"
        )
        != "4.6.15"
        or source_payload.get(
            "patch"
        )
        != "4.6.15S"
        or source_payload.get(
            "status"
        )
        != "SYMBOLIC_NEURAL_HYBRID_INTELLIGENCE_RESULT_READY"
        or source_payload.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
        or source_payload.get(
            "next_stage"
        )
        != "symbolic_neural_hybrid_certification"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15S final-result contract is invalid."
        )

    final_hybrid = source_payload.get(
        "final_symbolic_neural_hybrid_intelligence"
    )

    hybrid_boundaries = source_payload.get(
        "processing_boundaries"
    )

    if not isinstance(
        final_hybrid,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 final hybrid article state is missing."
        )

    if not isinstance(
        hybrid_boundaries,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 processing boundaries are missing."
        )

    if (
        final_hybrid.get(
            "final_status"
        )
        != "SYMBOLIC_NEURAL_HYBRID_INTELLIGENCE_READY"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 final hybrid article state is not ready."
        )

    if (
        hybrid_boundaries.get(
            "final_symbolic_neural_hybrid_result_prepared"
        )
        is not True
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 final-result preparation boundary is incomplete."
        )

    required_false_hybrid_boundaries = (
        "semantic_override_allowed",
        "new_reasoning_performed",
        "cross_candidate_synthesis_performed",
        "evidence_rewrite_performed",
        "candidate_meaning_change_performed",
        "conflict_resolution_reperformed",
        "confidence_recalculation_performed",
        "duplicate_resolution_reperformed",
        "article_consolidation_reperformed",
        "new_hybrid_fact_inference_performed",
        "new_article_fact_inference_performed",
        "truth_assessment_performed",
        "external_validation_performed",
        "external_model_called",
        "semantic_memory_written",
        "linking_decisions_performed",
        "persistence_performed",
    )

    for boundary_name in required_false_hybrid_boundaries:

        if (
            hybrid_boundaries.get(
                boundary_name
            )
            is not False
        ):
            raise ArticleSemanticConsolidationError(
                "4.6.15 frozen hybrid boundary violation: "
                + boundary_name
            )

    integrated_envelope = deepcopy(
        dict(
            envelope
        )
    )

    integrated_envelope[
        "hybrid_integration_status"
    ] = (
        "SYMBOLIC_NEURAL_HYBRID_RESULT_INTEGRATED"
    )

    integrated_envelope[
        "hybrid_group_ordinal"
    ] = 1

    integrated_envelope[
        "frozen_hybrid_contract_preserved"
    ] = True

    integrated_envelope[
        "hard_symbolic_authority_preserved"
    ] = True

    integrated_envelope[
        "neural_semantic_authority_preserved_as_interpretive_only"
    ] = True

    integrated_envelope[
        "agreement_conflict_state_preserved"
    ] = True

    integrated_envelope[
        "abstention_state_preserved"
    ] = True

    integrated_envelope[
        "confidence_state_preserved"
    ] = True

    integrated_envelope[
        "provenance_preserved"
    ] = True

    integrated_envelope[
        "redundancy_lineage_preserved"
    ] = True

    integrated_envelope[
        "article_identity_alignment_performed"
    ] = False

    integrated_envelope[
        "hybrid_reasoning_reperformed"
    ] = False

    integrated_envelope[
        "conflict_resolution_reperformed"
    ] = False

    integrated_envelope[
        "confidence_recalculated"
    ] = False

    integrated_envelope[
        "uncertainty_strengthened"
    ] = False

    integrated_envelope[
        "new_reasoning_performed"
    ] = False

    integrated_envelope[
        "new_fact_inference_performed"
    ] = False

    integrated_envelope[
        "new_relation_inference_performed"
    ] = False

    hybrid_integration = {
        "integration_status":
            "SYMBOLIC_NEURAL_HYBRID_RESULT_INTEGRATED",

        "group_name":
            "symbolic_neural_hybrid_intelligence",

        "layer_order": [
            layer_name
        ],

        "layer_count":
            1,

        "layer":
            integrated_envelope,

        "source_payload":
            deepcopy(
                dict(
                    source_payload
                )
            ),

        "final_symbolic_neural_hybrid_intelligence":
            deepcopy(
                dict(
                    final_hybrid
                )
            ),

        "integration_record": {
            "integration_record_id":
                "ASC_HYBRID:1",

            "layer_name":
                layer_name,

            "phase":
                "4.6.15",

            "source_schema_version":
                "symbolic_neural_hybrid_intelligence_result_v1",

            "source_patch":
                "4.6.15S",

            "source_status":
                "SYMBOLIC_NEURAL_HYBRID_INTELLIGENCE_RESULT_READY",

            "source_authority":
                expected_authority,

            "source_payload_preserved":
                True,

            "source_meaning_changed":
                False,

            "final_hybrid_state_preserved":
                True,

            "hard_symbolic_authority_preserved":
                True,

            "agreement_conflict_state_preserved":
                True,

            "abstention_state_preserved":
                True,

            "confidence_state_preserved":
                True,

            "provenance_preserved":
                True,

            "hybrid_reasoning_reperformed":
                False,

            "conflict_resolution_reperformed":
                False,

            "confidence_recalculated":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "integrated":
                True,
        },

        "source_payload_preserved":
            True,

        "source_meaning_preserved":
            True,

        "hard_symbolic_authority_preserved":
            True,

        "neural_semantic_authority":
            "INTERPRETIVE_ONLY",

        "agreement_conflict_state_preserved":
            True,

        "abstention_state_preserved":
            True,

        "confidence_state_preserved":
            True,

        "provenance_preserved":
            True,

        "redundancy_lineage_preserved":
            True,

        "article_identity_alignment_performed":
            False,

        "hybrid_reasoning_reperformed":
            False,

        "conflict_resolution_reperformed":
            False,

        "confidence_recalculated":
            False,

        "uncertainty_strengthened":
            False,

        "new_reasoning_performed":
            False,

        "new_fact_inference_performed":
            False,

        "new_relation_inference_performed":
            False,
    }

    return {
        "schema_version":
            "article_symbolic_neural_hybrid_integration_v1",

        "article_semantic_consolidation_version":
            ARTICLE_SEMANTIC_CONSOLIDATION_VERSION,

        "phase":
            ARTICLE_SEMANTIC_CONSOLIDATION_PHASE,

        "patch":
            "4.6.16I",

        "status":
            "SYMBOLIC_NEURAL_HYBRID_RESULT_INTEGRATED",

        "foundational_semantic_intelligence":
            deepcopy(
                dict(
                    foundational
                )
            ),

        "structured_reasoning_intelligence":
            deepcopy(
                dict(
                    structured
                )
            ),

        "contextual_comparative_intelligence":
            deepcopy(
                dict(
                    contextual
                )
            ),

        "symbolic_neural_hybrid_intelligence":
            hybrid_integration,

        "normalized_layers":
            deepcopy(
                dict(
                    normalized_layers
                )
            ),

        "normalized_group_index":
            deepcopy(
                dict(
                    normalized_group_index
                )
            ),

        "source_contextual_result":
            deepcopy(
                dict(
                    contextual_result
                )
            ),

        "processing_boundaries": {
            "intake_validation_preserved":
                True,

            "upstream_normalization_preserved":
                True,

            "foundational_assembly_preserved":
                True,

            "structured_reasoning_assembly_preserved":
                True,

            "contextual_comparative_assembly_preserved":
                True,

            "hybrid_integration_performed":
                True,

            "exact_single_hybrid_layer_integrated":
                True,

            "frozen_hybrid_contract_preserved":
                True,

            "hybrid_source_payload_preserved":
                True,

            "hybrid_source_meaning_preserved":
                True,

            "hard_symbolic_authority_preserved":
                True,

            "agreement_conflict_state_preserved":
                True,

            "abstention_state_preserved":
                True,

            "hybrid_confidence_state_preserved":
                True,

            "hybrid_provenance_preserved":
                True,

            "article_identity_alignment_performed":
                False,

            "cross_layer_provenance_alignment_performed":
                False,

            "cross_layer_state_index_construction_performed":
                False,

            "conflict_uncertainty_abstention_preservation_performed":
                False,

            "article_semantic_consolidation_performed":
                False,

            "hybrid_reasoning_reperformed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "cross_layer_fact_synthesis_performed":
                False,

            "conflict_resolution_performed":
                False,

            "confidence_recalculation_performed":
                False,

            "uncertainty_strengthening_performed":
                False,

            "fuzzy_semantic_deduplication_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_validation_performed":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "cross_layer_article_identity_alignment",
    }


# =====================================================================
# PATCH 4.6.16J ? Cross-Layer Article Identity Alignment
# =====================================================================

def align_cross_layer_article_identity_v1(
    hybrid_integration_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Align article identity across all 15 admitted Semantic Intelligence
    layers using the frozen 4.6.15S article_identity as the canonical
    anchor.

    Existing upstream identity evidence is compared exactly.

    Missing identity evidence is recorded as not independently asserted.
    It is never fabricated from another layer.

    This stage does NOT:
    - infer article identity from semantic meaning,
    - derive identity from URLs or titles,
    - synthesize missing identity fields,
    - rewrite upstream identities,
    - merge different identities,
    - perform semantic reasoning,
    - infer new facts or relations,
    - resolve semantic conflicts,
    - recalculate confidence,
    - strengthen uncertainty,
    - write Semantic Memory,
    - persist intelligence,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        hybrid_integration_result,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "hybrid_integration_result must be a mapping."
        )

    if (
        hybrid_integration_result.get(
            "schema_version"
        )
        != "article_symbolic_neural_hybrid_integration_v1"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16J requires "
            "article_symbolic_neural_hybrid_integration_v1."
        )

    if (
        hybrid_integration_result.get(
            "phase"
        )
        != "4.6.16"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16J requires Phase 4.6.16 input."
        )

    if (
        hybrid_integration_result.get(
            "patch"
        )
        != "4.6.16I"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16J requires canonical 4.6.16I input."
        )

    if (
        hybrid_integration_result.get(
            "status"
        )
        != "SYMBOLIC_NEURAL_HYBRID_RESULT_INTEGRATED"
    ):
        raise ArticleSemanticConsolidationError(
            "Symbolic-Neural Hybrid result is not integrated."
        )

    if (
        hybrid_integration_result.get(
            "next_stage"
        )
        != "cross_layer_article_identity_alignment"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16I does not hand off to article identity alignment."
        )

    if (
        hybrid_integration_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16J requires article-local transient intelligence."
        )

    boundaries = hybrid_integration_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16I processing boundaries are missing."
        )

    for boundary_name in (
        "intake_validation_preserved",
        "upstream_normalization_preserved",
        "foundational_assembly_preserved",
        "structured_reasoning_assembly_preserved",
        "contextual_comparative_assembly_preserved",
        "hybrid_integration_performed",
        "exact_single_hybrid_layer_integrated",
        "frozen_hybrid_contract_preserved",
        "hybrid_source_payload_preserved",
        "hybrid_source_meaning_preserved",
        "hard_symbolic_authority_preserved",
        "agreement_conflict_state_preserved",
        "abstention_state_preserved",
        "hybrid_confidence_state_preserved",
        "hybrid_provenance_preserved",
    ):
        if (
            boundaries.get(
                boundary_name
            )
            is not True
        ):
            raise ArticleSemanticConsolidationError(
                "Required 4.6.16I boundary is not preserved: "
                + boundary_name
            )

    if (
        boundaries.get(
            "article_identity_alignment_performed"
        )
        is not False
    ):
        raise ArticleSemanticConsolidationError(
            "Article identity alignment was already performed."
        )

    foundational = hybrid_integration_result.get(
        "foundational_semantic_intelligence"
    )

    structured = hybrid_integration_result.get(
        "structured_reasoning_intelligence"
    )

    contextual = hybrid_integration_result.get(
        "contextual_comparative_intelligence"
    )

    hybrid = hybrid_integration_result.get(
        "symbolic_neural_hybrid_intelligence"
    )

    normalized_layers = hybrid_integration_result.get(
        "normalized_layers"
    )

    normalized_group_index = hybrid_integration_result.get(
        "normalized_group_index"
    )

    for name, value in (
        (
            "foundational_semantic_intelligence",
            foundational,
        ),
        (
            "structured_reasoning_intelligence",
            structured,
        ),
        (
            "contextual_comparative_intelligence",
            contextual,
        ),
        (
            "symbolic_neural_hybrid_intelligence",
            hybrid,
        ),
        (
            "normalized_layers",
            normalized_layers,
        ),
        (
            "normalized_group_index",
            normalized_group_index,
        ),
    ):
        if not isinstance(
            value,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                name
                + " is missing or invalid."
            )

    expected_layer_order = list(
        _ARTICLE_SEMANTIC_LAYER_PHASES.keys()
    )

    if (
        list(
            normalized_layers.keys()
        )
        != expected_layer_order
    ):
        raise ArticleSemanticConsolidationError(
            "Normalized Semantic Intelligence layer order "
            "is not canonical."
        )

    if len(
        normalized_layers
    ) != 15:
        raise ArticleSemanticConsolidationError(
            "Identity alignment requires exactly 15 normalized layers."
        )

    if (
        hybrid.get(
            "integration_status"
        )
        != "SYMBOLIC_NEURAL_HYBRID_RESULT_INTEGRATED"
    ):
        raise ArticleSemanticConsolidationError(
            "Hybrid integration state is invalid."
        )

    if (
        boundaries.get(
            "frozen_hybrid_contract_preserved"
        )
        is not True
    ):
        raise ArticleSemanticConsolidationError(
            "Frozen hybrid contract was not preserved."
        )

    hybrid_source_payload = hybrid.get(
        "source_payload"
    )

    if not isinstance(
        hybrid_source_payload,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Frozen 4.6.15S source payload is missing."
        )

    normalized_hybrid = normalized_layers.get(
        "symbolic_neural_hybrid_intelligence"
    )

    if not isinstance(
        normalized_hybrid,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Normalized 4.6.15 layer is missing."
        )

    normalized_hybrid_payload = normalized_hybrid.get(
        "source_payload"
    )

    if not isinstance(
        normalized_hybrid_payload,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Normalized 4.6.15 source payload is missing."
        )

    if (
        dict(
            hybrid_source_payload
        )
        != dict(
            normalized_hybrid_payload
        )
    ):
        raise ArticleSemanticConsolidationError(
            "Integrated and normalized 4.6.15 payloads differ."
        )

    canonical_identity_raw = hybrid_source_payload.get(
        "article_identity"
    )

    if not isinstance(
        canonical_identity_raw,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Frozen 4.6.15S article_identity is missing."
        )

    canonical_identity = deepcopy(
        dict(
            canonical_identity_raw
        )
    )

    for required_field in (
        "article_id",
        "workspace_id",
    ):
        value = canonical_identity.get(
            required_field
        )

        if not isinstance(
            value,
            str,
        ) or not value.strip():
            raise ArticleSemanticConsolidationError(
                "Canonical article_identity requires non-empty "
                + required_field
                + "."
            )

    identity_records = []
    asserted_layer_names = []
    unasserted_layer_names = []

    for ordinal, layer_name in enumerate(
        expected_layer_order,
        1,
    ):

        envelope = normalized_layers.get(
            layer_name
        )

        if not isinstance(
            envelope,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " normalized envelope is missing."
            )

        if (
            envelope.get(
                "layer_name"
            )
            != layer_name
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " normalized envelope identity changed."
            )

        if (
            envelope.get(
                "normalization_status"
            )
            != "UPSTREAM_SEMANTIC_LAYER_NORMALIZED"
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " is not normalized."
            )

        source_payload = envelope.get(
            "source_payload"
        )

        if not isinstance(
            source_payload,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " source payload is invalid."
            )

        layer_identity_raw = source_payload.get(
            "article_identity"
        )

        if layer_identity_raw is None:

            identity_asserted = False
            identity_status = (
                "ARTICLE_IDENTITY_NOT_INDEPENDENTLY_ASSERTED"
            )

            preserved_identity = None

            unasserted_layer_names.append(
                layer_name
            )

        else:

            if not isinstance(
                layer_identity_raw,
                Mapping,
            ):
                raise ArticleSemanticConsolidationError(
                    layer_name
                    + " article_identity must be a mapping when present."
                )

            layer_identity = dict(
                layer_identity_raw
            )

            if layer_identity != canonical_identity:
                raise ArticleSemanticConsolidationError(
                    "Cross-layer article identity conflict detected in "
                    + layer_name
                    + "."
                )

            identity_asserted = True
            identity_status = (
                "ARTICLE_IDENTITY_MATCHED_CANONICAL"
            )

            preserved_identity = deepcopy(
                layer_identity
            )

            asserted_layer_names.append(
                layer_name
            )

        identity_records.append({
            "identity_record_id":
                "ASC_IDENTITY:"
                + str(
                    ordinal
                ),

            "ordinal":
                ordinal,

            "layer_name":
                layer_name,

            "phase":
                _ARTICLE_SEMANTIC_LAYER_PHASES[
                    layer_name
                ],

            "identity_asserted":
                identity_asserted,

            "identity_status":
                identity_status,

            "asserted_article_identity":
                preserved_identity,

            "canonical_identity_match":
                (
                    True
                    if identity_asserted
                    else None
                ),

            "identity_inferred":
                False,

            "identity_rewritten":
                False,

            "identity_synthesized":
                False,

            "semantic_identity_reasoning_performed":
                False,
        })

    if (
        "symbolic_neural_hybrid_intelligence"
        not in asserted_layer_names
    ):
        raise ArticleSemanticConsolidationError(
            "The frozen 4.6.15 layer must independently assert "
            "the canonical article_identity."
        )

    hybrid_identity_record = next(
        (
            record
            for record in identity_records
            if record[
                "layer_name"
            ]
            == "symbolic_neural_hybrid_intelligence"
        ),
        None,
    )

    if (
        not isinstance(
            hybrid_identity_record,
            Mapping,
        )
        or hybrid_identity_record.get(
            "canonical_identity_match"
        )
        is not True
    ):
        raise ArticleSemanticConsolidationError(
            "Frozen hybrid identity did not match its canonical anchor."
        )

    identity_alignment = {
        "alignment_status":
            "CROSS_LAYER_ARTICLE_IDENTITY_ALIGNED",

        "identity_authority":
            "FROZEN_4.6.15S_ARTICLE_IDENTITY",

        "identity_comparison_policy":
            "EXACT_STRUCTURAL_EQUALITY_FOR_ASSERTED_IDENTITIES",

        "missing_identity_policy":
            "PRESERVE_AS_NOT_INDEPENDENTLY_ASSERTED",

        "canonical_article_identity":
            deepcopy(
                canonical_identity
            ),

        "required_canonical_identity_fields": [
            "article_id",
            "workspace_id",
        ],

        "total_layer_count":
            len(
                expected_layer_order
            ),

        "asserted_identity_layer_count":
            len(
                asserted_layer_names
            ),

        "unasserted_identity_layer_count":
            len(
                unasserted_layer_names
            ),

        "asserted_identity_layers":
            deepcopy(
                asserted_layer_names
            ),

        "unasserted_identity_layers":
            deepcopy(
                unasserted_layer_names
            ),

        "identity_records":
            identity_records,

        "all_asserted_identities_match":
            True,

        "identity_conflict_detected":
            False,

        "identity_inference_performed":
            False,

        "identity_rewrite_performed":
            False,

        "missing_identity_synthesized":
            False,

        "semantic_identity_reasoning_performed":
            False,
    }

    return {
        "schema_version":
            "article_cross_layer_identity_alignment_v1",

        "article_semantic_consolidation_version":
            ARTICLE_SEMANTIC_CONSOLIDATION_VERSION,

        "phase":
            ARTICLE_SEMANTIC_CONSOLIDATION_PHASE,

        "patch":
            "4.6.16J",

        "status":
            "CROSS_LAYER_ARTICLE_IDENTITY_ALIGNED",

        "canonical_article_identity":
            deepcopy(
                canonical_identity
            ),

        "cross_layer_article_identity_alignment":
            identity_alignment,

        "foundational_semantic_intelligence":
            deepcopy(
                dict(
                    foundational
                )
            ),

        "structured_reasoning_intelligence":
            deepcopy(
                dict(
                    structured
                )
            ),

        "contextual_comparative_intelligence":
            deepcopy(
                dict(
                    contextual
                )
            ),

        "symbolic_neural_hybrid_intelligence":
            deepcopy(
                dict(
                    hybrid
                )
            ),

        "normalized_layers":
            deepcopy(
                dict(
                    normalized_layers
                )
            ),

        "normalized_group_index":
            deepcopy(
                dict(
                    normalized_group_index
                )
            ),

        "source_hybrid_integration_result":
            deepcopy(
                dict(
                    hybrid_integration_result
                )
            ),

        "processing_boundaries": {
            "intake_validation_preserved":
                True,

            "upstream_normalization_preserved":
                True,

            "foundational_assembly_preserved":
                True,

            "structured_reasoning_assembly_preserved":
                True,

            "contextual_comparative_assembly_preserved":
                True,

            "hybrid_integration_preserved":
                True,

            "article_identity_alignment_performed":
                True,

            "canonical_article_identity_preserved":
                True,

            "all_asserted_identities_match":
                True,

            "identity_conflict_rejection_enabled":
                True,

            "missing_identity_not_fabricated":
                True,

            "identity_inference_performed":
                False,

            "identity_rewrite_performed":
                False,

            "cross_layer_provenance_alignment_performed":
                False,

            "cross_layer_state_index_construction_performed":
                False,

            "conflict_uncertainty_abstention_preservation_performed":
                False,

            "article_semantic_consolidation_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "cross_layer_fact_synthesis_performed":
                False,

            "conflict_resolution_performed":
                False,

            "confidence_recalculation_performed":
                False,

            "uncertainty_strengthening_performed":
                False,

            "fuzzy_semantic_deduplication_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_validation_performed":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "cross_layer_provenance_alignment",
    }


# =====================================================================
# PATCH 4.6.16K ? Cross-Layer Provenance Alignment
# =====================================================================

def _collect_article_semantic_provenance_carriers_v1(
    value: Any,
) -> list[dict[str, Any]]:
    """
    Discover explicit provenance / lineage / grounding carriers already
    present in an upstream Semantic Intelligence result.

    Discovery is structural only.

    It does NOT:
    - infer provenance,
    - create provenance,
    - merge provenance records,
    - interpret provenance semantics,
    - repair lineage,
    - infer relationships between carriers.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import re

    provenance_key_pattern = re.compile(
        r"(?:"
        r"provenance|"
        r"lineage|"
        r"grounding|"
        r"source_span|"
        r"source_layer|"
        r"source_record|"
        r"evidence_source|"
        r"evidence_span|"
        r"evidence_ref|"
        r"trace|"
        r"explainability|"
        r"origin|"
        r"canonical_candidate_id|"
        r"redundan"
        r")",
        re.IGNORECASE,
    )

    carriers: list[dict[str, Any]] = []

    def walk(
        current: Any,
        path_parts: list[str],
    ) -> None:

        if isinstance(
            current,
            Mapping,
        ):

            for key, child in current.items():

                key_text = str(
                    key
                )

                child_path = (
                    path_parts
                    + [
                        key_text
                    ]
                )

                if provenance_key_pattern.search(
                    key_text
                ):

                    carriers.append({
                        "path":
                            ".".join(
                                child_path
                            ),

                        "key":
                            key_text,

                        "value":
                            deepcopy(
                                child
                            ),
                    })

                walk(
                    child,
                    child_path,
                )

        elif isinstance(
            current,
            (
                list,
                tuple,
            ),
        ):

            for index, child in enumerate(
                current
            ):

                walk(
                    child,
                    path_parts
                    + [
                        "["
                        + str(
                            index
                        )
                        + "]"
                    ],
                )

    walk(
        value,
        [],
    )

    return carriers


def align_cross_layer_provenance_v1(
    identity_alignment_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Align provenance structurally across all 15 Semantic Intelligence
    layers.

    K preserves heterogeneous provenance exactly as produced upstream.

    A layer may legitimately expose no explicit provenance-named carrier.
    Such a layer is recorded as having no independently exposed provenance
    carrier. K does not fabricate one.

    K builds:
    - one provenance record per Semantic Intelligence layer,
    - exact carrier paths and copied values,
    - a cross-layer carrier-key index,
    - explicit lists of layers with and without provenance carriers.

    K does NOT:
    - rewrite provenance,
    - merge provenance,
    - infer provenance,
    - synthesize missing provenance,
    - infer cross-layer lineage,
    - repair duplicate lineage,
    - reinterpret grounding,
    - perform new reasoning,
    - infer facts or relations,
    - resolve conflicts,
    - recalculate confidence,
    - strengthen uncertainty,
    - write Semantic Memory,
    - persist intelligence,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        identity_alignment_result,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "identity_alignment_result must be a mapping."
        )

    if (
        identity_alignment_result.get(
            "schema_version"
        )
        != "article_cross_layer_identity_alignment_v1"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16K requires "
            "article_cross_layer_identity_alignment_v1."
        )

    if (
        identity_alignment_result.get(
            "phase"
        )
        != "4.6.16"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16K requires Phase 4.6.16 input."
        )

    if (
        identity_alignment_result.get(
            "patch"
        )
        != "4.6.16J"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16K requires canonical 4.6.16J input."
        )

    if (
        identity_alignment_result.get(
            "status"
        )
        != "CROSS_LAYER_ARTICLE_IDENTITY_ALIGNED"
    ):
        raise ArticleSemanticConsolidationError(
            "Cross-layer article identity is not aligned."
        )

    if (
        identity_alignment_result.get(
            "next_stage"
        )
        != "cross_layer_provenance_alignment"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16J does not hand off to provenance alignment."
        )

    if (
        identity_alignment_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16K requires article-local transient intelligence."
        )

    boundaries = identity_alignment_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16J processing boundaries are missing."
        )

    for field in (
        "intake_validation_preserved",
        "upstream_normalization_preserved",
        "foundational_assembly_preserved",
        "structured_reasoning_assembly_preserved",
        "contextual_comparative_assembly_preserved",
        "hybrid_integration_preserved",
        "article_identity_alignment_performed",
        "canonical_article_identity_preserved",
        "all_asserted_identities_match",
        "identity_conflict_rejection_enabled",
        "missing_identity_not_fabricated",
    ):

        if (
            boundaries.get(
                field
            )
            is not True
        ):
            raise ArticleSemanticConsolidationError(
                "Required 4.6.16J boundary is not preserved: "
                + field
            )

    if (
        boundaries.get(
            "cross_layer_provenance_alignment_performed"
        )
        is not False
    ):
        raise ArticleSemanticConsolidationError(
            "Cross-layer provenance alignment was already performed."
        )

    canonical_identity = identity_alignment_result.get(
        "canonical_article_identity"
    )

    identity_alignment = identity_alignment_result.get(
        "cross_layer_article_identity_alignment"
    )

    normalized_layers = identity_alignment_result.get(
        "normalized_layers"
    )

    source_i_result = identity_alignment_result.get(
        "source_hybrid_integration_result"
    )

    if not isinstance(
        canonical_identity,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical article identity is missing."
        )

    if not isinstance(
        identity_alignment,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Cross-layer article identity alignment record is missing."
        )

    if (
        identity_alignment.get(
            "alignment_status"
        )
        != "CROSS_LAYER_ARTICLE_IDENTITY_ALIGNED"
    ):
        raise ArticleSemanticConsolidationError(
            "Article identity alignment state is invalid."
        )

    if (
        identity_alignment.get(
            "all_asserted_identities_match"
        )
        is not True
        or identity_alignment.get(
            "identity_conflict_detected"
        )
        is not False
    ):
        raise ArticleSemanticConsolidationError(
            "Provenance alignment requires conflict-free article identity."
        )

    if (
        identity_alignment.get(
            "total_layer_count"
        )
        != 15
    ):
        raise ArticleSemanticConsolidationError(
            "Identity alignment does not account for all 15 layers."
        )

    if len(
        identity_alignment.get(
            "identity_records",
            [],
        )
    ) != 15:
        raise ArticleSemanticConsolidationError(
            "Identity record accounting is incomplete."
        )

    if not isinstance(
        normalized_layers,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Normalized Semantic Intelligence layers are missing."
        )

    expected_order = list(
        _ARTICLE_SEMANTIC_LAYER_PHASES.keys()
    )

    if (
        list(
            normalized_layers.keys()
        )
        != expected_order
    ):
        raise ArticleSemanticConsolidationError(
            "Normalized Semantic Intelligence layer order is not canonical."
        )

    if len(
        normalized_layers
    ) != 15:
        raise ArticleSemanticConsolidationError(
            "Provenance alignment requires exactly 15 normalized layers."
        )

    # J embeds the complete I result.
    # Use it as a structural anti-drift witness.
    if not isinstance(
        source_i_result,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16J source I result is missing."
        )

    source_i_layers = source_i_result.get(
        "normalized_layers"
    )

    if not isinstance(
        source_i_layers,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Embedded I normalized layers are missing."
        )

    if (
        dict(
            normalized_layers
        )
        != dict(
            source_i_layers
        )
    ):
        raise ArticleSemanticConsolidationError(
            "Normalized source payloads drifted after identity alignment."
        )

    provenance_records = []
    carrier_key_index: dict[str, list[dict[str, Any]]] = {}

    layers_with_explicit_provenance = []
    layers_without_explicit_provenance = []

    total_carrier_count = 0

    for ordinal, layer_name in enumerate(
        expected_order,
        1,
    ):

        envelope = normalized_layers.get(
            layer_name
        )

        if not isinstance(
            envelope,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " normalized envelope is missing."
            )

        if (
            envelope.get(
                "layer_name"
            )
            != layer_name
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " normalized layer identity changed."
            )

        if (
            envelope.get(
                "normalization_status"
            )
            != "UPSTREAM_SEMANTIC_LAYER_NORMALIZED"
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " is not normalized."
            )

        source_payload = envelope.get(
            "source_payload"
        )

        if not isinstance(
            source_payload,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " source payload is invalid."
            )

        carriers = (
            _collect_article_semantic_provenance_carriers_v1(
                source_payload
            )
        )

        carrier_count = len(
            carriers
        )

        total_carrier_count += carrier_count

        if carrier_count:

            provenance_status = (
                "EXPLICIT_PROVENANCE_CARRIERS_PRESERVED"
            )

            layers_with_explicit_provenance.append(
                layer_name
            )

        else:

            provenance_status = (
                "NO_EXPLICIT_PROVENANCE_CARRIER_EXPOSED"
            )

            layers_without_explicit_provenance.append(
                layer_name
            )

        carrier_paths = []

        for carrier in carriers:

            carrier_path = carrier[
                "path"
            ]

            carrier_key = carrier[
                "key"
            ]

            carrier_paths.append(
                carrier_path
            )

            carrier_key_index.setdefault(
                carrier_key,
                [],
            ).append({
                "layer_name":
                    layer_name,

                "phase":
                    _ARTICLE_SEMANTIC_LAYER_PHASES[
                        layer_name
                    ],

                "path":
                    carrier_path,
            })

        provenance_records.append({
            "provenance_record_id":
                "ASC_PROVENANCE:"
                + str(
                    ordinal
                ),

            "ordinal":
                ordinal,

            "layer_name":
                layer_name,

            "phase":
                _ARTICLE_SEMANTIC_LAYER_PHASES[
                    layer_name
                ],

            "provenance_status":
                provenance_status,

            "explicit_provenance_carrier_count":
                carrier_count,

            "has_explicit_provenance_carriers":
                bool(
                    carrier_count
                ),

            "carrier_paths":
                carrier_paths,

            "carriers":
                deepcopy(
                    carriers
                ),

            "source_payload_preserved":
                True,

            "provenance_values_preserved":
                True,

            "provenance_rewritten":
                False,

            "provenance_merged":
                False,

            "provenance_inferred":
                False,

            "missing_provenance_synthesized":
                False,

            "cross_layer_lineage_inferred":
                False,
        })

    # Deterministic index ordering.
    deterministic_key_index = {}

    for key in sorted(
        carrier_key_index.keys()
    ):

        deterministic_key_index[
            key
        ] = sorted(
            carrier_key_index[
                key
            ],
            key=lambda item: (
                expected_order.index(
                    item[
                        "layer_name"
                    ]
                ),
                item[
                    "path"
                ],
            ),
        )

    provenance_alignment = {
        "alignment_status":
            "CROSS_LAYER_PROVENANCE_ALIGNED",

        "alignment_mode":
            "STRUCTURAL_PRESERVATION_AND_INDEXING",

        "canonical_article_identity":
            deepcopy(
                dict(
                    canonical_identity
                )
            ),

        "total_layer_count":
            15,

        "total_explicit_provenance_carrier_count":
            total_carrier_count,

        "layers_with_explicit_provenance_count":
            len(
                layers_with_explicit_provenance
            ),

        "layers_without_explicit_provenance_count":
            len(
                layers_without_explicit_provenance
            ),

        "layers_with_explicit_provenance":
            deepcopy(
                layers_with_explicit_provenance
            ),

        "layers_without_explicit_provenance":
            deepcopy(
                layers_without_explicit_provenance
            ),

        "provenance_records":
            provenance_records,

        "carrier_key_index":
            deterministic_key_index,

        "source_payloads_preserved":
            True,

        "existing_provenance_preserved":
            True,

        "missing_provenance_allowed":
            True,

        "missing_provenance_synthesized":
            False,

        "provenance_rewrite_performed":
            False,

        "provenance_merge_performed":
            False,

        "provenance_inference_performed":
            False,

        "cross_layer_lineage_inference_performed":
            False,

        "grounding_reinterpretation_performed":
            False,

        "redundancy_lineage_repair_performed":
            False,
    }

    return {
        "schema_version":
            "article_cross_layer_provenance_alignment_v1",

        "article_semantic_consolidation_version":
            ARTICLE_SEMANTIC_CONSOLIDATION_VERSION,

        "phase":
            ARTICLE_SEMANTIC_CONSOLIDATION_PHASE,

        "patch":
            "4.6.16K",

        "status":
            "CROSS_LAYER_PROVENANCE_ALIGNED",

        "canonical_article_identity":
            deepcopy(
                dict(
                    canonical_identity
                )
            ),

        "cross_layer_article_identity_alignment":
            deepcopy(
                dict(
                    identity_alignment
                )
            ),

        "cross_layer_provenance_alignment":
            provenance_alignment,

        "foundational_semantic_intelligence":
            deepcopy(
                dict(
                    identity_alignment_result[
                        "foundational_semantic_intelligence"
                    ]
                )
            ),

        "structured_reasoning_intelligence":
            deepcopy(
                dict(
                    identity_alignment_result[
                        "structured_reasoning_intelligence"
                    ]
                )
            ),

        "contextual_comparative_intelligence":
            deepcopy(
                dict(
                    identity_alignment_result[
                        "contextual_comparative_intelligence"
                    ]
                )
            ),

        "symbolic_neural_hybrid_intelligence":
            deepcopy(
                dict(
                    identity_alignment_result[
                        "symbolic_neural_hybrid_intelligence"
                    ]
                )
            ),

        "normalized_layers":
            deepcopy(
                dict(
                    normalized_layers
                )
            ),

        "normalized_group_index":
            deepcopy(
                dict(
                    identity_alignment_result[
                        "normalized_group_index"
                    ]
                )
            ),

        "source_identity_alignment_result":
            deepcopy(
                dict(
                    identity_alignment_result
                )
            ),

        "processing_boundaries": {
            "intake_validation_preserved":
                True,

            "upstream_normalization_preserved":
                True,

            "foundational_assembly_preserved":
                True,

            "structured_reasoning_assembly_preserved":
                True,

            "contextual_comparative_assembly_preserved":
                True,

            "hybrid_integration_preserved":
                True,

            "article_identity_alignment_preserved":
                True,

            "cross_layer_provenance_alignment_performed":
                True,

            "all_15_layers_provenance_accounted_for":
                True,

            "source_payloads_preserved":
                True,

            "existing_provenance_preserved":
                True,

            "missing_provenance_allowed":
                True,

            "missing_provenance_not_fabricated":
                True,

            "provenance_rewrite_performed":
                False,

            "provenance_merge_performed":
                False,

            "provenance_inference_performed":
                False,

            "cross_layer_lineage_inference_performed":
                False,

            "grounding_reinterpretation_performed":
                False,

            "redundancy_lineage_repair_performed":
                False,

            "cross_layer_state_index_construction_performed":
                False,

            "conflict_uncertainty_abstention_preservation_performed":
                False,

            "article_semantic_consolidation_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "cross_layer_fact_synthesis_performed":
                False,

            "conflict_resolution_performed":
                False,

            "confidence_recalculation_performed":
                False,

            "uncertainty_strengthening_performed":
                False,

            "fuzzy_semantic_deduplication_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_validation_performed":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "cross_layer_state_index_construction",
    }


# =====================================================================
# PATCH 4.6.16L ? Cross-Layer State / Index Construction
# =====================================================================

def _collect_article_semantic_state_carriers_v1(
    value: Any,
) -> list[dict[str, Any]]:
    """
    Discover already-existing structural state/index carriers.

    Discovery is key-based and preservation-only.

    This helper does NOT:
    - calculate semantic counts,
    - rebuild upstream indexes,
    - classify semantic state,
    - reinterpret confidence,
    - infer conflict,
    - infer uncertainty,
    - infer abstention,
    - resolve inconsistencies,
    - create new Semantic Intelligence.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import re

    state_key_pattern = re.compile(
        r"(?:"
        r"status|"
        r"state|"
        r"index|"
        r"count|"
        r"summary|"
        r"class|"
        r"type|"
        r"ready|"
        r"complete|"
        r"certified"
        r")",
        re.IGNORECASE,
    )

    carriers: list[dict[str, Any]] = []

    def walk(
        current: Any,
        path_parts: list[str],
    ) -> None:

        if isinstance(
            current,
            Mapping,
        ):

            for key, child in current.items():

                key_text = str(
                    key
                )

                child_path = (
                    path_parts
                    + [
                        key_text
                    ]
                )

                if state_key_pattern.search(
                    key_text
                ):

                    carriers.append({
                        "path":
                            ".".join(
                                child_path
                            ),

                        "key":
                            key_text,

                        "value":
                            deepcopy(
                                child
                            ),
                    })

                walk(
                    child,
                    child_path,
                )

        elif isinstance(
            current,
            (
                list,
                tuple,
            ),
        ):

            for index, child in enumerate(
                current
            ):

                walk(
                    child,
                    path_parts
                    + [
                        "["
                        + str(
                            index
                        )
                        + "]"
                    ],
                )

    walk(
        value,
        [],
    )

    return carriers


def construct_cross_layer_state_indexes_v1(
    provenance_alignment_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Construct deterministic structural state/index views across all
    15 Semantic Intelligence layers.

    L indexes only state already supplied by upstream layers.

    It does NOT:
    - recalculate upstream semantic counts,
    - rebuild an upstream state index,
    - recompute certification state,
    - reinterpret confidence classes,
    - infer or resolve conflicts,
    - infer or strengthen uncertainty,
    - infer or alter abstention,
    - perform cross-layer semantic reasoning,
    - synthesize facts,
    - rewrite source payloads,
    - write Semantic Memory,
    - persist intelligence,
    - make linking decisions.

    Conflict / uncertainty / abstention preservation remains the
    responsibility of 4.6.16M.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        provenance_alignment_result,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "provenance_alignment_result must be a mapping."
        )

    if (
        provenance_alignment_result.get(
            "schema_version"
        )
        != "article_cross_layer_provenance_alignment_v1"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16L requires "
            "article_cross_layer_provenance_alignment_v1."
        )

    if (
        provenance_alignment_result.get(
            "phase"
        )
        != "4.6.16"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16L requires Phase 4.6.16 input."
        )

    if (
        provenance_alignment_result.get(
            "patch"
        )
        != "4.6.16K"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16L requires canonical 4.6.16K input."
        )

    if (
        provenance_alignment_result.get(
            "status"
        )
        != "CROSS_LAYER_PROVENANCE_ALIGNED"
    ):
        raise ArticleSemanticConsolidationError(
            "Cross-layer provenance is not aligned."
        )

    if (
        provenance_alignment_result.get(
            "next_stage"
        )
        != "cross_layer_state_index_construction"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16K does not hand off to state/index construction."
        )

    if (
        provenance_alignment_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16L requires article-local transient intelligence."
        )

    boundaries = provenance_alignment_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16K processing boundaries are missing."
        )

    for field in (
        "intake_validation_preserved",
        "upstream_normalization_preserved",
        "foundational_assembly_preserved",
        "structured_reasoning_assembly_preserved",
        "contextual_comparative_assembly_preserved",
        "hybrid_integration_preserved",
        "article_identity_alignment_preserved",
        "cross_layer_provenance_alignment_performed",
        "all_15_layers_provenance_accounted_for",
        "source_payloads_preserved",
        "existing_provenance_preserved",
        "missing_provenance_allowed",
        "missing_provenance_not_fabricated",
    ):

        if (
            boundaries.get(
                field
            )
            is not True
        ):
            raise ArticleSemanticConsolidationError(
                "Required 4.6.16K boundary is not preserved: "
                + field
            )

    if (
        boundaries.get(
            "cross_layer_state_index_construction_performed"
        )
        is not False
    ):
        raise ArticleSemanticConsolidationError(
            "Cross-layer state/index construction was already performed."
        )

    canonical_identity = provenance_alignment_result.get(
        "canonical_article_identity"
    )

    identity_alignment = provenance_alignment_result.get(
        "cross_layer_article_identity_alignment"
    )

    provenance_alignment = provenance_alignment_result.get(
        "cross_layer_provenance_alignment"
    )

    normalized_layers = provenance_alignment_result.get(
        "normalized_layers"
    )

    normalized_group_index = provenance_alignment_result.get(
        "normalized_group_index"
    )

    source_j_result = provenance_alignment_result.get(
        "source_identity_alignment_result"
    )

    if not isinstance(
        canonical_identity,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical article identity is missing."
        )

    if not isinstance(
        identity_alignment,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Cross-layer identity alignment is missing."
        )

    if (
        identity_alignment.get(
            "alignment_status"
        )
        != "CROSS_LAYER_ARTICLE_IDENTITY_ALIGNED"
    ):
        raise ArticleSemanticConsolidationError(
            "Identity alignment state is invalid."
        )

    if not isinstance(
        provenance_alignment,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Cross-layer provenance alignment is missing."
        )

    if (
        provenance_alignment.get(
            "alignment_status"
        )
        != "CROSS_LAYER_PROVENANCE_ALIGNED"
    ):
        raise ArticleSemanticConsolidationError(
            "Provenance alignment state is invalid."
        )

    if (
        provenance_alignment.get(
            "total_layer_count"
        )
        != 15
    ):
        raise ArticleSemanticConsolidationError(
            "Provenance alignment does not account for all 15 layers."
        )

    if len(
        provenance_alignment.get(
            "provenance_records",
            [],
        )
    ) != 15:
        raise ArticleSemanticConsolidationError(
            "Provenance record accounting is incomplete."
        )

    if not isinstance(
        normalized_layers,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Normalized Semantic Intelligence layers are missing."
        )

    if not isinstance(
        normalized_group_index,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Normalized group index is missing."
        )

    expected_order = list(
        _ARTICLE_SEMANTIC_LAYER_PHASES.keys()
    )

    if (
        list(
            normalized_layers.keys()
        )
        != expected_order
    ):
        raise ArticleSemanticConsolidationError(
            "Normalized Semantic Intelligence layer order is not canonical."
        )

    if len(
        normalized_layers
    ) != 15:
        raise ArticleSemanticConsolidationError(
            "State/index construction requires exactly 15 layers."
        )

    # K embeds J. J embeds the canonical normalized payloads.
    # This prevents post-K source mutation from silently entering L.
    if not isinstance(
        source_j_result,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16K source J result is missing."
        )

    source_j_layers = source_j_result.get(
        "normalized_layers"
    )

    if not isinstance(
        source_j_layers,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Embedded J normalized layers are missing."
        )

    if (
        dict(
            normalized_layers
        )
        != dict(
            source_j_layers
        )
    ):
        raise ArticleSemanticConsolidationError(
            "Normalized source payloads drifted after provenance alignment."
        )

    layer_state_records = []

    layer_contract_index = {}
    source_status_index: dict[str, list[str]] = {}
    state_carrier_key_index: dict[str, list[dict[str, Any]]] = {}
    state_carrier_path_index = {}

    total_structural_state_carriers = 0

    for ordinal, layer_name in enumerate(
        expected_order,
        1,
    ):

        envelope = normalized_layers.get(
            layer_name
        )

        if not isinstance(
            envelope,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " normalized envelope is missing."
            )

        if (
            envelope.get(
                "layer_name"
            )
            != layer_name
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " normalized layer identity changed."
            )

        if (
            envelope.get(
                "normalization_status"
            )
            != "UPSTREAM_SEMANTIC_LAYER_NORMALIZED"
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " is not normalized."
            )

        source_payload = envelope.get(
            "source_payload"
        )

        if not isinstance(
            source_payload,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " source payload is invalid."
            )

        contract = (
            _ARTICLE_SEMANTIC_UPSTREAM_RESULT_CONTRACTS[
                layer_name
            ]
        )

        expected_authority = (
            _ARTICLE_SEMANTIC_INPUT_AUTHORITY[
                layer_name
            ]
        )

        if (
            envelope.get(
                "phase"
            )
            != contract[
                "phase"
            ]
            or envelope.get(
                "schema_version"
            )
            != contract[
                "schema_version"
            ]
            or envelope.get(
                "patch"
            )
            != contract[
                "patch"
            ]
            or envelope.get(
                "status"
            )
            != contract[
                "status"
            ]
            or envelope.get(
                "source_next_stage"
            )
            != contract[
                "next_stage"
            ]
            or envelope.get(
                "input_authority"
            )
            != expected_authority
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " normalized source contract drifted."
            )

        carriers = (
            _collect_article_semantic_state_carriers_v1(
                source_payload
            )
        )

        total_structural_state_carriers += len(
            carriers
        )

        carrier_paths = [
            carrier[
                "path"
            ]
            for carrier in carriers
        ]

        state_carrier_path_index[
            layer_name
        ] = deepcopy(
            carrier_paths
        )

        for carrier in carriers:

            carrier_key = carrier[
                "key"
            ]

            state_carrier_key_index.setdefault(
                carrier_key,
                [],
            ).append({
                "layer_name":
                    layer_name,

                "phase":
                    contract[
                        "phase"
                    ],

                "path":
                    carrier[
                        "path"
                    ],
            })

        source_status = source_payload.get(
            "status"
        )

        if not isinstance(
            source_status,
            str,
        ) or not source_status:
            raise ArticleSemanticConsolidationError(
                layer_name
                + " source status is missing."
            )

        source_status_index.setdefault(
            source_status,
            [],
        ).append(
            layer_name
        )

        layer_contract_index[
            layer_name
        ] = {
            "ordinal":
                ordinal,

            "phase":
                contract[
                    "phase"
                ],

            "schema_version":
                contract[
                    "schema_version"
                ],

            "patch":
                contract[
                    "patch"
                ],

            "status":
                contract[
                    "status"
                ],

            "next_stage":
                contract[
                    "next_stage"
                ],

            "group_name":
                envelope.get(
                    "group_name"
                ),

            "input_authority":
                expected_authority,
        }

        layer_state_records.append({
            "state_record_id":
                "ASC_STATE:"
                + str(
                    ordinal
                ),

            "ordinal":
                ordinal,

            "layer_name":
                layer_name,

            "phase":
                contract[
                    "phase"
                ],

            "source_status":
                source_status,

            "structural_state_carrier_count":
                len(
                    carriers
                ),

            "state_carrier_paths":
                deepcopy(
                    carrier_paths
                ),

            "state_carriers":
                deepcopy(
                    carriers
                ),

            "source_payload_preserved":
                True,

            "source_state_values_preserved":
                True,

            "semantic_count_recalculation_performed":
                False,

            "upstream_index_rebuild_performed":
                False,

            "state_reclassification_performed":
                False,

            "confidence_reinterpretation_performed":
                False,

            "conflict_preservation_performed":
                False,

            "uncertainty_preservation_performed":
                False,

            "abstention_preservation_performed":
                False,

            "new_reasoning_performed":
                False,
        })

    deterministic_key_index = {}

    for key in sorted(
        state_carrier_key_index.keys()
    ):

        deterministic_key_index[
            key
        ] = sorted(
            state_carrier_key_index[
                key
            ],
            key=lambda item: (
                expected_order.index(
                    item[
                        "layer_name"
                    ]
                ),
                item[
                    "path"
                ],
            ),
        )

    deterministic_status_index = {}

    for status in sorted(
        source_status_index.keys()
    ):

        deterministic_status_index[
            status
        ] = sorted(
            source_status_index[
                status
            ],
            key=lambda layer_name: (
                expected_order.index(
                    layer_name
                )
            ),
        )

    cross_layer_state_indexes = {
        "construction_status":
            "CROSS_LAYER_STATE_INDEXES_CONSTRUCTED",

        "construction_mode":
            "STRUCTURAL_INDEXING_OF_EXISTING_UPSTREAM_STATE",

        "canonical_article_identity":
            deepcopy(
                dict(
                    canonical_identity
                )
            ),

        "canonical_layer_order":
            deepcopy(
                expected_order
            ),

        "total_layer_count":
            15,

        "layer_state_record_count":
            len(
                layer_state_records
            ),

        "total_structural_state_carrier_count":
            total_structural_state_carriers,

        "layer_contract_index":
            layer_contract_index,

        "source_status_index":
            deterministic_status_index,

        "state_carrier_key_index":
            deterministic_key_index,

        "state_carrier_path_index":
            state_carrier_path_index,

        "layer_state_records":
            layer_state_records,

        "source_payloads_preserved":
            True,

        "source_state_values_preserved":
            True,

        "semantic_count_recalculation_performed":
            False,

        "upstream_index_rebuild_performed":
            False,

        "state_reclassification_performed":
            False,

        "confidence_reinterpretation_performed":
            False,

        "conflict_preservation_performed":
            False,

        "uncertainty_preservation_performed":
            False,

        "abstention_preservation_performed":
            False,

        "new_reasoning_performed":
            False,

        "new_fact_inference_performed":
            False,

        "new_relation_inference_performed":
            False,
    }

    return {
        "schema_version":
            "article_cross_layer_state_indexes_v1",

        "article_semantic_consolidation_version":
            ARTICLE_SEMANTIC_CONSOLIDATION_VERSION,

        "phase":
            ARTICLE_SEMANTIC_CONSOLIDATION_PHASE,

        "patch":
            "4.6.16L",

        "status":
            "CROSS_LAYER_STATE_INDEXES_CONSTRUCTED",

        "canonical_article_identity":
            deepcopy(
                dict(
                    canonical_identity
                )
            ),

        "cross_layer_article_identity_alignment":
            deepcopy(
                dict(
                    identity_alignment
                )
            ),

        "cross_layer_provenance_alignment":
            deepcopy(
                dict(
                    provenance_alignment
                )
            ),

        "cross_layer_state_indexes":
            cross_layer_state_indexes,

        "foundational_semantic_intelligence":
            deepcopy(
                dict(
                    provenance_alignment_result[
                        "foundational_semantic_intelligence"
                    ]
                )
            ),

        "structured_reasoning_intelligence":
            deepcopy(
                dict(
                    provenance_alignment_result[
                        "structured_reasoning_intelligence"
                    ]
                )
            ),

        "contextual_comparative_intelligence":
            deepcopy(
                dict(
                    provenance_alignment_result[
                        "contextual_comparative_intelligence"
                    ]
                )
            ),

        "symbolic_neural_hybrid_intelligence":
            deepcopy(
                dict(
                    provenance_alignment_result[
                        "symbolic_neural_hybrid_intelligence"
                    ]
                )
            ),

        "normalized_layers":
            deepcopy(
                dict(
                    normalized_layers
                )
            ),

        "normalized_group_index":
            deepcopy(
                dict(
                    normalized_group_index
                )
            ),

        "source_provenance_alignment_result":
            deepcopy(
                dict(
                    provenance_alignment_result
                )
            ),

        "processing_boundaries": {
            "intake_validation_preserved":
                True,

            "upstream_normalization_preserved":
                True,

            "foundational_assembly_preserved":
                True,

            "structured_reasoning_assembly_preserved":
                True,

            "contextual_comparative_assembly_preserved":
                True,

            "hybrid_integration_preserved":
                True,

            "article_identity_alignment_preserved":
                True,

            "cross_layer_provenance_alignment_preserved":
                True,

            "cross_layer_state_index_construction_performed":
                True,

            "all_15_layers_state_indexed":
                True,

            "source_payloads_preserved":
                True,

            "source_state_values_preserved":
                True,

            "semantic_count_recalculation_performed":
                False,

            "upstream_index_rebuild_performed":
                False,

            "state_reclassification_performed":
                False,

            "confidence_reinterpretation_performed":
                False,

            "conflict_uncertainty_abstention_preservation_performed":
                False,

            "article_semantic_consolidation_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "cross_layer_fact_synthesis_performed":
                False,

            "conflict_resolution_performed":
                False,

            "confidence_recalculation_performed":
                False,

            "uncertainty_strengthening_performed":
                False,

            "fuzzy_semantic_deduplication_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_validation_performed":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "conflict_uncertainty_abstention_preservation",
    }


# =====================================================================
# PATCH 4.6.16M ? Conflict, Uncertainty & Abstention Preservation
# =====================================================================

def _collect_article_semantic_preservation_carriers_v1(
    value: Any,
) -> list[dict[str, Any]]:
    """
    Discover already-existing conflict, contradiction, uncertainty,
    ambiguity, unresolved, abstention and confidence carriers.

    Discovery is structural and preservation-only.

    It does NOT:
    - infer conflict,
    - adjudicate contradiction,
    - infer uncertainty,
    - strengthen uncertainty,
    - calculate confidence,
    - infer abstention,
    - resolve unresolved state,
    - create new semantic state.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import re

    preservation_key_pattern = re.compile(
        r"(?:"
        r"conflict|"
        r"contradict|"
        r"uncertain|"
        r"uncertainty|"
        r"abstain|"
        r"abstention|"
        r"unresolved|"
        r"confidence|"
        r"hedge|"
        r"ambiguous|"
        r"ambiguity"
        r")",
        re.IGNORECASE,
    )

    carriers: list[dict[str, Any]] = []

    def classify_key(
        key_text: str,
    ) -> list[str]:

        lower_key = key_text.lower()

        categories = []

        if (
            "conflict" in lower_key
            or "contradict" in lower_key
        ):
            categories.append(
                "CONFLICT_OR_CONTRADICTION"
            )

        if (
            "uncertain" in lower_key
            or "uncertainty" in lower_key
            or "hedge" in lower_key
            or "ambiguous" in lower_key
            or "ambiguity" in lower_key
        ):
            categories.append(
                "UNCERTAINTY_OR_AMBIGUITY"
            )

        if (
            "abstain" in lower_key
            or "abstention" in lower_key
        ):
            categories.append(
                "ABSTENTION"
            )

        if "unresolved" in lower_key:
            categories.append(
                "UNRESOLVED"
            )

        if "confidence" in lower_key:
            categories.append(
                "CONFIDENCE"
            )

        return categories

    def walk(
        current: Any,
        path_parts: list[str],
    ) -> None:

        if isinstance(
            current,
            Mapping,
        ):

            for key, child in current.items():

                key_text = str(
                    key
                )

                child_path = (
                    path_parts
                    + [
                        key_text
                    ]
                )

                if preservation_key_pattern.search(
                    key_text
                ):

                    carriers.append({
                        "path":
                            ".".join(
                                child_path
                            ),

                        "key":
                            key_text,

                        "categories":
                            classify_key(
                                key_text
                            ),

                        "value":
                            deepcopy(
                                child
                            ),
                    })

                walk(
                    child,
                    child_path,
                )

        elif isinstance(
            current,
            (
                list,
                tuple,
            ),
        ):

            for index, child in enumerate(
                current
            ):

                walk(
                    child,
                    path_parts
                    + [
                        "["
                        + str(
                            index
                        )
                        + "]"
                    ],
                )

    walk(
        value,
        [],
    )

    return carriers


def preserve_conflict_uncertainty_abstention_v1(
    state_index_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Preserve already-certified conflict, uncertainty, ambiguity,
    unresolved, abstention and confidence state across the article.

    Authority boundaries:
    - Earlier layers retain their local signals exactly.
    - 4.6.14 remains authoritative for certified Uncertainty Intelligence.
    - 4.6.15 remains authoritative for governed hybrid conflict,
      unresolved state, abstention state and hybrid confidence state.

    M does NOT:
    - adjudicate contradiction,
    - resolve or re-resolve conflict,
    - transform ambiguity into certainty,
    - strengthen or weaken uncertainty,
    - calculate unified Semantic Confidence,
    - recalculate hybrid confidence,
    - invent unresolved state,
    - create an abstention decision,
    - remove an abstention decision,
    - perform new semantic reasoning,
    - infer facts or relations,
    - write Semantic Memory,
    - persist intelligence,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        state_index_result,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "state_index_result must be a mapping."
        )

    if (
        state_index_result.get(
            "schema_version"
        )
        != "article_cross_layer_state_indexes_v1"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16M requires article_cross_layer_state_indexes_v1."
        )

    if (
        state_index_result.get(
            "phase"
        )
        != "4.6.16"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16M requires Phase 4.6.16 input."
        )

    if (
        state_index_result.get(
            "patch"
        )
        != "4.6.16L"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16M requires canonical 4.6.16L input."
        )

    if (
        state_index_result.get(
            "status"
        )
        != "CROSS_LAYER_STATE_INDEXES_CONSTRUCTED"
    ):
        raise ArticleSemanticConsolidationError(
            "Cross-layer state indexes are not constructed."
        )

    if (
        state_index_result.get(
            "next_stage"
        )
        != "conflict_uncertainty_abstention_preservation"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16L does not hand off to preservation stage M."
        )

    if (
        state_index_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16M requires article-local transient intelligence."
        )

    boundaries = state_index_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16L processing boundaries are missing."
        )

    for field in (
        "intake_validation_preserved",
        "upstream_normalization_preserved",
        "foundational_assembly_preserved",
        "structured_reasoning_assembly_preserved",
        "contextual_comparative_assembly_preserved",
        "hybrid_integration_preserved",
        "article_identity_alignment_preserved",
        "cross_layer_provenance_alignment_preserved",
        "cross_layer_state_index_construction_performed",
        "all_15_layers_state_indexed",
        "source_payloads_preserved",
        "source_state_values_preserved",
    ):

        if (
            boundaries.get(
                field
            )
            is not True
        ):
            raise ArticleSemanticConsolidationError(
                "Required 4.6.16L boundary is not preserved: "
                + field
            )

    if (
        boundaries.get(
            "conflict_uncertainty_abstention_preservation_performed"
        )
        is not False
    ):
        raise ArticleSemanticConsolidationError(
            "Conflict/uncertainty/abstention preservation "
            "was already performed."
        )

    canonical_identity = state_index_result.get(
        "canonical_article_identity"
    )

    identity_alignment = state_index_result.get(
        "cross_layer_article_identity_alignment"
    )

    provenance_alignment = state_index_result.get(
        "cross_layer_provenance_alignment"
    )

    state_indexes = state_index_result.get(
        "cross_layer_state_indexes"
    )

    normalized_layers = state_index_result.get(
        "normalized_layers"
    )

    normalized_group_index = state_index_result.get(
        "normalized_group_index"
    )

    source_k_result = state_index_result.get(
        "source_provenance_alignment_result"
    )

    for name, value in (
        (
            "canonical_article_identity",
            canonical_identity,
        ),
        (
            "cross_layer_article_identity_alignment",
            identity_alignment,
        ),
        (
            "cross_layer_provenance_alignment",
            provenance_alignment,
        ),
        (
            "cross_layer_state_indexes",
            state_indexes,
        ),
        (
            "normalized_layers",
            normalized_layers,
        ),
        (
            "normalized_group_index",
            normalized_group_index,
        ),
        (
            "source_provenance_alignment_result",
            source_k_result,
        ),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                name
                + " is missing or invalid."
            )

    if (
        state_indexes.get(
            "construction_status"
        )
        != "CROSS_LAYER_STATE_INDEXES_CONSTRUCTED"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16L state-index construction status is invalid."
        )

    if (
        state_indexes.get(
            "total_layer_count"
        )
        != 15
        or state_indexes.get(
            "layer_state_record_count"
        )
        != 15
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16L does not account for all 15 layers."
        )

    expected_order = list(
        _ARTICLE_SEMANTIC_LAYER_PHASES.keys()
    )

    if (
        state_indexes.get(
            "canonical_layer_order"
        )
        != expected_order
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16L canonical layer order is invalid."
        )

    if (
        list(
            normalized_layers.keys()
        )
        != expected_order
    ):
        raise ArticleSemanticConsolidationError(
            "Normalized Semantic Intelligence layer order is not canonical."
        )

    source_k_layers = source_k_result.get(
        "normalized_layers"
    )

    if not isinstance(
        source_k_layers,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Embedded K normalized layers are missing."
        )

    if (
        dict(
            normalized_layers
        )
        != dict(
            source_k_layers
        )
    ):
        raise ArticleSemanticConsolidationError(
            "Normalized source payloads drifted after state indexing."
        )

    # Verify L's structural records still match the exact source payloads.
    l_records = state_indexes.get(
        "layer_state_records"
    )

    if not isinstance(
        l_records,
        list,
    ) or len(
        l_records
    ) != 15:
        raise ArticleSemanticConsolidationError(
            "4.6.16L state records are incomplete."
        )

    l_record_by_layer = {}

    for record in l_records:

        if not isinstance(
            record,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                "Every 4.6.16L state record must be a mapping."
            )

        layer_name = record.get(
            "layer_name"
        )

        if layer_name in l_record_by_layer:
            raise ArticleSemanticConsolidationError(
                "Duplicate 4.6.16L state record."
            )

        l_record_by_layer[
            layer_name
        ] = record

    if set(
        l_record_by_layer.keys()
    ) != set(
        expected_order
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16L state-record layer accounting is invalid."
        )

    # -----------------------------------------------------------------
    # 4.6.14 authoritative uncertainty source
    # -----------------------------------------------------------------

    uncertainty_envelope = normalized_layers.get(
        "uncertainty_intelligence"
    )

    if not isinstance(
        uncertainty_envelope,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.14 normalized uncertainty envelope is missing."
        )

    uncertainty_payload = uncertainty_envelope.get(
        "source_payload"
    )

    if not isinstance(
        uncertainty_payload,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.14 uncertainty payload is invalid."
        )

    if (
        uncertainty_payload.get(
            "status"
        )
        != "UNCERTAINTY_INTELLIGENCE_CERTIFIED"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.14 uncertainty source is not certified."
        )

    uncertainty_summary = uncertainty_payload.get(
        "final_uncertainty_summary"
    )

    if (
        uncertainty_summary is not None
        and not isinstance(
            uncertainty_summary,
            Mapping,
        )
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.14 final_uncertainty_summary must be a mapping "
            "when present."
        )

    if (
        isinstance(
            uncertainty_summary,
            Mapping,
        )
        and uncertainty_summary.get(
            "unified_semantic_confidence_calculated"
        )
        is True
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.14 must not calculate unified Semantic Confidence."
        )

    # -----------------------------------------------------------------
    # 4.6.15 authoritative hybrid governance source
    # -----------------------------------------------------------------

    hybrid_envelope = normalized_layers.get(
        "symbolic_neural_hybrid_intelligence"
    )

    if not isinstance(
        hybrid_envelope,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 normalized hybrid envelope is missing."
        )

    hybrid_payload = hybrid_envelope.get(
        "source_payload"
    )

    if not isinstance(
        hybrid_payload,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 hybrid payload is invalid."
        )

    if (
        hybrid_payload.get(
            "status"
        )
        != "SYMBOLIC_NEURAL_HYBRID_INTELLIGENCE_RESULT_READY"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 hybrid result is not ready."
        )

    hybrid_final = hybrid_payload.get(
        "final_symbolic_neural_hybrid_intelligence"
    )

    if not isinstance(
        hybrid_final,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 final hybrid state is missing."
        )

    if (
        hybrid_final.get(
            "final_status"
        )
        != "SYMBOLIC_NEURAL_HYBRID_INTELLIGENCE_READY"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 final hybrid state is not ready."
        )

    conflict_ids = hybrid_final.get(
        "governed_conflict_candidate_ids",
        [],
    )

    unresolved_ids = hybrid_final.get(
        "unresolved_candidate_ids",
        [],
    )

    abstention_ids = hybrid_final.get(
        "abstention_candidate_ids",
        [],
    )

    for field_name, value in (
        (
            "governed_conflict_candidate_ids",
            conflict_ids,
        ),
        (
            "unresolved_candidate_ids",
            unresolved_ids,
        ),
        (
            "abstention_candidate_ids",
            abstention_ids,
        ),
    ):

        if (
            not isinstance(
                value,
                list,
            )
            or not all(
                isinstance(
                    item,
                    str,
                )
                and item
                for item in value
            )
            or len(
                value
            )
            != len(
                set(
                    value
                )
            )
        ):
            raise ArticleSemanticConsolidationError(
                field_name
                + " must be a unique string list."
            )

    # Frozen 4.6.15 invariant:
    # unresolved candidates and abstention candidates are identical.
    if abstention_ids != unresolved_ids:
        raise ArticleSemanticConsolidationError(
            "4.6.15 abstention candidate IDs must exactly preserve "
            "the unresolved candidate IDs."
        )

    expected_conflict_flag = bool(
        conflict_ids
    )

    expected_unresolved_flag = bool(
        unresolved_ids
    )

    expected_abstention_flag = bool(
        abstention_ids
    )

    if (
        hybrid_final.get(
            "article_has_symbolically_governed_conflict"
        )
        is not expected_conflict_flag
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 governed-conflict article flag is inconsistent."
        )

    if (
        hybrid_final.get(
            "article_has_unresolved_hybrid_evidence"
        )
        is not expected_unresolved_flag
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 unresolved-evidence article flag is inconsistent."
        )

    if (
        hybrid_final.get(
            "article_requires_hybrid_abstention"
        )
        is not expected_abstention_flag
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 abstention article flag is inconsistent."
        )

    hybrid_boundaries = hybrid_payload.get(
        "processing_boundaries"
    )

    if not isinstance(
        hybrid_boundaries,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 processing boundaries are missing."
        )

    if (
        hybrid_boundaries.get(
            "conflict_resolution_reperformed"
        )
        is not False
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 conflict must not have been re-resolved."
        )

    if (
        hybrid_boundaries.get(
            "confidence_recalculation_performed"
        )
        is not False
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 confidence must not have been recalculated."
        )

    hybrid_summary = hybrid_payload.get(
        "final_result_summary"
    )

    if (
        hybrid_summary is not None
        and not isinstance(
            hybrid_summary,
            Mapping,
        )
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.15 final_result_summary must be a mapping when present."
        )

    if isinstance(
        hybrid_summary,
        Mapping,
    ):

        count_checks = (
            (
                "governed_conflict_candidate_count",
                len(
                    conflict_ids
                ),
            ),
            (
                "unresolved_candidate_count",
                len(
                    unresolved_ids
                ),
            ),
            (
                "abstention_candidate_count",
                len(
                    abstention_ids
                ),
            ),
        )

        for field_name, expected_count in count_checks:

            actual_count = hybrid_summary.get(
                field_name
            )

            if (
                actual_count is not None
                and actual_count != expected_count
            ):
                raise ArticleSemanticConsolidationError(
                    "4.6.15 summary "
                    + field_name
                    + " does not preserve authoritative hybrid state."
                )

    # -----------------------------------------------------------------
    # Preserve every relevant carrier from all 15 layers
    # -----------------------------------------------------------------

    preservation_records = []

    category_index = {
        "CONFLICT_OR_CONTRADICTION":
            [],
        "UNCERTAINTY_OR_AMBIGUITY":
            [],
        "ABSTENTION":
            [],
        "UNRESOLVED":
            [],
        "CONFIDENCE":
            [],
    }

    layers_with_preservation_carriers = []
    layers_without_preservation_carriers = []

    total_carrier_count = 0

    for ordinal, layer_name in enumerate(
        expected_order,
        1,
    ):

        envelope = normalized_layers[
            layer_name
        ]

        source_payload = envelope.get(
            "source_payload"
        )

        if not isinstance(
            source_payload,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " source payload is invalid."
            )

        expected_l_carriers = (
            _collect_article_semantic_state_carriers_v1(
                source_payload
            )
        )

        l_record = l_record_by_layer[
            layer_name
        ]

        if (
            l_record.get(
                "state_carriers"
            )
            != expected_l_carriers
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " L state carriers drifted from the source payload."
            )

        carriers = (
            _collect_article_semantic_preservation_carriers_v1(
                source_payload
            )
        )

        total_carrier_count += len(
            carriers
        )

        if carriers:
            layers_with_preservation_carriers.append(
                layer_name
            )
        else:
            layers_without_preservation_carriers.append(
                layer_name
            )

        for carrier in carriers:

            for category in carrier[
                "categories"
            ]:

                category_index[
                    category
                ].append({
                    "layer_name":
                        layer_name,

                    "phase":
                        _ARTICLE_SEMANTIC_LAYER_PHASES[
                            layer_name
                        ],

                    "path":
                        carrier[
                            "path"
                        ],

                    "key":
                        carrier[
                            "key"
                        ],
                })

        preservation_records.append({
            "preservation_record_id":
                "ASC_PRESERVATION:"
                + str(
                    ordinal
                ),

            "ordinal":
                ordinal,

            "layer_name":
                layer_name,

            "phase":
                _ARTICLE_SEMANTIC_LAYER_PHASES[
                    layer_name
                ],

            "carrier_count":
                len(
                    carriers
                ),

            "has_preservation_carriers":
                bool(
                    carriers
                ),

            "carrier_paths": [
                carrier[
                    "path"
                ]
                for carrier in carriers
            ],

            "carriers":
                deepcopy(
                    carriers
                ),

            "source_payload_preserved":
                True,

            "source_state_preserved":
                True,

            "conflict_state_preserved":
                True,

            "uncertainty_state_preserved":
                True,

            "abstention_state_preserved":
                True,

            "confidence_state_preserved":
                True,

            "conflict_resolution_performed":
                False,

            "contradiction_adjudication_performed":
                False,

            "uncertainty_reinterpretation_performed":
                False,

            "uncertainty_strengthening_performed":
                False,

            "confidence_recalculation_performed":
                False,

            "abstention_decision_created":
                False,

            "abstention_decision_removed":
                False,

            "new_reasoning_performed":
                False,
        })

    for category in category_index:

        category_index[
            category
        ] = sorted(
            category_index[
                category
            ],
            key=lambda item: (
                expected_order.index(
                    item[
                        "layer_name"
                    ]
                ),
                item[
                    "path"
                ],
            ),
        )

    preservation = {
        "preservation_status":
            "CONFLICT_UNCERTAINTY_ABSTENTION_PRESERVED",

        "preservation_mode":
            "EXACT_UPSTREAM_STATE_PRESERVATION",

        "canonical_article_identity":
            deepcopy(
                dict(
                    canonical_identity
                )
            ),

        "total_layer_count":
            15,

        "preservation_record_count":
            len(
                preservation_records
            ),

        "total_preservation_carrier_count":
            total_carrier_count,

        "layers_with_preservation_carriers":
            deepcopy(
                layers_with_preservation_carriers
            ),

        "layers_without_preservation_carriers":
            deepcopy(
                layers_without_preservation_carriers
            ),

        "category_index":
            category_index,

        "layer_preservation_records":
            preservation_records,

        "uncertainty_intelligence_authority":
            "CERTIFIED_4.6.14_UNCERTAINTY_INTELLIGENCE",

        "uncertainty_intelligence_snapshot":
            deepcopy(
                dict(
                    uncertainty_payload
                )
            ),

        "hybrid_governance_authority":
            "FROZEN_4.6.15S_HYBRID_RESULT",

        "hybrid_governance_snapshot":
            deepcopy(
                dict(
                    hybrid_payload
                )
            ),

        "governed_conflict_candidate_ids":
            deepcopy(
                conflict_ids
            ),

        "unresolved_candidate_ids":
            deepcopy(
                unresolved_ids
            ),

        "abstention_candidate_ids":
            deepcopy(
                abstention_ids
            ),

        "article_has_symbolically_governed_conflict":
            expected_conflict_flag,

        "article_has_unresolved_hybrid_evidence":
            expected_unresolved_flag,

        "article_requires_hybrid_abstention":
            expected_abstention_flag,

        "all_source_states_preserved":
            True,

        "uncertainty_layer_preserved":
            True,

        "hybrid_governance_state_preserved":
            True,

        "conflict_resolution_performed":
            False,

        "contradiction_adjudication_performed":
            False,

        "uncertainty_reinterpretation_performed":
            False,

        "uncertainty_strengthening_performed":
            False,

        "unified_semantic_confidence_calculated":
            False,

        "confidence_recalculation_performed":
            False,

        "abstention_decision_created":
            False,

        "abstention_decision_removed":
            False,

        "new_reasoning_performed":
            False,

        "new_fact_inference_performed":
            False,

        "new_relation_inference_performed":
            False,
    }

    return {
        "schema_version":
            "article_conflict_uncertainty_abstention_preservation_v1",

        "article_semantic_consolidation_version":
            ARTICLE_SEMANTIC_CONSOLIDATION_VERSION,

        "phase":
            ARTICLE_SEMANTIC_CONSOLIDATION_PHASE,

        "patch":
            "4.6.16M",

        "status":
            "CONFLICT_UNCERTAINTY_ABSTENTION_PRESERVED",

        "canonical_article_identity":
            deepcopy(
                dict(
                    canonical_identity
                )
            ),

        "cross_layer_article_identity_alignment":
            deepcopy(
                dict(
                    identity_alignment
                )
            ),

        "cross_layer_provenance_alignment":
            deepcopy(
                dict(
                    provenance_alignment
                )
            ),

        "cross_layer_state_indexes":
            deepcopy(
                dict(
                    state_indexes
                )
            ),

        "conflict_uncertainty_abstention_preservation":
            preservation,

        "foundational_semantic_intelligence":
            deepcopy(
                dict(
                    state_index_result[
                        "foundational_semantic_intelligence"
                    ]
                )
            ),

        "structured_reasoning_intelligence":
            deepcopy(
                dict(
                    state_index_result[
                        "structured_reasoning_intelligence"
                    ]
                )
            ),

        "contextual_comparative_intelligence":
            deepcopy(
                dict(
                    state_index_result[
                        "contextual_comparative_intelligence"
                    ]
                )
            ),

        "symbolic_neural_hybrid_intelligence":
            deepcopy(
                dict(
                    state_index_result[
                        "symbolic_neural_hybrid_intelligence"
                    ]
                )
            ),

        "normalized_layers":
            deepcopy(
                dict(
                    normalized_layers
                )
            ),

        "normalized_group_index":
            deepcopy(
                dict(
                    normalized_group_index
                )
            ),

        "source_state_index_result":
            deepcopy(
                dict(
                    state_index_result
                )
            ),

        "processing_boundaries": {
            "intake_validation_preserved":
                True,

            "upstream_normalization_preserved":
                True,

            "foundational_assembly_preserved":
                True,

            "structured_reasoning_assembly_preserved":
                True,

            "contextual_comparative_assembly_preserved":
                True,

            "hybrid_integration_preserved":
                True,

            "article_identity_alignment_preserved":
                True,

            "cross_layer_provenance_alignment_preserved":
                True,

            "cross_layer_state_index_construction_preserved":
                True,

            "conflict_uncertainty_abstention_preservation_performed":
                True,

            "all_15_layers_preservation_accounted_for":
                True,

            "uncertainty_layer_preserved":
                True,

            "hybrid_governance_state_preserved":
                True,

            "source_payloads_preserved":
                True,

            "conflict_resolution_performed":
                False,

            "contradiction_adjudication_performed":
                False,

            "uncertainty_reinterpretation_performed":
                False,

            "uncertainty_strengthening_performed":
                False,

            "unified_semantic_confidence_calculated":
                False,

            "confidence_recalculation_performed":
                False,

            "abstention_decision_created":
                False,

            "abstention_decision_removed":
                False,

            "article_semantic_consolidation_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "cross_layer_fact_synthesis_performed":
                False,

            "fuzzy_semantic_deduplication_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_validation_performed":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "article_level_semantic_consolidation",
    }


# =====================================================================
# PATCH 4.6.16N ? Article-Level Semantic Consolidation
# =====================================================================

def consolidate_article_semantic_intelligence_v1(
    preservation_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Consolidate all already-certified article-local Semantic Intelligence
    into one canonical article-level semantic representation.

    N is structural consolidation only.

    It preserves:
    - all 15 upstream layer payloads,
    - the four semantic intelligence groups,
    - canonical article identity,
    - cross-layer provenance,
    - structural state indexes,
    - conflict / uncertainty / abstention preservation state,
    - source authority boundaries.

    N does NOT:
    - perform new reasoning,
    - merge semantic conclusions,
    - synthesize facts,
    - infer relations,
    - resolve conflicts,
    - adjudicate contradictions,
    - reinterpret uncertainty,
    - strengthen uncertainty,
    - calculate unified Semantic Confidence,
    - recalculate confidence,
    - create or remove abstention,
    - perform fuzzy semantic deduplication,
    - assess truth,
    - validate externally,
    - call external models,
    - write Semantic Memory,
    - persist intelligence,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        preservation_result,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "preservation_result must be a mapping."
        )

    if (
        preservation_result.get(
            "schema_version"
        )
        != "article_conflict_uncertainty_abstention_preservation_v1"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16N requires "
            "article_conflict_uncertainty_abstention_preservation_v1."
        )

    if (
        preservation_result.get(
            "phase"
        )
        != "4.6.16"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16N requires Phase 4.6.16 input."
        )

    if (
        preservation_result.get(
            "patch"
        )
        != "4.6.16M"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16N requires canonical 4.6.16M input."
        )

    if (
        preservation_result.get(
            "status"
        )
        != "CONFLICT_UNCERTAINTY_ABSTENTION_PRESERVED"
    ):
        raise ArticleSemanticConsolidationError(
            "Conflict/uncertainty/abstention state is not preserved."
        )

    if (
        preservation_result.get(
            "next_stage"
        )
        != "article_level_semantic_consolidation"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16M does not hand off to article-level consolidation."
        )

    if (
        preservation_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16N requires article-local transient intelligence."
        )

    boundaries = preservation_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16M processing boundaries are missing."
        )

    required_true_boundaries = (
        "intake_validation_preserved",
        "upstream_normalization_preserved",
        "foundational_assembly_preserved",
        "structured_reasoning_assembly_preserved",
        "contextual_comparative_assembly_preserved",
        "hybrid_integration_preserved",
        "article_identity_alignment_preserved",
        "cross_layer_provenance_alignment_preserved",
        "cross_layer_state_index_construction_preserved",
        "conflict_uncertainty_abstention_preservation_performed",
        "all_15_layers_preservation_accounted_for",
        "uncertainty_layer_preserved",
        "hybrid_governance_state_preserved",
        "source_payloads_preserved",
    )

    for field in required_true_boundaries:

        if (
            boundaries.get(
                field
            )
            is not True
        ):
            raise ArticleSemanticConsolidationError(
                "Required 4.6.16M boundary is not preserved: "
                + field
            )

    required_false_boundaries = (
        "conflict_resolution_performed",
        "contradiction_adjudication_performed",
        "uncertainty_reinterpretation_performed",
        "uncertainty_strengthening_performed",
        "unified_semantic_confidence_calculated",
        "confidence_recalculation_performed",
        "abstention_decision_created",
        "abstention_decision_removed",
        "article_semantic_consolidation_performed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
        "cross_layer_fact_synthesis_performed",
        "fuzzy_semantic_deduplication_performed",
        "truth_assessment_performed",
        "external_validation_performed",
        "external_model_called",
        "semantic_memory_written",
        "linking_decisions_performed",
        "persistence_performed",
    )

    for field in required_false_boundaries:

        if (
            boundaries.get(
                field
            )
            is not False
        ):
            raise ArticleSemanticConsolidationError(
                "Forbidden 4.6.16M boundary is not False: "
                + field
            )

    canonical_identity = preservation_result.get(
        "canonical_article_identity"
    )

    identity_alignment = preservation_result.get(
        "cross_layer_article_identity_alignment"
    )

    provenance_alignment = preservation_result.get(
        "cross_layer_provenance_alignment"
    )

    state_indexes = preservation_result.get(
        "cross_layer_state_indexes"
    )

    preservation = preservation_result.get(
        "conflict_uncertainty_abstention_preservation"
    )

    foundational = preservation_result.get(
        "foundational_semantic_intelligence"
    )

    structured = preservation_result.get(
        "structured_reasoning_intelligence"
    )

    contextual = preservation_result.get(
        "contextual_comparative_intelligence"
    )

    hybrid = preservation_result.get(
        "symbolic_neural_hybrid_intelligence"
    )

    normalized_layers = preservation_result.get(
        "normalized_layers"
    )

    normalized_group_index = preservation_result.get(
        "normalized_group_index"
    )

    for name, value in (
        (
            "canonical_article_identity",
            canonical_identity,
        ),
        (
            "cross_layer_article_identity_alignment",
            identity_alignment,
        ),
        (
            "cross_layer_provenance_alignment",
            provenance_alignment,
        ),
        (
            "cross_layer_state_indexes",
            state_indexes,
        ),
        (
            "conflict_uncertainty_abstention_preservation",
            preservation,
        ),
        (
            "foundational_semantic_intelligence",
            foundational,
        ),
        (
            "structured_reasoning_intelligence",
            structured,
        ),
        (
            "contextual_comparative_intelligence",
            contextual,
        ),
        (
            "symbolic_neural_hybrid_intelligence",
            hybrid,
        ),
        (
            "normalized_layers",
            normalized_layers,
        ),
        (
            "normalized_group_index",
            normalized_group_index,
        ),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                name
                + " is missing or invalid."
            )

    if (
        identity_alignment.get(
            "alignment_status"
        )
        != "CROSS_LAYER_ARTICLE_IDENTITY_ALIGNED"
    ):
        raise ArticleSemanticConsolidationError(
            "Article identity alignment is invalid."
        )

    if (
        provenance_alignment.get(
            "alignment_status"
        )
        != "CROSS_LAYER_PROVENANCE_ALIGNED"
    ):
        raise ArticleSemanticConsolidationError(
            "Cross-layer provenance alignment is invalid."
        )

    if (
        state_indexes.get(
            "construction_status"
        )
        != "CROSS_LAYER_STATE_INDEXES_CONSTRUCTED"
    ):
        raise ArticleSemanticConsolidationError(
            "Cross-layer state indexes are invalid."
        )

    if (
        preservation.get(
            "preservation_status"
        )
        != "CONFLICT_UNCERTAINTY_ABSTENTION_PRESERVED"
    ):
        raise ArticleSemanticConsolidationError(
            "Conflict/uncertainty/abstention preservation is invalid."
        )

    expected_layer_order = list(
        _ARTICLE_SEMANTIC_LAYER_PHASES.keys()
    )

    if (
        list(
            normalized_layers.keys()
        )
        != expected_layer_order
    ):
        raise ArticleSemanticConsolidationError(
            "Normalized Semantic Intelligence layer order is not canonical."
        )

    if len(
        normalized_layers
    ) != 15:
        raise ArticleSemanticConsolidationError(
            "Article consolidation requires exactly 15 layers."
        )

    expected_groups = {
        "foundational_semantic_intelligence":
            list(
                _FOUNDATIONAL_SEMANTIC_LAYERS
            ),

        "structured_reasoning_intelligence":
            list(
                _STRUCTURED_REASONING_LAYERS
            ),

        "contextual_comparative_intelligence":
            list(
                _CONTEXTUAL_COMPARATIVE_LAYERS
            ),

        "symbolic_neural_hybrid_intelligence":
            list(
                _HYBRID_INTELLIGENCE_LAYERS
            ),
    }

    if (
        dict(
            normalized_group_index
        )
        != expected_groups
    ):
        raise ArticleSemanticConsolidationError(
            "Normalized Semantic Intelligence group index is not canonical."
        )

    expected_group_counts = {
        "foundational_semantic_intelligence":
            5,

        "structured_reasoning_intelligence":
            5,

        "contextual_comparative_intelligence":
            4,

        "symbolic_neural_hybrid_intelligence":
            1,
    }

    if (
        foundational.get(
            "layer_count"
        )
        != 5
        or foundational.get(
            "layer_order"
        )
        != list(
            _FOUNDATIONAL_SEMANTIC_LAYERS
        )
    ):
        raise ArticleSemanticConsolidationError(
            "Foundational semantic assembly is invalid."
        )

    if (
        structured.get(
            "layer_count"
        )
        != 5
        or structured.get(
            "layer_order"
        )
        != list(
            _STRUCTURED_REASONING_LAYERS
        )
    ):
        raise ArticleSemanticConsolidationError(
            "Structured reasoning assembly is invalid."
        )

    if (
        contextual.get(
            "layer_count"
        )
        != 4
        or contextual.get(
            "layer_order"
        )
        != list(
            _CONTEXTUAL_COMPARATIVE_LAYERS
        )
    ):
        raise ArticleSemanticConsolidationError(
            "Contextual/comparative assembly is invalid."
        )

    if (
        hybrid.get(
            "layer_count"
        )
        != 1
        or hybrid.get(
            "layer_order"
        )
        != list(
            _HYBRID_INTELLIGENCE_LAYERS
        )
    ):
        raise ArticleSemanticConsolidationError(
            "Hybrid integration group is invalid."
        )

    if (
        identity_alignment.get(
            "total_layer_count"
        )
        != 15
        or len(
            identity_alignment.get(
                "identity_records",
                [],
            )
        )
        != 15
    ):
        raise ArticleSemanticConsolidationError(
            "Identity alignment does not account for all 15 layers."
        )

    if (
        provenance_alignment.get(
            "total_layer_count"
        )
        != 15
        or len(
            provenance_alignment.get(
                "provenance_records",
                [],
            )
        )
        != 15
    ):
        raise ArticleSemanticConsolidationError(
            "Provenance alignment does not account for all 15 layers."
        )

    if (
        state_indexes.get(
            "total_layer_count"
        )
        != 15
        or state_indexes.get(
            "layer_state_record_count"
        )
        != 15
    ):
        raise ArticleSemanticConsolidationError(
            "State indexes do not account for all 15 layers."
        )

    if (
        preservation.get(
            "total_layer_count"
        )
        != 15
        or preservation.get(
            "preservation_record_count"
        )
        != 15
    ):
        raise ArticleSemanticConsolidationError(
            "Preservation stage does not account for all 15 layers."
        )

    if (
        preservation.get(
            "uncertainty_layer_preserved"
        )
        is not True
        or preservation.get(
            "hybrid_governance_state_preserved"
        )
        is not True
        or preservation.get(
            "all_source_states_preserved"
        )
        is not True
    ):
        raise ArticleSemanticConsolidationError(
            "Required preserved semantic state is incomplete."
        )

    # -------------------------------------------------------------
    # Construct exact per-layer canonical manifest.
    # -------------------------------------------------------------

    layer_manifest = []
    canonical_layer_payloads = {}

    for ordinal, layer_name in enumerate(
        expected_layer_order,
        1,
    ):

        envelope = normalized_layers[
            layer_name
        ]

        if not isinstance(
            envelope,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " normalized envelope is invalid."
            )

        source_payload = envelope.get(
            "source_payload"
        )

        if not isinstance(
            source_payload,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " source payload is invalid."
            )

        contract = (
            _ARTICLE_SEMANTIC_UPSTREAM_RESULT_CONTRACTS[
                layer_name
            ]
        )

        authority = (
            _ARTICLE_SEMANTIC_INPUT_AUTHORITY[
                layer_name
            ]
        )

        if (
            envelope.get(
                "phase"
            )
            != contract[
                "phase"
            ]
            or envelope.get(
                "schema_version"
            )
            != contract[
                "schema_version"
            ]
            or envelope.get(
                "patch"
            )
            != contract[
                "patch"
            ]
            or envelope.get(
                "status"
            )
            != contract[
                "status"
            ]
            or envelope.get(
                "source_next_stage"
            )
            != contract[
                "next_stage"
            ]
            or envelope.get(
                "input_authority"
            )
            != authority
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " source contract drifted before article consolidation."
            )

        canonical_layer_payloads[
            layer_name
        ] = deepcopy(
            dict(
                source_payload
            )
        )

        layer_manifest.append({
            "ordinal":
                ordinal,

            "layer_name":
                layer_name,

            "phase":
                contract[
                    "phase"
                ],

            "group_name":
                envelope.get(
                    "group_name"
                ),

            "schema_version":
                contract[
                    "schema_version"
                ],

            "patch":
                contract[
                    "patch"
                ],

            "status":
                contract[
                    "status"
                ],

            "input_authority":
                authority,

            "source_payload_preserved":
                True,

            "source_meaning_preserved":
                True,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "new_relation_inference_performed":
                False,
        })

    semantic_group_manifest = {
        group_name: {
            "layer_order":
                deepcopy(
                    layer_order
                ),

            "layer_count":
                expected_group_counts[
                    group_name
                ],

            "structurally_preserved":
                True,

            "semantic_merge_performed":
                False,

            "new_reasoning_performed":
                False,
        }
        for group_name, layer_order in expected_groups.items()
    }

    canonical_representation = {
        "representation_status":
            "ARTICLE_SEMANTIC_INTELLIGENCE_CONSOLIDATED",

        "representation_mode":
            "STRUCTURAL_PRESERVATION_AND_CANONICAL_PACKAGING",

        "article_semantic_consolidation_version":
            ARTICLE_SEMANTIC_CONSOLIDATION_VERSION,

        "canonical_article_identity":
            deepcopy(
                dict(
                    canonical_identity
                )
            ),

        "canonical_layer_order":
            deepcopy(
                expected_layer_order
            ),

        "total_layer_count":
            15,

        "semantic_group_order": [
            "foundational_semantic_intelligence",
            "structured_reasoning_intelligence",
            "contextual_comparative_intelligence",
            "symbolic_neural_hybrid_intelligence",
        ],

        "semantic_group_count":
            4,

        "semantic_group_manifest":
            semantic_group_manifest,

        "layer_manifest":
            layer_manifest,

        "canonical_layer_payloads":
            canonical_layer_payloads,

        "semantic_groups": {
            "foundational_semantic_intelligence":
                deepcopy(
                    dict(
                        foundational
                    )
                ),

            "structured_reasoning_intelligence":
                deepcopy(
                    dict(
                        structured
                    )
                ),

            "contextual_comparative_intelligence":
                deepcopy(
                    dict(
                        contextual
                    )
                ),

            "symbolic_neural_hybrid_intelligence":
                deepcopy(
                    dict(
                        hybrid
                    )
                ),
        },

        "cross_layer_artifacts": {
            "article_identity_alignment":
                deepcopy(
                    dict(
                        identity_alignment
                    )
                ),

            "provenance_alignment":
                deepcopy(
                    dict(
                        provenance_alignment
                    )
                ),

            "state_indexes":
                deepcopy(
                    dict(
                        state_indexes
                    )
                ),

            "conflict_uncertainty_abstention_preservation":
                deepcopy(
                    dict(
                        preservation
                    )
                ),
        },

        "all_15_layers_preserved":
            True,

        "all_four_semantic_groups_preserved":
            True,

        "identity_preserved":
            True,

        "provenance_preserved":
            True,

        "state_indexes_preserved":
            True,

        "conflict_uncertainty_abstention_state_preserved":
            True,

        "source_authority_boundaries_preserved":
            True,

        "semantic_merge_performed":
            False,

        "cross_layer_reasoning_performed":
            False,

        "cross_layer_fact_synthesis_performed":
            False,

        "conflict_resolution_performed":
            False,

        "contradiction_adjudication_performed":
            False,

        "uncertainty_reinterpretation_performed":
            False,

        "uncertainty_strengthening_performed":
            False,

        "unified_semantic_confidence_calculated":
            False,

        "confidence_recalculation_performed":
            False,

        "abstention_decision_created":
            False,

        "abstention_decision_removed":
            False,

        "fuzzy_semantic_deduplication_performed":
            False,

        "new_reasoning_performed":
            False,

        "new_fact_inference_performed":
            False,

        "new_relation_inference_performed":
            False,
    }

    return {
        "schema_version":
            "article_semantic_consolidation_result_v1",

        "article_semantic_consolidation_version":
            ARTICLE_SEMANTIC_CONSOLIDATION_VERSION,

        "phase":
            ARTICLE_SEMANTIC_CONSOLIDATION_PHASE,

        "patch":
            "4.6.16N",

        "status":
            "ARTICLE_SEMANTIC_INTELLIGENCE_CONSOLIDATED",

        "canonical_article_identity":
            deepcopy(
                dict(
                    canonical_identity
                )
            ),

        "canonical_article_semantic_representation":
            canonical_representation,

        "cross_layer_article_identity_alignment":
            deepcopy(
                dict(
                    identity_alignment
                )
            ),

        "cross_layer_provenance_alignment":
            deepcopy(
                dict(
                    provenance_alignment
                )
            ),

        "cross_layer_state_indexes":
            deepcopy(
                dict(
                    state_indexes
                )
            ),

        "conflict_uncertainty_abstention_preservation":
            deepcopy(
                dict(
                    preservation
                )
            ),

        "foundational_semantic_intelligence":
            deepcopy(
                dict(
                    foundational
                )
            ),

        "structured_reasoning_intelligence":
            deepcopy(
                dict(
                    structured
                )
            ),

        "contextual_comparative_intelligence":
            deepcopy(
                dict(
                    contextual
                )
            ),

        "symbolic_neural_hybrid_intelligence":
            deepcopy(
                dict(
                    hybrid
                )
            ),

        "normalized_layers":
            deepcopy(
                dict(
                    normalized_layers
                )
            ),

        "normalized_group_index":
            deepcopy(
                dict(
                    normalized_group_index
                )
            ),

        "source_preservation_result":
            deepcopy(
                dict(
                    preservation_result
                )
            ),

        "processing_boundaries": {
            "intake_validation_preserved":
                True,

            "upstream_normalization_preserved":
                True,

            "foundational_assembly_preserved":
                True,

            "structured_reasoning_assembly_preserved":
                True,

            "contextual_comparative_assembly_preserved":
                True,

            "hybrid_integration_preserved":
                True,

            "article_identity_alignment_preserved":
                True,

            "cross_layer_provenance_alignment_preserved":
                True,

            "cross_layer_state_index_construction_preserved":
                True,

            "conflict_uncertainty_abstention_preservation_preserved":
                True,

            "article_semantic_consolidation_performed":
                True,

            "canonical_article_semantic_representation_built":
                True,

            "all_15_layers_preserved":
                True,

            "all_four_semantic_groups_preserved":
                True,

            "source_authority_boundaries_preserved":
                True,

            "semantic_merge_performed":
                False,

            "cross_layer_reasoning_performed":
                False,

            "cross_layer_fact_synthesis_performed":
                False,

            "conflict_resolution_performed":
                False,

            "contradiction_adjudication_performed":
                False,

            "uncertainty_reinterpretation_performed":
                False,

            "uncertainty_strengthening_performed":
                False,

            "unified_semantic_confidence_calculated":
                False,

            "confidence_recalculation_performed":
                False,

            "abstention_decision_created":
                False,

            "abstention_decision_removed":
                False,

            "fuzzy_semantic_deduplication_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_validation_performed":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,

            "final_result_built":
                False,

            "full_layer_certification_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "final_article_semantic_consolidation_result",
    }


# =====================================================================
# PATCH 4.6.16O ? Final Article Semantic Consolidation Result
# =====================================================================

def build_final_article_semantic_consolidation_result_v1(
    article_consolidation_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Build the canonical final Phase 4.6.16 Article Semantic
    Consolidation result.

    O is final packaging / handoff only.

    It does NOT:
    - perform new reasoning,
    - modify any upstream semantic meaning,
    - merge semantic conclusions,
    - synthesize article facts,
    - infer new relations,
    - resolve conflicts,
    - adjudicate contradictions,
    - reinterpret or strengthen uncertainty,
    - calculate unified Semantic Confidence,
    - recalculate confidence,
    - create or remove abstention,
    - rebuild upstream indexes,
    - perform fuzzy semantic deduplication,
    - assess truth,
    - validate externally,
    - call external models,
    - write Semantic Memory,
    - persist intelligence,
    - make linking decisions.

    Successful execution produces the final transient result that is
    ready for 4.6.16P full-layer hard certification.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        article_consolidation_result,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "article_consolidation_result must be a mapping."
        )

    if (
        article_consolidation_result.get(
            "schema_version"
        )
        != "article_semantic_consolidation_result_v1"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16O requires article_semantic_consolidation_result_v1."
        )

    if (
        article_consolidation_result.get(
            "phase"
        )
        != "4.6.16"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16O requires Phase 4.6.16 input."
        )

    if (
        article_consolidation_result.get(
            "patch"
        )
        != "4.6.16N"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16O requires canonical 4.6.16N input."
        )

    if (
        article_consolidation_result.get(
            "status"
        )
        != "ARTICLE_SEMANTIC_INTELLIGENCE_CONSOLIDATED"
    ):
        raise ArticleSemanticConsolidationError(
            "Article Semantic Intelligence is not consolidated."
        )

    if (
        article_consolidation_result.get(
            "next_stage"
        )
        != "final_article_semantic_consolidation_result"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16N does not hand off to the final-result stage."
        )

    if (
        article_consolidation_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16O requires article-local transient intelligence."
        )

    boundaries = article_consolidation_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16N processing boundaries are missing."
        )

    required_true = (
        "intake_validation_preserved",
        "upstream_normalization_preserved",
        "foundational_assembly_preserved",
        "structured_reasoning_assembly_preserved",
        "contextual_comparative_assembly_preserved",
        "hybrid_integration_preserved",
        "article_identity_alignment_preserved",
        "cross_layer_provenance_alignment_preserved",
        "cross_layer_state_index_construction_preserved",
        "conflict_uncertainty_abstention_preservation_preserved",
        "article_semantic_consolidation_performed",
        "canonical_article_semantic_representation_built",
        "all_15_layers_preserved",
        "all_four_semantic_groups_preserved",
        "source_authority_boundaries_preserved",
    )

    for field in required_true:

        if (
            boundaries.get(
                field
            )
            is not True
        ):
            raise ArticleSemanticConsolidationError(
                "Required 4.6.16N boundary is not preserved: "
                + field
            )

    required_false = (
        "semantic_merge_performed",
        "cross_layer_reasoning_performed",
        "cross_layer_fact_synthesis_performed",
        "conflict_resolution_performed",
        "contradiction_adjudication_performed",
        "uncertainty_reinterpretation_performed",
        "uncertainty_strengthening_performed",
        "unified_semantic_confidence_calculated",
        "confidence_recalculation_performed",
        "abstention_decision_created",
        "abstention_decision_removed",
        "fuzzy_semantic_deduplication_performed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
        "truth_assessment_performed",
        "external_validation_performed",
        "external_model_called",
        "semantic_memory_written",
        "linking_decisions_performed",
        "persistence_performed",
        "final_result_built",
        "full_layer_certification_performed",
    )

    for field in required_false:

        if (
            boundaries.get(
                field
            )
            is not False
        ):
            raise ArticleSemanticConsolidationError(
                "Forbidden 4.6.16N boundary is not False: "
                + field
            )

    canonical_identity = article_consolidation_result.get(
        "canonical_article_identity"
    )

    representation = article_consolidation_result.get(
        "canonical_article_semantic_representation"
    )

    identity_alignment = article_consolidation_result.get(
        "cross_layer_article_identity_alignment"
    )

    provenance_alignment = article_consolidation_result.get(
        "cross_layer_provenance_alignment"
    )

    state_indexes = article_consolidation_result.get(
        "cross_layer_state_indexes"
    )

    preservation = article_consolidation_result.get(
        "conflict_uncertainty_abstention_preservation"
    )

    normalized_layers = article_consolidation_result.get(
        "normalized_layers"
    )

    normalized_group_index = article_consolidation_result.get(
        "normalized_group_index"
    )

    foundational = article_consolidation_result.get(
        "foundational_semantic_intelligence"
    )

    structured = article_consolidation_result.get(
        "structured_reasoning_intelligence"
    )

    contextual = article_consolidation_result.get(
        "contextual_comparative_intelligence"
    )

    hybrid = article_consolidation_result.get(
        "symbolic_neural_hybrid_intelligence"
    )

    for name, value in (
        (
            "canonical_article_identity",
            canonical_identity,
        ),
        (
            "canonical_article_semantic_representation",
            representation,
        ),
        (
            "cross_layer_article_identity_alignment",
            identity_alignment,
        ),
        (
            "cross_layer_provenance_alignment",
            provenance_alignment,
        ),
        (
            "cross_layer_state_indexes",
            state_indexes,
        ),
        (
            "conflict_uncertainty_abstention_preservation",
            preservation,
        ),
        (
            "normalized_layers",
            normalized_layers,
        ),
        (
            "normalized_group_index",
            normalized_group_index,
        ),
        (
            "foundational_semantic_intelligence",
            foundational,
        ),
        (
            "structured_reasoning_intelligence",
            structured,
        ),
        (
            "contextual_comparative_intelligence",
            contextual,
        ),
        (
            "symbolic_neural_hybrid_intelligence",
            hybrid,
        ),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                name
                + " is missing or invalid."
            )

    if (
        representation.get(
            "representation_status"
        )
        != "ARTICLE_SEMANTIC_INTELLIGENCE_CONSOLIDATED"
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical article semantic representation is not consolidated."
        )

    if (
        representation.get(
            "representation_mode"
        )
        != "STRUCTURAL_PRESERVATION_AND_CANONICAL_PACKAGING"
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical article semantic representation mode is invalid."
        )

    if (
        representation.get(
            "canonical_article_identity"
        )
        != canonical_identity
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical article identity drifted inside the representation."
        )

    expected_order = list(
        _ARTICLE_SEMANTIC_LAYER_PHASES.keys()
    )

    if (
        representation.get(
            "canonical_layer_order"
        )
        != expected_order
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical representation layer order is invalid."
        )

    if (
        representation.get(
            "total_layer_count"
        )
        != 15
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical representation must contain exactly 15 layers."
        )

    if (
        representation.get(
            "semantic_group_count"
        )
        != 4
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical representation must contain exactly four groups."
        )

    layer_manifest = representation.get(
        "layer_manifest"
    )

    canonical_payloads = representation.get(
        "canonical_layer_payloads"
    )

    semantic_groups = representation.get(
        "semantic_groups"
    )

    cross_layer_artifacts = representation.get(
        "cross_layer_artifacts"
    )

    if (
        not isinstance(
            layer_manifest,
            list,
        )
        or len(
            layer_manifest
        )
        != 15
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical layer manifest is incomplete."
        )

    if not isinstance(
        canonical_payloads,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical layer payloads are missing."
        )

    if (
        list(
            canonical_payloads.keys()
        )
        != expected_order
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical layer payload order is invalid."
        )

    if not isinstance(
        semantic_groups,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical semantic groups are missing."
        )

    expected_group_order = [
        "foundational_semantic_intelligence",
        "structured_reasoning_intelligence",
        "contextual_comparative_intelligence",
        "symbolic_neural_hybrid_intelligence",
    ]

    if (
        list(
            semantic_groups.keys()
        )
        != expected_group_order
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical semantic group order is invalid."
        )

    if not isinstance(
        cross_layer_artifacts,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical cross-layer artifacts are missing."
        )

    expected_artifacts = {
        "article_identity_alignment":
            identity_alignment,

        "provenance_alignment":
            provenance_alignment,

        "state_indexes":
            state_indexes,

        "conflict_uncertainty_abstention_preservation":
            preservation,
    }

    if (
        dict(
            cross_layer_artifacts
        )
        != expected_artifacts
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical cross-layer artifacts drifted from N."
        )

    expected_group_payloads = {
        "foundational_semantic_intelligence":
            foundational,

        "structured_reasoning_intelligence":
            structured,

        "contextual_comparative_intelligence":
            contextual,

        "symbolic_neural_hybrid_intelligence":
            hybrid,
    }

    if (
        dict(
            semantic_groups
        )
        != expected_group_payloads
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical semantic groups drifted from N."
        )

    if (
        list(
            normalized_layers.keys()
        )
        != expected_order
    ):
        raise ArticleSemanticConsolidationError(
            "Normalized layer order is not canonical."
        )

    if len(
        normalized_layers
    ) != 15:
        raise ArticleSemanticConsolidationError(
            "Normalized layer accounting is incomplete."
        )

    for ordinal, layer_name in enumerate(
        expected_order,
        1,
    ):

        envelope = normalized_layers[
            layer_name
        ]

        if not isinstance(
            envelope,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " normalized envelope is invalid."
            )

        source_payload = envelope.get(
            "source_payload"
        )

        if not isinstance(
            source_payload,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " source payload is invalid."
            )

        if (
            canonical_payloads.get(
                layer_name
            )
            != source_payload
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " canonical payload drifted from normalized source."
            )

        manifest_record = layer_manifest[
            ordinal - 1
        ]

        if not isinstance(
            manifest_record,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                "Canonical layer manifest record is invalid."
            )

        if (
            manifest_record.get(
                "ordinal"
            )
            != ordinal
            or manifest_record.get(
                "layer_name"
            )
            != layer_name
            or manifest_record.get(
                "phase"
            )
            != _ARTICLE_SEMANTIC_LAYER_PHASES[
                layer_name
            ]
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " manifest identity/order drifted."
            )

        if (
            manifest_record.get(
                "source_payload_preserved"
            )
            is not True
            or manifest_record.get(
                "source_meaning_preserved"
            )
            is not True
            or manifest_record.get(
                "new_reasoning_performed"
            )
            is not False
            or manifest_record.get(
                "new_fact_inference_performed"
            )
            is not False
            or manifest_record.get(
                "new_relation_inference_performed"
            )
            is not False
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " manifest preservation boundary is invalid."
            )

    required_representation_true = (
        "all_15_layers_preserved",
        "all_four_semantic_groups_preserved",
        "identity_preserved",
        "provenance_preserved",
        "state_indexes_preserved",
        "conflict_uncertainty_abstention_state_preserved",
        "source_authority_boundaries_preserved",
    )

    for field in required_representation_true:

        if (
            representation.get(
                field
            )
            is not True
        ):
            raise ArticleSemanticConsolidationError(
                "Canonical representation preservation boundary "
                "is invalid: "
                + field
            )

    required_representation_false = (
        "semantic_merge_performed",
        "cross_layer_reasoning_performed",
        "cross_layer_fact_synthesis_performed",
        "conflict_resolution_performed",
        "contradiction_adjudication_performed",
        "uncertainty_reinterpretation_performed",
        "uncertainty_strengthening_performed",
        "unified_semantic_confidence_calculated",
        "confidence_recalculation_performed",
        "abstention_decision_created",
        "abstention_decision_removed",
        "fuzzy_semantic_deduplication_performed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
    )

    for field in required_representation_false:

        if (
            representation.get(
                field
            )
            is not False
        ):
            raise ArticleSemanticConsolidationError(
                "Canonical representation forbidden operation "
                "is not False: "
                + field
            )

    if (
        identity_alignment.get(
            "alignment_status"
        )
        != "CROSS_LAYER_ARTICLE_IDENTITY_ALIGNED"
    ):
        raise ArticleSemanticConsolidationError(
            "Final result requires aligned article identity."
        )

    if (
        provenance_alignment.get(
            "alignment_status"
        )
        != "CROSS_LAYER_PROVENANCE_ALIGNED"
    ):
        raise ArticleSemanticConsolidationError(
            "Final result requires aligned provenance."
        )

    if (
        state_indexes.get(
            "construction_status"
        )
        != "CROSS_LAYER_STATE_INDEXES_CONSTRUCTED"
    ):
        raise ArticleSemanticConsolidationError(
            "Final result requires constructed state indexes."
        )

    if (
        preservation.get(
            "preservation_status"
        )
        != "CONFLICT_UNCERTAINTY_ABSTENTION_PRESERVED"
    ):
        raise ArticleSemanticConsolidationError(
            "Final result requires preserved governed semantic state."
        )

    conflict_ids = preservation.get(
        "governed_conflict_candidate_ids",
        [],
    )

    unresolved_ids = preservation.get(
        "unresolved_candidate_ids",
        [],
    )

    abstention_ids = preservation.get(
        "abstention_candidate_ids",
        [],
    )

    if (
        not isinstance(
            conflict_ids,
            list,
        )
        or not isinstance(
            unresolved_ids,
            list,
        )
        or not isinstance(
            abstention_ids,
            list,
        )
    ):
        raise ArticleSemanticConsolidationError(
            "Preserved hybrid governed-state indexes are invalid."
        )

    if unresolved_ids != abstention_ids:
        raise ArticleSemanticConsolidationError(
            "Preserved unresolved and abstention indexes diverged."
        )

    final_summary = {
        "final_status":
            "ARTICLE_SEMANTIC_CONSOLIDATION_RESULT_READY",

        "article_semantic_consolidation_version":
            ARTICLE_SEMANTIC_CONSOLIDATION_VERSION,

        "canonical_layer_count":
            15,

        "semantic_group_count":
            4,

        "identity_alignment_status":
            identity_alignment[
                "alignment_status"
            ],

        "provenance_alignment_status":
            provenance_alignment[
                "alignment_status"
            ],

        "state_index_construction_status":
            state_indexes[
                "construction_status"
            ],

        "preservation_status":
            preservation[
                "preservation_status"
            ],

        "article_semantic_consolidation_status":
            representation[
                "representation_status"
            ],

        "governed_conflict_candidate_ids":
            deepcopy(
                conflict_ids
            ),

        "unresolved_candidate_ids":
            deepcopy(
                unresolved_ids
            ),

        "abstention_candidate_ids":
            deepcopy(
                abstention_ids
            ),

        "article_has_symbolically_governed_conflict":
            preservation.get(
                "article_has_symbolically_governed_conflict"
            ),

        "article_has_unresolved_hybrid_evidence":
            preservation.get(
                "article_has_unresolved_hybrid_evidence"
            ),

        "article_requires_hybrid_abstention":
            preservation.get(
                "article_requires_hybrid_abstention"
            ),

        "all_15_layers_preserved":
            True,

        "all_four_semantic_groups_preserved":
            True,

        "semantic_state_modified":
            False,

        "semantic_merge_performed":
            False,

        "new_reasoning_performed":
            False,

        "new_fact_inference_performed":
            False,

        "new_relation_inference_performed":
            False,

        "conflict_resolution_performed":
            False,

        "uncertainty_strengthening_performed":
            False,

        "confidence_recalculation_performed":
            False,

        "abstention_decision_created":
            False,

        "abstention_decision_removed":
            False,

        "full_layer_certification_pending":
            True,
    }

    final_article_semantic_consolidation = {
        "final_status":
            "ARTICLE_SEMANTIC_CONSOLIDATION_RESULT_READY",

        "canonical_article_identity":
            deepcopy(
                dict(
                    canonical_identity
                )
            ),

        "canonical_article_semantic_representation":
            deepcopy(
                dict(
                    representation
                )
            ),

        "cross_layer_article_identity_alignment":
            deepcopy(
                dict(
                    identity_alignment
                )
            ),

        "cross_layer_provenance_alignment":
            deepcopy(
                dict(
                    provenance_alignment
                )
            ),

        "cross_layer_state_indexes":
            deepcopy(
                dict(
                    state_indexes
                )
            ),

        "conflict_uncertainty_abstention_preservation":
            deepcopy(
                dict(
                    preservation
                )
            ),

        "semantic_groups":
            deepcopy(
                dict(
                    semantic_groups
                )
            ),

        "normalized_layers":
            deepcopy(
                dict(
                    normalized_layers
                )
            ),

        "normalized_group_index":
            deepcopy(
                dict(
                    normalized_group_index
                )
            ),

        "final_summary":
            deepcopy(
                final_summary
            ),

        "source_meaning_preserved":
            True,

        "source_authority_boundaries_preserved":
            True,

        "final_packaging_only":
            True,

        "new_reasoning_performed":
            False,

        "semantic_state_modified":
            False,
    }

    return {
        "schema_version":
            "final_article_semantic_consolidation_result_v1",

        "article_semantic_consolidation_version":
            ARTICLE_SEMANTIC_CONSOLIDATION_VERSION,

        "phase":
            ARTICLE_SEMANTIC_CONSOLIDATION_PHASE,

        "patch":
            "4.6.16O",

        "status":
            "ARTICLE_SEMANTIC_CONSOLIDATION_RESULT_READY",

        "canonical_article_identity":
            deepcopy(
                dict(
                    canonical_identity
                )
            ),

        "final_article_semantic_consolidation":
            final_article_semantic_consolidation,

        "canonical_article_semantic_representation":
            deepcopy(
                dict(
                    representation
                )
            ),

        "final_result_summary":
            final_summary,

        "cross_layer_article_identity_alignment":
            deepcopy(
                dict(
                    identity_alignment
                )
            ),

        "cross_layer_provenance_alignment":
            deepcopy(
                dict(
                    provenance_alignment
                )
            ),

        "cross_layer_state_indexes":
            deepcopy(
                dict(
                    state_indexes
                )
            ),

        "conflict_uncertainty_abstention_preservation":
            deepcopy(
                dict(
                    preservation
                )
            ),

        "foundational_semantic_intelligence":
            deepcopy(
                dict(
                    foundational
                )
            ),

        "structured_reasoning_intelligence":
            deepcopy(
                dict(
                    structured
                )
            ),

        "contextual_comparative_intelligence":
            deepcopy(
                dict(
                    contextual
                )
            ),

        "symbolic_neural_hybrid_intelligence":
            deepcopy(
                dict(
                    hybrid
                )
            ),

        "normalized_layers":
            deepcopy(
                dict(
                    normalized_layers
                )
            ),

        "normalized_group_index":
            deepcopy(
                dict(
                    normalized_group_index
                )
            ),

        "source_article_semantic_consolidation_result":
            deepcopy(
                dict(
                    article_consolidation_result
                )
            ),

        "processing_boundaries": {
            "intake_validation_preserved":
                True,

            "upstream_normalization_preserved":
                True,

            "foundational_assembly_preserved":
                True,

            "structured_reasoning_assembly_preserved":
                True,

            "contextual_comparative_assembly_preserved":
                True,

            "hybrid_integration_preserved":
                True,

            "article_identity_alignment_preserved":
                True,

            "cross_layer_provenance_alignment_preserved":
                True,

            "cross_layer_state_index_construction_preserved":
                True,

            "conflict_uncertainty_abstention_preservation_preserved":
                True,

            "article_semantic_consolidation_preserved":
                True,

            "canonical_article_semantic_representation_preserved":
                True,

            "final_result_built":
                True,

            "final_result_validated":
                True,

            "all_15_layers_preserved":
                True,

            "all_four_semantic_groups_preserved":
                True,

            "source_authority_boundaries_preserved":
                True,

            "final_packaging_only":
                True,

            "semantic_state_modified":
                False,

            "semantic_merge_performed":
                False,

            "cross_layer_reasoning_performed":
                False,

            "cross_layer_fact_synthesis_performed":
                False,

            "conflict_resolution_performed":
                False,

            "contradiction_adjudication_performed":
                False,

            "uncertainty_reinterpretation_performed":
                False,

            "uncertainty_strengthening_performed":
                False,

            "unified_semantic_confidence_calculated":
                False,

            "confidence_recalculation_performed":
                False,

            "abstention_decision_created":
                False,

            "abstention_decision_removed":
                False,

            "upstream_index_rebuild_performed":
                False,

            "fuzzy_semantic_deduplication_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_validation_performed":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,

            "full_layer_certification_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "article_semantic_consolidation_full_layer_certification",
    }


# =====================================================================
# PATCH 4.6.16P ? Full-Layer Hard Certification
# =====================================================================

def certify_article_semantic_consolidation_v1(
    final_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Full-layer certification gate for Phase 4.6.16 Article Semantic
    Consolidation.

    P validates the already-built 4.6.16O result only.

    Certification does NOT:
    - perform new reasoning,
    - change semantic meaning,
    - merge semantic conclusions,
    - synthesize article facts,
    - infer new relations,
    - resolve or re-resolve conflicts,
    - adjudicate contradictions,
    - reinterpret or strengthen uncertainty,
    - calculate unified Semantic Confidence,
    - recalculate confidence,
    - create or remove abstention decisions,
    - rebuild upstream indexes,
    - perform fuzzy semantic deduplication,
    - assess truth,
    - validate against external authority,
    - call external models,
    - write Semantic Memory,
    - persist intelligence,
    - make linking decisions.

    Successful certification closes Phase 4.6.16 and hands the
    certified article-local semantic consolidation result to
    Phase 4.6.17.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        final_result,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "final_result must be a mapping."
        )

    if (
        final_result.get(
            "schema_version"
        )
        != "final_article_semantic_consolidation_result_v1"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16P requires "
            "final_article_semantic_consolidation_result_v1."
        )

    if (
        final_result.get(
            "phase"
        )
        != "4.6.16"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16P requires Phase 4.6.16 input."
        )

    if (
        final_result.get(
            "patch"
        )
        != "4.6.16O"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16P requires canonical 4.6.16O input."
        )

    if (
        final_result.get(
            "status"
        )
        != "ARTICLE_SEMANTIC_CONSOLIDATION_RESULT_READY"
    ):
        raise ArticleSemanticConsolidationError(
            "Final Article Semantic Consolidation result is not ready."
        )

    if (
        final_result.get(
            "next_stage"
        )
        != "article_semantic_consolidation_full_layer_certification"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16O does not hand off to full-layer certification."
        )

    if (
        final_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16P requires article-local transient intelligence."
        )

    boundaries = final_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "4.6.16O processing boundaries are missing."
        )

    required_true_boundaries = (
        "intake_validation_preserved",
        "upstream_normalization_preserved",
        "foundational_assembly_preserved",
        "structured_reasoning_assembly_preserved",
        "contextual_comparative_assembly_preserved",
        "hybrid_integration_preserved",
        "article_identity_alignment_preserved",
        "cross_layer_provenance_alignment_preserved",
        "cross_layer_state_index_construction_preserved",
        "conflict_uncertainty_abstention_preservation_preserved",
        "article_semantic_consolidation_preserved",
        "canonical_article_semantic_representation_preserved",
        "final_result_built",
        "final_result_validated",
        "all_15_layers_preserved",
        "all_four_semantic_groups_preserved",
        "source_authority_boundaries_preserved",
        "final_packaging_only",
    )

    for field in required_true_boundaries:

        if (
            boundaries.get(
                field
            )
            is not True
        ):
            raise ArticleSemanticConsolidationError(
                "Required 4.6.16O boundary is not preserved: "
                + field
            )

    required_false_boundaries = (
        "semantic_state_modified",
        "semantic_merge_performed",
        "cross_layer_reasoning_performed",
        "cross_layer_fact_synthesis_performed",
        "conflict_resolution_performed",
        "contradiction_adjudication_performed",
        "uncertainty_reinterpretation_performed",
        "uncertainty_strengthening_performed",
        "unified_semantic_confidence_calculated",
        "confidence_recalculation_performed",
        "abstention_decision_created",
        "abstention_decision_removed",
        "upstream_index_rebuild_performed",
        "fuzzy_semantic_deduplication_performed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
        "truth_assessment_performed",
        "external_validation_performed",
        "external_model_called",
        "semantic_memory_written",
        "linking_decisions_performed",
        "persistence_performed",
        "full_layer_certification_performed",
    )

    for field in required_false_boundaries:

        if (
            boundaries.get(
                field
            )
            is not False
        ):
            raise ArticleSemanticConsolidationError(
                "Forbidden 4.6.16O boundary is not False: "
                + field
            )

    canonical_identity = final_result.get(
        "canonical_article_identity"
    )

    final_package = final_result.get(
        "final_article_semantic_consolidation"
    )

    representation = final_result.get(
        "canonical_article_semantic_representation"
    )

    final_summary = final_result.get(
        "final_result_summary"
    )

    identity_alignment = final_result.get(
        "cross_layer_article_identity_alignment"
    )

    provenance_alignment = final_result.get(
        "cross_layer_provenance_alignment"
    )

    state_indexes = final_result.get(
        "cross_layer_state_indexes"
    )

    preservation = final_result.get(
        "conflict_uncertainty_abstention_preservation"
    )

    foundational = final_result.get(
        "foundational_semantic_intelligence"
    )

    structured = final_result.get(
        "structured_reasoning_intelligence"
    )

    contextual = final_result.get(
        "contextual_comparative_intelligence"
    )

    hybrid = final_result.get(
        "symbolic_neural_hybrid_intelligence"
    )

    normalized_layers = final_result.get(
        "normalized_layers"
    )

    normalized_group_index = final_result.get(
        "normalized_group_index"
    )

    for name, value in (
        (
            "canonical_article_identity",
            canonical_identity,
        ),
        (
            "final_article_semantic_consolidation",
            final_package,
        ),
        (
            "canonical_article_semantic_representation",
            representation,
        ),
        (
            "final_result_summary",
            final_summary,
        ),
        (
            "cross_layer_article_identity_alignment",
            identity_alignment,
        ),
        (
            "cross_layer_provenance_alignment",
            provenance_alignment,
        ),
        (
            "cross_layer_state_indexes",
            state_indexes,
        ),
        (
            "conflict_uncertainty_abstention_preservation",
            preservation,
        ),
        (
            "foundational_semantic_intelligence",
            foundational,
        ),
        (
            "structured_reasoning_intelligence",
            structured,
        ),
        (
            "contextual_comparative_intelligence",
            contextual,
        ),
        (
            "symbolic_neural_hybrid_intelligence",
            hybrid,
        ),
        (
            "normalized_layers",
            normalized_layers,
        ),
        (
            "normalized_group_index",
            normalized_group_index,
        ),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                name
                + " is missing or invalid."
            )

    for required_identity_field in (
        "article_id",
        "workspace_id",
    ):

        identity_value = canonical_identity.get(
            required_identity_field
        )

        if (
            not isinstance(
                identity_value,
                str,
            )
            or not identity_value.strip()
        ):
            raise ArticleSemanticConsolidationError(
                "Canonical article identity requires non-empty "
                + required_identity_field
                + "."
            )

    if (
        final_package.get(
            "final_status"
        )
        != "ARTICLE_SEMANTIC_CONSOLIDATION_RESULT_READY"
    ):
        raise ArticleSemanticConsolidationError(
            "Final Article Semantic Consolidation package is invalid."
        )

    if (
        final_package.get(
            "canonical_article_identity"
        )
        != canonical_identity
    ):
        raise ArticleSemanticConsolidationError(
            "Final package article identity drifted."
        )

    if (
        final_package.get(
            "canonical_article_semantic_representation"
        )
        != representation
    ):
        raise ArticleSemanticConsolidationError(
            "Final package representation drifted."
        )

    if (
        final_package.get(
            "cross_layer_article_identity_alignment"
        )
        != identity_alignment
        or final_package.get(
            "cross_layer_provenance_alignment"
        )
        != provenance_alignment
        or final_package.get(
            "cross_layer_state_indexes"
        )
        != state_indexes
        or final_package.get(
            "conflict_uncertainty_abstention_preservation"
        )
        != preservation
    ):
        raise ArticleSemanticConsolidationError(
            "Final package cross-layer artifacts drifted."
        )

    if (
        final_package.get(
            "normalized_layers"
        )
        != normalized_layers
        or final_package.get(
            "normalized_group_index"
        )
        != normalized_group_index
    ):
        raise ArticleSemanticConsolidationError(
            "Final package normalized layer state drifted."
        )

    if (
        final_package.get(
            "final_summary"
        )
        != final_summary
    ):
        raise ArticleSemanticConsolidationError(
            "Final package summary drifted."
        )

    if (
        final_package.get(
            "source_meaning_preserved"
        )
        is not True
        or final_package.get(
            "source_authority_boundaries_preserved"
        )
        is not True
        or final_package.get(
            "final_packaging_only"
        )
        is not True
        or final_package.get(
            "new_reasoning_performed"
        )
        is not False
        or final_package.get(
            "semantic_state_modified"
        )
        is not False
    ):
        raise ArticleSemanticConsolidationError(
            "Final package preservation boundaries are invalid."
        )

    if (
        representation.get(
            "representation_status"
        )
        != "ARTICLE_SEMANTIC_INTELLIGENCE_CONSOLIDATED"
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical semantic representation status is invalid."
        )

    if (
        representation.get(
            "representation_mode"
        )
        != "STRUCTURAL_PRESERVATION_AND_CANONICAL_PACKAGING"
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical semantic representation mode is invalid."
        )

    if (
        representation.get(
            "canonical_article_identity"
        )
        != canonical_identity
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical representation identity drifted."
        )

    expected_layer_order = list(
        _ARTICLE_SEMANTIC_LAYER_PHASES.keys()
    )

    if (
        representation.get(
            "canonical_layer_order"
        )
        != expected_layer_order
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical representation layer order is invalid."
        )

    if (
        representation.get(
            "total_layer_count"
        )
        != 15
        or representation.get(
            "semantic_group_count"
        )
        != 4
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical representation layer/group accounting is invalid."
        )

    if (
        list(
            normalized_layers.keys()
        )
        != expected_layer_order
        or len(
            normalized_layers
        )
        != 15
    ):
        raise ArticleSemanticConsolidationError(
            "Normalized layer accounting is invalid."
        )

    expected_group_index = {
        "foundational_semantic_intelligence":
            list(
                _FOUNDATIONAL_SEMANTIC_LAYERS
            ),

        "structured_reasoning_intelligence":
            list(
                _STRUCTURED_REASONING_LAYERS
            ),

        "contextual_comparative_intelligence":
            list(
                _CONTEXTUAL_COMPARATIVE_LAYERS
            ),

        "symbolic_neural_hybrid_intelligence":
            list(
                _HYBRID_INTELLIGENCE_LAYERS
            ),
    }

    if (
        dict(
            normalized_group_index
        )
        != expected_group_index
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical normalized group index is invalid."
        )

    layer_manifest = representation.get(
        "layer_manifest"
    )

    canonical_payloads = representation.get(
        "canonical_layer_payloads"
    )

    semantic_groups = representation.get(
        "semantic_groups"
    )

    cross_layer_artifacts = representation.get(
        "cross_layer_artifacts"
    )

    if (
        not isinstance(
            layer_manifest,
            list,
        )
        or len(
            layer_manifest
        )
        != 15
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical layer manifest is incomplete."
        )

    if not isinstance(
        canonical_payloads,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical layer payloads are missing."
        )

    if (
        list(
            canonical_payloads.keys()
        )
        != expected_layer_order
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical layer payload order is invalid."
        )

    if not isinstance(
        semantic_groups,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical semantic groups are missing."
        )

    expected_semantic_groups = {
        "foundational_semantic_intelligence":
            foundational,

        "structured_reasoning_intelligence":
            structured,

        "contextual_comparative_intelligence":
            contextual,

        "symbolic_neural_hybrid_intelligence":
            hybrid,
    }

    if (
        dict(
            semantic_groups
        )
        != expected_semantic_groups
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical semantic groups drifted."
        )

    if (
        final_package.get(
            "semantic_groups"
        )
        != semantic_groups
    ):
        raise ArticleSemanticConsolidationError(
            "Final-package semantic groups drifted."
        )

    if not isinstance(
        cross_layer_artifacts,
        Mapping,
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical cross-layer artifacts are missing."
        )

    expected_cross_layer_artifacts = {
        "article_identity_alignment":
            identity_alignment,

        "provenance_alignment":
            provenance_alignment,

        "state_indexes":
            state_indexes,

        "conflict_uncertainty_abstention_preservation":
            preservation,
    }

    if (
        dict(
            cross_layer_artifacts
        )
        != expected_cross_layer_artifacts
    ):
        raise ArticleSemanticConsolidationError(
            "Canonical cross-layer artifacts drifted."
        )

    for ordinal, layer_name in enumerate(
        expected_layer_order,
        1,
    ):

        envelope = normalized_layers[
            layer_name
        ]

        if not isinstance(
            envelope,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " normalized envelope is invalid."
            )

        source_payload = envelope.get(
            "source_payload"
        )

        if not isinstance(
            source_payload,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " source payload is invalid."
            )

        contract = (
            _ARTICLE_SEMANTIC_UPSTREAM_RESULT_CONTRACTS[
                layer_name
            ]
        )

        authority = (
            _ARTICLE_SEMANTIC_INPUT_AUTHORITY[
                layer_name
            ]
        )

        if (
            envelope.get(
                "phase"
            )
            != contract[
                "phase"
            ]
            or envelope.get(
                "schema_version"
            )
            != contract[
                "schema_version"
            ]
            or envelope.get(
                "patch"
            )
            != contract[
                "patch"
            ]
            or envelope.get(
                "status"
            )
            != contract[
                "status"
            ]
            or envelope.get(
                "source_next_stage"
            )
            != contract[
                "next_stage"
            ]
            or envelope.get(
                "input_authority"
            )
            != authority
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " upstream contract drifted."
            )

        if (
            canonical_payloads.get(
                layer_name
            )
            != source_payload
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " canonical payload drifted."
            )

        manifest_record = layer_manifest[
            ordinal - 1
        ]

        if not isinstance(
            manifest_record,
            Mapping,
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " manifest record is invalid."
            )

        if (
            manifest_record.get(
                "ordinal"
            )
            != ordinal
            or manifest_record.get(
                "layer_name"
            )
            != layer_name
            or manifest_record.get(
                "phase"
            )
            != contract[
                "phase"
            ]
            or manifest_record.get(
                "schema_version"
            )
            != contract[
                "schema_version"
            ]
            or manifest_record.get(
                "patch"
            )
            != contract[
                "patch"
            ]
            or manifest_record.get(
                "status"
            )
            != contract[
                "status"
            ]
            or manifest_record.get(
                "input_authority"
            )
            != authority
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " manifest contract drifted."
            )

        if (
            manifest_record.get(
                "source_payload_preserved"
            )
            is not True
            or manifest_record.get(
                "source_meaning_preserved"
            )
            is not True
            or manifest_record.get(
                "new_reasoning_performed"
            )
            is not False
            or manifest_record.get(
                "new_fact_inference_performed"
            )
            is not False
            or manifest_record.get(
                "new_relation_inference_performed"
            )
            is not False
        ):
            raise ArticleSemanticConsolidationError(
                layer_name
                + " manifest preservation boundary is invalid."
            )

    required_representation_true = (
        "all_15_layers_preserved",
        "all_four_semantic_groups_preserved",
        "identity_preserved",
        "provenance_preserved",
        "state_indexes_preserved",
        "conflict_uncertainty_abstention_state_preserved",
        "source_authority_boundaries_preserved",
    )

    for field in required_representation_true:

        if (
            representation.get(
                field
            )
            is not True
        ):
            raise ArticleSemanticConsolidationError(
                "Representation preservation boundary is invalid: "
                + field
            )

    required_representation_false = (
        "semantic_merge_performed",
        "cross_layer_reasoning_performed",
        "cross_layer_fact_synthesis_performed",
        "conflict_resolution_performed",
        "contradiction_adjudication_performed",
        "uncertainty_reinterpretation_performed",
        "uncertainty_strengthening_performed",
        "unified_semantic_confidence_calculated",
        "confidence_recalculation_performed",
        "abstention_decision_created",
        "abstention_decision_removed",
        "fuzzy_semantic_deduplication_performed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
    )

    for field in required_representation_false:

        if (
            representation.get(
                field
            )
            is not False
        ):
            raise ArticleSemanticConsolidationError(
                "Representation forbidden operation is not False: "
                + field
            )

    if (
        identity_alignment.get(
            "alignment_status"
        )
        != "CROSS_LAYER_ARTICLE_IDENTITY_ALIGNED"
        or identity_alignment.get(
            "all_asserted_identities_match"
        )
        is not True
        or identity_alignment.get(
            "identity_conflict_detected"
        )
        is not False
    ):
        raise ArticleSemanticConsolidationError(
            "Article identity alignment certification failed."
        )

    if (
        provenance_alignment.get(
            "alignment_status"
        )
        != "CROSS_LAYER_PROVENANCE_ALIGNED"
        or provenance_alignment.get(
            "total_layer_count"
        )
        != 15
        or len(
            provenance_alignment.get(
                "provenance_records",
                [],
            )
        )
        != 15
    ):
        raise ArticleSemanticConsolidationError(
            "Cross-layer provenance certification failed."
        )

    if (
        state_indexes.get(
            "construction_status"
        )
        != "CROSS_LAYER_STATE_INDEXES_CONSTRUCTED"
        or state_indexes.get(
            "total_layer_count"
        )
        != 15
        or state_indexes.get(
            "layer_state_record_count"
        )
        != 15
    ):
        raise ArticleSemanticConsolidationError(
            "Cross-layer state-index certification failed."
        )

    if (
        preservation.get(
            "preservation_status"
        )
        != "CONFLICT_UNCERTAINTY_ABSTENTION_PRESERVED"
        or preservation.get(
            "total_layer_count"
        )
        != 15
        or preservation.get(
            "preservation_record_count"
        )
        != 15
        or preservation.get(
            "all_source_states_preserved"
        )
        is not True
        or preservation.get(
            "uncertainty_layer_preserved"
        )
        is not True
        or preservation.get(
            "hybrid_governance_state_preserved"
        )
        is not True
    ):
        raise ArticleSemanticConsolidationError(
            "Conflict/uncertainty/abstention certification failed."
        )

    conflict_ids = preservation.get(
        "governed_conflict_candidate_ids",
        [],
    )

    unresolved_ids = preservation.get(
        "unresolved_candidate_ids",
        [],
    )

    abstention_ids = preservation.get(
        "abstention_candidate_ids",
        [],
    )

    for field_name, candidate_ids in (
        (
            "governed_conflict_candidate_ids",
            conflict_ids,
        ),
        (
            "unresolved_candidate_ids",
            unresolved_ids,
        ),
        (
            "abstention_candidate_ids",
            abstention_ids,
        ),
    ):

        if (
            not isinstance(
                candidate_ids,
                list,
            )
            or not all(
                isinstance(
                    candidate_id,
                    str,
                )
                and candidate_id
                for candidate_id in candidate_ids
            )
            or len(
                candidate_ids
            )
            != len(
                set(
                    candidate_ids
                )
            )
        ):
            raise ArticleSemanticConsolidationError(
                field_name
                + " is not a valid unique candidate-ID list."
            )

    if unresolved_ids != abstention_ids:
        raise ArticleSemanticConsolidationError(
            "Unresolved and abstention candidate IDs diverged."
        )

    expected_conflict_flag = bool(
        conflict_ids
    )

    expected_unresolved_flag = bool(
        unresolved_ids
    )

    expected_abstention_flag = bool(
        abstention_ids
    )

    if (
        preservation.get(
            "article_has_symbolically_governed_conflict"
        )
        is not expected_conflict_flag
        or preservation.get(
            "article_has_unresolved_hybrid_evidence"
        )
        is not expected_unresolved_flag
        or preservation.get(
            "article_requires_hybrid_abstention"
        )
        is not expected_abstention_flag
    ):
        raise ArticleSemanticConsolidationError(
            "Preserved article-level governed-state flags are inconsistent."
        )

    if (
        final_summary.get(
            "final_status"
        )
        != "ARTICLE_SEMANTIC_CONSOLIDATION_RESULT_READY"
        or final_summary.get(
            "canonical_layer_count"
        )
        != 15
        or final_summary.get(
            "semantic_group_count"
        )
        != 4
        or final_summary.get(
            "identity_alignment_status"
        )
        != "CROSS_LAYER_ARTICLE_IDENTITY_ALIGNED"
        or final_summary.get(
            "provenance_alignment_status"
        )
        != "CROSS_LAYER_PROVENANCE_ALIGNED"
        or final_summary.get(
            "state_index_construction_status"
        )
        != "CROSS_LAYER_STATE_INDEXES_CONSTRUCTED"
        or final_summary.get(
            "preservation_status"
        )
        != "CONFLICT_UNCERTAINTY_ABSTENTION_PRESERVED"
        or final_summary.get(
            "article_semantic_consolidation_status"
        )
        != "ARTICLE_SEMANTIC_INTELLIGENCE_CONSOLIDATED"
    ):
        raise ArticleSemanticConsolidationError(
            "Final-result summary lifecycle state is invalid."
        )

    if (
        final_summary.get(
            "governed_conflict_candidate_ids"
        )
        != conflict_ids
        or final_summary.get(
            "unresolved_candidate_ids"
        )
        != unresolved_ids
        or final_summary.get(
            "abstention_candidate_ids"
        )
        != abstention_ids
    ):
        raise ArticleSemanticConsolidationError(
            "Final-result summary governed-state indexes drifted."
        )

    if (
        final_summary.get(
            "article_has_symbolically_governed_conflict"
        )
        is not expected_conflict_flag
        or final_summary.get(
            "article_has_unresolved_hybrid_evidence"
        )
        is not expected_unresolved_flag
        or final_summary.get(
            "article_requires_hybrid_abstention"
        )
        is not expected_abstention_flag
    ):
        raise ArticleSemanticConsolidationError(
            "Final-result summary governed-state flags drifted."
        )

    if (
        final_summary.get(
            "all_15_layers_preserved"
        )
        is not True
        or final_summary.get(
            "all_four_semantic_groups_preserved"
        )
        is not True
        or final_summary.get(
            "full_layer_certification_pending"
        )
        is not True
    ):
        raise ArticleSemanticConsolidationError(
            "Final-result summary certification readiness is invalid."
        )

    for field in (
        "semantic_state_modified",
        "semantic_merge_performed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
        "conflict_resolution_performed",
        "uncertainty_strengthening_performed",
        "confidence_recalculation_performed",
        "abstention_decision_created",
        "abstention_decision_removed",
    ):

        if (
            final_summary.get(
                field
            )
            is not False
        ):
            raise ArticleSemanticConsolidationError(
                "Final-result summary forbidden operation "
                "is not False: "
                + field
            )

    certification = {
        "certification_status":
            "CERTIFIED",

        "certification_scope":
            "FULL_ARTICLE_SEMANTIC_CONSOLIDATION_LAYER",

        "certified_phase":
            "4.6.16",

        "certified_source_patch":
            "4.6.16O",

        "certification_mode":
            "STRUCTURAL_PRESERVATION_FULL_LAYER_CERTIFICATION",

        "canonical_layer_count":
            15,

        "semantic_group_count":
            4,

        "all_15_layers_certified":
            True,

        "all_four_semantic_groups_certified":
            True,

        "canonical_identity_certified":
            True,

        "cross_layer_provenance_certified":
            True,

        "cross_layer_state_indexes_certified":
            True,

        "conflict_uncertainty_abstention_preservation_certified":
            True,

        "canonical_article_semantic_representation_certified":
            True,

        "source_authority_boundaries_certified":
            True,

        "final_result_contract_certified":
            True,

        "deterministic_structural_preservation_certified":
            True,

        "semantic_state_modified":
            False,

        "semantic_merge_performed":
            False,

        "cross_layer_reasoning_performed":
            False,

        "cross_layer_fact_synthesis_performed":
            False,

        "conflict_resolution_performed":
            False,

        "contradiction_adjudication_performed":
            False,

        "uncertainty_reinterpretation_performed":
            False,

        "uncertainty_strengthening_performed":
            False,

        "unified_semantic_confidence_calculated":
            False,

        "confidence_recalculation_performed":
            False,

        "abstention_decision_created":
            False,

        "abstention_decision_removed":
            False,

        "upstream_index_rebuild_performed":
            False,

        "fuzzy_semantic_deduplication_performed":
            False,

        "new_reasoning_performed":
            False,

        "new_fact_inference_performed":
            False,

        "new_relation_inference_performed":
            False,

        "truth_assessment_performed":
            False,

        "external_validation_performed":
            False,

        "external_model_called":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,

        "persistence_performed":
            False,
    }

    return {
        "schema_version":
            "certified_article_semantic_consolidation_result_v1",

        "article_semantic_consolidation_version":
            ARTICLE_SEMANTIC_CONSOLIDATION_VERSION,

        "phase":
            ARTICLE_SEMANTIC_CONSOLIDATION_PHASE,

        "patch":
            "4.6.16P",

        "status":
            "ARTICLE_SEMANTIC_CONSOLIDATION_CERTIFIED",

        "canonical_article_identity":
            deepcopy(
                dict(
                    canonical_identity
                )
            ),

        "certification":
            certification,

        "certified_article_semantic_consolidation_result":
            deepcopy(
                dict(
                    final_result
                )
            ),

        "final_article_semantic_consolidation":
            deepcopy(
                dict(
                    final_package
                )
            ),

        "canonical_article_semantic_representation":
            deepcopy(
                dict(
                    representation
                )
            ),

        "final_result_summary":
            deepcopy(
                dict(
                    final_summary
                )
            ),

        "cross_layer_article_identity_alignment":
            deepcopy(
                dict(
                    identity_alignment
                )
            ),

        "cross_layer_provenance_alignment":
            deepcopy(
                dict(
                    provenance_alignment
                )
            ),

        "cross_layer_state_indexes":
            deepcopy(
                dict(
                    state_indexes
                )
            ),

        "conflict_uncertainty_abstention_preservation":
            deepcopy(
                dict(
                    preservation
                )
            ),

        "foundational_semantic_intelligence":
            deepcopy(
                dict(
                    foundational
                )
            ),

        "structured_reasoning_intelligence":
            deepcopy(
                dict(
                    structured
                )
            ),

        "contextual_comparative_intelligence":
            deepcopy(
                dict(
                    contextual
                )
            ),

        "symbolic_neural_hybrid_intelligence":
            deepcopy(
                dict(
                    hybrid
                )
            ),

        "normalized_layers":
            deepcopy(
                dict(
                    normalized_layers
                )
            ),

        "normalized_group_index":
            deepcopy(
                dict(
                    normalized_group_index
                )
            ),

        "processing_boundaries": {
            "intake_validation_certified":
                True,

            "upstream_normalization_certified":
                True,

            "foundational_assembly_certified":
                True,

            "structured_reasoning_assembly_certified":
                True,

            "contextual_comparative_assembly_certified":
                True,

            "hybrid_integration_certified":
                True,

            "article_identity_alignment_certified":
                True,

            "cross_layer_provenance_alignment_certified":
                True,

            "cross_layer_state_index_construction_certified":
                True,

            "conflict_uncertainty_abstention_preservation_certified":
                True,

            "article_semantic_consolidation_certified":
                True,

            "final_article_semantic_consolidation_result_certified":
                True,

            "canonical_article_semantic_representation_certified":
                True,

            "all_15_layers_certified":
                True,

            "all_four_semantic_groups_certified":
                True,

            "source_authority_boundaries_certified":
                True,

            "full_layer_certification_performed":
                True,

            "semantic_state_modified":
                False,

            "semantic_merge_performed":
                False,

            "cross_layer_reasoning_performed":
                False,

            "cross_layer_fact_synthesis_performed":
                False,

            "conflict_resolution_performed":
                False,

            "contradiction_adjudication_performed":
                False,

            "uncertainty_reinterpretation_performed":
                False,

            "uncertainty_strengthening_performed":
                False,

            "unified_semantic_confidence_calculated":
                False,

            "confidence_recalculation_performed":
                False,

            "abstention_decision_created":
                False,

            "abstention_decision_removed":
                False,

            "upstream_index_rebuild_performed":
                False,

            "fuzzy_semantic_deduplication_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "truth_assessment_performed":
                False,

            "external_validation_performed":
                False,

            "external_model_called":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "certified_semantic_article_profile_builder",
    }

