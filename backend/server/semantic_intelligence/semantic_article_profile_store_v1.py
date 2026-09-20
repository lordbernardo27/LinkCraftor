"""
LinkCraftor Semantic Intelligence
Phase 4.6.19 ? Semantic Article Profile Store

4.6.19B defines the persistence architecture only.

No profile write is permitted in this stage.
No Semantic Memory write is permitted.
No linking decision is permitted.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


SEMANTIC_ARTICLE_PROFILE_STORE_VERSION = (
    "semantic_article_profile_store_v1"
)

SEMANTIC_ARTICLE_PROFILE_STORE_PHASE = "4.6.19"


class SemanticArticleProfileStoreError(RuntimeError):
    """Raised when the Semantic Article Profile Store contract is violated."""


_PROFILE_STORE_STAGE_ORDER = (
    "4.6.19C",
    "4.6.19D",
    "4.6.19E",
    "4.6.19F",
    "4.6.19G",
    "4.6.19H",
    "4.6.19I",
    "4.6.19J",
    "4.6.19K",
)


_PROFILE_STORE_STAGE_NAMES = {
    "4.6.19C":
        "certified_profile_store_intake_validation",

    "4.6.19D":
        "storage_identity_key_definition",

    "4.6.19E":
        "persistence_envelope_assembly",

    "4.6.19F":
        "profile_write_contract",

    "4.6.19G":
        "read_back_verification",

    "4.6.19H":
        "integrity_immutability_verification",

    "4.6.19I":
        "store_metadata_versioning",

    "4.6.19J":
        "final_stored_semantic_article_profile_result",

    "4.6.19K":
        "full_profile_store_hard_certification",
}


_REQUIRED_418K_INPUT_CONTRACT = {
    "schema_version":
        "certified_semantic_article_profile_result_v1",

    "version":
        "semantic_article_profile_certification_v1",

    "phase":
        "4.6.18",

    "patch":
        "4.6.18K",

    "status":
        "SEMANTIC_ARTICLE_PROFILE_CERTIFIED",

    "persistence_policy":
        "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",

    "next_stage":
        "semantic_article_profile_store",
}


_REQUIRED_CERTIFIED_PROFILE_STATE = {
    "profile_schema_version":
        "canonical_semantic_article_profile_v1",

    "profile_status":
        "SEMANTIC_ARTICLE_PROFILE_CERTIFIED",

    "profile_certification_phase":
        "4.6.18",

    "profile_certification_patch":
        "4.6.18J",

    "profile_certification_status":
        "CERTIFIED",

    "profile_certification_scope":
        "FULL_SEMANTIC_ARTICLE_PROFILE",

    "profile_certification_mode":
        "STRUCTURAL_AND_PRESERVATION_PROFILE_CERTIFICATION",

    "profile_certification_ready":
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
}


_PROFILE_STORE_ARCHITECTURE_PRINCIPLES = (
    "CERTIFIED_PROFILE_ONLY",
    "EXACT_PROFILE_PRESERVATION",
    "NO_SEMANTIC_REWRITE",
    "NO_STATE_REINTERPRETATION",
    "NO_REASONING_DURING_PERSISTENCE",
    "DETERMINISTIC_STORAGE_IDENTITY",
    "IMMUTABLE_STORED_PROFILE_PAYLOAD",
    "EXPLICIT_VERSIONED_STORE_METADATA",
    "WRITE_THEN_READ_BACK_VERIFY",
    "CERTIFIED_READ_BACK_INTEGRITY",
    "PROFILE_STORE_SEPARATE_FROM_SEMANTIC_MEMORY",
    "PROFILE_STORE_SEPARATE_FROM_LINKING_RUNTIME",
    "PERSISTENCE_ADAPTER_BOUNDARY",
    "BACKEND_NEUTRAL_STORE_CONTRACT",
)


def define_semantic_article_profile_store_architecture_v1() -> dict[str, Any]:
    """
    Define the canonical 4.6.19 Profile Store architecture.

    This function defines contracts and boundaries only.
    It performs no write, read, persistence, or memory operation.
    """

    return {
        "schema_version":
            "semantic_article_profile_store_architecture_v1",

        "version":
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,

        "phase":
            SEMANTIC_ARTICLE_PROFILE_STORE_PHASE,

        "patch":
            "4.6.19B",

        "status":
            "SEMANTIC_ARTICLE_PROFILE_STORE_ARCHITECTURE_DEFINED",

        "store_scope":
            "CERTIFIED_SEMANTIC_ARTICLE_PROFILE_PERSISTENCE",

        "store_mode":
            "BACKEND_NEUTRAL_IMMUTABLE_PROFILE_STORE",

        "store_owner":
            "4.6.19_PROFILE_STORE",

        "source_owner":
            "4.6.18_PROFILE_CERTIFICATION",

        "future_semantic_memory_owner":
            "4.6.28_SEMANTIC_MEMORY",

        "required_input_contract":
            deepcopy(
                _REQUIRED_418K_INPUT_CONTRACT
            ),

        "required_certified_profile_state":
            deepcopy(
                _REQUIRED_CERTIFIED_PROFILE_STATE
            ),

        "architecture_principles":
            list(
                _PROFILE_STORE_ARCHITECTURE_PRINCIPLES
            ),

        "stage_order":
            list(
                _PROFILE_STORE_STAGE_ORDER
            ),

        "stage_names":
            deepcopy(
                _PROFILE_STORE_STAGE_NAMES
            ),

        "storage_layers": {
            "intake_layer": {
                "owner":
                    "4.6.19C",

                "responsibility":
                    "VALIDATE_CERTIFIED_4.6.18K_INPUT",

                "write_allowed":
                    False,
            },

            "identity_layer": {
                "owner":
                    "4.6.19D",

                "responsibility":
                    "DEFINE_DETERMINISTIC_STORAGE_IDENTITY_AND_KEY",

                "write_allowed":
                    False,
            },

            "envelope_layer": {
                "owner":
                    "4.6.19E",

                "responsibility":
                    "ASSEMBLE_VERSIONED_PERSISTENCE_ENVELOPE",

                "write_allowed":
                    False,
            },

            "write_layer": {
                "owner":
                    "4.6.19F",

                "responsibility":
                    "EXECUTE_PROFILE_WRITE_CONTRACT",

                "write_allowed":
                    True,
            },

            "read_back_layer": {
                "owner":
                    "4.6.19G",

                "responsibility":
                    "READ_AND_VERIFY_PERSISTED_PROFILE",

                "write_allowed":
                    False,
            },

            "integrity_layer": {
                "owner":
                    "4.6.19H",

                "responsibility":
                    "VERIFY_IMMUTABILITY_AND_CONTENT_INTEGRITY",

                "write_allowed":
                    False,
            },

            "metadata_layer": {
                "owner":
                    "4.6.19I",

                "responsibility":
                    "CERTIFY_STORE_METADATA_AND_VERSION",

                "write_allowed":
                    False,
            },

            "final_result_layer": {
                "owner":
                    "4.6.19J",

                "responsibility":
                    "ASSEMBLE_FINAL_STORED_PROFILE_RESULT",

                "write_allowed":
                    False,
            },

            "certification_layer": {
                "owner":
                    "4.6.19K",

                "responsibility":
                    "CERTIFY_FULL_PROFILE_STORE_PIPELINE",

                "write_allowed":
                    False,
            },
        },

        "persistence_contract": {
            "payload_authority":
                "4.6.18K_CERTIFIED_SEMANTIC_ARTICLE_PROFILE",

            "profile_payload_mutable":
                False,

            "semantic_sections_mutable":
                False,

            "governed_state_mutable":
                False,

            "structural_indexes_mutable":
                False,

            "certification_metadata_mutable":
                False,

            "store_metadata_separate_from_profile_payload":
                True,

            "write_requires_certified_profile":
                True,

            "write_requires_profile_store_ready":
                True,

            "write_requires_profile_persisted_false":
                True,

            "read_back_required_after_write":
                True,

            "integrity_verification_required":
                True,

            "version_metadata_required":
                True,

            "duplicate_write_policy":
                "DETERMINISTIC_IDEMPOTENT_CONTRACT",

            "backend_binding":
                "ADAPTER_BOUNDARY_DEFERRED_TO_WRITE_LAYER",
        },

        "immutability_contract": {
            "certified_profile_payload":
                "IMMUTABLE",

            "canonical_article_identity":
                "IMMUTABLE",

            "semantic_layers":
                "IMMUTABLE",

            "semantic_groups":
                "IMMUTABLE",

            "cross_layer_artifacts":
                "IMMUTABLE",

            "governed_state":
                "IMMUTABLE",

            "structural_indexes":
                "IMMUTABLE",

            "certified_source_semantic_representation":
                "IMMUTABLE",

            "store_metadata":
                "VERSIONED_SEPARATELY",
        },

        "ownership_boundaries": {
            "profile_certification":
                "4.6.18",

            "profile_persistence":
                "4.6.19",

            "knowledge_retrieval":
                "4.6.20",

            "cross_document_reasoning":
                "4.6.21",

            "semantic_memory":
                "4.6.28",

            "linking_decisions":
                "OUTSIDE_PROFILE_STORE",
        },

        "processing_boundaries": {
            "architecture_definition_performed":
                True,

            "certified_profile_intake_validation_performed":
                False,

            "storage_identity_defined":
                False,

            "persistence_envelope_assembled":
                False,

            "profile_write_performed":
                False,

            "profile_read_back_performed":
                False,

            "integrity_verification_performed":
                False,

            "store_metadata_versioning_performed":
                False,

            "final_stored_profile_result_built":
                False,

            "full_profile_store_certification_performed":
                False,

            "profile_payload_modified":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "semantic_merge_performed":
                False,

            "cross_document_reasoning_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "conflict_resolution_performed":
                False,

            "uncertainty_reinterpretation_performed":
                False,

            "confidence_recalculation_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ARCHITECTURE_DEFINITION_ONLY",

        "next_stage":
            "certified_profile_store_intake_validation",
    }


# =====================================================================
# PATCH 4.6.19C ? Certified Profile Store Intake Validation
# =====================================================================

def validate_certified_profile_store_intake_v1(
    certified_profile_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate the exact certified 4.6.18K profile-store handoff.

    This stage validates only.
    No persistence, key creation, read-back, memory write, or linking
    operation is permitted.
    """

    from collections.abc import Mapping
    from copy import deepcopy

    if not isinstance(
        certified_profile_result,
        Mapping,
    ):
        raise SemanticArticleProfileStoreError(
            "certified_profile_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.18K input envelope
    # -------------------------------------------------------------

    for field, expected in _REQUIRED_418K_INPUT_CONTRACT.items():

        if certified_profile_result.get(
            field
        ) != expected:
            raise SemanticArticleProfileStoreError(
                "Invalid 4.6.18K input field: "
                + field
            )

    architecture = define_semantic_article_profile_store_architecture_v1()

    if architecture.get(
        "status"
    ) != "SEMANTIC_ARTICLE_PROFILE_STORE_ARCHITECTURE_DEFINED":
        raise SemanticArticleProfileStoreError(
            "Profile Store architecture is not defined."
        )

    profile = certified_profile_result.get(
        "certified_semantic_article_profile"
    )

    full_certification = certified_profile_result.get(
        "full_profile_certification"
    )

    profile_certification = certified_profile_result.get(
        "profile_certification"
    )

    canonical_identity = certified_profile_result.get(
        "canonical_article_identity"
    )

    boundaries = certified_profile_result.get(
        "processing_boundaries"
    )

    source_profile = certified_profile_result.get(
        "source_uncertified_semantic_article_profile"
    )

    if not isinstance(
        profile,
        Mapping,
    ):
        raise SemanticArticleProfileStoreError(
            "Certified semantic article profile is missing."
        )

    if not isinstance(
        full_certification,
        Mapping,
    ):
        raise SemanticArticleProfileStoreError(
            "Full 4.6.18 profile certification is missing."
        )

    if not isinstance(
        profile_certification,
        Mapping,
    ):
        raise SemanticArticleProfileStoreError(
            "Profile certification record is missing."
        )

    if not isinstance(
        canonical_identity,
        Mapping,
    ):
        raise SemanticArticleProfileStoreError(
            "Canonical article identity is missing."
        )

    if not isinstance(
        boundaries,
        Mapping,
    ):
        raise SemanticArticleProfileStoreError(
            "4.6.18K processing boundaries are missing."
        )

    if not isinstance(
        source_profile,
        Mapping,
    ):
        raise SemanticArticleProfileStoreError(
            "Preserved uncertified source profile is missing."
        )

    # -------------------------------------------------------------
    # Certified-profile state
    # -------------------------------------------------------------

    for field, expected in _REQUIRED_CERTIFIED_PROFILE_STATE.items():

        if profile.get(
            field
        ) != expected:
            raise SemanticArticleProfileStoreError(
                "Certified profile state drifted: "
                + field
            )

    if profile.get(
        "profile_section_count"
    ) != 8:
        raise SemanticArticleProfileStoreError(
            "Certified profile section count must be 8."
        )

    if profile.get(
        "source_layer_count"
    ) != 15:
        raise SemanticArticleProfileStoreError(
            "Certified profile layer count must be 15."
        )

    if profile.get(
        "source_group_count"
    ) != 4:
        raise SemanticArticleProfileStoreError(
            "Certified profile group count must be 4."
        )

    if profile.get(
        "cross_layer_artifact_count"
    ) != 4:
        raise SemanticArticleProfileStoreError(
            "Certified profile artifact count must be 4."
        )

    required_sections = (
        "profile_identity",
        "source_authority",
        "semantic_layers",
        "semantic_groups",
        "cross_layer_artifacts",
        "governed_state",
        "structural_indexes",
        "certified_source_semantic_representation",
    )

    if profile.get(
        "profile_section_order"
    ) != list(
        required_sections
    ):
        raise SemanticArticleProfileStoreError(
            "Certified profile section order drifted."
        )

    for section_name in required_sections:

        if section_name not in profile:
            raise SemanticArticleProfileStoreError(
                "Certified profile section is missing: "
                + section_name
            )

    # -------------------------------------------------------------
    # Certification authority
    # -------------------------------------------------------------

    if full_certification.get(
        "certification_status"
    ) != "CERTIFIED":
        raise SemanticArticleProfileStoreError(
            "Full profile certification is not certified."
        )

    if full_certification.get(
        "certification_scope"
    ) != (
        "FULL_SEMANTIC_ARTICLE_PROFILE_CERTIFICATION_PIPELINE"
    ):
        raise SemanticArticleProfileStoreError(
            "Full profile certification scope drifted."
        )

    if full_certification.get(
        "certification_mode"
    ) != (
        "END_TO_END_STRUCTURAL_PRESERVATION_HARD_CERTIFICATION"
    ):
        raise SemanticArticleProfileStoreError(
            "Full profile certification mode drifted."
        )

    if full_certification.get(
        "profile_certified"
    ) is not True:
        raise SemanticArticleProfileStoreError(
            "Full certification does not mark profile certified."
        )

    if full_certification.get(
        "profile_store_ready"
    ) is not True:
        raise SemanticArticleProfileStoreError(
            "Full certification does not mark profile store-ready."
        )

    if full_certification.get(
        "profile_persisted"
    ) is not False:
        raise SemanticArticleProfileStoreError(
            "Profile must be unpersisted before 4.6.19 write."
        )

    if full_certification.get(
        "profile_store_owner"
    ) != "4.6.19_PROFILE_STORE":
        raise SemanticArticleProfileStoreError(
            "Profile Store ownership drifted."
        )

    if full_certification.get(
        "semantic_memory_owner"
    ) != "4.6.28_SEMANTIC_MEMORY":
        raise SemanticArticleProfileStoreError(
            "Semantic Memory ownership drifted."
        )

    if profile_certification.get(
        "certification_status"
    ) != "CERTIFIED":
        raise SemanticArticleProfileStoreError(
            "Profile certification record is not certified."
        )

    if profile_certification.get(
        "profile_certified"
    ) is not True:
        raise SemanticArticleProfileStoreError(
            "Profile certification record does not mark profile certified."
        )

    if profile_certification.get(
        "profile_persisted"
    ) is not False:
        raise SemanticArticleProfileStoreError(
            "Profile certification record indicates premature persistence."
        )

    # -------------------------------------------------------------
    # Identity alignment
    # -------------------------------------------------------------

    if profile.get(
        "profile_identity",
        {}
    ).get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise SemanticArticleProfileStoreError(
            "Certified profile canonical identity drifted."
        )

    if profile_certification.get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise SemanticArticleProfileStoreError(
            "Profile certification identity drifted."
        )

    # -------------------------------------------------------------
    # Preserved source profile
    # -------------------------------------------------------------

    if source_profile.get(
        "profile_status"
    ) != "CANONICAL_SEMANTIC_ARTICLE_PROFILE_ASSEMBLED":
        raise SemanticArticleProfileStoreError(
            "Preserved source-profile status drifted."
        )

    if source_profile.get(
        "profile_certified"
    ) is not False:
        raise SemanticArticleProfileStoreError(
            "Preserved source profile must remain uncertified."
        )

    if source_profile.get(
        "profile_persisted"
    ) is not False:
        raise SemanticArticleProfileStoreError(
            "Preserved source profile must remain unpersisted."
        )

    for section_name in required_sections:

        if profile.get(
            section_name
        ) != source_profile.get(
            section_name
        ):
            raise SemanticArticleProfileStoreError(
                "Certified profile content drifted from preserved source: "
                + section_name
            )

    # -------------------------------------------------------------
    # Forbidden upstream operations
    # -------------------------------------------------------------

    for field in (
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

        if boundaries.get(
            field
        ) is not False:
            raise SemanticArticleProfileStoreError(
                "Forbidden 4.6.18K boundary is not False: "
                + field
            )

    if boundaries.get(
        "profile_certified"
    ) is not True:
        raise SemanticArticleProfileStoreError(
            "4.6.18K boundary does not mark profile certified."
        )

    if boundaries.get(
        "profile_store_ready"
    ) is not True:
        raise SemanticArticleProfileStoreError(
            "4.6.18K boundary does not mark profile store-ready."
        )

    if boundaries.get(
        "full_profile_certification_performed"
    ) is not True:
        raise SemanticArticleProfileStoreError(
            "4.6.18K full certification boundary is missing."
        )

    # -------------------------------------------------------------
    # 4.6.19C output
    # -------------------------------------------------------------

    return {
        "schema_version":
            "semantic_article_profile_store_intake_v1",

        "version":
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,

        "phase":
            SEMANTIC_ARTICLE_PROFILE_STORE_PHASE,

        "patch":
            "4.6.19C",

        "status":
            "CERTIFIED_PROFILE_STORE_INTAKE_VALIDATED",

        "canonical_article_identity":
            deepcopy(
                dict(
                    canonical_identity
                )
            ),

        "certified_semantic_article_profile":
            deepcopy(
                dict(
                    profile
                )
            ),

        "source_certified_profile_result":
            deepcopy(
                dict(
                    certified_profile_result
                )
            ),

        "intake_validation": {
            "validation_status":
                "VALIDATED",

            "validation_scope":
                "CERTIFIED_4.6.18K_PROFILE_STORE_INPUT",

            "source_phase":
                "4.6.18",

            "source_patch":
                "4.6.18K",

            "source_profile_certified":
                True,

            "source_profile_store_ready":
                True,

            "source_profile_persisted":
                False,

            "canonical_identity_validated":
                True,

            "profile_structure_validated":
                True,

            "profile_certification_validated":
                True,

            "full_certification_validated":
                True,

            "source_profile_preservation_validated":
                True,

            "profile_payload_preserved":
                True,

            "semantic_memory_deferred":
                True,

            "profile_write_performed":
                False,

            "persistence_performed":
                False,
        },

        "processing_boundaries": {
            "architecture_definition_preserved":
                True,

            "certified_profile_intake_validation_performed":
                True,

            "storage_identity_defined":
                False,

            "persistence_envelope_assembled":
                False,

            "profile_write_performed":
                False,

            "profile_read_back_performed":
                False,

            "integrity_verification_performed":
                False,

            "store_metadata_versioning_performed":
                False,

            "final_stored_profile_result_built":
                False,

            "full_profile_store_certification_performed":
                False,

            "profile_payload_modified":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "semantic_merge_performed":
                False,

            "cross_document_reasoning_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "conflict_resolution_performed":
                False,

            "uncertainty_reinterpretation_performed":
                False,

            "confidence_recalculation_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "VALIDATION_ONLY_NO_WRITE",

        "next_stage":
            "storage_identity_key_definition",
    }

# =====================================================================
# PATCH 4.6.19D ? Storage Identity & Key Definition
# =====================================================================

def define_profile_storage_identity_v1(
    intake_validation_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Define the deterministic storage identity/key for a certified,
    validated Semantic Article Profile.

    4.6.19D performs identity definition only.

    It does NOT:
    - persist the profile,
    - generate the profile payload hash,
    - bind a persistence backend,
    - assign a physical storage location,
    - write Semantic Memory,
    - perform linking.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        intake_validation_result,
        Mapping,
    ):
        raise SemanticArticleProfileStoreError(
            "intake_validation_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.19C lifecycle
    # -------------------------------------------------------------

    required_lifecycle = {
        "schema_version":
            "semantic_article_profile_store_intake_v1",

        "version":
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,

        "phase":
            SEMANTIC_ARTICLE_PROFILE_STORE_PHASE,

        "patch":
            "4.6.19C",

        "status":
            "CERTIFIED_PROFILE_STORE_INTAKE_VALIDATED",

        "persistence_policy":
            "VALIDATION_ONLY_NO_WRITE",

        "next_stage":
            "storage_identity_key_definition",
    }

    for field, expected in required_lifecycle.items():

        if intake_validation_result.get(field) != expected:
            raise SemanticArticleProfileStoreError(
                f"Invalid 4.6.19C lifecycle field: {field}"
            )

    validation = intake_validation_result.get(
        "intake_validation"
    )

    profile = intake_validation_result.get(
        "certified_semantic_article_profile"
    )

    canonical_identity = intake_validation_result.get(
        "canonical_article_identity"
    )

    boundaries = intake_validation_result.get(
        "processing_boundaries"
    )

    if not isinstance(validation, Mapping):
        raise SemanticArticleProfileStoreError(
            "4.6.19C intake_validation is missing."
        )

    if not isinstance(profile, Mapping):
        raise SemanticArticleProfileStoreError(
            "Certified semantic article profile is missing."
        )

    if not isinstance(canonical_identity, Mapping):
        raise SemanticArticleProfileStoreError(
            "Canonical article identity is missing."
        )

    if not isinstance(boundaries, Mapping):
        raise SemanticArticleProfileStoreError(
            "4.6.19C processing boundaries are missing."
        )

    # -------------------------------------------------------------
    # Certified intake authority
    # -------------------------------------------------------------

    for field in (
        "source_profile_certified",
        "source_profile_store_ready",
        "canonical_identity_validated",
        "profile_structure_validated",
        "profile_certification_validated",
        "full_certification_validated",
        "source_profile_preservation_validated",
        "profile_payload_preserved",
        "semantic_memory_deferred",
    ):

        if validation.get(field) is not True:
            raise SemanticArticleProfileStoreError(
                f"Required intake validation field is not True: {field}"
            )

    for field in (
        "source_profile_persisted",
        "profile_write_performed",
        "persistence_performed",
    ):

        if validation.get(field) is not False:
            raise SemanticArticleProfileStoreError(
                f"Forbidden intake validation field is not False: {field}"
            )

    if boundaries.get(
        "certified_profile_intake_validation_performed"
    ) is not True:
        raise SemanticArticleProfileStoreError(
            "Certified-profile intake validation was not performed."
        )

    for field in (
        "storage_identity_defined",
        "persistence_envelope_assembled",
        "profile_write_performed",
        "profile_read_back_performed",
        "integrity_verification_performed",
        "store_metadata_versioning_performed",
        "final_stored_profile_result_built",
        "full_profile_store_certification_performed",
        "profile_payload_modified",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "semantic_merge_performed",
        "cross_document_reasoning_performed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
        "conflict_resolution_performed",
        "uncertainty_reinterpretation_performed",
        "confidence_recalculation_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
        "persistence_performed",
    ):

        if boundaries.get(field) is not False:
            raise SemanticArticleProfileStoreError(
                f"Forbidden 4.6.19C boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Canonical identity
    # -------------------------------------------------------------

    article_id = canonical_identity.get(
        "article_id"
    )

    workspace_id = canonical_identity.get(
        "workspace_id"
    )

    if not isinstance(article_id, str) or not article_id.strip():
        raise SemanticArticleProfileStoreError(
            "Canonical article_id must be a non-empty string."
        )

    if not isinstance(workspace_id, str) or not workspace_id.strip():
        raise SemanticArticleProfileStoreError(
            "Canonical workspace_id must be a non-empty string."
        )

    article_id = article_id.strip()
    workspace_id = workspace_id.strip()

    profile_identity = profile.get(
        "profile_identity"
    )

    if not isinstance(profile_identity, Mapping):
        raise SemanticArticleProfileStoreError(
            "Certified profile identity section is missing."
        )

    if profile_identity.get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise SemanticArticleProfileStoreError(
            "Certified profile canonical identity drifted."
        )

    if profile.get(
        "profile_certified"
    ) is not True:
        raise SemanticArticleProfileStoreError(
            "Storage identity requires profile_certified=True."
        )

    if profile.get(
        "profile_store_ready"
    ) is not True:
        raise SemanticArticleProfileStoreError(
            "Storage identity requires profile_store_ready=True."
        )

    if profile.get(
        "profile_persisted"
    ) is not False:
        raise SemanticArticleProfileStoreError(
            "Incoming profile must remain unpersisted."
        )

    if profile.get(
        "profile_store_owner"
    ) != "4.6.19_PROFILE_STORE":
        raise SemanticArticleProfileStoreError(
            "Profile Store ownership drifted."
        )

    if profile.get(
        "semantic_memory_owner"
    ) != "4.6.28_SEMANTIC_MEMORY":
        raise SemanticArticleProfileStoreError(
            "Semantic Memory ownership drifted."
        )

    # -------------------------------------------------------------
    # Deterministic identity material
    # -------------------------------------------------------------

    identity_material = {
        "namespace":
            "linkcraftor.semantic_article_profile_store",

        "store_schema_version":
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,

        "profile_schema_version":
            profile.get("profile_schema_version"),

        "workspace_id":
            workspace_id,

        "article_id":
            article_id,
    }

    canonical_identity_json = json.dumps(
        identity_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    identity_digest = hashlib.sha256(
        canonical_identity_json.encode("utf-8")
    ).hexdigest()

    storage_key = (
        "sap:v1:"
        + workspace_id
        + ":"
        + article_id
        + ":"
        + identity_digest[:24]
    )

    storage_identity = {
        "storage_identity_schema":
            "semantic_article_profile_storage_identity_v1",

        "storage_namespace":
            "linkcraftor.semantic_article_profile_store",

        "store_schema_version":
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,

        "profile_schema_version":
            profile.get("profile_schema_version"),

        "workspace_id":
            workspace_id,

        "article_id":
            article_id,

        "identity_algorithm":
            "SHA256",

        "identity_material_canonicalization":
            "JSON_SORTED_KEYS_COMPACT_UTF8",

        "identity_digest":
            identity_digest,

        "storage_key":
            storage_key,

        "storage_key_version":
            "v1",

        "deterministic":
            True,

        "article_scoped":
            True,

        "workspace_scoped":
            True,

        # Payload hashing belongs to E, because E owns the
        # persistence envelope containing the immutable payload.
        "profile_payload_hash":
            None,

        "profile_payload_hash_deferred_to_envelope_stage":
            True,

        "persistence_location_assigned":
            False,

        "persistence_backend_bound":
            False,

        "profile_write_performed":
            False,
    }

    return {
        "schema_version":
            "semantic_article_profile_storage_identity_result_v1",

        "version":
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,

        "phase":
            SEMANTIC_ARTICLE_PROFILE_STORE_PHASE,

        "patch":
            "4.6.19D",

        "status":
            "PROFILE_STORAGE_IDENTITY_DEFINED",

        "canonical_article_identity":
            deepcopy(dict(canonical_identity)),

        "storage_identity":
            storage_identity,

        "certified_semantic_article_profile":
            deepcopy(dict(profile)),

        "source_intake_validation_result":
            deepcopy(dict(intake_validation_result)),

        "processing_boundaries": {
            "architecture_definition_preserved":
                True,

            "certified_profile_intake_validation_preserved":
                True,

            "storage_identity_defined":
                True,

            "deterministic_storage_key_generated":
                True,

            "profile_payload_hash_generated":
                False,

            "persistence_backend_bound":
                False,

            "persistence_location_assigned":
                False,

            "persistence_envelope_assembled":
                False,

            "profile_write_performed":
                False,

            "profile_read_back_performed":
                False,

            "integrity_verification_performed":
                False,

            "store_metadata_versioning_performed":
                False,

            "final_stored_profile_result_built":
                False,

            "full_profile_store_certification_performed":
                False,

            "profile_payload_modified":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "semantic_merge_performed":
                False,

            "cross_document_reasoning_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "conflict_resolution_performed":
                False,

            "uncertainty_reinterpretation_performed":
                False,

            "confidence_recalculation_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "IDENTITY_DEFINITION_ONLY_NO_WRITE",

        "next_stage":
            "persistence_envelope_assembly",
    }


# =====================================================================
# PATCH 4.6.19E ? Persistence Envelope Assembly
# =====================================================================

def assemble_profile_persistence_envelope_v1(
    storage_identity_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Assemble the immutable persistence envelope for a certified profile.

    E calculates the deterministic profile payload hash and binds it to the
    already-certified storage identity.

    E does NOT write anything to storage.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        storage_identity_result,
        Mapping,
    ):
        raise SemanticArticleProfileStoreError(
            "storage_identity_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.19D lifecycle
    # -------------------------------------------------------------

    required_lifecycle = {
        "schema_version":
            "semantic_article_profile_storage_identity_result_v1",

        "version":
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,

        "phase":
            SEMANTIC_ARTICLE_PROFILE_STORE_PHASE,

        "patch":
            "4.6.19D",

        "status":
            "PROFILE_STORAGE_IDENTITY_DEFINED",

        "persistence_policy":
            "IDENTITY_DEFINITION_ONLY_NO_WRITE",

        "next_stage":
            "persistence_envelope_assembly",
    }

    for field, expected in required_lifecycle.items():

        if storage_identity_result.get(field) != expected:
            raise SemanticArticleProfileStoreError(
                f"Invalid 4.6.19D lifecycle field: {field}"
            )

    storage_identity = storage_identity_result.get(
        "storage_identity"
    )

    profile = storage_identity_result.get(
        "certified_semantic_article_profile"
    )

    canonical_identity = storage_identity_result.get(
        "canonical_article_identity"
    )

    boundaries = storage_identity_result.get(
        "processing_boundaries"
    )

    if not isinstance(storage_identity, Mapping):
        raise SemanticArticleProfileStoreError(
            "4.6.19D storage identity is missing."
        )

    if not isinstance(profile, Mapping):
        raise SemanticArticleProfileStoreError(
            "Certified semantic article profile is missing."
        )

    if not isinstance(canonical_identity, Mapping):
        raise SemanticArticleProfileStoreError(
            "Canonical article identity is missing."
        )

    if not isinstance(boundaries, Mapping):
        raise SemanticArticleProfileStoreError(
            "4.6.19D processing boundaries are missing."
        )

    # -------------------------------------------------------------
    # Storage identity authority
    # -------------------------------------------------------------

    for field, expected in (
        (
            "storage_identity_schema",
            "semantic_article_profile_storage_identity_v1",
        ),
        (
            "storage_namespace",
            "linkcraftor.semantic_article_profile_store",
        ),
        (
            "store_schema_version",
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,
        ),
        (
            "profile_schema_version",
            "canonical_semantic_article_profile_v1",
        ),
        (
            "identity_algorithm",
            "SHA256",
        ),
        (
            "identity_material_canonicalization",
            "JSON_SORTED_KEYS_COMPACT_UTF8",
        ),
        (
            "storage_key_version",
            "v1",
        ),
    ):

        if storage_identity.get(field) != expected:
            raise SemanticArticleProfileStoreError(
                f"Storage identity field drifted: {field}"
            )

    for field in (
        "deterministic",
        "article_scoped",
        "workspace_scoped",
        "profile_payload_hash_deferred_to_envelope_stage",
    ):

        if storage_identity.get(field) is not True:
            raise SemanticArticleProfileStoreError(
                f"Required storage identity field is not True: {field}"
            )

    for field in (
        "persistence_location_assigned",
        "persistence_backend_bound",
        "profile_write_performed",
    ):

        if storage_identity.get(field) is not False:
            raise SemanticArticleProfileStoreError(
                f"Forbidden storage identity field is not False: {field}"
            )

    if storage_identity.get(
        "profile_payload_hash"
    ) is not None:
        raise SemanticArticleProfileStoreError(
            "Profile payload hash must still be deferred before E."
        )

    workspace_id = canonical_identity.get(
        "workspace_id"
    )

    article_id = canonical_identity.get(
        "article_id"
    )

    if storage_identity.get(
        "workspace_id"
    ) != workspace_id:
        raise SemanticArticleProfileStoreError(
            "Storage identity workspace_id drifted."
        )

    if storage_identity.get(
        "article_id"
    ) != article_id:
        raise SemanticArticleProfileStoreError(
            "Storage identity article_id drifted."
        )

    # Recompute storage identity digest independently.
    identity_material = {
        "namespace":
            "linkcraftor.semantic_article_profile_store",

        "store_schema_version":
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,

        "profile_schema_version":
            profile.get(
                "profile_schema_version"
            ),

        "workspace_id":
            workspace_id,

        "article_id":
            article_id,
    }

    identity_json = json.dumps(
        identity_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    expected_identity_digest = hashlib.sha256(
        identity_json.encode("utf-8")
    ).hexdigest()

    if storage_identity.get(
        "identity_digest"
    ) != expected_identity_digest:
        raise SemanticArticleProfileStoreError(
            "Storage identity digest verification failed."
        )

    expected_storage_key = (
        "sap:v1:"
        + workspace_id
        + ":"
        + article_id
        + ":"
        + expected_identity_digest[:24]
    )

    if storage_identity.get(
        "storage_key"
    ) != expected_storage_key:
        raise SemanticArticleProfileStoreError(
            "Storage key verification failed."
        )

    # -------------------------------------------------------------
    # Certified profile authority
    # -------------------------------------------------------------

    if profile.get(
        "profile_certified"
    ) is not True:
        raise SemanticArticleProfileStoreError(
            "Persistence envelope requires a certified profile."
        )

    if profile.get(
        "profile_store_ready"
    ) is not True:
        raise SemanticArticleProfileStoreError(
            "Persistence envelope requires a store-ready profile."
        )

    if profile.get(
        "profile_persisted"
    ) is not False:
        raise SemanticArticleProfileStoreError(
            "Incoming profile must remain unpersisted."
        )

    if profile.get(
        "profile_store_owner"
    ) != "4.6.19_PROFILE_STORE":
        raise SemanticArticleProfileStoreError(
            "Profile Store owner drifted."
        )

    if profile.get(
        "semantic_memory_owner"
    ) != "4.6.28_SEMANTIC_MEMORY":
        raise SemanticArticleProfileStoreError(
            "Semantic Memory owner drifted."
        )

    profile_identity = profile.get(
        "profile_identity"
    )

    if (
        not isinstance(profile_identity, Mapping)
        or profile_identity.get(
            "canonical_article_identity"
        )
        != canonical_identity
    ):
        raise SemanticArticleProfileStoreError(
            "Profile canonical identity drifted."
        )

    # -------------------------------------------------------------
    # D processing boundaries
    # -------------------------------------------------------------

    for field in (
        "architecture_definition_preserved",
        "certified_profile_intake_validation_preserved",
        "storage_identity_defined",
        "deterministic_storage_key_generated",
    ):

        if boundaries.get(field) is not True:
            raise SemanticArticleProfileStoreError(
                f"Required 4.6.19D boundary is not True: {field}"
            )

    for field in (
        "profile_payload_hash_generated",
        "persistence_backend_bound",
        "persistence_location_assigned",
        "persistence_envelope_assembled",
        "profile_write_performed",
        "profile_read_back_performed",
        "integrity_verification_performed",
        "store_metadata_versioning_performed",
        "final_stored_profile_result_built",
        "full_profile_store_certification_performed",
        "profile_payload_modified",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "semantic_merge_performed",
        "cross_document_reasoning_performed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
        "conflict_resolution_performed",
        "uncertainty_reinterpretation_performed",
        "confidence_recalculation_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
        "persistence_performed",
    ):

        if boundaries.get(field) is not False:
            raise SemanticArticleProfileStoreError(
                f"Forbidden 4.6.19D boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Canonical immutable payload serialization
    # -------------------------------------------------------------

    profile_payload = deepcopy(
        dict(profile)
    )

    canonical_payload_json = json.dumps(
        profile_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    profile_payload_hash = hashlib.sha256(
        canonical_payload_json.encode("utf-8")
    ).hexdigest()

    payload_byte_length = len(
        canonical_payload_json.encode("utf-8")
    )

    # -------------------------------------------------------------
    # Persistence envelope
    # -------------------------------------------------------------

    persistence_envelope = {
        "persistence_envelope_schema":
            "semantic_article_profile_persistence_envelope_v1",

        "persistence_envelope_version":
            "v1",

        "store_schema_version":
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,

        "storage_namespace":
            storage_identity[
                "storage_namespace"
            ],

        "storage_key":
            storage_identity[
                "storage_key"
            ],

        "storage_identity_digest":
            storage_identity[
                "identity_digest"
            ],

        "workspace_id":
            workspace_id,

        "article_id":
            article_id,

        "profile_schema_version":
            profile[
                "profile_schema_version"
            ],

        "profile_payload_hash_algorithm":
            "SHA256",

        "profile_payload_canonicalization":
            "JSON_SORTED_KEYS_COMPACT_UTF8",

        "profile_payload_hash":
            profile_payload_hash,

        "profile_payload_byte_length":
            payload_byte_length,

        "profile_payload":
            profile_payload,

        "payload_immutable":
            True,

        "payload_hash_verified":
            True,

        "storage_identity_verified":
            True,

        "profile_certified":
            True,

        "profile_store_ready":
            True,

        "profile_persisted_before_write":
            False,

        "write_authorized_for_next_stage":
            True,

        "write_performed":
            False,

        "read_back_performed":
            False,

        "backend_bound":
            False,

        "physical_location_assigned":
            False,

        "semantic_memory_written":
            False,
    }

    return {
        "schema_version":
            "semantic_article_profile_persistence_envelope_result_v1",

        "version":
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,

        "phase":
            SEMANTIC_ARTICLE_PROFILE_STORE_PHASE,

        "patch":
            "4.6.19E",

        "status":
            "PROFILE_PERSISTENCE_ENVELOPE_ASSEMBLED",

        "canonical_article_identity":
            deepcopy(
                dict(canonical_identity)
            ),

        "storage_identity":
            deepcopy(
                dict(storage_identity)
            ),

        "persistence_envelope":
            persistence_envelope,

        "certified_semantic_article_profile":
            deepcopy(
                dict(profile)
            ),

        "source_storage_identity_result":
            deepcopy(
                dict(storage_identity_result)
            ),

        "processing_boundaries": {
            "architecture_definition_preserved":
                True,

            "certified_profile_intake_validation_preserved":
                True,

            "storage_identity_preserved":
                True,

            "deterministic_storage_key_preserved":
                True,

            "profile_payload_hash_generated":
                True,

            "profile_payload_hash_verified":
                True,

            "persistence_envelope_assembled":
                True,

            "write_authorized_for_next_stage":
                True,

            "persistence_backend_bound":
                False,

            "persistence_location_assigned":
                False,

            "profile_write_performed":
                False,

            "profile_read_back_performed":
                False,

            "integrity_verification_performed":
                False,

            "store_metadata_versioning_performed":
                False,

            "final_stored_profile_result_built":
                False,

            "full_profile_store_certification_performed":
                False,

            "profile_payload_modified":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "semantic_merge_performed":
                False,

            "cross_document_reasoning_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "conflict_resolution_performed":
                False,

            "uncertainty_reinterpretation_performed":
                False,

            "confidence_recalculation_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,

            "persistence_performed":
                False,
        },

        "persistence_policy":
            "ENVELOPE_ASSEMBLY_ONLY_NO_WRITE",

        "next_stage":
            "profile_write_contract",
    }


# =====================================================================
# PATCH 4.6.19F ? Profile Write Contract
# =====================================================================

class InMemorySemanticArticleProfileStoreAdapter:
    """
    Certification/reference adapter for the Profile Store contract.

    Production storage remains backend-neutral. A future filesystem,
    database, object-store, or AWS adapter can implement the same methods.
    """

    def __init__(self) -> None:
        self._records: dict[str, dict[str, Any]] = {}

    def write(
        self,
        storage_key: str,
        record: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Deterministic idempotent write.

        - First identical write -> CREATED
        - Repeated identical write -> IDEMPOTENT_NOOP
        - Different payload for existing key -> reject
        """

        from copy import deepcopy

        if not isinstance(storage_key, str) or not storage_key:
            raise SemanticArticleProfileStoreError(
                "Adapter storage_key must be a non-empty string."
            )

        if not isinstance(record, dict):
            raise SemanticArticleProfileStoreError(
                "Adapter record must be a dictionary."
            )

        existing = self._records.get(storage_key)

        if existing is None:

            self._records[
                storage_key
            ] = deepcopy(record)

            return {
                "adapter_write_status":
                    "CREATED",

                "record_created":
                    True,

                "idempotent_noop":
                    False,

                "conflict_detected":
                    False,
            }

        if existing == record:

            return {
                "adapter_write_status":
                    "IDEMPOTENT_NOOP",

                "record_created":
                    False,

                "idempotent_noop":
                    True,

                "conflict_detected":
                    False,
            }

        raise SemanticArticleProfileStoreError(
            "Deterministic storage-key conflict: existing record "
            "differs from requested immutable write."
        )

    def read(
        self,
        storage_key: str,
    ) -> dict[str, Any] | None:

        from copy import deepcopy

        record = self._records.get(
            storage_key
        )

        if record is None:
            return None

        return deepcopy(record)

    def record_count(self) -> int:
        return len(self._records)


def write_profile_persistence_envelope_v1(
    persistence_envelope_result: dict[str, Any],
    store_adapter: Any,
) -> dict[str, Any]:
    """
    Execute the canonical 4.6.19 profile write contract.

    F is the first stage allowed to perform persistence.

    The immutable certified profile payload itself is NEVER rewritten.
    The store receives the exact E persistence envelope payload.

    Semantic Memory is not written here.
    Read-back certification belongs to 4.6.19G.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        persistence_envelope_result,
        Mapping,
    ):
        raise SemanticArticleProfileStoreError(
            "persistence_envelope_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.19E lifecycle
    # -------------------------------------------------------------

    required_lifecycle = {
        "schema_version":
            "semantic_article_profile_persistence_envelope_result_v1",

        "version":
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,

        "phase":
            SEMANTIC_ARTICLE_PROFILE_STORE_PHASE,

        "patch":
            "4.6.19E",

        "status":
            "PROFILE_PERSISTENCE_ENVELOPE_ASSEMBLED",

        "persistence_policy":
            "ENVELOPE_ASSEMBLY_ONLY_NO_WRITE",

        "next_stage":
            "profile_write_contract",
    }

    for field, expected in required_lifecycle.items():

        if persistence_envelope_result.get(field) != expected:
            raise SemanticArticleProfileStoreError(
                f"Invalid 4.6.19E lifecycle field: {field}"
            )

    envelope = persistence_envelope_result.get(
        "persistence_envelope"
    )

    storage_identity = persistence_envelope_result.get(
        "storage_identity"
    )

    profile = persistence_envelope_result.get(
        "certified_semantic_article_profile"
    )

    canonical_identity = persistence_envelope_result.get(
        "canonical_article_identity"
    )

    boundaries = persistence_envelope_result.get(
        "processing_boundaries"
    )

    if not isinstance(envelope, Mapping):
        raise SemanticArticleProfileStoreError(
            "Persistence envelope is missing."
        )

    if not isinstance(storage_identity, Mapping):
        raise SemanticArticleProfileStoreError(
            "Storage identity is missing."
        )

    if not isinstance(profile, Mapping):
        raise SemanticArticleProfileStoreError(
            "Certified profile is missing."
        )

    if not isinstance(canonical_identity, Mapping):
        raise SemanticArticleProfileStoreError(
            "Canonical article identity is missing."
        )

    if not isinstance(boundaries, Mapping):
        raise SemanticArticleProfileStoreError(
            "4.6.19E processing boundaries are missing."
        )

    # -------------------------------------------------------------
    # Adapter contract
    # -------------------------------------------------------------

    if store_adapter is None:
        raise SemanticArticleProfileStoreError(
            "A Profile Store adapter is required."
        )

    write_method = getattr(
        store_adapter,
        "write",
        None,
    )

    read_method = getattr(
        store_adapter,
        "read",
        None,
    )

    if not callable(write_method):
        raise SemanticArticleProfileStoreError(
            "Profile Store adapter must implement write()."
        )

    if not callable(read_method):
        raise SemanticArticleProfileStoreError(
            "Profile Store adapter must implement read()."
        )

    # -------------------------------------------------------------
    # Envelope authority
    # -------------------------------------------------------------

    required_envelope = {
        "persistence_envelope_schema":
            "semantic_article_profile_persistence_envelope_v1",

        "persistence_envelope_version":
            "v1",

        "store_schema_version":
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,

        "storage_namespace":
            "linkcraftor.semantic_article_profile_store",

        "profile_schema_version":
            "canonical_semantic_article_profile_v1",

        "profile_payload_hash_algorithm":
            "SHA256",

        "profile_payload_canonicalization":
            "JSON_SORTED_KEYS_COMPACT_UTF8",
    }

    for field, expected in required_envelope.items():

        if envelope.get(field) != expected:
            raise SemanticArticleProfileStoreError(
                f"Persistence envelope field drifted: {field}"
            )

    for field in (
        "payload_immutable",
        "payload_hash_verified",
        "storage_identity_verified",
        "profile_certified",
        "profile_store_ready",
        "write_authorized_for_next_stage",
    ):

        if envelope.get(field) is not True:
            raise SemanticArticleProfileStoreError(
                f"Required envelope field is not True: {field}"
            )

    for field in (
        "profile_persisted_before_write",
        "write_performed",
        "read_back_performed",
        "backend_bound",
        "physical_location_assigned",
        "semantic_memory_written",
    ):

        if envelope.get(field) is not False:
            raise SemanticArticleProfileStoreError(
                f"Forbidden pre-write envelope field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Storage identity consistency
    # -------------------------------------------------------------

    storage_key = storage_identity.get(
        "storage_key"
    )

    if not isinstance(storage_key, str) or not storage_key:
        raise SemanticArticleProfileStoreError(
            "Storage key is missing."
        )

    if envelope.get(
        "storage_key"
    ) != storage_key:
        raise SemanticArticleProfileStoreError(
            "Envelope storage key drifted from storage identity."
        )

    if envelope.get(
        "storage_identity_digest"
    ) != storage_identity.get(
        "identity_digest"
    ):
        raise SemanticArticleProfileStoreError(
            "Envelope identity digest drifted."
        )

    if envelope.get(
        "workspace_id"
    ) != canonical_identity.get(
        "workspace_id"
    ):
        raise SemanticArticleProfileStoreError(
            "Envelope workspace identity drifted."
        )

    if envelope.get(
        "article_id"
    ) != canonical_identity.get(
        "article_id"
    ):
        raise SemanticArticleProfileStoreError(
            "Envelope article identity drifted."
        )

    # -------------------------------------------------------------
    # Recompute immutable payload hash before write
    # -------------------------------------------------------------

    envelope_profile = envelope.get(
        "profile_payload"
    )

    if not isinstance(envelope_profile, Mapping):
        raise SemanticArticleProfileStoreError(
            "Envelope profile payload is missing."
        )

    if envelope_profile != profile:
        raise SemanticArticleProfileStoreError(
            "Envelope profile payload drifted from certified profile."
        )

    canonical_payload_json = json.dumps(
        dict(envelope_profile),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    recalculated_hash = hashlib.sha256(
        canonical_payload_json.encode("utf-8")
    ).hexdigest()

    recalculated_bytes = len(
        canonical_payload_json.encode("utf-8")
    )

    if envelope.get(
        "profile_payload_hash"
    ) != recalculated_hash:
        raise SemanticArticleProfileStoreError(
            "Profile payload hash verification failed before write."
        )

    if envelope.get(
        "profile_payload_byte_length"
    ) != recalculated_bytes:
        raise SemanticArticleProfileStoreError(
            "Profile payload byte-length verification failed."
        )

    # -------------------------------------------------------------
    # Certified profile write eligibility
    # -------------------------------------------------------------

    if profile.get(
        "profile_certified"
    ) is not True:
        raise SemanticArticleProfileStoreError(
            "Profile must be certified before write."
        )

    if profile.get(
        "profile_store_ready"
    ) is not True:
        raise SemanticArticleProfileStoreError(
            "Profile must be store-ready before write."
        )

    if profile.get(
        "profile_persisted"
    ) is not False:
        raise SemanticArticleProfileStoreError(
            "Incoming profile is already marked persisted."
        )

    if profile.get(
        "profile_store_owner"
    ) != "4.6.19_PROFILE_STORE":
        raise SemanticArticleProfileStoreError(
            "Profile Store owner drifted."
        )

    if profile.get(
        "semantic_memory_owner"
    ) != "4.6.28_SEMANTIC_MEMORY":
        raise SemanticArticleProfileStoreError(
            "Semantic Memory owner drifted."
        )

    # -------------------------------------------------------------
    # E boundaries
    # -------------------------------------------------------------

    for field in (
        "architecture_definition_preserved",
        "certified_profile_intake_validation_preserved",
        "storage_identity_preserved",
        "deterministic_storage_key_preserved",
        "profile_payload_hash_generated",
        "profile_payload_hash_verified",
        "persistence_envelope_assembled",
        "write_authorized_for_next_stage",
    ):

        if boundaries.get(field) is not True:
            raise SemanticArticleProfileStoreError(
                f"Required 4.6.19E boundary is not True: {field}"
            )

    for field in (
        "persistence_backend_bound",
        "persistence_location_assigned",
        "profile_write_performed",
        "profile_read_back_performed",
        "integrity_verification_performed",
        "store_metadata_versioning_performed",
        "final_stored_profile_result_built",
        "full_profile_store_certification_performed",
        "profile_payload_modified",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "semantic_merge_performed",
        "cross_document_reasoning_performed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
        "conflict_resolution_performed",
        "uncertainty_reinterpretation_performed",
        "confidence_recalculation_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
        "persistence_performed",
    ):

        if boundaries.get(field) is not False:
            raise SemanticArticleProfileStoreError(
                f"Forbidden 4.6.19E boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Immutable stored record
    #
    # Important:
    # We do NOT change the profile payload's profile_persisted field.
    # That field describes the certified source payload at handoff time.
    #
    # Persistence state is store metadata surrounding the immutable
    # certified payload.
    # -------------------------------------------------------------

    stored_record = {
        "stored_record_schema":
            "semantic_article_profile_stored_record_v1",

        "store_schema_version":
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,

        "storage_namespace":
            envelope[
                "storage_namespace"
            ],

        "storage_key":
            storage_key,

        "storage_identity_digest":
            envelope[
                "storage_identity_digest"
            ],

        "profile_payload_hash":
            recalculated_hash,

        "profile_payload_hash_algorithm":
            "SHA256",

        "profile_payload_byte_length":
            recalculated_bytes,

        "workspace_id":
            envelope[
                "workspace_id"
            ],

        "article_id":
            envelope[
                "article_id"
            ],

        "profile_schema_version":
            envelope[
                "profile_schema_version"
            ],

        "certified_profile_payload":
            deepcopy(
                dict(envelope_profile)
            ),

        "store_state": {
            "profile_write_performed":
                True,

            "persistence_performed":
                True,

            "profile_store_written":
                True,

            "payload_immutable":
                True,

            "payload_hash_verified_before_write":
                True,

            "read_back_verified":
                False,

            "integrity_verified":
                False,

            "store_metadata_versioned":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },
    }

    adapter_result = store_adapter.write(
        storage_key,
        deepcopy(stored_record),
    )

    if not isinstance(adapter_result, Mapping):
        raise SemanticArticleProfileStoreError(
            "Profile Store adapter returned an invalid write result."
        )

    adapter_status = adapter_result.get(
        "adapter_write_status"
    )

    if adapter_status not in (
        "CREATED",
        "IDEMPOTENT_NOOP",
    ):
        raise SemanticArticleProfileStoreError(
            "Profile Store adapter write did not complete successfully."
        )

    if adapter_result.get(
        "conflict_detected"
    ) is not False:
        raise SemanticArticleProfileStoreError(
            "Profile Store adapter reported a write conflict."
        )

    # -------------------------------------------------------------
    # F result
    # -------------------------------------------------------------

    return {
        "schema_version":
            "semantic_article_profile_write_result_v1",

        "version":
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,

        "phase":
            SEMANTIC_ARTICLE_PROFILE_STORE_PHASE,

        "patch":
            "4.6.19F",

        "status":
            "SEMANTIC_ARTICLE_PROFILE_WRITE_COMPLETED",

        "canonical_article_identity":
            deepcopy(
                dict(canonical_identity)
            ),

        "storage_identity":
            deepcopy(
                dict(storage_identity)
            ),

        "persistence_envelope":
            deepcopy(
                dict(envelope)
            ),

        "stored_record":
            deepcopy(
                stored_record
            ),

        "write_receipt": {
            "write_status":
                "PERSISTED",

            "adapter_write_status":
                adapter_status,

            "storage_key":
                storage_key,

            "profile_payload_hash":
                recalculated_hash,

            "profile_write_performed":
                True,

            "persistence_performed":
                True,

            "profile_store_written":
                True,

            "payload_preserved_exactly":
                True,

            "idempotent_write":
                True,

            "record_created":
                adapter_result.get(
                    "record_created"
                )
                is True,

            "idempotent_noop":
                adapter_result.get(
                    "idempotent_noop"
                )
                is True,

            "conflict_detected":
                False,

            "read_back_verification_pending":
                True,

            "integrity_verification_pending":
                True,

            "semantic_memory_written":
                False,
        },

        "certified_semantic_article_profile":
            deepcopy(
                dict(profile)
            ),

        "source_persistence_envelope_result":
            deepcopy(
                dict(persistence_envelope_result)
            ),

        "processing_boundaries": {
            "architecture_definition_preserved":
                True,

            "certified_profile_intake_validation_preserved":
                True,

            "storage_identity_preserved":
                True,

            "persistence_envelope_preserved":
                True,

            "profile_payload_hash_preserved":
                True,

            "profile_write_performed":
                True,

            "profile_store_written":
                True,

            "persistence_performed":
                True,

            "idempotent_write_contract_enforced":
                True,

            "persistence_backend_bound_via_adapter":
                True,

            "profile_read_back_performed":
                False,

            "integrity_verification_performed":
                False,

            "store_metadata_versioning_performed":
                False,

            "final_stored_profile_result_built":
                False,

            "full_profile_store_certification_performed":
                False,

            "profile_payload_modified":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "semantic_merge_performed":
                False,

            "cross_document_reasoning_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "conflict_resolution_performed":
                False,

            "uncertainty_reinterpretation_performed":
                False,

            "confidence_recalculation_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "persistence_policy":
            "PROFILE_STORE_WRITE_COMPLETED",

        "next_stage":
            "read_back_verification",
    }


# =====================================================================
# PATCH 4.6.19G ? Read-Back Verification
# =====================================================================

def verify_profile_store_read_back_v1(
    profile_write_result: dict[str, Any],
    store_adapter: Any,
) -> dict[str, Any]:
    """
    Independently read the persisted Semantic Article Profile record back
    from the Profile Store adapter and verify exact persistence fidelity.

    G performs no write and does not alter the certified profile payload.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(profile_write_result, Mapping):
        raise SemanticArticleProfileStoreError(
            "profile_write_result must be a mapping."
        )

    for field, expected in (
        (
            "schema_version",
            "semantic_article_profile_write_result_v1",
        ),
        (
            "version",
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,
        ),
        (
            "phase",
            SEMANTIC_ARTICLE_PROFILE_STORE_PHASE,
        ),
        (
            "patch",
            "4.6.19F",
        ),
        (
            "status",
            "SEMANTIC_ARTICLE_PROFILE_WRITE_COMPLETED",
        ),
        (
            "persistence_policy",
            "PROFILE_STORE_WRITE_COMPLETED",
        ),
        (
            "next_stage",
            "read_back_verification",
        ),
    ):
        if profile_write_result.get(field) != expected:
            raise SemanticArticleProfileStoreError(
                f"Invalid 4.6.19F lifecycle field: {field}"
            )

    if store_adapter is None:
        raise SemanticArticleProfileStoreError(
            "Profile Store adapter is required for read-back verification."
        )

    read_method = getattr(store_adapter, "read", None)

    if not callable(read_method):
        raise SemanticArticleProfileStoreError(
            "Profile Store adapter must implement read()."
        )

    write_receipt = profile_write_result.get(
        "write_receipt"
    )

    expected_record = profile_write_result.get(
        "stored_record"
    )

    storage_identity = profile_write_result.get(
        "storage_identity"
    )

    profile = profile_write_result.get(
        "certified_semantic_article_profile"
    )

    canonical_identity = profile_write_result.get(
        "canonical_article_identity"
    )

    boundaries = profile_write_result.get(
        "processing_boundaries"
    )

    for name, value in (
        ("write_receipt", write_receipt),
        ("stored_record", expected_record),
        ("storage_identity", storage_identity),
        ("certified_semantic_article_profile", profile),
        ("canonical_article_identity", canonical_identity),
        ("processing_boundaries", boundaries),
    ):
        if not isinstance(value, Mapping):
            raise SemanticArticleProfileStoreError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # F write authority
    # -------------------------------------------------------------

    if write_receipt.get(
        "write_status"
    ) != "PERSISTED":
        raise SemanticArticleProfileStoreError(
            "4.6.19F write receipt is not persisted."
        )

    if write_receipt.get(
        "adapter_write_status"
    ) not in (
        "CREATED",
        "IDEMPOTENT_NOOP",
    ):
        raise SemanticArticleProfileStoreError(
            "4.6.19F adapter write status is invalid."
        )

    for field in (
        "profile_write_performed",
        "persistence_performed",
        "profile_store_written",
        "payload_preserved_exactly",
        "idempotent_write",
        "read_back_verification_pending",
        "integrity_verification_pending",
    ):
        if write_receipt.get(field) is not True:
            raise SemanticArticleProfileStoreError(
                f"Required write-receipt field is not True: {field}"
            )

    if write_receipt.get(
        "conflict_detected"
    ) is not False:
        raise SemanticArticleProfileStoreError(
            "Write receipt reports a persistence conflict."
        )

    if write_receipt.get(
        "semantic_memory_written"
    ) is not False:
        raise SemanticArticleProfileStoreError(
            "Semantic Memory was written prematurely."
        )

    # -------------------------------------------------------------
    # Expected stored-record contract
    # -------------------------------------------------------------

    for field, expected in (
        (
            "stored_record_schema",
            "semantic_article_profile_stored_record_v1",
        ),
        (
            "store_schema_version",
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,
        ),
        (
            "profile_payload_hash_algorithm",
            "SHA256",
        ),
        (
            "profile_schema_version",
            "canonical_semantic_article_profile_v1",
        ),
    ):
        if expected_record.get(field) != expected:
            raise SemanticArticleProfileStoreError(
                f"Expected stored-record field drifted: {field}"
            )

    storage_key = expected_record.get(
        "storage_key"
    )

    if not isinstance(storage_key, str) or not storage_key:
        raise SemanticArticleProfileStoreError(
            "Stored record has no valid storage key."
        )

    if storage_identity.get(
        "storage_key"
    ) != storage_key:
        raise SemanticArticleProfileStoreError(
            "Stored record key disagrees with storage identity."
        )

    if write_receipt.get(
        "storage_key"
    ) != storage_key:
        raise SemanticArticleProfileStoreError(
            "Write receipt key disagrees with stored record."
        )

    expected_payload_hash = expected_record.get(
        "profile_payload_hash"
    )

    if write_receipt.get(
        "profile_payload_hash"
    ) != expected_payload_hash:
        raise SemanticArticleProfileStoreError(
            "Write receipt payload hash drifted."
        )

    store_state = expected_record.get(
        "store_state"
    )

    if not isinstance(store_state, Mapping):
        raise SemanticArticleProfileStoreError(
            "Stored-record state is missing."
        )

    for field in (
        "profile_write_performed",
        "persistence_performed",
        "profile_store_written",
        "payload_immutable",
        "payload_hash_verified_before_write",
    ):
        if store_state.get(field) is not True:
            raise SemanticArticleProfileStoreError(
                f"Required stored-state field is not True: {field}"
            )

    for field in (
        "read_back_verified",
        "integrity_verified",
        "store_metadata_versioned",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):
        if store_state.get(field) is not False:
            raise SemanticArticleProfileStoreError(
                f"Pre-G stored-state field must remain False: {field}"
            )

    # -------------------------------------------------------------
    # Actual independent read
    # -------------------------------------------------------------

    read_back_record = store_adapter.read(
        storage_key
    )

    if not isinstance(read_back_record, Mapping):
        raise SemanticArticleProfileStoreError(
            "Persisted profile record could not be read back."
        )

    # The actual record in storage must exactly equal F's written record.
    if read_back_record != expected_record:
        raise SemanticArticleProfileStoreError(
            "Read-back record differs from 4.6.19F written record."
        )

    read_back_payload = read_back_record.get(
        "certified_profile_payload"
    )

    if not isinstance(read_back_payload, Mapping):
        raise SemanticArticleProfileStoreError(
            "Read-back certified profile payload is missing."
        )

    if read_back_payload != profile:
        raise SemanticArticleProfileStoreError(
            "Read-back profile payload differs from certified source profile."
        )

    if read_back_record.get(
        "workspace_id"
    ) != canonical_identity.get(
        "workspace_id"
    ):
        raise SemanticArticleProfileStoreError(
            "Read-back workspace identity drifted."
        )

    if read_back_record.get(
        "article_id"
    ) != canonical_identity.get(
        "article_id"
    ):
        raise SemanticArticleProfileStoreError(
            "Read-back article identity drifted."
        )

    # -------------------------------------------------------------
    # Independent payload-hash verification
    # -------------------------------------------------------------

    payload_json = json.dumps(
        dict(read_back_payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    recalculated_hash = hashlib.sha256(
        payload_json.encode("utf-8")
    ).hexdigest()

    recalculated_bytes = len(
        payload_json.encode("utf-8")
    )

    if read_back_record.get(
        "profile_payload_hash"
    ) != recalculated_hash:
        raise SemanticArticleProfileStoreError(
            "Read-back profile payload hash verification failed."
        )

    if read_back_record.get(
        "profile_payload_byte_length"
    ) != recalculated_bytes:
        raise SemanticArticleProfileStoreError(
            "Read-back profile payload byte length verification failed."
        )

    if expected_payload_hash != recalculated_hash:
        raise SemanticArticleProfileStoreError(
            "Read-back payload hash differs from F write receipt."
        )

    # -------------------------------------------------------------
    # F boundary contract
    # -------------------------------------------------------------

    for field in (
        "architecture_definition_preserved",
        "certified_profile_intake_validation_preserved",
        "storage_identity_preserved",
        "persistence_envelope_preserved",
        "profile_payload_hash_preserved",
        "profile_write_performed",
        "profile_store_written",
        "persistence_performed",
        "idempotent_write_contract_enforced",
        "persistence_backend_bound_via_adapter",
    ):
        if boundaries.get(field) is not True:
            raise SemanticArticleProfileStoreError(
                f"Required 4.6.19F boundary is not True: {field}"
            )

    for field in (
        "profile_read_back_performed",
        "integrity_verification_performed",
        "store_metadata_versioning_performed",
        "final_stored_profile_result_built",
        "full_profile_store_certification_performed",
        "profile_payload_modified",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "semantic_merge_performed",
        "cross_document_reasoning_performed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
        "conflict_resolution_performed",
        "uncertainty_reinterpretation_performed",
        "confidence_recalculation_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):
        if boundaries.get(field) is not False:
            raise SemanticArticleProfileStoreError(
                f"Forbidden 4.6.19F boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Read-back verification record
    # -------------------------------------------------------------

    verification = {
        "verification_status":
            "VERIFIED",

        "verification_scope":
            "PERSISTED_PROFILE_READ_BACK",

        "storage_key":
            storage_key,

        "storage_record_found":
            True,

        "stored_record_exact_match":
            True,

        "profile_payload_exact_match":
            True,

        "canonical_identity_exact_match":
            True,

        "profile_payload_hash_recalculated":
            True,

        "profile_payload_hash_verified":
            True,

        "profile_payload_byte_length_verified":
            True,

        "profile_payload_immutable":
            True,

        "profile_write_verified":
            True,

        "persistence_verified":
            True,

        "read_back_performed":
            True,

        "integrity_verification_pending":
            True,

        "store_metadata_versioning_pending":
            True,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    return {
        "schema_version":
            "semantic_article_profile_read_back_verification_result_v1",

        "version":
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,

        "phase":
            SEMANTIC_ARTICLE_PROFILE_STORE_PHASE,

        "patch":
            "4.6.19G",

        "status":
            "SEMANTIC_ARTICLE_PROFILE_READ_BACK_VERIFIED",

        "canonical_article_identity":
            deepcopy(
                dict(canonical_identity)
            ),

        "storage_identity":
            deepcopy(
                dict(storage_identity)
            ),

        "write_receipt":
            deepcopy(
                dict(write_receipt)
            ),

        "read_back_verification":
            verification,

        "read_back_stored_record":
            deepcopy(
                dict(read_back_record)
            ),

        "certified_semantic_article_profile":
            deepcopy(
                dict(profile)
            ),

        "source_profile_write_result":
            deepcopy(
                dict(profile_write_result)
            ),

        "processing_boundaries": {
            "architecture_definition_preserved":
                True,

            "certified_profile_intake_validation_preserved":
                True,

            "storage_identity_preserved":
                True,

            "persistence_envelope_preserved":
                True,

            "profile_write_preserved":
                True,

            "profile_store_write_preserved":
                True,

            "persistence_preserved":
                True,

            "profile_read_back_performed":
                True,

            "read_back_record_found":
                True,

            "read_back_record_exact_match_verified":
                True,

            "profile_payload_hash_reverified":
                True,

            "profile_payload_byte_length_reverified":
                True,

            "integrity_verification_performed":
                False,

            "store_metadata_versioning_performed":
                False,

            "final_stored_profile_result_built":
                False,

            "full_profile_store_certification_performed":
                False,

            "profile_payload_modified":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "semantic_merge_performed":
                False,

            "cross_document_reasoning_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "conflict_resolution_performed":
                False,

            "uncertainty_reinterpretation_performed":
                False,

            "confidence_recalculation_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "persistence_policy":
            "READ_BACK_VERIFICATION_COMPLETED",

        "next_stage":
            "integrity_immutability_verification",
    }


# =====================================================================
# PATCH 4.6.19H ? Integrity / Immutability Verification
# =====================================================================

def verify_profile_store_integrity_immutability_v1(
    read_back_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Certify persisted Semantic Article Profile integrity and immutability.

    H performs no write.

    It verifies:
    - exact persisted-record preservation,
    - exact certified-profile preservation,
    - canonical SHA-256 payload integrity,
    - structural identity consistency,
    - immutable semantic/profile sections,
    - separation of persistence metadata from certified payload,
    - no Semantic Memory or linking side effects.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        read_back_result,
        Mapping,
    ):
        raise SemanticArticleProfileStoreError(
            "read_back_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact G lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "semantic_article_profile_read_back_verification_result_v1",
        ),
        (
            "version",
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,
        ),
        (
            "phase",
            SEMANTIC_ARTICLE_PROFILE_STORE_PHASE,
        ),
        (
            "patch",
            "4.6.19G",
        ),
        (
            "status",
            "SEMANTIC_ARTICLE_PROFILE_READ_BACK_VERIFIED",
        ),
        (
            "persistence_policy",
            "READ_BACK_VERIFICATION_COMPLETED",
        ),
        (
            "next_stage",
            "integrity_immutability_verification",
        ),
    ):

        if read_back_result.get(field) != expected:
            raise SemanticArticleProfileStoreError(
                f"Invalid 4.6.19G lifecycle field: {field}"
            )

    verification = read_back_result.get(
        "read_back_verification"
    )

    stored_record = read_back_result.get(
        "read_back_stored_record"
    )

    profile = read_back_result.get(
        "certified_semantic_article_profile"
    )

    storage_identity = read_back_result.get(
        "storage_identity"
    )

    canonical_identity = read_back_result.get(
        "canonical_article_identity"
    )

    write_receipt = read_back_result.get(
        "write_receipt"
    )

    boundaries = read_back_result.get(
        "processing_boundaries"
    )

    source_f = read_back_result.get(
        "source_profile_write_result"
    )

    for name, value in (
        ("read_back_verification", verification),
        ("read_back_stored_record", stored_record),
        ("certified_semantic_article_profile", profile),
        ("storage_identity", storage_identity),
        ("canonical_article_identity", canonical_identity),
        ("write_receipt", write_receipt),
        ("processing_boundaries", boundaries),
        ("source_profile_write_result", source_f),
    ):

        if not isinstance(
            value,
            Mapping,
        ):
            raise SemanticArticleProfileStoreError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # G verification authority
    # -------------------------------------------------------------

    if verification.get(
        "verification_status"
    ) != "VERIFIED":
        raise SemanticArticleProfileStoreError(
            "Read-back verification is not VERIFIED."
        )

    if verification.get(
        "verification_scope"
    ) != "PERSISTED_PROFILE_READ_BACK":
        raise SemanticArticleProfileStoreError(
            "Read-back verification scope drifted."
        )

    for field in (
        "storage_record_found",
        "stored_record_exact_match",
        "profile_payload_exact_match",
        "canonical_identity_exact_match",
        "profile_payload_hash_recalculated",
        "profile_payload_hash_verified",
        "profile_payload_byte_length_verified",
        "profile_payload_immutable",
        "profile_write_verified",
        "persistence_verified",
        "read_back_performed",
        "integrity_verification_pending",
        "store_metadata_versioning_pending",
    ):

        if verification.get(
            field
        ) is not True:
            raise SemanticArticleProfileStoreError(
                f"Required G verification field is not True: {field}"
            )

    for field in (
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if verification.get(
            field
        ) is not False:
            raise SemanticArticleProfileStoreError(
                f"Forbidden G verification field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Stored-record structural contract
    # -------------------------------------------------------------

    for field, expected in (
        (
            "stored_record_schema",
            "semantic_article_profile_stored_record_v1",
        ),
        (
            "store_schema_version",
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,
        ),
        (
            "profile_payload_hash_algorithm",
            "SHA256",
        ),
        (
            "profile_schema_version",
            "canonical_semantic_article_profile_v1",
        ),
    ):

        if stored_record.get(field) != expected:
            raise SemanticArticleProfileStoreError(
                f"Stored-record structural field drifted: {field}"
            )

    stored_payload = stored_record.get(
        "certified_profile_payload"
    )

    store_state = stored_record.get(
        "store_state"
    )

    if not isinstance(
        stored_payload,
        Mapping,
    ):
        raise SemanticArticleProfileStoreError(
            "Stored certified profile payload is missing."
        )

    if not isinstance(
        store_state,
        Mapping,
    ):
        raise SemanticArticleProfileStoreError(
            "Stored record state is missing."
        )

    # -------------------------------------------------------------
    # Exact profile preservation
    # -------------------------------------------------------------

    if stored_payload != profile:
        raise SemanticArticleProfileStoreError(
            "Persisted certified profile differs from certified source."
        )

    required_profile_sections = (
        "profile_identity",
        "source_authority",
        "semantic_layers",
        "semantic_groups",
        "cross_layer_artifacts",
        "governed_state",
        "structural_indexes",
        "certified_source_semantic_representation",
    )

    for section_name in required_profile_sections:

        if section_name not in profile:
            raise SemanticArticleProfileStoreError(
                "Required certified profile section missing: "
                + section_name
            )

        if stored_payload.get(
            section_name
        ) != profile.get(
            section_name
        ):
            raise SemanticArticleProfileStoreError(
                "Stored semantic profile section drifted: "
                + section_name
            )

    if profile.get(
        "profile_section_order"
    ) != list(
        required_profile_sections
    ):
        raise SemanticArticleProfileStoreError(
            "Certified profile section order drifted."
        )

    if profile.get(
        "profile_section_count"
    ) != 8:
        raise SemanticArticleProfileStoreError(
            "Certified profile section count drifted."
        )

    if profile.get(
        "source_layer_count"
    ) != 15:
        raise SemanticArticleProfileStoreError(
            "Certified profile layer count drifted."
        )

    if profile.get(
        "source_group_count"
    ) != 4:
        raise SemanticArticleProfileStoreError(
            "Certified profile group count drifted."
        )

    if profile.get(
        "cross_layer_artifact_count"
    ) != 4:
        raise SemanticArticleProfileStoreError(
            "Certified profile artifact count drifted."
        )

    # -------------------------------------------------------------
    # Certification lifecycle preservation
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

        if profile.get(field) != expected:
            raise SemanticArticleProfileStoreError(
                f"Certified profile lifecycle drifted: {field}"
            )

    for field in (
        "profile_certification_ready",
        "profile_certified",
        "profile_store_ready",
    ):

        if profile.get(field) is not True:
            raise SemanticArticleProfileStoreError(
                f"Required profile field is not True: {field}"
            )

    # Important:
    # This remains False inside the immutable source payload because
    # persistence state is held by the surrounding store record.
    if profile.get(
        "profile_persisted"
    ) is not False:
        raise SemanticArticleProfileStoreError(
            "Certified source payload persistence flag was mutated."
        )

    # -------------------------------------------------------------
    # Canonical identity consistency
    # -------------------------------------------------------------

    if profile.get(
        "profile_identity",
        {}
    ).get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise SemanticArticleProfileStoreError(
            "Profile canonical identity drifted."
        )

    if stored_record.get(
        "workspace_id"
    ) != canonical_identity.get(
        "workspace_id"
    ):
        raise SemanticArticleProfileStoreError(
            "Stored workspace identity drifted."
        )

    if stored_record.get(
        "article_id"
    ) != canonical_identity.get(
        "article_id"
    ):
        raise SemanticArticleProfileStoreError(
            "Stored article identity drifted."
        )

    if storage_identity.get(
        "workspace_id"
    ) != canonical_identity.get(
        "workspace_id"
    ):
        raise SemanticArticleProfileStoreError(
            "Storage identity workspace drifted."
        )

    if storage_identity.get(
        "article_id"
    ) != canonical_identity.get(
        "article_id"
    ):
        raise SemanticArticleProfileStoreError(
            "Storage identity article drifted."
        )

    if stored_record.get(
        "storage_key"
    ) != storage_identity.get(
        "storage_key"
    ):
        raise SemanticArticleProfileStoreError(
            "Stored storage key drifted."
        )

    if stored_record.get(
        "storage_identity_digest"
    ) != storage_identity.get(
        "identity_digest"
    ):
        raise SemanticArticleProfileStoreError(
            "Stored identity digest drifted."
        )

    # -------------------------------------------------------------
    # Cryptographic payload integrity
    # -------------------------------------------------------------

    canonical_payload_json = json.dumps(
        dict(stored_payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    recalculated_hash = hashlib.sha256(
        canonical_payload_json.encode("utf-8")
    ).hexdigest()

    recalculated_length = len(
        canonical_payload_json.encode("utf-8")
    )

    if stored_record.get(
        "profile_payload_hash"
    ) != recalculated_hash:
        raise SemanticArticleProfileStoreError(
            "Stored payload SHA-256 integrity verification failed."
        )

    if stored_record.get(
        "profile_payload_byte_length"
    ) != recalculated_length:
        raise SemanticArticleProfileStoreError(
            "Stored payload byte-length integrity verification failed."
        )

    if write_receipt.get(
        "profile_payload_hash"
    ) != recalculated_hash:
        raise SemanticArticleProfileStoreError(
            "Stored payload hash drifted from F write receipt."
        )

    # -------------------------------------------------------------
    # Store-state integrity
    # -------------------------------------------------------------

    for field in (
        "profile_write_performed",
        "persistence_performed",
        "profile_store_written",
        "payload_immutable",
        "payload_hash_verified_before_write",
    ):

        if store_state.get(field) is not True:
            raise SemanticArticleProfileStoreError(
                f"Required stored state field is not True: {field}"
            )

    for field in (
        "read_back_verified",
        "integrity_verified",
        "store_metadata_versioned",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if store_state.get(field) is not False:
            raise SemanticArticleProfileStoreError(
                f"Stored state field must remain False before H: {field}"
            )

    # -------------------------------------------------------------
    # Confirm persistence metadata is external to certified payload
    # -------------------------------------------------------------

    forbidden_store_metadata_inside_profile = (
        "stored_record_schema",
        "storage_key",
        "storage_identity_digest",
        "profile_payload_hash",
        "profile_payload_hash_algorithm",
        "profile_payload_byte_length",
        "store_state",
        "adapter_write_status",
        "write_receipt",
        "read_back_verification",
    )

    for field in forbidden_store_metadata_inside_profile:

        if field in profile:
            raise SemanticArticleProfileStoreError(
                "Store metadata leaked into immutable certified profile: "
                + field
            )

    # -------------------------------------------------------------
    # G boundaries
    # -------------------------------------------------------------

    for field in (
        "architecture_definition_preserved",
        "certified_profile_intake_validation_preserved",
        "storage_identity_preserved",
        "persistence_envelope_preserved",
        "profile_write_preserved",
        "profile_store_write_preserved",
        "persistence_preserved",
        "profile_read_back_performed",
        "read_back_record_found",
        "read_back_record_exact_match_verified",
        "profile_payload_hash_reverified",
        "profile_payload_byte_length_reverified",
    ):

        if boundaries.get(field) is not True:
            raise SemanticArticleProfileStoreError(
                f"Required G boundary is not True: {field}"
            )

    for field in (
        "integrity_verification_performed",
        "store_metadata_versioning_performed",
        "final_stored_profile_result_built",
        "full_profile_store_certification_performed",
        "profile_payload_modified",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "semantic_merge_performed",
        "cross_document_reasoning_performed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
        "conflict_resolution_performed",
        "uncertainty_reinterpretation_performed",
        "confidence_recalculation_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise SemanticArticleProfileStoreError(
                f"Forbidden G boundary is not False: {field}"
            )

    integrity_certification = {
        "certification_status":
            "CERTIFIED",

        "certification_scope":
            "PERSISTED_SEMANTIC_ARTICLE_PROFILE_INTEGRITY_AND_IMMUTABILITY",

        "certification_mode":
            "EXACT_PAYLOAD_STRUCTURAL_AND_CRYPTOGRAPHIC_PRESERVATION",

        "certification_phase":
            "4.6.19",

        "certification_patch":
            "4.6.19H",

        "stored_record_verified":
            True,

        "storage_identity_verified":
            True,

        "canonical_identity_verified":
            True,

        "profile_payload_verified":
            True,

        "profile_payload_hash_verified":
            True,

        "profile_payload_byte_length_verified":
            True,

        "all_eight_profile_sections_verified":
            True,

        "semantic_layers_preserved":
            True,

        "semantic_groups_preserved":
            True,

        "cross_layer_artifacts_preserved":
            True,

        "governed_state_preserved":
            True,

        "structural_indexes_preserved":
            True,

        "certified_source_representation_preserved":
            True,

        "certification_metadata_preserved":
            True,

        "store_metadata_separated_from_profile_payload":
            True,

        "profile_payload_immutable":
            True,

        "profile_write_verified":
            True,

        "read_back_verified":
            True,

        "persistence_verified":
            True,

        "profile_payload_modified":
            False,

        "semantic_state_modified":
            False,

        "semantic_meaning_rewritten":
            False,

        "semantic_merge_performed":
            False,

        "conflict_resolution_performed":
            False,

        "uncertainty_reinterpretation_performed":
            False,

        "confidence_recalculation_performed":
            False,

        "new_reasoning_performed":
            False,

        "new_fact_inference_performed":
            False,

        "new_relation_inference_performed":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    return {
        "schema_version":
            "semantic_article_profile_integrity_verification_result_v1",

        "version":
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,

        "phase":
            SEMANTIC_ARTICLE_PROFILE_STORE_PHASE,

        "patch":
            "4.6.19H",

        "status":
            "SEMANTIC_ARTICLE_PROFILE_INTEGRITY_VERIFIED",

        "canonical_article_identity":
            deepcopy(
                dict(canonical_identity)
            ),

        "storage_identity":
            deepcopy(
                dict(storage_identity)
            ),

        "integrity_certification":
            integrity_certification,

        "verified_stored_record":
            deepcopy(
                dict(stored_record)
            ),

        "certified_semantic_article_profile":
            deepcopy(
                dict(profile)
            ),

        "source_read_back_result":
            deepcopy(
                dict(read_back_result)
            ),

        "processing_boundaries": {
            "architecture_definition_preserved":
                True,

            "certified_profile_intake_validation_preserved":
                True,

            "storage_identity_preserved":
                True,

            "persistence_envelope_preserved":
                True,

            "profile_write_preserved":
                True,

            "profile_store_write_preserved":
                True,

            "persistence_preserved":
                True,

            "profile_read_back_preserved":
                True,

            "integrity_verification_performed":
                True,

            "immutability_verified":
                True,

            "canonical_identity_verified":
                True,

            "storage_identity_verified":
                True,

            "profile_payload_hash_verified":
                True,

            "profile_payload_byte_length_verified":
                True,

            "all_eight_profile_sections_verified":
                True,

            "store_metadata_profile_separation_verified":
                True,

            "store_metadata_versioning_performed":
                False,

            "final_stored_profile_result_built":
                False,

            "full_profile_store_certification_performed":
                False,

            "profile_payload_modified":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "semantic_merge_performed":
                False,

            "cross_document_reasoning_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "conflict_resolution_performed":
                False,

            "uncertainty_reinterpretation_performed":
                False,

            "confidence_recalculation_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "persistence_policy":
            "PERSISTED_PROFILE_INTEGRITY_CERTIFIED",

        "next_stage":
            "store_metadata_versioning",
    }


# =====================================================================
# PATCH 4.6.19I ? Store Metadata & Versioning
# =====================================================================

def version_profile_store_metadata_v1(
    integrity_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Build and certify the versioned Profile Store metadata record.

    I does NOT rewrite the persisted certified profile payload.

    Store metadata remains logically separate from the immutable profile.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        integrity_result,
        Mapping,
    ):
        raise SemanticArticleProfileStoreError(
            "integrity_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact 4.6.19H lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "semantic_article_profile_integrity_verification_result_v1",
        ),
        (
            "version",
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,
        ),
        (
            "phase",
            SEMANTIC_ARTICLE_PROFILE_STORE_PHASE,
        ),
        (
            "patch",
            "4.6.19H",
        ),
        (
            "status",
            "SEMANTIC_ARTICLE_PROFILE_INTEGRITY_VERIFIED",
        ),
        (
            "persistence_policy",
            "PERSISTED_PROFILE_INTEGRITY_CERTIFIED",
        ),
        (
            "next_stage",
            "store_metadata_versioning",
        ),
    ):

        if integrity_result.get(field) != expected:
            raise SemanticArticleProfileStoreError(
                f"Invalid 4.6.19H lifecycle field: {field}"
            )

    integrity_certification = integrity_result.get(
        "integrity_certification"
    )

    stored_record = integrity_result.get(
        "verified_stored_record"
    )

    profile = integrity_result.get(
        "certified_semantic_article_profile"
    )

    storage_identity = integrity_result.get(
        "storage_identity"
    )

    canonical_identity = integrity_result.get(
        "canonical_article_identity"
    )

    boundaries = integrity_result.get(
        "processing_boundaries"
    )

    for name, value in (
        (
            "integrity_certification",
            integrity_certification,
        ),
        (
            "verified_stored_record",
            stored_record,
        ),
        (
            "certified_semantic_article_profile",
            profile,
        ),
        (
            "storage_identity",
            storage_identity,
        ),
        (
            "canonical_article_identity",
            canonical_identity,
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
            raise SemanticArticleProfileStoreError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # H certification authority
    # -------------------------------------------------------------

    if integrity_certification.get(
        "certification_status"
    ) != "CERTIFIED":
        raise SemanticArticleProfileStoreError(
            "Integrity certification is not CERTIFIED."
        )

    if integrity_certification.get(
        "certification_scope"
    ) != (
        "PERSISTED_SEMANTIC_ARTICLE_PROFILE_INTEGRITY_AND_IMMUTABILITY"
    ):
        raise SemanticArticleProfileStoreError(
            "Integrity certification scope drifted."
        )

    if integrity_certification.get(
        "certification_mode"
    ) != (
        "EXACT_PAYLOAD_STRUCTURAL_AND_CRYPTOGRAPHIC_PRESERVATION"
    ):
        raise SemanticArticleProfileStoreError(
            "Integrity certification mode drifted."
        )

    for field in (
        "stored_record_verified",
        "storage_identity_verified",
        "canonical_identity_verified",
        "profile_payload_verified",
        "profile_payload_hash_verified",
        "profile_payload_byte_length_verified",
        "all_eight_profile_sections_verified",
        "semantic_layers_preserved",
        "semantic_groups_preserved",
        "cross_layer_artifacts_preserved",
        "governed_state_preserved",
        "structural_indexes_preserved",
        "certified_source_representation_preserved",
        "certification_metadata_preserved",
        "store_metadata_separated_from_profile_payload",
        "profile_payload_immutable",
        "profile_write_verified",
        "read_back_verified",
        "persistence_verified",
    ):

        if integrity_certification.get(
            field
        ) is not True:
            raise SemanticArticleProfileStoreError(
                f"Required H certification field is not True: {field}"
            )

    for field in (
        "profile_payload_modified",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "semantic_merge_performed",
        "conflict_resolution_performed",
        "uncertainty_reinterpretation_performed",
        "confidence_recalculation_performed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if integrity_certification.get(
            field
        ) is not False:
            raise SemanticArticleProfileStoreError(
                f"Forbidden H certification field is not False: {field}"
            )

    # -------------------------------------------------------------
    # H processing-boundary authority
    # -------------------------------------------------------------

    for field in (
        "architecture_definition_preserved",
        "certified_profile_intake_validation_preserved",
        "storage_identity_preserved",
        "persistence_envelope_preserved",
        "profile_write_preserved",
        "profile_store_write_preserved",
        "persistence_preserved",
        "profile_read_back_preserved",
        "integrity_verification_performed",
        "immutability_verified",
        "canonical_identity_verified",
        "storage_identity_verified",
        "profile_payload_hash_verified",
        "profile_payload_byte_length_verified",
        "all_eight_profile_sections_verified",
        "store_metadata_profile_separation_verified",
    ):

        if boundaries.get(field) is not True:
            raise SemanticArticleProfileStoreError(
                f"Required 4.6.19H boundary is not True: {field}"
            )

    for field in (
        "store_metadata_versioning_performed",
        "final_stored_profile_result_built",
        "full_profile_store_certification_performed",
        "profile_payload_modified",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "semantic_merge_performed",
        "cross_document_reasoning_performed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
        "conflict_resolution_performed",
        "uncertainty_reinterpretation_performed",
        "confidence_recalculation_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise SemanticArticleProfileStoreError(
                f"Forbidden 4.6.19H boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Stored-record authority
    # -------------------------------------------------------------

    for field, expected in (
        (
            "stored_record_schema",
            "semantic_article_profile_stored_record_v1",
        ),
        (
            "store_schema_version",
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,
        ),
        (
            "profile_payload_hash_algorithm",
            "SHA256",
        ),
        (
            "profile_schema_version",
            "canonical_semantic_article_profile_v1",
        ),
    ):

        if stored_record.get(
            field
        ) != expected:
            raise SemanticArticleProfileStoreError(
                f"Stored record field drifted: {field}"
            )

    stored_payload = stored_record.get(
        "certified_profile_payload"
    )

    if not isinstance(
        stored_payload,
        Mapping,
    ):
        raise SemanticArticleProfileStoreError(
            "Stored certified profile payload is missing."
        )

    if stored_payload != profile:
        raise SemanticArticleProfileStoreError(
            "Stored payload drifted from certified profile."
        )

    if stored_record.get(
        "storage_key"
    ) != storage_identity.get(
        "storage_key"
    ):
        raise SemanticArticleProfileStoreError(
            "Stored record key drifted."
        )

    if stored_record.get(
        "storage_identity_digest"
    ) != storage_identity.get(
        "identity_digest"
    ):
        raise SemanticArticleProfileStoreError(
            "Stored identity digest drifted."
        )

    if stored_record.get(
        "workspace_id"
    ) != canonical_identity.get(
        "workspace_id"
    ):
        raise SemanticArticleProfileStoreError(
            "Stored workspace identity drifted."
        )

    if stored_record.get(
        "article_id"
    ) != canonical_identity.get(
        "article_id"
    ):
        raise SemanticArticleProfileStoreError(
            "Stored article identity drifted."
        )

    # -------------------------------------------------------------
    # Reverify payload hash before metadata versioning
    # -------------------------------------------------------------

    canonical_payload_json = json.dumps(
        dict(profile),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    payload_hash = hashlib.sha256(
        canonical_payload_json.encode(
            "utf-8"
        )
    ).hexdigest()

    payload_bytes = len(
        canonical_payload_json.encode(
            "utf-8"
        )
    )

    if stored_record.get(
        "profile_payload_hash"
    ) != payload_hash:
        raise SemanticArticleProfileStoreError(
            "Payload hash drifted before metadata versioning."
        )

    if stored_record.get(
        "profile_payload_byte_length"
    ) != payload_bytes:
        raise SemanticArticleProfileStoreError(
            "Payload byte length drifted before metadata versioning."
        )

    # -------------------------------------------------------------
    # Version identity
    # -------------------------------------------------------------

    store_record_version = 1

    version_identity_material = {
        "storage_namespace":
            storage_identity.get(
                "storage_namespace"
            ),

        "storage_key":
            storage_identity.get(
                "storage_key"
            ),

        "storage_identity_digest":
            storage_identity.get(
                "identity_digest"
            ),

        "profile_payload_hash":
            payload_hash,

        "store_record_version":
            store_record_version,

        "store_schema_version":
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,
    }

    version_identity_json = json.dumps(
        version_identity_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    version_digest = hashlib.sha256(
        version_identity_json.encode(
            "utf-8"
        )
    ).hexdigest()

    version_id = (
        "sapver:v1:"
        + version_digest[:32]
    )

    # -------------------------------------------------------------
    # Versioned store metadata
    # -------------------------------------------------------------

    store_metadata = {
        "store_metadata_schema":
            "semantic_article_profile_store_metadata_v1",

        "store_metadata_version":
            "v1",

        "store_schema_version":
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,

        "storage_namespace":
            storage_identity[
                "storage_namespace"
            ],

        "storage_key":
            storage_identity[
                "storage_key"
            ],

        "workspace_id":
            canonical_identity[
                "workspace_id"
            ],

        "article_id":
            canonical_identity[
                "article_id"
            ],

        "profile_schema_version":
            profile[
                "profile_schema_version"
            ],

        "profile_payload_hash":
            payload_hash,

        "profile_payload_hash_algorithm":
            "SHA256",

        "profile_payload_byte_length":
            payload_bytes,

        "storage_identity_digest":
            storage_identity[
                "identity_digest"
            ],

        "store_record_version":
            store_record_version,

        "store_record_version_id":
            version_id,

        "store_record_version_digest":
            version_digest,

        "version_digest_algorithm":
            "SHA256",

        "version_material_canonicalization":
            "JSON_SORTED_KEYS_COMPACT_UTF8",

        "previous_store_record_version":
            None,

        "previous_store_record_version_id":
            None,

        "is_initial_store_version":
            True,

        "is_current_store_version":
            True,

        "superseded":
            False,

        "profile_payload_immutable":
            True,

        "payload_integrity_certified":
            True,

        "read_back_verified":
            True,

        "persistence_verified":
            True,

        "metadata_separate_from_profile_payload":
            True,

        "future_revision_policy":
            "NEW_VERSION_METADATA_REQUIRED",

        "same_payload_duplicate_policy":
            "IDEMPOTENT_NO_NEW_PROFILE_VERSION",

        "changed_payload_policy":
            "REQUIRES_NEW_CERTIFIED_PROFILE_AND_NEW_STORE_VERSION",

        "profile_store_owner":
            "4.6.19_PROFILE_STORE",

        "semantic_memory_owner":
            "4.6.28_SEMANTIC_MEMORY",

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    metadata_certification = {
        "certification_status":
            "CERTIFIED",

        "certification_scope":
            "SEMANTIC_ARTICLE_PROFILE_STORE_METADATA_AND_VERSIONING",

        "certification_mode":
            "DETERMINISTIC_VERSIONED_METADATA_CERTIFICATION",

        "certification_phase":
            "4.6.19",

        "certification_patch":
            "4.6.19I",

        "storage_identity_preserved":
            True,

        "payload_hash_preserved":
            True,

        "payload_byte_length_preserved":
            True,

        "initial_version_assigned":
            True,

        "store_record_version":
            1,

        "version_identity_deterministic":
            True,

        "metadata_separate_from_profile_payload":
            True,

        "profile_payload_immutable":
            True,

        "profile_payload_modified":
            False,

        "profile_recertification_performed":
            False,

        "profile_rewrite_performed":
            False,

        "semantic_state_modified":
            False,

        "semantic_meaning_rewritten":
            False,

        "new_reasoning_performed":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,

        "physical_profile_rewrite_performed":
            False,
    }

    return {
        "schema_version":
            "semantic_article_profile_store_metadata_result_v1",

        "version":
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,

        "phase":
            SEMANTIC_ARTICLE_PROFILE_STORE_PHASE,

        "patch":
            "4.6.19I",

        "status":
            "SEMANTIC_ARTICLE_PROFILE_STORE_METADATA_VERSIONED",

        "canonical_article_identity":
            deepcopy(
                dict(canonical_identity)
            ),

        "storage_identity":
            deepcopy(
                dict(storage_identity)
            ),

        "store_metadata":
            store_metadata,

        "metadata_certification":
            metadata_certification,

        "verified_stored_record":
            deepcopy(
                dict(stored_record)
            ),

        "certified_semantic_article_profile":
            deepcopy(
                dict(profile)
            ),

        "source_integrity_result":
            deepcopy(
                dict(integrity_result)
            ),

        "processing_boundaries": {
            "architecture_definition_preserved":
                True,

            "certified_profile_intake_validation_preserved":
                True,

            "storage_identity_preserved":
                True,

            "persistence_envelope_preserved":
                True,

            "profile_write_preserved":
                True,

            "profile_store_write_preserved":
                True,

            "persistence_preserved":
                True,

            "profile_read_back_preserved":
                True,

            "integrity_verification_preserved":
                True,

            "store_metadata_versioning_performed":
                True,

            "deterministic_store_version_assigned":
                True,

            "store_metadata_profile_separation_preserved":
                True,

            "profile_payload_immutability_preserved":
                True,

            "final_stored_profile_result_built":
                False,

            "full_profile_store_certification_performed":
                False,

            "profile_payload_modified":
                False,

            "physical_profile_rewrite_performed":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "semantic_merge_performed":
                False,

            "cross_document_reasoning_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "conflict_resolution_performed":
                False,

            "uncertainty_reinterpretation_performed":
                False,

            "confidence_recalculation_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "persistence_policy":
            "VERSIONED_STORE_METADATA_CERTIFIED",

        "next_stage":
            "final_stored_semantic_article_profile_result",
    }


# =====================================================================
# PATCH 4.6.19J ? Final Stored Semantic Article Profile Result
# =====================================================================

def build_final_stored_semantic_article_profile_result_v1(
    metadata_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Assemble the final stored Semantic Article Profile result.

    J performs no new physical write.

    The certified Semantic Article Profile remains immutable.
    Persistence state is expressed by the surrounding Profile Store result.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        metadata_result,
        Mapping,
    ):
        raise SemanticArticleProfileStoreError(
            "metadata_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact I lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "semantic_article_profile_store_metadata_result_v1",
        ),
        (
            "version",
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,
        ),
        (
            "phase",
            SEMANTIC_ARTICLE_PROFILE_STORE_PHASE,
        ),
        (
            "patch",
            "4.6.19I",
        ),
        (
            "status",
            "SEMANTIC_ARTICLE_PROFILE_STORE_METADATA_VERSIONED",
        ),
        (
            "persistence_policy",
            "VERSIONED_STORE_METADATA_CERTIFIED",
        ),
        (
            "next_stage",
            "final_stored_semantic_article_profile_result",
        ),
    ):

        if metadata_result.get(field) != expected:
            raise SemanticArticleProfileStoreError(
                f"Invalid 4.6.19I lifecycle field: {field}"
            )

    metadata = metadata_result.get(
        "store_metadata"
    )

    metadata_certification = metadata_result.get(
        "metadata_certification"
    )

    stored_record = metadata_result.get(
        "verified_stored_record"
    )

    profile = metadata_result.get(
        "certified_semantic_article_profile"
    )

    storage_identity = metadata_result.get(
        "storage_identity"
    )

    canonical_identity = metadata_result.get(
        "canonical_article_identity"
    )

    boundaries = metadata_result.get(
        "processing_boundaries"
    )

    for name, value in (
        ("store_metadata", metadata),
        ("metadata_certification", metadata_certification),
        ("verified_stored_record", stored_record),
        ("certified_semantic_article_profile", profile),
        ("storage_identity", storage_identity),
        ("canonical_article_identity", canonical_identity),
        ("processing_boundaries", boundaries),
    ):

        if not isinstance(value, Mapping):
            raise SemanticArticleProfileStoreError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # I metadata-certification authority
    # -------------------------------------------------------------

    if metadata_certification.get(
        "certification_status"
    ) != "CERTIFIED":
        raise SemanticArticleProfileStoreError(
            "Store metadata is not certified."
        )

    if metadata_certification.get(
        "certification_scope"
    ) != (
        "SEMANTIC_ARTICLE_PROFILE_STORE_METADATA_AND_VERSIONING"
    ):
        raise SemanticArticleProfileStoreError(
            "Store metadata certification scope drifted."
        )

    if metadata_certification.get(
        "certification_mode"
    ) != (
        "DETERMINISTIC_VERSIONED_METADATA_CERTIFICATION"
    ):
        raise SemanticArticleProfileStoreError(
            "Store metadata certification mode drifted."
        )

    if metadata_certification.get(
        "store_record_version"
    ) != 1:
        raise SemanticArticleProfileStoreError(
            "Initial store record version must be 1."
        )

    for field in (
        "storage_identity_preserved",
        "payload_hash_preserved",
        "payload_byte_length_preserved",
        "initial_version_assigned",
        "version_identity_deterministic",
        "metadata_separate_from_profile_payload",
        "profile_payload_immutable",
    ):

        if metadata_certification.get(field) is not True:
            raise SemanticArticleProfileStoreError(
                f"Required I certification field is not True: {field}"
            )

    for field in (
        "profile_payload_modified",
        "profile_recertification_performed",
        "profile_rewrite_performed",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "new_reasoning_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
        "physical_profile_rewrite_performed",
    ):

        if metadata_certification.get(field) is not False:
            raise SemanticArticleProfileStoreError(
                f"Forbidden I certification field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Metadata authority
    # -------------------------------------------------------------

    for field, expected in (
        (
            "store_metadata_schema",
            "semantic_article_profile_store_metadata_v1",
        ),
        (
            "store_metadata_version",
            "v1",
        ),
        (
            "store_schema_version",
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,
        ),
        (
            "storage_namespace",
            "linkcraftor.semantic_article_profile_store",
        ),
        (
            "profile_schema_version",
            "canonical_semantic_article_profile_v1",
        ),
        (
            "profile_payload_hash_algorithm",
            "SHA256",
        ),
        (
            "store_record_version",
            1,
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

        if metadata.get(field) != expected:
            raise SemanticArticleProfileStoreError(
                f"Store metadata field drifted: {field}"
            )

    for field in (
        "is_initial_store_version",
        "is_current_store_version",
        "profile_payload_immutable",
        "payload_integrity_certified",
        "read_back_verified",
        "persistence_verified",
        "metadata_separate_from_profile_payload",
    ):

        if metadata.get(field) is not True:
            raise SemanticArticleProfileStoreError(
                f"Required metadata field is not True: {field}"
            )

    for field in (
        "superseded",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if metadata.get(field) is not False:
            raise SemanticArticleProfileStoreError(
                f"Forbidden metadata field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Stored record / profile consistency
    # -------------------------------------------------------------

    stored_payload = stored_record.get(
        "certified_profile_payload"
    )

    if not isinstance(stored_payload, Mapping):
        raise SemanticArticleProfileStoreError(
            "Stored certified profile payload is missing."
        )

    if stored_payload != profile:
        raise SemanticArticleProfileStoreError(
            "Stored certified profile differs from source profile."
        )

    if metadata.get(
        "storage_key"
    ) != stored_record.get(
        "storage_key"
    ):
        raise SemanticArticleProfileStoreError(
            "Metadata storage key drifted from stored record."
        )

    if metadata.get(
        "storage_key"
    ) != storage_identity.get(
        "storage_key"
    ):
        raise SemanticArticleProfileStoreError(
            "Metadata storage key drifted from storage identity."
        )

    if metadata.get(
        "storage_identity_digest"
    ) != stored_record.get(
        "storage_identity_digest"
    ):
        raise SemanticArticleProfileStoreError(
            "Metadata identity digest drifted."
        )

    if metadata.get(
        "workspace_id"
    ) != canonical_identity.get(
        "workspace_id"
    ):
        raise SemanticArticleProfileStoreError(
            "Metadata workspace identity drifted."
        )

    if metadata.get(
        "article_id"
    ) != canonical_identity.get(
        "article_id"
    ):
        raise SemanticArticleProfileStoreError(
            "Metadata article identity drifted."
        )

    # -------------------------------------------------------------
    # Payload integrity
    # -------------------------------------------------------------

    payload_json = json.dumps(
        dict(profile),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    payload_hash = hashlib.sha256(
        payload_json.encode("utf-8")
    ).hexdigest()

    payload_bytes = len(
        payload_json.encode("utf-8")
    )

    if metadata.get(
        "profile_payload_hash"
    ) != payload_hash:
        raise SemanticArticleProfileStoreError(
            "Metadata payload hash drifted."
        )

    if stored_record.get(
        "profile_payload_hash"
    ) != payload_hash:
        raise SemanticArticleProfileStoreError(
            "Stored-record payload hash drifted."
        )

    if metadata.get(
        "profile_payload_byte_length"
    ) != payload_bytes:
        raise SemanticArticleProfileStoreError(
            "Metadata payload byte length drifted."
        )

    if stored_record.get(
        "profile_payload_byte_length"
    ) != payload_bytes:
        raise SemanticArticleProfileStoreError(
            "Stored-record payload byte length drifted."
        )

    # -------------------------------------------------------------
    # Version identity verification
    # -------------------------------------------------------------

    version_material = {
        "storage_namespace":
            metadata[
                "storage_namespace"
            ],

        "storage_key":
            metadata[
                "storage_key"
            ],

        "storage_identity_digest":
            metadata[
                "storage_identity_digest"
            ],

        "profile_payload_hash":
            payload_hash,

        "store_record_version":
            1,

        "store_schema_version":
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,
    }

    version_json = json.dumps(
        version_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    version_digest = hashlib.sha256(
        version_json.encode("utf-8")
    ).hexdigest()

    if metadata.get(
        "store_record_version_digest"
    ) != version_digest:
        raise SemanticArticleProfileStoreError(
            "Store record version digest drifted."
        )

    if metadata.get(
        "store_record_version_id"
    ) != (
        "sapver:v1:"
        + version_digest[:32]
    ):
        raise SemanticArticleProfileStoreError(
            "Store record version ID drifted."
        )

    # -------------------------------------------------------------
    # Immutable certified profile lifecycle
    # -------------------------------------------------------------

    if profile.get(
        "profile_certified"
    ) is not True:
        raise SemanticArticleProfileStoreError(
            "Stored source profile is not certified."
        )

    if profile.get(
        "profile_store_ready"
    ) is not True:
        raise SemanticArticleProfileStoreError(
            "Stored source profile is not store-ready."
        )

    # Intentionally remains False in immutable certified source profile.
    if profile.get(
        "profile_persisted"
    ) is not False:
        raise SemanticArticleProfileStoreError(
            "Certified profile payload persistence flag was mutated."
        )

    if profile.get(
        "profile_store_owner"
    ) != "4.6.19_PROFILE_STORE":
        raise SemanticArticleProfileStoreError(
            "Profile Store owner drifted."
        )

    if profile.get(
        "semantic_memory_owner"
    ) != "4.6.28_SEMANTIC_MEMORY":
        raise SemanticArticleProfileStoreError(
            "Semantic Memory owner drifted."
        )

    # -------------------------------------------------------------
    # I processing-boundary authority
    # -------------------------------------------------------------

    for field in (
        "architecture_definition_preserved",
        "certified_profile_intake_validation_preserved",
        "storage_identity_preserved",
        "persistence_envelope_preserved",
        "profile_write_preserved",
        "profile_store_write_preserved",
        "persistence_preserved",
        "profile_read_back_preserved",
        "integrity_verification_preserved",
        "store_metadata_versioning_performed",
        "deterministic_store_version_assigned",
        "store_metadata_profile_separation_preserved",
        "profile_payload_immutability_preserved",
    ):

        if boundaries.get(field) is not True:
            raise SemanticArticleProfileStoreError(
                f"Required 4.6.19I boundary is not True: {field}"
            )

    for field in (
        "final_stored_profile_result_built",
        "full_profile_store_certification_performed",
        "profile_payload_modified",
        "physical_profile_rewrite_performed",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "semantic_merge_performed",
        "cross_document_reasoning_performed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
        "conflict_resolution_performed",
        "uncertainty_reinterpretation_performed",
        "confidence_recalculation_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise SemanticArticleProfileStoreError(
                f"Forbidden 4.6.19I boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Final store-owned persisted profile wrapper
    #
    # Certified profile remains untouched.
    # This wrapper owns persistence lifecycle.
    # -------------------------------------------------------------

    stored_semantic_article_profile = {
        "stored_profile_schema":
            "stored_semantic_article_profile_v1",

        "store_schema_version":
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,

        "storage_namespace":
            metadata[
                "storage_namespace"
            ],

        "storage_key":
            metadata[
                "storage_key"
            ],

        "store_record_version":
            metadata[
                "store_record_version"
            ],

        "store_record_version_id":
            metadata[
                "store_record_version_id"
            ],

        "store_record_version_digest":
            metadata[
                "store_record_version_digest"
            ],

        "canonical_article_identity":
            deepcopy(
                dict(canonical_identity)
            ),

        "profile_schema_version":
            profile[
                "profile_schema_version"
            ],

        "profile_payload_hash":
            payload_hash,

        "profile_payload_hash_algorithm":
            "SHA256",

        "profile_payload_byte_length":
            payload_bytes,

        "certified_profile_payload":
            deepcopy(
                dict(profile)
            ),

        "store_status":
            "PERSISTED",

        "profile_store_written":
            True,

        "profile_persistence_verified":
            True,

        "profile_read_back_verified":
            True,

        "profile_integrity_verified":
            True,

        "profile_immutability_verified":
            True,

        "store_metadata_versioned":
            True,

        "profile_payload_immutable":
            True,

        "metadata_separate_from_profile_payload":
            True,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    final_summary = {
        "final_status":
            "STORED_SEMANTIC_ARTICLE_PROFILE_READY",

        "profile_certified":
            True,

        "profile_persisted_in_profile_store":
            True,

        "source_profile_payload_mutated":
            False,

        "profile_store_written":
            True,

        "read_back_verified":
            True,

        "integrity_verified":
            True,

        "immutability_verified":
            True,

        "metadata_versioned":
            True,

        "store_record_version":
            1,

        "semantic_memory_written":
            False,

        "semantic_memory_owner":
            "4.6.28_SEMANTIC_MEMORY",

        "knowledge_retrieval_next_owner":
            "4.6.20_KNOWLEDGE_RETRIEVAL",

        "linking_decisions_performed":
            False,
    }

    return {
        "schema_version":
            "final_stored_semantic_article_profile_result_v1",

        "version":
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,

        "phase":
            SEMANTIC_ARTICLE_PROFILE_STORE_PHASE,

        "patch":
            "4.6.19J",

        "status":
            "STORED_SEMANTIC_ARTICLE_PROFILE_READY",

        "canonical_article_identity":
            deepcopy(
                dict(canonical_identity)
            ),

        "storage_identity":
            deepcopy(
                dict(storage_identity)
            ),

        "store_metadata":
            deepcopy(
                dict(metadata)
            ),

        "stored_semantic_article_profile":
            stored_semantic_article_profile,

        "certified_semantic_article_profile":
            deepcopy(
                dict(profile)
            ),

        "verified_stored_record":
            deepcopy(
                dict(stored_record)
            ),

        "metadata_certification":
            deepcopy(
                dict(metadata_certification)
            ),

        "final_result_summary":
            final_summary,

        "source_store_metadata_result":
            deepcopy(
                dict(metadata_result)
            ),

        "processing_boundaries": {
            "architecture_definition_preserved":
                True,

            "certified_profile_intake_validation_preserved":
                True,

            "storage_identity_preserved":
                True,

            "persistence_envelope_preserved":
                True,

            "profile_write_preserved":
                True,

            "profile_store_write_preserved":
                True,

            "persistence_preserved":
                True,

            "profile_read_back_preserved":
                True,

            "integrity_verification_preserved":
                True,

            "store_metadata_versioning_preserved":
                True,

            "final_stored_profile_result_built":
                True,

            "stored_profile_wrapper_created":
                True,

            "store_persistence_state_expressed":
                True,

            "profile_payload_immutability_preserved":
                True,

            "store_metadata_profile_separation_preserved":
                True,

            "full_profile_store_certification_performed":
                False,

            "additional_profile_write_performed":
                False,

            "profile_payload_modified":
                False,

            "physical_profile_rewrite_performed":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "semantic_merge_performed":
                False,

            "cross_document_reasoning_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "conflict_resolution_performed":
                False,

            "uncertainty_reinterpretation_performed":
                False,

            "confidence_recalculation_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "persistence_policy":
            "PROFILE_STORE_PERSISTED_RESULT_READY",

        "next_stage":
            "full_profile_store_hard_certification",
    }


# =====================================================================
# PATCH 4.6.19K ? Full Profile Store Hard Certification
# =====================================================================

def certify_semantic_article_profile_store_v1(
    final_store_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Hard-certify the complete 4.6.19 Semantic Article Profile Store.

    K certifies that the profile:
    - originated from the certified profile pipeline,
    - received deterministic storage identity,
    - received immutable persistence envelope,
    - was persisted through the write contract,
    - was read back exactly,
    - passed integrity/immutability verification,
    - received deterministic versioned store metadata,
    - reached the final stored-profile result,
    while preserving the certified profile payload exactly.

    K performs no new physical write.
    """

    from collections.abc import Mapping
    from copy import deepcopy
    import hashlib
    import json

    if not isinstance(
        final_store_result,
        Mapping,
    ):
        raise SemanticArticleProfileStoreError(
            "final_store_result must be a mapping."
        )

    # -------------------------------------------------------------
    # Exact J lifecycle
    # -------------------------------------------------------------

    for field, expected in (
        (
            "schema_version",
            "final_stored_semantic_article_profile_result_v1",
        ),
        (
            "version",
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,
        ),
        (
            "phase",
            SEMANTIC_ARTICLE_PROFILE_STORE_PHASE,
        ),
        (
            "patch",
            "4.6.19J",
        ),
        (
            "status",
            "STORED_SEMANTIC_ARTICLE_PROFILE_READY",
        ),
        (
            "persistence_policy",
            "PROFILE_STORE_PERSISTED_RESULT_READY",
        ),
        (
            "next_stage",
            "full_profile_store_hard_certification",
        ),
    ):

        if final_store_result.get(field) != expected:
            raise SemanticArticleProfileStoreError(
                f"Invalid 4.6.19J lifecycle field: {field}"
            )

    stored_profile = final_store_result.get(
        "stored_semantic_article_profile"
    )

    profile = final_store_result.get(
        "certified_semantic_article_profile"
    )

    metadata = final_store_result.get(
        "store_metadata"
    )

    stored_record = final_store_result.get(
        "verified_stored_record"
    )

    metadata_certification = final_store_result.get(
        "metadata_certification"
    )

    storage_identity = final_store_result.get(
        "storage_identity"
    )

    canonical_identity = final_store_result.get(
        "canonical_article_identity"
    )

    summary = final_store_result.get(
        "final_result_summary"
    )

    boundaries = final_store_result.get(
        "processing_boundaries"
    )

    for name, value in (
        ("stored_semantic_article_profile", stored_profile),
        ("certified_semantic_article_profile", profile),
        ("store_metadata", metadata),
        ("verified_stored_record", stored_record),
        ("metadata_certification", metadata_certification),
        ("storage_identity", storage_identity),
        ("canonical_article_identity", canonical_identity),
        ("final_result_summary", summary),
        ("processing_boundaries", boundaries),
    ):

        if not isinstance(value, Mapping):
            raise SemanticArticleProfileStoreError(
                name + " is missing."
            )

    # -------------------------------------------------------------
    # J final wrapper authority
    # -------------------------------------------------------------

    for field, expected in (
        (
            "stored_profile_schema",
            "stored_semantic_article_profile_v1",
        ),
        (
            "store_schema_version",
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,
        ),
        (
            "store_status",
            "PERSISTED",
        ),
        (
            "profile_payload_hash_algorithm",
            "SHA256",
        ),
        (
            "store_record_version",
            1,
        ),
    ):

        if stored_profile.get(field) != expected:
            raise SemanticArticleProfileStoreError(
                f"Final stored profile field drifted: {field}"
            )

    for field in (
        "profile_store_written",
        "profile_persistence_verified",
        "profile_read_back_verified",
        "profile_integrity_verified",
        "profile_immutability_verified",
        "store_metadata_versioned",
        "profile_payload_immutable",
        "metadata_separate_from_profile_payload",
    ):

        if stored_profile.get(field) is not True:
            raise SemanticArticleProfileStoreError(
                f"Required stored-profile field is not True: {field}"
            )

    for field in (
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if stored_profile.get(field) is not False:
            raise SemanticArticleProfileStoreError(
                f"Forbidden stored-profile field is not False: {field}"
            )

    # -------------------------------------------------------------
    # Certified profile preservation
    # -------------------------------------------------------------

    stored_payload = stored_profile.get(
        "certified_profile_payload"
    )

    if not isinstance(stored_payload, Mapping):
        raise SemanticArticleProfileStoreError(
            "Stored certified profile payload is missing."
        )

    if stored_payload != profile:
        raise SemanticArticleProfileStoreError(
            "Stored payload differs from certified profile."
        )

    if stored_record.get(
        "certified_profile_payload"
    ) != profile:
        raise SemanticArticleProfileStoreError(
            "Verified stored-record payload drifted."
        )

    if profile.get(
        "profile_certified"
    ) is not True:
        raise SemanticArticleProfileStoreError(
            "Certified profile is not certified."
        )

    if profile.get(
        "profile_store_ready"
    ) is not True:
        raise SemanticArticleProfileStoreError(
            "Certified profile is not store-ready."
        )

    # Immutable 4.6.18 source payload remains unchanged.
    if profile.get(
        "profile_persisted"
    ) is not False:
        raise SemanticArticleProfileStoreError(
            "Certified source profile payload was mutated."
        )

    if profile.get(
        "profile_store_owner"
    ) != "4.6.19_PROFILE_STORE":
        raise SemanticArticleProfileStoreError(
            "Profile Store ownership drifted."
        )

    if profile.get(
        "semantic_memory_owner"
    ) != "4.6.28_SEMANTIC_MEMORY":
        raise SemanticArticleProfileStoreError(
            "Semantic Memory ownership drifted."
        )

    # -------------------------------------------------------------
    # Canonical identity
    # -------------------------------------------------------------

    if profile.get(
        "profile_identity",
        {}
    ).get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise SemanticArticleProfileStoreError(
            "Profile canonical identity drifted."
        )

    if stored_profile.get(
        "canonical_article_identity"
    ) != canonical_identity:
        raise SemanticArticleProfileStoreError(
            "Stored-profile canonical identity drifted."
        )

    if metadata.get(
        "workspace_id"
    ) != canonical_identity.get(
        "workspace_id"
    ):
        raise SemanticArticleProfileStoreError(
            "Metadata workspace identity drifted."
        )

    if metadata.get(
        "article_id"
    ) != canonical_identity.get(
        "article_id"
    ):
        raise SemanticArticleProfileStoreError(
            "Metadata article identity drifted."
        )

    # -------------------------------------------------------------
    # Storage identity
    # -------------------------------------------------------------

    storage_key = storage_identity.get(
        "storage_key"
    )

    if not isinstance(storage_key, str) or not storage_key:
        raise SemanticArticleProfileStoreError(
            "Storage key is missing."
        )

    if stored_profile.get(
        "storage_key"
    ) != storage_key:
        raise SemanticArticleProfileStoreError(
            "Stored-profile storage key drifted."
        )

    if metadata.get(
        "storage_key"
    ) != storage_key:
        raise SemanticArticleProfileStoreError(
            "Metadata storage key drifted."
        )

    if stored_record.get(
        "storage_key"
    ) != storage_key:
        raise SemanticArticleProfileStoreError(
            "Stored-record storage key drifted."
        )

    identity_digest = storage_identity.get(
        "identity_digest"
    )

    if metadata.get(
        "storage_identity_digest"
    ) != identity_digest:
        raise SemanticArticleProfileStoreError(
            "Metadata identity digest drifted."
        )

    if stored_record.get(
        "storage_identity_digest"
    ) != identity_digest:
        raise SemanticArticleProfileStoreError(
            "Stored-record identity digest drifted."
        )

    # -------------------------------------------------------------
    # Payload cryptographic integrity
    # -------------------------------------------------------------

    payload_json = json.dumps(
        dict(profile),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    payload_hash = hashlib.sha256(
        payload_json.encode("utf-8")
    ).hexdigest()

    payload_bytes = len(
        payload_json.encode("utf-8")
    )

    for source_name, source in (
        ("stored_profile", stored_profile),
        ("metadata", metadata),
        ("stored_record", stored_record),
    ):

        if source.get(
            "profile_payload_hash"
        ) != payload_hash:
            raise SemanticArticleProfileStoreError(
                f"{source_name} payload hash drifted."
            )

        if source.get(
            "profile_payload_byte_length"
        ) != payload_bytes:
            raise SemanticArticleProfileStoreError(
                f"{source_name} payload byte length drifted."
            )

    # -------------------------------------------------------------
    # Versioning integrity
    # -------------------------------------------------------------

    version_material = {
        "storage_namespace":
            metadata[
                "storage_namespace"
            ],

        "storage_key":
            storage_key,

        "storage_identity_digest":
            identity_digest,

        "profile_payload_hash":
            payload_hash,

        "store_record_version":
            1,

        "store_schema_version":
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,
    }

    version_json = json.dumps(
        version_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    version_digest = hashlib.sha256(
        version_json.encode("utf-8")
    ).hexdigest()

    version_id = (
        "sapver:v1:"
        + version_digest[:32]
    )

    if metadata.get(
        "store_record_version_digest"
    ) != version_digest:
        raise SemanticArticleProfileStoreError(
            "Metadata store version digest drifted."
        )

    if metadata.get(
        "store_record_version_id"
    ) != version_id:
        raise SemanticArticleProfileStoreError(
            "Metadata store version ID drifted."
        )

    if stored_profile.get(
        "store_record_version_digest"
    ) != version_digest:
        raise SemanticArticleProfileStoreError(
            "Stored-profile version digest drifted."
        )

    if stored_profile.get(
        "store_record_version_id"
    ) != version_id:
        raise SemanticArticleProfileStoreError(
            "Stored-profile version ID drifted."
        )

    # -------------------------------------------------------------
    # Metadata certification
    # -------------------------------------------------------------

    if metadata_certification.get(
        "certification_status"
    ) != "CERTIFIED":
        raise SemanticArticleProfileStoreError(
            "Metadata certification is not CERTIFIED."
        )

    if metadata_certification.get(
        "certification_patch"
    ) != "4.6.19I":
        raise SemanticArticleProfileStoreError(
            "Metadata certification patch drifted."
        )

    if metadata_certification.get(
        "store_record_version"
    ) != 1:
        raise SemanticArticleProfileStoreError(
            "Metadata certification version drifted."
        )

    # -------------------------------------------------------------
    # J final summary
    # -------------------------------------------------------------

    if summary.get(
        "final_status"
    ) != "STORED_SEMANTIC_ARTICLE_PROFILE_READY":
        raise SemanticArticleProfileStoreError(
            "Final result summary status drifted."
        )

    for field in (
        "profile_certified",
        "profile_persisted_in_profile_store",
        "profile_store_written",
        "read_back_verified",
        "integrity_verified",
        "immutability_verified",
        "metadata_versioned",
    ):

        if summary.get(field) is not True:
            raise SemanticArticleProfileStoreError(
                f"Required summary field is not True: {field}"
            )

    for field in (
        "source_profile_payload_mutated",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if summary.get(field) is not False:
            raise SemanticArticleProfileStoreError(
                f"Forbidden summary field is not False: {field}"
            )

    if summary.get(
        "semantic_memory_owner"
    ) != "4.6.28_SEMANTIC_MEMORY":
        raise SemanticArticleProfileStoreError(
            "Summary Semantic Memory ownership drifted."
        )

    if summary.get(
        "knowledge_retrieval_next_owner"
    ) != "4.6.20_KNOWLEDGE_RETRIEVAL":
        raise SemanticArticleProfileStoreError(
            "Knowledge Retrieval handoff drifted."
        )

    # -------------------------------------------------------------
    # J processing-boundary authority
    # -------------------------------------------------------------

    for field in (
        "architecture_definition_preserved",
        "certified_profile_intake_validation_preserved",
        "storage_identity_preserved",
        "persistence_envelope_preserved",
        "profile_write_preserved",
        "profile_store_write_preserved",
        "persistence_preserved",
        "profile_read_back_preserved",
        "integrity_verification_preserved",
        "store_metadata_versioning_preserved",
        "final_stored_profile_result_built",
        "stored_profile_wrapper_created",
        "store_persistence_state_expressed",
        "profile_payload_immutability_preserved",
        "store_metadata_profile_separation_preserved",
    ):

        if boundaries.get(field) is not True:
            raise SemanticArticleProfileStoreError(
                f"Required 4.6.19J boundary is not True: {field}"
            )

    for field in (
        "full_profile_store_certification_performed",
        "additional_profile_write_performed",
        "profile_payload_modified",
        "physical_profile_rewrite_performed",
        "semantic_state_modified",
        "semantic_meaning_rewritten",
        "semantic_merge_performed",
        "cross_document_reasoning_performed",
        "new_reasoning_performed",
        "new_fact_inference_performed",
        "new_relation_inference_performed",
        "conflict_resolution_performed",
        "uncertainty_reinterpretation_performed",
        "confidence_recalculation_performed",
        "semantic_memory_written",
        "linking_decisions_performed",
    ):

        if boundaries.get(field) is not False:
            raise SemanticArticleProfileStoreError(
                f"Forbidden 4.6.19J boundary is not False: {field}"
            )

    # -------------------------------------------------------------
    # Full 4.6.19 certification
    # -------------------------------------------------------------

    full_certification = {
        "certification_status":
            "CERTIFIED",

        "certification_scope":
            "FULL_SEMANTIC_ARTICLE_PROFILE_STORE_PIPELINE",

        "certification_mode":
            "END_TO_END_PERSISTENCE_INTEGRITY_IMMUTABILITY_HARD_CERTIFICATION",

        "certified_phase":
            "4.6.19",

        "certified_source_patch":
            "4.6.19J",

        "profile_certified":
            True,

        "profile_store_persisted":
            True,

        "profile_store_written":
            True,

        "storage_identity_certified":
            True,

        "persistence_envelope_certified":
            True,

        "write_contract_certified":
            True,

        "read_back_certified":
            True,

        "integrity_certified":
            True,

        "immutability_certified":
            True,

        "metadata_versioning_certified":
            True,

        "final_stored_result_certified":
            True,

        "canonical_identity_preserved":
            True,

        "payload_hash_preserved":
            True,

        "payload_byte_length_preserved":
            True,

        "profile_payload_immutable":
            True,

        "metadata_separate_from_profile_payload":
            True,

        "store_record_version":
            1,

        "store_record_version_id":
            version_id,

        "profile_store_owner":
            "4.6.19_PROFILE_STORE",

        "knowledge_retrieval_owner":
            "4.6.20_KNOWLEDGE_RETRIEVAL",

        "semantic_memory_owner":
            "4.6.28_SEMANTIC_MEMORY",

        "source_profile_payload_mutated":
            False,

        "additional_profile_write_performed":
            False,

        "physical_profile_rewrite_performed":
            False,

        "profile_payload_modified":
            False,

        "semantic_state_modified":
            False,

        "semantic_meaning_rewritten":
            False,

        "semantic_merge_performed":
            False,

        "cross_document_reasoning_performed":
            False,

        "new_reasoning_performed":
            False,

        "new_fact_inference_performed":
            False,

        "new_relation_inference_performed":
            False,

        "conflict_resolution_performed":
            False,

        "uncertainty_reinterpretation_performed":
            False,

        "confidence_recalculation_performed":
            False,

        "semantic_memory_written":
            False,

        "linking_decisions_performed":
            False,
    }

    return {
        "schema_version":
            "certified_semantic_article_profile_store_result_v1",

        "version":
            SEMANTIC_ARTICLE_PROFILE_STORE_VERSION,

        "phase":
            SEMANTIC_ARTICLE_PROFILE_STORE_PHASE,

        "patch":
            "4.6.19K",

        "status":
            "SEMANTIC_ARTICLE_PROFILE_STORE_CERTIFIED",

        "canonical_article_identity":
            deepcopy(
                dict(canonical_identity)
            ),

        "full_profile_store_certification":
            full_certification,

        "storage_identity":
            deepcopy(
                dict(storage_identity)
            ),

        "store_metadata":
            deepcopy(
                dict(metadata)
            ),

        "stored_semantic_article_profile":
            deepcopy(
                dict(stored_profile)
            ),

        "certified_semantic_article_profile":
            deepcopy(
                dict(profile)
            ),

        "verified_stored_record":
            deepcopy(
                dict(stored_record)
            ),

        "final_result_summary":
            deepcopy(
                dict(summary)
            ),

        "source_final_store_result":
            deepcopy(
                dict(final_store_result)
            ),

        "processing_boundaries": {
            "architecture_definition_preserved":
                True,

            "certified_profile_intake_validation_preserved":
                True,

            "storage_identity_preserved":
                True,

            "persistence_envelope_preserved":
                True,

            "profile_write_preserved":
                True,

            "profile_store_write_preserved":
                True,

            "persistence_preserved":
                True,

            "profile_read_back_preserved":
                True,

            "integrity_verification_preserved":
                True,

            "store_metadata_versioning_preserved":
                True,

            "final_stored_profile_result_preserved":
                True,

            "full_profile_store_certification_performed":
                True,

            "profile_store_certified":
                True,

            "profile_payload_immutability_preserved":
                True,

            "store_metadata_profile_separation_preserved":
                True,

            "additional_profile_write_performed":
                False,

            "physical_profile_rewrite_performed":
                False,

            "profile_payload_modified":
                False,

            "semantic_state_modified":
                False,

            "semantic_meaning_rewritten":
                False,

            "semantic_merge_performed":
                False,

            "cross_document_reasoning_performed":
                False,

            "new_reasoning_performed":
                False,

            "new_fact_inference_performed":
                False,

            "new_relation_inference_performed":
                False,

            "conflict_resolution_performed":
                False,

            "uncertainty_reinterpretation_performed":
                False,

            "confidence_recalculation_performed":
                False,

            "semantic_memory_written":
                False,

            "linking_decisions_performed":
                False,
        },

        "persistence_policy":
            "PROFILE_STORE_CERTIFIED_PERSISTENCE",

        "next_stage":
            "knowledge_retrieval",
    }

