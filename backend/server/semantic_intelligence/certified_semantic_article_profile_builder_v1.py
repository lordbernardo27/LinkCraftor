
from __future__ import annotations

from copy import deepcopy
from typing import Any


class CertifiedSemanticArticleProfileBuilderError(Exception):
    """Raised when a 4.6.17 profile-builder contract is violated."""


CERTIFIED_SEMANTIC_ARTICLE_PROFILE_BUILDER_VERSION = (
    "certified_semantic_article_profile_builder_v1"
)

CERTIFIED_SEMANTIC_ARTICLE_PROFILE_BUILDER_PHASE = (
    "4.6.17"
)


# =====================================================================
# 4.6.17C ? Semantic Article Profile Architecture Definition
# =====================================================================

_CERTIFIED_CONSOLIDATION_INPUT_CONTRACT = {
    "schema_version":
        "certified_article_semantic_consolidation_result_v1",

    "phase":
        "4.6.16",

    "patch":
        "4.6.16P",

    "status":
        "ARTICLE_SEMANTIC_CONSOLIDATION_CERTIFIED",

    "persistence_policy":
        "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

    "next_stage":
        "certified_semantic_article_profile_builder",
}


_SEMANTIC_ARTICLE_PROFILE_SOURCE_GROUP_ORDER = (
    "foundational_semantic_intelligence",
    "structured_reasoning_intelligence",
    "contextual_comparative_intelligence",
    "symbolic_neural_hybrid_intelligence",
)


_SEMANTIC_ARTICLE_PROFILE_LAYER_ORDER = (
    "semantic_runtime_reader",
    "entity_concept_intelligence",
    "phrase_neighborhood_intelligence",
    "topic_intent_intelligence",
    "section_evidence_intelligence",
    "logical_intelligence",
    "relational_intelligence",
    "causal_intelligence",
    "quantitative_intelligence",
    "procedural_intelligence",
    "analogical_intelligence",
    "similarity_intelligence",
    "temporal_intelligence",
    "uncertainty_intelligence",
    "symbolic_neural_hybrid_intelligence",
)


