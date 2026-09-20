"""
LinkCraftor Semantic Intelligence
Phase 4.6.18 ? Semantic Article Profile Certification

Canonical rule:

Certify the structural and preservation integrity of the Semantic Article
Profile produced by the certified 4.6.17 builder, without re-running Semantic
Intelligence, reinterpreting meaning, modifying governed state, recomputing
confidence, resolving conflicts, persisting the profile, or making linking
decisions.

4.6.18 certifies the PROFILE.

4.6.17 certified the BUILDER.

Those are deliberately separate authorities.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


SEMANTIC_ARTICLE_PROFILE_CERTIFICATION_VERSION = (
    "semantic_article_profile_certification_v1"
)

SEMANTIC_ARTICLE_PROFILE_CERTIFICATION_PHASE = "4.6.18"


class SemanticArticleProfileCertificationError(ValueError):
    """Raised when the profile-certification contract is violated."""


# =====================================================================
# Canonical 4.6.17L source contract
# =====================================================================

_CERTIFIED_PROFILE_BUILDER_INPUT_CONTRACT = {
    "schema_version":
        "certified_semantic_article_profile_builder_result_v1",

    "version":
        "certified_semantic_article_profile_builder_v1",

    "phase":
        "4.6.17",

    "patch":
        "4.6.17L",

    "status":
        "SEMANTIC_ARTICLE_PROFILE_BUILDER_CERTIFIED",

    "persistence_policy":
        "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

    "next_stage":
        "semantic_article_profile_certification",
}


_REQUIRED_PROFILE_SECTION_ORDER = (
    "profile_identity",
    "source_authority",
    "semantic_layers",
    "semantic_groups",
    "cross_layer_artifacts",
    "governed_state",
    "structural_indexes",
    "certified_source_semantic_representation",
)


_REQUIRED_SEMANTIC_LAYER_ORDER = (
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


_REQUIRED_SEMANTIC_GROUP_ORDER = (
    "foundational_semantic_intelligence",
    "structured_reasoning_intelligence",
    "contextual_comparative_intelligence",
    "symbolic_neural_hybrid_intelligence",
)


_REQUIRED_SEMANTIC_GROUP_MEMBERSHIP = {
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


_REQUIRED_CROSS_LAYER_ARTIFACT_ORDER = (
    "article_identity_alignment",
    "provenance_alignment",
    "state_indexes",
    "conflict_uncertainty_abstention_preservation",
)


# =====================================================================
# Certification preservation rules
# =====================================================================

_PROFILE_CERTIFICATION_PRESERVATION_RULES = (
    "PRESERVE_CANONICAL_ARTICLE_IDENTITY",
    "PRESERVE_PROFILE_IDENTITY",
    "PRESERVE_SOURCE_AUTHORITY",
    "PRESERVE_ALL_15_SEMANTIC_LAYERS",
    "PRESERVE_CANONICAL_LAYER_ORDER",
    "PRESERVE_ALL_FOUR_SEMANTIC_GROUPS",
    "PRESERVE_CANONICAL_GROUP_ORDER",
    "PRESERVE_GROUP_MEMBERSHIP",
    "PRESERVE_ALL_FOUR_CROSS_LAYER_ARTIFACTS",
    "PRESERVE_GOVERNED_CONFLICT_STATE",
    "PRESERVE_UNCERTAINTY_STATE",
    "PRESERVE_CONFIDENCE_STATE",
    "PRESERVE_UNRESOLVED_STATE",
    "PRESERVE_ABSTENTION_STATE",
    "PRESERVE_STRUCTURAL_INDEXES",
    "PRESERVE_CERTIFIED_SOURCE_SEMANTIC_REPRESENTATION",
    "PRESERVE_SOURCE_MEANING",
    "PRESERVE_SOURCE_AUTHORITY_BOUNDARIES",
    "PRESERVE_ARTICLE_LOCAL_BOUNDARY",
    "PRESERVE_TRANSIENT_LIFECYCLE",
)


# =====================================================================
# Allowed operations
# =====================================================================

_PROFILE_CERTIFICATION_ALLOWED_OPERATIONS = (
    "CERTIFIED_BUILDER_RESULT_VALIDATION",
    "PROFILE_IDENTITY_INTEGRITY_CERTIFICATION",
    "SEMANTIC_LAYER_INTEGRITY_CERTIFICATION",
    "SEMANTIC_GROUP_INTEGRITY_CERTIFICATION",
    "CROSS_LAYER_ARTIFACT_INTEGRITY_CERTIFICATION",
    "GOVERNED_STATE_INTEGRITY_CERTIFICATION",
    "STRUCTURAL_INDEX_INTEGRITY_CERTIFICATION",
    "CANONICAL_PROFILE_INTEGRITY_CERTIFICATION",
    "DETERMINISTIC_STRUCTURAL_COMPARISON",
    "EXACT_PRESERVATION_VALIDATION",
    "PROFILE_CERTIFICATION_PACKAGING",
    "DEEP_COPY_PRESERVATION",
)


# =====================================================================
# Forbidden operations
# =====================================================================

_PROFILE_CERTIFICATION_FORBIDDEN_OPERATIONS = (
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
    "SEMANTIC_STATE_MODIFICATION",
    "SEMANTIC_MERGE",
    "CROSS_LAYER_REASONING",
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
    "SEMANTIC_RECLASSIFICATION",
    "SEMANTIC_COUNT_RECALCULATION",
    "FUZZY_SEMANTIC_DEDUPLICATION",
    "SOURCE_AUTHORITY_OVERRIDE",
    "SYMBOLIC_CONSTRAINT_OVERRIDE",
    "TRUTH_ASSESSMENT",
    "EXTERNAL_VALIDATION",
    "EXTERNAL_MODEL_CALL",
    "SEMANTIC_MEMORY_WRITE",
    "PROFILE_STORE_WRITE",
    "PERSISTENCE",
    "LINKING_DECISION",
)


# =====================================================================
# Authority model
# =====================================================================

_PROFILE_CERTIFICATION_AUTHORITY_MODEL = {
    "input_authority":
        "CERTIFIED_4.6.17L_SEMANTIC_ARTICLE_PROFILE_BUILDER_RESULT",

    "builder_certification_authority":
        "4.6.17L_FULL_SEMANTIC_ARTICLE_PROFILE_BUILDER_CERTIFICATION",

    "canonical_profile_authority":
        "4.6.17J_CANONICAL_SEMANTIC_ARTICLE_PROFILE",

    "profile_identity_authority":
        "4.6.17E_PROFILE_IDENTITY_VIA_4.6.17L",

    "semantic_layer_authority":
        "4.6.17F_SEMANTIC_LAYER_PROFILE_VIA_4.6.17L",

    "semantic_group_authority":
        "4.6.17F_SEMANTIC_GROUP_PROFILE_VIA_4.6.17L",

    "cross_layer_artifact_authority":
        "4.6.17G_CROSS_LAYER_ARTIFACT_PROFILE_VIA_4.6.17L",

    "governed_state_authority":
        "4.6.17H_GOVERNED_STATE_PROFILE_VIA_4.6.17L",

    "structural_index_authority":
        "4.6.17I_PROFILE_STRUCTURAL_INDEXES_VIA_4.6.17L",

    "profile_certification_authority":
        "4.6.18_SEMANTIC_ARTICLE_PROFILE_CERTIFICATION",

    "profile_persistence_authority":
        "4.6.19_PROFILE_STORE",

    "semantic_memory_authority":
        "4.6.28_SEMANTIC_MEMORY",
}


# =====================================================================
# Certification model
# =====================================================================

_PROFILE_CERTIFICATION_MODEL = {
    "certification_mode":
        "STRUCTURAL_AND_PRESERVATION_PROFILE_CERTIFICATION",

    "article_local_only":
        True,

    "transient_only":
        True,

    "certified_builder_required":
        True,

    "canonical_profile_required":
        True,

    "all_15_layers_required":
        True,

    "all_four_groups_required":
        True,

    "all_four_cross_layer_artifacts_required":
        True,

    "governed_state_integrity_required":
        True,

    "structural_index_integrity_required":
        True,

    "source_meaning_preservation_required":
        True,

    "source_authority_preservation_required":
        True,

    "new_semantic_reasoning_allowed":
        False,

    "semantic_rewrite_allowed":
        False,

    "semantic_state_modification_allowed":
        False,

    "cross_layer_reasoning_allowed":
        False,

    "conflict_resolution_allowed":
        False,

    "uncertainty_reinterpretation_allowed":
        False,

    "confidence_recalculation_allowed":
        False,

    "abstention_mutation_allowed":
        False,

    "profile_persistence_allowed":
        False,

    "semantic_memory_write_allowed":
        False,

    "linking_decision_allowed":
        False,
}


# =====================================================================
# Canonical certification stages
# =====================================================================

_PROFILE_CERTIFICATION_STAGE_ORDER = (
    "certified_builder_intake_validation",
    "profile_identity_certification",
    "semantic_layer_group_certification",
    "cross_layer_artifact_certification",
    "governed_state_certification",
    "structural_index_certification",
    "canonical_profile_integrity_certification",
    "final_certified_semantic_article_profile_result",
    "full_profile_certification_hard_certification",
)


def get_semantic_article_profile_certification_architecture_v1() -> dict[str, Any]:
    """
    Return the frozen Phase 4.6.18 certification architecture.

    Architecture definition only.
    No profile is certified by this function.
    """

    return {
        "schema_version":
            "semantic_article_profile_certification_architecture_v1",

        "version":
            SEMANTIC_ARTICLE_PROFILE_CERTIFICATION_VERSION,

        "phase":
            SEMANTIC_ARTICLE_PROFILE_CERTIFICATION_PHASE,

        "patch":
            "4.6.18B",

        "status":
            "SEMANTIC_ARTICLE_PROFILE_CERTIFICATION_ARCHITECTURE_DEFINED",

        "certified_builder_input_contract":
            deepcopy(
                _CERTIFIED_PROFILE_BUILDER_INPUT_CONTRACT
            ),

        "required_profile_section_order":
            list(
                _REQUIRED_PROFILE_SECTION_ORDER
            ),

        "required_semantic_layer_order":
            list(
                _REQUIRED_SEMANTIC_LAYER_ORDER
            ),

        "required_semantic_group_order":
            list(
                _REQUIRED_SEMANTIC_GROUP_ORDER
            ),

        "required_semantic_group_membership": {
            group_name:
                list(
                    members
                )
            for group_name, members in (
                _REQUIRED_SEMANTIC_GROUP_MEMBERSHIP.items()
            )
        },

        "required_cross_layer_artifact_order":
            list(
                _REQUIRED_CROSS_LAYER_ARTIFACT_ORDER
            ),

        "preservation_rules":
            list(
                _PROFILE_CERTIFICATION_PRESERVATION_RULES
            ),

        "allowed_operations":
            list(
                _PROFILE_CERTIFICATION_ALLOWED_OPERATIONS
            ),

        "forbidden_operations":
            list(
                _PROFILE_CERTIFICATION_FORBIDDEN_OPERATIONS
            ),

        "authority_model":
            deepcopy(
                _PROFILE_CERTIFICATION_AUTHORITY_MODEL
            ),

        "certification_model":
            deepcopy(
                _PROFILE_CERTIFICATION_MODEL
            ),

        "certification_stage_order":
            list(
                _PROFILE_CERTIFICATION_STAGE_ORDER
            ),

        "profile_certification_boundary": {
            "builder_already_certified":
                True,

            "profile_enters_uncertified":
                True,

            "profile_enters_unpersisted":
                True,

            "profile_may_be_certified_by_4_6_18":
                True,

            "profile_may_be_persisted_by_4_6_18":
                False,

            "profile_store_owner":
                "4.6.19",

            "semantic_memory_owner":
                "4.6.28",

            "certification_changes_semantic_meaning":
                False,

            "certification_changes_governed_state":
                False,

            "certification_recalculates_confidence":
                False,

            "certification_resolves_conflict":
                False,

            "certification_creates_or_removes_abstention":
                False,

            "certification_makes_linking_decisions":
                False,
        },

        "processing_boundaries": {
            "architecture_definition_performed":
                True,

            "profile_certification_performed":
                False,

            "profile_persistence_performed":
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
            "certified_builder_intake_validation",
    }


# =====================================================================
# PATCH 4.6.18C ? Certified Builder Intake Validation
# =====================================================================

def validate_certified_profile_builder_intake_v1(
    certified_builder_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate the exact certified 4.6.17L builder result before profile
    certification begins.

    C validates source authority and profile readiness only.

    C does NOT certify the profile itself.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        certified_builder_result,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "certified_builder_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.17L envelope
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "certified_semantic_article_profile_builder_result_v1",
        ),
        (
            "version",
            "certified_semantic_article_profile_builder_v1",
        ),
        (
            "phase",
            "4.6.17",
        ),
        (
            "patch",
            "4.6.17L",
        ),
        (
            "status",
            "SEMANTIC_ARTICLE_PROFILE_BUILDER_CERTIFIED",
        ),
        (
            "persistence_policy",
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        ),
        (
            "next_stage",
            "semantic_article_profile_certification",
        ),
    ):

        if certified_builder_result.get(
            field
        ) != expected:
            raise SemanticArticleProfileCertificationError(
                "Invalid certified builder contract field: "
                + field
            )

    canonical_identity = certified_builder_result.get(
        "canonical_article_identity"
    )

    builder_certification = certified_builder_result.get(
        "builder_certification"
    )

    final_profile = certified_builder_result.get(
        "final_semantic_article_profile"
    )

    final_summary = certified_builder_result.get(
        "final_result_summary"
    )

    boundaries = certified_builder_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "canonical_article_identity",
            canonical_identity,
        ),
        (
            "builder_certification",
            builder_certification,
        ),
        (
            "final_semantic_article_profile",
            final_profile,
        ),
        (
            "final_result_summary",
            final_summary,
        ),
        (
            "processing_boundaries",
            boundaries,
        ),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise SemanticArticleProfileCertificationError(
                name + " is missing or invalid."
            )

    # -------------------------------------------------------------
    # Builder certification authority
    # -------------------------------------------------------------

    for field, expected in (
        (
            "certification_status",
            "CERTIFIED",
        ),
        (
            "certification_scope",
            "FULL_SEMANTIC_ARTICLE_PROFILE_BUILDER",
        ),
        (
            "certified_phase",
            "4.6.17",
        ),
        (
            "certified_source_patch",
            "4.6.17K",
        ),
        (
            "certification_mode",
            "FULL_BUILDER_STRUCTURAL_PRESERVATION_CERTIFICATION",
        ),
    ):

        if builder_certification.get(
            field
        ) != expected:
            raise SemanticArticleProfileCertificationError(
                "Builder certification field drifted: "
                + field
            )

    required_builder_true = (
        "architecture_definition_certified",
        "certified_input_contract_certified",
        "certified_consolidation_intake_certified",
        "profile_identity_source_authority_assembly_certified",
        "semantic_layer_profile_assembly_certified",
        "semantic_group_profile_assembly_certified",
        "cross_layer_artifact_profile_assembly_certified",
        "governed_state_profile_assembly_certified",
        "profile_structural_index_construction_certified",
        "canonical_profile_assembly_certified",
        "final_profile_result_contract_certified",
        "all_15_layer_profiles_certified",
        "all_four_semantic_group_profiles_certified",
        "all_four_cross_layer_artifact_profiles_certified",
        "governed_state_preservation_certified",
        "deterministic_builder_output_certified",
        "builder_source_immutability_certified",
        "profile_ready_for_4_6_18",
    )

    for field in required_builder_true:

        if builder_certification.get(
            field
        ) is not True:
            raise SemanticArticleProfileCertificationError(
                "Required builder certification flag is not True: "
                + field
            )

    required_builder_false = (
        "semantic_article_profile_certified",
        "semantic_article_profile_persisted",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
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
    )

    for field in required_builder_false:

        if builder_certification.get(
            field
        ) is not False:
            raise SemanticArticleProfileCertificationError(
                "Forbidden builder certification flag is not False: "
                + field
            )

    # -------------------------------------------------------------
    # Canonical profile entry contract
    # -------------------------------------------------------------

    for field, expected in (
        (
            "profile_schema_version",
            "canonical_semantic_article_profile_v1",
        ),
        (
            "profile_status",
            "CANONICAL_SEMANTIC_ARTICLE_PROFILE_ASSEMBLED",
        ),
        (
            "profile_builder_phase",
            "4.6.17",
        ),
        (
            "profile_builder_patch",
            "4.6.17J",
        ),
        (
            "profile_mode",
            "CERTIFIED_SOURCE_STRUCTURAL_PROFILE",
        ),
    ):

        if final_profile.get(
            field
        ) != expected:
            raise SemanticArticleProfileCertificationError(
                "Canonical profile contract drifted: "
                + field
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
        raise SemanticArticleProfileCertificationError(
            "Profile must enter 4.6.18 ready, uncertified and unpersisted."
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
        raise SemanticArticleProfileCertificationError(
            "Profile structural accounting is invalid."
        )

    if (
        final_profile.get(
            "profile_section_order"
        )
        != list(
            _REQUIRED_PROFILE_SECTION_ORDER
        )
    ):
        raise SemanticArticleProfileCertificationError(
            "Profile section order drifted."
        )

    profile_identity = final_profile.get(
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
        raise SemanticArticleProfileCertificationError(
            "Canonical article identity drifted."
        )

    for field in (
        "source_meaning_preserved",
        "source_authority_preserved",
        "governed_state_preserved",
        "profile_navigation_only_indexes",
    ):

        if final_profile.get(
            field
        ) is not True:
            raise SemanticArticleProfileCertificationError(
                "Required profile preservation field is not True: "
                + field
            )

    profile_forbidden_true = (
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

    for field in profile_forbidden_true:

        if final_profile.get(
            field
        ) is not False:
            raise SemanticArticleProfileCertificationError(
                "Profile contains forbidden pre-certification state: "
                + field
            )

    # -------------------------------------------------------------
    # Exact top-level/profile preservation
    # -------------------------------------------------------------

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

    for profile_key, source_key in preservation_pairs:

        if (
            final_profile.get(
                profile_key
            )
            != certified_builder_result.get(
                source_key
            )
        ):
            raise SemanticArticleProfileCertificationError(
                profile_key
                + " drifted from certified builder output."
            )

    # -------------------------------------------------------------
    # Layer / group / artifact presence
    # -------------------------------------------------------------

    semantic_layers = final_profile.get(
        "semantic_layers"
    )

    semantic_groups = final_profile.get(
        "semantic_groups"
    )

    cross_layer_artifacts = final_profile.get(
        "cross_layer_artifacts"
    )

    governed_state = final_profile.get(
        "governed_state"
    )

    structural_indexes = final_profile.get(
        "structural_indexes"
    )

    for name, value in (
        (
            "semantic_layers",
            semantic_layers,
        ),
        (
            "semantic_groups",
            semantic_groups,
        ),
        (
            "cross_layer_artifacts",
            cross_layer_artifacts,
        ),
        (
            "governed_state",
            governed_state,
        ),
        (
            "structural_indexes",
            structural_indexes,
        ),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise SemanticArticleProfileCertificationError(
                name + " is missing or invalid."
            )

    if (
        semantic_layers.get(
            "canonical_layer_order"
        )
        != list(
            _REQUIRED_SEMANTIC_LAYER_ORDER
        )
        or semantic_layers.get(
            "layer_count"
        )
        != 15
        or len(
            semantic_layers.get(
                "layer_records",
                []
            )
        )
        != 15
    ):
        raise SemanticArticleProfileCertificationError(
            "Semantic layer intake contract is invalid."
        )

    if (
        semantic_groups.get(
            "canonical_group_order"
        )
        != list(
            _REQUIRED_SEMANTIC_GROUP_ORDER
        )
        or semantic_groups.get(
            "group_count"
        )
        != 4
        or len(
            semantic_groups.get(
                "group_records",
                []
            )
        )
        != 4
    ):
        raise SemanticArticleProfileCertificationError(
            "Semantic group intake contract is invalid."
        )

    if (
        cross_layer_artifacts.get(
            "canonical_artifact_order"
        )
        != list(
            _REQUIRED_CROSS_LAYER_ARTIFACT_ORDER
        )
        or cross_layer_artifacts.get(
            "artifact_count"
        )
        != 4
        or len(
            cross_layer_artifacts.get(
                "artifact_records",
                []
            )
        )
        != 4
    ):
        raise SemanticArticleProfileCertificationError(
            "Cross-layer artifact intake contract is invalid."
        )

    if (
        governed_state.get(
            "unresolved_candidate_ids"
        )
        != governed_state.get(
            "abstention_candidate_ids"
        )
    ):
        raise SemanticArticleProfileCertificationError(
            "Governed unresolved/abstention state drifted."
        )

    if (
        structural_indexes.get(
            "index_status"
        )
        != "PROFILE_STRUCTURAL_INDEXES_CONSTRUCTED"
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
        raise SemanticArticleProfileCertificationError(
            "Structural index intake contract is invalid."
        )

    # -------------------------------------------------------------
    # Final source summary / boundary contract
    # -------------------------------------------------------------

    if (
        final_summary.get(
            "final_result_status"
        )
        != "SEMANTIC_ARTICLE_PROFILE_RESULT_READY"
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
        raise SemanticArticleProfileCertificationError(
            "Final builder summary is invalid."
        )

    required_boundary_true = (
        "architecture_definition_certified",
        "certified_4_6_16_input_contract_certified",
        "certified_consolidation_intake_certified",
        "profile_identity_source_authority_assembly_certified",
        "semantic_layer_group_profile_assembly_certified",
        "cross_layer_artifact_profile_assembly_certified",
        "governed_state_profile_assembly_certified",
        "profile_structural_index_construction_certified",
        "canonical_profile_assembly_certified",
        "final_profile_result_contract_certified",
        "full_builder_certification_performed",
        "profile_ready_for_4_6_18_certification",
    )

    for field in required_boundary_true:

        if boundaries.get(
            field
        ) is not True:
            raise SemanticArticleProfileCertificationError(
                "Required 4.6.17L boundary is not True: "
                + field
            )

    required_boundary_false = (
        "semantic_article_profile_certified",
        "semantic_article_profile_persisted",
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

    for field in required_boundary_false:

        if boundaries.get(
            field
        ) is not False:
            raise SemanticArticleProfileCertificationError(
                "Forbidden 4.6.17L boundary is not False: "
                + field
            )

    return {
        "schema_version":
            "semantic_article_profile_certification_intake_v1",

        "version":
            SEMANTIC_ARTICLE_PROFILE_CERTIFICATION_VERSION,

        "phase":
            SEMANTIC_ARTICLE_PROFILE_CERTIFICATION_PHASE,

        "patch":
            "4.6.18C",

        "status":
            "CERTIFIED_PROFILE_BUILDER_INTAKE_VALIDATED",

        "canonical_article_identity":
            deepcopy(
                dict(
                    canonical_identity
                )
            ),

        "builder_certification":
            deepcopy(
                dict(
                    builder_certification
                )
            ),

        "profile_to_certify":
            deepcopy(
                dict(
                    final_profile
                )
            ),

        "source_final_result_summary":
            deepcopy(
                dict(
                    final_summary
                )
            ),

        "source_processing_boundaries":
            deepcopy(
                dict(
                    boundaries
                )
            ),

        "source_certified_builder_result":
            deepcopy(
                dict(
                    certified_builder_result
                )
            ),

        "processing_boundaries": {
            "certified_builder_intake_validation_performed":
                True,

            "builder_certification_validated":
                True,

            "profile_readiness_validated":
                True,

            "profile_uncertified_state_preserved":
                True,

            "profile_unpersisted_state_preserved":
                True,

            "profile_certification_performed":
                False,

            "profile_persistence_performed":
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
            "profile_identity_certification",
    }


# =====================================================================
# PATCH 4.6.18D ? Profile Identity Certification
# =====================================================================

def certify_profile_identity_v1(
    intake_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Certify the identity integrity of the Semantic Article Profile.

    D certifies only profile identity.

    It does NOT certify semantic layers, groups, artifacts, governed state,
    structural indexes, or the complete profile.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        intake_result,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "intake_result must be a mapping."
        )

    for field, expected in (
        (
            "schema_version",
            "semantic_article_profile_certification_intake_v1",
        ),
        (
            "version",
            "semantic_article_profile_certification_v1",
        ),
        (
            "phase",
            "4.6.18",
        ),
        (
            "patch",
            "4.6.18C",
        ),
        (
            "status",
            "CERTIFIED_PROFILE_BUILDER_INTAKE_VALIDATED",
        ),
        (
            "persistence_policy",
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        ),
        (
            "next_stage",
            "profile_identity_certification",
        ),
    ):

        if intake_result.get(
            field
        ) != expected:
            raise SemanticArticleProfileCertificationError(
                "Invalid 4.6.18C intake contract field: "
                + field
            )

    boundaries = intake_result.get(
        "processing_boundaries"
    )

    canonical_identity = intake_result.get(
        "canonical_article_identity"
    )

    profile = intake_result.get(
        "profile_to_certify"
    )

    source_builder_result = intake_result.get(
        "source_certified_builder_result"
    )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "4.6.18C processing boundaries are missing."
        )

    if not isinstance(
        canonical_identity,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Canonical article identity is missing."
        )

    if not isinstance(
        profile,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Profile to certify is missing."
        )

    if not isinstance(
        source_builder_result,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Certified builder source result is missing."
        )

    required_intake_true = (
        "certified_builder_intake_validation_performed",
        "builder_certification_validated",
        "profile_readiness_validated",
        "profile_uncertified_state_preserved",
        "profile_unpersisted_state_preserved",
    )

    for field in required_intake_true:

        if boundaries.get(
            field
        ) is not True:
            raise SemanticArticleProfileCertificationError(
                "Required 4.6.18C boundary is not True: "
                + field
            )

    required_intake_false = (
        "profile_certification_performed",
        "profile_persistence_performed",
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

    for field in required_intake_false:

        if boundaries.get(
            field
        ) is not False:
            raise SemanticArticleProfileCertificationError(
                "Forbidden 4.6.18C boundary is not False: "
                + field
            )

    profile_identity = profile.get(
        "profile_identity"
    )

    if not isinstance(
        profile_identity,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Profile identity is missing."
        )

    source_profile_identity = source_builder_result.get(
        "profile_identity"
    )

    if not isinstance(
        source_profile_identity,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Certified source profile identity is missing."
        )

    # -------------------------------------------------------------
    # Exact identity envelope
    # -------------------------------------------------------------

    if (
        profile_identity
        != source_profile_identity
    ):
        raise SemanticArticleProfileCertificationError(
            "Profile identity drifted from certified 4.6.17L identity."
        )

    if (
        profile_identity.get(
            "canonical_article_identity"
        )
        != canonical_identity
    ):
        raise SemanticArticleProfileCertificationError(
            "Profile canonical article identity is not exact."
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
        or not article_id
        or not isinstance(
            workspace_id,
            str,
        )
        or not workspace_id
    ):
        raise SemanticArticleProfileCertificationError(
            "Canonical article identity fields are invalid."
        )

    if (
        profile_identity.get(
            "article_id"
        )
        != article_id
        or profile_identity.get(
            "workspace_id"
        )
        != workspace_id
    ):
        raise SemanticArticleProfileCertificationError(
            "Profile article/workspace identity drifted."
        )

    # -------------------------------------------------------------
    # Certified identity authority
    # -------------------------------------------------------------

    if (
        profile_identity.get(
            "profile_identity_status"
        )
        != "PROFILE_IDENTITY_ASSEMBLED"
    ):
        raise SemanticArticleProfileCertificationError(
            "Profile identity status is invalid."
        )

    if (
        profile_identity.get(
            "identity_authority"
        )
        != "4.6.16P_CANONICAL_ARTICLE_IDENTITY"
    ):
        raise SemanticArticleProfileCertificationError(
            "Profile identity authority drifted."
        )

    if (
        profile_identity.get(
            "identity_source_phase"
        )
        != "4.6.16"
        or profile_identity.get(
            "identity_source_patch"
        )
        != "4.6.16P"
    ):
        raise SemanticArticleProfileCertificationError(
            "Profile identity source phase/patch drifted."
        )

    if (
        profile_identity.get(
            "identity_certified"
        )
        is not True
        or profile_identity.get(
            "identity_preserved"
        )
        is not True
    ):
        raise SemanticArticleProfileCertificationError(
            "Profile identity was not certified/preserved upstream."
        )

    if (
        profile_identity.get(
            "identity_rewritten"
        )
        is not False
        or profile_identity.get(
            "identity_inference_performed"
        )
        is not False
    ):
        raise SemanticArticleProfileCertificationError(
            "Profile identity contains forbidden rewrite/inference state."
        )

    # -------------------------------------------------------------
    # Cross-location identity alignment
    # -------------------------------------------------------------

    builder_identity = source_builder_result.get(
        "canonical_article_identity"
    )

    builder_profile = source_builder_result.get(
        "final_semantic_article_profile"
    )

    if not isinstance(
        builder_profile,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Certified source canonical profile is missing."
        )

    if (
        builder_identity
        != canonical_identity
        or builder_profile.get(
            "profile_identity"
        )
        != profile_identity
    ):
        raise SemanticArticleProfileCertificationError(
            "Certified builder identity alignment drifted."
        )

    certified_representation = profile.get(
        "certified_source_semantic_representation"
    )

    if not isinstance(
        certified_representation,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Certified source semantic representation is missing."
        )

    if (
        certified_representation.get(
            "canonical_article_identity"
        )
        != canonical_identity
    ):
        raise SemanticArticleProfileCertificationError(
            "Certified semantic representation identity drifted."
        )

    source_authority = profile.get(
        "source_authority"
    )

    if not isinstance(
        source_authority,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Source authority profile is missing."
        )

    if (
        source_authority.get(
            "canonical_identity_authority"
        )
        != "4.6.16P_CANONICAL_ARTICLE_IDENTITY"
    ):
        raise SemanticArticleProfileCertificationError(
            "Canonical identity authority boundary drifted."
        )

    identity_certification = {
        "certification_status":
            "CERTIFIED",

        "certification_scope":
            "SEMANTIC_ARTICLE_PROFILE_IDENTITY",

        "certification_mode":
            "EXACT_CERTIFIED_IDENTITY_PRESERVATION",

        "canonical_article_identity":
            deepcopy(
                dict(
                    canonical_identity
                )
            ),

        "article_id":
            article_id,

        "workspace_id":
            workspace_id,

        "identity_authority":
            "4.6.16P_CANONICAL_ARTICLE_IDENTITY",

        "identity_source_phase":
            "4.6.16",

        "identity_source_patch":
            "4.6.16P",

        "profile_identity_exact":
            True,

        "builder_identity_exact":
            True,

        "canonical_representation_identity_exact":
            True,

        "source_authority_identity_exact":
            True,

        "identity_certified_upstream":
            True,

        "identity_preserved":
            True,

        "identity_rewritten":
            False,

        "identity_inference_performed":
            False,

        "semantic_state_modified":
            False,

        "new_reasoning_performed":
            False,
    }

    return {
        "schema_version":
            "semantic_article_profile_identity_certification_v1",

        "version":
            SEMANTIC_ARTICLE_PROFILE_CERTIFICATION_VERSION,

        "phase":
            SEMANTIC_ARTICLE_PROFILE_CERTIFICATION_PHASE,

        "patch":
            "4.6.18D",

        "status":
            "PROFILE_IDENTITY_CERTIFIED",

        "canonical_article_identity":
            deepcopy(
                dict(
                    canonical_identity
                )
            ),

        "identity_certification":
            identity_certification,

        "profile_to_certify":
            deepcopy(
                dict(
                    profile
                )
            ),

        "source_profile_identity":
            deepcopy(
                dict(
                    profile_identity
                )
            ),

        "source_intake_result":
            deepcopy(
                dict(
                    intake_result
                )
            ),

        "processing_boundaries": {
            "certified_builder_intake_validation_preserved":
                True,

            "profile_identity_certification_performed":
                True,

            "profile_identity_exact_preservation_certified":
                True,

            "profile_identity_authority_certified":
                True,

            "cross_location_identity_alignment_certified":
                True,

            "semantic_layer_group_certification_performed":
                False,

            "cross_layer_artifact_certification_performed":
                False,

            "governed_state_certification_performed":
                False,

            "structural_index_certification_performed":
                False,

            "canonical_profile_integrity_certification_performed":
                False,

            "final_profile_certification_performed":
                False,

            "profile_persistence_performed":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "identity_rewritten":
                False,

            "identity_inference_performed":
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
            "semantic_layer_group_certification",
    }


# =====================================================================
# PATCH 4.6.18E ? Semantic Layer / Group Certification
# =====================================================================

def certify_semantic_layer_group_profiles_v1(
    identity_certification_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Certify the exact structural and preservation integrity of the
    15 semantic-layer profiles and four semantic-group profiles.

    No Semantic Intelligence is re-run here.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        identity_certification_result,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "identity_certification_result must be a mapping."
        )

    for field, expected in (
        (
            "schema_version",
            "semantic_article_profile_identity_certification_v1",
        ),
        (
            "version",
            "semantic_article_profile_certification_v1",
        ),
        (
            "phase",
            "4.6.18",
        ),
        (
            "patch",
            "4.6.18D",
        ),
        (
            "status",
            "PROFILE_IDENTITY_CERTIFIED",
        ),
        (
            "persistence_policy",
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        ),
        (
            "next_stage",
            "semantic_layer_group_certification",
        ),
    ):

        if identity_certification_result.get(field) != expected:
            raise SemanticArticleProfileCertificationError(
                "Invalid 4.6.18D lifecycle field: " + field
            )

    boundaries = identity_certification_result.get(
        "processing_boundaries"
    )

    profile = identity_certification_result.get(
        "profile_to_certify"
    )

    source_intake = identity_certification_result.get(
        "source_intake_result"
    )

    if not isinstance(boundaries, Mapping):
        raise SemanticArticleProfileCertificationError(
            "4.6.18D processing boundaries are missing."
        )

    if not isinstance(profile, Mapping):
        raise SemanticArticleProfileCertificationError(
            "Profile to certify is missing."
        )

    if not isinstance(source_intake, Mapping):
        raise SemanticArticleProfileCertificationError(
            "Source intake result is missing."
        )

    for field in (
        "certified_builder_intake_validation_preserved",
        "profile_identity_certification_performed",
        "profile_identity_exact_preservation_certified",
        "profile_identity_authority_certified",
        "cross_location_identity_alignment_certified",
    ):

        if boundaries.get(field) is not True:
            raise SemanticArticleProfileCertificationError(
                "Required 4.6.18D boundary is not True: " + field
            )

    for field in (
        "semantic_layer_group_certification_performed",
        "cross_layer_artifact_certification_performed",
        "governed_state_certification_performed",
        "structural_index_certification_performed",
        "canonical_profile_integrity_certification_performed",
        "final_profile_certification_performed",
        "profile_persistence_performed",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "identity_rewritten",
        "identity_inference_performed",
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

        if boundaries.get(field) is not False:
            raise SemanticArticleProfileCertificationError(
                "Forbidden 4.6.18D boundary is not False: " + field
            )

    semantic_layers = profile.get(
        "semantic_layers"
    )

    semantic_groups = profile.get(
        "semantic_groups"
    )

    if not isinstance(semantic_layers, Mapping):
        raise SemanticArticleProfileCertificationError(
            "Semantic-layer profile is missing."
        )

    if not isinstance(semantic_groups, Mapping):
        raise SemanticArticleProfileCertificationError(
            "Semantic-group profile is missing."
        )

    source_builder = source_intake.get(
        "source_certified_builder_result"
    )

    if not isinstance(source_builder, Mapping):
        raise SemanticArticleProfileCertificationError(
            "Certified builder source is missing."
        )

    if (
        semantic_layers
        != source_builder.get("semantic_layer_profile")
    ):
        raise SemanticArticleProfileCertificationError(
            "Semantic-layer profile drifted from certified builder."
        )

    if (
        semantic_groups
        != source_builder.get("semantic_group_profile")
    ):
        raise SemanticArticleProfileCertificationError(
            "Semantic-group profile drifted from certified builder."
        )

    if semantic_layers.get("profile_status") != (
        "SEMANTIC_LAYER_PROFILE_ASSEMBLED"
    ):
        raise SemanticArticleProfileCertificationError(
            "Semantic-layer profile status is invalid."
        )

    if semantic_layers.get("layer_count") != 15:
        raise SemanticArticleProfileCertificationError(
            "Semantic-layer count must be exactly 15."
        )

    if semantic_layers.get("canonical_layer_order") != list(
        _REQUIRED_SEMANTIC_LAYER_ORDER
    ):
        raise SemanticArticleProfileCertificationError(
            "Canonical semantic-layer order drifted."
        )

    layer_records = semantic_layers.get(
        "layer_records"
    )

    if (
        not isinstance(layer_records, list)
        or len(layer_records) != 15
    ):
        raise SemanticArticleProfileCertificationError(
            "Exactly 15 semantic-layer records are required."
        )

    layer_certification_records = []

    seen_layers = set()

    for ordinal, record in enumerate(
        layer_records,
        1,
    ):

        if not isinstance(record, Mapping):
            raise SemanticArticleProfileCertificationError(
                "Semantic-layer record is invalid."
            )

        expected_name = _REQUIRED_SEMANTIC_LAYER_ORDER[
            ordinal - 1
        ]

        layer_name = record.get(
            "layer_name"
        )

        if layer_name != expected_name:
            raise SemanticArticleProfileCertificationError(
                "Semantic-layer order/name drifted."
            )

        if layer_name in seen_layers:
            raise SemanticArticleProfileCertificationError(
                "Duplicate semantic-layer profile record."
            )

        seen_layers.add(
            layer_name
        )

        if record.get("ordinal") != ordinal:
            raise SemanticArticleProfileCertificationError(
                "Semantic-layer ordinal drifted."
            )

        profile_layer_id = record.get(
            "profile_layer_id"
        )

        if (
            not isinstance(profile_layer_id, str)
            or not profile_layer_id
        ):
            raise SemanticArticleProfileCertificationError(
                "Semantic-layer profile ID is invalid."
            )

        semantic_group = record.get(
            "semantic_group"
        )

        expected_group = None

        for group_name, members in (
            _REQUIRED_SEMANTIC_GROUP_MEMBERSHIP.items()
        ):
            if layer_name in members:
                expected_group = group_name
                break

        if semantic_group != expected_group:
            raise SemanticArticleProfileCertificationError(
                "Semantic-layer group assignment drifted."
            )

        if record.get(
            "source_payload_preserved"
        ) is not True:
            raise SemanticArticleProfileCertificationError(
                "Semantic-layer payload was not preserved."
            )

        if record.get(
            "source_authority_preserved"
        ) is not True:
            raise SemanticArticleProfileCertificationError(
                "Semantic-layer authority was not preserved."
            )

        if record.get(
            "new_reasoning_performed"
        ) is not False:
            raise SemanticArticleProfileCertificationError(
                "Semantic-layer profile contains new reasoning."
            )

        layer_certification_records.append(
            {
                "ordinal":
                    ordinal,

                "layer_name":
                    layer_name,

                "profile_layer_id":
                    profile_layer_id,

                "semantic_group":
                    semantic_group,

                "layer_certification_status":
                    "CERTIFIED",

                "source_payload_preserved":
                    True,

                "source_authority_preserved":
                    True,

                "semantic_state_modified":
                    False,

                "semantic_meaning_rewritten":
                    False,

                "new_reasoning_performed":
                    False,
            }
        )

    if semantic_layers.get(
        "all_layer_payloads_preserved"
    ) is not True:
        raise SemanticArticleProfileCertificationError(
            "All-layer payload preservation flag is invalid."
        )

    if semantic_layers.get(
        "all_layer_authorities_preserved"
    ) is not True:
        raise SemanticArticleProfileCertificationError(
            "All-layer authority preservation flag is invalid."
        )

    for field in (
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "cross_layer_reasoning_performed",
    ):

        if semantic_layers.get(field) is not False:
            raise SemanticArticleProfileCertificationError(
                "Forbidden semantic-layer state is not False: "
                + field
            )

    # -------------------------------------------------------------
    # Four semantic groups
    # -------------------------------------------------------------

    if semantic_groups.get("profile_status") != (
        "SEMANTIC_GROUP_PROFILE_ASSEMBLED"
    ):
        raise SemanticArticleProfileCertificationError(
            "Semantic-group profile status is invalid."
        )

    if semantic_groups.get("group_count") != 4:
        raise SemanticArticleProfileCertificationError(
            "Semantic-group count must be exactly four."
        )

    if semantic_groups.get("canonical_group_order") != list(
        _REQUIRED_SEMANTIC_GROUP_ORDER
    ):
        raise SemanticArticleProfileCertificationError(
            "Canonical semantic-group order drifted."
        )

    group_records = semantic_groups.get(
        "group_records"
    )

    if (
        not isinstance(group_records, list)
        or len(group_records) != 4
    ):
        raise SemanticArticleProfileCertificationError(
            "Exactly four semantic-group records are required."
        )

    group_certification_records = []

    seen_groups = set()

    for ordinal, record in enumerate(
        group_records,
        1,
    ):

        if not isinstance(record, Mapping):
            raise SemanticArticleProfileCertificationError(
                "Semantic-group record is invalid."
            )

        expected_name = _REQUIRED_SEMANTIC_GROUP_ORDER[
            ordinal - 1
        ]

        group_name = record.get(
            "group_name"
        )

        if group_name != expected_name:
            raise SemanticArticleProfileCertificationError(
                "Semantic-group order/name drifted."
            )

        if group_name in seen_groups:
            raise SemanticArticleProfileCertificationError(
                "Duplicate semantic-group profile record."
            )

        seen_groups.add(
            group_name
        )

        if record.get("ordinal") != ordinal:
            raise SemanticArticleProfileCertificationError(
                "Semantic-group ordinal drifted."
            )

        profile_group_id = record.get(
            "profile_group_id"
        )

        if (
            not isinstance(profile_group_id, str)
            or not profile_group_id
        ):
            raise SemanticArticleProfileCertificationError(
                "Semantic-group profile ID is invalid."
            )

        expected_members = list(
            _REQUIRED_SEMANTIC_GROUP_MEMBERSHIP[
                group_name
            ]
        )

        if record.get(
            "member_layer_order"
        ) != expected_members:
            raise SemanticArticleProfileCertificationError(
                "Semantic-group membership/order drifted."
            )

        if record.get(
            "source_group_preserved"
        ) is not True:
            raise SemanticArticleProfileCertificationError(
                "Semantic-group source was not preserved."
            )

        if record.get(
            "semantic_merge_performed"
        ) is not False:
            raise SemanticArticleProfileCertificationError(
                "Semantic-group merge was performed."
            )

        group_certification_records.append(
            {
                "ordinal":
                    ordinal,

                "group_name":
                    group_name,

                "profile_group_id":
                    profile_group_id,

                "member_layer_order":
                    deepcopy(
                        expected_members
                    ),

                "group_certification_status":
                    "CERTIFIED",

                "source_group_preserved":
                    True,

                "group_membership_preserved":
                    True,

                "semantic_merge_performed":
                    False,

                "cross_layer_reasoning_performed":
                    False,
            }
        )

    if semantic_groups.get(
        "all_group_payloads_preserved"
    ) is not True:
        raise SemanticArticleProfileCertificationError(
            "All-group payload preservation flag is invalid."
        )

    if semantic_groups.get(
        "all_group_memberships_preserved"
    ) is not True:
        raise SemanticArticleProfileCertificationError(
            "All-group membership preservation flag is invalid."
        )

    for field in (
        "semantic_merge_performed",
        "cross_layer_reasoning_performed",
    ):

        if semantic_groups.get(field) is not False:
            raise SemanticArticleProfileCertificationError(
                "Forbidden semantic-group state is not False: "
                + field
            )

    # -------------------------------------------------------------
    # Cross-check structural profile indexes without rebuilding them
    # -------------------------------------------------------------

    structural_indexes = profile.get(
        "structural_indexes"
    )

    if not isinstance(
        structural_indexes,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Structural indexes are missing."
        )

    if structural_indexes.get(
        "layer_index_count"
    ) != 15:
        raise SemanticArticleProfileCertificationError(
            "Layer structural-index count drifted."
        )

    if structural_indexes.get(
        "group_index_count"
    ) != 4:
        raise SemanticArticleProfileCertificationError(
            "Group structural-index count drifted."
        )

    layer_name_index = structural_indexes.get(
        "layer_name_index"
    )

    group_name_index = structural_indexes.get(
        "group_name_index"
    )

    group_membership_index = structural_indexes.get(
        "group_membership_index"
    )

    if not isinstance(layer_name_index, Mapping):
        raise SemanticArticleProfileCertificationError(
            "Layer name index is invalid."
        )

    if not isinstance(group_name_index, Mapping):
        raise SemanticArticleProfileCertificationError(
            "Group name index is invalid."
        )

    if not isinstance(group_membership_index, Mapping):
        raise SemanticArticleProfileCertificationError(
            "Group membership index is invalid."
        )

    for record in layer_records:

        if layer_name_index.get(
            record["layer_name"]
        ) != record["profile_layer_id"]:
            raise SemanticArticleProfileCertificationError(
                "Layer structural index drifted from layer profile."
            )

    for record in group_records:

        group_name = record[
            "group_name"
        ]

        if group_name_index.get(
            group_name
        ) != record[
            "profile_group_id"
        ]:
            raise SemanticArticleProfileCertificationError(
                "Group structural index drifted from group profile."
            )

        if group_membership_index.get(
            group_name
        ) != record[
            "member_layer_order"
        ]:
            raise SemanticArticleProfileCertificationError(
                "Group membership index drifted from group profile."
            )

    semantic_layer_group_certification = {
        "certification_status":
            "CERTIFIED",

        "certification_scope":
            "SEMANTIC_ARTICLE_PROFILE_LAYERS_AND_GROUPS",

        "certification_mode":
            "EXACT_STRUCTURAL_AND_AUTHORITY_PRESERVATION",

        "layer_count":
            15,

        "group_count":
            4,

        "canonical_layer_order":
            list(
                _REQUIRED_SEMANTIC_LAYER_ORDER
            ),

        "canonical_group_order":
            list(
                _REQUIRED_SEMANTIC_GROUP_ORDER
            ),

        "layer_certification_records":
            layer_certification_records,

        "group_certification_records":
            group_certification_records,

        "all_15_layers_certified":
            True,

        "all_four_groups_certified":
            True,

        "all_layer_payloads_preserved":
            True,

        "all_layer_authorities_preserved":
            True,

        "all_group_payloads_preserved":
            True,

        "all_group_memberships_preserved":
            True,

        "structural_index_alignment_certified":
            True,

        "semantic_state_modified":
            False,

        "semantic_meaning_rewritten":
            False,

        "semantic_merge_performed":
            False,

        "cross_layer_reasoning_performed":
            False,

        "new_reasoning_performed":
            False,
    }

    return {
        "schema_version":
            "semantic_article_profile_layer_group_certification_v1",

        "version":
            SEMANTIC_ARTICLE_PROFILE_CERTIFICATION_VERSION,

        "phase":
            SEMANTIC_ARTICLE_PROFILE_CERTIFICATION_PHASE,

        "patch":
            "4.6.18E",

        "status":
            "SEMANTIC_LAYER_GROUP_PROFILES_CERTIFIED",

        "canonical_article_identity":
            deepcopy(
                identity_certification_result[
                    "canonical_article_identity"
                ]
            ),

        "identity_certification":
            deepcopy(
                identity_certification_result[
                    "identity_certification"
                ]
            ),

        "semantic_layer_group_certification":
            semantic_layer_group_certification,

        "profile_to_certify":
            deepcopy(
                dict(
                    profile
                )
            ),

        "source_semantic_layer_profile":
            deepcopy(
                dict(
                    semantic_layers
                )
            ),

        "source_semantic_group_profile":
            deepcopy(
                dict(
                    semantic_groups
                )
            ),

        "source_identity_certification_result":
            deepcopy(
                dict(
                    identity_certification_result
                )
            ),

        "processing_boundaries": {
            "certified_builder_intake_validation_preserved":
                True,

            "profile_identity_certification_preserved":
                True,

            "semantic_layer_group_certification_performed":
                True,

            "all_15_semantic_layers_certified":
                True,

            "all_four_semantic_groups_certified":
                True,

            "layer_payload_preservation_certified":
                True,

            "layer_authority_preservation_certified":
                True,

            "group_membership_preservation_certified":
                True,

            "layer_group_structural_index_alignment_certified":
                True,

            "cross_layer_artifact_certification_performed":
                False,

            "governed_state_certification_performed":
                False,

            "structural_index_certification_performed":
                False,

            "canonical_profile_integrity_certification_performed":
                False,

            "final_profile_certification_performed":
                False,

            "profile_persistence_performed":
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
            "cross_layer_artifact_certification",
    }


# =====================================================================
# PATCH 4.6.18F ? Cross-Layer Artifact Certification
# =====================================================================

def certify_cross_layer_artifacts_v1(
    layer_group_certification_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Certify the four canonical cross-layer profile artifacts.

    This stage validates exact preservation only.
    No artifact is rebuilt or semantically reinterpreted.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        layer_group_certification_result,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "layer_group_certification_result must be a mapping."
        )

    for field, expected in (
        (
            "schema_version",
            "semantic_article_profile_layer_group_certification_v1",
        ),
        (
            "version",
            "semantic_article_profile_certification_v1",
        ),
        (
            "phase",
            "4.6.18",
        ),
        (
            "patch",
            "4.6.18E",
        ),
        (
            "status",
            "SEMANTIC_LAYER_GROUP_PROFILES_CERTIFIED",
        ),
        (
            "persistence_policy",
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        ),
        (
            "next_stage",
            "cross_layer_artifact_certification",
        ),
    ):

        if layer_group_certification_result.get(field) != expected:
            raise SemanticArticleProfileCertificationError(
                "Invalid 4.6.18E lifecycle field: " + field
            )

    boundaries = layer_group_certification_result.get(
        "processing_boundaries"
    )

    profile = layer_group_certification_result.get(
        "profile_to_certify"
    )

    source_d = layer_group_certification_result.get(
        "source_identity_certification_result"
    )

    if not isinstance(boundaries, Mapping):
        raise SemanticArticleProfileCertificationError(
            "4.6.18E processing boundaries are missing."
        )

    if not isinstance(profile, Mapping):
        raise SemanticArticleProfileCertificationError(
            "Profile to certify is missing."
        )

    if not isinstance(source_d, Mapping):
        raise SemanticArticleProfileCertificationError(
            "Source identity certification result is missing."
        )

    for field in (
        "certified_builder_intake_validation_preserved",
        "profile_identity_certification_preserved",
        "semantic_layer_group_certification_performed",
        "all_15_semantic_layers_certified",
        "all_four_semantic_groups_certified",
        "layer_payload_preservation_certified",
        "layer_authority_preservation_certified",
        "group_membership_preservation_certified",
        "layer_group_structural_index_alignment_certified",
    ):

        if boundaries.get(field) is not True:
            raise SemanticArticleProfileCertificationError(
                "Required 4.6.18E boundary is not True: " + field
            )

    for field in (
        "cross_layer_artifact_certification_performed",
        "governed_state_certification_performed",
        "structural_index_certification_performed",
        "canonical_profile_integrity_certification_performed",
        "final_profile_certification_performed",
        "profile_persistence_performed",
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

        if boundaries.get(field) is not False:
            raise SemanticArticleProfileCertificationError(
                "Forbidden 4.6.18E boundary is not False: " + field
            )

    artifact_profile = profile.get(
        "cross_layer_artifacts"
    )

    if not isinstance(
        artifact_profile,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Cross-layer artifact profile is missing."
        )

    # Recover exact certified builder source.
    source_c = source_d.get(
        "source_intake_result"
    )

    if not isinstance(
        source_c,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Source 4.6.18C intake result is missing."
        )

    source_builder = source_c.get(
        "source_certified_builder_result"
    )

    if not isinstance(
        source_builder,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Certified 4.6.17L builder result is missing."
        )

    source_artifact_profile = source_builder.get(
        "cross_layer_artifact_profile"
    )

    if (
        not isinstance(
            source_artifact_profile,
            Mapping,
        )
        or artifact_profile != source_artifact_profile
    ):
        raise SemanticArticleProfileCertificationError(
            "Cross-layer artifact profile drifted from certified builder."
        )

    if artifact_profile.get(
        "profile_status"
    ) != "CROSS_LAYER_ARTIFACT_PROFILE_ASSEMBLED":
        raise SemanticArticleProfileCertificationError(
            "Cross-layer artifact profile status is invalid."
        )

    if artifact_profile.get(
        "artifact_count"
    ) != 4:
        raise SemanticArticleProfileCertificationError(
            "Cross-layer artifact count must be exactly four."
        )

    if artifact_profile.get(
        "canonical_artifact_order"
    ) != list(
        _REQUIRED_CROSS_LAYER_ARTIFACT_ORDER
    ):
        raise SemanticArticleProfileCertificationError(
            "Canonical cross-layer artifact order drifted."
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
        ) != 4
    ):
        raise SemanticArticleProfileCertificationError(
            "Exactly four cross-layer artifact records are required."
        )

    artifact_certification_records = []
    seen_artifacts = set()

    for ordinal, record in enumerate(
        artifact_records,
        1,
    ):

        if not isinstance(
            record,
            Mapping,
        ):
            raise SemanticArticleProfileCertificationError(
                "Cross-layer artifact record is invalid."
            )

        expected_name = (
            _REQUIRED_CROSS_LAYER_ARTIFACT_ORDER[
                ordinal - 1
            ]
        )

        artifact_name = record.get(
            "artifact_name"
        )

        if artifact_name != expected_name:
            raise SemanticArticleProfileCertificationError(
                "Cross-layer artifact name/order drifted."
            )

        if artifact_name in seen_artifacts:
            raise SemanticArticleProfileCertificationError(
                "Duplicate cross-layer artifact record."
            )

        seen_artifacts.add(
            artifact_name
        )

        if record.get(
            "ordinal"
        ) != ordinal:
            raise SemanticArticleProfileCertificationError(
                "Cross-layer artifact ordinal drifted."
            )

        profile_artifact_id = record.get(
            "profile_artifact_id"
        )

        if (
            not isinstance(
                profile_artifact_id,
                str,
            )
            or not profile_artifact_id
        ):
            raise SemanticArticleProfileCertificationError(
                "Cross-layer profile artifact ID is invalid."
            )

        if record.get(
            "artifact_preserved"
        ) is not True:
            raise SemanticArticleProfileCertificationError(
                "Cross-layer artifact was not preserved."
            )

        if record.get(
            "artifact_recomputed"
        ) is not False:
            raise SemanticArticleProfileCertificationError(
                "Cross-layer artifact was recomputed."
            )

        artifact_certification_records.append(
            {
                "ordinal":
                    ordinal,

                "artifact_name":
                    artifact_name,

                "profile_artifact_id":
                    profile_artifact_id,

                "artifact_certification_status":
                    "CERTIFIED",

                "artifact_preserved":
                    True,

                "artifact_recomputed":
                    False,

                "semantic_state_modified":
                    False,

                "new_reasoning_performed":
                    False,
            }
        )

    # -------------------------------------------------------------
    # Exact four artifact preservation flags
    # -------------------------------------------------------------

    for field in (
        "identity_alignment_preserved",
        "provenance_alignment_preserved",
        "state_indexes_preserved",
        "governed_state_preservation_artifact_preserved",
    ):

        if artifact_profile.get(field) is not True:
            raise SemanticArticleProfileCertificationError(
                "Required artifact preservation field is not True: "
                + field
            )

    for field in (
        "artifact_recomputation_performed",
        "provenance_rebuild_performed",
        "state_index_rebuild_performed",
        "conflict_resolution_performed",
        "uncertainty_reinterpretation_performed",
        "confidence_recalculation_performed",
        "new_reasoning_performed",
    ):

        if artifact_profile.get(field) is not False:
            raise SemanticArticleProfileCertificationError(
                "Forbidden cross-layer artifact state is not False: "
                + field
            )

    # -------------------------------------------------------------
    # Structural-index alignment
    # -------------------------------------------------------------

    structural_indexes = profile.get(
        "structural_indexes"
    )

    if not isinstance(
        structural_indexes,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Structural indexes are missing."
        )

    artifact_name_index = structural_indexes.get(
        "artifact_name_index"
    )

    artifact_ordinal_index = structural_indexes.get(
        "artifact_ordinal_index"
    )

    if (
        not isinstance(
            artifact_name_index,
            Mapping,
        )
        or not isinstance(
            artifact_ordinal_index,
            Mapping,
        )
    ):
        raise SemanticArticleProfileCertificationError(
            "Artifact structural indexes are invalid."
        )

    if structural_indexes.get(
        "artifact_index_count"
    ) != 4:
        raise SemanticArticleProfileCertificationError(
            "Artifact structural-index count drifted."
        )

    for record in artifact_records:

        if artifact_name_index.get(
            record["artifact_name"]
        ) != record[
            "profile_artifact_id"
        ]:
            raise SemanticArticleProfileCertificationError(
                "Artifact name index drifted from artifact profile."
            )

        if artifact_ordinal_index.get(
            str(
                record["ordinal"]
            )
        ) != record[
            "artifact_name"
        ]:
            raise SemanticArticleProfileCertificationError(
                "Artifact ordinal index drifted from artifact profile."
            )

    # -------------------------------------------------------------
    # Certified semantic representation cross-check
    # -------------------------------------------------------------

    representation = profile.get(
        "certified_source_semantic_representation"
    )

    if not isinstance(
        representation,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Certified source semantic representation is missing."
        )

    representation_artifacts = representation.get(
        "cross_layer_artifacts"
    )

    if not isinstance(
        representation_artifacts,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Certified representation cross-layer artifacts are missing."
        )

    source_representation = source_builder.get(
        "canonical_article_semantic_representation"
    )

    if not isinstance(
        source_representation,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Certified builder semantic representation is missing."
        )

    source_representation_artifacts = source_representation.get(
        "cross_layer_artifacts"
    )

    if not isinstance(
        source_representation_artifacts,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Certified builder representation artifacts are missing."
        )

    if (
        representation_artifacts
        != source_representation_artifacts
    ):
        raise SemanticArticleProfileCertificationError(
            "Certified semantic representation artifact set drifted "
            "from the frozen 4.6.17L source."
        )

    if set(
        representation_artifacts.keys()
    ) != set(
        _REQUIRED_CROSS_LAYER_ARTIFACT_ORDER
    ):
        raise SemanticArticleProfileCertificationError(
            "Certified representation artifact names drifted."
        )

    for artifact_name in (
        _REQUIRED_CROSS_LAYER_ARTIFACT_ORDER
    ):

        matching_record = next(
            (
                record
                for record in artifact_records
                if record.get(
                    "artifact_name"
                ) == artifact_name
            ),
            None,
        )

        if not isinstance(
            matching_record,
            Mapping,
        ):
            raise SemanticArticleProfileCertificationError(
                "Required artifact profile record is missing."
            )

        if matching_record.get(
            "artifact_preserved"
        ) is not True:
            raise SemanticArticleProfileCertificationError(
                "Artifact profile preservation drifted: "
                + artifact_name
            )

        if matching_record.get(
            "artifact_recomputed"
        ) is not False:
            raise SemanticArticleProfileCertificationError(
                "Artifact profile was recomputed: "
                + artifact_name
            )

    cross_layer_artifact_certification = {
        "certification_status":
            "CERTIFIED",

        "certification_scope":
            "SEMANTIC_ARTICLE_PROFILE_CROSS_LAYER_ARTIFACTS",

        "certification_mode":
            "EXACT_ARTIFACT_PRESERVATION_CERTIFICATION",

        "artifact_count":
            4,

        "canonical_artifact_order":
            list(
                _REQUIRED_CROSS_LAYER_ARTIFACT_ORDER
            ),

        "artifact_certification_records":
            artifact_certification_records,

        "all_four_artifacts_certified":
            True,

        "identity_alignment_preserved":
            True,

        "provenance_alignment_preserved":
            True,

        "state_indexes_preserved":
            True,

        "governed_state_preservation_artifact_preserved":
            True,

        "structural_index_alignment_certified":
            True,

        "certified_representation_alignment_certified":
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

        "semantic_state_modified":
            False,

        "new_reasoning_performed":
            False,
    }

    return {
        "schema_version":
            "semantic_article_profile_cross_layer_artifact_certification_v1",

        "version":
            SEMANTIC_ARTICLE_PROFILE_CERTIFICATION_VERSION,

        "phase":
            SEMANTIC_ARTICLE_PROFILE_CERTIFICATION_PHASE,

        "patch":
            "4.6.18F",

        "status":
            "CROSS_LAYER_ARTIFACTS_CERTIFIED",

        "canonical_article_identity":
            deepcopy(
                layer_group_certification_result[
                    "canonical_article_identity"
                ]
            ),

        "identity_certification":
            deepcopy(
                layer_group_certification_result[
                    "identity_certification"
                ]
            ),

        "semantic_layer_group_certification":
            deepcopy(
                layer_group_certification_result[
                    "semantic_layer_group_certification"
                ]
            ),

        "cross_layer_artifact_certification":
            cross_layer_artifact_certification,

        "profile_to_certify":
            deepcopy(
                dict(
                    profile
                )
            ),

        "source_cross_layer_artifact_profile":
            deepcopy(
                dict(
                    artifact_profile
                )
            ),

        "source_layer_group_certification_result":
            deepcopy(
                dict(
                    layer_group_certification_result
                )
            ),

        "processing_boundaries": {
            "certified_builder_intake_validation_preserved":
                True,

            "profile_identity_certification_preserved":
                True,

            "semantic_layer_group_certification_preserved":
                True,

            "cross_layer_artifact_certification_performed":
                True,

            "all_four_cross_layer_artifacts_certified":
                True,

            "artifact_preservation_certified":
                True,

            "artifact_structural_index_alignment_certified":
                True,

            "artifact_certified_representation_alignment_certified":
                True,

            "governed_state_certification_performed":
                False,

            "structural_index_certification_performed":
                False,

            "canonical_profile_integrity_certification_performed":
                False,

            "final_profile_certification_performed":
                False,

            "profile_persistence_performed":
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
            "governed_state_certification",
    }


# =====================================================================
# PATCH 4.6.18G ? Governed State Certification
# =====================================================================

def certify_governed_state_profile_v1(
    artifact_certification_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Certify the exact preserved governed state of the Semantic Article
    Profile.

    Governed state includes:
    - governed conflict,
    - uncertainty,
    - confidence classification,
    - unresolved state,
    - abstention state,
    - article-level governed-state flags.

    No state decision is recomputed or changed.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        artifact_certification_result,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "artifact_certification_result must be a mapping."
        )

    for field, expected in (
        (
            "schema_version",
            "semantic_article_profile_cross_layer_artifact_certification_v1",
        ),
        (
            "version",
            "semantic_article_profile_certification_v1",
        ),
        (
            "phase",
            "4.6.18",
        ),
        (
            "patch",
            "4.6.18F",
        ),
        (
            "status",
            "CROSS_LAYER_ARTIFACTS_CERTIFIED",
        ),
        (
            "persistence_policy",
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        ),
        (
            "next_stage",
            "governed_state_certification",
        ),
    ):

        if artifact_certification_result.get(
            field
        ) != expected:
            raise SemanticArticleProfileCertificationError(
                "Invalid 4.6.18F lifecycle field: "
                + field
            )

    boundaries = artifact_certification_result.get(
        "processing_boundaries"
    )

    profile = artifact_certification_result.get(
        "profile_to_certify"
    )

    source_e = artifact_certification_result.get(
        "source_layer_group_certification_result"
    )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "4.6.18F processing boundaries are missing."
        )

    if not isinstance(
        profile,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Profile to certify is missing."
        )

    if not isinstance(
        source_e,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Source 4.6.18E result is missing."
        )

    required_true = (
        "certified_builder_intake_validation_preserved",
        "profile_identity_certification_preserved",
        "semantic_layer_group_certification_preserved",
        "cross_layer_artifact_certification_performed",
        "all_four_cross_layer_artifacts_certified",
        "artifact_preservation_certified",
        "artifact_structural_index_alignment_certified",
        "artifact_certified_representation_alignment_certified",
    )

    for field in required_true:

        if boundaries.get(
            field
        ) is not True:
            raise SemanticArticleProfileCertificationError(
                "Required 4.6.18F boundary is not True: "
                + field
            )

    required_false = (
        "governed_state_certification_performed",
        "structural_index_certification_performed",
        "canonical_profile_integrity_certification_performed",
        "final_profile_certification_performed",
        "profile_persistence_performed",
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

    for field in required_false:

        if boundaries.get(
            field
        ) is not False:
            raise SemanticArticleProfileCertificationError(
                "Forbidden 4.6.18F boundary is not False: "
                + field
            )

    governed_state = profile.get(
        "governed_state"
    )

    if not isinstance(
        governed_state,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Governed-state profile is missing."
        )

    # -------------------------------------------------------------
    # Recover frozen 4.6.17L source
    # -------------------------------------------------------------

    source_d = source_e.get(
        "source_identity_certification_result"
    )

    if not isinstance(
        source_d,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Source 4.6.18D result is missing."
        )

    source_c = source_d.get(
        "source_intake_result"
    )

    if not isinstance(
        source_c,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Source 4.6.18C result is missing."
        )

    source_builder = source_c.get(
        "source_certified_builder_result"
    )

    if not isinstance(
        source_builder,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Certified 4.6.17L builder result is missing."
        )

    source_governed_state = source_builder.get(
        "governed_state_profile"
    )

    if (
        not isinstance(
            source_governed_state,
            Mapping,
        )
        or governed_state != source_governed_state
    ):
        raise SemanticArticleProfileCertificationError(
            "Governed-state profile drifted from certified 4.6.17L source."
        )

    # -------------------------------------------------------------
    # Governed-state authority
    # -------------------------------------------------------------

    if governed_state.get(
        "profile_status"
    ) != "GOVERNED_STATE_PROFILE_ASSEMBLED":
        raise SemanticArticleProfileCertificationError(
            "Governed-state profile status is invalid."
        )

    if governed_state.get(
        "governance_mode"
    ) != "CERTIFIED_STATE_PROJECTION_ONLY":
        raise SemanticArticleProfileCertificationError(
            "Governed-state mode drifted."
        )

    if governed_state.get(
        "uncertainty_authority"
    ) != "CERTIFIED_4.6.14_UNCERTAINTY_INTELLIGENCE_VIA_4.6.16P":
        raise SemanticArticleProfileCertificationError(
            "Uncertainty authority drifted."
        )

    if governed_state.get(
        "hybrid_governance_authority"
    ) != "FROZEN_4.6.15S_HYBRID_STATE_VIA_4.6.16P":
        raise SemanticArticleProfileCertificationError(
            "Hybrid-governance authority drifted."
        )

    if governed_state.get(
        "preservation_authority"
    ) != "4.6.16P_CERTIFIED_GOVERNED_STATE_PRESERVATION":
        raise SemanticArticleProfileCertificationError(
            "Governed-state preservation authority drifted."
        )

    # -------------------------------------------------------------
    # Exact governed IDs
    # -------------------------------------------------------------

    governed_conflict_ids = governed_state.get(
        "governed_conflict_candidate_ids"
    )

    unresolved_ids = governed_state.get(
        "unresolved_candidate_ids"
    )

    abstention_ids = governed_state.get(
        "abstention_candidate_ids"
    )

    confidence_class_index = governed_state.get(
        "confidence_class_index"
    )

    for name, value in (
        (
            "governed_conflict_candidate_ids",
            governed_conflict_ids,
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

        if not isinstance(
            value,
            list,
        ):
            raise SemanticArticleProfileCertificationError(
                name + " must be a list."
            )

        if len(
            value
        ) != len(
            set(
                value
            )
        ):
            raise SemanticArticleProfileCertificationError(
                name + " contains duplicate candidate IDs."
            )

    if unresolved_ids != abstention_ids:
        raise SemanticArticleProfileCertificationError(
            "Unresolved candidate IDs must exactly equal abstention IDs."
        )

    if not isinstance(
        confidence_class_index,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Confidence-class index is invalid."
        )

    expected_confidence_classes = (
        "AGREEMENT",
        "SYMBOLICALLY_GOVERNED_CONFLICT",
        "UNRESOLVED",
    )

    if tuple(
        confidence_class_index.keys()
    ) != expected_confidence_classes:
        raise SemanticArticleProfileCertificationError(
            "Confidence-class index order/classes drifted."
        )

    if confidence_class_index.get(
        "SYMBOLICALLY_GOVERNED_CONFLICT"
    ) != governed_conflict_ids:
        raise SemanticArticleProfileCertificationError(
            "Governed-conflict IDs drifted from confidence index."
        )

    if confidence_class_index.get(
        "UNRESOLVED"
    ) != unresolved_ids:
        raise SemanticArticleProfileCertificationError(
            "Unresolved IDs drifted from confidence index."
        )

    # No candidate may be both agreement and governed conflict/unresolved.
    agreement_ids = confidence_class_index.get(
        "AGREEMENT"
    )

    if not isinstance(
        agreement_ids,
        list,
    ):
        raise SemanticArticleProfileCertificationError(
            "Agreement confidence class is invalid."
        )

    agreement_set = set(
        agreement_ids
    )

    governed_set = set(
        governed_conflict_ids
    )

    unresolved_set = set(
        unresolved_ids
    )

    if (
        agreement_set & governed_set
        or agreement_set & unresolved_set
        or governed_set & unresolved_set
    ):
        raise SemanticArticleProfileCertificationError(
            "Confidence classes overlap."
        )

    # -------------------------------------------------------------
    # Article-level governed flags
    # -------------------------------------------------------------

    for field in (
        "article_has_symbolically_governed_conflict",
        "article_has_unresolved_hybrid_evidence",
        "article_requires_hybrid_abstention",
    ):

        if not isinstance(
            governed_state.get(
                field
            ),
            bool,
        ):
            raise SemanticArticleProfileCertificationError(
                "Governed article flag is invalid: "
                + field
            )

    if governed_state.get(
        "article_has_symbolically_governed_conflict"
    ) != bool(
        governed_conflict_ids
    ):
        raise SemanticArticleProfileCertificationError(
            "Article governed-conflict flag drifted."
        )

    if governed_state.get(
        "article_has_unresolved_hybrid_evidence"
    ) != bool(
        unresolved_ids
    ):
        raise SemanticArticleProfileCertificationError(
            "Article unresolved-state flag drifted."
        )

    if governed_state.get(
        "article_requires_hybrid_abstention"
    ) != bool(
        abstention_ids
    ):
        raise SemanticArticleProfileCertificationError(
            "Article abstention flag drifted."
        )

    # -------------------------------------------------------------
    # Preservation guarantees
    # -------------------------------------------------------------

    for field in (
        "conflict_state_preserved",
        "uncertainty_state_preserved",
        "confidence_state_preserved",
        "unresolved_state_preserved",
        "abstention_state_preserved",
    ):

        if governed_state.get(
            field
        ) is not True:
            raise SemanticArticleProfileCertificationError(
                "Required governed-state preservation flag is not True: "
                + field
            )

    for field in (
        "semantic_state_modified",
        "conflict_resolution_performed",
        "contradiction_adjudication_performed",
        "uncertainty_reinterpretation_performed",
        "uncertainty_strengthening_performed",
        "confidence_recalculation_performed",
        "unified_semantic_confidence_calculated",
        "abstention_decision_created",
        "abstention_decision_removed",
        "new_reasoning_performed",
    ):

        if (
            field in governed_state
            and governed_state[
                field
            ] is not False
        ):
            raise SemanticArticleProfileCertificationError(
                "Forbidden governed-state operation detected: "
                + field
            )

    # -------------------------------------------------------------
    # Cross-check governed artifact
    # -------------------------------------------------------------

    artifact_profile = profile.get(
        "cross_layer_artifacts"
    )

    if not isinstance(
        artifact_profile,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Cross-layer artifact profile is missing."
        )

    artifact_records = artifact_profile.get(
        "artifact_records"
    )

    if not isinstance(
        artifact_records,
        list,
    ):
        raise SemanticArticleProfileCertificationError(
            "Cross-layer artifact records are missing."
        )

    governed_artifact_record = next(
        (
            record
            for record in artifact_records
            if isinstance(
                record,
                Mapping,
            )
            and record.get(
                "artifact_name"
            )
            == "conflict_uncertainty_abstention_preservation"
        ),
        None,
    )

    if not isinstance(
        governed_artifact_record,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Governed-state preservation artifact is missing."
        )

    if governed_artifact_record.get(
        "artifact_preserved"
    ) is not True:
        raise SemanticArticleProfileCertificationError(
            "Governed-state preservation artifact was not preserved."
        )

    if governed_artifact_record.get(
        "artifact_recomputed"
    ) is not False:
        raise SemanticArticleProfileCertificationError(
            "Governed-state preservation artifact was recomputed."
        )

    # -------------------------------------------------------------
    # Structural governed-state index alignment
    # -------------------------------------------------------------

    structural_indexes = profile.get(
        "structural_indexes"
    )

    if not isinstance(
        structural_indexes,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Structural indexes are missing."
        )

    governed_state_index = structural_indexes.get(
        "governed_state_index"
    )

    if not isinstance(
        governed_state_index,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Governed-state structural index is missing."
        )

    expected_governed_state_index = {
        "governed_conflict_candidate_ids":
            governed_conflict_ids,

        "unresolved_candidate_ids":
            unresolved_ids,

        "abstention_candidate_ids":
            abstention_ids,

        "confidence_class_index":
            confidence_class_index,

        "article_has_symbolically_governed_conflict":
            governed_state[
                "article_has_symbolically_governed_conflict"
            ],

        "article_has_unresolved_hybrid_evidence":
            governed_state[
                "article_has_unresolved_hybrid_evidence"
            ],

        "article_requires_hybrid_abstention":
            governed_state[
                "article_requires_hybrid_abstention"
            ],
    }

    if governed_state_index != expected_governed_state_index:
        raise SemanticArticleProfileCertificationError(
            "Governed-state structural index drifted."
        )

    governed_state_certification = {
        "certification_status":
            "CERTIFIED",

        "certification_scope":
            "SEMANTIC_ARTICLE_PROFILE_GOVERNED_STATE",

        "certification_mode":
            "EXACT_GOVERNED_STATE_PRESERVATION_CERTIFICATION",

        "governance_mode":
            "CERTIFIED_STATE_PROJECTION_ONLY",

        "uncertainty_authority":
            governed_state[
                "uncertainty_authority"
            ],

        "hybrid_governance_authority":
            governed_state[
                "hybrid_governance_authority"
            ],

        "preservation_authority":
            governed_state[
                "preservation_authority"
            ],

        "governed_conflict_candidate_ids":
            deepcopy(
                governed_conflict_ids
            ),

        "unresolved_candidate_ids":
            deepcopy(
                unresolved_ids
            ),

        "abstention_candidate_ids":
            deepcopy(
                abstention_ids
            ),

        "confidence_class_index":
            deepcopy(
                dict(
                    confidence_class_index
                )
            ),

        "article_has_symbolically_governed_conflict":
            governed_state[
                "article_has_symbolically_governed_conflict"
            ],

        "article_has_unresolved_hybrid_evidence":
            governed_state[
                "article_has_unresolved_hybrid_evidence"
            ],

        "article_requires_hybrid_abstention":
            governed_state[
                "article_requires_hybrid_abstention"
            ],

        "conflict_state_certified":
            True,

        "uncertainty_state_certified":
            True,

        "confidence_state_certified":
            True,

        "unresolved_state_certified":
            True,

        "abstention_state_certified":
            True,

        "governed_artifact_alignment_certified":
            True,

        "governed_structural_index_alignment_certified":
            True,

        "semantic_state_modified":
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
    }

    return {
        "schema_version":
            "semantic_article_profile_governed_state_certification_v1",

        "version":
            SEMANTIC_ARTICLE_PROFILE_CERTIFICATION_VERSION,

        "phase":
            SEMANTIC_ARTICLE_PROFILE_CERTIFICATION_PHASE,

        "patch":
            "4.6.18G",

        "status":
            "GOVERNED_STATE_CERTIFIED",

        "canonical_article_identity":
            deepcopy(
                artifact_certification_result[
                    "canonical_article_identity"
                ]
            ),

        "identity_certification":
            deepcopy(
                artifact_certification_result[
                    "identity_certification"
                ]
            ),

        "semantic_layer_group_certification":
            deepcopy(
                artifact_certification_result[
                    "semantic_layer_group_certification"
                ]
            ),

        "cross_layer_artifact_certification":
            deepcopy(
                artifact_certification_result[
                    "cross_layer_artifact_certification"
                ]
            ),

        "governed_state_certification":
            governed_state_certification,

        "profile_to_certify":
            deepcopy(
                dict(
                    profile
                )
            ),

        "source_governed_state_profile":
            deepcopy(
                dict(
                    governed_state
                )
            ),

        "source_artifact_certification_result":
            deepcopy(
                dict(
                    artifact_certification_result
                )
            ),

        "processing_boundaries": {
            "certified_builder_intake_validation_preserved":
                True,

            "profile_identity_certification_preserved":
                True,

            "semantic_layer_group_certification_preserved":
                True,

            "cross_layer_artifact_certification_preserved":
                True,

            "governed_state_certification_performed":
                True,

            "conflict_state_certified":
                True,

            "uncertainty_state_certified":
                True,

            "confidence_state_certified":
                True,

            "unresolved_state_certified":
                True,

            "abstention_state_certified":
                True,

            "governed_state_artifact_alignment_certified":
                True,

            "governed_state_structural_index_alignment_certified":
                True,

            "structural_index_certification_performed":
                False,

            "canonical_profile_integrity_certification_performed":
                False,

            "final_profile_certification_performed":
                False,

            "profile_persistence_performed":
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
            "structural_index_certification",
    }


# =====================================================================
# PATCH 4.6.18H ? Structural Index Certification
# =====================================================================

def certify_profile_structural_indexes_v1(
    governed_state_certification_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Certify the deterministic navigation/index structure produced by 4.6.17I.

    No upstream semantic index is rebuilt.
    No semantic classification/count is recalculated.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        governed_state_certification_result,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "governed_state_certification_result must be a mapping."
        )

    for field, expected in (
        (
            "schema_version",
            "semantic_article_profile_governed_state_certification_v1",
        ),
        (
            "version",
            "semantic_article_profile_certification_v1",
        ),
        (
            "phase",
            "4.6.18",
        ),
        (
            "patch",
            "4.6.18G",
        ),
        (
            "status",
            "GOVERNED_STATE_CERTIFIED",
        ),
        (
            "persistence_policy",
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        ),
        (
            "next_stage",
            "structural_index_certification",
        ),
    ):

        if governed_state_certification_result.get(
            field
        ) != expected:
            raise SemanticArticleProfileCertificationError(
                "Invalid 4.6.18G lifecycle field: "
                + field
            )

    boundaries = governed_state_certification_result.get(
        "processing_boundaries"
    )

    profile = governed_state_certification_result.get(
        "profile_to_certify"
    )

    source_f = governed_state_certification_result.get(
        "source_artifact_certification_result"
    )

    if not isinstance(boundaries, Mapping):
        raise SemanticArticleProfileCertificationError(
            "4.6.18G processing boundaries are missing."
        )

    if not isinstance(profile, Mapping):
        raise SemanticArticleProfileCertificationError(
            "Profile to certify is missing."
        )

    if not isinstance(source_f, Mapping):
        raise SemanticArticleProfileCertificationError(
            "Source 4.6.18F result is missing."
        )

    for field in (
        "certified_builder_intake_validation_preserved",
        "profile_identity_certification_preserved",
        "semantic_layer_group_certification_preserved",
        "cross_layer_artifact_certification_preserved",
        "governed_state_certification_performed",
        "conflict_state_certified",
        "uncertainty_state_certified",
        "confidence_state_certified",
        "unresolved_state_certified",
        "abstention_state_certified",
        "governed_state_artifact_alignment_certified",
        "governed_state_structural_index_alignment_certified",
    ):

        if boundaries.get(field) is not True:
            raise SemanticArticleProfileCertificationError(
                "Required 4.6.18G boundary is not True: "
                + field
            )

    for field in (
        "structural_index_certification_performed",
        "canonical_profile_integrity_certification_performed",
        "final_profile_certification_performed",
        "profile_persistence_performed",
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

        if boundaries.get(field) is not False:
            raise SemanticArticleProfileCertificationError(
                "Forbidden 4.6.18G boundary is not False: "
                + field
            )

    indexes = profile.get(
        "structural_indexes"
    )

    if not isinstance(indexes, Mapping):
        raise SemanticArticleProfileCertificationError(
            "Structural indexes are missing."
        )

    # -------------------------------------------------------------
    # Recover frozen 4.6.17L source
    # -------------------------------------------------------------

    source_e = source_f.get(
        "source_layer_group_certification_result"
    )

    if not isinstance(source_e, Mapping):
        raise SemanticArticleProfileCertificationError(
            "Source 4.6.18E result is missing."
        )

    source_d = source_e.get(
        "source_identity_certification_result"
    )

    if not isinstance(source_d, Mapping):
        raise SemanticArticleProfileCertificationError(
            "Source 4.6.18D result is missing."
        )

    source_c = source_d.get(
        "source_intake_result"
    )

    if not isinstance(source_c, Mapping):
        raise SemanticArticleProfileCertificationError(
            "Source 4.6.18C result is missing."
        )

    source_builder = source_c.get(
        "source_certified_builder_result"
    )

    if not isinstance(source_builder, Mapping):
        raise SemanticArticleProfileCertificationError(
            "Certified 4.6.17L builder result is missing."
        )

    source_indexes = source_builder.get(
        "structural_indexes"
    )

    if (
        not isinstance(source_indexes, Mapping)
        or indexes != source_indexes
    ):
        raise SemanticArticleProfileCertificationError(
            "Structural indexes drifted from certified 4.6.17L source."
        )

    # -------------------------------------------------------------
    # Core index contract
    # -------------------------------------------------------------

    if indexes.get(
        "index_status"
    ) != "PROFILE_STRUCTURAL_INDEXES_CONSTRUCTED":
        raise SemanticArticleProfileCertificationError(
            "Structural-index status is invalid."
        )

    if indexes.get(
        "index_mode"
    ) != "DETERMINISTIC_PROFILE_NAVIGATION_ONLY":
        raise SemanticArticleProfileCertificationError(
            "Structural-index mode drifted."
        )

    if (
        indexes.get("layer_index_count") != 15
        or indexes.get("group_index_count") != 4
        or indexes.get("artifact_index_count") != 4
    ):
        raise SemanticArticleProfileCertificationError(
            "Structural-index counts drifted."
        )

    if indexes.get(
        "profile_navigation_indexes_only"
    ) is not True:
        raise SemanticArticleProfileCertificationError(
            "Structural indexes are not navigation-only."
        )

    if indexes.get(
        "upstream_semantic_indexes_preserved"
    ) is not True:
        raise SemanticArticleProfileCertificationError(
            "Upstream semantic indexes were not preserved."
        )

    if indexes.get(
        "upstream_index_rebuild_performed"
    ) is not False:
        raise SemanticArticleProfileCertificationError(
            "Upstream index rebuild was performed."
        )

    # -------------------------------------------------------------
    # Required index maps
    # -------------------------------------------------------------

    required_mapping_fields = (
        "layer_name_index",
        "layer_phase_index",
        "layer_group_index",
        "layer_ordinal_index",
        "group_name_index",
        "group_ordinal_index",
        "group_membership_index",
        "artifact_name_index",
        "artifact_ordinal_index",
        "governed_state_index",
    )

    for field in required_mapping_fields:

        if not isinstance(
            indexes.get(field),
            Mapping,
        ):
            raise SemanticArticleProfileCertificationError(
                "Structural index is missing/invalid: "
                + field
            )

    layer_records = profile.get(
        "semantic_layers",
        {}
    ).get(
        "layer_records"
    )

    group_records = profile.get(
        "semantic_groups",
        {}
    ).get(
        "group_records"
    )

    artifact_records = profile.get(
        "cross_layer_artifacts",
        {}
    ).get(
        "artifact_records"
    )

    if (
        not isinstance(layer_records, list)
        or len(layer_records) != 15
    ):
        raise SemanticArticleProfileCertificationError(
            "Semantic-layer records are invalid."
        )

    if (
        not isinstance(group_records, list)
        or len(group_records) != 4
    ):
        raise SemanticArticleProfileCertificationError(
            "Semantic-group records are invalid."
        )

    if (
        not isinstance(artifact_records, list)
        or len(artifact_records) != 4
    ):
        raise SemanticArticleProfileCertificationError(
            "Cross-layer artifact records are invalid."
        )

    # -------------------------------------------------------------
    # Layer indexes
    # -------------------------------------------------------------

    for ordinal, record in enumerate(
        layer_records,
        1,
    ):

        layer_name = record.get(
            "layer_name"
        )

        layer_id = record.get(
            "profile_layer_id"
        )

        if indexes[
            "layer_name_index"
        ].get(
            layer_name
        ) != layer_id:
            raise SemanticArticleProfileCertificationError(
                "Layer-name index drifted."
            )

        if indexes[
            "layer_group_index"
        ].get(
            layer_name
        ) != record.get(
            "semantic_group"
        ):
            raise SemanticArticleProfileCertificationError(
                "Layer-group index drifted."
            )

        ordinal_index = indexes[
            "layer_ordinal_index"
        ]

        ordinal_value = (
            ordinal_index.get(
                str(ordinal)
            )
            if str(ordinal) in ordinal_index
            else ordinal_index.get(
                ordinal
            )
        )

        if ordinal_value != layer_name:
            raise SemanticArticleProfileCertificationError(
                "Layer-ordinal index drifted."
            )

        phase_value = indexes[
            "layer_phase_index"
        ].get(
            layer_name
        )

        expected_phase = record.get(
            "source_phase"
        )

        if (
            expected_phase is not None
            and phase_value != expected_phase
        ):
            raise SemanticArticleProfileCertificationError(
                "Layer-phase index drifted."
            )

    # -------------------------------------------------------------
    # Group indexes
    # -------------------------------------------------------------

    for ordinal, record in enumerate(
        group_records,
        1,
    ):

        group_name = record.get(
            "group_name"
        )

        group_id = record.get(
            "profile_group_id"
        )

        if indexes[
            "group_name_index"
        ].get(
            group_name
        ) != group_id:
            raise SemanticArticleProfileCertificationError(
                "Group-name index drifted."
            )

        ordinal_index = indexes[
            "group_ordinal_index"
        ]

        ordinal_value = (
            ordinal_index.get(
                str(ordinal)
            )
            if str(ordinal) in ordinal_index
            else ordinal_index.get(
                ordinal
            )
        )

        if ordinal_value != group_name:
            raise SemanticArticleProfileCertificationError(
                "Group-ordinal index drifted."
            )

        if indexes[
            "group_membership_index"
        ].get(
            group_name
        ) != record.get(
            "member_layer_order"
        ):
            raise SemanticArticleProfileCertificationError(
                "Group-membership index drifted."
            )

    # -------------------------------------------------------------
    # Artifact indexes
    # -------------------------------------------------------------

    for ordinal, record in enumerate(
        artifact_records,
        1,
    ):

        artifact_name = record.get(
            "artifact_name"
        )

        artifact_id = record.get(
            "profile_artifact_id"
        )

        if indexes[
            "artifact_name_index"
        ].get(
            artifact_name
        ) != artifact_id:
            raise SemanticArticleProfileCertificationError(
                "Artifact-name index drifted."
            )

        ordinal_index = indexes[
            "artifact_ordinal_index"
        ]

        ordinal_value = (
            ordinal_index.get(
                str(ordinal)
            )
            if str(ordinal) in ordinal_index
            else ordinal_index.get(
                ordinal
            )
        )

        if ordinal_value != artifact_name:
            raise SemanticArticleProfileCertificationError(
                "Artifact-ordinal index drifted."
            )

    # -------------------------------------------------------------
    # Governed-state index alignment
    # -------------------------------------------------------------

    governed = profile.get(
        "governed_state"
    )

    if not isinstance(
        governed,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Governed-state profile is missing."
        )

    expected_governed_index = {
        "governed_conflict_candidate_ids":
            governed[
                "governed_conflict_candidate_ids"
            ],

        "unresolved_candidate_ids":
            governed[
                "unresolved_candidate_ids"
            ],

        "abstention_candidate_ids":
            governed[
                "abstention_candidate_ids"
            ],

        "confidence_class_index":
            governed[
                "confidence_class_index"
            ],

        "article_has_symbolically_governed_conflict":
            governed[
                "article_has_symbolically_governed_conflict"
            ],

        "article_has_unresolved_hybrid_evidence":
            governed[
                "article_has_unresolved_hybrid_evidence"
            ],

        "article_requires_hybrid_abstention":
            governed[
                "article_requires_hybrid_abstention"
            ],
    }

    if indexes[
        "governed_state_index"
    ] != expected_governed_index:
        raise SemanticArticleProfileCertificationError(
            "Governed-state index drifted."
        )

    structural_index_certification = {
        "certification_status":
            "CERTIFIED",

        "certification_scope":
            "SEMANTIC_ARTICLE_PROFILE_STRUCTURAL_INDEXES",

        "certification_mode":
            "DETERMINISTIC_NAVIGATION_INDEX_PRESERVATION_CERTIFICATION",

        "index_mode":
            "DETERMINISTIC_PROFILE_NAVIGATION_ONLY",

        "layer_index_count":
            15,

        "group_index_count":
            4,

        "artifact_index_count":
            4,

        "layer_name_index_certified":
            True,

        "layer_phase_index_certified":
            True,

        "layer_group_index_certified":
            True,

        "layer_ordinal_index_certified":
            True,

        "group_name_index_certified":
            True,

        "group_ordinal_index_certified":
            True,

        "group_membership_index_certified":
            True,

        "artifact_name_index_certified":
            True,

        "artifact_ordinal_index_certified":
            True,

        "governed_state_index_certified":
            True,

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

        "semantic_state_modified":
            False,

        "new_reasoning_performed":
            False,
    }

    return {
        "schema_version":
            "semantic_article_profile_structural_index_certification_v1",

        "version":
            SEMANTIC_ARTICLE_PROFILE_CERTIFICATION_VERSION,

        "phase":
            SEMANTIC_ARTICLE_PROFILE_CERTIFICATION_PHASE,

        "patch":
            "4.6.18H",

        "status":
            "PROFILE_STRUCTURAL_INDEXES_CERTIFIED",

        "canonical_article_identity":
            deepcopy(
                governed_state_certification_result[
                    "canonical_article_identity"
                ]
            ),

        "identity_certification":
            deepcopy(
                governed_state_certification_result[
                    "identity_certification"
                ]
            ),

        "semantic_layer_group_certification":
            deepcopy(
                governed_state_certification_result[
                    "semantic_layer_group_certification"
                ]
            ),

        "cross_layer_artifact_certification":
            deepcopy(
                governed_state_certification_result[
                    "cross_layer_artifact_certification"
                ]
            ),

        "governed_state_certification":
            deepcopy(
                governed_state_certification_result[
                    "governed_state_certification"
                ]
            ),

        "structural_index_certification":
            structural_index_certification,

        "profile_to_certify":
            deepcopy(
                dict(
                    profile
                )
            ),

        "source_structural_indexes":
            deepcopy(
                dict(
                    indexes
                )
            ),

        "source_governed_state_certification_result":
            deepcopy(
                dict(
                    governed_state_certification_result
                )
            ),

        "processing_boundaries": {
            "certified_builder_intake_validation_preserved":
                True,

            "profile_identity_certification_preserved":
                True,

            "semantic_layer_group_certification_preserved":
                True,

            "cross_layer_artifact_certification_preserved":
                True,

            "governed_state_certification_preserved":
                True,

            "structural_index_certification_performed":
                True,

            "layer_indexes_certified":
                True,

            "group_indexes_certified":
                True,

            "artifact_indexes_certified":
                True,

            "governed_state_index_certified":
                True,

            "profile_navigation_only_index_contract_certified":
                True,

            "canonical_profile_integrity_certification_performed":
                False,

            "final_profile_certification_performed":
                False,

            "profile_persistence_performed":
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
            "canonical_profile_integrity_certification",
    }


# =====================================================================
# PATCH 4.6.18I ? Canonical Profile Integrity Certification
# =====================================================================

def certify_canonical_semantic_article_profile_integrity_v1(
    structural_index_certification_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Certify the complete canonical Semantic Article Profile as an exact
    preserved structural representation of the certified 4.6.17 source.

    I certifies canonical-profile integrity.

    I does NOT yet produce the final certified-profile result envelope.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        structural_index_certification_result,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "structural_index_certification_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.18H lifecycle contract
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "semantic_article_profile_structural_index_certification_v1",
        ),
        (
            "version",
            "semantic_article_profile_certification_v1",
        ),
        (
            "phase",
            "4.6.18",
        ),
        (
            "patch",
            "4.6.18H",
        ),
        (
            "status",
            "PROFILE_STRUCTURAL_INDEXES_CERTIFIED",
        ),
        (
            "persistence_policy",
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        ),
        (
            "next_stage",
            "canonical_profile_integrity_certification",
        ),
    ):

        if structural_index_certification_result.get(
            field
        ) != expected:
            raise SemanticArticleProfileCertificationError(
                "Invalid 4.6.18H lifecycle field: "
                + field
            )

    boundaries = structural_index_certification_result.get(
        "processing_boundaries"
    )

    profile = structural_index_certification_result.get(
        "profile_to_certify"
    )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "4.6.18H processing boundaries are missing."
        )

    if not isinstance(
        profile,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Canonical profile to certify is missing."
        )

    # -------------------------------------------------------------
    # H authority
    # -------------------------------------------------------------

    required_h_true = (
        "certified_builder_intake_validation_preserved",
        "profile_identity_certification_preserved",
        "semantic_layer_group_certification_preserved",
        "cross_layer_artifact_certification_preserved",
        "governed_state_certification_preserved",
        "structural_index_certification_performed",
        "layer_indexes_certified",
        "group_indexes_certified",
        "artifact_indexes_certified",
        "governed_state_index_certified",
        "profile_navigation_only_index_contract_certified",
    )

    for field in required_h_true:

        if boundaries.get(
            field
        ) is not True:
            raise SemanticArticleProfileCertificationError(
                "Required 4.6.18H boundary is not True: "
                + field
            )

    required_h_false = (
        "canonical_profile_integrity_certification_performed",
        "final_profile_certification_performed",
        "profile_persistence_performed",
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

    for field in required_h_false:

        if boundaries.get(
            field
        ) is not False:
            raise SemanticArticleProfileCertificationError(
                "Forbidden 4.6.18H boundary is not False: "
                + field
            )

    # -------------------------------------------------------------
    # Recover complete certification chain
    # -------------------------------------------------------------

    identity_certification = structural_index_certification_result.get(
        "identity_certification"
    )

    layer_group_certification = structural_index_certification_result.get(
        "semantic_layer_group_certification"
    )

    artifact_certification = structural_index_certification_result.get(
        "cross_layer_artifact_certification"
    )

    governed_state_certification = structural_index_certification_result.get(
        "governed_state_certification"
    )

    structural_index_certification = structural_index_certification_result.get(
        "structural_index_certification"
    )

    for name, value in (
        (
            "identity_certification",
            identity_certification,
        ),
        (
            "semantic_layer_group_certification",
            layer_group_certification,
        ),
        (
            "cross_layer_artifact_certification",
            artifact_certification,
        ),
        (
            "governed_state_certification",
            governed_state_certification,
        ),
        (
            "structural_index_certification",
            structural_index_certification,
        ),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise SemanticArticleProfileCertificationError(
                name + " is missing."
            )

        if value.get(
            "certification_status"
        ) != "CERTIFIED":
            raise SemanticArticleProfileCertificationError(
                name + " is not certified."
            )

    # -------------------------------------------------------------
    # Recover frozen 4.6.17L builder source
    # H -> G -> F -> E -> D -> C -> 4.6.17L
    # -------------------------------------------------------------

    source_g = structural_index_certification_result.get(
        "source_governed_state_certification_result"
    )

    if not isinstance(
        source_g,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Source 4.6.18G result is missing."
        )

    source_f = source_g.get(
        "source_artifact_certification_result"
    )

    if not isinstance(
        source_f,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Source 4.6.18F result is missing."
        )

    source_e = source_f.get(
        "source_layer_group_certification_result"
    )

    if not isinstance(
        source_e,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Source 4.6.18E result is missing."
        )

    source_d = source_e.get(
        "source_identity_certification_result"
    )

    if not isinstance(
        source_d,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Source 4.6.18D result is missing."
        )

    source_c = source_d.get(
        "source_intake_result"
    )

    if not isinstance(
        source_c,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Source 4.6.18C result is missing."
        )

    source_builder = source_c.get(
        "source_certified_builder_result"
    )

    if not isinstance(
        source_builder,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Certified 4.6.17L builder result is missing."
        )

    source_profile = source_builder.get(
        "final_semantic_article_profile"
    )

    if not isinstance(
        source_profile,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Frozen 4.6.17L canonical profile is missing."
        )

    if profile != source_profile:
        raise SemanticArticleProfileCertificationError(
            "Canonical profile drifted from frozen 4.6.17L profile."
        )

    # -------------------------------------------------------------
    # Canonical profile core contract
    # -------------------------------------------------------------

    for field, expected in (
        (
            "profile_schema_version",
            "canonical_semantic_article_profile_v1",
        ),
        (
            "profile_status",
            "CANONICAL_SEMANTIC_ARTICLE_PROFILE_ASSEMBLED",
        ),
        (
            "profile_builder_phase",
            "4.6.17",
        ),
        (
            "profile_builder_patch",
            "4.6.17J",
        ),
        (
            "profile_mode",
            "CERTIFIED_SOURCE_STRUCTURAL_PROFILE",
        ),
    ):

        if profile.get(
            field
        ) != expected:
            raise SemanticArticleProfileCertificationError(
                "Canonical profile field drifted: "
                + field
            )

    if profile.get(
        "profile_section_order"
    ) != list(
        _REQUIRED_PROFILE_SECTION_ORDER
    ):
        raise SemanticArticleProfileCertificationError(
            "Canonical profile section order drifted."
        )

    if profile.get(
        "profile_section_count"
    ) != 8:
        raise SemanticArticleProfileCertificationError(
            "Canonical profile section count must be 8."
        )

    if profile.get(
        "source_layer_count"
    ) != 15:
        raise SemanticArticleProfileCertificationError(
            "Canonical profile source-layer count must be 15."
        )

    if profile.get(
        "source_group_count"
    ) != 4:
        raise SemanticArticleProfileCertificationError(
            "Canonical profile source-group count must be 4."
        )

    if profile.get(
        "cross_layer_artifact_count"
    ) != 4:
        raise SemanticArticleProfileCertificationError(
            "Canonical profile artifact count must be 4."
        )

    # Profile enters I still not finally certified.
    if profile.get(
        "profile_certification_ready"
    ) is not True:
        raise SemanticArticleProfileCertificationError(
            "Canonical profile is not certification-ready."
        )

    if profile.get(
        "profile_certified"
    ) is not False:
        raise SemanticArticleProfileCertificationError(
            "Canonical source profile must remain uncertified before J."
        )

    if profile.get(
        "profile_persisted"
    ) is not False:
        raise SemanticArticleProfileCertificationError(
            "Canonical source profile must remain unpersisted."
        )

    # -------------------------------------------------------------
    # Exact eight-section integrity
    # -------------------------------------------------------------

    for section_name in (
        _REQUIRED_PROFILE_SECTION_ORDER
    ):

        if section_name not in profile:
            raise SemanticArticleProfileCertificationError(
                "Canonical profile section is missing: "
                + section_name
            )

    if profile.get(
        "profile_identity"
    ) != source_builder.get(
        "profile_identity"
    ):
        raise SemanticArticleProfileCertificationError(
            "Profile identity section drifted."
        )

    if profile.get(
        "source_authority"
    ) != source_builder.get(
        "source_authority_profile"
    ):
        raise SemanticArticleProfileCertificationError(
            "Source-authority section drifted."
        )

    if profile.get(
        "semantic_layers"
    ) != source_builder.get(
        "semantic_layer_profile"
    ):
        raise SemanticArticleProfileCertificationError(
            "Semantic-layer section drifted."
        )

    if profile.get(
        "semantic_groups"
    ) != source_builder.get(
        "semantic_group_profile"
    ):
        raise SemanticArticleProfileCertificationError(
            "Semantic-group section drifted."
        )

    if profile.get(
        "cross_layer_artifacts"
    ) != source_builder.get(
        "cross_layer_artifact_profile"
    ):
        raise SemanticArticleProfileCertificationError(
            "Cross-layer artifact section drifted."
        )

    if profile.get(
        "governed_state"
    ) != source_builder.get(
        "governed_state_profile"
    ):
        raise SemanticArticleProfileCertificationError(
            "Governed-state section drifted."
        )

    if profile.get(
        "structural_indexes"
    ) != source_builder.get(
        "structural_indexes"
    ):
        raise SemanticArticleProfileCertificationError(
            "Structural-index section drifted."
        )

    if profile.get(
        "certified_source_semantic_representation"
    ) != source_builder.get(
        "canonical_article_semantic_representation"
    ):
        raise SemanticArticleProfileCertificationError(
            "Certified source semantic representation drifted."
        )

    # -------------------------------------------------------------
    # Cross-certification alignment
    # -------------------------------------------------------------

    canonical_identity = structural_index_certification_result.get(
        "canonical_article_identity"
    )

    if (
        not isinstance(
            canonical_identity,
            Mapping,
        )
        or profile[
            "profile_identity"
        ].get(
            "canonical_article_identity"
        )
        != canonical_identity
    ):
        raise SemanticArticleProfileCertificationError(
            "Canonical identity alignment failed."
        )

    if identity_certification.get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise SemanticArticleProfileCertificationError(
            "Identity certification disagrees with canonical identity."
        )

    if layer_group_certification.get(
        "layer_count"
    ) != 15:
        raise SemanticArticleProfileCertificationError(
            "Layer certification count drifted."
        )

    if layer_group_certification.get(
        "group_count"
    ) != 4:
        raise SemanticArticleProfileCertificationError(
            "Group certification count drifted."
        )

    if artifact_certification.get(
        "artifact_count"
    ) != 4:
        raise SemanticArticleProfileCertificationError(
            "Artifact certification count drifted."
        )

    if governed_state_certification.get(
        "unresolved_candidate_ids"
    ) != profile[
        "governed_state"
    ].get(
        "unresolved_candidate_ids"
    ):
        raise SemanticArticleProfileCertificationError(
            "Governed unresolved-state certification drifted."
        )

    if governed_state_certification.get(
        "abstention_candidate_ids"
    ) != profile[
        "governed_state"
    ].get(
        "abstention_candidate_ids"
    ):
        raise SemanticArticleProfileCertificationError(
            "Governed abstention certification drifted."
        )

    if structural_index_certification.get(
        "layer_index_count"
    ) != 15:
        raise SemanticArticleProfileCertificationError(
            "Structural layer-index certification drifted."
        )

    if structural_index_certification.get(
        "group_index_count"
    ) != 4:
        raise SemanticArticleProfileCertificationError(
            "Structural group-index certification drifted."
        )

    if structural_index_certification.get(
        "artifact_index_count"
    ) != 4:
        raise SemanticArticleProfileCertificationError(
            "Structural artifact-index certification drifted."
        )

    # -------------------------------------------------------------
    # Preservation guarantees
    # -------------------------------------------------------------

    for field in (
        "source_meaning_preserved",
        "source_authority_preserved",
        "governed_state_preserved",
        "profile_navigation_only_indexes",
    ):

        if profile.get(
            field
        ) is not True:
            raise SemanticArticleProfileCertificationError(
                "Canonical profile preservation field is not True: "
                + field
            )

    optional_forbidden_profile_fields = (
        "semantic_state_modified",
        "semantic_meaning_rewritten",
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
        "semantic_reclassification_performed",
        "semantic_count_recalculation_performed",
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

    for field in optional_forbidden_profile_fields:

        if (
            field in profile
            and profile[
                field
            ] is not False
        ):
            raise SemanticArticleProfileCertificationError(
                "Forbidden canonical-profile state detected: "
                + field
            )

    canonical_profile_integrity_certification = {
        "certification_status":
            "CERTIFIED",

        "certification_scope":
            "CANONICAL_SEMANTIC_ARTICLE_PROFILE_INTEGRITY",

        "certification_mode":
            "FULL_CANONICAL_PROFILE_STRUCTURAL_PRESERVATION_CERTIFICATION",

        "canonical_article_identity":
            deepcopy(
                dict(
                    canonical_identity
                )
            ),

        "profile_schema_version":
            "canonical_semantic_article_profile_v1",

        "profile_builder_phase":
            "4.6.17",

        "profile_builder_patch":
            "4.6.17J",

        "profile_section_count":
            8,

        "source_layer_count":
            15,

        "source_group_count":
            4,

        "cross_layer_artifact_count":
            4,

        "profile_section_order":
            list(
                _REQUIRED_PROFILE_SECTION_ORDER
            ),

        "profile_identity_integrity_certified":
            True,

        "source_authority_integrity_certified":
            True,

        "semantic_layer_integrity_certified":
            True,

        "semantic_group_integrity_certified":
            True,

        "cross_layer_artifact_integrity_certified":
            True,

        "governed_state_integrity_certified":
            True,

        "structural_index_integrity_certified":
            True,

        "certified_source_representation_integrity_certified":
            True,

        "all_eight_profile_sections_certified":
            True,

        "source_meaning_preserved":
            True,

        "source_authority_preserved":
            True,

        "governed_state_preserved":
            True,

        "profile_navigation_only_indexes":
            True,

        "profile_ready_for_final_certification":
            True,

        "profile_final_certification_performed":
            False,

        "profile_persistence_performed":
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

        "new_reasoning_performed":
            False,

        "new_fact_inference_performed":
            False,

        "new_relation_inference_performed":
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
            "canonical_semantic_article_profile_integrity_certification_v1",

        "version":
            SEMANTIC_ARTICLE_PROFILE_CERTIFICATION_VERSION,

        "phase":
            SEMANTIC_ARTICLE_PROFILE_CERTIFICATION_PHASE,

        "patch":
            "4.6.18I",

        "status":
            "CANONICAL_SEMANTIC_ARTICLE_PROFILE_INTEGRITY_CERTIFIED",

        "canonical_article_identity":
            deepcopy(
                dict(
                    canonical_identity
                )
            ),

        "identity_certification":
            deepcopy(
                dict(
                    identity_certification
                )
            ),

        "semantic_layer_group_certification":
            deepcopy(
                dict(
                    layer_group_certification
                )
            ),

        "cross_layer_artifact_certification":
            deepcopy(
                dict(
                    artifact_certification
                )
            ),

        "governed_state_certification":
            deepcopy(
                dict(
                    governed_state_certification
                )
            ),

        "structural_index_certification":
            deepcopy(
                dict(
                    structural_index_certification
                )
            ),

        "canonical_profile_integrity_certification":
            canonical_profile_integrity_certification,

        "profile_to_certify":
            deepcopy(
                dict(
                    profile
                )
            ),

        "source_certified_builder_profile":
            deepcopy(
                dict(
                    source_profile
                )
            ),

        "source_structural_index_certification_result":
            deepcopy(
                dict(
                    structural_index_certification_result
                )
            ),

        "processing_boundaries": {
            "certified_builder_intake_validation_preserved":
                True,

            "profile_identity_certification_preserved":
                True,

            "semantic_layer_group_certification_preserved":
                True,

            "cross_layer_artifact_certification_preserved":
                True,

            "governed_state_certification_preserved":
                True,

            "structural_index_certification_preserved":
                True,

            "canonical_profile_integrity_certification_performed":
                True,

            "all_eight_profile_sections_integrity_certified":
                True,

            "cross_certification_alignment_certified":
                True,

            "canonical_profile_exact_source_preservation_certified":
                True,

            "profile_ready_for_final_certification":
                True,

            "final_profile_certification_performed":
                False,

            "profile_persistence_performed":
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
            "final_certified_semantic_article_profile_result",
    }


# =====================================================================
# PATCH 4.6.18J ? Final Certified Semantic Article Profile Result
# =====================================================================

def build_final_certified_semantic_article_profile_result_v1(
    canonical_profile_integrity_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Produce the final certified Semantic Article Profile result for 4.6.18.

    This stage owns the transition:
        profile_certified: False -> True

    It does NOT persist the profile.
    It does NOT alter semantic meaning, governed state, indexes, or source
    authority.

    The frozen source profile remains unchanged and uncertified inside its
    preserved source snapshot.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        canonical_profile_integrity_result,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "canonical_profile_integrity_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.18I lifecycle contract
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "canonical_semantic_article_profile_integrity_certification_v1",
        ),
        (
            "version",
            "semantic_article_profile_certification_v1",
        ),
        (
            "phase",
            "4.6.18",
        ),
        (
            "patch",
            "4.6.18I",
        ),
        (
            "status",
            "CANONICAL_SEMANTIC_ARTICLE_PROFILE_INTEGRITY_CERTIFIED",
        ),
        (
            "persistence_policy",
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        ),
        (
            "next_stage",
            "final_certified_semantic_article_profile_result",
        ),
    ):

        if canonical_profile_integrity_result.get(
            field
        ) != expected:
            raise SemanticArticleProfileCertificationError(
                "Invalid 4.6.18I lifecycle field: "
                + field
            )

    boundaries = canonical_profile_integrity_result.get(
        "processing_boundaries"
    )

    integrity_certification = canonical_profile_integrity_result.get(
        "canonical_profile_integrity_certification"
    )

    source_profile = canonical_profile_integrity_result.get(
        "profile_to_certify"
    )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "4.6.18I processing boundaries are missing."
        )

    if not isinstance(
        integrity_certification,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Canonical profile integrity certification is missing."
        )

    if not isinstance(
        source_profile,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Canonical source profile is missing."
        )

    # -------------------------------------------------------------
    # I authority must be complete
    # -------------------------------------------------------------

    required_i_true = (
        "certified_builder_intake_validation_preserved",
        "profile_identity_certification_preserved",
        "semantic_layer_group_certification_preserved",
        "cross_layer_artifact_certification_preserved",
        "governed_state_certification_preserved",
        "structural_index_certification_preserved",
        "canonical_profile_integrity_certification_performed",
        "all_eight_profile_sections_integrity_certified",
        "cross_certification_alignment_certified",
        "canonical_profile_exact_source_preservation_certified",
        "profile_ready_for_final_certification",
    )

    for field in required_i_true:

        if boundaries.get(
            field
        ) is not True:
            raise SemanticArticleProfileCertificationError(
                "Required 4.6.18I boundary is not True: "
                + field
            )

    required_i_false = (
        "final_profile_certification_performed",
        "profile_persistence_performed",
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

    for field in required_i_false:

        if boundaries.get(
            field
        ) is not False:
            raise SemanticArticleProfileCertificationError(
                "Forbidden 4.6.18I boundary is not False: "
                + field
            )

    # -------------------------------------------------------------
    # Integrity certification contract
    # -------------------------------------------------------------

    if integrity_certification.get(
        "certification_status"
    ) != "CERTIFIED":
        raise SemanticArticleProfileCertificationError(
            "Canonical profile integrity is not certified."
        )

    if integrity_certification.get(
        "certification_scope"
    ) != "CANONICAL_SEMANTIC_ARTICLE_PROFILE_INTEGRITY":
        raise SemanticArticleProfileCertificationError(
            "Canonical profile integrity scope drifted."
        )

    if integrity_certification.get(
        "certification_mode"
    ) != (
        "FULL_CANONICAL_PROFILE_STRUCTURAL_PRESERVATION_CERTIFICATION"
    ):
        raise SemanticArticleProfileCertificationError(
            "Canonical profile integrity mode drifted."
        )

    for field in (
        "profile_identity_integrity_certified",
        "source_authority_integrity_certified",
        "semantic_layer_integrity_certified",
        "semantic_group_integrity_certified",
        "cross_layer_artifact_integrity_certified",
        "governed_state_integrity_certified",
        "structural_index_integrity_certified",
        "certified_source_representation_integrity_certified",
        "all_eight_profile_sections_certified",
        "source_meaning_preserved",
        "source_authority_preserved",
        "governed_state_preserved",
        "profile_navigation_only_indexes",
        "profile_ready_for_final_certification",
    ):

        if integrity_certification.get(
            field
        ) is not True:
            raise SemanticArticleProfileCertificationError(
                "Canonical profile integrity field is not True: "
                + field
            )

    if integrity_certification.get(
        "profile_final_certification_performed"
    ) is not False:
        raise SemanticArticleProfileCertificationError(
            "Profile was already finally certified before J."
        )

    if integrity_certification.get(
        "profile_persistence_performed"
    ) is not False:
        raise SemanticArticleProfileCertificationError(
            "Profile was persisted before 4.6.19."
        )

    # -------------------------------------------------------------
    # Source profile must still be the exact frozen profile certified
    # by 4.6.18I / inherited from 4.6.17L.
    #
    # This closes the I -> J mutation window:
    # J must never certify a candidate that changed after I.
    # -------------------------------------------------------------

    frozen_source_profile = canonical_profile_integrity_result.get(
        "source_certified_builder_profile"
    )

    if not isinstance(
        frozen_source_profile,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "Frozen certified-builder profile source is missing."
        )

    if source_profile != frozen_source_profile:
        raise SemanticArticleProfileCertificationError(
            "Profile candidate drifted after canonical integrity "
            "certification."
        )

    # Forbidden fields may be absent in the frozen source contract,
    # but if they are introduced they must remain explicitly False.
    forbidden_candidate_true_fields = (
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

    for field in forbidden_candidate_true_fields:

        if (
            field in source_profile
            and source_profile[
                field
            ] is not False
        ):
            raise SemanticArticleProfileCertificationError(
                "Forbidden candidate-profile state detected: "
                + field
            )

    # -------------------------------------------------------------
    # Source profile must still be the frozen uncertified profile
    # -------------------------------------------------------------

    if source_profile.get(
        "profile_schema_version"
    ) != "canonical_semantic_article_profile_v1":
        raise SemanticArticleProfileCertificationError(
            "Canonical source profile schema drifted."
        )

    if source_profile.get(
        "profile_status"
    ) != "CANONICAL_SEMANTIC_ARTICLE_PROFILE_ASSEMBLED":
        raise SemanticArticleProfileCertificationError(
            "Canonical source profile status drifted."
        )

    if source_profile.get(
        "profile_certification_ready"
    ) is not True:
        raise SemanticArticleProfileCertificationError(
            "Canonical source profile is not certification-ready."
        )

    if source_profile.get(
        "profile_certified"
    ) is not False:
        raise SemanticArticleProfileCertificationError(
            "Source profile must enter J uncertified."
        )

    if source_profile.get(
        "profile_persisted"
    ) is not False:
        raise SemanticArticleProfileCertificationError(
            "Source profile must enter J unpersisted."
        )

    if source_profile.get(
        "profile_section_order"
    ) != list(
        _REQUIRED_PROFILE_SECTION_ORDER
    ):
        raise SemanticArticleProfileCertificationError(
            "Canonical source profile section order drifted."
        )

    if (
        source_profile.get(
            "profile_section_count"
        )
        != 8
        or source_profile.get(
            "source_layer_count"
        )
        != 15
        or source_profile.get(
            "source_group_count"
        )
        != 4
        or source_profile.get(
            "cross_layer_artifact_count"
        )
        != 4
    ):
        raise SemanticArticleProfileCertificationError(
            "Canonical source profile structural counts drifted."
        )

    # -------------------------------------------------------------
    # Create NEW certified profile.
    #
    # The source profile is never mutated.
    # Only lifecycle certification metadata changes.
    # -------------------------------------------------------------

    certified_profile = deepcopy(
        dict(
            source_profile
        )
    )

    certified_profile[
        "profile_status"
    ] = "SEMANTIC_ARTICLE_PROFILE_CERTIFIED"

    certified_profile[
        "profile_certification_phase"
    ] = "4.6.18"

    certified_profile[
        "profile_certification_patch"
    ] = "4.6.18J"

    certified_profile[
        "profile_certification_status"
    ] = "CERTIFIED"

    certified_profile[
        "profile_certification_scope"
    ] = "FULL_SEMANTIC_ARTICLE_PROFILE"

    certified_profile[
        "profile_certification_mode"
    ] = (
        "STRUCTURAL_AND_PRESERVATION_PROFILE_CERTIFICATION"
    )

    certified_profile[
        "profile_certification_ready"
    ] = True

    certified_profile[
        "profile_certified"
    ] = True

    certified_profile[
        "profile_persisted"
    ] = False

    certified_profile[
        "profile_store_ready"
    ] = True

    certified_profile[
        "profile_store_owner"
    ] = "4.6.19_PROFILE_STORE"

    certified_profile[
        "semantic_memory_owner"
    ] = "4.6.28_SEMANTIC_MEMORY"

    certified_profile[
        "source_meaning_preserved"
    ] = True

    certified_profile[
        "source_authority_preserved"
    ] = True

    certified_profile[
        "governed_state_preserved"
    ] = True

    certified_profile[
        "profile_navigation_only_indexes"
    ] = True

    certified_profile[
        "semantic_state_modified"
    ] = False

    certified_profile[
        "semantic_meaning_rewritten"
    ] = False

    certified_profile[
        "source_authority_override_performed"
    ] = False

    certified_profile[
        "artifact_recomputation_performed"
    ] = False

    certified_profile[
        "upstream_index_rebuild_performed"
    ] = False

    certified_profile[
        "semantic_reclassification_performed"
    ] = False

    certified_profile[
        "semantic_count_recalculation_performed"
    ] = False

    certified_profile[
        "semantic_merge_performed"
    ] = False

    certified_profile[
        "cross_layer_reasoning_performed"
    ] = False

    certified_profile[
        "cross_layer_fact_synthesis_performed"
    ] = False

    certified_profile[
        "conflict_resolution_performed"
    ] = False

    certified_profile[
        "contradiction_adjudication_performed"
    ] = False

    certified_profile[
        "uncertainty_reinterpretation_performed"
    ] = False

    certified_profile[
        "uncertainty_strengthening_performed"
    ] = False

    certified_profile[
        "unified_semantic_confidence_calculated"
    ] = False

    certified_profile[
        "confidence_recalculation_performed"
    ] = False

    certified_profile[
        "abstention_decision_created"
    ] = False

    certified_profile[
        "abstention_decision_removed"
    ] = False

    certified_profile[
        "new_reasoning_performed"
    ] = False

    certified_profile[
        "new_fact_inference_performed"
    ] = False

    certified_profile[
        "new_relation_inference_performed"
    ] = False

    certified_profile[
        "semantic_memory_written"
    ] = False

    certified_profile[
        "profile_store_written"
    ] = False

    certified_profile[
        "linking_decisions_performed"
    ] = False

    certified_profile[
        "persistence_performed"
    ] = False

    # -------------------------------------------------------------
    # Verify content sections remain byte-for-byte equal
    # -------------------------------------------------------------

    for section_name in (
        _REQUIRED_PROFILE_SECTION_ORDER
    ):

        if certified_profile.get(
            section_name
        ) != source_profile.get(
            section_name
        ):
            raise SemanticArticleProfileCertificationError(
                "Certification changed canonical profile section: "
                + section_name
            )

    # -------------------------------------------------------------
    # Final profile certification record
    # -------------------------------------------------------------

    profile_certification = {
        "certification_status":
            "CERTIFIED",

        "certification_scope":
            "FULL_SEMANTIC_ARTICLE_PROFILE",

        "certification_mode":
            "STRUCTURAL_AND_PRESERVATION_PROFILE_CERTIFICATION",

        "certification_phase":
            "4.6.18",

        "certification_patch":
            "4.6.18J",

        "canonical_article_identity":
            deepcopy(
                canonical_profile_integrity_result[
                    "canonical_article_identity"
                ]
            ),

        "profile_schema_version":
            "canonical_semantic_article_profile_v1",

        "profile_section_count":
            8,

        "source_layer_count":
            15,

        "source_group_count":
            4,

        "cross_layer_artifact_count":
            4,

        "identity_certified":
            True,

        "semantic_layers_certified":
            True,

        "semantic_groups_certified":
            True,

        "cross_layer_artifacts_certified":
            True,

        "governed_state_certified":
            True,

        "structural_indexes_certified":
            True,

        "canonical_profile_integrity_certified":
            True,

        "certified_source_representation_certified":
            True,

        "source_meaning_preserved":
            True,

        "source_authority_preserved":
            True,

        "governed_state_preserved":
            True,

        "profile_navigation_only_indexes":
            True,

        "profile_certified":
            True,

        "profile_persisted":
            False,

        "profile_store_ready":
            True,

        "profile_store_owner":
            "4.6.19_PROFILE_STORE",

        "semantic_memory_owner":
            "4.6.28_SEMANTIC_MEMORY",

        "semantic_state_modified":
            False,

        "semantic_meaning_rewritten":
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

        "semantic_memory_written":
            False,

        "profile_store_written":
            False,

        "linking_decisions_performed":
            False,

        "persistence_performed":
            False,
    }

    final_result_summary = {
        "result_status":
            "CERTIFIED_SEMANTIC_ARTICLE_PROFILE_READY",

        "profile_certification_phase":
            "4.6.18",

        "profile_certification_patch":
            "4.6.18J",

        "profile_certified":
            True,

        "profile_persisted":
            False,

        "profile_store_ready":
            True,

        "next_owner":
            "4.6.19_PROFILE_STORE",

        "source_profile_preserved":
            True,

        "source_meaning_preserved":
            True,

        "source_authority_preserved":
            True,

        "governed_state_preserved":
            True,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    return {
        "schema_version":
            "final_certified_semantic_article_profile_result_v1",

        "version":
            SEMANTIC_ARTICLE_PROFILE_CERTIFICATION_VERSION,

        "phase":
            SEMANTIC_ARTICLE_PROFILE_CERTIFICATION_PHASE,

        "patch":
            "4.6.18J",

        "status":
            "CERTIFIED_SEMANTIC_ARTICLE_PROFILE_READY",

        "canonical_article_identity":
            deepcopy(
                canonical_profile_integrity_result[
                    "canonical_article_identity"
                ]
            ),

        "profile_certification":
            profile_certification,

        "certified_semantic_article_profile":
            certified_profile,

        "source_uncertified_semantic_article_profile":
            deepcopy(
                dict(
                    source_profile
                )
            ),

        "canonical_profile_integrity_certification":
            deepcopy(
                dict(
                    integrity_certification
                )
            ),

        "identity_certification":
            deepcopy(
                canonical_profile_integrity_result[
                    "identity_certification"
                ]
            ),

        "semantic_layer_group_certification":
            deepcopy(
                canonical_profile_integrity_result[
                    "semantic_layer_group_certification"
                ]
            ),

        "cross_layer_artifact_certification":
            deepcopy(
                canonical_profile_integrity_result[
                    "cross_layer_artifact_certification"
                ]
            ),

        "governed_state_certification":
            deepcopy(
                canonical_profile_integrity_result[
                    "governed_state_certification"
                ]
            ),

        "structural_index_certification":
            deepcopy(
                canonical_profile_integrity_result[
                    "structural_index_certification"
                ]
            ),

        "final_result_summary":
            final_result_summary,

        "source_canonical_profile_integrity_result":
            deepcopy(
                dict(
                    canonical_profile_integrity_result
                )
            ),

        "processing_boundaries": {
            "certified_builder_intake_validation_preserved":
                True,

            "profile_identity_certification_preserved":
                True,

            "semantic_layer_group_certification_preserved":
                True,

            "cross_layer_artifact_certification_preserved":
                True,

            "governed_state_certification_preserved":
                True,

            "structural_index_certification_preserved":
                True,

            "canonical_profile_integrity_certification_preserved":
                True,

            "final_profile_certification_performed":
                True,

            "profile_certified":
                True,

            "profile_store_ready":
                True,

            "profile_persistence_performed":
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
            "semantic_article_profile_full_certification",
    }


# =====================================================================
# PATCH 4.6.18K ? Full Profile Certification Hard Certification
# =====================================================================

def certify_semantic_article_profile_v1(
    final_profile_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Full 4.6.18 end-to-end Semantic Article Profile certification.

    K certifies the entire 4.6.18 profile-certification pipeline.

    K does NOT persist the profile.
    Persistence belongs to 4.6.19.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        final_profile_result,
        Mapping,
    ):
        raise SemanticArticleProfileCertificationError(
            "final_profile_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact J envelope
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "final_certified_semantic_article_profile_result_v1",
        ),
        (
            "version",
            "semantic_article_profile_certification_v1",
        ),
        (
            "phase",
            "4.6.18",
        ),
        (
            "patch",
            "4.6.18J",
        ),
        (
            "status",
            "CERTIFIED_SEMANTIC_ARTICLE_PROFILE_READY",
        ),
        (
            "persistence_policy",
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        ),
        (
            "next_stage",
            "semantic_article_profile_full_certification",
        ),
    ):

        if final_profile_result.get(
            field
        ) != expected:
            raise SemanticArticleProfileCertificationError(
                "Invalid 4.6.18J lifecycle field: "
                + field
            )

    canonical_identity = final_profile_result.get(
        "canonical_article_identity"
    )

    profile_certification = final_profile_result.get(
        "profile_certification"
    )

    certified_profile = final_profile_result.get(
        "certified_semantic_article_profile"
    )

    source_profile = final_profile_result.get(
        "source_uncertified_semantic_article_profile"
    )

    integrity_certification = final_profile_result.get(
        "canonical_profile_integrity_certification"
    )

    identity_certification = final_profile_result.get(
        "identity_certification"
    )

    layer_group_certification = final_profile_result.get(
        "semantic_layer_group_certification"
    )

    artifact_certification = final_profile_result.get(
        "cross_layer_artifact_certification"
    )

    governed_state_certification = final_profile_result.get(
        "governed_state_certification"
    )

    structural_index_certification = final_profile_result.get(
        "structural_index_certification"
    )

    final_summary = final_profile_result.get(
        "final_result_summary"
    )

    source_i = final_profile_result.get(
        "source_canonical_profile_integrity_result"
    )

    boundaries = final_profile_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "canonical_article_identity",
            canonical_identity,
        ),
        (
            "profile_certification",
            profile_certification,
        ),
        (
            "certified_semantic_article_profile",
            certified_profile,
        ),
        (
            "source_uncertified_semantic_article_profile",
            source_profile,
        ),
        (
            "canonical_profile_integrity_certification",
            integrity_certification,
        ),
        (
            "identity_certification",
            identity_certification,
        ),
        (
            "semantic_layer_group_certification",
            layer_group_certification,
        ),
        (
            "cross_layer_artifact_certification",
            artifact_certification,
        ),
        (
            "governed_state_certification",
            governed_state_certification,
        ),
        (
            "structural_index_certification",
            structural_index_certification,
        ),
        (
            "final_result_summary",
            final_summary,
        ),
        (
            "source_canonical_profile_integrity_result",
            source_i,
        ),
        (
            "processing_boundaries",
            boundaries,
        ),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise SemanticArticleProfileCertificationError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # Profile certification authority
    # -------------------------------------------------------------

    for field, expected in (
        (
            "certification_status",
            "CERTIFIED",
        ),
        (
            "certification_scope",
            "FULL_SEMANTIC_ARTICLE_PROFILE",
        ),
        (
            "certification_mode",
            "STRUCTURAL_AND_PRESERVATION_PROFILE_CERTIFICATION",
        ),
        (
            "certification_phase",
            "4.6.18",
        ),
        (
            "certification_patch",
            "4.6.18J",
        ),
        (
            "profile_store_owner",
            "4.6.19_PROFILE_STORE",
        ),
        (
            "semantic_memory_owner",
            "4.6.28_SEMANTIC_MEMORY",
        ),
    ):

        if profile_certification.get(
            field
        ) != expected:
            raise SemanticArticleProfileCertificationError(
                "Profile certification field drifted: "
                + field
            )

    for field in (
        "identity_certified",
        "semantic_layers_certified",
        "semantic_groups_certified",
        "cross_layer_artifacts_certified",
        "governed_state_certified",
        "structural_indexes_certified",
        "canonical_profile_integrity_certified",
        "certified_source_representation_certified",
        "source_meaning_preserved",
        "source_authority_preserved",
        "governed_state_preserved",
        "profile_navigation_only_indexes",
        "profile_certified",
        "profile_store_ready",
    ):

        if profile_certification.get(
            field
        ) is not True:
            raise SemanticArticleProfileCertificationError(
                "Required profile-certification field is not True: "
                + field
            )

    for field in (
        "profile_persisted",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "conflict_resolution_performed",
        "uncertainty_reinterpretation_performed",
        "confidence_recalculation_performed",
        "abstention_decision_created",
        "abstention_decision_removed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
        "semantic_memory_written",
        "profile_store_written",
        "linking_decisions_performed",
        "persistence_performed",
    ):

        if profile_certification.get(
            field
        ) is not False:
            raise SemanticArticleProfileCertificationError(
                "Forbidden profile-certification field is not False: "
                + field
            )

    # -------------------------------------------------------------
    # Certified-profile lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "profile_schema_version",
            "canonical_semantic_article_profile_v1",
        ),
        (
            "profile_status",
            "SEMANTIC_ARTICLE_PROFILE_CERTIFIED",
        ),
        (
            "profile_builder_phase",
            "4.6.17",
        ),
        (
            "profile_builder_patch",
            "4.6.17J",
        ),
        (
            "profile_mode",
            "CERTIFIED_SOURCE_STRUCTURAL_PROFILE",
        ),
        (
            "profile_certification_phase",
            "4.6.18",
        ),
        (
            "profile_certification_patch",
            "4.6.18J",
        ),
        (
            "profile_certification_status",
            "CERTIFIED",
        ),
        (
            "profile_certification_scope",
            "FULL_SEMANTIC_ARTICLE_PROFILE",
        ),
        (
            "profile_certification_mode",
            "STRUCTURAL_AND_PRESERVATION_PROFILE_CERTIFICATION",
        ),
        (
            "profile_store_owner",
            "4.6.19_PROFILE_STORE",
        ),
        (
            "semantic_memory_owner",
            "4.6.28_SEMANTIC_MEMORY",
        ),
    ):

        if certified_profile.get(
            field
        ) != expected:
            raise SemanticArticleProfileCertificationError(
                "Certified profile field drifted: "
                + field
            )

    if certified_profile.get(
        "profile_section_order"
    ) != list(
        _REQUIRED_PROFILE_SECTION_ORDER
    ):
        raise SemanticArticleProfileCertificationError(
            "Certified profile section order drifted."
        )

    if (
        certified_profile.get(
            "profile_section_count"
        )
        != 8
        or certified_profile.get(
            "source_layer_count"
        )
        != 15
        or certified_profile.get(
            "source_group_count"
        )
        != 4
        or certified_profile.get(
            "cross_layer_artifact_count"
        )
        != 4
    ):
        raise SemanticArticleProfileCertificationError(
            "Certified profile structural counts drifted."
        )

    for field in (
        "profile_certification_ready",
        "profile_certified",
        "profile_store_ready",
        "source_meaning_preserved",
        "source_authority_preserved",
        "governed_state_preserved",
        "profile_navigation_only_indexes",
    ):

        if certified_profile.get(
            field
        ) is not True:
            raise SemanticArticleProfileCertificationError(
                "Required certified-profile field is not True: "
                + field
            )

    if certified_profile.get(
        "profile_persisted"
    ) is not False:
        raise SemanticArticleProfileCertificationError(
            "Certified profile must remain unpersisted in 4.6.18."
        )

    forbidden_certified_profile_fields = (
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
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
        "semantic_memory_written",
        "profile_store_written",
        "linking_decisions_performed",
        "persistence_performed",
    )

    for field in forbidden_certified_profile_fields:

        if certified_profile.get(
            field
        ) is not False:
            raise SemanticArticleProfileCertificationError(
                "Forbidden certified-profile field is not False: "
                + field
            )

    # -------------------------------------------------------------
    # Source profile must remain frozen and uncertified
    # -------------------------------------------------------------

    if source_profile.get(
        "profile_status"
    ) != "CANONICAL_SEMANTIC_ARTICLE_PROFILE_ASSEMBLED":
        raise SemanticArticleProfileCertificationError(
            "Frozen source-profile status drifted."
        )

    if source_profile.get(
        "profile_certified"
    ) is not False:
        raise SemanticArticleProfileCertificationError(
            "Frozen source profile must remain uncertified."
        )

    if source_profile.get(
        "profile_persisted"
    ) is not False:
        raise SemanticArticleProfileCertificationError(
            "Frozen source profile must remain unpersisted."
        )

    if source_i.get(
        "profile_to_certify"
    ) != source_profile:
        raise SemanticArticleProfileCertificationError(
            "J source profile drifted from I canonical source."
        )

    if source_i.get(
        "source_certified_builder_profile"
    ) != source_profile:
        raise SemanticArticleProfileCertificationError(
            "J source profile drifted from certified 4.6.17 builder source."
        )

    # -------------------------------------------------------------
    # All eight canonical sections remain exact
    # -------------------------------------------------------------

    for section_name in (
        _REQUIRED_PROFILE_SECTION_ORDER
    ):

        if certified_profile.get(
            section_name
        ) != source_profile.get(
            section_name
        ):
            raise SemanticArticleProfileCertificationError(
                "Certified profile semantic section drifted: "
                + section_name
            )

    # -------------------------------------------------------------
    # Subordinate certifications
    # -------------------------------------------------------------

    for name, certification, expected_scope in (
        (
            "identity",
            identity_certification,
            "SEMANTIC_ARTICLE_PROFILE_IDENTITY",
        ),
        (
            "layers_groups",
            layer_group_certification,
            "SEMANTIC_ARTICLE_PROFILE_LAYERS_AND_GROUPS",
        ),
        (
            "artifacts",
            artifact_certification,
            "SEMANTIC_ARTICLE_PROFILE_CROSS_LAYER_ARTIFACTS",
        ),
        (
            "governed_state",
            governed_state_certification,
            "SEMANTIC_ARTICLE_PROFILE_GOVERNED_STATE",
        ),
        (
            "structural_indexes",
            structural_index_certification,
            "SEMANTIC_ARTICLE_PROFILE_STRUCTURAL_INDEXES",
        ),
        (
            "canonical_profile_integrity",
            integrity_certification,
            "CANONICAL_SEMANTIC_ARTICLE_PROFILE_INTEGRITY",
        ),
    ):

        if certification.get(
            "certification_status"
        ) != "CERTIFIED":
            raise SemanticArticleProfileCertificationError(
                name + " certification is not certified."
            )

        if certification.get(
            "certification_scope"
        ) != expected_scope:
            raise SemanticArticleProfileCertificationError(
                name + " certification scope drifted."
            )

    # -------------------------------------------------------------
    # Cross-certification canonical identity
    # -------------------------------------------------------------

    if profile_certification.get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise SemanticArticleProfileCertificationError(
            "Profile-certification canonical identity drifted."
        )

    if identity_certification.get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise SemanticArticleProfileCertificationError(
            "Identity-certification canonical identity drifted."
        )

    if certified_profile.get(
        "profile_identity",
        {}
    ).get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise SemanticArticleProfileCertificationError(
            "Certified-profile canonical identity drifted."
        )

    # -------------------------------------------------------------
    # Final summary contract
    # -------------------------------------------------------------

    for field, expected in (
        (
            "result_status",
            "CERTIFIED_SEMANTIC_ARTICLE_PROFILE_READY",
        ),
        (
            "profile_certification_phase",
            "4.6.18",
        ),
        (
            "profile_certification_patch",
            "4.6.18J",
        ),
        (
            "next_owner",
            "4.6.19_PROFILE_STORE",
        ),
    ):

        if final_summary.get(
            field
        ) != expected:
            raise SemanticArticleProfileCertificationError(
                "Final-result summary field drifted: "
                + field
            )

    for field in (
        "profile_certified",
        "profile_store_ready",
        "source_profile_preserved",
        "source_meaning_preserved",
        "source_authority_preserved",
        "governed_state_preserved",
    ):

        if final_summary.get(
            field
        ) is not True:
            raise SemanticArticleProfileCertificationError(
                "Required final-summary field is not True: "
                + field
            )

    for field in (
        "profile_persisted",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if final_summary.get(
            field
        ) is not False:
            raise SemanticArticleProfileCertificationError(
                "Forbidden final-summary field is not False: "
                + field
            )

    # -------------------------------------------------------------
    # J processing boundaries
    # -------------------------------------------------------------

    required_j_true = (
        "certified_builder_intake_validation_preserved",
        "profile_identity_certification_preserved",
        "semantic_layer_group_certification_preserved",
        "cross_layer_artifact_certification_preserved",
        "governed_state_certification_preserved",
        "structural_index_certification_preserved",
        "canonical_profile_integrity_certification_preserved",
        "final_profile_certification_performed",
        "profile_certified",
        "profile_store_ready",
    )

    for field in required_j_true:

        if boundaries.get(
            field
        ) is not True:
            raise SemanticArticleProfileCertificationError(
                "Required 4.6.18J boundary is not True: "
                + field
            )

    required_j_false = (
        "profile_persistence_performed",
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

    for field in required_j_false:

        if boundaries.get(
            field
        ) is not False:
            raise SemanticArticleProfileCertificationError(
                "Forbidden 4.6.18J boundary is not False: "
                + field
            )

    full_profile_certification = {
        "certification_status":
            "CERTIFIED",

        "certification_scope":
            "FULL_SEMANTIC_ARTICLE_PROFILE_CERTIFICATION_PIPELINE",

        "certification_mode":
            "END_TO_END_STRUCTURAL_PRESERVATION_HARD_CERTIFICATION",

        "certified_phase":
            "4.6.18",

        "certified_source_patch":
            "4.6.18J",

        "architecture_definition_certified":
            True,

        "certified_builder_input_contract_certified":
            True,

        "certified_builder_intake_certified":
            True,

        "profile_identity_certified":
            True,

        "semantic_layers_certified":
            True,

        "semantic_groups_certified":
            True,

        "cross_layer_artifacts_certified":
            True,

        "governed_state_certified":
            True,

        "structural_indexes_certified":
            True,

        "canonical_profile_integrity_certified":
            True,

        "final_profile_result_certified":
            True,

        "all_eight_profile_sections_certified":
            True,

        "all_15_semantic_layers_certified":
            True,

        "all_four_semantic_groups_certified":
            True,

        "all_four_cross_layer_artifacts_certified":
            True,

        "governed_state_preservation_certified":
            True,

        "profile_navigation_index_contract_certified":
            True,

        "certified_source_profile_preserved":
            True,

        "profile_certified":
            True,

        "profile_persisted":
            False,

        "profile_store_ready":
            True,

        "profile_store_owner":
            "4.6.19_PROFILE_STORE",

        "semantic_memory_owner":
            "4.6.28_SEMANTIC_MEMORY",

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
            "certified_semantic_article_profile_result_v1",

        "version":
            SEMANTIC_ARTICLE_PROFILE_CERTIFICATION_VERSION,

        "phase":
            SEMANTIC_ARTICLE_PROFILE_CERTIFICATION_PHASE,

        "patch":
            "4.6.18K",

        "status":
            "SEMANTIC_ARTICLE_PROFILE_CERTIFIED",

        "canonical_article_identity":
            deepcopy(
                dict(
                    canonical_identity
                )
            ),

        "full_profile_certification":
            full_profile_certification,

        "profile_certification":
            deepcopy(
                dict(
                    profile_certification
                )
            ),

        "certified_semantic_article_profile":
            deepcopy(
                dict(
                    certified_profile
                )
            ),

        "source_uncertified_semantic_article_profile":
            deepcopy(
                dict(
                    source_profile
                )
            ),

        "canonical_profile_integrity_certification":
            deepcopy(
                dict(
                    integrity_certification
                )
            ),

        "identity_certification":
            deepcopy(
                dict(
                    identity_certification
                )
            ),

        "semantic_layer_group_certification":
            deepcopy(
                dict(
                    layer_group_certification
                )
            ),

        "cross_layer_artifact_certification":
            deepcopy(
                dict(
                    artifact_certification
                )
            ),

        "governed_state_certification":
            deepcopy(
                dict(
                    governed_state_certification
                )
            ),

        "structural_index_certification":
            deepcopy(
                dict(
                    structural_index_certification
                )
            ),

        "final_result_summary":
            deepcopy(
                dict(
                    final_summary
                )
            ),

        "source_final_profile_result":
            deepcopy(
                dict(
                    final_profile_result
                )
            ),

        "processing_boundaries": {
            "full_profile_certification_performed":
                True,

            "profile_certified":
                True,

            "profile_store_ready":
                True,

            "profile_persistence_performed":
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
            "semantic_article_profile_store",
    }