_SEMANTIC_ARTICLE_PROFILE_LAYER_PHASES = {
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


_SEMANTIC_ARTICLE_PROFILE_GROUP_MEMBERSHIP = {
    "foundational_semantic_intelligence": (
        "semantic_runtime_reader",
        "entity_concept_intelligence",
        "phrase_neighborhood_intelligence",
        "topic_intent_intelligence",
        "section_evidence_intelligence",
    ),

    "structured_reasoning_intelligence": (
        "logical_intelligence",
        "relational_intelligence",
        "causal_intelligence",
        "quantitative_intelligence",
        "procedural_intelligence",
    ),

    "contextual_comparative_intelligence": (
        "analogical_intelligence",
        "similarity_intelligence",
        "temporal_intelligence",
        "uncertainty_intelligence",
    ),

    "symbolic_neural_hybrid_intelligence": (
        "symbolic_neural_hybrid_intelligence",
    ),
}


_SEMANTIC_ARTICLE_PROFILE_REQUIRED_SOURCE_ARTIFACTS = (
    "canonical_article_identity",
    "certification",
    "canonical_article_semantic_representation",
    "final_result_summary",
    "cross_layer_article_identity_alignment",
    "cross_layer_provenance_alignment",
    "cross_layer_state_indexes",
    "conflict_uncertainty_abstention_preservation",
    "foundational_semantic_intelligence",
    "structured_reasoning_intelligence",
    "contextual_comparative_intelligence",
    "symbolic_neural_hybrid_intelligence",
    "normalized_layers",
    "normalized_group_index",
    "processing_boundaries",
)


_SEMANTIC_ARTICLE_PROFILE_PROFILE_SECTIONS = (
    "profile_identity",
    "source_certification",
    "semantic_layer_profile",
    "semantic_group_profile",
    "cross_layer_artifact_profile",
    "governed_state_profile",
    "structural_indexes",
    "profile_metadata",
)


_SEMANTIC_ARTICLE_PROFILE_PRESERVATION_RULES = (
    "PRESERVE_CERTIFIED_ARTICLE_IDENTITY",
    "PRESERVE_CERTIFIED_LAYER_ORDER",
    "PRESERVE_CERTIFIED_GROUP_ORDER",
    "PRESERVE_CERTIFIED_SOURCE_MEANING",
    "PRESERVE_CERTIFIED_SOURCE_AUTHORITY",
    "PRESERVE_CERTIFIED_PROVENANCE",
    "PRESERVE_CERTIFIED_STATE_INDEXES",
    "PRESERVE_CERTIFIED_CONFLICT_STATE",
    "PRESERVE_CERTIFIED_UNCERTAINTY_STATE",
    "PRESERVE_CERTIFIED_CONFIDENCE_STATE",
    "PRESERVE_CERTIFIED_UNRESOLVED_STATE",
    "PRESERVE_CERTIFIED_ABSTENTION_STATE",
    "PRESERVE_SYMBOLIC_CONSTRAINT_AUTHORITY",
    "PRESERVE_NEURAL_INTERPRETIVE_BOUNDARY",
    "PRESERVE_ARTICLE_LOCAL_BOUNDARY",
    "PRESERVE_TRANSIENT_LIFECYCLE",
)


_SEMANTIC_ARTICLE_PROFILE_ALLOWED_OPERATIONS = (
    "CERTIFIED_SOURCE_VALIDATION",
    "PROFILE_ORIENTED_STRUCTURAL_PROJECTION",
    "PROFILE_SECTION_ASSEMBLY",
    "DETERMINISTIC_LAYER_INDEXING",
    "DETERMINISTIC_GROUP_INDEXING",
    "DETERMINISTIC_ARTIFACT_INDEXING",
    "DETERMINISTIC_GOVERNED_STATE_INDEXING",
    "DEEP_COPY_PRESERVATION",
    "PROFILE_PACKAGING",
)


_SEMANTIC_ARTICLE_PROFILE_FORBIDDEN_OPERATIONS = (
    "NEW_SEMANTIC_REASONING",
    "NEW_FACT_INFERENCE",
    "NEW_RELATION_INFERENCE",
    "NEW_CAUSAL_INFERENCE",
    "NEW_QUANTITATIVE_CALCULATION",
    "NEW_PROCEDURAL_INFERENCE",
    "NEW_ANALOGICAL_INFERENCE",
    "NEW_SIMILARITY_INFERENCE",
    "NEW_TEMPORAL_INFERENCE",
    "NEW_UNCERTAINTY_INFERENCE",
    "SEMANTIC_MEANING_REWRITE",
    "CROSS_LAYER_FACT_SYNTHESIS",
    "CONFLICT_RESOLUTION",
    "CONTRADICTION_ADJUDICATION",
    "UNCERTAINTY_REINTERPRETATION",
    "UNCERTAINTY_STRENGTHENING",
    "UNIFIED_SEMANTIC_CONFIDENCE_CALCULATION",
    "CONFIDENCE_RECALCULATION",
    "ABSTENTION_DECISION_CREATION",
    "ABSTENTION_DECISION_REMOVAL",
    "UPSTREAM_INDEX_REBUILD",
    "FUZZY_SEMANTIC_DEDUPLICATION",
    "SOURCE_AUTHORITY_OVERRIDE",
    "SYMBOLIC_CONSTRAINT_OVERRIDE",
    "TRUTH_ASSESSMENT",
    "EXTERNAL_VALIDATION",
    "EXTERNAL_MODEL_CALL",
    "PROFILE_CERTIFICATION",
    "SEMANTIC_MEMORY_WRITE",
    "PROFILE_STORE_WRITE",
    "PERSISTENCE",
    "LINKING_DECISION",
)


_SEMANTIC_ARTICLE_PROFILE_AUTHORITY_MODEL = {
    "input_authority":
        "CERTIFIED_4.6.16P_ARTICLE_SEMANTIC_CONSOLIDATION",

    "canonical_identity_authority":
        "4.6.16P_CANONICAL_ARTICLE_IDENTITY",

    "canonical_semantic_representation_authority":
        "4.6.16P_CANONICAL_ARTICLE_SEMANTIC_REPRESENTATION",

    "provenance_authority":
        "4.6.16P_CROSS_LAYER_PROVENANCE_ALIGNMENT",

    "state_index_authority":
        "4.6.16P_CROSS_LAYER_STATE_INDEXES",

    "uncertainty_authority":
        "CERTIFIED_4.6.14_UNCERTAINTY_INTELLIGENCE_VIA_4.6.16P",

    "hybrid_governance_authority":
        "FROZEN_4.6.15S_HYBRID_STATE_VIA_4.6.16P",

    "profile_certification_authority":
        "4.6.18_PROFILE_CERTIFICATION",

    "profile_persistence_authority":
        "4.6.19_PROFILE_STORE",
}


_SEMANTIC_ARTICLE_PROFILE_BUILD_MODEL = {
    "mode":
        "CERTIFIED_STRUCTURAL_PROFILE_PROJECTION",

    "article_local_only":
        True,

    "transient_only":
        True,

    "source_is_certified":
        True,

    "source_semantic_meaning_rewrite":
        False,

    "cross_layer_reasoning":
        False,

    "cross_layer_fact_synthesis":
        False,

    "conflict_resolution":
        False,

    "uncertainty_reinterpretation":
        False,

    "confidence_recalculation":
        False,

    "abstention_decision_creation":
        False,

    "profile_certification":
        False,

    "profile_persistence":
        False,

    "semantic_memory_write":
        False,

    "linking_decision":
        False,
}


def get_certified_semantic_article_profile_builder_architecture_v1(
) -> dict[str, Any]:
    """
    Return the canonical 4.6.17 architecture definition.

    This function exposes architecture metadata only.
    It does not build, certify or persist a Semantic Article Profile.
    """

    return {
        "schema_version":
            "certified_semantic_article_profile_builder_architecture_v1",

        "version":
            CERTIFIED_SEMANTIC_ARTICLE_PROFILE_BUILDER_VERSION,

        "phase":
            CERTIFIED_SEMANTIC_ARTICLE_PROFILE_BUILDER_PHASE,

        "patch":
            "4.6.17C",

        "status":
            "SEMANTIC_ARTICLE_PROFILE_ARCHITECTURE_DEFINED",

        "governing_rule": (
            "Build a structured Semantic Article Profile from the "
            "certified 4.6.16 article semantic consolidation result, "
            "while preserving every certified meaning, authority, "
            "provenance, state, uncertainty, conflict, confidence, "
            "unresolved and abstention boundary exactly as certified."
        ),

        "certified_input_contract":
            deepcopy(
                _CERTIFIED_CONSOLIDATION_INPUT_CONTRACT
            ),

        "source_layer_order":
            list(
                _SEMANTIC_ARTICLE_PROFILE_LAYER_ORDER
            ),

        "source_layer_phases":
            deepcopy(
                _SEMANTIC_ARTICLE_PROFILE_LAYER_PHASES
            ),

        "source_group_order":
            list(
                _SEMANTIC_ARTICLE_PROFILE_SOURCE_GROUP_ORDER
            ),

        "source_group_membership": {
            key:
                list(
                    value
                )
            for key, value in (
                _SEMANTIC_ARTICLE_PROFILE_GROUP_MEMBERSHIP.items()
            )
        },

        "required_source_artifacts":
            list(
                _SEMANTIC_ARTICLE_PROFILE_REQUIRED_SOURCE_ARTIFACTS
            ),

        "profile_sections":
            list(
                _SEMANTIC_ARTICLE_PROFILE_PROFILE_SECTIONS
            ),

        "preservation_rules":
            list(
                _SEMANTIC_ARTICLE_PROFILE_PRESERVATION_RULES
            ),

        "allowed_operations":
            list(
                _SEMANTIC_ARTICLE_PROFILE_ALLOWED_OPERATIONS
            ),

        "forbidden_operations":
            list(
                _SEMANTIC_ARTICLE_PROFILE_FORBIDDEN_OPERATIONS
            ),

        "authority_model":
            deepcopy(
                _SEMANTIC_ARTICLE_PROFILE_AUTHORITY_MODEL
            ),

        "build_model":
            deepcopy(
                _SEMANTIC_ARTICLE_PROFILE_BUILD_MODEL
            ),

        "downstream_boundary": {
            "builder_output_is_profile_certification_ready":
                True,

            "builder_output_is_already_profile_certified":
                False,

            "next_phase":
                "4.6.18",

            "next_stage":
                "semantic_article_profile_certification",
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "certified_consolidation_intake",
    }


# =====================================================================
# PATCH 4.6.17D ? Certified Consolidation Intake
# =====================================================================

def validate_certified_consolidation_intake_v1(
    certified_consolidation_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate the certified 4.6.16P Article Semantic Consolidation result
    before any Semantic Article Profile construction begins.

    D is intake validation only.

    It does NOT:
    - construct a profile,
    - project semantic sections,
    - perform new reasoning,
    - change source meaning,
    - alter source authority,
    - resolve conflict,
    - reinterpret uncertainty,
    - recalculate confidence,
    - create/remove abstention,
    - certify a profile,
    - persist a profile,
    - write Semantic Memory,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        certified_consolidation_result,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "certified_consolidation_result must be a mapping."
        )

    for key, expected in (
        (
            "schema_version",
            "certified_article_semantic_consolidation_result_v1",
        ),
        (
            "phase",
            "4.6.16",
        ),
        (
            "patch",
            "4.6.16P",
        ),
        (
            "status",
            "ARTICLE_SEMANTIC_CONSOLIDATION_CERTIFIED",
        ),
        (
            "persistence_policy",
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        ),
        (
            "next_stage",
            "certified_semantic_article_profile_builder",
        ),
    ):

        if (
            certified_consolidation_result.get(
                key
            )
            != expected
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                "4.6.17D input contract mismatch for "
                + key
                + "."
            )

    for required_artifact in (
        _SEMANTIC_ARTICLE_PROFILE_REQUIRED_SOURCE_ARTIFACTS
    ):

        if required_artifact not in certified_consolidation_result:
            raise CertifiedSemanticArticleProfileBuilderError(
                "Required certified source artifact is missing: "
                + required_artifact
            )

    canonical_identity = certified_consolidation_result.get(
        "canonical_article_identity"
    )

    if not isinstance(
        canonical_identity,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Canonical article identity is missing."
        )

    for identity_field in (
        "article_id",
        "workspace_id",
    ):

        value = canonical_identity.get(
            identity_field
        )

        if (
            not isinstance(
                value,
                str,
            )
            or not value.strip()
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                "Canonical article identity requires non-empty "
                + identity_field
                + "."
            )

    certification = certified_consolidation_result.get(
        "certification"
    )

    if not isinstance(
        certification,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.16P certification object is missing."
        )

    required_certification_values = {
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
    }

    for field, expected in required_certification_values.items():

        if certification.get(
            field
        ) != expected:

            raise CertifiedSemanticArticleProfileBuilderError(
                "Certified source certification field is invalid: "
                + field
            )

    forbidden_certification_true_fields = (
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
    )

    for field in forbidden_certification_true_fields:

        if certification.get(
            field
        ) is not False:

            raise CertifiedSemanticArticleProfileBuilderError(
                "Certified source contains forbidden certification state: "
                + field
            )

    processing_boundaries = certified_consolidation_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        processing_boundaries,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.16P processing boundaries are missing."
        )

    required_certified_boundaries = (
        "intake_validation_certified",
        "upstream_normalization_certified",
        "foundational_assembly_certified",
        "structured_reasoning_assembly_certified",
        "contextual_comparative_assembly_certified",
        "hybrid_integration_certified",
        "article_identity_alignment_certified",
        "cross_layer_provenance_alignment_certified",
        "cross_layer_state_index_construction_certified",
        "conflict_uncertainty_abstention_preservation_certified",
        "article_semantic_consolidation_certified",
        "final_article_semantic_consolidation_result_certified",
        "canonical_article_semantic_representation_certified",
        "all_15_layers_certified",
        "all_four_semantic_groups_certified",
        "source_authority_boundaries_certified",
        "full_layer_certification_performed",
    )

    for field in required_certified_boundaries:

        if processing_boundaries.get(
            field
        ) is not True:

            raise CertifiedSemanticArticleProfileBuilderError(
                "Required certified source boundary is not True: "
                + field
            )

    for field in forbidden_certification_true_fields:

        if processing_boundaries.get(
            field
        ) is not False:

            raise CertifiedSemanticArticleProfileBuilderError(
                "Certified source processing boundary is invalid: "
                + field
            )

    normalized_layers = certified_consolidation_result.get(
        "normalized_layers"
    )

    if not isinstance(
        normalized_layers,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified normalized layers are missing."
        )

    if (
        list(
            normalized_layers.keys()
        )
        != list(
            _SEMANTIC_ARTICLE_PROFILE_LAYER_ORDER
        )
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified source layer order is not canonical."
        )

    if len(
        normalized_layers
    ) != 15:

        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified source must contain exactly 15 semantic layers."
        )

    normalized_group_index = certified_consolidation_result.get(
        "normalized_group_index"
    )

    if not isinstance(
        normalized_group_index,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified normalized group index is missing."
        )

    expected_group_index = {
        group_name:
            list(
                members
            )
        for group_name, members in (
            _SEMANTIC_ARTICLE_PROFILE_GROUP_MEMBERSHIP.items()
        )
    }

    if (
        dict(
            normalized_group_index
        )
        != expected_group_index
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified semantic group index is not canonical."
        )

    representation = certified_consolidation_result.get(
        "canonical_article_semantic_representation"
    )

    if not isinstance(
        representation,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified canonical article semantic representation is missing."
        )

    if (
        representation.get(
            "representation_status"
        )
        != "ARTICLE_SEMANTIC_INTELLIGENCE_CONSOLIDATED"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Canonical article semantic representation is not consolidated."
        )

    if (
        representation.get(
            "canonical_article_identity"
        )
        != canonical_identity
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified article identity drifted inside representation."
        )

    if (
        representation.get(
            "canonical_layer_order"
        )
        != list(
            _SEMANTIC_ARTICLE_PROFILE_LAYER_ORDER
        )
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified representation layer order is invalid."
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
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified representation layer/group accounting is invalid."
        )

    canonical_payloads = representation.get(
        "canonical_layer_payloads"
    )

    if not isinstance(
        canonical_payloads,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified canonical layer payloads are missing."
        )

    for layer_name in (
        _SEMANTIC_ARTICLE_PROFILE_LAYER_ORDER
    ):

        envelope = normalized_layers.get(
            layer_name
        )

        if not isinstance(
            envelope,
            Mapping,
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                layer_name
                + " normalized envelope is invalid."
            )

        if (
            envelope.get(
                "phase"
            )
            != _SEMANTIC_ARTICLE_PROFILE_LAYER_PHASES[
                layer_name
            ]
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                layer_name
                + " phase authority drifted."
            )

        source_payload = envelope.get(
            "source_payload"
        )

        if not isinstance(
            source_payload,
            Mapping,
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                layer_name
                + " source payload is invalid."
            )

        if (
            canonical_payloads.get(
                layer_name
            )
            != source_payload
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                layer_name
                + " certified canonical payload drifted."
            )

    source_snapshot = deepcopy(
        dict(
            certified_consolidation_result
        )
    )

    return {
        "schema_version":
            "certified_semantic_article_profile_intake_v1",

        "version":
            CERTIFIED_SEMANTIC_ARTICLE_PROFILE_BUILDER_VERSION,

        "phase":
            CERTIFIED_SEMANTIC_ARTICLE_PROFILE_BUILDER_PHASE,

        "patch":
            "4.6.17D",

        "status":
            "CERTIFIED_CONSOLIDATION_INTAKE_VALIDATED",

        "canonical_article_identity":
            deepcopy(
                dict(
                    canonical_identity
                )
            ),

        "source_certification":
            deepcopy(
                dict(
                    certification
                )
            ),

        "source_processing_boundaries":
            deepcopy(
                dict(
                    processing_boundaries
                )
            ),

        "canonical_article_semantic_representation":
            deepcopy(
                dict(
                    representation
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

        "certified_source_artifacts": {
            artifact_name:
                deepcopy(
                    certified_consolidation_result[
                        artifact_name
                    ]
                )
            for artifact_name in (
                _SEMANTIC_ARTICLE_PROFILE_REQUIRED_SOURCE_ARTIFACTS
            )
        },

        "source_certified_consolidation_result":
            source_snapshot,

        "processing_boundaries": {
            "certified_source_validated":
                True,

            "certified_source_contract_preserved":
                True,

            "canonical_article_identity_preserved":
                True,

            "canonical_semantic_representation_preserved":
                True,

            "all_15_layers_preserved":
                True,

            "all_four_semantic_groups_preserved":
                True,

            "source_authority_boundaries_preserved":
                True,

            "profile_identity_assembly_performed":
                False,

            "semantic_layer_profile_assembly_performed":
                False,

            "semantic_group_profile_assembly_performed":
                False,

            "cross_layer_artifact_profile_assembly_performed":
                False,

            "governed_state_profile_assembly_performed":
                False,

            "profile_structural_index_construction_performed":
                False,

            "canonical_profile_assembly_performed":
                False,

            "final_profile_result_built":
                False,

            "profile_certification_performed":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
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

            "profile_store_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "profile_identity_source_authority_assembly",
    }


# =====================================================================
# PATCH 4.6.17E ? Profile Identity & Source Authority Assembly
# =====================================================================

def assemble_profile_identity_source_authority_v1(
    intake_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Assemble the Semantic Article Profile identity envelope and certified
    source-authority model.

    E performs structural identity/authority projection only.

    It does NOT:
    - build semantic layer profiles,
    - build semantic group profiles,
    - build cross-layer artifact profiles,
    - build governed-state profiles,
    - construct structural indexes,
    - assemble the canonical final profile,
    - certify the profile,
    - persist the profile,
    - modify semantic meaning,
    - perform new reasoning,
    - resolve conflict,
    - reinterpret uncertainty,
    - recalculate confidence,
    - create/remove abstention,
    - write Semantic Memory,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        intake_result,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "intake_result must be a mapping."
        )

    if (
        intake_result.get(
            "schema_version"
        )
        != "certified_semantic_article_profile_intake_v1"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17E requires certified_semantic_article_profile_intake_v1."
        )

    if (
        intake_result.get(
            "phase"
        )
        != "4.6.17"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17E requires Phase 4.6.17 input."
        )

    if (
        intake_result.get(
            "patch"
        )
        != "4.6.17D"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17E requires canonical 4.6.17D input."
        )

    if (
        intake_result.get(
            "status"
        )
        != "CERTIFIED_CONSOLIDATION_INTAKE_VALIDATED"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified consolidation intake has not been validated."
        )

    if (
        intake_result.get(
            "next_stage"
        )
        != "profile_identity_source_authority_assembly"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17D does not hand off to identity/source-authority assembly."
        )

    if (
        intake_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17E requires article-local transient intelligence."
        )

    boundaries = intake_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17D processing boundaries are missing."
        )

    required_true = (
        "certified_source_validated",
        "certified_source_contract_preserved",
        "canonical_article_identity_preserved",
        "canonical_semantic_representation_preserved",
        "all_15_layers_preserved",
        "all_four_semantic_groups_preserved",
        "source_authority_boundaries_preserved",
    )

    for field in required_true:

        if boundaries.get(
            field
        ) is not True:

            raise CertifiedSemanticArticleProfileBuilderError(
                "Required 4.6.17D boundary is not True: "
                + field
            )

    required_false = (
        "profile_identity_assembly_performed",
        "semantic_layer_profile_assembly_performed",
        "semantic_group_profile_assembly_performed",
        "cross_layer_artifact_profile_assembly_performed",
        "governed_state_profile_assembly_performed",
        "profile_structural_index_construction_performed",
        "canonical_profile_assembly_performed",
        "final_profile_result_built",
        "profile_certification_performed",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
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
        "profile_store_written",
        "linking_decisions_performed",
        "persistence_performed",
    )

    for field in required_false:

        if boundaries.get(
            field
        ) is not False:

            raise CertifiedSemanticArticleProfileBuilderError(
                "Forbidden 4.6.17D boundary is not False: "
                + field
            )

    canonical_identity = intake_result.get(
        "canonical_article_identity"
    )

    source_certification = intake_result.get(
        "source_certification"
    )

    source_boundaries = intake_result.get(
        "source_processing_boundaries"
    )

    representation = intake_result.get(
        "canonical_article_semantic_representation"
    )

    normalized_layers = intake_result.get(
        "normalized_layers"
    )

    normalized_group_index = intake_result.get(
        "normalized_group_index"
    )

    source_snapshot = intake_result.get(
        "source_certified_consolidation_result"
    )

    for name, value in (
        (
            "canonical_article_identity",
            canonical_identity,
        ),
        (
            "source_certification",
            source_certification,
        ),
        (
            "source_processing_boundaries",
            source_boundaries,
        ),
        (
            "canonical_article_semantic_representation",
            representation,
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
            "source_certified_consolidation_result",
            source_snapshot,
        ),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                name
                + " is missing or invalid."
            )

    article_id = canonical_identity.get(
        "article_id"
    )

    workspace_id = canonical_identity.get(
        "workspace_id"
    )

    if (
        not isinstance(
            article_id,
            str,
        )
        or not article_id.strip()
        or not isinstance(
            workspace_id,
            str,
        )
        or not workspace_id.strip()
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Canonical profile identity is incomplete."
        )

    source_identity = source_snapshot.get(
        "canonical_article_identity"
    )

    if source_identity != canonical_identity:
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified source identity drifted from the intake identity."
        )

    if (
        representation.get(
            "canonical_article_identity"
        )
        != canonical_identity
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Canonical semantic representation identity drifted."
        )

    if (
        source_certification.get(
            "certification_status"
        )
        != "CERTIFIED"
        or source_certification.get(
            "certified_phase"
        )
        != "4.6.16"
        or source_certification.get(
            "certified_source_patch"
        )
        != "4.6.16O"
        or source_certification.get(
            "all_15_layers_certified"
        )
        is not True
        or source_certification.get(
            "all_four_semantic_groups_certified"
        )
        is not True
        or source_certification.get(
            "canonical_identity_certified"
        )
        is not True
        or source_certification.get(
            "source_authority_boundaries_certified"
        )
        is not True
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified source authority prerequisites are invalid."
        )

    expected_layer_order = list(
        _SEMANTIC_ARTICLE_PROFILE_LAYER_ORDER
    )

    if (
        list(
            normalized_layers.keys()
        )
        != expected_layer_order
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified source layer order is invalid."
        )

    expected_group_index = {
        group_name:
            list(
                members
            )
        for group_name, members in (
            _SEMANTIC_ARTICLE_PROFILE_GROUP_MEMBERSHIP.items()
        )
    }

    if (
        dict(
            normalized_group_index
        )
        != expected_group_index
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified source group membership is invalid."
        )

    layer_authority_records = []

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
            raise CertifiedSemanticArticleProfileBuilderError(
                layer_name
                + " normalized layer envelope is invalid."
            )

        input_authority = envelope.get(
            "input_authority"
        )

        phase = envelope.get(
            "phase"
        )

        if (
            not isinstance(
                input_authority,
                str,
            )
            or not input_authority
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                layer_name
                + " input authority is missing."
            )

        if (
            phase
            != _SEMANTIC_ARTICLE_PROFILE_LAYER_PHASES[
                layer_name
            ]
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                layer_name
                + " phase identity drifted."
            )

        group_name = next(
            group_name
            for group_name, members in (
                _SEMANTIC_ARTICLE_PROFILE_GROUP_MEMBERSHIP.items()
            )
            if layer_name in members
        )

        layer_authority_records.append({
            "ordinal":
                ordinal,

            "layer_name":
                layer_name,

            "phase":
                phase,

            "semantic_group":
                group_name,

            "input_authority":
                input_authority,

            "authority_source":
                "CERTIFIED_4.6.16P_NORMALIZED_LAYER",

            "authority_preserved":
                True,

            "source_meaning_preserved":
                True,

            "authority_override_performed":
                False,

            "new_reasoning_performed":
                False,
        })

    profile_identity = {
        "profile_identity_status":
            "PROFILE_IDENTITY_ASSEMBLED",

        "article_id":
            article_id,

        "workspace_id":
            workspace_id,

        "canonical_article_identity":
            deepcopy(
                dict(
                    canonical_identity
                )
            ),

        "identity_authority":
            "4.6.16P_CANONICAL_ARTICLE_IDENTITY",

        "identity_source_phase":
            "4.6.16",

        "identity_source_patch":
            "4.6.16P",

        "identity_certified":
            True,

        "identity_preserved":
            True,

        "identity_rewritten":
            False,

        "identity_inference_performed":
            False,
    }

    source_authority_profile = {
        "source_authority_status":
            "SOURCE_AUTHORITY_PROFILE_ASSEMBLED",

        "primary_input_authority":
            "CERTIFIED_4.6.16P_ARTICLE_SEMANTIC_CONSOLIDATION",

        "canonical_identity_authority":
            "4.6.16P_CANONICAL_ARTICLE_IDENTITY",

        "canonical_semantic_representation_authority":
            "4.6.16P_CANONICAL_ARTICLE_SEMANTIC_REPRESENTATION",

        "provenance_authority":
            "4.6.16P_CROSS_LAYER_PROVENANCE_ALIGNMENT",

        "state_index_authority":
            "4.6.16P_CROSS_LAYER_STATE_INDEXES",

        "uncertainty_authority":
            "CERTIFIED_4.6.14_UNCERTAINTY_INTELLIGENCE_VIA_4.6.16P",

        "hybrid_governance_authority":
            "FROZEN_4.6.15S_HYBRID_STATE_VIA_4.6.16P",

        "profile_certification_authority":
            "4.6.18_PROFILE_CERTIFICATION",

        "profile_persistence_authority":
            "4.6.19_PROFILE_STORE",

        "source_certification_status":
            source_certification[
                "certification_status"
            ],

        "source_certification_scope":
            source_certification[
                "certification_scope"
            ],

        "source_certified_phase":
            source_certification[
                "certified_phase"
            ],

        "source_certified_patch":
            source_certification[
                "certified_source_patch"
            ],

        "source_layer_count":
            15,

        "source_group_count":
            4,

        "layer_authority_records":
            layer_authority_records,

        "source_authority_boundaries_preserved":
            True,

        "authority_override_performed":
            False,

        "profile_certification_performed":
            False,

        "profile_persistence_performed":
            False,
    }

    return {
        "schema_version":
            "semantic_article_profile_identity_authority_v1",

        "version":
            CERTIFIED_SEMANTIC_ARTICLE_PROFILE_BUILDER_VERSION,

        "phase":
            CERTIFIED_SEMANTIC_ARTICLE_PROFILE_BUILDER_PHASE,

        "patch":
            "4.6.17E",

        "status":
            "PROFILE_IDENTITY_SOURCE_AUTHORITY_ASSEMBLED",

        "profile_identity":
            profile_identity,

        "source_authority_profile":
            source_authority_profile,

        "canonical_article_identity":
            deepcopy(
                dict(
                    canonical_identity
                )
            ),

        "source_certification":
            deepcopy(
                dict(
                    source_certification
                )
            ),

        "canonical_article_semantic_representation":
            deepcopy(
                dict(
                    representation
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

        "source_intake_result":
            deepcopy(
                dict(
                    intake_result
                )
            ),

        "processing_boundaries": {
            "certified_source_validation_preserved":
                True,

            "profile_identity_assembly_performed":
                True,

            "source_authority_assembly_performed":
                True,

            "canonical_article_identity_preserved":
                True,

            "canonical_semantic_representation_preserved":
                True,

            "all_15_layer_authorities_preserved":
                True,

            "all_four_semantic_group_boundaries_preserved":
                True,

            "source_authority_boundaries_preserved":
                True,

            "semantic_layer_profile_assembly_performed":
                False,

            "semantic_group_profile_assembly_performed":
                False,

            "cross_layer_artifact_profile_assembly_performed":
                False,

            "governed_state_profile_assembly_performed":
                False,

            "profile_structural_index_construction_performed":
                False,

            "canonical_profile_assembly_performed":
                False,

            "final_profile_result_built":
                False,

            "profile_certification_performed":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "source_authority_override_performed":
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

            "profile_store_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "semantic_layer_group_profile_assembly",
    }


# =====================================================================
# PATCH 4.6.17F ? Semantic Layer / Group Profile Assembly
# =====================================================================

def assemble_semantic_layer_group_profiles_v1(
    identity_authority_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Build deterministic profile-oriented views of the 15 certified
    Semantic Intelligence layers and four certified semantic groups.

    F performs structural projection only.

    It does NOT:
    - perform new semantic reasoning,
    - change source meaning,
    - change source authority,
    - merge conclusions across layers,
    - resolve conflict,
    - adjudicate contradiction,
    - reinterpret uncertainty,
    - recalculate confidence,
    - create/remove abstention,
    - build cross-layer artifact profiles,
    - build governed-state profiles,
    - construct final structural indexes,
    - assemble the canonical final profile,
    - certify the profile,
    - persist the profile,
    - write Semantic Memory,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        identity_authority_result,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "identity_authority_result must be a mapping."
        )

    if (
        identity_authority_result.get(
            "schema_version"
        )
        != "semantic_article_profile_identity_authority_v1"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17F requires semantic_article_profile_identity_authority_v1."
        )

    if (
        identity_authority_result.get(
            "phase"
        )
        != "4.6.17"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17F requires Phase 4.6.17 input."
        )

    if (
        identity_authority_result.get(
            "patch"
        )
        != "4.6.17E"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17F requires canonical 4.6.17E input."
        )

    if (
        identity_authority_result.get(
            "status"
        )
        != "PROFILE_IDENTITY_SOURCE_AUTHORITY_ASSEMBLED"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Profile identity/source authority has not been assembled."
        )

    if (
        identity_authority_result.get(
            "next_stage"
        )
        != "semantic_layer_group_profile_assembly"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17E does not hand off to semantic layer/group assembly."
        )

    if (
        identity_authority_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17F requires article-local transient intelligence."
        )

    boundaries = identity_authority_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17E processing boundaries are missing."
        )

    for field in (
        "certified_source_validation_preserved",
        "profile_identity_assembly_performed",
        "source_authority_assembly_performed",
        "canonical_article_identity_preserved",
        "canonical_semantic_representation_preserved",
        "all_15_layer_authorities_preserved",
        "all_four_semantic_group_boundaries_preserved",
        "source_authority_boundaries_preserved",
    ):

        if boundaries.get(
            field
        ) is not True:

            raise CertifiedSemanticArticleProfileBuilderError(
                "Required 4.6.17E boundary is not True: "
                + field
            )

    for field in (
        "semantic_layer_profile_assembly_performed",
        "semantic_group_profile_assembly_performed",
        "cross_layer_artifact_profile_assembly_performed",
        "governed_state_profile_assembly_performed",
        "profile_structural_index_construction_performed",
        "canonical_profile_assembly_performed",
        "final_profile_result_built",
        "profile_certification_performed",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "source_authority_override_performed",
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
        "profile_store_written",
        "linking_decisions_performed",
        "persistence_performed",
    ):

        if boundaries.get(
            field
        ) is not False:

            raise CertifiedSemanticArticleProfileBuilderError(
                "Forbidden 4.6.17E boundary is not False: "
                + field
            )

    profile_identity = identity_authority_result.get(
        "profile_identity"
    )

    source_authority_profile = identity_authority_result.get(
        "source_authority_profile"
    )

    canonical_identity = identity_authority_result.get(
        "canonical_article_identity"
    )

    representation = identity_authority_result.get(
        "canonical_article_semantic_representation"
    )

    normalized_layers = identity_authority_result.get(
        "normalized_layers"
    )

    normalized_group_index = identity_authority_result.get(
        "normalized_group_index"
    )

    for name, value in (
        (
            "profile_identity",
            profile_identity,
        ),
        (
            "source_authority_profile",
            source_authority_profile,
        ),
        (
            "canonical_article_identity",
            canonical_identity,
        ),
        (
            "canonical_article_semantic_representation",
            representation,
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
            raise CertifiedSemanticArticleProfileBuilderError(
                name
                + " is missing or invalid."
            )

    if (
        profile_identity.get(
            "canonical_article_identity"
        )
        != canonical_identity
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Profile identity drifted from canonical article identity."
        )

    if (
        source_authority_profile.get(
            "source_layer_count"
        )
        != 15
        or source_authority_profile.get(
            "source_group_count"
        )
        != 4
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Source authority layer/group accounting is invalid."
        )

    expected_layer_order = list(
        _SEMANTIC_ARTICLE_PROFILE_LAYER_ORDER
    )

    if (
        list(
            normalized_layers.keys()
        )
        != expected_layer_order
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Normalized layer order is not canonical."
        )

    canonical_payloads = representation.get(
        "canonical_layer_payloads"
    )

    semantic_groups = representation.get(
        "semantic_groups"
    )

    if not isinstance(
        canonical_payloads,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Canonical layer payloads are missing."
        )

    if not isinstance(
        semantic_groups,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Canonical semantic groups are missing."
        )

    if (
        list(
            canonical_payloads.keys()
        )
        != expected_layer_order
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Canonical payload order is invalid."
        )

    expected_group_order = list(
        _SEMANTIC_ARTICLE_PROFILE_SOURCE_GROUP_ORDER
    )

    if (
        list(
            semantic_groups.keys()
        )
        != expected_group_order
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Canonical semantic-group order is invalid."
        )

    expected_group_index = {
        group_name:
            list(
                members
            )
        for group_name, members in (
            _SEMANTIC_ARTICLE_PROFILE_GROUP_MEMBERSHIP.items()
        )
    }

    if (
        dict(
            normalized_group_index
        )
        != expected_group_index
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Normalized semantic-group membership drifted."
        )

    authority_records = source_authority_profile.get(
        "layer_authority_records"
    )

    if (
        not isinstance(
            authority_records,
            list,
        )
        or len(
            authority_records
        )
        != 15
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Layer authority records are incomplete."
        )

    authority_by_layer = {
        record.get(
            "layer_name"
        ):
            record
        for record in authority_records
        if isinstance(
            record,
            Mapping,
        )
    }

    if set(
        authority_by_layer.keys()
    ) != set(
        expected_layer_order
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Layer authority record accounting is invalid."
        )

    # -------------------------------------------------------------
    # Build 15 layer profile records.
    # -------------------------------------------------------------

    layer_profile_records = []

    for ordinal, layer_name in enumerate(
        expected_layer_order,
        1,
    ):

        envelope = normalized_layers[
            layer_name
        ]

        source_payload = envelope.get(
            "source_payload"
        )

        if not isinstance(
            envelope,
            Mapping,
        ) or not isinstance(
            source_payload,
            Mapping,
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                layer_name
                + " certified layer source is invalid."
            )

        if (
            canonical_payloads.get(
                layer_name
            )
            != source_payload
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                layer_name
                + " canonical payload drifted."
            )

        authority_record = authority_by_layer[
            layer_name
        ]

        if (
            authority_record.get(
                "ordinal"
            )
            != ordinal
            or authority_record.get(
                "phase"
            )
            != _SEMANTIC_ARTICLE_PROFILE_LAYER_PHASES[
                layer_name
            ]
            or authority_record.get(
                "input_authority"
            )
            != envelope.get(
                "input_authority"
            )
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                layer_name
                + " authority record drifted."
            )

        group_name = authority_record.get(
            "semantic_group"
        )

        if (
            group_name
            not in _SEMANTIC_ARTICLE_PROFILE_GROUP_MEMBERSHIP
            or layer_name
            not in _SEMANTIC_ARTICLE_PROFILE_GROUP_MEMBERSHIP[
                group_name
            ]
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                layer_name
                + " semantic-group membership is invalid."
            )

        layer_profile_records.append({
            "profile_layer_id":
                "SAP_LAYER:"
                + str(
                    ordinal
                ),

            "ordinal":
                ordinal,

            "layer_name":
                layer_name,

            "phase":
                envelope.get(
                    "phase"
                ),

            "semantic_group":
                group_name,

            "schema_version":
                envelope.get(
                    "schema_version"
                ),

            "patch":
                envelope.get(
                    "patch"
                ),

            "status":
                envelope.get(
                    "status"
                ),

            "source_next_stage":
                envelope.get(
                    "source_next_stage"
                ),

            "input_authority":
                envelope.get(
                    "input_authority"
                ),

            "certified_source_envelope":
                deepcopy(
                    dict(
                        envelope
                    )
                ),

            "certified_source_payload":
                deepcopy(
                    dict(
                        source_payload
                    )
                ),

            "source_payload_preserved":
                True,

            "source_meaning_preserved":
                True,

            "source_authority_preserved":
                True,

            "semantic_projection_only":
                True,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "new_relation_inference_performed":
                False,
        })

    # -------------------------------------------------------------
    # Build four semantic-group profile records.
    # -------------------------------------------------------------

    layer_profile_by_name = {
        record[
            "layer_name"
        ]:
            record
        for record in layer_profile_records
    }

    group_profile_records = []

    for group_ordinal, group_name in enumerate(
        expected_group_order,
        1,
    ):

        member_layers = list(
            _SEMANTIC_ARTICLE_PROFILE_GROUP_MEMBERSHIP[
                group_name
            ]
        )

        certified_group_payload = semantic_groups.get(
            group_name
        )

        if not isinstance(
            certified_group_payload,
            Mapping,
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                group_name
                + " certified semantic group is invalid."
            )

        group_profile_records.append({
            "profile_group_id":
                "SAP_GROUP:"
                + str(
                    group_ordinal
                ),

            "ordinal":
                group_ordinal,

            "group_name":
                group_name,

            "member_layer_count":
                len(
                    member_layers
                ),

            "member_layer_order":
                deepcopy(
                    member_layers
                ),

            "member_layer_profiles": [
                deepcopy(
                    layer_profile_by_name[
                        layer_name
                    ]
                )
                for layer_name in member_layers
            ],

            "certified_source_group":
                deepcopy(
                    dict(
                        certified_group_payload
                    )
                ),

            "source_group_preserved":
                True,

            "member_layer_order_preserved":
                True,

            "source_meaning_preserved":
                True,

            "semantic_merge_performed":
                False,

            "cross_layer_reasoning_performed":
                False,

            "new_reasoning_performed":
                False,
        })

    semantic_layer_profile = {
        "profile_status":
            "SEMANTIC_LAYER_PROFILE_ASSEMBLED",

        "layer_count":
            15,

        "canonical_layer_order":
            deepcopy(
                expected_layer_order
            ),

        "layer_records":
            layer_profile_records,

        "all_layer_payloads_preserved":
            True,

        "all_layer_authorities_preserved":
            True,

        "semantic_state_modified":
            False,

        "semantic_meaning_rewritten":
            False,

        "cross_layer_reasoning_performed":
            False,
    }

    semantic_group_profile = {
        "profile_status":
            "SEMANTIC_GROUP_PROFILE_ASSEMBLED",

        "group_count":
            4,

        "canonical_group_order":
            deepcopy(
                expected_group_order
            ),

        "group_records":
            group_profile_records,

        "all_group_payloads_preserved":
            True,

        "all_group_memberships_preserved":
            True,

        "semantic_merge_performed":
            False,

        "cross_layer_reasoning_performed":
            False,
    }

    return {
        "schema_version":
            "semantic_article_profile_layer_group_assembly_v1",

        "version":
            CERTIFIED_SEMANTIC_ARTICLE_PROFILE_BUILDER_VERSION,

        "phase":
            CERTIFIED_SEMANTIC_ARTICLE_PROFILE_BUILDER_PHASE,

        "patch":
            "4.6.17F",

        "status":
            "SEMANTIC_LAYER_GROUP_PROFILES_ASSEMBLED",

        "profile_identity":
            deepcopy(
                dict(
                    profile_identity
                )
            ),

        "source_authority_profile":
            deepcopy(
                dict(
                    source_authority_profile
                )
            ),

        "semantic_layer_profile":
            semantic_layer_profile,

        "semantic_group_profile":
            semantic_group_profile,

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

        "source_identity_authority_result":
            deepcopy(
                dict(
                    identity_authority_result
                )
            ),

        "processing_boundaries": {
            "certified_source_validation_preserved":
                True,

            "profile_identity_assembly_preserved":
                True,

            "source_authority_assembly_preserved":
                True,

            "semantic_layer_profile_assembly_performed":
                True,

            "semantic_group_profile_assembly_performed":
                True,

            "all_15_layer_profiles_assembled":
                True,

            "all_four_group_profiles_assembled":
                True,

            "canonical_layer_order_preserved":
                True,

            "canonical_group_order_preserved":
                True,

            "source_payloads_preserved":
                True,

            "source_authority_boundaries_preserved":
                True,

            "cross_layer_artifact_profile_assembly_performed":
                False,

            "governed_state_profile_assembly_performed":
                False,

            "profile_structural_index_construction_performed":
                False,

            "canonical_profile_assembly_performed":
                False,

            "final_profile_result_built":
                False,

            "profile_certification_performed":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "source_authority_override_performed":
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

            "profile_store_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "cross_layer_artifact_profile_assembly",
    }


# =====================================================================
# PATCH 4.6.17G ? Cross-Layer Artifact Profile Assembly
# =====================================================================

def assemble_cross_layer_artifact_profile_v1(
    layer_group_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Project the certified 4.6.16 cross-layer artifacts into the
    Semantic Article Profile without recomputation.

    G profiles:
    - article identity alignment,
    - cross-layer provenance alignment,
    - cross-layer state indexes,
    - conflict / uncertainty / abstention preservation.

    G does NOT:
    - re-align identities,
    - rebuild provenance,
    - rebuild state indexes,
    - re-resolve conflict,
    - reinterpret uncertainty,
    - recalculate confidence,
    - create/remove abstention,
    - perform new reasoning,
    - certify or persist the profile.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        layer_group_result,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "layer_group_result must be a mapping."
        )

    if (
        layer_group_result.get(
            "schema_version"
        )
        != "semantic_article_profile_layer_group_assembly_v1"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17G requires "
            "semantic_article_profile_layer_group_assembly_v1."
        )

    if (
        layer_group_result.get(
            "phase"
        )
        != "4.6.17"
        or layer_group_result.get(
            "patch"
        )
        != "4.6.17F"
        or layer_group_result.get(
            "status"
        )
        != "SEMANTIC_LAYER_GROUP_PROFILES_ASSEMBLED"
        or layer_group_result.get(
            "next_stage"
        )
        != "cross_layer_artifact_profile_assembly"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17F lifecycle contract is invalid."
        )

    if (
        layer_group_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17G requires transient article-local intelligence."
        )

    boundaries = layer_group_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17F processing boundaries are missing."
        )

    for field in (
        "certified_source_validation_preserved",
        "profile_identity_assembly_preserved",
        "source_authority_assembly_preserved",
        "semantic_layer_profile_assembly_performed",
        "semantic_group_profile_assembly_performed",
        "all_15_layer_profiles_assembled",
        "all_four_group_profiles_assembled",
        "canonical_layer_order_preserved",
        "canonical_group_order_preserved",
        "source_payloads_preserved",
        "source_authority_boundaries_preserved",
    ):

        if boundaries.get(
            field
        ) is not True:
            raise CertifiedSemanticArticleProfileBuilderError(
                "Required 4.6.17F boundary is not True: "
                + field
            )

    for field in (
        "cross_layer_artifact_profile_assembly_performed",
        "governed_state_profile_assembly_performed",
        "profile_structural_index_construction_performed",
        "canonical_profile_assembly_performed",
        "final_profile_result_built",
        "profile_certification_performed",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "source_authority_override_performed",
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
        "profile_store_written",
        "linking_decisions_performed",
        "persistence_performed",
    ):

        if boundaries.get(
            field
        ) is not False:
            raise CertifiedSemanticArticleProfileBuilderError(
                "Forbidden 4.6.17F boundary is not False: "
                + field
            )

    profile_identity = layer_group_result.get(
        "profile_identity"
    )

    source_authority_profile = layer_group_result.get(
        "source_authority_profile"
    )

    semantic_layer_profile = layer_group_result.get(
        "semantic_layer_profile"
    )

    semantic_group_profile = layer_group_result.get(
        "semantic_group_profile"
    )

    representation = layer_group_result.get(
        "canonical_article_semantic_representation"
    )

    for name, value in (
        (
            "profile_identity",
            profile_identity,
        ),
        (
            "source_authority_profile",
            source_authority_profile,
        ),
        (
            "semantic_layer_profile",
            semantic_layer_profile,
        ),
        (
            "semantic_group_profile",
            semantic_group_profile,
        ),
        (
            "canonical_article_semantic_representation",
            representation,
        ),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                name + " is missing or invalid."
            )

    cross_layer_artifacts = representation.get(
        "cross_layer_artifacts"
    )

    if not isinstance(
        cross_layer_artifacts,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified cross-layer artifacts are missing."
        )

    expected_artifact_order = (
        "article_identity_alignment",
        "provenance_alignment",
        "state_indexes",
        "conflict_uncertainty_abstention_preservation",
    )

    if (
        list(
            cross_layer_artifacts.keys()
        )
        != list(
            expected_artifact_order
        )
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified cross-layer artifact order is invalid."
        )

    identity_alignment = cross_layer_artifacts.get(
        "article_identity_alignment"
    )

    provenance_alignment = cross_layer_artifacts.get(
        "provenance_alignment"
    )

    state_indexes = cross_layer_artifacts.get(
        "state_indexes"
    )

    preservation = cross_layer_artifacts.get(
        "conflict_uncertainty_abstention_preservation"
    )

    for name, value in (
        (
            "article_identity_alignment",
            identity_alignment,
        ),
        (
            "provenance_alignment",
            provenance_alignment,
        ),
        (
            "state_indexes",
            state_indexes,
        ),
        (
            "conflict_uncertainty_abstention_preservation",
            preservation,
        ),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                name + " artifact is invalid."
            )

    if (
        identity_alignment.get(
            "alignment_status"
        )
        != "CROSS_LAYER_ARTICLE_IDENTITY_ALIGNED"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified identity alignment is invalid."
        )

    if (
        provenance_alignment.get(
            "alignment_status"
        )
        != "CROSS_LAYER_PROVENANCE_ALIGNED"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified provenance alignment is invalid."
        )

    if (
        state_indexes.get(
            "construction_status"
        )
        != "CROSS_LAYER_STATE_INDEXES_CONSTRUCTED"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified state indexes are invalid."
        )

    if (
        preservation.get(
            "preservation_status"
        )
        != "CONFLICT_UNCERTAINTY_ABSTENTION_PRESERVED"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified governed-state preservation is invalid."
        )

    artifact_records = [
        {
            "profile_artifact_id":
                "SAP_ARTIFACT:1",

            "ordinal":
                1,

            "artifact_name":
                "article_identity_alignment",

            "artifact_authority":
                "4.6.16P_CERTIFIED_ARTICLE_IDENTITY_ALIGNMENT",

            "certified_source_artifact":
                deepcopy(
                    dict(
                        identity_alignment
                    )
                ),

            "artifact_preserved":
                True,

            "artifact_recomputed":
                False,

            "new_reasoning_performed":
                False,
        },
        {
            "profile_artifact_id":
                "SAP_ARTIFACT:2",

            "ordinal":
                2,

            "artifact_name":
                "provenance_alignment",

            "artifact_authority":
                "4.6.16P_CERTIFIED_CROSS_LAYER_PROVENANCE_ALIGNMENT",

            "certified_source_artifact":
                deepcopy(
                    dict(
                        provenance_alignment
                    )
                ),

            "artifact_preserved":
                True,

            "artifact_recomputed":
                False,

            "new_reasoning_performed":
                False,
        },
        {
            "profile_artifact_id":
                "SAP_ARTIFACT:3",

            "ordinal":
                3,

            "artifact_name":
                "state_indexes",

            "artifact_authority":
                "4.6.16P_CERTIFIED_CROSS_LAYER_STATE_INDEXES",

            "certified_source_artifact":
                deepcopy(
                    dict(
                        state_indexes
                    )
                ),

            "artifact_preserved":
                True,

            "artifact_recomputed":
                False,

            "new_reasoning_performed":
                False,
        },
        {
            "profile_artifact_id":
                "SAP_ARTIFACT:4",

            "ordinal":
                4,

            "artifact_name":
                "conflict_uncertainty_abstention_preservation",

            "artifact_authority":
                "4.6.16P_CERTIFIED_GOVERNED_STATE_PRESERVATION",

            "certified_source_artifact":
                deepcopy(
                    dict(
                        preservation
                    )
                ),

            "artifact_preserved":
                True,

            "artifact_recomputed":
                False,

            "new_reasoning_performed":
                False,
        },
    ]

    cross_layer_artifact_profile = {
        "profile_status":
            "CROSS_LAYER_ARTIFACT_PROFILE_ASSEMBLED",

        "artifact_count":
            4,

        "canonical_artifact_order":
            list(
                expected_artifact_order
            ),

        "artifact_records":
            artifact_records,

        "identity_alignment_preserved":
            True,

        "provenance_alignment_preserved":
            True,

        "state_indexes_preserved":
            True,

        "governed_state_preservation_artifact_preserved":
            True,

        "artifact_recomputation_performed":
            False,

        "provenance_rebuild_performed":
            False,

        "state_index_rebuild_performed":
            False,

        "conflict_resolution_performed":
            False,

        "uncertainty_reinterpretation_performed":
            False,

        "confidence_recalculation_performed":
            False,

        "new_reasoning_performed":
            False,
    }

    return {
        "schema_version":
            "semantic_article_profile_cross_layer_artifact_assembly_v1",

        "version":
            CERTIFIED_SEMANTIC_ARTICLE_PROFILE_BUILDER_VERSION,

        "phase":
            CERTIFIED_SEMANTIC_ARTICLE_PROFILE_BUILDER_PHASE,

        "patch":
            "4.6.17G",

        "status":
            "CROSS_LAYER_ARTIFACT_PROFILE_ASSEMBLED",

        "profile_identity":
            deepcopy(
                dict(
                    profile_identity
                )
            ),

        "source_authority_profile":
            deepcopy(
                dict(
                    source_authority_profile
                )
            ),

        "semantic_layer_profile":
            deepcopy(
                dict(
                    semantic_layer_profile
                )
            ),

        "semantic_group_profile":
            deepcopy(
                dict(
                    semantic_group_profile
                )
            ),

        "cross_layer_artifact_profile":
            cross_layer_artifact_profile,

        "canonical_article_identity":
            deepcopy(
                dict(
                    layer_group_result[
                        "canonical_article_identity"
                    ]
                )
            ),

        "canonical_article_semantic_representation":
            deepcopy(
                dict(
                    representation
                )
            ),

        "normalized_layers":
            deepcopy(
                dict(
                    layer_group_result[
                        "normalized_layers"
                    ]
                )
            ),

        "normalized_group_index":
            deepcopy(
                dict(
                    layer_group_result[
                        "normalized_group_index"
                    ]
                )
            ),

        "source_layer_group_result":
            deepcopy(
                dict(
                    layer_group_result
                )
            ),

        "processing_boundaries": {
            "certified_source_validation_preserved":
                True,

            "profile_identity_assembly_preserved":
                True,

            "source_authority_assembly_preserved":
                True,

            "semantic_layer_profile_assembly_preserved":
                True,

            "semantic_group_profile_assembly_preserved":
                True,

            "cross_layer_artifact_profile_assembly_performed":
                True,

            "all_four_cross_layer_artifacts_profiled":
                True,

            "identity_alignment_preserved":
                True,

            "provenance_alignment_preserved":
                True,

            "state_indexes_preserved":
                True,

            "governed_state_preservation_artifact_preserved":
                True,

            "governed_state_profile_assembly_performed":
                False,

            "profile_structural_index_construction_performed":
                False,

            "canonical_profile_assembly_performed":
                False,

            "final_profile_result_built":
                False,

            "profile_certification_performed":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "source_authority_override_performed":
                False,

            "artifact_recomputation_performed":
                False,

            "provenance_rebuild_performed":
                False,

            "upstream_index_rebuild_performed":
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

            "profile_store_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "governed_state_profile_assembly",
    }


# =====================================================================
# PATCH 4.6.17H ? Governed State Profile Assembly
# =====================================================================

def assemble_governed_state_profile_v1(
    artifact_profile_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Assemble a profile-oriented view of already-certified governed
    semantic state.

    H profiles existing:
    - governed conflict state,
    - uncertainty state,
    - unresolved state,
    - abstention state,
    - confidence classification state,
    - article-level governed-state flags.

    H does NOT:
    - detect new conflict,
    - resolve or re-resolve conflict,
    - infer uncertainty,
    - strengthen or weaken uncertainty,
    - calculate unified Semantic Confidence,
    - recalculate confidence,
    - create or remove abstention,
    - synthesize new facts,
    - perform new semantic reasoning,
    - certify or persist the profile.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        artifact_profile_result,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "artifact_profile_result must be a mapping."
        )

    if (
        artifact_profile_result.get(
            "schema_version"
        )
        != "semantic_article_profile_cross_layer_artifact_assembly_v1"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17H requires "
            "semantic_article_profile_cross_layer_artifact_assembly_v1."
        )

    if (
        artifact_profile_result.get(
            "phase"
        )
        != "4.6.17"
        or artifact_profile_result.get(
            "patch"
        )
        != "4.6.17G"
        or artifact_profile_result.get(
            "status"
        )
        != "CROSS_LAYER_ARTIFACT_PROFILE_ASSEMBLED"
        or artifact_profile_result.get(
            "next_stage"
        )
        != "governed_state_profile_assembly"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17G lifecycle contract is invalid."
        )

    if (
        artifact_profile_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17H requires article-local transient intelligence."
        )

    boundaries = artifact_profile_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17G processing boundaries are missing."
        )

    for field in (
        "certified_source_validation_preserved",
        "profile_identity_assembly_preserved",
        "source_authority_assembly_preserved",
        "semantic_layer_profile_assembly_preserved",
        "semantic_group_profile_assembly_preserved",
        "cross_layer_artifact_profile_assembly_performed",
        "all_four_cross_layer_artifacts_profiled",
        "identity_alignment_preserved",
        "provenance_alignment_preserved",
        "state_indexes_preserved",
        "governed_state_preservation_artifact_preserved",
    ):

        if boundaries.get(
            field
        ) is not True:
            raise CertifiedSemanticArticleProfileBuilderError(
                "Required 4.6.17G boundary is not True: "
                + field
            )

    for field in (
        "governed_state_profile_assembly_performed",
        "profile_structural_index_construction_performed",
        "canonical_profile_assembly_performed",
        "final_profile_result_built",
        "profile_certification_performed",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "source_authority_override_performed",
        "artifact_recomputation_performed",
        "provenance_rebuild_performed",
        "upstream_index_rebuild_performed",
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
        "profile_store_written",
        "linking_decisions_performed",
        "persistence_performed",
    ):

        if boundaries.get(
            field
        ) is not False:
            raise CertifiedSemanticArticleProfileBuilderError(
                "Forbidden 4.6.17G boundary is not False: "
                + field
            )

    artifact_profile = artifact_profile_result.get(
        "cross_layer_artifact_profile"
    )

    representation = artifact_profile_result.get(
        "canonical_article_semantic_representation"
    )

    normalized_layers = artifact_profile_result.get(
        "normalized_layers"
    )

    for name, value in (
        (
            "cross_layer_artifact_profile",
            artifact_profile,
        ),
        (
            "canonical_article_semantic_representation",
            representation,
        ),
        (
            "normalized_layers",
            normalized_layers,
        ),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                name + " is missing or invalid."
            )

    artifact_records = artifact_profile.get(
        "artifact_records"
    )

    if (
        not isinstance(
            artifact_records,
            list,
        )
        or len(
            artifact_records
        )
        != 4
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Cross-layer artifact profile is incomplete."
        )

    artifact_by_name = {
        record.get(
            "artifact_name"
        ):
            record.get(
                "certified_source_artifact"
            )
        for record in artifact_records
        if isinstance(
            record,
            Mapping,
        )
    }

    representation_cross_layer_artifacts = representation.get(
        "cross_layer_artifacts"
    )

    if not isinstance(
        representation_cross_layer_artifacts,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Canonical representation cross-layer artifacts are missing."
        )

    expected_artifact_names = (
        "article_identity_alignment",
        "provenance_alignment",
        "state_indexes",
        "conflict_uncertainty_abstention_preservation",
    )

    if (
        list(
            representation_cross_layer_artifacts.keys()
        )
        != list(
            expected_artifact_names
        )
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Canonical representation cross-layer artifact order drifted."
        )

    if set(
        artifact_by_name.keys()
    ) != set(
        expected_artifact_names
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Profiled cross-layer artifact accounting is invalid."
        )

    for artifact_name in expected_artifact_names:

        if (
            artifact_by_name[
                artifact_name
            ]
            != representation_cross_layer_artifacts[
                artifact_name
            ]
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                artifact_name
                + " profiled artifact drifted from the canonical "
                "article semantic representation."
            )

    preservation = artifact_by_name.get(
        "conflict_uncertainty_abstention_preservation"
    )

    if not isinstance(
        preservation,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Governed-state preservation artifact is missing."
        )

    if (
        preservation.get(
            "preservation_status"
        )
        != "CONFLICT_UNCERTAINTY_ABSTENTION_PRESERVED"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Governed-state preservation artifact is invalid."
        )

    uncertainty_envelope = normalized_layers.get(
        "uncertainty_intelligence"
    )

    hybrid_envelope = normalized_layers.get(
        "symbolic_neural_hybrid_intelligence"
    )

    if not isinstance(
        uncertainty_envelope,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified uncertainty layer is missing."
        )

    if not isinstance(
        hybrid_envelope,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified hybrid layer is missing."
        )

    uncertainty_payload = uncertainty_envelope.get(
        "source_payload"
    )

    hybrid_payload = hybrid_envelope.get(
        "source_payload"
    )

    if not isinstance(
        uncertainty_payload,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified uncertainty payload is invalid."
        )

    if not isinstance(
        hybrid_payload,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified hybrid payload is invalid."
        )

    if (
        uncertainty_payload.get(
            "status"
        )
        != "UNCERTAINTY_INTELLIGENCE_CERTIFIED"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Uncertainty Intelligence source is not certified."
        )

    if (
        hybrid_payload.get(
            "status"
        )
        != "SYMBOLIC_NEURAL_HYBRID_INTELLIGENCE_RESULT_READY"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Hybrid Intelligence source is not ready."
        )

    hybrid_final = hybrid_payload.get(
        "final_symbolic_neural_hybrid_intelligence"
    )

    if not isinstance(
        hybrid_final,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Final hybrid governed state is missing."
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

    for field_name, values in (
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
                values,
                list,
            )
            or not all(
                isinstance(
                    value,
                    str,
                )
                and value
                for value in values
            )
            or len(
                values
            )
            != len(
                set(
                    values
                )
            )
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                field_name
                + " must be a unique string list."
            )

    if unresolved_ids != abstention_ids:
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified unresolved and abstention states diverged."
        )

    if (
        hybrid_final.get(
            "governed_conflict_candidate_ids"
        )
        != conflict_ids
        or hybrid_final.get(
            "unresolved_candidate_ids"
        )
        != unresolved_ids
        or hybrid_final.get(
            "abstention_candidate_ids"
        )
        != abstention_ids
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Hybrid governed state drifted from preservation authority."
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

    for source in (
        preservation,
        hybrid_final,
    ):

        if (
            source.get(
                "article_has_symbolically_governed_conflict"
            )
            is not expected_conflict_flag
            or source.get(
                "article_has_unresolved_hybrid_evidence"
            )
            is not expected_unresolved_flag
            or source.get(
                "article_requires_hybrid_abstention"
            )
            is not expected_abstention_flag
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                "Certified governed-state flags are inconsistent."
            )

    confidence_class_index = hybrid_final.get(
        "confidence_class_index",
        {}
    )

    if not isinstance(
        confidence_class_index,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified hybrid confidence-class index is invalid."
        )

    final_uncertainty_summary = uncertainty_payload.get(
        "final_uncertainty_summary"
    )

    if (
        final_uncertainty_summary is not None
        and not isinstance(
            final_uncertainty_summary,
            Mapping,
        )
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Certified uncertainty summary is invalid."
        )

    if (
        isinstance(
            final_uncertainty_summary,
            Mapping,
        )
        and final_uncertainty_summary.get(
            "unified_semantic_confidence_calculated"
        )
        is True
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Upstream uncertainty layer illegally calculated unified "
            "Semantic Confidence."
        )

    governed_state_profile = {
        "profile_status":
            "GOVERNED_STATE_PROFILE_ASSEMBLED",

        "governance_mode":
            "CERTIFIED_STATE_PROJECTION_ONLY",

        "uncertainty_authority":
            "CERTIFIED_4.6.14_UNCERTAINTY_INTELLIGENCE_VIA_4.6.16P",

        "hybrid_governance_authority":
            "FROZEN_4.6.15S_HYBRID_STATE_VIA_4.6.16P",

        "preservation_authority":
            "4.6.16P_CERTIFIED_GOVERNED_STATE_PRESERVATION",

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

        "confidence_class_index":
            deepcopy(
                dict(
                    confidence_class_index
                )
            ),

        "certified_uncertainty_snapshot":
            deepcopy(
                dict(
                    uncertainty_payload
                )
            ),

        "certified_hybrid_governance_snapshot":
            deepcopy(
                dict(
                    hybrid_payload
                )
            ),

        "certified_preservation_snapshot":
            deepcopy(
                dict(
                    preservation
                )
            ),

        "conflict_state_preserved":
            True,

        "uncertainty_state_preserved":
            True,

        "confidence_state_preserved":
            True,

        "unresolved_state_preserved":
            True,

        "abstention_state_preserved":
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
            "semantic_article_profile_governed_state_assembly_v1",

        "version":
            CERTIFIED_SEMANTIC_ARTICLE_PROFILE_BUILDER_VERSION,

        "phase":
            CERTIFIED_SEMANTIC_ARTICLE_PROFILE_BUILDER_PHASE,

        "patch":
            "4.6.17H",

        "status":
            "GOVERNED_STATE_PROFILE_ASSEMBLED",

        "profile_identity":
            deepcopy(
                dict(
                    artifact_profile_result[
                        "profile_identity"
                    ]
                )
            ),

        "source_authority_profile":
            deepcopy(
                dict(
                    artifact_profile_result[
                        "source_authority_profile"
                    ]
                )
            ),

        "semantic_layer_profile":
            deepcopy(
                dict(
                    artifact_profile_result[
                        "semantic_layer_profile"
                    ]
                )
            ),

        "semantic_group_profile":
            deepcopy(
                dict(
                    artifact_profile_result[
                        "semantic_group_profile"
                    ]
                )
            ),

        "cross_layer_artifact_profile":
            deepcopy(
                dict(
                    artifact_profile
                )
            ),

        "governed_state_profile":
            governed_state_profile,

        "canonical_article_identity":
            deepcopy(
                dict(
                    artifact_profile_result[
                        "canonical_article_identity"
                    ]
                )
            ),

        "canonical_article_semantic_representation":
            deepcopy(
                dict(
                    representation
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
                    artifact_profile_result[
                        "normalized_group_index"
                    ]
                )
            ),

        "source_cross_layer_artifact_result":
            deepcopy(
                dict(
                    artifact_profile_result
                )
            ),

        "processing_boundaries": {
            "certified_source_validation_preserved":
                True,

            "profile_identity_assembly_preserved":
                True,

            "source_authority_assembly_preserved":
                True,

            "semantic_layer_profile_assembly_preserved":
                True,

            "semantic_group_profile_assembly_preserved":
                True,

            "cross_layer_artifact_profile_assembly_preserved":
                True,

            "governed_state_profile_assembly_performed":
                True,

            "conflict_state_preserved":
                True,

            "uncertainty_state_preserved":
                True,

            "confidence_state_preserved":
                True,

            "unresolved_state_preserved":
                True,

            "abstention_state_preserved":
                True,

            "profile_structural_index_construction_performed":
                False,

            "canonical_profile_assembly_performed":
                False,

            "final_profile_result_built":
                False,

            "profile_certification_performed":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "source_authority_override_performed":
                False,

            "artifact_recomputation_performed":
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

            "profile_store_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "profile_structural_index_construction",
    }


# =====================================================================
# PATCH 4.6.17I ? Profile Structural Index Construction
# =====================================================================

def construct_profile_structural_indexes_v1(
    governed_state_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Construct deterministic structural navigation indexes over the
    already-built Semantic Article Profile components.

    These are PROFILE indexes only.

    I does NOT:
    - rebuild upstream semantic indexes,
    - infer semantic relationships,
    - calculate semantic confidence,
    - resolve conflicts,
    - reinterpret uncertainty,
    - alter abstention,
    - perform semantic deduplication,
    - certify or persist the profile.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        governed_state_result,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "governed_state_result must be a mapping."
        )

    if (
        governed_state_result.get(
            "schema_version"
        )
        != "semantic_article_profile_governed_state_assembly_v1"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17I requires "
            "semantic_article_profile_governed_state_assembly_v1."
        )

    if (
        governed_state_result.get(
            "phase"
        )
        != "4.6.17"
        or governed_state_result.get(
            "patch"
        )
        != "4.6.17H"
        or governed_state_result.get(
            "status"
        )
        != "GOVERNED_STATE_PROFILE_ASSEMBLED"
        or governed_state_result.get(
            "next_stage"
        )
        != "profile_structural_index_construction"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17H lifecycle contract is invalid."
        )

    if (
        governed_state_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17I requires transient article-local intelligence."
        )

    boundaries = governed_state_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17H processing boundaries are missing."
        )

    for field in (
        "certified_source_validation_preserved",
        "profile_identity_assembly_preserved",
        "source_authority_assembly_preserved",
        "semantic_layer_profile_assembly_preserved",
        "semantic_group_profile_assembly_preserved",
        "cross_layer_artifact_profile_assembly_preserved",
        "governed_state_profile_assembly_performed",
        "conflict_state_preserved",
        "uncertainty_state_preserved",
        "confidence_state_preserved",
        "unresolved_state_preserved",
        "abstention_state_preserved",
    ):

        if boundaries.get(
            field
        ) is not True:
            raise CertifiedSemanticArticleProfileBuilderError(
                "Required 4.6.17H boundary is not True: "
                + field
            )

    for field in (
        "profile_structural_index_construction_performed",
        "canonical_profile_assembly_performed",
        "final_profile_result_built",
        "profile_certification_performed",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "source_authority_override_performed",
        "artifact_recomputation_performed",
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
        "profile_store_written",
        "linking_decisions_performed",
        "persistence_performed",
    ):

        if boundaries.get(
            field
        ) is not False:
            raise CertifiedSemanticArticleProfileBuilderError(
                "Forbidden 4.6.17H boundary is not False: "
                + field
            )

    layer_profile = governed_state_result.get(
        "semantic_layer_profile"
    )

    group_profile = governed_state_result.get(
        "semantic_group_profile"
    )

    artifact_profile = governed_state_result.get(
        "cross_layer_artifact_profile"
    )

    governed_profile = governed_state_result.get(
        "governed_state_profile"
    )

    for name, value in (
        (
            "semantic_layer_profile",
            layer_profile,
        ),
        (
            "semantic_group_profile",
            group_profile,
        ),
        (
            "cross_layer_artifact_profile",
            artifact_profile,
        ),
        (
            "governed_state_profile",
            governed_profile,
        ),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                name + " is missing or invalid."
            )

    layer_records = layer_profile.get(
        "layer_records"
    )

    group_records = group_profile.get(
        "group_records"
    )

    artifact_records = artifact_profile.get(
        "artifact_records"
    )

    if (
        not isinstance(
            layer_records,
            list,
        )
        or len(
            layer_records
        )
        != 15
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Layer profile must contain exactly 15 records."
        )

    if (
        not isinstance(
            group_records,
            list,
        )
        or len(
            group_records
        )
        != 4
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Group profile must contain exactly four records."
        )

    if (
        not isinstance(
            artifact_records,
            list,
        )
        or len(
            artifact_records
        )
        != 4
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Artifact profile must contain exactly four records."
        )

    # -------------------------------------------------------------
    # Layer indexes
    # -------------------------------------------------------------

    layer_name_index = {}
    layer_phase_index = {}
    layer_group_index = {}
    layer_ordinal_index = {}

    for expected_ordinal, record in enumerate(
        layer_records,
        1,
    ):

        if not isinstance(
            record,
            Mapping,
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                "Layer profile record is invalid."
            )

        layer_name = record.get(
            "layer_name"
        )

        phase = record.get(
            "phase"
        )

        group_name = record.get(
            "semantic_group"
        )

        ordinal = record.get(
            "ordinal"
        )

        profile_layer_id = record.get(
            "profile_layer_id"
        )

        if (
            layer_name
            != _SEMANTIC_ARTICLE_PROFILE_LAYER_ORDER[
                expected_ordinal - 1
            ]
            or phase
            != _SEMANTIC_ARTICLE_PROFILE_LAYER_PHASES[
                layer_name
            ]
            or ordinal
            != expected_ordinal
            or not isinstance(
                profile_layer_id,
                str,
            )
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                "Layer profile structural identity drifted."
            )

        if layer_name in layer_name_index:
            raise CertifiedSemanticArticleProfileBuilderError(
                "Duplicate layer name in structural profile."
            )

        layer_name_index[
            layer_name
        ] = profile_layer_id

        layer_phase_index[
            phase
        ] = layer_name

        layer_group_index[
            layer_name
        ] = group_name

        layer_ordinal_index[
            str(
                ordinal
            )
        ] = layer_name

    # -------------------------------------------------------------
    # Group indexes
    # -------------------------------------------------------------

    group_name_index = {}
    group_ordinal_index = {}
    group_membership_index = {}

    for expected_ordinal, record in enumerate(
        group_records,
        1,
    ):

        if not isinstance(
            record,
            Mapping,
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                "Group profile record is invalid."
            )

        group_name = record.get(
            "group_name"
        )

        profile_group_id = record.get(
            "profile_group_id"
        )

        ordinal = record.get(
            "ordinal"
        )

        member_order = record.get(
            "member_layer_order"
        )

        if (
            group_name
            != _SEMANTIC_ARTICLE_PROFILE_SOURCE_GROUP_ORDER[
                expected_ordinal - 1
            ]
            or ordinal
            != expected_ordinal
            or not isinstance(
                profile_group_id,
                str,
            )
            or member_order
            != list(
                _SEMANTIC_ARTICLE_PROFILE_GROUP_MEMBERSHIP[
                    group_name
                ]
            )
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                "Group profile structural identity drifted."
            )

        group_name_index[
            group_name
        ] = profile_group_id

        group_ordinal_index[
            str(
                ordinal
            )
        ] = group_name

        group_membership_index[
            group_name
        ] = deepcopy(
            member_order
        )

    # -------------------------------------------------------------
    # Cross-layer artifact indexes
    # -------------------------------------------------------------

    artifact_name_index = {}
    artifact_ordinal_index = {}

    for expected_ordinal, record in enumerate(
        artifact_records,
        1,
    ):

        if not isinstance(
            record,
            Mapping,
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                "Artifact profile record is invalid."
            )

        artifact_name = record.get(
            "artifact_name"
        )

        ordinal = record.get(
            "ordinal"
        )

        profile_artifact_id = record.get(
            "profile_artifact_id"
        )

        if (
            ordinal
            != expected_ordinal
            or not isinstance(
                artifact_name,
                str,
            )
            or not isinstance(
                profile_artifact_id,
                str,
            )
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                "Artifact profile structural identity drifted."
            )

        artifact_name_index[
            artifact_name
        ] = profile_artifact_id

        artifact_ordinal_index[
            str(
                ordinal
            )
        ] = artifact_name

    expected_artifact_order = [
        "article_identity_alignment",
        "provenance_alignment",
        "state_indexes",
        "conflict_uncertainty_abstention_preservation",
    ]

    if (
        list(
            artifact_name_index.keys()
        )
        != expected_artifact_order
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Artifact profile order drifted."
        )

    # -------------------------------------------------------------
    # Governed-state indexes ? COPY ONLY.
    # -------------------------------------------------------------

    governed_state_index = {
        "governed_conflict_candidate_ids":
            deepcopy(
                governed_profile.get(
                    "governed_conflict_candidate_ids",
                    [],
                )
            ),

        "unresolved_candidate_ids":
            deepcopy(
                governed_profile.get(
                    "unresolved_candidate_ids",
                    [],
                )
            ),

        "abstention_candidate_ids":
            deepcopy(
                governed_profile.get(
                    "abstention_candidate_ids",
                    [],
                )
            ),

        "confidence_class_index":
            deepcopy(
                dict(
                    governed_profile.get(
                        "confidence_class_index",
                        {},
                    )
                )
            ),

        "article_has_symbolically_governed_conflict":
            governed_profile.get(
                "article_has_symbolically_governed_conflict"
            ),

        "article_has_unresolved_hybrid_evidence":
            governed_profile.get(
                "article_has_unresolved_hybrid_evidence"
            ),

        "article_requires_hybrid_abstention":
            governed_profile.get(
                "article_requires_hybrid_abstention"
            ),
    }

    if (
        governed_state_index[
            "unresolved_candidate_ids"
        ]
        != governed_state_index[
            "abstention_candidate_ids"
        ]
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Governed-state structural index detected unresolved/"
            "abstention drift."
        )

    structural_indexes = {
        "index_status":
            "PROFILE_STRUCTURAL_INDEXES_CONSTRUCTED",

        "index_mode":
            "DETERMINISTIC_PROFILE_NAVIGATION_ONLY",

        "layer_name_index":
            layer_name_index,

        "layer_phase_index":
            layer_phase_index,

        "layer_group_index":
            layer_group_index,

        "layer_ordinal_index":
            layer_ordinal_index,

        "group_name_index":
            group_name_index,

        "group_ordinal_index":
            group_ordinal_index,

        "group_membership_index":
            group_membership_index,

        "artifact_name_index":
            artifact_name_index,

        "artifact_ordinal_index":
            artifact_ordinal_index,

        "governed_state_index":
            governed_state_index,

        "layer_index_count":
            15,

        "group_index_count":
            4,

        "artifact_index_count":
            4,

        "profile_navigation_indexes_only":
            True,

        "upstream_semantic_indexes_preserved":
            True,

        "upstream_index_rebuild_performed":
            False,

        "semantic_reclassification_performed":
            False,

        "semantic_count_recalculation_performed":
            False,

        "confidence_recalculation_performed":
            False,

        "new_reasoning_performed":
            False,
    }

    return {
        "schema_version":
            "semantic_article_profile_structural_indexes_v1",

        "version":
            CERTIFIED_SEMANTIC_ARTICLE_PROFILE_BUILDER_VERSION,

        "phase":
            CERTIFIED_SEMANTIC_ARTICLE_PROFILE_BUILDER_PHASE,

        "patch":
            "4.6.17I",

        "status":
            "PROFILE_STRUCTURAL_INDEXES_CONSTRUCTED",

        "profile_identity":
            deepcopy(
                governed_state_result[
                    "profile_identity"
                ]
            ),

        "source_authority_profile":
            deepcopy(
                governed_state_result[
                    "source_authority_profile"
                ]
            ),

        "semantic_layer_profile":
            deepcopy(
                governed_state_result[
                    "semantic_layer_profile"
                ]
            ),

        "semantic_group_profile":
            deepcopy(
                governed_state_result[
                    "semantic_group_profile"
                ]
            ),

        "cross_layer_artifact_profile":
            deepcopy(
                governed_state_result[
                    "cross_layer_artifact_profile"
                ]
            ),

        "governed_state_profile":
            deepcopy(
                governed_profile
            ),

        "structural_indexes":
            structural_indexes,

        "canonical_article_identity":
            deepcopy(
                governed_state_result[
                    "canonical_article_identity"
                ]
            ),

        "canonical_article_semantic_representation":
            deepcopy(
                governed_state_result[
                    "canonical_article_semantic_representation"
                ]
            ),

        "normalized_layers":
            deepcopy(
                governed_state_result[
                    "normalized_layers"
                ]
            ),

        "normalized_group_index":
            deepcopy(
                governed_state_result[
                    "normalized_group_index"
                ]
            ),

        "source_governed_state_result":
            deepcopy(
                dict(
                    governed_state_result
                )
            ),

        "processing_boundaries": {
            "certified_source_validation_preserved":
                True,

            "profile_identity_assembly_preserved":
                True,

            "source_authority_assembly_preserved":
                True,

            "semantic_layer_profile_assembly_preserved":
                True,

            "semantic_group_profile_assembly_preserved":
                True,

            "cross_layer_artifact_profile_assembly_preserved":
                True,

            "governed_state_profile_assembly_preserved":
                True,

            "profile_structural_index_construction_performed":
                True,

            "layer_navigation_indexes_constructed":
                True,

            "group_navigation_indexes_constructed":
                True,

            "artifact_navigation_indexes_constructed":
                True,

            "governed_state_indexes_projected":
                True,

            "canonical_profile_assembly_performed":
                False,

            "final_profile_result_built":
                False,

            "profile_certification_performed":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "source_authority_override_performed":
                False,

            "artifact_recomputation_performed":
                False,

            "upstream_index_rebuild_performed":
                False,

            "semantic_reclassification_performed":
                False,

            "semantic_count_recalculation_performed":
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

            "profile_store_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "canonical_semantic_article_profile_assembly",
    }


# =====================================================================
# PATCH 4.6.17J ? Canonical Semantic Article Profile Assembly
# =====================================================================

def assemble_canonical_semantic_article_profile_v1(
    structural_index_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Assemble the canonical Semantic Article Profile from the already-built
    4.6.17 profile components.

    J performs canonical packaging only.

    It does NOT:
    - perform new semantic reasoning,
    - modify source meaning,
    - change source authority,
    - rebuild semantic indexes,
    - resolve conflict,
    - reinterpret uncertainty,
    - recalculate confidence,
    - create/remove abstention,
    - certify the profile,
    - persist the profile,
    - write Semantic Memory,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        structural_index_result,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "structural_index_result must be a mapping."
        )

    if (
        structural_index_result.get(
            "schema_version"
        )
        != "semantic_article_profile_structural_indexes_v1"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17J requires semantic_article_profile_structural_indexes_v1."
        )

    if (
        structural_index_result.get(
            "phase"
        )
        != "4.6.17"
        or structural_index_result.get(
            "patch"
        )
        != "4.6.17I"
        or structural_index_result.get(
            "status"
        )
        != "PROFILE_STRUCTURAL_INDEXES_CONSTRUCTED"
        or structural_index_result.get(
            "next_stage"
        )
        != "canonical_semantic_article_profile_assembly"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17I lifecycle contract is invalid."
        )

    if (
        structural_index_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17J requires article-local transient intelligence."
        )

    boundaries = structural_index_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17I processing boundaries are missing."
        )

    for field in (
        "certified_source_validation_preserved",
        "profile_identity_assembly_preserved",
        "source_authority_assembly_preserved",
        "semantic_layer_profile_assembly_preserved",
        "semantic_group_profile_assembly_preserved",
        "cross_layer_artifact_profile_assembly_preserved",
        "governed_state_profile_assembly_preserved",
        "profile_structural_index_construction_performed",
        "layer_navigation_indexes_constructed",
        "group_navigation_indexes_constructed",
        "artifact_navigation_indexes_constructed",
        "governed_state_indexes_projected",
    ):

        if boundaries.get(
            field
        ) is not True:
            raise CertifiedSemanticArticleProfileBuilderError(
                "Required 4.6.17I boundary is not True: "
                + field
            )

    for field in (
        "canonical_profile_assembly_performed",
        "final_profile_result_built",
        "profile_certification_performed",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "source_authority_override_performed",
        "artifact_recomputation_performed",
        "upstream_index_rebuild_performed",
        "semantic_reclassification_performed",
        "semantic_count_recalculation_performed",
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
        "profile_store_written",
        "linking_decisions_performed",
        "persistence_performed",
    ):

        if boundaries.get(
            field
        ) is not False:
            raise CertifiedSemanticArticleProfileBuilderError(
                "Forbidden 4.6.17I boundary is not False: "
                + field
            )

    required_components = {
        "profile_identity":
            structural_index_result.get(
                "profile_identity"
            ),

        "source_authority_profile":
            structural_index_result.get(
                "source_authority_profile"
            ),

        "semantic_layer_profile":
            structural_index_result.get(
                "semantic_layer_profile"
            ),

        "semantic_group_profile":
            structural_index_result.get(
                "semantic_group_profile"
            ),

        "cross_layer_artifact_profile":
            structural_index_result.get(
                "cross_layer_artifact_profile"
            ),

        "governed_state_profile":
            structural_index_result.get(
                "governed_state_profile"
            ),

        "structural_indexes":
            structural_index_result.get(
                "structural_indexes"
            ),
    }

    for name, value in required_components.items():

        if not isinstance(
            value,
            Mapping,
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                name + " is missing or invalid."
            )

    canonical_identity = structural_index_result.get(
        "canonical_article_identity"
    )

    representation = structural_index_result.get(
        "canonical_article_semantic_representation"
    )

    if not isinstance(
        canonical_identity,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Canonical article identity is missing."
        )

    if not isinstance(
        representation,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Canonical article semantic representation is missing."
        )

    profile_identity = required_components[
        "profile_identity"
    ]

    if (
        profile_identity.get(
            "canonical_article_identity"
        )
        != canonical_identity
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Canonical profile identity drifted."
        )

    semantic_layer_profile = required_components[
        "semantic_layer_profile"
    ]

    semantic_group_profile = required_components[
        "semantic_group_profile"
    ]

    cross_layer_artifact_profile = required_components[
        "cross_layer_artifact_profile"
    ]

    governed_state_profile = required_components[
        "governed_state_profile"
    ]

    structural_indexes = required_components[
        "structural_indexes"
    ]

    if (
        semantic_layer_profile.get(
            "layer_count"
        )
        != 15
        or semantic_group_profile.get(
            "group_count"
        )
        != 4
        or cross_layer_artifact_profile.get(
            "artifact_count"
        )
        != 4
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Canonical profile component accounting is invalid."
        )

    if (
        structural_indexes.get(
            "index_status"
        )
        != "PROFILE_STRUCTURAL_INDEXES_CONSTRUCTED"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Structural profile indexes are not ready."
        )

    canonical_profile = {
        "profile_schema_version":
            "canonical_semantic_article_profile_v1",

        "profile_status":
            "CANONICAL_SEMANTIC_ARTICLE_PROFILE_ASSEMBLED",

        "profile_builder_phase":
            "4.6.17",

        "profile_builder_patch":
            "4.6.17J",

        "profile_mode":
            "CERTIFIED_SOURCE_STRUCTURAL_PROFILE",

        "profile_identity":
            deepcopy(
                dict(
                    profile_identity
                )
            ),

        "source_authority":
            deepcopy(
                dict(
                    required_components[
                        "source_authority_profile"
                    ]
                )
            ),

        "semantic_layers":
            deepcopy(
                dict(
                    semantic_layer_profile
                )
            ),

        "semantic_groups":
            deepcopy(
                dict(
                    semantic_group_profile
                )
            ),

        "cross_layer_artifacts":
            deepcopy(
                dict(
                    cross_layer_artifact_profile
                )
            ),

        "governed_state":
            deepcopy(
                dict(
                    governed_state_profile
                )
            ),

        "structural_indexes":
            deepcopy(
                dict(
                    structural_indexes
                )
            ),

        "certified_source_semantic_representation":
            deepcopy(
                dict(
                    representation
                )
            ),

        "profile_section_order": [
            "profile_identity",
            "source_authority",
            "semantic_layers",
            "semantic_groups",
            "cross_layer_artifacts",
            "governed_state",
            "structural_indexes",
            "certified_source_semantic_representation",
        ],

        "profile_section_count":
            8,

        "source_layer_count":
            15,

        "source_group_count":
            4,

        "cross_layer_artifact_count":
            4,

        "source_meaning_preserved":
            True,

        "source_authority_preserved":
            True,

        "governed_state_preserved":
            True,

        "profile_navigation_only_indexes":
            True,

        "profile_certification_ready":
            True,

        "profile_certified":
            False,

        "profile_persisted":
            False,

        "semantic_state_modified":
            False,

        "semantic_meaning_rewritten":
            False,

        "semantic_merge_performed":
            False,

        "cross_layer_reasoning_performed":
            False,

        "conflict_resolution_performed":
            False,

        "uncertainty_reinterpretation_performed":
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
            "canonical_semantic_article_profile_assembly_result_v1",

        "version":
            CERTIFIED_SEMANTIC_ARTICLE_PROFILE_BUILDER_VERSION,

        "phase":
            CERTIFIED_SEMANTIC_ARTICLE_PROFILE_BUILDER_PHASE,

        "patch":
            "4.6.17J",

        "status":
            "CANONICAL_SEMANTIC_ARTICLE_PROFILE_ASSEMBLED",

        "canonical_article_identity":
            deepcopy(
                dict(
                    canonical_identity
                )
            ),

        "canonical_semantic_article_profile":
            canonical_profile,

        "profile_identity":
            deepcopy(
                dict(
                    profile_identity
                )
            ),

        "source_authority_profile":
            deepcopy(
                dict(
                    required_components[
                        "source_authority_profile"
                    ]
                )
            ),

        "semantic_layer_profile":
            deepcopy(
                dict(
                    semantic_layer_profile
                )
            ),

        "semantic_group_profile":
            deepcopy(
                dict(
                    semantic_group_profile
                )
            ),

        "cross_layer_artifact_profile":
            deepcopy(
                dict(
                    cross_layer_artifact_profile
                )
            ),

        "governed_state_profile":
            deepcopy(
                dict(
                    governed_state_profile
                )
            ),

        "structural_indexes":
            deepcopy(
                dict(
                    structural_indexes
                )
            ),

        "canonical_article_semantic_representation":
            deepcopy(
                dict(
                    representation
                )
            ),

        "normalized_layers":
            deepcopy(
                dict(
                    structural_index_result[
                        "normalized_layers"
                    ]
                )
            ),

        "normalized_group_index":
            deepcopy(
                dict(
                    structural_index_result[
                        "normalized_group_index"
                    ]
                )
            ),

        "source_structural_index_result":
            deepcopy(
                dict(
                    structural_index_result
                )
            ),

        "processing_boundaries": {
            "certified_source_validation_preserved":
                True,

            "profile_identity_assembly_preserved":
                True,

            "source_authority_assembly_preserved":
                True,

            "semantic_layer_profile_assembly_preserved":
                True,

            "semantic_group_profile_assembly_preserved":
                True,

            "cross_layer_artifact_profile_assembly_preserved":
                True,

            "governed_state_profile_assembly_preserved":
                True,

            "profile_structural_index_construction_preserved":
                True,

            "canonical_profile_assembly_performed":
                True,

            "canonical_profile_contains_all_required_sections":
                True,

            "canonical_profile_ready_for_final_result":
                True,

            "final_profile_result_built":
                False,

            "profile_certification_performed":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "source_authority_override_performed":
                False,

            "artifact_recomputation_performed":
                False,

            "upstream_index_rebuild_performed":
                False,

            "semantic_reclassification_performed":
                False,

            "semantic_count_recalculation_performed":
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

            "profile_store_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "final_semantic_article_profile_result",
    }


# =====================================================================
# PATCH 4.6.17K ? Final Semantic Article Profile Result
# =====================================================================

def build_final_semantic_article_profile_result_v1(
    canonical_profile_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Build the final 4.6.17 Semantic Article Profile result.

    K performs final packaging and downstream handoff only.

    It does NOT:
    - alter the canonical Semantic Article Profile,
    - perform new reasoning,
    - rewrite semantic meaning,
    - change source authority,
    - rebuild indexes,
    - resolve conflict,
    - reinterpret uncertainty,
    - recalculate confidence,
    - create/remove abstention,
    - certify the profile,
    - persist the profile,
    - write Semantic Memory,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        canonical_profile_result,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "canonical_profile_result must be a mapping."
        )

    if (
        canonical_profile_result.get(
            "schema_version"
        )
        != "canonical_semantic_article_profile_assembly_result_v1"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17K requires "
            "canonical_semantic_article_profile_assembly_result_v1."
        )

    if (
        canonical_profile_result.get(
            "phase"
        )
        != "4.6.17"
        or canonical_profile_result.get(
            "patch"
        )
        != "4.6.17J"
        or canonical_profile_result.get(
            "status"
        )
        != "CANONICAL_SEMANTIC_ARTICLE_PROFILE_ASSEMBLED"
        or canonical_profile_result.get(
            "next_stage"
        )
        != "final_semantic_article_profile_result"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17J lifecycle contract is invalid."
        )

    if (
        canonical_profile_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17K requires article-local transient intelligence."
        )

    boundaries = canonical_profile_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17J processing boundaries are missing."
        )

    for field in (
        "certified_source_validation_preserved",
        "profile_identity_assembly_preserved",
        "source_authority_assembly_preserved",
        "semantic_layer_profile_assembly_preserved",
        "semantic_group_profile_assembly_preserved",
        "cross_layer_artifact_profile_assembly_preserved",
        "governed_state_profile_assembly_preserved",
        "profile_structural_index_construction_preserved",
        "canonical_profile_assembly_performed",
        "canonical_profile_contains_all_required_sections",
        "canonical_profile_ready_for_final_result",
    ):

        if boundaries.get(
            field
        ) is not True:
            raise CertifiedSemanticArticleProfileBuilderError(
                "Required 4.6.17J boundary is not True: "
                + field
            )

    for field in (
        "final_profile_result_built",
        "profile_certification_performed",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "source_authority_override_performed",
        "artifact_recomputation_performed",
        "upstream_index_rebuild_performed",
        "semantic_reclassification_performed",
        "semantic_count_recalculation_performed",
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
        "profile_store_written",
        "linking_decisions_performed",
        "persistence_performed",
    ):

        if boundaries.get(
            field
        ) is not False:
            raise CertifiedSemanticArticleProfileBuilderError(
                "Forbidden 4.6.17J boundary is not False: "
                + field
            )

    canonical_profile = canonical_profile_result.get(
        "canonical_semantic_article_profile"
    )

    canonical_identity = canonical_profile_result.get(
        "canonical_article_identity"
    )

    if not isinstance(
        canonical_profile,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Canonical Semantic Article Profile is missing."
        )

    if not isinstance(
        canonical_identity,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Canonical article identity is missing."
        )

    if (
        canonical_profile.get(
            "profile_schema_version"
        )
        != "canonical_semantic_article_profile_v1"
        or canonical_profile.get(
            "profile_status"
        )
        != "CANONICAL_SEMANTIC_ARTICLE_PROFILE_ASSEMBLED"
        or canonical_profile.get(
            "profile_builder_phase"
        )
        != "4.6.17"
        or canonical_profile.get(
            "profile_builder_patch"
        )
        != "4.6.17J"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Canonical profile contract is invalid."
        )

    if (
        canonical_profile.get(
            "profile_certification_ready"
        )
        is not True
        or canonical_profile.get(
            "profile_certified"
        )
        is not False
        or canonical_profile.get(
            "profile_persisted"
        )
        is not False
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Canonical profile certification/persistence state is invalid."
        )

    profile_identity = canonical_profile.get(
        "profile_identity"
    )

    if (
        not isinstance(
            profile_identity,
            Mapping,
        )
        or profile_identity.get(
            "canonical_article_identity"
        )
        != canonical_identity
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Canonical profile identity drifted."
        )

    expected_sections = [
        "profile_identity",
        "source_authority",
        "semantic_layers",
        "semantic_groups",
        "cross_layer_artifacts",
        "governed_state",
        "structural_indexes",
        "certified_source_semantic_representation",
    ]

    if (
        canonical_profile.get(
            "profile_section_order"
        )
        != expected_sections
        or canonical_profile.get(
            "profile_section_count"
        )
        != 8
        or canonical_profile.get(
            "source_layer_count"
        )
        != 15
        or canonical_profile.get(
            "source_group_count"
        )
        != 4
        or canonical_profile.get(
            "cross_layer_artifact_count"
        )
        != 4
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Canonical profile section/count contract drifted."
        )

    for field in (
        "source_meaning_preserved",
        "source_authority_preserved",
        "governed_state_preserved",
        "profile_navigation_only_indexes",
        "profile_certification_ready",
    ):

        if canonical_profile.get(
            field
        ) is not True:
            raise CertifiedSemanticArticleProfileBuilderError(
                "Canonical profile preservation field is invalid: "
                + field
            )

    for field in (
        "profile_certified",
        "profile_persisted",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "semantic_merge_performed",
        "cross_layer_reasoning_performed",
        "conflict_resolution_performed",
        "uncertainty_reinterpretation_performed",
        "confidence_recalculation_performed",
        "abstention_decision_created",
        "abstention_decision_removed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
    ):

        if canonical_profile.get(
            field
        ) is not False:
            raise CertifiedSemanticArticleProfileBuilderError(
                "Canonical profile contains forbidden state: "
                + field
            )

    final_summary = {
        "final_result_status":
            "SEMANTIC_ARTICLE_PROFILE_RESULT_READY",

        "profile_schema_version":
            "canonical_semantic_article_profile_v1",

        "source_builder_phase":
            "4.6.17",

        "source_builder_patch":
            "4.6.17J",

        "profile_section_count":
            8,

        "source_layer_count":
            15,

        "source_group_count":
            4,

        "cross_layer_artifact_count":
            4,

        "profile_certification_ready":
            True,

        "profile_certification_performed":
            False,

        "profile_persistence_performed":
            False,

        "source_meaning_preserved":
            True,

        "source_authority_preserved":
            True,

        "governed_state_preserved":
            True,

        "semantic_state_modified":
            False,

        "new_reasoning_performed":
            False,
    }

    return {
        "schema_version":
            "final_semantic_article_profile_result_v1",

        "version":
            CERTIFIED_SEMANTIC_ARTICLE_PROFILE_BUILDER_VERSION,

        "phase":
            CERTIFIED_SEMANTIC_ARTICLE_PROFILE_BUILDER_PHASE,

        "patch":
            "4.6.17K",

        "status":
            "SEMANTIC_ARTICLE_PROFILE_RESULT_READY",

        "canonical_article_identity":
            deepcopy(
                dict(
                    canonical_identity
                )
            ),

        "final_semantic_article_profile":
            deepcopy(
                dict(
                    canonical_profile
                )
            ),

        "final_result_summary":
            final_summary,

        "profile_identity":
            deepcopy(
                canonical_profile_result[
                    "profile_identity"
                ]
            ),

        "source_authority_profile":
            deepcopy(
                canonical_profile_result[
                    "source_authority_profile"
                ]
            ),

        "semantic_layer_profile":
            deepcopy(
                canonical_profile_result[
                    "semantic_layer_profile"
                ]
            ),

        "semantic_group_profile":
            deepcopy(
                canonical_profile_result[
                    "semantic_group_profile"
                ]
            ),

        "cross_layer_artifact_profile":
            deepcopy(
                canonical_profile_result[
                    "cross_layer_artifact_profile"
                ]
            ),

        "governed_state_profile":
            deepcopy(
                canonical_profile_result[
                    "governed_state_profile"
                ]
            ),

        "structural_indexes":
            deepcopy(
                canonical_profile_result[
                    "structural_indexes"
                ]
            ),

        "canonical_article_semantic_representation":
            deepcopy(
                canonical_profile_result[
                    "canonical_article_semantic_representation"
                ]
            ),

        "normalized_layers":
            deepcopy(
                canonical_profile_result[
                    "normalized_layers"
                ]
            ),

        "normalized_group_index":
            deepcopy(
                canonical_profile_result[
                    "normalized_group_index"
                ]
            ),

        "source_canonical_profile_result":
            deepcopy(
                dict(
                    canonical_profile_result
                )
            ),

        "processing_boundaries": {
            "certified_source_validation_preserved":
                True,

            "profile_identity_assembly_preserved":
                True,

            "source_authority_assembly_preserved":
                True,

            "semantic_layer_profile_assembly_preserved":
                True,

            "semantic_group_profile_assembly_preserved":
                True,

            "cross_layer_artifact_profile_assembly_preserved":
                True,

            "governed_state_profile_assembly_preserved":
                True,

            "profile_structural_index_construction_preserved":
                True,

            "canonical_profile_assembly_preserved":
                True,

            "final_profile_result_built":
                True,

            "final_profile_contract_validated":
                True,

            "profile_ready_for_4_6_18_certification":
                True,

            "profile_certification_performed":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "source_authority_override_performed":
                False,

            "artifact_recomputation_performed":
                False,

            "upstream_index_rebuild_performed":
                False,

            "semantic_reclassification_performed":
                False,

            "semantic_count_recalculation_performed":
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

            "profile_store_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "semantic_article_profile_builder_full_certification",
    }


# =====================================================================
# PATCH 4.6.17L ? Full Builder Hard Certification
# =====================================================================

def certify_semantic_article_profile_builder_v1(
    final_profile_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Certify the 4.6.17 Semantic Article Profile BUILDER.

    This certifies that the builder correctly produced and preserved the
    final profile contract.

    IMPORTANT:
    This does NOT certify the Semantic Article Profile itself.
    Profile certification belongs exclusively to Phase 4.6.18.

    L does NOT:
    - set profile_certified=True,
    - persist the profile,
    - alter semantic state,
    - perform new reasoning,
    - resolve conflict,
    - reinterpret uncertainty,
    - recalculate confidence,
    - create/remove abstention,
    - write Semantic Memory,
    - make linking decisions.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        final_profile_result,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "final_profile_result must be a mapping."
        )

    if (
        final_profile_result.get(
            "schema_version"
        )
        != "final_semantic_article_profile_result_v1"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17L requires final_semantic_article_profile_result_v1."
        )

    if (
        final_profile_result.get(
            "phase"
        )
        != "4.6.17"
        or final_profile_result.get(
            "patch"
        )
        != "4.6.17K"
        or final_profile_result.get(
            "status"
        )
        != "SEMANTIC_ARTICLE_PROFILE_RESULT_READY"
        or final_profile_result.get(
            "next_stage"
        )
        != "semantic_article_profile_builder_full_certification"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17K lifecycle contract is invalid."
        )

    if (
        final_profile_result.get(
            "persistence_policy"
        )
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17L requires article-local transient intelligence."
        )

    boundaries = final_profile_result.get(
        "processing_boundaries"
    )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "4.6.17K processing boundaries are missing."
        )

    required_true_boundaries = (
        "certified_source_validation_preserved",
        "profile_identity_assembly_preserved",
        "source_authority_assembly_preserved",
        "semantic_layer_profile_assembly_preserved",
        "semantic_group_profile_assembly_preserved",
        "cross_layer_artifact_profile_assembly_preserved",
        "governed_state_profile_assembly_preserved",
        "profile_structural_index_construction_preserved",
        "canonical_profile_assembly_preserved",
        "final_profile_result_built",
        "final_profile_contract_validated",
        "profile_ready_for_4_6_18_certification",
    )

    for field in required_true_boundaries:

        if boundaries.get(
            field
        ) is not True:
            raise CertifiedSemanticArticleProfileBuilderError(
                "Required 4.6.17K boundary is not True: "
                + field
            )

    required_false_boundaries = (
        "profile_certification_performed",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "source_authority_override_performed",
        "artifact_recomputation_performed",
        "upstream_index_rebuild_performed",
        "semantic_reclassification_performed",
        "semantic_count_recalculation_performed",
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
        "profile_store_written",
        "linking_decisions_performed",
        "persistence_performed",
    )

    for field in required_false_boundaries:

        if boundaries.get(
            field
        ) is not False:
            raise CertifiedSemanticArticleProfileBuilderError(
                "Forbidden 4.6.17K boundary is not False: "
                + field
            )

    canonical_identity = final_profile_result.get(
        "canonical_article_identity"
    )

    final_profile = final_profile_result.get(
        "final_semantic_article_profile"
    )

    final_summary = final_profile_result.get(
        "final_result_summary"
    )

    if not isinstance(
        canonical_identity,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Canonical article identity is missing."
        )

    if not isinstance(
        final_profile,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Final Semantic Article Profile is missing."
        )

    if not isinstance(
        final_summary,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Final result summary is missing."
        )

    if (
        final_profile.get(
            "profile_schema_version"
        )
        != "canonical_semantic_article_profile_v1"
        or final_profile.get(
            "profile_status"
        )
        != "CANONICAL_SEMANTIC_ARTICLE_PROFILE_ASSEMBLED"
        or final_profile.get(
            "profile_builder_phase"
        )
        != "4.6.17"
        or final_profile.get(
            "profile_builder_patch"
        )
        != "4.6.17J"
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Final canonical profile contract is invalid."
        )

    if (
        final_profile.get(
            "profile_certification_ready"
        )
        is not True
        or final_profile.get(
            "profile_certified"
        )
        is not False
        or final_profile.get(
            "profile_persisted"
        )
        is not False
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Final profile must be ready but still uncertified/unpersisted."
        )

    final_profile_forbidden_true_fields = (
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "semantic_merge_performed",
        "cross_layer_reasoning_performed",
        "conflict_resolution_performed",
        "uncertainty_reinterpretation_performed",
        "confidence_recalculation_performed",
        "abstention_decision_created",
        "abstention_decision_removed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
    )

    for field in final_profile_forbidden_true_fields:

        if final_profile.get(
            field
        ) is not False:

            raise CertifiedSemanticArticleProfileBuilderError(
                "Final Semantic Article Profile contains forbidden state: "
                + field
            )

    if (
        final_profile.get(
            "profile_identity",
            {}
        ).get(
            "canonical_article_identity"
        )
        != canonical_identity
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Final profile identity drifted."
        )

    if (
        final_profile.get(
            "profile_section_count"
        )
        != 8
        or final_profile.get(
            "source_layer_count"
        )
        != 15
        or final_profile.get(
            "source_group_count"
        )
        != 4
        or final_profile.get(
            "cross_layer_artifact_count"
        )
        != 4
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Final profile structural accounting is invalid."
        )

    expected_sections = [
        "profile_identity",
        "source_authority",
        "semantic_layers",
        "semantic_groups",
        "cross_layer_artifacts",
        "governed_state",
        "structural_indexes",
        "certified_source_semantic_representation",
    ]

    if (
        final_profile.get(
            "profile_section_order"
        )
        != expected_sections
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Final profile section order drifted."
        )

    # Exact preservation against top-level K artifacts.
    preservation_pairs = (
        (
            "profile_identity",
            "profile_identity",
        ),
        (
            "source_authority",
            "source_authority_profile",
        ),
        (
            "semantic_layers",
            "semantic_layer_profile",
        ),
        (
            "semantic_groups",
            "semantic_group_profile",
        ),
        (
            "cross_layer_artifacts",
            "cross_layer_artifact_profile",
        ),
        (
            "governed_state",
            "governed_state_profile",
        ),
        (
            "structural_indexes",
            "structural_indexes",
        ),
        (
            "certified_source_semantic_representation",
            "canonical_article_semantic_representation",
        ),
    )

    for profile_key, result_key in preservation_pairs:

        if (
            final_profile.get(
                profile_key
            )
            != final_profile_result.get(
                result_key
            )
        ):
            raise CertifiedSemanticArticleProfileBuilderError(
                profile_key
                + " drifted from the final builder result."
            )

    governed_state = final_profile.get(
        "governed_state"
    )

    if not isinstance(
        governed_state,
        Mapping,
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Final governed-state profile is invalid."
        )

    if (
        governed_state.get(
            "unresolved_candidate_ids"
        )
        != governed_state.get(
            "abstention_candidate_ids"
        )
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Final unresolved and abstention states diverged."
        )

    structural_indexes = final_profile.get(
        "structural_indexes"
    )

    if (
        not isinstance(
            structural_indexes,
            Mapping,
        )
        or structural_indexes.get(
            "layer_index_count"
        )
        != 15
        or structural_indexes.get(
            "group_index_count"
        )
        != 4
        or structural_indexes.get(
            "artifact_index_count"
        )
        != 4
        or structural_indexes.get(
            "profile_navigation_indexes_only"
        )
        is not True
        or structural_indexes.get(
            "upstream_index_rebuild_performed"
        )
        is not False
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Final structural index contract is invalid."
        )

    if (
        final_summary.get(
            "final_result_status"
        )
        != "SEMANTIC_ARTICLE_PROFILE_RESULT_READY"
        or final_summary.get(
            "profile_schema_version"
        )
        != "canonical_semantic_article_profile_v1"
        or final_summary.get(
            "source_builder_phase"
        )
        != "4.6.17"
        or final_summary.get(
            "source_builder_patch"
        )
        != "4.6.17J"
        or final_summary.get(
            "profile_section_count"
        )
        != 8
        or final_summary.get(
            "source_layer_count"
        )
        != 15
        or final_summary.get(
            "source_group_count"
        )
        != 4
        or final_summary.get(
            "cross_layer_artifact_count"
        )
        != 4
        or final_summary.get(
            "profile_certification_ready"
        )
        is not True
        or final_summary.get(
            "profile_certification_performed"
        )
        is not False
        or final_summary.get(
            "profile_persistence_performed"
        )
        is not False
    ):
        raise CertifiedSemanticArticleProfileBuilderError(
            "Final 4.6.17 summary contract is invalid."
        )

    certification = {
        "certification_status":
            "CERTIFIED",

        "certification_scope":
            "FULL_SEMANTIC_ARTICLE_PROFILE_BUILDER",

        "certified_phase":
            "4.6.17",

        "certified_source_patch":
            "4.6.17K",

        "certification_mode":
            "FULL_BUILDER_STRUCTURAL_PRESERVATION_CERTIFICATION",

        "architecture_definition_certified":
            True,

        "certified_input_contract_certified":
            True,

        "certified_consolidation_intake_certified":
            True,

        "profile_identity_source_authority_assembly_certified":
            True,

        "semantic_layer_profile_assembly_certified":
            True,

        "semantic_group_profile_assembly_certified":
            True,

        "cross_layer_artifact_profile_assembly_certified":
            True,

        "governed_state_profile_assembly_certified":
            True,

        "profile_structural_index_construction_certified":
            True,

        "canonical_profile_assembly_certified":
            True,

        "final_profile_result_contract_certified":
            True,

        "all_15_layer_profiles_certified":
            True,

        "all_four_semantic_group_profiles_certified":
            True,

        "all_four_cross_layer_artifact_profiles_certified":
            True,

        "governed_state_preservation_certified":
            True,

        "deterministic_builder_output_certified":
            True,

        "builder_source_immutability_certified":
            True,

        "profile_ready_for_4_6_18":
            True,

        "semantic_article_profile_certified":
            False,

        "semantic_article_profile_persisted":
            False,

        "semantic_state_modified":
            False,

        "semantic_meaning_rewritten":
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

        "profile_store_written":
            False,

        "linking_decisions_performed":
            False,

        "persistence_performed":
            False,
    }

    return {
        "schema_version":
            "certified_semantic_article_profile_builder_result_v1",

        "version":
            CERTIFIED_SEMANTIC_ARTICLE_PROFILE_BUILDER_VERSION,

        "phase":
            CERTIFIED_SEMANTIC_ARTICLE_PROFILE_BUILDER_PHASE,

        "patch":
            "4.6.17L",

        "status":
            "SEMANTIC_ARTICLE_PROFILE_BUILDER_CERTIFIED",

        "canonical_article_identity":
            deepcopy(
                dict(
                    canonical_identity
                )
            ),

        "builder_certification":
            certification,

        "final_semantic_article_profile":
            deepcopy(
                dict(
                    final_profile
                )
            ),

        "final_result_summary":
            deepcopy(
                dict(
                    final_summary
                )
            ),

        "certified_builder_source_result":
            deepcopy(
                dict(
                    final_profile_result
                )
            ),

        "profile_identity":
            deepcopy(
                final_profile_result[
                    "profile_identity"
                ]
            ),

        "source_authority_profile":
            deepcopy(
                final_profile_result[
                    "source_authority_profile"
                ]
            ),

        "semantic_layer_profile":
            deepcopy(
                final_profile_result[
                    "semantic_layer_profile"
                ]
            ),

        "semantic_group_profile":
            deepcopy(
                final_profile_result[
                    "semantic_group_profile"
                ]
            ),

        "cross_layer_artifact_profile":
            deepcopy(
                final_profile_result[
                    "cross_layer_artifact_profile"
                ]
            ),

        "governed_state_profile":
            deepcopy(
                final_profile_result[
                    "governed_state_profile"
                ]
            ),

        "structural_indexes":
            deepcopy(
                final_profile_result[
                    "structural_indexes"
                ]
            ),

        "canonical_article_semantic_representation":
            deepcopy(
                final_profile_result[
                    "canonical_article_semantic_representation"
                ]
            ),

        "normalized_layers":
            deepcopy(
                final_profile_result[
                    "normalized_layers"
                ]
            ),

        "normalized_group_index":
            deepcopy(
                final_profile_result[
                    "normalized_group_index"
                ]
            ),

        "processing_boundaries": {
            "architecture_definition_certified":
                True,

            "certified_4_6_16_input_contract_certified":
                True,

            "certified_consolidation_intake_certified":
                True,

            "profile_identity_source_authority_assembly_certified":
                True,

            "semantic_layer_group_profile_assembly_certified":
                True,

            "cross_layer_artifact_profile_assembly_certified":
                True,

            "governed_state_profile_assembly_certified":
                True,

            "profile_structural_index_construction_certified":
                True,

            "canonical_profile_assembly_certified":
                True,

            "final_profile_result_contract_certified":
                True,

            "full_builder_certification_performed":
                True,

            "profile_ready_for_4_6_18_certification":
                True,

            "semantic_article_profile_certified":
                False,

            "semantic_article_profile_persisted":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "source_authority_override_performed":
                False,

            "artifact_recomputation_performed":
                False,

            "upstream_index_rebuild_performed":
                False,

            "semantic_reclassification_performed":
                False,

            "semantic_count_recalculation_performed":
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

            "profile_store_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

        "next_stage":
            "semantic_article_profile_certification",
    }

